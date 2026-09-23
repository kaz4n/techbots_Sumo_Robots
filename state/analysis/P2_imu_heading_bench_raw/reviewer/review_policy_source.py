"""Bind the narrow D111 tooling diff and untouched policy/upload evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
prior = json.loads((ROOT / 'state/reviews/P2_vbat_review_raw/policy_1790195692330086332.json').read_text())['copied_hashes']
files = ['tests/tooling/test_app_build_policy.py', 'tests/tooling/test_app_build_overrides.py',
    'tests/tooling/test_runtime_inert_policy.py', 'tests/tooling/test_opp_view_policy.py',
    'tests/tooling/test_qtr_raw_policy.py', 'tests/tooling/test_vbat_policy.py', 'tools/p0_inert_sources.json']
assert all(sha(ROOT / path) == prior[path] for path in files)
expected = {
    'tools/board_tool.py': 'd9457474482a917068c324d3a894b081f89d97014f8c315c9389fcfb8fd39bb4',
    'tools/app_build_policy.py': 'fd70b189fb83b188caac1ae7047fd0ea400a3a4b7a5f22edbed8c963aa29b894',
    'tests/tooling/test_imu_heading_bench_policy.py': '2968d48e6e15fb73cca1d8b067658a713c64ead0e06cfa471a420a908668a717'}
assert all(sha(ROOT / path) == value for path, value in expected.items())
freeze = json.loads((OUT.parent / 'policy/expectations_freeze.json').read_text())
assert expected[freeze['path']] == freeze['sha256']
result = subprocess.run(['git', 'diff', '--', 'tools/app_build_policy.py', 'tools/board_tool.py'],
    cwd=ROOT, capture_output=True, check=True)
(OUT / 'policy_diff.patch').write_bytes(result.stdout)
record = dict(verdict='PASS_SCOPED_TOOLING_SOURCE', hashes=expected,
    unchanged_from_D110={p: prior[p] for p in files},
    inspected=['literal project allowed-list addition', 'existing sensor inert flag constraint',
        'exact sketch route tuple and filename map', 'early MATCH/upload/profile refusal',
        'unchanged precompile pin/effective recipe/library/artifact verification',
        'checked failure propagates with no generic fallback', 'no new upload manifest key'],
    independence='New7 coordinator-authored cases frozen before red execution; reused separate same-model source reviewer.',
    limits='Tooling only. No firmware/target or upload approval; no board/network/MCU operation.')
(OUT / 'policy_source_review.json').write_text(json.dumps(record, indent=2) + '\n')
print(record['verdict'])
