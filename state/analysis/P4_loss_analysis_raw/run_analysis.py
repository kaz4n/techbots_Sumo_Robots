"""Run frozen offline D130 and unchanged CSV/countdown tests with exact receipts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
run_name = sys.argv[1]
assert run_name.replace('_', '').isalnum()
for name in ('baseline.json', 'freeze.json'):
    for relative, expected in json.loads((out/name).read_text())['sha256'].items():
        assert hashlib.sha256((root/relative).read_bytes()).hexdigest() == expected, relative
assert not (out/(run_name+'.json')).exists()
assert not (out/(run_name+'.txt')).exists()
argv = [sys.executable, '-m', 'unittest', '-v',
        'tests.tooling.test_target_loss_analysis',
        'tests.tooling.test_countdown_analysis', 'tests.tooling.test_csv_bundle']
env = os.environ.copy()
env['PYTHONPATH'] = os.pathsep.join((str(root/'tools'), str(root/'tests/tooling')))
record = {'argv': argv, 'start_utc': datetime.now(timezone.utc).isoformat(),
          'python': sys.version, 'run_name': run_name}
with (out/(run_name+'.txt')).open('wb') as log:
    result = subprocess.run(argv, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
record.update(returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
(out/(run_name+'.json')).write_text(json.dumps(record, indent=2)+'\n')
print((out/(run_name+'.txt')).read_text(errors='replace')[-4500:])
sys.exit(result.returncode)
