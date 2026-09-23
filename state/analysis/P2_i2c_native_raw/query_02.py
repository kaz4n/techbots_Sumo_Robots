from pathlib import Path
import json,hashlib,subprocess
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
ps=[I/'modules/hal/stm32/stm32cube/stm32u5xx/drivers/include/stm32u5xx_ll_i2c.h']
out=[]
for p in ps:
 b=p.read_bytes();out.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'text':b.decode()})
E=C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
T='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
qs=['p pclken_2','p _sw_isr_table[100]','p _sw_isr_table[101]','p __pinctrl_state_pins_0__device_dts_ord_40','disassemble i2c_stm32_irq_config_func_2','disassemble i2c_stm32_configure_timing','ptype I2C_TypeDef']
for q in qs:
 r=subprocess.run([T+'gdb','-nx','-nh','-batch',str(E),'-ex',q],capture_output=True,text=True,timeout=10)
 out.append({'gdb':q,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps(out))
