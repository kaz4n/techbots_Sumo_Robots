"""Reproduce historical fixture failures using the preserved pre-D132 tool."""
from pathlib import Path
from datetime import datetime, timezone
import contextlib
import hashlib
import json
import shutil
import sys
import tempfile
import unittest

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
assert not (out / 'prior_tool_baseline.json').exists()
sys.path[:0] = [str(root), str(root / 'tests/tooling')]
from tests.tooling import test_tools, test_adb_transport, test_app_default_run

cases = [
    (test_tools.ToolContractTests, 'test_only_allowlisted_inert_sketches_upload_after_compile_without_port'),
    (test_tools.ToolContractTests, 'test_reviewed_inert_immediate_upload_uses_same_artifact_and_zero_motor_macro'),
    (test_tools.ToolContractTests, 'test_reviewed_snapshot_survives_lf_checkout'),
    (test_adb_transport.AdbTransportTests, 'test_reviewed_default_inert_upload_follows_compile_with_same_artifact'),
    (test_adb_transport.AdbTransportTests, 'test_compile_failure_prevents_reviewed_inert_upload'),
]
prior = out / 'original/tools/board_tool.py'
record = {'start_utc': datetime.now(timezone.utc).isoformat(),
          'prior_tool_sha256': hashlib.sha256(prior.read_bytes()).hexdigest(),
          'cases': [cls.__name__ + '.' + name for cls, name in cases],
          'description': 'Same current sources and approval keys, only tool reverted in isolated scratch'}
with tempfile.TemporaryDirectory(prefix='d132-prior-tool-') as temp:
    fixture = Path(temp)
    for directory in ('tools', 'src', 'bench'):
        shutil.copytree(root / directory, fixture / directory,
                        ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(prior, fixture / 'tools/board_tool.py')
    test_tools.PROJECT = fixture
    test_adb_transport.PROJECT = fixture
    with (out / 'prior_tool_baseline.txt').open('w') as log:
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            result = unittest.TextTestRunner(stream=log, verbosity=2).run(
                unittest.TestSuite(cls(name) for cls, name in cases))
            # This historical source-map guard fails before any production tool use.
            try:
                with test_app_default_run.Fixture():
                    record['app_fixture_result'] = 'unexpected success'
            except AssertionError as error:
                record['app_fixture_result'] = str(error)
                print('Historical app fixture:', error)
record.update(tests_run=result.testsRun, failures=len(result.failures),
              errors=len(result.errors), test_returncode=0 if result.wasSuccessful() else 1,
              end_utc=datetime.now(timezone.utc).isoformat(), scratch_removed=True)
(out / 'prior_tool_baseline.json').write_text(json.dumps(record, indent=2) + '\n')
print((out / 'prior_tool_baseline.txt').read_text()[-2800:])
# Retain the failed test status rather than relabel expected failures as passing.
sys.exit(record['test_returncode'])
