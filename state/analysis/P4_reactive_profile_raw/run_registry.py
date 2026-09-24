"""Run the unchanged registry while locating this task's receipts beside it."""
from pathlib import Path
from datetime import datetime, timezone
import contextlib
import json
import sys
import unittest

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
sys.path[:0] = [str(root), str(root/'tests/tooling')]
from tests.tooling import test_runtime_config_registry as checks
checks.RAW = out
with (out/'registry.txt').open('w') as log:
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromModule(checks))
code = 0 if result.wasSuccessful() else 1
(out/'registry.json').write_text(json.dumps({
    'argv': sys.argv, 'utc': datetime.now(timezone.utc).isoformat(),
    'returncode': code, 'tests_run': result.testsRun,
    'receipt_directory_override_only': True}, indent=2)+'\n')
print((out/'registry.txt').read_text()[-1500:])
sys.exit(code)
