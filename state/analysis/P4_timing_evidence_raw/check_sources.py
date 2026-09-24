"""Compare every checked staged file to its real repository source."""
from pathlib import Path
import datetime
import hashlib
import json

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
result = {}
for profile in ('app', 'reactive_test', 'reactive_timing', 'reactive_timing_configured'):
    doc = json.loads((out/profile/'source_manifest.json').read_text())
    checks = {}
    project = 'reactive_timing' if profile == 'reactive_timing_configured' else profile
    folder = root/('src/app' if project == 'app' else 'bench/'+project)
    for name, digest in doc['files'].items():
        path = root/name if name.startswith('src/') else folder/name
        if profile == 'reactive_timing_configured' and name == 'src/config.h':
            path = out/'configured_config.h'
        checks[name] = hashlib.sha256(path.read_bytes()).hexdigest() == digest
    assert all(checks.values()), checks
    result[profile] = {'source_sha256': doc['source_sha256'], 'current_matches': checks}
result['checked_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
(out/'target_source_check.json').write_text(json.dumps(result, indent=2)+'\n')
print({k: len(v['current_matches']) for k, v in result.items() if isinstance(v, dict)})
