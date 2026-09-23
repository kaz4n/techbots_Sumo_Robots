from pathlib import Path
import hashlib,json,re,subprocess
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
H=I/'modules/hal/stm32/stm32cube/stm32u5xx'
requests=[
(H/'drivers/include/stm32u5xx_ll_rcc.h',r'ADCDAC|GetPLL2|GetADC|PLL2_Get|LL_RCC_PLL2_Is|GetSysClkSource',4,22),
(I/'zephyr/include/zephyr/dt-bindings/clock/stm32u5_clock.h',r'ADCDAC|PLL2|STM32_SRC|ADC|CCIPR',2,3),
(I/'zephyr/include/generated/zephyr/devicetree_generated.h',r'^#define DT_N_S_clocks_S_pll2_P_.*(div|mul|clocks|status)|^#define DT_N_S_clocks_S_msis_P_|^#define DT_N_S_soc_S_adc_42028000_P_st_adc_prescaler|^#define DT_N_S_soc_S_pin_controller_42020000_S_adc1_in9_pa4_P_|^#define DT_N_S_soc_S_adc_46021000_P_status|^#define DT_N_S_soc_S_dac_.*P_status',0,0),
(H/'soc/stm32u585xx.h',r'RCC_CCIPR1_ADCDACSEL|RCC_CCIPR2_ADCDACSEL|ADC1_BASE|ADC1_COMMON|ADC1_IRQn|ADC1_S|ADC1_NS|ADC1_COMMON_S|ADC1_COMMON_NS|PWR_SVMCR_ASV|ADC_TypeDef|ADC_Common_TypeDef',4,3),
(H/'drivers/include/stm32u5xx_ll_adc.h',r'ADC_CR_BITS_PROPERTY_RS|LL_ADC_CALIB_OFFSET_LINEARITY|ADC_CALIB_FACTOR_(LINEARITY|OFFSET)|ADC_CALIB_MODE_MASK|LL_ADC_SetChannelPreSelection|LL_ADC_REG_ReadConversionData14|LL_ADC_REG_ReadConversionData32|LL_ADC_SetGain|LL_ADC_ConfigOver|LL_ADC_SetChannelSingleDiff',3,12),
]
out=[]
for path,pattern,before,after in requests:
 if not path.exists():out.append({'path':str(path),'error':'absent'});continue
 data=path.read_bytes();lines=data.decode().splitlines();idx=set()
 for n,s in enumerate(lines):
  if re.search(pattern,s):idx.update(range(max(0,n-before),min(len(lines),n+after+1)))
 out.append({'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'lines':[[i+1,lines[i]] for i in sorted(idx)]})
E=C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
T='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
queries=['p __device_dts_ord_17','p adc_stm32_cfg_0','p adc_stm32_data_0','p adc_stm32_clocks_0','p __device_dts_ord_8','p __llext_sym_z_impl_clock_control_on','p __llext_sym_z_impl_clock_control_configure','p __llext_sym_z_impl_clock_control_get_rate','disassemble adc_stm32_init','disassemble adc_stm32_irq_cfg_func_0','disassemble adc_stm32_calibrate','disassemble adc_stm32_calibration_start.isra.0']
for q in queries:
 r=subprocess.run([T+'gdb','-nx','-nh','-batch',str(E),'-ex',q],capture_output=True,text=True,timeout=10)
 out.append({'gdb':q,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps(out))
