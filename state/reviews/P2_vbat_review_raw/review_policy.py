"""Privately execute frozen coordinator-authored D110 policy cases and old suites."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
receipt = OUT / ('policy_' + str(time.time_ns()) + '.json')
expected = {
    'tools/board_tool.py': '870e0e42cb99b89a75d2118ba49084bb4acef4ecff8489ce951053b30d6b1084',
    'tools/app_build_policy.py': '2bc153e564d9b78a40d3ed335ffd7d44c858b2e6be3c1560f2dbf371d91a2ab8',
    'tests/tooling/test_vbat_policy.py': '7f76363e66d65d07004ea8d566fdff7c775ee11f47ee820a7e890f8e9219bbd9'}
record = dict(scope='Private WSL copy; mocked transports only; no board or network',
    authorship='New7 vbat fixtures are coordinator-authored; separate reviewer execution after source reading', commands=[])
with tempfile.TemporaryDirectory(prefix='d110-policy-review-') as temp:
    copied = Path(temp)
    for folder in ('tools', 'tests'):
        shutil.copytree(ROOT / folder, copied / folder, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    fixture = Path('state/analysis/P2_app_build_raw/default_receipt')
    shutil.copytree(ROOT / fixture, copied / fixture)
    hashes = {p.relative_to(copied).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in copied.rglob('*') if p.is_file()}
    assert all(hashes[p] == h for p, h in expected.items())
    record['copied_hashes'] = hashes
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    env = dict(os.environ, PYTHONPATH='tests/tooling', PYTHONDONTWRITEBYTECODE='1')
    for modules in (['tests.tooling.test_vbat_policy'],
                    ['tests.tooling.test_app_build_policy', 'tests.tooling.test_app_build_overrides',
                     'tests.tooling.test_runtime_inert_policy', 'tests.tooling.test_opp_view_policy',
                     'tests.tooling.test_qtr_raw_policy']):
        argv = ['python3', '-m', 'unittest', *modules, '-v']
        result = subprocess.run(argv, cwd=copied, env=env, text=True, capture_output=True, timeout=300)
        record['commands'].append(dict(argv=argv, returncode=result.returncode,
            stdout=result.stdout, stderr=result.stderr))
        receipt.write_text(json.dumps(record, indent=2) + '\n')
        print(result.stderr[-500:], flush=True)
        assert result.returncode == 0
    record['verdict'] = 'PASS_EXACT_VBAT_ROUTE_AND_UNCHANGED_EXISTING_POLICY_SUITES'
    receipt.write_text(json.dumps(record, indent=2) + '\n')
print(receipt)
