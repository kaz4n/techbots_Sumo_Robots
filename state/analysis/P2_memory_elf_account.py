# Decodes fixed D-071 ABI records and ELF section/object census from saved bytes.
# Reports compiler-section sums separately from loader/free-memory evidence.
# Requires ELF32 little-endian ARM and cross-checks each ABI owner symbol size.
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'state/analysis/P2_memory_validation_raw'
TYPES=['Robot','AttemptRecorder','FrameBuffer','StoredFrame','EventBuffer',
       'AttemptSummary','RobotInput','RobotResult']

def string(data,offset):
    return data[offset:data.index(b'\0',offset)].decode()

def account(rate):
    path=OUT/f'candidate_{rate}.elf'; raw=path.read_bytes()
    header=struct.unpack_from('<16sHHIIIIIHHHHHH',raw)
    assert header[0][:6]==b'\x7fELF\x01\x01' and header[1:3]==(1,40)
    offset,entry_size,count,names_index=header[6],header[11],header[12],header[13]
    assert entry_size==40
    sections=[dict(zip(['name_offset','type','flags','addr','offset','size','link',
                        'info','alignment','entry_size'],struct.unpack_from('<10I',raw,offset+i*40)))
              for i in range(count)]
    names=sections[names_index]; name_data=raw[names['offset']:names['offset']+names['size']]
    for section in sections: section['name']=string(name_data,section['name_offset'])
    symbols=[]
    for section in sections:
        if section['type']!=2: continue
        strings=sections[section['link']]; strings=raw[strings['offset']:strings['offset']+strings['size']]
        for position in range(section['offset'],section['offset']+section['size'],16):
            name,value,size,info,other,index=struct.unpack_from('<IIIBBH',raw,position)
            symbols.append(dict(name=string(strings,name),value=value,size=size,
                                bind=info>>4,type=info&15,section_index=index))
    abi_symbol=next(s for s in symbols if s['name']=='_ZN12memory_probe3abiE')
    section=sections[abi_symbol['section_index']]
    abi_offset=section['offset']+abi_symbol['value']
    words=struct.unpack_from('<24I',raw,abi_offset)
    assert words[:2]==(1,96) and words[2]==rate and words[6:8]==(4,4)
    abi=dict(version=words[0],record_bytes=words[1],log_hz=words[2],window_ms=words[3],
             frame_capacity=words[4],event_capacity=words[5],pointer_bytes=words[6],size_t_bytes=words[7],
             sizes=dict(zip(TYPES,words[8:16])),alignments=dict(zip(TYPES,words[16:24])))
    owners=[s for s in symbols if s['name'] in ('_ZN12memory_probe11robot_ownerE',
                                               '_ZN12memory_probe14recorder_ownerE')]
    assert len(owners)==2
    assert {s['size'] for s in owners}=={abi['sizes']['Robot'],abi['sizes']['AttemptRecorder']}
    for owner in owners: owner['section']=sections[owner['section_index']]['name']
    allocated=[s for s in sections if s['flags']&2]
    ram=sum(s['size'] for s in allocated if s['name']!='.llext.rodata.noreloc')
    objects=sorted([s for s in symbols if s['type']==1 and s['size']>=256],key=lambda s:s['size'],reverse=True)
    return dict(rate_hz=rate,elf_sha256=hashlib.sha256(raw).hexdigest(),file_bytes=len(raw),abi=abi,
                owners=owners,large_objects=objects,sections=sections,compiler_ram_sum=ram,
                compiler_difference=262144-ram,
                limitation='Compiler section sum only; not measured free memory or loader acceptance')

rows=[account(rate) for rate in (50,25)]
(OUT/'elf_account.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{k:v for k,v in row.items() if k not in ('sections','large_objects')}
                  for row in rows],indent=2))
