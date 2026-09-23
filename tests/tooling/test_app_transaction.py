"""Independent D095 tests compile production sources as opaque bytes.

Receipts retain exact commands, outputs and hashes including failed attempts.
All transport use is a controlled local fixture; no real board lookup or upload.
"""
from contextlib import ExitStack, redirect_stderr
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / 'tests/locked/native_motor_port'


class AppTransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++')
        if compiler is None:
            raise RuntimeError('D095 tests require Linux/WSL g++')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-d095-', dir='/dev/shm')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.source = cls.stage / 'src'
        shutil.copytree(ROOT / 'src', cls.source)
        cls.raw = Path(os.environ.get('SUMO_APP_TRANSACTION_RECEIPT_DIR',
                       ROOT / 'state/analysis/P2_app_transaction_raw/author'))
        cls.raw.mkdir(parents=True, exist_ok=True)
        cls.base = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                    '-fno-sanitize-recover=all',
                    '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                    '-I', cls.source, '-I', ROOT / 'tests', '-isystem', ROOT / 'host/third_party']
        cls.main = cls.stage / 'main.o'
        cls.command([*cls.base, '-c', NATIVE / 'test_main.cc', '-o', cls.main])

    @classmethod
    def command(cls, argv, expected=0, timeout=180):
        paths = list(cls.source.rglob('*'))
        paths += [ROOT / 'tests/locked/test_motor_halt.cpp', ROOT / 'tests/test_app_transaction.cpp',
                  ROOT / 'tests/fixtures/app_transaction_fixture.h',
                  ROOT / 'tests/native_motors/app_transaction_probe.cc', Path(__file__)]
        paths += list((ROOT / 'bench/p2_app_transaction_compile').rglob('*'))
        hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
        try:
            result = subprocess.run(list(map(str, argv)), capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            result = SimpleNamespace(returncode=124, stdout=str(exc.stdout or ''),
                                     stderr=str(exc.stderr or '') + '\nTIMEOUT')
        receipt = {'argv': list(map(str, argv)), 'returncode': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr, 'sha256': hashes,
                   'capture': 'subprocess text=True; newline normalized'}
        (cls.raw / f'command_{time.time_ns()}.json').write_text(json.dumps(receipt, indent=2) + '\n')
        if result.returncode != expected:
            raise AssertionError(result.stdout + result.stderr)
        return result

    def build(self, label, allowed, probe=False):
        sources = sorted((self.source / 'core').glob('*.cpp'))
        sources += [self.source / 'hal' / p for p in ('motors.cpp', 'recorder.cpp', 'recorder_frames.cpp')]
        sources += [self.source / 'app/transaction.cpp']
        args = [*self.base, f'-DMOTORS_ALLOWED={allowed}', f'-DMATCH={allowed}']
        if probe:
            folder = self.stage / label
            shutil.copytree(ROOT / 'bench/p2_app_transaction_compile', folder)
            sketch = folder / 'sketch.cc'
            shutil.copyfile(folder / 'p2_app_transaction_compile.ino', sketch)
            args += ['-DARDUINO_ARCH_ZEPHYR', '-I', NATIVE, '-I', folder / 'src', '-I', folder,
                     '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
            sources += [self.source / 'hal/motor_port_unoq.cpp', NATIVE / 'native_fixture.cc',
                        ROOT / 'tests/native_motors/app_transaction_probe.cc', sketch,
                        folder / 'src/app_transaction_probe.cpp']
        else:
            sources += [ROOT / 'tests/locked/test_motor_halt.cpp', ROOT / 'tests/test_app_transaction.cpp']
        binary = self.stage / (label + '.exe')
        self.command([*args, *sources, self.main, '-o', binary])
        result = self.command([binary, '--no-colors'], timeout=120)
        self.assertIn('Status: SUCCESS!', result.stdout)
        print(label + ': ' + ' | '.join(line for line in result.stdout.splitlines()
              if 'test cases:' in line or 'assertions:' in line), flush=True)

    def test_actual_halt_transaction_contract_both_motor_settings(self):
        for allowed in (0, 1):
            self.build('owner-' + str(allowed), allowed)

    def test_actual_native_probe_inert_and_owner_allocation_free_both_settings(self):
        for allowed in (0, 1):
            self.build('probe-' + str(allowed), allowed, probe=True)

    def test_all_upload_modes_refuse_before_target_transport_lookup(self):
        spec = importlib.util.spec_from_file_location('d095_board_tool', ROOT / 'tools/board_tool.py')
        board = importlib.util.module_from_spec(spec); spec.loader.exec_module(board)
        records = []
        for transport in ('adb', 'ssh'):
            for match in (False, True):
                for startup in ('default', 'immediate'):
                    with self.subTest(transport=transport, match=match, startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict(os.environ, {'SUMO_TRANSPORT': transport}))
                        target = stack.enter_context(mock.patch.object(board, 'target'))
                        remote = stack.enter_context(mock.patch.object(board, 'remote'))
                        require = stack.enter_context(mock.patch.object(board, 'require_transport'))
                        with redirect_stderr(io.StringIO()), self.assertRaises(ValueError) as caught:
                            board.flash(SimpleNamespace(sketch='bench/p2_app_transaction_compile',
                                match=match, startup=startup, compile_only=False))
                        target.assert_not_called(); remote.assert_not_called(); require.assert_not_called()
                        records.append({'transport': transport, 'match': match, 'startup': startup,
                                        'error': str(caught.exception), 'calls': 0})
        (self.raw / f'upload_refusals_{time.time_ns()}.json').write_text(json.dumps(records, indent=2) + '\n')

    def fixture(self):
        from . import test_tools
        fixture = test_tools.ToolContractTests(methodName='runTest')
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        return fixture

    def tool(self, fixture, *args, **kwargs):
        result = fixture.run_tool(*args, **kwargs)
        data = {'args': args, 'kwargs': kwargs, 'returncode': result.returncode,
                'stdout': result.stdout, 'stderr': result.stderr, 'events': fixture.events}
        (self.raw / f'staging_{time.time_ns()}.json').write_text(json.dumps(data, indent=2) + '\n')
        return result

    def test_app_and_bench_stage_shared_support_beneath_src_app_with_real_includes(self):
        fixture = self.fixture()
        fixture.write('src/app/transaction.h', '#pragma once\nint appValue();\n')
        fixture.write('src/app/transaction.cpp', '#include "../config.h"\n#include "transaction.h"\nint appValue(){return FIXTURE_VALUE;}\n')
        for target, name in (('app', 'app'), ('bench/p0_matrix', 'p0_matrix')):
            result = self.tool(fixture, target, '--compile-only')
            self.assertEqual(result.returncode, 0, result.stderr)
            stage = fixture.root / 'build/stage' / name
            self.assertTrue((stage / (name + '.ino')).is_file())
            self.assertFalse((stage / 'transaction.cpp').exists())
            self.assertFalse((stage / 'transaction.h').exists())
            self.assertFalse((stage / 'src/app/app.ino').exists())
            for suffix in ('h', 'cpp'):
                self.assertEqual((stage / 'src/app' / ('transaction.' + suffix)).read_bytes(),
                                 (fixture.root / 'src/app' / ('transaction.' + suffix)).read_bytes())
            self.command(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsyntax-only',
                          stage / 'src/app/transaction.cpp'])
            fixture.assert_no_motion_command()

    def test_sketch_local_src_app_shadow_refused_without_transport(self):
        fixture = self.fixture()
        fixture.write('bench/p0_matrix/src/app/transaction.h', '#error forbidden shadow\n')
        result = self.tool(fixture, 'bench/p0_matrix', '--compile-only')
        fixture.assert_failed(result); self.assertIn('src/app', result.stderr.lower())
        self.assertIn('conflicts', result.stderr.lower())
        self.assertEqual(fixture.events, [])

    def test_compile_errors_propagate_without_upload_or_success(self):
        fixture = self.fixture()
        fixture.write('src/app/transaction.cpp', '#error intentional local fixture\n')
        result = self.tool(fixture, 'app', '--compile-only', changes={'FAKE_FAIL': 'compile'})
        fixture.assert_failed(result); self.assertEqual(len(fixture.commands('compile')), 1)
        self.assertEqual(fixture.commands('upload'), [])

    def test_actual_staged_transaction_cpp_and_header_resolve_without_root_include_flags(self):
        fixture = self.fixture(); fixture.use_reviewed_sources()
        result = self.tool(fixture, 'bench/p0_timing', '--compile-only')
        self.assertEqual(result.returncode, 0, result.stderr)
        stage = fixture.root / 'build/stage/p0_timing'
        self.command(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsyntax-only',
                      stage / 'src/app/transaction.cpp'])
        probe = fixture.root / 'public_header.cc'
        probe.write_text('#include "' + (stage / 'src/app/transaction.h').as_posix() + '"\n')
        self.command(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsyntax-only', probe])
        fixture.assert_no_motion_command()

    def test_flash_propagates_staging_error_before_any_remote_command(self):
        spec = importlib.util.spec_from_file_location('d095_stage_error', ROOT / 'tools/board_tool.py')
        board = importlib.util.module_from_spec(spec); spec.loader.exec_module(board)
        sentinel = OSError('D095 controlled staging failure')
        with ExitStack() as stack:
            stack.enter_context(mock.patch.object(board, 'target', return_value='fixture@board.invalid'))
            stack.enter_context(mock.patch.object(board, 'setting', return_value='/controlled_fixture'))
            stack.enter_context(mock.patch.object(board, 'require_transport'))
            stage = stack.enter_context(mock.patch.object(board, 'stage', side_effect=sentinel))
            verify = stack.enter_context(mock.patch.object(board, 'verify_core'))
            remote = stack.enter_context(mock.patch.object(board, 'remote'))
            with self.assertRaises(OSError) as caught:
                board.flash(SimpleNamespace(sketch='app', match=False, startup='default', compile_only=True))
            self.assertIs(caught.exception, sentinel)
            stage.assert_called_once_with('app'); verify.assert_not_called(); remote.assert_not_called()
        (self.raw / f'stage_error_{time.time_ns()}.json').write_text(json.dumps({
            'same_exception': True, 'error': str(sentinel), 'remote_calls': 0}) + '\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
