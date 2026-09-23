"""Verify frozen D111 private command receipts and the additive startup-only amendment."""
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
freeze=read(OUT.parent/'author/freeze.json')
runpath=OUT/'firmware_1790197445705089414.json'
run=read(runpath)
assert run['verdict']=='PASS_PRIVATE_UNCHANGED_D111_CASES' and run['results'][0]['returncode']==0
for path, expected in freeze['sha256'].items():
    assert run['copied_hashes'][path]==expected
    if path!='tests/tooling/imu_heading_bench_cases.cc': assert sha(ROOT/path)==expected
commands=[read(p) for p in (OUT/(runpath.stem+'_cases')).glob('command_*.json')]
executed=[c for c in commands if '--no-colors' in c['argv']]
refused=[c for c in commands if '-fsyntax-only' in c['argv']]
assert len(executed)==28 and len(refused)==3
assert all(c['returncode']==0 and not c['stderr'] for c in executed)
assert all(c['returncode']!=0 and 'static assertion failed' in c['stderr'] for c in refused)
assert all(c['returncode']==0 for c in commands if c not in refused)
def profile(c):
    cases=list(map(int,re.search(r'test cases:\s+(\d+)\s+\|\s+(\d+) passed \| (\d+) failed \| (\d+) skipped',c['stdout']).groups()))
    assertions=list(map(int,re.search(r'assertions:\s+(\d+)\s+\|\s+(\d+) passed \| (\d+) failed',c['stdout']).groups()))
    assert cases[0]==cases[1] and cases[2]==0 and assertions[0]==assertions[1] and assertions[2]==0
    return dict(name=Path(c['argv'][0]).name,cases=cases,assertions=assertions)
profiles=[profile(c) for c in executed]
for name in ('normal','asan_ubsan'):
    p=next(p for p in profiles if p['name']==name)
    assert p['cases']==[31,31,0,0] and p['assertions']==[1342660,1342660,0]
registry=[json.loads(line) for line in (OUT/(runpath.stem+'_cases')/'registry/registry_cases.jsonl').read_text().splitlines()]
assert len(registry)==6
assert not registry[0]['expected_failure'] and registry[0]['nested_d093_receipt']['success']
assert all(r['expected_failure'] and 'Ran 18 tests' in r['assertion'] and 'FAILED (failures=1)' in r['assertion'] and 'ERROR' not in r['assertion'] for r in registry[1:])
startup=read(OUT/'startup_review.json')
assert startup['verdict']=='PASS_PRIVATE_ADDITIVE_STARTUP_NATIVE_PROFILES'
assert sha(ROOT/'tests/tooling/imu_heading_bench_cases.cc')==startup['amended_cases']
added=[read(p) for p in (ROOT/startup['receipts']).glob('command_*.json')]
assert all(c['returncode']==0 and not c['stderr'] for c in added)
extra=[profile(c) for c in added if '--no-colors' in c['argv']]
assert len(extra)==2 and all(p['cases']==[3,3,0,31] and p['assertions']==[38,38,0] for p in extra)
policy=read(OUT/'policy_1790196950043960280.json')
assert all(c['returncode']==0 for c in policy['commands'])
assert 'Ran 7 tests' in policy['commands'][0]['stderr'] and 'Ran 114 tests' in policy['commands'][1]['stderr']
record=dict(verdict='PASS_PRIVATE_FROZEN_D111_EXECUTION_AND_ADDITIVE_STARTUP',firmware_receipt=runpath.name,
    firmware_receipt_sha256=sha(runpath),original_oracle_sha256=freeze['sha256']['tests/tooling/imu_heading_bench_cases.cc'],
    amended_oracle_sha256=startup['amended_cases'],harness_sha256=startup['harness_sha256'],profiles=profiles,
    amended_native_profiles=extra,unsafe_static_refusals=3,registry_profiles=6,registry_checks=108,
    policy_methods=121,policy_skips=0,
    notes=['Original full suite passed before one additive startup case; removing insertion restores original bytes exactly.',
        'Native/config/special selections intentionally exclude unrelated profiles; ordinary suites execute all31 with no skips.',
        'No private state seeding or impossible counter/sequence/numeric/checkpoint-gap execution claim.',
        'No unexpected original/amended private execution failure; three separate source-verifier input mistakes retained.',
        'D109 private full-host CTest2/2 retained; existing core/HAL files unchanged and all334 old tests byte-identical except independently proved additive registry lines.'])
(OUT/'execution_review.json').write_text(json.dumps(record,indent=2)+'\n')
print(record['verdict'])
