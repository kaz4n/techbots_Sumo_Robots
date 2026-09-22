# Builds and runs independent P0 UART adapter contract cases.
# Uses real opaque production sources and controlled installed-API substitutes.
# Run with Python 3 on Linux/WSL; each case starts fresh production static state.
"""Independent host adapter tests; never accesses or commands the board."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CASES = (
    "setup_success",
    "setup_init_negative",
    "setup_init_positive",
    "setup_nonready",
    "setup_config_failure",
    "setup_baud",
    "setup_parity",
    "setup_stop",
    "setup_data",
    "setup_flow",
    "setup_callback_negative",
    "setup_callback_positive",
    "packets",
    "busy_retention",
    "timeout_no_progress",
    "timeout_after",
    "timeout_partial",
    "timeout_final_tc",
    "timeout_wrap",
    "update_zero",
    "update_negative",
    "update_positive",
    "update_zero_final",
    "update_negative_final",
    "update_positive_final",
    "ready_zero",
    "ready_negative",
    "ready_positive",
    "ready_zero_final",
    "ready_negative_final",
    "ready_positive_final",
    "fill_zero",
    "fill_negative",
    "fill_oversized",
    "complete_zero_final",
    "complete_negative_final",
    "complete_positive_final",
    "idle_irq",
    "completed_idle_irq",
)


class CounterUartContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("g++")
        if compiler is None:
            raise RuntimeError("g++ required; on Windows run this runner in WSL")
        cls.temporary = tempfile.TemporaryDirectory(prefix="p0-counter-uart-")
        cls.addClassCleanup(cls.temporary.cleanup)
        stage = Path(cls.temporary.name)
        # The sketch's staged config must be the actual repository header.
        shutil.copyfile(ROOT / "src/config.h", stage / "config.h")
        cls.executable = stage / "counter_uart_cases"
        sources = ROOT / "bench/p0_matrix/src"
        command = [
            compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", "-pedantic",
            "-fno-exceptions", "-fno-rtti", "-DMOTORS_ALLOWED=0",
            "-I", str(HERE / "uart_stubs"), "-I", str(stage),
            "-I", str(sources), str(HERE / "counter_uart_cases.cc"),
            str(sources / "counter_uart.cpp"), str(sources / "counter_packet.cpp"),
            "-o", str(cls.executable),
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise AssertionError("Opaque adapter build failed:\n" + result.stdout
                                 + result.stderr)


def contract_case(name):
    def run(self):
        result = subprocess.run([str(self.executable), name], capture_output=True,
                                text=True, timeout=3)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "PASS " + name)
    return run


for case in CASES:
    setattr(CounterUartContract, "test_" + case, contract_case(case))


if __name__ == "__main__":
    unittest.main(verbosity=2)
