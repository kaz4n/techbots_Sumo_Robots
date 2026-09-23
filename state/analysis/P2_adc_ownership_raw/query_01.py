from pathlib import Path
import subprocess,json,hashlib,re
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
H=I/'modules/hal/stm32/stm32cube/stm32u5xx'
out=[]
cmsis=list(I.rglob('core_cm33.h'))
out.append({'core_cm33_paths':[str(p) for p in cmsis]})
req=[(p,r'__NVIC_GetEnableIRQ|__NVIC_GetPendingIRQ|__NVIC_GetActive|NVIC_GetEnableIRQ|NVIC_GetPendingIRQ|NVIC_GetActive',4,24) for p in cmsis]
req += [(H/'soc/stm32u585xx.h',r'ADC1_IRQn|ADC4_IRQn|DAC1_IRQn|ADC4_BASE_NS|ADC12_COMMON_BASE_NS|ADC1_BASE_NS|RCC_AHB2ENR1_ADC12EN|RCC_AHB2ENR1_ADC1EN|RCC_AHB2RSTR1_ADC12RST|PWR_SVMCR_ASV|DAC_CR_EN1|DAC_CR_EN2|DAC_CR_TEN1|ADC_CR_BITS',2,4),
(I/'zephyr/include/zephyr/device.h',r'struct device_state|uint8_t init_res|bool initialized|struct device \{|struct device_state \*state|device_is_ready\(',3,14),
(I/'zephyr/include/generated/zephyr/autoconf.h',r'CONFIG_PM|ADC|DAC|PRIVILEGED|USERSPACE|TRUSTED_EXECUTION',1,1),
(I/'zephyr/include/generated/zephyr/devicetree_generated.h',r'^#define DT_N_S_soc_S_dac_46021800.*(PINCTRL|_P_pinctrl_|_P_clocks_|_P_status |_ORD |zephyr_deferred_init)|^#define DT_N_S_soc_S_adc_46021000.*(PINCTRL|_P_pinctrl_|_P_status |_ORD |zephyr_deferred_init)',0,0)]
for p,pat,pre,post in req:
 if not p.exists():out.append({'path':str(p),'error':'absent'});continue
 b=p.read_bytes();lines=b.decode().splitlines();idx=set()
 for n,s in enumerate(lines):
  if re.search(pat,s):idx.update(range(max(0,n-pre),min(len(lines),n+post+1)))
 out.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'lines':[[i+1,lines[i]] for i in sorted(idx)]})
E=C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
T='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
queries=['p __device_dts_ord_64','p dac_stm32_cfg_0','p dac_stm32_data_0','p __pinctrl_states__device_dts_ord_64','p __pinctrl_states__device_dts_ord_54','p _sw_isr_table[37]','p _sw_isr_table[113]','disassemble dac_stm32_init','disassemble dac_stm32_channel_setup','disassemble dac_stm32_write_value','disassemble adc_stm32_isr_113','disassemble adc_stm32_isr_37','disassemble adc_stm32_init','disassemble stm32_clock_control_on']
for q in queries:
 r=subprocess.run([T+'gdb','-nx','-nh','-batch',str(E),'-ex',q],capture_output=True,text=True,timeout=10)
 out.append({'gdb':q,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps(out))
