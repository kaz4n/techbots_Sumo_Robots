"""Independently compare D086 target receipt against local bytes and five inert maps."""
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
target_path = Path(sys.argv[1]).resolve()
target = json.loads(target_path.read_text())
hash_file = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = {}
for file in (ROOT / 'bench/p2_adc_pair_compile').rglob('*'):
    if file.is_file():
        files[file.relative_to(ROOT / 'bench/p2_adc_pair_compile').as_posix()] = file.read_bytes()
for name in ('core', 'hal'):
    for file in (ROOT / 'src' / name).rglob('*'):
        if file.is_file():
            files[file.relative_to(ROOT).as_posix()] = file.read_bytes()
files['src/config.h'] = (ROOT / 'src/config.h').read_bytes()
expected_map = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
assert expected_map == target['source_files'], 'Target source map differs'
aggregate = hashlib.sha256()
for name, data in sorted(files.items()):
    aggregate.update(name.encode() + b'\0' + data)
assert aggregate.hexdigest() == target['source_sha256']
assert target['returncode'] == 0 and len(target['records']) == 3
for record in target['records']:
    assert record['bytes'] > 0 and len(record['sha256']) == 64
    for name in ('undefined', 'relocations', 'sections'):
        assert record[name]['returncode'] == 0
    if 'disassembly' in record:
        (OUT / 'target_disassembly.txt').write_text(record['disassembly'])
        (OUT / 'target_symbols.txt').write_text(record['nm_all']['stdout'])
        (OUT / 'target_init_array.txt').write_text(record['init_array']['stdout'])
exports = target['native_exports']
assert exports['returncode'] == 0
lines = exports['stdout'].splitlines()
assert len(lines) == len(target['native_names'])
assert all(int(line.split('=')[1], 16) != 0 for line in lines)
assert not target['math_missing']
if target['math_exports']:
    math = target['math_exports']
    assert math['returncode'] == 0
    assert len(math['stdout'].splitlines()) == len(target['math_symbols'])
    assert all(int(line.split('=')[1], 16) != 0 for line in math['stdout'].splitlines())
    base_functions = {}
    for line in target['math_base_symbols']:
        fields = line.split()
        if len(fields) == 3 and fields[1] in ('T', 't'):
            base_functions[fields[2]] = int(fields[0], 16)
    for name, line in zip(sorted(target['math_symbols'].values()), math['stdout'].splitlines()):
        canonical = name.removeprefix('__llext_sym___real_')
        assert int(line.split('=')[1], 16) & ~1 == base_functions[canonical]

spec = importlib.util.spec_from_file_location('review_board_tool', ROOT / 'tools/board_tool.py')
board = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board)
registry = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
required = {'bench/p0_adc', 'bench/p0_gpio', 'bench/p0_matrix', 'bench/p0_qtr', 'bench/p0_timing'}
assert set(registry) == required
identities, maps = {}, {}
with tempfile.TemporaryDirectory(prefix='d086-five-inert-') as temporary:
    frozen = Path(temporary)
    shutil.copytree(ROOT / 'src', frozen / 'src')
    for name in sorted(required):
        shutil.copytree(ROOT / name, frozen / name)
    board.ROOT = frozen
    for name in sorted(required):
        staged = board.stage(name)
        identities[name] = board.source_hash(staged)
        maps[name] = {file.relative_to(staged).as_posix(): hash_file(file)
                      for file in sorted(staged.rglob('*')) if file.is_file()}

unchanged = subprocess.check_output(['git', 'diff', '--name-only', 'd483268', '--', 'tests/locked'], cwd=ROOT, text=True)
assert not unchanged.strip(), 'Established locked files changed'
record = {'scope': 'Offline source/hash/ELF receipt comparison; no board access',
          'target_receipt': str(target_path.relative_to(ROOT)),
          'target_receipt_sha256': hash_file(target_path),
          'source_sha256': aggregate.hexdigest(), 'source_files': expected_map,
          'native_exports': len(lines), 'math_exports': len(target['math_symbols']),
          'elfs': [{k: r[k] for k in ('path', 'sha256', 'bytes')} for r in target['records']],
          'existing_five_candidate_identities': identities, 'existing_five_maps': maps,
          'locked_unchanged_from': 'd483268'}
(OUT / 'target_identity_audit.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'source': aggregate.hexdigest(), 'files': len(files), 'inert': identities}))
