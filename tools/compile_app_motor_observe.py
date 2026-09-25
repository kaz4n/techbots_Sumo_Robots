# Projects the reviewed static compile lifecycle onto the inhibited observation.
# Preserves original validators and ownership checks with fixed byte identities.
# Independent D193 contract tests check projection, private loading and dispatch.
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[1]
CALLER_SOURCE = 'tools/compile_app_motor_fault.py'
ADAPTER_SOURCE = 'tools/app_motor_fault_static_policy.py'
REMOTE_SOURCE = 'tools/app_motor_fault_compile_remote.py'
ORIGINALS = {
    CALLER_SOURCE: (29802, 'cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a'),
    ADAPTER_SOURCE: (8262, '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270'),
    REMOTE_SOURCE: (6891, '1428b9345d5f524b6c79ede2c30eabb240b6a45ef6a30a593063c3902054fec2'),
}
PROJECTED = {
    CALLER_SOURCE: (29904, '830299e516c9221db35f81e2b01100cd5f0444cd7a78ca6148048805d2078884'),
    ADAPTER_SOURCE: (8266, 'e3d23d5c6b2bd2d088f954a2dd2b574188edca8ca95d65a4432e54de759d169d'),
    REMOTE_SOURCE: (6897, 'f7886c869980afc969082b66ce8d3fc35801fe7c11134b406af158f06049160c'),
}
CALLER_REPLACEMENTS = (
    (b"CALLER = 'tools/compile_app_motor_fault.py'",
     b"CALLER = 'tools/compile_app_motor_observe.py'", 1),
    (b'P7_app_motor_fault_compile_contract.md', b'P7_app_motor_observe_compile_contract.md', 1),
    (b'P7_app_motor_fault_compile_raw', b'P7_app_motor_observe_compile_raw', 1),
    (b'app-motor-fault-static', b'app-motor-observe-static', 6),
    (b"'app_motor_fault.ino'", b"'app_motor_observe.ino'", 1),
    (b'bench/app_motor_fault', b'bench/app_motor_observe', 4),
    (b"'app_motor_fault'", b"'app_motor_observe'", 2),
    (b"'/app_motor_fault'", b"'/app_motor_observe'", 1),
    (b'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS',
     b'STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS', 1),
    (b'self.code[ADAPTER]', b'project_adapter(self.code[ADAPTER])', 2),
    (b'self.code[REMOTE_HELPER]', b'project_remote(self.code[REMOTE_HELPER])', 2),
)
ADAPTER_REPLACEMENTS = (
    (b"'app_motor_fault.ino'", b"'app_motor_observe.ino'", 1),
    (b'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS',
     b'STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS', 1),
)
REMOTE_REPLACEMENTS = (
    (b'app-motor-fault-static01', b'app-motor-observe-static01', 1),
    (b"'app_motor_fault.ino'", b"'app_motor_observe.ino'", 1),
    (b'app-motor-fault-static-artifacts-v1', b'app-motor-observe-static-artifacts-v1', 1),
    (ORIGINALS[ADAPTER_SOURCE][1].encode(), PROJECTED[ADAPTER_SOURCE][1].encode(), 1),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_request(argv):
    require(type(argv) is list and all(type(item) is str for item in argv),
            'Expected an exact argument list')
    require(len(argv) == 3 and argv[0] in ('--check-only', '--execute') and
            argv[1] == '--reviewed-head' and re.fullmatch('[0-9a-f]{40}', argv[2]),
            'Expected --check-only|--execute --reviewed-head <40lowerhex>')
    return argv[0], argv[2]


def _verify(raw, identity, label):
    require(type(raw) is bytes and len(raw) == identity[0] and
            hashlib.sha256(raw).hexdigest() == identity[1],
            'Fixed source bytes changed: ' + label)


def _project(raw, relative, replacements):
    _verify(raw, ORIGINALS[relative], relative)
    for old, new, count in replacements:
        require(raw.count(old) == count, 'Projection occurrence count changed: ' + relative)
        raw = raw.replace(old, new)
    _verify(raw, PROJECTED[relative], 'projected ' + relative)
    return raw


def project_caller(raw):
    return _project(raw, CALLER_SOURCE, CALLER_REPLACEMENTS)


def project_adapter(raw):
    return _project(raw, ADAPTER_SOURCE, ADAPTER_REPLACEMENTS)


def project_remote(raw):
    return _project(raw, REMOTE_SOURCE, REMOTE_REPLACEMENTS)


def _stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, getattr(info, 'st_file_attributes', 0), info.st_ctime_ns)


def _plain_chain(path):
    stamps = []
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        expected = stat.S_ISREG if item == path else stat.S_ISDIR
        require(expected(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 1024,
                'Nonplain original source path: ' + str(item))
        require(item != path or info.st_nlink == 1, 'Original source has multiple links')
        stamps.append(_stamp(info))
    return stamps


def _read_handle(path, before, relative):
    descriptor, stream, primary = None, None, None
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_CLOEXEC', 0)
    flags |= getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        descriptor = os.open(path, flags)
        info = os.fstat(descriptor)
        opened = _stamp(info)
        path_identity = before[-1][:-1] if os.name == 'nt' else before[-1]
        handle_identity = opened[:-1] if os.name == 'nt' else opened
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                not getattr(info, 'st_file_attributes', 0) & 1024 and
                path_identity == handle_identity,
                'Original source changed before reading: ' + relative)
        stream = os.fdopen(descriptor, 'rb')
        descriptor = None
        raw = stream.read(65537)
        closed = _stamp(os.fstat(stream.fileno()))
        after = _plain_chain(path)
        require(before == after and path_identity == handle_identity and opened == closed and
                len(raw) == before[-1][4] and len(raw) <= 65536,
                'Original source changed while reading: ' + relative)
        _verify(raw, ORIGINALS[relative], relative)
        return raw
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            if stream is not None:
                stream.close()
            elif descriptor is not None:
                os.close(descriptor)
        except BaseException:
            if primary is None:
                raise


def read_original(relative, *, root=ROOT):
    require(type(relative) is str and relative in ORIGINALS, 'Unexpected original source')
    path = Path(root).absolute() / relative
    before = _plain_chain(path)
    require(0 < before[-1][4] <= 65536, 'Original source exceeds bootstrap bound')
    return _read_handle(path, before, relative)


def load_caller(*, root=ROOT):
    root = Path(root).absolute()
    originals = {name: read_original(name, root=root) for name in ORIGINALS}
    caller = project_caller(originals[CALLER_SOURCE])
    project_adapter(originals[ADAPTER_SOURCE])
    project_remote(originals[REMOTE_SOURCE])
    module = types.ModuleType('_sumox_d193_observe_compile')
    module.__file__ = str(root / CALLER_SOURCE)
    module.project_adapter, module.project_remote = project_adapter, project_remote
    exec(compile(caller, module.__file__, 'exec'), module.__dict__)
    # Pin the immutable sources behind the projection, not generated disk copies.
    module.HARD_PINS = dict(module.HARD_PINS)
    for name in (CALLER_SOURCE, REMOTE_SOURCE):
        module.HARD_PINS[name] = ORIGINALS[name][1]
    module.REQUIRED = set(module.REQUIRED) | set(module.HARD_PINS)
    return module


def main(argv):
    parse_request(argv)
    require(sys.dont_write_bytecode, 'Python -B required')
    return load_caller(root=ROOT).main(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
