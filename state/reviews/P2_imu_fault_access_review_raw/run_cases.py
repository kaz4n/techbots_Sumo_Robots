"""Independent reviewer executable with actual sources; no shared build or board."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).parent
sources = [RAW / 'reviewer_cases.cc', ROOT / 'tests/native_imu_bus/test_main.cc']
sources += [ROOT / 'src/hal' / n for n in ('imu.cpp', 'imu_acquisition.cpp', 'imu_acquisition_async.cpp')]
sources += [ROOT / 'tests/support' / n for n in ('imu_bus_fake.cpp', 'imu_acquisition_fake.cpp', 'imu_resume_fake.cpp')]
receipt = {'sources': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}, 'commands': []}
with tempfile.TemporaryDirectory(prefix='d097-review-', dir='/dev/shm') as temp:
    exe = str(Path(temp) / 'review')
    argv = ['g++', '-std=c++17', '-O1', '-g', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
            '-fno-exceptions', '-fno-rtti', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
            '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS', '-I', str(ROOT / 'src'),
            '-I', str(ROOT / 'tests'), '-isystem', str(ROOT / 'host/third_party'),
            *map(str, sources), '-o', exe]
    for cmd in (argv, [exe, '--no-colors']):
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        receipt['commands'].append(dict(argv=cmd, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr))
        print(p.stdout + p.stderr)
        if p.returncode: break
dest = RAW / 'reviewer_cases.json'
assert not dest.exists(), 'Preserve earlier evidence'
dest.write_text(json.dumps(receipt, indent=2) + '\n')
raise SystemExit(p.returncode)
