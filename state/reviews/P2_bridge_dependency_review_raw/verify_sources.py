"""Independently verify D098 source receipts; no board access or production writes."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P2_bridge_dependency_raw'
OUT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

checks = []
for receipt_name in ('installed_receipt.json', 'primary_sources_receipt.json',
                     'primary_core_library_receipt.json', 'includes_receipt.json',
                     'generated_sketch_receipt.json', 'compile_primary_receipt.json'):
    receipt = json.loads((RAW / receipt_name).read_text())
    rows = receipt.get('files', [receipt])
    for row in rows:
        if 'sha256' not in row:
            continue
        saved = row.get('saved', row.get('path'))
        if not saved:
            continue
        target = ROOT / saved
        if not target.is_file():
            continue
        actual = sha(target)
        assert actual == row['sha256'], (receipt_name, saved)
        if 'copy_sha256' in row:
            assert actual == row['copy_sha256']
        if 'bytes' in row:
            assert len(target.read_bytes()) == row['bytes']
        checks.append({'receipt': receipt_name, 'file': saved, 'sha256': actual})

manifest = json.loads((RAW / 'manifest.json').read_text())
for row in manifest['files']:
    target = RAW / row['path']
    assert sha(target) == row['sha256'], row['path']
    assert len(target.read_bytes()) == row['bytes']

primary = json.loads((RAW / 'primary_core_library_receipt.json').read_text())
for row in primary['files']:
    relative = Path(row['path']).relative_to(Path('state/analysis/P2_bridge_dependency_raw/primary'))
    installed = RAW / 'installed' / relative
    same = (ROOT / row['path']).read_bytes() == installed.read_bytes()
    assert same == row['matches_installed'], str(relative)

checks_summary = {
    'scope': 'Independent local source/receipt bytes only; no new upstream or board query',
    'source_receipt_checks': len(checks),
    'audit_manifest_checks': len(manifest['files']),
    'primary_installed_comparisons': len(primary['files']),
    'checks': checks,
    'receipts_sha256': {p.name: sha(p) for p in RAW.glob('*receipt.json')},
}
(OUT / 'source_validation.json').write_text(json.dumps(checks_summary, indent=2)+'\n')
print(json.dumps({k:v for k,v in checks_summary.items() if k not in ('checks','receipts_sha256')}, indent=2))
