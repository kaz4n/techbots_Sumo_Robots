"""Independent D080 review command/status/source identity recorder; no board I/O."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[3]
base = Path(__file__).resolve().parent
name, *command = sys.argv[1:]
if not name.replace('_', '').isalnum() or not command:
    raise SystemExit('Expected receipt name and command argv')

def sources():
    paths = [root / 'host/CMakeLists.txt', root / 'state/analysis/P2_imu_setup_contract.md']
    for folder in ('src', 'tests', 'bench/p2_imu_setup_compile'):
        paths += [p for p in (root / folder).rglob('*') if p.is_file()
                  and p.suffix in ('.cpp', '.h', '.ino', '.cc', '.py')]
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(paths))}

before = sources()
start = datetime.now(timezone.utc).isoformat()
clock = time.monotonic()
environment = os.environ.copy()
environment['PYTHONDONTWRITEBYTECODE'] = '1'
with (base / (name + '.txt')).open('w', encoding='utf-8') as output:
    result = subprocess.run(command, cwd=root, env=environment, stdin=subprocess.DEVNULL,
                            stdout=output, stderr=subprocess.STDOUT)
after = sources()
data = dict(start_utc=start, end_utc=datetime.now(timezone.utc).isoformat(),
            elapsed_s=time.monotonic() - clock, cwd=str(root), argv=command,
            returncode=result.returncode, before=before, after=after,
            sources_unchanged=before == after)
data['output_sha256'] = hashlib.sha256((base / (name + '.txt')).read_bytes()).hexdigest()
(base / (name + '.json')).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in data.items() if k not in ('before', 'after')}))
raise SystemExit(result.returncode)
