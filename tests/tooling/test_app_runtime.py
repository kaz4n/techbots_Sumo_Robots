"""Build the D096 public-contract tests against opaque production source copies.

Synthetic button windows exist only in a temporary copied configuration.
Commands, failures, byte hashes and fake transport events remain append-only.
"""
from contextlib import ExitStack, redirect_stderr
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / 'tests/native_app_runtime'
HAL = ('motors.cpp', 'recorder.cpp', 'recorder_frames.cpp', 'power_inputs.cpp',
       'ui.cpp', 'imu_heading.cpp', 'imu_adapter.cpp',
       'line_qtr_adapter.cpp', 'qtr_cal.cpp', 'ui_display.cpp')


class AppRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++')
        if compiler is None:
            raise RuntimeError('D096 tests require Linux/WSL g++')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-d096-', dir='/dev/shm')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.source = cls.stage / 'default/src'
        shutil.copytree(ROOT / 'src', cls.source)
        cls.raw = Path(os.environ.get('SUMO_APP_RUNTIME_RECEIPT_DIR',
                       ROOT / 'state/analysis/P2_app_runtime_raw/author'))
        cls.raw.mkdir(parents=True, exist_ok=True)
        cls.base = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                    '-fno-sanitize-recover=all',
                    '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                    '-I', ROOT / 'tests', '-isystem', ROOT / 'host/third_party']
        cls.main = cls.stage / 'main.o'
        cls.command([*cls.base, '-c', ROOT / 'tests/locked/native_motor_port/test_main.cc',
                     '-o', cls.main])

    @classmethod
    def receipt(cls, kind, value):
        path = cls.raw / f'{kind}_{time.time_ns()}.json'
        # Exclusive creation prevents a failed attempt being replaced by a retry.
        with path.open('x', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n')

    @classmethod
    def hashes(cls):
        paths = list(cls.stage.rglob('*'))
        paths += list(NATIVE.rglob('*'))
        paths += [ROOT / 'tests/test_app_runtime.cpp', ROOT / 'tests/test_app_projection.cpp',
                  ROOT / 'tests/fixtures/app_runtime_fixture.h', Path(__file__)]
        paths += list((ROOT / 'tools').glob('*.py'))
        return {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in paths if path.is_file() and path.suffix != '.exe'}

    @classmethod
    def command(cls, argv, expected=0, timeout=180):
        hashes = cls.hashes()
        try:
            result = subprocess.run(list(map(str, argv)), cwd=ROOT, capture_output=True,
                                    text=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            result = SimpleNamespace(returncode=124, stdout=str(error.stdout or ''),
                                     stderr=str(error.stderr or '') + '\nTIMEOUT')
        cls.receipt('command', {'argv': list(map(str, argv)), 'cwd': str(ROOT),
                    'returncode': result.returncode, 'stdout': result.stdout,
                    'stderr': result.stderr, 'sha256': hashes,
                    'capture': 'subprocess text=True; newline normalized'})
        if result.returncode != expected:
            raise AssertionError(result.stdout + result.stderr)
        return result

    def configured_source(self):
        source = self.stage / 'configured/src'
        shutil.copytree(self.source, source)
        path = source / 'config.h'
        original = path.read_text()
        configured = original
        for name, value in (
                ('BUTTON_WINDOWS_CONFIGURED', '1U'),
                ('BUTTON_LOW_RAW', '{0U, 900U, 1900U, 2900U}'),
                ('BUTTON_HIGH_RAW', '{100U, 1100U, 2100U, 3100U}')):
            configured, count = re.subn(r'(\b' + name + r'(?:\[4\])?\s*=\s*)[^;]+;',
                                        r'\g<1>' + value + ';', configured)
            self.assertEqual(count, 1, name)
        path.write_text(configured)
        self.receipt('synthetic_config', {'path': str(path), 'source': configured,
                    'production_sha256': hashlib.sha256((ROOT / 'src/config.h').read_bytes()).hexdigest(),
                    'configured_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'purpose': 'Explicit synthetic host buttons only; no physical window grant'})
        return source

    def build(self, label, source, allowed, configured):
        sources = sorted((source / 'core').glob('*.cpp'))
        sources += [source / 'hal' / name for name in HAL]
        sources += [source / 'app/transaction.cpp', source / 'app/runtime.cpp', source / 'app/runtime_inputs.cpp',
                    ROOT / 'tests/test_app_runtime.cpp', ROOT / 'tests/test_app_projection.cpp',
                    NATIVE / 'allocation_probe.cc']
        args = [*self.base, '-I', source, f'-DMOTORS_ALLOWED={allowed}', f'-DMATCH={allowed}',
                '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
        if configured:
            args += ['-DAPP_TEST_CONFIGURED_BUTTONS=1']
        binary = self.stage / (label + '.exe')
        self.command([*args, *sources, self.main, '-o', binary])
        result = self.command([binary, '--no-colors'], timeout=180)
        self.assertIn('Status: SUCCESS!', result.stdout)
        print(label + ': ' + ' | '.join(line for line in result.stdout.splitlines()
              if 'test cases:' in line or 'assertions:' in line), flush=True)

    def test_actual_runtime_projection_and_no_allocation_both_button_profiles_and_motor_settings(self):
        configured = self.configured_source()
        for profile, source, synthetic in (('default', self.source, False),
                                          ('configured', configured, True)):
            for allowed in (0, 1):
                with self.subTest(profile=profile, allowed=allowed):
                    self.build(profile + '-' + str(allowed), source, allowed, synthetic)

    def test_app_upload_modes_refuse_before_target_or_transport_lookup(self):
        spec = importlib.util.spec_from_file_location('d096_board_tool', ROOT / 'tools/board_tool.py')
        board = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(board)
        for transport in ('adb', 'ssh'):
            for match in (False, True):
                for startup in ('default', 'immediate'):
                    with self.subTest(transport=transport, match=match, startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict(os.environ, {'SUMO_TRANSPORT': transport}))
                        target = stack.enter_context(mock.patch.object(board, 'target'))
                        remote = stack.enter_context(mock.patch.object(board, 'remote'))
                        require = stack.enter_context(mock.patch.object(board, 'require_transport'))
                        with redirect_stderr(io.StringIO()), self.assertRaises(ValueError) as caught:
                            board.flash(SimpleNamespace(sketch='app', match=match,
                                                       startup=startup, compile_only=False))
                        self.receipt('upload_refusal', {'transport': transport, 'match': match,
                            'startup': startup, 'error': str(caught.exception),
                            'target_calls': target.call_count, 'remote_calls': remote.call_count,
                            'transport_calls': require.call_count})
                        target.assert_not_called()
                        remote.assert_not_called()
                        require.assert_not_called()

    def fixture(self):
        from . import test_tools
        fixture = test_tools.ToolContractTests(methodName='runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        return fixture

    def tool(self, fixture, *args, **kwargs):
        result = fixture.run_tool(*args, **kwargs)
        self.receipt('staging', {'args': args, 'kwargs': kwargs, 'returncode': result.returncode,
                    'stdout': result.stdout, 'stderr': result.stderr, 'events': fixture.events})
        return result

    def test_app_and_inert_bench_stage_shared_runtime_and_native_sources_with_local_includes(self):
        fixture = self.fixture()
        fixture.write('src/app/runtime.h', '#pragma once\nint runtimeValue();\n')
        fixture.write('src/app/runtime.cpp', '#include "../config.h"\n#include "runtime.h"\n'
                      'int runtimeValue(){return FIXTURE_VALUE;}\n')
        fixture.write('src/app/native_sources_unoq.h', '#pragma once\nint nativeValue();\n')
        fixture.write('src/app/native_sources_unoq.cpp', '#include "runtime.h"\n'
                      '#include "native_sources_unoq.h"\nint nativeValue(){return runtimeValue();}\n')
        for target, name in (('app', 'app'), ('bench/p0_matrix', 'p0_matrix')):
            for match in (False, True):
                args = [target, '--compile-only'] + (['--match'] if match else [])
                result = self.tool(fixture, *args)
                self.assertEqual(result.returncode, 0, result.stderr)
                stage = fixture.root / 'build/stage' / name
                self.assertTrue((stage / (name + '.ino')).is_file())
                self.assertFalse((stage / 'src/app/app.ino').exists())
                for stem in ('runtime', 'native_sources_unoq'):
                    for suffix in ('h', 'cpp'):
                        filename = stem + '.' + suffix
                        self.assertFalse((stage / filename).exists())
                        self.assertEqual((stage / 'src/app' / filename).read_bytes(),
                                         (fixture.root / 'src/app' / filename).read_bytes())
                    self.command(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                                  '-fsyntax-only', stage / 'src/app' / (stem + '.cpp')])
                compiled, = fixture.commands('compile')
                self.assertIn(f'-DMATCH={int(match)} -DMOTORS_ALLOWED={int(match)}', ' '.join(compiled))
                fixture.assert_no_motion_command()

    def test_actual_runtime_and_native_public_headers_resolve_staged_without_root_include_flags(self):
        fixture = self.fixture()
        fixture.use_reviewed_sources()
        result = self.tool(fixture, 'app', '--match', '--compile-only')
        self.assertEqual(result.returncode, 0, result.stderr)
        stage = fixture.root / 'build/stage/app'
        for filename in ('runtime.h', 'runtime.cpp', 'native_sources_unoq.h',
                         'native_sources_unoq.cpp', 'transaction.h'):
            self.assertEqual((stage / 'src/app' / filename).read_bytes(),
                             (ROOT / 'src/app' / filename).read_bytes())
        self.command(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsyntax-only',
                      stage / 'src/app/runtime.cpp'])
        header = fixture.root / 'public_runtime.cc'
        header.write_text('#include "' + (stage / 'src/app/runtime.h').as_posix() + '"\n'
                          '#include "' + (stage / 'src/app/native_sources_unoq.h').as_posix() + '"\n')
        self.command(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsyntax-only', header])
        fixture.assert_no_motion_command()

    def test_sketch_local_runtime_shadow_refuses_without_transport(self):
        fixture = self.fixture()
        fixture.write('bench/p0_matrix/src/app/runtime.h', '#error forbidden shadow\n')
        result = self.tool(fixture, 'bench/p0_matrix', '--compile-only')
        fixture.assert_failed(result)
        self.assertIn('src/app', result.stderr.lower())
        self.assertIn('conflicts', result.stderr.lower())
        self.assertEqual(fixture.events, [])

    def test_failed_app_match_compile_has_no_upload_or_success(self):
        fixture = self.fixture()
        result = self.tool(fixture, 'app', '--match', '--compile-only',
                           changes={'FAKE_FAIL': 'compile'})
        fixture.assert_failed(result)
        self.assertEqual(len(fixture.commands('compile')), 1)
        self.assertEqual(fixture.commands('upload'), [])
        fixture.assert_no_motion_command()


if __name__ == '__main__':
    unittest.main(verbosity=2)
