from pathlib import Path
import json,re,hashlib
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
H=I/'modules/hal/stm32/stm32cube/stm32u5xx'
out=[]
for path,pattern in [(H/'soc/stm32u585xx.h',r'ADC12_COMMON|ADC1_COMMON|ADC1_(BASE|NS|S)|ADC1\s|ADC1_IRQn|AHB2PERIPH_BASE_NS'),(H/'drivers/include/stm32u5xx_ll_adc.h',r'__LL_ADC_COMMON_INSTANCE|ADC_CR_BITS_PROPERTY_RS|LL_ADC_REG_ReadConversionData32'),(I/'cmsis/CMSIS/Core/Include/core_cm33.h',r'__NVIC_GetEnableIRQ|__NVIC_GetPendingIRQ|__NVIC_GetActive')]:
 if not path.exists():out.append({'path':str(path),'error':'absent'});continue
 b=path.read_bytes();lines=b.decode().splitlines();idx=set()
 for n,s in enumerate(lines):
  if re.search(pattern,s):idx.update(range(max(0,n-1),min(len(lines),n+14)))
 out.append({'path':str(path),'sha256':hashlib.sha256(b).hexdigest(),'lines':[[n+1,lines[n]] for n in sorted(idx)]})
print(json.dumps(out))
