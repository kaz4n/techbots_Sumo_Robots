"""D103 independent host-only normal/UBSan tests and strict receiver receipts."""
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
counter = 0
hashes = {}

def command(argv, timeout=240):
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
    if code:
        print(out.decode(errors='replace') + err.decode(errors='replace'), flush=True)
        raise RuntimeError('command failed: ' + str(stem))
    return out

def roundtrip(wire, expected, label):
    sys.path.insert(0, str(ROOT / 'tools'))
    spec = importlib.util.spec_from_file_location('d103_dump_match', ROOT / 'tools/dump_match.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    parser = module.Parser()
    for byte in wire:
        parser.feed(bytes([byte]))
    capture = parser.finish()
    assert capture.origin == 1
    assert capture.frame_count > 0 and capture.event_count > 0
    for name in ('frames', 'events', 'summary'):
        assert getattr(capture, name) == (expected / ('expected_' + name + '.csv')).read_bytes(), name
    with tempfile.TemporaryDirectory(prefix='sumo-d103-capture-', dir='/dev/shm') as temporary:
        published = module.save_capture([wire[i:i + 13] for i in range(0, len(wire), 13)],
            Path(temporary), receive_mode='offline')
        shutil.copytree(published, RUN / ('captures-' + label) / published.name)
    (RUN / ('roundtrip-' + label + '.json')).write_text(json.dumps({
        'session': capture.session, 'epoch': capture.epoch, 'origin': capture.origin,
        'frames': capture.frame_count, 'events': capture.event_count, 'crc': capture.crc32,
        'wire_sha256': hashlib.sha256(wire).hexdigest(), 'exact_csv_comparison': True,
        'one_byte_parser': True, 'actual_runtime_go_stop_reset_menu': True,
        'offline_synthetic_only': True}, indent=2) + '\n')

def main():
    selected = sys.argv[1:]
    with tempfile.TemporaryDirectory(prefix='sumo-d103-', dir='/dev/shm') as temporary:
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
            inputs = list(source.rglob('*')) + list((ROOT / 'tests/fixtures/app_service_reset').glob('*'))
            inputs += [ROOT / 'tests/test_app_service_reset.cpp', ROOT / 'tests/fixtures/app_runtime_fixture.h',
                       ROOT / 'tests/fixtures/app_dump/fixture.h', ROOT / 'tests/fixtures/app_transaction_fixture.h',
                       Path(__file__), ROOT / 'src/config.h']
            hashes.clear()
            hashes.update({str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in inputs if p.is_file()})
            sources = sorted((source / 'core').glob('*.cpp'))
            sources += [source / 'hal' / name for name in HAL]
            sources += sorted((source / 'app').glob('*.cpp'))
            for allowed in (0, 1):
                for mode in ('normal', 'san', 'asan'):
                    label = profile + '-' + str(allowed) + '-' + mode
                    if selected and label not in selected:
                        continue
                    binary = stage / (label + '.exe')
                    flags = ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                        '-fno-exceptions', '-fno-rtti', '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
                        '-DMOTORS_ALLOWED=' + str(allowed), '-DMATCH=' + str(allowed),
                        '-I', source, '-I', ROOT / 'tests', '-isystem', ROOT / 'host/third_party']
                    if mode == 'san':
                        flags += ['-fsanitize=undefined', '-fno-sanitize-recover=all']
                    if mode == 'asan':
                        flags += ['-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                                  '-fno-omit-frame-pointer']
                    if profile == 'configured':
                        flags += ['-DAPP_TEST_CONFIGURED_BUTTONS=1']
                    command([*flags, *sources, ROOT / 'tests/test_app_service_reset.cpp',
                        ROOT / 'tests/locked/native_motor_port/test_main.cc', '-o', binary])
                    output = command([binary, '--no-colors']).decode()
                    print(label + ': ' + ' | '.join(x for x in output.splitlines()
                        if 'test cases:' in x or 'assertions:' in x), flush=True)
                    if profile == 'configured':
                        stream = stage / ('stream-' + label)
                        command([*flags, *sources, ROOT / 'tests/fixtures/app_service_reset/roundtrip.cc', '-o', stream])
                        expected = RUN / ('expected-' + label)
                        expected.mkdir()
                        wire = command([stream, expected])
                        (RUN / ('wire-' + label + '.txt')).write_bytes(wire)
                        roundtrip(wire, expected, label)
                        print('strict actual postmatch receiver PASS ' + label, flush=True)
    print('D103 author receipts: ' + str(RUN), flush=True)

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        (RUN / 'runner_failure.txt').write_text(traceback.format_exc())
        raise
