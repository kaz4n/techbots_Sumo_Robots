"""Independently rerun final frozen D114 capture cases in a private WSL tree."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
EXPECTED_SOURCE='f4b3db265bdf2d5a5fdada19ed9f51a44304d9ba5da8be78e598365afa2c4444'
EXPECTED_TEST=sys.argv[1]
receipt=OUT/('private_'+str(time.time_ns())+'.json')
with tempfile.TemporaryDirectory(prefix='d114-capture-review-') as temporary:
    copied=Path(temporary)
    for name in ('tools','tests'):
        shutil.copytree(ROOT/name,copied/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for leaf,names in (
        ('target_396bcc45_bench-default_checked',('ui_adc_probe.ino.elf','ui_adc_probe.ino.elf-zsk.bin')),
        ('root_capture_inputs',('zephyr-arduino_uno_q_stm32u585xx.elf','zephyr-arduino_uno_q_stm32u585xx.bin'))):
        relative=Path('state/analysis/P2_ui_adc_probe_raw')/leaf
        (copied/relative).mkdir(parents=True)
        for name in names: shutil.copyfile(ROOT/relative/name,copied/relative/name)
    hashes={p.relative_to(copied).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in copied.rglob('*') if p.is_file()}
    assert hashes['tools/ui_adc_capture.py']==EXPECTED_SOURCE
    assert hashes['tests/tooling/test_ui_adc_capture.py']==EXPECTED_TEST
    record=dict(scope='Source-aware separate reviewer; private synthetic tests; no board',copied_sha256=hashes)
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    argv=['python3','-B','-m','unittest','tests.tooling.test_ui_adc_capture','-v']
    result=subprocess.run(argv,cwd=copied,capture_output=True,text=True,timeout=180,
                          env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
    record.update(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(receipt=str(receipt),returncode=result.returncode,tail=result.stderr[-1500:])))
    raise SystemExit(result.returncode)
