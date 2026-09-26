# Observes fixed observer entry instructions through the reviewed file-only reader.
# Preserves accepted ABI evidence and reuses the historical parser privately.
# Independent entry contract tests check projections, pins, parsing and lifecycle.
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[3]
RAW = 'state/analysis/P7_app_motor_observe_compile_raw/'
ABI02 = RAW + 'inspect_static_abi02.py'
PARSER = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py'
ABI_RESULT = RAW + 'native_abi_static02/result.json'
ABI_LAYOUT = RAW + 'native_abi_static02/abi.json'
ABI_CLOSURE = RAW + 'native_abi_static02/local_result.json'
CONTRACT = 'state/analysis/P7_app_motor_observe_entry_contract.md'
CONTRACT_SHA = '437f8cb87b7456f0dfc766e506830e0f5ba23cc5b605de5957ff458b5603caaa'
ORIGINALS = {
    ABI02: (8219, 'a0a5aef19538059450bcb723b6f74cca4d9b7008454760285e8818540ceca421'),
    PARSER: (10317, 'cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34'),
    ABI_RESULT: (893020, 'a5e67635f43b96b813885687fbafe743cfc3ec6a93d089a66453ca574c0676da'),
    ABI_LAYOUT: (3704, 'dfc34596b65d3a82e21e28c3acf9fb1535bec2eb3b489d270c593c9fe3eab3a7'),
    ABI_CLOSURE: (275, '3f17b83efc79026b46d519646798f70d9cf898b0c4a0bef2e06e6da4da0e84a7'),
}
READER_INPUT = (16937, 'b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981')
READER_PROJECTED = (16955, '93729533a1d02e54f6812142aa94cf38e7a93a04d5e03d8a5fc4902386f6a421')
PARSER_PROJECTED = (10333, '6a82a9e5381aace9375673678bd763db95f93ad5de6d90d8d26abea2e2852767')
READER_REPLACEMENTS = (
    (b"'/inspect_static_abi02.py'", b"'/inspect_static_entry.py'", 1),
    (b"'native_abi_static02'", b"'native_entry_static01'", 1),
    (b'app-motor-observe-abi-static02', b'app-motor-observe-entry-static01', 1),
    (b'D194_STATIC_FILE_ONLY_ABI02', b'D194_STATIC_FILE_ONLY_ENTRY', 2),
    (b'STATIC_ABI_CHECKED', b'STATIC_ENTRY_CHECKED', 1),
    (b'STATIC_ABI_OBSERVED', b'STATIC_ENTRY_OBSERVED', 2),
    (b"'file-abi'", b"'file-entry'", 1),
    (b"'abi.json'", b"'entry.json'", 1),
    (b'StaticAbi', b'StaticEntry', 2),
)
PARSER_REPLACEMENTS = (
    (b'/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino',
     b'/home/arduino/sumox26_codex_build/app-motor-observe-static01/build/app_motor_observe.ino', 1),
    (b'15app_motor_fault', b'17app_motor_observe', 6),
    (b'0x08103b58', b'0x08103b5c', 2),
    (b'0x08103bb0', b'0x08103bb4', 2),
    (b'0x08103c08', b'0x08103c20', 2),
    (b'0x08103c94', b'0x08103cac', 2),
    (b'0x08103d24', b'0x08103d3c', 2),
    (b'0x08103d78', b'0x08103d98', 1),
    (b'0x0810c760', b'0x0810c780', 1),
    (b'0x0810c774', b'0x0810c794', 1),
    (b'0x08110bfc', b'0x08110c1c', 1),
    (b'0x08110bfe', b'0x08110c1e', 1),
    (b'0x08110c70', b'0x08110c90', 1),
    (b'0x08110cd8', b'0x08110cf8', 2),
    (b'0x08110d10', b'0x08110d30', 1),
    (b'0x08110ed8', b'0x08110ef8', 1),
    (b'0x08110f64', b'0x08110f84', 1),
    (b'0x0811326c', b'0x0811328c', 1),
    (b'0x08113290', b'0x081132b0', 1),
    (b'0x08115bec', b'0x08115c0c', 1),
    (b'0x08115c7c', b'0x08115c9c', 2),
    (b'0x08115cfc', b'0x08115d1c', 1),
    (b'0x08115f6c', b'0x08115f8c', 1),
    (b'0x08115f74', b'0x08115f94', 2),
    (b'0x08115f7c', b'0x08115f9c', 1),
    (b'0x0811602c', b'0x0811604c', 1),
    (b'0x08116036', b'0x08116056', 1),
    (b'0x08116044', b'0x08116064', 1),
    (b'0x08116046', b'0x08116066', 1),
    (b'0x08116048', b'0x08116068', 1),
    (b'0x08116074', b'0x08116094', 2),
    (b'0x081160e0', b'0x08116100', 1),
    (b'0x08116218', b'0x08116238', 4),
    (b'0x0811621c', b'0x0811623c', 1),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, getattr(info, 'st_file_attributes', 0), info.st_ctime_ns)


def _plain_chain(path):
    stamps = []
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        expected = stat.S_ISREG if item == path else stat.S_ISDIR
        require(expected(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 1024,
                'Nonplain ABI input path: ' + str(item))
        require(item != path or info.st_nlink == 1, 'ABI input has multiple links')
        stamps.append(_stamp(info))
    return stamps


def _read_handle(path, expected, limit, before):
    descriptor, stream, primary = None, None, None
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_CLOEXEC', 0)
    flags |= getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        descriptor = os.open(path, flags)
        info = os.fstat(descriptor)
        opened = _stamp(info)
        path_identity = before[-1][:-1] if os.name == 'nt' else before[-1]
        handle_identity = opened[:-1] if os.name == 'nt' else opened
        # CPython adds all execute bits to these Windows pathname stat results.
        if (os.name == 'nt' and path.suffix.lower() in ('.exe', '.bat', '.cmd', '.com') and
                stat.S_ISREG(path_identity[2]) and stat.S_ISREG(handle_identity[2]) and
                path_identity[2] == (handle_identity[2] | 0o111) and
                path_identity[2] ^ handle_identity[2] == 0o111):
            handle_identity = (*handle_identity[:2], path_identity[2], *handle_identity[3:])
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                not getattr(info, 'st_file_attributes', 0) & 1024 and
                path_identity == handle_identity, 'ABI input changed before reading')
        stream = os.fdopen(descriptor, 'rb')
        descriptor = None
        raw = stream.read(limit + 1)
        closed = _stamp(os.fstat(stream.fileno()))
        after = _plain_chain(path)
        require(before == after and opened == closed and
                0 < len(raw) == before[-1][4] <= limit, 'ABI input changed while reading')
        require(hashlib.sha256(raw).hexdigest() == expected, 'ABI input digest changed: ' + str(path))
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


def pinned(path, expected, limit=1048576):
    require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected),
            'Expected a fixed lowercase input digest')
    require(type(limit) is int and 0 < limit <= 16777216, 'Invalid ABI input bound')
    path = Path(path).absolute()
    before = _plain_chain(path)
    require(0 < before[-1][4] <= limit, 'ABI input exceeds byte bound')
    return _read_handle(path, expected, limit, before)


def _verify(raw, identity, label):
    require(type(raw) is bytes and len(raw) == identity[0] and
            hashlib.sha256(raw).hexdigest() == identity[1], 'Fixed source changed: ' + label)


def _project(raw, original, replacements, projected):
    _verify(raw, original, 'entry projection input')
    for old, new, count in replacements:
        require(raw.count(old) == count, 'Entry projection occurrence count changed')
        raw = raw.replace(old, new)
    _verify(raw, projected, 'entry projection output')
    return raw


def project_reader(raw):
    return _project(raw, READER_INPUT, READER_REPLACEMENTS, READER_PROJECTED)


def project_parser(raw):
    return _project(raw, ORIGINALS[PARSER], PARSER_REPLACEMENTS, PARSER_PROJECTED)


def _module(name, path, raw):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def load_reader(*, root=ROOT):
    root = Path(root).absolute()
    snapshots = {}
    for name, identity in ORIGINALS.items():
        snapshots[name] = pinned(root / name, identity[1])
        _verify(snapshots[name], identity, name)
    pinned(root / CONTRACT, CONTRACT_SHA)
    parser_raw = project_parser(snapshots[PARSER])
    abi = _module('_sumox_d194_entry_abi02', root / ABI02, snapshots[ABI02])
    original_projection = abi.project_reader

    def composed_projection(raw):
        return project_reader(original_projection(raw))

    abi.project_reader = composed_projection
    reader = abi.load_reader(root=root)
    parser = _module('_sumox_d194_entry_parser', root / PARSER, parser_raw)
    reader.HARD_PINS = dict(reader.HARD_PINS)
    reader.HARD_PINS.update({name: identity[1] for name, identity in ORIGINALS.items()})
    reader.HARD_PINS[CONTRACT] = CONTRACT_SHA
    reader.queries = parser.queries
    reader.summarize = parser.summarize
    return reader


def main(argv):
    require(type(argv) is list and all(type(item) is str for item in argv),
            'Expected an exact argument list')
    require(len(argv) == 3 and argv[0] in ('--check-only', '--execute') and
            argv[1] == '--reviewed-head' and re.fullmatch('[0-9a-f]{40}', argv[2]),
            'Expected --check-only|--execute --reviewed-head <40lowerhex>')
    require(sys.dont_write_bytecode, 'Python -B required')
    return load_reader(root=ROOT).main(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
