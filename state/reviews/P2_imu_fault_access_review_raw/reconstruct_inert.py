"""Reconstruct the seven previously allowed inert sketches from local bytes only."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).parent
KEYS = {'bench/p0_adc', 'bench/p0_gpio', 'bench/p0_matrix', 'bench/p0_qtr',
        'bench/p0_timing', 'bench/recorder_inert', 'bench/ui_matrix'}
APP = {'transaction.h', 'transaction.cpp', 'runtime.h', 'runtime.cpp',
       'runtime_inputs.cpp', 'native_sources_unoq.h', 'native_sources_unoq.cpp'}
approved = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
assert set(approved) == KEYS
entries = {}
for key in sorted(KEYS):
    bench = ROOT / key
    files = {p.relative_to(bench).as_posix(): p for p in bench.rglob('*')
             if p.is_file() and p.name != '.gitkeep'}
    for folder in ('core', 'hal'):
        files.update({p.relative_to(ROOT).as_posix(): p for p in (ROOT / 'src' / folder).rglob('*') if p.is_file()})
    files['src/config.h'] = ROOT / 'src/config.h'
    for p in (ROOT / 'src/app').rglob('*'):
        rel = p.relative_to(ROOT / 'src/app')
        if p.is_file() and rel.parts[0] != 'src' and p.suffix in ('.h', '.hpp', '.c', '.cc', '.cpp'):
            files[p.relative_to(ROOT).as_posix()] = p
    assert {n[8:] for n in files if n.startswith('src/app/')} == APP
    assert not any(n.endswith('/app.ino') for n in files)
    h = hashlib.sha256(); hashes = {}
    for name, p in sorted(files.items()):
        assert not p.is_symlink()
        data = p.read_bytes(); h.update(name.encode() + b'\0'); h.update(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    entries[key] = dict(source_sha256=h.hexdigest(), manifest_before=approved[key],
                        file_count=len(files), file_sha256=hashes)
receipt = dict(scope='Independent byte reconstruction only; no staging, board, manifest edit or new key', entries=entries)
out = RAW / 'inert_source_reconstruction.json'
assert not out.exists(), 'Preserve earlier reconstruction'
out.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: {n: v for n, v in r.items() if n != 'file_sha256'} for k, r in entries.items()}, indent=2))
