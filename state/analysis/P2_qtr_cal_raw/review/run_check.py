"""Capture a reviewer-only subprocess without replacing earlier evidence."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
import sys

out = Path(__file__).resolve().parent
name, *argv = sys.argv[1:]
assert name.replace('_', '').isalnum() and argv
assert not (out / (name + '.json')).exists()
start = datetime.now(timezone.utc).isoformat()
with (out / (name + '.txt')).open('w', encoding='utf-8') as stream:
    result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL)
record = dict(start_utc=start, end_utc=datetime.now(timezone.utc).isoformat(),
              argv=argv, returncode=result.returncode)
(out / (name + '.json')).write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record))
raise SystemExit(result.returncode)
