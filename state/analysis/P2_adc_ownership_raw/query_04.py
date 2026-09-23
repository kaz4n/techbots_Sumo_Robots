from pathlib import Path
import subprocess,json,hashlib,re
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
H=I/'modules/hal/stm32/stm32cube/stm32u5xx'
out=[]
req=[
(H/'drivers/include/stm32u5xx_ll_rcc.h',r'MSIPLL|MSI.*(UNLOCK|LOCK|READY)|MSI.*(Unlock|Lock)|UNLOCK',3,6),
(H/'soc/stm32u585xx.h',r'MSIPLL|MSI.*(UNLOCK|LOCK)|RCC_IRQn|MSI.*IRQ',1,2),
(H/'drivers/include/stm32u5xx_ll_exti.h',r'MSI|UNLOCK',4,7),
(I/'zephyr/include/generated/zephyr/devicetree_generated.h',r'DT_N_S_clocks_S_clk_msis_P_msi_pll_mode|DT_N_S_clocks_S_clk_msis_STATUS|DT_N_S_clocks_S_clk_msis_P_clock_frequency|DT_N_S_clocks_S_clk_msis_P_msi_range',0,0),
]
for p,pat,pre,post in req:
 b=p.read_bytes();lines=b.decode().splitlines();idx=set()
 for n,s in enumerate(lines):
  if re.search(pat,s):idx.update(range(max(0,n-pre),min(len(lines),n+post+1)))
 out.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'lines':[[i+1,lines[i]] for i in sorted(idx)]})
E=C/'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
T='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
queries=['info functions rcc','info functions stm32.*clock','p _sw_isr_table[9]','p _sw_isr_table[10]','info variables MSI','disassemble stm32_clock_control_init']
for q in queries:
 r=subprocess.run([T+'gdb','-nx','-nh','-batch',str(E),'-ex',q],capture_output=True,text=True,timeout=10)
 out.append({'gdb':q,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
print(json.dumps(out))
