"""Build independently authored D091 Runner cases against actual opaque sources.

Keeps bench-header tests out of normal source staging and the recursive CMake glob.
Runs normal and sanitizer binaries, retaining every command outcome as JSONL.
"""
import datetime
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "state/analysis/P2_recorder_bench_raw/author"


class RecorderBenchRunnerTests(unittest.TestCase):
    def run_command(self, command, cwd=ROOT):
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=180)
        RAW.mkdir(parents=True, exist_ok=True)
        record = {"time": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  "command": [str(value) for value in command], "cwd": str(cwd),
                  "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
        with (RAW / "runner_runs.jsonl").open("a", encoding="utf-8") as output:
            output.write(json.dumps(record) + "\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_normal_and_sanitizer_actual_runner(self):
        if os.name == "nt":
            self.run_command(["wsl.exe", "--exec", "python3", "-m", "unittest",
                              "tests.tooling.test_recorder_bench_runner", "-v"])
            return
        sources = sorted((ROOT / "src/core").glob("*.cpp"))
        sources += [ROOT / "src/hal" / name for name in
                    ["motors.cpp", "recorder.cpp", "recorder_frames.cpp"]]
        sources += [ROOT / "bench/recorder_inert/src/recorder_bench.cpp",
                    ROOT / "tests/tooling/recorder_bench_cases.cc"]
        common = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                  "-fno-exceptions", "-fno-rtti", "-DMOTORS_ALLOWED=0", "-DMATCH=0",
                  "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS", "-I", str(ROOT / "src"),
                  "-I", str(ROOT / "host/third_party"),
                  "-I", str(ROOT / "bench/recorder_inert/src")]
        with tempfile.TemporaryDirectory(prefix="sumox26_recorder_bench_") as temporary:
            for name, flags in [("normal", ["-O1"]),
                                ("sanitizer", ["-O1", "-g", "-fsanitize=address,undefined",
                                               "-fno-omit-frame-pointer", "-no-pie"])]:
                with self.subTest(profile=name):
                    executable = Path(temporary) / name
                    self.run_command(common + flags + [str(path) for path in sources] +
                                     ["-o", str(executable)])
                    self.run_command([str(executable)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
