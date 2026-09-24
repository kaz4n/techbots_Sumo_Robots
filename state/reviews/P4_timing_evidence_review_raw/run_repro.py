"""Execute the frozen D129 private reproducer on the host only, retaining logs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
name = sys.argv[1]
assert name.replace('_', '').isalnum()
receipt = OUT / (name + '.json')
assert not receipt.exists(), 'Never overwrite prior reviewer evidence'
freeze = json.loads((OUT / 'repro_freeze.json').read_text(encoding='utf-8-sig'))
assert hashlib.sha256((OUT / 'repro_original.cc').read_bytes()).hexdigest() == freeze['oracle_sha256']
WORK = Path(tempfile.mkdtemp(prefix='sumox_d129_repro_', dir='/dev/shm'))
FIX = WORK / 'fixture'
for directory in ('src', 'tests', 'host'):
    shutil.copytree(ROOT / directory, FIX / directory)
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted((ROOT / 'src').rglob('*')) if p.is_file()}
sources = sorted((FIX / 'src/core').glob('*.cpp')) + sorted((FIX / 'src/app').glob('*.cpp'))
hal = ('ui power_inputs imu_heading imu_adapter ui_display motors recorder_frames '
       'recorder recorder_csv recorder_dump line_qtr_adapter qtr_cal qtr_cal_format').split()
sources += [FIX / 'src/hal' / (p + '.cpp') for p in hal]
sources += [FIX / 'host/motor_gate_main.cpp', OUT / 'repro_original.cc']
cmake = 'cmake_minimum_required(VERSION 3.20)\nproject(d129_repro LANGUAGES CXX)\nset(CMAKE_CXX_STANDARD 17)\n'
cmake += 'add_executable(repro\n' + ''.join(f' "{p}"\n' for p in sources) + ')\n'
cmake += f'target_include_directories(repro PRIVATE "{FIX}/src" "{FIX}/tests" "{FIX}/host/third_party")\n'
cmake += 'target_compile_definitions(repro PRIVATE DOCTEST_CONFIG_NO_EXCEPTIONS SUMOX_P4_REACTIVE=1 SUMOX_TIMING_EVIDENCE=1 MOTORS_ALLOWED=1)\n'
cmake += 'target_compile_options(repro PRIVATE -Wall -Wextra -Wpedantic -Werror -fno-exceptions -fno-rtti)\n'
(WORK / 'CMakeLists.txt').write_text(cmake)
record = dict(started_utc=datetime.now(timezone.utc).isoformat(), source_sha256=hashes, commands=[])
commands = [('configure', ['cmake', '-S', str(WORK), '-B', str(WORK / 'build')]),
            ('build', ['cmake', '--build', str(WORK / 'build'), '--parallel', '2']),
            ('test', [str(WORK / 'build/repro')])]
status = 0
for stage, command in commands:
    result = subprocess.run(command, text=True, capture_output=True)
    (OUT / (name + '_' + stage + '.log')).write_text(result.stdout + result.stderr)
    record['commands'].append(dict(stage=stage, command=command, exit_code=result.returncode))
    if result.returncode:
        status = result.returncode
        break
record.update(exit_code=status, finished_utc=datetime.now(timezone.utc).isoformat())
receipt.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(dict(name=name, exit_code=status, commands=record['commands'])))
raise SystemExit(status)
