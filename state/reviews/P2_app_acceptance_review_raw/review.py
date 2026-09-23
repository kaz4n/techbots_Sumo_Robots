"""Local independent receipt, source, ELF32 and object audit; no board/build calls."""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P2_app_acceptance_raw'
OUT = Path(__file__).resolve().parent
BASE = ROOT / 'state/analysis/P2_bridge_dependency_raw'
sys.path.insert(0, str(ROOT / 'tools'))
import app_build_policy as policy


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return policy.decode(path.read_text(encoding='utf-8'))


class ELF:
    """New minimal decoder: does not reuse the author/D098 accounting code."""
    def __init__(self, path):
        self.raw = path.read_bytes()
        h = struct.unpack_from('<16sHHIIIIIHHHHHH', self.raw)
        assert h[0][:6] == b'\x7fELF\x01\x01' and h[1:3] == (1, 40)
        assert h[11] == 40
        rows = [struct.unpack_from('<10I', self.raw, h[6] + 40*i) for i in range(h[12])]
        table = self.raw[rows[h[13]][4]:rows[h[13]][4] + rows[h[13]][5]]
        text = lambda b, offset: b[offset:b.index(b'\0', offset)].decode()
        self.sections = [dict(zip(('name_offset', 'type', 'flags', 'address', 'offset',
            'size', 'link', 'info', 'align', 'entry_size'), row), name=text(table, row[0])) for row in rows]
        self.symbols = []
        self.tables = {}
        for idx, s in enumerate(self.sections):
            if s['type'] != 2:
                continue
            assert s['entry_size'] == 16
            strings = self.bytes(self.sections[s['link']])
            symbols = []
            for at in range(s['offset'], s['offset'] + s['size'], 16):
                name, value, size, info, other, section = struct.unpack_from('<IIIBBH', self.raw, at)
                symbols.append(dict(name=text(strings, name), value=value, size=size,
                    bind=info >> 4, type=info & 15, section=section, other=other))
            self.tables[idx] = symbols
            self.symbols.extend(symbols)
        self.relocations = []
        for s in self.sections:
            if s['type'] != 9:
                continue
            assert s['entry_size'] == 8
            for at in range(s['offset'], s['offset'] + s['size'], 8):
                offset, info = struct.unpack_from('<II', self.raw, at)
                symbol = self.tables[s['link']][info >> 8]
                self.relocations.append(dict(section=s['info'], offset=offset,
                    type=info & 255, symbol=symbol))

    def bytes(self, section):
        return bytes(section['size']) if section['type'] == 8 else self.raw[section['offset']:section['offset']+section['size']]

    def symbol(self, name):
        matches = [s for s in self.symbols if s['name'] == name and s['section'] != 0]
        assert len(matches) == 1, (name, matches)
        return matches[0]

    def function(self, name):
        s = self.symbol(name)
        section = self.sections[s['section']]
        start = (s['value'] & ~1) - section['address']
        data = bytearray(self.bytes(section)[start:start + s['size']])
        targets = []
        for r in self.relocations:
            if r['section'] != s['section'] or not start <= r['offset'] < start+s['size']:
                continue
            target = r['symbol']
            at = r['offset']-start
            targets.append((at, r['type'], target['name'], target['section']))
            # Absolute BSS offsets vary when MATCH retains additional functions.
            if target['type'] == 3 and self.sections[target['section']]['name'] == '.bss':
                offset = struct.unpack_from('<I', data, at)[0]
                owners = [o['name'] for o in self.symbols if o['type'] == 1 and
                    o['section'] == target['section'] and o['value'] == offset]
                assert len(owners) == 1, (name, offset, owners)
                targets[-1] = (at, r['type'], owners[0], '.bss')
                data[at:at+4] = bytes(4)
        return dict(bytes=data.hex(), targets=targets, bind=s['bind'], size=s['size'])

    def imports(self):
        return sorted({s['name'] for s in self.symbols if s['section'] == 0 and s['name']})


def relocation_map(text):
    result = {}
    name = None
    for line in text.splitlines():
        match = re.match(r"Relocation section '\.rel([^']+)'", line)
        if match:
            name = match[1]
            result[name] = []
        match = re.match(r'([0-9a-f]+)\s+[0-9a-f]+\s+(R_ARM_\S+)\s+([0-9a-f]+)\s+(.+)', line)
        if match and name is not None:
            result[name].append((int(match[1], 16), match[2], int(match[3], 16), match[4]))
    return result


def object_diff(old, new):
    before = {o['path']: o for o in old}
    after = {o['path']: o for o in new}
    assert before.keys() == after.keys()
    changed = []
    sections = relocations = 0
    for path in sorted(before):
        a, b = before[path], after[path]
        sa, sb = ({s['name']: s for s in o['alloc_sections']} for o in (a, b))
        ra, rb = (relocation_map(o['relocations']['stdout']) for o in (a, b))
        common = sa.keys() & sb.keys()
        sections += len(common)
        relocations += sum(len(rb.get(n, [])) for n in common)
        differences = dict(changed=[n for n in sorted(common) if sa[n] != sb[n]],
            relocated=[n for n in sorted(common) if ra.get(n, []) != rb.get(n, [])],
            added=sorted(sb.keys()-sa.keys()), removed=sorted(sa.keys()-sb.keys()))
        if any(differences.values()):
            changed.append(dict(path=path, **differences))
    return dict(objects=len(after), common_sections=sections, relocations=relocations, changes=changed)


def mode_review(mode, old, baseline):
    folder = RAW / mode
    audit = read(folder / 'audit.json')
    receipt = ROOT / read(folder / 'command.json')['receipt']
    v = read(receipt / 'verified.json')
    command = read(receipt / 'command.json')
    flags = '-DMATCH=1 -DMOTORS_ALLOWED=1' if mode.startswith('match') else '-DMATCH=0 -DMOTORS_ALLOWED=0'
    expected_fqbn = 'arduino:zephyr:unoq' + (':wait_linux_boot=no' if mode.endswith('immediate') else '')
    assert v['fqbn'] == expected_fqbn and v['compiler_returncode'] == 0 and v['precompile_checks'] is True
    assert v['policy'] == 'native-app-v1' and v['source_sha256'] == old['source_sha256']
    props = policy.validate_result((receipt/'compile.stdout.json').read_text(), v['fqbn'], flags, v['build_path'])
    preflight = policy.validate_preflight((receipt/'properties.stdout.json').read_text(),
        v['fqbn'], flags, v['build_path'], v['resolved_directories']['data'])
    time_keys = {'extra.time.utc', 'extra.time.local'}
    assert {k:v for k,v in props.items() if k not in time_keys} == {k:v for k,v in preflight.items() if k not in time_keys}
    assert command == read(receipt/'compile.command.json')
    assert read(receipt/'properties.command.json') == command[:-1]+['--show-properties=expanded', command[-1]]
    assert not any(value in command for value in ('--upload', '--preprocess', '--skip-libraries-discovery'))
    assert all(digest((receipt/name).read_bytes()) == sha for name, sha in audit['receipt_sha256'].items())
    assert audit['source_files'] == old['source_files']
    aggregate = hashlib.sha256()
    for name, sha in sorted(audit['source_files'].items()):
        local = ROOT/('src/app/app.ino' if name == 'app.ino' else name)
        data = local.read_bytes()
        assert digest(data) == sha
        aggregate.update(name.encode()+b'\0'+data)
    assert aggregate.hexdigest() == v['source_sha256'] == audit['source_sha256']
    pins = policy.installed_pins(v['resolved_directories']['data'])
    actual_pins = dict((line.split('  ', 1)[1], line.split('  ', 1)[0]) for line in
        (receipt/'precompile_pins.stdout.json').read_text().splitlines())
    assert actual_pins == pins and all(v['file_sha256'][name] == sha for name, sha in pins.items())
    for name, entry in audit['metadata'].items():
        assert len(entry['text'].encode()) == entry['bytes']
        assert digest(entry['text'].encode()) == entry['sha256']
        if name.endswith('.d'):
            assert not any(x in entry['text'] for x in ('Arduino_RouterBridge','Arduino_RPClite','MsgPack','DebugLog','ArxTypeTraits','ArxContainer'))
    commands = read_text_json(audit['metadata']['compile_commands.json']['text'])
    for c in commands:
        assert all(flag in c['arguments'] for flag in flags.split())
        if not c['file'].endswith('/tls-syms.S'):
            assert '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0' in c['arguments']
    assert audit['metadata']['sketch/app.ino.cpp']['sha256'] == old['metadata']['sketch/app.ino.cpp']['sha256']
    downloads = []
    for bundle in audit['bundles']:
        data = (folder/bundle['name']).read_bytes()
        assert len(data) == bundle['bytes'] and digest(data) == bundle['sha256'] == v['file_sha256'][bundle['path']]
        downloads.append(dict(name=bundle['name'], sha256=digest(data), bytes=len(data)))
    for record in audit['records']:
        path = folder/Path(record['path']).name
        elf = ELF(path)
        assert digest(elf.raw) == record['sha256'] and len(elf.raw) == record['bytes']
        assert elf.imports() == baseline.imports()
        assert elf.imports() == sorted(line.split()[-1] for line in record['undefined']['stdout'].splitlines())
    elf = ELF(folder/'app.ino.elf')
    startup = {}
    for name in ('main','setup','loop','initVariant','_Z10__loopHookv','_Z20start_static_threadsv','_GLOBAL__sub_I_setup'):
        startup[name] = elf.function(name)
        assert startup[name] == baseline.function(name), name
    assert startup['_Z10__loopHookv']['bytes'] == '7047' and startup['_Z10__loopHookv']['bind'] == 1
    init = [r['symbol']['name'] for r in elf.relocations if elf.sections[r['section']]['name'] == '.init_array']
    fini = [r for r in elf.relocations if elf.sections[r['section']]['name'] == '.fini_array']
    assert init == ['_GLOBAL__sub_I_setup'] and not fini
    assert any(elf.sections[r['section']]['name'] == '.exported_sym' and r['symbol']['name'] == 'main' for r in elf.relocations)
    assert elf.symbol('_ZN12_GLOBAL__N_17runtimeE')['size'] == 168888
    assert elf.symbol('_ZN12_GLOBAL__N_17sourcesE')['size'] == 848
    project = re.compile(r'^_ZNK?(?:3app|3imu|5power|6motors|8line_qtr|11opp_sensors|2ui|8recorder|3fsm|4edge|9countdown|10opp_fusion|8governor|6motion|7openers|5stall|8logframe|7qtr_cal)')
    old_functions = {s['name'] for s in baseline.symbols if s['type'] == 2 and project.match(s['name'])}
    new_functions = {s['name'] for s in elf.symbols if s['type'] == 2 and project.match(s['name'])}
    assert new_functions == old_functions and len(new_functions) == 493
    assert not any(any(t in s['name'] for t in ('Bridge','msgpack','Rpc','RPC','ZephyrSerial')) for s in elf.symbols)
    payload = sum(s['size'] for s in elf.sections if s['flags'] & 2 and s['name'] != '.llext.rodata.noreloc')
    round8 = lambda x: (x+7)//8*8
    regions = [s for s in elf.sections if s['flags'] & 2 and s['name'] != '.llext.rodata.noreloc' and s['size']]
    assert all(s['align'] <= 8 and s['offset'] % (s['align'] or 1) == 0 for s in regions)
    region_chunks = sum(8+round8(s['size']) if s['align'] == 8 else round8(s['size']+4) for s in regions)
    globals_count = sum(s['bind'] == 1 and s['type'] in (1,2) for s in elf.symbols)
    exports_bytes = next(s['size'] for s in elf.sections if s['name'] == '.exported_sym')
    conditional_peak = region_chunks + round8(196+4) + round8(len(elf.sections)*8+4) + round8(globals_count*8+4) + round8(exports_bytes+4) + 88
    compiler = read(receipt/'compile.stdout.json')['compiler_out']
    assert f'Global variables use {payload} bytes' in compiler
    for key in ('native_names','native_exports','base_sha256','math_aliases','math_symbols','math_missing','math_exports','base_static_threads'):
        assert audit[key] == old[key], key
    for key, count in (('native_exports',len(audit['native_names'])),('math_exports',len(audit['math_symbols']))):
        addresses = re.findall(r'^\$\d+ = (0x[0-9a-f]+)$', audit[key]['stdout'], re.M)
        assert len(addresses) == count and all(int(x,16) for x in addresses)
    objects = object_diff(old['objects'], audit['objects'])
    if mode != 'match-immediate':
        assert not objects['changes'] and elf.raw == baseline.raw
    else:
        expected = {
            'sketch/src/hal/motors.cpp.o': ['.text._ZN6motors9MotorGate8transactERKN4core7OutputsERN3fsm12PreviousTickE'],
            'sketch/src/hal/motor_port_unoq.cpp.o': [
                '.text._ZN6motors8UnoQPort11writeEnableEPvb',
                '.text._ZN6motors8UnoQPort8writePwmEPvNS_7ChannelEjj']}
        assert {x['path'] for x in objects['changes']} == expected.keys()
        for row in objects['changes']:
            assert row['changed'] == row['relocated'] == expected[row['path']]
            assert not row['added'] and not row['removed']
    return dict(source_files=len(audit['source_files']), source_sha256=v['source_sha256'],
        source_receipt=digest((folder/'audit.json').read_bytes()), downloaded=downloads,
        metadata=len(audit['metadata']), compile_commands=len(commands), pins=len(pins),
        controlled_commands=len([k for k in props if k.startswith(policy.COMMAND_PREFIXES)]),
        project_functions=len(new_functions),
        payload=payload, nominal_remaining=262144-payload, imports=len(elf.imports()),
        conditional_pristine_peak=conditional_peak, conditional_largest_payload=262144-conditional_peak-4,
        native_exports=len(audit['native_names']), aeabi_exports=len(audit['math_symbols']),
        startup=startup, init=init, object_comparison=objects,
        build_path=v['build_path'], receipt=str(receipt.relative_to(ROOT)))


def read_text_json(text):
    return policy.decode(text)


old = read(BASE/'target_570ef35f_candidate.json')
old['source_sha256'] = read(BASE/'570ef35f_candidate.json')['source_sha256']
baseline = ELF(BASE/'candidate_elf/app.ino.elf')
results = {}
for mode in ('bench-default','bench-immediate','match-immediate'):
    if (RAW/mode/'audit.json').exists():
        results[mode] = mode_review(mode, old, baseline)
report = dict(scope='Fresh-context same-model local independent review; no board/network/build/MCU action',
    new_decoder=True, modes=results, all_modes_present=len(results)==3,
    reviewed_files={str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in [
        ROOT/'tools/board_tool.py', ROOT/'tools/app_build_policy.py', ROOT/'tools/app_build_commands.json',
        ROOT/'tools/app_build_pins.json', ROOT/'state/analysis/P2_app_build_contract.md',
        ROOT/'state/analysis/P2_app_override_contract.md', ROOT/'tools/p0_inert_sources.json']})
previous = read(ROOT/'state/reviews/P2_app_override_review_raw/reviewer_probe_final.json')
assert all(digest((ROOT/path).read_bytes()) == sha for path,sha in previous['source_sha256'].items())
report['D100_locally_reviewed_source_identity'] = previous['source_sha256']
if 'bench-immediate' in results:
    a = (RAW/'bench-default/app.ino.elf-zsk.bin').read_bytes()
    b = (RAW/'bench-immediate/app.ino.elf-zsk.bin').read_bytes()
    assert len(a) == len(b)
    report['default_to_immediate_package_differences'] = [(i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert report['default_to_immediate_package_differences'] == [(14,0,4)]
(OUT/'review_results.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({m: dict(payload=r['payload'], imports=r['imports'], objects=r['object_comparison']) for m,r in results.items()}, indent=2))
