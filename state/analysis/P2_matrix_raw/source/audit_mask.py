# Reads exact installed CMSIS interrupt masking definitions and matrix device ABI.
# Separates finite CPU instructions from unmeasured interrupt latency effects.
# Tested by hashes and successful offline GDB/source-read receipts.
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
for p in list(I.rglob('cmsis_gcc*.h'))+[I/'zephyr/include/generated/zephyr/devicetree_generated.h',I/'zephyr/include/generated/zephyr/autoconf.h']:
 b=p.read_bytes();lines=b.decode().splitlines();idx=set()
 pattern=r'__disable_irq\(|__get_PRIMASK|__set_PRIMASK|__get_IPSR|__get_CONTROL|__DMB\(|__get_CONTROL|GET_SPECIAL_REG|SET_SPECIAL_REG'
 if 'devicetree' in p.name:pattern=r'^#define DT_N_S_soc_S_timers_40014800_(IRQ|REG|P_st_prescaler)|^#define DT_N_S_soc_S_timers_40014800_S_counter_(ORD|P_status|P_zephyr_deferred)|^#define DT_N_NODELABEL_counter_matrix'
 if 'autoconf' in p.name:pattern=r'CONFIG_(CPU_CORTEX_M|ARMV8|CPU_HAS_FPU|USERSPACE|SMP|ZERO_LATENCY|NUM_IRQ_PRIO|NUM_METAIRQ|COUNTER|MULTITHREADING)'
 for n,l in enumerate(lines):
  if re.search(pattern,l):idx.update(range(n,min(n+(12 if 'cmsis_gcc' in p.name else 1),len(lines))))
 out['files'].append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'lines':[[n+1,lines[n]] for n in sorted(idx)]})
args=[T+'gdb','-nx','-nh','-batch',str(E)]
for expr in ['p __device_dts_ord_233','p counter_stm32_driver_api','p __llext_sym_matrixBegin','p __llext_sym_matrixEnd','p __llext_sym_matrixGrayscaleWrite','p __llext_sym_matrixSetGrayscaleBits','p __llext_sym___device_dts_ord_233','p *(struct counter_stm32_config *)__device_dts_ord_233.config']:
 args+=['-ex',expr]
r=subprocess.run(args,capture_output=True,text=True,timeout=20)
out['commands'].append({'args':args,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
for f in ['memcpy','arch_irq_unlock_outlined']:
 args=[T+'objdump','-d','--disassemble='+f,str(E)]
 r=subprocess.run(args,capture_output=True,text=True,timeout=20);out['commands'].append({'args':args,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps(out))
'''
r=collect.remote('2629958581',['python3','-c',PROGRAM],capture=True,timeout=45)
d=json.loads(r.stdout)
(Path(__file__).parent/'mask_receipt.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,indent=2))
