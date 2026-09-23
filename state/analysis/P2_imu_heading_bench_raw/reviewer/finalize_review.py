"""Bind final bounded D111 verdict to inspected exact evidence and current frozen inputs."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
RAW=OUT.parent
def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
source=read(OUT/'source_review.json')
policy=read(OUT/'policy_source_review.json')
execution=read(OUT/'execution_review.json')
startup=read(OUT/'startup_review.json')
targets=[read(OUT/('target_9520e473_'+mode+'.json')) for mode in ('bench-default','bench-immediate')]
assert all(t['verdict']=='PASS_EXACT_CHECKED_IMU_HEADING_TARGET_AND_CONDITIONAL_FIT' for t in targets)
assert execution['verdict']=='PASS_PRIVATE_FROZEN_D111_EXECUTION_AND_ADDITIVE_STARTUP'
for path,expected in {**source['hashes'],**policy['hashes']}.items(): assert sha(ROOT/path)==expected,path
manifest=read(RAW/'target_sources_9520e473/manifest.json')
for path,expected in manifest['source_files'].items():
    current=ROOT/path if (ROOT/path).is_file() and path.startswith('src/') else ROOT/'bench/imu_heading'/path
    assert sha(current)==expected,path
oracle={'tests/tooling/imu_heading_bench_cases.cc':startup['amended_cases'],
        'tests/tooling/test_imu_heading_bench.py':startup['harness_sha256']}
for path,expected in oracle.items(): assert sha(ROOT/path)==expected,path
evidence=[ROOT/'state/reviews/P2_imu_heading_bench_review.md',ROOT/'state/analysis/P2_imu_heading_bench_contract.md',
    ROOT/'tests/tooling/test_p0_config.py',ROOT/'tools/p0_inert_sources.json',
    ROOT/'state/reviews/P2_qtr_raw_review_raw/firmware_1790195019448979762.json',
    RAW/'worker/first_source_freeze.json',RAW/'author/freeze.json',RAW/'author/coverage.md',
    RAW/'author/run1_summary.json',RAW/'author/startup_amendment.json',RAW/'author/startup_summary.json',
    RAW/'author/startup_source_identity.json',RAW/'author/validation.md']
evidence += [p for p in OUT.rglob('*') if p.is_file() and p.name not in ('final_review.json',) and '__pycache__' not in p.parts]
record=dict(verdict='PASS_SCOPED_SOURCE_TESTS_TOOLING_CHECKED_TARGET_AND_CONDITIONAL_FIT',date='2026-09-24 Asia/Dubai',
    reviewer_context='Reused same-model separate safety reviewer; read implementation. Not a human phase gate.',
    open_blockers=[],open_majors=[],open_minors=[],source_sha256=source['hashes'],
    staged_source_sha256=targets[0]['source_sha256'],tool_sha256=policy['hashes'],oracle_sha256=oracle,
    original_oracle_sha256=execution['original_oracle_sha256'],
    evidence_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in evidence},tests=execution,
    targets=targets,independence='Firmware test author used separate reused context without production body reads; policy cases coordinator-authored before red; reviewer source-informed execution in private WSL.',
    retained_host_evidence='D109 private tools/test_host.sh CTest2/2; exact protected HAL/core and prior tests remain unchanged, new shared config values are unused by existing code.',
    limitations=['No board/network/MCU operation or upload approval.','Conditional pristine-loader model, not actual load or free RAM.',
        'No physical bus/mounting/stillness/clock/drift/rotation or deployed capture provenance.','No whole-app WCET or human phase gate.',
        'Unreachable counter/sequence/numeric/checkpoint-gap defenses reviewed in source; no private seeding.'])
(OUT/'final_review.json').write_text(json.dumps(record,indent=2)+'\n')
print(record['verdict']);print(sha(OUT/'final_review.json'))
