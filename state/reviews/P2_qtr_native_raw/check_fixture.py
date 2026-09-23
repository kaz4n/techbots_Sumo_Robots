"""Compare controlled register declarations with saved installed primary headers."""
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
source = root/'state/analysis/P2_adc_ownership_raw/headers'
fixture = root/'tests/native_qtr'


def clean(text):
    return re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)


def norm(text):
    return re.sub(r'\s+', '', clean(text))


def defines(text):
    lines = clean(text).replace('\\\n',' ')
    result = {}
    for name,value in re.findall(r'^#define\s+(\w+)\s+([^\n]*)', lines, re.M):
        result.setdefault(name,set()).add(norm(value))
    return result


cmsis = (source/'stm32u585xx.h').read_text()
actual = defines(cmsis)
controlled = defines((fixture/'installed_bits.h').read_text())
assert all(name in actual and values <= actual[name] for name,values in controlled.items())
layouts = []
for name in ('GPIO_TypeDef','RCC_TypeDef','EXTI_TypeDef','DBGMCU_TypeDef'):
    pattern = r'typedef struct\s*\{([^{}]*)\}\s*'+name+r';'
    original = re.search(pattern,cmsis,re.S).group(0)
    replaced = re.sub(r'__I[O]?\s+uint32_t','volatile Reg',original)
    tested = re.search(pattern,(fixture/'installed_types.h').read_text(),re.S).group(0)
    assert norm(replaced) == norm(tested), name
    layouts.append(name)
getters = {}
for kind in ('gpio','exti'):
    original = clean((source/f'stm32u5xx_ll_{kind}.h').read_text()).replace('__STATIC_INLINE','inline')
    tested = clean((fixture/f'stm32u5xx_ll_{kind}.h').read_text())
    functions = re.findall(r'inline\s+uint32_t\s+(LL_\w+)\([^{}]*\)\s*\{[^{}]*\}', tested)
    for name in functions:
        pattern = r'inline\s+uint32_t\s+'+name+r'\([^{}]*\)\s*\{[^{}]*\}'
        assert norm(re.search(pattern,original).group(0)) == norm(re.search(pattern,tested).group(0)), name
    getters[kind] = functions
result = dict(installed_constant_names=len(controlled), register_layouts=layouts,
              exact_selected_getter_bodies=getters,
              source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in source.iterdir() if p.is_file()},
              fixture_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in fixture.iterdir() if p.is_file()},
              limits='Controlled declarations, register ordering and selected getter bodies only; no physical behavior proof.')
(out/'fixture_source_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(constants=len(controlled),layouts=layouts,getters=getters)))
