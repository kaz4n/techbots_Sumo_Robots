"""Independent offline D107 checked-source, ELF startup and loader audit."""
import hashlib
import importlib.util
import json
from pathlib import Path, PureWindowsPath
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_opp_view_raw'
sys.path.insert(0, str(ROOT / 'tools'))
import app_build_policy as policy
spec = importlib.util.spec_from_file_location('reviewed_elf', ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return json.loads(path.read_text())
name = sys.argv[1]
assert name.startswith('target_') and name.endswith('_checked') and '/' not in name and '\\' not in name
folder = RAW / name
audit = read(folder / 'audit.json')
receipt = folder / 'build_receipt'
verified = read(receipt / 'verified.json')
command = read(receipt / 'command.json')
immediate = '_bench-immediate_' in name
fqbn = policy.BASE_FQBN + (':wait_linux_boot=no' if immediate else '')
assert command[command.index('--fqbn') + 1] == verified['fqbn'] == fqbn
assert verified['compiler_returncode'] == 0 and verified['precompile_checks'] is True
assert verified['policy'] == policy.POLICY and verified['used_libraries'] == []
assert verified['source_sha256'] == audit['source_sha256']
for language in ('c', 'cpp'):
    assert f'compiler.{language}.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0' in command
flags = '-DMATCH=0 -DMOTORS_ALLOWED=0'
policy.validate_result((receipt / 'compile.stdout.json').read_text(), fqbn, flags, verified['build_path'], project='opp_view.ino')
policy.validate_preflight((receipt / 'properties.stdout.json').read_text(), fqbn, flags, verified['build_path'], verified['resolved_directories']['data'], project='opp_view.ino')
pins = policy.installed_pins(verified['resolved_directories']['data'])
precompile = (receipt / 'precompile_pins.stdout.json').read_text().splitlines()
assert precompile == [digest + '  ' + path for path, digest in pins.items()]
assert all(verified['file_sha256'][path] == digest for path, digest in pins.items())
assert all(not p.read_bytes() for p in receipt.glob('*.stderr.txt'))
assert audit['file_sha256'][next(p for p in audit['file_sha256'] if p.endswith('zephyr-arduino_uno_q_stm32u585xx.elf'))] == '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
frozen = RAW / ('target_sources_' + audit['source_sha256'][:8])
manifest = read(frozen / 'manifest.json')
assert manifest['source_files'] == audit['source_files'] and len(audit['source_files']) == 96
digest = hashlib.sha256()
# The actual coordinator is Windows. Existing board.source_hash sorts Path
# objects, so reproduce its component/case ordering explicitly on either host.
for path, expected in sorted(audit['source_files'].items(), key=lambda item: PureWindowsPath(item[0])):
    data = (frozen / path).read_bytes(); assert sha(data) == expected, path
    digest.update(path.encode()); digest.update(b'\0'); digest.update(data)
assert digest.hexdigest() == audit['source_sha256'] == manifest['source_sha256']
prior = read(RAW / 'target_sources_367814a0/manifest.json')['source_files']
delta = {p: dict(before=prior.get(p), after=h) for p, h in audit['source_files'].items() if prior.get(p) != h}
assert set(delta) == {'README.md', 'src/hal/ui_display.cpp'}
assert delta['src/hal/ui_display.cpp']['after'] == '9e9d5d9a44d8b0d637f2301d042f7021df890a270995e1806d4d4456dd58c535'
assert set(prior).issubset(audit['source_files'])
assert audit['source_files']['src/opp_view.cpp'] == '1be9bc511d0b1af5d1a95f664f20e93e0779c0cd617596cd272fe615ea1c55e3'

def refs(elf, name):
    sym = next(s for s in elf.symbols if s['name'] == name)
    at = sym['value'] & ~1
    return [r for r in elf.relocations if r['section'] == sym['section'] and at <= r['offset'] < at + sym['size']]
bindings = {
    '_ZN8opp_view6Native14beginOpponentsEPv': '_ZN11opp_sensors7Sensors5beginEv',
    '_ZN8opp_view6Native13readOpponentsEPv': '_ZNK11opp_sensors7Sensors4readEv',
    '_ZN8opp_view6Native11beginMatrixEPvN2ui11MatrixGrantE': '_ZN2ui10UnoQMatrix5beginENS_11MatrixGrantE',
    '_ZN8opp_view6Native12submitMatrixEPvjRKN2ui5FrameE': '_ZN2ui10UnoQMatrix6submitEjRKNS_5FrameE',
    '_ZN8opp_view6Native7clockUsEPv': 'micros',
}
used_allowed = {'__real___aeabi_uldivmod', '__real_abort', '__real_memset', 'matrixBegin',
                'matrixGrayscaleWrite', 'matrixSetGrayscaleBits', 'sys_clock_cycle_get_64',
                'z_impl_device_is_ready', 'z_impl_k_thread_create', 'z_impl_k_thread_name_set'}
records = []
for row in audit['records']:
    data = (folder / row['name']).read_bytes()
    assert sha(data) == row['sha256'] == verified['file_sha256'][row['path']]
    if not row['name'].endswith('.elf'): continue
    elf = module.Elf(folder / row['name']); account = elf.account()
    assert all(c['returncode'] == 0 and not c['stderr'] for c in row['commands'])
    assert len(account['init']) == 1 and account['init'][0]['name'] == '_GLOBAL__sub_I_setup'
    assert not account['fini']
    assert elf.functions()['_Z10__loopHookv'] == bytes.fromhex('7047')
    assert elf.functions()['initVariant'] == bytes.fromhex('7047')
    thread = next(s for s in elf.sections if s['name'] == '.static_thread_data_area')
    bounds = [s for s in elf.symbols if s['name'] in ('__static_thread_data_list_start', '__static_thread_data_list_end')]
    assert thread['size'] == 0 and len(bounds) == 2
    assert bounds[0]['section_index'] == bounds[1]['section_index'] == thread['index']
    assert bounds[0]['value'] == bounds[1]['value'] == 0
    used = sorted({r['name'] for r in elf.relocations if r['symbol_section'] == ''})
    assert {n for n in used if not n.startswith('__device_dts_ord_')} == used_allowed
    names = {s['name'] for s in elf.symbols if s['section_index'] and s['size']}
    assert not any(any(p in n for p in ('Bridge', 'Serial', 'Router', 'Robot', 'MotorGate', 'runtime', 'ui_display', 'recorder')) for n in names)
    assert [r['name'] for r in refs(elf, '__cxa_allocate_exception')] == ['abort']
    init_refs = [r['name'] for r in refs(elf, '_GLOBAL__sub_I_setup') if r['symbol_type'] == 2]
    assert init_refs == ['_ZN8opp_view6Native4portEv', '_ZN8opp_view6RunnerC1ERKNS_4PortE']
    assert [r['name'] for r in refs(elf, '_ZN8opp_view6RunnerC1ERKNS_4PortE')] == ['memset']
    assert [r['name'] for r in refs(elf, '_ZN8opp_view6Native4portEv')] == [
        '_ZN8opp_view6Native7clockUsEPv', '_ZN8opp_view6Native14beginOpponentsEPv',
        '_ZN8opp_view6Native13readOpponentsEPv', '_ZN8opp_view6Native11beginMatrixEPvN2ui11MatrixGrantE',
        '_ZN8opp_view6Native12submitMatrixEPvjRKN2ui5FrameE']
    for caller, callee in bindings.items(): assert [r['name'] for r in refs(elf, caller)] == [callee]
    assert [r['name'] for r in refs(elf, 'micros')] == ['sys_clock_cycle_get_64', '__aeabi_uldivmod']
    metadata = account['metadata_chunks']; regions = {r['name']: r['retained_chunk'] for r in account['copied_regions']}
    order = ['.text', '.data', '.rodata', '.bss', '.exported_sym', '.preinit_array', '.init_array', '.fini_array']
    extra = [n for n in regions if n not in order]
    assert not extra or row['name'] == 'opp_view.ino_temp.elf'
    allocations = [('extension', metadata['extension']), ('section_map', metadata['section_map'])]
    allocations += [(n, regions[n]) for n in order if n in regions] + [(n, regions[n]) for n in extra]
    allocations += [('global_symbols', metadata['global_symbols']), ('export_copy', metadata['export_copy'])]
    used_heap = metadata['initial_bookkeeping']; ledger = []
    for purpose, chunk in allocations:
        assert chunk <= 262144 - used_heap
        ledger.append(dict(purpose=purpose, chunk=chunk, available_before=262144-used_heap)); used_heap += chunk
    assert used_heap == account['conditional_pristine_peak_consumption']
    if row['name'] == 'opp_view.ino.elf':
        assert (0x08100010 + elf.section_header_offset) % 4 == 0
        for section in elf.sections:
            if section['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab'):
                assert (0x08100010 + section['offset']) % max(1, section['alignment']) == 0
        dis = next(c['stdout'] for c in row['commands'] if 'objdump' in c['argv'][0])
        witnesses = []
        for symbol in ['_GLOBAL__sub_I_setup', 'setup', '_ZN8opp_view6Runner5beginERKNS_6GrantsE',
                       '_ZN8opp_view6Runner4pollEv', '_ZN8opp_view6Native4portEv',
                       '_ZN8opp_view6RunnerC1ERKNS_4PortE', 'main', '_Z20start_static_threadsv',
                       '__cxa_allocate_exception', *bindings]:
            p = dis.index(' <' + symbol + '>:'); start = dis.rfind('\n', 0, p); end = dis.find('\n\n', p)
            witnesses.append(dis[start:end])
        (OUT / (name + '_witness.txt')).write_text('\n'.join(witnesses))
    records.append(dict(file=row['name'], sha256=row['sha256'], bytes=len(data),
        payload=account['compiler_payload'], conditional_peak=used_heap, free_span=262144-used_heap,
        largest_free_payload=262144-used_heap-4, allocations=ledger, used_imports=used,
        init_refs=init_refs, thread_bounds=bounds, native_bindings=bindings,
        bss=[s for s in elf.symbols if s['section'] == '.bss' and s['size']]))
assert audit['abi']['returncode'] == 0 and not audit['abi']['stderr']
assert audit['abi']['stdout'].startswith('$1 = 332\n$2 = 12\n')
output = dict(verdict='PASS_EXACT_CHECKED_TARGET_STARTUP_AND_CONDITIONAL_FIT',
    source_sha256=audit['source_sha256'], source_files=len(audit['source_files']), source_delta_from_367814a0=delta,
    source_order='Explicit PureWindowsPath order, matching the Windows producer board.source_hash; all individual bytes rehashed',
    profile=dict(match=0, motors_allowed=0, startup='immediate' if immediate else 'default'),
    artifacts=records, zsk_sha256=next(r['sha256'] for r in audit['records'] if r['name'].endswith('.bin')),
    abi=dict(Runner=332, Native=12),
    caveats='Core thread starter retains thread imports but has equal empty bounds. Exception allocator stub calls abort. Only local bytes/model; no load, MCU execution, native grant or physical acceptance.')
(OUT / (name + '.json')).write_text(json.dumps(output, indent=2) + '\n')
final = next(r for r in records if r['file'] == 'opp_view.ino.elf')
print(json.dumps(dict(verdict=output['verdict'], source_sha256=output['source_sha256'], **final), indent=2))
