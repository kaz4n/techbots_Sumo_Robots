"""Independently reconstruct only existing inert keys, without staging or transport."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
EXPECTED = {'bench/p0_adc','bench/p0_gpio','bench/p0_matrix','bench/p0_qtr',
            'bench/p0_timing','bench/recorder_inert','bench/ui_matrix'}
old = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
assert set(old) == EXPECTED
records = {}
shared_app = {'transaction.h','transaction.cpp','runtime.h','runtime.cpp',
              'runtime_inputs.cpp','native_sources_unoq.h','native_sources_unoq.cpp'}
for key in sorted(EXPECTED):
    bench = ROOT / key
    entries = {p.relative_to(bench).as_posix():p for p in bench.rglob('*')
               if p.is_file() and p.name != '.gitkeep'}
    for module in ('core','hal'):
        for p in (ROOT / 'src' / module).rglob('*'):
            if p.is_file(): entries[p.relative_to(ROOT).as_posix()] = p
    entries['src/config.h'] = ROOT / 'src/config.h'
    for p in (ROOT / 'src/app').rglob('*'):
        rel = p.relative_to(ROOT / 'src/app')
        if p.is_file() and rel.parts[0]!='src' and p.suffix in ('.h','.hpp','.c','.cc','.cpp'):
            entries[p.relative_to(ROOT).as_posix()] = p
    assert {k[len('src/app/'):] for k in entries if k.startswith('src/app/')} == shared_app
    assert not any(k.endswith('/app.ino') for k in entries)
    checksum = hashlib.sha256()
    files = {}
    for name,p in sorted(entries.items()):
        assert not p.is_symlink()
        data=p.read_bytes(); checksum.update(name.encode()+b'\0'); checksum.update(data)
        files[name]=hashlib.sha256(data).hexdigest()
    records[key]=dict(source_sha256=checksum.hexdigest(),files=len(files),
                      manifest_at_review=old[key],file_sha256=files)
result=dict(scope='Independent local byte reconstruction; no stage, board or new keys',
            baseline='38d71d3',entries=records)
target=Path(__file__).with_name('inert_source_reconstruction.json')
if target.exists(): raise SystemExit('Preserve prior reconstruction; use fresh explicitly named receipt')
target.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:{'sha256':v['source_sha256'],'files':v['files']} for k,v in records.items()},indent=2))
