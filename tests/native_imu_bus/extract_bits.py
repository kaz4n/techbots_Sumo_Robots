# Extracts installed STM32U585 I2C, RCC and GPIO declarations without API invention.
# Replaces volatile register words with equally sized observable storage only.
# Source hashes and derivation metadata make fixture bodies independently auditable.
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'state/analysis/P2_adc_ownership_raw/headers'
OUT = Path(__file__).resolve().parent
I2C = ROOT / 'state/analysis/P2_i2c_native_raw/stm32u5xx_ll_i2c.h'
assert hashlib.sha256(I2C.read_bytes()).hexdigest() == 'aeb2be3a463efbf1ca47b15c4696da323b5a212a47055b10cdd8fd2e8e92ae0a'
INTRO = '''// Copies exact installed STM32U585 definitions and selected LL operations.
// Observable four-byte words preserve offsets while modeling hardware side effects.
// Independent B3 native tests exercise the production transfer contract.
#pragma once
/* Copyright (c) 2021 STMicroelectronics. All rights reserved.
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 * Source identities and selected bodies are recorded in extraction.json.
 */
'''

def write(name, text):
    (OUT / name).write_bytes(('\n'.join(line.rstrip() for line in text.splitlines()).rstrip()+'\n').encode())

cmsis = (SOURCE / 'stm32u585xx.h').read_text()
bits = []
for line in cmsis.splitlines():
    if re.match(r'#define\s+(?:I2C|RCC|GPIO|PWR|SYSCFG)_\w+\s+', line):
        if line.rstrip().endswith('\\'):
            raise RuntimeError('Unexpected multiline CMSIS definition: '+line)
        name = line.split()[1]
        if name.endswith(('_NS', '_S')) or '_BASE' in name:
            continue
        bits.append(line.split('/*')[0].rstrip())
write('installed_bits.h', INTRO+'\n'.join(bits))
types = []
for name in ('I2C_TypeDef', 'GPIO_TypeDef', 'RCC_TypeDef', 'PWR_TypeDef', 'SYSCFG_TypeDef'):
    body = re.search(r'typedef struct\s*\{([^{}]*)\}\s*'+name+r';', cmsis, re.S).group(0)
    types.append(re.sub(r'__I[O]?\s+uint32_t', 'volatile Reg', body))
write('installed_types.h', INTRO+'#include "register.h"\n#include <cstdint>\nusing std::uint32_t;\n'+'\n'.join(types))

selections = {
    'i2c': ['LL_I2C_Enable','LL_I2C_Disable','LL_I2C_IsEnabled','LL_I2C_ConfigFilters',
            'LL_I2C_SetTiming','LL_I2C_HandleTransfer','LL_I2C_GenerateStopCondition',
            'LL_I2C_ReceiveData8','LL_I2C_TransmitData8'] +
           ['LL_I2C_IsActiveFlag_'+n for n in ('TXE','TXIS','RXNE','ADDR','NACK','STOP','TC','TCR','BERR','ARLO','OVR','BUSY')] +
           ['LL_I2C_ClearFlag_'+n for n in ('ADDR','NACK','STOP','BERR','ARLO','OVR')],
    'gpio': ['LL_GPIO_'+n for n in ('SetPinMode','GetPinMode','SetPinPull','GetPinPull',
            'SetPinOutputType','GetPinOutputType','SetPinSpeed','GetPinSpeed',
            'SetAFPin_8_15','GetAFPin_8_15','IsPinLocked','ReadInputPort','IsInputPinSet')],
    'bus': ['LL_APB1_GRP2_EnableClock','LL_APB1_GRP2_IsEnabledClock'],
    'rcc': ['LL_RCC_GetSysClkSource','LL_RCC_GetAHBPrescaler','LL_RCC_GetAPB1Prescaler',
            'LL_RCC_GetI2CClockSource','LL_RCC_PLL1_GetMainSource','LL_RCC_PLL1_GetDivider',
            'LL_RCC_PLL1_GetN','LL_RCC_PLL1_GetR','LL_RCC_PLL1_IsReady',
            'LL_RCC_PLL1_IsEnabledDomain_SYS','LL_RCC_PLL1FRACN_IsEnabled',
            'LL_RCC_MSI_IsEnabledRangeSelect','LL_RCC_MSIS_GetRange','LL_RCC_MSIS_IsReady',
            'LL_RCC_IsEnabledPLLMode','LL_RCC_GetMSIPLLMode'],
}
manifest = {'cmsis': {'path': str((SOURCE/'stm32u585xx.h').relative_to(ROOT)),
                     'sha256': hashlib.sha256((SOURCE/'stm32u585xx.h').read_bytes()).hexdigest()},
            'adaptations': ['__STATIC_INLINE becomes inline', '__IO/__I uint32_t storage becomes volatile four-byte Reg',
                            'comments stripped from selected bodies, trailing whitespace removed, LF newlines'],
            'headers': {}}
for kind, names in selections.items():
    path = I2C if kind == 'i2c' else SOURCE / f'stm32u5xx_ll_{kind}.h'
    original = path.read_text()
    text = re.sub(r'/\*.*?\*/', '', original, flags=re.S)
    prefix = r'(?:LL_\w+|RCC_OFFSET_\w+)' if kind == 'bus' else r'(?:LL_'+kind.upper()+r'_\w+|RCC_OFFSET_\w+)'
    defines = re.findall(r'^#define\s+'+prefix+r'\b(?:[^\n]*\\\n)*[^\n]*', text, re.M)
    functions = []
    for name in names:
        match = re.search(r'__STATIC_INLINE[^\n]*\b'+name+r'\([^{}]*\)\s*\{', text)
        if match is None:
            raise RuntimeError(name)
        depth, end = 1, match.end()
        while depth:
            depth += (text[end] == '{') - (text[end] == '}')
            end += 1
        functions.append(text[match.start():end].replace('__STATIC_INLINE', 'inline'))
    host_warning = '#pragma GCC diagnostic push\n#pragma GCC diagnostic ignored "-Wint-to-pointer-cast"\n' if kind == 'rcc' else ''
    host_end = '\n#pragma GCC diagnostic pop\n' if kind == 'rcc' else ''
    write(f'stm32u5xx_ll_{kind}.h', INTRO+'#include "native_cmsis.h"\n'+host_warning+'\n'.join(defines+functions)+host_end)
    manifest['headers'][kind] = {'path': str(path.relative_to(ROOT)),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'functions': names,
        'host_warning_scope': 'RCC fixed 32-bit peripheral-address cast warning only' if kind == 'rcc' else None}
write('extraction.json', json.dumps(manifest, indent=2))
print('Extracted', len(bits), 'CMSIS constants and', sum(map(len,selections.values())), 'exact installed LL bodies')
