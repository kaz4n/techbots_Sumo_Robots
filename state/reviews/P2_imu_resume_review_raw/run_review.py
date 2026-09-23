"""Compile actual native sources and independent reviewer cases; no board activity."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[3]
raw = Path(__file__).parent
fixture = root / 'tests/native_imu_bus'
sources = [raw / 'review_cases.cc', fixture / 'native_fixture.cc', fixture / 'isolation.cc',
           fixture / 'test_main.cc', root / 'src/hal/imu_bus_unoq.cpp', root / 'src/hal/imu_bus_async_unoq.cpp']
with tempfile.TemporaryDirectory(prefix='d094-independent-review-', dir='/dev/shm') as temporary:
    executable = Path(temporary) / 'review'
    command = ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
               '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined', '-fno-sanitize-recover=all',
               '-DARDUINO_ARCH_ZEPHYR', '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
               '-I', str(fixture), '-I', str(root / 'src'), '-isystem', str(root / 'host/third_party'),
               *map(str, sources), '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free', '-o', str(executable)]
    receipt = dict(sources={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}, commands=[])
    for argv in (command, [str(executable), '--no-colors']):
        p = subprocess.run(argv, capture_output=True, text=True, timeout=120)
        receipt['commands'].append(dict(argv=argv, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr))
        print(p.stdout + p.stderr)
        if p.returncode: break
    destination = raw / 'review_execution.json'
    if destination.exists(): raise SystemExit('Preserve previous evidence')
    destination.write_text(json.dumps(receipt, indent=2) + '\n')
    raise SystemExit(p.returncode)
