"""Run frozen D136 public or existing CSV/D130 regression tests, retaining results.
Synthetic temporary inputs use RAM scratch; no board operation is requested.
First source and test hashes are recorded before execution and checked afterward.
"""
from pathlib import Path
from datetime import datetime, timezone
import contextlib
import hashlib
import json
import sys
import unittest

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
group, label, expected_source = sys.argv[1:]
assert group in ('public', 'regression') and label.replace('_', '').isalnum()
assert not any((out / (label + ext)).exists() for ext in ('.json', '.txt'))
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
source = root / 'tools/analyze_opener_abort.py'
assert digest(source) == expected_source
old = json.loads((out / 'initial_inputs.json').read_text())
assert all(digest(root / name) == value for name, value in old.items())
public = json.loads((root / 'state/analysis/P5_abort_analysis_public/public_freeze.json').read_text())
for name, sha in public['files'].items():
    if name.endswith('.py'):
        assert digest(root / 'tests/tooling' / name) == sha
modules = ['test_opener_abort_wire', 'test_opener_abort_source',
           'test_opener_abort_cohort', 'test_opener_abort_binding']
if group == 'regression':
    modules = ['test_target_loss_analysis', 'test_countdown_analysis', 'test_csv_bundle']
sys.path[:0] = [str(root), str(root / 'tests/tooling')]
record = dict(group=group, label=label, modules=modules,
              start_utc=datetime.now(timezone.utc).isoformat(),
              implementation_sha256=expected_source, hardware_access=False,
              runner_sha256=digest(Path(__file__)))
with (out / (label + '.txt')).open('x') as log:
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
code = 0 if result.wasSuccessful() and not result.skipped else 1
record.update(returncode=code, tests_run=result.testsRun, failures=len(result.failures),
              errors=len(result.errors), skipped=len(result.skipped),
              end_utc=datetime.now(timezone.utc).isoformat())
assert digest(source) == expected_source
assert all(digest(root / name) == value for name, value in old.items())
record['prior_inputs_unchanged'] = True
record['log_sha256'] = digest(out / (label + '.txt'))
(out / (label + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print((out / (label + '.txt')).read_text()[-5000:])
sys.exit(code)
