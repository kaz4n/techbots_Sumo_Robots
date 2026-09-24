"""Archive bounded D127 host-tool execution after its independent oracle freeze."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
name = sys.argv[1]
assert name in ('windows', 'linux', 'linux_repair1', 'windows_repair1')
assert not (out/(name+'.json')).exists(), 'Never replace an executed receipt'
freeze = json.loads((out/'freeze.json').read_text())
for relative, digest in freeze['sha256'].items():
    assert hashlib.sha256((root/relative).read_bytes()).hexdigest() == digest, relative
argv = [sys.executable, '-m', 'unittest', '-v', 'test_countdown_analysis']
if name.startswith('linux'):
    argv.append('test_csv_bundle')
env = os.environ.copy()
env['PYTHONPATH'] = str(root/'tests/tooling')
env['PYTHONDONTWRITEBYTECODE'] = '1'
if os.name != 'nt':
    env['TMPDIR'] = '/dev/shm'
record = {'utc': datetime.now(timezone.utc).isoformat(), 'argv': argv,
          'python': sys.version, 'platform': sys.platform, 'synthetic_fixtures': True}
with (out/(name+'.txt')).open('wb') as log:
    result = subprocess.run(argv, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
record['returncode'] = result.returncode
(out/(name+'.json')).write_text(json.dumps(record, indent=2)+'\n')
print((out/(name+'.txt')).read_text(errors='replace')[-6500:])
sys.exit(result.returncode)
