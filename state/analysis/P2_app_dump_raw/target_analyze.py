# Decode D101 frozen ELF evidence and apply the pinned conditional loader model.
# Keep modeled allocation failure separate from compiler fit and runtime evidence.
# Reuses the D098 ELF decoder and records every source/artifact comparison.
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
REVIEW = ROOT / 'state/reviews/P2_bridge_dependency_review_raw'
sys.path.insert(0, str(REVIEW))
from elf_review import Elf


def load_function(filename, name):
    tree = ast.parse((REVIEW / filename).read_text())
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(nodes) == 1
    scope = dict(re=re, struct=struct)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'), scope)
    return scope[name]


prior_function = load_function('verify_elfs.py', 'function')
relocations = load_function('compare_objects.py', 'relocations')
BASE = ROOT / 'state/analysis/P2_app_acceptance_raw/bench-default'
baseline = json.loads((BASE / 'audit.json').read_text())
baseline_elf = Elf(BASE / 'app.ino.elf')


def function(elf, name):
    result = prior_function(elf, name)
    payload = bytes.fromhex(result['bytes_hex'])
    resolved = []
    for relocation in result['relocations']:
        if relocation['type'] == 2 and not relocation['name'] and relocation['section'] == '.bss':
            addend = struct.unpack_from('<I', payload, relocation['offset'])[0]
            # Final ET_REL symbols are section-relative, even with a nonzero sh_addr.
            targets = [s['name'] for s in elf.symbols if s['type'] == 1 and
                       s['section'] == '.bss' and s['value'] == addend]
            resolved.append(dict(offset=relocation['offset'], section_addend=addend, targets=targets))
    result['bss_targets'] = resolved
    return result


def compare_objects(audit):
    before = {o['path']: o for o in baseline['objects']}
    after = {o['path']: o for o in audit['objects']}
    changes = []
    count = 0
    for name in sorted(before.keys() & after.keys()):
        old = {s['name']: s for s in before[name]['alloc_sections']}
        new = {s['name']: s for s in after[name]['alloc_sections']}
        old_r = relocations(before[name]['relocations']['stdout'])
        new_r = relocations(after[name]['relocations']['stdout'])
        changed = [s for s in sorted(old.keys() & new.keys())
                   if old[s] != new[s] or old_r.get(s, []) != new_r.get(s, [])]
        count += len(old.keys() & new.keys())
        if changed or old.keys() != new.keys():
            changes.append(dict(path=name, changed=changed, added=sorted(new.keys()-old.keys()),
                                removed=sorted(old.keys()-new.keys())))
    assert not before.keys() - after.keys()
    for name in ('sketch/src/hal/dump_uart_unoq.cpp.o', 'sketch/src/hal/recorder_csv.cpp.o'):
        assert name in after and not any(c['path'] == name for c in changes)
    return dict(objects=len(after), common_alloc_sections=count,
                added_objects=sorted(after.keys()-before.keys()), changes=changes,
                native_uart_and_csv_alloc_sections_unchanged=True)


def loader(elf):
    account = elf.account()
    metadata = account['metadata_chunks']
    regions = sum(r['retained_chunk'] for r in account['copied_regions'])
    before_symbols = regions + metadata['extension'] + metadata['section_map'] + metadata['initial_bookkeeping']
    span = 262144 - before_symbols
    symbol_bytes = account['global_func_object_count'] * 8
    aligned_peeks = []
    for section in elf.sections:
        if section['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab', '.shstrtab'):
            assert (0x08100010 + section['offset']) % section['alignment'] == 0
            aligned_peeks.append(dict(name=section['name'], offset=section['offset'],
                                      alignment=section['alignment'], bytes=section['size']))
    assert (0x08100010 + elf.section_header_offset) % 4 == 0
    return dict(account=account, aligned_peeks=aligned_peeks,
        copied_region_chunks=regions, before_temporary_symbols=before_symbols,
        before_symbols_free_span=span, before_symbols_largest_payload=max(0, span-4),
        temporary_symbols_request=symbol_bytes, temporary_symbols_chunk=metadata['global_symbols'],
        temporary_symbols_fit=metadata['global_symbols'] <= span,
        temporary_symbols_chunk_deficit=max(0, metadata['global_symbols']-span),
        complete_peak_deficit=max(0, account['conditional_pristine_peak_consumption']-262144),
        conditional_largest_after_peak=(account['conditional_largest_payload']
            if account['conditional_pristine_peak_consumption'] <= 262144 else None),
        interpretation='Pinned pristine-pool/persistent-peek model only; no load/freeRAM/WCET measured')


def metadata(audit):
    commands = json.loads(audit['metadata']['compile_commands.json']['text'])
    value = '1' if audit['mode'] == 'match-immediate' else '0'
    for command in commands:
        args = command['arguments']
        assert '-DMATCH=' + value in args and '-DMOTORS_ALLOWED=' + value in args
        if not command['file'].endswith('/tls-syms.S'):
            assert '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0' in args
        assert not any('/Arduino/libraries/' in arg for arg in args)
    for name, row in audit['metadata'].items():
        payload = row['text'].encode()
        assert len(payload) == row['bytes'] and hashlib.sha256(payload).hexdigest() == row['sha256']
        if name.endswith('.d'):
            assert not any(token in row['text'] for token in ('Arduino_RouterBridge', 'Arduino_RPClite',
                'MsgPack', 'DebugLog', 'ArxTypeTraits', 'ArxContainer'))
    return dict(commands=len(commands), metadata=len(audit['metadata']),
                dependencies=sum(name.endswith('.d') for name in audit['metadata']))


def audit_folder(folder):
    audit = json.loads((folder / 'audit.json').read_text())
    assert all(v for k, v in audit['checks'].items() if k != 'current_source_at_collection')
    frozen = OUT / ('target_sources_' + audit['source_sha256'][:8])
    manifest = json.loads((frozen / 'manifest.json').read_text())
    digest = hashlib.sha256()
    for name, expected in sorted(manifest['source_files'].items()):
        data = (frozen / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected == audit['source_files'][name]
        digest.update(name.encode()+b'\0'); digest.update(data)
    assert digest.hexdigest() == audit['source_sha256'] and len(audit['source_files']) == 85
    verified = []
    for record in audit['records']:
        path = folder / Path(record['path']).name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
        elf = Elf(path)
        imported = sorted({s['name'] for s in elf.symbols if s['section_index'] == 0 and s['name']})
        assert imported == sorted(line.split()[-1] for line in record['undefined']['stdout'].splitlines())
        old = sorted(line.split()[-1] for line in baseline['records'][0]['undefined']['stdout'].splitlines())
        assert imported == old
        verified.append(dict(name=path.name, sha256=record['sha256'], imports=len(imported)))
    for key in ('base_sha256', 'native_names', 'math_missing', 'math_symbols', 'math_aliases', 'base_static_threads'):
        assert audit[key] == baseline[key], key
    for key in ('native_exports', 'math_exports'):
        assert audit[key]['returncode'] == 0 and audit[key]['stdout'] == baseline[key]['stdout']
    elf = Elf(folder / 'app.ino.elf')
    startup = {name: function(elf, name) for name in ('main', 'setup', 'loop', 'initVariant',
               '_Z10__loopHookv', '_Z20start_static_threadsv', '_GLOBAL__sub_I_setup', 'micros')}
    for name in ('main', 'loop', 'initVariant', '_Z10__loopHookv', '_Z20start_static_threadsv', 'micros'):
        for key in ('normalized_bytes_hex', 'relocations', 'bss_targets'):
            assert startup[name][key] == function(baseline_elf, name)[key], (name, key)
    assert startup['_Z10__loopHookv']['symbol']['bind'] == 1
    assert startup['_Z10__loopHookv']['bytes_hex'] == '7047'
    assert any('_ZN12_GLOBAL__N_17runtimeE' in row['targets'] for row in startup['setup']['bss_targets'])
    assert any('_ZN12_GLOBAL__N_17runtimeE' in row['targets'] for row in startup['loop']['bss_targets'])
    names = {s['name']: s for s in elf.symbols if s['section_index'] and s['name']}
    required = ['_ZN3app7Runtime14initializeDumpEv', '_ZN3app7Runtime11serviceDumpEv',
        '_ZNK3app7Runtime16dumpReceiptValidEv', '_ZNK3app7Runtime16dumpReadyContextEj',
        '_ZN8recorder4dump8Transfer5abortEv',
        '_ZN8recorder4dump8Transfer4stepERKNS0_7ContextERKN3fsm11RobotResultERKNS_15AttemptRecorderE',
        '_ZN8recorder4dump12UnoQDumpPort5beginERKNS0_10SetupGrantE',
        '_ZN8recorder4dump12UnoQDumpPort5readyEv', '_ZN8recorder4dump12UnoQDumpPort7advanceEPKcj',
        '_ZN8recorder4dump12UnoQDumpPort5abortEv', '_ZN8recorder3csv13summaryHeaderEPcj',
        '_ZN8recorder3csv11frameHeaderEPcj', '_ZN8recorder3csv11eventHeaderEPcj',
        '_ZN3app12unoQDumpPortERN8recorder4dump12UnoQDumpPortE']
    assert all(name in names for name in required)
    assert not any(any(token in name for token in ('Bridge', 'ZephyrSerial', 'msgpack', 'RPClite')) for name in names)
    functions = {name: function(elf, name) for name in required}
    owners = {name: names[name]['size'] for name in ('_ZN12_GLOBAL__N_17runtimeE',
              '_ZN12_GLOBAL__N_17sourcesE', '_ZN12_GLOBAL__N_19dump_portE')}
    memory = loader(elf)
    assert len(memory['account']['init']) == 1 and not memory['account']['fini']
    assert memory['account']['init'][0]['name'] == '_GLOBAL__sub_I_setup'
    assert 'main' in [r['name'] for r in elf.relocations if r['section'] == '.exported_sym']
    return dict(source_sha256=audit['source_sha256'], mode=audit['mode'], files=85,
                current_source_at_collection=audit['checks']['current_source_at_collection'],
                verified_elfs=verified, objects=compare_objects(audit), startup=startup,
                metadata=metadata(audit),
                required_retained_functions=functions, owners=owners, memory=memory,
                native_exports=len(audit['native_names']), aeabi_exports=len(audit['math_symbols']))


sources = json.loads((ROOT / 'state/analysis/P2_memory_validation_raw/source_receipt.json').read_text())
for source in sources:
    assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256']
results = {folder.name: audit_folder(folder) for folder in sorted(OUT.glob('target_*'))
           if folder.is_dir() and (folder / 'audit.json').exists()}
report = dict(scope='Frozen source/offline ELF audit; modeled loader blocker is not an actual load failure',
              pinned_source_receipts=sources, builds=results)
(OUT / 'target_summary.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({name: dict(source=r['source_sha256'], payload=r['memory']['account']['compiler_payload'],
      peak=r['memory']['account']['conditional_pristine_peak_consumption'],
      deficit=r['memory']['complete_peak_deficit'], owners=r['owners']) for name, r in results.items()}, indent=2))
