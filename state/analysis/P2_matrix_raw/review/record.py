"""Capture reviewer-owned local checks without changing implementation or tests."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[3]

name, *command = sys.argv[1:]
if not name.replace('_', '').isalnum() or not command:
    raise SystemExit('Expected simple receipt name and argv')
receipt = BASE / (name + '.json')
output = BASE / (name + '.txt')
if receipt.exists() or output.exists():
    raise SystemExit('Preserve prior receipt')
started = datetime.now(timezone.utc).isoformat()
with output.open('wb') as stream:
    proc = subprocess.run(command, cwd=ROOT, stdin=subprocess.DEVNULL,
                          stdout=stream, stderr=subprocess.STDOUT)
data = dict(start_utc=started, end_utc=datetime.now(timezone.utc).isoformat(),
            argv=command, returncode=proc.returncode,
            output_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
receipt.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
print(json.dumps(data))
raise SystemExit(proc.returncode)
