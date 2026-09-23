"""Bind D089 source review to six existing inert keys, without editing registry."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

out = Path(__file__).resolve().parent
root = out.parents[3]
staged = json.loads((out / 'staged_inert_sources.json').read_text())
target_path = out.parent / 'target_cc4819aa_bench-default.json'
target = json.loads(target_path.read_text())
assert target['returncode'] == 0 and len(target['records']) == 3
assert len(target['source_files']) == 67 and not target['math_missing']
assert len(target['native_names']) == 40 and len(target['math_aliases']) == 42
for record in target['records']:
    for key in ('undefined', 'relocations', 'sections'):
        assert record[key]['returncode'] == 0
for name, digest in target['source_files'].items():
    shared = name.startswith(('src/core/', 'src/hal/')) or name == 'src/config.h'
    local = root / (name if shared else 'bench/p2_qtr_cal_compile/' + name)
    assert hashlib.sha256(local.read_bytes()).hexdigest() == digest, str(local)
for key, files in staged['file_maps'].items():
    for name, digest in files.items():
        shared = name.startswith(('src/core/', 'src/hal/')) or name == 'src/config.h'
        local = root / (name if shared else key + '/' + name)
        assert hashlib.sha256(local.read_bytes()).hexdigest() == digest, str(local)
        if shared:
            assert target['source_files'][name] == digest
for check in ('build_durable', 'full_host', 'focused_d089', 'source_era_fixed_durable'):
    assert json.loads((out / (check + '.json')).read_text())['returncode'] == 0
unchanged = ['tests/locked', 'tools/board_tool.py', *staged['source_sha256']]
assert subprocess.check_output(['git', 'diff', staged['baseline'], '--', *unchanged], cwd=root) == b''
assert json.loads((out.parent / 'sanitizer_final.json').read_text())['returncode'] == 0
author_runs = [json.loads(line) for line in (out.parent / 'author/tooling_runs.jsonl').read_text().splitlines()]
assert len(author_runs) == 10 and all(r['returncode'] == 0 for r in author_runs)
reviewed = ['src/config.h', 'src/core/types.h', 'src/core/fsm.h', 'src/core/fsm_robot.cpp',
    'src/core/fsm_line.cpp', 'src/core/fsm_qtr_cal.cpp', 'src/hal/line_qtr_adapter.h',
    'src/hal/line_qtr_adapter.cpp', 'src/hal/qtr_cal.h', 'src/hal/qtr_cal.cpp',
    'src/hal/qtr_cal_format.cpp', 'src/hal/ui_display.h', 'src/hal/ui_display.cpp',
    'state/analysis/P2_qtr_cal_contract.md', 'tests/fixtures/qtr_cal_fixture.h',
    'tests/test_qtr_cal.cpp', 'tests/test_qtr_cal_handover.cpp',
    'tests/test_qtr_cal_motor_gate.cpp', 'tests/test_qtr_cal_display.cpp',
    'tests/tooling/test_qtr_cal.py']
record = dict(status='APPROVED_EXACT_INERT_SOURCES', baseline=staged['baseline'],
    reviewed_utc=datetime.now(timezone.utc).isoformat(),
    approved_sources=staged['source_sha256'], new_keys=[],
    target_source=target['source_sha256'], target_receipt=str(target_path.relative_to(root)),
    reviewed_files={name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in reviewed},
    exact_target_files=67, native_exports=40, aeabi_exports=42,
    tests=dict(reviewer_full_host='1254 main cases/24477190 assertions and39 enabled cases/3843500 assertions PASS',
        reviewer_focused='30 D089 cases/1900 assertions PASS',
        reviewer_reproducer='Both original era-resurrection failures now rejected',
        inspected_root_sanitizer='2/2 PASS', inspected_author_tooling='3 methods/10 subprocesses PASS'),
    scope='Source review permits updating only the existing six inert registry keys. No new key, upload, MCU action, motor permission, physical calibration, timing qualification or phase pass. Existing startup restrictions remain. p2_qtr_cal_compile stays compile-only. Full app and printing transport remain separate. Same-model fresh review; test author reused an earlier unrelated implementation context.')
destination = out / 'approved_inert_sources.json'
assert not destination.exists()
destination.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(dict(status=record['status'], approved_sources=record['approved_sources']), indent=2))
