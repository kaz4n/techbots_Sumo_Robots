# Reads installed readiness/getter definitions and their packaged ELF bindings.
# Identifies prechecks without executing a matrix or peripheral operation.
# Tested by source hashes and offline disassembly/GDB result codes.
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import collect
PROGRAM=r'''
from pathlib import Path
import hashlib,json,re,subprocess
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
E=C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
T='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
out={'files':[],'commands':[]}
for p,pattern in [(I/'zephyr/include/zephyr/device.h',r'device_is_ready|struct device_state|#define DEVICE_DT_GET'),(I/'zephyr/include/zephyr/drivers/counter.h',r'z_impl_counter_get_top_value\(|z_impl_counter_get_value\(|z_impl_counter_get_frequency\(')]:
 b=p.read_bytes();lines=b.decode().splitlines();idx=set()
 for n,l in enumerate(lines):
  if re.search(pattern,l):idx.update(range(max(0,n-5),min(len(lines),n+16)))
 out['files'].append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'lines':[[n+1,lines[n]] for n in sorted(idx)]})
for f in ['z_impl_device_is_ready','device_is_ready','counter_stm32_get_value','counter_stm32_get_top_value','counter_stm32_get_freq']:
 args=[T+'objdump','-d','--disassemble='+f,str(E)]
 r=subprocess.run(args,capture_output=True,text=True,timeout=20);out['commands'].append({'args':args,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
args=[T+'gdb','-nx','-nh','-batch',str(E),'-ex','p __llext_sym_z_impl_device_is_ready','-ex','ptype struct device_state']
r=subprocess.run(args,capture_output=True,text=True,timeout=20);out['commands'].append({'args':args,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps(out))
'''
r=collect.remote('2629958581',['python3','-c',PROGRAM],capture=True,timeout=45)
d=json.loads(r.stdout)
(Path(__file__).parent/'readiness_receipt_final.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,indent=2))
