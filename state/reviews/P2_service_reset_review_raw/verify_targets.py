"""Independent offline D103 source/ELF/startup/conditional-allocation audit."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_service_reset_raw'
source = json.loads((OUT / 'source_maps_1790187050866977000.json').read_text())
spec = importlib.util.spec_from_file_location('d103_review_elf',
    ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
decoder = importlib.util.module_from_spec(spec); spec.loader.exec_module(decoder)

def refs(elf, name):
    symbol = next(s for s in elf.symbols if s['name'] == name and s['size'])
    section = elf.sections[symbol['section_index']]
    offset = (symbol['value'] & ~1) - section['address']
    return [r['name'] for r in elf.relocations if r['section'] == section['name'] and
            offset <= r['offset'] < offset + symbol['size']]

def relocations(text):
    result = {}; section = None
    for line in text.splitlines():
        match = re.match(r"Relocation section '\.rel([^']+)'", line)
        if match:
            section = match[1]; result[section] = []; continue
        match = re.match(r'([0-9a-f]+)\s+[0-9a-f]+\s+(R_ARM_\S+)\s+([0-9a-f]+)\s+(.+)', line)
        if match and section is not None:
            result[section].append((int(match[1], 16), match[2], int(match[3], 16), match[4]))
    return result

def object_changes(before, after):
    old = {o['path']: o for o in before['objects']}; new = {o['path']: o for o in after['objects']}
    added = sorted(set(new) - set(old)); removed = sorted(set(old) - set(new)); changed = {}
    for name in set(old) & set(new):
        left = {s['name']: s for s in old[name]['alloc_sections']}
        right = {s['name']: s for s in new[name]['alloc_sections']}
        lr = relocations(old[name]['relocations']['stdout']); rr = relocations(new[name]['relocations']['stdout'])
        differences = [s for s in sorted(left.keys() | right.keys()) if
                       left.get(s) != right.get(s) or lr.get(s) != rr.get(s)]
        if differences: changed[name] = differences
    return {'added': added, 'removed': removed, 'changed': changed}

results = {}; audits = {}; stack = {}
for mode in ('bench-default', 'match-immediate'):
    folder = RAW / ('target_1fbd7238_' + mode)
    audit = json.loads((folder / 'audit.json').read_text()); audits[mode] = audit
    prior = ROOT / ('state/analysis/P2_frame_packing_raw/target_3bf0da00_' + mode)
    old = json.loads((prior / 'audit.json').read_text())
    baseline = decoder.Elf(prior / 'app.ino.elf').account()
    assert source['app']['source_sha256'] == audit['source_sha256']
    assert source['app']['file_sha256'] == audit['source_files']
    for name, digest in audit['source_files'].items():
        assert hashlib.sha256((RAW / 'target_sources_1fbd7238' / name).read_bytes()).hexdigest() == digest
        local = ROOT / ('src/app/app.ino' if name == 'app.ino' else name)
        assert hashlib.sha256(local.read_bytes()).hexdigest() == digest
    verified = []
    for row in audit['records']:
        path = folder / Path(row['path']).name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        elf = decoder.Elf(path)
        imports = sorted({s['name'] for s in elf.symbols if not s['section_index'] and s['name']})
        assert imports == baseline['undefined']
        verified.append({'name': path.name, 'sha256': row['sha256'], 'imports': len(imports)})
    binary = (folder / 'app.ino.elf-zsk.bin').read_bytes()
    elf_bytes = (folder / 'app.ino.elf').read_bytes()
    package = next(row for row in audit['bundles'] if row['name'] == 'app.ino.elf-zsk.bin')
    assert hashlib.sha256(binary).hexdigest() == package['sha256']
    assert len(binary) == len(elf_bytes) and binary[:7] == elf_bytes[:7] and binary[16:] == elf_bytes[16:]
    for key in ('base_sha256', 'native_names', 'math_missing', 'math_symbols', 'math_aliases', 'base_static_threads'):
        assert audit[key] == old[key], key
    for key in ('native_exports', 'math_exports'):
        assert audit[key]['returncode'] == 0 and audit[key]['stdout'] == old[key]['stdout']
    for name, row in audit['metadata'].items():
        data = row['text'].encode()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    value = '1' if mode == 'match-immediate' else '0'
    commands = json.loads(audit['metadata']['compile_commands.json']['text'])
    for command in commands:
        args = command['arguments']
        assert '-DMATCH=' + value in args and '-DMOTORS_ALLOWED=' + value in args
        if not command['file'].endswith('/tls-syms.S'): assert '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0' in args
        assert not any('/Arduino/libraries/' in a for a in args)
    elf = decoder.Elf(folder / 'app.ino.elf'); account = elf.account()
    assert len(account['init']) == 1 and not account['fini']
    assert account['init'][0]['name'] == '_GLOBAL__sub_I_setup'
    assert elf.functions()['_Z10__loopHookv'] == bytes.fromhex('7047')
    assert next(s for s in elf.symbols if s['name'] == '_Z10__loopHookv')['bind'] == 1
    assert next(s for s in elf.sections if s['name'] == '.static_thread_data_area')['size'] == 0
    assert '_Z10__loopHookv' in refs(elf, 'main')
    assert '_ZN3app7Runtime5beginERKNS_11SetupGrantsE' in refs(elf, 'setup')
    assert '_ZN3app7Runtime4stepEv' in refs(elf, 'loop')
    startup_refs = refs(elf, '_GLOBAL__sub_I_setup')
    assert not any('DumpPort5begin' in n or 'DumpPort5ready' in n or 'DumpPort7advance' in n for n in startup_refs)
    owners = {n: next(s['size'] for s in elf.symbols if s['name'] == n and s['size']) for n in (
        '_ZN12_GLOBAL__N_17runtimeE', '_ZN12_GLOBAL__N_19dump_portE', '_ZN12_GLOBAL__N_17sourcesE')}
    assert owners['_ZN12_GLOBAL__N_19dump_portE'] == 204
    assert owners['_ZN12_GLOBAL__N_17sourcesE'] == 848
    for section in elf.sections:
        if section['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab', '.shstrtab'):
            assert (0x08100010 + section['offset']) % section['alignment'] == 0
    assert (0x08100010 + elf.section_header_offset) % 4 == 0
    metadata = account['metadata_chunks']; pool = 262144; used = metadata['initial_bookkeeping']
    ordered = []; chunks = [('extension', metadata['extension']), ('section_map', metadata['section_map'])]
    region_order = ['.text', '.data', '.rodata', '.bss', '.exported_sym', '.preinit_array', '.init_array', '.fini_array']
    by_name = {s['name']: s['retained_chunk'] for s in account['copied_regions']}
    assert set(by_name) <= set(region_order)
    chunks += [(name, by_name[name]) for name in region_order if name in by_name]
    chunks += [('global_symbols', metadata['global_symbols']), ('export_copy', metadata['export_copy'])]
    for name, chunk in chunks:
        assert chunk <= pool - used, (mode, name, chunk, pool - used)
        ordered.append({'name': name, 'chunk': chunk, 'free_span_before': pool-used})
        used += chunk
    assert used == account['conditional_pristine_peak_consumption']
    changes = object_changes(old, audit)
    assert not changes['removed'] and changes['added'] == [
        'sketch/src/app/runtime_service.cpp.o', 'sketch/src/app/transaction_service.cpp.o']
    for name in ('sketch/src/hal/dump_uart_unoq.cpp.o', 'sketch/src/hal/recorder_csv.cpp.o',
                 'sketch/src/core/logframe.cpp.o', 'sketch/src/hal/motors.cpp.o'):
        assert name not in changes['changed']
    disassembly = audit['records'][0]['disassembly']
    functions = {c.splitlines()[0].split(' <', 1)[-1].removesuffix('>:'): c for c in
                 re.split(r'(?m)(?=^[0-9a-f]+ <)', disassembly) if c.splitlines() and ' <' in c.splitlines()[0]}
    selected = {name: functions[name] for name in ('fsm::Robot::reset()',
        'app::Runtime::applyServiceReset()', 'app::Transaction::resetStoppedRobotForService()', 'app::Runtime::step()')}
    assert 'subw\tsp, sp, #2644' in selected['fsm::Robot::reset()']
    assert '{r4, r5, r6, r7, r8, r9, sl, fp, lr}' in selected['fsm::Robot::reset()']
    stack[mode] = {'disassembly': selected, 'robot_reset_local_frame_bytes': 2680,
                   'scope': 'Local compiler frame only; caller/callee/interrupt headroom unmeasured'}
    results[mode] = {'source_files': len(audit['source_files']), 'elfs': verified,
        'objects': len(audit['objects']), 'metadata_files': len(audit['metadata']), 'owners': owners,
        'initializer_refs': startup_refs, 'compiler_payload': account['compiler_payload'],
        'conditional_loader_peak': used, 'conditional_free_span': pool-used,
        'conditional_largest_payload': pool-used-4, 'ordered_allocations': ordered,
        'source_object_changes': changes, 'package_sha256': package['sha256'],
        'package_header_7_through_15': binary[7:16].hex(), 'package_elf_payload_from_16_identical': True}

manifest = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
assert set(manifest) == set(source['entries'])
refreshed = manifest == {key: value['source_sha256'] for key, value in source['entries'].items()}
assert refreshed or manifest == {key: value['existing_key'] for key, value in source['entries'].items()}
result = {'scope': 'Independent local offline exact-source/ELF audit; no target operation',
          'source_sha256': source['app']['source_sha256'], 'modes': results, 'stack': stack,
          'mode_object_changes': object_changes(audits['bench-default'], audits['match-immediate']),
          'same_seven_keys_preserved': True, 'refreshed_keys_match_review': refreshed,
          'loader_primary_hashes': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
              'state/analysis/P2_memory_validation_raw/llext.h',
              'state/analysis/P2_memory_validation_raw/llext_mem.c',
              'state/analysis/P2_memory_validation_raw/llext_load.c')},
          'limits': 'No measured loadedRAM, total stack, WCET, UART/physical/gate/upload authority'}
out = OUT / ('target_verification_' + str(time.time_ns()) + '.json')
out.write_text(json.dumps(result, indent=2) + '\n')
print(out)
print(json.dumps({mode: {key: row[key] for key in ('compiler_payload', 'conditional_loader_peak',
    'conditional_free_span', 'conditional_largest_payload', 'owners')} for mode, row in results.items()}, indent=2))
