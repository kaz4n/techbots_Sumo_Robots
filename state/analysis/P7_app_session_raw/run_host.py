# Checks application session forwarding through real configuration and Runtime.
# Uses host-only synthetic sources and unchanged deployment admission fixtures.
# Saves compact commands/results and frees only this runner's temporary fixtures.
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).parent
OUT = RAW / sys.argv[1]
OUT.mkdir()
sys.path.insert(0, str(ROOT))
count = 0


def command(argv, pass_fds=()):
    global count
    count += 1
    result = subprocess.run(list(map(str, argv)), capture_output=True, timeout=180,
                            pass_fds=pass_fds, env=dict(os.environ, LC_ALL='C'))
    stem = OUT / ('command_%03d' % count)
    stem.with_suffix('.stdout').write_bytes(result.stdout)
    stem.with_suffix('.stderr').write_bytes(result.stderr)
    stem.with_suffix('.json').write_text(json.dumps(dict(argv=list(map(str, argv)),
        returncode=result.returncode), indent=2) + '\n', encoding='utf-8')
    if result.returncode:
        raise RuntimeError(str(stem) + ': ' + result.stderr.decode(errors='replace')[-1500:])
    return result.stdout


def python_tests():
    names = [f'tests.tooling.test_configured_setup.ConfiguredSetupTests.{name}' for name in (
        'test_00_D180_real_type_constexpr_defaults_in_all_build_combinations',
        'test_01_D180_each_of_seventeen_grants_maps_only_its_declared_field',
        'test_03_D180_mixed_grants_are_independent_of_build_flags',
        'test_13_D180_actual_entry_forwards_defaults_once_and_only_steps_in_loop',
        'test_14_D180_actual_entry_forwards_complete_synthetic_nonzero_grants',
        'test_16_D234_session_and_stream_are_exact_without_manufacturing_grants',
        'test_17_D234_undefined_receive_stream_is_rejected_before_enum_cast')]
    names.append('tests.tooling.test_commissioning_deploy')
    suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    with (OUT / 'unittest.txt').open('w', encoding='utf-8') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    receipt = dict(methods=result.testsRun, failures=len(result.failures),
                   errors=len(result.errors), skipped=len(result.skipped), success=result.wasSuccessful())
    (OUT / 'unittest.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    if not result.wasSuccessful():
        raise RuntimeError('Python fixture failed; preserved unittest.txt')
    return receipt


def runtime_tests():
    hal = ('motors.cpp', 'recorder.cpp', 'recorder_frames.cpp', 'recorder_csv.cpp',
           'recorder_dump.cpp', 'power_inputs.cpp', 'ui.cpp', 'imu_heading.cpp',
           'imu_adapter.cpp', 'line_qtr_adapter.cpp', 'qtr_cal.cpp', 'ui_display.cpp', 'qtr_cal_format.cpp')
    with tempfile.TemporaryDirectory(prefix='sumox-d234-', dir='/dev/shm') as temporary:
        stage = Path(temporary)
        source = stage / 'src'
        shutil.copytree(ROOT / 'src', source)
        original = (source / 'config.h').read_text(encoding='utf-8')
        sources = sorted((source / 'core').glob('*.cpp')) + [source / 'hal' / n for n in hal]
        sources += sorted((source / 'app').glob('*.cpp'))
        for profile, allowed in (('default', 0), ('configured', 0), ('configured', 1)):
            text = original
            if profile == 'configured':
                for name, value in (('BUTTON_WINDOWS_CONFIGURED', '1U'),
                    ('BUTTON_LOW_RAW', '{0U, 900U, 1900U, 2900U}'),
                    ('BUTTON_HIGH_RAW', '{100U, 1100U, 2100U, 3100U}')):
                    text, changed = re.subn(r'(\b' + name + r'(?:\[4\])?\s*=\s*)[^;]+;',
                        r'\g<1>' + value + ';', text)
                    assert changed == 1
            (source / 'config.h').write_text(text, encoding='utf-8')
            binary = stage / 'fixture'
            flags = ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined', '-fno-sanitize-recover=all',
                '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                '-DMOTORS_ALLOWED=' + str(allowed), '-DMATCH=' + str(allowed),
                '-I', source, '-I', ROOT / 'tests', '-isystem', ROOT / 'host/third_party']
            if profile == 'configured':
                flags.append('-DAPP_TEST_CONFIGURED_BUTTONS=1')
            command([*flags, *sources, ROOT / 'tests/test_app_dump.cpp',
                     ROOT / 'tests/locked/native_motor_port/test_main.cc', '-o', binary])
            descriptor = os.memfd_create('sumox-d234-runtime', flags=0)
            try:
                with os.fdopen(os.dup(descriptor), 'wb') as output:
                    output.write(binary.read_bytes())
                command([f'/proc/self/fd/{descriptor}', '--no-colors'], (descriptor,))
            finally:
                os.close(descriptor)
            binary.unlink()


started = time.monotonic()
record = dict(status='FAILED', native_calls=0)
try:
    assert sys.dont_write_bytecode and sys.platform == 'linux'
    assert shutil.disk_usage('/dev/shm').free >= 64 * 1024 * 1024
    record['python'] = python_tests()
    runtime_tests()
    record['status'] = 'HOST_PASS'
finally:
    record.update(commands=count, elapsed_seconds=time.monotonic() - started)
    (OUT / 'result.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record), flush=True)
