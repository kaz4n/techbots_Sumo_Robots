# Observes the separate native SETTLE report in the checked diagnostic ELF files.
# Preserves the reviewed ABI02 lifecycle and raw evidence under fresh ownership.
# Independent D204 fixtures check projections, layout, queries and closing guards.
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
RAW = 'state/analysis/P7_motor_const_compile_raw/'
ABI02 = 'state/analysis/P7_app_motor_observe_compile_raw/inspect_static_abi02.py'
COMPILE = 'tools/compile_motor_const.py'
MANIFEST = RAW + 'inputs_static.json'
OUTCOME = RAW + 'native_static01/result.json'
ARTIFACTS = RAW + 'native_static01/artifacts.json'
CONTRACT = 'state/analysis/P7_motor_const_abi_contract.md'
CONTRACT_SHA = '55a9f10dec0a7a148fc6fab3cc80ae131ae2e9a82ac74ce14c7aeb1c484ce3d1'
ORIGINALS = {
    ABI02: (8219, 'a0a5aef19538059450bcb723b6f74cca4d9b7008454760285e8818540ceca421'),
    COMPILE: (7557, '957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247'),
    MANIFEST: (13559, '1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95'),
    OUTCOME: (1605, '323a4d3c56c5465ad82321ba5c918091bf0b0e5500691bbcdb68dd1b2d5de5e7'),
    ARTIFACTS: (9645, 'fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd'),
}
INPUT = (16937, 'b03561df65e768cf582a42d520e6241a9cd02c3563685b87070bd3dfc820e981')
PROJECTED = (17051, '938c1de2cc35f4c57f63c411ba1ca5e732bd4f0f86788e65034c6c91b5f848e6')
REPLACEMENTS = (
    (b'P7_app_motor_observe_compile_raw', b'P7_motor_const_compile_raw', 1),
    (b"'/inspect_static_abi02.py'", b"'/inspect_static_abi.py'", 1),
    (b'tools/compile_app_motor_observe.py', b'tools/compile_motor_const.py', 1),
    (b"'native_abi_static02'", b"'native_abi_static01'", 1),
    (b'app-motor-observe-abi-static02', b'app-motor-const-abi-static01', 1),
    (b'app-motor-observe-static01', b'app-motor-const-static01', 1),
    (b'D194_STATIC_FILE_ONLY_ABI02', b'D204_STATIC_FILE_ONLY_ABI', 2),
    (b'3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0',
     b'4bc3a2e6ebb497d43a433aa887ab8388dd3dab075a4f44918ed614db30034cd2', 1),
    (b'70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827',
     b'957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247', 1),
    (b'aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e',
     b'1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95', 1),
    (b'24d12778bbb337a5cba411fadab5c5e7a8fd69f99beee7b68ac110c31613622b',
     b'323a4d3c56c5465ad82321ba5c918091bf0b0e5500691bbcdb68dd1b2d5de5e7', 1),
    (b'5ceba77dde7c493d66398bfd6d8e0e27e56345612290cb8fef9328f24b87625b',
     b'fc5eb9e233c4642e0388f14132efdebab535d55134ce39c43d33c485d67e4ddd', 1),
    (b"'countdown::Result', 'report_.polls')",
     b"'countdown::Result', 'motors::SettleProbeSample',\n"
     b"         'motors::SettleProbeReport', 'motors::SettleProbeReason', 'report_.polls')", 1),
    (b"    build = OWNER + '/build/app_motor_observe.ino'\n",
     b"    expressions += settle_expressions()\n"
     b"    build = OWNER + '/build/app_motor_observe.ino'\n", 1),
)
FIELDS = (
    ('motors::SettleProbeSample', 'elapsed_us', 0, 4),
    ('motors::SettleProbeSample', 'poll_index', 4, 4),
    ('motors::SettleProbeSample', 'reason', 8, 1),
    ('motors::SettleProbeSample', 'fresh_mask', 9, 1),
    ('motors::SettleProbeSample', 'valid', 10, 1),
    ('motors::SettleProbeSample', 'reserved', 11, 1),
    ('motors::SettleProbeReport', 'current', 0, 12),
    ('motors::SettleProbeReport', 'first_failure', 12, 12),
    ('motors::SettleProbeReport', 'has_current', 24, 1),
    ('motors::SettleProbeReport', 'has_failure', 25, 1),
    ('motors::SettleProbeReport', 'reserved', 26, 2),
)
REASONS = (
    ('NONE', 0), ('SUCCESS', 1), ('NULL_CONTEXT', 2), ('PRECONDITION', 3),
    ('INITIAL_BANK', 4), ('POLL_DEADLINE', 5), ('POLL_BANK', 6),
    ('FINAL_DEADLINE', 7), ('POLL_LIMIT', 8),
)
PROBE_SYMBOL = '_ZN6motors12_GLOBAL__N_119settle_probe_reportE'



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
    _verify(raw, INPUT, 'original ABI02 projection')
    for old, new, count in REPLACEMENTS:
        require(raw.count(old) == count, 'SETTLE ABI projection occurrence count changed')
        raw = raw.replace(old, new)
    _verify(raw, PROJECTED, 'projected SETTLE ABI reader')
    return raw


def settle_expressions():
    expressions = []
    for name, member, _, _ in FIELDS:
        key = name + '.' + member
        expressions += [
            'echo SUMOX_FIELD_OFFSET ' + key + '\\n',
            'p/d (unsigned long)&((' + name + '*)0)->' + member,
            'echo SUMOX_FIELD_WIDTH ' + key + '\\n',
            'p/d sizeof(((' + name + '*)0)->' + member + ')',
        ]
    for name, _ in REASONS:
        expressions += ['echo SUMOX_REASON ' + name + '\\n',
                        'p/d (unsigned int)motors::SettleProbeReason::' + name]
    return expressions


def _number(debug, label, name):
    pattern = r'^SUMOX_' + label + ' ' + re.escape(name) + r'\r?\n\$\d+ = (\d+)\r?$'
    values = re.findall(pattern, debug, re.MULTILINE)
    require(len(values) == 1, 'Missing or duplicate SETTLE number: ' + label + ' ' + name)
    return int(values[0])


def _field_observations(debug):
    expected = []
    for name, member, _, _ in FIELDS:
        key = name + '.' + member
        expected += ['SUMOX_FIELD_OFFSET ' + key, 'SUMOX_FIELD_WIDTH ' + key]
    expected += ['SUMOX_REASON ' + name for name, _ in REASONS]
    markers = [line for line in debug.splitlines() if re.search(r'SUMOX_(?:FIELD|REASON)', line)]
    require(markers == expected, 'SETTLE marker sequence differs')
    fields, reasons = {}, {}
    for name, member, offset, width in FIELDS:
        key = name + '.' + member
        observed = dict(offset=_number(debug, 'FIELD_OFFSET', key),
                        bytes=_number(debug, 'FIELD_WIDTH', key))
        require(observed == dict(offset=offset, bytes=width), 'SETTLE field differs: ' + key)
        fields[key] = observed
    for name, value in REASONS:
        observed = _number(debug, 'REASON', name)
        require(observed == value, 'SETTLE reason differs: ' + name)
        reasons[name] = observed
    return fields, reasons


def _probe_sizes(abi):
    require(type(abi.get('sizes')) is dict and type(abi.get('alignments')) is dict,
            'Missing observed SETTLE types')
    for name, size, alignment in (('motors::SettleProbeSample', 12, 4),
                                  ('motors::SettleProbeReport', 28, 4),
                                  ('motors::SettleProbeReason', 1, 1)):
        observed_size, observed_alignment = abi['sizes'].get(name), abi['alignments'].get(name)
        require(type(observed_size) is int and type(observed_alignment) is int and
                (observed_size, observed_alignment) == (size, alignment),
                'SETTLE size/alignment differs: ' + name)


def _report_symbol(elf):
    candidates = [line for line in elf.splitlines()
                  if line.split() and line.split()[-1] == PROBE_SYMBOL]
    require(len(candidates) == 1, 'Expected one SETTLE report symbol row')
    pattern = (r'\s*\d+:\s+([0-9a-fA-F]+)\s+(\d+|0x[0-9a-fA-F]+)\s+'
               r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(' + PROBE_SYMBOL + r')\s*')
    match = re.fullmatch(pattern, candidates[0])
    require(match is not None, 'Malformed SETTLE report symbol row')
    address, size, kind, bind, visibility, section, name = match.groups()
    require((kind, bind, visibility) == ('OBJECT', 'LOCAL', 'DEFAULT') and
            re.fullmatch('[0-9]+', section), 'SETTLE report symbol identity differs')
    return dict(symbol=name, address=int(address, 16),
                bytes=int(size, 16 if size.startswith('0x') else 10), section=int(section))


def _bss_section(elf, layout, section):
    require(type(layout.get('sections')) is list, 'Missing checked sections')
    checked = [item for item in layout['sections']
               if type(item) is dict and item.get('name') == '.bss']
    require(len(checked) == 1, 'Expected one checked BSS section')
    bss = checked[0]
    rows = [line for line in elf.splitlines() if re.match(r'^\s*\[\s*\d+\]\s+\.bss\b', line)]
    require(len(rows) == 1, 'Expected one observed BSS section')
    pattern = (r'\s*\[\s*(\d+)\]\s+\.bss\s+NOBITS\s+([0-9a-fA-F]+)\s+'
               r'[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+\S+\s+WA\s+\d+\s+\d+\s+\d+\s*')
    match = re.fullmatch(pattern, rows[0])
    require(match is not None and int(match[1]) == section and
            type(bss.get('address')) is int and type(bss.get('size')) is int and
            tuple(int(value, 16) for value in match.groups()[1:]) == (bss['address'], bss['size']),
            'SETTLE BSS section differs from checked layout')
    return bss


def _probe_object(elf, layout, abi):
    report = _report_symbol(elf)
    address, size, section = report['address'], report['bytes'], report['section']
    require(size == abi['sizes']['motors::SettleProbeReport'] and address % 4 == 0,
            'SETTLE report size or address alignment differs')
    require(all(type(abi.get(name)) is int for name in ('address', 'bytes', 'section')) and
            abi['address'] >= 0 and abi['bytes'] > 0 and section == abi['section'],
            'SETTLE and Runner section identities differ')
    bss = _bss_section(elf, layout, section)
    zero = layout.get('bss_zero')
    require(type(zero) is dict and all(type(zero.get(name)) is int for name in ('start', 'end')),
            'Missing checked zero-BSS interval')
    require(bss['address'] <= zero['start'] <= address < address + size <= zero['end'] <=
            bss['address'] + bss['size'], 'SETTLE report leaves initialized BSS')
    require(address + size <= abi['address'] or abi['address'] + abi['bytes'] <= address,
            'SETTLE report overlaps Runner')
    return dict(report, alignment=abi['alignments']['motors::SettleProbeReport'])


def summarize(result, layout, *, summary):
    require(type(result) is dict and type(result.get('commands')) is list and
            len(result['commands']) == 4 and all(type(row) is dict for row in result['commands']),
            'Expected four original ABI command records')
    require(type(layout) is dict and callable(summary), 'Expected checked layout and ABI02 summary')
    texts = []
    for row in result['commands'][2:]:
        encoded = row.get('stdout_base64')
        require(type(encoded) is str, 'Expected encoded file-tool stdout')
        texts.append(base64.b64decode(encoded, validate=True).decode('utf-8'))
    elf, debug = texts
    abi = summary(copy.deepcopy(result), copy.deepcopy(layout))
    require(type(abi) is dict and 'settle_probe' not in abi, 'Expected original ABI02 summary fields')
    _probe_sizes(abi)
    fields, reasons = _field_observations(debug)
    report = _probe_object(elf, layout, abi)
    return dict(abi, settle_probe=dict(report, fields=fields, reasons=reasons))


def load_reader(*, root=ROOT):
    root = Path(root).absolute()
    snapshots = {}
    for name, identity in ORIGINALS.items():
        snapshots[name] = pinned(root / name, identity[1])
        _verify(snapshots[name], identity, name)
    pinned(root / CONTRACT, CONTRACT_SHA)
    original = types.ModuleType('_sumox_d204_abi02_original')
    original.__file__ = str(root / ABI02)
    exec(compile(snapshots[ABI02], original.__file__, 'exec'), original.__dict__)
    original_projection = original.project_reader

    def composed_projection(raw):
        return project_reader(original_projection(raw))

    original.project_reader = composed_projection
    reader = original.load_reader(root=root)
    reader.settle_expressions = settle_expressions
    reader.HARD_PINS = dict(reader.HARD_PINS)
    reader.HARD_PINS.update({name: identity[1] for name, identity in ORIGINALS.items()})
    reader.HARD_PINS[CONTRACT] = CONTRACT_SHA
    original_summary = reader.summarize

    def settle_summary(result, layout):
        return summarize(result, layout, summary=original_summary)

    reader.summarize = settle_summary
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
