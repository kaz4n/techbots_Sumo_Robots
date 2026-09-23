"""Execute frozen D110 author cases in a private WSL copy without shared writes."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
receipt = OUT / ('firmware_' + str(time.time_ns()) + '.json')
record = dict(scope='Private WSL only; no board/network or shared build',
    independence='Reviewer read production; unchanged author metadata describes independent original authorship, not this reviewer.', results=[])
with tempfile.TemporaryDirectory(prefix='d110-review-') as temporary:
    copied = Path(temporary)
    for folder in ('src', 'tests', 'host', 'tools', 'bench', 'docs'):
        shutil.copytree(ROOT / folder, copied / folder, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ('P2_vbat_contract.md', 'P2_app_runtime_contract.md'):
        path = Path('state/analysis') / name
        (copied / path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, copied / path)
    path = Path('state/analysis/P2_vbat_raw/author/test_p0_config_before.py')
    (copied / path).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / path, copied / path)
    hashes = {p.relative_to(copied).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in copied.rglob('*') if p.is_file()}
    for path, expected in {
        'bench/vbat/src/vbat.cpp': 'b5fa7eea988e91a9b0fdb350b34fed982cef9893bde47e56c289e07a403c0475',
        'tests/tooling/vbat_cases.cc': '196faa64a112c6a7b37d50524a84433e83b1fb7a21403781953dcf02f795e0f7',
        'tests/tooling/test_vbat.py': '34e3a8967cb7048f5d4e482416c4cc01847ac2c9607cfab431283ed0bcbf1283'
    }.items(): assert hashes[path] == expected, path
    record['copied_hashes'] = hashes
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    argv = ['python3', '-m', 'unittest', 'tests.tooling.test_vbat', '-v']
    result = subprocess.run(argv, cwd=copied, text=True, capture_output=True, timeout=900)
    record['results'].append(dict(argv=argv, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    generated = copied / 'state/analysis/P2_vbat_raw/author'
    if generated.exists(): shutil.copytree(generated, OUT / (receipt.stem + '_cases'))
    print(result.stdout[-4000:], result.stderr[-2000:], flush=True)
    assert result.returncode == 0
    record['verdict'] = 'PASS_PRIVATE_UNCHANGED_D110_CASES'
    receipt.write_text(json.dumps(record, indent=2) + '\n')
print(receipt)
