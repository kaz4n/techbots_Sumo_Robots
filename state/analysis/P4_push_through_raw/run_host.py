"""Run D131 source-bound host fixtures, retaining receipts before releasing RAM."""
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
name, duration_text, flags_text = sys.argv[1:]
assert name.replace('_', '').isalnum()
duration = int(duration_text)
assert duration in (0, 20, 100)
flags = set(flags_text.split(',')) - {'plain'}
assert flags <= {'full', 'sanitize', 'configured', 'timing', 'review', 'legacy'}
assert 'full' not in flags or (duration == 0 and flags <= {'full', 'review'})
freeze = json.loads((out/'freeze.json').read_text())
for path, expected in freeze.items():
    assert hashlib.sha256((root/path).read_bytes()).hexdigest() == expected, path
build = Path('/dev/shm')/('sumox_d131_'+name)
assert not build.exists(), 'Do not overwrite prior runs'
assert not (out/(name+'.json')).exists(), 'Preserve original receipts'
build.mkdir()
source = root
record = {'name': name, 'duration_ms': duration, 'flags': sorted(flags),
          'start_utc': datetime.now(timezone.utc).isoformat(), 'commands': [],
          'input_freeze_sha256': hashlib.sha256((out/'freeze.json').read_bytes()).hexdigest()}
if duration or 'configured' in flags:
    source = build/'fixture'
    for directory in ('src', 'tests', 'host', 'bench'):
        shutil.copytree(root/directory, source/directory,
                        ignore=shutil.ignore_patterns('__pycache__'))
    config = source/'src/config.h'
    text = config.read_text()
    replacements = {'EDGE_PUSH_THROUGH_MS = 0U': f'EDGE_PUSH_THROUGH_MS = {duration}U'}
    if 'configured' in flags:
        replacements.update({
            'BUTTON_WINDOWS_CONFIGURED = 0U': 'BUTTON_WINDOWS_CONFIGURED = 1U',
            'BUTTON_LOW_RAW[4] = {0U, 0U, 0U, 0U}': 'BUTTON_LOW_RAW[4] = {0U, 900U, 1900U, 2900U}',
            'BUTTON_HIGH_RAW[4] = {0U, 0U, 0U, 0U}': 'BUTTON_HIGH_RAW[4] = {100U, 1100U, 2100U, 3100U}',
        })
    for before, after in replacements.items():
        assert text.count(before) == 1, before
        text = text.replace(before, after)
    config.write_text(text)
    shutil.copyfile(config, out/(name+'_config.h'))
    record['synthetic_replacements'] = replacements
commands = [['cmake', '-S', str(source/'host'), '-B', str(build/'build'),
             '-DCMAKE_BUILD_TYPE=Debug']]
compiler = []
if 'sanitize' in flags:
    compiler += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie']
    commands[0] += ['-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined -no-pie']
if 'configured' in flags:
    compiler += ['-DAPP_TEST_CONFIGURED_BUTTONS=1']
if 'timing' in flags:
    compiler += ['-DSUMOX_TIMING_EVIDENCE=1']
if compiler:
    commands[0] += ['-DCMAKE_CXX_FLAGS='+' '.join(compiler)]
commands += [['cmake', '--build', str(build/'build'), '--parallel', '1']]
if 'full' not in flags:
    prefix = 'timing_evidence' if 'legacy' in flags else 'push_through'
    commands[-1] += ['--target', prefix+'_m0_tests', prefix+'_m1_tests']
commands += [['ctest', '--test-dir', str(build/'build'), '--output-on-failure']]
if 'full' not in flags:
    commands[-1] += ['-R', '^'+prefix+'_']
if 'review' in flags:
    commands += [[sys.executable,
                  str(root/'state/reviews/P4_push_through_review_raw/run_private.py'),
                  str(source), str(build/'build'), name]]
environment = os.environ.copy()
environment['ASAN_OPTIONS'] = 'detect_leaks=1:halt_on_error=1'
environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
code = 0
with (out/(name+'.txt')).open('wb') as log:
    for argv in commands:
        result = subprocess.run(argv, cwd=root, env=environment, stdout=log, stderr=subprocess.STDOUT)
        record['commands'].append({'argv': argv, 'returncode': result.returncode})
        log.flush()
        if result.returncode:
            code = result.returncode
            break
archive = out/(name+'_build')
archive.mkdir()
for relative in ('CMakeCache.txt', 'Testing/Temporary/LastTest.log',
                 'Testing/Temporary/LastTestsFailed.log'):
    path = build/'build'/relative
    if path.is_file():
        shutil.copyfile(path, archive/path.name)
record['returncode'] = code
record['end_utc'] = datetime.now(timezone.utc).isoformat()
(out/(name+'.json')).write_text(json.dumps(record, indent=2)+'\n')
print(name, 'exit', code)
print((out/(name+'.txt')).read_text(errors='replace')[-6000:])
# These are exclusively generated RAM-backed host objects, never target evidence.
assert build.parent == Path('/dev/shm') and build.name == 'sumox_d131_'+name
if code == 0:
    shutil.rmtree(build)
sys.exit(code)
