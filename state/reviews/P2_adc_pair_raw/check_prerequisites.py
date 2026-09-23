"""Rehash cached primary-source evidence for the independent D086 review."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'state/analysis/P2_adc_pair_raw/source'
manifest = json.loads((SOURCE / 'manifest.json').read_text())
checks = []

def verify(path, expected):
    path = Path(path)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    checks.append({'path': str(path.relative_to(ROOT)), 'expected': expected,
                   'actual': actual, 'matches': actual == expected})

verify(ROOT / manifest['pdf'], manifest['pdf_sha256'])
for item in manifest['pages']:
    verify(SOURCE / item['text'], item['text_sha256'])
    if 'rendered' in item:
        verify(SOURCE / item['rendered'], item['rendered_sha256'])
for item in manifest['headers']:
    verify(ROOT / item['reused_local'], item['source_sha256'])
    verify(SOURCE / item['excerpt'], item['excerpt_sha256'])
verify(SOURCE / 'unoq.overlay', manifest['official_overlay_refresh']['sha256'])
verify(SOURCE / 'installed_binding_excerpts.json', manifest['binding_excerpt_sha256'])
bindings = json.loads((SOURCE / 'installed_binding_excerpts.json').read_text())
verify(ROOT / bindings['reused_receipt'], bindings['receipt_sha256'])
result = {'scope': 'Read-only cached-source identity check; no board access',
          'baseline': subprocess.check_output(['git', 'rev-parse', 'f194579'], cwd=ROOT, text=True).strip(),
          'checks': checks, 'all_match': all(x['matches'] for x in checks)}
(OUT / 'prerequisite_identity.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'checks': len(checks), 'all_match': result['all_match']}))
raise SystemExit(0 if result['all_match'] else 1)
