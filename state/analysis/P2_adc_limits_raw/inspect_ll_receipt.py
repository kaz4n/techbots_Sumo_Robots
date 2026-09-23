import json,pathlib
p=pathlib.Path('state/analysis/P2_adc_native_raw/installed_source_01.json');d=json.loads(p.read_text(encoding='utf-8-sig'))
print(type(d).__name__)
if isinstance(d,dict): print(list(d.keys()))
