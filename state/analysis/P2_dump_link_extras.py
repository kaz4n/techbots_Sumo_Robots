"""Capture final D090 main/constructor and libm binding evidence, offline on Linux."""
import json
import os
from pathlib import Path
import sys
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'tools'))
import board_tool as board
source = 'b8bb9366458c2472d856e81ea4678716ff16d00a3b3d16b51d008e1624818307'
folder = os.environ['SUMO_REMOTE_ROOT'] + '/' + source + '/p2_dump_compile/artifacts/bench-default'
program = r'''
import json,pathlib,subprocess,sys
root=pathlib.Path(sys.argv[1])
prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
base='/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
def run(argv):
    result=subprocess.run(argv,text=True,capture_output=True,timeout=30)
    if result.returncode: raise RuntimeError(result.stderr)
    return dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
elf=next(p for p in root.glob('*.elf') if p.name.endswith('.ino.elf'))
assembly=run([prefix+'objdump','-d','-C',str(elf)])
selected=[];retain=False
for line in assembly['stdout'].splitlines():
    if line.endswith('>:'): retain=('<main>:' in line or ('ZephyrSerialBuffer<' in line and '::ZephyrSerialBuffer()' in line))
    if retain: selected.append(line)
assembly['stdout']='\n'.join(selected)
bindings=run([prefix+'gdb','-nx','-nh','-batch',base,
    '-ex','p/x __llext_sym___real_fmod.addr','-ex','p/x __llext_sym___real_sqrt.addr'])
print(json.dumps(dict(assembly=assembly,bindings=bindings),indent=2))
'''
args = ['python3', '-c', program, folder]
result = board.remote(board.target(), args, capture=True, timeout=60)
path = root / 'state/analysis/P2_dump_raw/link_bodies.json'
assert not path.exists()
path.write_text(json.dumps(dict(source_sha256=source, argv=args, returncode=result.returncode,
                **json.loads(result.stdout)), indent=2) + '\n', encoding='utf-8', newline='\n')
print(path.relative_to(root))
