"""Bind actual D110 private execution summaries to unchanged frozen oracle bytes."""
import hashlib
import json
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_vbat_raw/author'
def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
freeze = read(RAW / 'freeze.json')
runpath = OUT / 'firmware_1790195790876863861.json'
run = read(runpath)
assert run['verdict'] == 'PASS_PRIVATE_UNCHANGED_D110_CASES'
assert run['results'][0]['returncode'] == 0
for path in ('tests/tooling/vbat_cases.cc', 'tests/tooling/test_vbat.py', 'src/config.h',
             'bench/vbat/src/vbat.h', 'bench/vbat/src/vbat_native.h', 'state/analysis/P2_vbat_contract.md'):
    assert sha(ROOT / path) == run['copied_hashes'][path] == freeze['sha256'][path]
assert run['copied_hashes']['bench/vbat/src/vbat.cpp'] == 'b5fa7eea988e91a9b0fdb350b34fed982cef9893bde47e56c289e07a403c0475'
commands = [read(p) for p in (OUT / (runpath.stem + '_cases')).glob('command_*.json')]
executed = [c for c in commands if '--no-colors' in c['argv']]
refused = [c for c in commands if '-fsyntax-only' in c['argv']]
assert len(executed) == 28 and len(refused) == 3
assert all(c['returncode'] == 0 and not c['stderr'] for c in executed)
assert all(c['returncode'] != 0 and 'static assertion failed' in c['stderr'] for c in refused)
assert all(c['returncode'] == 0 for c in commands if c not in refused)
profiles = []
for c in executed:
    name = Path(c['argv'][0]).name
    cases = list(map(int, re.search(r'test cases:\s+(\d+)\s+\|\s+(\d+) passed \| (\d+) failed \| (\d+) skipped', c['stdout']).groups()))
    assertions = list(map(int, re.search(r'assertions:\s+(\d+)\s+\|\s+(\d+) passed \| (\d+) failed', c['stdout']).groups()))
    assert cases[0] == cases[1] and cases[2] == 0 and assertions[0] == assertions[1] and assertions[2] == 0
    profiles.append(dict(name=name, cases=cases, assertions=assertions))
registry = [json.loads(line) for line in (OUT / (runpath.stem + '_cases') / 'registry/registry_cases.jsonl').read_text().splitlines()]
assert len(registry) == 5
assert not registry[0]['expected_failure'] and registry[0]['nested_d093_receipt']['success']
assert all(row['expected_failure'] and 'Ran 18 tests' in row['assertion'] for row in registry[1:])
old = read(ROOT / 'state/reviews/P2_qtr_raw_review_raw/firmware_1790195019448979762.json')['source_hashes']
old_tests = {p: h for p, h in old.items() if p.startswith('tests/')}
changed = [p for p, h in old_tests.items() if sha(ROOT / p) != h]
assert changed == ['tests/tooling/test_p0_config.py']
policy = read(OUT / 'policy_1790195692330086332.json')
assert all(c['returncode'] == 0 for c in policy['commands'])
assert 'Ran 7 tests' in policy['commands'][0]['stderr'] and 'Ran 107 tests' in policy['commands'][1]['stderr']
record = dict(verdict='PASS_PRIVATE_FROZEN_D110_EXECUTION', firmware_receipt=runpath.name,
    firmware_receipt_sha256=sha(runpath), oracle_sha256={p: freeze['sha256'][p] for p in ('tests/tooling/vbat_cases.cc', 'tests/tooling/test_vbat.py')},
    profiles=profiles, unsafe_static_refusals=3, registry_observations=90,
    unchanged_prior_test_files=len(old_tests)-1, sole_prior_test_delta='Exact permitted VBAT_BENCH_SAMPLES literal insertion proved in source_review.json',
    policy_methods=114, policy_skips=0, registry_profiles=5,
    notes=['Native filter executes two binding/sketch cases plus native failure case due to case-insensitive matching.',
        'Capacity/config/native filters intentional; ordinary31 includes conditional cases whose substantive checks execute in dedicated profiles.',
        'Missed-release saturation executes via five public records, normal and ASan/UBSan, without seeding private state.',
        'No firmware oracle amendments or unexpected private execution failures.',
        'D109 private full host CTest2/2 retained; exact additive unused shared constant does not trigger a redundant full host run.'])
(OUT / 'execution_review.json').write_text(json.dumps(record, indent=2) + '\n')
print(record['verdict'])
