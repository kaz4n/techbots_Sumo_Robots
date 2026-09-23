"""Capture Acquirer worker checks without board access or shared build mutation."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parents[4]
receipt = Path(__file__).resolve().parent
sources = [root / "src/hal" / name for name in (
    "imu_acquisition.h", "imu_acquisition.cpp", "imu_acquisition_async.cpp")]
commands = {
    "syntax": ["wsl", "--exec", "g++", "-std=c++17", "-Wall", "-Wextra",
        "-Wpedantic", "-Werror", "-fno-exceptions", "-fno-rtti", "-fsyntax-only",
        "src/hal/imu_acquisition.cpp", "src/hal/imu_acquisition_async.cpp"],
    "legacy": ["wsl", "--exec", "env",
        "SUMO_IMU_ACQUISITION_RECEIPT_DIR=state/analysis/P2_imu_resume_raw/acquirer_worker/legacy",
        "python3", "-m", "unittest",
        "tests.tooling.test_imu_acquisition.ImuAcquisitionTests.test_b3_d081_actual_acquirer_and_setup_contract",
        "tests.tooling.test_imu_acquisition.ImuAcquisitionTests.test_b3_d081_actual_probe_startup_and_10000_loops_are_inert_in_both_modes",
        "tests.tooling.test_imu_acquisition.ImuAcquisitionTests.test_b14_d081_invalid_silence_bounds_fail_before_acquisition",
        "tests.tooling.test_imu_acquisition.ImuAcquisitionTests.test_b14_d081_smallest_and_largest_forward_silence_bounds", "-v"],
}
for name, argv in commands.items():
    hashes = {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sources}
    result = subprocess.run(argv, cwd=root, text=True, capture_output=True, timeout=120)
    record = dict(argv=argv, cwd=str(root), returncode=result.returncode,
                  stdout=result.stdout, stderr=result.stderr, source_sha256=hashes,
                  capture="subprocess text=True, newline-normalized")
    (receipt / f"{name}_{time.time_ns()}.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"{name}: exit {result.returncode}")
    print(result.stdout + result.stderr, end="")
    if result.returncode:
        raise SystemExit(result.returncode)
