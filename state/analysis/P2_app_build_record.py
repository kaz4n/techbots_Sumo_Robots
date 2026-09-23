"""Capture D099 subprocess status/output without inferring a target pass."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

name, *command = sys.argv[1:]
if not name.replace('_', '').isalnum() or not command:
    raise SystemExit('Expected simple receipt name and exact command argv')
base = Path(__file__).with_name('P2_app_build_raw')
base.mkdir(exist_ok=True)
if (base / (name + '.json')).exists() or (base / (name + '.txt')).exists():
    raise SystemExit('Preserve prior receipt; use a new name')
start = datetime.now(timezone.utc).isoformat()
with (base / (name + '.txt')).open('w', encoding='utf-8') as output:
    result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL)
receipt = dict(argv=command, returncode=result.returncode, start_utc=start,
               end_utc=datetime.now(timezone.utc).isoformat())
(base / (name + '.json')).write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
raise SystemExit(result.returncode)
