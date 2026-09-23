"""Independently rerun D081 focused checks from a frozen Linux snapshot."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[3]
evidence = Path(__file__).resolve().parent
label = sys.argv[1]
if not label.replace('_', '').isalnum():
    raise SystemExit('Simple unique run label required')
out = evidence / label
out.mkdir(exist_ok=False)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command(name, argv, cwd, env):
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(argv, cwd=cwd, env=env, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=300, stdin=subprocess.DEVNULL)
    stream = out / (name + '.txt')
    stream.write_text(result.stdout, encoding='utf-8')
    receipt = dict(argv=list(map(str, argv)), cwd=str(cwd), returncode=result.returncode,
                   started_utc=started, ended_utc=datetime.now(timezone.utc).isoformat(),
                   output_sha256=digest(stream), capture='text=True; newline normalized')
    (out / (name + '.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)
    if result.returncode:
        print(result.stdout, flush=True)
        raise SystemExit(result.returncode)

with tempfile.TemporaryDirectory(prefix='d081-independent-review-', dir='/dev/shm') as tmp:
    stage = Path(tmp)
    for folder in ('src', 'tests', 'host', 'bench', 'tools', 'docs'):
        shutil.copytree(root / folder, stage / folder,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    manifest = {p.relative_to(stage).as_posix(): digest(p)
                for p in sorted(stage.rglob('*')) if p.is_file()}
    (out / 'snapshot_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    env = dict(os.environ, TMPDIR='/dev/shm', PYTHONDONTWRITEBYTECODE='1',
               SUMO_NATIVE_RECEIPT_DIR=str(out / 'native'),
               SUMO_IMU_ACQUISITION_RECEIPT_DIR=str(out / 'acquisition'),
               SUMO_IMU_SETUP_RECEIPT_DIR=str(out / 'setup'))
    compiler = shutil.which('g++')
    base = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
            '-fno-exceptions', '-fno-rtti', '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
            '-I', str(stage/'src'), '-isystem', str(stage/'host/third_party')]
    inputs = [stage/p for p in ('tests/native_imu_bus/test_main.cc',
              'tests/test_imu_acquisition.cpp', 'src/hal/imu.cpp',
              'src/hal/imu_acquisition.cpp', 'tests/support/imu_bus_fake.cpp',
              'tests/support/imu_acquisition_fake.cpp')]
    for mode in ('normal', 'sanitized'):
        binary = stage / ('focused-' + mode)
        sanitizers = [] if mode == 'normal' else ['-fsanitize=address,undefined',
                                                '-fno-sanitize-recover=all']
        command(mode + '_build', [*base, *sanitizers, *map(str, inputs), '-o', str(binary)], stage, env)
        command(mode + '_run', [str(binary), '--no-colors'], stage, env)
    command('native', [sys.executable, '-m', 'unittest', 'tests.tooling.test_imu_bus_unoq', '-v'], stage, env)
    command('acquisition_tooling', [sys.executable, '-m', 'unittest',
            'tests.tooling.test_imu_acquisition', '-v'], stage, env)
    command('config', [sys.executable, '-m', 'unittest', 'tests.tooling.test_p0_config', '-v'], stage, env)
    after = {name: digest(root/name) if (root/name).is_file() else None for name in manifest}
    changed = {name: (expected, after[name]) for name, expected in manifest.items()
               if expected != after[name]}
    (out/'source_changed_during_run.json').write_text(json.dumps(changed, indent=2) + '\n')
    print(json.dumps({'snapshot_files':len(manifest), 'source_changes_during_run':len(changed)}), flush=True)
