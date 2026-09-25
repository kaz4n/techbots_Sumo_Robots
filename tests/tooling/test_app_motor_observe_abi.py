# Tests D194 from its fixed public contract and the historical ABI interfaces.
# Synthetic file-tool packets and blocked transports separate host checks from hardware.
# Authored and frozen before reading or executing the new wrapper implementation.
import base64
import builtins
from contextlib import ExitStack
import copy
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock
import zlib

ROOT = Path(__file__).absolute().parents[2]
WRAPPER = 'state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi.py'
CONTRACT = 'state/analysis/P7_app_motor_observe_abi_contract.md'
CONTRACT_SHA = '889d6a7697f2ddc0051ef73f52f82c1dd43f35fa45af9fc2d4958f44441bf8ff'
ORIGINAL = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_abi.py'
NORMALIZER = 'state/analysis/P7_app_motor_fault_compile_raw/interpret_static_abi.py'
LAUNCHER = 'tools/compile_app_motor_observe.py'
COMPILE_RAW = 'state/analysis/P7_app_motor_observe_compile_raw'
HEAD = '1234567890abcdef1234567890abcdef12345678'
SOURCE = '3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
OWNER = '/home/arduino/sumox26_codex_build/app-motor-observe-static01'
SCOPE = '/home/arduino/sumox26_codex_build/app-motor-observe-abi-static01'
SYMBOL = '_ZN12_GLOBAL__N_110diagnosticE'
PINS = {
    ORIGINAL: (16600, '0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c'),
    NORMALIZER: (5928, '6a990871af18ca8bc5d10f9d11efda4619052bf1de5ab272188de746f95dad21'),
    LAUNCHER: (7583, '70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827'),
    COMPILE_RAW + '/inputs_static.json': (13333, 'aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e'),
    COMPILE_RAW + '/native_static01/result.json': (1615, '24d12778bbb337a5cba411fadab5c5e7a8fd69f99beee7b68ac110c31613622b'),
    COMPILE_RAW + '/native_static01/artifacts.json': (9651, '5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b'),
}
PROJECTED_SIZE = 16833
PROJECTED_SHA = 'f359bebbbba176036891027412327b6b59e47d849e46c37cfe3363cd70a95c14'
REJECT = (ValueError, TypeError, OSError, RuntimeError, SystemExit, KeyError)
TYPES = ('app_motor_observe::Runner', 'app_motor_observe::Report', 'app_motor_observe::Snapshot',
    'motor_fault::Trace', 'motor_fault::TraceReport', 'motor_fault::Call', 'app::Runtime',
    'app::RuntimeReport', 'app::Transaction', 'app::TransactionReport', 'fsm::RobotResult',
    'fsm::PreviousTick', 'motors::MotorGate', 'motors::Result', 'motors::HaltResult',
    'core::Outputs', 'countdown::LifecycleResult', 'countdown::Result', 'report_.polls', 'bool')
WINDOWS = {'trace_.report_': 'motor_fault::TraceReport', 'report_': 'app_motor_observe::Report',
    'report_.before_abort.runtime': 'app::RuntimeReport',
    'report_.before_abort.transaction': 'app::TransactionReport',
    'report_.before_abort.previous': 'fsm::PreviousTick', 'runtime_.report_': 'app::RuntimeReport',
    'runtime_.transaction_.report_': 'app::TransactionReport',
    'runtime_.transaction_.previous_': 'fsm::PreviousTick',
    'runtime_.transaction_.gate_': 'motors::MotorGate', 'report_.polls': 'report_.polls',
    'attempted_': 'bool'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def module(raw, path, name):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    value.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), value.__dict__)
    return value


def expected_projection(raw):
    replacements = [(b'app_motor_fault', b'app_motor_observe', 10),
        (b'app-motor-fault', b'app-motor-observe', 2),
        (b'D188_STATIC_FILE_ONLY_ABI', b'D194_STATIC_FILE_ONLY_ABI', 2),
        (b'self.compiler = loaded(COMPILE, HARD_PINS[COMPILE])',
         b'self.compiler = loaded(COMPILE, HARD_PINS[COMPILE]).load_caller(root=ROOT)', 1),
        (b'21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950', SOURCE.encode(), 1),
        (b'cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a', PINS[LAUNCHER][1].encode(), 1),
        (b'd4eae97c1c47a1ce0fa24c9d7e3ae44857a565cd7b85b9c17be45143654d3eb5', PINS[COMPILE_RAW + '/inputs_static.json'][1].encode(), 1),
        (b'f8928bd0b9a59f47c1bc02c627523af8f250535ffcd269e37e5a80414cc0ce82', PINS[COMPILE_RAW + '/native_static01/result.json'][1].encode(), 1),
        (b'57b98c00db1ed5d90394812fcbb3fb28effedd4381f6e2fc03a6e7c04b45a6ce', PINS[COMPILE_RAW + '/native_static01/artifacts.json'][1].encode(), 1),
        (b"'countdown::Result')", b"'countdown::Result', 'report_.polls')", 1),
        (b"    'attempted_': 'bool',", b"    'report_.polls': 'report_.polls',\n    'attempted_': 'bool',", 1),
        (b"    expressions = ['set max-value-size 1048576']\n    for name in (*TYPES, 'bool'):\n",
         b"    expressions = ['set max-value-size 1048576']\n    for name in (*TYPES, 'bool'):\n"
         b"        subject = ('((app_motor_observe::Runner*)0)->report_.polls'\n"
         b"                   if name == 'report_.polls' else name)\n", 1),
        (b"expression + '(' + name + ')'", b"expression + '(' + subject + ')'", 1),
        (b"'ptype /o ' + name", b"'ptype /o ' + subject", 1)]
    for before, after, count in replacements:
        if raw.count(before) != count:
            raise AssertionError('Contract projection occurrence: ' + repr(before))
        raw = raw.replace(before, after)
    if (len(raw), digest(raw)) != (PROJECTED_SIZE, PROJECTED_SHA):
        raise AssertionError('Contract projected bytes do not match')
    return raw


def record(argv, text=''):
    raw = text.encode()
    return dict(argv=argv, execution=dict(returncode=0, timed_out=False, reaped=True),
        deadline_seconds=60, reap_seconds=5, stdout_base64=base64.b64encode(raw).decode(),
        stdout_bytes=len(raw), stderr_base64='', stderr_bytes=0)


def packet(size_token='1024', polls_size=4, polls_offset=248):
    address = 0x20020000
    sizes = {name: 16 for name in TYPES}
    sizes.update({'app_motor_observe::Runner': 1024, 'app_motor_observe::Report': 256,
                  'report_.polls': polls_size, 'bool': 1})
    alignments = {name: 4 for name in TYPES}
    alignments['bool'] = 1
    lines = []
    for name in TYPES:
        for label, value in (('SIZE', sizes[name]), ('ALIGN', alignments[name])):
            lines.extend(['SUMOX_' + label + ' ' + name, '$1 = ' + str(value)])
        lines.extend(['SUMOX_LAYOUT ' + name, 'type = controlled fixture'])
    offsets = {name: index * 32 for index, name in enumerate(WINDOWS)}
    offsets['report_.polls'] = polls_offset
    for name, value in offsets.items():
        lines.extend(['SUMOX_OFFSET ' + name, '$2 = ' + str(value)])
    elf = ('  Type: EXEC (Executable file)\n'
           ' [ 7] .bss NOBITS 20020000 000100 002000 00 WA 0 0 4\n'
           '  91: 20020000 ' + size_token + ' OBJECT LOCAL DEFAULT 7 ' + SYMBOL + '\n')
    commands = [record(['readelf', '--version'], 'controlled readelf\n'),
                record(['gdb', '--version'], 'controlled gdb\n'),
                record(['readelf', '-hSWs'], elf), record(['gdb', 'fixture'], '\n'.join(lines) + '\n')]
    result = dict(scope='D194_STATIC_FILE_ONLY_ABI', status='OBSERVED', first_error=None,
                  commands=commands, final_checks=[dict(path='board_identity', status='PASS')])
    layout = dict(sections=[dict(name='.bss', address=address, size=8192)],
                  bss_zero=dict(start=address, end=address + 8192))
    return result, layout


def stream_text(result, index):
    return base64.b64decode(result['commands'][index]['stdout_base64']).decode()


def replace_text(result, index, text):
    row = result['commands'][index]
    row.update(stdout_base64=base64.b64encode(text.encode()).decode(), stdout_bytes=len(text.encode()))


class ContractCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode:
            raise RuntimeError('D194 oracle requires Python -B')
        cls.raw = (ROOT / WRAPPER).read_bytes()
        cls.inputs = {name: (ROOT / name).read_bytes() for name in PINS}
        for name, raw in cls.inputs.items():
            if (len(raw), digest(raw)) != PINS[name]:
                raise AssertionError('Fixed prior input changed: ' + name)
        if digest((ROOT / CONTRACT).read_bytes()) != CONTRACT_SHA:
            raise AssertionError('Frozen D194 contract changed')

    def setUp(self):
        self.subject = module(self.raw, ROOT / WRAPPER, '_d194_subject')
        for owner, names in ((subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
                             (socket, ('socket', 'create_connection'))):
            for name in names:
                patch = mock.patch.object(owner, name, side_effect=AssertionError('External effect: ' + name))
                patch.start(); self.addCleanup(patch.stop)

    def reject(self, call):
        with self.assertRaises(REJECT):
            call()

    def scratch(self):
        temp = tempfile.TemporaryDirectory(prefix='sumox-d194-',
                    dir='/dev/shm' if sys.platform == 'linux' else None)
        self.addCleanup(temp.cleanup)
        return Path(temp.name).resolve()

    def loaded(self):
        return self.subject.load_reader(root=ROOT)


class ProjectionContract(ContractCase):
    def test_import_performs_no_io_or_dispatch(self):
        with ExitStack() as stack:
            for owner, names in ((Path, ('open', 'read_bytes', 'read_text', 'write_bytes', 'write_text', 'mkdir')),
                                 (builtins, ('open',)), (io, ('open',)), (os, ('open',))):
                for name in names:
                    stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('Import I/O')))
            value = module(self.raw, ROOT / WRAPPER, '_d194_passive_import')
        for name in ('parse_request', 'pinned', 'project_reader', 'summarize', 'load_reader', 'main'):
            self.assertTrue(callable(getattr(value, name)))

    def test_projection_exact_contract_bytes_without_io_or_execution(self):
        original = self.inputs[ORIGINAL]
        expected = expected_projection(original)
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Projector read')), \
                mock.patch.object(os, 'open', side_effect=AssertionError('Projector opened')):
            self.subject.__dict__['__builtins__']['exec'] = mock.Mock(side_effect=AssertionError('Projector exec'))
            actual = self.subject.project_reader(original)
        self.assertIs(type(actual), bytes)
        self.assertEqual(actual, expected)
        self.assertEqual(digest(original), PINS[ORIGINAL][1])

    def test_projection_rejects_types_line_endings_truncation_and_mutation(self):
        raw = self.inputs[ORIGINAL]
        bad = [None, True, 1, raw.decode(), bytearray(raw), memoryview(raw), b'', raw[:-1], raw + b'\n',
               b'x' + raw[1:], raw.replace(b'\n', b'\r\n'), raw.replace(b'app_motor_fault', b'else', 1),
               raw + b'\n# app_motor_fault']
        for value in bad:
            with self.subTest(kind=type(value).__name__):
                self.reject(lambda: self.subject.project_reader(value))

    def test_cli_exact_forms_and_invalid_forms_precede_loading(self):
        for action in ('--check-only', '--execute'):
            self.assertEqual(self.subject.parse_request([action, '--reviewed-head', HEAD]), (action, HEAD))
        bad = [None, True, '', [], ('--check-only', '--reviewed-head', HEAD), ['--help'],
               ['--execute', '--reviewed-head', HEAD.upper()], ['--execute', '--reviewed-head', 1],
               ['--execute', '--reviewed-head', HEAD + '0'], ['--reviewed-head', HEAD, '--execute'],
               ['--execute', '--reviewed-head', HEAD, '--profile', 'match']]
        with mock.patch.object(self.subject, 'load_reader', side_effect=AssertionError('Invalid CLI loaded')):
            for value in bad:
                with self.subTest(value=value):
                    self.reject(lambda: self.subject.parse_request(value))
                    self.reject(lambda: self.subject.main(value))

    def test_main_requires_B_and_delegates_once_preserving_result_and_error(self):
        args = ['--check-only', '--reviewed-head', HEAD]
        with mock.patch.object(sys, 'dont_write_bytecode', False), mock.patch.object(
                self.subject, 'load_reader', side_effect=AssertionError('Missing -B loaded')):
            self.reject(lambda: self.subject.main(args))
        for action in ('--check-only', '--execute'):
            args = [action, '--reviewed-head', HEAD]
            private = types.SimpleNamespace(main=mock.Mock(return_value=79))
            with mock.patch.object(self.subject, 'load_reader', return_value=private) as load:
                self.assertEqual(self.subject.main(args), 79)
                load.assert_called_once_with(root=self.subject.ROOT)
                private.main.assert_called_once_with(args)
        error = RuntimeError('delegated original error')
        with mock.patch.object(self.subject, 'load_reader', return_value=types.SimpleNamespace(
                main=mock.Mock(side_effect=error))):
            with self.assertRaises(RuntimeError) as caught:
                self.subject.main(args)
            self.assertIs(caught.exception, error)

    def test_loader_private_namespaces_roots_pins_and_passive_load(self):
        before = dict(sys.modules)
        value, other = self.loaded(), self.loaded()
        self.assertIsNot(value, other)
        self.assertEqual(value.ROOT, ROOT)
        self.assertEqual(Path(value.__file__), ROOT / ORIGINAL)
        self.assertNotEqual(value.__name__, '__main__')
        self.assertEqual(sys.modules, before)
        self.assertIs(value.pinned, self.subject.pinned)
        for name in (ORIGINAL, NORMALIZER, LAUNCHER, CONTRACT):
            self.assertEqual(value.HARD_PINS[name], CONTRACT_SHA if name == CONTRACT else PINS[name][1])
        self.assertEqual(value.SELF, WRAPPER)
        self.assertEqual(value.OWNER, OWNER)
        self.assertEqual(value.SOURCE, SOURCE)
        self.assertEqual(value.BOOT, BOOT)
        self.assertEqual(tuple((*value.TYPES, 'bool')), TYPES)
        self.assertEqual(value.WINDOWS, WINDOWS)

    def test_loader_checks_every_source_and_contract_before_any_execution(self):
        for failed in (ORIGINAL, NORMALIZER, LAUNCHER, CONTRACT):
            root = self.scratch()
            for name in (ORIGINAL, NORMALIZER, LAUNCHER, CONTRACT):
                path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT / name).read_bytes())
            (root / failed).write_bytes(b'rejected exact pin')
            executed = []
            actual = builtins.exec
            self.subject.__dict__['__builtins__']['exec'] = lambda *args: (executed.append(True), actual(*args))[1]
            self.reject(lambda: self.subject.load_reader(root=root))
            self.assertFalse(executed, failed)

    def test_loader_uses_fixture_root_without_instantiating_owner(self):
        root = self.scratch()
        for name in (ORIGINAL, NORMALIZER, LAUNCHER, CONTRACT):
            path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())
        value = self.subject.load_reader(root=root)
        self.assertEqual(value.ROOT, root)
        self.assertEqual(Path(value.__file__), root / ORIGINAL)
        self.assertFalse((root / COMPILE_RAW / 'native_abi_static01').exists())
        self.assertFalse((root / 'state/analysis/P7_current_app_compile_raw').exists())

    def test_loader_rejects_projection_before_source_execution(self):
        self.subject.__dict__['__builtins__']['exec'] = mock.Mock(side_effect=AssertionError('Failed projection executed'))
        with mock.patch.object(self.subject, 'project_reader', side_effect=ValueError('Rejected projection')):
            self.reject(self.loaded)

    def test_real_compiler_loader_retains_original_pins_and_new_inventory(self):
        value = self.loaded()
        owner = value.StaticAbi(HEAD)
        self.assertEqual(owner.compiler.PROJECT, 'app_motor_observe.ino')
        self.assertEqual(owner.compiler.CALLER, LAUNCHER)
        self.assertIn('tools/compile_app_motor_fault.py', owner.compiler.HARD_PINS)
        names = owner.source_names()
        self.assertIn('bench/app_motor_observe/app_motor_observe.ino', names)
        self.assertFalse(any(name.startswith('bench/app_motor_fault/') for name in names))
        self.assertEqual(owner.remote, SCOPE)
        self.assertEqual(owner.output, ROOT / COMPILE_RAW / 'native_abi_static01')
        self.assertEqual(owner.local_pins[WRAPPER], digest(self.raw))


class BootstrapContract(ContractCase):
    def sample(self):
        root = self.scratch(); path = root / 'parent' / 'input.py'; path.parent.mkdir()
        raw = b'one checked local input\n'; path.write_bytes(raw)
        return root, path, raw

    def test_absolute_relative_limit_and_digest_contract(self):
        _, path, raw = self.sample()
        self.assertEqual(self.subject.pinned(path, digest(raw), len(raw)), raw)
        relative = os.path.relpath(path, Path.cwd())
        self.assertEqual(self.subject.pinned(relative, digest(raw)), raw)
        for expected, limit in [(digest(raw).upper(), 100), ('a' * 63, 100), (None, 100),
                                (digest(raw), True), (digest(raw), 0), (digest(raw), 16777217)]:
            with self.subTest(expected=expected, limit=limit):
                self.reject(lambda: self.subject.pinned(path, expected, limit))

    def test_empty_oversized_missing_wrong_digest_and_directory_refuse(self):
        _, path, raw = self.sample()
        self.reject(lambda: self.subject.pinned(path, '0' * 64))
        self.reject(lambda: self.subject.pinned(path.parent, digest(raw)))
        for value in (b'', b'x' * 33):
            path.write_bytes(value)
            self.reject(lambda: self.subject.pinned(path, digest(value), 32))
        path.unlink()
        self.reject(lambda: self.subject.pinned(path, digest(raw)))

    def test_real_hardlink_refuses(self):
        root, path, raw = self.sample()
        os.link(path, root / 'second-link')
        self.reject(lambda: self.subject.pinned(path, digest(raw)))

    def test_real_file_and_parent_symlink_refuse(self):
        root, path, raw = self.sample()
        link = root / 'linked-input'
        try:
            link.symlink_to(path)
        except OSError as error:
            if os.name == 'nt' and getattr(error, 'winerror', None) == 1314:
                self.skipTest('Windows symlink creation unavailable: WinError 1314')
            raise
        self.reject(lambda: self.subject.pinned(link, digest(raw)))
        folder = root / 'linked-parent'; folder.symlink_to(path.parent, target_is_directory=True)
        self.reject(lambda: self.subject.pinned(folder / path.name, digest(raw)))

    def test_reparse_on_file_parent_or_root_refuses_before_open(self):
        root, path, raw = self.sample(); original = Path.lstat
        class Reparse:
            def __init__(self, value): self.value = value; self.st_file_attributes = 1024
            def __getattr__(self, key): return getattr(self.value, key)
        for target in (path, path.parent, root):
            def observed(item, *args, **kwargs):
                value = original(item, *args, **kwargs)
                return Reparse(value) if item == target else value
            with mock.patch.object(Path, 'lstat', observed), mock.patch.object(
                    os, 'open', side_effect=AssertionError('Reparse path opened')):
                self.reject(lambda: self.subject.pinned(path, digest(raw)))

    def test_initial_descriptor_type_link_and_identity_refuse_before_read(self):
        _, path, raw = self.sample(); original = os.fstat
        class Changed:
            def __init__(self, value, field, replacement):
                self.value = value; setattr(self, field, replacement)
            def __getattr__(self, key): return getattr(self.value, key)
        values = {'st_ino': path.stat().st_ino + 1, 'st_mode': stat.S_IFIFO | 0o600,
                  'st_nlink': 2, 'st_file_attributes': 1024}
        for field, replacement in values.items():
            with self.subTest(field=field), mock.patch.object(os, 'fstat',
                    lambda fd: Changed(original(fd), field, replacement)), mock.patch.object(
                    os, 'fdopen', side_effect=AssertionError('Rejected descriptor wrapped/read')):
                self.reject(lambda: self.subject.pinned(path, digest(raw)))

    def test_descriptor_drift_including_same_api_ctime_refuses(self):
        _, path, raw = self.sample(); original = os.fstat
        class Drift:
            def __init__(self, value, field): self.value = value; setattr(self, field, getattr(value, field) + 1)
            def __getattr__(self, key): return getattr(self.value, key)
        for field in ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'):
            count = []
            def observed(fd):
                value = original(fd); count.append(True)
                return Drift(value, field) if len(count) == 2 else value
            with self.subTest(field=field), mock.patch.object(os, 'fstat', observed):
                self.reject(lambda: self.subject.pinned(path, digest(raw)))

    def test_ctime_cross_api_exception_is_only_windows_and_each_api_stays_stable(self):
        _, path, raw = self.sample(); original = os.fstat
        class HandleTime:
            def __init__(self, value): self.value = value; self.st_ctime_ns = value.st_ctime_ns + 123456789
            def __getattr__(self, key): return getattr(self.value, key)
        with mock.patch.object(os, 'fstat', lambda fd: HandleTime(original(fd))):
            if os.name == 'nt': self.assertEqual(self.subject.pinned(path, digest(raw)), raw)
            else: self.reject(lambda: self.subject.pinned(path, digest(raw)))

    def test_parent_snapshot_drift_during_read_refuses(self):
        _, path, raw = self.sample(); fdopen = os.fdopen
        before = path.parent.stat()
        class Stream:
            def __init__(self, actual): self.actual = actual
            def fileno(self): return self.actual.fileno()
            def read(self, size):
                value = self.actual.read(size)
                os.utime(path.parent, ns=(before.st_atime_ns, before.st_mtime_ns + 1000000000))
                return value
            def close(self): self.actual.close()
            def __enter__(self): return self
            def __exit__(self, *_): self.close()
        with mock.patch.object(os, 'fdopen', lambda *args, **kwargs: Stream(fdopen(*args, **kwargs))):
            self.reject(lambda: self.subject.pinned(path, digest(raw)))

    def test_read_is_bounded_and_preserves_primary_over_close(self):
        _, path, raw = self.sample(); fdopen = os.fdopen
        primary, secondary = OSError('primary read'), OSError('secondary close')
        for mode in ('read', 'check', 'close'):
            reads, closes = [], []
            class Stream:
                def __init__(self, stream): self.stream = stream
                def fileno(self): return self.stream.fileno()
                def read(self, size=-1):
                    reads.append(size)
                    if mode == 'read': raise primary
                    value = self.stream.read(size)
                    return b'x' + value[1:] if mode == 'check' else value
                def close(self): closes.append(True); self.stream.close(); raise secondary
                def __enter__(self): return self
                def __exit__(self, *_): self.close()
            with mock.patch.object(os, 'fdopen', lambda *args, **kwargs: Stream(fdopen(*args, **kwargs))):
                with self.assertRaises(REJECT) as caught:
                    self.subject.pinned(path, digest(raw), 32)
            self.assertEqual(reads, [33]); self.assertTrue(closes)
            if mode == 'check': self.assertIsNot(caught.exception, secondary)
            else: self.assertIs(caught.exception, primary if mode == 'read' else secondary)

    @unittest.skipUnless(sys.platform == 'linux', 'Linux FIFO descriptor race fixture')
    def test_regular_to_fifo_swap_is_nonblocking_and_never_read(self):
        root, path, raw = self.sample(); saved = root / 'retained'
        original = os.open; attempts = []
        def opened(candidate, flags, *args, **kwargs):
            if Path(candidate) == path:
                self.assertTrue(flags & os.O_NONBLOCK)
                attempts.append(True); path.rename(saved); os.mkfifo(path)
            return original(candidate, flags, *args, **kwargs)
        try:
            with mock.patch.object(os, 'open', opened), mock.patch.object(
                    os, 'fdopen', side_effect=AssertionError('FIFO read attempted')):
                self.reject(lambda: self.subject.pinned(path, digest(raw)))
            self.assertEqual(attempts, [True])
        finally:
            if saved.exists(): path.unlink(); saved.rename(path)


class AbiContract(ContractCase):
    def setUp(self):
        super().setUp()
        self.reader = self.loaded()

    def test_queries_observe_twenty_groups_eleven_windows_and_member_polls(self):
        captured = []
        backend = types.SimpleNamespace(PREFIX='/fixed/tool-',
            gdb=lambda file, expressions: captured.append((file, expressions)) or ['gdb', file, *expressions])
        commands = self.reader.queries(backend)
        self.assertEqual(len(commands), 4)
        self.assertEqual(commands[:3], [['/fixed/tool-readelf', '--version'], ['/fixed/tool-gdb', '--version'],
            ['/fixed/tool-readelf', '-hSWs', OWNER + '/build/app_motor_observe.ino.elf']])
        debug, expressions = captured[0]
        self.assertEqual(debug, OWNER + '/build/app_motor_observe.ino_debug.elf')
        for label in ('SIZE', 'ALIGN', 'LAYOUT'):
            self.assertEqual(sum(item.startswith('echo SUMOX_' + label + ' ') for item in expressions), 20)
        self.assertEqual(sum(item.startswith('echo SUMOX_OFFSET ') for item in expressions), 11)
        member = '((app_motor_observe::Runner*)0)->report_.polls'
        for expression in ('p/d sizeof(' + member + ')', 'p/d alignof(' + member + ')', 'ptype /o ' + member,
                           'p/d (unsigned long)&' + member):
            self.assertIn(expression, expressions)

    def test_decimal_and_hex_normalize_only_private_copy_with_exact_metadata(self):
        for token in ('1024', '001024', '0x400', '0x0400'):
            result, layout = packet(token); before, layout_before = copy.deepcopy(result), copy.deepcopy(layout)
            answer = self.reader.summarize(result, layout)
            self.assertEqual(result, before); self.assertEqual(layout, layout_before)
            self.assertEqual(answer['status'], 'STATIC_ABI_OBSERVED')
            self.assertEqual(answer['bytes'], 1024)
            projection = answer['readelf_size_projection']
            projected = '1024' if token.startswith('0x') else token
            original_text = stream_text(result, 2)
            expected_text = original_text.replace(' ' + token + ' OBJECT', ' ' + projected + ' OBJECT')
            self.assertEqual(projection, dict(symbol=SYMBOL, original_token=token, size_bytes=1024,
                projected_token=projected, changed=expected_text != original_text,
                original_stdout_sha256=digest(original_text.encode()),
                projected_stdout_sha256=digest(expected_text.encode()),
                original_stdout_bytes=len(original_text.encode()), projected_stdout_bytes=len(expected_text.encode())))

    def test_public_summary_passes_private_rows_and_preserves_layout(self):
        result, layout = packet('0x400'); before = copy.deepcopy(result)
        seen = []
        normalizer = module(self.inputs[NORMALIZER], ROOT / NORMALIZER, '_d194_original_normalizer')
        def parser(private, same_layout):
            seen.append(private)
            self.assertIs(same_layout, layout)
            self.assertIsNot(private, result)
            for old, new in zip(result['commands'], private['commands']): self.assertIsNot(old, new)
            self.assertEqual(private['commands'][:2], result['commands'][:2])
            self.assertEqual(private['commands'][3], result['commands'][3])
            return {'status': 'controlled parser result'}
        answer = self.subject.summarize(result, layout, parser=parser, normalize=normalizer.normalize)
        self.assertEqual(result, before); self.assertEqual(len(seen), 1)
        self.assertEqual(answer['status'], 'controlled parser result')
        self.assertTrue(answer['readelf_size_projection']['changed'])

    def test_polls_size_and_offset_are_observed_instead_of_assumed(self):
        for size, offset in ((4, 248), (8, 280), (12, 408)):
            result, layout = packet(polls_size=size, polls_offset=offset)
            answer = self.reader.summarize(result, layout)
            self.assertEqual(answer['sizes']['report_.polls'], size)
            self.assertEqual(answer['windows']['report_.polls'], dict(type='report_.polls',
                offset=offset, address=0x20020000 + offset, bytes=size))

    def test_summary_rejects_bad_container_counts_rows_base64_and_utf8(self):
        result, layout = packet()
        bad = [None, [], {'commands': []}, {'commands': result['commands'][:3]},
               {'commands': result['commands'] + [{}]}, {'commands': [None] * 4}]
        for encoded in ('@@', 'YQ===', base64.b64encode(b'\xff').decode()):
            value = copy.deepcopy(result); value['commands'][2]['stdout_base64'] = encoded; bad.append(value)
        for value in bad:
            with self.subTest(value_type=type(value).__name__):
                self.reject(lambda: self.reader.summarize(value, layout))

    def test_normalizer_rejects_missing_duplicate_malformed_zero_oversized_symbols(self):
        for token in ('0', '0x0', '1048577', '0x100001', '0X400', '-1024', '1e3', '0xZZ'):
            result, layout = packet(token)
            self.reject(lambda: self.reader.summarize(result, layout))
        result, layout = packet(); text = stream_text(result, 2)
        row = text.splitlines(keepends=True)[-1]
        for changed in (text.replace(SYMBOL, SYMBOL + 'x'), text + row,
                        text.replace('OBJECT', 'FUNC'), text.replace('LOCAL', 'GLOBAL')):
            replace_text(result, 2, changed)
            self.reject(lambda: self.reader.summarize(result, layout))

    def test_parser_rejects_exec_section_symbol_size_and_bss_bounds(self):
        result, layout = packet(); text = stream_text(result, 2)
        for changed in (text.replace('EXEC (Executable file)', 'DYN (Shared object file)'),
                        text.replace('NOBITS', 'PROGBITS'), text.replace('002000', '001000'),
                        text.replace('1024 OBJECT', '1028 OBJECT'),
                        text.replace('91: 20020000', '91: 20020001')):
            value = copy.deepcopy(result); replace_text(value, 2, changed)
            self.reject(lambda: self.reader.summarize(value, layout))
        short = copy.deepcopy(layout); short['bss_zero']['end'] = 0x200203ff
        self.reject(lambda: self.reader.summarize(result, short))

    def test_parser_rejects_missing_duplicate_tags_and_alignment_windows(self):
        result, layout = packet(); text = stream_text(result, 3)
        cases = [text.replace('SUMOX_SIZE report_.polls\n$1 = 4\n', ''),
                 text + 'SUMOX_SIZE report_.polls\n$7 = 4\n',
                 text.replace('SUMOX_LAYOUT report_.polls\n', ''),
                 text + 'SUMOX_LAYOUT report_.polls\n',
                 text.replace('SUMOX_ALIGN report_.polls\n$1 = 4', 'SUMOX_ALIGN report_.polls\n$1 = 3'),
                 text.replace('SUMOX_OFFSET report_.polls\n$2 = 248', 'SUMOX_OFFSET report_.polls\n$2 = 1024'),
                 text.replace('SUMOX_OFFSET report_.polls\n$2 = 248', 'SUMOX_OFFSET report_.polls\n$2 = 249'),
                 text + 'SUMOX_OFFSET report_.polls\n$3 = 248\n']
        for changed in cases:
            value = copy.deepcopy(result); replace_text(value, 3, changed)
            self.reject(lambda: self.reader.summarize(value, layout))

    def test_command_receipts_reject_argv_execution_deadlines_streams_and_stderr(self):
        good = record(['tool', 'file'], 'one\n')
        self.reader.checked_command(good, good['argv'])
        mutations = [('argv', ['other']), ('execution', dict(returncode=1, timed_out=False, reaped=True)),
            ('execution', dict(returncode=0, timed_out=True, reaped=True)),
            ('execution', dict(returncode=0, timed_out=False, reaped=False)), ('deadline_seconds', 61),
            ('reap_seconds', 6), ('stdout_bytes', True), ('stdout_bytes', 0), ('stdout_bytes', 1048577),
            ('stdout_base64', '####'), ('stdout_base64', 'b25lCg==='), ('error', None),
            ('stderr_base64', 'eA==')]
        for key, value in mutations:
            bad = copy.deepcopy(good); bad[key] = value
            with self.subTest(key=key, value=value):
                self.reject(lambda: self.reader.checked_command(bad, good['argv']))


class LifecycleContract(ContractCase):
    def prepared_owner(self):
        reader = self.loaded(); owner = reader.StaticAbi(HEAD)
        owner.compiler.CompileDiagnostic.admission(owner)
        owner.local = mock.Mock(return_value=None)
        owner.output = self.scratch() / 'exclusive-abi'
        space = mock.patch.object(reader.shutil, 'disk_usage', return_value=types.SimpleNamespace(free=268435456))
        space.start(); self.addCleanup(space.stop)
        return reader, owner

    def executing_owner(self):
        reader = self.loaded(); owner = reader.StaticAbi.__new__(reader.StaticAbi)
        owner.output = self.scratch() / 'exclusive-abi'
        result, layout = packet('0x400')
        owner.packet = {'layout': {'validator_report': layout}}
        owner.commands = [row['argv'] for row in result['commands']]
        owner.remote_pins = {}; owner.inputs = {'files': {}}; owner.local_pins = {}
        owner.program = 'controlled file-only program'; owner.bootstrap = 'controlled packed command'
        owner.claimed = False; owner.counter = 0
        owner.base = reader.loaded(reader.LEGACY, reader.HARD_PINS[reader.LEGACY])
        owner.prepare = mock.Mock(return_value={'status': 'STATIC_ABI_CHECKED'})
        owner.local = mock.Mock(return_value=None)
        owner.direct = mock.Mock(return_value=(types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None))
        writes = []
        owner.executor = {'write': lambda path, value: writes.append((path.name, copy.deepcopy(value)))}
        return reader, owner, result, writes

    def test_real_prepare_composes_four_file_tools_pins_and_windows_bound_without_claim(self):
        reader, owner = self.prepared_owner()
        value = owner.prepare()
        self.assertEqual(value['status'], 'STATIC_ABI_CHECKED')
        self.assertEqual(value['source_sha256'], SOURCE); self.assertEqual(value['boot_id'], BOOT)
        self.assertEqual(value['file_commands'], 4)
        self.assertEqual(len(owner.remote_pins), 12)
        self.assertFalse(owner.output.exists()); self.assertFalse(owner.claimed)
        command = ['/usr/bin/env', '-i', *(key + '=' + value for key, value in owner.base.ENV.items()),
                   '/usr/bin/python3', '-I', '-B', '-c', owner.bootstrap]
        argv = [owner.base.ADB, '-s', owner.base.BOARD, 'shell', '-T', shlex.join(command)]
        units = len(subprocess.list2cmdline(argv).encode('utf-16-le')) // 2 + 1
        self.assertEqual(value['command_units'], units); self.assertLessEqual(units, 30000)
        self.assertIn('D194_STATIC_FILE_ONLY_ABI', owner.program)
        self.assertNotIn('D188_STATIC_FILE_ONLY_ABI', owner.program)
        self.assertIn("if os.path.lexists(REMOTE):raise ValueError('ABI scope path exists')", owner.program)
        self.assertEqual(owner.commands[2][-1], OWNER + '/build/app_motor_observe.ino.elf')
        self.assertIn('-nx', owner.commands[3]); self.assertIn('-nh', owner.commands[3])
        self.assertFalse(any(item.startswith('target ') or item.startswith('call ') for item in owner.commands[3]))

    def test_local_refuses_wrong_head_dirty_tree_source_and_boot(self):
        reader = self.loaded(); owner = reader.StaticAbi(HEAD)
        owner.source_sha256, owner.boot = SOURCE, BOOT
        original = reader.pinned
        def read(path, expected, limit=1048576):
            return b'controlled ADB identity' if Path(path) == Path(owner.base.ADB) else original(path, expected, limit)
        with mock.patch.object(reader, 'pinned', read), mock.patch.object(
                owner.compiler.CompileDiagnostic, 'admission', return_value=None):
            for head, changes in [('0' * 40, []), (HEAD, [(' M', 'src/config.h')]),
                                  (HEAD, [('??', 'unrelated-output')])]:
                owner.git_state = mock.Mock(return_value=(head, changes))
                self.reject(owner.local)
            owner.git_state = mock.Mock(return_value=(HEAD, []))
            owner.local()
            owner.source_sha256 = '0' * 64; self.reject(owner.local)
            owner.source_sha256 = SOURCE; owner.boot = 'wrong'; self.reject(owner.local)

    def test_local_accepts_only_claimed_owner_untracked_outputs_and_checks_local_pins(self):
        reader = self.loaded(); owner = reader.StaticAbi(HEAD)
        owner.source_sha256, owner.boot = SOURCE, BOOT
        own = owner.output.relative_to(ROOT).as_posix() + '/result.json'
        owner.git_state = mock.Mock(return_value=(HEAD, [('??', own)]))
        with mock.patch.object(reader, 'pinned', return_value=b'controlled local pin') as pins, \
                mock.patch.object(owner.compiler.CompileDiagnostic, 'admission', return_value=None):
            self.reject(owner.local)
            owner.claimed = True; owner.local()
            observed = {str(call.args[0]) for call in pins.call_args_list}
            self.assertTrue({str(ROOT / name) for name in owner.local_pins} <= observed)
            owner.git_state.return_value = (HEAD, [(' M', own)]); self.reject(owner.local)
            owner.git_state.return_value = (HEAD, [])
            pins.side_effect = ValueError('pinned local source changed'); self.reject(owner.local)

    def test_prepare_consumed_owner_and_low_space_refuse(self):
        _, owner = self.prepared_owner(); owner.output.mkdir()
        self.reject(owner.prepare)
        owner.output.rmdir()
        with mock.patch.object(owner.base.shutil, 'disk_usage', return_value=types.SimpleNamespace(free=134217727)):
            self.reject(owner.prepare)

    def test_prepare_rejects_command_over_windows_bound(self):
        _, owner = self.prepared_owner()
        with mock.patch.object(subprocess, 'list2cmdline', return_value='x' * 30000):
            self.reject(owner.prepare)
        self.assertFalse(owner.output.exists())

    def test_prepare_rejects_wrong_compile_receipt_before_any_claim(self):
        reader, owner = self.prepared_owner(); original = reader.pinned
        path = ROOT / reader.OUTCOME
        for field, bad in (('status', 'FAILED'), ('first_error', {'message': 'failed'}),
                           ('source_sha256', '0' * 64), ('boot_id', 'different'),
                           ('compiler_calls', 2), ('query_calls', 0),
                           ('final_checks', [{'status': 'FAILED'}])):
            receipt = json.loads(self.inputs[COMPILE_RAW + '/native_static01/result.json'])
            receipt[field] = bad
            def read(candidate, expected, *args):
                return json.dumps(receipt).encode() if Path(candidate) == path else original(candidate, expected, *args)
            with self.subTest(field=field), mock.patch.object(reader, 'pinned', read):
                self.reject(owner.prepare)
            self.assertFalse(owner.output.exists())

    def test_execute_retains_raw_before_normalized_abi_and_independent_closure(self):
        _, owner, result, writes = self.executing_owner(); before = copy.deepcopy(result)
        closure = owner.execute()
        self.assertEqual([name for name, _ in writes], ['inputs.json', 'result.json', 'abi.json', 'local_result.json'])
        self.assertEqual(writes[1][1], before)
        self.assertTrue(writes[2][1]['readelf_size_projection']['changed'])
        self.assertEqual(result, before)
        self.assertEqual(closure['status'], 'STATIC_ABI_OBSERVED')
        self.assertEqual(closure['final_checks'], [dict(name='local', status='PASS')])
        owner.direct.assert_called_once_with(owner.bootstrap, 'file-abi', 400)
        owner.local.assert_called_once_with()
        self.assertTrue(owner.claimed); self.assertTrue(owner.output.is_dir())

    def test_execute_consumed_owner_is_not_reused(self):
        _, owner, _, writes = self.executing_owner()
        owner.output.mkdir()
        self.reject(owner.execute)
        owner.direct.assert_not_called(); owner.local.assert_not_called()
        self.assertFalse(writes)

    def test_execute_scope_status_error_command_count_and_closure_refusals_retain_raw(self):
        cases = [('scope', 'D188_STATIC_FILE_ONLY_ABI'), ('status', 'FAILED'),
                 ('first_error', {'message': 'native failure'}), ('commands', []),
                 ('final_checks', []), ('final_checks', [{'path': 'board_identity', 'status': 'FAILED'}]),
                 ('final_checks', [{'path': 'board_identity', 'status': 'PASS', 'extra': 1}]),
                 ('final_checks', [{'path': 'board_identity', 'status': 'PASS'}] * 2)]
        for key, value in cases:
            _, owner, result, writes = self.executing_owner(); result[key] = value
            owner.direct.return_value = (types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None)
            with self.subTest(key=key): self.reject(owner.execute)
            self.assertEqual(writes[1], ('result.json', result))
            self.assertNotIn('abi.json', [name for name, _ in writes])
            self.assertEqual(writes[-1][1]['status'], 'FAILED'); owner.local.assert_called_once_with()

    def test_execute_invalid_stream_or_parser_failure_is_closed_after_raw_retention(self):
        for failure in ('stream', 'parser'):
            _, owner, result, writes = self.executing_owner()
            if failure == 'stream': result['commands'][0]['stdout_bytes'] += 1
            else: replace_text(result, 3, stream_text(result, 3).replace('SUMOX_SIZE report_.polls', 'MISSING'))
            owner.direct.return_value = (types.SimpleNamespace(stdout=json.dumps(result), stderr=''), None)
            self.reject(owner.execute)
            self.assertEqual(writes[1][1], result)
            self.assertEqual(writes[-1][0], 'local_result.json'); owner.local.assert_called_once_with()

    def test_execute_transport_stderr_or_oversized_reply_refuses_and_closes(self):
        for stdout, stderr in (('{}', 'unexpected'), ('x' * 8388609, '')):
            _, owner, _, writes = self.executing_owner()
            owner.direct.return_value = (types.SimpleNamespace(stdout=stdout, stderr=stderr), None)
            self.reject(owner.execute)
            self.assertEqual([name for name, _ in writes], ['inputs.json', 'local_result.json'])
            self.assertEqual(writes[-1][1]['status'], 'FAILED')

    def test_execute_actual_decoder_rejects_duplicate_keys_nonfinite_and_invalid_json(self):
        for stdout in ('{"scope": 1, "scope": 2}', '{"value": NaN}', '{broken'):
            _, owner, _, writes = self.executing_owner()
            owner.direct.return_value = (types.SimpleNamespace(stdout=stdout, stderr=''), None)
            self.reject(owner.execute)
            self.assertEqual([name for name, _ in writes], ['inputs.json', 'local_result.json'])
            owner.local.assert_called_once_with()

    def test_primary_child_error_survives_local_and_receipt_close_failures(self):
        _, owner, _, writes = self.executing_owner()
        primary, local, close = RuntimeError('first child failure'), ValueError('local failure'), OSError('close failure')
        owner.direct.side_effect = primary; owner.local.side_effect = local
        def write(path, value):
            writes.append((path.name, copy.deepcopy(value)))
            if path.name == 'local_result.json': raise close
        owner.executor['write'] = write
        with self.assertRaises(RuntimeError) as caught: owner.execute()
        self.assertIs(caught.exception, primary)
        self.assertIs(caught.exception.__cause__, close)
        self.assertEqual(primary.local_closure['first_error']['message'], str(primary))
        self.assertEqual(primary.local_closure['final_checks'][0]['status'], 'FAILED')
        self.assertEqual(primary.evidence_write_errors, [{'type': 'OSError', 'message': str(close)}])

    def test_lone_local_or_closure_write_failure_remains_failure(self):
        for stage in ('local', 'write'):
            _, owner, _, writes = self.executing_owner(); error = OSError('closing ' + stage)
            if stage == 'local': owner.local.side_effect = error
            else:
                def write(path, value):
                    writes.append((path.name, copy.deepcopy(value)))
                    if path.name == 'local_result.json': raise error
                owner.executor['write'] = write
            with self.assertRaises(OSError) as caught: owner.execute()
            self.assertIs(caught.exception, error)
            owner.local.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
