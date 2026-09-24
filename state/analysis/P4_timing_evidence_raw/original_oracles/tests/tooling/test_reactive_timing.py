# Checks D129's exact inert timing-evidence compile route from the public contract.
# Separates mocked build metadata from native compilation and physical evidence.
# Independent policy fixtures exercise admission, artifact identity and refusal.
import copy
import json
from pathlib import Path
import re
import unittest
from unittest import mock
from . import test_opp_view_policy as fixture

ROOT = Path(__file__).resolve().parents[2]
SKETCH = 'bench/reactive_timing'
PROJECT = 'reactive_timing.ino'
REACTIVE = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P4_REACTIVE=1'
FLAGS = REACTIVE + ' -DSUMOX_TIMING_EVIDENCE=1'


def document(immediate=False, project=PROJECT, flags=FLAGS):
    return json.loads(json.dumps(fixture.document(immediate, project)).replace(fixture.FLAGS, flags))


class ReactiveTimingTests(unittest.TestCase):
    def validate(self, value, fqbn=fixture.FQBN, flags=FLAGS):
        return fixture.policy.validate_result(json.dumps(value), fqbn, flags,
                                              fixture.BUILD, project=PROJECT)

    def preflight(self, value, fqbn=fixture.FQBN, flags=FLAGS):
        return fixture.policy.validate_preflight(json.dumps(value), fqbn, flags,
            fixture.BUILD, fixture.DATA, project=PROJECT)

    def test_exact_project_both_compilers_and_default_startup_validate(self):
        props = self.validate(document())
        self.assertEqual(props, self.preflight(document()))
        self.assertEqual(props['build.project_name'], PROJECT)
        self.assertEqual(props['build.boot_mode'], 'wait')
        for key in ('compiler.c.extra_flags', 'compiler.cpp.extra_flags'):
            self.assertEqual(props[key], FLAGS)

    def test_missing_extra_wrong_profile_motor_match_and_immediate_flags_refuse(self):
        invalid = ('', fixture.FLAGS, REACTIVE, FLAGS + ' -DOTHER=1', ' ' + FLAGS, FLAGS + ' ',
                   FLAGS.replace('MATCH=0', 'MATCH=1'), FLAGS.replace('MOTORS_ALLOWED=0', 'MOTORS_ALLOWED=1'),
                   FLAGS.replace('REACTIVE=1', 'REACTIVE=0'), FLAGS.replace('REACTIVE=1', 'REACTIVE=2'),
                   FLAGS.replace('EVIDENCE=1', 'EVIDENCE=0'), FLAGS.replace('EVIDENCE=1', 'EVIDENCE=2'),
                   FLAGS + ' -DSUMOX_TIMING_EVIDENCE=0',
                   fixture.FLAGS + ' -DSUMOX_TIMING_EVIDENCE=1')
        invalid += tuple(FLAGS + ' -D' + name + '=1' for name in
            ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL', 'SUMOX_P3_STOP_TRIAL'))
        for fqbn in (fixture.FQBN, fixture.IMMEDIATE):
            for flags in invalid:
                with self.subTest(fqbn=fqbn, flags=flags), self.assertRaises(ValueError):
                    fixture.policy.selected_project(PROJECT, fqbn, flags)
        for boundary in (self.validate, self.preflight):
            with self.assertRaises(ValueError):
                boundary(document(True), fixture.IMMEDIATE)

    def test_each_compiler_flag_and_expanded_recipe_must_bind_the_same_profile(self):
        original = document()
        changed = 0
        for index, entry in enumerate(fixture.entries(original)):
            if FLAGS not in entry:
                continue
            changed += 1
            for replacement in (fixture.FLAGS, REACTIVE, FLAGS.replace('MOTORS_ALLOWED=0', 'MOTORS_ALLOWED=1')):
                bad = copy.deepcopy(original)
                fixture.entries(bad)[index] = entry.replace(FLAGS, replacement)
                for boundary in (self.validate, self.preflight):
                    with self.subTest(index=index, replacement=replacement), self.assertRaises(ValueError):
                        boundary(bad)
        self.assertGreaterEqual(changed, 4)

    def test_each_mixed_project_recipe_or_artifact_refuses(self):
        original = document()
        changed = 0
        for index, entry in enumerate(fixture.entries(original)):
            if PROJECT not in entry:
                continue
            changed += 1
            for other in ('app.ino', 'reactive_test.ino', 'reactive_timing_other.ino'):
                bad = copy.deepcopy(original)
                fixture.entries(bad)[index] = entry.replace(PROJECT, other)
                for boundary in (self.validate, self.preflight):
                    with self.subTest(index=index, other=other), self.assertRaises(ValueError):
                        boundary(bad)
        self.assertGreaterEqual(changed, 6)

    def test_unsuccessful_external_library_and_upload_receipts_refuse(self):
        for key, value in (('success', False), ('success', 1), ('error', 'failed'),
                           ('upload_result', {'success': True})):
            bad = document()
            bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.validate(bad)
        bad = document()
        bad['builder_result']['used_libraries'] = [{'name': 'Arduino_RouterBridge'}]
        with self.assertRaises(ValueError):
            self.validate(bad)

    def test_timing_flags_cannot_cross_into_any_old_project(self):
        projects = ('app.ino', 'runtime_inert.ino', 'opp_view.ino', 'qtr_raw.ino', 'vbat.ino',
                    'imu_heading.ino', 'ui.ino', 'ui_adc_probe.ino', 'motor_stand.ino', 'recorder.ino',
                    'motor_direction.ino', 'drive_test.ino', 'turn_accuracy.ino', 'stopping_distance.ino',
                    'reactive_test.ino')
        for project in projects:
            with self.subTest(project=project), self.assertRaises(ValueError):
                fixture.policy.validate_result(json.dumps(document(project=project)),
                    fixture.FQBN, FLAGS, fixture.BUILD, project=project)

    def test_uninstrumented_app_and_reactive_project_keep_their_exact_flags(self):
        for project, flags in (('app.ino', fixture.FLAGS), ('reactive_test.ino', REACTIVE)):
            with self.subTest(project=project):
                props = fixture.policy.validate_result(json.dumps(document(project=project, flags=flags)),
                    fixture.FQBN, flags, fixture.BUILD, project=project)
                self.assertEqual(props['compiler.c.extra_flags'], flags)
                self.assertEqual(props['compiler.cpp.extra_flags'], flags)

    def test_compile_only_dispatches_the_literal_checked_project_without_upload(self):
        for startup in (None, 'default'):
            with self.subTest(startup=startup), fixture.isolated_flash(SKETCH) as calls:
                fixture.board.flash(fixture.args(SKETCH, startup))
                source = '/fixture/root/' + 'a' * 64 + '/reactive_timing'
                calls['compile_app'].assert_called_once_with('fixture-board', 'a' * 64, source,
                    '/fixture/root', fixture.FQBN, FLAGS, 'default', project=PROJECT)
                self.assertEqual(calls['remote'].call_args_list,
                                 [mock.call('fixture-board', ['mkdir', '-p', source])])
                calls['verify_inert_source'].assert_not_called()
                calls['verify_runtime_artifacts'].assert_not_called()

    def test_upload_match_immediate_or_foreign_run_requests_refuse_before_io(self):
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

    def test_local_regular_and_dangling_sketch_profiles_refuse_before_io(self):
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

    def test_checked_failure_propagates_without_unchecked_fallback(self):
        for failure in ('setting', 'compile_app'):
            with self.subTest(failure=failure), fixture.isolated_flash(SKETCH) as calls:
                calls[failure].side_effect = ValueError('synthetic checked refusal')
                with self.assertRaises(ValueError):
                    fixture.board.flash(fixture.args(SKETCH))
                for call in calls['remote'].call_args_list:
                    self.assertEqual(call.args[1][0], 'mkdir')
                if failure == 'setting':
                    calls['compile_app'].assert_not_called()
                else:
                    calls['compile_app'].assert_called_once()

    def test_verified_artifact_names_are_exact_and_project_bound(self):
        props = self.validate(document())
        remote = mock.Mock()
        with mock.patch.object(fixture.policy, 'verify_hashes', return_value={}) as verify:
            fixture.policy.verify_files(remote, 'fixture-board', props, fixture.BUILD, fixture.ARTIFACTS)
        self.assertEqual(verify.call_args.args[3], [fixture.BUILD + '/' + PROJECT + suffix
            for suffix in ('.elf', '_debug.elf', '_temp.elf')] +
            [fixture.ARTIFACTS + '/' + PROJECT + '.elf-zsk.bin'])
        remote.assert_not_called()

    def test_no_inert_upload_key_was_added(self):
        manifest = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
        self.assertNotIn(SKETCH, manifest)

    def test_wrapper_binds_actual_sources_empty_grants_and_all_four_compile_conditions(self):
        source = (ROOT / SKETCH / PROJECT).read_text()
        for literal in ('#include "src/app/native_sources_unoq.h"',
                        '#include "src/hal/motor_port_unoq.h"', 'app::NativeSources sources;',
                        'motors::UnoQPort motor_port;',
                        'app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port()};',
                        'runtime.begin(app::SetupGrants{});', 'runtime.step();'):
            self.assertIn(literal, source)
        guarded = source.replace('\\\n', ' ')
        conditions = re.findall(r'^#if\s+(.+)$', guarded, re.MULTILINE)
        expected = ('SUMOX_TIMING_EVIDENCE == 1', 'SUMOX_P4_REACTIVE == 1',
                    'MATCH == 0', 'MOTORS_ALLOWED == 0')
        self.assertTrue(any(all(term in condition for term in expected) for condition in conditions))
        self.assertIn('#error', source)
        self.assertNotRegex(source, r'#\s*define\s+(SUMOX_TIMING_EVIDENCE|SUMOX_P4_REACTIVE|MOTORS_ALLOWED|MATCH)\b')
        self.assertNotIn('SetupGrants{true', source)


if __name__ == '__main__':
    unittest.main(verbosity=2)
