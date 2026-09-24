"""Isolated configured-source Runtime probes; no transport or firmware staging."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
WORK = Path('/dev/shm/sumox_d123_reviewer_private_v3')
WORK.mkdir(exist_ok=True)
FIX = WORK / 'fixture'
FIX.mkdir(exist_ok=True)
for directory in ('src', 'tests', 'host'):
    shutil.copytree(ROOT / directory, FIX / directory, dirs_exist_ok=True)
config = FIX / 'src/config.h'
text = config.read_text()
for before, after in (
    ('BUTTON_WINDOWS_CONFIGURED = 0U', 'BUTTON_WINDOWS_CONFIGURED = 1U'),
    ('BUTTON_LOW_RAW[4] = {0U, 0U, 0U, 0U}',
     'BUTTON_LOW_RAW[4] = {0U, 900U, 1900U, 2900U}'),
    ('BUTTON_HIGH_RAW[4] = {0U, 0U, 0U, 0U}',
     'BUTTON_HIGH_RAW[4] = {100U, 1100U, 2100U, 3100U}'),
):
    if text.count(before) != 1:
        raise RuntimeError('Unrecognized configuration fixture: ' + before)
    text = text.replace(before, after)
config.write_text(text)
shutil.copy2(OUT / 'private_runtime.cc', WORK / 'private_runtime.cc')
sources = sorted((FIX / 'src/core').glob('*.cpp')) + sorted((FIX / 'src/app').glob('*.cpp'))
hal = ('ui power_inputs imu_heading imu_adapter ui_display motors recorder_frames '
       'recorder recorder_csv recorder_dump line_qtr_adapter qtr_cal qtr_cal_format').split()
sources += [FIX / 'src/hal' / (name + '.cpp') for name in hal]
sources += [FIX / 'host/motor_gate_main.cpp', WORK / 'private_runtime.cc']
cmake = '''cmake_minimum_required(VERSION 3.20)
project(private_review LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
enable_testing()
'''
for motors in (0, 1):
    target = f'private_runtime_m{motors}'
    cmake += f'add_executable({target}\n' + ''.join(f'  "{p}"\n' for p in sources) + ')\n'
    cmake += f'target_include_directories({target} PRIVATE "{FIX}/src" "{FIX}/tests" "{FIX}/host/third_party")\n'
    cmake += f'target_compile_definitions({target} PRIVATE DOCTEST_CONFIG_NO_EXCEPTIONS APP_TEST_CONFIGURED_BUTTONS=1 SUMOX_P3_DRIVE_TEST=1 MOTORS_ALLOWED={motors})\n'
    cmake += f'target_compile_options({target} PRIVATE -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)\n'
    cmake += f'add_test(NAME {target} COMMAND {target})\n'
(WORK / 'CMakeLists.txt').write_text(cmake)
commands = [('configure', ['cmake', '-S', str(WORK), '-B', str(WORK / 'build')]),
            ('build', ['cmake', '--build', str(WORK / 'build'), '--parallel', '2']),
            ('tests', ['ctest', '--test-dir', str(WORK / 'build'), '--verbose'])]
results = []
for name, command in commands:
    result = subprocess.run(command, text=True, capture_output=True, timeout=600)
    (OUT / ('runtime_' + name + '.log')).write_text(result.stdout + result.stderr)
    results.append(dict(name=name, command=command, returncode=result.returncode))
    if result.returncode != 0:
        break
freeze = json.loads((ROOT / 'state/analysis/P3_drive_test_raw/freeze.json').read_text())
matches = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == expected
           for p, expected in freeze['sha256'].items()}
report = dict(result='PASS' if len(results) == 3 and all(r['returncode'] == 0 for r in results)
              and all(value for path, value in matches.items() if path.startswith('src/'))
              else 'FAIL', commands=results,
              source_freeze_matches=matches, finished_utc=datetime.now(timezone.utc).isoformat(),
              limitations=['Synthetic callback observations only; no board or motor operation.',
                           'Fixture-only ADC windows changed in isolated /dev/shm source copy.'])
(OUT / 'private_runtime_validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(dict(result=report['result'], commands=results)))
raise SystemExit(0 if report['result'] == 'PASS' else 1)
