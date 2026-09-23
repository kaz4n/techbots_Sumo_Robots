# Verifies D-076/B1 native opponent input and B5 raw polarity contracts.
# Compiles the opaque production source with independent counted native headers.
# Run under Linux/WSL; no test uses a board, upload, motor or live sensor.
from contextlib import ExitStack
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / 'tests/support/opponent_gpio'
ERROR_VALUES = (-(1 << 31), -1234, -19, -5, -1, 2, 7, (1 << 31) - 1)


class OpponentNativeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = shutil.which('g++')
        if cls.compiler is None:
            raise RuntimeError('g++ required; run this test under Linux/WSL')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-opponent-native-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        # Same constexpr array form as wiring_private.h, with controlled specs.
        entries = '\n'.join(f'#if OPP_TABLE_SIZE > {i}\nfixtureSpec({i}),\n#endif'
                            for i in range(70))
        (cls.stage / 'wiring_private.h').write_text(
            '#pragma once\n#include "mapping.h"\nnamespace zephyr { namespace arduino {\n'
            'constexpr gpio_dt_spec arduino_pins[] = {\n' + entries + '\n};\n}}\n',
            encoding='utf-8')
        cls.base = [cls.compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
                    '-pedantic', '-fno-exceptions', '-fno-rtti',
                    '-fsanitize=undefined', '-fno-sanitize-recover=all',
                    '-DARDUINO_ARCH_ZEPHYR', '-DMOTORS_ALLOWED=0',
                    '-I', str(FIXTURES), '-I', str(cls.stage),
                    '-I', str(ROOT / 'src')]
        cls.core = cls.stage / 'opp_fusion.o'
        cls.checked_build([*cls.base, '-c', str(ROOT / 'src/core/opp_fusion.cpp'),
                           '-o', str(cls.core)])
        cls.default = cls.build_variant()

    @classmethod
    def checked_build(cls, command, expected_success=True):
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if expected_success and result.returncode:
            raise AssertionError('Opaque native source build failed:\n' + result.stdout + result.stderr)
        return result

    @classmethod
    def build_variant(cls, kind=0, slot=0, count=70, probe=False, motors=0):
        target = cls.stage / f'opp-{kind}-{slot}-{count}-{probe}-{motors}'
        command = [*cls.base, f'-DOPP_MAP_KIND={kind}', f'-DOPP_BAD_SLOT={slot}',
                   f'-DOPP_TABLE_SIZE={count}', str(FIXTURES / 'cases.cc'),
                   str(ROOT / 'src/hal/opp_sensors.cpp'), str(cls.core),
                   '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
        if probe:
            # Stage exactly the public bench shape; no implementation is read.
            (cls.stage / 'src').mkdir(exist_ok=True)
            shutil.copyfile(ROOT / 'src/config.h', cls.stage / 'src/config.h')
            sketch = cls.stage / 'probe.cpp'
            shutil.copyfile(ROOT / 'bench/p2_opp_compile/p2_opp_compile.ino', sketch)
            command += ['-DOPP_PROBE', '-I', str(ROOT / 'bench/p2_opp_compile/src'),
                        '-I', str(ROOT / 'bench/p2_opp_compile'), str(sketch),
                        str(ROOT / 'bench/p2_opp_compile/src/opponent_probe.cpp')]
        if motors:
            command += ['-UMOTORS_ALLOWED', '-DMOTORS_ALLOWED=1']
        result = cls.checked_build([*command, '-o', str(target)], not motors)
        return result if motors else target

    def run_case(self, name, *args, executable=None):
        result = subprocess.run([str(executable or self.default), name, *map(str, args)],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), 'PASS ' + name)

    def test_b1_all_128_electrical_masks_are_uncorrected_and_independent(self):
        self.run_case('masks')

    def test_b5_all_128_masks_have_exactly_one_polarity_conversion_in_real_debouncer(self):
        self.run_case('composition')

    def test_b1_signed_config_failures_at_every_slot_invalidate_previous_success(self):
        for slot in range(7):
            for value in (*ERROR_VALUES, 1):
                with self.subTest(slot=slot, value=value):
                    self.run_case('init-failure', slot, value)

    def test_b1_initialization_readiness_at_every_slot_and_explicit_retry(self):
        for slot in range(7):
            with self.subTest(slot=slot):
                self.run_case('init-ready', slot)

    def test_b1_read_failures_at_every_slot_clear_stale_bits_and_recover_without_begin(self):
        for slot in range(7):
            for value in ERROR_VALUES:
                with self.subTest(slot=slot, value=value):
                    self.run_case('read-failure', slot, value)

    def test_b1_lost_readiness_at_every_slot_skips_only_that_read(self):
        for slot in range(7):
            with self.subTest(slot=slot):
                self.run_case('read-ready', slot)

    def test_b1_mixed_failures_and_complete_unavailability_retain_all_statuses(self):
        self.run_case('mixed')

    def test_b1_clock_brackets_each_native_pass_with_unsigned_wrap(self):
        self.run_case('timestamps')

    def test_b1_constructor_and_uninitialized_read_are_inert_and_instances_are_independent(self):
        self.run_case('instances')

    def test_b1_ten_thousand_reads_are_bounded_and_allocate_nothing(self):
        self.run_case('long-run')

    def test_b1_null_invalid_pin_nonzero_flags_and_duplicate_maps_reject_entire_bank(self):
        for kind in range(1, 7):
            for slot in range(7):
                with self.subTest(kind=kind, slot=slot):
                    binary = self.build_variant(kind=kind, slot=slot)
                    self.run_case('malformed', executable=binary)

    def test_b1_each_arduino_index_must_be_inside_the_native_table(self):
        for index in (11, 12, 13, 16, 17, 18, 19):
            with self.subTest(table_size=index):
                binary = self.build_variant(count=index)
                self.run_case('malformed', executable=binary)

    def test_b1_each_physical_pin_must_be_in_the_device_mask(self):
        for slot in range(7):
            with self.subTest(slot=slot):
                self.run_case('mask-invalid', slot)

    def test_b1_highest_representable_gpio_bit_is_valid_without_signed_shift(self):
        for slot in range(7):
            with self.subTest(slot=slot):
                binary = self.build_variant(kind=7, slot=slot)
                self.run_case('valid-high-pin', executable=binary)

    def test_b1_equal_pin_numbers_on_different_ports_are_not_duplicates(self):
        for slot in range(7):
            with self.subTest(slot=slot):
                binary = self.build_variant(kind=8, slot=slot)
                self.run_case('valid-high-pin', executable=binary)

    def test_b1_probe_global_constructor_setup_and_10000_loops_never_call_native_io(self):
        self.run_case('probe', executable=self.build_variant(probe=True))

    def test_b1_probe_motor_enabled_build_is_rejected(self):
        result = self.build_variant(probe=True, motors=1)
        self.assertNotEqual(result.returncode, 0, 'Motor-enabled opponent probe compiled')
        self.assertIn('static assertion failed', result.stderr)

    def test_b1_all_probe_upload_modes_refuse_before_transport_lookup(self):
        specification = importlib.util.spec_from_file_location(
            'opponent_probe_board_tool', ROOT / 'tools/board_tool.py')
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        for match in (False, True):
            for startup in (None, 'default', 'immediate'):
                with self.subTest(match=match, startup=startup), ExitStack() as stack:
                    target = stack.enter_context(mock.patch.object(module, 'target'))
                    remote = stack.enter_context(mock.patch.object(module, 'remote'))
                    args = SimpleNamespace(sketch='bench/p2_opp_compile', match=match,
                                           startup=startup, compile_only=False)
                    with self.assertRaises(ValueError):
                        module.flash(args)
                    target.assert_not_called()
                    remote.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
