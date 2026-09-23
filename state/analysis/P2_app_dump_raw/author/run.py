"""D101 independent scoped host builds and strict receiver roundtrip receipts."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
RUN = RAW / ('run_' + str(time.time_ns()))
RUN.mkdir()
HAL = ('motors.cpp', 'recorder.cpp', 'recorder_frames.cpp', 'recorder_csv.cpp',
       'recorder_dump.cpp', 'power_inputs.cpp', 'ui.cpp', 'imu_heading.cpp',
       'imu_adapter.cpp', 'line_qtr_adapter.cpp', 'qtr_cal.cpp', 'ui_display.cpp')
hashes = {}
counter = 0

def command(argv, timeout=180):
    global counter
    counter += 1
    stem = RUN / ('command_%02d' % counter)
    try:
        result = subprocess.run(list(map(str, argv)), cwd=ROOT, capture_output=True, timeout=timeout)
        code, out, err = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        code, out, err = 124, error.stdout or b'', (error.stderr or b'') + b'\nTIMEOUT'
    stem.with_suffix('.stdout').write_bytes(out)
    stem.with_suffix('.stderr').write_bytes(err)
    stem.with_suffix('.json').write_text(json.dumps({'argv': list(map(str, argv)),
        'cwd': str(ROOT), 'returncode': code, 'sha256': hashes,
        'stdout_sha256': hashlib.sha256(out).hexdigest(),
        'stderr_sha256': hashlib.sha256(err).hexdigest()}, indent=2) + '\n')
    if code != 0:
        print(out.decode(errors='replace') + err.decode(errors='replace'), flush=True)
        raise RuntimeError('command failed: ' + str(stem))
    return out

def check_capture(wire, expected, allowed):
    sys.path.insert(0, str(ROOT / 'tools'))
    spec = importlib.util.spec_from_file_location('d101_dump_match', ROOT / 'tools/dump_match.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    parser = module.Parser()
    # Every byte boundary is exercised, including all envelope/CRC separators.
    for value in wire:
        parser.feed(bytes([value]))
    capture = parser.finish()
    assert capture.origin == 1
    assert capture.frame_count > 0 and capture.event_count > 0
    for name in ('frames', 'events', 'summary'):
        assert getattr(capture, name) == (expected / ('expected_' + name + '.csv')).read_bytes(), name
    # DrvFS does not implement renameat2(RENAME_NOREPLACE). Exercise the real
    # no-overwrite publication contract on a native Linux filesystem, then copy
    # its completed evidence bundle; retain the original DrvFS failure receipt.
    with tempfile.TemporaryDirectory(prefix='sumo-d101-capture-', dir='/dev/shm') as temp:
        published = module.save_capture([wire[i:i + 13] for i in range(0, len(wire), 13)],
            Path(temp), receive_mode='offline')
        destination = RUN / ('captures-' + str(allowed)) / published.name
        shutil.copytree(published, destination)
    record = {'motor_allowed': allowed, 'session': capture.session, 'epoch': capture.epoch,
        'origin': capture.origin, 'frames': capture.frame_count, 'events': capture.event_count,
        'crc32': capture.crc32, 'wire_sha256': hashlib.sha256(wire).hexdigest(),
        'destination': str(destination), 'exact_csv_comparison': True,
        'one_byte_fragment_parser': True, 'offline_only': True}
    (RUN / ('roundtrip-' + str(allowed) + '.json')).write_text(json.dumps(record, indent=2) + '\n')
    print('strict receiver roundtrip ' + str(allowed) + ': ' + json.dumps(record), flush=True)

def main():
    with tempfile.TemporaryDirectory(prefix='sumo-d101-', dir='/dev/shm') as temporary:
        stage = Path(temporary)
        for profile in ('default', 'configured'):
            source = stage / profile / 'src'
            shutil.copytree(ROOT / 'src', source)
            if profile == 'configured':
                config = source / 'config.h'
                text = config.read_text()
                for name, value in (('BUTTON_WINDOWS_CONFIGURED', '1U'),
                    ('BUTTON_LOW_RAW', '{0U, 900U, 1900U, 2900U}'),
                    ('BUTTON_HIGH_RAW', '{100U, 1100U, 2100U, 3100U}')):
                    text, count = re.subn(r'(\b' + name + r'(?:\[4\])?\s*=\s*)[^;]+;',
                        r'\g<1>' + value + ';', text)
                    assert count == 1, name
                config.write_text(text)
                (RUN / 'synthetic_config.h').write_bytes(config.read_bytes())
            inputs = list(source.rglob('*')) + list((ROOT / 'tests/fixtures/app_dump').glob('*'))
            inputs += [ROOT / 'tests/test_app_dump.cpp', ROOT / 'tests/fixtures/app_runtime_fixture.h',
                       Path(__file__), ROOT / 'src/config.h']
            hashes.clear()
            hashes.update({str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in inputs if p.is_file()})
            sources = sorted((source / 'core').glob('*.cpp'))
            sources += [source / 'hal' / name for name in HAL]
            sources += sorted((source / 'app').glob('*.cpp'))
            for allowed in (0, 1):
                label = profile + '-' + str(allowed)
                binary = stage / (label + '.exe')
                flags = ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                    '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined', '-fno-sanitize-recover=all',
                    '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                    '-DMOTORS_ALLOWED=' + str(allowed), '-DMATCH=' + str(allowed),
                    '-I', source, '-I', ROOT / 'tests', '-isystem', ROOT / 'host/third_party']
                if profile == 'configured':
                    flags += ['-DAPP_TEST_CONFIGURED_BUTTONS=1']
                command([*flags, *sources, ROOT / 'tests/test_app_dump.cpp',
                    ROOT / 'tests/locked/native_motor_port/test_main.cc', '-o', binary])
                output = command([binary, '--no-colors']).decode()
                print(label + ': ' + ' | '.join(x for x in output.splitlines()
                    if 'test cases:' in x or 'assertions:' in x), flush=True)
                if profile == 'configured':
                    stream = stage / ('stream-' + str(allowed))
                    command([*flags, *sources, ROOT / 'tests/fixtures/app_dump/roundtrip.cc', '-o', stream])
                    expected = RUN / ('expected-' + str(allowed)); expected.mkdir()
                    wire = command([stream, expected]); (RUN / ('wire-' + str(allowed) + '.txt')).write_bytes(wire)
                    check_capture(wire, expected, allowed)
    print('D101 author receipts: ' + str(RUN), flush=True)

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        (RUN / 'runner_failure.txt').write_text(traceback.format_exc())
        raise
