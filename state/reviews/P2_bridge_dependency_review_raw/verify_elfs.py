"""Validate actual downloaded D098 ELF bytes, retention and conditional loader math."""
from pathlib import Path
import hashlib
import json
import re
import struct
from elf_review import Elf

ROOT=Path(__file__).resolve().parents[3]
RAW=ROOT/'state/analysis/P2_bridge_dependency_raw'
OUT=Path(__file__).resolve().parent

verified=[]
final={}
accounts={}
for branch in ('control','candidate'):
    receipt=json.loads((RAW/f'{branch}_elf_receipt.json').read_text())
    audit=json.loads((RAW/f'target_570ef35f_{branch}.json').read_text())
    assert receipt['returncode']==0 and len(receipt['files'])==3
    records={Path(x['path']).name:x for x in audit['records']}
    for row in receipt['files']:
        path=ROOT/row['local_path']; payload=path.read_bytes()
        digest=hashlib.sha256(payload).hexdigest()
        assert digest==row['sha256']==records[path.name]['sha256']
        assert len(payload)==row['bytes']==records[path.name]['bytes']
        elf=Elf(path)
        undefined=sorted({s['name'] for s in elf.symbols if s['section_index']==0 and s['name']})
        recorded=sorted(line.split()[-1] for line in records[path.name]['undefined']['stdout'].splitlines())
        assert undefined==recorded
        verified.append(dict(branch=branch,path=row['local_path'],sha256=digest,
                             bytes=len(payload),imports=len(undefined)))
        if path.name=='app.ino.elf':
            final[branch]=elf;accounts[branch]=elf.account()

candidate=final['candidate'];control=final['control']
assert accounts['control']['compiler_payload']==275760
assert accounts['candidate']['compiler_payload']==248308
assert len(accounts['control']['init'])==12 and len(accounts['candidate']['init'])==1
assert len(accounts['control']['fini'])==10 and not accounts['candidate']['fini']
assert accounts['candidate']['init'][0]['name']=='_GLOBAL__sub_I_setup'
assert all(not any(x in s['name'] for x in ('Bridge','msgpack','Rpc','RPC','ZephyrSerial')) for s in candidate.symbols)
assert not any(s['name'] in ('Serial','Serial1','Serial2','Serial3','Monitor') for s in candidate.symbols)

def function(elf,name):
    symbol=next(s for s in elf.symbols if s['name']==name)
    at=symbol['value']&~1
    rels=[dict(offset=r['offset']-at,type=r['type'],name=r['name'],section=r['symbol_section'])
          for r in elf.relocations if r['section']==symbol['section'] and at<=r['offset']<at+symbol['size']]
    payload=bytearray(elf.functions()[name])
    normalized=bytearray(payload)
    resolved=[]
    for r in rels:
        if r['type']==2 and not r['name'] and r['section']=='.bss':
            addend=struct.unpack_from('<I',payload,r['offset'])[0]
            section=next(s for s in elf.sections if s['name']=='.bss')
            matches=[s['name'] for s in elf.symbols if s['type']==1 and s['section']=='.bss'
                     and s['value']-section['address']==addend]
            resolved.append(dict(offset=r['offset'],targets=matches))
            normalized[r['offset']:r['offset']+4]=b'\0'*4
    return dict(symbol=symbol,bytes_hex=payload.hex(),normalized_bytes_hex=normalized.hex(),
                relocations=rels,bss_targets=resolved)

startup={name:function(candidate,name) for name in ('main','setup','loop','initVariant',
    '_Z10__loopHookv','_Z20start_static_threadsv','_GLOBAL__sub_I_setup')}
for name in ('main','setup','loop','initVariant','_Z10__loopHookv','_Z20start_static_threadsv'):
    assert startup[name]['normalized_bytes_hex']==function(control,name)['normalized_bytes_hex'],name
    assert startup[name]['relocations']==function(control,name)['relocations'],name
    assert startup[name]['bss_targets']==function(control,name)['bss_targets'],name
assert startup['_Z10__loopHookv']['symbol']['bind']==1
assert startup['_Z10__loopHookv']['bytes_hex']=='7047'
assert [r['name'] for r in startup['main']['relocations']]==[
    'initVariant','_Z20start_static_threadsv','setup','loop','_Z10__loopHookv']
exports=[r['name'] for r in candidate.relocations if r['section']=='.exported_sym']
assert 'main' in exports
owners={name:next(s['size'] for s in candidate.symbols if s['name']==name)
        for name in ('_ZN12_GLOBAL__N_17runtimeE','_ZN12_GLOBAL__N_17sourcesE')}
assert owners=={'_ZN12_GLOBAL__N_17runtimeE':168888,'_ZN12_GLOBAL__N_17sourcesE':848}
for name,size in owners.items():
    assert next(s['size'] for s in control.symbols if s['name']==name)==size

project=re.compile(r'^_ZNK?(?:3app|3imu|5power|6motors|8line_qtr|11opp_sensors|2ui|8recorder|3fsm|4edge|9countdown|10opp_fusion|8governor|6motion|7openers|5stall|8logframe|7qtr_cal)')
project_a={s['name'] for s in control.symbols if s['type']==2 and project.match(s['name'])}
project_b={s['name'] for s in candidate.symbols if s['type']==2 and project.match(s['name'])}
assert project_a==project_b

flash_base=0x08100010
assert (flash_base+candidate.section_header_offset)%4==0
peek_names=('.llext.rodata.noreloc','.symtab','.strtab','.shstrtab')
peeks=[]
for s in candidate.sections:
    if s['name'] in peek_names:
        assert (flash_base+s['offset'])%s['alignment']==0
        peeks.append(dict(name=s['name'],size=s['size'],offset=s['offset'],alignment=s['alignment']))
result=dict(scope='Independent downloaded-ELF decoding; loader arithmetic is conditional, not measured',
    verified_elfs=verified,accounts=accounts,startup=startup,
    unchanged_retained_project_functions=len(project_a),owners=owners,
    hypothetical_flash_base=hex(flash_base),aligned_peek_sections=peeks,
    saving=accounts['control']['compiler_payload']-accounts['candidate']['compiler_payload'])
result['reviewer_harness_correction']='Initial final-linked byte equality failed at setup runtime .bss addend 8 versus 0, as expected after BSS reordering. Comparison now resolves both relocation words to the same runtime object and normalizes only those words; original-object bytes/relocations were already identical. No production change.'
(OUT/'elf_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(verified_elfs=len(verified),retained_project_functions=len(project_a),
    bytes_saved=result['saving'],candidate_payload=accounts['candidate']['compiler_payload'],
    conditional_peak=accounts['candidate']['conditional_pristine_peak_consumption'],
    conditional_largest_payload=accounts['candidate']['conditional_largest_payload']),indent=2))
