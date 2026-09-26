# Records bounded first D212 host checks without contacting the board.
# Saves frozen input closure and original streams in exclusive suite owners.
# Uses Linux RAM fixtures and a dedicated Windows temporary directory.
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
WSL_ROOT = '/mnt/c/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots'


def changed(pins):
    result = []
    for name, pin in pins.items():
        body = (ROOT / name).read_bytes()
        if len(body) != pin['bytes'] or hashlib.sha256(body).hexdigest() != pin['sha256']:
            result.append(name)
    return result


def main():
    assert sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 3
    platform, suite = sys.argv[1:]
    assert platform in ('linux', 'windows')
    assert suite in ('remote', 'actions', 'run', 'interpreter')
    group = 'interpreter' if suite == 'interpreter' else 'native'
    freeze_path = RAW / (group + '_coordinator_freeze02.json')
    frozen = freeze_path.read_bytes()
    pins = json.loads(frozen)['files']
    assert not changed(pins)
    owner = RAW / ('first_' + suite + '_' + platform + '02')
    owner.mkdir()
    script = 'tests/tooling/test_ordinary_app_' + suite + '.py'
    env, temporary = dict(os.environ), None
    if platform == 'windows':
        temporary = owner / 'temporary'
        temporary.mkdir()
        assert temporary.resolve().is_relative_to(RAW.resolve())
        env.update(TEMP=str(temporary), TMP=str(temporary), TMPDIR=str(temporary))
        command = [sys.executable, '-I', '-B', script]
    else:
        command = ['wsl', '-d', 'Ubuntu', '--', 'bash', '-lc',
                   'cd ' + shlex.quote(WSL_ROOT) + ' && exec ' +
                   shlex.join(['env', 'TMPDIR=/dev/shm', 'python3', '-I', '-B', script])]
    record = dict(schema='d212-first-host-invocation-v1', platform=platform, suite=suite,
                  argv=command, started=datetime.datetime.now().astimezone().isoformat(),
                  timeout_seconds=600, temporary_root=str(temporary) if temporary else '/dev/shm',
                  freeze_sha256=hashlib.sha256(frozen).hexdigest())
    with (owner / 'intent.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=600)
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(command, -1, error.stdout or b'', error.stderr or b'')
        record['timed_out'] = True
    for name, body in (('stdout', result.stdout), ('stderr', result.stderr)):
        with (owner / name).open('xb') as stream:
            stream.write(body)
        record[name + '_sha256'] = hashlib.sha256(body).hexdigest()
    record.update(returncode=result.returncode, elapsed_seconds=time.monotonic()-start,
                  changed_inputs=changed(pins), freeze_unchanged=freeze_path.read_bytes() == frozen,
                  temporary_remnants=sorted(p.name for p in temporary.iterdir()) if temporary else None)
    with (owner / 'result.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(record))
    print(result.stderr.decode('utf-8', 'replace')[-2500:])
    return int(bool(result.returncode or record['changed_inputs'] or
                    not record['freeze_unchanged'] or record['temporary_remnants']))


if __name__ == '__main__':
    sys.exit(main())
