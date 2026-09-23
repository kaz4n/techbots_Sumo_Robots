# Captures Linux-side D-071 build artifacts and target ELF inspection output.
# Reads files only; never uploads, resets, loads or communicates with the MCU.
# Exact command/status/hash receipts permit independent reconstruction.
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import board_tool as b
OUT=ROOT/'state/analysis/P2_memory_validation_raw'
rate=int(sys.argv[1])
if rate not in (25,50): raise SystemExit('invalid rate')
os.environ.update(SUMO_TRANSPORT='adb',SUMO_ADB_EXECUTABLE=str(Path.home()/'AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'))
compiled=json.loads((OUT/f'compile_{rate}{"_retry1" if rate==50 else ""}.json').read_text())
args=compiled['remote_commands'][-1]['argv']
remote_folder=args[args.index('--output-dir')+1]
if rate==50:
    inventory=json.loads(json.loads((OUT/'cache_50_inventory.json').read_text())['stdout'])
    remote_folder=str(Path(inventory[0]['options_path']).parent).replace('\\','/')
elf=remote_folder+'/p2_recorder_memory.ino.elf'
prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
report=dict(rate_hz=rate,utc=datetime.now(timezone.utc).isoformat(),remote_elf=elf,
            compile_exit_status=compiled['exit_status'],checks=[])
receipt=OUT/f'elf_{rate}_receipt.json'
if receipt.exists(): raise SystemExit('Refusing to overwrite ELF receipt')
commands=[('sections',[prefix+'readelf','-hSW',elf]),
          ('symbols',[prefix+'nm','-C','-S','--size-sort',elf]),
          ('relocations',[prefix+'readelf','-rW',elf]),
          ('disassembly',[prefix+'objdump','-Cd',elf]),
          ('remote_hash',['sha256sum',elf]),
          ('compiler_version',[prefix+'g++','--version']),
          ('libraries',['arduino-cli','lib','list'])]
for name,cmd in commands:
    result=b.remote('2629958581',cmd,capture=True)
    target=OUT/f'elf_{rate}_{name}.txt'
    target.write_bytes(result.stdout.encode())
    report['checks'].append(dict(name=name,argv=cmd,exit_status=result.returncode,
                                 path=target.relative_to(ROOT).as_posix(),
                                 sha256=hashlib.sha256(target.read_bytes()).hexdigest(),stderr=result.stderr))
    receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
local=OUT/f'candidate_{rate}.elf'
cmd=[b.adb_executable(),'-s','2629958581','pull',elf,str(local)]
result=subprocess.run(cmd,text=True,capture_output=True)
report['checks'].append(dict(name='pull',argv=cmd,exit_status=result.returncode,
                             stdout=result.stdout,stderr=result.stderr))
if result.returncode==0:
    report['local_elf_sha256']=hashlib.sha256(local.read_bytes()).hexdigest()
receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
raise SystemExit(result.returncode)
