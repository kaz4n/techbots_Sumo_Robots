"""Copied-source D102 reviewer runs in Linux shared memory, with immutable receipts."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
stamp = str(time.time_ns())
receipt = RAW / ('review_' + stamp + '.json')
record = dict(scope='Independent D102 public probe and isolated sanitizer regression; no hardware/network', results=[])

def run(argv):
    result = subprocess.run(argv, text=True, capture_output=True)
    record['results'].append(dict(argv=argv, returncode=result.returncode,
                                 stdout=result.stdout, stderr=result.stderr))
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    print(result.stdout, result.stderr, flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)

with tempfile.TemporaryDirectory(prefix='d102-review-', dir='/dev/shm') as temporary:
    copied = Path(temporary)
    for folder in ('src', 'tests', 'host'):
        shutil.copytree(ROOT / folder, copied / folder)
    shutil.copy2(RAW / 'public_probe.cpp', copied / 'public_probe.cpp')
    shutil.copy2(RAW / 'view_probe.cpp', copied / 'view_probe.cpp')
    shutil.copytree(ROOT / 'bench/p2_recorder_memory/src', copied / 'memory_probe')
    record['source_test_hashes'] = {p.relative_to(copied).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in copied.rglob('*') if p.is_file()}
    common = ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Werror', '-Wpedantic',
              '-fno-exceptions', '-fno-rtti', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
              '-I', str(copied / 'src'), '-I', str(copied / 'host/third_party'),
              '-I', str(copied / 'memory_probe')]
    binary = copied / 'probe'
    run(common + [str(copied / 'public_probe.cpp'), str(copied / 'src/hal/recorder_frames.cpp'), '-o', str(binary)])
    run([str(binary)])
    sources = sorted((copied / 'src/core').glob('*.cpp')) + sorted((copied / 'src/app').glob('*.cpp'))
    sources += [copied / 'src/hal' / name for name in (
        'motors.cpp', 'recorder.cpp', 'recorder_frames.cpp', 'recorder_csv.cpp', 'recorder_dump.cpp',
        'power_inputs.cpp', 'ui.cpp', 'imu_heading.cpp', 'imu_adapter.cpp', 'line_qtr_adapter.cpp', 'qtr_cal.cpp', 'qtr_cal_format.cpp',
        'ui_display.cpp')]
    names = ('test_recorder_frames.cpp', 'test_attempt_recorder.cpp', 'test_recorder_csv.cpp',
             'test_recorder_rate.cpp', 'test_tick_timing.cpp', 'test_frame_packing.cpp')
    tests = [copied / 'tests' / name for name in names] + [copied / 'view_probe.cpp']
    sources.append(copied / 'memory_probe/memory_probe.cpp')
    binary = copied / 'regressions'
    run(common + ['-DDOCTEST_CONFIG_NO_EXCEPTIONS'] + list(map(str, sources)) +
        [str(copied / 'host/motor_gate_main.cpp')] + list(map(str, tests)) + ['-o', str(binary)])
    run([str(binary)])
print(receipt)
