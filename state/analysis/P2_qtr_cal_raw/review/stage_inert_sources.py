"""Stage six inert keys in a private workspace using the actual staging helper."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

out = Path(__file__).resolve().parent
root = out.parents[3]
sys.path.insert(0, str(root / 'tools'))
import board_tool as board

baseline = '4f11a1b131d0ad3179d6b564cee3f29542b02b5f'
keys = tuple(sorted(json.loads((root / 'tools/p0_inert_sources.json').read_text())))
assert keys == ('bench/p0_adc', 'bench/p0_gpio', 'bench/p0_matrix',
                'bench/p0_qtr', 'bench/p0_timing', 'bench/ui_matrix')
assert subprocess.check_output(['git', 'diff', baseline, '--', *keys,
    'tools/board_tool.py', 'tests/locked'], cwd=root) == b''
workspace = root / 'build/qtr_cal_fresh_review/staging_workspace'
assert not workspace.exists(), 'Preserve earlier private staging snapshots'
workspace.mkdir(parents=True)
shutil.copytree(root / 'src', workspace / 'src')
for key in keys:
    shutil.copytree(root / key, workspace / key)
board.ROOT = workspace
hashes, maps = {}, {}
for key in keys:
    staged = board.stage(key)
    hashes[key] = board.source_hash(staged)
    maps[key] = {}
    for path in sorted(p for p in staged.rglob('*') if p.is_file()):
        name = path.relative_to(staged).as_posix()
        shared = name.startswith(('src/core/', 'src/hal/')) or name == 'src/config.h'
        original = root / (name if shared else key + '/' + name)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == hashlib.sha256(original.read_bytes()).hexdigest(), str(original)
        maps[key][name] = digest
record = dict(status='STAGED_EXACT_SIX_KEYS', baseline=baseline,
    created_utc=datetime.now(timezone.utc).isoformat(), source_sha256=hashes,
    file_maps=maps, workspace=str(workspace),
    scope='Local private source staging only. No board access or upload authorization.')
(out / 'staged_inert_sources.json').write_text(json.dumps(record, indent=2) + '\n',
    encoding='utf-8', newline='\n')
print(json.dumps(dict(status=record['status'], source_sha256=hashes), indent=2))
