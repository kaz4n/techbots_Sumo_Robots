"""Reproduce frozen D084 checks from an isolated Linux snapshot, without a board."""
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
    raise SystemExit('Expected simple unique evidence label')
out = evidence / label
out.mkdir(exist_ok=False)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(name, argv, cwd, env):
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(list(map(str, argv)), cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=600, stdin=subprocess.DEVNULL)
    stream = out / (name + '.txt')
    stream.write_bytes(result.stdout)
    receipt = dict(argv=list(map(str, argv)), cwd=str(cwd), returncode=result.returncode,
                   started_utc=started, ended_utc=datetime.now(timezone.utc).isoformat(),
                   output_sha256=digest(stream), capture='raw combined output bytes')
    (out / (name + '.json')).write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)
    if result.returncode:
        print(result.stdout.decode(errors='replace'), flush=True)
        raise SystemExit(result.returncode)


with tempfile.TemporaryDirectory(prefix='d084-independent-review-', dir='/dev/shm') as tmp:
    stage = Path(tmp)
    for folder in ('src', 'tests', 'host', 'bench', 'tools', 'docs'):
        shutil.copytree(root / folder, stage / folder,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (stage/'state/analysis').mkdir(parents=True)
    shutil.copyfile(root/'state/analysis/P2_imu_integration_contract.md',
                    stage/'state/analysis/P2_imu_integration_contract.md')
    manifest = {p.relative_to(stage).as_posix(): digest(p)
                for p in sorted(stage.rglob('*')) if p.is_file()}
    (out / 'snapshot_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    env = dict(os.environ, TMPDIR='/dev/shm', PYTHONDONTWRITEBYTECODE='1',
               SUMO_IMU_INTEGRATION_RECEIPT_DIR=str(out/'integration_tooling'))
    compiler = shutil.which('g++')
    base = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
            '-fno-exceptions', '-fno-rtti', '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
            '-I', str(stage/'src'), '-isystem', str(stage/'host/third_party')]
    inputs = [stage/'tests/native_imu_bus/test_main.cc',
              *sorted((stage/'src/core').glob('*.cpp')),
              *[stage/'src/hal'/name for name in ('imu_heading.cpp', 'imu_adapter.cpp')],
              *[stage/name for name in sys.argv[2:]]]
    for mode in ('normal', 'sanitized'):
        binary = stage / ('focused-' + mode)
        sanitizers = [] if mode == 'normal' else ['-fsanitize=address,undefined',
                                                '-fno-sanitize-recover=all']
        command(mode + '_build', [*base, *sanitizers, *inputs, '-o', binary], stage, env)
        command(mode + '_run', [binary, '--no-colors'], stage, env)
    command('integration_tooling', [sys.executable, '-m', 'unittest',
            'tests.tooling.test_imu_integration', '-v'], stage, env)
    command('config', [sys.executable, '-m', 'unittest', 'tests.tooling.test_p0_config', '-v'], stage, env)
    changed = {name: (expected, digest(root/name) if (root/name).is_file() else None)
               for name, expected in manifest.items()
               if not (root/name).is_file() or expected != digest(root/name)}
    (out/'source_changed_during_run.json').write_text(json.dumps(changed, indent=2) + '\n')
    print(json.dumps({'snapshot_files':len(manifest), 'source_changes_during_run':len(changed)}), flush=True)
