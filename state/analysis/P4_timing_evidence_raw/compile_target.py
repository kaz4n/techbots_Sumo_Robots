"""Checked D129 Linux compile and artifact collection only; never upload/reset."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
profile = sys.argv[1]
assert profile in ('app', 'reactive_test', 'reactive_timing', 'reactive_timing_configured')
configured = profile == 'reactive_timing_configured'
project = 'reactive_timing' if configured else profile
sketch = 'app' if project == 'app' else 'bench/' + project
source_root = root
if configured:
    source_root = root/'build/d129_configured_fixture'
    assert not source_root.exists(), 'Do not overwrite prior fixture evidence'
    for name in ('src', 'tools', 'bench/reactive_timing'):
        shutil.copytree(root/name, source_root/name,
                        ignore=shutil.ignore_patterns('__pycache__'))
    config = source_root/'src/config.h'
    data = config.read_text()
    replacements = {
        'BUTTON_WINDOWS_CONFIGURED = 0U': 'BUTTON_WINDOWS_CONFIGURED = 1U',
        'BUTTON_LOW_RAW[4] = {0U, 0U, 0U, 0U}': 'BUTTON_LOW_RAW[4] = {0U, 900U, 1900U, 2900U}',
        'BUTTON_HIGH_RAW[4] = {0U, 0U, 0U, 0U}': 'BUTTON_HIGH_RAW[4] = {100U, 1100U, 2100U, 3100U}',
    }
    for before, after in replacements.items():
        assert data.count(before) == 1
        data = data.replace(before, after)
    config.write_text(data)
    (out/'configured_config.h').write_bytes(config.read_bytes())
env = os.environ.copy()
adb = str(Path(os.environ['LOCALAPPDATA'])/'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
env.update(SUMO_TRANSPORT='adb', SUMO_ADB_SERIAL='2629958581', SUMO_ADB_EXECUTABLE=adb,
           SUMO_REMOTE_ROOT='/home/arduino/sumox26_codex_build')
argv = [sys.executable, 'tools/board_tool.py', 'flash', sketch, '--compile-only']
record = {'argv': argv, 'start_utc': datetime.now(timezone.utc).isoformat(),
          'compile_only': True, 'synthetic_config_overlay': configured, 'cwd':str(source_root)}
run = subprocess.run(argv, cwd=source_root, env=env, capture_output=True, timeout=900)
(out/(profile+'_compile.txt')).write_bytes(run.stdout+run.stderr)
record.update(returncode=run.returncode, end_utc=datetime.now(timezone.utc).isoformat())
(out/(profile+'_compile.json')).write_text(json.dumps(record, indent=2)+'\n')
print(run.stdout[-5000:].decode('utf-8', 'replace'), flush=True)
print(run.stderr[-2000:].decode('utf-8', 'replace'), flush=True)
if run.returncode: raise SystemExit(run.returncode)
match = re.search(r'APP BUILD CHECKED: native-app-v1; receipt=(.+)', run.stdout.decode())
assert match
receipt = Path(match.group(1).strip())
folder = out/profile
folder.mkdir(exist_ok=False)
shutil.copytree(receipt, folder/'receipt')
verified = json.loads((receipt/'verified.json').read_text())
stage = source_root/'build/stage'/project
files = {}
digest = hashlib.sha256()
for path in sorted(p for p in stage.rglob('*') if p.is_file()):
    name = path.relative_to(stage).as_posix()
    data = path.read_bytes()
    files[name] = hashlib.sha256(data).hexdigest()
    digest.update(name.encode()+b'\0'+data)
assert digest.hexdigest() == verified['source_sha256']
(folder/'source_manifest.json').write_text(json.dumps({'source_sha256':digest.hexdigest(), 'files':files}, indent=2)+'\n')
records = []
for remote, expected in verified['file_sha256'].items():
    if not (remote.startswith(verified['build_path']+'/') and remote.endswith('.ino.elf')):
        continue
    local = folder/Path(remote).name
    command = [adb, '-s', '2629958581', 'pull', remote, str(local)]
    pulled = subprocess.run(command, capture_output=True, timeout=60)
    row = {'argv':command, 'returncode':pulled.returncode,
           'stdout':pulled.stdout.decode(errors='replace'), 'stderr':pulled.stderr.decode(errors='replace')}
    assert pulled.returncode == 0
    row['sha256'] = hashlib.sha256(local.read_bytes()).hexdigest()
    assert row['sha256'] == expected
    records.append(row)
assert len(records) == 1
(folder/'artifact_collection.json').write_text(json.dumps(records, indent=2)+'\n')
print(profile, 'checked and archived', verified['source_sha256'], flush=True)
