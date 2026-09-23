"""Run unchanged D091 host suites while keeping reviewer receipts isolated."""
import datetime
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
from tests.tooling import test_recorder_bench_runner as runner
runner.RAW = RAW
names = sys.argv[1:] or [
    'tests.tooling.test_recorder_heap',
    'tests.tooling.test_recorder_capture',
    'tests.tooling.test_recorder_upload',
    'tests.tooling.test_recorder_bench_runner',
]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
record = dict(started_utc=started, finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              modules=names, tests=result.testsRun, failures=len(result.failures),
              errors=len(result.errors), skipped=len(result.skipped), success=result.wasSuccessful())
with (RAW / 'review_runs.jsonl').open('a') as stream:
    stream.write(json.dumps(record) + '\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
