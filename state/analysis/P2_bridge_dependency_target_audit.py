"""Collect D098 source/ELF evidence from board Linux without attaching to the MCU."""
import json
import os
from pathlib import Path
import re
import sys

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / 'tools'))
import board_tool as board

source, mode = sys.argv[1:]
if not re.fullmatch(r'[0-9a-f]{64}', source) or mode not in ('control', 'candidate'):
    raise SystemExit('Expected source hash and isolated branch')
compile_receipt = json.loads((repo / 'state/analysis/P2_bridge_dependency_raw' /
                            (source[:8] + '_' + mode + '.json')).read_text())
folder = os.environ['SUMO_REMOTE_ROOT'] + '/' + source + '/app'
artifacts = compile_receipt['build_path']
program = r'''
import hashlib,json,pathlib,re,subprocess,sys
root=pathlib.Path(sys.argv[1]); mode=sys.argv[2]; artifacts=pathlib.Path(sys.argv[3])
prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
base='/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
def run(args):
    result=subprocess.run(args,capture_output=True,text=True,timeout=30)
    if result.returncode: raise RuntimeError(str(args)+': '+result.stderr)
    return dict(argv=args,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
files={}
for path in sorted(root.rglob('*')):
    if path.is_file() and 'artifacts' not in path.relative_to(root).parts:
        files[path.relative_to(root).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
records=[]; native=set(); math_helpers=set()
for path in sorted(artifacts.glob('*.elf')):
    nm=run([prefix+'nm','-C',str(path)])
    undefined=run([prefix+'nm','-u',str(path)])
    markers=('app::','recorder::','motors::','__loopHook','qtr_cal::','ui::','power::','line_qtr::','countdown::','fsm::','imu::','opp_sensors::','opp_fusion::','edge::','logframe::','<setup>','<loop>','<main>','<__aeabi_atexit>','candidatePeriod',' setup',' loop',' main',
             '_GLOBAL__sub_I','initVariant','__loopHook','__aeabi_')
    record=dict(path=str(path),bytes=path.stat().st_size,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        nm=[line for line in nm['stdout'].splitlines() if any(k in line for k in markers)],
        sizes=run([prefix+'nm','-S','--size-sort','-C',str(path)]),
        size_sections=run([prefix+'size','-A',str(path)]),
        undefined=undefined,relocations=run([prefix+'readelf','-rW',str(path)]),
        sections=run([prefix+'readelf','-SW',str(path)]))
    # Preserve full retained-method disassembly only once, in the upload-format ELF.
    if path.name.endswith('.ino.elf'):
        assembly=run([prefix+'objdump','-d','-C',str(path)])
        selected=[]; retain=False
        for line in assembly['stdout'].splitlines():
            if line.endswith('>:'): retain=any(k in line for k in markers)
            if retain: selected.append(line)
        record['disassembly']='\n'.join(selected)
        record['init_array']=run([prefix+'readelf','-x','.init_array',str(path)])
        record['nm_all']=nm
    for line in undefined['stdout'].splitlines():
        symbol=line.split()[-1]
        if '__aeabi_' in symbol: math_helpers.add(symbol)
        if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',symbol) and any(
            k in symbol for k in ('gpio','pwm','device','cycle','micros','pinctrl','clock','matrix')):
            native.add(symbol)
    records.append(record)
if len(records)!=3: raise SystemExit('Expected exactly three compiled ELF artifacts')
gdb=[prefix+'gdb','-nx','-nh','-batch',base]
for symbol in sorted(native): gdb+=['-ex','p/x __llext_sym_'+symbol+'.addr']
exports=run(gdb) if native else None
base_nm=run([prefix+'nm','-C',base])
base_names={line.split()[-1] for line in base_nm['stdout'].splitlines() if line.split()}
math_aliases={name:name.removeprefix('__real_') for name in sorted(math_helpers)}
math_symbols={name:'__llext_sym_'+name for name in math_aliases}
math_missing=[name for name,symbol in math_symbols.items() if symbol not in base_names]
math_gdb=[prefix+'gdb','-nx','-nh','-batch',base]
for symbol in sorted(set(math_symbols.values()) & base_names):
    math_gdb+=['-ex','p/x '+symbol+'.addr']
math_exports=run(math_gdb) if len(math_gdb)>5 else None
import struct

def alloc_sections(path):
    data=path.read_bytes()
    if data[:6]!=b'\x7fELF\x01\x01': raise RuntimeError('Expected ELF32 little endian: '+str(path))
    header=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
    offset,entsize,count,names=header[6],header[11],header[12],header[13]
    sections=[struct.unpack_from('<IIIIIIIIII',data,offset+i*entsize) for i in range(count)]
    string=sections[names]; strings=data[string[4]:string[4]+string[5]]
    results=[]
    for section in sections:
        if section[2]&2:
            name=strings[section[0]:].split(b'\0',1)[0].decode()
            payload=b'' if section[1]==8 else data[section[4]:section[4]+section[5]]
            results.append(dict(name=name,type=section[1],flags=section[2],size=section[5],
                                align=section[8],sha256=hashlib.sha256(payload).hexdigest()))
    return results

objects=[]
for path in sorted(artifacts.rglob('*.o')):
    objects.append(dict(path=path.relative_to(artifacts).as_posix(),bytes=path.stat().st_size,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),alloc_sections=alloc_sections(path),
        relocations=run([prefix+'readelf','-rW',str(path)]),
        symbols=run([prefix+'readelf','-sW',str(path)])))
metadata={}
for path in sorted(artifacts.rglob('*')):
    if path.is_file() and (path.suffix=='.d' or path.name in
       ('build.options.json','compile_commands.json','app.ino.cpp','rodata_split.ld')):
        content=path.read_bytes()
        metadata[path.relative_to(artifacts).as_posix()]=dict(sha256=hashlib.sha256(content).hexdigest(),
            bytes=len(content),text=content.decode('utf-8',errors='replace'))
print(json.dumps(dict(source_files=files,objects=objects,metadata=metadata,records=records,native_names=sorted(native),
    native_exports=exports,base_sha256=hashlib.sha256(pathlib.Path(base).read_bytes()).hexdigest(),
    math_aliases=math_aliases,math_symbols=math_symbols,math_missing=math_missing,
    math_exports=math_exports,math_base_symbols=[line for line in base_nm['stdout'].splitlines()
        if '__aeabi_' in line],
    base_static_threads=[l for l in base_nm['stdout'].splitlines() if 'static_thread' in l]),indent=2))
'''
args = ['python3', '-c', program, folder, mode, artifacts]
result = board.remote(board.target(), args, capture=True, timeout=120)
data = dict(source_sha256=source, mode=mode, argv=args, returncode=result.returncode,
            failed_compile_cache=compile_receipt['returncode'] != 0,
            compile_returncode=compile_receipt['returncode'],
            scope='Board Linux file/offline ELF inspection only; no MCU target, pin or upload',
            **json.loads(result.stdout))
path = repo / 'state/analysis/P2_bridge_dependency_raw' / ('target_' + source[:8] + '_' + mode + '.json')
path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
if data['source_files'] != compile_receipt['source_files']:
    raise SystemExit('Post-compile exact source set/hash mismatch; evidence preserved')
print(json.dumps(dict(receipt=str(path.relative_to(repo)), source=source, mode=mode,
                     files=len(data['source_files']), artifacts=len(data['records']),
                     native_imports=len(data['native_names']))))
