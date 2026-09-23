"""Refresh only independently reviewed inert keys after exact local staging checks."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board

review = json.loads((ROOT / 'state/reviews/P2_app_transaction_review_raw/inert_source_reconstruction.json').read_text())
manifest = ROOT / 'tools/p0_inert_sources.json'
before = json.loads(manifest.read_text())
if before.keys() != review['entries'].keys() or len(before) != 7:
    raise SystemExit('Existing reviewed key set differs')
after = {}
records = {}
for sketch, expected in review['entries'].items():
    stage = board.stage(sketch)
    files = {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(stage.rglob('*')) if p.is_file()}
    if files != expected['file_sha256']:
        raise SystemExit('Independent per-file reconstruction mismatch: ' + sketch)
    digest = hashlib.sha256()
    for p in sorted(stage.rglob('*')):
        if p.is_file():
            digest.update(p.relative_to(stage).as_posix().encode() + b'\0')
            digest.update(p.read_bytes())
    checksum = digest.hexdigest()
    if checksum != expected['source_sha256']:
        raise SystemExit('Independent aggregate reconstruction mismatch: ' + sketch)
    after[sketch] = checksum
    records[sketch] = dict(source_sha256=checksum, files=len(files))
receipt = ROOT / 'state/analysis/P2_app_transaction_raw/manifest_refresh.json'
if receipt.exists():
    raise SystemExit('Preserve earlier manifest receipt')
manifest.write_text(json.dumps(after, indent=2) + '\n', encoding='utf-8')
receipt.write_text(json.dumps(dict(status='PASS_REVIEWED_EXACT_STAGING', before=before,
    after=after, records=records, scope='Local staging only; no transport or new upload key'), indent=2) + '\n')
print(json.dumps(dict(status='PASS_REVIEWED_EXACT_STAGING', keys=len(after))))
