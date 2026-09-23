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
registry = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
assert set(registry) == {'bench/p0_adc', 'bench/p0_gpio', 'bench/p0_matrix', 'bench/p0_qtr', 'bench/p0_timing'}
changed = subprocess.check_output(['git', 'diff', '--name-only', 'd483268', '--', 'src', *registry], cwd=ROOT, text=True).splitlines()
assert set(changed) == {'src/config.h', 'src/hal/power.cpp', 'src/hal/power.h'}, changed
spec = importlib.util.spec_from_file_location('inert_review_board', ROOT / 'tools/board_tool.py')
board = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board)
identities, maps = {}, {}
with tempfile.TemporaryDirectory(prefix='d086-five-inert-review-') as temporary:
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
    'baseline_existing_inert': 'd483268',
    'reviewed_changed_files': changed,
    'file_maps': maps,
    'evidence': ['P2_adc_pair_review.md source review', 'prerequisite_identity.json'],
    'scope': 'Exact existing five inert registry identities only. Existing sketches and all prior startup code are unchanged. Reviewed changes add constant pin metadata and plain Reader state/methods without native global initialization. Final native tests/target review may remain pending. No new key, upload/run authorization, hardware acceptance or phase gate.'
}
(OUT / 'inert_approval.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'approved_existing_keys': identities}))
