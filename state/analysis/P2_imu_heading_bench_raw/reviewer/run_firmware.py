"""Execute unchanged independent D111 cases in an isolated WSL copy."""
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
with tempfile.TemporaryDirectory(prefix='d111-review-') as temporary:
    copied = Path(temporary)
    for folder in ('src','tests','host','tools','bench','docs'):
        shutil.copytree(ROOT/folder,copied/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for path in ('state/analysis/P2_imu_heading_bench_contract.md','state/analysis/P2_app_runtime_contract.md',
                 'state/analysis/P2_imu_heading_bench_raw/registry/test_p0_config_before.py'):
        (copied/path).parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/path,copied/path)
    hashes = {p.relative_to(copied).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
              for p in copied.rglob('*') if p.is_file()}
    for path,expected in {
        'bench/imu_heading/src/imu_heading_bench.cpp':'6d3c6c5f5234d995689cc265c65de7848e2bc2dd6b8fa0748e6b2f1cec8ce61f',
        'tests/tooling/imu_heading_bench_cases.cc':'a9e9fce1b293a43c7b8631447da67cfa43c6b67c70fe877f058beb4cbc2f8e11',
        'tests/tooling/test_imu_heading_bench.py':'bcc2b6da626d20e61603b9b91550ff4371f584f0bffce7679639b09d8be1407b',
    }.items(): assert hashes[path] == expected,path
    record['copied_hashes'] = hashes
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    argv = ['python3','-B','-m','unittest','tests.tooling.test_imu_heading_bench','-v']
    env = dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH='tests/tooling')
    result = subprocess.run(argv,cwd=copied,env=env,text=True,capture_output=True,timeout=1200)
    record['results'].append(dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    generated = copied/'state/analysis/P2_imu_heading_bench_raw/author'
    if generated.exists(): shutil.copytree(generated,OUT/(receipt.stem+'_cases'))
    print(result.stdout[-6000:],result.stderr[-6000:],flush=True)
    record['verdict'] = 'PASS_PRIVATE_UNCHANGED_D111_CASES' if result.returncode == 0 else 'FAIL_PRIVATE_UNCHANGED_D111_CASES'
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    print(receipt,flush=True)
    assert result.returncode == 0
