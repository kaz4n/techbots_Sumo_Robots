"""Reviewer-local copied-source builds only; no staging, transport or shared builds."""
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
stamp = str(time.time_ns())
results = []
with tempfile.TemporaryDirectory(prefix='d096-review-', dir='/dev/shm') as temp:
    src = Path(temp) / 'src'
    shutil.copytree(ROOT / 'src', src)
    historical = '--historical-d-policy' in sys.argv
    if historical:
        runtime = src / 'app/runtime.cpp'
        body = runtime.read_text()
        old = 'const DecisionSource projection{this, projectThunk, clockAcceptedThunk};'
        assert old in body
        runtime.write_text(body.replace(old, 'const DecisionSource projection{this, projectThunk};'))
        inputs = src / 'app/runtime_inputs.cpp'
        body = inputs.read_text()
        old = '    return decision_input_;'
        assert body.count(old) == 1
        inputs.write_text(body.replace(old, '    if (projection_failed_) decision_input_.line.contract_valid = false;\n'+old))
    sources = sorted((src / 'core').glob('*.cpp'))
    sources += [src / 'app' / name for name in ('transaction.cpp', 'runtime.cpp', 'runtime_inputs.cpp')]
    sources += [src / 'hal' / name for name in ('motors.cpp','recorder.cpp','recorder_frames.cpp',
        'power_inputs.cpp','ui.cpp','imu_heading.cpp','imu_adapter.cpp','line_qtr_adapter.cpp',
        'qtr_cal.cpp','ui_display.cpp')]
    sources += [RAW / 'reviewer_clock.cpp']
    hashes = {str(p.relative_to(src)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in src.rglob('*') if p.is_file()}
    for mode in (0,1):
        binary = Path(temp) / f'review-{mode}'
        command = ['g++','-std=c++17','-O1','-Wall','-Wextra','-Werror','-Wpedantic',
            '-fno-exceptions','-fno-rtti','-fsanitize=address,undefined',
            '-fno-sanitize-recover=all',f'-DMOTORS_ALLOWED={mode}', '-I',str(src),
            *map(str,sources),'-o',str(binary)]
        if historical: command.insert(1, '-DREVIEW_HISTORICAL=1')
        for args in (command,[str(binary)]):
            p = subprocess.run(args,capture_output=True,text=True)
            results.append(dict(argv=args,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
            (RAW / f'clock_results_{stamp}.json').write_text(json.dumps(
                dict(source_sha256=hashes,results=results,historical_d_policy=historical,
                scope='Reconstructed original two-line D policy in isolated copy' if historical else 'Actual copied production source'),indent=2)+'\n')
            print(p.stdout,p.stderr,flush=True)
            if p.returncode: raise SystemExit(p.returncode)
