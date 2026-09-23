"""Run independent ADC test modules from a frozen Linux temporary checkout."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
label, *modules = sys.argv[1:]
assert label.replace('_', '').isalnum() and modules
receipt = OUT / label
receipt.mkdir(exist_ok=False)
started = datetime.now(timezone.utc).isoformat()
with tempfile.TemporaryDirectory(prefix='d086-review-', dir='/dev/shm') as temporary:
    stage = Path(temporary)
    before = {}
    for name in ('src', 'tests', 'host', 'tools', 'bench'):
        shutil.copytree(ROOT / name, stage / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (stage / 'state/analysis').mkdir(parents=True)
    shutil.copyfile(ROOT / 'state/analysis/P2_adc_pair_contract.md',
                    stage / 'state/analysis/P2_adc_pair_contract.md')
    for path in sorted(stage.rglob('*')):
        if path.is_file():
            before[path.relative_to(stage).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    environment = os.environ.copy()
    environment['TMPDIR'] = '/dev/shm'
    environment['PYTHONDONTWRITEBYTECODE'] = '1'
    environment['SUMO_NATIVE_RECEIPT_DIR'] = str(receipt / 'native')
    command = ['python3', '-m', 'unittest', *modules, '-v']
    with (receipt / 'output.txt').open('w') as output:
        result = subprocess.run(command, cwd=stage, env=environment,
                                stdout=output, stderr=subprocess.STDOUT)
    author_receipts = stage / 'state/analysis/P2_adc_pair_raw/author'
    if author_receipts.exists():
        shutil.copytree(author_receipts, receipt / 'pair_native')
    drift = [name for name, digest in before.items()
             if not (ROOT / name).is_file() or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest]
    record = {'started': started, 'ended': datetime.now(timezone.utc).isoformat(),
              'argv': command, 'returncode': result.returncode, 'frozen_files': before,
              'live_drift': drift,
              'scope': 'Host native fixtures in isolated Linux checkout; no board operation'}
    (receipt / 'receipt.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'returncode': result.returncode, 'frozen_files': len(before), 'drift': drift}))
raise SystemExit(result.returncode)
