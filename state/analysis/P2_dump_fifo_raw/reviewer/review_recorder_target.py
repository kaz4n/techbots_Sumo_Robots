"""Offline exact D117 recorder ELF/startup/ABI and reused conditional heap audit."""
import hashlib
import importlib.util
import json
from pathlib import Path, PureWindowsPath
import re
import struct
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_dump_fifo_raw'
NAME = sys.argv[1]
assert re.fullmatch(r'target_[a-f0-9]{8}_bench-default_checked', NAME)
FOLDER = RAW / NAME
SOURCE = json.loads((FOLDER / 'audit.json').read_bytes())['source_sha256']
sys.path.insert(0, str(ROOT / 'tools'))
import app_build_policy as policy
spec = importlib.util.spec_from_file_location('existing_elf_review', ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def refs(elf, name):
    sym = next(s for s in elf.symbols if s['name'] == name)
    at = sym['value'] & ~1
    return [r for r in elf.relocations if r['section'] == sym['section'] and at <= r['offset'] < at + sym['size']]


def calls(elf, name):
    return [r['name'] for r in refs(elf, name) if r['symbol_type'] == 2]


def symbol_bytes(elf, sym):
    return elf.section_bytes(elf.sections[sym['section_index']])[sym['value']:sym['value'] + sym['size']]


audit = read(FOLDER / 'audit.json')
receipt = FOLDER / 'build_receipt'
verified = read(receipt / 'verified.json')
command = read(receipt / 'command.json')
assert command[command.index('--fqbn') + 1] == verified['fqbn'] == policy.BASE_FQBN
assert command[-1] == '/home/arduino/sumox26_codex_build/' + SOURCE + '/recorder'
flags = '-DMATCH=0 -DMOTORS_ALLOWED=0'
for language in ('c', 'cpp'):
    assert f'compiler.{language}.extra_flags={flags}' in command
assert verified['compiler_returncode'] == 0 and verified['precompile_checks'] is True
assert verified['policy'] == policy.POLICY and verified['used_libraries'] == []
assert verified['source_sha256'] == audit['source_sha256'] == SOURCE
assert '/bench-default/' in verified['build_path'] and verified['build_path'].endswith('/build')
assert verified['artifacts'] == verified['build_path'][:-5] + 'artifacts'
policy.validate_result((receipt / 'compile.stdout.json').read_text(), policy.BASE_FQBN, flags, verified['build_path'], project='recorder.ino')
policy.validate_preflight((receipt / 'properties.stdout.json').read_text(), policy.BASE_FQBN, flags,
                          verified['build_path'], verified['resolved_directories']['data'], project='recorder.ino')
pins = policy.installed_pins(verified['resolved_directories']['data'])
assert (receipt / 'precompile_pins.stdout.json').read_text().splitlines() == [h + '  ' + p for p, h in pins.items()]
assert all(verified['file_sha256'][p] == h for p, h in pins.items())
assert all(not p.read_bytes() for p in receipt.glob('*.stderr.txt'))
frozen = RAW / ('target_sources_' + SOURCE[:8])
manifest = read(frozen / 'manifest.json')
assert manifest['source_files'] == audit['source_files'] and manifest['source_sha256'] == SOURCE
assert len(audit['source_files']) == 95
digest = hashlib.sha256()
for name, expected in sorted(audit['source_files'].items(), key=lambda item: PureWindowsPath(item[0])):
    data = (frozen / name).read_bytes()
    assert sha(data) == expected, name
    digest.update(name.encode() + b'\0' + data)
assert digest.hexdigest() == SOURCE
prior_freeze = read(ROOT / 'state/analysis/P2_recorder_transport_raw/implementer/first_source_freeze.json')
bench = {name.removeprefix('bench/recorder/'): meta['sha256'] for name, meta in prior_freeze['files'].items()}
freeze_matches = []
for freeze_path in sorted((RAW / 'implementer').glob('*_source_freeze.json')):
    candidate = read(freeze_path)
    selection = {p: x['sha256'] for p, x in candidate['files'].items() if p.startswith('src/hal/')}
    selection['recorder.ino'] = candidate['files']['bench/recorder/recorder.ino']['sha256']
    if all(audit['source_files'][p] == h for p, h in selection.items()):
        freeze_matches.append((freeze_path, selection))
assert len(freeze_matches) == 1
freeze_path, selection = freeze_matches[0]
bench['recorder.ino'] = selection['recorder.ino']
assert len(bench) == 5 and all(audit['source_files'][p] == h for p, h in bench.items())
prior = read(ROOT / 'state/analysis/P2_recorder_transport_raw/target_sources_e2cd303f/manifest.json')['source_files']
shared = {p: h for p, h in audit['source_files'].items() if p not in bench}
assert len(shared) == 90
assert {p for p,h in shared.items() if prior[p] != h} == {'src/hal/dump_uart_unoq.h','src/hal/dump_uart_unoq.cpp'}

# Resolve the actual relocation-used imports through the pinned loader's export
# section, independent of the sketch's many unused imported declarations.
loader = (ROOT / 'state/analysis/P2_ui_adc_probe_raw/root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.elf').read_bytes()
loader_sha = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
assert sha(loader) == loader_sha
assert audit['file_sha256'][next(p for p in audit['file_sha256'] if p.endswith('zephyr-arduino_uno_q_stm32u585xx.elf'))] == loader_sha
header = struct.unpack_from('<16sHHIIIIIHHHHHH', loader)
sections = [struct.unpack_from('<10I', loader, header[6] + i * header[11]) for i in range(header[12])]
strings = sections[header[13]]
names = loader[strings[4]:strings[4] + strings[5]]
exports_section = next(s for s in sections if names[s[0]:].split(b'\0')[0] == b'llext_const_symbol_area')
exports = {}
for offset in range(exports_section[4], exports_section[4] + exports_section[5], 8):
    address, value = struct.unpack_from('<II', loader, offset)
    section = next(s for s in sections if s[1] != 8 and s[3] <= address < s[3] + s[5])
    start = section[4] + address - section[3]
    name = loader[start:section[4] + section[5]].split(b'\0')[0].decode()
    assert name not in exports or exports[name] == value
    exports[name] = value

runner_ctor = '_ZN18recorder_transport6RunnerC1ERKNS_9ClockPortERKN3app8DumpPortE'
runner_begin = '_ZN18recorder_transport6Runner5beginEbRKN8recorder4dump10SetupGrantE'
runner_poll = '_ZN18recorder_transport6Runner4pollEv'
terminal = '_ZNK18recorder_transport6Runner8terminalEv'
motor_port = '_ZN18recorder_transport6Runner9motorPortEPS0_'
factory = '_ZN3app12unoQDumpPortERN8recorder4dump12UnoQDumpPortE'
native_port = '_ZN8recorder4dump12UnoQDumpPort4portEv'
transaction_ctor = '_ZN3app11TransactionC1ERKN6motors4PortE'
gate_ctor = '_ZN6motors9MotorGateC1ERKNS_4PortE'
robot_ctor = '_ZN3fsm5RobotC1Ev'
inert_callbacks = [
    '_ZN18recorder_transport6Runner15configureEnableEPv',
    '_ZN18recorder_transport6Runner12configurePwmEPvN6motors7ChannelE',
    '_ZN18recorder_transport6Runner11writeEnableEPvb',
    '_ZN18recorder_transport6Runner8writePwmEPvN6motors7ChannelEjj',
    '_ZN18recorder_transport6Runner6settleEPv',
    '_ZN18recorder_transport6Runner10ownerClockEPv']
allowed_imports = {
    '__device_dts_ord_78', '__device_dts_ord_9', '__device_dts_ord_94',
    '__real___aeabi_d2f', '__real___aeabi_d2iz', '__real___aeabi_dadd',
    '__real___aeabi_dcmpeq', '__real___aeabi_dcmpge', '__real___aeabi_dcmpgt',
    '__real___aeabi_dcmple', '__real___aeabi_dcmplt', '__real___aeabi_dcmpun',
    '__real___aeabi_ddiv', '__real___aeabi_dmul', '__real___aeabi_dsub',
    '__real___aeabi_f2d', '__real___aeabi_i2d', '__real___aeabi_ui2d',
    '__real___aeabi_ul2d', '__real___aeabi_uldivmod', '__real_abort', '__real_fmod',
    '__real_memcpy', '__real_memset', '__real_sqrt', 'sys_clock_cycle_get_64',
    'z_impl_device_init', 'z_impl_device_is_ready',
    'z_impl_k_thread_create', 'z_impl_k_thread_name_set'}
constructor_refs = {
    runner_ctor: [motor_port, transaction_ctor, 'memset'],
    transaction_ctor: [gate_ctor, robot_ctor, 'memset', '_ZN3fsm11RobotResultC1Ev'],
    gate_ctor: [],
    robot_ctor: ['memset', '_ZN10opp_fusion17FusionObservationC1Ev',
                 '_ZN3fsm11RobotResultC1Ev', '_ZN6motion4TurnC1Ev',
                 '_ZN6motion8StraightC1Ev', '_ZN7openers5FlankC1Ev'],
    '_ZN10opp_fusion17FusionObservationC1Ev': [],
    '_ZN3fsm11RobotResultC1Ev': ['memset'],
    '_ZN6motion4TurnC1Ev': [], '_ZN6motion8StraightC1Ev': [],
    '_ZN7openers5FlankC1Ev': ['_ZN6motion4TurnC1Ev', '_ZN6motion8StraightC1Ev']}

def normalized(elf, name):
    body = bytearray(elf.functions()[name])
    sym = next(s for s in elf.symbols if s['name'] == name)
    for rel in refs(elf, name):
        if rel['type'] != 2:
            assert rel['type'] in (10, 47, 48)
            continue  # THM_CALL/MOVW/MOVT instruction bytes must remain exact.
        offset = rel['offset'] - (sym['value'] & ~1)
        body[offset:offset + 4] = b'\0' * 4
    return bytes(body)

records = []
final_elf = module.Elf(FOLDER / 'recorder.ino.elf')
final_functions = final_elf.functions()
for row in audit['records']:
    data = (FOLDER / row['name']).read_bytes()
    assert sha(data) == row['sha256'] == verified['file_sha256'][row['path']]
    if not row['name'].endswith('.elf'):
        continue
    elf = module.Elf(FOLDER / row['name'])
    account, functions = elf.account(), elf.functions()
    assert len(row['commands']) == 5 and all(c['returncode'] == 0 and not c['stderr'] for c in row['commands'])
    assert len(account['init']) == 1 and account['init'][0]['name'] == '_GLOBAL__sub_I_setup' and not account['fini']
    assert not any(r for r in elf.relocations if r['section'] == '.preinit_array')
    assert functions['_Z10__loopHookv'] == functions['initVariant'] == bytes.fromhex('7047')
    assert next(s for s in elf.symbols if s['name'] == 'initVariant')['bind'] == 2
    assert next(s for s in elf.symbols if s['name'] == '_Z10__loopHookv')['bind'] == 1
    thread = next(s for s in elf.sections if s['name'] == '.static_thread_data_area')
    bounds = [s for s in elf.symbols if s['name'] in ('__static_thread_data_list_start', '__static_thread_data_list_end')]
    assert thread['size'] == 0 and len(bounds) == 2
    assert all(s['section_index'] == thread['index'] and s['value'] == 0 for s in bounds)
    # Debug relocations describe types and are excluded from executable import use.
    used = sorted({r['name'] for r in elf.relocations if r['symbol_section'] == '' and not r['section'].startswith('.debug')})
    assert set(used) == allowed_imports and all(name in exports for name in used)
    defined = {s['name'] for s in elf.symbols if s['section_index'] and s['size']}
    forbidden = ('Bridge', 'Serial', 'Router', 'Runtime', 'UnoQPort', 'UnoQMatrix',
                 'native_pins', 'line_qtr', 'InputOwner', '_ZN5power', '_ZN3imu', 'Matrix')
    assert not any(any(part in name for part in forbidden) for name in defined)
    assert not any(name in used for name in ('malloc', 'calloc', 'realloc', 'free', '_Znwj', '_Znaj'))
    assert calls(elf, '__cxa_allocate_exception') == ['abort']
    assert calls(elf, 'main') == ['initVariant', '_Z20start_static_threadsv', 'setup', 'loop', '_Z10__loopHookv']
    assert calls(elf, 'setup') == [runner_begin]
    assert functions['setup'][:20] == bytes.fromhex('07b50021034b01aa03480191984703b05df804fb')
    assert calls(elf, 'loop') == [runner_poll]
    assert calls(elf, '_GLOBAL__sub_I_setup') == ['_ZN12_GLOBAL__N_17clockUsEPv', factory, runner_ctor]
    assert calls(elf, factory) == ['_ZN3app12_GLOBAL__N_15beginEPvRKN8recorder4dump10SetupGrantE',
                                  '_ZN3app12_GLOBAL__N_15readyEPv', native_port]
    assert calls(elf, native_port) == ['_ZN8recorder4dump12UnoQDumpPort5writeEPvPKcj',
                                      '_ZN8recorder4dump12UnoQDumpPort6cancelEPv']
    assert calls(elf, motor_port) == inert_callbacks
    for name in (native_port, motor_port):
        # These reviewed leaf functions store callbacks but never invoke them.
        assert bytes.fromhex('9847') not in functions[name]
    for name, expected in constructor_refs.items():
        assert calls(elf, name) == expected, name
    assert functions[terminal] == bytes.fromhex('90f82000012804d0083801288cbf002001207047')
    # Reviewed false-path: consume attempt, terminal check, DISABLED store, return.
    assert functions[runner_begin].startswith(bytes.fromhex('73b500f5203696f841310446154643b9294b984728b9012386f8413121b984f82030002002b070bd'))
    # Poll calls terminal first and branches directly to return for DISABLED.
    assert functions[runner_poll][:14] == bytes.fromhex('73b52c4b04469847064600284fd1')
    runner = next(s for s in elf.symbols if s['name'] == '_ZN12_GLOBAL__N_16runnerE')
    native = next(s for s in elf.symbols if s['name'] == '_ZN12_GLOBAL__N_111native_dumpE')
    assert (runner['size'], runner['value'], runner['section']) == (164176, 0, '.bss')
    assert (native['size'], native['value'], native['section']) == (208, 0, '.data')
    assert symbol_bytes(elf, native) == b'\x01' + bytes(207)
    bss = elf.sections[runner['section_index']]
    owner = next(s for s in elf.symbols if s['name'] == '_ZN8recorder4dump12_GLOBAL__N_110uart_ownerE')
    assert (owner['value'], owner['size'], owner['section']) == (164176, 4, '.bss')
    assert bss['size'] == owner['value'] + owner['size'] == 164180 and bss['alignment'] == 8
    metadata = account['metadata_chunks']
    regions = {r['name']: r['retained_chunk'] for r in account['copied_regions']}
    order = ['.text', '.data', '.rodata', '.bss', '.exported_sym', '.preinit_array', '.init_array', '.fini_array']
    extra = [name for name in regions if name not in order]
    assert not extra or row['name'] == 'recorder.ino_temp.elf'
    allocations = [('extension', metadata['extension']), ('section_map', metadata['section_map'])]
    allocations += [(name, regions[name]) for name in order if name in regions] + [(name, regions[name]) for name in extra]
    allocations += [('global_symbols', metadata['global_symbols']), ('export_copy', metadata['export_copy'])]
    consumed, ledger = metadata['initial_bookkeeping'], []
    for purpose, chunk in allocations:
        ledger.append(dict(purpose=purpose, chunk=chunk, available_before=262144 - consumed, fits=chunk <= 262144 - consumed))
        consumed += chunk
    assert consumed == account['conditional_pristine_peak_consumption'] and all(x['fits'] for x in ledger)
    assert set(functions) == set(final_functions)
    for name in functions:
        if row['name'] == 'recorder.ino_debug.elf':
            assert functions[name] == final_functions[name], name
        elif row['name'] == 'recorder.ino_temp.elf':
            assert normalized(elf, name) == normalized(final_elf, name), name
            assert calls(elf, name) == calls(final_elf, name), name
            nonabs = lambda image: [(r['offset'], r['type'], r['name']) for r in refs(image, name) if r['type'] != 2]
            assert nonabs(elf) == nonabs(final_elf), name
    if row['name'] == 'recorder.ino.elf':
        assert (0x08100010 + elf.section_header_offset) % 4 == 0
        for section in elf.sections:
            if section['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab'):
                assert (0x08100010 + section['offset']) % max(1, section['alignment']) == 0
        disassembly = next(c['stdout'] for c in row['commands'] if 'objdump' in c['argv'][0])
        witnesses = []
        selected = ['_GLOBAL__sub_I_setup', 'setup', runner_begin, runner_poll, terminal,
                    factory, native_port, motor_port, *constructor_refs,
                    'main', '_Z20start_static_threadsv', '__cxa_allocate_exception', *inert_callbacks]
        for name in dict.fromkeys(selected):
            at = disassembly.index(' <' + name + '>:')
            witnesses.append(disassembly[disassembly.rfind('\n', 0, at):disassembly.find('\n\n', at)])
        (OUT / (NAME + '_witness.txt')).write_text('\n'.join(witnesses))
    records.append(dict(file=row['name'], sha256=row['sha256'], bytes=len(data), payload=account['compiler_payload'],
        conditional_peak=consumed, free_span=262144 - consumed, largest_free_payload=262144 - consumed - 4,
        allocations=ledger, copied_regions=account['copied_regions'], metadata=metadata,
        used_imports={name: f'0x{exports[name]:08x}' for name in used}, sole_initializer=account['init'],
        runner=runner, native=native, bss=bss, thread_bounds=bounds,
        function_identity_count=len(functions), default_enabled=False, startup_callback_or_clock_io=False))

abi = audit['abi']
assert abi['returncode'] == 0 and not abi['stderr']
sizes = [int(x) for x in re.findall(r'^\$\d+ = (\d+)$', abi['stdout'], re.MULTILINE)]
assert sizes == [164176, 120, 8, 162544, 504, 24, 159200, 126300, 1408, 208]
assert '/*     32      |     120 */    struct recorder_transport::Report' in abi['stdout']
assert '/*    152      |  162544 */    class app::Transaction' in abi['stdout']
assert '/* 162696      |    1408 */    class recorder::dump::Transfer' in abi['stdout']
assert '/* 164161      |       1 */    bool attempted_' in abi['stdout']
final_bytes = (FOLDER / 'recorder.ino.elf').read_bytes()
zsk = (FOLDER / 'recorder.ino.elf-zsk.bin').read_bytes()
assert len(zsk) == len(final_bytes) and zsk[16:] == final_bytes[16:]
assert [i for i, (a, b) in enumerate(zip(final_bytes, zsk)) if a != b] == [7, 8, 9, 10, 12, 13]
assert zsk[7] == 1 and int.from_bytes(zsk[8:12], 'little') == len(zsk)
result = dict(verdict='PASS_EXACT_CHECKED_DEFAULT_RECORDER_TARGET_AND_CONDITIONAL_FIT', source_sha256=SOURCE,
    source_files=95, unchanged_shared_files=88, artifact_records=records,
    source_freeze_path=str(freeze_path.relative_to(ROOT)), source_freeze_sha256=sha(freeze_path.read_bytes()),
    abi=dict(zip(('Runner', 'Report', 'ClockPort', 'Transaction', 'TransactionReport', 'DumpPort',
                  'AttemptRecorder', 'FrameBuffer', 'Transfer', 'UnoQDumpPort'), sizes)),
    abi_offsets=dict(report=32, transaction=152, transfer=162696, attempted=164161),
    elf_sha256=sha(final_bytes), zsk_sha256=sha(zsk), loader_sha256=loader_sha,
    model_sha256=sha((ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py').read_bytes()),
    zsk_header_hex=zsk[:16].hex(),
    reviewer_harness_corrections='D116 model and final/debug/temp normalization reused; see target_harness_notes.md for D117 run corrections.',
    evidence='Direct byte parsing and retained16 offline ELF/ABI commands. Every function compared final/debug and ABS32-normalized temporary image. Actual default false branch and startup constructor references inspected; no target execution.',
    import_qualification='Native UART/device/clock callback code is retained but not invoked by passive default startup. Static thread bounds are empty; unused matrix/allocator/core import declarations are not runtime dependencies.',
    limits='Conditional pristine256KiB loader pool, persistent aligned peeks, unchanged loader/config, no interleaved or constructor allocation. No actual load/free-RAM/stack/WCET/receiver delivery or upload permission. Actual setup ACK, byte service rate, clean framing and delivery remain unqualified; FIFO reference-model tests are separate.')
(OUT / (NAME + '.json')).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: records[0][k] for k in ('sha256', 'bytes', 'payload', 'conditional_peak', 'free_span', 'largest_free_payload')}, indent=2))

