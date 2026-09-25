# Observes new static diagnostic initialization instructions from pinned ELF files.
# Reuses the reviewed file-only owner with explicit scope substitutions only.
# Controlled command/parser checks and separate review precede native execution.
import base64
import hashlib
from pathlib import Path
import re
import stat
import sys
import types

ROOT = Path(__file__).absolute().parents[3]
RAW = 'state/analysis/P7_app_motor_fault_compile_raw/'
ORIGINAL = RAW + 'inspect_static_abi.py'
ORIGINAL_SHA = '0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c'
ABI_RESULT = RAW + 'native_abi_static01/result.json'
ABI_SHA = '684670c538bb032ab3b4b4ebc68ffd6cbecb743f0209aacc154af58b244101d2'
SUBSTITUTIONS = (
    ("'/inspect_static_abi.py'", "'/inspect_static_entry.py'", 1),
    ("'native_abi_static01'", "'native_entry_static01'", 1),
    ('app-motor-fault-abi-static01', 'app-motor-fault-entry-static01', 1),
    ('D188_STATIC_FILE_ONLY_ABI', 'D188_STATIC_FILE_ONLY_ENTRY', 2),
    ('STATIC_ABI_CHECKED', 'STATIC_ENTRY_CHECKED', 1),
    ('STATIC_ABI_OBSERVED', 'STATIC_ENTRY_OBSERVED', 2),
    ("'file-abi'", "'file-entry'", 1),
    ("'abi.json'", "'entry.json'", 1),
    ('StaticAbi', 'StaticEntry', 2),
)
RANGES = (
    ('entry_point', 0x08100010, 0x081000c8, ('entry_point',)),
    ('setup', 0x081000c8, 0x081000e8, ('setup',)),
    ('loop', 0x081000e8, 0x08100104, ('loop',)),
    ('global_initializer', 0x08100104, 0x08100298, ('_GLOBAL__sub_I_setup',)),
    ('app_dump_port', 0x081002a8, 0x081002d0, ('_ZN3app12unoQDumpPortERN8recorder4dump12UnoQDumpPortE',)),
    ('sources_port', 0x081003e0, 0x0810045c, ('_ZN3app13NativeSources4portEv',)),
    ('sources_adc_port', 0x0810045c, 0x08100470, ('_ZN3app13NativeSources7adcPortEv',)),
    ('runner_constructor', 0x08103984, 0x08103b58, tuple('_ZN15app_motor_fault6RunnerC' + str(n) +
        'ERKN6motors4PortERKN5power9InputPortERKN3app10SourcePortERKNS9_8DumpPortE' for n in (1, 2))),
    ('runner_application_valid', 0x08103b58, 0x08103bb0, ('_ZNK15app_motor_fault6Runner16applicationValidEv',)),
    ('runner_stop_reason', 0x08103bb0, 0x08103c08, ('_ZNK15app_motor_fault6Runner10stopReasonEv',)),
    ('runner_freeze', 0x08103c08, 0x08103c94, ('_ZN15app_motor_fault6Runner6freezeENS_6ReasonE',)),
    ('runner_begin', 0x08103c94, 0x08103d24, ('_ZN15app_motor_fault6Runner5beginERKN11motor_fault6GrantsE',)),
    ('runner_poll', 0x08103d24, 0x08103d78, ('_ZN15app_motor_fault6Runner4pollEv',)),
    ('dump_port', 0x0810c760, 0x0810c774, ('_ZN8recorder4dump12UnoQDumpPort4portEv',)),
    ('loop_hook', 0x08110bfc, 0x08110bfe, ('_Z10__loopHookv',)),
    ('candidate_rate', 0x08110c70, 0x08110cd8, ('_ZN6motors12_GLOBAL__N_113candidateRateEj',)),
    ('candidate_period', 0x08110cd8, 0x08110d10, ('_ZN6motors12_GLOBAL__N_115candidatePeriodEj',)),
    ('motor_port', 0x08110ed8, 0x08110f64, ('_ZN6motors8UnoQPort4portEv',)),
    ('power_reader_port', 0x0811326c, 0x08113290, ('_ZN5power15readerInputPortERNS_6ReaderE',)),
    ('trace_constructor', 0x08115bec, 0x08115c7c,
        tuple('_ZN11motor_fault5TraceC' + str(n) + 'ERKN6motors4PortE' for n in (1, 2))),
    ('trace_port', 0x08115c7c, 0x08115cfc, ('_ZN11motor_fault5Trace4portEv',)),
    ('memcpy', 0x08115f6c, 0x08115f74, ('memcpy',)),
    ('memset', 0x08115f74, 0x08115f7c, ('memset',)),
    ('unsigned_divide', 0x0811602c, 0x08116036, ('__aeabi_uldivmod',)),
    ('init_variant', 0x08116044, 0x08116046, ('initVariant',)),
    ('main', 0x08116048, 0x08116074, ('main',)),
    ('start_static_threads', 0x08116074, 0x081160e0, ('_Z20start_static_threadsv',)),
)
BOUNDS = {name: (0x0811621c if name == '__init_array_end' else 0x08116218)
          for name in ('__init_array_start', '__init_array_end', '__preinit_array_start',
                       '__preinit_array_end', '__static_thread_data_list_start', '__static_thread_data_list_end')}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def queries(reader):
    expressions = []
    for index, (_, start, end, _) in enumerate(RANGES):
        expressions += [f'echo SUMOX_ENTRY_{index:02d}\\n', f'disassemble /r 0x{start:08x},0x{end:08x}']
    expressions += ['echo SUMOX_ENTRY_END\\n']
    build = '/home/arduino/sumox26_codex_build/app-motor-fault-static01/build/app_motor_fault.ino'
    return [[reader.PREFIX + 'readelf', '--version'], [reader.PREFIX + 'gdb', '--version'],
            [reader.PREFIX + 'readelf', '-hSWs', '-x', '.init_array', build + '.elf'],
            reader.gdb(build + '_debug.elf', expressions)]


def symbol_rows(elf):
    rows = {}
    pattern = r'^\s*\d+:\s+([0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+|\d+)\s+(\w+)\s+(\w+)\s+DEFAULT\s+(\d+)\s+(\S+)\s*$'
    for address, size, kind, bind, section, name in re.findall(pattern, elf, re.MULTILINE):
        value = (int(address, 16), int(size, 16 if size.startswith('0x') else 10), kind, bind, int(section))
        rows.setdefault(name, []).append(value)
    return rows


def symbols(elf, layout):
    require(re.search(r'^\s*Type:\s+EXEC \(Executable file\)\s*$', elf, re.MULTILINE), 'Expected static ET_EXEC')
    rows = symbol_rows(elf)
    text = next(item for item in layout['sections'] if item['name'] == '.text')
    for label, start, end, aliases in RANGES:
        require(text['address'] <= start < end <= text['address'] + text['size'], 'Function outside checked text')
        bind = 'LOCAL' if label in ('global_initializer', 'candidate_rate', 'candidate_period') else (
            'WEAK' if label in ('init_variant', 'main') else 'GLOBAL')
        for name in aliases:
            require(rows.get(name) == [(start | 1, end - start, 'FUNC', bind, 1)], 'Function symbol changed: ' + name)
    for name, address in BOUNDS.items():
        bind = 'GLOBAL' if name.startswith('__static_thread') else 'LOCAL'
        require(rows.get(name) == [(address, 0, 'NOTYPE', bind, 2)], 'Initialization bound changed: ' + name)


def initializer(elf, layout):
    sections = [item for item in layout['sections'] if item['name'] == '.init_array']
    require(len(sections) == 1 and sections[0]['address'] == 0x08116218 and sections[0]['size'] == 4,
            'Checked initializer section differs')
    marker = "Hex dump of section '.init_array':"
    require(elf.count(marker) == 1, 'Missing or duplicate initializer byte dump')
    dump = elf.split(marker, 1)[1]
    lines = re.findall(r'^\s*0x([0-9a-fA-F]+)\s+([0-9a-fA-F]{8})(?:\s+[^\r\n]*)?$', dump, re.MULTILINE)
    require(len(lines) == 1 and int(lines[0][0], 16) == 0x08116218, 'Initializer byte span differs')
    data = bytes.fromhex(lines[0][1])
    pointer = int.from_bytes(data, 'little')
    require(pointer == 0x08100105, 'Initializer pointer differs from observed constructor symbol')
    return dict(address=0x08116218, bytes_hex=data.hex(), pointer=pointer, bounds=BOUNDS)


def disassembly(debug):
    labels = [f'SUMOX_ENTRY_{index:02d}' for index in range(len(RANGES))] + ['SUMOX_ENTRY_END']
    require(re.findall(r'^SUMOX_ENTRY_(?:\d{2}|END)$', debug, re.MULTILINE) == labels,
            'Missing, extra, reordered or duplicate entry markers')
    observed = []
    for current, following, (name, start, end, aliases) in zip(labels, labels[1:], RANGES):
        block = debug.split(current + '\n', 1)[1].split(following + '\n', 1)[0]
        headers = re.findall(r'^Dump of assembler code from (0x[0-9a-fA-F]+) to (0x[0-9a-fA-F]+):$', block, re.MULTILINE)
        require(len(headers) == 1 and tuple(int(value, 16) for value in headers[0]) == (start, end) and
                block.count('End of assembler dump.') == 1, 'Disassembly header/end differs')
        rows = re.findall(r'^\s*(0x[0-9a-fA-F]+)(?:\s+<[^>\r\n]+>)?:\s+([0-9a-fA-F]{4}(?:[ \t]+[0-9a-fA-F]{4})?|[0-9a-fA-F]{8})[ \t]+([^\r\n]+)$', block, re.MULTILINE)
        addresses = [int(row[0], 16) for row in rows]
        require(addresses and addresses[0] == start and addresses == sorted(set(addresses)) and
                all(start <= value < end for value in addresses), 'Empty or out-of-range instruction rows')
        require(len(re.findall(r'^\s*0x[0-9a-fA-F]+', block, re.MULTILINE)) == len(rows),
                'Unparsed instruction address row')
        cursor = start
        for address, opcodes, _ in rows:
            require(int(address, 16) == cursor, 'Gap or overlap in disassembly')
            cursor += len(''.join(opcodes.split())) // 2
        require(cursor == end, 'Disassembly does not exactly cover selected function')
        observed.append(dict(name=name, start=start, end=end, symbols=aliases,
                             instruction_rows=len(rows), validated_bytes=cursor-start,
                             raw_block_sha256=sha(block.encode())))
    return observed


def summarize(result, layout):
    elf, debug = [base64.b64decode(row['stdout_base64'], validate=True).decode('utf-8')
                  for row in result['commands'][2:]]
    symbols(elf, layout)
    return dict(status='STATIC_ENTRY_OBSERVED', initialization=initializer(elf, layout),
                disassembly=disassembly(debug),
                limitation='File instructions only; semantic review pending, no MCU execution or runtime acceptance')


def load():
    path = ROOT / ORIGINAL
    for item in (path, *path.parents):
        info = item.lstat()
        kind = stat.S_ISREG if item == path else stat.S_ISDIR
        require(kind(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 1024, 'Nonplain original helper')
    require(path.stat().st_size <= 1048576, 'Original helper exceeds bound')
    raw = path.read_bytes()
    require(sha(raw) == ORIGINAL_SHA, 'Original ABI helper changed')
    source = raw.decode('utf-8')
    for old, new, count in SUBSTITUTIONS:
        require(source.count(old) == count, 'Private substitution count changed: ' + old)
        source = source.replace(old, new)
    module = types.ModuleType('_fixed_static_entry')
    module.__file__ = str(ROOT / ORIGINAL)
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    module.HARD_PINS.update({ORIGINAL: ORIGINAL_SHA, ABI_RESULT: ABI_SHA})
    module.queries, module.summarize = queries, summarize
    return module


def main(argv):
    load().main(argv)


if __name__ == '__main__':
    main(sys.argv[1:])
