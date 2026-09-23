"""Run D075 builds/tests in one WSL lifetime so RAM-backed artifacts survive."""
import os
from pathlib import Path
import subprocess
import sys

os.environ['TMPDIR'] = '/dev/shm'
recorder = str(Path(__file__).with_name('P2_motor_gate_record.py'))
for mode in ('normal', 'sanitizer'):
    build = '/dev/shm/sumox-d075-' + mode
    configure = ['cmake', '-S', 'host', '-B', build, '-DCMAKE_BUILD_TYPE=Debug']
    if mode == 'sanitizer':
        configure += ['-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer',
                      '-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined']
    steps = [('configure', configure), ('build', ['cmake', '--build', build, '--parallel', '2']),
             ('default', [build + '/sumox26_tests']),
             ('enabled', [build + '/motor_gate_enabled_tests'])]
    for name, command in steps:
        result = subprocess.run([sys.executable, recorder, mode + '_' + name, *command])
        if result.returncode:
            raise SystemExit(result.returncode)
