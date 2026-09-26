# Regresses D194's narrowly bounded Windows executable-extension stat difference.
# Separates CPython path-only execute bits from identity changes and same-API drift.
# Freeze before execution; only tiny owned files are read, never launched.
from contextlib import ExitStack
import hashlib
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[2]
SUBJECT = ROOT / 'state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi.py'
REG = stat.S_IFREG
RAW = b'controlled pinned bytes; not an executable image\n'
SHA = hashlib.sha256(RAW).hexdigest()
REJECT = (ValueError, OSError, RuntimeError, TypeError)
PRIMARY_SOURCES = (
    'https://github.com/python/cpython/blob/v3.13.11/Modules/posixmodule.c#L1831-L1852',
    'https://github.com/python/cpython/blob/v3.13.11/Python/fileutils.c#L999-L1028',
)


class ChangedStat:
    def __init__(self, original, changes):
        self.original = original
        self.__dict__.update(changes)

    def __getattr__(self, name):
        return getattr(self.original, name)


class WindowsExecutableModeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode:
            raise RuntimeError('D194 regression requires Python -B')
        cls.source = SUBJECT.read_bytes()

    def setUp(self):
        self.subject = types.ModuleType('_d194_windows_mode_oracle')
        self.subject.__file__ = str(SUBJECT)
        exec(compile(self.source, str(SUBJECT), 'exec'), self.subject.__dict__)
        temporary = tempfile.TemporaryDirectory(prefix='sumox-d194-mode-',
                    dir='/dev/shm' if sys.platform == 'linux' else None)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for owner, names in ((subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
                             (socket, ('socket', 'create_connection'))):
            for name in names:
                patch = mock.patch.object(owner, name, side_effect=AssertionError('External operation: ' + name))
                patch.start(); self.addCleanup(patch.stop)

    def scenario(self, *, filename='probe.exe', platform='nt', path_mode=REG | 0o777,
                 handle_mode=REG | 0o666, path_fields=None, handle_fields=None,
                 path_after=None, handle_after=None, expect='accept', expected_sha=SHA):
        path = self.root / filename
        path.write_bytes(RAW)
        baseline = path.stat()
        real_stat, real_fstat, real_fdopen = Path.stat, os.fstat, os.fdopen
        reads, wraps, handles = [], [], []
        def observed_path(item, *args, **kwargs):
            info = real_stat(item, *args, **kwargs)
            if item != path: return info
            values = dict(st_mode=path_mode, st_ctime_ns=baseline.st_ctime_ns)
            values.update(path_fields or {})
            if reads: values.update(path_after or {})
            return ChangedStat(baseline, values)
        def observed_handle(fd):
            real_fstat(fd)
            handles.append(fd)
            values = dict(st_mode=handle_mode, st_ctime_ns=baseline.st_ctime_ns)
            values.update(handle_fields or {})
            if reads: values.update(handle_after or {})
            return ChangedStat(baseline, values)
        class Stream:
            def __init__(self, actual): self.actual = actual
            def fileno(self): return self.actual.fileno()
            def read(self, size=-1): reads.append(size); return self.actual.read(size)
            def close(self): return self.actual.close()
            def __enter__(self): return self
            def __exit__(self, *_): self.close()
        def wrapped(*args, **kwargs):
            wraps.append(True)
            return Stream(real_fdopen(*args, **kwargs))
        private_os = types.SimpleNamespace(**vars(os))
        private_os.name = platform
        private_os.fstat = observed_handle
        private_os.fdopen = wrapped
        with mock.patch.object(self.subject, 'os', private_os), mock.patch.object(Path, 'stat', observed_path):
            if expect == 'accept':
                self.assertEqual(self.subject.pinned(path, expected_sha), RAW)
            else:
                with self.assertRaises(REJECT): self.subject.pinned(path, expected_sha)
        if expect == 'early':
            self.assertFalse(reads, 'Identity mismatch must refuse before reading')
            self.assertFalse(wraps, 'Identity mismatch must refuse before fdopen')
        else:
            self.assertTrue(reads, 'Fixture must reach the checked read')
            self.assertTrue(all(0 < count <= 1048577 for count in reads))
        return len(handles)

    def test_real_executable_named_regular_file_is_read_without_launching(self):
        path = self.root / 'tiny.EXe'
        path.write_bytes(RAW)
        before = path.lstat()
        self.assertEqual(self.subject.pinned(path, SHA), RAW)
        after = path.lstat()
        self.assertEqual((before.st_mode, before.st_ino, before.st_size, before.st_mtime_ns),
                         (after.st_mode, after.st_ino, after.st_size, after.st_mtime_ns))
        self.assertEqual(path.read_bytes(), RAW)

    def test_complete_path_only_execute_delta_accepts_all_four_extensions_and_case(self):
        for extension in ('.exe', '.bat', '.cmd', '.com', '.EXE', '.BaT', '.cMd', '.CoM'):
            with self.subTest(extension=extension): self.scenario(filename='probe' + extension)

    def test_readonly_regular_modes_accept_only_the_same_complete_delta(self):
        for extension in ('.exe', '.bat', '.cmd', '.com'):
            with self.subTest(extension=extension):
                self.scenario(filename='readonly' + extension, path_mode=REG | 0o555, handle_mode=REG | 0o444)

    def test_exact_mode_equality_remains_valid_for_both_platforms_and_suffixes(self):
        for platform in ('nt', 'posix'):
            for filename in ('equal.exe', 'equal.txt'):
                for mode in (REG | 0o666, REG | 0o777, REG | 0o444):
                    with self.subTest(platform=platform, filename=filename, mode=oct(mode)):
                        self.scenario(platform=platform, filename=filename, path_mode=mode, handle_mode=mode)

    def test_nonwindows_execute_difference_refuses_before_read_for_every_extension(self):
        for extension in ('.exe', '.bat', '.cmd', '.com'):
            with self.subTest(extension=extension):
                self.scenario(platform='posix', filename='probe' + extension, expect='early')

    def test_nonmatching_or_nonfinal_extension_differences_refuse_before_read(self):
        for filename in ('probe', 'probe.py', 'probe.txt', 'probe.exe.txt', 'probe.executable', 'probe.cmdx'):
            with self.subTest(filename=filename): self.scenario(filename=filename, expect='early')

    def test_partial_execute_deltas_and_reverse_direction_refuse_before_read(self):
        for path_bits, handle_bits in ((0o766, 0o666), (0o676, 0o666), (0o667, 0o666),
                                       (0o776, 0o666), (0o777, 0o766), (0o666, 0o777)):
            with self.subTest(path_mode=oct(path_bits), handle_mode=oct(handle_bits)):
                self.scenario(path_mode=REG | path_bits, handle_mode=REG | handle_bits, expect='early')

    def test_other_permission_and_special_bits_are_never_masked(self):
        for path_bits, handle_bits in ((0o777, 0o664), (0o777, 0o644), (0o555, 0o666),
                                       (0o4777, 0o666), (0o2777, 0o666), (0o1777, 0o666)):
            with self.subTest(path_mode=oct(path_bits), handle_mode=oct(handle_bits)):
                self.scenario(path_mode=REG | path_bits, handle_mode=REG | handle_bits, expect='early')

    def test_other_identity_field_mismatches_refuse_before_read(self):
        for field in ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_file_attributes'):
            with self.subTest(field=field):
                self.scenario(handle_fields={field: -1}, expect='early')

    def test_nonregular_reparse_and_multiple_links_refuse_before_read(self):
        for kind in (stat.S_IFDIR, stat.S_IFIFO, stat.S_IFLNK, stat.S_IFCHR):
            with self.subTest(kind=kind):
                self.scenario(handle_mode=kind | 0o666, expect='early')
        for fields in ({'st_nlink': 2}, {'st_file_attributes': 1024}):
            with self.subTest(fields=fields): self.scenario(handle_fields=fields, expect='early')
        self.scenario(path_fields={'st_file_attributes': 1024}, expect='early')
        self.scenario(path_fields={'st_nlink': 2}, expect='early')

    def test_full_path_mode_must_stay_identical_after_read(self):
        for after in (REG | 0o666, REG | 0o776, REG | 0o555):
            with self.subTest(after=oct(after)):
                self.scenario(path_after={'st_mode': after}, expect='late')

    def test_full_descriptor_mode_must_stay_identical_after_read(self):
        for after in (REG | 0o777, REG | 0o667, REG | 0o444):
            with self.subTest(after=oct(after)):
                self.scenario(handle_after={'st_mode': after}, expect='late')

    def test_windows_ctime_api_difference_retains_within_api_stability(self):
        self.scenario(path_fields={'st_ctime_ns': 123}, handle_fields={'st_ctime_ns': 456})
        self.scenario(path_fields={'st_ctime_ns': 123}, handle_fields={'st_ctime_ns': 456},
                      path_after={'st_ctime_ns': 124}, expect='late')
        self.scenario(path_fields={'st_ctime_ns': 123}, handle_fields={'st_ctime_ns': 456},
                      handle_after={'st_ctime_ns': 457}, expect='late')

    def test_hash_is_still_required_after_eligible_mode_difference(self):
        self.scenario(expected_sha='0' * 64, expect='late')


if __name__ == '__main__':
    unittest.main(verbosity=2)
