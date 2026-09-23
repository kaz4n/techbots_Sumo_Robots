"""D094 independent source tests; production CPP is staged as opaque bytes.

All command streams and exact source hashes are retained, including failures.
No command invokes board lookup, transport, hardware or firmware upload.
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
NATIVE = ROOT/'tests/native_imu_bus'

class ImuResumeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++')
        if compiler is None:
            raise RuntimeError('D094 tests require Linux/WSL g++')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-d094-', dir='/dev/shm')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.source = cls.stage/'src'
        shutil.copytree(ROOT/'src', cls.source)
        cls.receipts = Path(os.environ.get('SUMO_IMU_RESUME_RECEIPT_DIR',
            ROOT/'state/analysis/P2_imu_resume_raw/author'))
        cls.receipts.mkdir(parents=True, exist_ok=True)
        cls.base = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                    '-fno-sanitize-recover=all', '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                    '-I', cls.source, '-I', ROOT/'tests', '-isystem', ROOT/'host/third_party']
        cls.main = cls.stage/'main.o'
        cls.command([*cls.base, '-c', NATIVE/'test_main.cc', '-o', cls.main])

    @classmethod
    def command(cls, argv, expected=0, timeout=180):
        paths = [p for p in cls.source.rglob('*') if p.is_file()]
        paths += [p for p in NATIVE.rglob('*') if p.is_file() and '__pycache__' not in str(p)]
        paths += [ROOT/'tests/test_imu_resume.cpp', ROOT/'tests/tooling/test_imu_resume.py']
        paths += list((ROOT/'tests/support').glob('imu*'))
        paths += list((ROOT/'bench/p2_imu_resume_compile').rglob('*.h'))
        paths += list((ROOT/'bench/p2_imu_resume_compile').rglob('*.cpp'))
        paths += list((ROOT/'bench/p2_imu_resume_compile').glob('*.ino'))
        hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
        try:
            result = subprocess.run(list(map(str, argv)), capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            result = SimpleNamespace(returncode=124, stdout=str(exc.stdout or ''), stderr=str(exc.stderr or '')+'\nTIMEOUT')
        payload = {'argv': list(map(str, argv)), 'returncode': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr, 'sha256': hashes,
                   'capture': 'subprocess text=True; newline normalized'}
        (cls.receipts/f'command_{time.time_ns()}.json').write_text(json.dumps(payload, indent=2)+'\n')
        if result.returncode != expected:
            raise AssertionError(result.stdout + result.stderr)
        return result

    def build(self, label, cases, native=False, full=False, definitions=(), extras=()):
        sources = list(cases)
        if full:
            sources += sorted((self.source/'core').glob('*.cpp'))
            sources += [self.source/'hal'/p for p in ('imu.cpp', 'imu_acquisition.cpp',
                'imu_acquisition_async.cpp', 'imu_heading.cpp', 'imu_adapter.cpp')]
        args = list(self.base) + list(definitions)
        if native:
            args += ['-DARDUINO_ARCH_ZEPHYR', '-I', NATIVE,
                     '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
            sources += [self.source/'hal/imu_bus_unoq.cpp', self.source/'hal/imu_bus_async_unoq.cpp',
                        NATIVE/'native_fixture.cc', NATIVE/'isolation.cc']
        else:
            sources += [ROOT/'tests/support'/p for p in ('imu_bus_fake.cpp',
                        'imu_acquisition_fake.cpp', 'imu_resume_fake.cpp')]
        binary = self.stage/label
        self.command([*args, *sources, *extras, self.main, '-o', binary])
        result = self.command([binary, '--no-colors'], timeout=90)
        self.assertIn('Status: SUCCESS!', result.stdout)
        print(label + ': ' + ' | '.join(line for line in result.stdout.splitlines()
              if 'test cases:' in line or 'assertions:' in line), flush=True)

    def test_actual_acquirer_estimator_robot_contract_both_motor_settings(self):
        for enabled in (0, 1):
            self.build(f'host-{enabled}', [ROOT/'tests/test_imu_resume.cpp'], full=True,
                       definitions=(f'-DMOTORS_ALLOWED={enabled}',))

    def test_actual_native_resumption_protocol_budget_and_faults(self):
        self.build('native', [NATIVE/'resume_cases.cc'], native=True)

    def test_established_native_suites_still_pass_with_async_linked(self):
        cases = ('cases.cc', 'failure_cases.cc', 'ownership_cases.cc', 'timing_cases.cc', 'acquisition_cases.cc')
        self.build('legacy-native', [NATIVE/p for p in cases], native=True)

    def test_actual_probe_startup_is_inert_in_both_macro_modes(self):
        probe = self.stage/'probe'; shutil.copytree(ROOT/'bench/p2_imu_resume_compile', probe)
        sketch = probe/'sketch.cc'; shutil.copyfile(probe/'p2_imu_resume_compile.ino', sketch)
        extras = [probe/'src/imu_resume_probe.cpp', sketch] + [self.source/'hal'/p
                  for p in ('motors.cpp', 'recorder.cpp', 'recorder_frames.cpp')]
        for enabled in (0, 1):
            self.build(f'probe-{enabled}', [NATIVE/'resume_probe.cc'], native=True, full=True,
                       definitions=(f'-DMOTORS_ALLOWED={enabled}', f'-DMATCH={enabled}',
                                    '-I', str(probe), '-I', str(probe/'src')), extras=extras)

    def test_all_upload_modes_refuse_before_target_or_transport_lookup(self):
        spec = importlib.util.spec_from_file_location('d094_board_tool', ROOT/'tools/board_tool.py')
        board = importlib.util.module_from_spec(spec); spec.loader.exec_module(board)
        for transport in ('adb', 'ssh'):
            for match in (False, True):
                for startup in ('default', 'immediate'):
                    with self.subTest(transport=transport, match=match, startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict(os.environ, {'SUMO_TRANSPORT': transport}))
                        target = stack.enter_context(mock.patch.object(board, 'target'))
                        remote = stack.enter_context(mock.patch.object(board, 'remote'))
                        require = stack.enter_context(mock.patch.object(board, 'require_transport'))
                        with redirect_stderr(io.StringIO()), self.assertRaises(ValueError):
                            board.flash(SimpleNamespace(sketch='bench/p2_imu_resume_compile',
                                match=match, startup=startup, compile_only=False))
                        target.assert_not_called(); remote.assert_not_called(); require.assert_not_called()

if __name__ == '__main__':
    unittest.main(verbosity=2)
