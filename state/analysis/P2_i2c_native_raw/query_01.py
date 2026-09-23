from pathlib import Path
import json,hashlib,re,subprocess
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
H=I/'modules/hal/stm32/stm32cube/stm32u5xx'
out=[]
req=[
(I/'zephyr/include/generated/zephyr/devicetree_generated.h',r'DT_N_S_soc_S_i2c_40008400_(P_(interrupts|clocks|clock_frequency|pinctrl|zephyr_deferred)|IRQ|REG|ORD)|DT_N_S_soc_S_pinctrl.*(pd12|pd13)',0,0),
(H/'drivers/include/stm32u5xx_ll_i2c.h',r'__STATIC_INLINE.*LL_I2C_(HandleTransfer|TransmitData8|ReceiveData8|IsActiveFlag|ClearFlag|Enable\(|Disable\(|IsEnabled\(|GenerateStopCondition|GetTransferSize|GetTransferDirection|SetTiming|GetTiming)|#define LL_I2C_(MODE_|GENERATE_|AUTOEND|SOFTEND|RELOAD|ADDRESSING_MODE)',1,16),
(H/'soc/stm32u585xx.h',r'I2C4.*IRQ|I2C4_BASE_NS|RCC_APB1ENR2_I2C4EN|RCC_CCIPR2_I2C4SEL|RCC_APB1RSTR2_I2C4RST|^#define I2C_(CR1|CR2|ISR|ICR)',0,0),
(H/'drivers/include/stm32u5xx_ll_rcc.h',r'LL_RCC_I2C4_CLKSOURCE|LL_RCC_I2C4_CLKSOURCE|LL_RCC_GetI2CClockSource',2,12),
]
for p,pat,pre,post in req:
 b=p.read_bytes();ls=b.decode().splitlines();idx=set()
 for n,s in enumerate(ls):
  if re.search(pat,s):idx.update(range(max(0,n-pre),min(len(ls),n+post+1)))
 out.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'lines':[[i+1,ls[i]] for i in sorted(idx)]})
E=C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
T='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
qs=['p __device_dts_ord_40','p *(struct i2c_stm32_config*)__device_dts_ord_40.config','p *(struct i2c_stm32_data*)__device_dts_ord_40.data','info functions i2c_stm32_irq','info functions i2c_stm32_config','disassemble i2c_stm32_init','disassemble i2c_stm32_activate','disassemble i2c_stm32_runtime_configure']
for q in qs:
 r=subprocess.run([T+'gdb','-nx','-nh','-batch',str(E),'-ex',q],capture_output=True,text=True,timeout=10)
 out.append({'gdb':q,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps(out))
