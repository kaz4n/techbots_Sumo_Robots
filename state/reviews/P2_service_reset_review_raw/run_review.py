"""Immutable copied-source D103 reviewer ASan/UBSan runs, without board access."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
receipt = RAW / ('review_' + str(time.time_ns()) + '.json')
record = {'scope': 'Independent public-owner sanitizer probes, no board/network/shared build', 'results': []}

def run(argv):
    result = subprocess.run(list(map(str, argv)), capture_output=True, text=True)
    record['results'].append({'argv': list(map(str, argv)), 'returncode': result.returncode,
                              'stdout': result.stdout, 'stderr': result.stderr})
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    print(result.stdout, result.stderr, flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)

with tempfile.TemporaryDirectory(prefix='d103-review-', dir='/dev/shm') as temporary:
    copied = Path(temporary)
    for folder in ('src', 'tests', 'host'):
        shutil.copytree(ROOT / folder, copied / folder)
    shutil.copy2(RAW / 'reviewer_extra.cpp', copied / 'reviewer_extra.cpp')
    record['original_source_test_hashes'] = {
        p.relative_to(copied).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in copied.rglob('*') if p.is_file()}
    config = copied / 'src/config.h'
    text = config.read_text()
    for name, value in (('BUTTON_WINDOWS_CONFIGURED', '1U'),
                        ('BUTTON_LOW_RAW', '{0U, 900U, 1900U, 2900U}'),
                        ('BUTTON_HIGH_RAW', '{100U, 1100U, 2100U, 3100U}')):
        text, count = re.subn(r'(\b' + name + r'(?:\[4\])?\s*=\s*)[^;]+;',
                             r'\g<1>' + value + ';', text)
        assert count == 1, name
    config.write_text(text)
    record['synthetic_button_config_sha256'] = hashlib.sha256(config.read_bytes()).hexdigest()
    sources = sorted((copied / 'src/core').glob('*.cpp')) + sorted((copied / 'src/app').glob('*.cpp'))
    sources += [copied / 'src/hal' / name for name in (
        'motors.cpp', 'recorder.cpp', 'recorder_frames.cpp', 'recorder_csv.cpp', 'recorder_dump.cpp',
        'power_inputs.cpp', 'ui.cpp', 'imu_heading.cpp', 'imu_adapter.cpp', 'line_qtr_adapter.cpp',
        'qtr_cal.cpp', 'qtr_cal_format.cpp', 'ui_display.cpp')]
    tests = [copied / 'reviewer_extra.cpp']
    if '--author' in sys.argv:
        tests += [copied / 'tests/test_app_service_reset.cpp']
    for allowed in (0, 1):
        binary = copied / ('review-' + str(allowed))
        flags = ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                 '-fno-exceptions', '-fno-rtti', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                 '-DDOCTEST_CONFIG_NO_EXCEPTIONS', '-DAPP_TEST_CONFIGURED_BUTTONS=1',
                 '-DMOTORS_ALLOWED=' + str(allowed), '-DMATCH=' + str(allowed),
                 '-I', copied / 'src', '-I', copied / 'tests', '-isystem', copied / 'host/third_party']
        run([*flags, *sources, *tests, copied / 'host/motor_gate_main.cpp', '-o', binary])
        run([binary, '--no-colors'])
print(receipt)
