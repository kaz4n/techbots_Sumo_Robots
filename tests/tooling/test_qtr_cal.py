"""Compile D089 contract variants without inspecting implementation bodies.

Actual source bytes are staged opaquely; only public config values are replaced.
One aggregate JSONL receipt preserves commands, statuses and full process output.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "state/analysis/P2_qtr_cal_raw/author"
TESTS = ["test_qtr_cal.cpp", "test_qtr_cal_handover.cpp",
         "test_qtr_cal_motor_gate.cpp", "test_qtr_cal_display.cpp"]
HAL = ["line_qtr_adapter.cpp", "qtr_cal.cpp", "qtr_cal_format.cpp",
       "motors.cpp", "ui_display.cpp"]


class QtrCalibrationTests(unittest.TestCase):
    def test_additive_d088_d089_config_registry(self):
        script = """
from decimal import Decimal
from unittest.mock import patch
import unittest
from tests.tooling import test_p0_config as legacy
integers = {'UI_FRAME_PERIOD_US': 40000, 'UI_FAULT_PAGE_MS': 500,
            'UI_BENCH_SCENE_MS': 2000, 'QTR_CAL_SAMPLES': 16,
            'QTR_CAL_CAPTURE_MS': 1000}
floats = {'UI_BATTERY_EMPTY_V': Decimal('9.5'), 'UI_BATTERY_FULL_V': Decimal('12.6')}
with patch.dict(legacy.BEHAVIOR_EXTRA_DEFAULTS, integers), patch.dict(legacy.BEHAVIOR_EXTRA_FLOAT_DEFAULTS, floats):
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(legacy.P0ConfigTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
"""
        self.run_command([sys.executable, "-c", script], ROOT)

    def run_command(self, command, cwd):
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=180)
        RAW.mkdir(parents=True, exist_ok=True)
        record = {"time": time.time(), "command": [str(v) for v in command],
                  "cwd": str(cwd), "returncode": result.returncode,
                  "stdout": result.stdout, "stderr": result.stderr}
        with (RAW / "tooling_runs.jsonl").open("a", encoding="utf-8") as output:
            output.write(json.dumps(record) + "\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def stage(self, target, values):
        shutil.copytree(ROOT / "src", target / "src")
        shutil.copytree(ROOT / "tests/fixtures", target / "tests/fixtures")
        for name in TESTS:
            shutil.copy2(ROOT / "tests" / name, target / "tests" / name)
        path = target / "src/config.h"
        config = path.read_text()
        for name, value in values.items():
            config, count = re.subn(r"(" + name + r"\s*=\s*)\d+U", rf"\g<1>{value}U", config)
            self.assertEqual(count, 1, name)
        path.write_text(config)

    def sources(self, stage):
        return sorted((stage / "src/core").glob("*.cpp")) + [stage / "src/hal" / name for name in HAL]

    def compiler(self, stage, enabled=1):
        return ["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                "-fno-exceptions", "-fno-rtti", "-DDOCTEST_CONFIG_NO_EXCEPTIONS",
                f"-DMOTORS_ALLOWED={enabled}", "-I", str(stage / "src"),
                "-I", str(ROOT / "host/third_party")]

    def test_nondefault_confirmation_and_batch_profiles(self):
        for confirmation, count in [(2, 1), (3, 32)]:
            with self.subTest(confirmation=confirmation, count=count), tempfile.TemporaryDirectory() as temporary:
                stage = Path(temporary)
                self.stage(stage, {"QTR_CONFIRM_TICKS": confirmation, "QTR_CAL_SAMPLES": count})
                command = self.compiler(stage) + [str(p) for p in self.sources(stage)]
                command += [str(stage / "tests" / name) for name in TESTS]
                command += [str(stage / "tests/fixtures/qtr_cal_main.cc"), "-o", str(stage / "cases")]
                self.run_command(command, stage)
                self.run_command([str(stage / "cases")], stage)

    def test_maximum_supported_batch(self):
        with tempfile.TemporaryDirectory() as temporary:
            stage = Path(temporary)
            self.stage(stage, {"QTR_CAL_SAMPLES": 256})
            command = self.compiler(stage) + [str(stage / "src/hal" / name) for name in HAL[:3]]
            command += [str(stage / "tests/test_qtr_cal.cpp"),
                        str(stage / "tests/fixtures/qtr_cal_main.cc"), "-o", str(stage / "cases")]
            self.run_command(command, stage)
            self.run_command([str(stage / "cases")], stage)

    def test_actual_probe_setup_and_ten_thousand_loops(self):
        with tempfile.TemporaryDirectory() as temporary:
            stage = Path(temporary)
            self.stage(stage, {})
            shutil.copytree(ROOT / "bench/p2_qtr_cal_compile", stage / "probe")
            shutil.copytree(stage / "src", stage / "probe/src", dirs_exist_ok=True)
            for enabled in (0, 1):
                command = self.compiler(stage, enabled) + [f"-DMATCH={enabled}", "-I", str(stage / "probe/src")]
                command += [str(p) for p in self.sources(stage)]
                command += [str(p) for p in (stage / "probe/src").glob("*.cpp")]
                command += [str(stage / "tests/fixtures/qtr_cal_startup.cc"), "-x", "c++",
                            str(stage / "probe/p2_qtr_cal_compile.ino"), "-o", str(stage / "startup")]
                self.run_command(command, stage)
                self.run_command([str(stage / "startup")], stage)
