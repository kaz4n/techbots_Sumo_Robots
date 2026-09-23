"""Run independent D112 contract-derived cases against opaque isolated sources.

Existing D110 fixtures are adapted to raw A1 sequence and actual decoder evidence.
No production body is read; historical registry deltas use their frozen after-image.
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
RAW = ROOT / "state/analysis/P2_ui_bench_raw/author"
CASES = ROOT / "tests/tooling/ui_bench_cases.cc"


def receipt(kind, record):
    RAW.mkdir(parents=True, exist_ok=True)
    record["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (RAW / f"{kind}_{time.time_ns()}.json").open("x", encoding="utf-8") as output:
        json.dump(record, output, indent=2)
        output.write("\n")


class UiBenchTests(unittest.TestCase):
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
            text, count = re.subn(r"(\b" + name + r"(?:\[4\])?\s*=\s*)[^;]+;", r"\g<1>" + value + ";", text)
            self.assertEqual(count, 1)
        config.write_text(text, encoding="utf-8")
        receipt("config_profile", {"changes": changes, "sha256": hashlib.sha256(config.read_bytes()).hexdigest()})

    def test_frozen_runner_native_capacity_config_and_saturation(self):
        receipt("test_freeze", {"implementation_body_read": False, "sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (CASES, Path(__file__), ROOT / "state/analysis/P2_ui_bench_contract.md",
                         ROOT / "bench/ui/src/ui_bench.h", ROOT / "bench/ui/src/ui_bench_native.h")}})
        if os.name == "nt":
            self.command(["wsl.exe", "--exec", "python3", "-m", "unittest",
                          "tests.tooling.test_ui_bench.UiBenchTests.test_frozen_runner_native_capacity_config_and_saturation", "-v"])
            return
        compiler = shutil.which("g++")
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix="sumo-d112-author-", dir="/dev/shm") as temporary:
            stage = Path(temporary)
            source, bench = stage / "src", stage / "bench"
            shutil.copytree(ROOT / "src", source)
            shutil.copytree(ROOT / "bench/ui", bench)
            shutil.copyfile(CASES, stage / "cases.cc")
            receipt("opaque_source_copy", {"sha256": {
                str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest()
                for folder in (source, bench) for path in sorted(folder.rglob("*")) if path.is_file()}})
            (stage / "Arduino.h").write_text("#pragma once\nunsigned long micros();\n")
            (stage / "main.cc").write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
            shutil.copyfile(bench / "ui.ino", bench / "sketch.cpp")
            common = [compiler, "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                      "-fno-exceptions", "-fno-rtti", "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS",
                      "-DD112_TEST_SEPARATE_MAIN", "-DMOTORS_ALLOWED=0", "-DMATCH=0",
                      "-I", source, "-I", bench / "src", "-I", stage, "-isystem", ROOT / "host/third_party",
                      "-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free"]
            sources = [stage / "cases.cc", bench / "src/ui_bench.cpp", source / "hal/ui.cpp"]
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
                             [*sources, bench / "src/ui_bench_native.cpp", bench / "sketch.cpp"],
                             stage / label, "D112 Native startup*,D112 Native forwards*")
        config = source / "config.h"
        original = config.read_text(encoding="utf-8")
        for value in (1, 0):
            for label, flags in (("normal", []), ("san", sanitizer)):
                with self.subTest(capacity=value, profile=label):
                    self.change_config(config, original, {"UI_BENCH_SAMPLES": str(value) + "U"})
                    selection = None if value else "D112 passive*,D112 missing*,D112 invalid config*"
                    extra = ["-DTEST_CAPACITY_ONE"] + (["-DTEST_INVALID_CONFIG"] if value == 0 else [])
                    self.execute(common, [*flags, *extra], sources, stage / f"capacity-{value}-{label}", selection)
        config.write_text(original, encoding="utf-8")

    def config_profiles(self, stage, common, sources, source, sanitizer):
        config = source / "config.h"
        original = config.read_text(encoding="utf-8")
        invalid = [("TICK_US", "0U"), ("TICK_US", "0x80000000U"),
                   ("VBAT_ADC_CONVERSION_US", "0U"), ("VBAT_ADC_CONVERSION_US", "1001U")]
        for index, (name, value) in enumerate(invalid):
            with self.subTest(invalid_config=name, value=value):
                self.change_config(config, original, {name: value})
                self.execute(common, [*sanitizer, "-DTEST_INVALID_CONFIG"], sources,
                             stage / f"invalid-{index}", "D112 passive*,D112 missing*,D112 invalid config*")
        for index, changes in enumerate(({"VBAT_ADC_REFERENCE_V": "2.4F"}, {"VBAT_DIVIDER_RATIO": "0.9F"})):
            with self.subTest(native_config=changes):
                self.change_config(config, original, changes)
                self.execute(common, [*sanitizer, "-DTEST_NATIVE_CONFIG"], sources,
                             stage / f"native-config-{index}", "D112 native configuration validation*")
        configured = {"BUTTON_WINDOWS_CONFIGURED": "1U", "BUTTON_LOW_RAW": "{100U, 200U, 300U, 400U}",
                      "BUTTON_HIGH_RAW": "{110U, 210U, 310U, 410U}"}
        overlap = {**configured, "BUTTON_LOW_RAW": "{100U, 105U, 300U, 400U}",
                   "BUTTON_HIGH_RAW": "{110U, 115U, 310U, 410U}"}
        for name, changes, define in (("windows", configured, "-DTEST_DECODER_CONFIGURED"),
                                      ("overlap", overlap, "-DTEST_DECODER_OVERLAP")):
            for label, flags in (("normal", []), ("san", sanitizer)):
                with self.subTest(decoder=name, profile=label):
                    self.change_config(config, original, changes)
                    self.execute(common, [*flags, define], sources, stage / f"{name}-{label}", "D112 decoder synthetic*")
        malformed = [{"BUTTON_WINDOWS_CONFIGURED": "2U"}, {"BUTTON_LOW_RAW": "{111U, 200U, 300U, 400U}"},
                     {"BUTTON_HIGH_RAW": "{16384U, 210U, 310U, 410U}"}, {"BUTTON_SAMPLE_MAX_AGE_US": "0U"},
                     {"BUTTON_SAMPLE_MAX_AGE_US": "99U"}, {"BUTTON_SAMPLE_MAX_AGE_US": "0x80000000U"}]
        for index, changes in enumerate(malformed):
            with self.subTest(decoder_invalid=changes):
                self.change_config(config, original, {**configured, **changes})
                self.execute(common, [*sanitizer, "-DTEST_DECODER_INVALID"], sources,
                             stage / f"decoder-invalid-{index}", "D112 decoder malformed*")
        special = [("saturation", {"TICK_US": "1U", "VBAT_ADC_CONVERSION_US": "1U"},
                    "-DTEST_SATURATION", "D112 five public*"),
                   ("long_period", {"TICK_US": "0x7fffffffU"},
                    "-DTEST_LONG_PERIOD", "D112 accumulated source*")]
        for name, changes, define, selection in special:
            for label, flags in (("normal", []), ("san", sanitizer)):
                with self.subTest(special=name, profile=label):
                    self.change_config(config, original, changes)
                    self.execute(common, [*flags, define], sources, stage / f"{name}-{label}", selection)
        for name, changes in (("conversion-period-equality", {"VBAT_ADC_CONVERSION_US": "1000U"}),
                              ("decoder-age-minimum", {"BUTTON_SAMPLE_MAX_AGE_US": "100U"})):
            with self.subTest(valid_boundary=name):
                self.change_config(config, original, changes)
                self.execute(common, sanitizer, sources, stage / name, "D112 valid config smoke*")
        config.write_text(original, encoding="utf-8")

    def test_registry_single_addition_original_18_checks_and_wrong_129(self):
        from . import test_runtime_config_registry as registry
        original = (ROOT / "state/analysis/P2_ui_bench_raw/registry/test_p0_config_before.py").read_bytes()
        current = (ROOT / "state/analysis/P2_ui_bench_raw/registry/test_p0_config_after.py").read_bytes()
        added = b"    'UI_BENCH_SAMPLES': 128,  # D112 finite A1 raw/decoder evidence count.\n"
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
            with tempfile.TemporaryDirectory(prefix="sumo-d112-wrong-capacity-") as temporary:
                project = Path(temporary)
                (project / "docs").mkdir()
                (project / "src").mkdir()
                shutil.copyfile(ROOT / "docs/BEHAVIOR.md", project / "docs/BEHAVIOR.md")
                text = (ROOT / "src/config.h").read_text(encoding="utf-8")
                changed, count = re.subn(r"(\bUI_BENCH_SAMPLES\s*=\s*)[^;]+;", r"\g<1>129U;", text)
                self.assertEqual(count, 1)
                (project / "src/config.h").write_text(changed, encoding="utf-8")
                case = registry.RuntimeConfigRegistryTests()
                case.run_registry("D112-wrong-capacity-129", project, expected_failure=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
