"""Inspect exact failed-link startup and imports without MCU or transport access."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[3]
RAW=Path(__file__).resolve().parent
receipt=ROOT/'state/analysis/P2_app_runtime_raw/target_4cb637f9_bench-default.json'
data=json.loads(receipt.read_text())
prior=json.loads((ROOT/'state/analysis/P2_app_transaction_raw/target_9d6c0005_bench-default.json').read_text())
actual=next(r for r in data['records'] if 'disassembly' in r)
blocks=[b for b in re.split(r'(?m)(?=^[0-9a-f]+ <)',actual['disassembly']) if b.strip()]
startup=[b for b in blocks if '_GLOBAL__sub_I' in b.splitlines()[0] or
         any(n in b.splitlines()[0] for n in ('<setup>','<loop>','<main>','<__loopHook()>'))]
rel=actual['relocations']['stdout']
init=re.search(r"Relocation section '\.rel\.init_array'[^\n]*\n(.*?)(?=\nRelocation section|\Z)",rel,re.S)
assert init and 'contains 12 entries' in init[0]
entry_relocations=[s for s in rel.splitlines() if re.match(
    r'^(000000(80|84|88|94|98)|00001e[3456][048c]|000163(c4|c8|cc|d0|d4)) ',s)]
prior_imports={s.split()[-1] for s in prior['records'][0]['undefined']['stdout'].splitlines()}
assert len(prior_imports)==188
for r in data['records']:
    assert {s.split()[-1] for s in r['undefined']['stdout'].splitlines()}==prior_imports
assert data['base_sha256']==prior['base_sha256']
for key, count in (('native_exports',40),('math_exports',42)):
    values=re.findall(r'= (0x[0-9a-f]+)',data[key]['stdout'])
    assert len(values)==count and all(int(v,16)>0 for v in values)
out=dict(scope='Exact-source failed-link offline startup evidence; not target acceptance',
    source=data['source_sha256'],target_compile_accepted=False,
    receipt_sha256=hashlib.sha256(receipt.read_bytes()).hexdigest(),
    init_entries=12,init_relocations=init[0],entrypoint_relocations=entry_relocations,
    startup_blocks=startup,unchanged_imports=188,unchanged_loader_sha256=data['base_sha256'],
    native_exports_nonzero=40,aeabi_exports_nonzero=42,
    observations=['setup zeroes SetupGrants then calls Runtime.begin',
       'loop binds Runtime.step', 'main binds initVariant, start_static_threads, setup, loop, empty loop hook',
       'app constructor only initializes storage and invokes passive port factories and Runtime constructor',
       'inherited Bridge, serial and C++ runtime startup remain; no native runtime measurement inferred'])
target=RAW/'final_startup_review.json'
if target.exists(): raise SystemExit('Preserve earlier startup evidence')
target.write_text(json.dumps(out,indent=2)+'\n')
print('PASS_OFFLINE_FAILED_LINK_STARTUP:12init/188imports/40native/42AEABI; RAM blocker remains')
