"""D109 private host and unchanged independent-author case execution."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
receipt = OUT / ('firmware_' + str(time.time_ns()) + '.json')
record = dict(scope='Private WSL only; no board/network or shared build',
              independence='Reviewer has read production. Unchanged author harness metadata describes original independent test authoring, not this reviewer.',
              results=[])
with tempfile.TemporaryDirectory(prefix='d109-review-') as temporary:
    copied = Path(temporary)
    for folder in ('src', 'tests', 'host', 'tools', 'bench', 'docs'):
        shutil.copytree(ROOT / folder, copied / folder, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ('P2_qtr_raw_contract.md', 'P2_app_runtime_contract.md'):
        contract = Path('state/analysis') / name
        (copied / contract).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / contract, copied / contract)
    record['source_hashes'] = {p.relative_to(copied).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in copied.rglob('*') if p.is_file()}
    assert record['source_hashes']['bench/qtr_raw/src/qtr_raw.cpp'] == '54b0a21b7b2867d9f816f476bec2b8cddf7b6ca7f902b7e682ccce2a9bceed33'
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    commands = (['bash', 'tools/test_host.sh'], ['python3', '-m', 'unittest', 'tests.tooling.test_qtr_raw', '-v'])
    if '--registry-only' in sys.argv:
        commands = (['python3', '-m', 'unittest', 'tests.tooling.test_qtr_raw.QtrRawTests.test_additive_registry_keeps_original_18_assertions_and_rejects_129', '-v'],)
    for command in commands:
        result = subprocess.run(command, cwd=copied, text=True, capture_output=True, timeout=600)
        record['results'].append(dict(argv=command, returncode=result.returncode,
                                      stdout=result.stdout, stderr=result.stderr))
        receipt.write_text(json.dumps(record, indent=2) + '\n')
        print(result.stdout[-2500:], result.stderr[-2000:], flush=True)
        generated = copied / 'state/analysis/P2_qtr_raw_raw/author'
        if generated.exists(): shutil.copytree(generated, OUT / (receipt.stem + '_cases'), dirs_exist_ok=True)
        log = copied / 'build/host/Testing/Temporary/LastTest.log'
        if log.exists(): shutil.copy2(log, OUT / (receipt.stem + '_LastTest.log'))
        assert result.returncode == 0
    record['verdict'] = 'PASS_PRIVATE_D109_REGISTRY' if '--registry-only' in sys.argv else 'PASS_PRIVATE_HOST_AND_UNCHANGED_D109_CASES'
    receipt.write_text(json.dumps(record, indent=2) + '\n')
print(receipt)
