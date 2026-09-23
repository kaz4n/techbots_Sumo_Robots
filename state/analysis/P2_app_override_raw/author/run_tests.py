# Captures independent D099-R1 local regression output and its exact source hashes.
# Preserves red evidence without replacing earlier runs or invoking any transport.
# Run with Windows Python; the unittest process runs in WSL Ubuntu.
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[4]
FOLDER = Path(__file__).parent
name = sys.argv[1]
if not name.replace('_', '').replace('-', '').isalnum():
    raise SystemExit('Use a plain evidence name')
if any((FOLDER / (name + suffix)).exists() for suffix in ('.json', '.stdout.txt', '.stderr.txt')):
    raise SystemExit('Evidence names are append-only')
command = ['wsl', '-d', 'Ubuntu', '--', 'bash', '-lc',
           'cd /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots && '
           'python3 -m unittest discover -s tests/tooling -p test_app_build_overrides.py -v']
identities = ['tools/app_build_policy.py', 'tools/board_tool.py',
              'tests/tooling/test_app_build_overrides.py',
              'tests/fixtures/app_build_overrides/mutations.json',
              'tests/fixtures/app_build_overrides/fault_command.py',
              'tests/tooling/fake_command.py', 'tests/tooling/fake_app_reference.json',
              'state/analysis/P2_app_build_raw/default_receipt/compile.stdout.json']
hashes = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in identities}
result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=180)
after = {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in identities}
(FOLDER / (name + '.stdout.txt')).write_bytes(result.stdout)
(FOLDER / (name + '.stderr.txt')).write_bytes(result.stderr)
(FOLDER / (name + '.json')).write_text(json.dumps({
    'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'command': command,
    'returncode': result.returncode, 'sha256_before_run': hashes,
    'sha256_after_run': after, 'source_identities_stable_during_run': hashes == after,
    'scope': 'Pure validators and isolated local command fixtures; no board or network'},
    indent=2) + '\n', encoding='utf-8')
sys.stdout.buffer.write(result.stdout)
sys.stderr.buffer.write(result.stderr)
raise SystemExit(result.returncode)
