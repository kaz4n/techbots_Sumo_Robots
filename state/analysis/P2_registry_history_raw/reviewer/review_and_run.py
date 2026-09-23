"""Verify two historical fixture paths; execute live mismatch and historical tamper controls privately."""
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
RAW=OUT.parent
def sha(data): return hashlib.sha256(data).hexdigest()
changes=json.loads((RAW/'change.json').read_text())
expected={
 'tests/tooling/test_vbat.py':(b'current = (ROOT / "tests/tooling/test_p0_config.py").read_bytes()',b'current = (ROOT / "state/analysis/P2_vbat_raw/registry/test_p0_config_after.py").read_bytes()'),
 'tests/tooling/test_imu_heading_bench.py':(b'after = (ROOT / "tests/tooling/test_p0_config.py").read_bytes()',b'after = (folder / "test_p0_config_after.py").read_bytes()')}
for item in changes['changes']:
    path=item['path'];before=(RAW/(Path(path).stem+'_before.py')).read_bytes();after=(ROOT/path).read_bytes()
    old,new=expected[path]
    assert before.count(old)==1 and before.replace(old,new)==after
    assert sha(before)==item['before_sha256'] and sha(after)==item['after_sha256']
snapshots={
 'state/analysis/P2_vbat_raw/registry/test_p0_config_before.py':'c0156a8e50ee38bb317f531a17c3c1ac704ec2d28b4b5bd3324a25204bc0e248',
 'state/analysis/P2_vbat_raw/registry/test_p0_config_after.py':'9252acfc639c9729fe47b03d1d5e5f7e21088ef90bcb0c65132620f00315ce5e',
 'state/analysis/P2_vbat_raw/author/test_p0_config_before.py':'c0156a8e50ee38bb317f531a17c3c1ac704ec2d28b4b5bd3324a25204bc0e248',
 'state/analysis/P2_imu_heading_bench_raw/registry/test_p0_config_before.py':'9252acfc639c9729fe47b03d1d5e5f7e21088ef90bcb0c65132620f00315ce5e',
 'state/analysis/P2_imu_heading_bench_raw/registry/test_p0_config_after.py':'6c92b892222e9c1eeccd824693798015cdd9f2cffda0837a66540f6158b41065'}
for path,expected_hash in snapshots.items(): assert sha((ROOT/path).read_bytes())==expected_hash,path
methods=['tests.tooling.test_vbat.VbatTests.test_registry_single_addition_original_18_checks_and_wrong_129',
 'tests.tooling.test_imu_heading_bench.ImuHeadingBenchTests.test_registry_five_literal_additions_unchanged_18_checks_and_wrong_values']
result={'scope':'Private WSL filesystem only. No implementation/locked-test/board/network operation.','changes':changes,
 'snapshot_sha256':snapshots,'commands':[]}
receipt=OUT/('run_'+str(time.time_ns())+'.json')
with tempfile.TemporaryDirectory(prefix='registry-history-review-') as temporary:
    stage=Path(temporary)
    for directory in ('tests','src','docs','tools'):
        shutil.copytree(ROOT/directory,stage/directory,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for path in [*snapshots,'state/analysis/P2_app_runtime_contract.md']:
        (stage/path).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,stage/path)
    result['initial_copy_sha256']={p.relative_to(stage).as_posix():sha(p.read_bytes()) for p in stage.rglob('*') if p.is_file()}
    env=dict(os.environ,PYTHONPATH='tests/tooling',PYTHONDONTWRITEBYTECODE='1')
    def run(label, selected, failed=False, nested=False):
        args=['python3','-B','-m','unittest',*selected,'-v']
        r=subprocess.run(args,cwd=stage,env=env,text=True,capture_output=True,timeout=120)
        row=dict(label=label,argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,expected_failure=failed)
        result['commands'].append(row);receipt.write_text(json.dumps(result,indent=2)+'\n')
        assert (r.returncode!=0)==failed,(label,r.stdout,r.stderr)
        assert 'ERROR' not in r.stdout+r.stderr,(label,r.stderr)
        if failed: assert 'FAIL' in r.stderr,(label,r.stderr)
        if nested: assert 'Ran 18 tests' in r.stderr,(label,r.stderr)
        print(label+': expected '+('refusal' if failed else 'PASS'),flush=True)
    current_vbat=(stage/'tests/tooling/test_vbat.py').read_bytes()
    (stage/'tests/tooling/test_vbat.py').write_bytes((RAW/'test_vbat_before.py').read_bytes())
    run('original-vbat-red-against-D111-live-registry',[methods[0]],True)
    (stage/'tests/tooling/test_vbat.py').write_bytes(current_vbat)
    run('corrected-both-history-and-live-controls',methods)
    config=stage/'src/config.h';config_bytes=config.read_bytes()
    values={'VBAT_BENCH_SAMPLES':(128,methods[0]),'IMU_BENCH_TRIAL_US':(60000000,methods[1]),
        'IMU_BENCH_CHECKPOINT_US':(1000000,methods[1]),'IMU_BENCH_CHECKPOINTS':(61,methods[1]),
        'IMU_BENCH_DEADLINE_US':(70000000,methods[1]),'IMU_BENCH_MAX_POLLS':(100000000,methods[1])}
    for name,(value,method) in values.items():
        altered,n=re.subn(rb'(\b'+name.encode()+rb'\s*=\s*)[^;]+;',lambda m:m[1]+str(value+1).encode()+b'U;',config_bytes)
        assert n==1;config.write_bytes(altered)
        run('wrong-current-value-'+name,[method],True,True)
        config.write_bytes(config_bytes)
    registry=stage/'tests/tooling/test_p0_config.py';registry_bytes=registry.read_bytes()
    line=b"    'REVIEW_FUTURE_PERIOD_US': 1234,  # Synthetic future addition; never adopted.\n"
    assert registry_bytes.count(b'BEHAVIOR_EXTRA_DEFAULTS = {\n')==1
    registry.write_bytes(registry_bytes.replace(b'BEHAVIOR_EXTRA_DEFAULTS = {\n',b'BEHAVIOR_EXTRA_DEFAULTS = {\n'+line))
    config.write_bytes(config_bytes+b'\nnamespace config {\ninline constexpr std::uint32_t REVIEW_FUTURE_PERIOD_US = 1234U;\n}\n')
    run('synthetic-future-addition-retains-both-history-and-live-checks',methods)
    registry.write_bytes(registry_bytes);config.write_bytes(config_bytes)
    for index,name in enumerate(('P2_vbat_raw','P2_imu_heading_bench_raw')):
        path=stage/'state/analysis'/name/'registry/test_p0_config_after.py';saved=path.read_bytes()
        path.write_bytes(saved+b'\n# deliberately corrupt historical snapshot\n')
        run('historical-tamper-'+name,[methods[index]],True)
        path.write_bytes(saved)
    generated=stage/'state/analysis'
    for name in ('P2_vbat_raw','P2_imu_heading_bench_raw'):
        src=generated/name/'author'
        if src.exists(): shutil.copytree(src,OUT/(receipt.stem+'_cases')/name)
result['verdict']='PASS_EXACT_TWO_PATH_FIX_HISTORY_AND_LIVE_CONTROLS'
receipt.write_text(json.dumps(result,indent=2)+'\n')
print(receipt)
