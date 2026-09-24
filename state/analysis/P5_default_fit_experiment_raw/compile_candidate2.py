"""Run one checked isolated candidate2 target compile and retain its source and ELF evidence."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys

out = Path(__file__).resolve().parent
root = out.parents[2]
project = root / 'build/p5_default_fit_candidate2'
manifest = json.loads((out / 'candidate2_materialized_manifest.json').read_text())
for name, row in manifest['files'].items():
    assert hashlib.sha256((project / name).read_bytes()).hexdigest() == row['sha256'], name
folder = out / 'app_candidate2'
folder.mkdir(exist_ok=False)
env = os.environ.copy()
adb = str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
env.update(SUMO_TRANSPORT='adb', SUMO_ADB_SERIAL='2629958581', SUMO_ADB_EXECUTABLE=adb,
           SUMO_REMOTE_ROOT='/home/arduino/sumox26_codex_build', PYTHONDONTWRITEBYTECODE='1')
argv = [sys.executable, '-B', str(out / 'invoke_candidate2.py')]
record = {'argv': argv, 'start_utc': datetime.now(timezone.utc).isoformat(),
          'compile_only': True, 'synthetic_config_overlay': False, 'cwd': str(root),
          'native_jobs': 1, 'materialized_manifest_sha256':
          hashlib.sha256((out / 'candidate2_materialized_manifest.json').read_bytes()).hexdigest()}
before = set((project / 'build/app-receipts').glob('*'))
run = subprocess.run(argv, cwd=root, env=env, capture_output=True, timeout=900)
(out / 'candidate2_compile.txt').write_bytes(run.stdout + run.stderr)
record.update(returncode=run.returncode, end_utc=datetime.now(timezone.utc).isoformat())
(out / 'candidate2_compile.json').write_text(json.dumps(record, indent=2) + '\n')
new_receipts = set((project / 'build/app-receipts').glob('*')) - before
assert len(new_receipts) <= 1
if new_receipts:
    receipt = new_receipts.pop()
    shutil.copytree(receipt, folder / 'receipt')
stage = project / 'build/stage/app'
files = {}
digest = hashlib.sha256()
for path in sorted(p for p in stage.rglob('*') if p.is_file()):
    name = path.relative_to(stage).as_posix()
    data = path.read_bytes()
    files[name] = hashlib.sha256(data).hexdigest()
    digest.update(name.encode() + b'\0' + data)
(folder / 'source_manifest.json').write_text(json.dumps(
    {'source_sha256': digest.hexdigest(), 'files': files}, indent=2) + '\n')
print(run.stdout[-1800:].decode('utf-8', 'replace'), flush=True)
print(run.stderr[-1200:].decode('utf-8', 'replace'), flush=True)
if run.returncode:
    raise SystemExit(run.returncode)
verified = json.loads((folder / 'receipt/verified.json').read_text())
assert digest.hexdigest() == verified['source_sha256']
records = []
for remote, expected in verified['file_sha256'].items():
    if not (remote.startswith(verified['build_path'] + '/') and remote.endswith('/app.ino.elf')):
        continue
    local = folder / Path(remote).name
    command = [adb, '-s', '2629958581', 'pull', remote, str(local)]
    pulled = subprocess.run(command, capture_output=True, timeout=60)
    row = {'argv': command, 'returncode': pulled.returncode,
           'stdout': pulled.stdout.decode(errors='replace'), 'stderr': pulled.stderr.decode(errors='replace')}
    records.append(row)
    (folder / 'artifact_collection.json').write_text(json.dumps(records, indent=2) + '\n')
    assert pulled.returncode == 0
    row['sha256'] = hashlib.sha256(local.read_bytes()).hexdigest()
    assert row['sha256'] == expected
assert len(records) == 1
(folder / 'artifact_collection.json').write_text(json.dumps(records, indent=2) + '\n')
print('app candidate2 checked and archived', verified['source_sha256'], flush=True)
