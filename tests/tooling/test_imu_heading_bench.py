"""Execute independently frozen D111 oracles against opaque source copies.

No production implementation body supplies expected values. Actual Estimator and
Services bodies are linked unchanged; only the native Acquirer is substituted.
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
RAW = ROOT / "state/analysis/P2_imu_heading_bench_raw/author"
CASES = ROOT / "tests/tooling/imu_heading_bench_cases.cc"
DEFAULTS = {
    "IMU_BENCH_TRIAL_US": 60000000,
    "IMU_BENCH_CHECKPOINT_US": 1000000,
    "IMU_BENCH_CHECKPOINTS": 61,
    "IMU_BENCH_DEADLINE_US": 70000000,
    "IMU_BENCH_MAX_POLLS": 100000000,
}


def receipt(kind, record):
    RAW.mkdir(parents=True, exist_ok=True)
    record["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (RAW / f"{kind}_{time.time_ns()}.json").open("x", encoding="utf-8") as output:
        json.dump(record, output, indent=2)
        output.write("\n")


class ImuHeadingBenchTests(unittest.TestCase):
    def command(self, argv, refuse=False):
        argv = list(map(str, argv))
        try:
            result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=600)
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

    def test_frozen_runner_native_boundaries_and_config(self):
        receipt("test_freeze", {"implementation_body_read": False, "sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (CASES, Path(__file__), ROOT / "state/analysis/P2_imu_heading_bench_contract.md",
                         ROOT / "bench/imu_heading/src/imu_heading_bench.h",
                         ROOT / "bench/imu_heading/src/imu_heading_bench_native.h")}})
        if os.name == "nt":
            self.command(["wsl.exe", "--exec", "python3", "-m", "unittest",
                          "tests.tooling.test_imu_heading_bench.ImuHeadingBenchTests.test_frozen_runner_native_boundaries_and_config", "-v"])
            return
        compiler = shutil.which("g++")
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix="sumo-d111-author-", dir="/dev/shm") as temporary:
            stage = Path(temporary)
            source, bench = stage / "src", stage / "bench"
            shutil.copytree(ROOT / "src", source)
            shutil.copytree(ROOT / "bench/imu_heading", bench)
            shutil.copyfile(CASES, stage / "cases.cc")
            receipt("opaque_source_copy", {"sha256": {
                str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest()
                for folder in (source, bench) for path in sorted(folder.rglob("*")) if path.is_file()}})
            (stage / "Arduino.h").write_text("#pragma once\nunsigned long micros();\n")
            (stage / "main.cc").write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
            shutil.copyfile(bench / "imu_heading.ino", bench / "sketch.cpp")
            common = [compiler, "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                      "-fno-exceptions", "-fno-rtti", "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS",
                      "-DD111_TEST_SEPARATE_MAIN", "-DMOTORS_ALLOWED=0", "-DMATCH=0",
                      "-I", source, "-I", bench / "src", "-I", stage, "-isystem", ROOT / "host/third_party",
                      "-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free"]
            sources = [stage / "cases.cc", bench / "src/imu_heading_bench.cpp",
                       source / "hal/imu_heading.cpp", source / "core/countdown.cpp"]
            sanitizer = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                         "-fno-omit-frame-pointer", "-no-pie"]
            self.runner_profiles(stage, common, sources, bench, sanitizer)
            self.config_profiles(stage, common, sources, source, sanitizer)
            for allowed, match in ((1, 0), (0, 1), (1, 1)):
                with self.subTest(refused_motor=allowed, refused_match=match):
                    flags = [part for part in common if part not in ("-DMOTORS_ALLOWED=0", "-DMATCH=0")]
                    self.command([*flags, f"-DMOTORS_ALLOWED={allowed}", f"-DMATCH={match}",
                                  "-DARDUINO_ARCH_ZEPHYR", "-fsyntax-only", bench / "sketch.cpp"], refuse=True)

    def runner_profiles(self, stage, common, sources, bench, sanitizer):
        for label, flags in (("normal", []), ("asan_ubsan", sanitizer)):
            with self.subTest(profile=label):
                self.execute(common, flags, sources, stage / label)
        for label, flags in (("native_normal", []), ("native_san", sanitizer)):
            with self.subTest(profile=label):
                self.execute(common, [*flags, "-DARDUINO_ARCH_ZEPHYR", "-DTEST_NATIVE_BINDING"],
                             [*sources, bench / "src/imu_heading_bench_native.cpp", bench / "sketch.cpp"],
                             stage / label, "D111 default sketch*,D111 Native*")

    def config_profiles(self, stage, common, sources, source, sanitizer):
        config = source / "config.h"
        original = config.read_text(encoding="utf-8")
        invalid = [("TICK_US", "0U"), ("TICK_US", "2001U"),
                   ("IMU_HEADING_MAX_GAP_US", "0U"), ("IMU_HEADING_MAX_GAP_US", "0x80000000U"),
                   ("IMU_BENCH_CHECKPOINT_US", "0U"), ("IMU_BENCH_CHECKPOINT_US", "1999U"),
                   ("IMU_BENCH_TRIAL_US", "0U"), ("IMU_BENCH_TRIAL_US", "60000001U"),
                   ("IMU_BENCH_CHECKPOINTS", "0U"), ("IMU_BENCH_CHECKPOINTS", "60U"),
                   ("IMU_BENCH_DEADLINE_US", "0U"), ("IMU_BENCH_DEADLINE_US", "0x80000000U"),
                   ("IMU_BENCH_DEADLINE_US", "65500000U"),
                   ("IMU_BENCH_MAX_POLLS", "0U"), ("IMU_BENCH_MAX_POLLS", "0xFFFFFFFFU")]
        for index, (name, value) in enumerate(invalid):
            with self.subTest(invalid_config=name, value=value):
                self.change_config(config, original, {name: value})
                self.execute(common, [*sanitizer, "-DTEST_INVALID_CONFIG"], sources, stage / f"invalid-{index}",
                             "D111 passive*,D111 grants*,D111 invalid configuration*")
        with self.subTest(estimator_config=True):
            self.change_config(config, original, {"IMU_SILENCE_US": "2000U"})
            self.execute(common, [*sanitizer, "-DTEST_ESTIMATOR_CONFIG"], sources, stage / "estimator-config",
                         "D111 passive*,D111 grants*,D111 invalid configuration*")
        special = [
            ("short-cal", {"CAL_START_MS": "1U", "CAL_END_MS": "4U"}, "-DTEST_SHORT_CAL", "D111 short public*"),
            ("poll-limit", {"IMU_BENCH_MAX_POLLS": "5U"}, "-DTEST_LIMIT", "D111 finite poll budget*"),
            ("short-trial", {"IMU_BENCH_TRIAL_US": "4000U", "IMU_BENCH_CHECKPOINT_US": "2000U",
                              "IMU_BENCH_CHECKPOINTS": "3U"}, "-DTEST_SHORT_TRIAL",
             "D111 sixty second*,D111 nondivisible*,D111 failed final*"),
        ]
        for name, changes, define, selection in special:
            for label, flags in (("normal", []), ("san", sanitizer)):
                with self.subTest(special=name, profile=label):
                    self.change_config(config, original, changes)
                    self.execute(common, [*flags, define], sources, stage / f"{name}-{label}", selection)
        for name, changes in (("deadline-min-plus-one", {"IMU_BENCH_DEADLINE_US": "65500001U"}),
                              ("tick-gap-equality", {"TICK_US": "2000U"})):
            with self.subTest(valid_boundary=name):
                self.change_config(config, original, changes)
                self.execute(common, sanitizer, sources, stage / name, "D111 valid admission*")
        config.write_text(original, encoding="utf-8")

    def test_registry_five_literal_additions_unchanged_18_checks_and_wrong_values(self):
        from . import test_runtime_config_registry as registry
        folder = ROOT / "state/analysis/P2_imu_heading_bench_raw/registry"
        before = (folder / "test_p0_config_before.py").read_bytes()
        after = (ROOT / "tests/tooling/test_p0_config.py").read_bytes()
        restored = after
        for name, value in DEFAULTS.items():
            line = f"    '{name}': {value},  # D111 finite heading bench bound.\n".encode()
            self.assertEqual(restored.count(line), 1)
            restored = restored.replace(line, b"", 1)
        self.assertEqual(restored, before)
        receipt("registry_delta", {"literal_defaults": DEFAULTS, "five_additions_other_bytes_identical": True,
                                   "before_sha256": hashlib.sha256(before).hexdigest(),
                                   "after_sha256": hashlib.sha256(after).hexdigest()})
        with mock.patch.object(registry, "RAW", RAW / "registry"):
            case = registry.RuntimeConfigRegistryTests()
            case.run_registry("D111-approved-five-literals")
            for name, value in DEFAULTS.items():
                with tempfile.TemporaryDirectory(prefix="sumo-d111-wrong-registry-") as temporary:
                    project = Path(temporary)
                    (project / "docs").mkdir(); (project / "src").mkdir()
                    shutil.copyfile(ROOT / "docs/BEHAVIOR.md", project / "docs/BEHAVIOR.md")
                    text = (ROOT / "src/config.h").read_text(encoding="utf-8")
                    changed, count = re.subn(r"(\b" + name + r"\s*=\s*)[^;]+;", r"\g<1>" + str(value + 1) + "U;", text)
                    self.assertEqual(count, 1)
                    (project / "src/config.h").write_text(changed, encoding="utf-8")
                    case.run_registry("D111-wrong-" + name, project, expected_failure=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
