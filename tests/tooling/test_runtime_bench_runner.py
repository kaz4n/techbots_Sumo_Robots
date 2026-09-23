"""Build independent D104 contract tests with opaque copied production sources.

No implementation text is examined or altered; all default config values remain.
Freeze test hashes before builds and append exact command outcomes, even failures.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "state/analysis/P2_runtime_inert_raw/author"
CASES = ROOT / "tests/tooling/runtime_bench_cases.cc"
HAL = ("motors.cpp", "recorder.cpp", "recorder_frames.cpp", "recorder_csv.cpp",
       "recorder_dump.cpp", "power_inputs.cpp", "ui.cpp", "imu_heading.cpp",
       "imu_adapter.cpp", "line_qtr_adapter.cpp", "qtr_cal.cpp", "ui_display.cpp")
APP = ("transaction.cpp", "runtime.cpp", "runtime_inputs.cpp", "runtime_dump.cpp",
       "runtime_service.cpp", "transaction_service.cpp")


def receipt(kind, record):
    RAW.mkdir(parents=True, exist_ok=True)
    record["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (RAW / f"{kind}_{time.time_ns()}.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")


class RuntimeBenchRunnerTests(unittest.TestCase):
    def command(self, argv, expected=0):
        values = list(map(str, argv))
        try:
            result = subprocess.run(values, cwd=ROOT, text=True, capture_output=True, timeout=240)
        except subprocess.TimeoutExpired as error:
            receipt("command", {"argv": values, "cwd": str(ROOT), "returncode": 124,
                               "stdout": str(error.stdout), "stderr": str(error.stderr)})
            raise
        except OSError as error:
            receipt("command", {"argv": values, "cwd": str(ROOT), "returncode": None,
                               "stdout": "", "stderr": repr(error), "status": "launch_failed"})
            raise
        receipt("command", {"argv": values, "cwd": str(ROOT), "returncode": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr,
                            "text_capture": "subprocess text=True newline normalization"})
        if expected == "refuse":
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("static assertion failed", result.stderr)
        else:
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_actual_runtime_contract_normal_sanitizer_and_compile_refusals(self):
        receipt("test_freeze", {"purpose": "Freeze independently authored tests before implementation build/run",
                               "sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                          for path in (CASES, Path(__file__), ROOT / "state/analysis/P2_runtime_inert_contract.md")}})
        if os.name == "nt":
            self.command(["wsl.exe", "--exec", "python3", "-m", "unittest",
                          "tests.tooling.test_runtime_bench_runner", "-v"])
            return
        compiler = shutil.which("g++")
        self.assertIsNotNone(compiler, "Linux/WSL g++ is required")
        with tempfile.TemporaryDirectory(prefix="sumo-d104-author-", dir="/dev/shm") as temporary:
            stage = Path(temporary)
            source = stage / "src"
            bench = stage / "bench"
            shutil.copytree(ROOT / "src", source)
            shutil.copytree(ROOT / "bench/runtime_inert/src", bench)
            shutil.copyfile(CASES, stage / "cases.cc")
            receipt("opaque_source_copy", {"sha256": {
                str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest()
                for folder in (source, bench) for path in sorted(folder.rglob("*")) if path.is_file()}})
            common = [compiler, "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                      "-fno-exceptions", "-fno-rtti", "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS",
                      "-I", source, "-I", bench, "-isystem", ROOT / "host/third_party"]
            sources = sorted((source / "core").glob("*.cpp"))
            sources += [source / "hal" / name for name in HAL]
            sources += [source / "app" / name for name in APP]
            sources += [bench / "runtime_bench.cpp", stage / "cases.cc"]
            flags = ["-DMOTORS_ALLOWED=0", "-DMATCH=0",
                     "-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free"]
            for label, profile in (("normal", ["-O1"]), ("asan_ubsan", ["-O1", "-g",
                    "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                    "-fno-omit-frame-pointer", "-no-pie"])):
                with self.subTest(profile=label):
                    binary = stage / label
                    self.command([*common, *flags, *profile, *sources, "-o", binary])
                    result = self.command([binary, "--no-colors"])
                    self.assertIn("Status: SUCCESS!", result.stdout)
                    print(label + ": " + " | ".join(line for line in result.stdout.splitlines()
                          if "test cases:" in line or "assertions:" in line), flush=True)
            for allowed, match in ((1, 0), (0, 1), (1, 1)):
                with self.subTest(refused_motor=allowed, refused_match=match):
                    self.command([*common, f"-DMOTORS_ALLOWED={allowed}", f"-DMATCH={match}",
                                  "-fsyntax-only", bench / "runtime_bench.cpp"], expected="refuse")


if __name__ == "__main__":
    unittest.main(verbosity=2)
