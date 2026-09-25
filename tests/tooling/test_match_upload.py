# Tests D182's MATCH adapter against its contract and frozen uploader interface.
# Protects exact precompiled selection, copied bindings and unchanged ownership.
# Freeze before execution; spies and tiny owned RAM fixtures never run a child.
import copy
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / 'state/analysis/P7_static_startup_raw'
SOURCE = '1234567890abcdef' * 4
BUILD_ID = '234567890abcdef1' * 2
RUN_ID = '34567890abcdef12' * 2
BOOT_ID = '456789ab-cdef-1234-5678-90abcdef1234'
PARENT = '/home/arduino/sumox26_codex_build'
SKETCH = PARENT + '/' + SOURCE + '/app'
RUNROOT = PARENT + '/_app_builds/native-app-v1/' + SOURCE + '/match-immediate/' + BUILD_ID
RAW = RUNROOT + '/build/app.ino.elf'
PACKAGED = RUNROOT + '/build/app.ino.elf-zsk.bin'
EXPORTED = RUNROOT + '/artifacts/app.ino.elf-zsk.bin'
OUTPUT = PARENT + '/match-' + SOURCE[:8] + '-' + RUN_ID + '-upload'
ARGV = ['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload', '--fqbn',
        'arduino:zephyr:unoq:wait_linux_boot=no', '--input-file', RAW, SKETCH]
UPLOADER_SHA = 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DerivedString(str):
    pass


class FalseyCallable:
    def __init__(self, value):
        self.value, self.calls = value, 0

    def __bool__(self):
        return False

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.value


class MatchUploadContract(unittest.TestCase):
    def setUp(self):
        self.uploader = load(FROZEN / 'upload_remote.py', 'd182_frozen_upload')
        self.support = load(FROZEN / 'capture_remote.py', 'd182_frozen_support')
        self.subject = load(ROOT / 'tools/match_upload.py', 'd182_subject')
        self.helper = object()
        self.bindings = self.make_bindings()
        patcher = mock.patch.object(subprocess, 'Popen',
                                    side_effect=AssertionError('Native child forbidden'))
        self.addCleanup(patcher.stop)
        patcher.start()

    def expected_profile(self):
        files = dict(self.uploader.FILE_PATHS)
        files.update(raw=RAW, sketch=PACKAGED, exported=EXPORTED)
        return {'fixed': {'schema': 'fixed-match-upload-v1', 'run_id': RUN_ID,
                          'source_sha256': SOURCE, 'output': OUTPUT},
                'schema_prefix': 'match-upload-', 'files': files,
                'absent': self.uploader.ABSENT[:-3] + tuple(
                    SKETCH + '/sketch.' + ext for ext in ('yaml', 'yml', 'json')),
                'argv': list(ARGV)}

    def make_bindings(self):
        profile = self.expected_profile()
        return {**profile['fixed'], 'boot_id': BOOT_ID, 'uid': 1000,
                'files': {role: {'path': path, 'bytes': 8, 'sha256': 'a' * 64}
                          for role, path in profile['files'].items()},
                'directories': {path: ['fixture'] for path in self.uploader.DIRECTORIES},
                'absent': list(profile['absent'])}

    def profile(self, **kwargs):
        options = dict(source_sha256=SOURCE, build_id=BUILD_ID, run_id=RUN_ID)
        options.update(kwargs)
        return self.subject.match_profile(self.uploader, self.support, **options)

    def upload(self, **kwargs):
        options = dict(bindings=self.bindings, source_sha256=SOURCE,
                       build_id=BUILD_ID, run_id=RUN_ID, clock=lambda: 17.25)
        options.update(kwargs)
        return self.subject.upload_match(self.helper, self.support, self.uploader, **options)

    def instance(self, **kwargs):
        with mock.patch.object(self.uploader, '_upload', side_effect=lambda value: value) as call:
            result = self.upload(**kwargs)
        call.assert_called_once_with(result)
        return result

    def reject(self, **kwargs):
        with mock.patch.object(self.uploader, '_upload') as dispatch:
            with self.assertRaises((ValueError, TypeError)):
                self.upload(**kwargs)
        dispatch.assert_not_called()

    def test_D182_frozen_uploader_identity(self):
        self.assertEqual(hashlib.sha256((FROZEN / 'upload_remote.py').read_bytes()).hexdigest(),
                         UPLOADER_SHA)

    def test_D182_import_and_profile_have_no_filesystem_or_child_effects(self):
        with mock.patch('builtins.open', side_effect=AssertionError('file open')), \
                mock.patch.object(Path, 'open', side_effect=AssertionError('Path open')), \
                mock.patch.object(self.uploader.os, 'open', side_effect=AssertionError('os open')):
            module = load(ROOT / 'tools/match_upload.py', 'd182_import_probe')
            profile = module.match_profile(self.uploader, self.support, SOURCE, BUILD_ID, RUN_ID)
        self.assertEqual(profile, self.expected_profile())

    def test_D182_profile_has_only_contract_fields_and_exact_identity(self):
        profile = self.profile()
        self.assertEqual(set(profile), {'fixed', 'schema_prefix', 'files', 'absent', 'argv'})
        self.assertEqual(profile['fixed'], self.expected_profile()['fixed'])
        self.assertEqual(profile['schema_prefix'], 'match-upload-')

    def test_D182_profile_has_exact_eighteen_paths(self):
        files = self.profile()['files']
        self.assertEqual(len(files), 18)
        self.assertEqual(files, self.expected_profile()['files'])
        self.assertEqual((files['raw'], files['sketch'], files['exported']),
                         (RAW, PACKAGED, EXPORTED))

    def test_D182_exact_upload_command_has_no_compile_or_alternate_flags(self):
        self.assertEqual(self.profile()['argv'], ARGV)

    def test_D182_absence_tuple_preserves_historical_non_sketch_entries(self):
        absent = self.profile()['absent']
        self.assertIs(type(absent), tuple)
        self.assertEqual(absent, self.expected_profile()['absent'])

    def test_D182_profiles_are_independent_without_global_aliases(self):
        first, second = self.profile(), self.profile()
        first['files']['cli'] = '/wrong'
        first['fixed']['source_sha256'] = 'f' * 64
        first['argv'].append('--wrong')
        self.assertEqual(second, self.expected_profile())
        self.assertEqual(self.uploader.FILE_PATHS['cli'], '/usr/bin/arduino-cli')

    def check_bad_identifier(self, name, valid):
        invalid = (None, True, 4, valid.encode(), DerivedString(valid), '', valid[:-1],
                   valid + '0', valid.upper(), 'g' + valid[1:], valid + '\n', '../' + valid)
        for value in invalid:
            with self.subTest(field=name, value=repr(value)):
                with self.assertRaises((ValueError, TypeError)):
                    self.profile(**{name: value})
                self.reject(**{name: value})

    def test_D182_source_requires_exact_lowercase_64hex_string(self):
        self.check_bad_identifier('source_sha256', SOURCE)

    def test_D182_build_requires_exact_lowercase_32hex_string(self):
        self.check_bad_identifier('build_id', BUILD_ID)

    def test_D182_run_requires_exact_lowercase_32hex_string(self):
        self.check_bad_identifier('run_id', RUN_ID)

    def test_D182_no_caller_path_flags_profile_or_mode_options(self):
        for name in ('profile', 'argv', 'flags', 'sketch', 'output', 'startup', 'link_mode'):
            with self.subTest(name=name):
                self.reject(**{name: 'untrusted'})

    def test_D182_unknown_missing_and_non_string_binding_fields_rejected(self):
        for field in self.bindings:
            value = copy.deepcopy(self.bindings)
            del value[field]
            with self.subTest(missing=field):
                self.reject(bindings=value)
        for extra in ('unknown', 7):
            self.reject(bindings={**self.bindings, extra: None})
        for malformed in (None, [], 'bindings'):
            self.reject(bindings=malformed)

    def test_D182_unknown_and_missing_file_roles_rejected(self):
        for role in self.bindings['files']:
            value = copy.deepcopy(self.bindings)
            del value['files'][role]
            with self.subTest(missing=role):
                self.reject(bindings=value)
        value = copy.deepcopy(self.bindings)
        value['files']['extra'] = dict(value['files']['raw'])
        self.reject(bindings=value)

    def test_D182_malformed_file_pins_rejected(self):
        variants = ({'bytes': True}, {'bytes': 0}, {'bytes': -1}, {'bytes': 67108865},
                    {'sha256': 'A' * 64}, {'sha256': 'a' * 63}, {'path': '/elsewhere'},
                    {'extra': None})
        for update in variants:
            with self.subTest(update=update):
                value = copy.deepcopy(self.bindings)
                value['files']['cli'].update(update)
                self.reject(bindings=value)

    def test_D182_identity_directory_and_absence_bindings_are_strict(self):
        variants = ({'schema': 'fixed-static-upload-v1'}, {'run_id': BUILD_ID},
                    {'source_sha256': 'f' * 64}, {'output': OUTPUT + '-other'},
                    {'uid': True}, {'uid': 0}, {'boot_id': BOOT_ID.upper()},
                    {'directories': {}}, {'absent': []},
                    {'absent': tuple(self.bindings['absent'])})
        for update in variants:
            with self.subTest(update=update):
                self.reject(bindings={**self.bindings, **update})

    def test_D182_package_export_byte_count_mismatch_rejected_before_dispatch(self):
        self.bindings['files']['exported']['bytes'] += 1
        self.reject()

    def test_D182_package_export_digest_mismatch_rejected_before_dispatch(self):
        self.bindings['files']['exported']['sha256'] = 'b' * 64
        self.reject()

    def test_D182_raw_elf_may_differ_from_both_identical_packages(self):
        self.bindings['files']['raw'].update(bytes=9, sha256='b' * 64)
        attempt = self.instance()
        self.assertEqual(attempt.input_bindings, self.bindings)

    def test_D182_frozen_checker_runs_before_dispatch_and_caller_copy_is_detached(self):
        original = copy.deepcopy(self.bindings)
        checker = self.uploader._checked_bindings
        order, checked = [], []
        def check(support, bindings, profile):
            order.append('check')
            self.assertIs(support, self.support)
            self.assertEqual(profile, self.expected_profile())
            result = checker(support, bindings, profile)
            checked.append(result)
            return result
        def dispatch(attempt):
            order.append('dispatch')
            self.assertIs(attempt.input_bindings, checked[0])
            self.bindings['files']['raw']['path'] = '/changed-after-admission'
            self.bindings['absent'].clear()
            self.assertEqual(attempt.input_bindings, original)
            return attempt
        with mock.patch.object(self.uploader, '_checked_bindings', side_effect=check), \
                mock.patch.object(self.uploader, '_upload', side_effect=dispatch):
            self.upload()
        self.assertEqual(order, ['check', 'dispatch'])

    def test_D182_falsey_supplied_clock_and_executor_preserved(self):
        clock, executor = FalseyCallable(31), FalseyCallable(None)
        attempt = self.instance(clock=clock, executor=executor)
        self.assertIs(attempt.clock, clock)
        self.assertIs(attempt.executor, executor)
        self.assertEqual((clock.calls, executor.calls), (1, 0))
        self.assertEqual((attempt.started, attempt.latest), (31, 31))

    def test_D182_defaults_use_monotonic_root_and_no_executor(self):
        with mock.patch('time.monotonic', return_value=123.5) as clock:
            attempt = self.instance(clock=None)
        clock.assert_called_once_with()
        self.assertIs(attempt.clock, clock)
        self.assertEqual(attempt.fs_root, Path('/'))
        self.assertIsNone(attempt.executor)

    def test_D182_all_initializer_fields_match_frozen_lifecycle(self):
        root, executor = Path('/owned-fixture'), object()
        with mock.patch.object(self.support, 'utc', return_value='fixed-time'):
            attempt = self.instance(fs_root=root, executor=executor)
        for name, expected in (('helper', self.helper), ('support', self.support),
                               ('fs_root', root), ('executor', executor),
                               ('limit_files', self.uploader.limit_upload_files)):
            self.assertIs(getattr(attempt, name), expected, name)
        self.assertEqual(attempt.run_id, RUN_ID)
        self.assertEqual(attempt.profile, self.expected_profile())
        self.assertEqual(attempt.argv, ARGV)
        self.assertEqual((attempt.started, attempt.latest), (17.25, 17.25))
        self.assertEqual((attempt.root_fd, attempt.output_fd, attempt.claimed,
                          attempt.first_exception, attempt.process_error),
                         (None, None, False, None, None))
        self.assertEqual(attempt.context_failures, [])
        self.assertEqual(attempt.report, {'schema': 'match-upload-result-v1', 'run_id': None,
            'source_sha256': SOURCE, 'status': 'FAILED', 'attempts': 0,
            'started_utc': 'fixed-time', 'finished_utc': None, 'started_monotonic': 17.25,
            'finished_monotonic': None, 'subprocess': None, 'stdout': None,
            'stderr': None, 'first_error': None, 'postcheck_errors': []})

    def test_D182_subclass_inherits_every_lifecycle_method_without_old_constructor(self):
        with mock.patch.object(self.uploader.Upload, '__init__',
                               side_effect=AssertionError('historical constructor')), \
                mock.patch.object(self.uploader, 'selected_profile',
                                  side_effect=AssertionError('historical profile')):
            attempt = self.instance()
        self.assertIsInstance(attempt, self.uploader.Upload)
        self.assertIsNot(type(attempt), self.uploader.Upload)
        for name, method in vars(self.uploader.Upload).items():
            if callable(method) and name != '__init__':
                self.assertIs(getattr(type(attempt), name), method, name)

    def test_D182_uploader_globals_preserve_identity_and_value(self):
        names = tuple(vars(self.uploader))
        objects = {name: getattr(self.uploader, name) for name in names}
        builtin_entries = dict(objects['__builtins__'])
        values = {name: copy.deepcopy(value) for name, value in objects.items()
                  if name != '__builtins__' and
                  type(value) in (dict, list, tuple, str, int, type(None))}
        self.profile()
        self.instance()
        self.assertEqual(tuple(vars(self.uploader)), names)
        for name, value in objects.items():
            self.assertIs(getattr(self.uploader, name), value, name)
        self.assertEqual(set(self.uploader.__builtins__), set(builtin_entries))
        for name, value in builtin_entries.items():
            self.assertIs(self.uploader.__builtins__[name], value, name)
        for name, value in values.items():
            self.assertEqual(getattr(self.uploader, name), value, name)

    def test_D182_inherited_budget_and_file_stream_limits_unchanged(self):
        clock = FalseyCallable(10)
        attempt = self.instance(clock=clock)
        self.assertEqual(attempt.budget(), 180)
        clock.value = 189
        self.assertEqual(attempt.budget(), 1)
        clock.value = 190
        with self.assertRaises(ValueError):
            attempt.budget()
        self.assertEqual(self.uploader.STREAM_LIMIT, 1048576)
        with mock.patch.object(self.support.resource, 'setrlimit') as limit:
            attempt.limit_files()
        limit.assert_called_once_with(self.support.resource.RLIMIT_FSIZE, (2303728, 2303728))

    def test_D182_success_return_is_delegated_exactly_once_without_copy(self):
        result = {'status': 'UPLOADED', 'sentinel': object()}
        with mock.patch.object(self.uploader, '_upload', return_value=result) as dispatch:
            self.assertIs(self.upload(), result)
        dispatch.assert_called_once()

    def test_D182_failed_return_is_not_rewritten_or_retried(self):
        result = {'status': 'FAILED', 'attempts': 1, 'first_error': object()}
        with mock.patch.object(self.uploader, '_upload', return_value=result) as dispatch:
            self.assertIs(self.upload(), result)
        dispatch.assert_called_once()

    def test_D182_preclaim_exception_identity_propagates_without_retry(self):
        error = RuntimeError('preclaim refusal')
        with mock.patch.object(self.uploader, '_upload', side_effect=error) as dispatch:
            with self.assertRaises(RuntimeError) as caught:
                self.upload()
        self.assertIs(caught.exception, error)
        dispatch.assert_called_once()

    def test_D182_no_dispatch_through_historical_public_wrappers(self):
        with mock.patch.object(self.uploader, 'upload', side_effect=AssertionError('old upload')), \
                mock.patch.object(self.uploader, 'upload_loader',
                                  side_effect=AssertionError('old loader')):
            self.instance()

    def test_D182_invalid_clock_fails_before_lifecycle_dispatch(self):
        for value in (True, float('nan'), float('inf'), '17', None):
            with self.subTest(value=value):
                self.reject(clock=lambda value=value: value)


class MatchInheritedLifecycle(unittest.TestCase):
    def setUp(self):
        legacy = load(FROZEN / 'test_upload_remote.py', 'd182_legacy_fixture')
        self.fixture = legacy.UploadContract(methodName='runTest')
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.setUp()
        self.subject = load(ROOT / 'tools/match_upload.py', 'd182_lifecycle_subject')
        f = self.fixture
        self.bindings = copy.deepcopy(f.bindings)
        self.bindings.update(schema='fixed-match-upload-v1', run_id=RUN_ID,
                             source_sha256=SOURCE, output=OUTPUT)
        for role, path in (('raw', RAW), ('sketch', PACKAGED), ('exported', EXPORTED)):
            raw = b'raw ELF' if role == 'raw' else b'identical packaged ELF'
            self.bindings['files'][role] = {'path': path, 'bytes': len(raw),
                                             'sha256': hashlib.sha256(raw).hexdigest()}
            target = f.logical(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        self.bindings['absent'] = self.bindings['absent'][:-3] + [
            SKETCH + '/sketch.' + ext for ext in ('yaml', 'yml', 'json')]
        f.logical(SKETCH).mkdir(parents=True)
        self.calls, self.after_child = [], None
        self.outcome = {'returncode': 0, 'timed_out': False, 'reaped': True}

    def execute(self, argv, stdout, stderr, timeout):
        self.calls.append((list(argv), timeout))
        self.assertEqual(argv, ARGV)
        self.assertEqual(timeout, 120)
        stdout.write_bytes(b'synthetic upload\n')
        stderr.write_bytes(b'')
        if self.after_child is not None:
            self.after_child()
        return dict(self.outcome)

    def upload(self):
        f = self.fixture
        return self.subject.upload_match(f.helper, f.support, f.subject,
            bindings=self.bindings, source_sha256=SOURCE, build_id=BUILD_ID, run_id=RUN_ID,
            fs_root=f.root, executor=self.execute, clock=f.clock)

    def test_D182_complete_lifecycle_checks_exported_file_and_match_receipt_schemas(self):
        before = copy.deepcopy(self.bindings)
        report = self.upload()
        self.assertEqual((report['status'], report['attempts']), ('UPLOADED', 1))
        self.assertEqual((report['schema'], report['run_id'], report['source_sha256']),
                         ('match-upload-result-v1', RUN_ID, SOURCE))
        self.assertEqual(self.bindings, before)
        self.assertEqual(self.calls, [(ARGV, 120)])
        self.assertGreaterEqual(sum(path == EXPORTED for path, _ in self.fixture.pin_reads), 2)
        import json
        for kind in ('attempt', 'command', 'result'):
            value = json.loads(self.fixture.logical(OUTPUT + '/upload_' + kind + '.json').read_text())
            self.assertEqual(value['schema'], 'match-upload-' + kind + '-v1')
            self.assertEqual((value['run_id'], value['source_sha256']), (RUN_ID, SOURCE))

    def test_D182_actual_export_mismatch_refuses_before_claim_and_child(self):
        self.fixture.logical(EXPORTED).write_bytes(b'wrong packaged content')
        with self.assertRaises(ValueError):
            self.upload()
        self.assertEqual(self.calls, [])
        self.assertFalse(self.fixture.logical(OUTPUT).exists())

    def test_D182_postchild_export_mutation_retained_as_failed_postcheck(self):
        self.after_child = lambda: self.fixture.logical(EXPORTED).write_bytes(b'changed')
        report = self.upload()
        self.assertEqual((report['status'], report['attempts']), ('FAILED', 1))
        self.assertIn('exported', [value['check'] for value in report['postcheck_errors']])
        self.assertEqual(self.calls, [(ARGV, 120)])
        self.assertTrue(self.fixture.logical(OUTPUT + '/upload_result.json').is_file())

    def test_D182_child_failure_keeps_one_attempt_and_all_streams(self):
        self.outcome['returncode'] = 43
        report = self.upload()
        self.assertEqual((report['status'], report['attempts']), ('FAILED', 1))
        self.assertEqual(report['subprocess'], self.outcome)
        self.assertEqual((report['stdout'], report['stderr']), ('synthetic upload\n', ''))
        self.assertEqual(self.calls, [(ARGV, 120)])
        self.assertTrue(self.fixture.logical(OUTPUT + '/upload_attempt.json').is_file())

    def test_D182_consumed_output_is_not_reused_or_cleaned_up(self):
        self.assertEqual(self.upload()['status'], 'UPLOADED')
        output = self.fixture.logical(OUTPUT)
        before = {path.name: path.read_bytes() for path in output.iterdir()}
        with self.assertRaises(FileExistsError):
            self.upload()
        self.assertEqual(self.calls, [(ARGV, 120)])
        self.assertEqual({path.name: path.read_bytes() for path in output.iterdir()}, before)


if __name__ == '__main__':
    unittest.main()
