"""Bind the narrow D112 tooling diff and untouched policy/upload evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
prior = json.loads((ROOT / 'state/analysis/P2_imu_heading_bench_raw/reviewer/policy_1790196950043960280.json').read_text())['copied_hashes']
files = ['tests/tooling/test_app_build_policy.py', 'tests/tooling/test_app_build_overrides.py',
    'tests/tooling/test_runtime_inert_policy.py', 'tests/tooling/test_opp_view_policy.py',
    'tests/tooling/test_qtr_raw_policy.py', 'tests/tooling/test_vbat_policy.py', 'tests/tooling/test_imu_heading_bench_policy.py', 'tools/p0_inert_sources.json']
assert all(sha(ROOT / path) == prior[path] for path in files)
expected = {
    'tools/board_tool.py': '91716ebeadeb1bcbb466342cf01f28ec56c384442e8d9ed553d9d3234d1885e9',
    'tools/app_build_policy.py': '5f90d922f210373ef8eb412dc0a7a4229c7f377674ea7085fa3b3e0174396c23',
    'tests/tooling/test_ui_bench_policy.py': '5c4cff7945564782759b27d4bea23b5c99a65fb9b2034fc2caca65c650d69b32'}
assert all(sha(ROOT / path) == value for path, value in expected.items())
freeze = json.loads((OUT.parent / 'policy/expectations_freeze.json').read_text())
assert expected[freeze['path']] == freeze['sha256']
result = subprocess.run(['git', 'diff', 'e898cf3', '--', 'tools/app_build_policy.py', 'tools/board_tool.py'],
    cwd=ROOT, capture_output=True, check=True)
(OUT / 'policy_diff.patch').write_bytes(result.stdout)
record = dict(verdict='PASS_SCOPED_TOOLING_SOURCE', hashes=expected,
    unchanged_from_D111={p: prior[p] for p in files},
    inspected=['literal project allowed-list addition', 'existing sensor inert flag constraint',
        'exact sketch route tuple and filename map', 'early MATCH/upload/profile refusal',
        'unchanged precompile pin/effective recipe/library/artifact verification',
        'checked failure propagates with no generic fallback', 'no new upload manifest key'],
    independence='New7 coordinator-authored cases frozen before red execution; reused separate same-model source reviewer.',
    limits='Tooling only. No firmware/target or upload approval; no board/network/MCU operation.')
(OUT / 'policy_source_review.json').write_text(json.dumps(record, indent=2) + '\n')
print(record['verdict'])
