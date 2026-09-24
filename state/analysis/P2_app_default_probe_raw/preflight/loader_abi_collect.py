"""One bounded board-Linux offline ABI query; no debugger target connection."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board

os.environ['SUMO_TRANSPORT'] = 'adb'
os.environ['SUMO_ADB_SERIAL'] = '2629958581'
os.environ['SUMO_ADB_EXECUTABLE'] = str(Path(os.environ['LOCALAPPDATA']) /
    'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
PROGRAM = r'''
import subprocess,json,hashlib
from pathlib import Path
elf=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf')
gdb=Path('/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r={'elf_sha256':sha(elf),'gdb_sha256':sha(gdb)}
assert r['elf_sha256']=='39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
assert r['gdb_sha256']=='8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778'
queries=['set pagination off','set language c','p/x &llext_list','p/x &llext_heap',
 'p sizeof(struct llext)','ptype /o struct llext','ptype /o struct k_heap',
 'p/x &kheap__k_mem_llext_heap']
argv=[str(gdb),'-nx','-nh','-batch',str(elf)]
for q in queries:argv+=['-ex',q]
r['argv']=argv
try:
 p=subprocess.run(argv,capture_output=True,text=True,timeout=20)
 r.update(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
except subprocess.TimeoutExpired as e:
 r.update(returncode=None,timeout=True,stdout=repr(e.stdout),stderr=repr(e.stderr))
r['after_elf_sha256']=sha(elf)
print(json.dumps(r))
'''
destination = RAW / 'loader_abi_receipt.json'
if destination.exists():
    raise ValueError('Refuse evidence overwrite')
receipt = {'start_utc': datetime.now(timezone.utc).isoformat(),
    'remote_argv': ['python3', '-c', PROGRAM], 'timeout_seconds': 30,
    'scope': 'Offline ELF type/symbol reads only; no target remote/run/attach or MCU.'}
try:
    result = board.remote(board.target(), receipt['remote_argv'], capture=True, timeout=30)
    receipt.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
    receipt.update(error=type(error).__name__, stdout=repr(error.stdout),
                   stderr=repr(error.stderr))
finally:
    receipt['end_utc'] = datetime.now(timezone.utc).isoformat()
    destination.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print(receipt.get('stdout', ''))
print(receipt.get('stderr', ''))
