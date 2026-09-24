# Tests D139 read-only stage reuse against its public file and guard contract.
# Synthetic trees preserve exact filenames without reading production bodies.
# Root executes this frozen unittest file before any qualification helper run.
import builtins
from contextlib import ExitStack, contextmanager
import copy
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

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
SOURCE_MANIFEST = ROOT / 'state/analysis/P7_default_qualification_raw/working_source_manifest.json'
AUTHORIZED_REAL_DIGEST = 'fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2'
VALID_CONFIG = b'''#pragma once
#include <cstdint>
namespace config {
inline constexpr std::uint32_t EDGE_PUSH_THROUGH_MS = 0U;
inline constexpr std::uint32_t MODE_ARC_ENABLED = 1U;
inline constexpr std::uint32_t MODE_WAIT_ENABLED = 1U;
inline constexpr std::uint32_t MODE_DEFAULT = 1U;
}
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ReuseRejected(Exception):
    pass


def digest(files):
    result = hashlib.sha256()
    for name in sorted(files):
        result.update(name.encode('utf-8') + b'\0' + files[name])
    return result.hexdigest()


def snapshot(root):
    result = {}
    for path in [root, *sorted(root.rglob('*'))]:
        stat = path.lstat()
        name = path.relative_to(root).as_posix()
        kind = 'link' if path.is_symlink() else ('dir' if path.is_dir() else 'file')
        value = os.readlink(path) if kind == 'link' else (path.read_bytes() if kind == 'file' else None)
        result[name] = (kind, stat.st_mode, stat.st_size, stat.st_mtime_ns, value)
    return result


@contextmanager
def no_actions():
    attempts = []
    original_open, original_io_open, original_os_open = builtins.open, io.open, os.open

    def forbidden(*args, **kwargs):
        attempts.append('filesystem mutation or process/remote action')
        raise AssertionError('D139 adapter attempted a forbidden mutation/action')

    def checked_open(original):
        def open_readonly(file, mode='r', *args, **kwargs):
            if any(flag in str(mode) for flag in 'wax+'):
                return forbidden(file, mode)
            return original(file, mode, *args, **kwargs)
        return open_readonly

    def readonly_os_open(path, flags, *args, **kwargs):
        if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            return forbidden(path, flags)
        return original_os_open(path, flags, *args, **kwargs)

    with ExitStack() as stack:
        stack.enter_context(mock.patch('builtins.open', checked_open(original_open)))
        stack.enter_context(mock.patch('io.open', checked_open(original_io_open)))
        stack.enter_context(mock.patch('os.open', readonly_os_open))
        for name in ('mkdir', 'rmdir', 'unlink', 'write_bytes', 'write_text', 'touch',
                     'rename', 'replace', 'symlink_to', 'hardlink_to', 'chmod'):
            stack.enter_context(mock.patch.object(Path, name, forbidden))
        for module, names in ((os, ('remove', 'unlink', 'rmdir', 'mkdir', 'makedirs',
                                   'rename', 'replace', 'system', 'chmod')),
                              (shutil, ('rmtree', 'copy', 'copy2', 'copyfile', 'copytree', 'move')),
                              (socket, ('socket', 'create_connection')),
                              (subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output'))):
            for name in names:
                stack.enter_context(mock.patch.object(module, name, forbidden))
        yield attempts


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError('Cannot create module loader')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    with no_actions() as attempts:
        spec.loader.exec_module(module)
    if attempts:
        raise AssertionError('Module import attempted forbidden action')
    return module


class Fixture:
    def __init__(self, names, prior):
        base = Path(os.environ.get('D139_TEST_TMP', '/dev/shm')).resolve()
        if not base.is_dir():
            raise AssertionError('Set D139_TEST_TMP to an existing RAM scratch directory')
        self.temporary = tempfile.TemporaryDirectory(prefix='sumox_d139_tests_', dir=base)
        self.root = Path(self.temporary.name).resolve()
        if self.root.parent != base or not self.root.name.startswith('sumox_d139_tests_'):
            raise AssertionError('Unexpected synthetic fixture root')
        self.base = base
        self.stage = self.root / 'build/stage/app'
        self.source_data = {name: ('// D139 synthetic ' + name + '\n').encode() for name in names}
        self.source_data['src/app/.gitkeep'] = b''
        self.source_data['src/config.h'] = VALID_CONFIG
        self.stage_data = {}
        for name, data in self.source_data.items():
            self.put(self.root / name, data)
            if name == 'src/app/.gitkeep':
                continue
            target = 'app.ino' if name == 'src/app/app.ino' else name
            self.stage_data[target] = data
            self.put(self.stage / target, data)
        self.source_manifest = {'file_count': 103, 'files': {
            name: {'sha256': sha(data), 'bytes': len(data)} for name, data in self.source_data.items()}}
        self.stage_manifest = {'file_count': 102, 'source_sha256': digest(self.stage_data),
                               'files': {name: sha(data) for name, data in self.stage_data.items()}}
        # Freeze once before fault stimuli; later coherent drift cannot update it.
        self.authorized_digest = self.stage_manifest['source_sha256']
        self.guard_calls, self.forbidden_calls = [], []
        self.reject_guard = None

        def fail(message):
            raise ReuseRejected(message)

        def guarded(kind, callback):
            def call(path):
                self.guard_calls.append((kind, Path(path).resolve()))
                if self.reject_guard == kind:
                    fail('synthetic ' + kind + ' guard rejection')
                with mock.patch.object(prior, 'ROOT', self.root), mock.patch.object(prior, 'fail', fail):
                    return callback(path)
            return call

        def forbidden(*args, **kwargs):
            self.forbidden_calls.append((args, kwargs))
            raise AssertionError('Forbidden original staging/remote entry point')

        self.board = types.SimpleNamespace(ROOT=self.root, fail=fail,
            check_source=guarded('source', prior.check_source),
            validate_push_through_config=guarded('push', prior.validate_push_through_config),
            validate_mode_availability_config=guarded('mode', prior.validate_mode_availability_config),
            stage=forbidden, remote=forbidden, sync_sources=forbidden,
            compile=forbidden, upload=forbidden, reset=forbidden, main=forbidden)

    @staticmethod
    def put(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def close(self):
        if self.root.parent != self.base or not self.root.name.startswith('sumox_d139_tests_'):
            raise AssertionError('Refusing cleanup outside owned synthetic fixture')
        self.temporary.cleanup()

    def replace_config(self, data):
        self.put(self.root / 'src/config.h', data)
        self.put(self.stage / 'src/config.h', data)
        self.source_data['src/config.h'] = self.stage_data['src/config.h'] = data
        self.source_manifest['files']['src/config.h'] = {'sha256': sha(data), 'bytes': len(data)}
        self.stage_manifest['files']['src/config.h'] = sha(data)
        self.stage_manifest['source_sha256'] = digest(self.stage_data)


class ReuseStageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior = load_module('d139_prior_board_tool', ROOT / 'tools/board_tool.py')
        adapter_path = os.environ.get('D139_REUSE_ADAPTER')
        if not adapter_path:
            raise AssertionError('D139_REUSE_ADAPTER must identify the reviewed helper')
        cls.adapter = load_module('d139_reuse_adapter', Path(adapter_path).resolve())
        cls.names = tuple(sorted(json.loads(SOURCE_MANIFEST.read_text(encoding='utf-8'))['files']))
        if len(cls.names) != 103 or len(set(cls.names)) != 103:
            raise AssertionError('Expected exact103 source filename set')

    def fixture(self):
        fixture = Fixture(self.names, self.prior)
        self.addCleanup(fixture.close)
        return fixture

    def invoke(self, f, sketch='app'):
        before = snapshot(f.root)
        source_before = copy.deepcopy(f.source_manifest)
        stage_before = copy.deepcopy(f.stage_manifest)
        # Public synthetic seam only; production literal is checked separately.
        with mock.patch.object(self.adapter, 'AUTHORIZED_SOURCE_SHA256', f.authorized_digest), no_actions() as attempts:
            try:
                return self.adapter.verifiedStage(f.board, sketch, f.source_manifest, f.stage_manifest)
            finally:
                self.assertEqual([], attempts)
                self.assertEqual([], f.forbidden_calls)
                self.assertEqual(before, snapshot(f.root))
                self.assertEqual(source_before, f.source_manifest)
                self.assertEqual(stage_before, f.stage_manifest)

    def rejected(self, f, sketch='app'):
        with self.assertRaises(ReuseRejected):
            self.invoke(f, sketch)

    def test_actual_authorization_literal_matches_the_reviewed_current_stage(self):
        self.assertEqual(AUTHORIZED_REAL_DIGEST, self.adapter.AUTHORIZED_SOURCE_SHA256)

    def test_exact_source_stage_mapping_digest_and_original_guards_are_required(self):
        f = self.fixture()
        path, receipt = self.invoke(f)
        self.assertEqual(f.stage, Path(path))
        self.assertEqual({'source_files': 103, 'stage_files': 102,
                          'source_sha256': f.authorized_digest, 'read_only_reuse': True}, receipt)
        self.assertEqual(103, len(f.source_manifest['files']))
        self.assertEqual(102, len(f.stage_manifest['files']))
        self.assertEqual(sha(f.source_data['src/app/app.ino']), f.stage_manifest['files']['app.ino'])
        self.assertNotIn('src/app/.gitkeep', f.stage_manifest['files'])
        self.assertIn(('source', (f.root / 'src/app').resolve()), f.guard_calls)
        self.assertIn(('source', (f.root / 'src').resolve()), f.guard_calls)
        self.assertIn(('push', (f.stage / 'src/config.h').resolve()), f.guard_calls)
        self.assertIn(('mode', (f.stage / 'src/config.h').resolve()), f.guard_calls)

    def test_wrong_sketch_never_reuses_or_falls_back(self):
        for sketch in ('', 'bench/p0_timing', 'app/', '../app', 'APP'):
            with self.subTest(sketch=sketch):
                self.rejected(self.fixture(), sketch)

    def test_source_missing_extra_and_changed_bytes_are_rejected(self):
        for mutation in ('missing', 'extra', 'changed'):
            with self.subTest(mutation=mutation):
                f = self.fixture()
                path = f.root / 'src/core/types.h'
                if mutation == 'missing':
                    path.unlink()
                elif mutation == 'extra':
                    f.put(f.root / 'src/core/extra.h', b'// unexpected\n')
                else:
                    path.write_bytes(b'// changed\n')
                self.rejected(f)

    def test_source_manifest_missing_extra_and_wrong_digest_are_rejected(self):
        for mutation in ('missing', 'extra', 'hash'):
            with self.subTest(mutation=mutation):
                f = self.fixture()
                files = f.source_manifest['files']
                if mutation == 'missing':
                    del files['src/core/types.h']
                elif mutation == 'extra':
                    files['src/core/extra.h'] = {'sha256': sha(b''), 'bytes': 0}
                else:
                    files['src/core/types.h']['sha256'] = '0' * 64
                self.rejected(f)

    def test_nonbinding_size_metadata_never_replaces_real_hash_validation(self):
        f = self.fixture()
        f.source_manifest['files']['src/core/types.h']['bytes'] += 123
        path, receipt = self.invoke(f)
        self.assertEqual(f.stage, path)
        self.assertEqual(f.authorized_digest, receipt['source_sha256'])
        f.put(f.root / 'src/core/types.h', b'changed despite metadata')
        self.rejected(f)

    def test_stage_missing_extra_and_changed_bytes_are_rejected(self):
        for mutation in ('missing', 'extra', 'changed'):
            with self.subTest(mutation=mutation):
                f = self.fixture()
                path = f.stage / 'src/core/types.h'
                if mutation == 'missing':
                    path.unlink()
                elif mutation == 'extra':
                    f.put(f.stage / 'unexpected.bin', b'extra')
                else:
                    path.write_bytes(b'// altered staged bytes\n')
                self.rejected(f)

    def test_stage_manifest_missing_extra_hash_and_aggregate_are_rejected(self):
        for mutation in ('missing', 'extra', 'hash', 'aggregate'):
            with self.subTest(mutation=mutation):
                f = self.fixture()
                files = f.stage_manifest['files']
                if mutation == 'missing':
                    del files['src/core/types.h']
                elif mutation == 'extra':
                    files['extra.h'] = sha(b'')
                elif mutation == 'hash':
                    files['src/core/types.h'] = 'f' * 64
                else:
                    f.stage_manifest['source_sha256'] = '0' * 64
                self.rejected(f)

    def test_self_consistent_stage_changes_still_must_match_current_source(self):
        f = self.fixture()
        changed = b'// internally consistent but not current source\n'
        f.put(f.stage / 'src/core/types.h', changed)
        f.stage_data['src/core/types.h'] = changed
        f.stage_manifest['files']['src/core/types.h'] = sha(changed)
        f.stage_manifest['source_sha256'] = digest(f.stage_data)
        self.rejected(f)

    def test_self_consistent_source_change_still_must_match_stage(self):
        f = self.fixture()
        changed = b'// new source absent from immutable stage\n'
        f.put(f.root / 'src/core/types.h', changed)
        f.source_manifest['files']['src/core/types.h'] = {'sha256': sha(changed), 'bytes': len(changed)}
        self.rejected(f)

    def test_coherent_source_stage_and_manifest_drift_cannot_replace_authorized_digest(self):
        f = self.fixture()
        changed = b'// coherent replacement outside the authorized source freeze\n'
        f.put(f.root / 'src/core/types.h', changed)
        f.put(f.stage / 'src/core/types.h', changed)
        f.source_manifest['files']['src/core/types.h'] = {'sha256': sha(changed), 'bytes': len(changed)}
        f.stage_data['src/core/types.h'] = changed
        f.stage_manifest['files']['src/core/types.h'] = sha(changed)
        f.stage_manifest['source_sha256'] = digest(f.stage_data)
        self.assertNotEqual(f.authorized_digest, f.stage_manifest['source_sha256'])
        self.rejected(f)

    def test_app_ino_mapping_cannot_be_changed_with_matching_manifest_digest(self):
        f = self.fixture()
        data = f.stage_data.pop('app.ino')
        (f.stage / 'app.ino').unlink()
        f.put(f.stage / 'src/app/app.ino', data)
        f.stage_data['src/app/app.ino'] = data
        del f.stage_manifest['files']['app.ino']
        f.stage_manifest['files']['src/app/app.ino'] = sha(data)
        f.stage_manifest['source_sha256'] = digest(f.stage_data)
        self.rejected(f)

    def test_excluded_gitkeep_is_not_an_admissible_staged_file(self):
        f = self.fixture()
        f.put(f.stage / 'src/app/.gitkeep', b'')
        f.stage_data['src/app/.gitkeep'] = b''
        f.stage_manifest['files']['src/app/.gitkeep'] = sha(b'')
        f.stage_manifest['source_sha256'] = digest(f.stage_data)
        self.rejected(f)

    def test_unsafe_manifest_names_are_rejected(self):
        for manifest in ('source', 'stage'):
            for name in ('../escape.h', '/absolute.h', 'src/../escape.h', 'src\\core\\types.h'):
                with self.subTest(manifest=manifest, name=name):
                    f = self.fixture()
                    files = (f.source_manifest if manifest == 'source' else f.stage_manifest)['files']
                    files[name] = files.pop('src/core/types.h')
                    self.rejected(f)

    def test_file_symlinks_are_rejected_even_when_target_bytes_match(self):
        for tree in ('source', 'stage'):
            with self.subTest(tree=tree):
                f = self.fixture()
                path = (f.root if tree == 'source' else f.stage) / 'src/core/types.h'
                target = f.root / 'matching_link_target.h'
                target.write_bytes(path.read_bytes())
                path.unlink()
                path.symlink_to(target)
                self.rejected(f)

    def test_directory_and_stage_ancestry_symlinks_are_rejected(self):
        for relative in ('src/core', 'build/stage/app/src/core', 'build/stage/app', 'build/stage', 'build'):
            with self.subTest(relative=relative):
                f = self.fixture()
                original = f.root / relative
                target = f.root / 'relocated_fixture_directory'
                original.rename(target)
                original.symlink_to(target, target_is_directory=True)
                self.rejected(f)

    def test_sketch_local_reserved_entries_are_rejected_even_when_empty(self):
        for name in ('config.h', 'core', 'hal', 'app'):
            with self.subTest(name=name):
                f = self.fixture()
                (f.root / 'src/app/src' / name).mkdir(parents=True)
                self.rejected(f)

    def test_original_guard_rejections_propagate_without_fallback(self):
        for kind in ('source', 'push', 'mode'):
            with self.subTest(kind=kind):
                f = self.fixture()
                f.reject_guard = kind
                self.rejected(f)
                self.assertTrue(any(call[0] == kind for call in f.guard_calls))

    def test_actual_push_config_validation_is_not_skipped_when_hashes_match(self):
        f = self.fixture()
        f.replace_config(VALID_CONFIG.replace(b'EDGE_PUSH_THROUGH_MS = 0U', b'EDGE_PUSH_THROUGH_MS = 101U'))
        # Authorize this synthetic fixture only, so rejection must reach the validator.
        f.authorized_digest = f.stage_manifest['source_sha256']
        self.rejected(f)
        self.assertTrue(any(call[0] == 'push' for call in f.guard_calls))

    def test_actual_mode_config_validation_is_not_skipped_when_hashes_match(self):
        f = self.fixture()
        f.replace_config(VALID_CONFIG.replace(b'MODE_ARC_ENABLED = 1U', b'MODE_ARC_ENABLED = 0U')
                         .replace(b'MODE_DEFAULT = 1U', b'MODE_DEFAULT = 4U'))
        f.authorized_digest = f.stage_manifest['source_sha256']
        self.rejected(f)
        self.assertTrue(any(call[0] == 'mode' for call in f.guard_calls))

    def test_repeat_verification_is_readonly_and_returns_the_same_stage(self):
        f = self.fixture()
        first_path, first_receipt = self.invoke(f)
        second_path, second_receipt = self.invoke(f)
        self.assertEqual(first_path, second_path)
        self.assertIsInstance(first_receipt, dict)
        self.assertIsInstance(second_receipt, dict)


if __name__ == '__main__':
    unittest.main()
