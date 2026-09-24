"""Verify the staged and remote source bytes for the checked D139 default compile."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shlex
import subprocess

out = Path(__file__).resolve().parent
root = out.parents[2]
read = lambda path: json.loads(path.read_text())
source = read(out / 'app/source_manifest.json')
working = read(out / 'working_source_manifest.json')
receipt = read(out / 'app/receipt/verified.json')
command = read(out / 'remote_snapshot_ready.json')['argv']
remote_root = command[-1]
adb = str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
digest = hashlib.sha256()
for name, expected in sorted(source['files'].items()):
    original = 'src/app/app.ino' if name == 'app.ino' else name
    assert working['files'][original]['sha256'] == expected, name
    data = (root / original).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected, name
    digest.update(name.encode() + b'\0' + data)
assert digest.hexdigest() == source['source_sha256'] == receipt['source_sha256']
args = ['sha256sum', '--', *[remote_root + '/' + name for name in source['files']]]
argv = [adb, '-s', '2629958581', 'shell', '-T', shlex.join(args)]
result = subprocess.run(argv, capture_output=True, text=True, timeout=60)
record = {'utc': datetime.now(timezone.utc).isoformat(), 'argv': argv,
          'scope': 'Read-only exact remote staged source hash verification; no compiler or MCU access',
          'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
          'source_sha256': source['source_sha256'], 'source_files': len(source['files'])}
(out / 'remote_source_binding.json').write_text(json.dumps(record, indent=2) + '\n')
assert result.returncode == 0
remote = {line.split(maxsplit=1)[1].strip(): line.split()[0] for line in result.stdout.splitlines()}
assert remote == {remote_root + '/' + name: value for name, value in source['files'].items()}
print('Current, frozen, staged and remote source binding passed for', len(remote), 'files.')
