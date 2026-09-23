"""Independent read-only exact staged source maps; never stages or updates keys."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
EXPECTED = {'bench/p0_adc', 'bench/p0_gpio', 'bench/p0_matrix', 'bench/p0_qtr',
            'bench/p0_timing', 'bench/recorder_inert', 'bench/ui_matrix'}
manifest = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
assert set(manifest) == EXPECTED

def shared(name):
    return name == 'src/config.h' or name.startswith(('src/core/', 'src/hal/')) or (
        name.startswith('src/app/') and not name.startswith('src/app/src/') and
        Path(name).suffix in ('.h', '.hpp', '.c', '.cc', '.cpp'))

def committed(revision):
    names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', revision], cwd=ROOT).decode().splitlines()
    return {name: subprocess.check_output(['git', 'show', f'{revision}:{name}'], cwd=ROOT)
            for name in names if shared(name) or any(name.startswith(k + '/') for k in EXPECTED)}

def digest(entries):
    hashed = hashlib.sha256()
    for name, data in sorted(entries.items()):
        hashed.update(name.encode() + b'\0'); hashed.update(data)
    return hashed.hexdigest()

def hashes(entries):
    return {name: hashlib.sha256(data).hexdigest() for name, data in sorted(entries.items())}

def staged(all_files, key):
    result = {name: data for name, data in all_files.items() if shared(name)}
    result.update({name[len(key) + 1:]: data for name, data in all_files.items()
                   if name.startswith(key + '/') and Path(name).name != '.gitkeep'})
    assert not any(name.endswith('app.ino') for name in result)
    return result

original = committed('f5f8f34')
checkpoint = committed('0b1013b')
current = {p.relative_to(ROOT).as_posix(): p.read_bytes()
           for folder in ['src', *sorted(EXPECTED)] for p in (ROOT / folder).rglob('*')
           if p.is_file() and (shared(p.relative_to(ROOT).as_posix()) or folder != 'src')}
records = {}
for key in sorted(EXPECTED):
    old = staged(original, key); before = staged(checkpoint, key); final = staged(current, key)
    assert digest(old) == manifest[key], (key, 'Existing allowlist changed before review')
    names = set(old) | set(final)
    records[key] = dict(source_sha256=digest(final), files=len(final), existing_key=manifest[key],
                        file_sha256=hashes(final), changes_since_allowlist={name: dict(
                            before=hashes({name: old[name]})[name] if name in old else None,
                            after=hashes({name: final[name]})[name] if name in final else None)
                            for name in sorted(names) if old.get(name) != final.get(name)},
                        d102_changes=[name for name in sorted(set(before) | set(final))
                                      if before.get(name) != final.get(name)])
app = {name: data for name, data in current.items() if shared(name)}
app['app.ino'] = (ROOT / 'src/app/app.ino').read_bytes()
result = dict(scope='Read-only reconstruction; unchanged exact seven keys; no stage/transport/upload',
              baseline='0b1013b', existing_allowlist_baseline='f5f8f34',
              entries=records, app=dict(source_sha256=digest(app), files=len(app), file_sha256=hashes(app)))
target = RAW / 'source_maps.json'
assert not target.exists(), 'Preserve prior receipt'
target.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'app': result['app']['source_sha256'], 'entries': {
    k: {'digest': v['source_sha256'], 'changes': list(v['changes_since_allowlist']),
        'd102_changes': v['d102_changes']} for k, v in records.items()}}, indent=2))
