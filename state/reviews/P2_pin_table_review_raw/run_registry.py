"""Run the additive D096 registry repair on an isolated copy, retaining receipts."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
receipt = OUT / ('registry_' + str(time.time_ns()) + '.json')
with tempfile.TemporaryDirectory(prefix='d106-registry-review-') as temporary:
    copied = Path(temporary)
    for name in ('src', 'tests', 'tools', 'docs'):
        shutil.copytree(ROOT/name, copied/name, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    contract = Path('state/analysis/P2_app_runtime_contract.md')
    (copied/contract).parent.mkdir(parents=True)
    shutil.copy2(ROOT/contract,copied/contract)
    hashes={p.relative_to(copied).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in copied.rglob('*') if p.is_file()}
    command=['python3','-m','unittest','tests.tooling.test_runtime_config_registry','-v']
    result=subprocess.run(command,cwd=copied,capture_output=True,text=True,timeout=120)
    receipt.write_text(json.dumps(dict(argv=command,returncode=result.returncode,
        stdout=result.stdout,stderr=result.stderr,source_hashes=hashes),indent=2)+'\n')
    nested=copied/'state/analysis/P2_pin_table_raw/registry_cases.jsonl'
    if nested.exists():shutil.copy2(nested,OUT/(receipt.stem+'_cases.jsonl'))
    print(result.stdout,result.stderr,receipt)
    raise SystemExit(result.returncode)
