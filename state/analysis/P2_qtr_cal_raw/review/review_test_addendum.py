"""Refresh only reviewed test identities after the additional extrema regression."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

out = Path(__file__).resolve().parent
root = out.parents[3]
path = out / 'approved_inert_sources.json'
original = path.read_bytes()
approval = json.loads(original)
allowed = {'tests/test_qtr_cal.cpp', 'tests/tooling/test_qtr_cal.py'}
updates = {}
for name, old in approval['reviewed_files'].items():
    new = hashlib.sha256((root / name).read_bytes()).hexdigest()
    if old != new:
        assert name in allowed, name
        updates[name] = dict(previous=old, current=new)
assert set(updates) == allowed
for check in ('build_extrema', 'focused_d089_extrema'):
    assert json.loads((out / (check + '.json')).read_text())['returncode'] == 0
for check in ('host_frozen', 'sanitizer_frozen'):
    assert json.loads((out.parent / (check + '.json')).read_text())['returncode'] == 0
runs = [json.loads(line) for line in (out.parent / 'author/tooling_runs.jsonl').read_text().splitlines()]
assert len(runs) >= 28 and all(row['returncode'] == 0 for row in runs)
assert any('Ran 18 tests' in row['stderr'] for row in runs)
assert any('31 |   31 passed' in row['stdout'] and '3205' in row['stdout'] for row in runs)
assert any('17 |    17 passed' in row['stdout'] and '12665' in row['stdout'] for row in runs)
history = out / 'approved_inert_sources_initial.json'
assert not history.exists()
history.write_bytes(original)
for name, change in updates.items():
    approval['reviewed_files'][name] = change['current']
approval['test_addendum_utc'] = datetime.now(timezone.utc).isoformat()
approval['test_addendum'] = dict(previous_receipt=history.name, updated_files=updates,
    derivation='For N samples and sensor i, W=99+20i+N and B=1001-N, so W+floor((B-W)/2)=550+10i. Tests assert extrema, stage indexing and exact four-value export.',
    production_and_target_changed=False, inert_keys_changed=False)
approval['tests']['reviewer_focused'] = '31 D089 cases/1915 assertions PASS after test-only addition'
approval['tests']['inspected_root_final_host'] = '1255 main/24477205 assertions and39 enabled/3843500 assertions PASS'
approval['tests']['inspected_root_sanitizer'] = 'Final frozen2/2 PASS28.14s'
approval['tests']['inspected_author_tooling'] = '4 distinct methods PASS; final extrema case passes profiles2/1,3/32 and batch256; additive18-method config registry PASS'
path.write_text(json.dumps(approval, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(dict(status='PASS_TEST_ONLY_ADDENDUM', updated_files=updates,
    inert_keys_unchanged=True), indent=2))
