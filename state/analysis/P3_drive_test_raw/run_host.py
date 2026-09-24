"""Run source-bound D123 host validation and archive logs before WSL exits."""
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
assert profile in ('normal', 'sanitize', 'configured', 'configured_sanitize')
run_name = sys.argv[2] if len(sys.argv) > 2 else profile
assert run_name.replace('_', '').isalnum()
focused = profile.startswith('configured') or len(sys.argv) > 2
freeze = json.loads((out/'freeze.json').read_text())
for name, expected in freeze['sha256'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest() == expected, name

build = Path('/dev/shm')/('sumox_d123_'+run_name)
assert not build.exists(), 'Never overwrite a prior run'
build.mkdir()
source = root
if profile.startswith('configured'):
    source = build/'fixture'
    for name in ('src', 'tests', 'host', 'bench'):
        shutil.copytree(root/name, source/name, ignore=shutil.ignore_patterns('__pycache__'))
    config = source/'src/config.h'
    text = config.read_text()
    replacements = {
        'BUTTON_WINDOWS_CONFIGURED = 0U': 'BUTTON_WINDOWS_CONFIGURED = 1U',
        'BUTTON_LOW_RAW[4] = {0U, 0U, 0U, 0U}': 'BUTTON_LOW_RAW[4] = {0U, 900U, 1900U, 2900U}',
        'BUTTON_HIGH_RAW[4] = {0U, 0U, 0U, 0U}': 'BUTTON_HIGH_RAW[4] = {100U, 1100U, 2100U, 3100U}',
    }
    for before, after in replacements.items():
        assert text.count(before) == 1, before
        text = text.replace(before, after)
    config.write_text(text)

commands = [['cmake', '-S', str(source/'host'), '-B', str(build/'build'),
             '-DCMAKE_BUILD_TYPE=Debug']]
flags = []
if 'sanitize' in profile:
    flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie']
    commands[0] += ['-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined -no-pie']
if profile.startswith('configured'):
    flags += ['-DAPP_TEST_CONFIGURED_BUTTONS=1']
if flags:
    commands[0] += ['-DCMAKE_CXX_FLAGS='+' '.join(flags)]
commands += [['cmake', '--build', str(build/'build'), '--parallel', '4']]
if focused:
    commands[-1] += ['--target', 'drive_test_m0_tests', 'drive_test_m1_tests']
commands += [['ctest', '--test-dir', str(build/'build'), '--output-on-failure']]
if focused:
    commands[-1] += ['-R', '^drive_test_']

record = {'profile': profile, 'run_name': run_name, 'focused': focused,
          'start_utc': datetime.now(timezone.utc).isoformat(),
          'synthetic_config_overlay': profile.startswith('configured'), 'commands': []}
env = os.environ.copy()
env['ASAN_OPTIONS'] = 'detect_leaks=1:halt_on_error=1'
env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
code = 0
with (out/(run_name+'.txt')).open('wb') as log:
    for argv in commands:
        result = subprocess.run(argv, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        record['commands'].append({'argv': argv, 'returncode': result.returncode})
        log.flush()
        if result.returncode:
            code = result.returncode
            break
archive = out/(run_name+'_build')
archive.mkdir(exist_ok=False)
for relative in ('CMakeCache.txt', 'Testing/Temporary/LastTest.log',
                 'Testing/Temporary/LastTestsFailed.log'):
    path = build/'build'/relative
    if path.is_file():
        shutil.copyfile(path, archive/path.name)
record['returncode'] = code
record['end_utc'] = datetime.now(timezone.utc).isoformat()
(out/(run_name+'.json')).write_text(json.dumps(record, indent=2)+'\n')
print(profile, 'exit', code)
print((out/(run_name+'.txt')).read_text(errors='replace')[-4500:])
sys.exit(code)
