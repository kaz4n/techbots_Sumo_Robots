"""Append current clarified-contract binding; never overwrite the original freeze."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
original = json.loads((RAW / 'second_source_freeze.json').read_text())
contract = ROOT / 'state/analysis/P2_ui_bench_contract.md'
files = [{'path': item['path'], 'sha256': hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()}
    for item in original['files']]
assert all(current['sha256'] == prior['sha256'] for current, prior in zip(files, original['files']))
record = {'observed_utc': datetime.now(timezone.utc).isoformat(),
    'note': 'The second source freeze captured the then-readable prior contract hash while the coordinator was updating its literal ordering. This later binding qualifies that dependency; original receipt and sources remain unchanged.',
    'original_freeze_utc': original['utc'], 'original_contract_sha256': original['contract_sha256'],
    'clarified_contract_path': 'state/analysis/P2_ui_bench_contract.md',
    'clarified_contract_sha256': hashlib.sha256(contract.read_bytes()).hexdigest(),
    'clarified_contract_mtime_utc': datetime.fromtimestamp(contract.stat().st_mtime, timezone.utc).isoformat(),
    'source_files_unchanged': files, 'independent_test_bodies_read': False}
destination = RAW / 'second_clarified_contract_binding.json'
assert not destination.exists()
destination.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print(json.dumps(record, indent=2))
