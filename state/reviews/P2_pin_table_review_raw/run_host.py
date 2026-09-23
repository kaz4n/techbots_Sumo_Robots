"""Independent D106 checks in a private WSL copy; no board access."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
receipt = OUT / ('host_' + str(time.time_ns()) + '.json')
record = {'scope': 'Private WSL copy, synthetic native descriptors only', 'results': []}
with tempfile.TemporaryDirectory(prefix='d106-review-') as temporary:
    copied = Path(temporary)
    for name in ('src', 'tests', 'host', 'tools', 'bench'):
        shutil.copytree(ROOT / name, copied / name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    contract = Path('state/analysis/P2_pin_table_contract.md')
    (copied / contract).parent.mkdir(parents=True)
    shutil.copy2(ROOT / contract, copied / contract)
    record['source_hashes'] = {p.relative_to(copied).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in copied.rglob('*') if p.is_file()}
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    for command in (['bash', 'tools/test_host.sh'],
                    ['python3', '-m', 'unittest', 'tests.tooling.test_native_pins', '-v']):
        result = subprocess.run(command, cwd=copied, capture_output=True, text=True, timeout=600)
        record['results'].append(dict(argv=command, returncode=result.returncode,
                                     stdout=result.stdout, stderr=result.stderr))
        receipt.write_text(json.dumps(record, indent=2) + '\n')
        print(result.stdout, result.stderr, flush=True)
        if result.returncode:
            raise SystemExit(result.returncode)
    test_log = copied / 'build/host/Testing/Temporary/LastTest.log'
    if test_log.exists(): shutil.copy2(test_log, OUT / (receipt.stem + '_LastTest.log'))
    generated = copied / 'state/analysis/P2_pin_table_raw/author'
    if generated.exists(): shutil.copytree(generated, OUT / (receipt.stem + '_native'))
print(receipt)
