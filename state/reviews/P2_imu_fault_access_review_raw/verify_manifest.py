"""Confirm the refreshed manifest matches the independent frozen-byte reconstruction."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
RAW=Path(__file__).parent
path=ROOT/'tools/p0_inert_sources.json'
actual=json.loads(path.read_text())
review=json.loads((RAW/'inert_source_reconstruction.json').read_text())['entries']
expected={k:v['source_sha256'] for k,v in review.items()}
assert actual==expected and len(actual)==7
for key,v in review.items():
    for name,checksum in v['file_sha256'].items():
        shared=name=='src/config.h' or name.startswith(('src/core/','src/hal/','src/app/'))
        source=(ROOT/name) if shared else (ROOT/key/name)
        assert hashlib.sha256(source.read_bytes()).hexdigest()==checksum
out=RAW/'manifest_refresh_verified.json'
assert not out.exists()
out.write_text(json.dumps(dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                              keys=actual, exact_match=True, new_keys=[]),indent=2)+'\n')
print('PASS: all seven manifest entries exactly match independent reconstruction; shared source hashes unchanged.')
