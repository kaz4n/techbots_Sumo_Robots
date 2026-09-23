"""Bind read-only D111 source findings to frozen bytes and protected-file evidence."""
import hashlib
import json
from pathlib import Path
import subprocess
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RAW = OUT.parent
def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return json.loads(path.read_text())
def git(*args): return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True).stdout
freeze = read(RAW / 'worker/first_source_freeze.json')
hashes = {}
for row in freeze['files']:
    data = (ROOT / row['path']).read_bytes()
    assert sha(data) == row['sha256']
    assert data == (RAW / 'worker/first_sources' / row['path']).read_bytes()
    hashes[row['path']] = row['sha256']
contract = ROOT / 'state/analysis/P2_imu_heading_bench_contract.md'
assert sha(contract.read_bytes()) == freeze['contract_sha256']
public_path = 'bench/imu_heading/src/imu_heading_bench.h'
adopted = git('show', '9299192:' + public_path).replace(b'\r\n', b'\n')
actual = (ROOT / public_path).read_bytes().replace(b'\r\n', b'\n')
assert adopted.split(b'private:')[0] == actual.split(b'private:')[0]
native_path = 'bench/imu_heading/src/imu_heading_bench_native.h'
assert git('show', '9299192:' + native_path).replace(b'\r\n', b'\n') == (ROOT / native_path).read_bytes().replace(b'\r\n', b'\n')
before = (RAW / 'registry/test_p0_config_before.py').read_bytes()
after = (RAW / 'registry/test_p0_config_after.py').read_bytes()
addition = (b'    "IMU_BENCH_TRIAL_US": 60000000,\n'
            b'    "IMU_BENCH_CHECKPOINT_US": 1000000,\n'
            b'    "IMU_BENCH_CHECKPOINTS": 61,\n'
            b'    "IMU_BENCH_DEADLINE_US": 70000000,\n'
            b'    "IMU_BENCH_MAX_POLLS": 100000000,\n')
# The coordinator saved raw before/after files, so compare without newline normalization.
assert after.count(addition) == 1 and after.replace(addition, b'') == before
assert after == (ROOT / 'tests/test_p0_config.py').read_bytes()
old_paths = git('ls-tree', '-r', '--name-only', '60e2193', 'tests').decode().splitlines()
unchanged = []
for path in old_paths:
    if path == 'tests/test_p0_config.py': continue
    assert git('show', '60e2193:' + path) == (ROOT / path).read_bytes(), path
    unchanged.append(path)
syntax = read(RAW / 'worker/first_syntax.json')
result = dict(verdict='PASS_SCOPED_FROZEN_SOURCE_REVIEW_TEST_EXECUTION_PENDING', hashes=hashes,
    contract_sha256=freeze['contract_sha256'], public_API_unchanged=True,
    registry=dict(before_sha256=sha(before), after_sha256=sha(after), exact_addition_bytes=len(addition)),
    prior_test_files_byte_identical=len(unchanged),
    inspected=[
        'Begin permission/port/config/Estimator order; disabled/repeated/terminal passivity',
        'One passive native Acquirer, exact six callbacks; actual Estimator and Services only',
        'S/A/C chronology, accumulated half-range/lifetime/grid admission and immutable first cause',
        'Reply shape precedes A; terminal SOURCE delivery and A-DEADLINE diagnostic-only delivery',
        'Pending begins conservatively; complete clears only after A/source; native FAULT owns cleanup',
        'Cancel once with actual accepted trigger or historical last clock; C measurement boundaries',
        'Original release grids, one action per active poll, early polls and pre-S poll limit',
        'Actual calibration window/absence/source admission, applyBias once and retention on failed C',
        'Published float-heading difference in double; actual-source checkpoint crossing and immutable prefix',
        'Fixed 61 slots, no runtime allocation or unbounded bench loops, exact config zero-divisor exclusions',
        'Accepted observation counts/extrema only after healthy C; diagnostic completion counts before A',
        'Native healthy Setup/Progress shape matches existing production owners; no shared HAL/core changes'],
    source_review_only_limits=[
        'NUMERIC from two finite published float headings is unreachable for ordinary valid finite trial bounds',
        'A second skipped checkpoint boundary is precluded by admitted estimator gap <= checkpoint period',
        'Diagnostic saturation arithmetic is inspected; finite lifetime and poll limit preclude fabricated overflow claims',
        'No physical mounting, power, clock, WCET, drift/rotation or capture provenance is inferred'],
    test_status='Independent author executable suite has not yet frozen/executed; no final firmware verdict.',
    unchanged_full_host_context='D109 private tools/test_host.sh CTest 2/2 PASS; all old test files remain byte identical except the five additive registry literals, and D111 target audit proves only five unused shared config constants changed since D110.')
(OUT / 'source_review.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ('verdict','prior_test_files_byte_identical','registry')}, indent=2))
