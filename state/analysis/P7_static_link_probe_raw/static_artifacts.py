# Checks the fixed static probe's ELF layout and package bytes without I/O.
# Keeps structural evidence separate from source freshness and runtime acceptance.
# Tested by independent synthetic packets under P7_static_artifact_test_draft.

import hashlib
import struct


FLASH_START = 0x08100010
FLASH_END = 0x081C0000
RAM_START = 0x20013890
RAM_END = 0x20053890
ENTRY = FLASH_START | 1
ELF_NAMES = ('app.ino.elf', 'app.ino_debug.elf', 'app.ino_temp.elf')
LIMITS = {name: 16777216 for name in ELF_NAMES}
LIMITS.update({'app.ino.bin': 786416, 'app.ino.bin-zsk.bin': 786432,
               'app.ino.elf-zsk.bin': 16777216, 'app.ino.map': 16777216})
ALLOCATIONS = {
    '.text': (1, (6,), False),
    '.static_thread_data_area': (1, (2, 3), False),
    '.preinit_array': (16, (2, 3), False),
    '.init_array': (14, (2, 3), False),
    '.fini_array': (15, (2, 3), False),
    '.rodata': (1, (2,), False),
    '.ARM.extab': (1, (2,), False),
    '.ARM': (0x70000001, (2, 130), False),
    '.data': (1, (3, 7), True),
    '.bss': (8, (3,), True),
}
ESSENTIAL = ('entry_point', '_sidata', '_sdata', '_edata', '_sbss', '_ebss')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def extent(start, size, limit, label):
    require(0 <= start <= limit and 0 <= size <= limit - start,
            label + ' extent out of bounds')
    return start + size


def alignment(value):
    return value == 0 or value & (value - 1) == 0


def disjoint(intervals, label):
    previous_end = 0
    for start, end in sorted((a, b) for a, b in intervals if a != b):
        require(start >= previous_end, label + ' overlap')
        previous_end = end


def within(start, end, lower, upper):
    return lower <= start <= end <= upper


def string_at(data, offset):
    require(0 <= offset < len(data), 'string offset out of bounds')
    end = data.find(b'\0', offset, min(len(data), offset + 4097))
    require(end >= 0, 'unterminated or oversized name')
    try:
        return data[offset:end].decode('ascii')
    except UnicodeDecodeError as error:
        raise ValueError('non-ASCII name') from error


def forbidden_name(name):
    return (name.startswith(('.tdata', '.tbss', '.got', '.igot', '.plt', '.iplt'))
            or name == '.ARM.attributes' or name.startswith('.ARM.attributes.'))


class Elf:
    def __init__(self, data):
        self.data = data
        self.header = self.read_header()
        self.sections = self.read_sections()
        self.programs = self.read_programs()
        self.allocated = self.check_layout()
        self.symbols, self.weak = self.read_symbols()
        self.bounds = self.check_symbols()

    def read_header(self):
        require(len(self.data) >= 52, 'short ELF header')
        expected_ident = b'\x7fELF\x01\x01\x01' + bytes(9)
        require(self.data[:16] == expected_ident, 'ELF identification mismatch')
        fields = struct.unpack_from('<HHIIIIIHHHHHH', self.data, 16)
        names = ('type', 'machine', 'version', 'entry', 'phoff', 'shoff', 'flags',
                 'ehsize', 'phentsize', 'phnum', 'shentsize', 'shnum', 'shstrndx')
        h = dict(zip(names, fields))
        require((h['type'], h['machine'], h['version'], h['entry'], h['flags']) ==
                (2, 40, 1, ENTRY, 0x05000400), 'ELF executable/ABI mismatch')
        require((h['ehsize'], h['phentsize'], h['shentsize']) == (52, 32, 40),
                'ELF table entry size mismatch')
        require(1 <= h['phnum'] <= 64 and 1 <= h['shnum'] <= 4096,
                'ELF table count unsupported')
        require(0 < h['shstrndx'] < h['shnum'], 'section name table index invalid')
        phend = extent(h['phoff'], h['phnum'] * 32, len(self.data), 'program table')
        shend = extent(h['shoff'], h['shnum'] * 40, len(self.data), 'section table')
        self.table_ranges = [(0, 52), (h['phoff'], phend), (h['shoff'], shend)]
        disjoint(self.table_ranges, 'ELF tables')
        return h

    def read_sections(self):
        h = self.header
        fields = ('name_offset', 'type', 'flags', 'address', 'offset', 'size',
                  'link', 'info', 'alignment', 'entsize')
        rows = [dict(zip(fields, struct.unpack_from('<10I', self.data,
                h['shoff'] + index * 40))) for index in range(h['shnum'])]
        require(not any(rows[0].values()), 'nonzero NULL section')
        names = rows[h['shstrndx']]
        require(names['type'] == 3, 'section names not STRTAB')
        extent(names['offset'], names['size'], len(self.data), 'section names')
        pool = self.data[names['offset']:names['offset'] + names['size']]
        names_seen, ranges = set(), list(self.table_ranges)
        for index, s in enumerate(rows):
            s['index'] = index
            s['name'] = string_at(pool, s['name_offset'])
            if index == 0:
                require(s['name'] == '', 'NULL section has a name')
                s['bytes'] = b''
                continue
            require(s['name'] and s['name'] not in names_seen, 'duplicate/empty section name')
            names_seen.add(s['name'])
            self.check_section(s)
            if s['type'] != 8:
                end = extent(s['offset'], s['size'], len(self.data), 'section file')
                ranges.append((s['offset'], end))
                s['bytes'] = self.data[s['offset']:end]
            else:
                require(s['offset'] <= len(self.data), 'NOBITS file offset invalid')
                s['bytes'] = b''
        disjoint(ranges, 'section file/table')
        return rows

    def check_section(self, s):
        require(alignment(s['alignment']), 'section alignment is not a power of two')
        require(not forbidden_name(s['name']), 'forbidden section name')
        require(not s['flags'] & 0x400, 'TLS section flag')
        require(s['type'] not in (0, 6, 11), 'unsupported section type')
        require(s['type'] not in (4, 9) or s['size'] == 0, 'relocation requires classification')
        extent(s['address'], s['size'], 1 << 32, 'section address')
        align = max(1, s['alignment'])
        if s['type'] != 8:
            require(s['offset'] % align == 0, 'section file offset alignment')
        if s['flags'] & 2:
            require(s['address'] % align == 0, 'section address alignment')
            require(s['name'] in ALLOCATIONS, 'unexplained allocated section')
            kind, flags, ram = ALLOCATIONS[s['name']]
            require(s['type'] == kind and s['flags'] in flags, 'allocation type/flags')
            if s['size']:
                lo, hi = (RAM_START, RAM_END) if ram else (FLASH_START, FLASH_END)
                require(within(s['address'], s['address'] + s['size'], lo, hi),
                        'allocation outside assigned region')
        else:
            require(s['name'] not in ALLOCATIONS, 'named allocation missing ALLOC')
            require(s['type'] in (1, 2, 3, 4, 7, 9), 'unsupported metadata section')

    def read_programs(self):
        fields = ('type', 'offset', 'vaddr', 'paddr', 'filesz', 'memsz', 'flags', 'align')
        programs = []
        for index in range(self.header['phnum']):
            p = dict(zip(fields, struct.unpack_from('<8I', self.data,
                     self.header['phoff'] + index * 32)))
            require(p['type'] in (0, 1, 6, 0x6474E551, 0x70000001),
                    'unsupported program header')
            if p['type'] == 0:
                continue
            extent(p['offset'], p['filesz'], len(self.data), 'segment file')
            extent(p['vaddr'], p['memsz'], 1 << 32, 'segment address')
            require(p['filesz'] <= p['memsz'], 'segment filesz exceeds memsz')
            require(alignment(p['align']), 'segment alignment invalid')
            require((p['vaddr'] - p['offset']) % max(1, p['align']) == 0,
                    'segment alignment incongruent')
            if p['type'] == 0x6474E551:
                require(not p['flags'] & 1, 'executable stack')
            if p['type'] == 1:
                self.check_load(p)
                programs.append(p)
        disjoint([(p['vaddr'], p['vaddr'] + p['memsz']) for p in programs], 'LOAD VMA')
        disjoint([(p['paddr'], p['paddr'] + p['filesz']) for p in programs], 'LOAD LMA')
        return programs

    def check_load(self, p):
        require(p['flags'] & ~7 == 0, 'unknown LOAD permissions')
        end = p['vaddr'] + p['memsz']
        if p['memsz']:
            require(within(p['vaddr'], end, FLASH_START, FLASH_END) or
                    within(p['vaddr'], end, RAM_START, RAM_END), 'LOAD VMA outside regions')
        if p['filesz']:
            end = extent(p['paddr'], p['filesz'], 1 << 32, 'LOAD physical')
            require(within(p['paddr'], end, FLASH_START, FLASH_END), 'LOAD LMA outside flash')

    def map_section(self, s):
        matches = [p for p in self.programs if within(s['address'],
                   s['address'] + s['size'], p['vaddr'], p['vaddr'] + p['memsz'])]
        require(len(matches) == 1, 'section needs exactly one LOAD')
        p = matches[0]
        permissions = 4 | (2 if s['flags'] & 1 else 0) | (1 if s['flags'] & 4 else 0)
        require(p['flags'] & permissions == permissions, 'LOAD lacks section permission')
        s['load_address'] = None
        if s['type'] == 8:
            return
        delta = s['address'] - p['vaddr']
        require(delta + s['size'] <= p['filesz'] and s['offset'] == p['offset'] + delta,
                'section file/VMA mapping mismatch')
        lma = p['paddr'] + delta
        require(within(lma, lma + s['size'], FLASH_START, FLASH_END), 'section LMA outside flash')
        require(ALLOCATIONS[s['name']][2] or lma == s['address'], 'flash LMA differs from VMA')
        s['load_address'] = lma

    def check_layout(self):
        allocated = [s for s in self.sections if s['flags'] & 2 and s['size']]
        self.named = {s['name']: s for s in allocated}
        require(all(name in self.named for name in ('.text', '.data', '.bss')),
                'required allocation missing or empty')
        disjoint([(s['address'], s['address'] + s['size']) for s in allocated], 'section VMA')
        for s in allocated:
            self.map_section(s)
        for p in self.programs:
            require(any(within(s['address'], s['address'] + s['size'], p['vaddr'],
                               p['vaddr'] + p['memsz']) for s in allocated), 'empty LOAD mapping')
        text, data, bss = (self.named[n] for n in ('.text', '.data', '.bss'))
        require(text['address'] == FLASH_START and text['size'] >= 2, 'text/entry placement')
        require(data['address'] == RAM_START, 'data not at RAM origin')
        require(data['address'] + data['size'] <= bss['address'], 'data/bss order')
        self.ram_end = bss['address'] + bss['size']
        require(self.ram_end % 1024 == 0, 'BSS final alignment')
        ranges = [(s['load_address'], s['load_address'] + s['size'])
                  for s in allocated if s['load_address'] is not None]
        disjoint(ranges, 'section LMA')
        require(min(a for a, _ in ranges) == FLASH_START, 'flat payload origin')
        self.flash_end = max(b for _, b in ranges)
        for p in self.programs:
            top = self.ram_end if p['vaddr'] >= RAM_START else self.flash_end
            require(p['vaddr'] + p['memsz'] <= top, 'segment extends beyond allocations')
            if p['filesz']:
                require(p['paddr'] + p['filesz'] <= self.flash_end, 'segment exceeds flash load end')
        return sorted(allocated, key=lambda s: (s['address'], s['name']))

    def read_symbols(self):
        tables = [s for s in self.sections if s['type'] == 2]
        require(len(tables) == 1, 'need one SYMTAB')
        s = tables[0]
        require(s['entsize'] == 16 and s['size'] % 16 == 0 and
                1 <= s['size'] // 16 <= 65536, 'SYMTAB entry size/count')
        count = s['size'] // 16
        require(1 <= s['info'] <= count, 'SYMTAB local partition invalid')
        require(0 < s['link'] < len(self.sections) and self.sections[s['link']]['type'] == 3,
                'SYMTAB string link invalid')
        pool = self.sections[s['link']]['bytes']
        require(s['bytes'][:16] == bytes(16), 'nonzero null symbol')
        symbols, weak = {}, set()
        for index in range(count):
            name, value, size, info, other, section = struct.unpack_from('<IIIBBH', s['bytes'], index * 16)
            symbol = {'value': value, 'size': size, 'bind': info >> 4,
                      'type': info & 15, 'other': other, 'section': section}
            name = string_at(pool, name)
            self.check_symbol(symbol, index, s['info'], name)
            symbols.setdefault(name, []).append(symbol)
            if name and section == 0 and symbol['bind'] == 2:
                weak.add(name)
        return symbols, weak

    def check_symbol(self, symbol, index, split, name):
        bind, kind, section = symbol['bind'], symbol['type'], symbol['section']
        require(bind in (0, 1, 2) and kind in (0, 1, 2, 3, 4) and symbol['other'] <= 3,
                'unsupported symbol encoding')
        require((bind == 0) == (index < split), 'SYMTAB local partition mismatch')
        require(section < len(self.sections) or section == 0xFFF1, 'symbol section index invalid')
        if kind in (3, 4):
            require(bind == 0, 'SECTION/FILE symbol not local')
            require((kind == 3 and 0 < section < len(self.sections)) or
                    (kind == 4 and section == 0xFFF1), 'SECTION/FILE index invalid')
        require(not name or section != 0 or bind == 2, 'unresolved nonweak symbol')

    def check_symbols(self):
        selected = {}
        for name in ESSENTIAL:
            entries = self.symbols.get(name, [])
            require(len(entries) == 1 and entries[0]['section'] != 0,
                    'essential symbol missing/ambiguous/undefined: ' + name)
            selected[name] = entries[0]
        entry, text = selected['entry_point'], self.named['.text']
        require(entry['type'] == 2 and entry['value'] == ENTRY and
                entry['section'] == text['index'] and 0 < entry['size'] <= text['size'],
                'entry symbol inconsistent')
        self.entry_identity = tuple(entry[key] for key in
                                    ('value', 'size', 'type', 'bind', 'other')) + ('.text',)
        values = {name: s['value'] for name, s in selected.items()}
        data, bss = self.named['.data'], self.named['.bss']
        require(values['_sidata'] == data['load_address'] and
                values['_sdata'] == data['address'] and
                values['_edata'] == data['address'] + data['size'], 'data copy symbols mismatch')
        require(all(values[n] % 4 == 0 for n in ESSENTIAL[1:]), 'copy/zero alignment')
        require(values['_sbss'] == bss['address'] and
                within(values['_sbss'], values['_ebss'], bss['address'], self.ram_end),
                'BSS zero symbols mismatch')
        require((values['_ebss'] + 1023) // 1024 * 1024 == self.ram_end,
                'BSS zero/padding mismatch')
        return values

    def normalized(self):
        fields = ('name', 'type', 'flags', 'address', 'size', 'alignment', 'load_address', 'bytes')
        allocated = sorted((s for s in self.sections if s['flags'] & 2),
                           key=lambda s: (s['address'], s['name']))
        return [tuple(s.get(f) for f in fields) for s in allocated]

    def binary(self):
        result = bytearray(self.flash_end - FLASH_START)
        for s in self.allocated:
            if s['load_address'] is not None:
                offset = s['load_address'] - FLASH_START
                result[offset:offset + s['size']] = s['bytes']
        return bytes(result)


def package_header(length):
    return bytes(7) + struct.pack('<BIHBB', 1, length, 0x2341, 2, 0)


def validate_packages(artifacts, final):
    raw = artifacts['app.ino.bin']
    require(not raw.startswith(b'\x7fELF'), 'raw BIN would bypass header prepend')
    require(raw == final.binary(), 'BIN differs from allocated load bytes/gaps')
    flat = artifacts['app.ino.bin-zsk.bin']
    require(flat == package_header(len(flat)) + raw, 'flat ZSK header/payload mismatch')
    elf = artifacts['app.ino.elf']
    patched = elf[:7] + package_header(len(elf))[7:] + elf[16:]
    require(artifacts['app.ino.elf-zsk.bin'] == patched, 'diagnostic ELF-ZSK mismatch')


def report(artifacts, images):
    final, values = images[0], images[0].bounds
    section_fields = ('name', 'type', 'flags', 'address', 'size', 'alignment', 'load_address')
    return {
        'status': 'STATIC_LAYOUT_PACKAGE_PASS', 'entry': ENTRY,
        'flash': {'start': FLASH_START, 'end': final.flash_end, 'remaining': FLASH_END - final.flash_end},
        'ram': {'start': RAM_START, 'end': final.ram_end, 'remaining': RAM_END - final.ram_end},
        'data_copy': {'source': values['_sidata'], 'destination': values['_sdata'],
                      'bytes': values['_edata'] - values['_sdata']},
        'bss_zero': {'start': values['_sbss'], 'end': values['_ebss'],
                     'bytes': values['_ebss'] - values['_sbss']},
        'sections': [{key: s[key] for key in section_fields} for s in final.allocated],
        'weak_undefined': sorted(set().union(*(elf.weak for elf in images))),
        'artifacts': {name: {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
                      for name, data in artifacts.items()},
    }


def validate_artifacts(artifacts):
    require(type(artifacts) is dict, 'artifacts must be a dict')
    require(all(type(name) is str for name in artifacts) and set(artifacts) == set(LIMITS),
            'fixed seven artifacts required')
    for name, data in artifacts.items():
        require(type(data) is bytes and 0 < len(data) <= LIMITS[name], 'artifact type/size invalid')
    images = [Elf(artifacts[name]) for name in ELF_NAMES]
    final = images[0]
    for image in images[1:]:
        require(image.normalized() == final.normalized() and image.bounds == final.bounds and
                image.entry_identity == final.entry_identity,
                'allocated image/initialization differs across ELF forms')
    validate_packages(artifacts, final)
    return report(artifacts, images)
