# Tests the D154 upload contract without reading its implementation during authorship.
# Protects one-shot ownership, fixed selection and honest process/finalization evidence.
# Linux fixtures use tiny files and controlled processes; freeze before execution.
from contextlib import contextmanager
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = 'fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2'
PARENT = '/home/arduino/sumox26_codex_build'
BUILD = (PARENT + '/_app_builds/static-app-probe-v1/' + SOURCE +
         '/bench-default/f0220228320c4b2aa20c3e5e8264c813/build')
ARGV = ['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload', '--fqbn',
        'arduino:zephyr:unoq:link_mode=static', '--input-file', BUILD + '/app.ino.bin',
        PARENT + '/' + SOURCE + '/app']
ENV = {'HOME': '/home/arduino', 'USER': 'arduino', 'LOGNAME': 'arduino',
       'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C',
       'ARDUINO_DIRECTORIES_DATA': '/home/arduino/.arduino15',
       'ARDUINO_DIRECTORIES_USER': '/home/arduino/Arduino',
       'ARDUINO_UPDATER_ENABLE_NOTIFICATION': 'false'}
SUCCESS = {'returncode': 0, 'timed_out': False, 'reaped': True}
REPORT_KEYS = {'schema', 'run_id', 'source_sha256', 'status', 'attempts',
               'started_utc', 'finished_utc', 'started_monotonic', 'finished_monotonic',
               'subprocess', 'stdout', 'stderr', 'first_error', 'postcheck_errors'}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Clock:
    def __init__(self):
        self.value, self.error = 100.0, None

    def __call__(self):
        if self.error:
            raise self.error
        return self.value


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux descriptors required')
class UploadContract(unittest.TestCase):
    def setUp(self):
        self.patch(subprocess, 'Popen', side_effect=AssertionError('Native processes forbidden'))
        self.patch(os, 'killpg', side_effect=AssertionError('Native group signals forbidden'))
        self.temp = tempfile.TemporaryDirectory(prefix='sumox_upload_contract_', dir='/dev/shm')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.subject = load(HERE / 'upload_remote.py', 'upload_contract_subject')
        self.helper = load(ROOT / 'state/analysis/P7_static_link_probe_raw/static_remote.py',
                           'upload_contract_descriptor_helper')
        self.support = load(HERE / 'capture_remote.py', 'upload_contract_frozen_support')
        self.bindings = json.loads((HERE / 'upload_bindings.json').read_text())
        self.clock = Clock()
        self.calls, self.pin_reads, self.directory_reads, self.stat_reads = [], [], [], []
        self.stdout, self.stderr = b'upload complete\n', b'normal diagnostic\n'
        self.outcome, self.execute_error, self.after_execute = dict(SUCCESS), None, None
        self.receipt_dir = None
        self.make_files()
        self.install_helper_seams()
        self.install_null_fixture()
        self.subject.BINDINGS = copy.deepcopy(self.bindings)

    def patch(self, target, name, **kwargs):
        patcher = mock.patch.object(target, name, **kwargs)
        result = patcher.start()
        self.addCleanup(patcher.stop)
        return result

    def logical(self, path):
        return self.root / str(path).lstrip('/')

    def make_files(self):
        self.payloads = {}
        for role, pin in self.bindings['files'].items():
            raw = ('tiny fixed input ' + role).encode()
            self.payloads[role] = raw
            pin.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
            target = self.logical(pin['path'])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        for path, names in self.bindings['directories'].items():
            for name in names:
                (self.logical(path) / name).mkdir(parents=True, exist_ok=True)
        for path in ('/proc', '/dev', '/tmp', ARGV[-1]):
            self.logical(path).mkdir(parents=True, exist_ok=True)
        self.output = self.logical(self.bindings['output'])
        self.receipt_dir = self.output
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.logical('/dev/null').write_bytes(b'')

    def install_helper_seams(self):
        self.identity_value = {'user': 'arduino', 'uid': 1000, 'gid': 1000,
            'home': '/home/arduino', 'sysname': 'Linux', 'release': 'synthetic',
            'machine': 'aarch64', 'boot_id': self.bindings['boot_id'],
            'python': list(sys.version_info[:3])}
        self.helper.identity = lambda fd: copy.deepcopy(self.identity_value)
        def directory_info(info, logical):
            if not stat.S_ISDIR(info.st_mode):
                raise ValueError('not a directory: ' + logical)
            return self.helper.directory_id(info)
        self.helper.directory_info = directory_info
        self.real_read = self.helper.logical_read
        self.helper.logical_read = self.tracked_read
        self.real_directory = self.helper.directory
        self.helper.directory = self.tracked_directory

    def install_null_fixture(self):
        self.real_stat, self.real_lstat, self.real_fstat = os.stat, os.lstat, os.fstat
        info = self.real_stat(self.logical('/dev/null'))
        self.null_identity = (info.st_dev, info.st_ino)
        self.null_mode, self.null_device = stat.S_IFCHR | 0o600, os.makedev(1, 3)
        self.patch(os, 'stat', side_effect=self.tracked_stat)
        self.patch(os, 'lstat', side_effect=lambda *a, **k: self.device_info(self.real_lstat(*a, **k)))
        self.patch(os, 'fstat', side_effect=lambda *a, **k: self.device_info(self.real_fstat(*a, **k)))

    def device_info(self, info):
        if (info.st_dev, info.st_ino) != self.null_identity:
            return info
        fields = {name: getattr(info, name) for name in dir(info) if name.startswith('st_')}
        return SimpleNamespace(**dict(fields, st_mode=self.null_mode, st_rdev=self.null_device))

    def actual_path(self, path, dir_fd=None):
        if isinstance(path, int):
            return Path(os.readlink('/proc/self/fd/' + str(path)))
        if dir_fd is not None:
            return Path(os.readlink('/proc/self/fd/' + str(dir_fd))) / os.fsdecode(path)
        return Path(os.fsdecode(path))

    def tracked_stat(self, path, *args, **kwargs):
        self.stat_reads.append(self.actual_path(path, kwargs.get('dir_fd')))
        return self.device_info(self.real_stat(path, *args, **kwargs))

    def tracked_read(self, fd, logical, limit, proc=False):
        self.pin_reads.append((logical, limit))
        return self.real_read(fd, logical, limit, proc)

    @contextmanager
    def tracked_directory(self, fd, logical):
        self.directory_reads.append(logical)
        with self.real_directory(fd, logical) as result:
            yield result

    def local_argument(self, path):
        candidate = Path(path)
        return candidate if candidate.is_relative_to(self.root) else self.logical(candidate)

    def verify_launch(self, argv, stdout_path, stderr_path, timeout):
        self.assertEqual(argv, ARGV)
        self.assertEqual(len(self.calls), 0, 'No retry or second command is permitted')
        self.assertEqual(self.local_argument(stdout_path), self.output / 'upload.stdout')
        self.assertEqual(self.local_argument(stderr_path), self.output / 'upload.stderr')
        self.assertEqual(timeout, min(120, 280 - self.clock.value))
        for name in ('upload_attempt.json', 'upload_command.json'):
            self.assertTrue((self.output / name).is_file())
        claim = json.loads((self.output / 'upload_attempt.json').read_text())
        text = json.dumps(claim)
        for value in (self.bindings['boot_id'], SOURCE, self.bindings['run_id']):
            self.assertIn(value, text)
        self.assertIn(json.dumps(ARGV), text)
        self.calls.append((copy.deepcopy(argv), timeout))

    def execute(self, argv, stdout_path, stderr_path, timeout):
        self.verify_launch(argv, stdout_path, stderr_path, timeout)
        for path, raw in ((stdout_path, self.stdout), (stderr_path, self.stderr)):
            if raw is not None:
                self.local_argument(path).write_bytes(raw)
        if self.after_execute:
            self.after_execute()
        if self.execute_error:
            raise self.execute_error
        return copy.deepcopy(self.outcome)

    def upload(self, **kwargs):
        options = dict(fs_root=self.root, executor=self.execute, clock=self.clock)
        options.update(kwargs)
        return self.subject.upload(self.helper, self.support, **options)

    def assert_report(self, report, status):
        self.assertEqual(set(report), REPORT_KEYS)
        self.assertEqual(report['schema'], 'static-upload-result-v1')
        self.assertEqual(report['status'], status)
        self.assertEqual(report['run_id'], self.bindings['run_id'])
        self.assertEqual(report['source_sha256'], SOURCE)
        self.assertIn(report['attempts'], (0, 1))
        self.assertEqual(json.loads((self.receipt_dir / 'upload_result.json').read_text()), report)
        self.assertIsInstance(report['postcheck_errors'], list)
        for error in report['postcheck_errors']:
            self.assertEqual(set(error), {'check', 'type', 'message'})
        if status == 'UPLOADED':
            self.assertEqual(report['attempts'], 1)
            self.assertIsNone(report['first_error'])
            self.assertEqual(report['postcheck_errors'], [])
            self.assertEqual(report['subprocess'], SUCCESS)
        else:
            self.assertEqual(set(report['first_error']), {'type', 'message'})

    def rejected(self):
        try:
            report = self.upload()
        except Exception:
            pass
        else:
            self.assertEqual(report['status'], 'FAILED')
            self.assertEqual(report['attempts'], 0)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.output.exists())

    def failed(self):
        report = self.upload()
        self.assert_report(report, 'FAILED')
        self.assertEqual(len(self.calls), 1)
        return report

    def process(self, comm, pid='501'):
        path = self.logical('/proc/' + pid)
        path.mkdir()
        (path / 'comm').write_text(comm + '\n')
        return path

    def test_success_exact_command_receipt_and_nonempty_diagnostics(self):
        report = self.upload()
        self.assert_report(report, 'UPLOADED')
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(report['stdout'], self.stdout.decode())
        self.assertEqual(report['stderr'], self.stderr.decode())
        claim = json.loads((self.output / 'upload_attempt.json').read_text())
        self.assertIn(json.dumps(self.bindings, sort_keys=True), json.dumps(claim, sort_keys=True))
        self.assertIn(json.dumps(ENV, sort_keys=True), json.dumps(claim, sort_keys=True))

    def test_exact_roles_and_fixed_paths_are_validated(self):
        original = copy.deepcopy(self.bindings)
        for role in original['files']:
            with self.subTest(role=role):
                modified = copy.deepcopy(original)
                modified['files'][role]['path'] = '/tmp/alternative-' + role
                self.subject.BINDINGS = modified
                self.rejected()
        for mutate in (lambda b: b.update(extra=1), lambda b: b.pop('schema'),
                       lambda b: b['files'].pop('cli'),
                       lambda b: b.update(files={**b['files'], 'extra': b['files']['cli']})):
            modified = copy.deepcopy(original)
            mutate(modified)
            self.subject.BINDINGS = modified
            self.rejected()

    def test_scalar_types_hashes_sizes_and_fixed_output(self):
        changes = [('uid', True), ('uid', 0), ('schema', 'wrong'), ('run_id', 'other'),
                   ('source_sha256', 'a' * 64), ('boot_id', 'bad'),
                   ('output', PARENT + '/other'), ('output', self.bindings['output'] + '/')]
        for name, value in changes:
            with self.subTest(name=name, value=value):
                modified = copy.deepcopy(self.bindings)
                modified[name] = value
                self.subject.BINDINGS = modified
                self.rejected()
        for name, value in (('bytes', True), ('bytes', 0), ('bytes', 67108865),
                            ('sha256', 'A' * 64), ('sha256', 1), ('path', '/tmp/../x')):
            modified = copy.deepcopy(self.bindings)
            modified['files']['cli'][name] = value
            self.subject.BINDINGS = modified
            self.rejected()

    def test_directory_and_absence_binding_shapes(self):
        directory = next(iter(self.bindings['directories']))
        for names in ([], ['..'], ['x/y'], ['x', 'x'], 'arduino', ['v' + str(i) for i in range(65)]):
            modified = copy.deepcopy(self.bindings)
            modified['directories'][directory] = names
            self.subject.BINDINGS = modified
            self.rejected()
        for paths in (self.bindings['absent'][:-1], self.bindings['absent'] + ['/tmp/other'],
                      self.bindings['absent'][:-1] + [self.bindings['absent'][0]]):
            modified = copy.deepcopy(self.bindings)
            modified['absent'] = paths
            self.subject.BINDINGS = modified
            self.rejected()

    def test_non_python_b_rejected_before_mutation(self):
        flags = mock.Mock(wraps=sys.flags)
        flags.dont_write_bytecode = 0
        with mock.patch.object(sys, 'flags', flags), mock.patch.object(sys, 'dont_write_bytecode', False):
            self.rejected()

    def test_identity_mismatch_rejected(self):
        original = dict(self.identity_value)
        for name, value in (('uid', True), ('uid', 0), ('user', 'root'), ('home', '/tmp'),
                            ('machine', 'x86_64'), ('sysname', 'Windows'),
                            ('boot_id', '00000000-0000-0000-0000-000000000000')):
            self.identity_value = dict(original, **{name: value})
            self.rejected()

    def test_each_pin_content_is_checked_before_claim(self):
        for role, pin in self.bindings['files'].items():
            with self.subTest(role=role):
                path = self.logical(pin['path'])
                path.write_bytes(b'x' * len(self.payloads[role]))
                self.rejected()
                path.write_bytes(self.payloads[role])

    def test_symlink_and_nonregular_pin_rejected(self):
        path = self.logical(self.bindings['files']['cli']['path'])
        backup = path.with_name('original-cli')
        path.rename(backup)
        path.symlink_to(backup)
        self.rejected()
        path.unlink()
        os.mkfifo(path)
        self.rejected()

    def test_extra_version_and_non_directory_entries_rejected(self):
        for logical in self.bindings['directories']:
            path = self.logical(logical) / 'unreviewed-version'
            path.mkdir()
            self.rejected()
            path.rmdir()
        path = self.logical('/home/arduino/.arduino15/packages/builtin')
        path.rmdir()
        path.write_bytes(b'not a directory')
        self.rejected()
        path.unlink()
        path.symlink_to(self.logical('/tmp'), target_is_directory=True)
        self.rejected()

    def test_every_forbidden_override_and_dangling_link_rejected(self):
        for logical in self.bindings['absent']:
            with self.subTest(path=logical):
                path = self.logical(logical)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'override')
                self.rejected()
                path.unlink()
                path.symlink_to(self.logical('/nonexistent'))
                self.rejected()
                path.unlink()

    def test_missing_absence_ancestors_are_allowed_but_symlink_ancestors_are_not(self):
        path = self.logical('/home/arduino/target')
        self.assertFalse(path.exists())
        path.symlink_to(self.logical('/tmp'), target_is_directory=True)
        self.rejected()

    def test_permission_error_does_not_count_as_absence(self):
        target = self.logical(self.bindings['absent'][0])
        real = os.stat
        def denied(path, *args, **kwargs):
            if self.actual_path(path, kwargs.get('dir_fd')) == target:
                raise PermissionError('denied absence inspection')
            return real(path, *args, **kwargs)
        with mock.patch.object(os, 'stat', side_effect=denied):
            self.rejected()

    def test_null_device_type_number_and_symlink_checked(self):
        self.null_mode = stat.S_IFREG | 0o600
        self.rejected()
        self.null_mode, self.null_device = stat.S_IFCHR | 0o600, os.makedev(1, 5)
        self.rejected()
        self.null_device = os.makedev(1, 3)
        path = self.logical('/dev/null')
        original = self.logical('/dev/original-null')
        path.rename(original)
        path.symlink_to(original)
        self.rejected()

    def test_exact_conflicting_process_names(self):
        for name in ('openocd', 'remoteocd', 'arduino-cli'):
            path = self.process(name)
            self.rejected()
            (path / 'comm').unlink()
            path.rmdir()
        self.process('arduino-cli-helper')
        self.assert_report(self.upload(), 'UPLOADED')

    def test_missing_comm_with_live_pid_rejected(self):
        self.logical('/proc/501').mkdir()
        self.rejected()

    def test_disappeared_pid_is_allowed(self):
        path = self.process('other')
        real = self.helper.logical_read
        def vanished(fd, logical, limit, proc=False):
            if logical == '/proc/501/comm':
                (path / 'comm').unlink()
                path.rmdir()
                raise FileNotFoundError('pid vanished')
            return real(fd, logical, limit, proc)
        self.helper.logical_read = vanished
        self.assert_report(self.upload(), 'UPLOADED')

    def test_process_enumeration_is_bounded(self):
        for number in range(4097):
            self.logical('/proc/' + str(number)).mkdir()
        self.rejected()

    def test_tmp_remoteocd_preexisting_rejected(self):
        path = self.logical('/tmp/remoteocd')
        path.symlink_to(self.logical('/nonexistent'))
        self.rejected()

    def test_tmp_remoteocd_created_by_upload_is_allowed(self):
        self.after_execute = lambda: self.logical('/tmp/remoteocd').mkdir()
        self.assert_report(self.upload(), 'UPLOADED')

    def test_preexisting_output_never_entered_or_modified(self):
        self.output.mkdir()
        marker = self.output / 'keep'
        marker.write_bytes(b'original')
        before = marker.stat()
        with self.assertRaises(Exception):
            self.upload()
        self.assertEqual(self.calls, [])
        self.assertEqual(list(self.output.iterdir()), [marker])
        self.assertEqual(marker.read_bytes(), b'original')
        self.assertEqual(marker.stat().st_mtime_ns, before.st_mtime_ns)

    def test_output_symlink_never_entered(self):
        target = self.logical('/tmp/untouched')
        target.mkdir()
        self.output.symlink_to(target, target_is_directory=True)
        with self.assertRaises(Exception):
            self.upload()
        self.assertEqual(list(target.iterdir()), [])
        self.assertEqual(self.calls, [])

    def test_consumed_attempt_cannot_be_reused(self):
        self.outcome['returncode'] = 8
        self.failed()
        before = {path.name: path.read_bytes() for path in self.output.iterdir()}
        with self.assertRaises(Exception):
            self.upload()
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.output.iterdir()})

    def test_injected_exception_preserves_first_error(self):
        self.execute_error = RuntimeError('primary upload failure')
        report = self.failed()
        self.assertEqual(report['first_error'], {'type': 'RuntimeError', 'message': 'primary upload failure'})
        self.assertIsNone(report['subprocess'])

    def test_nonzero_outcome_preserved(self):
        self.outcome['returncode'] = 19
        self.assertEqual(self.failed()['subprocess'], self.outcome)

    def test_timeout_outcome_preserved(self):
        self.outcome.update(returncode=-9, timed_out=True)
        self.assertEqual(self.failed()['subprocess'], self.outcome)

    def test_unreaped_outcome_preserved(self):
        self.outcome.update(returncode=None, reaped=False)
        self.assertEqual(self.failed()['subprocess'], self.outcome)

    def test_malformed_return_is_not_presented_as_an_outcome(self):
        self.outcome = {'returncode': True, 'timed_out': False, 'reaped': True}
        self.assertIsNone(self.failed()['subprocess'])

    def test_extra_outcome_key_rejected(self):
        self.outcome['extra'] = 1
        self.assertIsNone(self.failed()['subprocess'])

    def test_nonboolean_outcome_flags_rejected(self):
        self.outcome['reaped'] = 1
        self.assertIsNone(self.failed()['subprocess'])

    def test_nonmapping_outcome_rejected(self):
        self.outcome = None
        self.assertIsNone(self.failed()['subprocess'])

    def test_missing_stream_does_not_hide_other_stream(self):
        self.stdout = None
        report = self.failed()
        self.assertIsNone(report['stdout'])
        self.assertEqual(report['stderr'], self.stderr.decode())

    def test_symlink_stream_rejected(self):
        def substitute():
            path = self.output / 'upload.stdout'
            path.unlink()
            path.symlink_to(self.logical(self.bindings['files']['cli']['path']))
        self.after_execute = substitute
        self.failed()

    def test_nonregular_stream_rejected_without_blocking(self):
        def substitute():
            path = self.output / 'upload.stderr'
            path.unlink()
            os.mkfifo(path)
        self.after_execute = substitute
        self.failed()

    def test_stream_exactly_one_mib_is_rejected(self):
        self.stdout = b'x' * 1048576
        self.failed()

    def test_invalid_utf8_stream_uses_replacement(self):
        self.stdout = b'\xffdone\n'
        report = self.upload()
        self.assert_report(report, 'UPLOADED')
        self.assertEqual(report['stdout'], '\ufffddone\n')

    def test_independent_postchecks_preserve_primary(self):
        def change():
            self.pin_reads.clear()
            self.stat_reads.clear()
            self.directory_reads.clear()
            for pin in self.bindings['files'].values():
                self.logical(pin['path']).write_bytes(b'changed')
            for logical in self.bindings['directories']:
                (self.logical(logical) / 'unexpected').mkdir()
            for logical in self.bindings['absent']:
                target = self.logical(logical)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(b'override')
            self.identity_value['boot_id'] = 'different'
            self.null_mode = stat.S_IFREG | 0o600
            self.process('openocd')
        self.after_execute, self.execute_error = change, RuntimeError('first process failure')
        report = self.failed()
        self.assertEqual(report['first_error']['message'], 'first process failure')
        observed = {path for path, limit in self.pin_reads}
        self.assertTrue({pin['path'] for pin in self.bindings['files'].values()} <= observed)
        self.assertGreaterEqual(len(report['postcheck_errors']), 37)

    def test_output_drift_retains_result_in_original_directory(self):
        def change():
            self.receipt_dir = self.output.with_name('retained-upload-attempt')
            self.output.rename(self.receipt_dir)
            self.output.mkdir()
        self.after_execute = change
        self.failed()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_parent_drift_does_not_write_replacement_parent(self):
        def change():
            old_parent = self.output.parent.with_name('retained-build-parent')
            self.output.parent.rename(old_parent)
            self.output.parent.mkdir()
            self.receipt_dir = old_parent / self.output.name
        self.after_execute = change
        self.failed()
        self.assertEqual(list(self.output.parent.iterdir()), [])

    def test_admission_deadline_prevents_claim(self):
        real = self.helper.logical_read
        def delayed(fd, logical, limit, proc=False):
            result = real(fd, logical, limit, proc)
            self.clock.value = 280.0
            return result
        self.helper.logical_read = delayed
        self.rejected()

    def test_remaining_budget_limits_injected_wait(self):
        real = self.helper.logical_read
        def delayed(fd, logical, limit, proc=False):
            result = real(fd, logical, limit, proc)
            self.clock.value = 200.0
            return result
        self.helper.logical_read = delayed
        self.assert_report(self.upload(), 'UPLOADED')
        self.assertEqual(self.calls[0][1], 80.0)

    def test_post_command_clock_failure_retains_consumed_receipt(self):
        real = os.fsync
        def failed_clock(fd):
            result = real(fd)
            if self.actual_path(fd).name == 'upload_command.json':
                self.clock.error = RuntimeError('clock broke after plan')
            return result
        with mock.patch.object(os, 'fsync', side_effect=failed_clock):
            report = self.upload()
        self.assert_report(report, 'FAILED')
        self.assertEqual(self.calls, [])
        self.assertEqual(report['first_error']['message'], 'clock broke after plan')
        self.assertEqual(report['finished_monotonic'], 100.0)

    def test_clock_error_does_not_replace_executor_error(self):
        self.execute_error = RuntimeError('primary upload failure')
        self.after_execute = lambda: setattr(self.clock, 'error', ValueError('clock failed'))
        report = self.failed()
        self.assertEqual(report['first_error']['message'], 'primary upload failure')
        self.assertEqual(report['finished_monotonic'], 100.0)
        self.assertIn('clock failed', json.dumps(report['postcheck_errors']))

    def test_nonfinite_and_backward_clock_rejected(self):
        for value in (float('nan'), float('inf'), True):
            self.clock.value = value
            self.rejected()
        self.clock.value = 100.0
        real = self.helper.logical_read
        def backwards(fd, logical, limit, proc=False):
            result = real(fd, logical, limit, proc)
            self.clock.value = 99.0
            return result
        self.helper.logical_read = backwards
        self.rejected()

    def test_final_receipt_persistence_failure_raises(self):
        real = os.open
        def denied(path, *args, **kwargs):
            if Path(os.fsdecode(path)).name == 'upload_result.json':
                raise OSError('result persistence failed')
            return real(path, *args, **kwargs)
        with mock.patch.object(os, 'open', side_effect=denied):
            with self.assertRaisesRegex(OSError, 'result persistence failed'):
                self.upload()
        self.assertEqual(len(self.calls), 1)

    def test_claim_fsync_failure_consumes_attempt_and_runs_postchecks(self):
        real, failed = os.fsync, []
        def interrupted(fd):
            if self.actual_path(fd).name == 'upload_attempt.json' and not failed:
                failed.append(True)
                raise OSError('claim fsync failure')
            return real(fd)
        with mock.patch.object(os, 'fsync', side_effect=interrupted):
            report = self.upload()
        self.assert_report(report, 'FAILED')
        self.assertEqual(self.calls, [])
        self.assertEqual(report['first_error']['message'], 'claim fsync failure')
        for pin in self.bindings['files'].values():
            self.assertGreaterEqual(sum(path == pin['path'] for path, limit in self.pin_reads), 2)
        with self.assertRaises(Exception):
            self.upload()
        self.assertEqual(self.calls, [])

    def test_command_fsync_failure_prevents_executor(self):
        real = os.fsync
        def interrupted(fd):
            if self.actual_path(fd).name == 'upload_command.json':
                raise OSError('command fsync failure')
            return real(fd)
        with mock.patch.object(os, 'fsync', side_effect=interrupted):
            report = self.upload()
        self.assert_report(report, 'FAILED')
        self.assertEqual(self.calls, [])
        self.assertEqual(report['first_error']['message'], 'command fsync failure')

    def fake_popen(self, argv, **kwargs):
        self.assertEqual(argv, ARGV)
        self.assertEqual(kwargs['env'], ENV)
        self.assertEqual(kwargs['cwd'], '/home/arduino')
        self.assertFalse(kwargs['shell'])
        self.assertTrue(kwargs['start_new_session'])
        self.assertEqual(kwargs['stdin'], subprocess.DEVNULL)
        self.assertIs(kwargs['preexec_fn'], self.support.limit_child_output)
        with mock.patch.object(self.support.resource, 'setrlimit') as limit:
            kwargs['preexec_fn']()
            limit.assert_called_once_with(self.support.resource.RLIMIT_FSIZE, (1048576, 1048576))
        self.assertTrue((self.output / 'upload_attempt.json').exists())
        self.assertTrue((self.output / 'upload_command.json').exists())
        for stream, raw in ((kwargs['stdout'], self.stdout), (kwargs['stderr'], self.stderr)):
            if isinstance(stream, int):
                os.write(stream, raw)
            else:
                stream.write(raw)
        return self.child

    def default_run(self, wait_values=None, kill_error=None):
        self.child = mock.Mock(pid=45671)
        self.child.wait.side_effect = wait_values or [0]
        with mock.patch.object(subprocess, 'Popen', side_effect=self.fake_popen) as spawn:
            with mock.patch.object(os, 'killpg', side_effect=kill_error) as kill:
                report = self.upload(executor=None)
        spawn.assert_called_once()
        return report, kill

    def test_default_process_environment_limits_and_exclusive_modes(self):
        real, observed = os.open, []
        def traced(path, flags, *args, **kwargs):
            if Path(os.fsdecode(path)).name.startswith('upload') and kwargs.get('dir_fd') is not None:
                observed.append((Path(os.fsdecode(path)).name, flags))
            return real(path, flags, *args, **kwargs)
        with mock.patch.object(os, 'open', side_effect=traced):
            with mock.patch.dict(os.environ, {'ARDUINO_BOGUS': 'forbidden', 'PYTHONPATH': 'forbidden'}):
                report, kill = self.default_run()
        self.assert_report(report, 'UPLOADED')
        kill.assert_not_called()
        self.child.wait.assert_called_once_with(timeout=120)
        created = {name for name, flags in observed if flags & os.O_CREAT}
        self.assertTrue({'upload_attempt.json', 'upload_command.json', 'upload_result.json',
                         'upload.stdout', 'upload.stderr'} <= created)
        for name, flags in observed:
            if flags & os.O_CREAT:
                self.assertTrue(flags & os.O_EXCL and flags & os.O_NOFOLLOW)
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o700)
        for path in self.output.iterdir():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_default_timeout_kills_only_owned_group_and_reaps(self):
        report, kill = self.default_run([subprocess.TimeoutExpired(ARGV, 120), -9])
        self.assert_report(report, 'FAILED')
        self.assertEqual(report['subprocess'], {'returncode': -9, 'timed_out': True, 'reaped': True})
        kill.assert_called_once_with(45671, signal.SIGKILL)
        self.assertEqual(self.child.wait.call_args_list, [mock.call(timeout=120), mock.call(timeout=5)])

    def test_default_unreaped_timeout_remains_unknown(self):
        report, kill = self.default_run([subprocess.TimeoutExpired(ARGV, 120),
                                         subprocess.TimeoutExpired(ARGV, 5)])
        self.assert_report(report, 'FAILED')
        self.assertEqual(report['subprocess'], {'returncode': None, 'timed_out': True, 'reaped': False})
        kill.assert_called_once_with(45671, signal.SIGKILL)

    def test_default_kill_error_preserved_and_reap_attempted(self):
        report, kill = self.default_run([subprocess.TimeoutExpired(ARGV, 120), 0],
                                         OSError('owned group kill failed'))
        self.assert_report(report, 'FAILED')
        self.assertEqual(report['first_error']['message'], 'owned group kill failed')
        self.assertEqual(self.child.wait.call_args_list[-1], mock.call(timeout=5))

    def test_default_reap_error_does_not_replace_first_kill_error(self):
        report, kill = self.default_run([subprocess.TimeoutExpired(ARGV, 120),
                                         RuntimeError('later reap error')], OSError('first kill error'))
        self.assert_report(report, 'FAILED')
        self.assertEqual(report['first_error']['message'], 'first kill error')
        kill.assert_called_once_with(45671, signal.SIGKILL)

    def test_default_spawn_failure_is_not_retried(self):
        with mock.patch.object(subprocess, 'Popen', side_effect=OSError('spawn failed')) as spawn:
            report = self.upload(executor=None)
        self.assert_report(report, 'FAILED')
        self.assertEqual(report['first_error']['message'], 'spawn failed')
        spawn.assert_called_once()

    def test_default_rechecks_budget_after_stream_creation(self):
        real = os.open
        def delayed(path, flags, *args, **kwargs):
            fd = real(path, flags, *args, **kwargs)
            if Path(os.fsdecode(path)).name == 'upload.stderr' and flags & os.O_CREAT:
                self.clock.value = 280.0
            return fd
        with mock.patch.object(os, 'open', side_effect=delayed):
            with mock.patch.object(subprocess, 'Popen') as spawn:
                report = self.upload(executor=None)
        self.assert_report(report, 'FAILED')
        self.assertEqual(report['attempts'], 1)
        spawn.assert_not_called()

    def test_default_recomputes_shorter_wait_after_stream_creation(self):
        real = os.open
        def delayed(path, flags, *args, **kwargs):
            fd = real(path, flags, *args, **kwargs)
            if Path(os.fsdecode(path)).name == 'upload.stderr' and flags & os.O_CREAT:
                self.clock.value = 200.0
            return fd
        with mock.patch.object(os, 'open', side_effect=delayed):
            report, kill = self.default_run()
        self.assert_report(report, 'UPLOADED')
        self.child.wait.assert_called_once_with(timeout=80)

    def test_support_globals_and_capture_are_not_repurposed(self):
        before = dict(vars(self.support))
        with mock.patch.object(self.support, 'Capture', side_effect=AssertionError('Capture forbidden')):
            with mock.patch.object(self.support, 'collect', side_effect=AssertionError('capture forbidden')):
                self.assert_report(self.upload(), 'UPLOADED')
        self.assertEqual(set(vars(self.support)), set(before))
        for name, value in before.items():
            self.assertIs(vars(self.support)[name], value, name)


if __name__ == '__main__':
    unittest.main(verbosity=2)
