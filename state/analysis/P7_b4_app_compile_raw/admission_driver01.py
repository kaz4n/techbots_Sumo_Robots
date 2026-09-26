# Records one read-only D214 board admission and independent closing observation.
# Preserves the D208 programs while checking current local pins and fresh owners.
# Reviewed before use; no compiler, staging, firmware or privileged operation.
import ast
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
ADB = Path('C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
ADB_SHA = 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'


def pin(path):
    body = path.read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def local(preparation):
    for name, expected in preparation['files'].items():
        assert pin(ROOT / name) == expected, name
    freeze = json.loads((RAW / 'coordinator_freeze01.json').read_bytes())
    for name, expected in freeze['files'].items():
        assert pin(ROOT / name) == expected, name
    assert pin(ADB)['sha256'] == ADB_SHA
    owners = [ROOT / 'build/stage/b4-app-m0-static01', RAW / 'native_static01']
    states = {str(path): os.path.lexists(path) for path in owners}
    assert not any(states.values()), states
    free = shutil.disk_usage(ROOT).free
    assert free >= 134217728
    return dict(frozen_inputs=len(freeze['files']), changed_inputs=[],
                owners_exist=states, local_free_bytes=free, adb_sha256=ADB_SHA)


def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def observe(name, preparation):
    source = (RAW / name).read_bytes()
    source_pin = dict(bytes=len(source), sha256=hashlib.sha256(source).hexdigest())
    assert source_pin == preparation['files'][(RAW / name).relative_to(ROOT).as_posix()]
    code = source.decode('utf-8')
    argv = [str(ADB), '-s', '2629958581', 'shell', '-T',
            shlex.join(['/usr/bin/python3', '-I', '-B', '-c', code])]
    units = len(subprocess.list2cmdline(argv).encode('utf-16-le')) // 2 + 1
    assert units <= 30000
    item = dict(source=name, source_pin=source_pin, argv=argv,
                command_utf16_units=units, timeout_seconds=75,
                started=datetime.datetime.now().astimezone().isoformat())
    start = time.monotonic()
    try:
        completed = subprocess.run(argv, cwd=ROOT, capture_output=True, timeout=75)
        item.update(returncode=completed.returncode,
                    stdout=completed.stdout.decode('utf-8', 'replace'), stderr=completed.stderr.decode('utf-8', 'replace'),
                    stdout_base64=base64.b64encode(completed.stdout).decode('ascii'),
                    stderr_base64=base64.b64encode(completed.stderr).decode('ascii'))
        assert completed.returncode == 0 and not completed.stderr
        observed = json.loads(completed.stdout)
        if name == 'admission_source01.py':
            packet = ast.literal_eval(ast.parse(code).body[0].value)
            assert observed['status'] == 'PASS'
            assert set(observed['files']) == set(packet['pins'])
            assert all(observed['files'][path]['sha256'] == digest
                       for path, digest in packet['pins'].items())
        else:
            assert observed['uid'] == 1000 and observed['user'] == 'arduino'
            assert observed['resuid'] == [1000] * 3 and observed['resgid'] == [1000] * 3
            assert observed['boot_id'] == preparation['expected_boot_id']
            assert observed['cli_sha256'] == preparation['expected_cli_sha256']
            assert not observed['remote_owner_exists'] and not observed['conflicts']
            assert observed['free_bytes'] >= 1073741824
        item['observed'] = observed
    except Exception as error:
        item['error'] = dict(type=type(error).__name__, message=str(error))
        if isinstance(error, subprocess.TimeoutExpired):
            item.update(timed_out=True, stdout=(error.stdout or b'').decode('utf-8', 'replace'),
                        stderr=(error.stderr or b'').decode('utf-8', 'replace'),
                        stdout_base64=base64.b64encode(error.stdout or b'').decode('ascii'),
                        stderr_base64=base64.b64encode(error.stderr or b'').decode('ascii'))
    item['elapsed_seconds'] = time.monotonic() - start
    return item


def main():
    assert sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    preparation_raw = (RAW / 'admission_preparation01.json').read_bytes()
    preparation = json.loads(preparation_raw)
    assert not os.path.lexists(RAW / 'admission01.json')
    assert not os.path.lexists(RAW / 'admission_intent01.json')
    result = dict(schema='d214-readonly-board-admission-v1', status='FAILED',
                  started=datetime.datetime.now().astimezone().isoformat(),
                  preparation_sha256=hashlib.sha256(preparation_raw).hexdigest(),
                  local_before=local(preparation), commands=[], first_error=None)
    save(RAW / 'admission_intent01.json', result)
    for name in ('admission_source01.py', 'admission_closing_source01.py'):
        try:
            item = observe(name, preparation)
        except Exception as error:
            item = dict(source=name, pretransport_error=True,
                        error=dict(type=type(error).__name__, message=str(error)))
        result['commands'].append(item)
        if 'error' in item and result['first_error'] is None:
            result['first_error'] = dict(source=name, **item['error'])
    try:
        result['local_after'] = local(preparation)
        assert (RAW / 'admission_preparation01.json').read_bytes() == preparation_raw
    except Exception as error:
        result['closing_error'] = dict(type=type(error).__name__, message=str(error))
    if result['first_error'] is None and 'closing_error' not in result:
        result['status'] = 'PASS'
    result['finished'] = datetime.datetime.now().astimezone().isoformat()
    save(RAW / 'admission01.json', result)
    print(json.dumps(dict(status=result['status'], commands=len(result['commands']),
                          first_error=result['first_error'], receipt=pin(RAW / 'admission01.json'))))
    return int(result['status'] != 'PASS')


if __name__ == '__main__':
    sys.exit(main())
