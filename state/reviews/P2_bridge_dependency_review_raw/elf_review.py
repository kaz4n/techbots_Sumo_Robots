"""Small independent ELF32/ARM decoder for local D098 review receipts only."""
from pathlib import Path
import hashlib
import struct

def cstring(data, at):
    return data[at:data.index(b'\0', at)].decode()

class Elf:
    def __init__(self, path):
        self.path = Path(path)
        self.raw = self.path.read_bytes()
        hdr = struct.unpack_from('<16sHHIIIIIHHHHHH', self.raw)
        assert hdr[0][:6] == b'\x7fELF\x01\x01' and hdr[1:3] == (1, 40)
        assert hdr[11] == 40
        self.section_header_offset = hdr[6]
        self.sections = []
        for idx in range(hdr[12]):
            row = dict(zip(('name_offset','type','flags','address','offset','size',
                            'link','info','alignment','entry_size'),
                           struct.unpack_from('<10I', self.raw, hdr[6] + idx * 40)))
            row['index'] = idx
            self.sections.append(row)
        strsec = self.sections[hdr[13]]
        names = self.section_bytes(strsec)
        for row in self.sections:
            row['name'] = cstring(names, row['name_offset'])
        self.symbols = []
        self.tables = {}
        for row in self.sections:
            if row['type'] != 2:
                continue
            assert row['entry_size'] == 16
            strings = self.section_bytes(self.sections[row['link']])
            table = []
            for offset in range(row['offset'], row['offset'] + row['size'], 16):
                name, value, size, info, other, index = struct.unpack_from('<IIIBBH', self.raw, offset)
                symbol = dict(name=cstring(strings, name), value=value, size=size,
                              bind=info>>4, type=info&15, other=other, section_index=index,
                              section=self.sections[index]['name'] if index<len(self.sections) else str(index))
                table.append(symbol)
            self.tables[row['index']] = table
            self.symbols.extend(table)
        self.relocations = []
        for row in self.sections:
            if row['type'] != 9:
                continue
            assert row['entry_size'] == 8
            for offset in range(row['offset'], row['offset'] + row['size'], 8):
                at, info = struct.unpack_from('<II', self.raw, offset)
                sym = self.tables[row['link']][info>>8]
                self.relocations.append(dict(section=self.sections[row['info']]['name'],
                    offset=at,type=info&255,name=sym['name'],symbol_section=sym['section'],
                    symbol_type=sym['type'],symbol_value=sym['value']))

    def section_bytes(self, section):
        if section['type'] == 8:
            return bytes(section['size'])
        return self.raw[section['offset']:section['offset']+section['size']]

    def functions(self):
        result = {}
        for s in self.symbols:
            if s['type'] != 2 or s['section_index'] == 0 or not s['size']:
                continue
            section = self.sections[s['section_index']]
            at = (s['value'] & ~1) - section['address']
            result[s['name']] = self.section_bytes(section)[at:at+s['size']]
        return result

    def account(self):
        copied = [s for s in self.sections if s['flags'] & 2 and s['name'] != '.llext.rodata.noreloc']
        globals_ = [s for s in self.symbols if s['bind'] == 1 and s['type'] in (1,2)]
        # Exact pinned non-Harvard 32-bit k_heap model, conditional on pristine pool
        # and flash peeking. No target loading or stack/constructor allocation claim.
        def round8(n): return (n+7)&~7
        regions=[]
        for s in copied:
            if s['size'] == 0:
                continue
            assert s['alignment'] <= 8
            prepad = s['offset'] & (s['alignment']-1) if s['alignment'] else 0
            amount = s['size'] + prepad
            chunk = (8 + round8(amount)) if s['alignment'] == 8 else round8(amount+4)
            regions.append(dict(name=s['name'],payload=s['size'],alignment=s['alignment'],
                                prepad=prepad,retained_chunk=chunk))
        sym_request = len(globals_)*8
        sect_request = len(self.sections)*8
        exports = next((s['size'] for s in self.sections if s['name']=='.exported_sym'),0)
        metadata = dict(extension=round8(196+4),section_map=round8(sect_request+4),
                        global_symbols=round8(sym_request+4),export_copy=round8(exports+4),
                        initial_bookkeeping=88)
        peak = sum(r['retained_chunk'] for r in regions)+sum(metadata.values())
        return dict(path=str(self.path),sha256=hashlib.sha256(self.raw).hexdigest(),
                    bytes=len(self.raw),sections=self.sections,section_header_offset=self.section_header_offset,
                    compiler_payload=sum(s['size'] for s in copied),
                    nominal_compiler_remaining=262144-sum(s['size'] for s in copied),
                    global_func_object_count=len(globals_),
                    undefined=sorted({s['name'] for s in self.symbols if s['section_index']==0 and s['name']}),
                    init=[r for r in self.relocations if r['section']=='.init_array'],
                    fini=[r for r in self.relocations if r['section']=='.fini_array'],
                    copied_regions=regions,metadata_chunks=metadata,
                    conditional_pristine_peak_consumption=peak,
                    conditional_pristine_peak_free_span=262144-peak,
                    conditional_largest_payload=262144-peak-4,
                    limitation='Conditional pristine-pool source model, not actual load/free-memory/WCET evidence')

def allocated_signature(elf):
    """Compare object sections without unstable symbol-table indices/debug paths."""
    out = {}
    for s in elf.sections:
        if not s['flags']&2:
            continue
        rels = [dict(offset=r['offset'],type=r['type'],name=r['name'],
                     symbol_section=r['symbol_section'],symbol_value=r['symbol_value'])
                for r in elf.relocations if r['section']==s['name']]
        out[s['name']] = dict(size=s['size'],alignment=s['alignment'],
            bytes_sha256=hashlib.sha256(elf.section_bytes(s)).hexdigest(),relocations=rels)
    return out
