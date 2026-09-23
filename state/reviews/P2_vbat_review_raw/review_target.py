"""Audit D110 exact checked source, battery-only startup and conditional loader fit."""
import hashlib
import importlib.util
import json
from pathlib import Path, PureWindowsPath
import struct
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_vbat_raw'
sys.path.insert(0, str(ROOT / 'tools'))
import app_build_policy as policy
spec = importlib.util.spec_from_file_location('reviewed_elf', ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return json.loads(path.read_text())
mode = sys.argv[1]
assert mode in ('bench-default', 'bench-immediate')
folder = RAW / ('target_8e3efb92_' + mode + '_checked')
audit = read(folder / 'audit.json'); receipt = folder / 'build_receipt'
verified = read(receipt / 'verified.json'); command = read(receipt / 'command.json')
fqbn = policy.BASE_FQBN + (':wait_linux_boot=no' if mode == 'bench-immediate' else '')
flags = '-DMATCH=0 -DMOTORS_ALLOWED=0'
assert command[command.index('--fqbn')+1] == verified['fqbn'] == fqbn
for language in ('c', 'cpp'): assert f'compiler.{language}.extra_flags={flags}' in command
assert verified['compiler_returncode'] == 0 and verified['precompile_checks'] is True
assert verified['policy'] == policy.POLICY and verified['used_libraries'] == []
assert verified['source_sha256'] == audit['source_sha256'] == '8e3efb92cc6fb2ea66fdb79c96184279fbee7040ad40d9356be9365b0757c1c8'
policy.validate_result((receipt / 'compile.stdout.json').read_text(), fqbn, flags, verified['build_path'], project='vbat.ino')
policy.validate_preflight((receipt / 'properties.stdout.json').read_text(), fqbn, flags, verified['build_path'], verified['resolved_directories']['data'], project='vbat.ino')
pins = policy.installed_pins(verified['resolved_directories']['data'])
assert (receipt / 'precompile_pins.stdout.json').read_text().splitlines() == [h + '  ' + p for p, h in pins.items()]
assert all(verified['file_sha256'][p] == h for p, h in pins.items())
assert all(not p.read_bytes() for p in receipt.glob('*.stderr.txt'))
assert audit['file_sha256'][next(p for p in audit['file_sha256'] if p.endswith('zephyr-arduino_uno_q_stm32u585xx.elf'))] == '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
frozen = RAW / 'target_sources_8e3efb92'
assert read(frozen / 'manifest.json')['source_files'] == audit['source_files']
assert len(audit['source_files']) == 96
digest = hashlib.sha256()
for path, expected in sorted(audit['source_files'].items(), key=lambda item: PureWindowsPath(item[0])):
    data = (frozen / path).read_bytes(); assert sha(data) == expected, path
    digest.update(path.encode()); digest.update(b'\0'); digest.update(data)
assert digest.hexdigest() == audit['source_sha256']
prior_dir = ROOT / 'state/analysis/P2_qtr_raw_raw/target_sources_5c468e20'
prior = read(prior_dir / 'manifest.json')['source_files']
shared = {p: h for p, h in audit['source_files'].items() if p.startswith('src/') and (ROOT / p).is_file()}
assert len(shared) == 90 and [p for p in shared if shared[p] != prior[p]] == ['src/config.h']
addition = b'inline constexpr std::uint32_t VBAT_BENCH_SAMPLES = 128U; // D110 finite capture; count exception\n'
assert (frozen / 'src/config.h').read_bytes().replace(addition, b'') == (prior_dir / 'src/config.h').read_bytes()
for row in read(RAW / 'worker/second_source_freeze.json')['files']:
    staged = row['path'].removeprefix('bench/vbat/')
    assert audit['source_files'][staged] == row['sha256']

def refs(elf, name):
    sym = next(s for s in elf.symbols if s['name'] == name); at = sym['value'] & ~1
    return [r for r in elf.relocations if r['section'] == sym['section'] and at <= r['offset'] < at + sym['size']]
def symbol_bytes(elf, sym):
    return elf.section_bytes(elf.sections[sym['section_index']])[sym['value']:sym['value']+sym['size']]
binding = {'_ZN4vbat6Native7clockUsEPv': ['micros'],
    '_ZN4vbat6Native12beginBatteryEPv': ['_ZN5power6Reader5beginEv'],
    '_ZN4vbat6Native11readBatteryEPv': ['_ZN5power6Reader4readEv']}
allowed_used = {'__real___aeabi_uldivmod', '__real_abort', '__real_memset',
    'sys_clock_cycle_get_64', 'z_impl_device_is_ready', 'z_impl_k_thread_create', 'z_impl_k_thread_name_set'}
previous_table = next(r for r in read(ROOT / 'state/reviews/P2_pin_table_review_raw/target_d72bff70_bench-default.json')['artifacts'] if r['file'] == 'app.ino.elf')['table']
records = []
for row in audit['records']:
    data = (folder / row['name']).read_bytes()
    assert sha(data) == row['sha256'] == verified['file_sha256'][row['path']]
    if not row['name'].endswith('.elf'): continue
    elf = module.Elf(folder / row['name']); account = elf.account()
    assert all(c['returncode'] == 0 and not c['stderr'] for c in row['commands'])
    assert len(account['init']) == 1 and account['init'][0]['name'] == '_GLOBAL__sub_I_setup' and not account['fini']
    assert elf.functions()['_Z10__loopHookv'] == elf.functions()['initVariant'] == bytes.fromhex('7047')
    thread = next(s for s in elf.sections if s['name'] == '.static_thread_data_area')
    bounds = [s for s in elf.symbols if s['name'] in ('__static_thread_data_list_start', '__static_thread_data_list_end')]
    assert thread['size'] == 0 and len(bounds) == 2
    assert bounds[0]['section_index'] == bounds[1]['section_index'] == thread['index'] and bounds[0]['value'] == bounds[1]['value'] == 0
    used = sorted({r['name'] for r in elf.relocations if r['symbol_section'] == ''})
    assert {n for n in used if not n.startswith('__device_dts_ord_')} == allowed_used
    names = {s['name'] for s in elf.symbols if s['section_index'] and s['size']}
    assert not any(any(p in n for p in ('Bridge', 'Serial', 'Router', 'Robot', 'MotorGate', 'runtime', 'recorder', 'opp_sensors', 'UnoQMatrix', 'qtr_cal', 'line_qtr', 'InputOwner', 'beginWithButtons', 'readButtons')) for n in names)
    assert [r['name'] for r in refs(elf, '__cxa_allocate_exception')] == ['abort']
    init_refs = [r['name'] for r in refs(elf, '_GLOBAL__sub_I_setup') if r['symbol_type'] == 2]
    assert init_refs == ['_ZN4vbat6Native4portEv', '_ZN4vbat6RunnerC1ERKNS_4PortE']
    assert [r['name'] for r in refs(elf, '_ZN4vbat6RunnerC1ERKNS_4PortE')] == ['memset']
    assert [r['name'] for r in refs(elf, '_ZN4vbat6Native4portEv')] == list(binding)
    for caller, expected in binding.items(): assert [r['name'] for r in refs(elf, caller)] == expected
    assert [r['name'] for r in refs(elf, '_ZN5power6Reader5beginEv')] == ['_ZN5power6Reader12beginProfileEb']
    assert [r['name'] for r in refs(elf, '_ZN5power6Reader4readEv')] == ['_ZN5power6Reader7acquireEjb']
    # Witness disassembly: begin sets r1=false; read sets r3=true and r2=rank9.
    assert elf.functions()['_ZN5power6Reader5beginEv'].startswith(bytes.fromhex('0021'))
    assert bytes.fromhex('01230922') in elf.functions()['_ZN5power6Reader4readEv']
    assert elf.functions()['setup'].startswith(bytes.fromhex('0023'))
    table = next(s for s in elf.symbols if s['name'] == '_ZN6zephyr7arduinoL12arduino_pinsE')
    assert table['size'] == 560 and sha(symbol_bytes(elf, table)) == previous_table['bytes_sha256']
    assert not elf.sections[table['section_index']]['flags'] & 1
    rels = [dict(offset=r['offset']-table['value'], type=r['type'], name=r['name'], symbol_section=r['symbol_section'], symbol_value=r['symbol_value']) for r in elf.relocations if r['section'] == table['section'] and table['value'] <= r['offset'] < table['value'] + table['size']]
    assert rels == previous_table['relocations']
    count = next(s for s in elf.symbols if s['name'] == '_ZN11native_pins5COUNTE')
    ptr = next(s for s in elf.symbols if s['name'] == '_ZN11native_pins5TABLEE')
    assert struct.unpack('<I', symbol_bytes(elf, count))[0] == 70
    links = [r for r in elf.relocations if r['section'] == ptr['section'] and r['offset'] == ptr['value']]
    assert len(links) == 1 and links[0]['symbol_section'] == table['section']
    assert links[0]['symbol_value'] + struct.unpack('<I', symbol_bytes(elf, ptr))[0] == table['value']
    native = next(s for s in elf.symbols if s['name'] == '_ZN12_GLOBAL__N_16nativeE')
    runner = next(s for s in elf.symbols if s['name'] == '_ZN12_GLOBAL__N_16runnerE')
    assert native['size'] == 32 and native['section'] == '.data' and runner['size'] == 6280
    metadata = account['metadata_chunks']; regions = {r['name']: r['retained_chunk'] for r in account['copied_regions']}
    order = ['.text', '.data', '.rodata', '.bss', '.exported_sym', '.preinit_array', '.init_array', '.fini_array']
    extra = [n for n in regions if n not in order]
    assert not extra or row['name'] == 'vbat.ino_temp.elf'
    allocations = [('extension', metadata['extension']), ('section_map', metadata['section_map'])]
    allocations += [(n, regions[n]) for n in order if n in regions] + [(n, regions[n]) for n in extra]
    allocations += [('global_symbols', metadata['global_symbols']), ('export_copy', metadata['export_copy'])]
    used_heap = metadata['initial_bookkeeping']; ledger = []
    for purpose, chunk in allocations:
        ledger.append(dict(purpose=purpose, chunk=chunk, available_before=262144-used_heap, fits=chunk <= 262144-used_heap)); used_heap += chunk
    assert used_heap == account['conditional_pristine_peak_consumption'] and all(r['fits'] for r in ledger)
    if row['name'] == 'vbat.ino.elf':
        assert (0x08100010 + elf.section_header_offset) % 4 == 0
        for section in elf.sections:
            if section['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab'):
                assert (0x08100010 + section['offset']) % max(1, section['alignment']) == 0
        dis = next(c['stdout'] for c in row['commands'] if 'objdump' in c['argv'][0]); witnesses = []
        for symbol in ['_GLOBAL__sub_I_setup', 'setup', '_ZN4vbat6Runner5beginERKNS_6GrantsE', '_ZN4vbat6Runner4pollEv',
                       '_ZN4vbat6Native4portEv', '_ZN4vbat6RunnerC1ERKNS_4PortE', 'main', '_Z20start_static_threadsv',
                       '__cxa_allocate_exception', '_ZN5power6Reader5beginEv', '_ZN5power6Reader4readEv', *binding]:
            p = dis.index(' <' + symbol + '>:'); start = dis.rfind('\n', 0, p); end = dis.find('\n\n', p)
            witnesses.append(dis[start:end])
        (OUT / ('target_8e3efb92_' + mode + '_witness.txt')).write_text('\n'.join(witnesses))
    records.append(dict(file=row['name'], sha256=row['sha256'], bytes=len(data), payload=account['compiler_payload'],
        conditional_peak=used_heap, free_span=262144-used_heap, largest_free_payload=262144-used_heap-4,
        allocations=ledger, init_refs=init_refs, used_imports=used, native_bindings=binding,
        sole_native=native, runner=runner, pin_table_bytes_sha256=sha(symbol_bytes(elf, table)), thread_bounds=bounds,
        compiled_constants=dict(begin_buttons=False, read_rank=9, read_voltage=True, sketch_grant=False)))
assert audit['abi']['returncode'] == 0 and not audit['abi']['stderr']
assert audit['abi']['stdout'].startswith('$1 = 6280\n$2 = 32\n')
assert '120      |    6144' in audit['abi']['stdout'] and 'captures_[128]' in audit['abi']['stdout']
result = dict(verdict='PASS_EXACT_CHECKED_VBAT_TARGET_AND_CONDITIONAL_FIT', source_sha256=audit['source_sha256'],
    source_files=96, shared_source_delta_from_D109=['src/config.h: exact additive VBAT_BENCH_SAMPLES=128 only'],
    mode=mode, artifacts=records, abi=dict(Runner=6280, Native=32, Sample=20, Capture=48, capture_offset=120, capture_count=128, capture_bytes=6144),
    zsk_sha256=next(r['sha256'] for r in audit['records'] if r['name'].endswith('.bin')),
    limits='Core thread starter has empty bounds; exception allocation stub aborts. Device descriptors and retained ADC code are not execution. Pristine-pool model only, no target upload/readout/physical/WCET evidence.')
(OUT / ('target_8e3efb92_' + mode + '.json')).write_text(json.dumps(result, indent=2) + '\n')
final = next(r for r in records if r['file'] == 'vbat.ino.elf')
print(json.dumps({k: final[k] for k in ('sha256', 'bytes', 'payload', 'conditional_peak', 'free_span', 'largest_free_payload')}, indent=2))
