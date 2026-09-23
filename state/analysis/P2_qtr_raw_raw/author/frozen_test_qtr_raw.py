"""Execute independent D109 cases against opaque isolated production copies.

Expectations derive from frozen D109/D085/D089 contracts and public declarations.
Native tests substitute only existing Reader methods, preserving the new binding.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "state/analysis/P2_qtr_raw_raw/author"
CASES = ROOT / "tests/tooling/qtr_raw_cases.cc"


def receipt(kind, record):
    RAW.mkdir(parents=True, exist_ok=True)
    record["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (RAW / f"{kind}_{time.time_ns()}.json").open("x", encoding="utf-8") as output:
        json.dump(record, output, indent=2)
        output.write("\n")


class QtrRawTests(unittest.TestCase):
    def command(self, argv, refuse=False):
        argv = list(map(str, argv))
        try:
            result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=240)
        except (OSError, subprocess.TimeoutExpired) as error:
            receipt("command", {"argv": argv, "exception": repr(error)})
            raise
        receipt("command", {"argv": argv, "returncode": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr})
        if refuse:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("static assertion failed", result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def execute(self, common, flags, sources, binary, selection=None):
        main = binary.parent / ("doctest-san.o" if "-fsanitize=address,undefined" in flags else "doctest-normal.o")
        if not main.exists():
            self.command([*common, *flags, "-c", binary.parent / "main.cc", "-o", main])
        self.command([*common, *flags, *sources, main, "-o", binary])
        args = [binary, "--no-colors", "--order-by=file"]
        if selection:
            args.append("--test-case=" + selection)
        result = self.command(args)
        self.assertIn("Status: SUCCESS!", result.stdout)
        print(binary.name + ": " + " | ".join(line for line in result.stdout.splitlines()
              if "test cases:" in line or "assertions:" in line), flush=True)

    def test_frozen_runner_native_capacity_and_forbidden_flags(self):
        receipt("test_freeze", {"implementation_body_read": False, "sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (CASES, Path(__file__), ROOT / "state/analysis/P2_qtr_raw_contract.md",
                         ROOT / "bench/qtr_raw/src/qtr_raw.h", ROOT / "bench/qtr_raw/src/qtr_raw_native.h")}})
        if os.name == "nt":
            self.command(["wsl.exe", "--exec", "python3", "-m", "unittest",
                          "tests.tooling.test_qtr_raw.QtrRawTests.test_frozen_runner_native_capacity_and_forbidden_flags", "-v"])
            return
        compiler = shutil.which("g++")
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix="sumo-d109-author-", dir="/dev/shm") as temporary:
            stage = Path(temporary)
            source, bench = stage / "src", stage / "bench"
            shutil.copytree(ROOT / "src", source)
            shutil.copytree(ROOT / "bench/qtr_raw", bench)
            shutil.copyfile(CASES, stage / "cases.cc")
            receipt("opaque_source_copy", {"sha256": {
                str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest()
                for folder in (source, bench) for path in sorted(folder.rglob("*")) if path.is_file()}})
            (stage / "Arduino.h").write_text("#pragma once\nunsigned long micros();\n")
            (stage / "main.cc").write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
            shutil.copyfile(bench / "qtr_raw.ino", bench / "sketch.cpp")
            common = [compiler, "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                      "-fno-exceptions", "-fno-rtti", "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS",
                      "-DD109_TEST_SEPARATE_MAIN", "-DMOTORS_ALLOWED=0", "-DMATCH=0",
                      "-I", source, "-I", bench / "src", "-I", stage, "-isystem", ROOT / "host/third_party",
                      "-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free"]
            sources = [stage / "cases.cc", bench / "src/qtr_raw.cpp", source / "hal/line_qtr_adapter.cpp"]
            sanitizer = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                         "-fno-omit-frame-pointer", "-no-pie"]
            self.runner_profiles(stage, common, sources, bench, source, sanitizer)
            for allowed, match in ((1, 0), (0, 1), (1, 1)):
                with self.subTest(refused_motor=allowed, refused_match=match):
                    flags = [part for part in common if part not in ("-DMOTORS_ALLOWED=0", "-DMATCH=0")]
                    self.command([*flags, f"-DMOTORS_ALLOWED={allowed}", f"-DMATCH={match}",
                                  "-DARDUINO_ARCH_ZEPHYR", "-fsyntax-only", bench / "sketch.cpp"], refuse=True)

    def runner_profiles(self, stage, common, sources, bench, source, sanitizer):
        for label, flags in (("normal", []), ("asan_ubsan", sanitizer)):
            with self.subTest(profile=label):
                self.execute(common, flags, sources, stage / label)
        for label, flags in (("native_normal", []), ("native_san", sanitizer)):
            with self.subTest(profile=label):
                self.execute(common, [*flags, "-DARDUINO_ARCH_ZEPHYR", "-DTEST_NATIVE_BINDING"],
                             [*sources, bench / "src/qtr_raw_native.cpp", bench / "sketch.cpp"],
                             stage / label, "D109 default sketch*,D109 Native*")
        config = source / "config.h"
        original = config.read_text(encoding="utf-8")
        for value in (1, 0):
            for label, flags in (("normal", []), ("san", sanitizer)):
                with self.subTest(capacity=value, profile=label):
                    changed, count = re.subn(r"(\bQTR_BENCH_FRAMES\s*=\s*)[^;]+;",
                                            r"\g<1>" + str(value) + "U;", original)
                    self.assertEqual(count, 1)
                    config.write_text(changed, encoding="utf-8")
                    receipt("capacity_profile", {"capacity": value, "profile": label,
                                                  "sha256": hashlib.sha256(config.read_bytes()).hexdigest()})
                    selection = None if value else "D109 fixture*,D109 passive*,D109 every missing*,D109 zero capacity*"
                    self.execute(common, [*flags, "-DTEST_CAPACITY_ONE"], sources,
                                 stage / f"capacity-{value}-{label}", selection)
        config.write_text(original, encoding="utf-8")

    def test_additive_registry_keeps_original_18_assertions_and_rejects_129(self):
        from . import test_runtime_config_registry as registry
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(registry.RuntimeConfigRegistryTests)
        with mock.patch.object(registry, "RAW", RAW / "registry"):
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            self.assertEqual(result.testsRun, 2)
            self.assertTrue(result.wasSuccessful())
            with tempfile.TemporaryDirectory(prefix="sumo-d109-wrong-capacity-") as temporary:
                project = Path(temporary)
                (project / "docs").mkdir()
                (project / "src").mkdir()
                shutil.copyfile(ROOT / "docs/BEHAVIOR.md", project / "docs/BEHAVIOR.md")
                original = (ROOT / "src/config.h").read_text(encoding="utf-8")
                changed, count = re.subn(r"(\bQTR_BENCH_FRAMES\s*=\s*)[^;]+;", r"\g<1>129U;", original)
                self.assertEqual(count, 1)
                (project / "src/config.h").write_text(changed, encoding="utf-8")
                case = registry.RuntimeConfigRegistryTests()
                case.run_registry("D109-wrong-capacity-129", project, expected_failure=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
