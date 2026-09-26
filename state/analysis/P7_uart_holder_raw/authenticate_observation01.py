# Runs the single reviewed read-only UART holder observation through ADB.
# Supplies authentication through no-echo stdin and retains no credential.
# Checked by source review and exact source/argv/intent validation before use.
import base64
import datetime
import getpass
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import time
import warnings
import zlib

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
ADB = Path('C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
ADB_SHA = 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'
SOURCE = ROOT / 'tools/observe_uart_holders.py'
SERIAL = '2629958581'


def pin(path):
    body = path.read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def command(source):
    payload = base64.b64encode(zlib.compress(source, 9)).decode('ascii')
    program = ('import base64,zlib;exec(compile(zlib.decompress(base64.b64decode('
               + repr(payload) + ")),'<reviewed-uart-holder>','exec'))")
    remote = ['/usr/bin/sudo', '-k', '-S', '-p', '', '-H', '--', '/usr/bin/python3',
              '-I', '-B', '-c', program]
    return [str(ADB), '-s', SERIAL, 'shell', '-T', shlex.join(remote)]


def admission():
    intent = json.loads((RAW / 'observation_intent01.json').read_bytes())
    if intent['schema'] != 'd223-readonly-uart-observation-v1':
        raise ValueError('Wrong observation intent')
    for name, expected in intent['files'].items():
        if name not in ('tools/observe_uart_holders.py',
                        'state/analysis/P7_uart_holder_contract.md',
                        'state/reviews/P7_uart_holder_review.md',
                        'state/analysis/P7_uart_holder_raw/authenticate_observation01.py',
                        'tests/tooling/test_uart_holder_observer.py'):
            raise ValueError('Unexpected intent input')
        if pin(ROOT / name) != expected:
            raise ValueError('Reviewed input changed: ' + name)
    if len(intent['files']) != 5 or pin(ADB)['sha256'] != ADB_SHA:
        raise ValueError('Missing inputs or changed ADB')
    argv = command(SOURCE.read_bytes())
    units = len(subprocess.list2cmdline(argv).encode('utf-16-le')) // 2 + 1
    if argv != intent['argv'] or units > 30000 or intent['timeout_seconds'] != 65:
        raise ValueError('Unreviewed command or bound')
    if not intent.get('readonly') or intent['serial'] != SERIAL:
        raise ValueError('Wrong device or operation')
    return intent, argv


def execute(intent, argv):
    record = dict(schema='d223-uart-observation-transport-v1',
        utc=datetime.datetime.now().astimezone().isoformat(),
        intent=pin(RAW / 'observation_intent01.json'),
        credential_transport='No-echo console to native stdin; credential omitted',
        first_error=None)
    with (RAW / 'observation_invocation01.json').open('x', encoding='utf-8') as stream:
        json.dump(record, stream, indent=2)
    credential = None
    started = time.monotonic()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            credential = getpass.getpass('Board read-only UART observation authentication: ')
        result = subprocess.run(argv, input=(credential + '\n').encode(),
                                capture_output=True, timeout=65)
        record['returncode'] = result.returncode
        for name, body in (('stdout', result.stdout), ('stderr', result.stderr)):
            with (RAW / ('observation01.' + name)).open('xb') as stream:
                stream.write(body)
            record[name] = pin(RAW / ('observation01.' + name))
    except subprocess.TimeoutExpired as error:
        record['first_error'] = dict(type='TimeoutExpired',
            disposition='Remote completion indeterminate; do not retry')
        for name, body in (('stdout', error.stdout or b''), ('stderr', error.stderr or b'')):
            with (RAW / ('observation01.' + name)).open('xb') as stream:
                stream.write(body)
            record[name] = pin(RAW / ('observation01.' + name))
    except Exception as error:
        record['first_error'] = dict(type=type(error).__name__, message=str(error))
    finally:
        del credential
        record['elapsed_seconds'] = time.monotonic() - started
        record['closing_errors'] = []
        for path, expected in intent['files'].items():
            try:
                if pin(ROOT / path) != expected:
                    raise ValueError('Reviewed input changed')
            except Exception as error:
                record['closing_errors'].append(dict(path=path, type=type(error).__name__))
        record['inputs_unchanged'] = not record['closing_errors']
        with (RAW / 'observation_transport01.json').open('x', encoding='utf-8') as stream:
            json.dump(record, stream, indent=2)
    print(json.dumps({k: record.get(k) for k in
          ('returncode', 'first_error', 'elapsed_seconds', 'inputs_unchanged')}))
    return int(record.get('returncode') not in (0, 2) or
               record['first_error'] is not None or not record['inputs_unchanged'])


def main():
    if len(sys.argv) != 1 or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise SystemExit('Use isolated Python with -B and no arguments')
    for name in ('observation_invocation01.json', 'observation_transport01.json',
                 'observation01.stdout', 'observation01.stderr'):
        if (RAW / name).exists() or (RAW / name).is_symlink():
            raise ValueError('Observation owner already consumed')
    intent, argv = admission()
    return execute(intent, argv)


if __name__ == '__main__':
    sys.exit(main())
