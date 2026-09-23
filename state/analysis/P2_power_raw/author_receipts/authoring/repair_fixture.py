from pathlib import Path
import json
f=Path('tests/native_power')
snaps={str(p.relative_to(f)):p.read_text(encoding='utf-8-sig') for p in f.rglob('*') if p.is_file() and 'receipts' not in p.parts}
(f/'receipts/initial_fixture_snapshot.json').write_text(json.dumps(snaps))
p=f/'extract_bits.py'
s=p.read_text(encoding='utf-8-sig').replace('(?:ADC|RCC|PWR|SYSCFG|DAC|GPIO)_','(?:ADC4|ADC|RCC|PWR|SYSCFG|DAC|GPIO)_')
s=s.replace("macros.append(line.split('/*')[0].rstrip())","name=line.split()[1]\n        if name.endswith(('_NS','_S')) or '_BASE' in name: continue\n        macros.append(line.split('/*')[0].rstrip())")
s=s.replace('defines=re.findall',"text=re.sub(r'/\*.*?\*/','',text,flags=re.S)\n    defines=re.findall")
p.write_text(s)
p=f/'register.h'
s=p.read_text(encoding='utf-8-sig').replace('std::uint32_t value;','std::uint32_t value;\n    Reg()=default;\n    Reg(const volatile Reg& r):value(static_cast<std::uint32_t>(r)){}')
p.write_text(s)
p=f/'native_fixture.cc'
s=p.read_text().replace('Reg::operator std::uint32_t() const volatile {','Reg::operator std::uint32_t() const volatile {\n    auto a=reinterpret_cast<std::uintptr_t>(this);\n    if(!((a>=0x42020000UL&&a<0x42029000UL)||(a>=0x46020000UL&&a<0x46022000UL)||(a>=0x40010000UL&&a<0x40011000UL)))return value;')
p.write_text(s)
p=f/'zephyr/devicetree.h'
p.write_text(p.read_text()+'\n#define FIX_PROP_adc1_zephyr_deferred_init 1\n')
