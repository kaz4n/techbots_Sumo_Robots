"""Bind the exact reviewed D109 source, offline execution and target evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_qtr_raw_raw'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text())

source = read(OUT / 'source_review.json')
freeze = read(RAW / 'worker/first_source_freeze.json')
for path, value in source['source_sha256'].items():
    assert digest(ROOT / path) == value, path
assert digest(ROOT / 'src/config.h') == freeze['config_sha256']
assert digest(ROOT / 'state/analysis/P2_qtr_raw_contract.md') == freeze['contract_sha256']
tooling = read(OUT / 'tooling_review.json')
for path, value in tooling['tool_hashes'].items():
    assert digest(ROOT / path) == value, path
assert tooling['reviewer_run']['new_methods'] + tooling['reviewer_run']['unchanged_methods'] == 107
profiles = []
for mode, receipt in [('bench-default', '234198a7663b4c6dadb135cfdbe524e8'),
                      ('bench-immediate', '4b7b3c53a16e4b52be8bf760fb62df3e')]:
    target = read(OUT / f'target_5c468e20_{mode}.json')
    assert target['verdict'] == 'PASS_EXACT_CHECKED_QTR_TARGET_AND_CONDITIONAL_FIT'
    folder = RAW / f'target_5c468e20_{mode}_checked'
    for row in target['artifacts']:
        assert digest(folder / row['file']) == row['sha256']
    assert digest(folder / 'qtr_raw.ino.elf-zsk.bin') == target['zsk_sha256']
    profiles.append(dict(mode=mode, checked_receipt=receipt,
        directory=str(folder.relative_to(ROOT)).replace('\\', '/'),
        source_sha256=target['source_sha256'], source_files=target['source_files'],
        artifacts=target['artifacts'], zsk_sha256=target['zsk_sha256'], abi=target['abi']))
assert profiles[0]['artifacts'][0]['sha256'] == profiles[1]['artifacts'][0]['sha256']
report = OUT.parent / 'P2_qtr_raw_review.md'
assert len(report.read_text().splitlines()) <= 30
paths = [report, ROOT / 'src/config.h', ROOT / 'state/analysis/P2_qtr_raw_contract.md',
    ROOT / 'tests/tooling/qtr_raw_cases.cc', ROOT / 'tests/tooling/test_qtr_raw.py',
    ROOT / 'tests/tooling/test_qtr_raw_policy.py', ROOT / 'tests/tooling/test_p0_config.py',
    ROOT / 'tools/p0_inert_sources.json', RAW / 'worker/first_source_freeze.json',
    OUT / 'source_review.json', OUT / 'tooling_review.json', OUT / 'review_target.py',
    OUT / 'review_source.py', OUT / 'run_firmware.py', OUT / 'harness_notes.md',
    OUT / 'firmware_1790195019448979762.json', OUT / 'firmware_1790195143197198498.json',
    OUT / 'policy_1790194542142774429.json',
    OUT / 'target_5c468e20_bench-default.json', OUT / 'target_5c468e20_bench-immediate.json']
record = dict(verdict='PASS_SCOPED_SOURCE_HOST_CHECKED_TARGET_AND_CONDITIONAL_FIT',
    date='2026-09-24 Asia/Dubai', reviewer_context='Separate reused same-model context; read implementation; not a human phase gate.',
    source_sha256=source['source_sha256'], tool_sha256=tooling['tool_hashes'],
    evidence_sha256={str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in paths},
    open_blockers=[], open_majors=[],
    minor_dispositions=[dict(id='R1', category='evidence wording', status='qualified in reviewer proof and root validation; author correction requested',
        finding='Registry addition also changes preceding declaration terminator CRLF to LF; all other bytes and assertions preserved.',
        production_or_test_change_required=False, rerun_required=False)],
    tests=dict(policy_methods=107, policy_skips=0, private_host_ctest='2/2 PASS',
        cpp_profiles=source['executed_profiles'], unsafe_flag_refusals=3,
        registry_observations=90, registry_initial_missing_private_fixture='preserved; exact historical fixture copied and registry only rerun',
        authorship='Firmware executable oracles frozen before execution, authored in parallel from frozen contract/API without implementation body reads; policy tests coordinator-authored.'),
    targets=profiles,
    limits=['No board, network, upload, reset or MCU action by reviewer.',
        'Conditional pristine-pool loader model; no measured loaded free RAM or WCET.',
        'Native Reader substitutes and disabled-sketch execution are not physical GPIO evidence.',
        'Counter saturation and sequence wrap are source-reviewed rather than billion-call execution.',
        'No physical sensor/pin acceptance, motor permission, phase pass or approval of future artifacts.'])
(OUT / 'final_review.json').write_text(json.dumps(record, indent=2) + '\n')
print(record['verdict'])
print('final_review.json SHA256 ' + digest(OUT / 'final_review.json'))
