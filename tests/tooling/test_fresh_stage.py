# Tests D170 fresh staging ownership, preserved source layout and failure evidence.
# Derives expectations from the contract and public P0 fixtures, not production bodies.
# Run Python -B unittest; Linux fixtures use owned RAM and never dispatch board work.
from contextlib import contextmanager, ExitStack
import hashlib
import importlib.util
import inspect
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


PROJECT = Path(__file__).resolve().parents[2]
CONFIG = (b'#pragma once\r\n#include <cstdint>\r\nnamespace config {\r\n'
          b'inline constexpr std::uint32_t EDGE_PUSH_THROUGH_MS = 0U;\r\n}\r\n')
SHARED = {
    'src/config.h': CONFIG,
    'src/core/value.h': b'#pragma once\nint coreValue();\n',
    'src/core/value.cpp': b'#include "value.h"\nint coreValue() { return 7; }\n',
    'src/hal/value.h': b'#pragma once\nint halValue();\n',
    'src/hal/value.cpp': b'#include "value.h"\nint halValue() { return 9; }\n',
}
BENCH = {
    'motor_fault.ino': b'#include "src/config.h"\r\nvoid setup() {}\r\nvoid loop() {}\r\n',
    'local.h': b'// sketch-local header\r\n',
    'detail/extra.h': '// UTF-8 source: caf\u00e9\n'.encode('utf-8'),
    'detail/caf\u00e9.h': b'// UTF-8 relative filename\n',
    'src/local_probe.h': b'#pragma once\n',
    'src/local_probe.cpp': b'#include "local_probe.h"\n',
}
APP = {
    'app.ino': b'#include "src/config.h"\nvoid setup() {}\nvoid loop() {}\n',
    'local.h': b'// app-local header\r\n',
    'detail/extra.h': b'// nested app source\n',
}
REJECTION = (ValueError, TypeError, OSError)


def tree_snapshot(root):
    """Observe bytes/mtime without traversing links or Windows reparse points."""
    result = {}
    pending = [Path(root)]
    while pending:
        path = pending.pop()
        info = path.lstat()
        relative = path.relative_to(root).as_posix()
        reparse = bool(getattr(info, 'st_file_attributes', 0) & 0x400)
        if stat.S_ISLNK(info.st_mode) or reparse:
            result[relative] = ('link', os.readlink(path), info.st_mtime_ns)
        elif stat.S_ISDIR(info.st_mode):
            result[relative] = ('dir', info.st_mtime_ns)
            pending.extend(sorted(path.iterdir()))
        else:
            result[relative] = ('file', path.read_bytes(), info.st_mtime_ns)
    return result


def expected_hash(files):
    digest = hashlib.sha256()
    for relative, raw in sorted(files.items()):
        digest.update(relative.encode('utf-8') + b'\0' + raw)
    return digest.hexdigest()


class FreshStageTests(unittest.TestCase):
    def setUp(self):
        ram = Path('/dev/shm') if sys.platform == 'linux' else None
        if ram is not None and not ram.is_dir():
            self.skipTest('Linux D170 fixtures require /dev/shm')
        temporary = tempfile.TemporaryDirectory(prefix='d170-fresh-', dir=ram)
        self.addCleanup(temporary.cleanup)
        self.sandbox = Path(temporary.name).resolve()
        self.root = self.sandbox / 'project'
        tools = self.root / 'tools'
        # Copy opaque modules only; no production ROOT is rebound or stage reused.
        tools.mkdir(parents=True)
        for source in (PROJECT / 'tools').iterdir():
            if source.suffix in ('.py', '.json') and source.is_file():
                shutil.copyfile(source, tools / source.name)
        for relative, raw in SHARED.items():
            self.write(relative, raw)
        for folder, files in (('bench/motor_fault', BENCH), ('src/app', APP)):
            for relative, raw in files.items():
                self.write(folder + '/' + relative, raw)
        modules = mock.patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        for source in tools.glob('*.py'):
            sys.modules.pop(source.stem, None)
        path_patch = mock.patch.object(sys, 'path', [str(tools)] + sys.path)
        path_patch.start()
        self.addCleanup(path_patch.stop)
        spec = importlib.util.spec_from_file_location('_d170_isolated_board', tools / 'board_tool.py')
        self.board = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = self.board
        with mock.patch.object(sys, 'dont_write_bytecode', True):
            spec.loader.exec_module(self.board)
        self.assertEqual(self.root, self.board.ROOT)

    def write(self, relative, raw):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path

    def symlink(self, link, target, directory=False):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest('Fixture symlink unavailable: ' + str(error))

    def legacy_sentinel(self):
        path = self.write('build/stage/motor_fault/evidence.bin', b'legacy\0\xff\r\n')
        os.utime(path, ns=(1234567890000000000, 1234567890000000000))
        return path.parent, tree_snapshot(path.parent)

    @contextmanager
    def operations(self, explicit=True, forbid_writes=False):
        """Fail visibly on any forbidden call, even if production catches its error."""
        with ExitStack() as stack:
            calls = []
            board_names = ('target', 'require_transport', 'verify_core', 'sync_sources',
                           'remote', 'compile_app', 'verify_runtime_artifacts')
            targets = [(self.board, name) for name in board_names]
            targets += [(subprocess, name) for name in
                        ('Popen', 'run', 'call', 'check_call', 'check_output')]
            targets += [(os, 'system'), (os, 'popen')]
            if explicit:
                targets += [(shutil, 'rmtree'), (shutil, 'move')]
                targets += [(os, name) for name in ('remove', 'unlink', 'rmdir', 'rename', 'replace')]
                targets += [(Path, name) for name in ('unlink', 'rmdir', 'rename', 'replace')]
            if forbid_writes:
                targets += [(os, 'mkdir'), (Path, 'mkdir'), (shutil, 'copyfile'),
                            (shutil, 'copy2'), (shutil, 'copytree'),
                            (Path, 'write_bytes'), (Path, 'write_text')]
            for owner, name in targets:
                calls.append(stack.enter_context(mock.patch.object(
                    owner, name, side_effect=AssertionError('Forbidden D170 call: ' + name))))
            try:
                yield
            finally:
                for call in calls:
                    call.assert_not_called()

    def assert_layout(self, output, sketch):
        if sketch == 'bench/motor_fault':
            expected = dict(SHARED, **BENCH)
        else:
            expected = dict(SHARED)
            expected['app.ino'] = APP['app.ino']
        expected.update({'src/app/' + name: raw for name, raw in APP.items()
                         if name != 'app.ino'})
        actual = {path.relative_to(output).as_posix(): path.read_bytes()
                  for path in output.rglob('*') if path.is_file()}
        self.assertEqual(expected, actual)
        self.assertEqual(expected_hash(expected), self.board.source_hash(output))
        self.assertFalse(any(path.is_symlink() for path in output.rglob('*')))

    def assert_refused_without_writes(self, attempt, sketch='bench/motor_fault'):
        before = tree_snapshot(self.sandbox)
        with self.operations(forbid_writes=True), self.assertRaises(REJECTION):
            self.board.stage(sketch, attempt=attempt)
        self.assertEqual(before, tree_snapshot(self.sandbox))

    def test_public_attempt_is_keyword_only_and_defaults_to_none(self):
        parameter = inspect.signature(self.board.stage).parameters['attempt']
        self.assertEqual(inspect.Parameter.KEYWORD_ONLY, parameter.kind)
        self.assertIsNone(parameter.default)
        with self.operations(forbid_writes=True), self.assertRaises(TypeError):
            self.board.stage('bench/motor_fault', 'positional')
        self.assertFalse((self.root / 'build').exists())

    def test_fresh_bench_and_app_exact_layout_bytes_hash_preserve_legacy(self):
        sentinel, before = self.legacy_sentinel()
        sources = {name: tree_snapshot(self.root / name) for name in ('src', 'bench')}
        for index, sketch in enumerate(('bench/motor_fault', 'app')):
            with self.subTest(sketch=sketch), self.operations():
                token = 'fresh-' + str(index)
                output = self.board.stage(sketch, attempt=token)
                self.assertEqual(self.root / 'build/stage' / token / Path(sketch).name, output)
                self.assert_layout(output, sketch)
            self.assertEqual(before, tree_snapshot(sentinel))
        for name, snapshot in sources.items():
            self.assertEqual(snapshot, tree_snapshot(self.root / name))

    def test_portable_token_boundaries_and_reserved_near_misses_accept(self):
        for token in ('a', '0', 'a' * 48, '9' + '_-' * 23 + '_',
                      'a_', 'a-', 'con0', 'com0', 'com10', 'lpt0', 'lpt10', 'auxx'):
            with self.subTest(token=token), self.operations():
                output = self.board.stage('bench/motor_fault', attempt=token)
                self.assertEqual(self.root / 'build/stage' / token / 'motor_fault', output)
                self.assert_layout(output, 'bench/motor_fault')

    def test_invalid_tokens_fail_before_staging_directories_exist(self):
        for token in ('', 'a' * 49, '_a', '-a', '.', '..', '../escape', 'a/b', 'a\\b',
                      '/absolute', 'C:\\escape', 'A', 'aB', ' a', 'a ', 'a\n', 'a\r\n',
                      'a\t', 'a.b', 'a:b', 'a\0b', 'a;echo', 'a*', '\u00e9', '\uff11'):
            with self.subTest(token=repr(token)):
                self.assert_refused_without_writes(token)
                self.assertFalse((self.root / 'build').exists())

    def test_non_exact_strings_fail_before_staging_directories_exist(self):
        class StringSubclass(str):
            pass

        for token in (True, False, 0, 1, 1.5, b'valid', bytearray(b'valid'),
                      Path('valid'), [], {}, object(), StringSubclass('valid')):
            with self.subTest(kind=type(token).__name__):
                self.assert_refused_without_writes(token)
                self.assertFalse((self.root / 'build').exists())

    def test_all_windows_device_tokens_fail_on_every_host(self):
        tokens = ['con', 'prn', 'aux', 'nul']
        tokens += [prefix + str(number) for prefix in ('com', 'lpt') for number in range(1, 10)]
        for token in tokens:
            with self.subTest(token=token):
                self.assert_refused_without_writes(token)
        self.assertFalse((self.root / 'build').exists())

    def test_existing_file_empty_and_populated_directory_owners_refuse(self):
        self.write('build/stage/file-owner', b'unique owner\xff')
        (self.root / 'build/stage/empty-owner').mkdir()
        self.write('build/stage/full-owner/nested/evidence', b'keep every byte')
        for token in ('file-owner', 'empty-owner', 'full-owner'):
            with self.subTest(token=token):
                self.assert_refused_without_writes(token)

    def test_existing_live_and_dangling_link_owners_refuse(self):
        base = self.root / 'build/stage'
        base.mkdir(parents=True)
        target = self.sandbox / 'outside'
        target.mkdir()
        (target / 'evidence').write_bytes(b'outside original')
        for name, destination, directory in (
                ('live-dir', target, True), ('live-file', target / 'evidence', False),
                ('dangling', target / 'absent', True)):
            self.symlink(base / name, destination, directory)
            with self.subTest(name=name):
                self.assert_refused_without_writes(name)

    def test_attempt_namespace_cannot_reuse_the_protected_legacy_directory(self):
        sentinel, before = self.legacy_sentinel()
        self.assert_refused_without_writes('motor_fault')
        self.assertEqual(before, tree_snapshot(sentinel))

    def assert_unsafe_ancestor(self, relative, kind):
        path = self.root / relative if relative else self.root
        if path == self.root:
            target = self.sandbox / 'saved-project'
            path.rename(target)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            target = self.sandbox / 'external-directory'
            target.mkdir()
            (target / 'sentinel').write_bytes(b'ancestry evidence')
        if kind == 'file':
            path.write_bytes(b'not a directory\0')
        else:
            self.symlink(path, target if kind == 'live' else self.sandbox / 'missing', True)
        self.assert_refused_without_writes('new-owner')

    def test_root_symlink_refuses_before_writes(self):
        self.assert_unsafe_ancestor('', 'live')

    def test_build_symlink_refuses_before_writes(self):
        self.assert_unsafe_ancestor('build', 'live')

    def test_stage_symlink_refuses_before_writes(self):
        self.assert_unsafe_ancestor('build/stage', 'live')

    def test_internal_build_symlink_is_not_a_plain_directory(self):
        target = self.root / 'plain-directory'
        target.mkdir()
        self.symlink(self.root / 'build', target, True)
        self.assert_refused_without_writes('contained-link')

    def test_dangling_build_link_refuses_before_writes(self):
        self.assert_unsafe_ancestor('build', 'dangling')

    def test_dangling_stage_link_refuses_before_writes(self):
        self.assert_unsafe_ancestor('build/stage', 'dangling')

    def test_non_directory_root_refuses_before_writes(self):
        self.assert_unsafe_ancestor('', 'file')

    def test_non_directory_build_refuses_before_writes(self):
        self.assert_unsafe_ancestor('build', 'file')

    def test_non_directory_stage_refuses_before_writes(self):
        self.assert_unsafe_ancestor('build/stage', 'file')

    @unittest.skipUnless(os.name == 'nt', 'Actual Windows junction fixture')
    def test_windows_junction_ancestry_refuses_before_writes(self):
        powershell = shutil.which('powershell') or shutil.which('pwsh')
        if powershell is None:
            self.skipTest('PowerShell unavailable for owned junction fixture')
        target = self.sandbox / 'junction-target'
        target.mkdir()
        (target / 'evidence').write_bytes(b'junction target must survive')
        link = self.root / 'build'
        env = dict(os.environ, D170_LINK=str(link), D170_TARGET=str(target))
        result = subprocess.run([powershell, '-NoProfile', '-NonInteractive', '-Command',
            'New-Item -ItemType Junction -Path $env:D170_LINK -Target $env:D170_TARGET '
            '-ErrorAction Stop | Out-Null'], env=env, capture_output=True, text=True,
            timeout=15, check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(0xA0000003, link.lstat().st_reparse_tag)
        self.assert_refused_without_writes('junction-owner')

    def test_ancestry_is_rechecked_after_missing_base_creation(self):
        target = self.sandbox / 'replacement-target'
        target.mkdir()
        probe = self.sandbox / 'symlink-capability'
        self.symlink(probe, target, True)
        stage = self.root / 'build/stage'
        real_mkdir = Path.mkdir
        replaced = []

        def make(path, *args, **kwargs):
            if path == stage and not path.exists():
                real_mkdir(path.parent, parents=True, exist_ok=True)
                path.symlink_to(target, target_is_directory=True)
                replaced.append(path)
                return None
            return real_mkdir(path, *args, **kwargs)

        before = tree_snapshot(target)
        with self.operations(), mock.patch.object(Path, 'mkdir', make), self.assertRaises(REJECTION):
            self.board.stage('bench/motor_fault', attempt='rechecked')
        self.assertEqual([stage], replaced)
        self.assertEqual(before, tree_snapshot(target))
        self.assertTrue(stage.is_symlink())

    def test_owner_claim_is_exclusive_if_an_owner_appears_at_mkdir(self):
        owner = self.root / 'build/stage/exclusive'
        real_mkdir = Path.mkdir
        claimed = []

        def make(path, *args, **kwargs):
            if path == owner and not claimed:
                real_mkdir(path)
                (path / 'winner').write_bytes(b'other owner retains this')
                claimed.append(path)
            return real_mkdir(path, *args, **kwargs)

        with self.operations(), mock.patch.object(Path, 'mkdir', make), self.assertRaises(REJECTION):
            self.board.stage('bench/motor_fault', attempt='exclusive')
        self.assertEqual([owner], claimed)
        self.assertEqual(['winner'], [path.name for path in owner.iterdir()])
        self.assertEqual(b'other owner retains this', (owner / 'winner').read_bytes())

    def test_copy_failure_retains_partial_bytes_and_consumes_attempt(self):
        sentinel, before = self.legacy_sentinel()
        owner = self.root / 'build/stage/copy-failed'
        copied = []
        # Windows copy2 can bypass copyfile through CopyFile2; inject after copy2.
        real_copy2 = shutil.copy2

        def fail_after_copy(source, destination, *args, **kwargs):
            result = real_copy2(source, destination, *args, **kwargs)
            destination = Path(result)
            if destination.is_relative_to(owner):
                copied.append((destination, destination.read_bytes()))
                raise OSError('controlled post-claim copy failure')
            return result

        with self.operations(), mock.patch.object(shutil, 'copy2', fail_after_copy):
            with self.assertRaisesRegex(OSError, 'controlled post-claim copy failure'):
                self.board.stage('bench/motor_fault', attempt='copy-failed')
        self.assertTrue(copied, 'Fixture fault must occur after at least one actual copied file')
        for path, raw in copied:
            self.assertEqual(raw, path.read_bytes())
        self.assertTrue(owner.is_dir())
        self.assert_refused_without_writes('copy-failed')
        self.assertEqual(before, tree_snapshot(sentinel))

    def test_real_config_failure_retains_invalid_copy_and_consumes_attempt(self):
        sentinel, before = self.legacy_sentinel()
        invalid = CONFIG.replace(b'= 0U;', b'= 101U;')
        self.write('src/config.h', invalid)
        with self.operations(), self.assertRaises(ValueError):
            self.board.stage('bench/motor_fault', attempt='config-failed')
        copied = self.root / 'build/stage/config-failed/motor_fault/src/config.h'
        self.assertEqual(invalid, copied.read_bytes())
        self.write('src/config.h', CONFIG)
        self.assert_refused_without_writes('config-failed')
        self.assertEqual(before, tree_snapshot(sentinel))

    def test_reserved_sketch_local_sources_still_refuse(self):
        for index, relative in enumerate(('config.h', 'core/conflict.h', 'hal/conflict.h')):
            path = self.write('bench/motor_fault/src/' + relative, b'// conflicting source\n')
            with self.subTest(relative=relative), self.operations(), self.assertRaises(REJECTION):
                self.board.stage('bench/motor_fault', attempt='reserved-' + str(index))
            self.assertEqual(b'// conflicting source\n', path.read_bytes())
            path.unlink()
            if '/' in relative:
                path.parent.rmdir()

    def test_source_links_still_refuse_without_changing_the_target(self):
        target = self.sandbox / 'source-target.h'
        target.write_bytes(b'// source target evidence\n')
        for index, relative in enumerate(('bench/motor_fault/linked.h', 'src/core/linked.h')):
            link = self.root / relative
            self.symlink(link, target)
            with self.subTest(relative=relative), self.operations(), self.assertRaises(REJECTION):
                self.board.stage('bench/motor_fault', attempt='source-link-' + str(index))
            self.assertEqual(b'// source target evidence\n', target.read_bytes())
            self.assertTrue(link.is_symlink())
            link.unlink()

    def test_omitted_and_none_keep_legacy_path_and_restage_behavior(self):
        for index, explicit_none in enumerate((False, True)):
            raw = BENCH['local.h'] + ('// legacy revision ' + str(index) + '\n').encode()
            self.write('bench/motor_fault/local.h', raw)
            with self.operations(explicit=False):
                output = (self.board.stage('bench/motor_fault', attempt=None) if explicit_none
                          else self.board.stage('bench/motor_fault'))
            self.assertEqual(self.root / 'build/stage/motor_fault', output)
            self.assertEqual(raw, (output / 'local.h').read_bytes())
            self.assertEqual(CONFIG, (output / 'src/config.h').read_bytes())
        self.assertEqual(['motor_fault'], [path.name for path in output.parent.iterdir()])


if __name__ == '__main__':
    unittest.main()
