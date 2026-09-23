"""D113 reviewer execution in an isolated local WSL copy; no real transports."""
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
stamp = str(time.time_ns())
record = {'scope': 'Read-only source review; isolated WSL tests; no board/MCU/network',
          'reviewer': 'Reused separate same-model context, production body read', 'profiles': []}
receipt = OUT / ('private_' + stamp + '.json')
expected_source = '5a78257ac02733231958477ff7e139bb3a0987ce0fb893446132cc9b05853717'
with tempfile.TemporaryDirectory(prefix='d113-review-') as temporary:
    copied = Path(temporary)
    for folder in ('src', 'tests', 'tools', 'docs'):
        shutil.copytree(ROOT / folder, copied / folder,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    hashes = {p.relative_to(copied).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in copied.rglob('*') if p.is_file()}
    assert hashes['tools/dump_match.py'] == expected_source
    assert hashes['tests/tooling/test_dump_connection.py'] == 'c864142fed553356254cdbfc97d7cdccf41eb2b4a78ed4a1cc4537292445fe44'
    record['copied_sha256'] = hashes
    original = ast.parse((OUT / 'dump_match.py.baseline').read_text())
    current = ast.parse((copied / 'tools/dump_match.py').read_text())
    def definitions(tree):
        return {node.name: ast.dump(node, include_attributes=False)
                for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    before, after = definitions(original), definitions(current)
    record['legacy_unchanged_definitions'] = [name for name in before if before[name] == after.get(name)]
    record['legacy_changed_definitions'] = [name for name in before if before[name] != after.get(name)]
    for name in ('Parser', 'Capture', 'bundle', 'offline_chunks', 'declarations', 'publish'):
        assert before[name] == after[name], name
    def literal(tree, name):
        return next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == name for t in node.targets))
    assert literal(original, 'REMOTE_RECEIVER') == literal(current, 'REMOTE_RECEIVER')
    record['legacy_receiver_literal_identical'] = True
    driver = copied / 'review_driver.py'
    driver.write_text('''import json, os, sys, unittest
from unittest import mock
from tests.tooling import test_p0_config as legacy
names = ['tests.tooling.test_dump_connection'+('' if sys.argv[1] == 'all' else '.ConnectionHostTests'),
         'tests.tooling.test_dump_match']
# D093 and D096 literal additions already approved; original test assertions remain.
extra = {'VBAT_SAMPLE_PERIOD_US':10000, 'VBAT_SAMPLE_MAX_AGE_US':20000,
         'APP_QTR_SERVICE_US':600, 'APP_SERVICE_MAX_PASSES':8192,
         'APP_CLOCK_STALL_MAX_POLLS':65536}
with mock.patch.dict(legacy.BEHAVIOR_EXTRA_DEFAULTS, extra):
    suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
print(json.dumps(dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped))))
sys.exit(not result.wasSuccessful())
''')
    mode = sys.argv[1] if len(sys.argv) > 1 else 'host'
    argv = ['python3', '-B', str(driver), mode]
    receipt.write_text(json.dumps(record, indent=2)+'\n')
    run = subprocess.run(argv, cwd=copied, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
                         text=True, capture_output=True, timeout=180)
    record['profiles'].append(dict(mode=mode, argv=argv, returncode=run.returncode,
                                   stdout=run.stdout, stderr=run.stderr))
    receipt.write_text(json.dumps(record, indent=2)+'\n')
    print(run.stdout, run.stderr[-5000:], receipt, flush=True)
    assert run.returncode == 0
