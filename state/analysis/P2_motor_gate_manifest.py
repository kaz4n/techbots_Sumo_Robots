"""Reproduce reviewed additions-only inert source maps without board operations."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / 'tools'))
import board_tool as board

previous = json.loads((repo / 'state/analysis/P2_csv_inert_manifest_proposal.json').read_text())
proposal = {}
with tempfile.TemporaryDirectory(prefix='sumo-d075-manifest-', dir='/dev/shm') as folder:
    snapshot = Path(folder)
    for relative in ['src', *previous]:
        board.check_source(repo / relative)
        shutil.copytree(repo / relative, snapshot / relative)
    board.ROOT = snapshot
    for sketch, old in previous.items():
        staged = board.stage(sketch)
        files = {p.relative_to(staged).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(staged.rglob('*')) if p.is_file()}
        assert set(files) - set(old['files']) == {'src/hal/motors.h', 'src/hal/motors.cpp'}
        assert all(files.get(name) == value for name, value in old['files'].items())
        proposal[sketch] = dict(old=old['new'], new=board.source_hash(staged), files=files)
path = repo / 'state/analysis/P2_motor_gate_inert_manifest_proposal.json'
path.write_text(json.dumps(proposal, indent=2) + '\n', encoding='utf-8')
print(json.dumps({name: item['new'] for name, item in proposal.items()}, indent=2))
