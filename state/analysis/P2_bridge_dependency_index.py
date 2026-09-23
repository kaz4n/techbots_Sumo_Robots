"""Check exact captured D098 evidence bytes in the Git index before committing."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[2]
folders = ('state/analysis/P2_bridge_dependency_raw',
           'state/reviews/P2_bridge_dependency_review_raw')
output = root / folders[0] / 'index_integrity.json'
if output.exists():
    raise SystemExit('Preserve prior index receipt')
records = []
for folder in folders:
    for path in sorted((root / folder).rglob('*')):
        if not path.is_file():
            continue
        name = path.relative_to(root).as_posix()
        current = path.read_bytes()
        staged = subprocess.run(['git', 'show', ':' + name], cwd=root,
                                check=True, capture_output=True).stdout
        if staged != current:
            raise SystemExit('Index bytes differ: ' + name)
        records.append(dict(path=name, bytes=len(current),
                            sha256=hashlib.sha256(current).hexdigest()))
output.write_text(json.dumps(dict(status='PASS_EXACT_INDEX', files=records), indent=2)+'\n')
print(json.dumps(dict(status='PASS_EXACT_INDEX', files=len(records))))
