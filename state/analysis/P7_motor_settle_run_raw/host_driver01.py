# Records first D201 controlled host tests without contacting the board.
# Preserves frozen inputs, original streams and failures for each distinct owner.
# Linux and Windows suites run serially with Python bytecode disabled.
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
WSL_ROOT = '/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots'


def check_inputs(files):
    changed = []
    for name, pin in files.items():
        body = (ROOT / name).read_bytes()
        if (len(body), hashlib.sha256(body).hexdigest()) != (pin['bytes'], pin['sha256']):
            changed.append(name)
    return changed


def main():
    assert sys.dont_write_bytecode and len(sys.argv) == 3
    platform, suite = sys.argv[1:]
    assert platform in ('linux', 'windows')
    assert suite in ('remote', 'actions', 'run', 'interpreter')
    group = 'interpreter' if suite == 'interpreter' else 'native'
    freeze = json.loads((RAW / (group + '_coordinator_freeze01.json')).read_bytes())
    assert not check_inputs(freeze['files'])
    owner = RAW / ('first_' + suite + '_' + platform + '01')
    owner.mkdir()
    script = 'tests/tooling/test_motor_settle_' + suite + '.py'
    if platform == 'windows':
        command = [sys.executable, '-I', '-B', script]
    else:
        argv = ['env', 'TMPDIR=/dev/shm', 'python3', '-I', '-B', script]
        command = ['wsl', '-d', 'Ubuntu', '--', 'bash', '-lc',
                   'cd ' + shlex.quote(WSL_ROOT) + ' && exec ' + shlex.join(argv)]
    record = dict(schema='d201-first-host-invocation-v1', platform=platform, suite=suite,
                  argv=command, started=datetime.datetime.now().astimezone().isoformat())
    (owner / 'intent.json').write_text(json.dumps(record, indent=2) + '\n')
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=360)
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(command, -1, error.stdout or b'', error.stderr or b'')
        record['timed_out'] = True
    (owner / 'stdout').write_bytes(result.stdout)
    (owner / 'stderr').write_bytes(result.stderr)
    changed = check_inputs(freeze['files'])
    record.update(returncode=result.returncode, elapsed_seconds=time.monotonic() - start,
                  changed_inputs=changed, stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
                  stderr_sha256=hashlib.sha256(result.stderr).hexdigest())
    (owner / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))
    print(result.stderr.decode('utf-8', 'replace')[-2500:])
    return 1 if result.returncode or changed else 0


if __name__ == '__main__':
    sys.exit(main())
