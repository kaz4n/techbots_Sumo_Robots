# Verifies the compile probe cannot activate its production MotorGate.
# Keeps default and active-branch compilation separate from upload permission.
# Runs strict host executables and controlled upload refusals without board access.
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


class MotorGateProbeTests(unittest.TestCase):
    def compile_and_run(self, allowed):
        with tempfile.TemporaryDirectory(prefix='sumo_motor_probe_') as folder:
            path = Path(folder)
            shutil.copytree(ROOT / 'src', path / 'src')
            shutil.copy2(ROOT / 'bench/p2_motor_gate_compile/p2_motor_gate_compile.ino',
                         path / 'probe.cpp')
            (path / 'main.cpp').write_text('''
#define EMPTY 197
#include "probe.cpp"
static_assert(EMPTY == 197, "Arduino macro must be restored");
int main() {
    if (p2_motor_gate.fault() != motors::Fault::NONE) return 1;
    if (p2_motor_gate_probe != nullptr) return 2;
    setup();
    if (p2_motor_gate_probe != &motorGateProbe) return 3;
    for (unsigned i = 0; i < 10000; ++i) loop();
    // Calling begin/apply/reset on this null Port would change the fault.
    return p2_motor_gate.fault() == motors::Fault::NONE ? 0 : 4;
}
''', encoding='utf-8')
            binary = path / 'probe'
            command = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic',
                       '-Werror', '-fno-exceptions', '-fno-rtti',
                       '-fsanitize=undefined', '-fno-sanitize-recover=all',
                       f'-DMOTORS_ALLOWED={allowed}', f'-DMATCH={allowed}',
                       '-I', str(path), str(path / 'main.cpp'),
                       str(path / 'src/hal/motors.cpp'),
                       *map(str, sorted((path / 'src/core').glob('*.cpp'))),
                       '-o', str(binary)]
            built = subprocess.run(command, capture_output=True, text=True, timeout=90)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            ran = subprocess.run([str(binary)], capture_output=True, text=True, timeout=15)
            self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)

    def test_default_probe_startup_and_10000_loops_are_inert(self):
        self.compile_and_run(0)

    def test_enabled_branch_probe_startup_and_10000_loops_are_inert(self):
        self.compile_and_run(1)

    def test_all_upload_configurations_refuse_before_target_lookup(self):
        spec = importlib.util.spec_from_file_location('motor_probe_board_tool',
                                                      ROOT / 'tools/board_tool.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for match in (False, True):
            for startup in (None, 'default', 'immediate'):
                with self.subTest(match=match, startup=startup), ExitStack() as stack:
                    target = stack.enter_context(mock.patch.object(module, 'target'))
                    remote = stack.enter_context(mock.patch.object(module, 'remote'))
                    args = SimpleNamespace(sketch='bench/p2_motor_gate_compile',
                                           match=match, startup=startup, compile_only=False)
                    with self.assertRaises(ValueError):
                        module.flash(args)
                    target.assert_not_called()
                    remote.assert_not_called()


if __name__ == '__main__':
    unittest.main()
