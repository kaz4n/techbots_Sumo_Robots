# Corrects only the observed polls alignment query under a fresh file-only owner.
# Preserves the consumed failure and composes the unchanged reviewed ABI reader.
# Independent ABI02 contract tests check pins, projection, type and lifecycle.
import base64
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[3]
RAW = 'state/analysis/P7_app_motor_observe_compile_raw/'
ORIGINAL = RAW + 'inspect_static_abi.py'
FAILED_RESULT = RAW + 'native_abi_static01/result.json'
FAILED_CLOSURE = RAW + 'native_abi_static01/local_result.json'
CONTRACT = 'state/analysis/P7_app_motor_observe_abi02_contract.md'
CONTRACT_SHA = '772615cda21858c3ca32eea6a541d97ec79985054cdbdad5ea029c225a5d673c'
ORIGINALS = {
    ORIGINAL: (9318, '497f756e4eab440d659a4d26ef38ec8d92abdd9f92a5938d1da04705745f42d5'),
    FAILED_RESULT: (893217, 'e83afc5f10cec2ed72f88d6567f6f13e5809518e1b89f3d5988d988b297e78f5'),
    FAILED_CLOSURE: (336, '589b78d1ff3cacbe96869f2f2c43d3fc546a9ff2cbfc26c34d1ad3a3d9b9ec01'),
}
INPUT = (16833, 'f359bebbbba176036891027412327b6b59e47d849e46c37cfe3363cd70a95c14')
PROJECTED = (16937, 'b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981')
REPLACEMENTS = (
    (b"'/inspect_static_abi.py'", b"'/inspect_static_abi02.py'", 1),
    (b"'native_abi_static01'", b"'native_abi_static02'", 1),
    (b'app-motor-observe-abi-static01', b'app-motor-observe-abi-static02', 1),
    (b'D194_STATIC_FILE_ONLY_ABI', b'D194_STATIC_FILE_ONLY_ABI02', 2),
    (b"expression + '(' + subject + ')'",
     b"expression + '(' + ('unsigned int' if name == 'report_.polls' and\n"
     b"                            label == 'ALIGN' else subject) + ')'", 1),
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


def project_reader(raw):
    _verify(raw, INPUT, 'original observer ABI projection')
    for old, new, count in REPLACEMENTS:
        require(raw.count(old) == count, 'ABI02 projection occurrence count changed')
        raw = raw.replace(old, new)
    _verify(raw, PROJECTED, 'projected ABI02 reader')
    return raw


def summarize(result, layout, *, summary):
    require(type(result) is dict and type(result.get('commands')) is list and
            len(result['commands']) == 4 and all(type(row) is dict for row in result['commands']),
            'Expected four original ABI command records')
    require(callable(summary), 'Expected fixed normalized ABI summary')
    encoded = result['commands'][3].get('stdout_base64')
    require(type(encoded) is str, 'Expected encoded GDB stdout')
    debug = base64.b64decode(encoded, validate=True).decode('utf-8')
    marker = 'SUMOX_LAYOUT report_.polls'
    block = r'^SUMOX_LAYOUT report_\.polls\r?\ntype = unsigned int\r?\nSUMOX_SIZE bool\r?$'
    require(debug.count(marker) == 1 and len(re.findall(block, debug, re.MULTILINE)) == 1,
            'Current polls member type differs from observed unsigned int')
    observed = summary(result, layout)
    require(type(observed) is dict, 'Expected normalized ABI summary fields')
    return dict(observed, polls_alignment_type={
        'type': 'unsigned int', 'evidence_sha256': ORIGINALS[FAILED_RESULT][1]})


def load_reader(*, root=ROOT):
    root = Path(root).absolute()
    snapshots = {}
    for name, identity in ORIGINALS.items():
        snapshots[name] = pinned(root / name, identity[1])
        _verify(snapshots[name], identity, name)
    pinned(root / CONTRACT, CONTRACT_SHA)
    original = types.ModuleType('_sumox_d194_abi02_original')
    original.__file__ = str(root / ORIGINAL)
    exec(compile(snapshots[ORIGINAL], original.__file__, 'exec'), original.__dict__)
    original_projection = original.project_reader

    def composed_projection(raw):
        return project_reader(original_projection(raw))

    original.project_reader = composed_projection
    reader = original.load_reader(root=root)
    reader.HARD_PINS = dict(reader.HARD_PINS)
    reader.HARD_PINS.update({name: identity[1] for name, identity in ORIGINALS.items()})
    reader.HARD_PINS[CONTRACT] = CONTRACT_SHA
    normalized_summary = reader.summarize

    def current_type_summary(result, layout):
        return summarize(result, layout, summary=normalized_summary)

    reader.summarize = current_type_summary
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
