"""Preserve independent D080 host commands and output without reading implementation."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent

def run(args):
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    paths = ['src/hal/imu.cpp', 'src/hal/imu.h', 'src/config.h',
             'tests/test_imu_setup.cpp', 'tests/support/imu_bus_fake.cpp',
             'tests/support/imu_bus_fake.h']
    data = {'argv': args, 'cwd': str(ROOT), 'exit_code': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr,
            'capture': 'text mode; newline normalized',
            'sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}}
    path = OUT / f'host_{time.time_ns()}.json'
    path.write_text(json.dumps(data, indent=2) + '\n')
    print(path, flush=True)
    print(result.stdout + result.stderr, flush=True)
    return result.returncode

if __name__ == '__main__':
    sys.exit(run(sys.argv[1:]))
