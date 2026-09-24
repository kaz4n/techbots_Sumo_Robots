# Executes only the frozen standalone guard host tests with external calls denied.
# Temporary fixtures stay in Linux shared memory and never reach a board.
# Exclusive receipts preserve first failures, hashes and the actual unittest result.
from contextlib import ExitStack, redirect_stdout, redirect_stderr
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[4]
sys.dont_write_bytecode = True
TEST = ROOT / 'tests/tooling/test_app_default_run.py'
TOOL = ROOT / 'tools/app_default_run.py'
label = sys.argv[1]
if not label.isalnum(): raise ValueError('simple unique receipt label required')
output = Path(__file__).parent / label
output.mkdir(exist_ok=False)
receipt = dict(start_utc=datetime.now(timezone.utc).isoformat(),
    scope='SYNTHETIC_HOST_GUARD_TESTS_NO_BOARD', python=sys.version,
    test_sha256=hashlib.sha256(TEST.read_bytes()).hexdigest(),
    implementation_sha256=hashlib.sha256(TOOL.read_bytes()).hexdigest())
log = io.StringIO()
try:
    spec = importlib.util.spec_from_file_location('d118_guard_tests',TEST)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with ExitStack() as stack,redirect_stdout(log),redirect_stderr(log):
        for name in ('subprocess.run','subprocess.Popen','socket.create_connection'):
            stack.enter_context(mock.patch(name,side_effect=AssertionError('unexpected real external operation')))
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        result = unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    receipt.update(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
        skipped=len(result.skipped),successful=result.wasSuccessful())
except Exception as error:
    receipt.update(error=repr(error),successful=False)
    raise
finally:
    (output/'unittest.txt').write_text(log.getvalue())
    receipt['finish_utc']=datetime.now(timezone.utc).isoformat()
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
raise SystemExit(0 if receipt['successful'] else 1)
