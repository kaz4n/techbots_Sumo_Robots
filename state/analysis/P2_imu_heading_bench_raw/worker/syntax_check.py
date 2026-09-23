from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

root = Path.cwd()
raw = root / "state/analysis/P2_imu_heading_bench_raw/worker"
profiles = [{}, {"IMU_BENCH_CHECKPOINTS": 0}, {"IMU_BENCH_CHECKPOINTS": 1},
            {"IMU_BENCH_CHECKPOINT_US": 0}, {"TICK_US": 0},
            {"IMU_BENCH_DEADLINE_US": 0x80000000}, {"IMU_BENCH_MAX_POLLS": 0}]
results = []
for profile in profiles:
    with tempfile.TemporaryDirectory(prefix="imu-heading-syntax-") as tmp:
        stage = Path(tmp)
        src = stage / "src"
        shutil.copytree(root / "src", src)
        for name in ("imu_heading_bench.h", "imu_heading_bench_native.h",
                     "imu_heading_bench.cpp", "imu_heading_bench_native.cpp"):
            shutil.copyfile(root / "bench/imu_heading/src" / name, src / name)
        shutil.copyfile(root / "bench/imu_heading/imu_heading.ino", stage / "imu_heading.ino")
        config = (src / "config.h").read_text()
        for symbol, value in profile.items():
            config, count = re.subn(r"(" + symbol + r"\s*=\s*)\d+U",
                                   lambda match: match[1] + str(value) + "U", config)
            assert count == 1, (symbol, count)
        (src / "config.h").write_text(config)
        (stage / "Arduino.h").write_text("#pragma once\nunsigned long micros();\n")
        argv = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                "-fno-exceptions", "-fno-rtti", "-fsyntax-only", "-x", "c++",
                "-I", str(stage), "-I", str(src), str(src / "imu_heading_bench.cpp"),
                str(src / "imu_heading_bench_native.cpp"), str(stage / "imu_heading.ino")]
        outcome = subprocess.run(argv, capture_output=True, text=True)
        results.append({"temporary_config_overrides": profile, "argv": argv,
                        "exit_code": outcome.returncode, "stdout": outcome.stdout,
                        "stderr": outcome.stderr,
                        "cpp_sha256": hashlib.sha256((src / "imu_heading_bench.cpp").read_bytes()).hexdigest(),
                        "temporary_config_sha256": hashlib.sha256(config.encode()).hexdigest()})
receipt = {"compiler": subprocess.run(["g++", "--version"], capture_output=True,
                                      text=True, check=True).stdout,
           "scope": "Syntax only; temporary config profiles and Arduino clock declaration. No test bodies read.",
           "results": results}
destination = raw / "first_syntax.json"
assert not destination.exists(), "Do not overwrite previous execution evidence"
destination.write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({"checks": len(results), "failed": [x for x in results if x["exit_code"]]}, indent=2))
raise SystemExit(any(item["exit_code"] for item in results))
