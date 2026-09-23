"""Independent local copied-source D101 review; never stages or contacts a board."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
stamp = str(time.time_ns())
record = {"scope": "Copied production sources, independent reviewer factory probe",
          "source_sha256": {}, "results": []}

def run(argv):
    result = subprocess.run(argv, capture_output=True, text=True)
    record["results"].append(dict(argv=argv, returncode=result.returncode,
                                  stdout=result.stdout, stderr=result.stderr))
    (RAW / f"review_{stamp}.json").write_text(json.dumps(record, indent=2) + "\n")
    print(result.stdout, result.stderr, flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)

with tempfile.TemporaryDirectory(prefix="d101-review-", dir="/dev/shm") as temp:
    source = Path(temp) / "src"
    shutil.copytree(ROOT / "src", source)
    record["source_sha256"] = {str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in source.rglob("*") if path.is_file()}
    binary = Path(temp) / "factory"
    run(["g++", "-std=c++17", "-O1", "-Wall", "-Wextra", "-Werror", "-Wpedantic",
         "-fno-exceptions", "-fno-rtti", "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
         "-DARDUINO_ARCH_ZEPHYR", "-I", str(source),
         str(source / "app/dump_port_unoq.cpp"), str(RAW / "factory_probe.cpp"), "-o", str(binary)])
    run([str(binary)])
    if "--runtime" in sys.argv:
        record["scope"] += "; rerun independently authored actual Runtime tests, both motor configurations"
        copied_tests = Path(temp) / "tests"
        copied_tests.mkdir()
        shutil.copytree(ROOT / "tests/fixtures", copied_tests / "fixtures")
        test_names = ["test_app_dump.cpp"]
        if "--prior-runtime" in sys.argv:
            test_names += ["test_app_runtime.cpp", "test_app_projection.cpp"]
        for name in test_names:
            shutil.copy2(ROOT / "tests" / name, copied_tests / name)
        config_path = source / "config.h"
        config = config_path.read_text()
        for name, value in (("BUTTON_WINDOWS_CONFIGURED", "1U"),
                            ("BUTTON_LOW_RAW", "{0U, 900U, 1900U, 2900U}"),
                            ("BUTTON_HIGH_RAW", "{100U, 1100U, 2100U, 3100U}")):
            config, matches = re.subn(r'(\b' + name + r'(?:\[4\])?\s*=\s*)[^;]+;',
                                      r'\g<1>' + value + ';', config)
            assert matches == 1
        config_path.write_text(config)
        record["synthetic_config_only"] = config
        record["synthetic_config_sha256"] = hashlib.sha256(config_path.read_bytes()).hexdigest()
        record["test_sha256"] = {str(p.relative_to(copied_tests)): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in copied_tests.rglob("*") if p.is_file()}
        source_files = sorted((source / "core").glob("*.cpp")) + sorted((source / "app").glob("*.cpp"))
        source_files += [source / "hal" / name for name in (
            "motors.cpp", "recorder.cpp", "recorder_frames.cpp", "recorder_csv.cpp", "recorder_dump.cpp",
            "power_inputs.cpp", "ui.cpp", "imu_heading.cpp", "imu_adapter.cpp", "line_qtr_adapter.cpp",
            "qtr_cal.cpp", "ui_display.cpp")]
        for mode in (0, 1):
            binary = Path(temp) / f"runtime-{mode}"
            run(["g++", "-std=c++17", "-O1", "-Wall", "-Wextra", "-Werror", "-Wpedantic",
                 "-fno-exceptions", "-fno-rtti", "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                 "-DDOCTEST_CONFIG_NO_EXCEPTIONS", "-DAPP_TEST_CONFIGURED_BUTTONS=1",
                 f"-DMOTORS_ALLOWED={mode}", f"-DMATCH={mode}",
                 "-I", str(source), "-I", str(ROOT / "host/third_party"),
                 *map(str, source_files), str(ROOT / "host/motor_gate_main.cpp"),
                 *[str(copied_tests / name) for name in test_names], "-o", str(binary)])
            run([str(binary)])
