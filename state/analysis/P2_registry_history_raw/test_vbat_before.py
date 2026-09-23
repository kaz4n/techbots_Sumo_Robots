"""Run independently frozen D110 tests against isolated opaque source copies.

The public contract defines the oracle; native owner substitutes execute the
actual new binding and sketch without touching the existing ADC implementation.
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
RAW = ROOT / "state/analysis/P2_vbat_raw/author"
CASES = ROOT / "tests/tooling/vbat_cases.cc"


def receipt(kind, record):
    RAW.mkdir(parents=True, exist_ok=True)
    record["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (RAW / f"{kind}_{time.time_ns()}.json").open("x", encoding="utf-8") as output:
        json.dump(record, output, indent=2)
        output.write("\n")


class VbatTests(unittest.TestCase):
    def command(self, argv, refuse=False):
        argv = list(map(str, argv))
        try:
            result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=300)
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

    def change_config(self, config, original, changes):
        text = original
        for name, value in changes.items():
            text, count = re.subn(r"(\b" + name + r"\s*=\s*)[^;]+;", r"\g<1>" + value + ";", text)
            self.assertEqual(count, 1)
        config.write_text(text, encoding="utf-8")
        receipt("config_profile", {"changes": changes, "sha256": hashlib.sha256(config.read_bytes()).hexdigest()})

    def test_frozen_runner_native_capacity_config_and_saturation(self):
        receipt("test_freeze", {"implementation_body_read": False, "sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (CASES, Path(__file__), ROOT / "state/analysis/P2_vbat_contract.md",
                         ROOT / "bench/vbat/src/vbat.h", ROOT / "bench/vbat/src/vbat_native.h")}})
        if os.name == "nt":
            self.command(["wsl.exe", "--exec", "python3", "-m", "unittest",
                          "tests.tooling.test_vbat.VbatTests.test_frozen_runner_native_capacity_config_and_saturation", "-v"])
            return
        compiler = shutil.which("g++")
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix="sumo-d110-author-", dir="/dev/shm") as temporary:
            stage = Path(temporary)
            source, bench = stage / "src", stage / "bench"
            shutil.copytree(ROOT / "src", source)
            shutil.copytree(ROOT / "bench/vbat", bench)
            shutil.copyfile(CASES, stage / "cases.cc")
            receipt("opaque_source_copy", {"sha256": {
                str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest()
                for folder in (source, bench) for path in sorted(folder.rglob("*")) if path.is_file()}})
            (stage / "Arduino.h").write_text("#pragma once\nunsigned long micros();\n")
            (stage / "main.cc").write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
            shutil.copyfile(bench / "vbat.ino", bench / "sketch.cpp")
            common = [compiler, "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                      "-fno-exceptions", "-fno-rtti", "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS",
                      "-DD110_TEST_SEPARATE_MAIN", "-DMOTORS_ALLOWED=0", "-DMATCH=0",
                      "-I", source, "-I", bench / "src", "-I", stage, "-isystem", ROOT / "host/third_party",
                      "-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free"]
            sources = [stage / "cases.cc", bench / "src/vbat.cpp"]
            sanitizer = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                         "-fno-omit-frame-pointer", "-no-pie"]
            self.runner_profiles(stage, common, sources, bench, source, sanitizer)
            self.config_profiles(stage, common, sources, source, sanitizer)
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
                             [*sources, bench / "src/vbat_native.cpp", bench / "sketch.cpp"],
                             stage / label, "D110 default sketch*,D110 Native*")
        config = source / "config.h"
        original = config.read_text(encoding="utf-8")
        for value in (1, 0):
            for label, flags in (("normal", []), ("san", sanitizer)):
                with self.subTest(capacity=value, profile=label):
                    self.change_config(config, original, {"VBAT_BENCH_SAMPLES": str(value) + "U"})
                    selection = None if value else "D110 passive*,D110 missing*,D110 invalid config*"
                    extra = ["-DTEST_CAPACITY_ONE"] + (["-DTEST_INVALID_CONFIG"] if value == 0 else [])
                    self.execute(common, [*flags, *extra], sources, stage / f"capacity-{value}-{label}", selection)
        config.write_text(original, encoding="utf-8")

    def config_profiles(self, stage, common, sources, source, sanitizer):
        config = source / "config.h"
        original = config.read_text(encoding="utf-8")
        invalid = [("VBAT_SAMPLE_PERIOD_US", "0U"), ("VBAT_SAMPLE_PERIOD_US", "0x80000000U"),
                   ("VBAT_ADC_CONVERSION_US", "0U"), ("VBAT_ADC_CONVERSION_US", "10001U"),
                   ("VBAT_ADC_REFERENCE_V", "2.4F"), ("VBAT_ADC_REFERENCE_V", "0x1.cccccep+1F"),
                   ("VBAT_ADC_REFERENCE_V", '__builtin_nanf("")'),
                   ("VBAT_ADC_REFERENCE_V", "__builtin_inff()"),
                   ("VBAT_DIVIDER_RATIO", "0x1.fffffep-1F"),
                   ("VBAT_DIVIDER_RATIO", '__builtin_nanf("")'),
                   ("VBAT_DIVIDER_RATIO", "__builtin_inff()")]
        for index, (name, value) in enumerate(invalid):
            with self.subTest(invalid_config=name, value=value):
                self.change_config(config, original, {name: value})
                self.execute(common, [*sanitizer, "-DTEST_INVALID_CONFIG"], sources,
                             stage / f"invalid-{index}", "D110 passive*,D110 missing*,D110 invalid config*")
        valid = [{"VBAT_ADC_REFERENCE_V": "0x1.333336p+1F"}, {"VBAT_ADC_REFERENCE_V": "3.6F"},
                 {"VBAT_DIVIDER_RATIO": "1.0F"}, {"VBAT_ADC_CONVERSION_US": "10000U"},
                 {"VBAT_SAMPLE_MAX_AGE_US": "0U"}]
        for index, changes in enumerate(valid):
            with self.subTest(valid_config=changes):
                self.change_config(config, original, changes)
                self.execute(common, sanitizer, sources, stage / f"valid-{index}", "D110 valid config smoke*")
        special = [("saturation", {"VBAT_SAMPLE_PERIOD_US": "1U", "VBAT_ADC_CONVERSION_US": "1U"},
                    "-DTEST_SATURATION", "D110 five public*"),
                   ("long_period", {"VBAT_SAMPLE_PERIOD_US": "0x7fffffffU"},
                    "-DTEST_LONG_PERIOD", "D110 accumulated source*")]
        for name, changes, define, selection in special:
            for label, flags in (("normal", []), ("san", sanitizer)):
                with self.subTest(special=name, profile=label):
                    self.change_config(config, original, changes)
                    self.execute(common, [*flags, define], sources, stage / f"{name}-{label}", selection)
        config.write_text(original, encoding="utf-8")

    def test_registry_single_addition_original_18_checks_and_wrong_129(self):
        from . import test_runtime_config_registry as registry
        original = (RAW / "test_p0_config_before.py").read_bytes()
        current = (ROOT / "tests/tooling/test_p0_config.py").read_bytes()
        added = b"    'VBAT_BENCH_SAMPLES': 128,  # D110 finite battery bench capture, approved count.\n"
        self.assertEqual(current.count(added), 1)
        self.assertEqual(current.replace(added, b"", 1), original)
        receipt("registry_amendment_check", {"before_sha256": hashlib.sha256(original).hexdigest(),
                                             "after_sha256": hashlib.sha256(current).hexdigest(),
                                             "one_literal_addition_all_other_bytes_identical": True})
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(registry.RuntimeConfigRegistryTests)
        with mock.patch.object(registry, "RAW", RAW / "registry"):
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            self.assertEqual(result.testsRun, 2)
            self.assertTrue(result.wasSuccessful())
            with tempfile.TemporaryDirectory(prefix="sumo-d110-wrong-capacity-") as temporary:
                project = Path(temporary)
                (project / "docs").mkdir()
                (project / "src").mkdir()
                shutil.copyfile(ROOT / "docs/BEHAVIOR.md", project / "docs/BEHAVIOR.md")
                text = (ROOT / "src/config.h").read_text(encoding="utf-8")
                changed, count = re.subn(r"(\bVBAT_BENCH_SAMPLES\s*=\s*)[^;]+;", r"\g<1>129U;", text)
                self.assertEqual(count, 1)
                (project / "src/config.h").write_text(changed, encoding="utf-8")
                case = registry.RuntimeConfigRegistryTests()
                case.run_registry("D110-wrong-capacity-129", project, expected_failure=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
