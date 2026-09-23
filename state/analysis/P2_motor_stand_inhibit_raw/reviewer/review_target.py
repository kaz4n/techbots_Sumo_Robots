"""Offline exact D115 default ELF/startup/ABI and reused conditional heap audit."""
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
RAW = ROOT / 'state/analysis/P2_motor_stand_inhibit_raw'
SOURCE = 'bb3b462aef66f5a0a70ed24849b47e408ef93470d975071d64ad78d4a97260fe'
FOLDER = RAW / 'target_bb3b462a_bench-default_checked'
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
assert command[-1] == '/home/arduino/sumox26_codex_build/' + SOURCE + '/motor_stand'
flags = '-DMATCH=0 -DMOTORS_ALLOWED=0'
for language in ('c', 'cpp'):
    assert f'compiler.{language}.extra_flags={flags}' in command
assert verified['compiler_returncode'] == 0 and verified['precompile_checks'] is True
assert verified['policy'] == policy.POLICY and verified['used_libraries'] == []
assert verified['source_sha256'] == audit['source_sha256'] == SOURCE
assert verified['build_path'].endswith('/bench-default/a7b05d1e88d242d19bca7129e5cf8e46/build')
assert verified['artifacts'] == verified['build_path'][:-5] + 'artifacts'
policy.validate_result((receipt / 'compile.stdout.json').read_text(), policy.BASE_FQBN, flags, verified['build_path'], project='motor_stand.ino')
policy.validate_preflight((receipt / 'properties.stdout.json').read_text(), policy.BASE_FQBN, flags,
                          verified['build_path'], verified['resolved_directories']['data'], project='motor_stand.ino')
pins = policy.installed_pins(verified['resolved_directories']['data'])
assert (receipt / 'precompile_pins.stdout.json').read_text().splitlines() == [h + '  ' + p for p, h in pins.items()]
assert all(verified['file_sha256'][p] == h for p, h in pins.items())
assert all(not p.read_bytes() for p in receipt.glob('*.stderr.txt'))
frozen = RAW / 'target_sources_bb3b462a'
manifest = read(frozen / 'manifest.json')
assert manifest['source_files'] == audit['source_files'] and manifest['source_sha256'] == SOURCE
assert len(audit['source_files']) == 95
digest = hashlib.sha256()
for name, expected in sorted(audit['source_files'].items(), key=lambda item: PureWindowsPath(item[0])):
    data = (frozen / name).read_bytes()
    assert sha(data) == expected, name
    digest.update(name.encode() + b'\0' + data)
assert digest.hexdigest() == SOURCE
implementation = read(RAW / 'implementer/first_source_freeze.json')
bench = {name.removeprefix('bench/motor_stand/'): meta['sha256'] for name, meta in implementation['files'].items()}
assert len(bench) == 5 and all(audit['source_files'][name] == h for name, h in bench.items())
prior = read(ROOT / 'state/analysis/P2_ui_adc_probe_raw/target_sources_396bcc45/manifest.json')['source_files']
shared = {name: h for name, h in audit['source_files'].items() if name not in bench}
assert len(shared) == 90 and all(prior[name] == h for name, h in shared.items())

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

previous_table = next(r for r in read(ROOT / 'state/reviews/P2_pin_table_review_raw/target_d72bff70_bench-default.json')['artifacts'] if r['file'] == 'app.ino.elf')['table']
allowed_used = {'__real___aeabi_uldivmod', '__real_abort', '__real_memset', 'pinctrl_configure_pins',
                'pinctrl_lookup_state', 'sys_clock_cycle_get_64', 'z_impl_device_init',
                'z_impl_device_is_ready', 'z_impl_k_thread_create', 'z_impl_k_thread_name_set'}
native_callbacks = ['_ZN6motors8UnoQPort18configureEnableLowEPv', '_ZN6motors8UnoQPort12configurePwmEPvNS_7ChannelE',
                    '_ZN6motors8UnoQPort11writeEnableEPvb', '_ZN6motors8UnoQPort8writePwmEPvNS_7ChannelEjj',
                    '_ZN6motors8UnoQPort6settleEPv', '_ZN6motors8UnoQPort7clockUsEPv']
runner_ctor = '_ZN11motor_stand6RunnerC1ERKN6motors4PortE'
runner_begin = '_ZN11motor_stand6Runner5beginERKNS_6GrantsE'
runner_poll = '_ZN11motor_stand6Runner4pollEv'
native_port = '_ZN11motor_stand6Native4portEv'
uno_port = '_ZN6motors8UnoQPort4portEv'
gate_ctor = '_ZN6motors9MotorGateC1ERKNS_4PortE'
candidate = '_ZN6motors12_GLOBAL__N_115candidatePeriodEj'
rate = '_ZN6motors12_GLOBAL__N_113candidateRateEj'
records = []
final_functions = None
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
    assert functions['_Z10__loopHookv'] == functions['initVariant'] == functions[runner_poll] == bytes.fromhex('7047')
    thread = next(s for s in elf.sections if s['name'] == '.static_thread_data_area')
    bounds = [s for s in elf.symbols if s['name'] in ('__static_thread_data_list_start', '__static_thread_data_list_end')]
    assert thread['size'] == 0 and len(bounds) == 2
    assert all(s['section_index'] == thread['index'] and s['value'] == 0 for s in bounds)
    used = sorted({r['name'] for r in elf.relocations if r['symbol_section'] == ''})
    assert {n for n in used if not n.startswith('__device_dts_ord_')} == allowed_used
    assert all(name in exports for name in used)
    defined = {s['name'] for s in elf.symbols if s['section_index'] and s['size']}
    forbidden = ('Bridge', 'Serial', 'Router', 'Robot', 'runtime', 'recorder', 'opp_sensors', 'UnoQMatrix',
                 'qtr_cal', 'line_qtr', 'InputOwner', '_ZN5power', 'imu', 'Matrix', 'MotorGate5apply', 'MotorGate5reset')
    assert not any(any(part in name for part in forbidden) for name in defined)
    assert not any(name in used for name in ('malloc', 'calloc', 'realloc', 'free', '_Znwj', '_Znaj'))
    assert calls(elf, '__cxa_allocate_exception') == ['abort']
    assert calls(elf, 'main') == ['initVariant', '_Z20start_static_threadsv', 'setup', 'loop', '_Z10__loopHookv']
    assert calls(elf, 'setup') == [runner_begin] and functions['setup'].startswith(bytes.fromhex('0023'))
    assert calls(elf, 'loop') == [runner_poll]
    assert calls(elf, '_GLOBAL__sub_I_setup') == [native_port, runner_ctor]
    assert calls(elf, native_port) == [uno_port] and calls(elf, runner_ctor) == [gate_ctor]
    assert not refs(elf, gate_ctor)
    assert calls(elf, uno_port) == ['memset', *native_callbacks, candidate]
    assert calls(elf, candidate) == [rate, '__aeabi_uldivmod']
    assert calls(elf, rate) == ['__aeabi_uldivmod']
    rate_constants = ('.llext.rodata.noreloc',) if row['name'] != 'motor_stand.ino_temp.elf' else (
        '.rodata._ZN6motors12_GLOBAL__N_1L10PRESCALERSE',
        '.rodata._ZN6motors12_GLOBAL__N_1L7DOMAINSE',
        '.rodata._ZN6motors12_GLOBAL__N_1L9SELECTORSE')
    assert all(r['symbol_section'] in (*rate_constants, '.text') for r in refs(elf, rate))
    assert calls(elf, runner_begin) == ['_ZN6motors9MotorGate5beginEv', '_ZNK6motors9MotorGate5faultEv', '_ZN6motors9MotorGate4haltEv']
    # Actual reviewed instruction prefix: consumed-attempt guard, grant load,
    # false-path DISABLED store and return before the first Gate call.
    prefix = bytes.fromhex('f0b590f87050044685b0002d4bd1012680f870600b782bb9354680f85860284605b0f0bd')
    assert functions[runner_begin].startswith(prefix)
    assert functions[gate_ctor].find(bytes.fromhex('9847')) == -1
    table = [s for s in elf.symbols if s['name'] == '_ZN6zephyr7arduinoL12arduino_pinsE']
    assert len(table) == 1
    table = table[0]
    assert table['size'] == 560 and sha(symbol_bytes(elf, table)) == previous_table['bytes_sha256']
    assert not elf.sections[table['section_index']]['flags'] & 1
    rels = [dict(offset=r['offset'] - table['value'], type=r['type'], name=r['name'], symbol_section=r['symbol_section'], symbol_value=r['symbol_value'])
            for r in elf.relocations if r['section'] == table['section'] and table['value'] <= r['offset'] < table['value'] + table['size']]
    assert rels == previous_table['relocations']
    count = next(s for s in elf.symbols if s['name'] == '_ZN11native_pins5COUNTE')
    pointer = next(s for s in elf.symbols if s['name'] == '_ZN11native_pins5TABLEE')
    assert struct.unpack('<I', symbol_bytes(elf, count))[0] == 70
    links = [r for r in elf.relocations if r['section'] == pointer['section'] and r['offset'] == pointer['value']]
    assert len(links) == 1 and links[0]['symbol_section'] == table['section']
    assert links[0]['symbol_value'] + struct.unpack('<I', symbol_bytes(elf, pointer))[0] == table['value']
    runner = next(s for s in elf.symbols if s['name'] == '_ZN12_GLOBAL__N_16runnerE')
    native = next(s for s in elf.symbols if s['name'] == '_ZN12_GLOBAL__N_16nativeE')
    assert (runner['size'], runner['value'], runner['section']) == (120, 0, '.bss')
    assert (native['size'], native['value'], native['section']) == (40, 120, '.bss')
    bss = elf.sections[runner['section_index']]
    assert bss['size'] == 160 and bss['alignment'] == 8
    metadata = account['metadata_chunks']
    regions = {r['name']: r['retained_chunk'] for r in account['copied_regions']}
    order = ['.text', '.data', '.rodata', '.bss', '.exported_sym', '.preinit_array', '.init_array', '.fini_array']
    extra = [name for name in regions if name not in order]
    assert not extra or row['name'] == 'motor_stand.ino_temp.elf'
    allocations = [('extension', metadata['extension']), ('section_map', metadata['section_map'])]
    allocations += [(name, regions[name]) for name in order if name in regions] + [(name, regions[name]) for name in extra]
    allocations += [('global_symbols', metadata['global_symbols']), ('export_copy', metadata['export_copy'])]
    consumed, ledger = metadata['initial_bookkeeping'], []
    for purpose, chunk in allocations:
        ledger.append(dict(purpose=purpose, chunk=chunk, available_before=262144 - consumed, fits=chunk <= 262144 - consumed))
        consumed += chunk
    assert consumed == account['conditional_pristine_peak_consumption'] and all(x['fits'] for x in ledger)
    if row['name'] == 'motor_stand.ino.elf':
        assert (0x08100010 + elf.section_header_offset) % 4 == 0
        for section in elf.sections:
            if section['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab'):
                assert (0x08100010 + section['offset']) % max(1, section['alignment']) == 0
        final_functions = functions
        disassembly = next(c['stdout'] for c in row['commands'] if 'objdump' in c['argv'][0])
        witnesses = []
        for name in ['_GLOBAL__sub_I_setup', 'setup', runner_begin, runner_poll, runner_ctor, gate_ctor, native_port,
                     uno_port, candidate, rate, 'main', '_Z20start_static_threadsv', '__cxa_allocate_exception', *native_callbacks]:
            at = disassembly.index(' <' + name + '>:')
            witnesses.append(disassembly[disassembly.rfind('\n', 0, at):disassembly.find('\n\n', at)])
        (OUT / 'target_bb3b462a_bench-default_witness.txt').write_text('\n'.join(witnesses))
    else:
        assert final_functions is not None
        compared = ['setup', '_GLOBAL__sub_I_setup', runner_ctor, gate_ctor, runner_begin, runner_poll, native_port, uno_port, candidate, rate]
        if row['name'] == 'motor_stand.ino_debug.elf':
            assert all(functions[name] == final_functions[name] for name in compared)
        else:
            final_elf = module.Elf(FOLDER / 'motor_stand.ino.elf')
            for name in compared:
                normalized = []
                for image in (elf, final_elf):
                    body = bytearray(image.functions()[name])
                    symbol = next(s for s in image.symbols if s['name'] == name)
                    for relocation in refs(image, name):
                        assert relocation['type'] == 2
                        offset = relocation['offset'] - (symbol['value'] & ~1)
                        body[offset:offset + 4] = b'\0' * 4
                    normalized.append(body)
                assert normalized[0] == normalized[1], name
                assert calls(elf, name) == calls(final_elf, name), name
    records.append(dict(file=row['name'], sha256=row['sha256'], bytes=len(data), payload=account['compiler_payload'],
        conditional_peak=consumed, free_span=262144 - consumed, largest_free_payload=262144 - consumed - 4,
        allocations=ledger, copied_regions=account['copied_regions'], metadata=metadata,
        used_imports={name: f'0x{exports[name]:08x}' for name in used}, sole_initializer=account['init'],
        runner=runner, native=native, bss=bss, thread_bounds=bounds, pin_table_sha256=sha(symbol_bytes(elf, table)),
        default_grant=False, startup_callback_or_clock_io=False))
abi = audit['abi']
assert abi['returncode'] == 0 and not abi['stderr']
assert re.findall(r'^\$\d+ = (\d+)$', abi['stdout'], re.MULTILINE) == ['120', '40', '24', '16', '44']
assert '/*     88      |      24 */    struct motor_stand::Report' in abi['stdout']
assert '/*    112      |       1 */    bool attempted_' in abi['stdout']
assert '/*      8      |      16 */    struct motors::HaltResult' in abi['stdout']
final_bytes = (FOLDER / 'motor_stand.ino.elf').read_bytes()
zsk = (FOLDER / 'motor_stand.ino.elf-zsk.bin').read_bytes()
assert len(zsk) == len(final_bytes) and zsk[16:] == final_bytes[16:]
assert [i for i, (a, b) in enumerate(zip(final_bytes, zsk)) if a != b] == [7, 8, 9, 12, 13]
result = dict(verdict='PASS_EXACT_CHECKED_DEFAULT_INHIBIT_TARGET_AND_CONDITIONAL_FIT', source_sha256=SOURCE,
    source_files=95, unchanged_shared_files=90, artifact_records=records,
    abi=dict(Runner=120, Native=40, MotorGate=88, Report=24, HaltResult=16, Port=44, report_offset=88, attempted_offset=112),
    elf_sha256=sha(final_bytes), zsk_sha256=sha(zsk), loader_sha256=loader_sha,
    evidence='Direct byte parsing plus retained16 offline ELF/ABI commands. Actual default false-grant instructions and constructor paths inspected; no target execution.',
    import_qualification='Retained pinctrl/device-init/native clock functions are callback targets, not executed by passive startup; static thread bounds are empty.',
    limits='Conditional pristine256KiB loader pool, successful persistent peeks, unchanged loader/config and no interleaved/constructor allocation. No actual load/free-RAM/stack/WCET/electrical inhibition, physical motor acceptance or upload permission.')
(OUT / 'target_bb3b462a_bench-default.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: records[0][k] for k in ('sha256', 'bytes', 'payload', 'conditional_peak', 'free_span', 'largest_free_payload')}, indent=2))
