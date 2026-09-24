# Runs frozen D136 private probes only after coordinator authorization.
# Binds the exact implementation hash, contract, private files and CSV dependency.
# No compiler, board, subprocess or network access; fixture scratch is temporary.
import contextlib
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import traceback
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def forbidden(*args, **kwargs):
    raise AssertionError('Private D136 checks prohibit external processes/networking')


def main():
    source_root, label, expected_implementation = sys.argv[1:]
    root = Path(source_root).resolve()
    assert re.fullmatch(r'[A-Za-z0-9_]{1,80}', label)
    assert re.fullmatch(r'[0-9a-f]{64}', expected_implementation)
    assert os.environ.get('TMPDIR') == '/dev/shm', 'Coordinator must select RAM scratch'
    output_json, output_log = HERE / (label + '.json'), HERE / (label + '.txt')
    assert not output_json.exists() and not output_log.exists(), 'Preserve original receipts'
    frozen_path = HERE / 'private_freeze.json'
    frozen = json.loads(frozen_path.read_text(encoding='utf-8-sig'))
    for name, expected in frozen['files'].items():
        assert sha(HERE / name) == expected, 'Private freeze changed: ' + name
    for name, expected in frozen['dependencies'].items():
        assert sha(root / name) == expected, 'Dependency changed: ' + name
    implementation = root / 'tools/analyze_opener_abort.py'
    assert sha(implementation) == expected_implementation, 'Implementation freeze mismatch'
    paths = [implementation, frozen_path, HERE / 'private_probes.py', Path(__file__)]
    paths += [root / name for name in frozen['dependencies']]
    bindings = {str(p.relative_to(root)): sha(p) for p in paths}
    record = dict(label=label, start_utc=datetime.now(timezone.utc).isoformat(),
                  command=[sys.executable, str(Path(__file__)), *sys.argv[1:]],
                  python_version=sys.version, bindings=bindings,
                  scope='Independent frozen synthetic D136 public-API probes only',
                  provenance='Separate same-model reviewer; prior P4/D134/design context reused',
                  board_access=False, compiler_access=False, observed_hardware_trials=0,
                  tests_run=0, failures=0, errors=0, skipped=0, returncode=1)
    with output_log.open('x', encoding='utf-8') as log:
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log), \
             patch.object(subprocess, 'Popen', side_effect=forbidden), \
             patch.object(os, 'system', side_effect=forbidden), \
             patch.object(socket, 'socket', side_effect=forbidden):
            try:
                spec = importlib.util.spec_from_file_location('private_d136', HERE / 'private_probes.py')
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.initialize(root)
                suite = unittest.defaultTestLoader.loadTestsFromModule(module)
                assert suite.countTestCases() == 19
                result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
                record.update(tests_run=result.testsRun, failures=len(result.failures),
                              errors=len(result.errors), skipped=len(result.skipped),
                              returncode=0 if result.wasSuccessful() and not result.skipped else 1)
            except Exception:
                traceback.print_exc()
                record['harness_exception'] = True
    record['inputs_unchanged'] = all(sha(root / name) == expected for name, expected in bindings.items())
    if not record['inputs_unchanged']:
        record['returncode'] = 1
    record['log_sha256'] = sha(output_log)
    record['end_utc'] = datetime.now(timezone.utc).isoformat()
    with output_json.open('x', encoding='utf-8') as output:
        json.dump(record, output, indent=2)
        output.write('\n')
    print(output_log.read_text(encoding='utf-8'))
    print(json.dumps({key: record[key] for key in
                      ('label', 'tests_run', 'failures', 'errors', 'skipped', 'inputs_unchanged', 'returncode')}))
    return record['returncode']


if __name__ == '__main__':
    sys.exit(main())
