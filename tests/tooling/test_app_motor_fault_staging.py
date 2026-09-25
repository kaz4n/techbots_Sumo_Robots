"""Tests D186 exact shared-trace staging and generic route refusal in isolation.
Uses opaque tooling APIs and owned synthetic source trees, with no native target.
Run: python3 -B -m unittest tests.tooling.test_app_motor_fault_staging -v.
"""
from contextlib import contextmanager, ExitStack
import importlib
import importlib.util
import itertools
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

PROJECT = Path(__file__).resolve().parents[2]
SKETCH = 'bench/app_motor_fault'
REJECTION = (ValueError, TypeError, OSError)
SOURCE_FILES = {
    'src/config.h': b'#pragma once\n#include <cstdint>\nnamespace config {\n'
                    b'inline constexpr std::uint32_t EDGE_PUSH_THROUGH_MS = 0U;\n}\n',
    'src/core/value.h': b'// shared core\n',
    'src/hal/value.h': b'// shared hal\n',
    'src/app/app.ino': b'void setup() {}\nvoid loop() {}\n',
    'src/app/runtime.h': b'// shared application\n',
    'bench/app_motor_fault/app_motor_fault.ino': b'// diagnostic sketch\r\n',
    'bench/app_motor_fault/src/app_motor_fault.h': b'// local header\r\n',
    'bench/app_motor_fault/src/app_motor_fault.cpp': b'// local implementation\n',
    'bench/app_motor_fault/detail/retained.h': b'// local nested header\n',
    'bench/motor_fault/src/motor_fault.h': b'// exact canonical header\r\n\x00\xff',
    'bench/motor_fault/src/motor_fault.cpp': b'// exact canonical implementation\n',
}


def snapshot(root):
    result = {}
    pending = [root]
    while pending:
        path = pending.pop()
        info = path.lstat()
        key = path.relative_to(root).as_posix()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            result[key] = ('link', os.readlink(path))
        elif stat.S_ISDIR(info.st_mode):
            pending.extend(path.iterdir())
        else:
            result[key] = path.read_bytes()
    return result


class AppMotorFaultStagingTests(unittest.TestCase):
    def setUp(self):
        ram = '/dev/shm' if sys.platform == 'linux' else None
        temporary = tempfile.TemporaryDirectory(prefix='sumox-d186-stage-', dir=ram)
        self.addCleanup(temporary.cleanup)
        self.sandbox = Path(temporary.name).resolve()
        self.root = self.sandbox / 'project'
        tools = self.root / 'tools'
        tools.mkdir(parents=True)
        for path in (PROJECT / 'tools').iterdir():
            if path.suffix in ('.py', '.json') and path.is_file():
                shutil.copyfile(path, tools / path.name)
        for name, content in SOURCE_FILES.items():
            self.write(name, content)
        self.sentinel = self.write('build/stage/app_motor_fault/evidence', b'old attempt remains')
        modules = mock.patch.dict(sys.modules)
        modules.start(); self.addCleanup(modules.stop)
        for source in tools.glob('*.py'):
            sys.modules.pop(source.stem, None)
        search = mock.patch.object(sys, 'path', [str(tools), *sys.path])
        search.start(); self.addCleanup(search.stop)
        spec = importlib.util.spec_from_file_location('_d186_isolated_board', tools / 'board_tool.py')
        self.board = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.board
        with mock.patch.object(sys, 'dont_write_bytecode', True):
            spec.loader.exec_module(self.board)
            self.policy = importlib.import_module('app_build_policy')
        self.assertEqual(self.root, self.board.ROOT)

    def write(self, relative, raw):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path

    @contextmanager
    def offline(self, refuse_stage=False, refuse_writes=False):
        with ExitStack() as stack:
            calls = []
            names = ('target', 'require_transport', 'verify_core', 'sync_sources',
                     'remote', 'compile_app', 'verify_runtime_artifacts')
            for name in names + (('stage',) if refuse_stage else ()):
                calls.append(stack.enter_context(mock.patch.object(self.board, name,
                    side_effect=AssertionError('Unexpected target/stage: ' + name))))
            operations = [(subprocess, n) for n in ('run', 'Popen', 'call', 'check_call', 'check_output')]
            operations += [(shutil, n) for n in ('rmtree', 'move')]
            if refuse_writes:
                operations += [(Path, n) for n in ('mkdir', 'write_bytes', 'write_text', 'unlink')]
                operations += [(shutil, n) for n in ('copyfile', 'copy2', 'copytree')]
            for owner, name in operations:
                calls.append(stack.enter_context(mock.patch.object(owner, name,
                    side_effect=AssertionError('Forbidden host effect: ' + name))))
            try:
                yield
            finally:
                for call in calls:
                    call.assert_not_called()

    def test_exact_shared_bytes_and_source_immutability(self):
        before = {name: (self.root / name).read_bytes() for name in SOURCE_FILES}
        with self.offline():
            output = self.board.stage(SKETCH, attempt='complete')
        self.assertEqual(self.root / 'build/stage/complete/app_motor_fault', output)
        expected = {name.removeprefix('bench/app_motor_fault/'): content
                    for name, content in SOURCE_FILES.items() if name.startswith(SKETCH + '/')}
        expected.update({name: raw for name, raw in SOURCE_FILES.items()
                         if name.startswith('src/') and name != 'src/app/app.ino'})
        expected.update({'src/' + name: SOURCE_FILES['bench/motor_fault/src/' + name]
                         for name in ('motor_fault.h', 'motor_fault.cpp')})
        self.assertEqual(expected, snapshot(output))
        self.assertEqual(before, {name: (self.root / name).read_bytes() for name in SOURCE_FILES})
        self.assertEqual(b'old attempt remains', self.sentinel.read_bytes())

    def test_missing_attempt_and_existing_owner_refuse_before_writes(self):
        self.write('build/stage/used/evidence', b'existing owner')
        for kwargs in ({}, {'attempt': None}, {'attempt': 'used'}):
            before = snapshot(self.sandbox)
            with self.subTest(kwargs=kwargs), self.offline(refuse_writes=True), self.assertRaises(REJECTION):
                self.board.stage(SKETCH, **kwargs)
            self.assertEqual(before, snapshot(self.sandbox))

    def test_each_missing_canonical_trace_file_refuses(self):
        for index, name in enumerate(('motor_fault.h', 'motor_fault.cpp')):
            path = self.root / 'bench/motor_fault/src' / name
            data = path.read_bytes(); path.unlink()
            with self.subTest(name=name), self.offline(), self.assertRaises(REJECTION):
                self.board.stage(SKETCH, attempt='missing-' + str(index))
            path.write_bytes(data)
            self.assertEqual(b'old attempt remains', self.sentinel.read_bytes())

    def test_each_local_collision_refuses_and_preserves_source(self):
        for index, name in enumerate(('motor_fault.h', 'motor_fault.cpp')):
            path = self.write(SKETCH + '/src/' + name, b'local collision must remain')
            with self.subTest(name=name), self.offline(), self.assertRaises(REJECTION):
                self.board.stage(SKETCH, attempt='collision-' + str(index))
            self.assertEqual(b'local collision must remain', path.read_bytes())
            path.unlink()

    def test_partial_copy_failure_retains_bytes_and_consumed_owner(self):
        original = shutil.copy2
        seen = []
        owner = self.root / 'build/stage/partial'

        def fail(source, destination, *args, **kwargs):
            result = original(source, destination, *args, **kwargs)
            destination = Path(result)
            if destination.is_relative_to(owner):
                seen.append((destination, destination.read_bytes()))
                raise OSError('D186 deliberate post-copy failure')
            return result

        with self.offline(), mock.patch.object(shutil, 'copy2', fail):
            with self.assertRaisesRegex(OSError, 'D186 deliberate post-copy failure'):
                self.board.stage(SKETCH, attempt='partial')
        self.assertTrue(seen)
        for path, raw in seen:
            self.assertEqual(raw, path.read_bytes())
        with self.offline(refuse_writes=True), self.assertRaises(REJECTION):
            self.board.stage(SKETCH, attempt='partial')

    def test_shared_and_local_symlink_sources_refuse(self):
        candidates = ('bench/app_motor_fault', 'bench/app_motor_fault/src',
                      'bench/app_motor_fault/detail', 'src', 'src/core',
                      'bench/motor_fault/src', 'bench/motor_fault/src/motor_fault.h')
        for index, name in enumerate(candidates):
            with self.subTest(name=name):
                source = self.root / name
                parked = source.with_name(source.name + '-actual')
                source.rename(parked)
                try:
                    try:
                        source.symlink_to(parked, target_is_directory=parked.is_dir())
                    except (OSError, NotImplementedError) as error:
                        self.skipTest('Host cannot create symbolic links: ' + str(error))
                    with self.offline(), self.assertRaises(REJECTION):
                        self.board.stage(SKETCH, attempt='link-' + str(index))
                finally:
                    if source.is_symlink():
                        source.unlink()
                    parked.rename(source)

    def test_reparse_metadata_on_every_source_boundary_refuses(self):
        candidates = ('bench', 'bench/app_motor_fault', 'bench/app_motor_fault/src',
                      'bench/app_motor_fault/detail', 'bench/app_motor_fault/detail/retained.h',
                      'src', 'src/core', 'src/core/value.h', 'src/app',
                      'bench/motor_fault', 'bench/motor_fault/src',
                      'bench/motor_fault/src/motor_fault.h',
                      'bench/motor_fault/src/motor_fault.cpp')
        original = Path.lstat

        class Reparse:
            def __init__(self, info):
                self.info = info
                self.st_file_attributes = getattr(info, 'st_file_attributes', 0) | 0x400

            def __getattr__(self, name):
                return getattr(self.info, name)

        for index, name in enumerate(candidates):
            target = self.root / name

            def attributes(path, *args, **kwargs):
                info = original(path, *args, **kwargs)
                return Reparse(info) if path == target else info

            with self.subTest(name=name), mock.patch.object(Path, 'lstat', attributes):
                with self.offline(), self.assertRaises(REJECTION):
                    self.board.stage(SKETCH, attempt='reparse-' + str(index))

    @unittest.skipUnless(sys.platform == 'win32', 'real junction fixture needs Windows')
    def test_real_windows_directory_junctions_refuse(self):
        candidates = ('bench/app_motor_fault/src', 'src/core', 'bench/motor_fault/src')
        for index, name in enumerate(candidates):
            source = self.root / name
            parked = source.with_name(source.name + '-actual')
            source.rename(parked)
            try:
                command = f"New-Item -ItemType Junction -Path '{source}' -Target '{parked}' | Out-Null"
                subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', command],
                               check=True, capture_output=True, text=True)
                with self.subTest(name=name), self.offline(), self.assertRaises(REJECTION):
                    self.board.stage(SKETCH, attempt='junction-' + str(index))
            finally:
                if source.exists():
                    source.rmdir()
                parked.rename(source)

    def test_generic_flash_every_flag_combination_refuses_before_io(self):
        for startup, match, compile_only in itertools.product((None, 'default', 'immediate'),
                                                             (False, True), (False, True)):
            args = SimpleNamespace(sketch=SKETCH, startup=startup,
                                   match=match, compile_only=compile_only)
            with self.subTest(startup=startup, match=match, compile_only=compile_only):
                with self.offline(refuse_stage=True, refuse_writes=True), self.assertRaises(REJECTION):
                    self.board.flash(args)

    def test_dynamic_policy_does_not_register_new_project(self):
        for fqbn, match, motors in itertools.product(('arduino:zephyr:unoq',
                'arduino:zephyr:unoq:wait_linux_boot=no'), (0, 1), (0, 1)):
            flags = f'-DMATCH={match} -DMOTORS_ALLOWED={motors}'
            with self.subTest(fqbn=fqbn, flags=flags), self.offline(), self.assertRaises(ValueError):
                self.policy.selected_project('app_motor_fault.ino', fqbn, flags)


if __name__ == '__main__':
    unittest.main(verbosity=2)
