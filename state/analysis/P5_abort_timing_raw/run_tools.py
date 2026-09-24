"""Run frozen D135 tooling or prior regression checks without board access."""
from pathlib import Path
from datetime import datetime, timezone
import contextlib
import hashlib
import json
import sys
import unittest

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
sys.path[:0] = [str(root), str(root / 'tests/tooling')]
group, label = sys.argv[1:]
assert group in ('admission', 'regression')
assert label.replace('_', '').isalnum()
assert not any((out / (label + ext)).exists() for ext in ('.json', '.txt'))
freeze_path = out / 'freeze.json'
for name, expected in json.loads(freeze_path.read_text()).items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
names = ['test_mode_availability', 'test_push_literal_admission',
         'test_runtime_config_registry', 'test_reactive_timing']
if group == 'regression':
    prior = root / 'state/analysis/P4_push_literal_raw/regression_retry1.json'
    names = json.loads(prior.read_text())['modules']
from tests.tooling import test_runtime_config_registry
test_runtime_config_registry.RAW = out
record = dict(group=group, label=label, modules=names,
              start_utc=datetime.now(timezone.utc).isoformat(),
              freeze_sha256=hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
              hardware_access=False)
with (out / (label + '.txt')).open('w') as log:
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        suite = unittest.defaultTestLoader.loadTestsFromNames(
            ['tests.tooling.' + name for name in names])
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
code = 0 if result.wasSuccessful() else 1
record.update(returncode=code, tests_run=result.testsRun,
              failures=len(result.failures), errors=len(result.errors),
              skipped=len(result.skipped), end_utc=datetime.now(timezone.utc).isoformat())
(out / (label + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print((out / (label + '.txt')).read_text()[-4500:])
sys.exit(code)
