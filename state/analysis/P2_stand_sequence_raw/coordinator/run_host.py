"""Record D119 full host commands; does not access the board."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys
root = Path(__file__).resolve().parents[4]
out = Path(__file__).resolve().parent
profile = sys.argv[1]
commands = {
    "normal": ["wsl", "-d", "Ubuntu", "--", "bash", "tools/test_host.sh"],
    "sanitize": ["wsl", "-d", "Ubuntu", "--", "bash", "-c", "cmake -S host -B build/host-sanitize && cmake --build build/host-sanitize --parallel 2 && ctest --test-dir build/host-sanitize --output-on-failure"]
}
argv = commands[profile]
names = ["src/core/stand_sequence.cpp", "src/core/stand_sequence.h", "tests/test_stand_sequence.cpp", "src/config.h"]
before = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
start = datetime.now(timezone.utc).isoformat()
result = subprocess.run(argv, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=900)
end = datetime.now(timezone.utc).isoformat()
(out / (profile + ".txt")).write_bytes(result.stdout)
record = {"argv": argv, "cwd": str(root), "start_utc": start, "end_utc": end, "returncode": result.returncode, "before_sha256": before, "after_sha256": {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}}
(out / (profile + ".json")).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record), flush=True)
print(result.stdout[-3500:].decode("utf-8", "replace"), flush=True)
raise SystemExit(result.returncode)
