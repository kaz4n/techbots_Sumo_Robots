# Projects the reviewed file-only ABI reader onto the compiled observation.
# Preserves raw receipts and reuses pinned size normalization without board logic.
# Independent D194 contract tests check binding, member queries and private loading.
import base64
import copy
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[3]
READER = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_abi.py'
NORMALIZER = 'state/analysis/P7_app_motor_fault_compile_raw/interpret_static_abi.py'
LAUNCHER = 'tools/compile_app_motor_observe.py'
CONTRACT = 'state/analysis/P7_app_motor_observe_abi_contract.md'
CONTRACT_SHA = '889d6a7697f2ddc0051ef73f52f82c1dd43f35fa45af9fc2d4958f44441bf8ff'
ORIGINALS = {
    READER: (16600, '0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c'),
    NORMALIZER: (5928, '6a990871af18ca8bc5d10f9d11efda4619052bf1de5ab272188de746f95dad21'),
    LAUNCHER: (7583, '70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827'),
}
PROJECTED = (16833, 'f359bebbbba176036891027412327b6b59e47d849e46c37cfe3363cd70a95c14')
REPLACEMENTS = (
    (b'app_motor_fault', b'app_motor_observe', 10),
    (b'app-motor-fault', b'app-motor-observe', 2),
    (b'D188_STATIC_FILE_ONLY_ABI', b'D194_STATIC_FILE_ONLY_ABI', 2),
    (b'self.compiler = loaded(COMPILE, HARD_PINS[COMPILE])',
     b'self.compiler = loaded(COMPILE, HARD_PINS[COMPILE]).load_caller(root=ROOT)', 1),
    (b'21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950',
     b'3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0', 1),
    (b'cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a',
     b'70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827', 1),
    (b'd4eae97c1c47a1ce0fa24c9d7e3ae44857a565cd7b85b9c17be45143654d3eb5',
     b'aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e', 1),
    (b'f8928bd0b9a59f47c1bc02c627523af8f250535ffcd269e37e5a80414cc0ce82',
     b'24d12778bbb337a5cba411fadab5c5e7a8fd69f99beee7b68ac110c31613622b', 1),
    (b'57b98c00db1ed5d90394812fcbb3fb28effedd4381f6e2fc03a6e7c04b45a6ce',
     b'5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b', 1),
    (b"'countdown::Result')", b"'countdown::Result', 'report_.polls')", 1),
    (b"    'attempted_': 'bool',",
     b"    'report_.polls': 'report_.polls',\n    'attempted_': 'bool',", 1),
    (b"    expressions = ['set max-value-size 1048576']\n    for name in (*TYPES, 'bool'):\n",
     b"    expressions = ['set max-value-size 1048576']\n    for name in (*TYPES, 'bool'):\n"
     b"        subject = ('((app_motor_observe::Runner*)0)->report_.polls'\n"
     b"                   if name == 'report_.polls' else name)\n", 1),
    (b"expression + '(' + name + ')'", b"expression + '(' + subject + ')'", 1),
    (b"'ptype /o ' + name", b"'ptype /o ' + subject", 1),
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
            hashlib.sha256(raw).hexdigest() == identity[1], 'Fixed source changed: ' + label)


def project_reader(raw):
    _verify(raw, ORIGINALS[READER], READER)
    for old, new, count in REPLACEMENTS:
        require(raw.count(old) == count, 'ABI projection occurrence count changed')
        raw = raw.replace(old, new)
    _verify(raw, PROJECTED, 'projected ABI reader')
    return raw


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


def summarize(result, layout, *, parser, normalize):
    require(type(result) is dict and type(result.get('commands')) is list and
            len(result['commands']) == 4 and all(type(row) is dict for row in result['commands']),
            'Expected four original ABI command records')
    require(callable(parser) and callable(normalize), 'Expected fixed parser and normalizer')
    private = copy.deepcopy(result)
    record = private['commands'][2]
    require(type(record.get('stdout_base64')) is str, 'Expected encoded readelf stdout')
    original = base64.b64decode(record['stdout_base64'], validate=True).decode('utf-8')
    projected, projection = normalize(original)
    raw = projected.encode('utf-8')
    record.update(stdout_base64=base64.b64encode(raw).decode(), stdout_bytes=len(raw))
    abi = parser(private, copy.deepcopy(layout))
    return dict(abi, readelf_size_projection=projection)


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
    projected = project_reader(snapshots[READER])
    reader = _module('_sumox_d194_abi_reader', root / READER, projected)
    normalizer = _module('_sumox_d194_abi_normalizer', root / NORMALIZER, snapshots[NORMALIZER])
    reader.pinned = pinned
    reader.HARD_PINS = dict(reader.HARD_PINS)
    reader.HARD_PINS.update({READER: ORIGINALS[READER][1],
                             NORMALIZER: ORIGINALS[NORMALIZER][1], CONTRACT: CONTRACT_SHA})
    original_parser = reader.summarize

    def normalized_summary(result, layout):
        return summarize(result, layout, parser=original_parser, normalize=normalizer.normalize)

    reader.summarize = normalized_summary
    return reader


def main(argv):
    parse_request(argv)
    require(sys.dont_write_bytecode, 'Python -B required')
    return load_reader(root=ROOT).main(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
