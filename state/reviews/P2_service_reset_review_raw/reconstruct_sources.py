"""Read-only D103 exact staging reconstruction; never updates upload keys."""
from pathlib import Path
import hashlib
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
BASELINE = '9a8797d'
EXPECTED = {'bench/p0_adc', 'bench/p0_gpio', 'bench/p0_matrix', 'bench/p0_qtr',
            'bench/p0_timing', 'bench/recorder_inert', 'bench/ui_matrix'}
manifest = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
assert set(manifest) == EXPECTED

def shared(name):
    return name == 'src/config.h' or name.startswith(('src/core/', 'src/hal/')) or (
        name.startswith('src/app/') and not name.startswith('src/app/src/') and
        Path(name).suffix in ('.h', '.hpp', '.c', '.cc', '.cpp'))

def digest(entries):
    result = hashlib.sha256()
    for name, data in sorted(entries.items()):
        result.update(name.encode() + b'\0'); result.update(data)
    return result.hexdigest()

def hashes(entries):
    return {name: hashlib.sha256(data).hexdigest() for name, data in sorted(entries.items())}

def staged(entries, key):
    result = {name: data for name, data in entries.items() if shared(name)}
    result.update({name[len(key) + 1:]: data for name, data in entries.items()
                   if name.startswith(key + '/') and Path(name).name != '.gitkeep'})
    assert not any(name.endswith('app.ino') for name in result)
    return result

names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE], cwd=ROOT).decode().splitlines()
baseline = {name: subprocess.check_output(['git', 'show', f'{BASELINE}:{name}'], cwd=ROOT)
            for name in names if shared(name) or any(name.startswith(k + '/') for k in EXPECTED)}
current = {p.relative_to(ROOT).as_posix(): p.read_bytes()
           for folder in ['src', *sorted(EXPECTED)] for p in (ROOT / folder).rglob('*')
           if p.is_file() and (shared(p.relative_to(ROOT).as_posix()) or folder != 'src')}
records = {}
for key in sorted(EXPECTED):
    old = staged(baseline, key); final = staged(current, key)
    assert digest(old) == manifest[key], (key, 'Allowlist changed before review')
    changes = {name: {'before': hashlib.sha256(old[name]).hexdigest() if name in old else None,
                      'after': hashlib.sha256(final[name]).hexdigest() if name in final else None}
               for name in sorted(set(old) | set(final)) if old.get(name) != final.get(name)}
    records[key] = {'source_sha256': digest(final), 'files': len(final),
                    'existing_key': manifest[key], 'file_sha256': hashes(final), 'changes': changes}
app = {name: data for name, data in current.items() if shared(name)}
app['app.ino'] = (ROOT / 'src/app/app.ino').read_bytes()
result = {'scope': 'Read-only exact seven staging maps; no staging/network/upload',
          'baseline': BASELINE, 'entries': records,
          'app': {'source_sha256': digest(app), 'files': len(app), 'file_sha256': hashes(app)}}
out = RAW / ('source_maps_' + str(time.time_ns()) + '.json')
out.write_text(json.dumps(result, indent=2) + '\n')
print(out)
print(json.dumps({'app': result['app']['source_sha256'],
                  'entries': {k: {'digest': v['source_sha256'], 'changes': list(v['changes'])}
                              for k, v in records.items()}}, indent=2))
