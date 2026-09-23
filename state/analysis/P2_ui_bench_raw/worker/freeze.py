"""Preserve the first D112 implementation before executing checks."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
destination = RAW / 'first_sources'
destination.mkdir(exist_ok=False)
files = ['bench/ui/ui.ino', 'bench/ui/src/ui_bench.h', 'bench/ui/src/ui_bench.cpp',
    'bench/ui/src/ui_bench_native.h', 'bench/ui/src/ui_bench_native.cpp']
record = {'utc': datetime.now(timezone.utc).isoformat(), 'scope': 'First source freeze before syntax or tests',
    'independence': 'No independent test bodies or expected values read.', 'files': []}
for name in files:
    source = ROOT / name
    target = destination / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    record['files'].append({'path': name, 'bytes': source.stat().st_size,
        'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
record['dependencies'] = [{'path': name, 'sha256': hashlib.sha256((ROOT / name).read_bytes()).hexdigest()}
    for name in ['src/config.h', 'src/hal/power.h', 'src/hal/ui.h', 'src/hal/ui.cpp',
        'state/analysis/P2_ui_bench_contract.md']]
(RAW / 'first_source_freeze.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, indent=2))
