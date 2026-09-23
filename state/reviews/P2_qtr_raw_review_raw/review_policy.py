"""Run unchanged root-authored QTR policy cases and old suites privately."""
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
expected = {'tools/board_tool.py': 'c3dc2e31e447165c4e83c65913b534a0649f4f51114a2998b68c5986579aa5d7',
            'tools/app_build_policy.py': '218cad95f4d443e7af68893c0f63b57120da888fc73ac6f0f03cea1b1bd51343',
            'tests/tooling/test_qtr_raw_policy.py': '062c0c03f29df6ddb8bfeeee7b1808f633b648db790109e094674940a73692a7'}
record = dict(scope='Private WSL copy; mocked transports only; no board or network',
              authorship='New7 QTR fixtures are coordinator-authored; this is separate reviewer execution',
              commands=[])
with tempfile.TemporaryDirectory(prefix='d109-policy-review-') as temp:
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
    for modules in (['tests.tooling.test_qtr_raw_policy'],
                    ['tests.tooling.test_app_build_policy', 'tests.tooling.test_app_build_overrides',
                     'tests.tooling.test_runtime_inert_policy', 'tests.tooling.test_opp_view_policy']):
        argv = ['python3', '-m', 'unittest', *modules, '-v']
        result = subprocess.run(argv, cwd=copied, env=env, text=True, capture_output=True, timeout=300)
        record['commands'].append(dict(argv=argv, returncode=result.returncode,
                                       stdout=result.stdout, stderr=result.stderr))
        receipt.write_text(json.dumps(record, indent=2) + '\n')
        print(result.stderr[-1000:], flush=True)
        assert result.returncode == 0
    record['verdict'] = 'PASS_EXACT_QTR_ROUTE_AND_UNCHANGED_EXISTING_POLICY_SUITES'
    receipt.write_text(json.dumps(record, indent=2) + '\n')
print(receipt)
