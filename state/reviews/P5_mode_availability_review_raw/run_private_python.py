"""Execute frozen D134 Python review probes with external processes forbidden."""
from pathlib import Path
from datetime import datetime, timezone
import contextlib
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
label, = sys.argv[1:]
assert label.replace('_', '').isalnum()
assert not any((HERE / (label + suffix)).exists() for suffix in ('.json', '.txt'))
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
freeze_path = HERE / 'private_freeze.json'
freeze = json.loads(freeze_path.read_text())
for name, expected in freeze['files'].items():
    assert digest(HERE / name) == expected, name
contract = ROOT / 'state/analysis/P5_mode_availability_contract.md'
assert digest(contract) == freeze['contract_sha256']
combined = ROOT / 'state/analysis/P5_mode_availability_raw/freeze.json'
combined_inputs = json.loads(combined.read_text())
board = ROOT / 'tools/board_tool.py'
assert digest(board) == combined_inputs['tools/board_tool.py']
bindings = {str(path.relative_to(ROOT)): digest(path) for path in
            (board, contract, HERE / 'private_mode_literals.py', freeze_path,
             combined, Path(__file__))}
record = dict(label=label, start_utc=datetime.now(timezone.utc).isoformat(),
              bindings=bindings, compiler_access=False, board_access=False,
              command=[sys.executable, str(Path(__file__)), label],
              python_version=sys.version, tmpdir=os.environ.get('TMPDIR'))
assert os.environ.get('TMPDIR') == '/dev/shm'

def forbidden(*args, **kwargs):
    raise AssertionError('Private Python probes must not invoke external processes or networking')

with (HERE / (label + '.txt')).open('w') as log:
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log), \
         patch.object(subprocess, 'Popen', side_effect=forbidden), \
         patch.object(os, 'system', side_effect=forbidden), \
         patch('socket.socket', side_effect=forbidden):
        spec = importlib.util.spec_from_file_location('private_mode_literals',
                                                     HERE / 'private_mode_literals.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        assert suite.countTestCases() == 8
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
code = 0 if result.wasSuccessful() else 1
record.update(returncode=code, tests_run=result.testsRun, failures=len(result.failures),
              errors=len(result.errors), skipped=len(result.skipped),
              end_utc=datetime.now(timezone.utc).isoformat(),
              inputs_unchanged=all(digest(ROOT / name) == expected
                                   for name, expected in bindings.items()))
assert record['inputs_unchanged']
(HERE / (label + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print((HERE / (label + '.txt')).read_text())
sys.exit(code)
