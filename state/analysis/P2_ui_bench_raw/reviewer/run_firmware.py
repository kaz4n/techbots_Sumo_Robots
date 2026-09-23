"""Execute unchanged independent D112 cases in an isolated WSL copy."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
receipt = OUT / ('firmware_' + str(time.time_ns()) + '.json')
record = dict(scope='Private WSL copy only; no board/network or shared build',
    independence='Reviewer has read production. Unchanged author metadata describes original separate-context authorship, not this reviewer.',results=[])
with tempfile.TemporaryDirectory(prefix='d112-review-') as temporary:
    copied = Path(temporary)
    for folder in ('src','tests','host','tools','bench','docs'):
        shutil.copytree(ROOT/folder,copied/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for path in ('state/analysis/P2_ui_bench_contract.md','state/analysis/P2_app_runtime_contract.md',
                 'state/analysis/P2_ui_bench_raw/registry/test_p0_config_before.py',
                 'state/analysis/P2_ui_bench_raw/registry/test_p0_config_after.py'):
        (copied/path).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/path,copied/path)
    hashes = {p.relative_to(copied).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
              for p in copied.rglob('*') if p.is_file()}
    for path,expected in {
        'bench/ui/src/ui_bench.cpp':'bc2def36d611f534112288dfca538ab36d51aff58d73c7e5e09eb1f0d9a7e70d',
        'tests/tooling/ui_bench_cases.cc':'0bf8fd656423114d35be2fc4589d726751888e512698030222ad8f71709b2bd3',
        'tests/tooling/test_ui_bench.py':'6fe512682214029421949f144f8adf2891e3b30531a2514a1c18de886cdae1b8',
    }.items(): assert hashes[path] == expected,path
    record['copied_hashes'] = hashes
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    argv = ['python3','-B','-m','unittest','tests.tooling.test_ui_bench','-v']
    env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH='tests/tooling')
    result = subprocess.run(argv,cwd=copied,env=env,text=True,capture_output=True,timeout=1200)
    record['results'].append(dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    generated = copied/'state/analysis/P2_ui_bench_raw/author'
    if generated.exists(): shutil.copytree(generated,OUT/(receipt.stem+'_cases'))
    print(result.stdout[-6000:],result.stderr[-6000:],flush=True)
    record['verdict'] = 'PASS_PRIVATE_UNCHANGED_D112_CASES' if result.returncode == 0 else 'FAIL_PRIVATE_UNCHANGED_D112_CASES'
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    print(receipt,flush=True)
    assert result.returncode == 0
