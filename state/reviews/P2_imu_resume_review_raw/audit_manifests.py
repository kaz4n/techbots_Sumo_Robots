"""Independently reconstruct board staging bytes without board access or manifest edits."""
import hashlib
import json
import sys
from pathlib import Path, PureWindowsPath

root = Path(__file__).resolve().parents[3]
raw = Path(__file__).parent
old = json.loads((root / 'tools/p0_inert_sources.json').read_text())
result = {}
for sketch, approved in old.items():
    files = {}
    folder = root / sketch
    for source in folder.rglob('*'):
        if source.is_file() and source.relative_to(folder).parts[0] != '.gitkeep':
            files[source.relative_to(folder).as_posix()] = source
    files['src/config.h'] = root / 'src/config.h'
    for module in ('core', 'hal'):
        for source in (root / 'src' / module).rglob('*'):
            if source.is_file():
                files[source.relative_to(root).as_posix()] = source
    ordered = sorted(files, key=PureWindowsPath)
    digest = hashlib.sha256()
    for name in ordered:
        digest.update(name.encode() + b'\0')
        digest.update(files[name].read_bytes())
    result[sketch] = dict(approved_before=approved, current=digest.hexdigest(), file_count=len(files),
        files={name: hashlib.sha256(files[name].read_bytes()).hexdigest() for name in ordered})
out = raw / ('independent_manifests' + (sys.argv[1] if len(sys.argv) > 1 else '') + '.json')
if out.exists():
    raise SystemExit('Preserve receipt; use a new name for another snapshot')
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: {q:v for q,v in d.items() if q != 'files'} for k,d in result.items()}, indent=2))
