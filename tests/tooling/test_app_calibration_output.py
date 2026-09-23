"""Build D105 actual-Runtime tests against opaque production source copies.

Only isolated button windows and one deadline-test configuration are replaced.
The author has D104 context but did not read D105 implementation bodies.
All command results and source hashes are retained; no shared build or board I/O.
"""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "state/analysis/P2_calibration_delivery_raw/author"
CASES = ROOT / "tests/tooling/calibration_output_cases.cc"
HAL = ("motors.cpp", "recorder.cpp", "recorder_frames.cpp", "recorder_csv.cpp",
       "recorder_dump.cpp", "power_inputs.cpp", "ui.cpp", "imu_heading.cpp",
       "imu_adapter.cpp", "line_qtr_adapter.cpp", "qtr_cal.cpp", "qtr_cal_format.cpp", "ui_display.cpp")
APP = ("transaction.cpp", "runtime.cpp", "runtime_inputs.cpp", "runtime_dump.cpp",
       "runtime_service.cpp", "transaction_service.cpp", "runtime_calibration.cpp")


def receipt(kind, content):
    RAW.mkdir(parents=True, exist_ok=True)
    content["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (RAW / f"{kind}_{time.time_ns()}.json").open("x", encoding="utf-8") as stream:
        json.dump(content, stream, indent=2); stream.write("\n")


class AppCalibrationOutputTests(unittest.TestCase):
    def command(self, argv, env=None, timeout=240):
        values = list(map(str, argv))
        try:
            result = subprocess.run(values, cwd=ROOT, text=True, capture_output=True,
                                    timeout=timeout, env=env)
        except (subprocess.TimeoutExpired, OSError) as error:
            receipt("command", {"argv": values, "returncode": None, "error": repr(error),
                                "stdout": str(getattr(error, "stdout", "")),
                                "stderr": str(getattr(error, "stderr", ""))})
            raise
        receipt("command", {"argv": values, "cwd": str(ROOT), "returncode": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def configure(self, source, changes):
        path = source / "config.h"; text = path.read_text()
        for name, value in changes.items():
            text, count = re.subn(r"(\b" + name + r"(?:\[4\])?\s*=\s*)[^;]+;",
                                  r"\g<1>" + value + ";", text)
            self.assertEqual(count, 1, name)
        path.write_text(text)
        receipt("synthetic_config", {"changes": changes, "path": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "scope": "Isolated host fixture only; no physical calibration or production config change"})

    def test_actual_runtime_grants_calibration_transport_and_parser_roundtrip(self):
        test_paths = [CASES, Path(__file__), ROOT / "tests/tooling/test_qtr_config.py"]
        receipt("test_freeze", {"independence": "D105 implementation bodies not inspected; prior D104 author context",
            "sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in test_paths}})
        if os.name == "nt":
            self.command(["wsl.exe", "--exec", "python3", "-m", "unittest",
                          "tests.tooling.test_app_calibration_output", "-v"], timeout=600)
            return
        compiler = shutil.which("g++"); self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix="sumo-d105-author-", dir="/dev/shm") as temporary:
            stage = Path(temporary); source = stage / "src"
            shutil.copytree(ROOT / "src", source); shutil.copyfile(CASES, stage / "cases.cc")
            receipt("opaque_source_copy", {"sha256": {
                str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(source.rglob("*")) if path.is_file()}})
            self.configure(source, {"BUTTON_WINDOWS_CONFIGURED": "1U",
                "BUTTON_LOW_RAW": "{0U, 900U, 1900U, 2900U}",
                "BUTTON_HIGH_RAW": "{100U, 1100U, 2100U, 3100U}"})
            common = [compiler, "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                "-fno-exceptions", "-fno-rtti", "-DAPP_TEST_CONFIGURED_BUTTONS=1",
                "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS",
                "-I", ROOT / "tests", "-isystem", ROOT / "host/third_party"]
            def sources(folder):
                return [*sorted((folder / "core").glob("*.cpp")),
                        *(folder / "hal" / name for name in HAL),
                        *(folder / "app" / name for name in APP), stage / "cases.cc"]
            for match in (0, 1):
                for sanitized in (False, True):
                    label = f"match{match}-" + ("san" if sanitized else "normal")
                    with self.subTest(profile=label):
                        binary = stage / label; output = stage / (label + "-snippet.txt")
                        flags = [f"-DMATCH={match}", f"-DMOTORS_ALLOWED={match}"]
                        if sanitized: flags += ["-g", "-fsanitize=address,undefined",
                            "-fno-sanitize-recover=all", "-fno-omit-frame-pointer", "-no-pie"]
                        self.command([*common, *flags, "-I", source, *sources(source), "-o", binary])
                        env = {**os.environ, "SUMO_QTR_SNIPPET_OUTPUT": str(output)}
                        result = self.command([binary, "--no-colors"], env=env)
                        print(label + ": " + " | ".join(line for line in result.stdout.splitlines()
                            if "test cases:" in line or "assertions:" in line), flush=True)
                        if match == 0:
                            spec = importlib.util.spec_from_file_location("d105_roundtrip_parser", ROOT / "tools/qtr_config.py")
                            parser = importlib.util.module_from_spec(spec); spec.loader.exec_module(parser)
                            data = output.read_bytes()
                            expected = {"white_us": [350] * 4, "timeout_us": 1500,
                                        "provenance": "UNATTRIBUTED_BARE_LINE"}
                            self.assertEqual(parser.decode_snippet(data, 1500), expected)
                            receipt("actual_roundtrip", {"profile": label, "bytes_hex": data.hex(),
                                "sha256": hashlib.sha256(data).hexdigest(), "result": expected})
            short = stage / "short-src"; shutil.copytree(source, short)
            self.configure(short, {"DUMP_STALL_MS": "20U", "DUMP_TOTAL_MS": "40U"})
            binary = stage / "short-deadline"
            self.command([*common, "-DMATCH=0", "-DMOTORS_ALLOWED=0", "-DCO_SHORT_TOTAL=1",
                          "-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-no-pie",
                          "-I", short, *sources(short), "-o", binary])
            self.command([binary, "--no-colors", "--test-case=*total deadline*"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
