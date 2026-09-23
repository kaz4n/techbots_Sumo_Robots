"""Issue exact D088 source review approval after target and independent checks."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
output = OUT/'approved_inert_sources.json'
assert not output.exists(), 'Preserve review approval'
staged = json.loads((OUT/'staged_sources.json').read_text())
target = json.loads((OUT/'target_identity.json').read_text())
assert target['status'] == 'PASS'
for name in ('native_capture_final', 'display_frozen', 'host_final'):
    assert json.loads((OUT/(name+'.json')).read_text())['returncode'] == 0
for sketch, files in staged['file_maps'].items():
    for name, digest in files.items():
        shared = name.startswith(('src/core/', 'src/hal/')) or name == 'src/config.h'
        local = ROOT/(name if shared else sketch+'/'+name)
        assert hashlib.sha256(local.read_bytes()).hexdigest() == digest, str(local)
unchanged = ['tests/locked', 'tools/p0_capture.py', 'tools/p0_matrix_capture.py', 'tools/p0_mem_read.cfg']
assert subprocess.check_output(['git', 'diff', 'd899668', '--', *unchanged], cwd=ROOT) == b''
reviewed = [ROOT/name for name in ('tools/board_tool.py', 'tests/test_ui_display.cpp',
    'tests/tooling/test_ui_matrix_native.py', 'tests/tooling/test_ui_matrix_upload.py',
    'state/analysis/P2_matrix_runtime_capture.py', 'state/analysis/P2_matrix_contract.md',
    'state/analysis/P2_matrix_native_audit.md')]
reviewed += [p for p in (ROOT/'tests/fixtures/ui_matrix_native').rglob('*') if p.is_file()]
record = dict(status='APPROVED_EXACT_INERT_SOURCES', reviewed_at_utc=datetime.now(timezone.utc).isoformat(),
    baseline='d899668', approved_sources=staged['source_sha256'],
    new_key='bench/ui_matrix', new_key_allowed_startup='default',
    unchanged_baseline_paths=unchanged,
    reviewed_files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in reviewed},
    staged_maps_receipt='staged_sources.json', target_receipt='target_identity.json',
    tests=dict(full_normal_host='2/2 PASS; established tests unchanged',
               final_display='15 cases / 1521100 assertions PASS',
               native_and_capture='23 methods PASS; 866 native processes across normal and ASan/UBSan'),
    native_compile_source_sha256=hashlib.sha256((ROOT/'src/hal/ui_matrix_unoq.cpp').read_bytes()).hexdigest(),
    capture_wrapper_sha256=hashlib.sha256((ROOT/'state/analysis/P2_matrix_runtime_capture.py').read_bytes()).hexdigest(),
    scope='Source and actual target review approve updating only these six exact inert registry keys. bench/ui_matrix requires MATCH=0 MOTORS_ALLOWED=0 normal startup. Its setup/loop do no external sensor or motor operation. Root must pass upload-tool regression before invoking the user-authorized bare-board upload/capture. No phase gate, optical acceptance, motor permission or full-tick timing qualification. Inherited Bridge loop hook remains unqualified.')
output.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=record['status'], approved_sources=record['approved_sources']),indent=2))
