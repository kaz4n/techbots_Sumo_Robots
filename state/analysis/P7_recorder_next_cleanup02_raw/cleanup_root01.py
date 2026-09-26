# Runs the pinned exact cleanup only through task-authorized sudo authentication.
# Elevates only its read-only process scan; deletion retains Arduino credentials.
# Independent credential, source, failure and original-guard fixtures verify it.
import base64
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
import stat
import sys
import types
import zlib

STAGE = '/home/arduino/sumox26_codex_build/cleanup-recorder-next-root02'
PINS = {
    'cleanup_remoteocd01.py': (7723, '4c6e8bbfecb10a42d9963a0159a3f3e869bbf9db5e9b13b4f09a099991f39059'),
    'static_remote.py': (33321, '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8')}
USER = {'uids': [1000, 1000, 0], 'gids': [1000, 1000, 0]}
ROOT = {'uids': [0, 0, 0], 'gids': [0, 0, 0]}
OBSERVER = {'uids': [1000, 0, 0], 'gids': [1000, 1000, 0]}
DROPPED = {'uids': [1000, 1000, 1000], 'gids': [1000, 1000, 1000]}
PROJECTION_OLD = b'                except FileNotFoundError:\n                    continue\n'
PROJECTION_NEW = b'                except FileNotFoundError:\n                    raise\n'
PROJECTION_SHA = 'd002e6ad16e202c49c1cb3ef4b22f01bc4da3c0674f1dccfb155eb22d7d66755'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def credentials():
    return {'uids': list(os.getresuid()), 'gids': list(os.getresgid())}


def error_record(stage, error):
    return {'stage': stage, 'type': type(error).__name__, 'message': str(error)}


def stamp(info):
    return tuple(getattr(info, 'st_' + key) for key in
                 ('dev', 'ino', 'mode', 'uid', 'gid', 'nlink', 'size', 'mtime_ns', 'ctime_ns'))


def read_source(name):
    require(name in PINS, 'Unknown source basename')
    limit, digest = PINS[name]
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    fds, ancestors, pending = [], [], None
    try:
        current = os.open('/', directory_flags)
        fds.append(current)
        logical = ''
        for part in STAGE.split('/')[1:]:
            logical += '/' + part
            before = os.stat(part, dir_fd=current, follow_symlinks=False)
            require(stat.S_ISDIR(before.st_mode), 'Nonplain source ancestor')
            if logical == '/home/arduino' or logical.startswith('/home/arduino/'):
                require(before.st_uid == 1000, 'Source ancestor owner changed')
            child = os.open(part, directory_flags, dir_fd=current)
            fds.append(child)
            require(stamp(os.fstat(child)) == stamp(before), 'Source ancestor changed')
            ancestors.append((current, part, stamp(before)))
            current = child
        before = os.stat(name, dir_fd=current, follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_uid == before.st_gid == 1000
                and before.st_nlink == 1 and before.st_size == limit, 'Unsafe source file')
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                     dir_fd=current)
        fds.append(fd)
        require(stamp(os.fstat(fd)) == stamp(before), 'Source changed while opening')
        raw = bytearray()
        while len(raw) <= limit:
            part = os.read(fd, limit + 1 - len(raw))
            if not part:
                break
            raw.extend(part)
        require(len(raw) == limit and hashlib.sha256(raw).hexdigest() == digest,
                'Source bytes differ')
        require(stamp(os.fstat(fd)) == stamp(before) and
                stamp(os.stat(name, dir_fd=current, follow_symlinks=False)) == stamp(before),
                'Source changed while reading')
        for parent, child, identity in ancestors:
            require(stamp(os.stat(child, dir_fd=parent, follow_symlinks=False)) == identity,
                    'Source ancestry changed')
    except Exception as error:
        pending = error
    finally:
        for fd in reversed(fds):
            try:
                os.close(fd)
            except Exception as error:
                if pending is None:
                    pending = error
    if pending is not None:
        raise pending
    return bytes(raw)


def load_cleanup():
    raw, helper = read_source('cleanup_remoteocd01.py'), read_source('static_remote.py')
    require(raw.count(PROJECTION_OLD) == 1, 'Missing or ambiguous process projection')
    raw = raw.replace(PROJECTION_OLD, PROJECTION_NEW)
    require(hashlib.sha256(raw).hexdigest() == PROJECTION_SHA, 'Process projection changed')
    module = types.ModuleType('pinned_original_cleanup')
    exec(compile(raw, STAGE + '/cleanup_remoteocd01.py', 'exec'), module.__dict__)
    return module, helper


def enter_user():
    require(credentials() == ROOT, 'Human root invocation required')
    os.setgroups([1000])
    os.setresgid(1000, 1000, 0)
    os.setresuid(1000, 1000, 0)
    require(credentials() == USER and os.getgroups() == [1000], 'User credentials not established')


def observe(original, records):
    record = {'before': credentials(), 'errors': []}
    records.append(record)
    admitted, pending, result, stage = False, None, None, 'admission'
    try:
        require(record['before'] == USER, 'Observer entered with wrong credentials')
        admitted = True
        stage = 'elevation'
        os.seteuid(0)
        record['during'] = credentials()
        require(record['during'] == OBSERVER, 'Observer elevation failed')
        stage = 'scan'
        result = original()
        record['result'] = result
    except Exception as error:
        pending = error
        record['errors'].append(error_record(stage, error))
    finally:
        if admitted:
            try:
                os.seteuid(1000)
                record['after'] = credentials()
                require(record['after'] == USER, 'Observer did not restore Arduino credentials')
            except Exception as error:
                record['errors'].append(error_record('restoration', error))
                if pending is None:
                    pending = error
    if pending is not None:
        raise pending
    return result


def drop_privilege():
    errors = []
    for stage, operation in (('drop_gid', os.setresgid), ('drop_uid', os.setresuid)):
        try:
            operation(1000, 1000, 1000)
        except Exception as error:
            errors.append(error_record(stage, error))
    try:
        require(credentials() == DROPPED, 'Saved root credentials remain')
    except Exception as error:
        errors.append(error_record('verify_drop', error))
    return errors


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate original receipt key')
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError('Nonfinite original receipt value: ' + value)


def run_original(module, helper, out):
    original = module.processes
    module.processes = lambda: observe(original, out['observations'])
    saved_argv, stream = sys.argv, io.StringIO()
    try:
        sys.argv = [STAGE + '/cleanup_remoteocd01.py',
                    base64.b64encode(zlib.compress(helper)).decode('ascii')]
        with redirect_stdout(stream):
            out['cleanup_returncode'] = module.main()
    finally:
        sys.argv = saved_argv
        out['cleanup_stdout'] = stream.getvalue()
    out['cleanup_result'] = json.loads(out['cleanup_stdout'], object_pairs_hook=unique_object,
                                       parse_constant=invalid_constant)
    require(type(out['cleanup_result']) is dict, 'Original receipt is not an object')
    require(out['cleanup_returncode'] == 0 and
            out['cleanup_result'].get('status') == 'REMOVED_EXACT_STALE_COPIES',
            'Original cleanup failed')


def execute():
    out = {'schema': 'recorder-next-authenticated-scratch-cleanup-v1', 'status': 'FAILED',
           'source_pins': {name: {'bytes': size, 'sha256': digest}
                           for name, (size, digest) in PINS.items()},
           'source_projection': {'count': 1, 'before': PROJECTION_OLD.decode('ascii'),
                                 'after': PROJECTION_NEW.decode('ascii'),
                                 'projected_sha256': PROJECTION_SHA},
           'initial_credentials': None, 'final_credentials': None, 'observations': [],
           'cleanup_stdout': '', 'cleanup_result': None, 'cleanup_returncode': None,
           'first_error': None, 'privilege_drop_errors': []}
    admitted = False
    try:
        out['initial_credentials'] = credentials()
        require(out['initial_credentials'] == ROOT, 'Human root invocation required')
        admitted = True
        require(len(sys.argv) == 1 and sys.flags.dont_write_bytecode and sys.flags.isolated,
                'No arguments and isolated Python-I-B required')
        module, helper = load_cleanup()
        enter_user()
        run_original(module, helper, out)
        require(credentials() == USER, 'Cleanup returned with wrong credentials')
        out['status'] = 'REMOVED_EXACT_STALE_COPIES'
    except Exception as error:
        out['first_error'] = error_record('wrapper', error)
    finally:
        if admitted:
            out['privilege_drop_errors'] = drop_privilege()
        out['final_credentials'] = credentials()
        if out['privilege_drop_errors']:
            out['status'] = 'FAILED'
    return out


def main():
    out = execute()
    print(json.dumps(out, separators=(',', ':')))
    return 0 if out['status'] == 'REMOVED_EXACT_STALE_COPIES' else 1


if __name__ == '__main__':
    sys.exit(main())
