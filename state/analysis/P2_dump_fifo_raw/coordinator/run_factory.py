# Re-runs the unchanged D101 193-check binding probe against current public sources.
# Copies source to an isolated host directory; no board or shared build action.
# Records exact inputs and both compile/run statuses without changing any oracle.
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
record = {'scope': 'Unchanged D101 factory probe, current copied public sources', 'commands': []}
output = RAW / ('factory_' + str(time.time_ns()) + '.json')


def run(argv):
    start = time.time_ns()
    result = subprocess.run(list(map(str, argv)), capture_output=True, text=True, timeout=180)
    record['commands'].append(dict(argv=list(map(str, argv)), start_ns=start,
        end_ns=time.time_ns(), returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
    output.write_text(json.dumps(record, indent=2) + '\n')
    if result.returncode:
        raise SystemExit(result.returncode)
    print(result.stdout, end='')


with tempfile.TemporaryDirectory(prefix='d117-factory-', dir='/dev/shm') as temporary:
    folder = Path(temporary)
    source = folder / 'src'
    shutil.copytree(ROOT / 'src', source)
    probe = folder / 'factory_probe.cpp'
    shutil.copyfile(ROOT / 'state/reviews/P2_app_dump_review_raw/factory_probe.cpp', probe)
    record['source_sha256'] = {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in folder.rglob('*') if p.is_file()}
    binary = folder / 'factory'
    run(['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Werror', '-Wpedantic',
         '-fno-exceptions', '-fno-rtti', '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
         '-DARDUINO_ARCH_ZEPHYR', '-I', source, source / 'app/dump_port_unoq.cpp', probe, '-o', binary])
    run([binary])
