"""Verify the frozen D124 source/oracle and pre-task locked-test bytes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P3_turn_trial_raw'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
freeze = json.loads((RAW / 'freeze.json').read_text())
prior = json.loads((RAW / 'prior_locked.json').read_text())
frozen = {p: sha(ROOT / p) == expected for p, expected in freeze['sha256'].items()}
locked = {p: sha(ROOT / p) == expected for p, expected in prior.items()}
copy_matches = sha(RAW / 'test_turn_trial.cpp') == sha(ROOT / 'tests/test_turn_trial.cpp')
reports = {}
for name in ('normal', 'sanitize', 'registry', 'regression'):
    path = RAW / (name + '.json')
    if path.exists():
        result = json.loads(path.read_text())
        reports[name] = dict(sha256=sha(path), returncode=result['returncode'],
                             commands_pass=all(x['returncode'] == 0 for x in result['commands']))
record = dict(checked_utc=datetime.now(timezone.utc).isoformat(), frozen=frozen,
              locked=locked, archived_oracle_matches=copy_matches, receipts=reports)
record['result'] = 'PASS' if all(frozen.values()) and all(locked.values()) and copy_matches and \
    len(reports) == 4 and all(r['returncode'] == 0 and r['commands_pass'] for r in reports.values()) else 'FAIL'
(OUT / 'evidence_bindings.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record))
raise SystemExit(0 if record['result'] == 'PASS' else 1)
