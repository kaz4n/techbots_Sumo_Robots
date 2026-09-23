"""Run D105 review in a private WSL source copy; preserve raw commands/hashes."""
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
receipt = RAW / ('host_' + str(time.time_ns()) + '.json')
record = {'results': [], 'scope': 'Private WSL source copy; synthetic callbacks only'}


def run(argv, cwd):
    result = subprocess.run(list(map(str, argv)), cwd=cwd, capture_output=True,
                            text=True, timeout=600)
    record['results'].append(dict(argv=list(map(str, argv)), cwd=str(cwd),
        returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    print(result.stdout, result.stderr, flush=True)
    return result.returncode


with tempfile.TemporaryDirectory(prefix='d105-review-') as temporary:
    copied = Path(temporary)
    for folder in ('src', 'tests', 'host', 'tools', 'bench'):
        origin = ROOT / folder
        if folder == 'src' and '--frozen' in sys.argv:
            origin = ROOT / 'state/analysis/P2_calibration_delivery_raw/target_sources_c05916c6/src'
        shutil.copytree(origin, copied / folder,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    record['source_hashes'] = {p.relative_to(copied).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in copied.rglob('*') if p.is_file()}
    if '--original' in sys.argv:
        shutil.copyfile(RAW / 'initial_runtime.cpp', copied / 'src/app/runtime.cpp')
        record['original_runtime_sha256'] = hashlib.sha256((RAW/'initial_runtime.cpp').read_bytes()).hexdigest()
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    if '--host' in sys.argv:
        code = run(['bash', 'tools/test_host.sh'], copied)
        log = copied / 'build/host/Testing/Temporary/LastTest.log'
        if log.exists(): shutil.copy2(log, RAW / (receipt.stem + '_LastTest.log'))
        if code: raise SystemExit(code)
    if '--parser' in sys.argv:
        if run(['python3', '-m', 'unittest', 'tests.tooling.test_qtr_config', '-v'], copied):
            raise SystemExit(1)
    if '--transport' in sys.argv:
        config = copied / 'src/config.h'
        content = config.read_text()
        for name, value in [('BUTTON_WINDOWS_CONFIGURED','1U'),
            ('BUTTON_LOW_RAW','{0U, 900U, 1900U, 2900U}'),
            ('BUTTON_HIGH_RAW','{100U, 1100U, 2100U, 3100U}')]:
            content, count = re.subn(r'(\b'+name+r'(?:\[4\])?\s*=\s*)[^;]+;', r'\g<1>'+value+';', content)
            assert count == 1
        config.write_text(content)
        record['synthetic_button_config_sha256'] = hashlib.sha256(config.read_bytes()).hexdigest()
        cases = copied / 'tests/tooling/calibration_output_cases.cc'
        cases.write_bytes(cases.read_bytes() + b'\n' + (RAW/'extra_cases.cc').read_bytes())
        record['review_cases_sha256'] = hashlib.sha256(cases.read_bytes()).hexdigest()
        hal = ['motors.cpp','recorder.cpp','recorder_frames.cpp','recorder_csv.cpp','recorder_dump.cpp',
               'power_inputs.cpp','ui.cpp','imu_heading.cpp','imu_adapter.cpp','line_qtr_adapter.cpp',
               'qtr_cal.cpp','qtr_cal_format.cpp','ui_display.cpp']
        sources = sorted((copied/'src/core').glob('*.cpp')) + sorted((copied/'src/app').glob('*.cpp'))
        sources += [copied/'src/hal'/name for name in hal] + [cases]
        common = ['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror',
                  '-fno-exceptions','-fno-rtti','-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                  '-DAPP_TEST_CONFIGURED_BUTTONS=1','-DMATCH=0',
                  '-DMOTORS_ALLOWED=' + ('1' if '--allowed-one' in sys.argv else '0'),
                  '-I',copied/'src','-I',copied/'tests','-isystem',copied/'host/third_party']
        profiles = [('normal', [])]
        if '--sanitize' in sys.argv:
            profiles.append(('asan_ubsan',['-g','-fsanitize=address,undefined',
                '-fno-sanitize-recover=all','-fno-omit-frame-pointer','-no-pie']))
        any_failed = False
        for label, flags in profiles:
            binary = copied / label
            if run([*common,*flags,*sources,'-o',binary],copied): raise SystemExit(1)
            args = [binary,'--no-colors']
            if '--reviewer-only' in sys.argv: args += ['--test-case=*D105 reviewer*']
            any_failed = bool(run(args,copied)) or any_failed
        if any_failed: raise SystemExit(1)
print(receipt)
