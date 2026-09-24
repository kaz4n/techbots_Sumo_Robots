"""Compare every checked staged file to its real repository source."""
from pathlib import Path
import datetime
import hashlib
import json

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
result = {}
for profile in ('app', 'turn_accuracy'):
    doc = json.loads((out/profile/'source_manifest.json').read_text())
    checks = {}
    folder = root/('src/app' if profile == 'app' else 'bench/turn_accuracy')
    for name, digest in doc['files'].items():
        path = root/name if name.startswith('src/') else folder/name
        checks[name] = hashlib.sha256(path.read_bytes()).hexdigest() == digest
    assert all(checks.values()), checks
    result[profile] = {'source_sha256': doc['source_sha256'], 'current_matches': checks}
result['checked_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
(out/'target_source_check.json').write_text(json.dumps(result, indent=2)+'\n')
print({k: len(v['current_matches']) for k, v in result.items() if isinstance(v, dict)})
