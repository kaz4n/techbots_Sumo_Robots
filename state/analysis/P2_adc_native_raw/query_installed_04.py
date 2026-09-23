from pathlib import Path
import json,subprocess
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
E=C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
T='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
out=[]
queries=['p __device_dts_ord_9','p *(struct clock_control_driver_api*)__device_dts_ord_9.api','p __llext_sym___device_dts_ord_9','p __device_dts_ord_54','p __device_dts_ord_64','p adc_stm32_cfg_1','ptype /o ADC_TypeDef','ptype /o ADC_Common_TypeDef','p/x ADC1','p/x ADC1_COMMON','disassemble adc_stm32_isr_37','disassemble adc_stm32_isr']
for q in queries:
 r=subprocess.run([T+'gdb','-nx','-nh','-batch',str(E),'-ex',q],capture_output=True,text=True,timeout=10)
 out.append({'gdb':q,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps(out))
