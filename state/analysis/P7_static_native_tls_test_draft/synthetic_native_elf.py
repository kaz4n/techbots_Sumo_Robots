# Extends public synthetic ELF fixtures with the six contracted native TLS aliases.
# Builds only in-memory tables; original fixtures and their bytes remain unchanged.
# Tested independently through the frozen D147 contract suite, never a target ELF.
import struct

import synthetic_elf as base


ALIASES = {'_TLS_MODULE_BASE_': 8, '_rand_next': 8, 'z_tls_current': 16,
           'errno': 20, '_strtok_last': 24, '_localtime_buf': 28}
ELF_NAMES = base.ELF_NAMES


def symbol_rows(elf):
    table = base.section(elf, '.symtab')[2]
    strings = base.section(elf, '.strtab')[2]
    names = elf[strings[4]:strings[4] + strings[5]]
    result = []
    for offset in range(table[4], table[4] + table[5], 16):
        row = struct.unpack_from('<IIIBBH', elf, offset)
        name = names[row[0]:names.index(b'\0', row[0])].decode('ascii')
        result.append((name, *row[1:]))
    return result


def replace_symbols(elf, rows, local_end=4):
    strings, offsets = base.names_table(row[0] for row in rows)
    symbols = b''.join(struct.pack('<IIIBBH', offsets[name], *fields)
                       for name, *fields in rows)
    old_shoff = base.header(elf, 'shoff')[2]
    count = base.header(elf, 'shnum')[2]
    sections = [list(struct.unpack_from('<10I', elf, old_shoff + 40 * i))
                for i in range(count)]
    result = bytearray(elf)
    for name, content, alignment in (('.strtab', strings, 1), ('.symtab', symbols, 4)):
        offset = base.align(len(result), alignment)
        result.extend(bytes(offset - len(result)) + content)
        index = base.section(elf, name)[0]
        sections[index][4:6] = (offset, len(content))
        if name == '.symtab':
            sections[index][7] = local_end
    shoff = base.align(len(result))
    result.extend(bytes(shoff - len(result)))
    result.extend(b''.join(struct.pack('<10I', *row) for row in sections))
    return base.edit_header(bytes(result), 'shoff', shoff)


def make_elf(*args, **kwargs):
    elf = base.make_elf(*args, **kwargs)
    aliases = [(name, value, 0, 0x16, 0, 0xfff1) for name, value in ALIASES.items()]
    return replace_symbols(elf, symbol_rows(elf) + aliases)


def packet(**options):
    final = make_elf(**options)
    result = base.packet(**options)
    result['app.ino.elf'] = final
    result['app.ino_debug.elf'] = make_elf(32, b'Native alias debug fixture', **options)
    result['app.ino_temp.elf'] = make_elf(64, b'Native alias first-link fixture', **options)
    result['app.ino.elf-zsk.bin'] = base.diagnostic(final)
    return result
