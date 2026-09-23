"""Compare current source bytes with the actual D081 compile receipt, offline."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
raw = root / 'state/analysis/P2_imu_acquisition_raw'
target = json.loads((raw / 'target_147e08b1_bench-default.json').read_text())
sketch = root / 'bench/p2_imu_acquisition_compile'
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
result = dict(files=len(files), source_sha256=digest.hexdigest(),
              current_matches_actual_target_map=True, native_exports=36,
              scope='Current source comparison and offline ELF receipt checks; no board action',
              elfs=[{k: r[k] for k in ('path', 'sha256', 'bytes')}
                    for r in target['records']])
(raw / 'root_target_integrity.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
