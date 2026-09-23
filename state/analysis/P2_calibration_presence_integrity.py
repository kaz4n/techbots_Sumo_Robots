"""Compare current source bytes with the actual D083 compile receipt, offline."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
raw = root / 'state/analysis/P2_calibration_presence_raw'
target = json.loads(Path(sys.argv[1]).read_text())
sketch = root / 'bench/p2_calibration_compile'
files = {p.relative_to(sketch).as_posix(): p.read_bytes()
         for p in sketch.rglob('*') if p.is_file()}
files['src/config.h'] = (root / 'src/config.h').read_bytes()
for module in ('core', 'hal'):
    for p in (root / 'src' / module).rglob('*'):
        if p.is_file():
            files[p.relative_to(root).as_posix()] = p.read_bytes()
hashes = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
assert hashes == target['source_files'], 'Current files differ from compiled target'
digest = hashlib.sha256()
for name in sorted(files):
    digest.update(name.encode() + b'\0')
    digest.update(files[name])
assert digest.hexdigest() == target['source_sha256'], 'Aggregate mismatch'
assert target['returncode'] == 0 and len(target['records']) == 3
assert target['native_exports']['returncode'] == 0
exports = target['native_exports']['stdout'].splitlines()
assert len(exports) == len(target['native_names']) == 36
assert all(int(line.split('=')[1].strip(), 16) != 0 for line in exports)
assert not target['math_missing']
assert target['math_exports']['returncode'] == 0
math_lines = target['math_exports']['stdout'].splitlines()
math_names = sorted(target['math_symbols'].values())
assert len(math_lines) == len(math_names) and math_names
base_functions = {}
for line in target['math_base_symbols']:
    fields = line.split()
    if len(fields) == 3 and fields[1] in ('T', 't'):
        base_functions[fields[2]] = int(fields[0], 16)
math_bindings = {}
for name, line in zip(math_names, math_lines):
    address = int(line.split('=')[1].strip(), 16)
    canonical = name.removeprefix('__llext_sym___real_')
    assert address != 0 and address & ~1 == base_functions[canonical], name
    math_bindings[name] = address
result = dict(math_bindings=math_bindings, files=len(files), source_sha256=digest.hexdigest(),
              current_matches_actual_target_map=True, native_exports=36,
              scope='Current source comparison and offline ELF receipt checks; no board action',
              elfs=[{k: r[k] for k in ('path', 'sha256', 'bytes')}
                    for r in target['records']])
(raw / 'root_target_integrity.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
