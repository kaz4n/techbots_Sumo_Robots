from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

root = Path.cwd()
raw = root / "state/analysis/P2_vbat_raw/worker"
config = (root / "src/config.h").read_text()
assert "VBAT_BENCH_SAMPLES" in config
profiles = [
    {"capacity": 128}, {"capacity": 1}, {"capacity": 0},
    {"capacity": 128, "period": 0},
    {"capacity": 128, "period": 0x80000000},
    {"capacity": 128, "period": 1, "conversion": 1},
]
results = []
for profile in profiles:
    with tempfile.TemporaryDirectory(prefix="vbat-syntax-") as tmp:
        stage = Path(tmp)
        src = stage / "src"
        (src / "hal").mkdir(parents=True)
        for name in ("vbat.h", "vbat_native.h", "vbat.cpp", "vbat_native.cpp"):
            shutil.copyfile(root / "bench/vbat/src" / name, src / name)
        shutil.copyfile(root / "bench/vbat/vbat.ino", stage / "vbat.ino")
        shutil.copyfile(root / "src/hal/power.h", src / "hal/power.h")
        local = config
        for field, symbol in (("capacity", "VBAT_BENCH_SAMPLES"),
                              ("period", "VBAT_SAMPLE_PERIOD_US"),
                              ("conversion", "VBAT_ADC_CONVERSION_US")):
            if field in profile:
                local, count = re.subn(r"(" + symbol + r"\s*=\s*)\d+U",
                                      lambda match: match[1] + str(profile[field]) + "U", local)
                assert count == 1, (symbol, count)
        (src / "config.h").write_text(local)
        (stage / "Arduino.h").write_text("#pragma once\nunsigned long micros();\n")
        argv = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                "-fno-exceptions", "-fno-rtti", "-fsyntax-only", "-x", "c++",
                "-I", str(stage), "-I", str(src), str(src / "vbat.cpp"),
                str(src / "vbat_native.cpp"), str(stage / "vbat.ino")]
        outcome = subprocess.run(argv, capture_output=True, text=True)
        results.append({"temporary_profile": profile, "argv": argv,
                        "exit_code": outcome.returncode, "stdout": outcome.stdout,
                        "stderr": outcome.stderr,
                        "cpp_sha256": hashlib.sha256((src / "vbat.cpp").read_bytes()).hexdigest(),
                        "temporary_config_sha256": hashlib.sha256(local.encode()).hexdigest()})
receipt = {"compiler": subprocess.run(["g++", "--version"], capture_output=True,
                                      text=True, check=True).stdout,
           "scope": "Syntax only; temporary config profiles and Arduino clock declaration. No test bodies read.",
           "results": results}
(raw / "second_syntax.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
raise SystemExit(any(item["exit_code"] for item in results))
