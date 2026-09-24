#!/usr/bin/env python3
"""Validate frozen D120 targets with only the authorized synthetic ADC overlay."""
import datetime
import difflib
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

REPO = Path('/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots')
OUT = REPO / 'state/analysis/P2_stand_integration_raw/configured'
WORK = Path('/dev/shm/sumox_d120_configured')
SOURCE = WORK / 'source'
COPIED = ('src', 'host', 'tests', 'bench/motor_stand', 'bench/recorder')
TARGETS = ('stand_integration_m0_tests', 'stand_integration_m1_tests')
commands = []


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def snapshot(base):
    return {str(path.relative_to(base)): sha(path)
            for folder in COPIED for path in sorted((base / folder).rglob('*'))
            if path.is_file()}


def run(name, args, extra_env=None):
    env = os.environ.copy()
    env.update(extra_env or {})
    command = {'name': name, 'argv': args, 'cwd': str(WORK),
               'environment_overrides': extra_env or {}, 'started_at': now(),
               'shell_display': shlex.join(args)}
    commands.append(command)
    write_json('commands.json', commands)
    with (OUT / f'{name}.stdout.txt').open('w') as stdout, \
         (OUT / f'{name}.stderr.txt').open('w') as stderr:
        result = subprocess.run(args, cwd=WORK, env=env, stdout=stdout, stderr=stderr)
    command['exit_code'] = result.returncode
    command['finished_at'] = now()
    write_json('commands.json', commands)
    print(f'{name}: exit {result.returncode}', flush=True)
    if result.returncode != 0:
        raise RuntimeError(f'{name} failed with exit {result.returncode}; no source/test repair made')


before = snapshot(REPO)
write_json('original_before.json', before)
oracle = json.loads((REPO / 'state/analysis/P2_stand_integration_raw/oracle/oracle_freeze.json').read_text())
freeze_check = [{'path': row['path'], 'expected': row['sha256'],
                 'actual': sha(REPO / row['path'])} for row in oracle['files']]
write_json('oracle_before.json', freeze_check)
if any(row['actual'] != row['expected'] for row in freeze_check):
    raise SystemExit('Frozen public/oracle source mismatch before execution')
WORK.mkdir(exist_ok=False)
SOURCE.mkdir()
for folder in COPIED:
    shutil.copytree(REPO / folder, SOURCE / folder)
copied_before = snapshot(SOURCE)
write_json('isolated_before_overlay.json', copied_before)
if copied_before != before:
    raise SystemExit('Source copy mismatch before overlay')
path = SOURCE / 'src/config.h'
original = path.read_bytes()
overlay = original
for old, new in (
    (b'BUTTON_WINDOWS_CONFIGURED = 0U;', b'BUTTON_WINDOWS_CONFIGURED = 1U;'),
    (b'BUTTON_LOW_RAW[4] = {0U, 0U, 0U, 0U};', b'BUTTON_LOW_RAW[4] = {0U, 900U, 1900U, 2900U};'),
    (b'BUTTON_HIGH_RAW[4] = {0U, 0U, 0U, 0U};', b'BUTTON_HIGH_RAW[4] = {100U, 1100U, 2100U, 3100U};'),
):
    if overlay.count(old) != 1:
        raise SystemExit(f'Expected exactly one overlay anchor: {old!r}')
    overlay = overlay.replace(old, new)
path.write_bytes(overlay)
(OUT / 'config_overlay.diff').write_text(''.join(difflib.unified_diff(
    original.decode().splitlines(keepends=True), overlay.decode().splitlines(keepends=True),
    fromfile='original/src/config.h', tofile='isolated/src/config.h')))
isolated = snapshot(SOURCE)
write_json('isolated_after_overlay.json', isolated)
changes = [name for name in before if before[name] != isolated[name]]
if changes != ['src/config.h']:
    raise SystemExit(f'Unexpected overlay changes: {changes}')
summary = {'started_at': now(), 'profile': 'synthetic configured ADC only',
           'copied_folders': list(COPIED), 'workspace': str(WORK), 'status': 'RUNNING',
           'hardware_actions': False, 'source_edits': ['isolated src/config.h only'],
           'frozen_tests_unchanged': True}
write_json('summary.json', summary)
try:
    for profile in ('normal', 'sanitizer'):
        build = WORK / profile
        flags = '-DAPP_TEST_CONFIGURED_BUTTONS=1'
        args = ['cmake', '-S', str(SOURCE / 'host'), '-B', str(build), '-DCMAKE_BUILD_TYPE=Debug']
        if profile == 'sanitizer':
            flags += ' -fsanitize=address,undefined -fno-omit-frame-pointer -fno-pie'
            args.append('-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined -no-pie')
        args.append('-DCMAKE_CXX_FLAGS=' + flags)
        run(profile + '_configure', args)
        run(profile + '_build', ['cmake', '--build', str(build), '--parallel', '2', '--target', *TARGETS])
        for target in TARGETS:
            env = {'ASAN_OPTIONS': 'detect_leaks=1:abort_on_error=1',
                   'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1'} if profile == 'sanitizer' else None
            name = profile + '_' + target
            run(name, [str(build / target)], env)
            output = (OUT / f'{name}.stdout.txt').read_text()
            if not any('test cases:' in line and line.split('|')[0].split(':')[1].strip() == '19'
                       for line in output.splitlines()):
                raise RuntimeError(f'{name} did not report exactly 19 executed test cases')
    summary['status'] = 'PASS'
except BaseException as error:
    summary['status'] = 'FAIL'
    summary['error'] = str(error)
finally:
    original_after = snapshot(REPO)
    isolated_after = snapshot(SOURCE)
    write_json('original_after.json', original_after)
    write_json('isolated_after_execution.json', isolated_after)
    oracle_after = [{'path': row['path'], 'expected': row['sha256'],
                     'actual': sha(REPO / row['path'])} for row in oracle['files']]
    write_json('oracle_after.json', oracle_after)
    summary['original_unchanged'] = original_after == before
    summary['isolated_unchanged_after_overlay'] = isolated_after == isolated
    summary['oracle_matches_before_and_after'] = oracle_after == freeze_check
    summary['finished_at'] = now()
    summary['commands'] = commands
    if not all((summary['original_unchanged'], summary['isolated_unchanged_after_overlay'],
                summary['oracle_matches_before_and_after'])):
        summary['status'] = 'FAIL'
    write_json('summary.json', summary)
print(json.dumps({key: value for key, value in summary.items() if key != 'commands'}, indent=2), flush=True)
sys.exit(0 if summary['status'] == 'PASS' else 1)
