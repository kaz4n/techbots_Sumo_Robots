"""Diagnose only observed filesystem calls of the first frozen independent fixture."""
import json
from pathlib import Path
import sys
import tempfile
from unittest import mock

raw = Path(__file__).resolve().parent
stage = Path(json.loads((raw/'run1_source_copy.json').read_text())['stage'])
sys.path.insert(0, str(stage))
from tests.tooling.test_dump_connection import ConnectionRemoteTests

reports = []
for observer in (False, True):
    case = ConnectionRemoteTests('test_actual_receiver_order_records_exact_bytes_and_zero_sends')
    case.setUp()
    if observer:
        case.box.install_records()
    command = case.command(observer=observer)
    original = case.box.mapped
    calls = []
    def traced(path):
        try:
            result = original(path)
            calls.append({'path':str(path),'mapped':str(result)})
            return result
        except Exception as error:
            calls.append({'path':str(path),'error':repr(error)})
            raise
    case.box.mapped = traced
    result = None
    error = None
    with mock.patch('traceback.print_exc', lambda: sys.stderr.write(repr(sys.exception()))):
        try:
            result = case.box.execute(command)
        except Exception as caught:
            error = repr(caught)
    reports.append({'observer':observer,'calls':calls,'error':error,
                    'returncode':result.returncode if result else None,
                    'stdout':result.stdout if result else None,
                    'stderr':result.stderr if result else None,
                    'files':[str(path.relative_to(case.box.root)) for path in case.box.root.rglob('*')],
                    'events':case.box.events})
    case.doCleanups()
(raw/'fixture_diagnosis.json').write_text(json.dumps(reports,indent=2)+'\n')
print(json.dumps(reports,indent=2))
