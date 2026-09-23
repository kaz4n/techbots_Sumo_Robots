"""Run the reviewer-only core regression and preserve exact source identities."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
label = sys.argv[1]
with tempfile.TemporaryDirectory(prefix='d085-review-regression-', dir='/dev/shm') as tmp:
    stage = Path(tmp)
    shutil.copytree(root/'src', stage/'src')
    if len(sys.argv) > 2 and sys.argv[2] == 'confirm2':
        config = stage/'src/config.h'
        config.write_text(config.read_text().replace('QTR_CONFIRM_TICKS = 1U;', 'QTR_CONFIRM_TICKS = 2U;'))
    inputs = sorted((stage/'src/core').glob('*.cpp'))
    sources = {p.relative_to(stage).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
               for p in (stage/'src').rglob('*') if p.is_file()}
    argv = ['g++','-std=c++17','-O1','-Wall','-Wextra','-Werror','-pedantic',
            '-fno-exceptions','-fno-rtti','-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
            '-I'+str(stage/'src'),'-isystem',str(root/'host/third_party'),
            str(root/'tests/native_qtr/test_main.cc'),str(out/'reviewer_regressions.cc'),
            *map(str,inputs),'-o',str(stage/'review')]
    build = subprocess.run(argv,capture_output=True,text=True)
    run = subprocess.run([str(stage/'review'),'--no-colors'],capture_output=True,text=True) if build.returncode==0 else None
    result = dict(sources=sources,compile=dict(argv=argv,exit=build.returncode,out=build.stdout,err=build.stderr),
                  run=None if run is None else dict(exit=run.returncode,out=run.stdout,err=run.stderr))
    (out/(label+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(compile=result['compile'],run=result['run'])))
