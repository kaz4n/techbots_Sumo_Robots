from pathlib import Path
import subprocess,json,hashlib,re
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
H=I/'modules/hal/stm32/stm32cube/stm32u5xx'
out=[]
req=[
(C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.config',r'CONFIG_PM|CONFIG_USERSPACE|CONFIG_ADC|CONFIG_DAC|CONFIG_DYNAMIC_INTERRUPTS',1,1),
(C/'cores/arduino/wiring_analog.cpp',r'analogRead|analogWrite|dac_|adc_|set_pin_for_analog|restore',5,14),
(H/'drivers/include/stm32u5xx_ll_dac.h',r'__STATIC_INLINE.*LL_DAC_(Enable|Disable|IsEnabled|IsEnabledDMAReq|IsEnabledTrigger|IsEnabledCalibration)|LL_DAC_CHANNEL_1',1,14),
(H/'drivers/include/stm32u5xx_ll_adc.h',r'LL_ADC_REG_GetTriggerSource|LL_ADC_REG_GetContinuousMode|LL_ADC_REG_IsConversionOngoing|LL_ADC_IsCalibrationOnGoing|ADC_CR_BITS_PROPERTY_RS',2,14),
(H/'soc/stm32u585xx.h',r'^#define (DAC_CR_(EN1|TEN1|WAVE1|MAMP1|DMAEN1|DMAUDRIE1|CEN1)|ADC4_CFGR1_(EXTEN|CONT|DMAEN|AUTOFF|WAIT)|ADC4_CR_|RCC_AHB2ENR1_ADC12EN|RCC_AHB2ENR1_ADC1EN|RCC_CCIPR3_ADCDACSEL|RCC_AHB3ENR_ADC4EN)',0,2),
]
for p,pat,pre,post in req:
 if not p.exists():out.append({'path':str(p),'error':'absent'});continue
 b=p.read_bytes();lines=b.decode().splitlines();idx=set()
 for n,s in enumerate(lines):
  if re.search(pat,s):idx.update(range(max(0,n-pre),min(len(lines),n+post+1)))
 out.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'lines':[[i+1,lines[i]] for i in sorted(idx)]})
virtual=[]
for p in I.rglob('*.h'):
 if p.name in ['cmsis.h','cmsis_core_m_defaults.h','cmsis_nvic.h','cmsis_nvic_m.h','cmsis_nvic_virtual.h']:
  b=p.read_bytes();lines=b.decode().splitlines();matches=[[n+1,s] for n,s in enumerate(lines) if 'CMSIS_NVIC_VIRTUAL' in s or 'NVIC_Get' in s]
  virtual.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'matches':matches})
out.append({'cmsis_wrapper_candidates':virtual})
E=C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
T='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
queries=['p __pinctrl_state_pins_0__device_dts_ord_64','p __pinctrl_dev_config__device_dts_ord_54','p/x *(unsigned int*)0x080098e8','p/x *(unsigned int*)0x080098f4','p/x &__device_dts_ord_17','p/x &__device_dts_ord_54','disassemble z_impl_device_init','disassemble do_device_init','disassemble z_impl_device_deinit','disassemble adc_stm32_disable','disassemble adc_stm32_calibration_start','disassemble adc_stm32_calibrate','disassemble dac_stm32_channel_setup','disassemble dac_stm32_write_value']
for q in queries:
 r=subprocess.run([T+'gdb','-nx','-nh','-batch',str(E),'-ex',q],capture_output=True,text=True,timeout=10)
 out.append({'gdb':q,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps(out))
