from pathlib import Path
import subprocess,json,hashlib,re
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
H=I/'modules/hal/stm32/stm32cube/stm32u5xx'
out=[]
req=[
(I/'zephyr/include/generated/zephyr/devicetree_generated.h',r'msi_pll_mode|msi_range|NODELABEL_clk_msi|clk_msis|clk_msik',0,0),
(I/'zephyr/include/zephyr/drivers/clock_control/stm32_clock_control.h',r'STM32_MSIS_PLL_MODE|STM32_MSIK_PLL_MODE',2,3),
(H/'drivers/include/stm32u5xx_ll_rcc.h',r'__STATIC_INLINE.*LL_RCC_MSI_(IsEnabledPLLMode|EnablePLLMode|DisablePLLMode)|__STATIC_INLINE.*LL_RCC_(GetMSIPLLMode|IsEnabledPLLMode)',2,10),
(H/'soc/stm32u585xx.h',r'^#define (RCC_CR_MSIPLLEN|RCC_ICSCR1_MSIPLLSEL|ADC_CFGR1_EXTEN|ADC_CFGR1_CONT|ADC4_CFGR1_DMACFG|ADC4_CFGR1_DMAEN|ADC_IER|ADC_CR_(ADEN|ADDIS|ADSTART|ADSTP|ADCAL)|DAC_CR_(EN1|CEN1|TEN1|WAVE1|DMAEN1))',0,0),
(H/'drivers/include/stm32u5xx_ll_adc.h',r'__STATIC_INLINE.*LL_ADC_REG_(IsTriggerSourceSWStart|GetContinuousMode|GetDMATransfer)|__STATIC_INLINE.*LL_ADC_(IsEnabled|IsCalibrationOnGoing|REG_IsConversionOngoing)',2,10),
]
for p,pat,pre,post in req:
 if not p.exists():out.append({'path':str(p),'error':'absent'});continue
 b=p.read_bytes();lines=b.decode().splitlines();idx=set()
 for n,s in enumerate(lines):
  if re.search(pat,s):idx.update(range(max(0,n-pre),min(len(lines),n+post+1)))
 out.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'lines':[[i+1,lines[i]] for i in sorted(idx)]})
for p in I.rglob('*stm32*.h'):
 if 'clock' in p.name:
  b=p.read_bytes();lines=b.decode().splitlines();idx=set()
  for n,s in enumerate(lines):
   if re.search(r'STM32_MSIS_PLL_MODE|STM32_MSIK_PLL_MODE',s):idx.update(range(max(0,n-2),min(len(lines),n+4)))
  if idx:out.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'lines':[[i+1,lines[i]] for i in sorted(idx)]})
print(json.dumps(out))
