# Independently checks the human-only root02 wrapper against its public contract.
# Models credentials, descriptors and original cleanup work without privilege or board access.
# Freeze this oracle before first execution with Linux Python -I -B.
import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import marshal
import os
from pathlib import Path
import posixpath
import stat
import subprocess
import sys
import types
import unittest
from unittest import mock
import zlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STAGE = '/home/arduino/sumox26_codex_build/cleanup-app-inert-root02'
SUCCESS = 'REMOVED_EXACT_STALE_COPIES'
USER = {'uids': [1000, 1000, 0], 'gids': [1000, 1000, 0]}
FINAL = {'uids': [1000, 1000, 1000], 'gids': [1000, 1000, 1000]}
PINS = {
    'cleanup_remoteocd01.py': (HERE / 'cleanup_remoteocd01.py', 7873,
        '23ef85ae3c386cc76751eea0fb18a90148a6fe513e3e8c753d527c06efcbbe95'),
    'static_remote.py': (ROOT / 'state/analysis/P7_static_link_probe_raw/static_remote.py', 33321,
        '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'),
}
SCAN_OLD = '                except FileNotFoundError:\n                    continue\n'
SCAN_NEW = '                except FileNotFoundError:\n                    raise\n'
PROJECTED_SHA = '51286ad414794e82f3161bed16cbb47dca421e831316e053a7eab967469f602e'


def source(name):
    path, size, digest = PINS[name]
    raw = path.read_bytes()
    if len(raw) != size or hashlib.sha256(raw).hexdigest() != digest:
        raise AssertionError('Frozen dependency changed: ' + name)
    return raw


class FakeOS:
    """Small descriptor and credential model; absent syscalls fail closed."""
    def __init__(self):
        self.uids = [0, 0, 0]
        self.gids = [0, 0, 0]
        self.groups = [0]
        self.calls = []
        self.fail = {}
        self.ignore = set()
        self.records = {}
        self.handles = {}
        self.offsets = {}
        self.closed = []
        self.next_fd = 10
        for directory in ('/', '/home', '/home/arduino',
                          '/home/arduino/sumox26_codex_build', STAGE):
            owner = 1000 if directory.startswith('/home/arduino') else 0
            self.add(directory, None, uid=owner, gid=owner)
        for name in PINS:
            self.add(STAGE + '/' + name, source(name))

    def __getattr__(self, name):
        if name.startswith('O_') or name in ('SEEK_SET', 'SEEK_CUR', 'SEEK_END'):
            return getattr(os, name)
        raise AssertionError('Unmodeled syscall: ' + name)

    def add(self, path, raw, uid=1000, gid=1000):
        self.records[path] = types.SimpleNamespace(
            st_mode=(stat.S_IFDIR | 0o755) if raw is None else (stat.S_IFREG | 0o644),
            st_uid=uid, st_gid=gid, st_nlink=2 if raw is None else 1,
            st_size=0 if raw is None else len(raw), st_dev=34,
            st_ino=len(self.records) + 101, st_mtime_ns=100, st_ctime_ns=100, raw=raw)

    def op(self, name, args):
        self.calls.append((name, args, tuple(self.uids), tuple(self.gids)))
        error = self.fail.get((name, args))
        if error is not None:
            raise error
        return (name, args) not in self.ignore

    def getresuid(self):
        return tuple(self.uids)

    def getresgid(self):
        return tuple(self.gids)

    def getuid(self):
        return self.uids[0]

    def geteuid(self):
        return self.uids[1]

    def getgid(self):
        return self.gids[0]

    def getegid(self):
        return self.gids[1]

    def getgroups(self):
        return self.groups[:]

    def setgroups(self, values):
        if self.op('setgroups', tuple(values)):
            self.groups = list(values)

    def setresgid(self, *values):
        if self.op('setresgid', values):
            self.gids = list(values)

    def setresuid(self, *values):
        if self.op('setresuid', values):
            self.uids = list(values)

    def seteuid(self, value):
        if self.op('seteuid', (value,)):
            self.uids[1] = value

    def path(self, path, dir_fd=None):
        path = os.fspath(path)
        result = posixpath.normpath(posixpath.join(self.handles[dir_fd], path)
                                    if dir_fd is not None else path)
        if result not in self.records:
            raise FileNotFoundError(result)
        return result

    def open(self, path, flags, mode=0o777, *, dir_fd=None):
        resolved = self.path(path, dir_fd)
        if not flags & os.O_NOFOLLOW:
            raise AssertionError('Every descriptor open requires O_NOFOLLOW')
        if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
            raise AssertionError('Source reader attempted a write')
        record = self.records[resolved]
        if stat.S_ISLNK(record.st_mode):
            raise OSError('Modeled nofollow refusal')
        if flags & os.O_DIRECTORY and not stat.S_ISDIR(record.st_mode):
            raise NotADirectoryError(resolved)
        self.op('open', (resolved,))
        fd = self.next_fd
        self.next_fd += 1
        self.handles[fd], self.offsets[fd] = resolved, 0
        return fd

    def fstat(self, fd):
        self.op('fstat', (self.handles[fd],))
        return self.records[self.handles[fd]]

    def stat(self, path, *, dir_fd=None, follow_symlinks=True):
        if follow_symlinks:
            raise AssertionError('Named source stat must not follow links')
        return self.records[self.path(path, dir_fd)]

    def read(self, fd, count):
        self.op('read', (self.handles[fd],))
        raw = self.records[self.handles[fd]].raw
        offset = self.offsets[fd]
        value = raw[offset:offset + count]
        self.offsets[fd] += len(value)
        return value

    def close(self, fd):
        path = self.handles.pop(fd)
        self.offsets.pop(fd)
        self.closed.append(fd)
        self.op('close', (path,))

    def listdir(self, path):
        parent = self.handles[path] if isinstance(path, int) else path
        return [posixpath.basename(name) for name in self.records
                if name != parent and posixpath.dirname(name) == parent]

    def unlink(self, name, *, dir_fd=None):
        path = self.path(name, dir_fd)
        if self.uids[1] != 1000 or self.gids[1] != 1000:
            raise AssertionError('Original unlink ran with privileged identity')
        self.op('unlink', (path,))
        del self.records[path]

    def rmdir(self, name, *, dir_fd=None):
        path = self.path(name, dir_fd)
        if self.uids[1] != 1000 or self.gids[1] != 1000 or self.listdir(path):
            raise AssertionError('Original rmdir identity/content invalid')
        self.op('rmdir', (path,))
        del self.records[path]

    def fsync(self, fd):
        self.op('fsync', (self.handles[fd],))

    @property
    def path_module(self):
        return types.SimpleNamespace(lexists=lambda path: path in self.records)


def normalized_code(code):
    constants = tuple(normalized_code(item) if isinstance(item, types.CodeType) else item
                      for item in code.co_consts)
    return code.replace(co_filename='/independent/source.py', co_consts=constants)


class ProcFixture:
    def __init__(self, *, name='adbd', target='/unrelated', denied=False, missing=False, departed=False):
        self.comm, self.target = name, target
        self.denied, self.missing, self.departed = denied, missing, departed
        self.stat_calls = 0

    def node(self, path):
        owner = self
        class Node:
            def __init__(self, name):
                self.path = name
                self.name = posixpath.basename(name)
            def __truediv__(self, name):
                return Node(self.path + '/' + name)
            def iterdir(self):
                if self.path == '/proc':
                    return iter([Node('/proc/637')])
                if self.path == '/proc/637/fd':
                    if owner.denied:
                        raise PermissionError('modeled same-user fd denied')
                    return iter([Node('/proc/637/fd/7')])
                raise AssertionError('Unmodeled proc listing: ' + self.path)
            def read_text(self):
                if self.path != '/proc/637/comm':
                    raise AssertionError('Unmodeled proc text')
                return owner.comm + '\n'
            def stat(self):
                owner.stat_calls += 1
                if owner.departed and owner.stat_calls > 1:
                    raise FileNotFoundError('PID departed')
                return types.SimpleNamespace(st_uid=1000)
        return Node(path)

    def readlink(self, node):
        if self.missing:
            raise FileNotFoundError('modeled missing cwd or FD')
        return self.target


def load_subject():
    if not sys.platform.startswith('linux') or not sys.flags.dont_write_bytecode or not sys.flags.isolated:
        raise RuntimeError('Linux Python -I -B required; no actual credentials may change')
    spec = importlib.util.spec_from_file_location('_independent_cleanup_root02', HERE / 'cleanup_root02.py')
    module = importlib.util.module_from_spec(spec)
    with contextlib.ExitStack() as stack:
        for name in ('setresuid', 'setresgid', 'seteuid', 'setuid', 'setgid',
                     'setgroups', 'unlink', 'rmdir', 'system'):
            stack.enter_context(mock.patch.object(os, name, side_effect=AssertionError('Import has side effect: ' + name)))
        stack.enter_context(mock.patch.object(subprocess, 'run', side_effect=AssertionError('Native child forbidden')))
        stack.enter_context(mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Native child forbidden')))
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return module


class Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject = load_subject()

    def setUp(self):
        self.os = FakeOS()
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.object(self.subject, 'os', self.os))
        self.stack.enter_context(mock.patch.object(sys, 'argv', [STAGE + '/cleanup_root02.py']))
        self.stack.enter_context(mock.patch.object(subprocess, 'run', side_effect=AssertionError('Native child forbidden')))
        self.stack.enter_context(mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Native child forbidden')))

    def user(self):
        self.os.uids, self.os.gids = USER['uids'][:], USER['gids'][:]

    def original(self, behavior=None):
        module = types.ModuleType('original_cleanup_fixture')
        module.processes = mock.Mock(return_value={'checked': 3})
        module.cleanup = object()
        module.inventory = object()
        module.PINS = object()
        module.main_calls = 0
        def main():
            module.main_calls += 1
            self.assertEqual(self.subject.credentials(), USER)
            self.assertEqual(len(sys.argv), 2)
            self.assertEqual(zlib.decompress(base64.b64decode(sys.argv[1], validate=True)), source('static_remote.py'))
            if behavior is not None:
                return behavior(module)
            report = module.processes()
            self.assertEqual(self.subject.credentials(), USER)
            print(json.dumps({'schema': 'd190-exact-scratch-cleanup-v1', 'status': SUCCESS,
                              'removed': ['a', 'b', 'c'], 'first_error': None, 'scan': report}))
            return 0
        module.main = main
        self.stack.enter_context(mock.patch.object(self.subject, 'load_cleanup', return_value=(module, source('static_remote.py'))))
        return module

    def test_import_safe_and_original_sources_still_pinned(self):
        for name in PINS:
            self.assertTrue(source(name))
        self.assertEqual(self.os.calls, [])

    def test_credentials_are_full_real_effective_saved_lists(self):
        self.os.uids, self.os.gids = [4, 5, 6], [7, 8, 9]
        self.assertEqual(self.subject.credentials(), {'uids': [4, 5, 6], 'gids': [7, 8, 9]})

    def test_enter_user_clears_groups_and_sets_gid_before_uid(self):
        self.subject.enter_user()
        self.assertEqual(self.subject.credentials(), USER)
        self.assertEqual(self.os.groups, [1000])
        selected = [(name, args) for name, args, unused, unused2 in self.os.calls]
        self.assertEqual(selected, [('setgroups', (1000,)), ('setresgid', (1000, 1000, 0)),
                                    ('setresuid', (1000, 1000, 0))])

    def test_enter_user_rejects_any_wrong_initial_uid_or_gid_without_mutation(self):
        for field in ('uids', 'gids'):
            for index in range(3):
                with self.subTest(field=field, index=index):
                    self.os.uids, self.os.gids, self.os.calls = [0, 0, 0], [0, 0, 0], []
                    getattr(self.os, field)[index] = 1000
                    with self.assertRaises(Exception):
                        self.subject.enter_user()
                    self.assertEqual(self.os.calls, [])

    def test_enter_user_detects_syscall_failure_and_silent_wrong_result(self):
        for name, args in (('setgroups', (1000,)), ('setresgid', (1000, 1000, 0)),
                           ('setresuid', (1000, 1000, 0))):
            with self.subTest(name=name):
                self.os.uids, self.os.gids = [0, 0, 0], [0, 0, 0]
                self.os.fail = {(name, args): PermissionError('entry denied')}
                with self.assertRaises(Exception):
                    self.subject.enter_user()
        self.os.fail = {}
        self.os.uids, self.os.gids = [0, 0, 0], [0, 0, 0]
        self.os.ignore = {('setresuid', (1000, 1000, 0))}
        with self.assertRaises(Exception):
            self.subject.enter_user()

    def test_observe_elevates_only_euid_calls_once_and_restores(self):
        self.user()
        records = []
        def scan():
            self.assertEqual(self.subject.credentials(), {'uids': [1000, 0, 0], 'gids': USER['gids']})
            return {'process_names_checked': 19, 'same_uid_handles_checked': 4}
        original = mock.Mock(side_effect=scan)
        result = self.subject.observe(original, records)
        original.assert_called_once_with()
        self.assertEqual(result['process_names_checked'], 19)
        self.assertEqual(self.subject.credentials(), USER)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['before'], USER)
        self.assertEqual(records[0]['during'], {'uids': [1000, 0, 0], 'gids': USER['gids']})
        self.assertEqual(records[0]['after'], USER)
        self.assertEqual(records[0]['errors'], [])
        self.assertEqual(records[0]['result'], result)

    def test_observe_does_not_skip_permission_or_use_rejection(self):
        for error in (PermissionError('same-user fd denied'), ValueError('Scratch directory is in use'),
                      ValueError('Native process is active')):
            with self.subTest(error=str(error)):
                self.user()
                records = []
                with self.assertRaises(type(error)) as seen:
                    self.subject.observe(mock.Mock(side_effect=error), records)
                self.assertIs(seen.exception, error)
                self.assertEqual(self.subject.credentials(), USER)
                self.assertEqual(len(records), 1)
                self.assertTrue(any(row['message'] == str(error) for row in records[0]['errors']))

    def test_observe_wrong_entry_never_calls_original_or_elevates(self):
        records, scan = [], mock.Mock()
        with self.assertRaises(Exception):
            self.subject.observe(scan, records)
        scan.assert_not_called()
        self.assertFalse(any(name == 'seteuid' and args == (0,) for name, args, unused, unused2 in self.os.calls))

    def test_observe_elevation_failure_still_restores_and_records(self):
        self.user()
        self.os.fail[('seteuid', (0,))] = PermissionError('elevation denied')
        records, scan = [], mock.Mock()
        with self.assertRaises(Exception):
            self.subject.observe(scan, records)
        scan.assert_not_called()
        self.assertTrue(any(name == 'seteuid' and args == (1000,) for name, args, unused, unused2 in self.os.calls))
        self.assertEqual(self.subject.credentials(), USER)
        self.assertEqual(records[0]['errors'][0]['message'], 'elevation denied')

    def test_observe_scan_and_restore_failure_preserve_both_and_raise_first(self):
        self.user()
        first = PermissionError('scan first')
        self.os.fail[('seteuid', (1000,))] = PermissionError('restore second')
        records = []
        with self.assertRaises(PermissionError) as seen:
            self.subject.observe(mock.Mock(side_effect=first), records)
        self.assertIs(seen.exception, first)
        messages = [row['message'] for row in records[0]['errors']]
        self.assertIn('scan first', messages)
        self.assertIn('restore second', messages)

    def test_observe_restoration_failure_refuses_success_and_silent_credential_drift(self):
        for failure in ('error', 'silent'):
            with self.subTest(failure=failure):
                self.user()
                self.os.fail, self.os.ignore = {}, set()
                if failure == 'error':
                    self.os.fail[('seteuid', (1000,))] = PermissionError('restore denied')
                else:
                    self.os.ignore.add(('seteuid', (1000,)))
                records = []
                with self.assertRaises(Exception):
                    self.subject.observe(lambda: {'checked': True}, records)
                self.assertTrue(records[0]['errors'])

    def test_observe_gid_drift_is_rejected_even_after_euid_restoration(self):
        self.user()
        def changed():
            self.os.gids[1] = 0
            return {'checked': True}
        records = []
        with self.assertRaises(Exception):
            self.subject.observe(changed, records)
        self.assertEqual(self.os.uids, USER['uids'])
        self.assertTrue(records[0]['errors'])

    def test_drop_privilege_removes_saved_root_and_attempts_both_on_failure(self):
        self.user()
        self.assertEqual(self.subject.drop_privilege(), [])
        self.assertEqual(self.subject.credentials(), FINAL)
        self.user()
        self.os.fail[('setresgid', (1000, 1000, 1000))] = PermissionError('group drop denied')
        errors = self.subject.drop_privilege()
        self.assertTrue(any(row['message'] == 'group drop denied' for row in errors))
        self.assertEqual(self.os.uids, FINAL['uids'])

    def test_drop_privilege_detects_silent_retained_saved_uid(self):
        self.user()
        self.os.ignore.add(('setresuid', (1000, 1000, 1000)))
        self.assertTrue(self.subject.drop_privilege())

    def test_read_source_exact_two_dependencies_and_descriptor_closure(self):
        for name in PINS:
            self.assertEqual(self.subject.read_source(name), source(name))
            self.assertFalse(self.os.handles)
        self.assertTrue(self.os.closed)

    def test_read_source_refuses_arbitrary_names_before_open(self):
        for name in ('../cleanup_remoteocd01.py', STAGE + '/static_remote.py', 'other.py', '', 'a/static_remote.py'):
            with self.subTest(name=name):
                self.os.calls = []
                with self.assertRaises(Exception):
                    self.subject.read_source(name)
                self.assertEqual(self.os.calls, [])

    def test_read_source_refuses_nonplain_ancestry_and_wrong_owner(self):
        for path, field, bad in ((STAGE, 'st_mode', stat.S_IFLNK | 0o755),
                                 ('/home/arduino', 'st_uid', 0),
                                 (STAGE, 'st_uid', 0),
                                 (STAGE + '/static_remote.py', 'st_mode', stat.S_IFDIR | 0o755),
                                 (STAGE + '/static_remote.py', 'st_uid', 0),
                                 (STAGE + '/static_remote.py', 'st_gid', 0),
                                 (STAGE + '/static_remote.py', 'st_nlink', 2),
                                 (STAGE + '/static_remote.py', 'st_size', 1)):
            with self.subTest(path=path, field=field):
                record = self.os.records[path]
                old = getattr(record, field)
                setattr(record, field, bad)
                try:
                    with self.assertRaises(Exception):
                        self.subject.read_source('static_remote.py')
                    self.assertFalse(self.os.handles)
                finally:
                    setattr(record, field, old)

    def test_read_source_hash_corruption_and_read_error_close_all_descriptors(self):
        path = STAGE + '/static_remote.py'
        raw = self.os.records[path].raw
        self.os.records[path].raw = bytes([raw[0] ^ 1]) + raw[1:]
        with self.assertRaises(Exception):
            self.subject.read_source('static_remote.py')
        self.assertFalse(self.os.handles)
        self.os.records[path].raw = raw
        self.os.fail[('read', (path,))] = OSError('read denied')
        with self.assertRaises(Exception):
            self.subject.read_source('static_remote.py')
        self.assertFalse(self.os.handles)

    def test_read_source_stat_drift_is_refused(self):
        path = STAGE + '/static_remote.py'
        original_read = self.os.read
        def changed(fd, count):
            raw = original_read(fd, count)
            if self.os.handles[fd] == path:
                self.os.records[path].st_mtime_ns += 1
            return raw
        with mock.patch.object(self.os, 'read', side_effect=changed):
            with self.assertRaises(Exception):
                self.subject.read_source('static_remote.py')
        self.assertFalse(self.os.handles)

    def test_read_source_attempts_every_close_preserving_first_error(self):
        path = STAGE + '/static_remote.py'
        first = OSError('read first')
        self.os.fail[('read', (path,))] = first
        self.os.fail[('close', (path,))] = OSError('close second')
        with self.assertRaises(OSError) as seen:
            self.subject.read_source('static_remote.py')
        self.assertIs(seen.exception, first)
        self.assertFalse(self.os.handles)
        self.os.fail = {('close', (path,)): OSError('close sole')}
        with self.assertRaises(OSError) as seen:
            self.subject.read_source('static_remote.py')
        self.assertEqual(str(seen.exception), 'close sole')
        self.assertFalse(self.os.handles)

    def test_load_cleanup_uses_exact_sources_without_main_execution(self):
        with mock.patch.object(self.subject, 'read_source', side_effect=source) as read:
            original, helper = self.subject.load_cleanup()
        self.assertCountEqual([call.args[0] for call in read.call_args_list], list(PINS))
        self.assertNotEqual(original.__name__, '__main__')
        self.assertEqual(helper, source('static_remote.py'))
        self.assertEqual(original.HELPER_SHA, PINS['static_remote.py'][2])
        self.assertTrue(callable(original.cleanup))
        self.assertEqual(self.os.calls, [])

    def test_loaded_original_has_only_exact_missing_link_projection(self):
        raw = source('cleanup_remoteocd01.py').decode('utf-8')
        self.assertEqual(raw.count(SCAN_OLD), 1)
        projected = raw.replace(SCAN_OLD, SCAN_NEW)
        self.assertEqual(self.subject.PROJECTION_OLD, SCAN_OLD.encode())
        self.assertEqual(self.subject.PROJECTION_NEW, SCAN_NEW.encode())
        self.assertEqual(self.subject.PROJECTION_SHA, PROJECTED_SHA)
        self.assertEqual(len(projected.encode()), 7870)
        self.assertEqual(hashlib.sha256(projected.encode()).hexdigest(), PROJECTED_SHA)
        expected = types.ModuleType('_independent_projected_original')
        exec(compile(projected, '/independent/source.py', 'exec'), expected.__dict__)
        with mock.patch.object(self.subject, 'read_source', side_effect=source):
            observed, unused = self.subject.load_cleanup()
        names = [name for name, value in expected.__dict__.items()
                 if isinstance(value, types.FunctionType)]
        for name in names:
            with self.subTest(function=name):
                self.assertEqual(marshal.dumps(normalized_code(getattr(observed, name).__code__)),
                                 marshal.dumps(normalized_code(getattr(expected, name).__code__)))
        self.assertEqual(observed.PINS, expected.PINS)
        self.assertEqual(observed.EXPECTED, expected.EXPECTED)

    def test_projected_scan_missing_link_rejects_surviving_pid_accepts_departed_pid(self):
        with mock.patch.object(self.subject, 'read_source', side_effect=source):
            original, unused = self.subject.load_cleanup()
        for departed in (False, True):
            with self.subTest(departed=departed):
                proc = ProcFixture(missing=True, departed=departed)
                original.Path = proc.node
                original.os = types.SimpleNamespace(getpid=lambda: 42, readlink=proc.readlink)
                if departed:
                    result = original.processes()
                    self.assertEqual(result['same_uid_handles_checked'], 1)
                else:
                    with self.assertRaises(FileNotFoundError):
                        original.processes()

    def test_projected_scan_retains_permission_native_name_and_directory_use_rejections(self):
        with mock.patch.object(self.subject, 'read_source', side_effect=source):
            original, unused = self.subject.load_cleanup()
        fixtures = [ProcFixture(denied=True), ProcFixture(target='/tmp/remoteocd'),
                    ProcFixture(target='/tmp/remoteocd/data (deleted)')]
        fixtures.extend(ProcFixture(name=name) for name in ('arduino-cli', 'remoteocd', 'openocd', 'dfu-util'))
        for proc in fixtures:
            with self.subTest(name=proc.comm, denied=proc.denied, target=proc.target):
                original.Path = proc.node
                original.os = types.SimpleNamespace(getpid=lambda: 42, readlink=proc.readlink)
                with self.assertRaises(Exception):
                    original.processes()

    def test_original_cleanup_mutations_run_uid1000_with_three_root_observations(self):
        original = types.ModuleType('_independent_cleanup_body_fixture')
        exec(compile(source('cleanup_remoteocd01.py'), '/independent/original.py', 'exec'), original.__dict__)
        fs = self.os
        fs.add('/tmp', None, 0, 0)
        fs.add('/tmp/remoteocd', None)
        fs.records['/tmp/remoteocd'].st_ino = 33
        pins, originals = {}, {}
        for index, name in enumerate(original.PINS):
            raw = ('controlled fixture ' + str(index)).encode()
            path = '/retained/' + name
            pins[name] = (len(raw), hashlib.sha256(raw).hexdigest(), path)
            originals[path] = raw
            fs.add('/tmp/remoteocd/' + name, raw)
        original.PINS = pins
        original.os = types.SimpleNamespace(**{name: getattr(fs, name) for name in
            ('fstat', 'stat', 'listdir', 'unlink', 'rmdir', 'fsync')}, path=fs.path_module)
        @contextlib.contextmanager
        def directory(unused, path):
            fd = fs.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                yield fd
            finally:
                fs.close(fd)
        @contextlib.contextmanager
        def child(parent, name, unused):
            fd = fs.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
            try:
                yield fd
            finally:
                fs.close(fd)
        def identity(unused):
            self.assertEqual(self.subject.credentials(), USER)
            return original.EXPECTED.copy()
        helper = types.SimpleNamespace(identity=identity, directory=directory, child_directory=child,
            logical_read=lambda unused, path, size: originals[path],
            read_file=lambda fd, name, size: (fs.records[fs.path(name, fd)].raw, None))
        def scan():
            self.assertEqual(self.subject.credentials(), {'uids': [1000, 0, 0], 'gids': USER['gids']})
            return {'process_names_checked': 5, 'same_uid_handles_checked': 2}
        original.processes = scan
        def main():
            result = dict(schema='d190-exact-scratch-cleanup-v1', status='FAILED',
                          removed=[], directory_removed=False, use_checks=[], first_error=None)
            fd = fs.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                original.cleanup(helper, fd, result)
                result['status'] = SUCCESS
            except Exception as error:
                result['first_error'] = {'type': type(error).__name__, 'message': str(error)}
            finally:
                fs.close(fd)
            print(json.dumps(result))
            return 0 if result['status'] == SUCCESS else 1
        original.main = main
        with mock.patch.object(self.subject, 'load_cleanup', return_value=(original, source('static_remote.py'))):
            result = self.subject.execute()
        self.assertEqual(result['status'], SUCCESS, result)
        self.assertEqual(len(result['observations']), 3)
        self.assertEqual(result['cleanup_result']['removed'], sorted(pins))
        self.assertTrue(result['cleanup_result']['originals_unchanged'])
        mutations = [item for item in fs.calls if item[0] in ('unlink', 'rmdir')]
        self.assertEqual([item[0] for item in mutations], ['unlink', 'unlink', 'unlink', 'rmdir'])
        self.assertTrue(all(item[2][1] == 1000 and item[3][1] == 1000 for item in mutations))
        self.assertFalse(fs.handles)
        self.assertNotIn('/tmp/remoteocd', fs.records)

    def test_execute_success_keeps_original_functions_calls_once_and_restores_argv(self):
        original = self.original()
        kept = {name: getattr(original, name) for name in ('main', 'cleanup', 'inventory', 'PINS')}
        argv = sys.argv
        result = self.subject.execute()
        self.assertEqual(result['schema'], 'd190-human-root-cleanup-v2')
        self.assertEqual(result['source_projection'], {'count': 1, 'before': SCAN_OLD,
            'after': SCAN_NEW, 'projected_sha256': PROJECTED_SHA})
        self.assertEqual(result['status'], SUCCESS)
        self.assertEqual(original.main_calls, 1)
        for name, value in kept.items():
            self.assertIs(getattr(original, name), value)
        self.assertIs(sys.argv, argv)
        self.assertEqual(result['cleanup_returncode'], 0)
        self.assertEqual(json.loads(result['cleanup_stdout']), result['cleanup_result'])
        self.assertEqual(result['cleanup_result']['removed'], ['a', 'b', 'c'])
        self.assertEqual(result['initial_credentials'], {'uids': [0, 0, 0], 'gids': [0, 0, 0]})
        self.assertEqual(result['final_credentials'], FINAL)
        self.assertEqual(result['privilege_drop_errors'], [])
        self.assertIsNone(result['first_error'])
        self.assertEqual(len(result['observations']), 1)

    def test_execute_wrong_identity_or_extra_argument_cannot_enter_cleanup(self):
        original = self.original()
        self.os.uids = [1000, 1000, 1000]
        result = self.subject.execute()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(original.main_calls, 0)
        self.assertEqual(self.os.calls, [])
        self.os.uids = [0, 0, 0]
        sys.argv.append('--arbitrary')
        result = self.subject.execute()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(original.main_calls, 0)

    def test_execute_requires_python_b_before_loading_or_cleanup(self):
        original = self.original()
        flags = types.SimpleNamespace(dont_write_bytecode=0)
        with mock.patch.object(self.subject.sys, 'flags', flags):
            result = self.subject.execute()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(original.main_calls, 0)

    def test_execute_requires_isolated_python_before_loading_or_cleanup(self):
        original = self.original()
        flags = types.SimpleNamespace(dont_write_bytecode=1, isolated=0)
        with mock.patch.object(self.subject.sys, 'flags', flags):
            result = self.subject.execute()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(original.main_calls, 0)

    def test_execute_load_failure_still_drops_root(self):
        with mock.patch.object(self.subject, 'load_cleanup', side_effect=ValueError('source rejected')):
            result = self.subject.execute()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['first_error']['message'], 'source rejected')
        self.assertEqual(self.subject.credentials(), FINAL)

    def test_execute_entry_failure_still_drops_root_without_original_main(self):
        original = self.original()
        self.os.fail[('setresuid', (1000, 1000, 0))] = PermissionError('entry failed')
        result = self.subject.execute()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(original.main_calls, 0)
        self.assertEqual(self.subject.credentials(), FINAL)
        self.assertIn('entry failed', result['first_error']['message'])

    def test_execute_original_failure_retains_partial_receipt_exactly(self):
        receipt = {'schema': 'd190-exact-scratch-cleanup-v1', 'status': 'FAILED', 'removed': ['first'],
                   'directory_removed': False, 'first_error': {'type': 'OSError', 'message': 'unlink failed'}}
        def failed(unused):
            print(json.dumps(receipt))
            return 1
        self.original(failed)
        result = self.subject.execute()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['cleanup_result'], receipt)
        self.assertEqual(result['cleanup_returncode'], 1)
        self.assertEqual(self.subject.credentials(), FINAL)

    def test_execute_main_exception_retains_raw_partial_stdout_and_first_error(self):
        def raised(unused):
            print('{"partial":', end='')
            raise RuntimeError('original main failed')
        self.original(raised)
        result = self.subject.execute()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['cleanup_stdout'], '{"partial":')
        self.assertEqual(result['first_error']['message'], 'original main failed')
        self.assertEqual(self.subject.credentials(), FINAL)

    def test_execute_invalid_json_or_success_status_with_nonzero_exit_is_failure(self):
        for output, code in (('not json', 0), ('[]', 0),
                             (json.dumps({'status': SUCCESS}), 1),
                             (json.dumps({'status': 'FAILED'}), 0),
                             ('{"status":"FAILED","status":"' + SUCCESS + '"}', 0)):
            with self.subTest(output=output, code=code):
                self.os.uids, self.os.gids = [0, 0, 0], [0, 0, 0]
                def invalid(unused):
                    print(output)
                    return code
                self.original(invalid)
                result = self.subject.execute()
                self.assertEqual(result['status'], 'FAILED')
                self.assertEqual(result['cleanup_stdout'], output + '\n')
                self.assertEqual(self.subject.credentials(), FINAL)

    def test_execute_terminal_drop_errors_cannot_convert_original_success_to_success(self):
        self.original()
        self.os.fail[('setresgid', (1000, 1000, 1000))] = PermissionError('terminal group drop failed')
        result = self.subject.execute()
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['cleanup_result']['status'], SUCCESS)
        self.assertTrue(result['privilege_drop_errors'])
        self.assertEqual(self.os.uids, FINAL['uids'])

    def test_execute_original_error_remains_first_when_terminal_drop_also_fails(self):
        def raised(unused):
            raise RuntimeError('original first')
        self.original(raised)
        self.os.fail[('setresuid', (1000, 1000, 1000))] = PermissionError('terminal second')
        result = self.subject.execute()
        self.assertEqual(result['first_error']['message'], 'original first')
        self.assertTrue(any(row['message'] == 'terminal second' for row in result['privilege_drop_errors']))

    def test_main_prints_one_compact_result_and_returns_status(self):
        for status, expected in ((SUCCESS, 0), ('FAILED', 1)):
            result = {'status': status, 'first_error': None}
            output = io.StringIO()
            with mock.patch.object(self.subject, 'execute', return_value=result), contextlib.redirect_stdout(output):
                self.assertEqual(self.subject.main(), expected)
            self.assertEqual(output.getvalue(), json.dumps(result, separators=(',', ':')) + '\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
