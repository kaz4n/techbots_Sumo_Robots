"""Compile only the owned Runner in copied normal and zero-period source trees."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[4]
output = Path(__file__).resolve().parent / "third_syntax.json"
results = []
for period in (1000, 0):
    with tempfile.TemporaryDirectory(prefix="opp-view-syntax-") as temporary:
        stage = Path(temporary)
        shutil.copytree(root / "src", stage / "src")
        shutil.copytree(root / "bench/opp_view/src", stage / "bench")
        config = stage / "src/config.h"
        original = config.read_text()
        needle = "inline constexpr std::uint32_t TICK_US = 1000U;"
        assert original.count(needle) == 1
        config.write_text(original.replace(needle, f"inline constexpr std::uint32_t TICK_US = {period}U;"))
        command = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                   "-fsyntax-only", "-I", str(stage / "src"), str(stage / "bench/opp_view.cpp")]
        result = subprocess.run(command, capture_output=True, text=True)
        results.append({"tick_us_in_temporary_copy": period, "argv": command,
                        "production_cpp_sha256": hashlib.sha256((root / "bench/opp_view/src/opp_view.cpp").read_bytes()).hexdigest(),
                        "temporary_config_sha256": hashlib.sha256(config.read_bytes()).hexdigest(),
                        "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
output.write_text(json.dumps(results, indent=2) + "\n")
print(output)
print(json.dumps(results, indent=2))
raise SystemExit(any(result["exit_code"] != 0 for result in results))
