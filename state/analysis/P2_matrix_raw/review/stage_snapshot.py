"""Independently reproduce the six narrowly reviewed inert staged source maps."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
names = ['bench/p0_adc', 'bench/p0_gpio', 'bench/p0_matrix', 'bench/p0_qtr',
         'bench/p0_timing', 'bench/ui_matrix']
assert not (OUT / 'staged_sources.json').exists(), 'Preserve old receipt'
assert subprocess.check_output(['git', 'diff', 'd899668', '--', *names[:5]], cwd=ROOT) == b''
scratch = OUT / 'staging'
assert not scratch.exists(), 'Fresh isolated destination required'
scratch.mkdir()
shutil.copytree(ROOT / 'src', scratch / 'src')
for name in names:
    shutil.copytree(ROOT / name, scratch / name)
spec = importlib.util.spec_from_file_location('review_board_tool', ROOT / 'tools/board_tool.py')
board = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board)
board.ROOT = scratch
identities, maps = {}, {}
for name in names:
    folder = board.stage(name)
    identities[name] = board.source_hash(folder)
    maps[name] = {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(folder.rglob('*')) if p.is_file()}
    for relative, digest in maps[name].items():
        current = ROOT / (relative if relative.startswith(('src/core/', 'src/hal/')) or
                          relative == 'src/config.h' else name + '/' + relative)
        assert hashlib.sha256(current.read_bytes()).hexdigest() == digest, relative
record = dict(baseline='d899668', existing_five_sketches_unchanged=True,
              source_sha256=identities, file_maps=maps,
              scope='Independent local isolated staging only. Not an upload approval until final reviewer assessment.')
(OUT / 'staged_sources.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(json.dumps(identities, indent=2))
