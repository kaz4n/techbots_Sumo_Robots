# Compiles and runs independent tests of the opaque P0 counter packet source.
# Keeps firmware-format and lifecycle evidence separate from board execution.
# Run with python3 -m unittest discover -s tests/tooling -p test_counter_packet.py -v.
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class CounterPacketHostTests(unittest.TestCase):
    def test_public_packet_contract(self):
        compiler = shutil.which("g++")
        self.assertIsNotNone(compiler, "g++ is required to test the real packet implementation")
        with tempfile.TemporaryDirectory(prefix="p0-counter-packet-") as temporary:
            build = Path(temporary).resolve()
            self.assertNotIn(ROOT, build.parents, "test builds must stay outside the workspace")
            binary = build / "counter_packet_tests"
            command = [
                compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                "-fno-exceptions", "-fno-rtti",
                "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS",
                "-I", str(ROOT), "-I", str(ROOT / "host" / "third_party"),
                str(ROOT / "tests" / "tooling" / "counter_packet_cases.cc"),
                str(ROOT / "bench" / "p0_matrix" / "src" / "counter_packet.cpp"),
                "-o", str(binary),
            ]
            compiled = subprocess.run(command, capture_output=True, text=True, timeout=90)
            self.assertEqual(compiled.returncode, 0, compiled.stdout + compiled.stderr)
            tested = subprocess.run(
                [str(binary), "--no-colors"], capture_output=True, text=True, timeout=30
            )
            self.assertEqual(tested.returncode, 0, tested.stdout + tested.stderr)
            print(tested.stdout, end="")


if __name__ == "__main__":
    unittest.main()
