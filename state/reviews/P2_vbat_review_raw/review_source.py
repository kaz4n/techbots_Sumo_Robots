"""Bind D110 implementation, narrow tooling changes and exact registry addition."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_vbat_raw'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text())
freeze = read(RAW / 'worker/second_source_freeze.json')
hashes = {}
for row in freeze['files']:
    path = ROOT / row['path']
    assert sha(path) == row['sha256'], path
    assert path.read_bytes() == (RAW / 'worker/second_sources' / row['path']).read_bytes()
    hashes[row['path']] = row['sha256']
previous = read(ROOT / 'state/reviews/P2_qtr_raw_review_raw/firmware_1790195019448979762.json')['source_hashes']
shared = {p: h for p, h in previous.items() if p.startswith('src/')}
changes = [p for p, h in shared.items() if sha(ROOT / p) != h]
assert changes == ['src/config.h']
before_config = ROOT / 'state/analysis/P2_qtr_raw_raw/target_sources_5c468e20/src/config.h'
addition = b'inline constexpr std::uint32_t VBAT_BENCH_SAMPLES = 128U; // D110 finite capture; count exception\n'
assert (ROOT / 'src/config.h').read_bytes().replace(addition, b'') == before_config.read_bytes()
before_registry = (RAW / 'registry/test_p0_config_before.py').read_bytes()
after_registry = (ROOT / 'tests/tooling/test_p0_config.py').read_bytes()
entry = b"    'VBAT_BENCH_SAMPLES': 128,  # D110 finite battery bench capture, approved count.\n"
assert after_registry.count(entry) == 1 and after_registry.replace(entry, b'') == before_registry
assert after_registry == (RAW / 'registry/test_p0_config_after.py').read_bytes()
assert (RAW / 'policy/frozen_test_vbat_policy.py').read_bytes() == (ROOT / 'tests/tooling/test_vbat_policy.py').read_bytes()
policy_previous = read(ROOT / 'state/reviews/P2_qtr_raw_review_raw/policy_1790194542142774429.json')['copied_hashes']
old_tests = [p for p in policy_previous if p.startswith('tests/tooling/test_') and p.endswith('_policy.py')]
old_tests += ['tests/tooling/test_app_build_overrides.py', 'tools/p0_inert_sources.json']
for path in old_tests: assert sha(ROOT / path) == policy_previous[path], path
patch = subprocess.run(['git', 'diff', '6563aaa', '--', 'tools/app_build_policy.py', 'tools/board_tool.py'],
    cwd=ROOT, capture_output=True, check=True).stdout
(OUT / 'policy_diff.patch').write_bytes(patch)
record = dict(verdict='PASS_SCOPED_SOURCE_AND_TOOLING_INSPECTION_PENDING_EXECUTION_TARGET',
    source_sha256=hashes, contract_sha256=sha(ROOT / 'state/analysis/P2_vbat_contract.md'),
    preflight_sha256=sha(ROOT / 'state/analysis/P2_vbat_test_preflight.md'),
    tool_sha256={p: sha(ROOT / p) for p in ('tools/board_tool.py', 'tools/app_build_policy.py')},
    unchanged_shared_sources=len(shared)-1, shared_change='Exact additive VBAT_BENCH_SAMPLES=128 line only',
    registry=dict(before_sha256=hashlib.sha256(before_registry).hexdigest(),
        after_sha256=hashlib.sha256(after_registry).hexdigest(), exact_added_bytes_only=True),
    unchanged_old_policy_and_upload_files={p: sha(ROOT / p) for p in old_tests},
    reviewed_observables=['float endpoints and strict zero-period compile guard',
        'passive grants and one-shot begin with ports before config',
        'known enum and shape precedence before independent clock fault',
        'S/A/C consecutive and accumulated operation/source-era chronology',
        'old source era retained through C and reanchored to new actual start only on commit',
        'local missed releases charged once before actual read',
        'sample_seen before A; early no-read preserves acceptance history',
        'tentative capture hidden until admitted C; immutable published records',
        'terminal fresh clearing only; no stop or invented shutdown',
        'only battery Reader begin/read, no A1 InputOwner',
        'saturating counters with no private state seeding'],
    limits='Reused same-model source review; independent author suites and exact targets pending. D109 private full host result retained; no redundant full host rerun without a finding. No MCU/board/network or implementation/test edits.')
(OUT / 'source_review.json').write_text(json.dumps(record, indent=2) + '\n')
print(record['verdict'])
