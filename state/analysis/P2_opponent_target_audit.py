"""Collect D076 compiled ELF methods, relocations and native export identities."""
import json
import os
from pathlib import Path
import sys

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / 'tools'))
import board_tool as board

source = board.source_hash(repo / 'build/stage/p2_opp_compile')
folder = os.environ['SUMO_REMOTE_ROOT'] + '/' + source + '/p2_opp_compile/artifacts/bench-default'
program = r'''
import hashlib, json, pathlib, re, subprocess, sys
root = pathlib.Path(sys.argv[1])
prefix = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
base = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
records, needed = [], set()
def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(str(args)+': '+result.stderr)
    return dict(argv=args, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
for path in sorted(root.glob('*.elf')):
    nm = run([prefix+'nm','-C',str(path)])
    undefined = run([prefix+'nm','-u',str(path)])
    disassembly = run([prefix+'objdump','-d','-C',str(path)])
    relocations = run([prefix+'readelf','-rW',str(path)])
    markers = ('opp_sensors::','opponent_probe::','<setup>','<loop>',' setup',' loop',
               '_GLOBAL__sub_I','initVariant','__loopHook')
    selected, retain = [], False
    for line in disassembly['stdout'].splitlines():
        if line.endswith('>:'):
            retain = any(m in line for m in markers)
        if retain:
            selected.append(line)
    for line in undefined['stdout'].splitlines():
        symbol = line.split()[-1]
        if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',symbol):
            needed.add(symbol)
    records.append(dict(path=str(path),bytes=path.stat().st_size,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        nm=[line for line in nm['stdout'].splitlines() if any(m in line for m in markers)],
        nm_all=nm,undefined=undefined,relocations=relocations,
        sections=run([prefix+'readelf','-SW',str(path)]),
        init_array=run([prefix+'readelf','-x','.init_array',str(path)]),
        disassembly=chr(10).join(selected)))
if len(records) != 3:
    raise SystemExit('Expected three ELF artifacts')
native = sorted(s for s in needed if any(k in s for k in ('gpio','device','micros','cycle')))
gdb = [prefix+'gdb','-nx','-nh','-batch',base]
for symbol in native:
    gdb += ['-ex','p/x __llext_sym_'+symbol+'.addr']
exports = run(gdb) if native else None
base_symbols = run([prefix+'nm','-C',base])
static_threads = [line for line in base_symbols['stdout'].splitlines()
                  if any(k in line for k in ('static_thread','thread_data','initVariant','__loopHook'))]
print(json.dumps(dict(records=records,native_names=native,native_exports=exports,
    base_static_thread_symbols=static_threads),indent=2))
'''
result = board.remote(board.target(), ['python3','-c',program,folder], capture=True, timeout=60)
output = repo / 'state/analysis/P2_opponent_raw'
output.mkdir(exist_ok=True)
data = dict(source_sha256=source,scope='Linux ELF files only; no MCU target/debug/run',
            returncode=result.returncode, **json.loads(result.stdout))
(output/'target_elf.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(source=source,artifacts=len(data['records']),native_names=data['native_names'])))
