"""Bind final D110 scoped approval to exact source, test, policy and target bytes."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_vbat_raw'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text())
source = read(OUT / 'source_review.json')
execution = read(OUT / 'execution_review.json')
assert execution['verdict'] == 'PASS_PRIVATE_FROZEN_D110_EXECUTION'
for path, expected in {**source['source_sha256'], **source['tool_sha256'], **execution['oracle_sha256']}.items():
    assert digest(ROOT / path) == expected, path
assert digest(ROOT / 'state/analysis/P2_vbat_contract.md') == source['contract_sha256']
profiles = []
for mode, receipt in [('bench-default', 'f89f7f7cae7e4a37b98b50d45c1e0968'),
                      ('bench-immediate', '9a49eb8337304454b61e59f4c6363a6f')]:
    target = read(OUT / f'target_8e3efb92_{mode}.json')
    assert target['verdict'] == 'PASS_EXACT_CHECKED_VBAT_TARGET_AND_CONDITIONAL_FIT'
    folder = RAW / f'target_8e3efb92_{mode}_checked'
    for row in target['artifacts']:
        assert digest(folder / row['file']) == row['sha256']
    assert digest(folder / 'vbat.ino.elf-zsk.bin') == target['zsk_sha256']
    profiles.append(dict(mode=mode, checked_receipt=receipt,
        directory=folder.relative_to(ROOT).as_posix(), source_sha256=target['source_sha256'],
        source_files=target['source_files'], artifacts=target['artifacts'],
        zsk_sha256=target['zsk_sha256'], abi=target['abi']))
assert profiles[0]['artifacts'][0]['sha256'] == profiles[1]['artifacts'][0]['sha256']
report = OUT.parent / 'P2_vbat_review.md'
assert len(report.read_text().splitlines()) <= 30
paths = [report, ROOT / 'state/analysis/P2_vbat_contract.md', ROOT / 'state/analysis/P2_vbat_test_preflight.md',
    ROOT / 'tests/tooling/test_vbat_policy.py', ROOT / 'tests/tooling/test_p0_config.py',
    ROOT / 'tools/p0_inert_sources.json', RAW / 'worker/second_source_freeze.json',
    RAW / 'author/freeze.json', RAW / 'author/run1_summary.json', RAW / 'author/coverage.md', RAW / 'author/validation.md',
    OUT / 'source_review.json', OUT / 'execution_review.json', OUT / 'harness_notes.md',
    OUT / 'review_source.py', OUT / 'review_execution.py', OUT / 'review_target.py', OUT / 'review_policy.py', OUT / 'run_firmware.py',
    OUT / 'firmware_1790195790876863861.json', OUT / 'policy_1790195692330086332.json',
    OUT / 'target_8e3efb92_bench-default.json', OUT / 'target_8e3efb92_bench-immediate.json',
    OUT / 'target_8e3efb92_bench-default_witness.txt', OUT / 'target_8e3efb92_bench-immediate_witness.txt']
record = dict(verdict='PASS_SCOPED_SOURCE_TESTS_TOOLING_CHECKED_TARGET_AND_CONDITIONAL_FIT',
    date='2026-09-24 Asia/Dubai', reviewer_context='Reused same-model separate safety reviewer; read implementation. Not a human phase gate.',
    open_blockers=[], open_majors=[], open_minors=[], source_sha256=source['source_sha256'],
    tool_sha256=source['tool_sha256'], oracle_sha256=execution['oracle_sha256'],
    evidence_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
    tests=execution, targets=profiles,
    independence='Firmware author and implementer wrote in parallel from adopted contract/API; executable expectations froze before first execution, no implementation bodies read by author. New policy fixtures coordinator-authored, separately read and executed by reviewer.',
    retained_host_evidence='D109 private full host CTest2/2; exact shared source delta is one unused count literal,331 prior test files unchanged, remaining prior test only authorized literal addition. No redundant full host rerun.',
    limits=['No reviewer board/network/upload/reset/MCU action.',
        'Only frozen bytes approved; no future artifact or upload authorization.',
        'Native substitutions and passive sketch tests are not ADC readout or physical acceptance.',
        'Conditional pristine262144-byte pool model, no observed loaded RAM or native/app WCET.',
        'Missed counter saturation executed through public records; other impractical saturation branches source reviewed.',
        'No ADC shutdown synthesized; boot-lifetime native ownership persists.',
        'No0.05V accuracy, wiring permission, motor permission or human phase gate.'])
(OUT / 'final_review.json').write_text(json.dumps(record, indent=2) + '\n')
print(record['verdict'])
print(digest(OUT / 'final_review.json'))
