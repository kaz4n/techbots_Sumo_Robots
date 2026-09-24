"""Build one frozen M1 profile for bounded copied-source fault checks.
Keep all temporary objects in owned RAM scratch and retain compact receipts.
Run only after the ordinary D135 validation pipeline releases the compiler.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
label = sys.argv[1]
assert label.replace('_', '').isalnum()
assert not any((out / (label + ext)).exists() for ext in ('.json', '.txt'))
freeze_path = out / 'freeze.json'
freeze = json.loads(freeze_path.read_text())

def verify():
    for name, expected in freeze.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name

verify()
record = dict(label=label, start_utc=datetime.now(timezone.utc).isoformat(),
              input_freeze_sha256=hashlib.sha256(freeze_path.read_bytes()).hexdigest(),
              runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              hardware_access=False, commands=[])
with tempfile.TemporaryDirectory(prefix='sumox_d135_faults_', dir='/dev/shm') as scratch:
    build = Path(scratch) / 'build'
    commands = [
        ['cmake', '-S', str(root / 'host'), '-B', str(build),
         '-DCMAKE_BUILD_TYPE=Debug',
         '-DCMAKE_CXX_FLAGS=-fsanitize=address,undefined -fno-omit-frame-pointer -fno-pie',
         '-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined -no-pie'],
        ['cmake', '--build', str(build), '--parallel', '1',
         '--target', 'opener_timing_m1_tests'],
        ['ctest', '--test-dir', str(build), '--output-on-failure',
         '--no-tests=error', '-R', '^opener_timing_m1_host$'],
        [sys.executable, str(root / 'state/reviews/P5_abort_timing_review_raw/run_mutations.py'),
         str(root), str(build), label],
    ]
    env = os.environ.copy()
    env.update(TMPDIR=scratch, CMAKE_BUILD_PARALLEL_LEVEL='1',
               ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',
               UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
    with (out / (label + '.txt')).open('xb') as log:
        for argv in commands:
            log.write(('ARGV ' + json.dumps(argv) + '\n').encode()); log.flush()
            result = subprocess.run(argv, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
            record['commands'].append(dict(argv=argv, returncode=result.returncode))
            if result.returncode:
                break
record.update(returncode=result.returncode, scratch_released=True,
              end_utc=datetime.now(timezone.utc).isoformat())
verify()
record['source_verified_after_run'] = True
(out / (label + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print((out / (label + '.txt')).read_text(errors='replace')[-3000:])
sys.exit(result.returncode)
