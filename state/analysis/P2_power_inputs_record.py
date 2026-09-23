"""Record exact validation subprocess arguments, output and exit status for D093."""
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

name, *command = sys.argv[1:]
if not name.replace('_', '').isalnum() or not command:
    raise SystemExit('Expected simple receipt name and command arguments')
base = Path(__file__).parent / 'P2_power_inputs_raw'
base.mkdir(exist_ok=True)
if (base / (name + '.json')).exists() or (base / (name + '.txt')).exists():
    raise SystemExit('Receipt name already exists; preserve earlier evidence')
environment = os.environ.copy()
if os.name != 'nt':
    environment['TMPDIR'] = '/dev/shm'
started = datetime.now(timezone.utc).isoformat()
with (base / (name + '.txt')).open('w', encoding='utf-8') as output:
    process = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT,
                             env=environment, stdin=subprocess.DEVNULL)
receipt = dict(start_utc=started, end_utc=datetime.now(timezone.utc).isoformat(),
               argv=command, returncode=process.returncode)
if (base / (name + '.json')).exists():
    raise SystemExit('Subprocess created the receipt path; preserve it and use a distinct receipt name')
(base / (name + '.json')).write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt))
raise SystemExit(process.returncode)
