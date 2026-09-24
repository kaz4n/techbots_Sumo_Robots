"""Run one frozen D138 host profile, retain receipts, release owned RAM scratch."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
label, flags_text = sys.argv[1:]
assert label.replace('_', '').isalnum()
flags = set(flags_text.split(',')) - {'plain'}
assert flags <= {'full', 'sanitize', 'configured', 'private'}
assert not ('full' in flags and 'configured' in flags)
assert not any((out / (label + ext)).exists() for ext in ('.json', '.txt'))
freeze_path = out / 'freeze_retry2.json'
freeze = json.loads(freeze_path.read_text())

def verify():
    for name, expected in freeze.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name

verify()
record = dict(label=label, flags=sorted(flags),
              start_utc=datetime.now(timezone.utc).isoformat(),
              input_freeze_sha256=hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
              runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              commands=[], hardware_access=False, frozen_inputs=len(freeze))
code = 1
with tempfile.TemporaryDirectory(prefix='sumox_d138_', dir='/dev/shm') as scratch:
    scratch = Path(scratch)
    source = root
    if {'configured', 'private'} & flags:
        source = scratch / 'fixture'
        for directory in ('src', 'tests', 'host', 'bench'):
            shutil.copytree(root / directory, source / directory,
                            ignore=shutil.ignore_patterns('__pycache__'))
    if 'configured' in flags:
        path = source / 'src/config.h'
        text = path.read_text()
        replacements = {
            'BUTTON_WINDOWS_CONFIGURED = 0U': 'BUTTON_WINDOWS_CONFIGURED = 1U',
            'BUTTON_LOW_RAW[4] = {0U, 0U, 0U, 0U}': 'BUTTON_LOW_RAW[4] = {0U, 900U, 1900U, 2900U}',
            'BUTTON_HIGH_RAW[4] = {0U, 0U, 0U, 0U}': 'BUTTON_HIGH_RAW[4] = {100U, 1100U, 2100U, 3100U}',
        }
        for before, after in replacements.items():
            assert text.count(before) == 1, before
            text = text.replace(before, after)
        path.write_text(text)
        record['synthetic_replacements'] = replacements
        record['fixture_config_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    if 'private' in flags:
        probe = root / 'state/reviews/P7_readiness_review_raw/probes.cc'
        copied = source / 'private_probe.cc'
        copied.write_bytes(probe.read_bytes())
        record['private_probe_sha256'] = hashlib.sha256(copied.read_bytes()).hexdigest()
        test_include = (source / 'tests').as_posix()
        with (source / 'host/CMakeLists.txt').open('a') as cmake:
            for motor in (0, 1):
                cmake.write(f'\ntarget_sources(readiness_m{motor}_tests PRIVATE \"{copied.as_posix()}\")\n')
                cmake.write(f'target_include_directories(readiness_m{motor}_tests PRIVATE \"{test_include}\")\n')
    build = scratch / 'build'
    commands = [['cmake', '-S', str(source / 'host'), '-B', str(build),
                 '-DCMAKE_BUILD_TYPE=Debug']]
    compiler = []
    if 'sanitize' in flags:
        compiler += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie']
        commands[0] += ['-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined -no-pie']
    if 'configured' in flags:
        compiler += ['-DAPP_TEST_CONFIGURED_BUTTONS=1']
    if compiler:
        commands[0] += ['-DCMAKE_CXX_FLAGS=' + ' '.join(compiler)]
    commands += [['cmake', '--build', str(build), '--parallel', '1']]
    if 'full' not in flags:
        commands[-1] += ['--target', 'readiness_m0_tests', 'readiness_m1_tests']
    commands += [['ctest', '--test-dir', str(build), '--output-on-failure', '--no-tests=error']]
    if 'full' not in flags:
        commands[-1] += ['-R', '^readiness_']
    environment = os.environ.copy()
    environment.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',
                       UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',
                       TMPDIR=str(scratch), CMAKE_BUILD_PARALLEL_LEVEL='1')
    with (out / (label + '.txt')).open('xb') as log:
        for argv in commands:
            log.write(('ARGV ' + json.dumps(argv) + '\n').encode()); log.flush()
            start = datetime.now(timezone.utc).isoformat()
            result = subprocess.run(argv, cwd=root, env=environment,
                                    stdout=log, stderr=subprocess.STDOUT)
            record['commands'].append(dict(argv=argv, returncode=result.returncode,
                start_utc=start, end_utc=datetime.now(timezone.utc).isoformat()))
            code = result.returncode
            if code:
                break
    last = build / 'Testing/Temporary/LastTest.log'
    if last.is_file():
        shutil.copyfile(last, out / (label + '_LastTest.log'))
    record['returncode'] = code
record['scratch_released'] = True
verify()
record['source_verified_after_run'] = True
record['end_utc'] = datetime.now(timezone.utc).isoformat()
record['log_sha256'] = hashlib.sha256((out / (label + '.txt')).read_bytes()).hexdigest()
(out / (label + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print((out / (label + '.txt')).read_text(errors='replace')[-2500:])
sys.exit(code)
