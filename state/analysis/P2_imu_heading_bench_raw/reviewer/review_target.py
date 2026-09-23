"""Read-only audit of D111 frozen checked artifacts and conditional loader allocations."""
import hashlib
import importlib.util
import json
from pathlib import Path, PureWindowsPath
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RAW = OUT.parent
sys.path.insert(0, str(ROOT / 'tools'))
import app_build_policy as policy
spec = importlib.util.spec_from_file_location('elf_review', ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return json.loads(path.read_text())
source = '9520e47316b6edb7405bd5182f498453c4860f79fdd197a03ff34c14c7b69c05'
mode = sys.argv[1]
assert mode in ('bench-default', 'bench-immediate')
folder = RAW / ('target_' + source[:8] + '_' + mode + '_checked')
audit = read(folder / 'audit.json'); receipt = folder / 'build_receipt'
verified = read(receipt / 'verified.json'); command = read(receipt / 'command.json')
fqbn = policy.BASE_FQBN + (':wait_linux_boot=no' if mode == 'bench-immediate' else '')
flags = '-DMATCH=0 -DMOTORS_ALLOWED=0'
assert command[command.index('--fqbn')+1] == verified['fqbn'] == fqbn
for language in ('c', 'cpp'): assert f'compiler.{language}.extra_flags={flags}' in command
assert verified['compiler_returncode'] == 0 and verified['precompile_checks'] is True
assert verified['policy'] == policy.POLICY and verified['used_libraries'] == []
assert verified['source_sha256'] == audit['source_sha256'] == source
policy.validate_result((receipt / 'compile.stdout.json').read_text(), fqbn, flags, verified['build_path'], project='imu_heading.ino')
policy.validate_preflight((receipt / 'properties.stdout.json').read_text(), fqbn, flags, verified['build_path'], verified['resolved_directories']['data'], project='imu_heading.ino')
pins = policy.installed_pins(verified['resolved_directories']['data'])
assert (receipt / 'precompile_pins.stdout.json').read_text().splitlines() == [h + '  ' + p for p, h in pins.items()]
assert all(verified['file_sha256'][p] == h for p, h in pins.items())
assert all(not p.read_bytes() for p in receipt.glob('*.stderr.txt'))
assert audit['file_sha256'][next(p for p in audit['file_sha256'] if p.endswith('zephyr-arduino_uno_q_stm32u585xx.elf'))] == '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
frozen = RAW / ('target_sources_' + source[:8])
assert read(frozen / 'manifest.json')['source_files'] == audit['source_files']
assert len(audit['source_files']) == 96
digest = hashlib.sha256()
for path, expected in sorted(audit['source_files'].items(), key=lambda item: PureWindowsPath(item[0])):
    data = (frozen / path).read_bytes(); assert sha(data) == expected, path
    digest.update(path.encode()); digest.update(b'\0'); digest.update(data)
assert digest.hexdigest() == source
prior_dir = ROOT / 'state/analysis/P2_vbat_raw/target_sources_8e3efb92'
prior = read(prior_dir / 'manifest.json')['source_files']
shared = {p: h for p, h in audit['source_files'].items() if p.startswith('src/') and p in prior}
assert len(shared) == 90 and [p for p in shared if shared[p] != prior[p]] == ['src/config.h']
addition = (b'// D111 finite bench evidence bounds, not physical timing; counts are naming exceptions.\n'
    b'inline constexpr std::uint32_t IMU_BENCH_TRIAL_US = 60000000U;\n'
    b'inline constexpr std::uint32_t IMU_BENCH_CHECKPOINT_US = 1000000U;\n'
    b'inline constexpr std::uint32_t IMU_BENCH_CHECKPOINTS = 61U;\n'
    b'inline constexpr std::uint32_t IMU_BENCH_DEADLINE_US = 70000000U;\n'
    b'inline constexpr std::uint32_t IMU_BENCH_MAX_POLLS = 100000000U;\n')
assert (frozen / 'src/config.h').read_bytes().replace(addition, b'') == (prior_dir / 'src/config.h').read_bytes()
freeze = read(RAW / 'worker/first_source_freeze.json')
assert sha((ROOT / 'state/analysis/P2_imu_heading_bench_contract.md').read_bytes()) == freeze['contract_sha256']
for row in freeze['files']:
    staged = row['path'].removeprefix('bench/imu_heading/')
    assert audit['source_files'][staged] == row['sha256']
    assert sha((ROOT / row['path']).read_bytes()) == row['sha256']

def refs(elf, name):
    sym = next(s for s in elf.symbols if s['name'] == name); at = sym['value'] & ~1
    return [r for r in elf.relocations if r['section'] == sym['section'] and at <= r['offset'] < at + sym['size']]
prefix = '_ZN17imu_heading_bench'
binding = {prefix+'6Native7clockUsEPv': ['micros'],
    prefix+'6Native10startSetupEPvjb': ['_ZN3imu8Acquirer5startEjb'],
    prefix+'6Native12advanceSetupEPvj': ['_ZN3imu8Acquirer12advanceSetupEj'],
    prefix+'6Native9beginReadEPvj': ['_ZN3imu8Acquirer9beginReadEj'],
    prefix+'6Native11advanceReadEPvj': ['_ZN3imu8Acquirer11advanceReadEj'],
    prefix+'6Native10cancelReadEPvj': ['_ZN3imu8Acquirer10cancelReadEj']}
allowed_used = {'__real___aeabi_' + op for op in ('d2f','dadd','dcmpgt','dcmple','dcmplt','dcmpun','ddiv','dmul','dsub','f2d','ui2d','uldivmod')}
allowed_used |= {'__real_abort','__real_memcpy','__real_memset','sys_clock_cycle_get_64',
    'z_impl_device_is_ready','z_impl_k_thread_create','z_impl_k_thread_name_set',
    '__device_dts_ord_40','__device_dts_ord_9','__device_dts_ord_92'}
records = []
for row in audit['records']:
    data = (folder / row['name']).read_bytes()
    assert sha(data) == row['sha256'] == verified['file_sha256'][row['path']]
    if not row['name'].endswith('.elf'): continue
    elf = module.Elf(folder / row['name']); account = elf.account(); functions = elf.functions()
    assert all(c['returncode'] == 0 and not c['stderr'] for c in row['commands'])
    assert len(account['init']) == 1 and account['init'][0]['name'] == '_GLOBAL__sub_I_setup' and not account['fini']
    assert functions['_Z10__loopHookv'] == functions['initVariant'] == bytes.fromhex('7047')
    thread = next(s for s in elf.sections if s['name'] == '.static_thread_data_area')
    bounds = [s for s in elf.symbols if s['name'] in ('__static_thread_data_list_start', '__static_thread_data_list_end')]
    assert thread['size'] == 0 and len(bounds) == 2
    assert bounds[0]['section_index'] == bounds[1]['section_index'] == thread['index'] and bounds[0]['value'] == bounds[1]['value'] == 0
    used = sorted({r['name'] for r in elf.relocations if r['symbol_section'] == ''})
    assert set(used) == allowed_used
    names = {s['name'] for s in elf.symbols if s['section_index'] and s['size']}
    assert not any(any(p in n for p in ('Bridge','Serial','Router','Robot','MotorGate','runtime','recorder','opp_sensors','UnoQMatrix','qtr_cal','line_qtr','InputOwner','Wire','TwoWire','Adafruit','native_pins','arduino_pins','Reader')) for n in names)
    assert [r['name'] for r in refs(elf, '__cxa_allocate_exception')] == ['abort']
    init_refs = [r['name'] for r in refs(elf, '_GLOBAL__sub_I_setup') if r['symbol_type'] == 2]
    assert init_refs == ['memset', prefix+'6Native4portEv', prefix+'6RunnerC1ERKNS_4PortE']
    assert [r['name'] for r in refs(elf, prefix+'6RunnerC1ERKNS_4PortE')] == ['memset']
    assert [r['name'] for r in refs(elf, prefix+'6Native4portEv')] == list(binding)
    for caller, expected in binding.items(): assert [r['name'] for r in refs(elf, caller)] == expected
    assert [r['name'] for r in refs(elf, 'setup') if r['symbol_type'] == 2] == [prefix+'6Runner5beginERKNS_6GrantsE']
    # Disassembly witness zeros all 12 bytes of Grants before the only begin call.
    assert functions['setup'][:12] == bytes.fromhex('1fb5002301a9cde901330393')
    native = next(s for s in elf.symbols if s['name'] == '_ZN12_GLOBAL__N_16nativeE')
    runner = next(s for s in elf.symbols if s['name'] == '_ZN12_GLOBAL__N_16runnerE')
    assert native['size'] == 516 and native['section'] == '.bss' and runner['size'] == 10784
    metadata = account['metadata_chunks']; regions = {r['name']: r['retained_chunk'] for r in account['copied_regions']}
    order = ['.text','.data','.rodata','.bss','.exported_sym','.preinit_array','.init_array','.fini_array']
    extra = [n for n in regions if n not in order]
    assert not extra or row['name'] == 'imu_heading.ino_temp.elf'
    allocations = [('extension',metadata['extension']), ('section_map',metadata['section_map'])]
    allocations += [(n,regions[n]) for n in order if n in regions] + [(n,regions[n]) for n in extra]
    allocations += [('global_symbols',metadata['global_symbols']),('export_copy',metadata['export_copy'])]
    used_heap = metadata['initial_bookkeeping']; ledger = []
    for purpose, chunk in allocations:
        ledger.append(dict(purpose=purpose,chunk=chunk,available_before=262144-used_heap,fits=chunk<=262144-used_heap)); used_heap += chunk
    assert used_heap == account['conditional_pristine_peak_consumption'] and all(r['fits'] for r in ledger)
    if row['name'] == 'imu_heading.ino.elf':
        assert (0x08100010 + elf.section_header_offset) % 4 == 0
        for section in elf.sections:
            if section['name'] in ('.llext.rodata.noreloc','.symtab','.strtab'):
                assert (0x08100010 + section['offset']) % max(1,section['alignment']) == 0
        dis = next(c['stdout'] for c in row['commands'] if 'objdump' in c['argv'][0]); witnesses = []
        for symbol in ['_GLOBAL__sub_I_setup','setup',prefix+'6Runner5beginERKNS_6GrantsE',prefix+'6Runner4pollEv',prefix+'6Native4portEv',prefix+'6RunnerC1ERKNS_4PortE','main','_Z20start_static_threadsv','__cxa_allocate_exception',*binding]:
            p = dis.index(' <'+symbol+'>:'); start=dis.rfind('\n',0,p); end=dis.find('\n\n',p)
            witnesses.append(dis[start:end])
        (OUT / ('target_'+source[:8]+'_'+mode+'_witness.txt')).write_text('\n'.join(witnesses))
    records.append(dict(file=row['name'],sha256=row['sha256'],bytes=len(data),payload=account['compiler_payload'],
        conditional_peak=used_heap,free_span=262144-used_heap,largest_free_payload=262144-used_heap-4,
        allocations=ledger,init_refs=init_refs,used_imports=used,native_bindings=binding,sole_native=native,
        runner=runner,thread_bounds=bounds,compiled_constants=dict(all_grants=False,mounting_confirmed=False,initial_bias=0)))
assert audit['abi']['returncode'] == 0 and not audit['abi']['stderr']
assert audit['abi']['stdout'].startswith('$1 = 10784\n$2 = 516\n')
assert '752      |   10004' in audit['abi']['stdout'] and 'checkpoints_[61]' in audit['abi']['stdout']
result = dict(verdict='PASS_EXACT_CHECKED_IMU_HEADING_TARGET_AND_CONDITIONAL_FIT',source_sha256=source,source_files=96,
    shared_source_delta_from_D110=['src/config.h: exact five additive D111 constants and their comment only'],
    mode=mode,artifacts=records,abi=dict(Runner=10784,Native=516,Sample=104,Estimate=48,Checkpoint=164,checkpoint_offset=752,checkpoint_count=61,checkpoint_bytes=10004),
    zsk_sha256=next(r['sha256'] for r in audit['records'] if r['name'].endswith('.bin')),
    limits='Sole existing native Acquirer/Bus/Setup is constructed passively; all default grants false before any callback. Core thread starter bounds empty; exception allocation stub aborts. Pristine-pool model only; no upload/load/readout/physical/WCET evidence.')
(OUT / ('target_'+source[:8]+'_'+mode+'.json')).write_text(json.dumps(result,indent=2)+'\n')
final=next(r for r in records if r['file']=='imu_heading.ino.elf')
print(json.dumps({k:final[k] for k in ('sha256','bytes','payload','conditional_peak','free_span','largest_free_payload')},indent=2))
