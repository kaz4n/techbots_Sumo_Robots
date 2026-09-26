# Runs the separately reviewed D219 fixed capture attempt once at a clean HEAD.
# Checks prerequisite bytes, saves both outcomes, and never retries a command.
# Its launcher retains native ownership, intent, timeout and closing safeguards.
import base64
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


def pin(path):
    body = path.read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def changed(pins):
    return [name for name, expected in pins.items() if pin(ROOT / name) != expected]


def invoke(argv, timeout):
    row = dict(argv=argv, timeout_seconds=timeout,
               started=datetime.datetime.now().astimezone().isoformat())
    start = time.monotonic()
    try:
        result = subprocess.run(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                                capture_output=True, timeout=timeout)
        row.update(returncode=result.returncode,
                   stdout=result.stdout.decode('utf-8', 'replace'),
                   stderr=result.stderr.decode('utf-8', 'replace'))
        streams = (result.stdout, result.stderr)
    except subprocess.TimeoutExpired as error:
        row.update(returncode=-1, timed_out=True,
                   stdout=(error.stdout or b'').decode('utf-8', 'replace'),
                   stderr=(error.stderr or b'').decode('utf-8', 'replace'))
        streams = (error.stdout or b'', error.stderr or b'')
    except Exception as error:
        row.update(returncode=-1, error=dict(type=type(error).__name__, message=str(error)),
                   stdout='', stderr='')
        streams = (b'', b'')
    for name, body in zip(('stdout', 'stderr'), streams):
        row[name + '_base64'] = base64.b64encode(body).decode('ascii')
        row[name + '_sha256'] = hashlib.sha256(body).hexdigest()
    row['elapsed_seconds'] = time.monotonic() - start
    return row


def closing(report, pins, frozen_raw, head):
    checks = (
        ('changed_inputs', lambda: changed(pins), []),
        ('prerequisites_unchanged',
         lambda: (RAW / 'capture_native_prerequisites01.json').read_bytes() == frozen_raw, True),
        ('head_after', lambda: subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, timeout=30).decode().strip(), head))
    report['closing_errors'] = []
    for name, operation, expected in checks:
        try:
            report[name] = operation()
            if report[name] != expected:
                raise ValueError(name + ' differs from expected closing value')
        except Exception as error:
            row = dict(stage=name, type=type(error).__name__, message=str(error))
            report['closing_errors'].append(row)
            report['first_error'] = report['first_error'] or row


def main():
    assert sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    output = RAW / 'capture_native_invocations01.json'
    assert not os.path.lexists(output) and not os.path.lexists(RAW / 'native_capture01')
    frozen_raw = (RAW / 'capture_native_prerequisites01.json').read_bytes()
    pins = json.loads(frozen_raw)['files']
    assert not changed(pins)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    assert len(head) == 40 and all(c in '0123456789abcdef' for c in head)
    assert not subprocess.check_output(['git', 'status', '--porcelain=v1',
                                       '--untracked-files=all'], cwd=ROOT)
    launcher = 'tools/capture_b4_recorder.py'
    report = dict(schema='d219-capture-native-invocations-v1', reviewed_head=head,
                  prerequisites_sha256=hashlib.sha256(frozen_raw).hexdigest(), first_error=None)
    report['check'] = invoke([sys.executable, '-I', '-B', launcher,
                              '--check-only', '--reviewed-head', head], 120)
    if report['check']['returncode'] == 0:
        report['execute'] = invoke([sys.executable, '-I', '-B', '-X',
                                   'pycache_prefix=' + str(RAW / 'native_capture01/pycache'),
                                   launcher, '--execute', '--reviewed-head', head], 1500)
    for name in ('check', 'execute'):
        if name in report and report[name]['returncode'] != 0:
            report['first_error'] = report['first_error'] or dict(stage=name, outcome=report[name])
    closing(report, pins, frozen_raw, head)
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    summary = {name: {k: row[k] for k in ('returncode', 'elapsed_seconds')}
               for name, row in report.items() if name in ('check', 'execute')}
    summary.update(changed_inputs=report.get('changed_inputs'), receipt=pin(output),
                   first_error_stage=(report['first_error'] or {}).get('stage'))
    print(json.dumps(summary))
    return int(report['first_error'] is not None or 'execute' not in report)


if __name__ == '__main__':
    sys.exit(main())
