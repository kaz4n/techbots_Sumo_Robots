# Compiles opaque production B3 transport bytes against an independent native model.
# Every staged source/config and subprocess result is retained with exact hashes.
# Linux/WSL execution has no board connection and refuses every probe upload mode.
from contextlib import ExitStack
import hashlib
import importlib.util
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
FIXTURE = ROOT / 'tests/native_imu_bus'

class NativeImuBusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++')
        if compiler is None:
            raise RuntimeError('Run native IMU bus tests under Linux/WSL with g++')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-native-imu-bus-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.manifests = {}
        cls.base = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
            '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined', '-fno-sanitize-recover=all',
            '-DARDUINO_ARCH_ZEPHYR', '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
            '-I', str(FIXTURE), '-isystem', str(ROOT/'host/third_party')]
        cls.main = cls.stage/'main.o'
        cls.command([*cls.base, '-c', str(FIXTURE/'test_main.cc'), '-o', str(cls.main)])

    @classmethod
    def command(cls, argv, timeout=120, expected=0):
        try:
            result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            result = SimpleNamespace(returncode=124, stdout=str(exc.stdout or ''), stderr=str(exc.stderr or '')+'\nTIMEOUT')
        folder = Path(os.environ.get('SUMO_NATIVE_RECEIPT_DIR', ROOT/'state/analysis/P2_imu_bus_raw/author_receipts'))
        folder.mkdir(parents=True, exist_ok=True)
        native = next((Path(a) for a in argv if str(a).endswith('/hal/imu_bus_unoq.cpp')), None)
        manifest = cls.manifests.get(str(argv[0]))
        if native:
            manifest = {'production': hashlib.sha256(native.read_bytes()).hexdigest(),
                'header': hashlib.sha256(native.with_suffix('.h').read_bytes()).hexdigest(),
                'config': hashlib.sha256((native.parent.parent/'config.h').read_bytes()).hexdigest()}
        payload = {'argv': list(map(str, argv)), 'returncode': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr, 'staged_source_manifest': manifest,
            'capture': 'subprocess text=True; newline normalized',
            'fixture_manifest': {str(p.relative_to(FIXTURE)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in FIXTURE.rglob('*') if p.is_file() and '__pycache__' not in str(p)}}
        (folder/f'native_imu_bus_{time.time_ns()}.json').write_bytes((json.dumps(payload,indent=2)+'\n').encode())
        if result.returncode != expected:
            raise AssertionError('Opaque native command failed:\n'+result.stdout+result.stderr)
        return result

    @classmethod
    def variant(cls, case='cases.cc', definitions=(), edits=None, probe=False):
        slot = cls.stage/f'variant-{len(list(cls.stage.glob("variant-*")))}'
        source = slot/'src'
        (source/'hal').mkdir(parents=True)
        for p in (ROOT/'src/hal').glob('imu_bus*'):
            if p.is_file():
                shutil.copyfile(p, source/'hal'/p.name)
        shutil.copyfile(ROOT/'src/config.h', source/'config.h')
        if edits:
            config = (source/'config.h').read_text()
            for name, value in edits.items():
                config, n = re.subn(r'(\b'+re.escape(name)+r'\s*=\s*)[^;]+;', r'\g<1>'+value+';', config)
                if n != 1:
                    raise AssertionError('Unmatched config name: '+name)
            (source/'config.h').write_text(config)
        binary = slot/'native-imu-bus'
        argv = [*cls.base, '-I', str(source), *definitions, str(FIXTURE/case),
            str(FIXTURE/'native_fixture.cc'), str(FIXTURE/'isolation.cc'),
            str(source/'hal/imu_bus_unoq.cpp'), str(cls.main),
            '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
        if probe:
            sketch = slot/'imu_bus_sketch.cpp'
            shutil.copyfile(ROOT/'bench/p2_imu_bus_compile/p2_imu_bus_compile.ino',sketch)
            argv += ['-I',str(ROOT/'bench/p2_imu_bus_compile/src'),'-I',str(ROOT/'bench/p2_imu_bus_compile'),
                     str(ROOT/'bench/p2_imu_bus_compile/src/imu_bus_probe.cpp'),str(sketch)]
        cls.command([*argv,'-o',str(binary)])
        cls.manifests[str(binary)] = {'production':hashlib.sha256((source/'hal/imu_bus_unoq.cpp').read_bytes()).hexdigest(),
            'header':hashlib.sha256((source/'hal/imu_bus_unoq.h').read_bytes()).hexdigest(),
            'config':hashlib.sha256((source/'config.h').read_bytes()).hexdigest()}
        return binary

    def execute(self, binary):
        result = self.command([str(binary),'--no-colors'],timeout=40)
        self.assertIn('Status: SUCCESS!',result.stdout)
        print(' | '.join(x for x in result.stdout.splitlines() if 'test cases:' in x or 'assertions:' in x),flush=True)

    def test_b3_isolation_propagates_child_assertions_and_signals(self):
        binary = self.variant('isolation_selftest.cc')
        for name in ('*assertion*','*signal*'):
            result = self.command([str(binary),'--no-colors','--test-case='+name],expected=1)
            self.assertIn('Status: FAILURE!',result.stdout)

    def test_b3_transport_contract(self):
        self.execute(self.variant())

    def test_b3_failures_and_cleanup(self):
        self.execute(self.variant('failure_cases.cc'))

    def test_b3_ownership_and_boot_claim(self):
        self.execute(self.variant('ownership_cases.cc'))

    def test_b3_deadlines_wrap_and_frozen_time(self):
        self.execute(self.variant('timing_cases.cc'))

    def test_b3_installed_metadata_mismatch(self):
        for kind in range(1,28):
            with self.subTest(kind=kind):
                self.execute(self.variant('metadata_cases.cc',(f'-DNATIVE_BAD_METADATA={kind}',)))

    def test_b3_configuration_rejection(self):
        variants = [('IMU_I2C_ADDRESS','0x67U'),('IMU_I2C_ADDRESS','0x6aU'),
            ('IMU_I2C_GPIO_PORT','2U'),('IMU_I2C_SCL_PIN','13U'),('IMU_I2C_SDA_PIN','12U'),
            ('IMU_I2C_AF','5U'),('IMU_I2C_TIMINGR','0x40FC1228U')]
        for name in ('IMU_I2C_SETUP_US','IMU_I2C_TRANSFER_US','IMU_I2C_CLEANUP_US','IMU_I2C_MAX_POLLS'):
            variants += [(name,'0U'),(name,'0x80000000U')]
        for name,value in variants:
            with self.subTest(name=name,value=value):
                self.execute(self.variant('config_cases.cc',edits={name:value}))

    def test_b3_second_supported_address(self):
        self.execute(self.variant(edits={'IMU_I2C_ADDRESS':'0x69U'}))

    def test_b3_probe_startup_and_ten_thousand_loops_are_inert(self):
        for allowed in (0,1):
            with self.subTest(allowed=allowed):
                self.execute(self.variant('probe_cases.cc',(f'-DMATCH={allowed}',f'-DMOTORS_ALLOWED={allowed}'),probe=True))

    def test_b3_every_probe_upload_mode_refuses_before_transport_lookup(self):
        spec = importlib.util.spec_from_file_location('imu_bus_board_tool',ROOT/'tools/board_tool.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for transport in ('adb','ssh'):
            for match in (False,True):
                for startup in ('default','immediate'):
                    with self.subTest(transport=transport,match=match,startup=startup),ExitStack() as stack:
                        stack.enter_context(mock.patch.dict('os.environ',{'SUMO_TRANSPORT':transport}))
                        target=stack.enter_context(mock.patch.object(module,'target'))
                        remote=stack.enter_context(mock.patch.object(module,'remote'))
                        with self.assertRaises(ValueError):
                            module.flash(SimpleNamespace(sketch='bench/p2_imu_bus_compile',match=match,startup=startup,compile_only=False))
                        target.assert_not_called();remote.assert_not_called()

if __name__ == '__main__':
    unittest.main(verbosity=2)
