"""Bind final D113 reviewer conclusions to the inspected bytes and private runs."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
RAW=Path(__file__).resolve().parent
BASE=RAW.parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
source=ROOT/'tools/dump_match.py'
assert sha(source)=='5a78257ac02733231958477ff7e139bb3a0987ce0fb893446132cc9b05853717'
test=ROOT/'tests/tooling/test_dump_connection.py'
assert sha(test)=='c864142fed553356254cdbfc97d7cdccf41eb2b4a78ed4a1cc4537292445fe44'
first=(BASE/'worker/first_dump_match.py').read_bytes()
second=source.read_bytes()
line=b'            require("SUMO_TRANSPORT" in os.environ, "MODE", "Connection-ticket modes require explicit SUMO_TRANSPORT.")\n'
assert second.count(line)==1 and second.replace(line,b'')==first
baseline=json.loads((RAW/'baseline.json').read_text())
changed=[name for name, expected in baseline['existing_test_working_sha256'].items() if sha(ROOT/name)!=expected]
assert not changed,changed
def methods(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
original_methods=methods(BASE/'author/frozen_test_dump_connection.py')
final_methods=methods(test)
assert len(original_methods)==40 and len(final_methods)==42
assert all(final_methods[n]==v for n,v in original_methods.items())
private=RAW/'private_1790200331977387435.json'
run=json.loads(private.read_text())
assert run['profiles'][0]['returncode']==0
assert json.loads(run['profiles'][0]['stdout'].splitlines()[0])==dict(tests=75,failures=0,errors=0,skips=0)
author=json.loads((BASE/'author/run4_final_summary.json').read_text())
assert author['success'] and author['tests_run']==75 and author['skipped']==0
edge=json.loads((RAW/'edge_5a78257a.json').read_text())
assert all(c['returncode']==2 and c['remote_calls']==0 for c in edge['cases'] if c['profile']=='missing-transport')
record=dict(verdict='PASS_SCOPED_D113_SOURCE_AND_CONTROLLED_TESTS',utc=datetime.now(timezone.utc).isoformat(),
    reviewer='Reused separate same-model read-only context; source body read; not human/cross-model gate',
    source_sha256=sha(source),test_sha256=sha(test),
    contract_sha256=sha(ROOT/'state/analysis/P2_dump_receiver_arm_contract.md'),
    documentation_sha256=sha(ROOT/'tools/README.md'),
    private_receipt=private.name,private_receipt_sha256=sha(private),
    original_test_methods_preserved=len(original_methods),final_new_test_methods=len(final_methods),
    prior_test_files_unchanged=len(baseline['existing_test_working_sha256']),
    private_tests=dict(methods=75,failures=0,errors=0,skips=0),
    source_fix='Exact one-line explicit SUMO_TRANSPORT check; private red then green',
    findings=[dict(id='R1',severity='MINOR',status='CLOSED',evidence=['edge_1492b81d.json','edge_5a78257a.json']),
              dict(id='E1',severity='MINOR',status='CLOSED_FIXTURE_COMPATIBILITY',evidence=['fixture_fix1_review.json','../author/run1_summary.json','../author/run2_fixture1_summary.json'])],
    preserved_failures=['../author/run1_summary.json','private_1790200264870632165.json','edge_1492b81d.json','finalizer_initial_failure.json'],
    checks=['Legacy Parser/bundle/offline definitions and original remote receiver unchanged',
            'Exact no-follow records; bounded process/fd/TCP sampling; no application sends',
            'Final query before yield; receive/parser/query failure precedence',
            'Actual board.remote SSH and ADB missing executable paths controlled without process launch',
            'Original 40 independent methods unchanged; additions and fixture correction separately frozen'],
    scope_limits=['No board/Linux receiver execution, real sockets, UART, MCU, reset, upload or service actions',
                  'TCP observation never proves router registration, clean decoder, physical acceptance or MCU permission',
                  'Concurrent D114 board_tool staging edit is outside this verdict; copied helper hashes preserved in private receipt',
                  'No full unchanged host-suite rerun required by coordinator; actual D090 C++ roundtrip executed'],
    private_helper_sha256={name:run['copied_sha256'][name] for name in ('tools/board_tool.py','tools/validate_csv_bundle.py')})
(RAW/'final_review.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k] for k in ('verdict','source_sha256','test_sha256','contract_sha256','prior_test_files_unchanged')}))
