# Runs the independent 25Hz candidate tests with unchanged locked safety cases.
# Keeps alternate-rate expectations out of the production CMake suite.
# Captures compiler/run statuses and hashes in a separate offline receipt.
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import recorder_memory_build
OUT = ROOT/'state/analysis/P2_memory_validation_raw'
receipt = OUT/'candidate_host.json'
if receipt.exists():
    raise SystemExit('Refusing to overwrite candidate host receipt')
candidate = recorder_memory_build.prepare_source(25)
build = candidate/'host_checks'
build.mkdir()
sources = [ROOT/'tests/candidates/recorder25.cc',
           *sorted((ROOT/'tests/locked').glob('*.cpp')),
           *sorted((candidate/'src/core').glob('*.cpp')),
           candidate/'src/hal/recorder.cpp', candidate/'src/hal/recorder_frames.cpp']
report = dict(candidate=str(candidate), start_utc=datetime.now(timezone.utc).isoformat(),
              scope='Synthetic host fixtures only; no hardware measurements',
              source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              checks=[])
base = ['g++','-std=c++17','-Wall','-Wextra','-Wpedantic','-Werror',
        '-fno-exceptions','-fno-rtti','-DDOCTEST_CONFIG_NO_EXCEPTIONS',
        '-I'+str(candidate/'src'),'-isystem',str(ROOT/'host/third_party'),
        '-I'+str(ROOT/'tests')]
for name, options in [('normal',['-O2']), ('sanitize',['-O1','-g','-fsanitize=address,undefined',
                                                     '-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
    binary = build/name
    commands = [base+options+[str(p) for p in sources]+['-o',str(binary)], [str(binary)]]
    for action, command in zip(('compile','run'), commands):
        started = time.monotonic()
        result = subprocess.run(command,text=True,capture_output=True)
        row = dict(name=name+'_'+action, argv=command, exit_status=result.returncode,
                   seconds=time.monotonic()-started, stdout=result.stdout, stderr=result.stderr)
        report['checks'].append(row)
        receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(row['name'], row['exit_status'], row['seconds'], flush=True)
        if result.returncode:
            print(result.stdout, result.stderr)
            raise SystemExit(result.returncode)
report['end_utc'] = datetime.now(timezone.utc).isoformat()
receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
