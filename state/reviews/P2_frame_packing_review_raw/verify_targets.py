"""Independent offline D102 source, ELF, loader-order and inert-key verification."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_frame_packing_raw'
source = json.loads((OUT / 'source_maps.json').read_text())
spec = importlib.util.spec_from_file_location('review_elf', ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
decoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)
old_folder = ROOT / 'state/analysis/P2_app_dump_raw/target_83600858_match-immediate'
old_audit = json.loads((old_folder / 'audit.json').read_text())
old_elf = decoder.Elf(old_folder / 'app.ino.elf')
old_account = old_elf.account()
old_imports = old_account['undefined']

def refs(elf, name):
    symbol = next(s for s in elf.symbols if s['name'] == name and s['size'])
    section = elf.sections[symbol['section_index']]
    offset = (symbol['value'] & ~1) - section['address']
    return [r['name'] for r in elf.relocations if r['section'] == section['name'] and
            offset <= r['offset'] < offset + symbol['size']]

def relocation_map(text):
    result = {}; section = None
    for line in text.splitlines():
        match = re.match(r"Relocation section '\.rel([^']+)'", line)
        if match:
            section = match[1]; result[section] = []; continue
        match = re.match(r'([0-9a-f]+)\s+[0-9a-f]+\s+(R_ARM_\S+)\s+([0-9a-f]+)\s+(.+)', line)
        if match and section is not None:
            result[section].append((int(match[1], 16), match[2], int(match[3], 16), match[4]))
    return result

def object_changes(a, b):
    old = {o['path']: o for o in a['objects']}; new = {o['path']: o for o in b['objects']}
    assert old.keys() == new.keys()
    changed = {}
    for name in old:
        left = {s['name']: s for s in old[name]['alloc_sections']}
        right = {s['name']: s for s in new[name]['alloc_sections']}
        lr = relocation_map(old[name]['relocations']['stdout'])
        rr = relocation_map(new[name]['relocations']['stdout'])
        differences = [s for s in sorted(left.keys() | right.keys()) if
                       left.get(s) != right.get(s) or lr.get(s) != rr.get(s)]
        if differences: changed[name] = differences
    return changed

results = {}
audits = {}
for mode in ('bench-default', 'match-immediate'):
    folder = RAW / ('target_3bf0da00_' + mode)
    audit = json.loads((folder / 'audit.json').read_text())
    audits[mode] = audit
    assert source['app']['file_sha256'] == audit['source_files']
    assert source['app']['source_sha256'] == audit['source_sha256']
    for name, digest in audit['source_files'].items():
        assert hashlib.sha256((RAW / 'target_sources_3bf0da00' / name).read_bytes()).hexdigest() == digest
        path = ROOT / ('src/app/app.ino' if name == 'app.ino' else name)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    verified = []
    for row in audit['records']:
        path = folder / Path(row['path']).name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256']
        elf = decoder.Elf(path)
        imports = sorted({s['name'] for s in elf.symbols if not s['section_index'] and s['name']})
        assert imports == old_imports
        verified.append(dict(name=path.name, sha256=row['sha256'], imports=len(imports)))
    for key in ('base_sha256', 'native_names', 'math_missing', 'math_symbols', 'math_aliases', 'base_static_threads'):
        assert audit[key] == old_audit[key], key
    for key in ('native_exports', 'math_exports'):
        assert audit[key]['returncode'] == 0 and audit[key]['stdout'] == old_audit[key]['stdout']
    for name, row in audit['metadata'].items():
        data = row['text'].encode()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    mode_value = '1' if mode == 'match-immediate' else '0'
    commands = json.loads(audit['metadata']['compile_commands.json']['text'])
    for command in commands:
        args = command['arguments']
        assert '-DMATCH=' + mode_value in args and '-DMOTORS_ALLOWED=' + mode_value in args
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
    assert owners['_ZN12_GLOBAL__N_17runtimeE'] == 166216
    assert owners['_ZN12_GLOBAL__N_19dump_portE'] == 204
    assert owners['_ZN12_GLOBAL__N_17sourcesE'] == 848
    # Every flash-peek premise is checked; ordered allocations are cumulative and
    # unreleased up to this peak, so this also checks the required contiguous tail.
    for s in elf.sections:
        if s['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab', '.shstrtab'):
            assert (0x08100010 + s['offset']) % s['alignment'] == 0
    assert (0x08100010 + elf.section_header_offset) % 4 == 0
    metadata = account['metadata_chunks']; pool = 262144
    used = metadata['initial_bookkeeping']
    ordered = []
    chunks = [('extension', metadata['extension']), ('section_map', metadata['section_map'])]
    # llext_mem.h enum order and llext_copy_regions iterate TEXT, DATA, RODATA,
    # BSS, EXPORT, followed by the non-peeked setup arrays; not ELF section order.
    region_order = ['.text', '.data', '.rodata', '.bss', '.exported_sym',
                    '.preinit_array', '.init_array', '.fini_array']
    by_name = {s['name']: s['retained_chunk'] for s in account['copied_regions']}
    assert set(by_name) <= set(region_order)
    chunks += [(name, by_name[name]) for name in region_order if name in by_name]
    chunks += [('global_symbols', metadata['global_symbols']), ('export_copy', metadata['export_copy'])]
    for name, chunk in chunks:
        assert chunk <= pool - used, (mode, name, chunk, pool - used)
        ordered.append(dict(name=name, chunk=chunk, free_span_before=pool-used,
                            largest_payload_before=pool-used-4))
        used += chunk
    assert used == account['conditional_pristine_peak_consumption']
    changes = object_changes(old_audit, audit)
    for name in ('sketch/src/hal/dump_uart_unoq.cpp.o', 'sketch/src/hal/recorder_csv.cpp.o',
                 'sketch/src/core/logframe.cpp.o'):
        assert name not in changes
    results[mode] = dict(exact_source_files=len(audit['source_files']), elfs=verified,
        objects=len(audit['objects']), metadata=len(audit['metadata']), compile_commands=len(commands),
        owners=owners, initializer_refs=startup_refs, compiler_payload=account['compiler_payload'],
        copied_regions=account['copied_regions'], metadata_chunks=metadata,
        conditional_loader_peak=used, conditional_free_span=pool-used,
        conditional_largest_payload=pool-used-4, ordered_allocations=ordered,
        changes_from_d101_match=changes)

manifest = json.loads((ROOT / 'tools/p0_inert_sources.json').read_text())
assert set(manifest) == set(source['entries'])
assert manifest == {key: value['source_sha256'] for key, value in source['entries'].items()}
abi = json.loads((RAW / 'target_abi_retry/receipt.json').read_text())
assert abi['returncode'] == 0 and abi['source_sha256'] == source['app']['source_sha256']
debug_hash = next(r['sha256'] for r in results['bench-default']['elfs'] if r['name'] == 'app.ino_debug.elf')
assert abi['expected_debug_elf_sha256'] == debug_hash
values = [int(v) for v in re.findall(r'^\$\d+ = (\d+)$', (RAW / 'target_abi_retry/stdout.txt').read_text(), re.M)]
assert values == [126300, 4, 26, 1, 159200, 8, 166216, 8]
result = dict(scope='Independent offline review, exact staged identity and conditional pinned allocator only',
              source_sha256=source['app']['source_sha256'], modes=results, target_abi_values=values,
              mode_object_changes=object_changes(audits['bench-default'], audits['match-immediate']),
              same_seven_refreshed_keys_match_review=True,
              d101_match_loader_peak=old_account['conditional_pristine_peak_consumption'],
              d102_match_loader_saving=old_account['conditional_pristine_peak_consumption']-results['match-immediate']['conditional_loader_peak'],
              loader_order_primary_files={name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in (
                  'state/analysis/P2_memory_validation_raw/llext.h',
                  'state/analysis/P2_memory_validation_raw/llext_mem.c',
                  'state/analysis/P2_memory_validation_raw/llext_load.c')},
              limit='No measured load/freeRAM/stack/WCET, physical acceptance, gate or upload authority')
target = OUT / 'final_target_verification.json'
assert not target.exists()
target.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({mode: {k: v for k, v in value.items() if k in (
    'compiler_payload', 'conditional_loader_peak', 'conditional_free_span', 'conditional_largest_payload', 'owners')}
    for mode, value in results.items()}, indent=2))
