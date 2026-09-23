"""D097 independent getter and actual native callback tests.

Production CPP is copied and compiled as opaque bytes, never parsed for assertions.
Commands, source hashes and raw outputs are retained for success and failure alike.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/native_imu_setup_failure'


class ImuSetupFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++')
        if compiler is None:
            raise RuntimeError('D097 tests require Linux/WSL g++')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-d097-', dir='/dev/shm')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.source = cls.stage / 'src'
        shutil.copytree(ROOT / 'src', cls.source)
        cls.receipts = Path(os.environ.get('SUMO_IMU_FAULT_ACCESS_RECEIPT_DIR',
            ROOT / 'state/analysis/P2_imu_fault_access_raw/author'))
        cls.receipts.mkdir(parents=True, exist_ok=True)
        cls.paths = sorted(p for p in cls.source.rglob('*') if p.is_file())
        cls.paths += sorted(p for p in FIXTURE.iterdir() if p.is_file())
        cls.paths += [ROOT / p for p in ('tests/test_imu_setup_failure.cpp',
            'tests/tooling/test_imu_setup_failure.py', 'tests/native_imu_bus/test_main.cc',
            'host/third_party/doctest.h', 'state/analysis/P2_imu_fault_access_contract.md')]
        cls.paths += sorted((ROOT / 'tests/support').glob('imu*'))
        cls.manifest = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in cls.paths}
        cls.base = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
            '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
            '-fno-sanitize-recover=all', '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
            '-I', cls.source, '-I', ROOT / 'tests', '-isystem', ROOT / 'host/third_party']
        cls.command([compiler, '--version'])
        cls.main = cls.stage / 'main.o'
        cls.command([*cls.base, '-c', ROOT / 'tests/native_imu_bus/test_main.cc', '-o', cls.main])

    @classmethod
    def command(cls, argv):
        argv = list(map(str, argv))
        name = 'command_' + str(time.time_ns())
        try:
            result = subprocess.run(argv, capture_output=True, timeout=180)
            code, stdout, stderr = result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            code, stdout, stderr = 124, exc.stdout or b'', (exc.stderr or b'') + b'\nTIMEOUT\n'
        (cls.receipts / (name + '.stdout')).write_bytes(stdout)
        (cls.receipts / (name + '.stderr')).write_bytes(stderr)
        payload = {'argv': argv, 'returncode': code, 'sha256': cls.manifest,
            'stdout': stdout.decode('utf-8', errors='replace'),
            'stderr': stderr.decode('utf-8', errors='replace'),
            'raw_stdout': name + '.stdout', 'raw_stderr': name + '.stderr',
            'raw_stdout_sha256': hashlib.sha256(stdout).hexdigest(),
            'raw_stderr_sha256': hashlib.sha256(stderr).hexdigest()}
        (cls.receipts / (name + '.json')).write_text(json.dumps(payload, indent=2) + '\n')
        if code != 0:
            raise AssertionError(payload['stdout'] + payload['stderr'])
        return payload['stdout']

    def build(self, label, sources, enabled, native=False):
        args = [*self.base, f'-DMOTORS_ALLOWED={enabled}', f'-DMATCH={enabled}']
        if native:
            args += ['-DARDUINO_ARCH_ZEPHYR', '-I', FIXTURE]
        binary = self.stage / label
        self.command([*args, *sources, self.main, '-o', binary])
        output = self.command([binary, '--no-colors'])
        self.assertIn('Status: SUCCESS!', output)
        print(label + ': ' + ' | '.join(line for line in output.splitlines()
              if 'test cases:' in line or 'assertions:' in line), flush=True)

    def test_b3_b14_actual_acquirer_passive_evidence_both_modes(self):
        sources = [ROOT / 'tests/test_imu_setup_failure.cpp']
        sources += [ROOT / 'tests/support' / name for name in
            ('imu_bus_fake.cpp', 'imu_acquisition_fake.cpp', 'imu_resume_fake.cpp')]
        sources += [self.source / 'hal' / name for name in
            ('imu.cpp', 'imu_acquisition.cpp', 'imu_acquisition_async.cpp')]
        for enabled in (0, 1):
            with self.subTest(enabled=enabled):
                self.build(f'acquirer-{enabled}', sources, enabled)

    def test_b3_actual_native_callback_uses_getter_both_modes(self):
        sources = [FIXTURE / 'callback_cases.cc', self.source / 'app/native_sources_unoq.cpp']
        for enabled in (0, 1):
            with self.subTest(enabled=enabled):
                self.build(f'callback-{enabled}', sources, enabled, native=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
