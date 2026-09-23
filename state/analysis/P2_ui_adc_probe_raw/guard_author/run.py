"""Run frozen public-contract guard cases in an opaque private WSL copy."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
stamp=str(time.time_ns())
freeze=json.loads((OUT/'freeze.json').read_text())
test=ROOT/'tests/tooling/test_ui_adc_run.py'
assert hashlib.sha256(test.read_bytes()).hexdigest()==freeze['test_sha256']
record=dict(scope='Private WSL synthetic fixtures only; no board/network/upload',
    implementation_bodies_read=False,
    independence='Reused reviewer context saw prior board_tool; new guard and pending board diff unread')
with tempfile.TemporaryDirectory(prefix='d114-run-guard-') as temporary:
    copied=Path(temporary)
    for folder in ('tools','tests'):
        shutil.copytree(ROOT/folder,copied/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    record['copied_sha256']={p.relative_to(copied).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in copied.rglob('*') if p.is_file()}
    receipt=OUT/('run_'+stamp+'.json')
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    argv=['python3','-B','-m','unittest','tests.tooling.test_ui_adc_run','-v']
    result=subprocess.run(argv,cwd=copied,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
                          capture_output=True,text=True,timeout=120)
    record.update(argv=argv,returncode=result.returncode)
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    (OUT/('run_'+stamp+'_stdout.txt')).write_text(result.stdout)
    (OUT/('run_'+stamp+'_stderr.txt')).write_text(result.stderr)
    summary=[line for line in result.stderr.splitlines() if
             line.startswith(('test_','Ran ','OK','FAILED','ERROR:','FAIL:'))]
    print(json.dumps(dict(receipt=str(receipt),returncode=result.returncode,summary=summary)),flush=True)
    raise SystemExit(result.returncode)
