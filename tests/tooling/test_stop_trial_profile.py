# Checks D126's literal P3 compile-only route against its adopted contract.
# Keeps profile identity and refusal expectations separate from production tooling.
# All transport is mocked; these checks provide no board or physical evidence.
import copy
import json
from pathlib import Path
import unittest
from unittest import mock
from . import test_opp_view_policy as fixture

ROOT = Path(__file__).resolve().parents[2]
SKETCH = 'bench/stopping_distance'
PROJECT = 'stopping_distance.ino'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P3_STOP_TRIAL=1'
TURN_FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P3_TURN_TRIAL=1'
DRIVE_FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P3_DRIVE_TEST=1'
B4_FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_B4_STAND=1'


def document(immediate=False, project=PROJECT, flags=FLAGS):
    return json.loads(json.dumps(fixture.document(immediate, project)).replace(fixture.FLAGS, flags))


class StopTrialProfileTests(unittest.TestCase):
    def validate(self, value, fqbn=fixture.FQBN, flags=FLAGS):
        return fixture.policy.validate_result(json.dumps(value), fqbn, flags,
                                              fixture.BUILD, project=PROJECT)

    def preflight(self, value, fqbn=fixture.FQBN, flags=FLAGS):
        return fixture.policy.validate_preflight(json.dumps(value), fqbn, flags,
            fixture.BUILD, fixture.DATA, project=PROJECT)

    def test_exact_default_project_and_both_compiler_flags_validate(self):
        result = self.validate(document())
        self.assertEqual(result, self.preflight(document()))
        self.assertEqual(result['build.project_name'], PROJECT)
        self.assertEqual(result['build.boot_mode'], 'wait')
        for key in ('compiler.c.extra_flags', 'compiler.cpp.extra_flags'):
            self.assertEqual(result[key], FLAGS)

    def test_immediate_match_motor_missing_or_extra_flags_refuse(self):
        invalid = ('', fixture.FLAGS, B4_FLAGS, DRIVE_FLAGS, TURN_FLAGS, FLAGS + ' -DSUMOX_B4_STAND=1',
                   FLAGS + ' -DOTHER=1', FLAGS + ' -DSUMOX_P3_STOP_TRIAL=0',
                   FLAGS.replace('TRIAL=1', 'TRIAL=0'), FLAGS.replace('TRIAL=1', 'TRIAL=2'),
                   FLAGS.replace('MATCH=0', 'MATCH=1'),
                   FLAGS.replace('MOTORS_ALLOWED=0', 'MOTORS_ALLOWED=1'),
                   '-DMATCH=1 -DMOTORS_ALLOWED=1', ' ' + FLAGS, FLAGS + ' ')
        for fqbn in (fixture.FQBN, fixture.IMMEDIATE):
            for flags in invalid:
                with self.subTest(fqbn=fqbn, flags=flags), self.assertRaises(ValueError):
                    fixture.policy.selected_project(PROJECT, fqbn, flags)
        for boundary in (self.validate, self.preflight):
            with self.assertRaises(ValueError):
                boundary(document(True), fixture.IMMEDIATE)

    def test_each_compiler_flag_and_expanded_recipe_drift_refuses(self):
        original = document()
        changed = 0
        for index, entry in enumerate(fixture.entries(original)):
            if FLAGS not in entry:
                continue
            changed += 1
            for replacement in (fixture.FLAGS, B4_FLAGS,
                                FLAGS.replace('MOTORS_ALLOWED=0', 'MOTORS_ALLOWED=1')):
                bad = copy.deepcopy(original)
                fixture.entries(bad)[index] = entry.replace(FLAGS, replacement)
                for boundary in (self.validate, self.preflight):
                    with self.subTest(index=index, replacement=replacement,
                                      boundary=boundary.__name__), self.assertRaises(ValueError):
                        boundary(bad)
        self.assertGreaterEqual(changed, 4)

    def test_each_mixed_project_recipe_refuses(self):
        original = document()
        changed = 0
        for index, entry in enumerate(fixture.entries(original)):
            if PROJECT not in entry:
                continue
            changed += 1
            for other in ('app.ino', 'motor_direction.ino', 'stopping_distance_other.ino'):
                bad = copy.deepcopy(original)
                fixture.entries(bad)[index] = entry.replace(PROJECT, other)
                for boundary in (self.validate, self.preflight):
                    with self.subTest(index=index, other=other), self.assertRaises(ValueError):
                        boundary(bad)
        self.assertGreaterEqual(changed, 6)

    def test_external_library_upload_or_unsuccessful_result_refuses(self):
        for key, value in (('success', False), ('upload_result', {'success': True})):
            bad = document()
            bad[key] = value
            with self.assertRaises(ValueError):
                self.validate(bad)
        bad = document()
        bad['builder_result']['used_libraries'] = [{'name': 'Arduino_RouterBridge'}]
        with self.assertRaises(ValueError):
            self.validate(bad)

    def test_profile_flags_are_not_accepted_for_other_projects(self):
        for project in ('app.ino', 'runtime_inert.ino', 'opp_view.ino', 'qtr_raw.ino',
                        'vbat.ino', 'imu_heading.ino', 'ui.ino', 'ui_adc_probe.ino',
                        'motor_stand.ino', 'recorder.ino', 'motor_direction.ino', 'drive_test.ino', 'turn_accuracy.ino'):
            with self.subTest(project=project), self.assertRaises(ValueError):
                fixture.policy.validate_result(json.dumps(document(project=project)),
                    fixture.FQBN, FLAGS, fixture.BUILD, project=project)

    def test_old_app_and_b4_exact_profiles_still_validate(self):
        for project, flags in (('app.ino', fixture.FLAGS), ('motor_direction.ino', B4_FLAGS), ('drive_test.ino', DRIVE_FLAGS), ('turn_accuracy.ino', TURN_FLAGS)):
            with self.subTest(project=project):
                props = fixture.policy.validate_result(json.dumps(document(project=project, flags=flags)),
                    fixture.FQBN, flags, fixture.BUILD, project=project)
                self.assertEqual(props['compiler.c.extra_flags'], flags)
                self.assertEqual(props['compiler.cpp.extra_flags'], flags)

    def test_default_compile_uses_only_checked_literal_project(self):
        for startup in (None, 'default'):
            with self.subTest(startup=startup), fixture.isolated_flash(SKETCH) as calls:
                fixture.board.flash(fixture.args(SKETCH, startup))
                source = '/fixture/root/' + 'a' * 64 + '/stopping_distance'
                calls['compile_app'].assert_called_once_with('fixture-board', 'a' * 64, source,
                    '/fixture/root', fixture.FQBN, FLAGS, 'default', project=PROJECT)
                self.assertEqual(calls['remote'].call_args_list,
                                 [mock.call('fixture-board', ['mkdir', '-p', source])])
                calls['verify_inert_source'].assert_not_called()
                calls['verify_runtime_artifacts'].assert_not_called()

    def test_upload_match_immediate_and_foreign_run_options_refuse_before_io(self):
        requests = []
        for startup in (None, 'default', 'immediate'):
            for match in (False, True):
                for compile_only in (False, True):
                    if not match and compile_only and startup != 'immediate':
                        continue
                    requests.append(fixture.args(SKETCH, startup, match, compile_only))
        for compile_only in (False, True):
            request = fixture.args(SKETCH, compile_only=compile_only)
            request.run_ui_adc_probe = 'd114-ui-adc-01'
            requests.append(request)
        for request in requests:
            with self.subTest(request=request), fixture.isolated_flash(SKETCH) as calls:
                with self.assertRaises(ValueError):
                    fixture.board.flash(request)
                for name in ('target', 'require_transport', 'stage', 'remote', 'compile_app',
                             'sync_sources', 'verify_core', 'source_hash'):
                    calls[name].assert_not_called()

    def test_regular_and_dangling_profiles_refuse_before_io(self):
        for name in ('sketch.yaml', 'sketch.yml'):
            for dangling in (False, True):
                with self.subTest(name=name, dangling=dangling), fixture.isolated_flash(SKETCH) as calls:
                    folder = fixture.board.ROOT / SKETCH
                    folder.mkdir(parents=True)
                    path = folder / name
                    if dangling:
                        path.symlink_to(folder / 'missing')
                    else:
                        path.write_text('profile: unreviewed')
                    with self.assertRaises(ValueError):
                        fixture.board.flash(fixture.args(SKETCH))
                    for entry in ('target', 'require_transport', 'stage', 'remote', 'compile_app'):
                        calls[entry].assert_not_called()

    def test_configuration_or_checked_failure_does_not_fall_back(self):
        for failure in ('setting', 'compile_app'):
            with self.subTest(failure=failure), fixture.isolated_flash(SKETCH) as calls:
                calls[failure].side_effect = ValueError('controlled checked refusal')
                with self.assertRaises(ValueError):
                    fixture.board.flash(fixture.args(SKETCH))
                for call in calls['remote'].call_args_list:
                    self.assertEqual(call.args[1][0], 'mkdir')
                if failure == 'setting':
                    calls['compile_app'].assert_not_called()
                else:
                    calls['compile_app'].assert_called_once()

    def test_selected_artifact_names_remain_exact(self):
        props = self.validate(document())
        remote = mock.Mock()
        with mock.patch.object(fixture.policy, 'verify_hashes', return_value={}) as verify:
            fixture.policy.verify_files(remote, 'fixture-board', props, fixture.BUILD, fixture.ARTIFACTS)
        artifacts = verify.call_args.args[3]
        self.assertEqual(artifacts, [fixture.BUILD + '/' + PROJECT + suffix
            for suffix in ('.elf', '_debug.elf', '_temp.elf')] +
            [fixture.ARTIFACTS + '/' + PROJECT + '.elf-zsk.bin'])
        remote.assert_not_called()

    def test_no_new_inert_upload_key_exists(self):
        manifest = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
        self.assertNotIn(SKETCH, manifest)

    def test_native_wrapper_declares_empty_grants_and_exact_compile_guard(self):
        source = (ROOT / SKETCH / PROJECT).read_text()
        for literal in ('#include "src/app/native_sources_unoq.h"',
                        '#include "src/hal/motor_port_unoq.h"',
                        'app::NativeSources sources;', 'motors::UnoQPort motor_port;',
                        'app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port()};',
                        'runtime.begin(app::SetupGrants{});', 'runtime.step();',
                        'SUMOX_P3_STOP_TRIAL == 1 && MATCH == 0 && MOTORS_ALLOWED == 0'):
            self.assertIn(literal, source)
        self.assertNotIn('SUMOX_P3_STOP_TRIAL 1', source)
        self.assertNotIn('SetupGrants{true', source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
