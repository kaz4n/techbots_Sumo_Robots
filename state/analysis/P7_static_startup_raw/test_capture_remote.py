# Tests the D153 collector from its public contract with controlled host seams.
# Keeps finite read ownership and subprocess cleanup independent of implementation.
# Freeze this file before its first Python -B execution; no native tools are launched.
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
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAN = (
    ('before.loader.0', 0x08000000, 65536),
    ('before.loader.1', 0x08010000, 65536),
    ('before.loader.2', 0x08020000, 65536),
    ('before.loader.3', 0x08030000, 65536),
    ('before.loader.4', 0x08040000, 1536),
    ('before.sketch.0', 0x08100000, 65536),
    ('before.sketch.1', 0x08110000, 27560),
    ('first.runtime', 0x2003BC98, 28),
    ('first.transaction', 0x2003B2B0, 24),
    ('second.runtime', 0x2003BC98, 28),
    ('second.transaction', 0x2003B2B0, 24),
    ('after.sketch.0', 0x08100000, 65536),
    ('after.sketch.1', 0x08110000, 27560),
    ('after.loader.0', 0x08000000, 65536),
    ('after.loader.1', 0x08010000, 65536),
    ('after.loader.2', 0x08020000, 65536),
    ('after.loader.3', 0x08030000, 65536),
    ('after.loader.4', 0x08040000, 1536),
)
LOADER = bytes(range(256)) * 1030
SKETCH = (bytes(reversed(range(256))) * 364)[:93096]
REPORT_KEYS = {'schema', 'run_id', 'source_sha256', 'status', 'counts',
               'started_utc', 'finished_utc', 'started_monotonic',
               'finished_monotonic', 'wait', 'reads', 'first_error',
               'postcheck_errors', 'analysis'}
ENV = {'HOME': '/home/arduino', 'USER': 'arduino', 'LOGNAME': 'arduino',
       'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}
SUCCESS = {'returncode': 0, 'timed_out': False, 'reaped': True}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeClock:
    def __init__(self):
        self.now = 100.0
        self.sleeps = []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class Decoder:
    def __init__(self, case):
        self.case = case
        self.calls = []
        self.result = {'flash': dict.fromkeys(('before_loader', 'before_sketch',
                       'after_loader', 'after_sketch'), True),
                       'observation': 'RUNNING_COUNTER_ADVANCED',
                       'runtime': [{}, {}], 'transaction': [{}, {}], 'epoch_delta': 1,
                       'errors': []}

    def read_plan(self):
        return PLAN

    def analyze_capture(self, reads, loader, sketch):
        self.calls.append((reads, loader, sketch))
        self.case.assertEqual(tuple(reads), tuple(self.case.triples))
        self.case.assertEqual((loader, sketch), (LOADER, SKETCH))
        return copy.deepcopy(self.result)


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux descriptor semantics required')
class CaptureRemoteContract(unittest.TestCase):
    def setUp(self):
        guard = mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Only controlled process substitutes allowed'))
        guard.start()
        self.addCleanup(guard.stop)
        guard = mock.patch.object(os, 'killpg', side_effect=AssertionError('Only controlled group substitutes allowed'))
        guard.start()
        self.addCleanup(guard.stop)
        self.temp = tempfile.TemporaryDirectory(prefix='sumox_capture_contract_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.subject = load(HERE / 'capture_remote.py', 'capture_remote_contract_subject')
        self.helper = load(ROOT / 'state/analysis/P7_static_link_probe_raw/static_remote.py',
                           'capture_remote_frozen_descriptor_helper')
        self.bindings = json.loads((HERE / 'capture_bindings.json').read_text())
        self.contents = {key: ('synthetic-' + key).encode() for key in self.bindings['files']}
        self.contents['sketch'] = SKETCH
        for key, pin in self.bindings['files'].items():
            raw = self.contents[key]
            pin.update(bytes=len(raw), sha256=digest(raw))
            path = self.logical(pin['path'])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.bindings['loader_image'] = {'bytes': len(LOADER), 'sha256': digest(LOADER)}
        self.subject.BINDINGS = copy.deepcopy(self.bindings)
        self.output = self.logical(self.bindings['output'])
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.logical('/proc').mkdir()
        self.logical('/home/arduino').mkdir(exist_ok=True)
        self.clock = FakeClock()
        self.calls, self.triples, self.identity_calls, self.pin_checks = [], [], [], []
        self.after_execute = None
        self.process_result = copy.deepcopy(SUCCESS)
        self.execute_error = None
        self.raw_change = None
        self.stdout = b''
        self.stderr = b'Open On-Chip Debugger: normal diagnostics\n'
        self.decoder = Decoder(self)
        self.identity_value = {'user': 'arduino', 'uid': 1000, 'gid': 1000,
            'home': '/home/arduino', 'sysname': 'Linux', 'release': 'fixture',
            'machine': 'aarch64', 'boot_id': self.bindings['boot_id'],
            'python': list(sys.version_info[:3])}
        self.helper.identity = self.identity
        # The frozen helper remains responsible for actual traversal/read checks.
        # Only native user ownership is synthetic in this small host filesystem.
        self.helper.directory_info = self.directory_info
        self.original_logical_read = self.helper.logical_read
        self.helper.logical_read = self.logical_read
        self.loader_calls = []

    def logical(self, path):
        return self.root / str(path).lstrip('/')

    def identity(self, fd):
        self.identity_calls.append(fd)
        return copy.deepcopy(self.identity_value)

    def directory_info(self, info, logical):
        if not stat.S_ISDIR(info.st_mode):
            raise ValueError('Not a directory: ' + logical)
        return self.helper.directory_id(info)

    def logical_read(self, fd, logical, limit, proc=False):
        for key, pin in self.bindings['files'].items():
            if logical == pin['path']:
                self.pin_checks.append((key, limit))
        return self.original_logical_read(fd, logical, limit, proc)

    def loader_image(self, raw):
        self.assertEqual(raw, self.contents['loader'])
        self.loader_calls.append(raw)
        return LOADER

    def bytes_for(self, item):
        name, address, count = item
        if '.loader.' in name:
            return LOADER[address - 0x08000000:address - 0x08000000 + count]
        if '.sketch.' in name:
            return SKETCH[address - 0x08100000:address - 0x08100000 + count]
        return (b'\x01\x00' + bytes(count - 2))

    def local_argument(self, path):
        value = Path(path)
        if value.is_relative_to(self.root):
            return value
        return self.logical(value)

    def check_launch(self, argv, stdout_path, stderr_path, timeout):
        index = len(self.calls)
        self.assertLess(index, len(PLAN))
        name, address, size = PLAN[index]
        logical_raw = self.bindings['output'] + f'/{index:02d}-{name}.bin'
        expected = [self.bindings['files']['openocd']['path'], '-f',
            self.bindings['files']['config']['path'], '-c',
            f'dump_image {{{logical_raw}}} 0x{address:08x} {size}', '-c', 'shutdown']
        self.assertEqual(argv, expected)
        self.assertEqual(self.local_argument(stdout_path), self.output / f'{index:02d}.stdout')
        self.assertEqual(self.local_argument(stderr_path), self.output / f'{index:02d}.stderr')
        self.assertEqual(timeout, min(30.0, 700.0 - self.clock.now))
        self.assertTrue((self.output / 'capture_attempt.json').is_file())
        self.assertTrue((self.output / f'{index:02d}.command.json').is_file())
        claim = json.loads((self.output / 'capture_attempt.json').read_text())
        self.assertIn(self.bindings['run_id'], json.dumps(claim))
        self.assertIn(self.bindings['source_sha256'], json.dumps(claim))
        self.assertFalse(self.logical(logical_raw).exists())
        self.calls.append((copy.deepcopy(argv), timeout))
        return index, self.logical(logical_raw)

    def write_raw(self, index, target):
        item = PLAN[index]
        data = self.bytes_for(item)
        if self.raw_change:
            changed = self.raw_change(index, data, target)
            if changed is None:
                return
            data = changed
        with target.open('xb') as output:
            output.write(data)
        self.triples.append((item[0], item[1], data))

    def execute(self, argv, stdout_path, stderr_path, timeout):
        index, target = self.check_launch(argv, stdout_path, stderr_path, timeout)
        if self.execute_error:
            raise self.execute_error
        self.local_argument(stdout_path).write_bytes(self.stdout)
        self.local_argument(stderr_path).write_bytes(self.stderr)
        self.write_raw(index, target)
        if self.after_execute:
            self.after_execute(index)
        return copy.deepcopy(self.process_result)

    def collect(self, **kwargs):
        args = dict(fs_root=self.root, executor=self.execute, clock=self.clock,
                    sleeper=self.clock.sleep)
        args.update(kwargs)
        return self.subject.collect(self.helper, self.decoder, self.loader_image, **args)

    def assert_report(self, report, status):
        self.assertEqual(set(report), REPORT_KEYS)
        self.assertEqual(report['schema'], 'static-capture-result-v1')
        self.assertEqual(report['status'], status)
        self.assertEqual(report['run_id'], self.bindings['run_id'])
        self.assertEqual(report['source_sha256'], self.bindings['source_sha256'])
        self.assertEqual(set(report['counts']), {'commands', 'reads', 'requested_bytes'})
        self.assertEqual(report['counts']['commands'], len(self.calls))
        expected_bytes = sum(item[2] for item in PLAN[:len(self.calls)])
        self.assertEqual(report['counts']['requested_bytes'], expected_bytes)
        self.assertEqual(report['counts']['reads'], len(report['reads']))
        for read, item in zip(report['reads'], PLAN):
            self.assertEqual(set(read), {'name', 'address', 'bytes', 'sha256', 'file'})
            self.assertEqual((read['name'], read['address'], read['bytes']), item)
            self.assertEqual(read['sha256'], digest(self.bytes_for(item)))
        for error in report['postcheck_errors']:
            self.assertEqual(set(error), {'check', 'type', 'message'})
        if status == 'FAILED':
            self.assertEqual(set(report['first_error']), {'type', 'message'})
        else:
            self.assertIsNone(report['first_error'])
            self.assertEqual(report['postcheck_errors'], [])
        saved = json.loads((self.output / 'capture_result.json').read_text())
        self.assertEqual(saved, report)
        return report

    def refused(self):
        try:
            report = self.collect()
        except Exception:
            report = None
        self.assertEqual(self.calls, [])
        self.assertFalse(self.output.exists())
        if report is not None:
            self.assertEqual(report['status'], 'FAILED')

    def test_complete_exact_plan_receipts_and_diagnostics(self):
        report = self.assert_report(self.collect(), 'COLLECTED')
        self.assertEqual(report['counts'], {'commands': 18, 'reads': 18, 'requested_bytes': 713656})
        self.assertEqual(len(self.decoder.calls), 1)
        self.assertEqual(report['analysis'], self.decoder.result)
        self.assertEqual(self.clock.sleeps, [2])
        self.assertEqual(report['wait'], {'requested_seconds': 2, 'before': 100.0, 'after': 102.0})
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o700)
        self.assertEqual(len(list(self.output.glob('*.command.json'))), 18)
        self.assertEqual(len(list(self.output.glob('*.result.json'))), 18)
        self.assertGreaterEqual(len(self.identity_calls), 2)
        for key in self.bindings['files']:
            self.assertGreaterEqual(sum(name == key for name, _ in self.pin_checks), 2)
        self.assertTrue(all(limit == self.bindings['files'][key]['bytes'] for key, limit in self.pin_checks))

    def test_existing_output_is_never_modified(self):
        self.output.mkdir()
        sentinel = self.output / 'user-owned'
        sentinel.write_bytes(b'preserve me')
        with self.assertRaises(Exception):
            self.collect()
        self.assertEqual(self.calls, [])
        self.assertEqual(list(self.output.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_bytes(), b'preserve me')

    def test_success_cannot_be_repeated(self):
        self.assert_report(self.collect(), 'COLLECTED')
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        with self.assertRaises(Exception):
            self.collect()
        self.assertEqual(len(self.calls), 18)
        self.assertEqual({p.name: p.read_bytes() for p in self.output.iterdir()}, before)

    def test_bindings_exact_shapes_types_and_path_admission(self):
        cases = []
        class StrChild(str):
            pass
        class IntChild(int):
            pass
        for key, value in [('schema', 'unknown'), ('run_id', 'another-run'), ('uid', True),
                           ('uid', 0), ('uid', IntChild(1000)),
                           ('schema', StrChild(self.bindings['schema'])),
                           ('boot_id', self.bindings['boot_id'].upper()),
                           ('source_sha256', 'A'*64), ('source_sha256', '0'*64),
                           ('output', self.bindings['output'] + '/child'),
                           ('output', self.bindings['output'] + '-other')]:
            changed = copy.deepcopy(self.bindings)
            changed[key] = value
            cases.append(changed)
        for key in self.bindings:
            changed = copy.deepcopy(self.bindings)
            del changed[key]
            cases.append(changed)
        changed = copy.deepcopy(self.bindings)
        changed['extra'] = 1
        cases.append(changed)
        for extra in (True, False):
            changed = copy.deepcopy(self.bindings)
            if extra:
                changed['files']['extra'] = copy.deepcopy(changed['files']['openocd'])
            else:
                del changed['files']['openocd']
            cases.append(changed)
        for value in ({'bytes': 263680}, {'bytes': True, 'sha256': digest(LOADER)},
                      {'bytes': 263679, 'sha256': digest(LOADER)},
                      dict(self.bindings['loader_image'], extra=1)):
            changed = copy.deepcopy(self.bindings)
            changed['loader_image'] = value
            cases.append(changed)
        for key, value in [('bytes', True), ('bytes', 0), ('bytes', 64*1024*1024+1),
                           ('sha256', 'a'*63), ('sha256', 'A'*64),
                           ('path', '/opt//openocd'), ('path', '/opt/../openocd'),
                           ('path', '/opt/./openocd'), ('path', '/opt/open ocd'),
                           ('path', 'relative'), ('extra', 1)]:
            changed = copy.deepcopy(self.bindings)
            changed['files']['openocd'][key] = value
            cases.append(changed)
        for changed in cases:
            with self.subTest(changed=changed):
                self.subject.BINDINGS = changed
                self.refused()

    def test_python_bytecode_mode_is_rejected_before_mutation(self):
        original = sys.flags
        class FlagsWithoutB:
            dont_write_bytecode = 0
            def __getattr__(self, key):
                return getattr(original, key)
        with mock.patch.object(sys, 'dont_write_bytecode', False), \
             mock.patch.object(sys, 'flags', FlagsWithoutB()):
            self.refused()

    def test_all_identity_mismatches_rejected(self):
        original = copy.deepcopy(self.identity_value)
        for key, value in [('user', 'root'), ('uid', 1001), ('home', '/tmp'),
                           ('sysname', 'Darwin'), ('machine', 'x86_64'),
                           ('boot_id', '00000000-0000-0000-0000-000000000000')]:
            with self.subTest(key=key):
                self.identity_value = dict(original, **{key: value})
                self.refused()

    def test_each_pin_mismatch_rejected_without_execution(self):
        for key, pin in self.bindings['files'].items():
            with self.subTest(key=key):
                path = self.logical(pin['path'])
                path.write_bytes(b'!' + self.contents[key][1:])
                self.refused()
                path.write_bytes(self.contents[key])

    def test_invalid_loader_reference_rejected(self):
        self.loader_image = lambda raw: b'!' + LOADER[1:]
        self.refused()

    def test_loader_reference_exact_bytes_type_and_length(self):
        for value in (bytearray(LOADER), memoryview(LOADER), LOADER[:-1], LOADER + b'!'):
            with self.subTest(kind=type(value), size=len(value)):
                self.loader_image = lambda raw: value
                self.refused()

    def test_pin_symlink_and_parent_symlink_rejected(self):
        target = self.logical(self.bindings['files']['config']['path'])
        real = target.with_suffix('.real')
        target.rename(real)
        target.symlink_to(real)
        self.refused()
        target.unlink()
        real.rename(target)
        parent = self.output.parent
        moved = parent.with_name(parent.name + '-saved')
        parent.rename(moved)
        parent.symlink_to(moved, target_is_directory=True)
        self.refused()

    def test_exact_process_conflicts_reject_without_execution(self):
        for name in ('openocd', 'remoteocd', 'arduino-cli'):
            with self.subTest(name=name):
                folder = self.logical('/proc/123')
                folder.mkdir(exist_ok=True)
                (folder / 'comm').write_text(name + '\n')
                self.refused()

    def test_similar_process_name_does_not_conflict(self):
        folder = self.logical('/proc/123')
        folder.mkdir()
        (folder / 'comm').write_text('openocd-helper\n')
        self.assert_report(self.collect(), 'COLLECTED')

    def test_present_process_with_unreadable_comm_is_not_disappearance(self):
        self.logical('/proc/123').mkdir()
        self.refused()

    def test_disappeared_process_entry_is_allowed(self):
        folder = self.logical('/proc/123')
        folder.mkdir()
        original = self.helper.logical_read
        def read(fd, logical, limit, proc=False):
            if logical == '/proc/123/comm':
                folder.rmdir()
                raise FileNotFoundError('process disappeared')
            return original(fd, logical, limit, proc)
        self.helper.logical_read = read
        self.assert_report(self.collect(), 'COLLECTED')

    def test_receipts_are_fsynced_before_each_launch(self):
        synced = []
        real_fsync = os.fsync
        def fsync(fd):
            synced.append(os.readlink('/proc/self/fd/' + str(fd)))
            return real_fsync(fd)
        original = self.execute
        def execute(*args):
            index = len(self.calls)
            self.assertIn(str(self.output / 'capture_attempt.json'), synced)
            self.assertIn(str(self.output), synced)
            self.assertIn(str(self.output / f'{index:02d}.command.json'), synced)
            return original(*args)
        with mock.patch.object(os, 'fsync', fsync):
            self.assert_report(self.collect(executor=execute), 'COLLECTED')

    def test_command_exception_retains_first_error_and_stops(self):
        self.execute_error = RuntimeError('primary spawn failure')
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(report['first_error'], {'type': 'RuntimeError', 'message': 'primary spawn failure'})
        self.assertEqual(report['counts']['reads'], 0)
        self.assertEqual(len(self.calls), 1)
        self.assertIsNone(report['analysis'])
        self.assertEqual(self.decoder.calls, [])
        self.assertTrue((self.output / '00.result.json').is_file())

    def test_claim_fsync_failure_consumes_directory_and_finalizes(self):
        original = os.fsync
        failed = []
        def fsync(fd):
            if not failed and os.readlink('/proc/self/fd/' + str(fd)).endswith('/capture_attempt.json'):
                failed.append(True)
                raise OSError('controlled claim fsync failure')
            return original(fd)
        with mock.patch.object(os, 'fsync', fsync):
            report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(self.calls, [])
        self.assertEqual(report['first_error']['message'], 'controlled claim fsync failure')
        self.assertGreaterEqual(len(self.identity_calls), 2)
        for key in self.bindings['files']:
            self.assertEqual(sum(name == key for name, _ in self.pin_checks), 2)

    def test_command_receipt_fsync_failure_does_not_launch(self):
        original = os.fsync
        def fsync(fd):
            if os.readlink('/proc/self/fd/' + str(fd)).endswith('/00.command.json'):
                raise OSError('controlled command fsync failure')
            return original(fd)
        with mock.patch.object(os, 'fsync', fsync):
            report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(self.calls, [])
        self.assertEqual(report['counts']['requested_bytes'], 0)

    def test_preexisting_next_command_receipt_is_preserved(self):
        sentinel = b'occupied command receipt'
        def collide(index):
            if index == 0:
                (self.output / '01.command.json').write_bytes(sentinel)
        self.after_execute = collide
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(report['counts']['requested_bytes'], 65536)
        self.assertEqual((self.output / '01.command.json').read_bytes(), sentinel)

    def test_bad_process_results_stop_after_single_attempt(self):
        cases = [dict(SUCCESS, returncode=1), dict(SUCCESS, timed_out=True),
                 dict(SUCCESS, reaped=False), dict(SUCCESS, returncode=None),
                 dict(SUCCESS, returncode=False), dict(SUCCESS, timed_out=0),
                 dict(SUCCESS, reaped=1), dict(SUCCESS, extra=1), {}, None]
        for result in cases:
            with self.subTest(result=result):
                # A separate directory is required because every attempt is terminal.
                case = type(self)('test_complete_exact_plan_receipts_and_diagnostics')
                case.setUp()
                try:
                    case.process_result = result
                    report = case.assert_report(case.collect(), 'FAILED')
                    self.assertEqual(len(case.calls), 1)
                    self.assertIsNone(report['analysis'])
                    self.assertEqual(case.decoder.calls, [])
                finally:
                    case.doCleanups()

    def test_missing_short_oversize_and_symlink_raw_stop(self):
        for mode in ('missing', 'short', 'oversize', 'symlink'):
            with self.subTest(mode=mode):
                case = type(self)('test_complete_exact_plan_receipts_and_diagnostics')
                case.setUp()
                try:
                    def change(index, raw, target):
                        if mode == 'missing':
                            return None
                        if mode == 'short':
                            return raw[:-1]
                        if mode == 'oversize':
                            return raw + b'!'
                        real = target.with_suffix('.real')
                        real.write_bytes(raw)
                        target.symlink_to(real)
                        return None
                    case.raw_change = change
                    report = case.assert_report(case.collect(), 'FAILED')
                    self.assertEqual((len(case.calls), report['counts']['reads']), (1, 0))
                    self.assertIsNone(report['analysis'])
                finally:
                    case.doCleanups()

    def test_first_flash_mismatch_suppresses_all_ram_and_decoder(self):
        self.raw_change = lambda index, raw, target: (b'!' + raw[1:]) if index == 0 else raw
        report = self.collect()
        self.assertEqual(report['status'], 'FAILED')
        self.assertEqual(len(self.calls), 7)
        self.assertEqual(report['counts']['reads'], 7)
        self.assertIsNone(report['analysis'])
        self.assertEqual(self.decoder.calls, [])
        self.assertEqual(self.clock.sleeps, [])
        self.assertFalse((self.output / '07.command.json').exists())

    def test_wait_occurs_only_between_pair_one_and_pair_two(self):
        def sleep(seconds):
            self.assertEqual(len(self.calls), 9)
            self.clock.sleep(seconds)
        self.assert_report(self.collect(sleeper=sleep), 'COLLECTED')

    def test_short_wait_aborts_before_second_sample(self):
        def sleep(seconds):
            self.clock.sleeps.append(seconds)
            self.clock.now += 1.999
        report = self.assert_report(self.collect(sleeper=sleep), 'FAILED')
        self.assertEqual(len(self.calls), 9)
        self.assertIsNone(report['analysis'])
        self.assertLess(report['wait']['after'] - report['wait']['before'], 2)

    def test_sleep_exception_preserves_requested_wait(self):
        def sleep(seconds):
            raise RuntimeError('sleep refused')
        report = self.assert_report(self.collect(sleeper=sleep), 'FAILED')
        self.assertEqual(len(self.calls), 9)
        self.assertEqual(report['wait'], {'requested_seconds': 2, 'before': 100.0, 'after': None})
        self.assertEqual(report['first_error']['message'], 'sleep refused')

    def test_deadline_caps_next_timeout_and_stops_without_retry(self):
        def advance(index):
            self.clock.now = 680.0 if index == 0 else 700.0
        self.after_execute = advance
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual([call[1] for call in self.calls], [30.0, 20.0])
        self.assertIsNone(report['analysis'])
        self.assertGreaterEqual(len(self.identity_calls), 2)
        for key in self.bindings['files']:
            self.assertGreaterEqual(sum(name == key for name, _ in self.pin_checks), 2)

    def test_deadline_expiring_in_wait_does_not_launch_second_sample(self):
        def sleep(seconds):
            self.clock.now = 700.0
        report = self.assert_report(self.collect(sleeper=sleep), 'FAILED')
        self.assertEqual(len(self.calls), 9)
        self.assertIsNone(report['analysis'])

    def test_clock_failure_retains_first_error_and_finalizes(self):
        broken = []
        def clock():
            if broken:
                raise RuntimeError('controlled monotonic failure')
            return self.clock.now
        def execute(*args):
            self.check_launch(*args)
            broken.append(True)
            raise OSError('original execution failure')
        report = self.assert_report(self.collect(executor=execute, clock=clock), 'FAILED')
        self.assertEqual(report['first_error']['message'], 'original execution failure')
        self.assertEqual(report['finished_monotonic'], 100.0)
        evidence = json.dumps(report) + (self.output / '00.result.json').read_text()
        self.assertIn('controlled monotonic failure', evidence)
        self.assertEqual(len(self.calls), 1)
        for key in self.bindings['files']:
            self.assertEqual(sum(name == key for name, _ in self.pin_checks), 2)

    def test_collected_fault_and_no_progress_remain_honest(self):
        self.decoder.result.update(observation='SAMPLED_FAULT', epoch_delta=None)
        report = self.assert_report(self.collect(), 'COLLECTED')
        self.assertEqual(report['analysis']['observation'], 'SAMPLED_FAULT')

    def test_collected_no_progress_is_not_upgraded(self):
        self.decoder.result.update(observation='NO_RUNNING_PROGRESS', epoch_delta=0)
        report = self.assert_report(self.collect(), 'COLLECTED')
        self.assertEqual(report['analysis']['observation'], 'NO_RUNNING_PROGRESS')

    def test_late_flash_mismatch_analysis_retained(self):
        self.decoder.result['flash']['after_sketch'] = False
        self.decoder.result.update(observation='FLASH_MISMATCH', epoch_delta=None,
                                   runtime=[], transaction=[])
        report = self.assert_report(self.collect(), 'COLLECTED')
        self.assertEqual(report['analysis']['observation'], 'FLASH_MISMATCH')

    def test_decoder_exception_yields_failed_complete_capture(self):
        self.decoder.analyze_capture = mock.Mock(side_effect=ValueError('decode rejected'))
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(report['counts']['reads'], 18)
        self.assertIsNone(report['analysis'])
        self.decoder.analyze_capture.assert_called_once()

    def test_malformed_decoder_returns_do_not_become_analysis(self):
        cases = [None, [], {}, dict(self.decoder.result, observation='SUCCESS'),
                 dict(self.decoder.result, extra=1), dict(self.decoder.result, epoch_delta=True),
                 dict(self.decoder.result, epoch_delta=-1), dict(self.decoder.result, epoch_delta=2**32),
                 dict(self.decoder.result, runtime=[]), dict(self.decoder.result, transaction=[{}]),
                 dict(self.decoder.result, errors=[1]), dict(self.decoder.result, flash={})]
        bad_flash = copy.deepcopy(self.decoder.result)
        bad_flash['flash']['before_loader'] = 1
        cases.append(bad_flash)
        for value in cases:
            with self.subTest(value=value):
                case = type(self)('test_complete_exact_plan_receipts_and_diagnostics')
                case.setUp()
                try:
                    case.decoder.analyze_capture = mock.Mock(return_value=value)
                    report = case.assert_report(case.collect(), 'FAILED')
                    self.assertEqual(report['counts']['reads'], 18)
                    self.assertIsNone(report['analysis'])
                    case.decoder.analyze_capture.assert_called_once()
                finally:
                    case.doCleanups()

    def test_postchecks_attempt_all_pins_and_identity_after_primary_failure(self):
        def execute(*args):
            index, target = self.check_launch(*args)
            for key, pin in self.bindings['files'].items():
                self.logical(pin['path']).write_bytes(b'bad')
            self.identity_value['boot_id'] = '00000000-0000-0000-0000-000000000000'
            raise RuntimeError('primary execution error')
        report = self.assert_report(self.collect(executor=execute), 'FAILED')
        self.assertEqual(report['first_error']['message'], 'primary execution error')
        self.assertGreaterEqual(len(report['postcheck_errors']), 6)
        for key in self.bindings['files']:
            self.assertEqual(sum(name == key for name, _ in self.pin_checks), 2)
        self.assertGreaterEqual(len(self.identity_calls), 2)

    def test_pin_drift_after_complete_capture_fails_final_status(self):
        def drift(index):
            if index == 17:
                self.logical(self.bindings['files']['config']['path']).write_bytes(b'changed')
        self.after_execute = drift
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(report['counts']['reads'], 18)
        self.assertTrue(report['postcheck_errors'])

    def test_output_replacement_stops_and_records_only_in_original_directory(self):
        old_output = self.output
        moved = old_output.with_name(old_output.name + '-moved')
        def replace(index):
            if index == 0:
                old_output.rename(moved)
                old_output.mkdir()
                (old_output / 'replacement-sentinel').write_bytes(b'do not touch')
                self.output = moved
        self.after_execute = replace
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(report['postcheck_errors'])
        self.assertEqual([p.name for p in old_output.iterdir()], ['replacement-sentinel'])

    def test_parent_replacement_stops_and_keeps_original_receipts(self):
        old_parent = self.output.parent
        moved_parent = old_parent.with_name(old_parent.name + '-moved')
        def replace(index):
            if index == 0:
                old_parent.rename(moved_parent)
                old_parent.mkdir()
                (old_parent / 'replacement-sentinel').write_bytes(b'do not touch')
                self.output = moved_parent / self.output.name
        self.after_execute = replace
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(report['postcheck_errors'])
        self.assertEqual([p.name for p in old_parent.iterdir()], ['replacement-sentinel'])

    def test_result_receipt_existing_entry_is_not_overwritten(self):
        sentinel = b'preexisting result must survive'
        def collide(index):
            if index == 17:
                (self.output / 'capture_result.json').write_bytes(sentinel)
        self.after_execute = collide
        with self.assertRaises(Exception):
            self.collect()
        self.assertEqual((self.output / 'capture_result.json').read_bytes(), sentinel)

    def test_stdout_at_exact_limit_is_failure(self):
        self.stdout = bytes(1024*1024)
        report = self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(len(self.calls), 1)
        self.assertIsNone(report['analysis'])

    def test_stderr_at_exact_limit_is_failure(self):
        self.stderr = bytes(1024*1024)
        self.assert_report(self.collect(), 'FAILED')
        self.assertEqual(len(self.calls), 1)

    def run_default_wrapper(self, mode):
        case = self
        waits, kills, limits = [], [], []
        class Process:
            pid = 456789
            returncode = None
            def wait(self, timeout):
                waits.append(timeout)
                if mode in ('timeout', 'kill-error', 'unreaped') and len(waits) == 1:
                    raise subprocess.TimeoutExpired('controlled-openocd', timeout)
                if mode == 'unreaped':
                    raise subprocess.TimeoutExpired('controlled-reap', timeout)
                self.returncode = -signal.SIGKILL if mode == 'timeout' else 0
                return self.returncode
        def popen(argv, **kwargs):
            index = len(case.calls)
            stdout = kwargs['stdout']
            stderr = kwargs['stderr']
            out_name = os.readlink('/proc/self/fd/' + str(stdout if isinstance(stdout, int) else stdout.fileno()))
            err_name = os.readlink('/proc/self/fd/' + str(stderr if isinstance(stderr, int) else stderr.fileno()))
            index, target = case.check_launch(argv, out_name, err_name, 30.0)
            case.assertEqual(kwargs.get('cwd'), '/home/arduino')
            case.assertEqual(kwargs.get('env'), ENV)
            case.assertIs(kwargs.get('start_new_session'), True)
            case.assertEqual(kwargs.get('stdin'), subprocess.DEVNULL)
            case.assertFalse(kwargs.get('shell', False))
            case.assertTrue(callable(kwargs.get('preexec_fn')))
            kwargs['preexec_fn']()
            if mode == 'spawn-error':
                raise OSError('controlled spawn failure')
            case.write_raw(index, target)
            return Process()
        def killpg(pid, sig):
            kills.append((pid, sig))
            if mode == 'kill-error':
                raise OSError('controlled kill failure')
        import resource
        with mock.patch.object(subprocess, 'Popen', popen), \
             mock.patch.object(os, 'killpg', killpg), \
             mock.patch.object(os, 'getpgid', lambda pid: pid if pid == 456789 else self.fail('Unowned PID lookup')), \
             mock.patch.object(resource, 'setrlimit', lambda which, bounds: limits.append((which, bounds))):
            report = self.collect(executor=None)
        return report, waits, kills, limits

    def test_default_wrapper_fixed_environment_session_limits_and_success(self):
        original_open, creations = os.open, []
        def opened(path, flags, *args, **kwargs):
            if str(path).endswith(('.json', '.stdout', '.stderr')) and flags & os.O_CREAT:
                self.assertTrue(flags & os.O_EXCL)
                self.assertTrue(flags & os.O_NOFOLLOW)
                self.assertIn('dir_fd', kwargs)
                self.assertEqual(os.readlink('/proc/self/fd/' + str(kwargs['dir_fd'])), str(self.output))
                creations.append(str(path))
            return original_open(path, flags, *args, **kwargs)
        with mock.patch.object(os, 'open', opened):
            report, waits, kills, limits = self.run_default_wrapper('success')
        self.assert_report(report, 'COLLECTED')
        self.assertEqual(waits, [30.0]*18)
        self.assertEqual(kills, [])
        import resource
        self.assertEqual(limits, [(resource.RLIMIT_FSIZE, (1048576, 1048576))]*18)
        self.assertEqual(len([path for path in creations if path.endswith('.stdout')]), 18)
        self.assertEqual(len([path for path in creations if path.endswith('.stderr')]), 18)

    def test_default_wrapper_expiry_during_stream_open_never_launches(self):
        original = os.open
        def opened(path, flags, *args, **kwargs):
            fd = original(path, flags, *args, **kwargs)
            if str(path).endswith('.stderr') and flags & os.O_CREAT:
                self.clock.now = 700.0
            return fd
        with mock.patch.object(os, 'open', opened), \
             mock.patch.object(subprocess, 'Popen') as popen:
            report = self.collect(executor=None)
        popen.assert_not_called()
        self.assertEqual(report['status'], 'FAILED')
        self.assertEqual(report['counts'], {'commands': 1, 'reads': 0, 'requested_bytes': 65536})
        self.assertEqual(json.loads((self.output / 'capture_result.json').read_text()), report)
        self.assertIsNone(report['analysis'])

    def test_default_wrapper_timeout_kills_owned_group_and_bounded_reap(self):
        report, waits, kills, limits = self.run_default_wrapper('timeout')
        self.assert_report(report, 'FAILED')
        self.assertEqual(waits, [30.0, 5.0])
        self.assertEqual(kills, [(456789, signal.SIGKILL)])
        self.assertEqual(len(self.calls), 1)
        receipt = json.loads((self.output / '00.result.json').read_text())
        self.assertIn('true', json.dumps(receipt).lower())

    def test_default_wrapper_kill_error_still_attempts_bounded_reap(self):
        report, waits, kills, limits = self.run_default_wrapper('kill-error')
        self.assert_report(report, 'FAILED')
        self.assertEqual(waits, [30.0, 5.0])
        self.assertEqual(kills, [(456789, signal.SIGKILL)])
        self.assertIn('controlled kill failure', json.dumps(report))

    def test_default_wrapper_unreaped_timeout_never_claims_success(self):
        report, waits, kills, limits = self.run_default_wrapper('unreaped')
        self.assert_report(report, 'FAILED')
        self.assertEqual(waits, [30.0, 5.0])
        self.assertEqual(kills, [(456789, signal.SIGKILL)])
        self.assertEqual(len(self.calls), 1)

    def test_default_wrapper_spawn_exception_is_terminal(self):
        report, waits, kills, limits = self.run_default_wrapper('spawn-error')
        self.assert_report(report, 'FAILED')
        self.assertEqual((waits, kills), ([], []))
        self.assertEqual(len(self.calls), 1)
        self.assertIn('controlled spawn failure', json.dumps(report))


if __name__ == '__main__':
    unittest.main()
