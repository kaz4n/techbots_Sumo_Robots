# Saves first D203 controlled test runs without contacting the board.
# Checks frozen files before and after each distinct platform/suite owner.
# Serial Windows/WSL execution preserves all inherited assertions and failures.
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


def main():
    assert sys.dont_write_bytecode and len(sys.argv) == 3
    platform, group = sys.argv[1:]
    assert platform in ('windows', 'linux') and group in ('caller', 'remote')
    freeze = json.loads((RAW / 'coordinator_freeze01.json').read_text())
    for name, pin in freeze['files'].items():
        data = (ROOT / name).read_bytes()
        assert len(data) == pin['bytes'] and hashlib.sha256(data).hexdigest() == pin['sha256'], name
    owner = RAW / (group + '_first_' + platform + '01')
    owner.mkdir()
    script = 'tests/tooling/test_motor_const_compile' + ('_remote' if group == 'remote' else '') + '.py'
    if platform == 'windows':
        command = [sys.executable, '-I', '-B', script]
    else:
        argv = ['env', 'TMPDIR=/dev/shm', 'python3', '-I', '-B', script]
        command = ['wsl', '-d', 'Ubuntu', '--', 'bash', '-lc',
                   'cd ' + shlex.quote(WSL_ROOT) + ' && exec ' + shlex.join(argv)]
    record = dict(schema='d203-first-host-invocation-v1', platform=platform,
                  group=group, argv=command, started=datetime.datetime.now().astimezone().isoformat())
    (owner / 'intent.json').write_text(json.dumps(record, indent=2) + '\n')
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=360)
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(command, -1, error.stdout or b'', error.stderr or b'')
        record['timed_out'] = True
    (owner / 'stdout').write_bytes(result.stdout)
    (owner / 'stderr').write_bytes(result.stderr)
    changed = [name for name, pin in freeze['files'].items()
               if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != pin['sha256']]
    record.update(returncode=result.returncode, elapsed_seconds=time.monotonic()-start,
                  changed_inputs=changed, stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),
                  stderr_sha256=hashlib.sha256(result.stderr).hexdigest())
    (owner / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))
    print(result.stderr.decode('utf-8', 'replace')[-4000:])
    return 1 if result.returncode or changed else 0


if __name__ == '__main__':
    sys.exit(main())
