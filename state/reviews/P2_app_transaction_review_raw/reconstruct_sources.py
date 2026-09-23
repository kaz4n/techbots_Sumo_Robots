"""Independently reconstruct existing seven inert source trees without staging."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
EXPECTED = {'bench/p0_adc', 'bench/p0_gpio', 'bench/p0_matrix', 'bench/p0_qtr',
            'bench/p0_timing', 'bench/recorder_inert', 'bench/ui_matrix'}
old = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
assert set(old) == EXPECTED, 'No allowlist key may be added/removed'
records = {}
for key in sorted(EXPECTED):
    bench = ROOT / key
    entries = {}
    for path in bench.rglob('*'):
        if path.is_file() and path.name != '.gitkeep':
            entries[path.relative_to(bench).as_posix()] = path
    for module in ('core', 'hal'):
        for path in (ROOT / 'src' / module).rglob('*'):
            if path.is_file():
                entries[path.relative_to(ROOT).as_posix()] = path
    entries['src/config.h'] = ROOT / 'src/config.h'
    for path in (ROOT / 'src/app').rglob('*'):
        relative = path.relative_to(ROOT / 'src/app')
        if (path.is_file() and relative.parts[0] != 'src' and
            path.suffix in ('.h', '.hpp', '.c', '.cc', '.cpp')):
            entries[path.relative_to(ROOT).as_posix()] = path
    assert set(name for name in entries if name.startswith('src/app/')) == {
        'src/app/transaction.h', 'src/app/transaction.cpp'}
    digest = hashlib.sha256()
    per_file = {}
    for name, path in sorted(entries.items()):
        data = path.read_bytes()
        digest.update(name.encode() + b'\0')
        digest.update(data)
        per_file[name] = hashlib.sha256(data).hexdigest()
    records[key] = dict(source_sha256=digest.hexdigest(), files=len(per_file),
                        manifest_at_review=old[key], file_sha256=per_file)
target = Path(__file__).with_name('inert_source_reconstruction.json')
target.write_text(json.dumps(dict(scope='Local byte reconstruction only; no stage or board action',
                                  entries=records), indent=2) + '\n')
print(json.dumps({k: {'sha256': v['source_sha256'], 'files': v['files']} for k,v in records.items()}, indent=2))
