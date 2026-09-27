"""Run the frozen D244 B7 oracle and unchanged ordinary safety checks serially.

Retain source identities and raw output before removing only owned host scratch.
These callback and copied-source fixtures provide no native or physical evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

from tests.tooling.test_epoch_timing import HAL, APP

ROOT = Path(__file__).resolve().parents[2]
ORDINARY = ('tests/locked/test_countdown.cpp', 'tests/locked/test_countdown_lifecycle.cpp',
            'tests/locked/test_countdown_integration.cpp', 'tests/locked/test_countdown_services.cpp',
            'tests/locked/test_edge_escape.cpp', 'tests/locked/test_edge_guard.cpp',
            'tests/locked/test_edge_headon.cpp', 'tests/locked/test_motor_gate.cpp',
            'tests/test_governor.cpp')


def pins():
    paths = list((ROOT / 'src').rglob('*')) + list((ROOT / 'tests/fixtures').rglob('*'))
    paths += [ROOT / p for p in (*ORDINARY, 'tests/test_b7_brownout.cc',
        'tests/tooling/test_b7_brownout.py', 'tests/tooling/test_epoch_timing.py',
        'host/CMakeLists.txt', 'host/motor_gate_main.cpp', 'host/third_party/doctest.h',
        'state/analysis/P2_b7_brownout_contract.md')]
    return {str(p.relative_to(ROOT)): {'bytes': p.stat().st_size,
        'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted(paths) if p.is_file()}


def execute(raw, receipt, argv, expect_failure=False, timeout=300):
    argv = list(map(str, argv))
    number, started = len(receipt['commands']), time.time()
    try:
        result = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=timeout)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        code, stdout, stderr = 124, error.stdout or b'', (error.stderr or b'') + b'\nTIMEOUT\n'
    (raw / f'{number:02d}.stdout').write_bytes(stdout)
    (raw / f'{number:02d}.stderr').write_bytes(stderr)
    receipt['commands'].append({'argv': argv, 'returncode': code,
        'expected_compile_rejection': expect_failure, 'seconds': time.time() - started})
    print(f'{number:02d} rc={code} {Path(argv[0]).name}', flush=True)
    if (expect_failure and code != 1) or (not expect_failure and code != 0):
        raise RuntimeError(f'Unexpected command {number} result; raw output retained')
    return stdout, stderr


def configured_source(scratch, receipt):
    source = scratch / 'configured/src'
    shutil.copytree(ROOT / 'src', source)
    config = source / 'config.h'
    text = config.read_text()
    for name, value in (('BUTTON_WINDOWS_CONFIGURED', '1U'),
                        ('BUTTON_LOW_RAW', '{0U, 900U, 1900U, 2900U}'),
                        ('BUTTON_HIGH_RAW', '{100U, 1100U, 2100U, 3100U}')):
        text, count = re.subn(r'(\b' + name + r'(?:\[4\])?\s*=\s*)[^;]+;',
                              r'\g<1>' + value + ';', text)
        if count != 1:
            raise RuntimeError(f'Unexpected synthetic fixture declaration: {name}')
    config.write_text(text)
    receipt['synthetic_buttons'] = {'source': text,
        'production_sha256': hashlib.sha256((ROOT / 'src/config.h').read_bytes()).hexdigest(),
        'configured_sha256': hashlib.sha256(config.read_bytes()).hexdigest(),
        'purpose': 'Synthetic host A1 windows only; all production setup grants unchanged'}
    return source


def compile_run(scratch, run, source, motors, configured=False, ordinary=False):
    label = f'{"ordinary" if ordinary else "b7"}_m{motors}_{"synthetic" if configured else "default"}'
    sources = sorted((source / 'core').glob('*.cpp'))
    sources += [source / 'hal' / p for p in HAL] + [source / 'app' / p for p in APP]
    tests = ORDINARY if ordinary else ('tests/test_b7_brownout.cc',)
    sources += [ROOT / p for p in (*tests, 'host/motor_gate_main.cpp')]
    binary = scratch / label
    definitions = ['-DMATCH=0', f'-DMOTORS_ALLOWED={motors}']
    if not ordinary:
        definitions += ['-DSUMOX_B7_BROWNOUT=1']
    if configured:
        definitions += ['-DAPP_TEST_CONFIGURED_BUTTONS=1']
    run(['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
         '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined', '-fno-sanitize-recover=all',
         '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS', *definitions,
         '-I', source, '-I', ROOT / 'tests', '-isystem', ROOT / 'host/third_party',
         *sources, '-o', binary])
    output, _ = run([binary, '--no-colors'])
    print(output.decode(), end='', flush=True)
    if b'Status: SUCCESS!' not in output:
        raise RuntimeError('Missing successful doctest closure')


def exclusions(scratch, run):
    probe = scratch / 'profile.cc'
    probe.write_text('#include "config.h"\nint main(){return 0;}\n')
    common = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
              '-DMOTORS_ALLOWED=0', '-fsyntax-only', '-I', ROOT / 'src', probe]
    profiles = ('MATCH', 'SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
                'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
                'SUMOX_P5_ABORT_TIMING', 'SUMOX_MOTOR_FAULT_PROBE')
    for profile in profiles:
        flags = [f'-D{profile}=1']
        if profile == 'SUMOX_TIMING_EVIDENCE':
            flags += ['-DSUMOX_P4_REACTIVE=1']
        run([*common, *flags])
        _, error = run([*common, *flags, '-DSUMOX_B7_BROWNOUT=1'], expect_failure=True)
        if b'B7 brownout' not in error:
            raise RuntimeError(f'Missing dedicated B7 exclusion diagnostic for {profile}')
    for value in ('2', '-1'):
        _, error = run([*common, f'-DSUMOX_B7_BROWNOUT={value}'], expect_failure=True)
        if b'SUMOX_B7_BROWNOUT must be 0 or 1' not in error:
            raise RuntimeError('Missing B7 boolean diagnostic')
    probe.write_text('#include "config.h"\nstatic_assert(SUMOX_B7_BROWNOUT==0);\n')
    run(common)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    args = parser.parse_args()
    raw = args.raw.resolve()
    raw.mkdir(parents=True, exist_ok=False)
    scratch = Path(tempfile.mkdtemp(prefix='sumo-d244-', dir='/dev/shm'))
    receipt = {'schema': 'd244-focused-host-v1', 'target_evidence': False,
        'commands': [], 'started_unix': time.time(), 'scratch': str(scratch)}
    run = lambda argv, **kwargs: execute(raw, receipt, argv, **kwargs)
    try:
        receipt['pins_before'] = pins()
        run(['g++', '--version'])
        source = configured_source(scratch, receipt)
        for motors in (0, 1):
            compile_run(scratch, run, ROOT / 'src', motors)
            compile_run(scratch, run, source, motors, configured=True)
        for motors in (0, 1):
            compile_run(scratch, run, ROOT / 'src', motors, ordinary=True)
        exclusions(scratch, run)
        receipt['pins_after'] = pins()
        if receipt['pins_before'] != receipt['pins_after']:
            raise RuntimeError('Inputs changed during focused validation')
        receipt['status'] = 'PASS_HOST_ONLY'
    except BaseException as error:
        receipt['status'], receipt['error'] = 'FAIL', repr(error)
        raise
    finally:
        receipt['finished_unix'] = time.time()
        receipt['scratch_bytes_before_cleanup'] = sum(p.stat().st_size for p in scratch.rglob('*') if p.is_file())
        shutil.rmtree(scratch)
        receipt['scratch_removed'] = not scratch.exists()
        (raw / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
