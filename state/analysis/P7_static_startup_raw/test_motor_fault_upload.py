# Tests D175's closed dynamic diagnostic profile from its public contract.
# Protects exact selection, isolated ownership and unchanged bounded upload evidence.
# Frozen Linux fixtures use tiny files and controlled children; freeze before running.
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
SOURCE = '8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36'
RUN = 'motor-fault-8f592937-run01'
PARENT = '/home/arduino/sumox26_codex_build'
BUILD = (PARENT + '/motor-fault-active01/_app_builds/native-app-v1/' + SOURCE +
         '/bench-default/3aafdd0129f64799b4db51efe78e5c44/build')
SKETCH = PARENT + '/motor-fault-active01/motor_fault'
OUTPUT = PARENT + '/' + RUN + '-upload'
ARGV = ['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload', '--fqbn',
        'arduino:zephyr:unoq', '--input-file', BUILD + '/motor_fault.ino.elf', SKETCH]
GLOBAL_NAMES = ('SOURCE', 'BUILD', 'SKETCH', 'FILE_PATHS', 'ABSENT', 'BINDINGS')

spec = importlib.util.spec_from_file_location('motor_fault_frozen_upload_fixture',
                                             HERE / 'test_upload_loader.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
legacy = fixture.legacy


def diagnostic_bindings(original):
    result = copy.deepcopy(original)
    result.update(schema='fixed-motor-fault-upload-v1', run_id=RUN,
                  source_sha256=SOURCE, output=OUTPUT)
    result['files']['raw']['path'] = BUILD + '/motor_fault.ino.elf'
    result['files']['sketch']['path'] = BUILD + '/motor_fault.ino.elf-zsk.bin'
    result['absent'] = original['absent'][:11] + [SKETCH + '/sketch.' + suffix
                                                for suffix in ('yaml', 'yml', 'json')]
    return result


def field_values(value, key):
    if isinstance(value, dict):
        found = [value[key]] if key in value else []
        for item in value.values():
            found.extend(field_values(item, key))
        return found
    if isinstance(value, list):
        return [found for item in value for found in field_values(item, key)]
    return []


class MotorFaultUpload(fixture.UploadLoaderContract):
    def setUp(self):
        super().setUp()
        self.legacy_bindings = copy.deepcopy(self.bindings)
        self.global_objects = {name: getattr(self.subject, name) for name in GLOBAL_NAMES}
        self.global_values = copy.deepcopy(self.global_objects)
        self.global_keys = set(vars(self.subject))
        self.bindings = diagnostic_bindings(self.legacy_bindings)
        self.admitted_bindings = copy.deepcopy(self.bindings)
        self.output = self.logical(OUTPUT)
        self.receipt_dir = self.output
        self.logical(SKETCH).mkdir(parents=True)
        for role in ('raw', 'sketch'):
            target = self.logical(self.bindings['files'][role]['path'])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(self.payloads[role])

    def assert_globals_unchanged(self):
        self.assertEqual(set(vars(self.subject)), self.global_keys)
        for name in GLOBAL_NAMES:
            self.assertIs(getattr(self.subject, name), self.global_objects[name], name)
            self.assertEqual(getattr(self.subject, name), self.global_values[name], name)

    def upload(self, **kwargs):
        options = dict(fs_root=self.root, executor=self.execute, clock=self.clock,
                       bindings=self.bindings, run_id=RUN)
        options.update(kwargs)
        return self.subject.upload_loader(self.helper, self.support, **options)

    def verify_launch(self, argv, stdout_path, stderr_path, timeout):
        self.assert_globals_unchanged()
        self.assertEqual(argv, ARGV)
        self.assertEqual(self.calls, [], 'One command only; no retry or compile')
        self.assertEqual(self.local_argument(stdout_path), self.output / 'upload.stdout')
        self.assertEqual(self.local_argument(stderr_path), self.output / 'upload.stderr')
        self.assertEqual(timeout, min(120, 280 - self.clock.value))
        self.check_prelaunch_receipts()
        self.calls.append((copy.deepcopy(argv), timeout))

    def check_prelaunch_receipts(self):
        for kind in ('attempt', 'command'):
            claim = json.loads((self.output / ('upload_' + kind + '.json')).read_text())
            self.assertEqual(claim['schema'], 'motor-fault-upload-' + kind + '-v1')
            for key, expected in (('source_sha256', SOURCE), ('run_id', RUN)):
                for actual in field_values(claim, key):
                    self.assertEqual(actual, expected)
            self.assertIn(json.dumps(ARGV), json.dumps(claim))
        attempt = json.loads((self.output / 'upload_attempt.json').read_text())
        self.assertTrue(field_values(attempt, 'source_sha256'))
        self.assertTrue(field_values(attempt, 'run_id'))
        encoded = json.dumps(attempt, sort_keys=True)
        self.assertIn(json.dumps(self.admitted_bindings, sort_keys=True), encoded)
        self.assertIn(json.dumps(legacy.ENV, sort_keys=True), encoded)

    def assert_report(self, report, status):
        self.assertEqual(set(report), legacy.REPORT_KEYS)
        self.assertEqual(report['schema'], 'motor-fault-upload-result-v1')
        self.assertEqual(report['run_id'], RUN)
        self.assertEqual(report['source_sha256'], SOURCE)
        self.assertEqual(report['status'], status)
        self.assertIn(report['attempts'], (0, 1))
        self.assertEqual(json.loads((self.receipt_dir / 'upload_result.json').read_text()), report)
        self.assertIsInstance(report['postcheck_errors'], list)
        for error in report['postcheck_errors']:
            self.assertEqual(set(error), {'check', 'type', 'message'})
        if status == 'UPLOADED':
            self.assertEqual(report['attempts'], 1)
            self.assertIsNone(report['first_error'])
            self.assertEqual(report['postcheck_errors'], [])
            self.assertEqual(report['subprocess'], legacy.SUCCESS)
        else:
            self.assertEqual(set(report['first_error']), {'type', 'message'})
        self.assert_globals_unchanged()

    def reject_options(self, **kwargs):
        before = copy.deepcopy(self.bindings)
        try:
            report = self.upload(**kwargs)
        except Exception:
            pass
        else:
            self.assertEqual(report['status'], 'FAILED')
            self.assertEqual(report['attempts'], 0)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.output.exists())
        for run in ('run01', 'run02'):
            path = self.legacy_bindings['output'].replace('-run01-', '-' + run + '-')
            self.assertFalse(self.logical(path).exists())
        self.assertEqual(self.bindings, before)
        self.assert_globals_unchanged()

    def fake_popen(self, argv, **kwargs):
        self.assertEqual(argv, ARGV)
        self.assertEqual(kwargs['env'], legacy.ENV)
        self.assertEqual(kwargs['cwd'], '/home/arduino')
        self.assertFalse(kwargs['shell'])
        self.assertTrue(kwargs['start_new_session'])
        self.assertEqual(kwargs['stdin'], subprocess.DEVNULL)
        self.assertIs(kwargs['preexec_fn'], self.subject.limit_upload_files)
        with mock.patch.object(self.support.resource, 'setrlimit') as limit:
            kwargs['preexec_fn']()
        limit.assert_called_once_with(self.support.resource.RLIMIT_FSIZE, (2303728, 2303728))
        self.assert_globals_unchanged()
        self.check_prelaunch_receipts()
        for stream, raw in ((kwargs['stdout'], self.stdout), (kwargs['stderr'], self.stderr)):
            if isinstance(stream, int):
                os.write(stream, raw)
            else:
                stream.write(raw)
        return self.child

    def test_D175_exact_dynamic_profile_receipts_and_untouched_caller(self):
        before = copy.deepcopy(self.bindings)
        observed = json.loads((HERE.parent / 'P7_motor_fault_raw/active_verified.json').read_text())
        self.assertEqual((observed['source_sha256'], observed['build_path']), (SOURCE, BUILD))
        self.assertEqual(len(self.bindings['files']), 17)
        self.assertEqual(len(self.bindings['directories']), 3)
        self.assertEqual(len(self.bindings['absent']), 14)
        for role in set(self.bindings['files']) - {'raw', 'sketch'}:
            self.assertEqual(self.bindings['files'][role], self.legacy_bindings['files'][role])
        self.assertEqual(self.bindings['directories'], self.legacy_bindings['directories'])
        self.assertEqual(self.bindings['absent'][:11], self.legacy_bindings['absent'][:11])
        report = self.upload()
        self.assert_report(report, 'UPLOADED')
        self.assertEqual(self.calls, [(ARGV, 120)])
        self.assertEqual(self.bindings, before)
        self.assertEqual((report['stdout'], report['stderr']),
                         (self.stdout.decode(), self.stderr.decode()))
        self.assertFalse(self.logical(self.legacy_bindings['output']).exists())
        for pin in self.bindings['files'].values():
            self.assertGreaterEqual(sum(path == pin['path'] for path, _ in self.pin_reads), 2)

    def test_D175_run_selector_requires_exact_string_before_ownership(self):
        class DerivedString(str):
            pass
        invalid = ('', 'motor-fault-8f592937', RUN + 'x', RUN + '/', RUN.upper(),
                   RUN.replace('run01', 'run02'), '../' + RUN, RUN + '/../run01',
                   None, True, 1, RUN.encode(), [RUN], {'run_id': RUN}, DerivedString(RUN))
        for run in invalid:
            with self.subTest(run=run):
                self.reject_options(run_id=run)

    def test_D175_schema_source_run_and_output_cannot_mix_profiles(self):
        fields = ('schema', 'source_sha256', 'run_id', 'output')
        for key in fields:
            candidate = copy.deepcopy(self.bindings)
            candidate[key] = self.legacy_bindings[key]
            with self.subTest(field=key):
                self.reject_options(bindings=candidate)
        for run in ('static-fcddbd8e-run01', 'static-fcddbd8e-run02'):
            self.reject_options(run_id=run)
        self.reject_options(bindings=self.legacy_bindings)
        self.reject_options(bindings=None)

    def test_D175_legacy_api_cannot_admit_dynamic_profile(self):
        options = dict(fs_root=self.root, executor=self.execute, clock=self.clock)
        with self.assertRaises(Exception):
            self.subject.upload(self.helper, self.support, bindings=self.bindings, **options)
        with self.assertRaises(TypeError):
            self.subject.upload(self.helper, self.support, run_id=RUN, **options)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.output.exists())
        self.assert_globals_unchanged()

    def test_D175_every_file_role_path_is_fixed(self):
        for role in self.bindings['files']:
            candidate = copy.deepcopy(self.bindings)
            candidate['files'][role]['path'] = '/tmp/alternative-' + role
            with self.subTest(role=role):
                self.reject_options(bindings=candidate)
        for role in ('raw', 'sketch'):
            candidate = copy.deepcopy(self.bindings)
            candidate['files'][role] = copy.deepcopy(self.legacy_bindings['files'][role])
            self.reject_options(bindings=candidate)

    def test_D175_binding_and_file_role_shapes_remain_exact(self):
        mutations = (lambda b: b.update(extra=1), lambda b: b.pop('schema'),
                     lambda b: b['files'].pop('raw'),
                     lambda b: b['files'].update(extra=copy.deepcopy(b['files']['raw'])),
                     lambda b: b['files']['raw'].update(extra=1),
                     lambda b: b.update(output=OUTPUT + '/'))
        for mutate in mutations:
            candidate = copy.deepcopy(self.bindings)
            mutate(candidate)
            self.reject_options(bindings=candidate)

    def test_D175_raw_selector_cannot_be_the_packaged_sibling_or_export(self):
        for path in (BUILD + '/motor_fault.ino.elf-zsk.bin',
                     BUILD.replace('/build', '/artifacts') + '/motor_fault.ino.elf-zsk.bin',
                     BUILD + '/app.ino.bin'):
            candidate = copy.deepcopy(self.bindings)
            candidate['files']['raw']['path'] = path
            self.reject_options(bindings=candidate)

    def test_D175_directory_selection_and_absence_lists_are_closed(self):
        candidate = copy.deepcopy(self.bindings)
        path = next(iter(candidate['directories']))
        candidate['directories']['/tmp/replacement'] = candidate['directories'].pop(path)
        self.reject_options(bindings=candidate)
        candidates = [self.legacy_bindings['absent'], self.bindings['absent'][:-1],
                      self.bindings['absent'] + ['/tmp/additional'],
                      self.bindings['absent'][:-1] + [self.bindings['absent'][0]]]
        for absent in candidates:
            candidate = copy.deepcopy(self.bindings)
            candidate['absent'] = copy.deepcopy(absent)
            self.reject_options(bindings=candidate)

    def test_D175_no_caller_command_environment_or_flags_override(self):
        for key, value in (('argv', ['echo']), ('env', {}), ('environment', {}),
                           ('fqbn', 'arduino:zephyr:unoq:link_mode=static'), ('flags', [])):
            with self.subTest(key=key):
                self.reject_options(**{key: value})

    def test_D175_each_supplied_pin_is_read_and_hashed_before_claim(self):
        legacy.UploadContract.test_each_pin_content_is_checked_before_claim(self)
        self.assert_globals_unchanged()

    def test_D175_pin_extents_and_hashes_are_checked_against_actual_bytes(self):
        for role in ('raw', 'sketch'):
            for key, value in (('bytes', self.bindings['files'][role]['bytes'] + 1),
                               ('sha256', '0' * 64), ('bytes', True), ('sha256', 'A' * 64)):
                candidate = copy.deepcopy(self.bindings)
                candidate['files'][role][key] = value
                with self.subTest(role=role, key=key, value=value):
                    self.reject_options(bindings=candidate)

    def test_D175_every_shared_and_diagnostic_absence_is_checked(self):
        legacy.UploadContract.test_every_forbidden_override_and_dangling_link_rejected(self)

    def test_D175_legacy_sketch_override_is_not_a_diagnostic_override(self):
        for path in self.legacy_bindings['absent'][-3:]:
            self.logical(path).write_bytes(b'legacy-only override')
        self.assert_report(self.upload(), 'UPLOADED')

    def test_D175_caller_mutation_cannot_rewrite_admitted_pins_or_profile(self):
        def mutate():
            self.bindings['files']['raw'].update(path='/tmp/changed', sha256='0' * 64)
            self.bindings['directories'].clear()
            self.bindings['absent'].clear()
            self.bindings.update(source_sha256='0' * 64, run_id='changed', output='/tmp/changed')
        self.after_execute = mutate
        self.assert_report(self.upload(), 'UPLOADED')
        self.check_prelaunch_receipts()

    def test_D175_nested_static_run01_and_run02_keep_dynamic_selection(self):
        results, calls = [], []
        def nested():
            for suffix in ('run01', 'run02'):
                bindings = copy.deepcopy(self.legacy_bindings)
                bindings['run_id'] = 'static-fcddbd8e-' + suffix
                bindings['output'] = bindings['output'].replace('-run01-', '-' + suffix + '-')
                def execute(argv, stdout, stderr, timeout):
                    self.assert_globals_unchanged()
                    self.assertEqual(argv, legacy.ARGV)
                    self.assertEqual(timeout, 120)
                    calls.append(copy.deepcopy(argv))
                    for path in (stdout, stderr):
                        self.local_argument(path).write_bytes(b'')
                    return dict(legacy.SUCCESS)
                before = copy.deepcopy(bindings)
                result = self.subject.upload_loader(self.helper, self.support, fs_root=self.root,
                    executor=execute, clock=self.clock, bindings=bindings, run_id=bindings['run_id'])
                self.assertEqual(bindings, before)
                self.assertEqual(result['schema'], 'static-upload-result-v1')
                self.assertEqual(result['run_id'], bindings['run_id'])
                self.assertEqual(result['source_sha256'], legacy.SOURCE)
                self.assertEqual(result['status'], 'UPLOADED')
                results.append(result)
        self.after_execute = nested
        self.assert_report(self.upload(), 'UPLOADED')
        self.assertEqual(len(results), 2)
        self.assertEqual(calls, [legacy.ARGV, legacy.ARGV])
        self.check_prelaunch_receipts()

    def test_D175_preexisting_owner_is_never_entered_or_modified(self):
        legacy.UploadContract.test_preexisting_output_never_entered_or_modified(self)

    def test_D175_owner_symlink_is_never_entered(self):
        legacy.UploadContract.test_output_symlink_never_entered(self)

    def test_D175_failed_child_preserves_consumed_owner_and_blocks_retry(self):
        legacy.UploadContract.test_consumed_attempt_cannot_be_reused(self)

    def test_D175_failure_keeps_first_error_and_all_independent_finalchecks(self):
        legacy.UploadContract.test_independent_postchecks_preserve_primary(self)
        for logical in self.bindings['directories']:
            self.assertIn(logical, self.directory_reads)
        for logical in self.bindings['absent']:
            self.assertIn(self.logical(logical), self.stat_reads)

    def test_D175_missing_stdout_keeps_stderr_and_failed_outcome(self):
        legacy.UploadContract.test_missing_stream_does_not_hide_other_stream(self)

    def test_D175_output_drift_persists_only_in_original_owned_directory(self):
        legacy.UploadContract.test_output_drift_retains_result_in_original_directory(self)

    def test_D175_claim_persistence_failure_consumes_owner_without_execution(self):
        legacy.UploadContract.test_claim_fsync_failure_consumes_attempt_and_runs_postchecks(self)

    def test_D175_controlled_default_child_uses_fixed_env_cap_and_exclusive_files(self):
        legacy.UploadContract.test_default_process_environment_limits_and_exclusive_modes(self)

    def test_D175_controlled_default_timeout_kills_owned_group_and_reaps(self):
        legacy.UploadContract.test_default_timeout_kills_only_owned_group_and_reaps(self)

    def test_D175_controlled_default_unreaped_timeout_stays_unknown(self):
        legacy.UploadContract.test_default_unreaped_timeout_remains_unknown(self)

    def test_D175_controlled_default_spawn_failure_never_retries(self):
        legacy.UploadContract.test_default_spawn_failure_is_not_retried(self)

    def test_D175_admission_deadline_refuses_before_ownership(self):
        legacy.UploadContract.test_admission_deadline_prevents_claim(self)

    def test_D175_default_child_uses_remaining_total_budget(self):
        legacy.UploadContract.test_default_recomputes_shorter_wait_after_stream_creation(self)

    def test_D175_default_child_cannot_launch_after_total_deadline(self):
        legacy.UploadContract.test_default_rechecks_budget_after_stream_creation(self)

    def test_D175_both_streams_just_below_one_mib_remain_accepted(self):
        fixture.UploadLoaderContract.test_both_streams_just_below_one_mib_remain_accepted(self)

    def test_D175_stdout_exactly_one_mib_is_rejected(self):
        legacy.UploadContract.test_stream_exactly_one_mib_is_rejected(self)

    def test_D175_stderr_exactly_one_mib_is_rejected(self):
        fixture.UploadLoaderContract.test_stderr_exactly_one_mib_is_rejected(self)

    def test_D175_frozen_capture_limit_is_still_one_mib(self):
        fixture.UploadLoaderContract.test_frozen_d153_limit_remains_one_mib(self)

    def test_D175_capture_support_is_not_repurposed(self):
        legacy.UploadContract.test_support_globals_and_capture_are_not_repurposed(self)


def load_tests(loader, suite, pattern):
    return unittest.TestSuite(MotorFaultUpload(name) for name in sorted(MotorFaultUpload.__dict__)
                              if name.startswith('test_'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
