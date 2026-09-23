"""Independently reconstruct old/current staged bytes without staging or board I/O."""
from pathlib import Path
import hashlib
import json
import subprocess

root = Path.cwd()
out = root / 'state/reviews/P2_power_inputs_review_raw'
baseline = '8e4544a'
def old(path):
    return subprocess.check_output(['git', 'show', baseline + ':' + path])
registry = json.loads(old('tools/p0_inert_sources.json'))
current_registry = json.loads((root / 'tools/p0_inert_sources.json').read_text())
assert set(current_registry) == set(registry) and len(registry) == 7
old_paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', baseline]).decode().splitlines()
shared = lambda p: p == 'src/config.h' or p.startswith(('src/core/', 'src/hal/'))
new_shared = {p.relative_to(root).as_posix(): p.read_bytes()
              for folder in ['src/core', 'src/hal']
              for p in (root / folder).rglob('*') if p.is_file()}
new_shared['src/config.h'] = (root / 'src/config.h').read_bytes()
old_shared = {p: old(p) for p in old_paths if shared(p)}
def digest(files):
    h = hashlib.sha256()
    for path, data in sorted(files.items()):
        h.update(path.encode() + b'\0')
        h.update(data)
    return h.hexdigest()
rows = []
candidate = {}
for key, prior_hash in registry.items():
    prefix = key + '/'
    previous = {p[len(prefix):]: old(p) for p in old_paths
                if p.startswith(prefix) and p != prefix + '.gitkeep'}
    previous.update(old_shared)
    current = {p.relative_to(root / key).as_posix(): p.read_bytes()
               for p in (root / key).rglob('*') if p.is_file()
               and p.relative_to(root / key).as_posix() != '.gitkeep'}
    current.update(new_shared)
    assert digest(previous) == prior_hash, (key, 'baseline hash mismatch')
    added = sorted(set(current) - set(previous))
    changed = sorted(p for p in set(current) & set(previous) if current[p] != previous[p])
    removed = sorted(set(previous) - set(current))
    assert added == ['src/hal/power_inputs.cpp', 'src/hal/power_inputs.h', 'src/hal/power_inputs_unoq.cpp']
    assert changed == ['src/config.h'] and not removed
    assert all(b'InputOwner' not in data and b'readerInputPort' not in data
               for p, data in current.items() if not shared(p))
    candidate[key] = digest(current)
    rows.append(dict(key=key, baseline_sha256=prior_hash, candidate_sha256=candidate[key],
                     added=added, changed=changed, removed=removed,
                     current_files={p: hashlib.sha256(data).hexdigest()
                                    for p, data in sorted(current.items())}))
result = dict(baseline=baseline, scope='Seven existing inert keys only; no registry write or upload permission',
              rows=rows)
(out / 'inert_source_review.json').write_text(json.dumps(result, indent=2) + '\n')
(out / 'inert_candidate.json').write_text(json.dumps(candidate, indent=2) + '\n')
print(json.dumps(candidate, indent=2))
