"""Run one D134 frozen host configuration and release its owned RAM scratch."""
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
label, arc, wait, default, flags_text = sys.argv[1:]
assert label.replace('_', '').isalnum()
assert arc in ('0', '1') and wait in ('0', '1') and default in tuple('123456')
flags = set(flags_text.split(',')) - {'plain'}
assert flags <= {'full', 'sanitize', 'configured', 'review'}
assert 'full' not in flags or (arc, wait, default) == ('1', '1', '1')
assert not any((out / (label + ext)).exists() for ext in ('.json', '.txt'))
freeze_path = out / 'core_freeze.json'
freeze = json.loads(freeze_path.read_text())
for name, expected in freeze.items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
record = dict(label=label, arc=int(arc), wait=int(wait), default=int(default),
              flags=sorted(flags), start_utc=datetime.now(timezone.utc).isoformat(),
              input_freeze_sha256=hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
              commands=[], hardware_access=False)
code = 1
with tempfile.TemporaryDirectory(prefix='sumox_d134_', dir='/dev/shm') as scratch:
    scratch = Path(scratch)
    source = root
    if (arc, wait, default) != ('1', '1', '1') or 'configured' in flags:
        source = scratch / 'fixture'
        for directory in ('src', 'tests', 'host', 'bench'):
            shutil.copytree(root / directory, source / directory,
                            ignore=shutil.ignore_patterns('__pycache__'))
        path = source / 'src/config.h'
        text = path.read_text()
        replacements = {
            'MODE_ARC_ENABLED = 1U': f'MODE_ARC_ENABLED = {arc}U',
            'MODE_WAIT_ENABLED = 1U': f'MODE_WAIT_ENABLED = {wait}U',
            'MODE_DEFAULT = 1U': f'MODE_DEFAULT = {default}U',
        }
        if 'configured' in flags:
            replacements.update({
                'BUTTON_WINDOWS_CONFIGURED = 0U': 'BUTTON_WINDOWS_CONFIGURED = 1U',
                'BUTTON_LOW_RAW[4] = {0U, 0U, 0U, 0U}': 'BUTTON_LOW_RAW[4] = {0U, 900U, 1900U, 2900U}',
                'BUTTON_HIGH_RAW[4] = {0U, 0U, 0U, 0U}': 'BUTTON_HIGH_RAW[4] = {100U, 1100U, 2100U, 3100U}',
            })
        for before, after in replacements.items():
            assert text.count(before) == 1, before
            text = text.replace(before, after)
        path.write_text(text)
        record['synthetic_replacements'] = replacements
        record['fixture_config_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
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
        commands[-1] += ['--target', 'mode_availability_m0_tests', 'mode_availability_m1_tests']
    commands += [['ctest', '--test-dir', str(build), '--output-on-failure']]
    if 'full' not in flags:
        commands[-1] += ['-R', '^mode_availability_']
    if 'review' in flags:
        commands += [[sys.executable,
                      str(root / 'state/reviews/P5_mode_availability_review_raw/run_private.py'),
                      str(source), str(build), label]]
    environment = os.environ.copy()
    environment.update(ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',
                       UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    with (out / (label + '.txt')).open('wb') as log:
        for argv in commands:
            result = subprocess.run(argv, cwd=root, env=environment,
                                    stdout=log, stderr=subprocess.STDOUT)
            record['commands'].append(dict(argv=argv, returncode=result.returncode))
            code = result.returncode
            if code:
                break
    last = build / 'Testing/Temporary/LastTest.log'
    if last.is_file():
        shutil.copyfile(last, out / (label + '_LastTest.log'))
    record['end_utc'] = datetime.now(timezone.utc).isoformat()
    record['returncode'] = code
record['scratch_released'] = True
(out / (label + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print((out / (label + '.txt')).read_text(errors='replace')[-4000:])
sys.exit(code)
