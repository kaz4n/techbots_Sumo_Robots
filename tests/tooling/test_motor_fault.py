#!/usr/bin/env python3
"""D162 independent public-contract test driver for the inert MotorGate probe.
Builds serially in RAM and preserves no executable or bytecode in the checkout.
Run: python3 -B tests/tooling/test_motor_fault.py [--sanitize-only].
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SANITIZE_ONLY = "--sanitize-only" in sys.argv
if SANITIZE_ONLY:
    sys.argv.remove("--sanitize-only")


def checked_run(command, **kwargs):
    result = subprocess.run(command, text=True, capture_output=True, **kwargs)
    if result.returncode:
        raise AssertionError(
            f"exit={result.returncode}: {' '.join(map(str, command))}\n"
            f"{result.stdout}{result.stderr}"
        )
    return result


class MotorFaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform != "linux" or not hasattr(os, "memfd_create"):
            raise unittest.SkipTest("Linux RAM scratch and memfd execution required")
        cls.compiler = shutil.which("g++")
        if cls.compiler is None:
            raise unittest.SkipTest("g++ required")
        if shutil.disk_usage("/dev/shm").free < 64 * 1024 * 1024:
            raise RuntimeError("at least 64 MiB of RAM scratch required")
        cls.scratch = tempfile.TemporaryDirectory(prefix="sumox-motor-fault-", dir="/dev/shm")
        cls.directory = Path(cls.scratch.name)
        cls.flags = [cls.compiler, "-std=c++17", "-O1", "-g", "-Wall", "-Wextra",
                     "-Werror", "-fno-exceptions", "-fno-rtti",
                     "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS", "-DMATCH=0",
                     "-DMOTORS_ALLOWED=0", "-ffunction-sections", "-fdata-sections",
                     "-I" + str(ROOT / "src"),
                     "-I" + str(ROOT / "host/third_party"),
                     "-I" + str(ROOT / "bench/motor_fault/src")]

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def build_and_run(self, sanitizer):
        binary = self.directory / ("sanitized" if sanitizer else "normal")
        sources = [ROOT / "tests/tooling/motor_fault_cases.cc",
                   ROOT / "bench/motor_fault/src/motor_fault.cpp",
                   ROOT / "src/hal/motors.cpp", *sorted((ROOT / "src/core").glob("*.cpp"))]
        options = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-no-pie"] if sanitizer else []
        checked_run([*self.flags, *options, *map(str, sources), "-Wl,--gc-sections", "-o", str(binary)])
        descriptor = os.memfd_create("sumox-motor-fault", flags=0)
        try:
            with os.fdopen(os.dup(descriptor), "wb") as target:
                target.write(binary.read_bytes())
            env = dict(os.environ, ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",
                       UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1")
            result = checked_run([f"/proc/self/fd/{descriptor}"], pass_fds=(descriptor,), env=env)
            print(("SANITIZED " if sanitizer else "NORMAL ") + result.stdout.strip())
        finally:
            os.close(descriptor)
            binary.unlink(missing_ok=True)

    @unittest.skipIf(SANITIZE_ONLY, "sanitizer-only invocation")
    def test_01_normal_contract(self):
        self.build_and_run(False)

    def test_02_sanitized_contract(self):
        self.build_and_run(True)

    @unittest.skipIf(SANITIZE_ONLY, "sanitizer-only invocation")
    def test_03_motor_capable_flags_refused(self):
        for match, motors in ((0, 1), (1, 0), (1, 1)):
            with self.subTest(match=match, motors=motors):
                flags = [x for x in self.flags if not x.startswith(("-DMATCH=", "-DMOTORS_ALLOWED="))]
                result = subprocess.run(
                    [*flags, f"-DMATCH={match}", f"-DMOTORS_ALLOWED={motors}",
                     "-x", "c++", "-fsyntax-only", "-"],
                    input='#include "motor_fault.h"\n', text=True, capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Motor fault diagnostic requires inert flags", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
