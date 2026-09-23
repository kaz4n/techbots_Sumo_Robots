# Extracts exact installed constants, layouts and LL operation bodies.
# Replaces only volatile register storage with an equally sized observable word.
# Independent tests model silicon side effects; production CPP is never inspected.
import json, re, hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
source=root/'state/analysis/P2_adc_ownership_raw/headers'
out=root/'tests/native_qtr'
cmsis=(source/'stm32u585xx.h').read_text()
license_notice='/* Copyright (c) 2021 STMicroelectronics. All rights reserved.\n * This software is licensed under terms that can be found in the LICENSE file\n * in the root directory of this software component.\n * If no LICENSE file comes with this software, it is provided AS-IS.\n * Extracted from the exact installed headers retained with hashes in\n * state/analysis/P2_adc_ownership_raw/headers/manifest.json.\n */\n'
intro='// Copies source-verified installed STM32U585 declarations.\n// Four-byte observable storage preserves native offsets and command encodings.\n// Independent B2 tests supply hardware side effects and fault injection.\n#pragma once\n'+license_notice
macros=[]
for line in cmsis.splitlines():
    if re.match(r'#define\s+(?:GPIO|RCC|EXTI|DBGMCU)_\w+\s+',line):
        if line.rstrip().endswith('\\'): raise RuntimeError(line)
        name=line.split()[1]
        if name.endswith(('_NS','_S')) or '_BASE' in name or name=='ADC4_COMMON': continue
        macros.append(line.split('/*')[0].rstrip())
(out/'installed_bits.h').write_text(intro+'\n'.join(macros)+'\n')
types=[]
for name in ['GPIO_TypeDef','RCC_TypeDef','EXTI_TypeDef','DBGMCU_TypeDef']:
    text=re.search(r'typedef struct\s*\{([^{}]*)\}\s*'+name+r';',cmsis,re.S).group(0)
    text=re.sub(r'__I[O]?\s+uint32_t', 'volatile Reg',text)
    types.append(text)
(out/'installed_types.h').write_text(intro+'#include "register.h"\n#include <cstdint>\nusing std::uint32_t;\n'+'\n'.join(types)+'\n')
selections={
'gpio':['LL_GPIO_GetPinMode','LL_GPIO_GetPinPull','LL_GPIO_GetPinOutputType','LL_GPIO_GetPinSpeed','LL_GPIO_IsPinLocked','LL_GPIO_GetAFPin_0_7','LL_GPIO_GetAFPin_8_15'],
'exti':['LL_EXTI_GetEXTISource']}
for kind,names in selections.items():
    text=(source/f'stm32u5xx_ll_{kind}.h').read_text()
    text=re.sub(r'/\*.*?\*/','',text,flags=re.S)
    defines=re.findall(r'^#define\s+(?:LL_'+kind.upper()+r'_\w+|ADC_CR_BITS_PROPERTY_RS|ADC_CALIB_\w+)\b(?:[^\n]*\\\n)*[^\n]*',text,re.M)
    if kind=="exti":
        defines=[d for d in defines if not d.startswith("#define LL_EXTI_LINE_ALL_0_31")]
        defines += ["#if defined(EXTI_IMR1_IM24) && defined(EXTI_IMR1_IM25)\n#define LL_EXTI_LINE_ALL_0_31 0x03FFFFFFU\n#else\n#define LL_EXTI_LINE_ALL_0_31 0x00FFFFFFU\n#endif"]
    functions=[]
    for name in names:
        m=re.search(r'__STATIC_INLINE[^\n]*\b'+name+r'\([^{}]*\)\s*\{',text)
        if not m: raise RuntimeError(name)
        depth=1; start=m.start(); end=m.end()
        while depth:
            if text[end]=='{':depth+=1
            if text[end]=='}':depth-=1
            end+=1
        functions.append(text[start:end].replace('__STATIC_INLINE','inline'))
    (out/f'stm32u5xx_ll_{kind}.h').write_text(intro+'#include "native_cmsis.h"\n'+'\n'.join(defines)+'\n'+'\n'.join(functions)+'\n')
print(len(macros),'installed bit constants; exact selected native LL bodies and layouts')
for path in [out/'installed_bits.h', out/'installed_types.h', *[out/f'stm32u5xx_ll_{kind}.h' for kind in selections]]:
    path.write_bytes(('\n'.join(line.rstrip(' \t') for line in path.read_text().splitlines()).rstrip('\n')+'\n').encode('utf-8'))
