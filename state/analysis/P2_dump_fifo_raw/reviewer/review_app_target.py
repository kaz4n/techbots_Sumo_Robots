"""D117 offline app identity/startup/native ABI and reused loader-model audit."""
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
sys.path.insert(0, str(ROOT / 'tools'))
import app_build_policy as policy
model_path = ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py'
spec = importlib.util.spec_from_file_location('existing_model', model_path)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_bytes())
name = sys.argv[1]
assert re.fullmatch(r'target_[a-f0-9]{8}_(bench-default|match-immediate)', name)
FOLDER = RAW / name
audit = read(FOLDER / 'audit.json')
SOURCE = audit['source_sha256']
mode = name.split('_', 2)[2]
match = mode == 'match-immediate'
receipt = FOLDER / 'build_receipt'
verified = read(receipt / 'verified.json')
command = read(receipt / 'command.json')
flags = f'-DMATCH={int(match)} -DMOTORS_ALLOWED={int(match)}'
fqbn = policy.BASE_FQBN + (':wait_linux_boot=no' if match else '')
assert command[command.index('--fqbn') + 1] == verified['fqbn'] == fqbn
for language in ('c', 'cpp'):
    assert f'compiler.{language}.extra_flags={flags}' in command
assert command[-1] == '/home/arduino/sumox26_codex_build/' + SOURCE + '/app'
assert verified['compiler_returncode'] == 0 and verified['precompile_checks'] is True
assert verified['policy'] == policy.POLICY and verified['used_libraries'] == []
assert verified['source_sha256'] == SOURCE
assert verified['artifacts'] == verified['build_path'][:-5] + 'artifacts'
policy.validate_result((receipt / 'compile.stdout.json').read_text(), fqbn, flags, verified['build_path'])
policy.validate_preflight((receipt / 'properties.stdout.json').read_text(), fqbn, flags,
                          verified['build_path'], verified['resolved_directories']['data'])
pins = policy.installed_pins(verified['resolved_directories']['data'])
assert (receipt / 'precompile_pins.stdout.json').read_text().splitlines() == [h + '  ' + p for p, h in pins.items()]
assert all(verified['file_sha256'][p] == h for p, h in pins.items())
assert all(not p.read_bytes() for p in receipt.glob('*.stderr.txt'))
frozen = RAW / ('target_sources_' + SOURCE[:8])
manifest = read(frozen / 'manifest.json')
assert manifest['source_files'] == audit['source_files'] and manifest['source_sha256'] == SOURCE
assert len(audit['source_files']) == 91 and len(audit['objects']) == 79
digest = hashlib.sha256()
for path, expected in sorted(audit['source_files'].items(), key=lambda item: PureWindowsPath(item[0])):
    data = (frozen / path).read_bytes()
    assert sha(data) == expected, path
    digest.update(path.encode() + b'\0' + data)
assert digest.hexdigest() == SOURCE
prior_shared = read(ROOT / 'state/analysis/P2_recorder_transport_raw/target_sources_e2cd303f/manifest.json')['source_files']
shared = {p: h for p, h in audit['source_files'].items() if p != 'app.ino'}
assert len(shared) == 90 and set(shared).issubset(prior_shared)
changed_shared = {p: dict(before=prior_shared[p], after=h) for p, h in shared.items() if prior_shared[p] != h}
assert set(changed_shared) == {'src/hal/dump_uart_unoq.h', 'src/hal/dump_uart_unoq.cpp'}
freeze_matches = []
for freeze_path in sorted((RAW / 'implementer').glob('*_source_freeze.json')):
    candidate = read(freeze_path)
    if (audit['source_files']['app.ino'] == candidate['files']['src/app/app.ino']['sha256']
            and all(shared[p] == candidate['files'][p]['sha256'] for p in changed_shared)):
        freeze_matches.append(freeze_path)
assert len(freeze_matches) == 1, freeze_matches
freeze_path = freeze_matches[0]

loader = (ROOT / 'state/analysis/P2_ui_adc_probe_raw/root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.elf').read_bytes()
loader_sha = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
assert sha(loader) == audit['base_sha256'] == loader_sha
header = struct.unpack_from('<16sHHIIIIIHHHHHH', loader)
sections = [struct.unpack_from('<10I', loader, header[6] + i * header[11]) for i in range(header[12])]
strings = sections[header[13]]
names = loader[strings[4]:strings[4] + strings[5]]
export_section = next(s for s in sections if names[s[0]:].split(b'\0')[0] == b'llext_const_symbol_area')
exports = {}
for off in range(export_section[4], export_section[4] + export_section[5], 8):
    address, value = struct.unpack_from('<II', loader, off)
    section = next(s for s in sections if s[1] != 8 and s[3] <= address < s[3] + s[5])
    start = section[4] + address - section[3]
    symbol = loader[start:section[4] + section[5]].split(b'\0')[0].decode()
    assert symbol not in exports or exports[symbol] == value
    exports[symbol] = value


def refs(elf, name):
    sym = next(s for s in elf.symbols if s['name'] == name)
    at = sym['value'] & ~1
    return [r for r in elf.relocations if r['section'] == sym['section'] and at <= r['offset'] < at + sym['size']]


def functions(elf):
    return {s['name']: elf.section_bytes(elf.sections[s['section_index']])[s['value'] & ~1:(s['value'] & ~1) + s['size']]
            for s in elf.symbols if s['type'] == 2 and s['section_index'] and s['size']}


def normalized(elf, name):
    data = bytearray(functions(elf)[name])
    sym = next(s for s in elf.symbols if s['name'] == name)
    for rel in refs(elf, name):
        if rel['type'] != 2:
            assert rel['type'] in (10, 30, 47, 48)  # Includes unchanged IMU THM_JUMP24.
            continue
        at = rel['offset'] - (sym['value'] & ~1)
        data[at:at + 4] = bytes(4)
    return bytes(data)


def calls(elf, name):
    return [r['name'] for r in refs(elf, name) if r['symbol_type'] == 2]


def used_imports(elf):
    return sorted({r['name'] for r in elf.relocations if r['symbol_section'] == '' and not r['section'].startswith('.debug')})


prior = model.Elf(ROOT / ('state/analysis/P2_display_channel_raw/target_618d3a96_' + mode + '/app.ino.elf'))
final = model.Elf(FOLDER / 'app.ino.elf')
final_funcs = functions(final)
prior_funcs = functions(prior)
new_functions = sorted(set(final_funcs) - set(prior_funcs))
removed_functions = sorted(set(prior_funcs) - set(final_funcs))
changed_functions = sorted(n for n in set(final_funcs) & set(prior_funcs) if normalized(final, n) != normalized(prior, n))
assert not removed_functions
assert all('UnoQDumpPort' in n for n in new_functions + changed_functions), new_functions + changed_functions
records = []
for row in audit['records']:
    file = Path(row['path']).name
    elf = model.Elf(FOLDER / file)
    assert sha(elf.raw) == row['sha256'] == verified['file_sha256'][row['path']]
    assert len(elf.raw) == row['bytes']
    keys = ['sizes', 'size_sections', 'undefined', 'relocations', 'sections']
    if file == 'app.ino.elf':
        keys += ['init_array', 'nm_all']
    for key in keys:
        assert row[key]['returncode'] == 0 and not row[key]['stderr']
    account, funcs = elf.account(), functions(elf)
    assert len(account['init']) == 1 and account['init'][0]['name'] == '_GLOBAL__sub_I_setup'
    assert not account['fini'] and not any(r for r in elf.relocations if r['section'] == '.preinit_array')
    assert funcs['_Z10__loopHookv'] == funcs['initVariant'] == bytes.fromhex('7047')
    assert next(s for s in elf.symbols if s['name'] == '_Z10__loopHookv')['bind'] == 1
    assert next(s for s in elf.symbols if s['name'] == 'initVariant')['bind'] == 2
    thread = next(s for s in elf.sections if s['name'] == '.static_thread_data_area')
    bounds = [s for s in elf.symbols if s['name'] in ('__static_thread_data_list_start', '__static_thread_data_list_end')]
    assert thread['size'] == 0 and len(bounds) == 2
    assert all(s['section_index'] == thread['index'] and s['value'] == 0 for s in bounds)
    used = used_imports(elf)
    assert used == used_imports(prior) and all(n in exports for n in used)
    assert not any(n in used for n in ('malloc', 'calloc', 'realloc', 'free', '_Znwj', '_Znaj'))
    assert calls(elf, '__cxa_allocate_exception') == ['abort']
    assert calls(elf, 'main') == ['initVariant', '_Z20start_static_threadsv', 'setup', 'loop', '_Z10__loopHookv']
    for n in ('setup', 'loop', '_GLOBAL__sub_I_setup'):
        assert normalized(elf, n) == normalized(prior, n) and calls(elf, n) == calls(prior, n)
    native = next(s for s in elf.symbols if s['name'] == '_ZN12_GLOBAL__N_19dump_portE')
    section = elf.sections[native['section_index']]
    data = elf.section_bytes(section)[native['value']:native['value'] + native['size']]
    assert native['section'] == '.data' and native['size'] == 208 and data == b'\x01' + bytes(207)
    assert not any(r for r in elf.relocations if r['section'] == native['section'] and native['value'] <= r['offset'] < native['value'] + native['size'])
    assert set(funcs) == set(final_funcs)
    for n in funcs:
        if file == 'app.ino_debug.elf':
            assert funcs[n] == final_funcs[n], n
        if file == 'app.ino_temp.elf':
            assert normalized(elf, n) == normalized(final, n) and calls(elf, n) == calls(final, n), n
            nonabs = lambda image: [(r['offset'], r['type'], r['name']) for r in refs(image, n) if r['type'] != 2]
            assert nonabs(elf) == nonabs(final), n
    if file == 'app.ino.elf':
        assert (0x08100010 + elf.section_header_offset) % 4 == 0
        for s in elf.sections:
            if s['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab'):
                assert (0x08100010 + s['offset']) % max(1, s['alignment']) == 0
    metadata = account['metadata_chunks']
    regions = {r['name']: r['retained_chunk'] for r in account['copied_regions']}
    order = ['.text', '.data', '.rodata', '.bss', '.exported_sym', '.preinit_array', '.init_array', '.fini_array']
    extra = [n for n in regions if n not in order]
    assert not extra or file == 'app.ino_temp.elf'
    allocations = [('extension', metadata['extension']), ('section_map', metadata['section_map'])]
    allocations += [(n, regions[n]) for n in order if n in regions] + [(n, regions[n]) for n in extra]
    allocations += [('global_symbols', metadata['global_symbols']), ('export_copy', metadata['export_copy'])]
    consumed, ledger = metadata['initial_bookkeeping'], []
    for purpose, chunk in allocations:
        ledger.append(dict(purpose=purpose, chunk=chunk, available_before=262144 - consumed, fits=chunk <= 262144 - consumed))
        consumed += chunk
    assert consumed == account['conditional_pristine_peak_consumption']
    records.append(dict(file=file, sha256=sha(elf.raw), bytes=len(elf.raw), payload=account['compiler_payload'],
                        peak=consumed, span=262144 - consumed, largest_payload=262144 - consumed - 4,
                        allocations=ledger, metadata=metadata, copied_regions=account['copied_regions'],
                        used_imports={n: f'0x{exports[n]:08x}' for n in used}, native=native,
                        native_initialized_bytes_sha256=sha(data), functions_identical_count=len(funcs)))
    if file == 'app.ino.elf':
        witness = []
        local_disassembly = OUT / (name + '_full_objdump.txt')
        disassembly = local_disassembly.read_text() if local_disassembly.exists() else row['disassembly']
        selected = ['setup', 'loop', '_GLOBAL__sub_I_setup', *new_functions, *changed_functions]
        selected += [n for n in funcs if 'unoQDumpPort' in n]
        for n in dict.fromkeys(selected):
            marker = ' <' + n + '>:'
            at = disassembly.find(marker)
            if at < 0:
                witness.append('Not included in retained disassembly excerpt; ELF bytes independently checked: ' + n)
                continue
            witness.append(disassembly[disassembly.rfind('\n', 0, at) + 1:disassembly.find('\n\n', at)])
        (OUT / (name + '_witness.txt')).write_text('\n'.join(witness))
abi = read(FOLDER / 'd117_abi.json')
debug_hash = sha((FOLDER / 'app.ino_debug.elf').read_bytes())
assert abi['before_sha256'] == abi['after_sha256'] == debug_hash
assert abi['returncode'] == 0 and not abi['stderr'] and 'error' not in abi
sizes = [int(n) for n in re.findall(r'^\$\d+ = (\d+)$', abi['stdout'], re.M)]
assert sizes == [208, 4, 166304 if match else 166376, 8, 162544, 8, 24, 4, 1408, 8], sizes
assert '/*      0      |       1 */    const recorder::dump::Buffering buffering_' in abi['stdout']
package = (FOLDER / 'app.ino.elf-zsk.bin').read_bytes()
bundle = next(b for b in audit['bundles'] if b['name'] == 'app.ino.elf-zsk.bin')
assert sha(package) == bundle['sha256'] == verified['file_sha256'][bundle['path']]
assert len(package) == len(final.raw) and package[16:] == final.raw[16:]
assert package[7] == 1 and int.from_bytes(package[8:12], 'little') == len(package)
deployed = next(r for r in records if r['file'] == 'app.ino.elf')
fit = all(r['fits'] for r in deployed['allocations'])
result = dict(verdict='PASS_TARGET_IDENTITY_STARTUP_NATIVE_ABI_CONDITIONAL_FIT' if fit else 'BLOCKER_DEFAULT_TARGET_ALLOCATION_FIT',
              source_sha256=SOURCE, mode=mode, source_files=91, objects=79, unchanged_shared_files=88,
              changed_shared=changed_shared, records=records, zsk_sha256=sha(package),
              source_freeze_path=str(freeze_path.relative_to(ROOT)), source_freeze_sha256=sha(freeze_path.read_bytes()),
              loader_sha256=loader_sha, model_sha256=sha(model_path.read_bytes()),
              prior_profile_elf_sha256=sha(prior.raw), new_functions=new_functions, changed_functions=changed_functions,
              startup='Unchanged app source/normalized instructions/call bindings; existing Transaction/MotorGate setup is not passive. New native object initializes only mode byte1; false dump grants remain.',
              abi_sizes_and_alignments=sizes, gdb_sha256=abi['gdb_sha256'],
              limitations='Pristine256KiB pool, persistent aligned flash peeks and no interleaved allocations. No actual MCU load, memory/WCET, setup ACK, native stream rate/framing/receiver delivery, physical grants or upload permission.')
(OUT / (name + '.json')).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(verdict=result['verdict'], source=SOURCE, **{k: deployed[k] for k in ('sha256', 'payload', 'peak', 'span', 'largest_payload')}), indent=2))
