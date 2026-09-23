"""Run existing staging checks against a local snapshot and fake transports only."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='d085-staging-review-', dir='/dev/shm') as tmp:
    stage = Path(tmp)
    for folder in ('src','tests','host','bench','tools','docs'):
        shutil.copytree(root/folder, stage/folder,
                        ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    manifest = {p.relative_to(stage).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(stage.rglob('*')) if p.is_file()}
    (out/'staging_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR='/dev/shm',
               PYTHONPATH=str(stage/'tests/tooling'))
    argv = [sys.executable,'-m','unittest','tests.tooling.test_staged_core','-v']
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(argv,cwd=stage,env=env,capture_output=True,timeout=300)
    (out/'staging_stdout.txt').write_bytes(result.stdout)
    (out/'staging_stderr.txt').write_bytes(result.stderr)
    receipt = dict(argv=argv,cwd=str(stage),started_utc=started,
                   ended_utc=datetime.now(timezone.utc).isoformat(),exit=result.returncode,
                   stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
                   stderr_sha256=hashlib.sha256(result.stderr).hexdigest())
    (out/'staging_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
    print(result.stderr.decode(errors='replace'))
    raise SystemExit(result.returncode)
