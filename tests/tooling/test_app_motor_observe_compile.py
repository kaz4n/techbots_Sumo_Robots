# Tests D193 from its frozen byte-projection and fixed-compile public contract.
# Reuses D188 assertions in private metadata-projected oracle namespaces only.
# Freeze before Python -B execution; every process endpoint stays controlled.
import ast
import base64
import builtins
from contextlib import ExitStack
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock
import zlib

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = 'tools/compile_app_motor_observe.py'
CONTRACT = 'state/analysis/P7_app_motor_observe_compile_contract.md'
RAW = 'state/analysis/P7_app_motor_observe_compile_raw'
HEAD = '1234567890abcdef1234567890abcdef12345678'
PROJECT = 'app_motor_observe.ino'
REMOTE = '/home/arduino/sumox26_codex_build/app-motor-observe-static01'
REJECT = (ValueError, TypeError, RuntimeError, OSError, SystemExit)
ORIGINALS = {
    'caller': ('tools/compile_app_motor_fault.py', 29802,
               'cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a'),
    'adapter': ('tools/app_motor_fault_static_policy.py', 8262,
                '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270'),
    'remote': ('tools/app_motor_fault_compile_remote.py', 6891,
               '1428b9345d5f524b6c79ede2c30eabb240b6a45ef6a30a593063c3902054fec2'),
}
PROJECTED = {
    'caller': (29904, '830299e516c9221db35f81e2b01100cd5f0444cd7a78ca6148048805d2078884'),
    'adapter': (8266, 'e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d'),
    'remote': (6897, 'f7886c869980afc969082b66ce8d3fc35801fe7c11134b406af158f06049160c'),
}
SUBSTITUTIONS = {
    'caller': (
        (b"CALLER = 'tools/compile_app_motor_fault.py'", b"CALLER = 'tools/compile_app_motor_observe.py'", 1),
        (b'P7_app_motor_fault_compile_contract.md', b'P7_app_motor_observe_compile_contract.md', 1),
        (b'P7_app_motor_fault_compile_raw', b'P7_app_motor_observe_compile_raw', 1),
        (b'app-motor-fault-static', b'app-motor-observe-static', 6),
        (b"'app_motor_fault.ino'", b"'app_motor_observe.ino'", 1),
        (b'bench/app_motor_fault', b'bench/app_motor_observe', 4),
        (b"'app_motor_fault'", b"'app_motor_observe'", 2),
        (b"'/app_motor_fault'", b"'/app_motor_observe'", 1),
        (b'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS', b'STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS', 1),
        (b'self.code[ADAPTER]', b'project_adapter(self.code[ADAPTER])', 2),
        (b'self.code[REMOTE_HELPER]', b'project_remote(self.code[REMOTE_HELPER])', 2),
    ),
    'adapter': (
        (b"'app_motor_fault.ino'", b"'app_motor_observe.ino'", 1),
        (b'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS', b'STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS', 1),
    ),
    'remote': (
        (b'app-motor-fault-static01', b'app-motor-observe-static01', 1),
        (b"'app_motor_fault.ino'", b"'app_motor_observe.ino'", 1),
        (b'app-motor-fault-static-artifacts-v1', b'app-motor-observe-static-artifacts-v1', 1),
        (ORIGINALS['adapter'][2].encode(), PROJECTED['adapter'][1].encode(), 1),
    ),
}
ORACLE = 'tests/tooling/test_app_motor_fault_compile.py'
ORACLE_SHA = '53d547ad4c9c4df9e55313014e89ab731fddcf8edde6983c5cb535d253f73e96'
REMOTE_ORACLE = 'tests/tooling/test_app_motor_fault_compile_remote.py'
REMOTE_ORACLE_SHA = 'db0ff0284eb7c528a852f39a57fcb668c72c098543b6d6813298fc2dfeddd80b'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def module(raw, path, name):
    result = types.ModuleType(name)
    result.__file__ = str(path)
    result.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), result.__dict__)
    return result


def checked(path, expected):
    raw = path.read_bytes()
    if digest(raw) != expected:
        raise AssertionError('Historical oracle/source changed: ' + str(path))
    return raw


def expected_projection(kind, raw):
    name, size, sha = ORIGINALS[kind]
    if type(raw) is not bytes or len(raw) != size or digest(raw) != sha:
        raise AssertionError('Independent original pin: ' + name)
    for old, new, count in SUBSTITUTIONS[kind]:
        if raw.count(old) != count:
            raise AssertionError('Independent substitution count: ' + repr(old))
        raw = raw.replace(old, new)
    size, sha = PROJECTED[kind]
    if len(raw) != size or digest(raw) != sha:
        raise AssertionError('Independent projected pin: ' + kind)
    return raw


def metadata_oracle(raw):
    # Only test-fixture identity strings change; every D188 assertion is retained.
    protected = (ORIGINALS['adapter'][0], ORIGINALS['remote'][0], REMOTE_ORACLE)
    for index, name in enumerate(protected):
        raw = raw.replace(name.encode(), ('@PRESERVE_' + str(index) + '@').encode())
    for old, new in ((b'app_motor_fault', b'app_motor_observe'),
                     (b'app-motor-fault', b'app-motor-observe'),
                     (b'STATIC_APP_MOTOR_FAULT', b'STATIC_APP_MOTOR_OBSERVE')):
        raw = raw.replace(old, new)
    for index, name in enumerate(protected):
        raw = raw.replace(('@PRESERVE_' + str(index) + '@').encode(), name.encode())
    return raw


def inherited_oracle():
    oracle = module(metadata_oracle(checked(ROOT / ORACLE, ORACLE_SHA)), ROOT / ORACLE,
                    '_d193_private_inherited_oracle')
    original_load = oracle.load

    def private_load(path, name):
        if Path(path) == ROOT / LAUNCHER:
            launcher = module(path.read_bytes(), path, '_d193_fixture_launcher')
            return launcher.load_caller(root=ROOT)
        if Path(path) == ROOT / REMOTE_ORACLE:
            raw = checked(path, REMOTE_ORACLE_SHA)
            return module(metadata_oracle(raw), path, '_d193_private_artifact_oracle')
        return original_load(path, name)

    oracle.load = private_load
    oracle.FIXED = [*oracle.FIXED, ORIGINALS['caller'][0]]
    return oracle


class ProjectionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode:
            raise RuntimeError('D193 independent tests require Python -B')
        cls.raw = (ROOT / LAUNCHER).read_bytes()
        cls.originals = {kind: checked(ROOT / item[0], item[2]) for kind, item in ORIGINALS.items()}

    def setUp(self):
        self.subject = module(self.raw, ROOT / LAUNCHER, '_d193_independent_subject')
        for owner, names in ((subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
                             (socket, ('socket', 'create_connection'))):
            for name in names:
                patch = mock.patch.object(owner, name, side_effect=AssertionError('External effect: ' + name))
                patch.start(); self.addCleanup(patch.stop)

    def reject(self, function):
        with self.assertRaises(REJECT):
            function()

    def scratch(self):
        temporary = tempfile.TemporaryDirectory(prefix='sumox-d193-original-',
                    dir='/dev/shm' if sys.platform == 'linux' else None)
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name).resolve()
        for kind, (name, _, _) in ORIGINALS.items():
            path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.originals[kind])
        return root

    def test_import_only_defines_without_source_reads_writes_or_dispatch(self):
        with ExitStack() as stack:
            for owner, names in ((Path, ('read_bytes', 'read_text', 'open', 'write_bytes',
                                         'write_text', 'mkdir', 'unlink')),
                                 (builtins, ('open',)), (io, ('open',)), (os, ('open',))):
                for name in names:
                    stack.enter_context(mock.patch.object(owner, name,
                        side_effect=AssertionError('Import did I/O: ' + name)))
            subject = module(self.raw, ROOT / LAUNCHER, '_d193_import_no_effect')
        for name in ('parse_request', 'project_caller', 'project_adapter', 'project_remote',
                     'read_original', 'load_caller', 'main'):
            self.assertTrue(callable(getattr(subject, name)))

    def test_every_projector_matches_independent_order_counts_bytes_and_hash(self):
        for kind, original in self.originals.items():
            with self.subTest(kind=kind), ExitStack() as stack:
                for owner, names in ((Path, ('read_bytes', 'read_text', 'open', 'write_bytes',
                                             'write_text', 'mkdir', 'unlink')),
                                     (builtins, ('open',)), (io, ('open',)), (os, ('open',))):
                    for name in names:
                        stack.enter_context(mock.patch.object(owner, name,
                            side_effect=AssertionError('Projection did I/O: ' + name)))
                expected = expected_projection(kind, original)
                actual = getattr(self.subject, 'project_' + kind)(original)
                self.assertIs(type(actual), bytes)
                self.assertEqual(actual, expected)
                self.assertEqual(digest(original), ORIGINALS[kind][2])

    def test_projectors_reject_nonbytes_drift_line_endings_missing_extra_occurrences(self):
        for kind, raw in self.originals.items():
            project = getattr(self.subject, 'project_' + kind)
            bad = [None, True, 1, raw.decode(), bytearray(raw), memoryview(raw), b'',
                   raw + b'\n', raw[:-1], b'x' + raw[1:], raw.replace(b'\r\n', b'\n')]
            for old, new, _ in SUBSTITUTIONS[kind]:
                bad.extend((raw.replace(old, new, 1), raw + b'\n# ' + old))
            for value in bad:
                if type(value) is bytes and value == raw:
                    continue
                with self.subTest(kind=kind, bad_type=type(value).__name__):
                    self.reject(lambda: project(value))

    def test_cli_exact_forms_and_main_invalid_forms_precede_source_load(self):
        for action in ('--check-only', '--execute'):
            args = [action, '--reviewed-head', HEAD]
            self.assertEqual(self.subject.parse_request(args), (action, HEAD))
        invalid = (None, True, '', [], ['--execute'], ('--execute', '--reviewed-head', HEAD),
            ['--execute', '--reviewed-head', HEAD.upper()], ['--execute', '--reviewed-head', 1],
            ['--execute', '--reviewed-head', HEAD + '0'], ['--reviewed-head', HEAD, '--execute'],
            ['--execute', '--reviewed-head', HEAD, '--upload'], ['--help'])
        with mock.patch.object(self.subject, 'load_caller', side_effect=AssertionError('Invalid CLI loaded')):
            for args in invalid:
                with self.subTest(args=args):
                    self.reject(lambda: self.subject.parse_request(args))
                    self.reject(lambda: self.subject.main(args))

    def test_main_requires_no_bytecode_then_delegates_once_and_preserves_result_error(self):
        args = ['--check-only', '--reviewed-head', HEAD]
        with mock.patch.object(sys, 'dont_write_bytecode', False), mock.patch.object(
                self.subject, 'load_caller', side_effect=AssertionError('Bytecode mode loaded')):
            self.reject(lambda: self.subject.main(args))
        for action in ('--check-only', '--execute'):
            args = [action, '--reviewed-head', HEAD]
            private = types.SimpleNamespace(main=mock.Mock(return_value=71))
            with mock.patch.object(self.subject, 'load_caller', return_value=private) as loader:
                self.assertEqual(self.subject.main(args), 71)
                loader.assert_called_once_with(root=self.subject.ROOT)
                private.main.assert_called_once_with(args)
        primary = RuntimeError('delegated exact failure')
        with mock.patch.object(self.subject, 'load_caller', return_value=types.SimpleNamespace(
                main=mock.Mock(side_effect=primary))):
            with self.assertRaises(RuntimeError) as caught:
                self.subject.main(args)
            self.assertIs(caught.exception, primary)

    def test_checked_originals_accept_exact_files_and_reject_unlisted_names_before_read(self):
        root = self.scratch()
        for kind, (name, _, _) in ORIGINALS.items():
            self.assertEqual(self.subject.read_original(name, root=root), self.originals[kind])
        invalid = (None, True, Path(ORIGINALS['caller'][0]), '../tools/compile_app_motor_fault.py',
                   '/tools/compile_app_motor_fault.py', 'tools//compile_app_motor_fault.py',
                   'tools\\compile_app_motor_fault.py', LAUNCHER, CONTRACT)
        with mock.patch.object(Path, 'open', side_effect=AssertionError('Invalid name was opened')):
            for name in invalid:
                with self.subTest(name=name):
                    self.reject(lambda: self.subject.read_original(name, root=root))

    def test_each_original_missing_empty_oversize_and_content_drift_refuse(self):
        root = self.scratch()
        for kind, (name, _, _) in ORIGINALS.items():
            path = root / name
            path.unlink(); self.reject(lambda: self.subject.read_original(name, root=root))
            for raw in (b'', b'x' * 65537, self.originals[kind] + b'\n', b'x' + self.originals[kind][1:]):
                path.write_bytes(raw)
                with self.subTest(name=name, size=len(raw)):
                    self.reject(lambda: self.subject.read_original(name, root=root))
            path.write_bytes(self.originals[kind])

    def test_original_symlink_hardlink_and_parent_link_refuse(self):
        root = self.scratch()
        for kind, (name, _, _) in ORIGINALS.items():
            path = root / name; saved = root / (kind + '-retained')
            path.rename(saved)
            try:
                path.symlink_to(saved)
                self.reject(lambda: self.subject.read_original(name, root=root))
                path.unlink(); os.link(saved, path)
                self.reject(lambda: self.subject.read_original(name, root=root))
                path.unlink()
            finally:
                if path.is_symlink() or path.exists(): path.unlink()
                saved.rename(path)
        folder = root / 'tools'; saved = root / 'plain-tools'; folder.rename(saved)
        try:
            folder.symlink_to(saved, target_is_directory=True)
            self.reject(lambda: self.subject.read_original(ORIGINALS['caller'][0], root=root))
        finally:
            folder.unlink(); saved.rename(folder)

    def test_reparse_on_file_parent_and_fixture_root_refuses(self):
        root = self.scratch(); name = ORIGINALS['caller'][0]; original = Path.lstat
        class Reparse:
            def __init__(self, value):
                self.value = value
                self.st_file_attributes = getattr(value, 'st_file_attributes', 0) | 1024
            def __getattr__(self, key): return getattr(self.value, key)
        for target in (root / name, root / 'tools', root):
            def lstat(path, *args, **kwargs):
                value = original(path, *args, **kwargs)
                return Reparse(value) if path == target else value
            with self.subTest(target=target), mock.patch.object(Path, 'lstat', lstat):
                self.reject(lambda: self.subject.read_original(name, root=root))

    def test_descriptor_identity_and_same_api_ctime_drift_refuse(self):
        root = self.scratch(); name = ORIGINALS['caller'][0]; original = os.fstat
        class Changed:
            def __init__(self, value, field):
                self.value = value
                setattr(self, field, getattr(value, field) + 1)
            def __getattr__(self, key): return getattr(self.value, key)
        for field in ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'):
            calls = []
            def fstat(fd):
                value = original(fd); calls.append(True)
                return Changed(value, field) if len(calls) == 2 else value
            with self.subTest(field=field), mock.patch.object(os, 'fstat', fstat):
                self.reject(lambda: self.subject.read_original(name, root=root))

    def test_read_bound_primary_read_error_and_secondary_close_error_are_truthful(self):
        root = self.scratch(); name = ORIGINALS['caller'][0]
        original, fdopen = Path.open, os.fdopen
        primary, secondary = OSError('primary read failure'), OSError('secondary close failure')
        for mode in ('close', 'read', 'check'):
            requested = []
            class Stream:
                def __init__(self, actual): self.actual = actual
                def fileno(self): return self.actual.fileno()
                def read(self, size=-1):
                    requested.append(size)
                    if mode == 'read': raise primary
                    raw = self.actual.read(size)
                    return b'x' + raw[1:] if mode == 'check' else raw
                def close(self): self.actual.close(); raise secondary
                def __enter__(self): return self
                def __exit__(self, *_): self.close()
            def opened(path, *args, **kwargs): return Stream(original(path, *args, **kwargs))
            def fdopened(fd, *args, **kwargs): return Stream(fdopen(fd, *args, **kwargs))
            with self.subTest(mode=mode), \
                    mock.patch.object(Path, 'open', opened), mock.patch.object(os, 'fdopen', fdopened):
                with self.assertRaises(REJECT) as caught:
                    self.subject.read_original(name, root=root)
                if mode == 'check':
                    self.assertIsNot(caught.exception, secondary)
                else:
                    self.assertIs(caught.exception, primary if mode == 'read' else secondary)
            self.assertTrue(requested)
            self.assertTrue(all(0 < size <= 65537 for size in requested))

    def test_opened_descriptor_drift_rejects_before_any_read(self):
        root = self.scratch(); name = ORIGINALS['caller'][0]
        fstat, fdopen, opened = os.fstat, os.fdopen, Path.open
        class Different:
            def __init__(self, value): self.value = value; self.st_ino = value.st_ino + 1
            def __getattr__(self, key): return getattr(self.value, key)
        class NoRead:
            def __init__(self, actual): self.actual = actual
            def fileno(self): return self.actual.fileno()
            def close(self): return self.actual.close()
            def read(self, *_): raise AssertionError('Drifted descriptor was read')
            def __enter__(self): return self
            def __exit__(self, *_): self.close()
        with mock.patch.object(os, 'fstat', lambda fd: Different(fstat(fd))), \
                mock.patch.object(os, 'fdopen', lambda *args, **kwargs: NoRead(fdopen(*args, **kwargs))), \
                mock.patch.object(Path, 'open', lambda *args, **kwargs: NoRead(opened(*args, **kwargs))):
            self.reject(lambda: self.subject.read_original(name, root=root))

    @unittest.skipUnless(sys.platform == 'linux', 'FIFO swap fixture uses Linux nonblocking descriptors')
    def test_regular_to_fifo_swap_is_nonblocking_and_never_read(self):
        root = self.scratch(); name = ORIGINALS['caller'][0]
        path = root / name; saved = root / 'retained-caller'
        opened, fdopen = os.open, os.fdopen
        attempts, reads = [], []
        class NoRead:
            def __init__(self, actual): self.actual = actual
            def fileno(self): return self.actual.fileno()
            def close(self): return self.actual.close()
            def read(self, *_): reads.append(True); raise AssertionError('FIFO was read')
            def __enter__(self): return self
            def __exit__(self, *_): self.close()
        def swapped(candidate, flags, *args, **kwargs):
            if Path(candidate) == path:
                self.assertTrue(flags & os.O_NONBLOCK, 'Bootstrap open must not wait on swapped FIFO')
                attempts.append(flags); path.rename(saved); os.mkfifo(path)
            return opened(candidate, flags, *args, **kwargs)
        try:
            with mock.patch.object(os, 'open', swapped), mock.patch.object(os, 'fdopen',
                    lambda *args, **kwargs: NoRead(fdopen(*args, **kwargs))):
                self.reject(lambda: self.subject.read_original(name, root=root))
            self.assertEqual(len(attempts), 1); self.assertFalse(reads)
        finally:
            if saved.exists(): path.unlink(); saved.rename(path)

    def test_all_three_checks_complete_before_execution_and_failure_executes_nothing(self):
        actual_exec = builtins.exec
        for failed_kind in ('caller', 'adapter', 'remote'):
            seen, executed = [], []
            def execute(*args): executed.append(True); return actual_exec(*args)
            self.subject.__dict__['__builtins__']['exec'] = execute
            with ExitStack() as stack:
                for kind in ORIGINALS:
                    project = getattr(self.subject, 'project_' + kind)
                    def wrapped(raw, kind=kind, project=project):
                        seen.append(kind)
                        if kind == failed_kind: raise ValueError('Deliberate rejected projection')
                        return project(raw)
                    stack.enter_context(mock.patch.object(self.subject, 'project_' + kind, wrapped))
                self.reject(lambda: self.subject.load_caller(root=ROOT))
            self.assertIn(failed_kind, seen); self.assertFalse(executed)
        seen, executed = [], []
        with ExitStack() as stack:
            for kind in ORIGINALS:
                project = getattr(self.subject, 'project_' + kind)
                def wrapped(raw, kind=kind, project=project): seen.append(kind); return project(raw)
                stack.enter_context(mock.patch.object(self.subject, 'project_' + kind, wrapped))
            def execute(*args):
                self.assertEqual(set(seen), set(ORIGINALS)); executed.append(True)
                return actual_exec(*args)
            self.subject.__dict__['__builtins__']['exec'] = execute
            self.subject.load_caller(root=ROOT)
        self.assertEqual(len(executed), 1)

    def test_private_loading_preserves_modules_defaults_original_paths_and_hard_pins(self):
        root = self.scratch()
        sentinel = types.ModuleType('sentinel'); sentinel.unchanged = object()
        shared_names = ('compile_app_motor_fault', 'app_motor_fault_static_policy',
                        'app_motor_fault_compile_remote')
        with mock.patch.dict(sys.modules, {name: sentinel for name in shared_names}):
            original_dict = dict(sentinel.__dict__)
            first = self.subject.load_caller(root=root)
            second = self.subject.load_caller(root=root)
            self.assertEqual(sentinel.__dict__, original_dict)
            self.assertTrue(all(sys.modules[name] is sentinel for name in shared_names))
            self.assertFalse(any(value is first or value is second for value in sys.modules.values()))
        self.assertIsInstance(first, types.ModuleType); self.assertIsNot(first, second)
        self.assertIsNot(first.CompileDiagnostic, second.CompileDiagnostic)
        self.assertNotEqual(first.__name__, '__main__')
        self.assertEqual(Path(first.__file__), root / ORIGINALS['caller'][0])
        self.assertEqual(first.ROOT, root)
        self.assertEqual(first.CompileDiagnostic.__init__.__kwdefaults__['root'], root)
        self.assertEqual(first.PROJECT, PROJECT); self.assertEqual(first.CALLER, LAUNCHER)
        self.assertEqual(first.CONTRACT, CONTRACT); self.assertEqual(first.RAW, RAW)
        self.assertEqual(first.ATTEMPT, 'app-motor-observe-static01'); self.assertEqual(first.REMOTE, REMOTE)
        self.assertEqual(first.ADAPTER, ORIGINALS['adapter'][0])
        self.assertEqual(first.REMOTE_HELPER, ORIGINALS['remote'][0])
        inherited = module(self.originals['caller'], ROOT / ORIGINALS['caller'][0], '_d193_old_pins')
        expected = dict(inherited.HARD_PINS)
        expected.update({ORIGINALS[k][0]: ORIGINALS[k][2] for k in ('caller', 'remote')})
        self.assertEqual(first.HARD_PINS, expected)
        self.assertEqual(first.REQUIRED, {LAUNCHER, CONTRACT, ORIGINALS['remote'][0],
            'tools/board_tool.py', 'tools/app_build_commands.json', 'tools/app_build_pins.json', *expected})
        self.assertNotIn(LAUNCHER, first.HARD_PINS); self.assertNotIn(CONTRACT, first.HARD_PINS)


def additional_owner_cases(oracle):
    class NewOwnerContract(oracle.CallerFixture):
        def test_added_original_caller_remote_hard_pins_cannot_be_manifest_repaired(self):
            for kind in ('caller', 'remote'):
                name = ORIGINALS[kind][0]; path = self.root / name; original = path.read_bytes()
                path.write_bytes(original + b'\n# drift\n')
                self.manifest(files=dict(self.files, **{name: digest(path.read_bytes())}))
                with self.subTest(name=name): self.reject(lambda: self.owner().check())
                path.write_bytes(original)

        def test_owner_code_preserves_originals_and_payload_projects_only_two_sources(self):
            owner = self.owner(); owner.local(); owner.prepare()
            for kind, (name, _, _) in ORIGINALS.items():
                self.assertEqual(owner.code[name], checked(ROOT / name, ORIGINALS[kind][2]))
            program = owner.artifact_program()
            assignments = {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse(program).body
                if isinstance(n, ast.Assign) and len(n.targets) == 1 and
                isinstance(n.targets[0], ast.Name) and n.targets[0].id in ('token', 'expected', 'source_sha')}
            packed = base64.b64decode(assignments['token'], validate=True)
            raw = zlib.decompress(packed); payload = json.loads(raw)
            self.assertEqual(digest(raw), assignments['expected'])
            source = payload['source'].encode()
            self.assertEqual(digest(source), PROJECTED['remote'][1])
            self.assertEqual(assignments['source_sha'], PROJECTED['remote'][1])
            self.assertEqual(source, expected_projection('remote', owner.code[ORIGINALS['remote'][0]]))
            self.assertEqual(payload['bundle']['adapter'].encode(),
                             expected_projection('adapter', owner.code[ORIGINALS['adapter'][0]]))
            for key, name in (('helper', self.subject.READER), ('extension', self.subject.EXTENSION),
                              ('base', self.subject.BASE_ARTIFACTS)):
                self.assertEqual(payload['bundle'][key].encode(), owner.code[name])
            self.assertEqual(set(payload), {'source', 'bundle'})
            self.assertEqual(set(payload['bundle']), {'helper', 'adapter', 'extension', 'base'})

        def test_old_manifest_source_tree_and_artifact_packets_remain_rejected(self):
            self.manifest(schema='app-motor-fault-static-inputs-v1')
            self.reject(lambda: self.owner().check()); self.manifest()
            owner = self.owner(); owner.local()
            old = module(checked(ROOT / REMOTE_ORACLE, REMOTE_ORACLE_SHA), ROOT / REMOTE_ORACLE,
                         '_d193_original_artifact_oracle')
            self.reject(lambda: owner.validate_artifact_reply(json.dumps(old.synthetic_reply())))
            for field, value in (('schema', 'app-motor-fault-static-artifacts-v1'),
                                 ('build_path', REMOTE.replace('observe', 'fault') + '/build'),
                                 ('artifacts_path', REMOTE.replace('observe', 'fault') + '/artifacts')):
                reply = self.remote_fixture.synthetic_reply(); reply[field] = value
                self.reject(lambda: owner.validate_artifact_reply(json.dumps(reply)))
            self.assertNotIn('bench/app_motor_fault/app_motor_fault.ino', self.files)
            self.assertIn('bench/app_motor_observe/app_motor_observe.ino', self.files)

    return NewOwnerContract


def load_tests(loader, standard, pattern):
    oracle = inherited_oracle()
    suite = unittest.TestSuite([standard])
    names = ('LocalAdmissionContract', 'ArtifactReplyContract', 'PreflightContract', 'ExecutionContract')
    inherited = unittest.TestSuite(loader.loadTestsFromTestCase(getattr(oracle, name)) for name in names)
    if inherited.countTestCases() != 40:
        raise AssertionError('Established D188 assertion inventory changed')
    suite.addTests(inherited)
    suite.addTests(loader.loadTestsFromTestCase(additional_owner_cases(oracle)))
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
