# Runs the independent D099 host checks and preserves exact subprocess evidence.
# Avoids nested PowerShell-to-bash status expansion ambiguity from the first run.
# Execute with Windows Python; invoked tests use only synthetic local transports.
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[4]
name = sys.argv[1]
command = ['wsl', '-d', 'Ubuntu', '--', 'bash', '-lc',
           'cd /mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots && '
           'python3 -m unittest discover -s tests/tooling -p test_app_build_policy.py -v']
result = subprocess.run(command, cwd=root, capture_output=True, timeout=180)
folder = Path(__file__).parent
(folder / (name + '.stdout.txt')).write_bytes(result.stdout)
(folder / (name + '.stderr.txt')).write_bytes(result.stderr)
(folder / (name + '.json')).write_text(json.dumps({
    'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'command': command,
    'returncode': result.returncode, 'scope': 'Synthetic host tests only; no board'},
    indent=2) + '\n', encoding='utf-8')
sys.stdout.buffer.write(result.stdout)
sys.stderr.buffer.write(result.stderr)
raise SystemExit(result.returncode)
