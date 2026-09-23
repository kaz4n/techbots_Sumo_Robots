"""Offline D106 target byte, relocation, startup and ordered-allocation audit."""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P2_pin_table_raw'
OUT = Path(__file__).resolve().parent
def sha(data): return hashlib.sha256(data).hexdigest()
spec = importlib.util.spec_from_file_location('reviewed_elf_decoder',
    ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
baseline_path = ROOT / 'state/analysis/P2_calibration_delivery_raw/target_c05916c6_bench-default/app.ino.elf'
baseline = module.Elf(baseline_path)
assert sha(baseline.raw) == 'd953266f6c160f237685db17fbec257c6bb346212e4f3ff0788f9e7c061d553b'

def bytes_for(elf, symbol):
    section = elf.sections[symbol['section_index']]
    # ET_REL st_value is section-relative even when sh_addr has a layout hint.
    offset = symbol['value']
    return elf.section_bytes(section)[offset:offset+symbol['size']]

def table_proof(elf):
    output = []
    for symbol in elf.symbols:
        if symbol['name'] != '_ZN6zephyr7arduinoL12arduino_pinsE': continue
        section = elf.sections[symbol['section_index']]
        offset = symbol['value']
        rels = [dict(offset=r['offset']-offset, type=r['type'], name=r['name'],
                     symbol_section=r['symbol_section'], symbol_value=r['symbol_value'])
                for r in elf.relocations if r['section']==symbol['section']
                and offset <= r['offset'] < offset+symbol['size']]
        assert symbol['size'] == 560 and len(rels) == 70
        assert all(r['offset']==i*8 and r['type']==2 and r['symbol_section']==''
                   and r['name'].startswith('__device_dts_ord_') for i,r in enumerate(rels))
        output.append(dict(symbol=symbol, bytes_sha256=sha(bytes_for(elf,symbol)),
                           relocations=rels, relocations_sha256=sha(json.dumps(rels,sort_keys=True).encode())))
    return output

def initializer_signature(elf):
    symbol = next(s for s in elf.symbols if s['name']=='_GLOBAL__sub_I_setup')
    section = elf.sections[symbol['section_index']]
    offset = symbol['value'] & ~1
    data = bytearray(elf.functions()[symbol['name']])
    rels = []
    for r in elf.relocations:
        if r['section'] != symbol['section'] or not offset <= r['offset'] < offset+symbol['size']: continue
        local = r['offset']-offset
        rels.append(dict(offset=local,type=r['type'],name=r['name'],symbol_section=r['symbol_section']))
        data[local:local+4] = bytes(4)
    return dict(size=symbol['size'], instructions_without_relocation_words=sha(data), references=rels)

old_tables = table_proof(baseline)
assert len(old_tables)==4
assert len({r['bytes_sha256'] for r in old_tables})==1
assert len({r['relocations_sha256'] for r in old_tables})==1
old_signature = initializer_signature(baseline)
old_imports = baseline.account()['undefined']
old_used_imports = sorted({r['name'] for r in baseline.relocations if r['symbol_section']==''})
name = sys.argv[1]
assert name.startswith('target_') and '/' not in name and '\\' not in name
folder = RAW / name
audit = json.loads((folder/'audit.json').read_text())
command=json.loads((folder/'build_receipt/command.json').read_text())
verified=json.loads((folder/'build_receipt/verified.json').read_text())
match='_match-' in name
immediate=name.endswith('-immediate')
import_baseline_sha256=sha(baseline.raw)
if match:
    # D105 had no MATCH target; compare actual import usage with reviewed D103 MATCH.
    imported=module.Elf(ROOT/'state/analysis/P2_service_reset_raw/target_1fbd7238_match-immediate/app.ino.elf')
    import_baseline_sha256=sha(imported.raw)
    assert import_baseline_sha256=='e3d539a21a54c481ba8e8a6f91ff3551082f4f2313deaf53c12114b7c3c88bc3'
    assert imported.account()['undefined']==old_imports
    old_used_imports=sorted({r['name'] for r in imported.relocations if r['symbol_section']==''})
assert command[command.index('--fqbn')+1]==('arduino:zephyr:unoq:wait_linux_boot=no' if immediate else 'arduino:zephyr:unoq')
for language in ('c','cpp'):
    assert f'compiler.{language}.extra_flags=-DMATCH={int(match)} -DMOTORS_ALLOWED={int(match)}' in command
assert verified['source_sha256']==audit['source_sha256']
assert verified['compiler_returncode']==0 and verified['precompile_checks'] and not verified['used_libraries']
frozen = RAW / ('target_sources_'+audit['source_sha256'][:8])
manifest = json.loads((frozen/'manifest.json').read_text())
assert manifest['source_files']==audit['source_files']
aggregate = hashlib.sha256()
for path,digest in sorted(audit['source_files'].items()):
    data = (frozen/path).read_bytes(); assert sha(data)==digest, path
    aggregate.update(path.encode()); aggregate.update(b'\0'); aggregate.update(data)
assert aggregate.hexdigest()==audit['source_sha256']==manifest['source_sha256']
records=[]
for row in audit['records']:
    path=folder/Path(row['path']).name
    assert sha(path.read_bytes())==row['sha256']
    elf=module.Elf(path); account=elf.account()
    if path.name=='app.ino.elf':
        assert (0x08100010+elf.section_header_offset)%4==0
        for section in elf.sections:
            if section['name'] in ('.llext.rodata.noreloc','.symtab','.strtab'):
                assert (0x08100010+section['offset'])%max(1,section['alignment'])==0
    assert len(account['init'])==1 and account['init'][0]['name']=='_GLOBAL__sub_I_setup'
    assert not account['fini']
    assert elf.functions()['_Z10__loopHookv']==bytes.fromhex('7047')
    assert next(s for s in elf.sections if s['name']=='.static_thread_data_area')['size']==0
    tables=table_proof(elf)
    assert len(tables)==1
    assert tables[0]['bytes_sha256']==old_tables[0]['bytes_sha256']
    assert tables[0]['relocations']==old_tables[0]['relocations']
    table=tables[0]['symbol']
    count=next(s for s in elf.symbols if s['name']=='_ZN11native_pins5COUNTE')
    pointer=next(s for s in elf.symbols if s['name']=='_ZN11native_pins5TABLEE')
    assert count['type']==pointer['type']==1 and count['bind']==pointer['bind']==1
    assert count['size']==pointer['size']==4
    assert not elf.sections[count['section_index']]['flags'] & 1
    assert not elf.sections[pointer['section_index']]['flags'] & 1
    actual_count=struct.unpack('<I',bytes_for(elf,count))[0]
    assert actual_count==70 and actual_count*8==table['size']
    pointer_offset=pointer['value']
    links=[r for r in elf.relocations if r['section']==pointer['section'] and r['offset']==pointer_offset]
    assert len(links)==1 and links[0]['type']==2
    link=links[0]; addend=struct.unpack('<I',bytes_for(elf,pointer))[0]
    assert link['symbol_section']==table['section']
    assert link['symbol_value']+addend==table['value'], (link,addend,table)
    current_imports=account['undefined']
    current_used_imports=sorted({r['name'] for r in elf.relocations if r['symbol_section']==''})
    assert current_imports==old_imports
    assert current_used_imports==old_used_imports
    init_signature=initializer_signature(elf)
    # Intermediate linker layouts may have extra rodata sections; final proof is exact.
    if path.name=='app.ino.elf': assert init_signature==old_signature
    metadata=account['metadata_chunks']
    regions={r['name']:r['retained_chunk'] for r in account['copied_regions']}
    order=['.text','.data','.rodata','.bss','.exported_sym','.preinit_array','.init_array','.fini_array']
    extra=[s for s in regions if s not in order]
    assert not extra or path.name=='app.ino_temp.elf'
    allocations=[('extension',metadata['extension']),('section_map',metadata['section_map'])]
    allocations += [(s,regions[s]) for s in order if s in regions]+[(s,regions[s]) for s in extra]
    allocations += [('symbols',metadata['global_symbols']),('export_copy',metadata['export_copy'])]
    used=metadata['initial_bookkeeping']; ledger=[]
    for purpose,chunk in allocations:
        ledger.append(dict(purpose=purpose,chunk=chunk,available_before=262144-used,fits=chunk<=262144-used))
        used+=chunk
    assert used==account['conditional_pristine_peak_consumption']
    records.append(dict(file=path.name,sha256=row['sha256'],bytes=len(elf.raw),
        compiler_payload=account['compiler_payload'],conditional_peak=used,free_span=262144-used,
        largest_free_payload=262144-used-4,allocations=ledger,table=tables[0],
        count=dict(symbol=count,value=actual_count),pointer=dict(symbol=pointer,relocation=link,addend=addend),
        imports_unchanged=True,used_imports_unchanged=True,initializer=init_signature))
package=folder/'app.ino.elf-zsk.bin'
package_row=next(r for r in audit['bundles'] if r['name']==package.name)
assert sha(package.read_bytes())==package_row['sha256']
final=next(r for r in records if r['file']=='app.ino.elf')
fits=all(r['fits'] for r in final['allocations'])
output=dict(verdict='PASS_EXACT_TABLE_AND_CONDITIONAL_FIT' if fits else 'BLOCKER_TARGET_FIT',
    source_sha256=audit['source_sha256'],source_files=len(audit['source_files']),objects=len(audit['objects']),
    artifacts=records,zsk_sha256=package_row['sha256'],baseline_elf_sha256=sha(baseline.raw),
    actual_import_baseline_elf_sha256=import_baseline_sha256,
    profile=dict(match=match,motors_allowed=match,startup='immediate' if immediate else 'default'),
    limitation='Conditional pristine loader model only; no upload, actual free RAM, WCET or physical gate')
(OUT/(name+'.json')).write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(dict(verdict=output['verdict'],source_sha256=output['source_sha256'],
    elf_sha256=final['sha256'],compiler_payload=final['compiler_payload'],conditional_peak=final['conditional_peak'],
    free_span=final['free_span'],largest_free_payload=final['largest_free_payload']),indent=2))
