"""Independently compares retained installed declarations with the native fixture."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
FIX=ROOT/'tests/native_imu_bus'
COMMON=ROOT/'state/analysis/P2_adc_ownership_raw/headers'
def clean(text):
    return re.sub(r'/\*.*?\*/','',text,flags=re.S)
def normalize(text):
    return re.sub(r'\s+','',text)
def functions(text):
    text=clean(text);found={}
    for match in re.finditer(r'(?:__STATIC_INLINE|inline)\s+[^\n]*\b(LL_\w+)\([^{}]*\)\s*\{',text):
        end,depth=match.end(),1
        while depth:
            depth+=(text[end]=='{')-(text[end]=='}');end+=1
        found[match.group(1)]=normalize(text[match.start():end].replace('__STATIC_INLINE','inline'))
    return found
def macros(text):
    text=clean(text).replace('\\\n',' ')
    return {m.group(1):normalize(m.group(2)) for m in re.finditer(r'^#define\s+(\w+)([^\n]*)',text,re.M)}
reports=[]
manifest=json.loads((FIX/'extraction.json').read_text())
for name,source in [(f'stm32u5xx_ll_{x}.h',ROOT/manifest['headers'][x]['path']) for x in ('i2c','gpio','rcc','bus')]:
    original=source.read_text();fixture=(FIX/name).read_text()
    of,ff=functions(original),functions(fixture);om,fm=macros(original),macros(fixture)
    reports.append(dict(name=name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        fixture_sha256=hashlib.sha256((FIX/name).read_bytes()).hexdigest(),
        functions={key:val==of.get(key) for key,val in ff.items()},
        macros={key:val==om.get(key) for key,val in fm.items()}))
cmsis=(COMMON/'stm32u585xx.h').read_text();original_macros=macros(cmsis)
bits={key:value==original_macros.get(key) for key,value in macros((FIX/'installed_bits.h').read_text()).items()}
types={}
for name in ('I2C_TypeDef','GPIO_TypeDef','RCC_TypeDef','PWR_TypeDef','SYSCFG_TypeDef'):
    pattern=r'typedef struct\s*\{([^{}]*)\}\s*'+name+r';'
    original=re.search(pattern,cmsis,re.S).group(0)
    converted=re.sub(r'__I[O]?\s+uint32_t','volatile Reg',original)
    actual=re.search(pattern,(FIX/'installed_types.h').read_text(),re.S).group(0)
    types[name]=normalize(clean(converted))==normalize(clean(actual))
result=dict(reports=reports,cmsis_bits=bits,types=types,
    all_match=all(all(x['functions'].values()) and all(x['macros'].values()) for x in reports) and all(bits.values()) and all(types.values()),
    scope='Offline equivalence with retained installed sources; fake progression is not a hardware measurement')
(OUT/'fixture_equivalence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(all_match=result['all_match'],functions=sum(len(x['functions']) for x in reports),
    ll_macros=sum(len(x['macros']) for x in reports),cmsis_bits=len(bits),types=types)))
assert result['all_match']
