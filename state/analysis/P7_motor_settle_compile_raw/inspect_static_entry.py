# Observes fixed SETTLE and entry instructions through the reviewed file-only reader.
# Preserves accepted ABI evidence and reuses the historical entry parser privately.
# Independent entry fixtures check projections, parsing, pins and attempt closure.
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[3]
RAW = 'state/analysis/P7_motor_settle_compile_raw/'
ABI = RAW + 'inspect_static_abi.py'
PARSER = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_entry.py'
ABI_RESULT = RAW + 'native_abi_static01/result.json'
ABI_LAYOUT = RAW + 'native_abi_static01/abi.json'
ABI_CLOSURE = RAW + 'native_abi_static01/local_result.json'
ABI_REVIEW = 'state/reviews/P7_motor_settle_abi_actual_review.md'
ARTIFACTS = RAW + 'native_static01/artifacts.json'
BINDING = RAW + 'entry_binding01.json'
CONTRACT = 'state/analysis/P7_motor_settle_entry_contract.md'
CONTRACT_SHA = 'af8ce726bf49b79fecc07548bd78a808d788894ea9e9e1b59daa69eae8a54e7d'
ORIGINALS = {
    ABI: (16106, '0f2b37c906a8ad78d596a1256af94d67d3d47793f6025a5e9dc4449d928002ea'),
    PARSER: (10317, 'cb9ee5bbd5ca8a74510185d77e7d880acf1a03f05608a5ea1459e534a287fa34'),
    ABI_RESULT: (905572, '230ef847f74e84d032a87336f74a4817d4cd8317a0ea5abc72c54fdd0d03eb6e'),
    ABI_LAYOUT: (5410, '069ed01bee9fba11159a4d93d156b8ada35ea5c11414b77870d80b6182d59941'),
    ABI_CLOSURE: (275, 'eb68ef2e125445ad94fc5c0dc251c2a411d55120ab1299e205a1674b572576f9'),
    ABI_REVIEW: (7312, 'a7c3993ab5e0d008b4464bf93f89b5877447992fa8e3197d8c869812e11f874f'),
    ARTIFACTS: (9648, 'e18384c14c0b1367667b265ab4c532a4010be65697460a1cd45487bccd9eca10'),
    BINDING: (20870, '6234676242fdd7e61136fd2a1f66fabb0242b10ee597ef2bf6555a9444ecfd2b'),
}
READER_INPUT = (17061, '67ff238ce7a9f847e53d98fb4f3c47f02bbea12c51a1062457f1583a9399acc6')
READER_PROJECTED = (17085, 'db4122376e7ef2da92ca49633b01248514274744b429ad54bede8d0c8d8da9f8')
PARSER_PROJECTED = (10562, '7f96678955bc37082766f3b02b46b1cdbba832624815b1ba4266a549d3e372f2')
READER_REPLACEMENTS = (
    (b"'/inspect_static_abi.py'", b"'/inspect_static_entry.py'", 1),
    (b"'native_abi_static01'", b"'native_entry_static01'", 1),
    (b'app-motor-settle-abi-static01', b'app-motor-settle-entry-static01', 1),
    (b'D199_STATIC_FILE_ONLY_ABI', b'D199_STATIC_FILE_ONLY_ENTRY', 2),
    (b'STATIC_ABI_CHECKED', b'STATIC_ENTRY_CHECKED', 1),
    (b'STATIC_ABI_OBSERVED', b'STATIC_ENTRY_OBSERVED', 2),
    (b"'file-abi'", b"'file-entry'", 1),
    (b"'abi.json'", b"'entry.json'", 1),
    (b'StaticAbi', b'StaticEntry', 2),
)
PARSER_REPLACEMENTS = (
    (b'/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino',
     b'/home/arduino/sumox26_codex_build/app-motor-settle-static01/build/app_motor_observe.ino', 1),
    (b'15app_motor_fault', b'17app_motor_observe', 6),
    (b'0x0811621c', b'0x081162dc', 1),
    (b'0x08116218', b'0x081162d8', 4),
    (b'0x081160e0', b'0x081161a0', 1),
    (b'0x08116074', b'0x08116134', 2),
    (b'0x08116048', b'0x08116108', 1),
    (b'0x08116046', b'0x08116106', 1),
    (b'0x08116044', b'0x08116104', 1),
    (b'0x08116036', b'0x081160f6', 1),
    (b'0x0811602c', b'0x081160ec', 1),
    (b'0x08115f7c', b'0x0811603c', 1),
    (b'0x08115f74', b'0x08116034', 2),
    (b'0x08115f6c', b'0x0811602c', 1),
    (b'0x08115cfc', b'0x08115dbc', 1),
    (b'0x08115c7c', b'0x08115d3c', 2),
    (b'0x08115bec', b'0x08115cac', 1),
    (b'0x08113290', b'0x08113350', 1),
    (b'0x0811326c', b'0x0811332c', 1),
    (b'0x08110f64', b'0x08110fc0', 1),
    (b'0x08110ed8', b'0x08110f34', 1),
    (b'0x08110d10', b'0x08110d30', 1),
    (b'0x08110cd8', b'0x08110cf8', 2),
    (b'0x08110c70', b'0x08110c90', 1),
    (b'0x08110bfe', b'0x08110c1e', 1),
    (b'0x08110bfc', b'0x08110c1c', 1),
    (b'0x0810c774', b'0x0810c794', 1),
    (b'0x0810c760', b'0x0810c780', 1),
    (b'0x08103d78', b'0x08103d98', 1),
    (b'0x08103d24', b'0x08103d3c', 2),
    (b'0x08103c94', b'0x08103cac', 2),
    (b'0x08103c08', b'0x08103c20', 2),
    (b'0x08103bb0', b'0x08103bb4', 2),
    (b'0x08103b58', b'0x08103b5c', 2),
    (b"    ('start_static_threads', 0x08116134, 0x081161a0, ('_Z20start_static_threadsv',)),\n"
     b')',
     b"    ('start_static_threads', 0x08116134, 0x081161a0, ('_Z20start_static_threadsv',)),\n"
     b"    ('publish_settle', 0x08110d60, 0x08110d9c,\n"
     b"        ('_ZN6motors12_GLOBAL__N_113publishSettleENS_17SettleProbeReasonEjjhh',)),\n"
     b"    ('motor_settle', 0x081115bc, 0x081116e0, ('_ZN6motors8UnoQPort6settleEPv',)),\n"
     b')', 1),
    (b"('global_initializer', 'candidate_rate', 'candidate_period')",
     b"('global_initializer', 'candidate_rate', 'candidate_period', 'publish_settle')", 1),
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
    abi = _module('_sumox_d199_entry_abi', root / ABI, snapshots[ABI])
    original_projection = abi.project_reader

    def composed_projection(raw):
        return project_reader(original_projection(raw))

    abi.project_reader = composed_projection
    reader = abi.load_reader(root=root)
    parser = _module('_sumox_d199_entry_parser', root / PARSER, parser_raw)
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
