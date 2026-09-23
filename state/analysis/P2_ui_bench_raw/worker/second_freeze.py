"""Retain the exact source correction before checks; preserve the first snapshot."""
from datetime import datetime, timezone
from pathlib import Path
import difflib
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
first = json.loads((RAW / 'first_source_freeze.json').read_text())
destination = RAW / 'second_sources'
destination.mkdir(exist_ok=False)
record = {'utc': datetime.now(timezone.utc).isoformat(),
    'reason': 'Coordinator clarification: save actual sample and sample_seen before A; no validation/decoder before A.',
    'scope': 'Two-line reorder in ui_bench.cpp only. No independent test bodies read.', 'files': []}
for item in first['files']:
    name = item['path']
    original = RAW / 'first_sources' / name
    assert hashlib.sha256(original.read_bytes()).hexdigest() == item['sha256']
    source = ROOT / name
    target = destination / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    record['files'].append({'path': name, 'bytes': source.stat().st_size,
        'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'first_sha256': item['sha256']})
record['contract_sha256'] = hashlib.sha256((ROOT / 'state/analysis/P2_ui_bench_contract.md').read_bytes()).hexdigest()
(RAW / 'second_source_freeze.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
name = 'bench/ui/src/ui_bench.cpp'
change = ''.join(difflib.unified_diff((RAW / 'first_sources' / name).read_text().splitlines(True),
    (ROOT / name).read_text().splitlines(True), fromfile='first/' + name, tofile='second/' + name))
(RAW / 'second_source.diff').write_text(change, encoding='utf-8')
print(json.dumps(record, indent=2))
print(change)
