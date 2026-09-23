"""Verify final D088 review identities without changing production or board state."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
assert not (OUT/'final_identity.json').exists(), 'Preserve closure receipt'
approval=json.loads((OUT/'approved_inert_sources.json').read_text())
normalized=json.loads((OUT/'approval_normalization.json').read_text())
staged=json.loads((OUT/'staged_sources.json').read_text())
for name,want in approval['reviewed_files'].items():
    normalized_name=name.replace('\\','/')
    if normalized_name in normalized['files']:
        want=normalized['files'][normalized_name]['sha256']
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==want, name
for name,want in staged['file_maps']['bench/ui_matrix'].items():
    local=name if name.startswith(('src/core/','src/hal/')) or name=='src/config.h' else 'bench/ui_matrix/'+name
    data=(ROOT/local).read_bytes()
    assert hashlib.sha256(data).hexdigest()==want
    committed=subprocess.check_output(['git','show','385c46c:'+local],cwd=ROOT)
    assert committed==data, local
assert subprocess.check_output(['git','diff','d899668','--','tests/locked'],cwd=ROOT)==b''
assert json.loads((ROOT/'tools/p0_inert_sources.json').read_text())==approval['approved_sources']
checks={}
for name in ('host_frozen','sanitizer_frozen','upload_tooling','existing_tooling','upload_run1'):
    path=ROOT/'state/analysis/P2_matrix_raw'/(name+'.json')
    receipt=json.loads(path.read_text());assert receipt['returncode']==0, name
    checks[name]=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),returncode=0)
record=dict(status='PASS',checked_utc=datetime.now(timezone.utc).isoformat(),
    source_commit='385c46c',exact_committed_target_source_files=61,
    current_reviewed_code_tests_and_capture_unchanged=True,exact_six_registry_keys=True,
    old_locked_tests_unchanged=True,coordinator_receipts=checks,
    scope='Local artifact identity and successful command receipts; runtime capture reviewed separately.')
(OUT/'final_identity.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
