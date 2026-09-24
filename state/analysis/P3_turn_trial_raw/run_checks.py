"""Capture D124 pure-helper and unchanged-host verification before WSL exits."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
profile = sys.argv[1]
assert profile in ('normal', 'sanitize', 'regression', 'registry')
freeze = json.loads((out/'freeze.json').read_text())
for name, digest in freeze['sha256'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest() == digest, name
build = Path('/dev/shm')/('sumox_d124_'+profile)
build.mkdir(exist_ok=False)
env = os.environ.copy()
env['ASAN_OPTIONS'] = 'detect_leaks=1:halt_on_error=1'
env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
if profile in ('normal', 'sanitize'):
    command = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
               '-fno-exceptions', '-fno-rtti', '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
               '-I', 'src', '-isystem', 'host/third_party', 'host/motor_gate_main.cpp',
               'src/core/motion.cpp', 'src/core/turn_trial.cpp', 'tests/test_turn_trial.cpp',
               '-o', str(build/'turn_trial_tests')]
    if profile == 'sanitize':
        command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie']
    commands = [command, [str(build/'turn_trial_tests')]]
elif profile == 'registry':
    env['PYTHONPATH'] = 'tests/tooling'
    commands = [['python3', '-m', 'unittest', 'tests.tooling.test_runtime_config_registry']]
else:
    commands = [['cmake', '-S', 'host', '-B', str(build), '-DCMAKE_BUILD_TYPE=Debug'],
                ['cmake', '--build', str(build), '--parallel', '4'],
                ['ctest', '--test-dir', str(build), '--output-on-failure']]
record = {'start_utc': datetime.now(timezone.utc).isoformat(), 'commands': []}
code = 0
with (out/(profile+'.txt')).open('wb') as log:
    for argv in commands:
        result = subprocess.run(argv, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        record['commands'].append({'argv': argv, 'returncode': result.returncode})
        log.flush()
        if result.returncode:
            code = result.returncode
            break
if profile == 'regression':
    for name in ('CMakeCache.txt', 'Testing/Temporary/LastTest.log',
                 'Testing/Temporary/LastTestsFailed.log'):
        path = build/name
        if path.is_file():
            shutil.copyfile(path, out/('regression_'+path.name))
record.update(returncode=code, end_utc=datetime.now(timezone.utc).isoformat())
(out/(profile+'.json')).write_text(json.dumps(record, indent=2)+'\n')
print(profile, 'exit', code)
print((out/(profile+'.txt')).read_text(errors='replace')[-3000:])
sys.exit(code)
