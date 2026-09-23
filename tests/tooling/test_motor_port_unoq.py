# Verifies the actual D077 native UNO Q Port and actual MotorGate against contracts.
# Compiles opaque production files with counted installed-shaped hardware fixtures.
# Linux/WSL only; all tests are local and none access a board or upload firmware.
from contextlib import ExitStack
import importlib.util
import hashlib
import json
import os
import time
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/locked/native_motor_port'


class NativeMotorPortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = shutil.which('g++')
        if cls.compiler is None:
            raise RuntimeError('Run native motor tests under Linux/WSL with g++')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-native-motor-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.base = [cls.compiler, '-std=c++17', '-O1', '-Wall', '-Wextra',
                    '-Wpedantic', '-Werror', '-fno-exceptions', '-fno-rtti',
                    '-fsanitize=undefined', '-fno-sanitize-recover=all',
                    '-DARDUINO_ARCH_ZEPHYR', '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
                    '-I', str(FIXTURE), '-I', str(ROOT / 'src'),
                    '-isystem', str(ROOT / 'host/third_party')]
        cls.core = []
        for source in sorted((ROOT / 'src/core').glob('*.cpp')):
            obj = cls.stage / (source.stem + '.o')
            cls.build([*cls.base, '-c', str(source), '-o', str(obj)])
            cls.core.append(str(obj))
        cls.main = cls.stage / 'doctest-main.o'
        cls.build([*cls.base, '-c', str(FIXTURE / 'test_main.cc'), '-o', str(cls.main)])
        cls.binaries = {allowed: cls.variant(allowed=allowed) for allowed in (0, 1)}

    @classmethod
    def receipt(cls, command, result):
        folder = os.environ.get('SUMO_NATIVE_RECEIPT_DIR')
        if folder:
            path = Path(folder)
            path.mkdir(parents=True, exist_ok=True)
            payload = {'argv': list(map(str, command)), 'returncode': result.returncode,
                       'stdout': result.stdout, 'stderr': result.stderr,
                       'capture': 'subprocess text=True; newline normalized',
                       'production_sha256': hashlib.sha256((ROOT / 'src/hal/motor_port_unoq.cpp').read_bytes()).hexdigest()}
            (path / ('native_tests_' + str(time.time_ns()) + '.json')).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    @classmethod
    def build(cls, command):
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        cls.receipt(command, result)
        if result.returncode:
            raise AssertionError('Opaque native build failed:\n' + result.stdout + result.stderr)
        return result

    @classmethod
    def variant(cls, allowed=0, definitions=(), metadata=False, probe=False):
        target = cls.stage / ('native-' + str(len(list(cls.stage.glob('native-*')))))
        case = 'metadata_cases.cc' if metadata else 'probe_cases.cc' if probe else 'cases.cc'
        command = [*cls.base, f'-DMOTORS_ALLOWED={allowed}', f'-DMATCH={allowed}',
                   *definitions, str(FIXTURE / case), str(FIXTURE / 'native_fixture.cc'),
                   str(ROOT / 'src/hal/motor_port_unoq.cpp'),
                   str(ROOT / 'src/hal/motors.cpp'), *cls.core, str(cls.main),
                   '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
        if probe:
            # Opaque staging preserves the real source bytes and public include shape.
            source_dir = cls.stage / 'src'
            if not source_dir.exists():
                source_dir.symlink_to(ROOT / 'src', target_is_directory=True)
            sketch = cls.stage / 'native_probe_sketch.cpp'
            shutil.copyfile(ROOT / 'bench/p2_motor_native_compile/p2_motor_native_compile.ino', sketch)
            command += ['-I', str(ROOT / 'bench/p2_motor_native_compile/src'),
                        '-I', str(ROOT / 'bench/p2_motor_native_compile'),
                        str(ROOT / 'bench/p2_motor_native_compile/src/native_motor_probe.cpp'),
                        str(sketch)]
        cls.build([*command, '-o', str(target)])
        return target

    def run_binary(self, executable):
        result = subprocess.run([str(executable), '--no-colors'], capture_output=True,
                                text=True, timeout=35)
        self.receipt([str(executable), '--no-colors'], result)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Status: SUCCESS!', result.stdout)
        print(' | '.join(line for line in result.stdout.splitlines() if 'test cases:' in line or 'assertions:' in line), flush=True)

    def test_b3_b6_b7_actual_native_default_disabled_contract(self):
        self.run_binary(self.binaries[0])

    def test_b3_b6_b7_actual_native_host_only_enabled_contract(self):
        self.run_binary(self.binaries[1])

    def test_b3_invalid_gpio_mappings_at_every_motor_signal_reject_before_configuration(self):
        for kind in (1, 2, 3, 4, 5, 11, 12):
            for slot in range(4 if kind == 5 else 5):
                with self.subTest(kind=kind, slot=slot):
                    self.run_binary(self.variant(definitions=(f'-DNATIVE_BAD_MAP={kind}',
                                    f'-DNATIVE_BAD_SLOT={slot}'), metadata=True))

    def test_b3_invalid_pwm_mappings_at_every_motor_channel_reject_before_configuration(self):
        for kind in (6, 7, 8, 9, 10):
            for slot in range(4):
                with self.subTest(kind=kind, slot=slot):
                    self.run_binary(self.variant(definitions=(f'-DNATIVE_BAD_MAP={kind}',
                                    f'-DNATIVE_BAD_SLOT={slot}'), metadata=True))

    def test_b3_null_native_configs_and_mismatched_paired_tables_reject(self):
        for define in ('NATIVE_NULL_CONFIG=1', 'NATIVE_NULL_CONFIG=2',
                       'NATIVE_NULL_CONFIG=3', 'NATIVE_NULL_CONFIG=4',
                       'NATIVE_SHORT_PWM', 'NATIVE_SHORT_PAD'):
            with self.subTest(metadata=define):
                self.run_binary(self.variant(definitions=('-D' + define,), metadata=True))

    def test_b3_selected_arduino_indices_must_exist_in_generated_table(self):
        for size in (3, 5, 6, 9, 10, 19):
            with self.subTest(table_size=size):
                self.run_binary(self.variant(definitions=(f'-DNATIVE_TABLE_SIZE={size}',),
                                             metadata=True))

    def test_b3_unsupported_clock_zero_nonintegral_overflow_domain_and_divisor_reject(self):
        for definition in ('NATIVE_HCLK=0', 'NATIVE_HCLK=159999999',
                           'NATIVE_HCLK=4000000000UL', 'NATIVE_DOMAIN1=13',
                           'NATIVE_DOMAIN3=14', 'NATIVE_CLOCK_DIV=1',
                           'NATIVE_APB1=0', 'NATIVE_APB2=0'):
            with self.subTest(clock=definition):
                self.run_binary(self.variant(definitions=('-DNATIVE_INVALID_CLOCK',
                                                         '-D' + definition), metadata=True))

    def test_b3_native_probe_default_and_match_startup_and_10000_loops_are_inert(self):
        for allowed in (0, 1):
            with self.subTest(motors_allowed=allowed):
                self.run_binary(self.variant(allowed=allowed, probe=True))

    def test_b3_all_native_probe_upload_modes_refuse_before_transport_lookup(self):
        spec = importlib.util.spec_from_file_location('native_motor_board_tool',
                                                      ROOT / 'tools/board_tool.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for transport in ('adb', 'ssh'):
            for match in (False, True):
                for startup in ('default', 'immediate'):
                    with self.subTest(transport=transport, match=match, startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict('os.environ', {'SUMO_TRANSPORT': transport}))
                        target = stack.enter_context(mock.patch.object(module, 'target'))
                        remote = stack.enter_context(mock.patch.object(module, 'remote'))
                        args = SimpleNamespace(sketch='bench/p2_motor_native_compile', match=match,
                                               startup=startup, compile_only=False)
                        with self.assertRaises(ValueError):
                            module.flash(args)
                        target.assert_not_called()
                        remote.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
