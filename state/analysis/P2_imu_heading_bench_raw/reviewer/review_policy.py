"""Privately execute unchanged coordinator D111 policy cases and prior suites."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
receipt = OUT / ('policy_' + str(time.time_ns()) + '.json')
expected = {
    'tools/board_tool.py': 'd9457474482a917068c324d3a894b081f89d97014f8c315c9389fcfb8fd39bb4',
    'tools/app_build_policy.py': 'fd70b189fb83b188caac1ae7047fd0ea400a3a4b7a5f22edbed8c963aa29b894',
    'tests/tooling/test_imu_heading_bench_policy.py': '2968d48e6e15fb73cca1d8b067658a713c64ead0e06cfa471a420a908668a717'}
record = dict(scope='Private WSL copy; mocked transports only; no board or network',
    authorship='New7 IMU heading policy cases are coordinator-authored; separate reviewer execution after source reading', commands=[])
with tempfile.TemporaryDirectory(prefix='d111-policy-review-') as temp:
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
    for modules in (['tests.tooling.test_imu_heading_bench_policy'],
                    ['tests.tooling.test_app_build_policy', 'tests.tooling.test_app_build_overrides',
                     'tests.tooling.test_runtime_inert_policy', 'tests.tooling.test_opp_view_policy',
                     'tests.tooling.test_qtr_raw_policy', 'tests.tooling.test_vbat_policy']):
        argv = ['python3', '-m', 'unittest', *modules, '-v']
        result = subprocess.run(argv, cwd=copied, env=env, text=True, capture_output=True, timeout=300)
        record['commands'].append(dict(argv=argv, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
        receipt.write_text(json.dumps(record, indent=2) + '\n')
        print(result.stderr[-500:], flush=True)
        assert result.returncode == 0
    record['verdict'] = 'PASS_EXACT_IMU_HEADING_ROUTE_AND_UNCHANGED_EXISTING_POLICY_SUITES'
    receipt.write_text(json.dumps(record, indent=2) + '\n')
print(receipt)
