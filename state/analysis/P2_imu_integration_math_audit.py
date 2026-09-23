"""Collect additional retained Robot math bindings from board Linux files only."""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'tools'))
import board_tool as board

raw = root / 'state/analysis/P2_imu_integration_raw'
target = json.loads((raw / 'target_f3bc1f7f_bench-default.json').read_text())
elf = next(r['path'] for r in target['records'] if r['path'].endswith('.ino.elf'))
program = r'''
import hashlib,json,pathlib,subprocess,sys
prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
base='/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
elf=sys.argv[1]
def run(args):
    result=subprocess.run(args,capture_output=True,text=True,timeout=30)
    if result.returncode: raise RuntimeError(result.stderr)
    return dict(argv=args,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
names=('fmod','sqrt')
gdb=[prefix+'gdb','-nx','-nh','-batch',base]
for name in names: gdb+=['-ex','p/x __llext_sym___real_'+name+'.addr']
nm=run([prefix+'nm','-C',base])
nm['stdout']='\n'.join(l for l in nm['stdout'].splitlines() if l.split()[-1] in names or any('__llext_sym___real_'+n in l for n in names))
assembly=run([prefix+'objdump','-d','-C',elf])
selected=[]; keep=False
for line in assembly['stdout'].splitlines():
    if line.endswith('>:'): keep=any('<'+n+'>' in line for n in names)
    if keep: selected.append(line)
assembly['stdout']='\n'.join(selected)
print(json.dumps(dict(names=names,base_sha256=hashlib.sha256(pathlib.Path(base).read_bytes()).hexdigest(),
    elf_sha256=hashlib.sha256(pathlib.Path(elf).read_bytes()).hexdigest(),base_nm=nm,
    exports=run(gdb),wrappers=assembly),indent=2))
'''
argv = ['python3', '-c', program, elf]
result = board.remote(board.target(), argv, capture=True, timeout=60)
data = dict(argv=argv, returncode=result.returncode,
            scope='Read-only board Linux files and offline ELF; no MCU action',
            **json.loads(result.stdout))
assert data['base_sha256'] == target['base_sha256']
assert data['elf_sha256'] == next(r['sha256'] for r in target['records'] if r['path'] == elf)
(raw / 'target_additional_math.json').write_text(json.dumps(data, indent=2) + '\n')
print(json.dumps(dict(returncode=result.returncode, names=data['names'],
                     receipt='target_additional_math.json')))
