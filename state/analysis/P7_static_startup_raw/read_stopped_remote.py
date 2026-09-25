# Reads four fixed stopped-state windows through the already verified passive MEM-AP route.
# Preserves a separate one-shot diagnostic without reset, upload or firmware changes.
# Scoped source review and the actual bounded labelled output qualify this observation.
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import types
import zlib

PARENT = '/home/arduino/sumox26_codex_build'
NAME = 'static-stopped-fcddbd8e-run02-diagnostic01'
PLAN = [('BEFORE', 0x2003bc98, 7), ('TRANSACTION', 0x2003b2b0, 126),
        ('INPUT', 0x2003bef0, 48), ('AFTER', 0x2003bc98, 7)]
PINS = {'helper': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8',
        'support': 'ab0bb32031c1986cc58db1f410a0bdca59449a9dae237672085a81e291b33458',
        'bindings': 'c2c87df6165556602a5a79472caedf0755c070b2e2f3e0b834f17ab0de5c0d32'}


def load():
    if len(sys.argv) != 2 or not sys.dont_write_bytecode:
        raise ValueError('Fixed payload and Python -B required')
    packed = base64.b64decode(sys.argv[1], validate=True)
    d = zlib.decompressobj()
    raw = d.decompress(packed, 131073)
    if len(raw) > 131072 or not d.eof or d.unused_data or d.unconsumed_tail:
        raise ValueError('Payload framing')
    value = json.loads(raw)
    if set(value) != set(PINS):
        raise ValueError('Unexpected payload fields')
    for key, sha in PINS.items():
        if hashlib.sha256(value[key].encode()).hexdigest() != sha:
            raise ValueError('Pinned input changed: ' + key)
    modules = {}
    for key in ('helper', 'support'):
        m = types.ModuleType('stopped_' + key)
        m.__file__ = '/__sumox__/' + key + '.py'
        exec(compile(value[key], m.__file__, 'exec'), m.__dict__)
        modules[key] = m
    return modules['helper'], modules['support'], json.loads(value['bindings'])


def check(h, s, b, root, errors=None):
    identity = None
    try:
        identity = h.identity(root)
        for key, value in [('boot_id', b['boot_id']), ('uid', 1000), ('user', 'arduino'),
                           ('home', '/home/arduino'), ('sysname', 'Linux'), ('machine', 'aarch64')]:
            s.require(identity[key] == value and type(identity[key]) is type(value), 'Identity drift')
    except Exception as error:
        if errors is None:
            raise
        errors.append(s.error_record(error))
    for name, pin in b['files'].items():
        try:
            raw = h.logical_read(root, pin['path'], pin['bytes'])
            s.require(len(raw) == pin['bytes'] and s.digest(raw) == pin['sha256'], 'File drift: ' + name)
        except Exception as error:
            if errors is None:
                raise
            errors.append(s.error_record(error))
    return identity


def write_record(s, folder, name, value):
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o600, dir_fd=folder)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(s.json_bytes(value))
        stream.flush()
        os.fsync(stream.fileno())
    os.fsync(folder)


def main():
    h, s, b = load()
    report = {'scope': NAME, 'status': 'FAILED', 'commands': 0, 'reads_bytes': 752,
              'first_error': None, 'postcheck_errors': [], 'started_utc': s.utc()}
    root = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        report['identity'] = check(h, s, b, root)
        with h.directory(root, PARENT) as parent:
            os.mkdir(NAME, 0o700, dir_fd=parent)
            os.fsync(parent)
            with h.child_directory(parent, NAME, PARENT + '/' + NAME) as folder:
                acquire(h, s, b, root, folder, report)
    finally:
        os.close(root)
    print(s.json_bytes(report).decode(), end='')
    if report['status'] != 'COLLECTED':
        raise SystemExit(1)


def acquire(h, s, b, root, folder, report):
    argv = [b['files']['openocd']['path'], '-f', b['files']['config']['path']]
    for label, address, count in PLAN:
        argv += ['-c', 'echo STOP_DIAG_' + label, '-c', f'mdw phys 0x{address:08x} {count}']
    argv += ['-c', 'echo STOP_DIAG_END', '-c', 'shutdown']
    report.update(argv=argv, plan=PLAN)
    write_record(s, folder, 'intent.json', report)
    streams = []
    try:
        for name in ('stdout', 'stderr'):
            fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=folder)
            streams.append(os.fdopen(fd, 'w+b'))
        report['commands'] = 1
        child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=streams[0],
                                 stderr=streams[1], env=s.ENVIRONMENT, cwd='/home/arduino',
                                 shell=False, start_new_session=True,
                                 preexec_fn=s.limit_child_output)
        report['subprocess'] = s.wait_child(child, 30)
        for name, stream in zip(('stdout', 'stderr'), streams):
            stream.flush()
            os.fsync(stream.fileno())
            stream.seek(0)
            raw = stream.read(1048576)
            report[name] = raw.decode('utf-8', errors='replace')
            s.require(len(raw) < 1048576, 'Diagnostic stream exceeds bound')
        s.check_execution(report['subprocess'])
        report['status'] = 'COLLECTED'
    except Exception as error:
        report['first_error'] = s.error_record(error)
        if hasattr(error, 'subprocess_result'):
            report['subprocess'] = error.subprocess_result
    finally:
        for stream in streams:
            try:
                stream.close()
            except Exception as error:
                report['first_error'] = report['first_error'] or s.error_record(error)
                report['postcheck_errors'].append(s.error_record(error))
    check(h, s, b, root, report['postcheck_errors'])
    if report['postcheck_errors']:
        report['status'] = 'FAILED'
    report['finished_utc'] = s.utc()
    write_record(s, folder, 'result.json', report)


if __name__ == '__main__':
    main()
