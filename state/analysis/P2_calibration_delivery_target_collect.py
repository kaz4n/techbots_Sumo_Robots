# Collect D105 completed board-Linux artifacts without touching the MCU.
# Freeze exact staged source so concurrent edits cannot change build provenance.
# Reuse the prior checked collector and preserve all original raw receipts.
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('d101', ROOT / 'state/analysis/P2_app_dump_target_collect.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
collector.RAW = ROOT / 'state/analysis/P2_calibration_delivery_raw'
EXPECTED_FILES = 89


def freeze_source():
    folder = collector.RAW / ('target_sources_' + collector.SOURCE[:8])
    manifest = folder / 'manifest.json'
    if manifest.exists():
        return json.loads(manifest.read_text())
    stage = ROOT / 'build/stage/app'
    payloads = {p.relative_to(stage).as_posix(): p.read_bytes()
                for p in stage.rglob('*') if p.is_file()}
    if len(payloads) != EXPECTED_FILES:
        raise ValueError('Staged source count differs from the explicitly selected revision')
    digest = hashlib.sha256()
    for name in sorted(payloads):
        digest.update(name.encode() + b'\0')
        digest.update(payloads[name])
    if digest.hexdigest() != collector.SOURCE:
        raise ValueError('Staged source does not match the explicit receipt source')
    folder.mkdir(parents=True, exist_ok=False)
    for name, payload in payloads.items():
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    data = dict(source_sha256=collector.SOURCE,
                source_files={n: hashlib.sha256(p).hexdigest() for n, p in sorted(payloads.items())},
                frozen_utc=datetime.now(timezone.utc).isoformat(), origin='exact build/stage/app bytes')
    manifest.write_text(json.dumps(data, indent=2) + '\n')
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('receipt', type=Path)
    parser.add_argument('mode', choices=('bench-default', 'bench-immediate', 'match-immediate'))
    parser.add_argument('--source', required=True)
    parser.add_argument('--files', type=int, choices=(89, 91), default=89)
    parser.add_argument('--pin-table', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{64}', args.source):
        raise ValueError('Requires a complete explicit SHA256')
    collector.SOURCE = args.source
    EXPECTED_FILES = args.files
    if args.pin_table:
        if args.files != 91:
            raise ValueError('D106 pin-table revision must contain exactly 91 source files')
        collector.RAW = ROOT / 'state/analysis/P2_pin_table_raw'
    collector.freeze_source = freeze_source
    collector.collect(args.receipt.resolve(), args.mode)
