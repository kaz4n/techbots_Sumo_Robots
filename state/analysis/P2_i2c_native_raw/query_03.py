from pathlib import Path
import json,hashlib,re
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
out=[]
for p in I.rglob('*.h'):
 if p.name not in ['pinctrl_soc.h','stm32-pinctrl.h','stm32-pinctrl-common.h']:continue
 if 'stm32' not in str(p):continue
 b=p.read_bytes();ls=b.decode().splitlines();idx=set()
 for n,s in enumerate(ls):
  if re.search(r'PUPD|OSPEED|PUSHPULL|OPENDRAIN|OTYPE|PINMUX|PINCFG|pincfg|pull_up|pull_down|drive_open|slew_rate',s):idx.update(range(max(0,n-2),min(len(ls),n+4)))
 out.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'lines':[[i+1,ls[i]] for i in sorted(idx)]})
p=I/'zephyr/include/generated/zephyr/devicetree_generated.h'
b=p.read_bytes();ls=b.decode().splitlines();idx=[]
for n,s in enumerate(ls):
 if re.search(r'DT_N_S_soc_S_pin_controller_42020000_S_i2c4_(scl_pd12|sda_pd13)_P_(bias|drive|slew|pinmux)|DT_N_S_soc_S_gpio_42020c00_(ORD|REG)',s):idx.append([n+1,s])
out.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'lines':idx})
print(json.dumps(out))
