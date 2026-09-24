# Tests D135's exact inert opener-timing route using adopted public policy APIs.
# Keeps mocked compiler receipts and isolated syntax probes separate from native evidence.
# Independent tests never contact a board, upload an artifact or execute motor code.
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

if __package__:
    from . import test_opp_view_policy as fixture
else:
    import test_opp_view_policy as fixture

ROOT = Path(__file__).resolve().parents[2]
SKETCH = 'bench/opener_timing'
PROJECT = 'opener_timing.ino'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P5_ABORT_TIMING=1'
OLD_PROFILES = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
                'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE')


def document(immediate=False, project=PROJECT, flags=FLAGS):
    return json.loads(json.dumps(fixture.document(immediate, project)).replace(fixture.FLAGS, flags))


class OpenerTimingPolicyTests(unittest.TestCase):
    def validate(self, value, fqbn=fixture.FQBN, flags=FLAGS):
        return fixture.policy.validate_result(json.dumps(value), fqbn, flags,
                                              fixture.BUILD, project=PROJECT)

    def preflight(self, value, fqbn=fixture.FQBN, flags=FLAGS):
        return fixture.policy.validate_preflight(json.dumps(value), fqbn, flags,
            fixture.BUILD, fixture.DATA, project=PROJECT)

    def test_exact_project_default_startup_and_both_compilers_validate(self):
        props = self.validate(document())
        self.assertEqual(props, self.preflight(document()))
        self.assertEqual(props['build.project_name'], PROJECT)
        self.assertEqual(props['build.boot_mode'], 'wait')
        for key in ('compiler.c.extra_flags', 'compiler.cpp.extra_flags'):
            self.assertEqual(props[key], FLAGS)

    def test_missing_extra_wrong_motor_match_profile_and_immediate_flags_refuse(self):
        invalid = ('', fixture.FLAGS, ' ' + FLAGS, FLAGS + ' ', FLAGS + ' -DOTHER=1',
                   FLAGS.replace('MATCH=0', 'MATCH=1'),
                   FLAGS.replace('MOTORS_ALLOWED=0', 'MOTORS_ALLOWED=1'),
                   FLAGS.replace('TIMING=1', 'TIMING=0'), FLAGS.replace('TIMING=1', 'TIMING=2'),
                   FLAGS + ' -DSUMOX_P5_ABORT_TIMING=0', FLAGS + ' -DSUMOX_P5_ABORT_TIMING=1')
        invalid += tuple(FLAGS + ' -D' + name + '=' + value
                         for name in OLD_PROFILES for value in ('0', '1'))
        for fqbn in (fixture.FQBN, fixture.IMMEDIATE):
            for flags in invalid:
                with self.subTest(fqbn=fqbn, flags=flags), self.assertRaises(ValueError):
                    fixture.policy.selected_project(PROJECT, fqbn, flags)
        for boundary in (self.validate, self.preflight):
            with self.assertRaises(ValueError):
                boundary(document(True), fixture.IMMEDIATE)

    def test_each_compiler_flag_and_expanded_recipe_must_bind_same_profile(self):
        original = document()
        changed = 0
        for index, entry in enumerate(fixture.entries(original)):
            if FLAGS not in entry:
                continue
            changed += 1
            for replacement in (fixture.FLAGS, FLAGS.replace('MOTORS_ALLOWED=0', 'MOTORS_ALLOWED=1'),
                                FLAGS + ' -USUMOX_P5_ABORT_TIMING'):
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
            for other in ('app.ino', 'reactive_timing.ino', 'opener_timing_other.ino'):
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

    def test_p5_flags_cannot_cross_into_any_old_project(self):
        projects = ('app.ino', 'runtime_inert.ino', 'opp_view.ino', 'qtr_raw.ino', 'vbat.ino',
                    'imu_heading.ino', 'ui.ino', 'ui_adc_probe.ino', 'motor_stand.ino', 'recorder.ino',
                    'motor_direction.ino', 'drive_test.ino', 'turn_accuracy.ino', 'stopping_distance.ino',
                    'reactive_test.ino', 'reactive_timing.ino')
        for project in projects:
            with self.subTest(project=project), self.assertRaises(ValueError):
                fixture.policy.validate_result(json.dumps(document(project=project)),
                    fixture.FQBN, FLAGS, fixture.BUILD, project=project)

    def test_old_app_reactive_and_p4_timing_profiles_keep_exact_admission(self):
        reactive = fixture.FLAGS + ' -DSUMOX_P4_REACTIVE=1'
        for project, flags in (('app.ino', fixture.FLAGS), ('reactive_test.ino', reactive),
                               ('reactive_timing.ino', reactive + ' -DSUMOX_TIMING_EVIDENCE=1')):
            with self.subTest(project=project):
                props = fixture.policy.validate_result(json.dumps(document(project=project, flags=flags)),
                    fixture.FQBN, flags, fixture.BUILD, project=project)
                self.assertEqual(props['compiler.c.extra_flags'], flags)
                self.assertEqual(props['compiler.cpp.extra_flags'], flags)

    def test_compile_only_dispatches_literal_checked_project_without_upload(self):
        for startup in (None, 'default'):
            with self.subTest(startup=startup), fixture.isolated_flash(SKETCH) as calls:
                fixture.board.flash(fixture.args(SKETCH, startup))
                source = '/fixture/root/' + 'a' * 64 + '/opener_timing'
                calls['compile_app'].assert_called_once_with('fixture-board', 'a' * 64, source,
                    '/fixture/root', fixture.FQBN, FLAGS, 'default', project=PROJECT)
                self.assertEqual(calls['remote'].call_args_list,
                                 [mock.call('fixture-board', ['mkdir', '-p', source])])
                calls['verify_inert_source'].assert_not_called()
                calls['verify_runtime_artifacts'].assert_not_called()

    def test_upload_match_immediate_and_foreign_run_refuse_before_io(self):
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

    def test_local_regular_and_dangling_profiles_refuse_before_io(self):
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

    def test_wrapper_binds_native_owners_empty_grants_without_source_macro_overrides(self):
        source = (ROOT / SKETCH / PROJECT).read_text()
        for literal in ('#include "src/app/native_sources_unoq.h"',
                        '#include "src/hal/motor_port_unoq.h"', 'app::NativeSources sources;',
                        'motors::UnoQPort motor_port;',
                        'app::Runtime runtime{motor_port.port(), sources.adcPort(), sources.port()};',
                        'runtime.begin(app::SetupGrants{});', 'runtime.step();'):
            self.assertIn(literal, source)
        self.assertNotRegex(source, r'#\s*(?:define|undef)\s+(?:SUMOX_\w+|MOTORS_ALLOWED|MATCH)\b')
        self.assertNotIn('SetupGrants{true', source)

    def compile_syntax(self, source, flags, include):
        compiler = shutil.which('g++')
        self.assertIsNotNone(compiler, 'WSL/Linux g++ required for isolated compile-only profile probes')
        return subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
            '-fsyntax-only', '-fno-exceptions', '-fno-rtti', '-x', 'c++', '-I', str(include),
            *('-D' + name + '=' + str(value) for name, value in flags.items()), '-'],
            input=source, capture_output=True, text=True, check=False, timeout=30)

    def test_public_header_default_and_explicit_zero_keep_old_profile_identity(self):
        source = ('#include "core/fsm.h"\nstatic_assert(SUMOX_P5_ABORT_TIMING == 0);\n'
                  'static_assert(!fsm::RobotResult::OPENER_TIMING_PROFILE);\n'
                  'static_assert(!fsm::RobotResult::TIMING_EVIDENCE_PROFILE);\n'
                  'static_assert(logframe::ROBOT_EVENT_CAPACITY == 21);\n')
        for flags in ({'MATCH': 0}, {'MATCH': 0, 'SUMOX_P5_ABORT_TIMING': 0}):
            with self.subTest(flags=flags):
                result = self.compile_syntax(source, flags, ROOT / 'src')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_public_header_accepts_both_motor_variants_and_rejects_conflicting_profiles(self):
        source = ('#include "core/fsm.h"\nstatic_assert(SUMOX_P5_ABORT_TIMING == 1);\n'
                  'static_assert(fsm::RobotResult::OPENER_TIMING_PROFILE);\n'
                  'static_assert(!fsm::RobotResult::TIMING_EVIDENCE_PROFILE);\n'
                  'static_assert(logframe::ROBOT_EVENT_CAPACITY == 21);\n')
        expected = dict(MATCH=0, MOTORS_ALLOWED=0, SUMOX_P5_ABORT_TIMING=1)
        cases = [('M0', expected, True), ('M1', dict(expected, MOTORS_ALLOWED=1), True)]
        cases += [(name, dict(expected, **{name: 1}), False) for name in ('MATCH',) + OLD_PROFILES]
        for label, flags, accepted in cases:
            with self.subTest(profile=label):
                result = self.compile_syntax(source, flags, ROOT / 'src')
                self.assertEqual(result.returncode == 0, accepted, result.stdout + result.stderr)

    def test_public_header_rejects_nonbinary_or_noninteger_profile_values(self):
        source = '#include "core/fsm.h"\n'
        for value in (-1, 2, 2147483647, '1.0', '1e0'):
            with self.subTest(value=value):
                result = self.compile_syntax(source, {'MATCH': 0, 'SUMOX_P5_ABORT_TIMING': value}, ROOT / 'src')
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue((result.stdout + result.stderr).strip())

    def test_actual_wrapper_compile_guard_accepts_only_its_exact_inert_profile(self):
        with tempfile.TemporaryDirectory(prefix='d135-wrapper-') as temporary:
            stage = Path(temporary)
            native = stage / 'src/app/native_sources_unoq.h'
            motor = stage / 'src/hal/motor_port_unoq.h'
            native.parent.mkdir(parents=True)
            motor.parent.mkdir(parents=True)
            native.write_text('''#pragma once
namespace motors { struct Port; }
namespace app {
struct AdcPort {}; struct SourcePort {}; struct SetupGrants {};
struct NativeSources { AdcPort adcPort(); SourcePort port(); };
struct Runtime { Runtime(motors::Port, AdcPort, SourcePort); void begin(SetupGrants); void step(); };
}
''', encoding='ascii')
            motor.write_text('#pragma once\nnamespace motors { struct Port {}; struct UnoQPort { Port port(); }; }\n',
                             encoding='ascii')
            source = (ROOT / SKETCH / PROJECT).read_text()
            expected = dict(MATCH=0, MOTORS_ALLOWED=0, SUMOX_P5_ABORT_TIMING=1)
            expected.update({name: 0 for name in OLD_PROFILES})
            cases = [('exact', expected, True)]
            for name, value in expected.items():
                for wrong in (1 - value, 2):
                    cases.append((name + '=' + str(wrong), dict(expected, **{name: wrong}), False))
            for label, flags, accepted in cases:
                with self.subTest(profile=label):
                    result = self.compile_syntax(source, flags, stage)
                    self.assertEqual(result.returncode == 0, accepted, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
