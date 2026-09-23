# Reads installed Linux source and a packaged ELF; never connects to the MCU.
# Preserves exact source identities and bounded line selections for the ADC audit.
# Run locally with the established ADB transport; stdout is a compact receipt.
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.board_tool import remote

os.environ['SUMO_TRANSPORT'] = 'adb'
os.environ['SUMO_ADB_SERIAL'] = '2629958581'
os.environ['SUMO_ADB_EXECUTABLE'] = str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')

PROGRAM = r'''
from pathlib import Path
import hashlib,json,re,subprocess
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
I=C/'variants/arduino_uno_q_stm32u585xx/llext-edk/include'
H=I/'modules/hal/stm32/stm32cube/stm32u5xx'
requests=[
(H/'drivers/include/stm32u5xx_ll_adc.h',r'LL_ADC_(Enable|Disable|IsEnabled|StartCalibration|IsCalibration|SetCalibration|GetCalibration|SetCommonClock|GetCommonClock|SetResolution|SetDataAlignment|SetLowPower|REG_|SetChannel|SetSequencer|ClearFlag|IsActiveFlag|DisableIT)|LL_ADC_DELAY|LL_ADC_CALIB|LL_ADC_CLOCK|LL_ADC_SAMPLINGTIME|LL_ADC_RESOLUTION',5,34),
(H/'drivers/include/stm32u5xx_ll_rcc.h',r'LL_RCC_(SetADCClockSource|GetADCClockSource)|LL_RCC_ADC_CLKSOURCE',5,28),
(H/'drivers/include/stm32u5xx_ll_bus.h',r'PERIPH_ADC|PERIPH_GPIOA',2,3),
(H/'drivers/include/stm32u5xx_ll_pwr.h',r'LL_PWR_(EnableVddA|IsEnabledVddA|EnableVDDA|IsEnabledVDDA)|VDDA|VddA',5,15),
(H/'soc/stm32u585xx.h',r'ADC1_BASE|ADC1_COMMON|ADC1_IRQn|ADC4_IRQn|ADC1_S|ADC1_NS|ADC1_COMMON_S|ADC1_COMMON_NS|ADC_ISR_|ADC_CR_|ADC_CFGR_|ADC_CFGR1_|ADC_CFGR2_|ADC_CCR_|ADC_CALFACT|ADC_SMPR|ADC_SQR1_|RCC_CCIPR1_ADCDACSEL|RCC_AHB2ENR1_ADC12EN|PWR_SVMCR_ASV|ADC_TypeDef|ADC_Common_TypeDef',1,2),
(I/'zephyr/include/generated/zephyr/devicetree_generated.h',r'NODELABEL_adc1|adc_42028000.*(clock|reg_|resolution|interrupt|zephyr_deferred)|adc_42028000.*EXISTS|adc_42028000.*_VAL_|adc_42028000.*_ORD|adc_42028000.*_P_status|adc_42028000.*_P_st_|adc_42028000.*_P_pinctrl|adc_42028000.*_P_io_channels|NODELABEL_adc4|NODELABEL_rcc|NODELABEL_pll2|pll_0.*(div|mul)|adc1_in9|adc1_in10',2,3),
(I/'zephyr/include/generated/zephyr/autoconf.h',r'ADC|STM32U5|CLOCK|POWER|PINCTRL|TRUSTED|SECURE|SINGLE_THREAD',0,0),
(C/'variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay',r'adc|pll2|pll1|msis|rcc|vref',5,15),
]
out=[]
for path,pattern,before,after in requests:
 if not path.exists(): out.append({'path':str(path),'error':'absent'});continue
 data=path.read_bytes();lines=data.decode().splitlines();idx=set()
 for n,s in enumerate(lines):
  if re.search(pattern,s): idx.update(range(max(0,n-before),min(len(lines),n+after+1)))
 out.append({'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'line_count':len(lines),'lines':[[i+1,lines[i]] for i in sorted(idx)]})
print(json.dumps(out))
'''

if len(sys.argv) > 1:
    PROGRAM = Path(sys.argv[1]).read_text(encoding='utf-8')
result = remote('2629958581', ['python3', '-c', PROGRAM], capture=True, timeout=45)
records = json.loads(result.stdout)
destination = Path(__file__).with_name(sys.argv[2] if len(sys.argv) > 2 else 'installed_source_01.json')
destination.write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'receipt':str(destination),'records':len(records),'stderr':result.stderr,'exit':result.returncode}))
