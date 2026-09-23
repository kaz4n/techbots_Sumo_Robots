"""D104 copied-source host/tooling review, without network or shared build writes."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
receipt = RAW / ('host_' + str(time.time_ns()) + '.json')
record = {'scope': 'Isolated copied-source D104 host and controlled-tooling checks',
          'results': []}


def run(argv, cwd):
    result = subprocess.run(list(map(str, argv)), cwd=cwd, capture_output=True,
                            text=True, timeout=600)
    record['results'].append({'argv': list(map(str, argv)), 'cwd': str(cwd),
                              'returncode': result.returncode,
                              'stdout': result.stdout, 'stderr': result.stderr})
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    print(result.stdout, result.stderr, flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)


with tempfile.TemporaryDirectory(prefix='d104-review-') as temporary:
    copied = Path(temporary)
    for folder in ('src', 'tests', 'host', 'tools', 'bench'):
        shutil.copytree(ROOT / folder, copied / folder,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    historical = Path('state/analysis/P2_app_build_raw/default_receipt')
    shutil.copytree(ROOT / historical, copied / historical)
    contract = Path('state/analysis/P2_runtime_inert_contract.md')
    shutil.copy2(ROOT / contract, copied / contract)
    record['copied_hashes'] = {
        path.relative_to(copied).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in copied.rglob('*') if path.is_file()}
    if '--extra' in sys.argv:
        cases = copied / 'tests/tooling/runtime_bench_cases.cc'
        cases.write_bytes(cases.read_bytes() + b'\n' + (RAW / 'extra_cases.cc').read_bytes())
        record['reviewer_cases_sha256'] = hashlib.sha256(cases.read_bytes()).hexdigest()
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    modules = [value for value in sys.argv[1:] if value not in ('--skip-host', '--extra')]
    if '--skip-host' not in sys.argv:
        run(['bash', 'tools/test_host.sh'], copied)
    log = copied / 'build/host/Testing/Temporary/LastTest.log'
    if log.is_file():
        shutil.copy2(log, RAW / (receipt.stem + '_LastTest.log'))
    if modules:
        run(['env', 'PYTHONPATH=tests/tooling', 'python3', '-m', 'unittest', *modules, '-v'], copied)
    # New independent tests may retain their own commands inside the isolated copy.
    for path in (copied / 'state/analysis').rglob('*'):
        if path.is_file() and 'P2_runtime_inert' in str(path):
            target = RAW / receipt.stem / path.relative_to(copied)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
print(receipt)
