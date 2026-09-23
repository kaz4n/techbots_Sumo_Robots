# Checks the source-derived fixture itself before introducing opaque production code.
# Retains complete compiler and execution streams including failures as evidence.
# Linux/WSL only and never opens a serial, SSH, ADB or MCU connection.
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

root=Path(__file__).resolve().parents[2]
fixture=Path(__file__).resolve().parent
receipts=root/'state/analysis/P2_imu_bus_raw/author_receipts'
receipts.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='sumo-i2c-fixture-',dir='/dev/shm') as tmp:
    binary=Path(tmp)/'fixture'
    commands=[['g++','-std=c++17','-Wall','-Wextra','-Wpedantic','-Werror','-fno-exceptions','-fno-rtti',
        '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS','-I',str(fixture),'-isystem',str(root/'host/third_party'),
        *[str(fixture/f) for f in ('fixture_cases.cc','native_fixture.cc','isolation.cc','test_main.cc')],
        '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free','-o',str(binary)],
        [str(binary),'--no-colors']]
    for case in ('cases.cc','failure_cases.cc','timing_cases.cc','ownership_cases.cc','metadata_cases.cc','config_cases.cc'):
        commands.append(['g++','-std=c++17','-Wall','-Wextra','-Wpedantic','-Werror','-fno-exceptions','-fno-rtti',
            '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS','-I',str(fixture),'-I',str(root/'src'),
            '-isystem',str(root/'host/third_party'),'-c',str(fixture/case),'-o',str(Path(tmp)/(case+'.o'))])
    for argv in commands:
        result=subprocess.run(argv,text=True,capture_output=True,timeout=90)
        payload={'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
                 'capture':'subprocess text=True; newline normalized'}
        (receipts/f'fixture_{time.time_ns()}.json').write_bytes((json.dumps(payload,indent=2)+'\n').encode())
        print(result.stdout+result.stderr)
        if result.returncode:raise SystemExit(result.returncode)
