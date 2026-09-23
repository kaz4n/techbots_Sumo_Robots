"""Capture D102 scoped tooling, ABI and assertion-migration evidence.

Runs host-only checks with fresh receipts and leaves historical evidence unchanged.
The coordinator separately owns full host/sanitizer and target acceptance.
"""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

RAW = Path(__file__).resolve().parent
ROOT = RAW.parents[3]
FILES = (
    'src/hal/recorder_frames.h', 'src/hal/recorder_frames.cpp',
    'src/hal/recorder_dump.cpp', 'bench/recorder_inert/src/recorder_bench.cpp',
    'bench/p2_recorder_memory/src/memory_probe.cpp',
    'tests/test_recorder_frames.cpp', 'tests/test_attempt_recorder.cpp',
    'tests/test_recorder_csv.cpp', 'tests/test_recorder_rate.cpp',
    'tests/test_tick_timing.cpp', 'tests/fixtures/app_dump/roundtrip.cc',
    'tests/tooling/recorder_bench_cases.cc', 'tests/tooling/test_recorder_memory.py',
)


def capture(name, command):
    result = subprocess.run(list(map(str, command)), cwd=ROOT, capture_output=True)
    (RAW / f'{name}.stdout').write_bytes(result.stdout)
    (RAW / f'{name}.stderr').write_bytes(result.stderr)
    (RAW / f'{name}.json').write_text(json.dumps({
        'command': list(map(str, command)), 'exit_status': result.returncode,
        'sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                   for name in FILES},
    }, indent=2) + '\n')
    print(name, 'exit', result.returncode, flush=True)
    return result.returncode == 0


def assertions(text):
    result = []
    for match in re.finditer(r'\b(?:CHECK(?:_FALSE)?|REQUIRE(?:_FALSE)?)\s*\(', text):
        position, depth = match.end(), 1
        while depth:
            depth += (text[position] == '(') - (text[position] == ')')
            position += 1
        result.append(re.sub(r'\s+', '', text[match.start():position]))
    return result


def old_api(expression):
    expression = re.sub(r'readFrame\((buffer|view),(.*),storage\)',
                        r'\1.at(\2)', expression)
    for name in ('source', 'middle', 'newest', 'borrowed'):
        expression = expression.replace(f'append(*{name},', f'append({name}->bytes,')
    expression = expression.replace(
        '(frames.read(5001U,storage)?&storage:nullptr)', 'frames.at(5001U)')
    return expression.replace('stored.bytes.data[4]',
        'rig.source.frames().at(rig.source.frames().size()-1U)->bytes.data[4]')


def audit():
    records = []
    for name in FILES:
        before = subprocess.check_output(['git', 'show', f'f6f65fc:{name}'], cwd=ROOT).decode()
        after = (ROOT / name).read_text()
        old, new = Counter(assertions(before)), Counter(map(old_api, assertions(after)))
        records.append({'file': name, 'original_assertions': sum(old.values()),
                        'current_assertions': sum(new.values()),
                        'missing_after_explicit_API_mapping': list((old - new).elements()),
                        'added_after_explicit_API_mapping': list((new - old).elements())})
    (RAW / 'assertion_preservation.json').write_text(json.dumps(records, indent=2) + '\n')
    assert all(not row['missing_after_explicit_API_mapping'] for row in records)


def abi():
    with tempfile.TemporaryDirectory(prefix='d102-abi-') as temporary:
        source, binary = Path(temporary) / 'abi.cc', Path(temporary) / 'abi'
        source.write_text('#include "hal/recorder.h"\n#include <cstdio>\nint main() {\n'
            'std::printf("size_t=%zu pointer=%zu FrameBuffer=%zu align=%zu '
            'StoredFrame=%zu align=%zu AttemptRecorder=%zu align=%zu\\n", '
            'sizeof(std::size_t),sizeof(void*),sizeof(recorder::FrameBuffer),'
            'alignof(recorder::FrameBuffer),sizeof(recorder::StoredFrame),'
            'alignof(recorder::StoredFrame),sizeof(recorder::AttemptRecorder),'
            'alignof(recorder::AttemptRecorder));}\n')
        if not capture('abi_compile', ['g++', '-std=c++17', '-Wall', '-Wextra',
                    '-Werror', '-I', ROOT / 'src', source, '-o', binary]):
            return False
        return capture('abi_run', [binary])


def test_module(name):
    sys.path.insert(0, str(ROOT))
    module = __import__(f'tests.tooling.test_recorder_{name}', fromlist=['*'])
    if name == 'bench_runner':
        module.RAW = RAW / 'bench_runner'
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


def guarded_fixture_compile():
    with tempfile.TemporaryDirectory(prefix='d102-fixture-') as temporary:
        results = []
        for label, source in (('csv', 'test_recorder_csv.cpp'),
                              ('timing', 'test_tick_timing.cpp')):
            results.append(capture(label + '_fixture_compile', [
                'g++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                '-fno-exceptions', '-fno-rtti', '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
                '-I', ROOT / 'src', '-I', ROOT / 'tests',
                '-isystem', ROOT / 'host/third_party', '-c', ROOT / 'tests' / source,
                '-o', Path(temporary) / (label + '.o')]))
        return all(results)


if __name__ == '__main__':
    os.chdir(ROOT)
    if len(sys.argv) == 2:
        raise SystemExit(0 if test_module(sys.argv[1]) else 1)
    audit()
    results = [abi()]
    for module in ('memory', 'bench_runner'):
        results.append(capture(module, [sys.executable, __file__, module]))
    raise SystemExit(0 if all(results) else 1)
