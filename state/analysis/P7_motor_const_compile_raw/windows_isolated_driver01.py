# Runs the unchanged caller suite once with a dedicated Windows temporary root.
# Preserves the first failure and source guards while isolating shared Temp use.
# Frozen input closure and exact saved unittest output qualify this host run.
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
FREEZE = RAW / 'windows_isolated_freeze01.json'
OWNER = RAW / 'caller_isolated_windows01'


def changed(pins):
    result = []
    for name, pin in pins.items():
        data = (ROOT / name).read_bytes()
        if len(data) != pin['bytes'] or hashlib.sha256(data).hexdigest() != pin['sha256']:
            result.append(name)
    return result


def main():
    assert os.name == 'nt' and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    frozen = FREEZE.read_bytes()
    pins = json.loads(frozen)['files']
    assert not changed(pins)
    OWNER.mkdir()
    temporary = OWNER / 'temporary'
    temporary.mkdir()
    assert temporary.resolve().is_relative_to(RAW.resolve())
    env = dict(os.environ, TEMP=str(temporary), TMP=str(temporary), TMPDIR=str(temporary))
    command = [sys.executable, '-I', '-B', 'tests/tooling/test_motor_const_compile.py']
    record = dict(schema='d203-isolated-windows-caller-invocation-v1', argv=command,
                  started=datetime.datetime.now().astimezone().isoformat(),
                  temporary_root=str(temporary), timeout_seconds=360,
                  freeze_sha256=hashlib.sha256(frozen).hexdigest(),
                  first_failure='caller_first_windows01/result.json',
                  boundary='One new environment-scoped run; original failure is not relabelled or explained.')
    with (OWNER / 'intent.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
    start = time.monotonic()
    try:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=360)
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(command, -1, error.stdout or b'', error.stderr or b'')
        record['timed_out'] = True
    for name, data in (('stdout', result.stdout), ('stderr', result.stderr)):
        with (OWNER / name).open('xb') as stream:
            stream.write(data)
        record[name + '_sha256'] = hashlib.sha256(data).hexdigest()
    record.update(returncode=result.returncode, elapsed_seconds=time.monotonic()-start,
                  changed_inputs=changed(pins), freeze_unchanged=FREEZE.read_bytes() == frozen,
                  temporary_remnants=sorted(path.name for path in temporary.iterdir()))
    with (OWNER / 'result.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
        stream.write('\n')
    print(json.dumps(record))
    print(result.stderr.decode('utf-8', 'replace')[-4000:])
    return int(bool(result.returncode or record['changed_inputs'] or
                    not record['freeze_unchanged'] or record['temporary_remnants']))


if __name__ == '__main__':
    sys.exit(main())
