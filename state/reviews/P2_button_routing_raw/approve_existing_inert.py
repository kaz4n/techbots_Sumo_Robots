"""Record narrowly scoped approval of unchanged inert probes with reviewed sources."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
output_name = sys.argv[1] if len(sys.argv) > 1 else 'inert_approval.json'
assert output_name in ('inert_approval.json', 'inert_approval_final.json')
assert not (OUT / output_name).exists(), 'Preserve existing approval receipt'
registry = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
assert set(registry) == {'bench/p0_adc', 'bench/p0_gpio', 'bench/p0_matrix', 'bench/p0_qtr', 'bench/p0_timing'}
changed = subprocess.check_output(['git', 'diff', '--name-only', 'c10f473', '--', 'src', *registry], cwd=ROOT, text=True).splitlines()
assert set(changed) == {'src/config.h', 'src/core/countdown.cpp', 'src/core/countdown.h', 'src/core/fsm.h', 'src/core/fsm_robot.cpp', 'src/core/logframe.cpp', 'src/core/logframe.h', 'src/core/types.h', 'src/hal/ui.h'}, changed
spec = importlib.util.spec_from_file_location('inert_review_board', ROOT / 'tools/board_tool.py')
board = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board)
identities, maps = {}, {}
with tempfile.TemporaryDirectory(prefix='d087-five-inert-review-') as temporary:
    stage = Path(temporary)
    shutil.copytree(ROOT / 'src', stage / 'src')
    for name in registry:
        shutil.copytree(ROOT / name, stage / name)
    board.ROOT = stage
    for name in sorted(registry):
        folder = board.stage(name)
        identities[name] = board.source_hash(folder)
        maps[name] = {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(folder.rglob('*')) if p.is_file()}
        for relative, digest in maps[name].items():
            current = ROOT / (relative if relative.startswith(('src/core/', 'src/hal/')) or relative == 'src/config.h'
                              else name + '/' + relative)
            assert hashlib.sha256(current.read_bytes()).hexdigest() == digest
record = {
    'status': 'APPROVED_EXISTING_FIVE_KEYS_ONLY',
    'approved_existing_keys': identities,
    'baseline_existing_inert': 'c10f473',
    'reviewed_changed_files': changed + ['src/core/fsm_buttons.cpp', 'src/hal/ui.cpp'],
    'file_maps': maps,
    'evidence': ['P2_button_routing_review.md source review', 'target_identity_audit.json'],
    'scope': 'Exact existing five inert registry identities only. Existing sketches and all prior startup code are unchanged. Reviewed changes add constant unconfigured button metadata, pure decoder, admission state and dual-clock method bodies without native global initialization. Final native tests/target review may remain pending. No new key, upload/run authorization, hardware acceptance or phase gate.'
}
if output_name == 'inert_approval_final.json':
    initial = json.loads((OUT / 'target_identity_audit.json').read_text())
    path = ROOT / 'src/core/logframe.h'
    current = path.read_bytes()
    assert b'\r' not in current
    before = initial['source_files']['src/core/logframe.h']
    assert hashlib.sha256(current.replace(b'\n', b'\r\n')).hexdigest() == before
    current_map = maps['bench/p0_adc']
    changed = [name for name, digest in initial['source_files'].items()
               if name.startswith(('src/core/', 'src/hal/')) or name == 'src/config.h'
               if current_map[name] != digest]
    assert changed == ['src/core/logframe.h'], changed
    record['normalization_only'] = {'file': 'src/core/logframe.h', 'before_sha256': before,
                                   'after_sha256': hashlib.sha256(current).hexdigest(),
                                   'old_bytes_reconstructed_exactly_from_LF_by_CRLF': True,
                                   'other_production_files_unchanged': True}
(OUT / output_name).write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'approved_existing_keys': identities}))

