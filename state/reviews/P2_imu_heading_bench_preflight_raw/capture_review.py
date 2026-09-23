"""Snapshot only D111 draft/API and read-only compatibility inputs for preflight."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
paths = ['state/analysis/P2_imu_heading_bench_contract_draft.md',
    'state/analysis/P2_imu_heading_bench_design.md',
    'state/analysis/P2_imu_heading_bench_headers/imu_heading_bench.h',
    'state/analysis/P2_imu_heading_bench_headers/imu_heading_bench_native.h',
    'src/hal/imu.cpp', 'src/hal/imu.h', 'src/hal/imu_acquisition.cpp',
    'src/hal/imu_acquisition_async.cpp', 'src/hal/imu_acquisition.h',
    'src/hal/imu_heading.cpp', 'src/hal/imu_heading.h', 'src/hal/imu_bus_unoq.h',
    'src/core/countdown.cpp', 'src/core/countdown.h', 'src/config.h',
    'state/analysis/P2_calibration_presence_contract.md',
    'state/analysis/P2_imu_resume_contract.md', 'state/analysis/P2_imu_heading_contract.md']
hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
suffix = hashes[paths[0]][:12]
for path in paths[:4]:
    out = OUT / suffix / Path(path).name
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists(): assert out.read_bytes() == (ROOT / path).read_bytes()
    else: out.write_bytes((ROOT / path).read_bytes())
(OUT / ('inputs_' + suffix + '.json')).write_text(json.dumps(dict(
    scope='Preflight source/API compatibility only; no executable tests, implementation edits or board actions',
    input_sha256=hashes), indent=2) + '\n')
print(suffix)
