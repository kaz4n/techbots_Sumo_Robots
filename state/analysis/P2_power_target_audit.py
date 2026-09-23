"""Collect D078 source/ELF evidence from board Linux without attaching to the MCU."""
import json
import os
from pathlib import Path
import re
import sys

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / 'tools'))
import board_tool as board

source, mode = sys.argv[1:]
if not re.fullmatch(r'[0-9a-f]{64}', source) or mode not in ('bench-default', 'match-immediate'):
    raise SystemExit('Expected exact source SHA256 and supported artifact mode')
folder = os.environ['SUMO_REMOTE_ROOT'] + '/' + source + '/p2_power_compile'
program = r'''
import hashlib,json,pathlib,re,subprocess,sys
root=pathlib.Path(sys.argv[1]); mode=sys.argv[2]
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
records=[]; native=set()
for path in sorted((root/'artifacts'/mode).glob('*.elf')):
    nm=run([prefix+'nm','-C',str(path)])
    undefined=run([prefix+'nm','-u',str(path)])
    markers=('power::','power_probe::','<setup>','<loop>',' setup',' loop',
             '_GLOBAL__sub_I','initVariant','__loopHook')
    record=dict(path=str(path),bytes=path.stat().st_size,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        nm=[line for line in nm['stdout'].splitlines() if any(k in line for k in markers)],
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
        if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',symbol) and any(
            k in symbol for k in ('gpio','pwm','device','cycle','micros','pinctrl','clock')):
            native.add(symbol)
    records.append(record)
if len(records)!=3: raise SystemExit('Expected exactly three compiled ELF artifacts')
gdb=[prefix+'gdb','-nx','-nh','-batch',base]
for symbol in sorted(native): gdb+=['-ex','p/x __llext_sym_'+symbol+'.addr']
exports=run(gdb) if native else None
base_nm=run([prefix+'nm','-C',base])
print(json.dumps(dict(source_files=files,records=records,native_names=sorted(native),
    native_exports=exports,base_sha256=hashlib.sha256(pathlib.Path(base).read_bytes()).hexdigest(),
    base_static_threads=[l for l in base_nm['stdout'].splitlines() if 'static_thread' in l]),indent=2))
'''
args = ['python3', '-c', program, folder, mode]
result = board.remote(board.target(), args, capture=True, timeout=60)
data = dict(source_sha256=source, mode=mode, argv=args, returncode=result.returncode,
            scope='Board Linux file/offline ELF inspection only; no MCU target, pin or upload',
            **json.loads(result.stdout))
path = repo / 'state/analysis/P2_power_raw' / ('target_' + source[:8] + '_' + mode + '.json')
path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(receipt=str(path.relative_to(repo)), source=source, mode=mode,
                     files=len(data['source_files']), artifacts=len(data['records']),
                     native_imports=len(data['native_names']))))
