# Constructs tiny independent ELF/package fixtures from the public artifact contract.
# Separates section bytes, load addresses, BSS padding and diagnostic-only changes.
# Draft support only; not executed or frozen before reviewed scope adoption.
import struct


FLASH = 0x08100010
RAM = 0x20013890
BSS_END = 0x20013c00
TEXT = b'\x00\xbf\x70\x47\x00\xbf\x00\xbf'
RODATA = b'RODATA!!'
DATA = b'\x01\x02\x03\x04\x05\x06\x07\x08'
RAW = TEXT + bytes(8) + RODATA + bytes(8) + DATA
ELF_NAMES = ('app.ino.elf', 'app.ino_debug.elf', 'app.ino_temp.elf')


def align(value, alignment=4):
    return (value + alignment - 1) & -alignment


def names_table(names):
    data = bytearray(b'\0')
    offsets = {'': 0}
    for name in names:
        if name not in offsets:
            offsets[name] = len(data)
            data.extend(name.encode('ascii') + b'\0')
    return bytes(data), offsets


def symbols(weak_name='optional_weak_hook'):
    rows = [('', 0, 0, 0, 0), ('', FLASH, 0, 3, 1),
            ('local_label', FLASH + 2, 0, 0, 1),
            ('local_label', FLASH + 4, 0, 0, 1),
            ('entry_point', FLASH | 1, 2, 0x12, 1),
            ('_sidata', FLASH + 32, 0, 0x10, 0xfff1),
            ('_sdata', RAM, 0, 0x10, 3),
            ('_edata', RAM + 8, 0, 0x10, 3),
            ('_sbss', RAM + 8, 0, 0x10, 4),
            ('_ebss', RAM + 24, 0, 0x10, 4),
            (weak_name, 0, 0, 0x20, 0)]
    strings, names = names_table(row[0] for row in rows)
    table = b''.join(struct.pack('<IIIBBH', names[name], value, size, info, 0, section)
                     for name, value, size, info, section in rows)
    return strings, table


def section_rows(base, debug, rodata_name, rodata_type, rodata_flags):
    rows = [
        ['', 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ['.text', 1, 6, FLASH, base, len(TEXT), 0, 0, 4, 0],
        [rodata_name, rodata_type, rodata_flags, FLASH + 16, base + 16, len(RODATA), 0, 0, 4, 0],
        ['.data', 1, 3, RAM, base + 32, len(DATA), 0, 0, 4, 0],
        ['.bss', 8, 3, RAM + 8, base + 40, BSS_END - RAM - 8, 0, 0, 8, 0],
        ['.shstrtab', 3, 0, 0, 0, 0, 0, 0, 1, 0],
        ['.strtab', 3, 0, 0, 0, 0, 0, 0, 1, 0],
        ['.symtab', 2, 0, 0, 0, 0, 6, 4, 4, 16],
    ]
    if debug:
        rows.append(['.debug_info', 1, 0, 0, 0, 0, 0, 0, 1, 0])
    return rows


def make_elf(file_pad=0, debug=b'', weak_name='optional_weak_hook',
             rodata_name='.rodata', rodata_type=1, rodata_flags=2):
    base = 0x100 + file_pad
    rows = section_rows(base, debug, rodata_name, rodata_type, rodata_flags)
    section_strings, section_names = names_table(row[0] for row in rows)
    symbol_strings, symbol_table = symbols(weak_name)
    blob = bytearray(base + 40)
    blob[base:base + 40] = TEXT + b'\xa5' * 8 + RODATA + b'\x5a' * 8 + DATA
    extras = [(5, section_strings), (6, symbol_strings), (7, symbol_table)]
    if debug:
        extras.append((8, debug))
    for index, data in extras:
        offset = align(len(blob), rows[index][8])
        blob.extend(bytes(offset - len(blob)) + data)
        rows[index][4:6] = [offset, len(data)]
    shoff = align(len(blob))
    blob.extend(bytes(shoff - len(blob)))
    for row in rows:
        blob.extend(struct.pack('<10I', section_names[row[0]], *row[1:]))
    ident = b'\x7fELF\x01\x01\x01' + bytes(9)
    header = struct.pack('<16sHHIIIIIHHHHHH', ident, 2, 40, 1, FLASH | 1,
                         52, shoff, 0x05000400, 52, 32, 3, 40, len(rows), 5)
    blob[:52] = header
    programs = [(1, base, FLASH, FLASH, 24, 24, 5, 4),
                (1, base + 32, RAM, FLASH + 32, 8, BSS_END - RAM, 6, 4),
                (0x6474e551, 0, 0, 0, 0, 0, 6, 4)]
    blob[52:148] = b''.join(struct.pack('<8I', *row) for row in programs)
    return bytes(blob)


def metadata(length):
    result = bytearray(16)
    result[7] = 1
    struct.pack_into('<I', result, 8, length)
    struct.pack_into('<H', result, 12, 0x2341)
    result[14] = 2
    return bytes(result)


def diagnostic(elf):
    result = bytearray(elf)
    result[7:16] = metadata(len(elf))[7:16]
    return bytes(result)


def packet(**options):
    final = make_elf(**options)
    return {
        'app.ino.elf': final,
        'app.ino_debug.elf': make_elf(32, b'Independent debug payload', **options),
        'app.ino_temp.elf': make_elf(64, b'Different first-link debug payload', **options),
        'app.ino.bin': RAW,
        'app.ino.bin-zsk.bin': metadata(len(RAW) + 16) + RAW,
        'app.ino.elf-zsk.bin': diagnostic(final),
        'app.ino.map': b'Synthetic map bytes; no entry-order or source evidence.\n',
    }


def header(elf, field):
    fields = {'type': (16, 'H'), 'machine': (18, 'H'), 'version': (20, 'I'),
              'entry': (24, 'I'), 'phoff': (28, 'I'), 'shoff': (32, 'I'),
              'flags': (36, 'I'), 'ehsize': (40, 'H'), 'phentsize': (42, 'H'),
              'phnum': (44, 'H'), 'shentsize': (46, 'H'), 'shnum': (48, 'H'),
              'shstrndx': (50, 'H')}
    offset, kind = fields[field]
    return offset, kind, struct.unpack_from('<' + kind, elf, offset)[0]


def edit_header(elf, field, value):
    offset, kind, _ = header(elf, field)
    return edit_number(elf, offset, value, kind)


def edit_number(elf, offset, value, kind='I'):
    result = bytearray(elf)
    struct.pack_into('<' + kind, result, offset, value)
    return bytes(result)


def section(elf, name):
    shoff = header(elf, 'shoff')[2]
    names_index = header(elf, 'shstrndx')[2]
    names = struct.unpack_from('<10I', elf, shoff + names_index * 40)
    strings = elf[names[4]:names[4] + names[5]]
    for index in range(header(elf, 'shnum')[2]):
        offset = shoff + index * 40
        row = struct.unpack_from('<10I', elf, offset)
        label = strings[row[0]:strings.index(b'\0', row[0])].decode('ascii')
        if label == name:
            return index, offset, row
    raise KeyError(name)


def edit_section(elf, name, field, value):
    fields = ('name', 'type', 'flags', 'address', 'offset', 'size', 'link',
              'info', 'alignment', 'entsize')
    return edit_number(elf, section(elf, name)[1] + 4 * fields.index(field), value)


def edit_program(elf, index, field, value):
    fields = ('type', 'offset', 'vaddr', 'paddr', 'filesz', 'memsz', 'flags', 'alignment')
    offset = header(elf, 'phoff')[2] + index * 32 + fields.index(field) * 4
    return edit_number(elf, offset, value)


def symbol(elf, name, occurrence=0):
    symbols = section(elf, '.symtab')[2]
    strings = section(elf, '.strtab')[2]
    names = elf[strings[4]:strings[4] + strings[5]]
    matches = []
    for index in range(symbols[5] // 16):
        offset = symbols[4] + index * 16
        row = struct.unpack_from('<IIIBBH', elf, offset)
        label = names[row[0]:names.index(b'\0', row[0])].decode('ascii')
        if label == name:
            matches.append((index, offset, row))
    return matches[occurrence]


def edit_symbol(elf, name, field, value, occurrence=0):
    fields = {'name': (0, 'I'), 'value': (4, 'I'), 'size': (8, 'I'),
              'info': (12, 'B'), 'other': (13, 'B'), 'section': (14, 'H')}
    delta, kind = fields[field]
    return edit_number(elf, symbol(elf, name, occurrence)[1] + delta, value, kind)


def mutate_elfs(artifacts, change, names=ELF_NAMES):
    result = dict(artifacts)
    for name in names:
        result[name] = change(result[name])
    result['app.ino.elf-zsk.bin'] = diagnostic(result['app.ino.elf'])
    return result


def replace_raw(artifacts, raw):
    result = dict(artifacts)
    result['app.ino.bin'] = raw
    result['app.ino.bin-zsk.bin'] = metadata(len(raw) + 16) + raw
    return result
