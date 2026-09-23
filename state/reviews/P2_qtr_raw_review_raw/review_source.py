"""Bind D109 source freeze and permitted test/registry amendments exactly."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_qtr_raw_raw'
def sha(data): return hashlib.sha256(data).hexdigest()
freeze = json.loads((RAW / 'worker/first_source_freeze.json').read_text())
for path, digest in freeze['source_sha256'].items():
    assert sha((ROOT / path).read_bytes()) == digest, path
    local = RAW / 'worker/first_sources' / path.removeprefix('bench/qtr_raw/')
    assert local.read_bytes() == (ROOT / path).read_bytes(), local
author = RAW / 'author'
before = (author / 'frozen_qtr_raw_cases.cc').read_bytes()
current = (ROOT / 'tests/tooling/qtr_raw_cases.cc').read_bytes()
changed, negative = re.subn(rb'STATIC_REQUIRE_FALSE\(([^\n]+)\);', rb'static_assert(!\1);', before)
changed, positive = re.subn(rb'STATIC_REQUIRE\(([^\n]+)\);', rb'static_assert(\1);', changed)
assert negative == 4 and positive == 1 and changed == current
assert sha(current) == '80fec60e0c9a8eb67ad853e9b082a177663363c238dbf3e00b574ae8c4a1a7ab'
assert (author / 'frozen_test_qtr_raw.py').read_bytes() == (ROOT / 'tests/tooling/test_qtr_raw.py').read_bytes()
before_registry = (author / 'test_p0_config_before.py').read_bytes()
registry = (ROOT / 'tests/tooling/test_p0_config.py').read_bytes()
entry = b"    'QTR_BENCH_FRAMES': 128,  # D109 finite raw bench capture, approved count.\n"
anchor_before = b'BEHAVIOR_EXTRA_DEFAULTS = {\r\n'
anchor_after = b'BEHAVIOR_EXTRA_DEFAULTS = {\n'
assert before_registry.count(anchor_before) == 1
assert registry.count(entry) == 1 and registry.count(anchor_after) == 1
assert registry.replace(entry, b'').replace(anchor_after, anchor_before) == before_registry
run = json.loads((OUT / 'firmware_1790195019448979762.json').read_text())
assert run['results'][0]['returncode'] == 0
assert '100% tests passed, 0 tests failed out of 2' in run['results'][0]['stdout']
assert run['results'][1]['returncode'] == 1 and 'P2_app_runtime_contract.md' in run['results'][1]['stderr']
for path, digest in freeze['source_sha256'].items(): assert run['source_hashes'][path] == digest
commands = []
for path in sorted((OUT / 'firmware_1790195019448979762_cases').glob('command_*.json')):
    row = json.loads(path.read_text()); commands.append(row)
executed = [r for r in commands if '--no-colors' in r['argv']]
assert len(executed) == 8 and all(r['returncode'] == 0 and not r['stderr'] for r in executed)
refused = [r for r in commands if '-fsyntax-only' in r['argv']]
assert len(refused) == 3 and all(r['returncode'] != 0 and 'static assertion failed' in r['stderr'] for r in refused)
registry_run = json.loads((OUT / 'firmware_1790195143197198498.json').read_text())
assert registry_run['verdict'] == 'PASS_PRIVATE_D109_REGISTRY'
assert registry_run['results'][0]['returncode'] == 0
record = dict(verdict='PASS_FROZEN_D109_SOURCE_AND_PRIVATE_HOST_CASE_EVIDENCE',
    source_sha256=freeze['source_sha256'], contract_sha256=freeze['contract_sha256'],
    test_amendment=dict(before_sha256=sha(before), after_sha256=sha(current), negative_predicates=negative, positive_predicates=positive, runtime_bytes_unchanged=True),
    registry_amendment=dict(before_sha256=sha(before_registry), after_sha256=sha(registry), only_literal_addition_and_neighbor_newline=True, neighbor_line='BEHAVIOR_EXTRA_DEFAULTS = {', neighbor_line_ending='CRLF->LF', all_other_bytes_preserved=True),
    public_observables_reviewed=['default silence and one attempt', 'first-fault and independent clock latch',
        'whole-operation and source-era half-range admission', 'actual S/A/P/Q/C and no clocks after rejection',
        'one command plus at most one needed cancellation', 'separate primary/cleanup records',
        'tentative slot hidden until accepted C', '128 immutable captures and terminal final pulse',
        'no classifier/remap/transport/other owner', 'saturating counters source reviewed without private seeding'],
    executed_profiles=[dict(argv=r['argv'], returncode=r['returncode'], summaries=[l for l in r['stdout'].splitlines() if 'test cases:' in l or 'assertions:' in l]) for r in executed],
    host_receipt='firmware_1790195019448979762.json', registry_receipt='firmware_1790195143197198498.json',
    limits='Independent authoring from contracts in separate reused context; reviewer read implementation. Native substitutes are not GPIO evidence; saturation and sequence wrap not executed.')
(OUT / 'source_review.json').write_text(json.dumps(record, indent=2) + '\n')
print(record['verdict'])
