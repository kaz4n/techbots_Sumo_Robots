# Tests D166 diagnostic operation names under the observed CONFIG_PWM=1 macro.
# Preserves the target macro and numeric evidence ABI without reading implementation.
# Syntax-checks an opaque header/implementation inclusion in RAM; no binary or board.
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class MotorFaultMacroTests(unittest.TestCase):
    def test_observed_pwm_macro_survives_header_and_implementation_with_stable_operation_ids(self):
        compiler = shutil.which('g++')
        self.assertIsNotNone(compiler, 'g++ is required; macro regression must not silently skip')
        self.assertTrue(Path('/dev/shm').is_dir(), 'Linux RAM scratch is required')
        header = ROOT / 'bench/motor_fault/src/motor_fault.h'
        implementation = ROOT / 'bench/motor_fault/src/motor_fault.cpp'
        source = (
            f'#include "{header.as_posix()}"\n'
            '#if !defined(CONFIG_PWM) || CONFIG_PWM != 1\n'
            '#error "header must preserve CONFIG_PWM=1"\n'
            '#endif\n'
            f'#include "{implementation.as_posix()}"\n'
            '#if !defined(CONFIG_PWM) || CONFIG_PWM != 1\n'
            '#error "implementation must preserve CONFIG_PWM=1"\n'
            '#endif\n'
            'static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "inert fixture flags");\n'
            'static_assert(static_cast<int>(motor_fault::Operation::CONFIGURE_ENABLE) == 0);\n'
            'static_assert(static_cast<int>(motor_fault::Operation::CONFIGURE_PWM) == 1);\n'
            'static_assert(static_cast<int>(motor_fault::Operation::ENABLE) == 2);\n'
            'static_assert(static_cast<int>(motor_fault::Operation::PWM) == 3);\n'
            'static_assert(static_cast<int>(motor_fault::Operation::SETTLE) == 4);\n'
        )
        with tempfile.TemporaryDirectory(prefix='sumox-pwm-macro-', dir='/dev/shm') as temporary:
            translation_unit = Path(temporary) / 'macro_contract.cc'
            translation_unit.write_text(source, encoding='utf-8')
            command = [compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
                       '-fno-exceptions', '-fno-rtti', '-fsyntax-only',
                       '-DMATCH=0', '-DMOTORS_ALLOWED=0', '-DCONFIG_PWM=1',
                       '-I' + str(ROOT / 'src'), str(translation_unit)]
            result = subprocess.run(command, text=True, capture_output=True, timeout=60)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual([translation_unit], list(Path(temporary).iterdir()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
