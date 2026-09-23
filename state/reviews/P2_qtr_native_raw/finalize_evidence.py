"""Bind completed independent D085 checks and the five-key adoption to live source."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

out = Path(__file__).resolve().parent
root = out.parents[2]
run = out / 'full_review_final2'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
snapshot = json.loads((run / 'snapshot_manifest.json').read_text())
reviewed = {name: digest for name, digest in snapshot.items()
            if name.startswith(('src/', 'tests/', 'host/', 'bench/'))}
changed = [name for name, digest in reviewed.items() if sha(root / name) != digest]
assert not changed, changed
approval = json.loads((out / 'inert_approval.json').read_text())
adopted = json.loads((root / 'tools/p0_inert_sources.json').read_text())
assert adopted == approval['approved_existing_keys']
assert len(adopted) == 5
receipts = []
nonzero = []
for path in sorted((run / 'native_tooling').glob('*.json')):
    receipt = json.loads(path.read_text())
    receipts.append(dict(path=path.relative_to(out).as_posix(), sha256=sha(path)))
    if receipt.get('returncode', 0):
        nonzero.append(dict(path=path.relative_to(out).as_posix(),
                            argv=receipt['argv'], returncode=receipt['returncode']))
assert len(nonzero) == 2, nonzero
assert all(item['returncode'] == 1 and any('--test-case=*' in arg for arg in item['argv'])
           for item in nonzero)
result = dict(verified_utc=datetime.now(timezone.utc).isoformat(),
              head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
              reviewed_source_files=len(reviewed), changed_reviewed_files=changed,
              registry_sha256=sha(root / 'tools/p0_inert_sources.json'),
              adopted_existing_keys=adopted,
              native_command_receipts=receipts,
              expected_isolation_sentinel_failures=nonzero,
              scope='Offline software review; no target execution or hardware acceptance.')
(out / 'final_evidence_audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: value for key, value in result.items()
                  if key != 'native_command_receipts'}, indent=2))
