"""Run the review finding regressions against actual Acquirer code; no board I/O."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import sys
root = Path(__file__).resolve().parents[3]
raw = Path(__file__).parent
sources = [raw / 'acquirer_cases.cc', root / 'tests/native_imu_bus/test_main.cc']
sources += [root / 'src/hal' / f for f in ('imu.cpp', 'imu_acquisition.cpp', 'imu_acquisition_async.cpp')]
sources += [root / 'tests/support' / f for f in ('imu_bus_fake.cpp', 'imu_acquisition_fake.cpp', 'imu_resume_fake.cpp')]
with tempfile.TemporaryDirectory(prefix='d094-acquirer-review-', dir='/dev/shm') as temporary:
    executable = Path(temporary) / 'review'
    command = ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
        '-fno-exceptions', '-fno-rtti', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
        '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS', '-I', str(root / 'src'),
        '-I', str(root / 'tests'), '-isystem', str(root / 'host/third_party'), *map(str, sources), '-o', str(executable)]
    receipt = dict(sources={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}, commands=[])
    for argv in (command, [str(executable), '--no-colors']):
        p = subprocess.run(argv, capture_output=True, text=True, timeout=120)
        receipt['commands'].append(dict(argv=argv, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr))
        print(p.stdout + p.stderr)
        if p.returncode: break
    destination = raw / ('acquirer_execution' + (sys.argv[1] if len(sys.argv) > 1 else '') + '.json')
    if destination.exists(): raise SystemExit('Preserve previous evidence')
    destination.write_text(json.dumps(receipt, indent=2) + '\n')
    raise SystemExit(p.returncode)
