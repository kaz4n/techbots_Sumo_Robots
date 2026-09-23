# Reads installed matrix headers and disassembles packaged ELF on board Linux.
# Records actual native API bindings without upload or MCU/debugger attachment.
# Tested by subprocess return codes and exact retained hashes.
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import collect

PROGRAM=r'''
from pathlib import Path
import base64,hashlib,json,re,subprocess
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
T='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
E=C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
out={'elf':{'path':str(E),'bytes':E.stat().st_size,'sha256':hashlib.sha256(E.read_bytes()).hexdigest()},'files':[],'commands':[]}
paths=[C/'libraries/Arduino_LED_Matrix/library.properties',C/'variants/arduino_uno_q_stm32u585xx/syms-dynamic.ld',I/'zephyr/include/zephyr/drivers/counter.h',I/'zephyr/include/generated/zephyr/devicetree_generated.h']
for p in paths:
 b=p.read_bytes();s=b.decode();rec={'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 if len(b)<100000:rec['text']=s
 else:rec['excerpts']=[[n+1,l] for n,l in enumerate(s.splitlines()) if re.search('counter_matrix|counter.*_ORD|timers_40001400|counter.*10000',l)]
 out['files'].append(rec)
def run(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=20);out['commands'].append({'args':args,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
run([T+'nm','-S','-n',str(E)])
out['commands'][-1]['stdout']='\n'.join(l for l in out['commands'][-1]['stdout'].splitlines() if re.search('matrix|timer_irq_handler_fn|counter_stm32|irq_lock|irq_unlock|z_impl_counter',l))
for f in ['matrixBegin','matrixEnd','matrixGrayscaleWrite','matrixSetGrayscaleBits','timer_irq_handler_fn','turnLed','counter_stm32_start','counter_stm32_stop','counter_stm32_set_top_value']:
 run([T+'objdump','-d','--disassemble='+f,str(E)])
run([T+'gdb','-nx','-nh','-batch',str(E),'-ex','info variables matrix','-ex','info variables counter_stm32'])
print(json.dumps(out))
'''
r=collect.remote('2629958581',['python3','-c',PROGRAM],capture=True,timeout=45)
d=json.loads(r.stdout)
(Path(__file__).parent/'binary_receipt.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'exit':r.returncode,'stderr':r.stderr,'commands':[(x['args'][0],x['exit']) for x in d['commands']]}))
