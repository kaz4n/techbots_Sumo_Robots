"""Run D108 safety review host entry point on an isolated immutable copy."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
receipt = OUT / ('host_' + str(time.time_ns()) + '.json')
with tempfile.TemporaryDirectory(prefix='d108-review-') as temporary:
    copied = Path(temporary)
    for name in ('src', 'tests', 'host', 'tools'):
        shutil.copytree(ROOT / name, copied / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    hashes = {p.relative_to(copied).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in copied.rglob('*') if p.is_file()}
    assert hashes['src/hal/ui_display.cpp'] == '9e9d5d9a44d8b0d637f2301d042f7021df890a270995e1806d4d4456dd58c535'
    record = dict(scope='Private WSL host simulation only; no shared build, board or network', source_hashes=hashes)
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    result = subprocess.run(['bash', 'tools/test_host.sh'], cwd=copied, capture_output=True, text=True, timeout=600)
    record.update(argv=['bash', 'tools/test_host.sh'], returncode=result.returncode,
                  stdout=result.stdout, stderr=result.stderr)
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    log = copied / 'build/host/Testing/Temporary/LastTest.log'
    if log.exists(): shutil.copy2(log, OUT / (receipt.stem + '_LastTest.log'))
    print(result.stdout[-2500:], result.stderr[-2000:], flush=True)
    assert result.returncode == 0
print(receipt)
