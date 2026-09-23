"""Reviewer rerun of unchanged independently frozen D114 tests in private WSL."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
receipt=OUT/('policy_'+str(time.time_ns())+'.json')
pins={'tools/board_tool.py':'e0444bc4c8922a53469d232dcab72bb91b6a59f8be50a80f4eb8e8badbad44d6',
      'tools/app_build_policy.py':'744d7d411e9ed68fb724d3ac2fc4081ea35ebca7c8e5414be54ee7feb1a1e161',
      'tests/tooling/test_ui_adc_probe_policy.py':'f88ff324c23f6c0b3d0b91498874498910fa19eb0c9529dec84360990a73f297',
      'bench/ui_adc_probe/ui_adc_probe.ino':'87e305fe7c3eb4d606224065fea2a2a1ef2dce93351c195ea9bf43748eaf0a60'}
with tempfile.TemporaryDirectory(prefix='d114-review-') as temporary:
    copied=Path(temporary)
    for folder in ('src','tools','tests','docs','bench'):
        shutil.copytree(ROOT/folder,copied/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    hashes={p.relative_to(copied).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in copied.rglob('*') if p.is_file()}
    assert all(hashes[p]==h for p,h in pins.items())
    record=dict(scope='Private WSL only; no board/shared build',reviewer='Reused source-aware separate same-model context',
                copied_sha256=hashes)
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    argv=['python3','-B','-m','unittest','tests.tooling.test_ui_adc_probe_policy','tests.tooling.test_ui_bench_policy','-v']
    result=subprocess.run(argv,cwd=copied,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
                          capture_output=True,text=True,timeout=180)
    record.update(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    print(receipt,result.stdout,result.stderr[-3000:],flush=True)
    assert result.returncode==0
