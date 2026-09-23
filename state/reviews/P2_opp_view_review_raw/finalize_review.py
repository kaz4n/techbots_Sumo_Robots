"""Bind the D107 reviewer verdict to exact already-audited files only."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
unchanged = ['tools/p0_inert_sources.json', 'src/config.h', 'tests/tooling/test_app_build_policy.py',
             'tests/tooling/test_app_build_overrides.py', 'tests/tooling/test_runtime_inert_policy.py']
for rel in unchanged:
    expected = subprocess.run(['git', 'show', 'HEAD:' + rel], cwd=ROOT, capture_output=True, check=True).stdout
    assert (ROOT / rel).read_bytes().replace(b'\r\n', b'\n') == expected.replace(b'\r\n', b'\n'), rel
assert 'bench/opp_view' not in json.loads((ROOT / unchanged[0]).read_text())
profiles = {}
for profile in ['bench-default', 'bench-immediate']:
    p = OUT / ('target_332787f0_' + profile + '_checked.json'); r = json.loads(p.read_text())
    profiles[profile] = dict(review_sha256=sha(p), source_sha256=r['source_sha256'],
        artifacts=[{k: a[k] for k in ['file', 'sha256', 'bytes', 'payload', 'conditional_peak',
                                      'free_span', 'largest_free_payload']} for a in r['artifacts']],
        zsk_sha256=r['zsk_sha256'])
paths = ['bench/opp_view/opp_view.ino', 'bench/opp_view/src/opp_view.cpp', 'bench/opp_view/src/opp_view.h',
         'bench/opp_view/src/opp_view_native.h', 'bench/opp_view/src/opp_view_native.cpp',
         'tools/board_tool.py', 'tools/app_build_policy.py', 'tools/p0_inert_sources.json',
         'tests/tooling/test_opp_view_policy.py', 'tests/tooling/test_opp_view.py', 'tests/tooling/opp_view_cases.cc',
         'state/analysis/P2_opp_view_contract.md', 'state/reviews/P2_opp_view_review.md']
result = dict(verdict='PASS_SCOPED_SOURCE_HOST_POLICY_AND_CHECKED_TARGET',
    findings={'D107-R1': 'CLOSED', 'D107-R2': 'CLOSED', 'D107-R3': 'CLOSED_EXACT_CHECKED_ONLY_GENERIC_STILL_REJECTED'},
    profiles=profiles, files_sha256={p: sha(ROOT / p) for p in paths},
    reviewer_test_receipts=['host_1790193025104410083.json', 'host_1790193374436463538.json',
                           'passive_1790193155331447426.json', 'policy_1790193719040116930.json'],
    unchanged_scope='Listed old files match Git HEAD after checkout newline normalization; raw hashes separately retained',
    limits='No upload, board/network/MCU operation, physical grant, actual free RAM/WCET or phase pass. Reused same-model reviewer context.')
(OUT / 'final_review.json').write_text(json.dumps(result, indent=2) + '\n')
print('Final review written; report lines', len((ROOT / 'state/reviews/P2_opp_view_review.md').read_text().splitlines()))
