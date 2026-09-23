"""Verify preserved D112 author and private execution receipts without changing tests."""
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
RAW=OUT.parent
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
freeze=read(RAW/'author/freeze.json')
for p,h in freeze['sha256'].items(): assert sha(ROOT/p)==h,p
private_path=OUT/'firmware_1790198614083708719.json'
private=read(private_path)
assert private['verdict']=='PASS_PRIVATE_UNCHANGED_D112_CASES'
assert private['results'][0]['returncode']==0
for p,h in freeze['sha256'].items():
    if p in private['copied_hashes']: assert private['copied_hashes'][p]==h,p
for row in read(RAW/'worker/second_source_freeze.json')['files']:
    assert private['copied_hashes'][row['path']]==row['sha256']
summary=read(RAW/'author/run1_summary.json')
assert summary['result']=='PASS' and summary['no_test_amendments']
def audit_commands(folder):
    rows=[(p,read(p)) for p in sorted(folder.glob('command_*.json'))]
    # The author's additional Windows-to-WSL wrapper is separately retained.
    rows=[(p,r) for p,r in rows if 'wsl.exe' not in r['argv'][0]]
    assert len(rows)==65
    programs=[]; refused=[]
    for p,r in rows:
        if '-fsyntax-only' in r['argv']:
            assert r['returncode']!=0 and 'static assertion failed' in r['stderr']
            refused.append(p.name)
        else:
            assert r['returncode']==0,(p,r['stderr'])
            assert not r['stderr'],p
            if '--order-by=file' in r['argv']:
                assert 'Status: SUCCESS!' in r['stdout']
                counts=re.search(r'test cases:\s+(\d+)\s+\|\s+(\d+) passed\s+\|\s+0 failed',r['stdout'])
                assertions=re.search(r'assertions:\s+(\d+)\s+\|\s+(\d+) passed\s+\|\s+0 failed',r['stdout'])
                assert counts and assertions
                assert counts[1]==counts[2] and assertions[1]==assertions[2]
                programs.append(dict(name=Path(r['argv'][0]).name,cases=int(counts[1]),assertions=int(assertions[1]),receipt=p.name))
    assert len(programs)==30 and len(refused)==3
    assert [x for x in programs if x['name'] in ('normal','asan_ubsan')]==[
        dict(name=x['name'],cases=35,assertions=21759,receipt=x['receipt']) for x in programs if x['name'] in ('normal','asan_ubsan')]
    registry=[json.loads(s) for s in (folder/'registry/registry_cases.jsonl').read_text().splitlines()]
    assert len(registry)==5 and sum(not row['expected_failure'] for row in registry)==1
    return dict(commands=len(rows),programs=programs,expected_compile_refusals=refused,registry_profiles=5,registry_original_assertions=90)
author=audit_commands(RAW/'author')
independent=audit_commands(OUT/'firmware_1790198614083708719_cases')
assert [(r['name'],r['cases'],r['assertions']) for r in author['programs']]==[(r['name'],r['cases'],r['assertions']) for r in independent['programs']]
result=dict(verdict='PASS_FROZEN_AUTHOR_AND_PRIVATE_EXECUTION',author=author,reviewer=independent,
    private_receipt_sha256=sha(private_path),frozen_inputs_sha256=freeze['sha256'],
    independence='Separate reused same-model contract-only author; reviewer read implementation and reran unchanged tests in isolated WSL copy. Coordinator authored tooling cases.',
    limits=['Named profile filters deliberately exclude unrelated cases; main and capacity1 profiles have no skips.',
        'Native substitutes counted Reader methods; actual ADC behavior remains existing provider scope.',
        'Synthetic windows are not physical thresholds; no full B6 gestures, optics, hardware, WCET or gate claim.',
        'Exactly-once decoder call additionally source/ELF reviewed; unreachable giant counters and sequence wrap source reviewed only.',
        'No redundant full-host rerun; prior D109 private CTest2/2 retained under coordinator scope, 337 prior tests and89 shared source files unchanged.'])
(OUT/'firmware_review.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['verdict'])
