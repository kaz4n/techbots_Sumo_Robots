"""Verify saved D120 results and index the bounded evidence bundle."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
root = Path(__file__).resolve().parents[4]
raw = Path(__file__).resolve().parent.parent
out = raw/'coordinator'
for name in ('normal','sanitize','sanitizer_archive','policy_repaired','app_account','bench_account'):
    record = json.loads((out/(name+'.json')).read_text())
    assert record['returncode'] == 0, name
    before, after = record['before_sha256'], record['after_sha256']
    assert all(after.get(path) == value for path,value in before.items()), name
    additions = set(after)-set(before)
    assert not additions or (name == 'policy_repaired' and additions == {
        'tests/test_stand_integration.cc', 'tests/locked/test_stand_integration_safety.cc'}), name
for name in ('app','motor_direction'):
    record = json.loads((out/(name+'_compile.json')).read_text())
    assert record['returncode'] == 0 and record['compile_only']
    assert record['argv'][-1] == '--compile-only'
    account = json.loads((out/name/'loader_account.json').read_text())
    assert account['conditional_pristine_peak_free_span'] >= 0
log = (out/'sanitize_build/LastTest.log').read_text()
for count in (1496,187,18):
    assert any('test cases:' in line and str(count) in line for line in log.splitlines())
assert log.count('0 failed | 0 skipped') == 4
rows = []
for path in sorted(p for p in raw.rglob('*') if p.is_file()):
    if path.name == 'artifact_index.json' or '__pycache__' in path.parts or path.suffix == '.pyc':
        continue
    data = path.read_bytes()
    rows.append({'path':path.relative_to(raw).as_posix(),'bytes':len(data),
                 'sha256':hashlib.sha256(data).hexdigest()})
record = {'created_utc':datetime.now(timezone.utc).isoformat(), 'files':rows,
          'count':len(rows),'bytes':sum(row['bytes'] for row in rows)}
(raw/'artifact_index.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({key:value for key,value in record.items() if key != 'files'}))
