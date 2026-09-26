# Derives small recorder failure-status windows from the exact D238 ELF files.
# Uses offline GDB expressions only; current collector and historical compile identities are separate.
# Focused adversarial fixtures qualify the map before separately admitted native collection.
import ast
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import subprocess
import sys
import types
import zlib

ROOT = Path(__file__).absolute().parents[1]
SELF = 'tools/recorder_six_result_abi.py'
RAW = 'state/analysis/P7_recorder_six_result_raw'
COMPILE_HEAD = '1b2af246cd88e6207e846ee340f8c4e46a5bb980'
ATTEMPT = '771c04943d4c4a759055d794fa4b706e'
SESSION = 8582740024591403637
SOURCE = '289300a4be9547cd294dc1f753bbe17a429d16776c46467fec5417b1290f4ffc'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
OWNER = '/home/arduino/sumox26_codex_build/recorder-771c04943d4c4a75'
COMPILE_RAW = 'state/analysis/P7_recorder_delivery_raw/recorder-771c04943d4c4a75'
D209 = 'state/analysis/P7_ordinary_app_static_compile_raw/inspect_static_abi.py'
D188 = 'state/analysis/P7_app_motor_fault_compile_raw/inspect_static_abi.py'
D173 = 'state/analysis/P7_motor_fault_raw/inspect_active_abi.py'
DELIVERY = 'tools/run_recorder_delivery.py'
PINS = {
    D209: (44449, 'f816a52366d7031f860d5cdd93e0715905df4b675a24e89d8dbb1d2b63eda97d'),
    D188: (16600, '0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c'),
    D173: (10183, '50c074024105e5920ab1557557abfd45c1bcd4280224e2360935a40caf46869a'),
    DELIVERY: (50735, 'df287140c3fbb24ebc5cc1bc4e98d1974f42522746ab5b33175a26cc807698f0'),
}
TYPES = ('recorder_transport::Runner', 'recorder_transport::Report',
         'app::Transaction', 'app::TransactionReport', 'recorder::dump::Transfer',
         'recorder::dump::Report', 'recorder::dump::UnoQDumpPort', 'bool',
         'recorder::dump::FailureRecord')
OBJECTS = (('runner', '_ZN12_GLOBAL__N_16runnerE', TYPES[0]),
           ('native_dump', '_ZN12_GLOBAL__N_111native_dumpE', TYPES[6]))
WINDOWS = {
    'runner_report': ('runner', 'report_', TYPES[1]),
    'transfer_report': ('runner', 'transfer_.report_', TYPES[5]),
    'transaction_report': ('runner', 'transaction_.report_', TYPES[3]),
    'session': ('runner', 'session_', None),
    'packet_started_us': ('native_dump', 'started_us_', None),
    'first_failure': ('native_dump', 'first_failure_', TYPES[8]),
    'native_status': ('native_dump', 'status_', None),
    'native_cleanup_verified': ('native_dump', 'cleanup_verified_', None),
    'native_initialized': ('native_dump', 'initialized_', None),
    'native_attempted': ('native_dump', 'attempted_', None),
    'native_active': ('native_dump', 'active_', None),
    'native_poisoned': ('native_dump', 'poisoned_', None),
}
ENUMS = {
    'recorder_transport::Phase': 'NOT_STARTED DISABLED STARTING RECORDING STOPPING RESET_GESTURE SERVICE_MENU DUMPING SENT_UNCONFIRMED FAILED'.split(),
    'recorder_transport::Failure': 'NONE ORDER PORT GRANT CONFIG CLOCK DEADLINE MISSED_RELEASE TRANSACTION SCENARIO RECORDING RESET DUMP_SETUP DUMP'.split(),
    'recorder::dump::NativeStatus': 'NOT_INITIALIZED OK CONTEXT OWNERSHIP DEVICE READY_LOW READY_ERROR REGISTER POISONED TIMEOUT INVALID_ARGUMENT'.split(),
    'recorder::dump::Phase': 'IDLE ACTIVE SENT_UNCONFIRMED CANCELLED FAILED REFUSED'.split(),
    'recorder::dump::Reason': 'NONE CONTEXT STALE_CONTEXT RESULT_ORDER TIME_ORDER LINUX_UNAVAILABLE NO_EVIDENCE SOURCE_CHANGED FORMAT PORT STALL TOTAL RESET INVALID_CONFIG SESSION_CHANGED'.split(),
    'app::Phase': 'NOT_INITIALIZED IDLE ACQUIRING DECIDED FAULT'.split(),
    'app::Fault': 'NONE SETUP ORDER CLOCK IDENTITY RECEIPT ABORTED'.split(),
    'recorder::dump::FailureSite': 'NONE SETUP SETUP_OWNERSHIP SETUP_READY FIFO_OWNERSHIP FIFO_READBACK WRITE_POISONED WRITE_CONTEXT WRITE_OWNERSHIP WRITE_ARGUMENT TRANSMIT_OWNERSHIP TRANSMIT_READY TRANSMIT_DEADLINE STORE_DEADLINE COMPLETE_OWNERSHIP COMPLETE_READY COMPLETE_DEADLINE TC_DEADLINE CANCEL REPEATED_BEGIN'.split(),
    'recorder::dump::CleanupDisposition': 'NOT_ATTEMPTED SKIPPED_POISONED SKIPPED_CONTEXT SKIPPED_OWNERSHIP VERIFIED READBACK_FAILED'.split(),
}
# Every tuple is (parent window, member name or empty scalar window, width, kind).
FIELDS = [
    ('runner_report', 'phase', 1, 'recorder_transport::Phase'),
    ('runner_report', 'failure', 1, 'recorder_transport::Failure'),
    ('runner_report', 'dump_setup', 1, 'recorder::dump::NativeStatus'),
]
FIELDS += [('runner_report', x, 1, 'bool') for x in (
    'setup_completed go_seen service_only reset_pending reset_done counters_saturated').split()]
FIELDS += [('runner_report', x, 4, 'uint') for x in (
    'setup_completed_us last_poll_us next_release_us epochs missed_releases maximum_lateness_us '
    'maximum_execution_us release_us stop_us reset_epoch_started_us request_us configure_enable_calls '
    'configure_pwm_calls write_enable_calls write_pwm_calls settle_calls enabled_en nonzero_pwm invalid_motor_calls').split()]
FIELDS += [('runner_report', x, 8, 'uint') for x in (
    'release_token stop_token reset_from_token request_token').split()]
FIELDS += [('transfer_report', 'phase', 1, 'recorder::dump::Phase'),
           ('transfer_report', 'reason', 1, 'recorder::dump::Reason')]
FIELDS += [('transfer_report', x, 8, 'uint') for x in ('session', 'epoch')]
FIELDS += [('transfer_report', x, 4, 'uint') for x in ('bytes', 'frames', 'events', 'crc')]
FIELDS += [('transaction_report', 'phase', 1, 'app::Phase'),
           ('transaction_report', 'fault', 1, 'app::Fault')]
FIELDS += [('transaction_report', x, 1, 'bool') for x in ('decision_made', 'finished', 'timing_valid')]
FIELDS += [('transaction_report', x, 4, 'uint') for x in (
    'started_us', 'decision_us', 'completed_us', 'execution_us')]
FIELDS += [('session', '', 8, 'uint'), ('native_status', '', 1, 'recorder::dump::NativeStatus')]
FIELDS += [('packet_started_us', '', 4, 'uint')]
FIELDS += [(x, '', 1, 'bool') for x in WINDOWS if x.startswith('native_') and x != 'native_status']
FIELDS += [('first_failure', 'reason', 1, 'recorder::dump::NativeStatus'),
           ('first_failure', 'site', 1, 'recorder::dump::FailureSite'),
           ('first_failure', 'cleanup', 1, 'recorder::dump::CleanupDisposition'),
           ('first_failure', 'cleanup_ownership', 1, 'recorder::dump::NativeStatus')]
FIELDS += [('first_failure', x, 1, 'uint') for x in ('packet_offset', 'packet_size', 'payload_size')]
FIELDS += [('first_failure', 'ownership_evaluated', 1, 'bool')]


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def component(raw, names):
    lines, found, selected = raw.decode().splitlines(keepends=True), set(), []
    for node in ast.parse(raw).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
            require(node.name not in found, 'Duplicate primitive')
            found.add(node.name)
            selected.append(''.join(lines[node.lineno - 1:node.end_lineno]))
    require(found == set(names), 'Missing primitive')
    return '\n\n'.join(selected)


def expressions():
    answer = ['set max-value-size 1048576']
    def pair(kind, name, command):
        answer.extend(['echo SUMOX_' + kind + ' ' + name + '\\n', command])
    for name in TYPES:
        pair('SIZE', name, 'p/d sizeof(' + name + ')')
        pair('ALIGN', name, 'p/d alignof(' + name + ')')
        pair('LAYOUT', name, 'ptype /o ' + name)
    objects = {key: name for key, symbol, name in OBJECTS}
    for key, (owner, member, name) in WINDOWS.items():
        expr = '((' + objects[owner] + '*)0)->' + member
        pair('OFFSET', key, 'p/d (unsigned long)&' + expr)
        pair('EXTENT', key, 'p/d sizeof(' + expr + ')')
    for parent, member, width, kind in FIELDS:
        if not member:
            continue
        name, expr = parent + '.' + member, '((' + WINDOWS[parent][2] + '*)0)->' + member
        pair('FIELD', name, 'p/d (unsigned long)&' + expr)
        pair('WIDTH', name, 'p/d sizeof(' + expr + ')')
    for name, values in ENUMS.items():
        pair('ENUM_WIDTH', name, 'p/d sizeof(' + name + ')')
        for value in values:
            pair('ENUM', name + '::' + value, 'p/d (unsigned int)' + name + '::' + value)
    return answer


def queries(reader):
    build = OWNER + '/build/recorder.ino'
    return [[reader.PREFIX + 'readelf', '--version'], [reader.PREFIX + 'gdb', '--version'],
            [reader.PREFIX + 'readelf', '-hSWs', build + '.elf'],
            reader.gdb(build + '_debug.elf', expressions())]


def checked_objects(parser, elf, layout, sizes, aligns):
    require(re.findall(r'^\s*Type:\s*(.*?)\s*$', elf, re.M) == ['EXEC (Executable file)'],
            'Expected exact static ELF header')
    section, zero = parser._bss(elf, layout)
    data = [s for s in layout['sections'] if s['name'] == '.data']
    require(len(data) == 1, 'Missing data section')
    data, copy = data[0], layout['data_copy']
    require(all(type(copy.get(k)) is int for k in ('destination', 'source', 'bytes')) and
            copy['destination'] == data['address'] and copy['bytes'] == data['size'] and
            copy['source'] == data['load_address'], 'Data copy differs from section')
    rows = [s for s in elf.splitlines() if re.match(r'^\s*\[.*?\]\s+\.data(?:\s|$)', s)]
    require(len(rows) == 1, 'Missing or duplicate data section')
    match = re.fullmatch(r'\s*\[\s*(\d+)\]\s+\.data\s+PROGBITS\s+([\da-fA-F]+)\s+[\da-fA-F]+\s+([\da-fA-F]+)\s+[\da-fA-F]+\s+WA\s+\d+\s+\d+\s+\d+\s*', rows[0])
    require(match is not None and (int(match[2], 16), int(match[3], 16)) ==
            (data['address'], data['size']), 'Native data section differs')
    intervals = {section: (zero['start'], zero['end'], '.bss'),
                 int(match[1]): (copy['destination'], copy['destination'] + copy['bytes'], '.data')}
    require(len(intervals) == 2, 'Duplicate RAM section index')
    objects = {}
    for key, symbol, name in OBJECTS:
        address, size, index = parser._symbol(elf, symbol)
        require(index in intervals and (key != 'runner' or index == section), 'Unexpected object section')
        lower, upper, kind = intervals[index]
        require(size == sizes[name] and address % aligns[name] == 0 and
                lower <= address < address + size <= upper, 'Object leaves initialized RAM')
        objects[key] = dict(symbol=symbol, type=name, address=address, bytes=size,
                            section=index, section_name=kind, alignment=aligns[name])
    a, b = objects.values()
    require(a['address'] + a['bytes'] <= b['address'] or b['address'] + b['bytes'] <= a['address'],
            'Objects overlap')
    return objects


def checked_windows(parser, blocks, objects, sizes, aligns):
    windows, intervals = {}, []
    for key, (owner, member, name) in WINDOWS.items():
        obj = objects[owner]
        offset, size = parser._numeric(blocks, 'OFFSET', key), parser._numeric(blocks, 'EXTENT', key)
        expected = sizes[name] if name else next(w for p, m, w, k in FIELDS if p == key)
        alignment = aligns[name] if name else min(expected, 8)
        address = obj['address'] + offset
        require(size == expected and offset + size <= obj['bytes'] and address % alignment == 0,
                'Window leaves object or differs from type')
        intervals.append((address, address + size))
        windows[key] = dict(object=owner, member=member, type=name, offset=offset,
                            address=address, bytes=size, alignment=alignment)
    intervals.sort()
    require(all(a[1] <= b[0] for a, b in zip(intervals, intervals[1:])), 'Windows overlap')
    return windows


def checked_fields(parser, blocks, windows):
    fields, ranges = {}, {}
    for parent, member, width, kind in FIELDS:
        key = parent + ('.' + member if member else '')
        offset = parser._numeric(blocks, 'FIELD', key) if member else 0
        observed = parser._numeric(blocks, 'WIDTH', key) if member else windows[parent]['bytes']
        require(observed == width and offset + width <= windows[parent]['bytes'] and
                (windows[parent]['address'] + offset) % min(width, 8) == 0, 'Field extent or alignment differs')
        ranges.setdefault(parent, []).append((offset, offset + width))
        fields[key] = dict(window=parent, offset=offset, bytes=width, kind=kind)
    for items in ranges.values():
        items.sort()
        require(all(a[1] <= b[0] for a, b in zip(items, items[1:])), 'Fields overlap')
    return fields


def summarize(result, layout, parser, reader, checker):
    parser.COMMANDS = tuple(tuple(c) for c in queries(reader))
    parser.ABI_TYPES = TYPES
    parser.MARKERS = tuple(x[5:-2] for x in expressions() if x.startswith('echo '))
    elf, debug = parser._streams(result, checker)
    blocks = parser._debug_blocks(debug)
    sizes, aligns, layouts = parser._type_observations(blocks)
    objects = checked_objects(parser, elf, layout, sizes, aligns)
    windows = checked_windows(parser, blocks, objects, sizes, aligns)
    fields = checked_fields(parser, blocks, windows)
    enums = {}
    for name, values in ENUMS.items():
        require(parser._numeric(blocks, 'ENUM_WIDTH', name) == 1, 'Enum width differs')
        enums[name] = {value: parser._numeric(blocks, 'ENUM', name + '::' + value) for value in values}
        require(enums[name] == dict(zip(values, range(len(values)))), 'Enum values differ')
    return dict(schema='recorder-failure-abi-v1', status='STATIC_ABI_OBSERVED',
                compile_head=COMPILE_HEAD, attempt=ATTEMPT, session=SESSION, source_sha256=SOURCE,
                objects=objects, sizes=sizes, alignments=aligns, layouts=layouts,
                windows=windows, fields=fields, enums=enums,
                limitation='File layout only; no MCU data, coherent snapshot, timing or physical acceptance')


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


def verified_module(root, name):
    size, digest = PINS[name]
    raw = pinned(root / name, digest)
    require(len(raw) == size, 'Pinned dependency size differs')
    module = types.ModuleType('_recorder_six_result_' + Path(name).stem)
    module.__file__ = str(root / name)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def prepare_owner(head, *, root=ROOT):
    """Prepare one file-only owner; this performs no board operation."""
    root = Path(root).absolute()
    delivery = verified_module(root, DELIVERY)
    parser, legacy, reader = (verified_module(root, name) for name in (D209, D188, D173))
    plan_raw = (root / RAW / 'plan.json').read_bytes()
    plan = json.loads(plan_raw)
    require(plan['schema'] == 'recorder-failure-plan-v1' and plan['compile_head'] == COMPILE_HEAD and
            plan['attempt'] == ATTEMPT and plan['source_sha256'] == SOURCE and
            plan['expressions'] == expressions(), 'Fixed file-only plan differs')
    require(set(plan['compile_records']) == {'inputs.json', 'result.json', 'artifacts.json', 'staged_files.json'},
            'Unexpected compile record inventory')
    compile_owner = delivery.make_owner(dict(action='--check-only', attempt=ATTEMPT, reviewed_head=COMPILE_HEAD), root=root)
    # Historical source admission compares the 145 exact bytes to COMPILE_HEAD.
    compile_owner.admission()
    require(compile_owner.source_sha256 == SOURCE and len(compile_owner.inputs['files']) == 145 and
            len(compile_owner.expected_stage) == 110, 'Compile source inventory differs')
    legacy.SOURCE, legacy.BOOT, legacy.RAW = SOURCE, BOOT, RAW
    legacy.summarize = lambda result, layout: summarize(result, layout, parser, reader, legacy.checked_command)
    execute_source = component(pinned(root / D188, PINS[D188][1]), {'StaticAbi'})
    require(execute_source.count('D188_STATIC_FILE_ONLY_ABI') == 2, 'Inherited scope seam differs')
    execute_source = execute_source.replace('D188_STATIC_FILE_ONLY_ABI', 'D238_FILE_ONLY_ABI')
    exec(compile(execute_source, '<D238-pinned-lifecycle>', 'exec'), legacy.__dict__)

    class RecorderAbi(legacy.StaticAbi):
        def __init__(self):
            self.root, self.reviewed_head, self.base = root, head, compile_owner.base
            self.output, self.remote = root / RAW / 'native_abi01', OWNER + '-failure-abi01'
            self.claimed, self.counter, self.executor = False, 0, None
            self.inputs, self.code = compile_owner.inputs, compile_owner.code
            self.local_pins = {name: digest for name, (size, digest) in PINS.items()}
            self.local_pins[RAW + '/plan.json'] = sha(plan_raw)
            for name, pin in plan['compile_records'].items():
                self.local_pins[COMPILE_RAW + '/' + name] = pin['sha256']
            for name in (SELF, 'tools/recorder_six_result_capture.py', 'state/analysis/P7_recorder_six_result_contract.md'):
                self.local_pins[name] = sha(self.base.read(root / name))
            for name in ('git_state', 'transport', 'direct', 'preamble'):
                setattr(self, name, types.MethodType(getattr(self.base.CompileCurrent, name), self))

        def local(self):
            require(sys.dont_write_bytecode, 'Python -B required')
            require(not os.path.lexists(self.output / 'pycache'), 'Bytecode output must stay absent')
            current, changes = self.git_state()
            prefix = self.output.relative_to(root).as_posix() + '/'
            require(current == self.reviewed_head and all(self.claimed and state == '??' and name.startswith(prefix)
                    for state, name in changes), 'Collector HEAD or clean tree changed')
            observed = {name: pinned(root / name, digest) for name, digest in self.local_pins.items()}
            require(observed == compile_owner._bootstrap._head_bytes(root, self.reviewed_head, set(observed)),
                    'Collector inputs differ from reviewed HEAD')
            compile_owner.admission()
            require(self.inputs == compile_owner.inputs and self.code == compile_owner.code,
                    'Historical compile inputs changed')
            pinned(Path(self.base.ADB), self.base.ADB_SHA, 16777216)

        def prepare(self):
            self.local()
            require(not os.path.lexists(self.output), 'File-only ABI owner already consumed')
            self.base.plain(self.output.parent, directory=True)
            require(shutil.disk_usage(root).free >= 134217728, 'Less than 128MiB local free space')
            self.executor = self.base.executor_namespace(root, self.code[self.base.EXECUTOR])
            self.executor['BOOT'] = self.base.BOOT = BOOT
            records = {name: json.loads(pinned(root / COMPILE_RAW / name, pin['sha256']))
                       for name, pin in plan['compile_records'].items()}
            require(records['inputs.json'] == self.inputs and
                    records['staged_files.json'] == compile_owner.expected_stage, 'Compile source records differ')
            delivery.validate_compile(records['result.json'], records['artifacts.json'], compile_owner.identity('ignored'))
            compile_owner.validate_artifact_reply(json.dumps(records['artifacts.json']))
            self.packet = records['artifacts.json']
            pins = {OWNER + '/' + name: row['sha256'] for name, row in self.packet['files'].items()}
            pins.update(reader.TOOLS)
            core = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
            pins[core + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'] = self.packet['loader']['sha256']
            pins[core + '/variants/arduino_uno_q_stm32u585xx/tls-syms.S'] = self.packet['tls_source']['sha256']
            require(len(pins) == 12, 'Remote file inventory differs')
            self.remote_pins, self.commands = pins, queries(reader)
            self.program = self.preamble() + 'import subprocess,base64\n'
            self.program += "if os.path.lexists(REMOTE):raise ValueError('ABI scope path exists')\n"
            self.program += self.executor['extracted_wait'](self.code[self.base.SUPPORT])
            self.program += 'pins=' + repr(pins) + '\ncommands=' + repr(self.commands) + '\n'
            require(reader.REMOTE_READ.count('D173_FILE_ONLY_ABI') == 1, 'File-only primitive seam differs')
            self.program += reader.REMOTE_READ.replace('D173_FILE_ONLY_ABI', 'D238_FILE_ONLY_ABI')
            packed = base64.b64encode(zlib.compress(self.program.encode(), 9)).decode()
            self.bootstrap = 'import base64,zlib;exec(zlib.decompress(base64.b64decode(' + repr(packed) + ')))'
            command = ['/usr/bin/env', '-i', *(k + '=' + v for k, v in self.base.ENV.items()),
                       '/usr/bin/python3', '-I', '-B', '-c', self.bootstrap]
            argv = [self.base.ADB, '-s', self.base.BOARD, 'shell', '-T', shlex.join(command)]
            self.units = len(subprocess.list2cmdline(argv).encode('utf-16-le')) // 2 + 1
            require(self.units <= 30000, 'Windows command exceeds 30000 units')
            return dict(status='STATIC_ABI_CHECKED', reviewed_head=head, compile_head=COMPILE_HEAD,
                        source_sha256=SOURCE, boot_id=BOOT, command_units=self.units,
                        file_commands=4, output=str(self.output))

    return RecorderAbi()


def main(argv):
    require(type(argv) is list and len(argv) == 3 and argv[0] in ('--check-only', '--execute') and
            argv[1] == '--reviewed-head' and re.fullmatch('[0-9a-f]{40}', argv[2]), 'Invalid file-only command')
    owner = prepare_owner(argv[2])
    result = owner.prepare() if argv[0] == '--check-only' else owner.execute()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main(sys.argv[1:])
