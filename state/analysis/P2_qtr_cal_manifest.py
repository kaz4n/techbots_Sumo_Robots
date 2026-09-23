"""Adopt the six independently reviewed inert identities after byte checks."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'tools'))
import board_tool as board

manifest = root / 'tools/p0_inert_sources.json'
previous = json.loads(manifest.read_text())
review = json.loads((root / 'state/analysis/P2_qtr_cal_raw/review/approved_inert_sources.json').read_text())
approved = review['approved_sources']
assert set(approved) == set(previous) and len(approved) == 6
actual = {}
maps = {}
with tempfile.TemporaryDirectory(prefix='sumo-d089-manifest-') as temporary:
    snapshot = Path(temporary)
    for relative in ['src', *approved]:
        board.check_source(root / relative)
        shutil.copytree(root / relative, snapshot / relative)
    board.ROOT = snapshot
    for sketch in approved:
        staged = board.stage(sketch)
        actual[sketch] = board.source_hash(staged)
        maps[sketch] = {p.relative_to(staged).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in sorted(staged.rglob('*')) if p.is_file()}
assert actual == approved, 'Current sources differ from independent approval'
receipt = dict(old=previous, review_approved=approved, verified_file_maps=maps,
               scope='Six existing inert identities refreshed; no new upload key or board action')
(root / 'state/analysis/P2_qtr_cal_raw/manifest_adoption.json').write_text(
    json.dumps(receipt, indent=2) + '\n')
manifest.write_text(json.dumps(approved, indent=2) + '\n')
print(json.dumps(dict(adopted=len(approved), approved=approved)))
