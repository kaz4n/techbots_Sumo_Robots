from pathlib import Path
import hashlib,json,re,subprocess
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
H=I/'modules/hal/stm32/stm32cube/stm32u5xx'
requests=[
(H/'drivers/include/stm32u5xx_ll_gpio.h',r'LL_GPIO_(SetPinMode|GetPinMode|SetPinPull|GetPinPull|IsPinLocked)|LL_GPIO_MODE_ANALOG',4,12),
(H/'drivers/include/stm32u5xx_ll_pwr.h',r'LL_PWR_(EnableVDDA|IsEnabledVDDA)|PWR_SVMCR_ASV',3,14),
(H/'drivers/include/stm32u5xx_ll_bus.h',r'LL_AHB2_GRP1_(EnableClock|IsEnabledClock)|LL_AHB3_GRP1_(EnableClock|IsEnabledClock)|PERIPH_(ADC|GPIOA|PWR)',2,12),
(I/'zephyr/include/zephyr/device.h',r'struct device_state|initialized|init_res|device_is_ready|device_init\(',4,14),
(I/'zephyr/include/generated/zephyr/devicetree_generated.h',r'^#define DT_N_S_soc_S_(adc_46021000|dac_46021800).*(ORD |deferred_init |P_clocks_IDX_[01]_VAL_|P_pinmux )|^#define DT_N_S_soc_S_rcc_46020c00_ORD |^#define DT_N_S_soc_S_pin_controller_42020000_S_adc1_in9_pa4_P_|^#define DT_N_S_soc_S_adc_42028000_P_resets',0,0),
]
out=[]
for path,pattern,before,after in requests:
 data=path.read_bytes();lines=data.decode().splitlines();idx=set()
 for n,s in enumerate(lines):
  if re.search(pattern,s):idx.update(range(max(0,n-before),min(len(lines),n+after+1)))
 out.append({'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'lines':[[i+1,lines[i]] for i in sorted(idx)]})
E=C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
T='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
queries=['p __device_dts_ord_10','p rcc_stm32_driver_api','p __pinctrl_states__device_dts_ord_17','p __pinctrl_state_pins_2__device_dts_ord_17','p __devstate_dts_ord_17','p/x &_sw_isr_table[37]','p _sw_isr_table[37]','disassemble adc_stm32_isr_37_init','disassemble adc_stm32_calibration_start','disassemble stm32_clock_control_on','disassemble stm32_clock_control_get_subsys_rate','disassemble stm32_clock_control_configure']
for q in queries:
 r=subprocess.run([T+'gdb','-nx','-nh','-batch',str(E),'-ex',q],capture_output=True,text=True,timeout=10)
 out.append({'gdb':q,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps(out))
