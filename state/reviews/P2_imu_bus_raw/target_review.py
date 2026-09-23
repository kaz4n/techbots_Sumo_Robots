"""Binds current bytes to actual board-Linux target receipts and inert startup."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
receipt=ROOT/'state/analysis/P2_imu_bus_raw/target_f3e9b546_bench-default.json'
data=json.loads(receipt.read_text())
folder=ROOT/'bench/p2_imu_bus_compile'
files={p.relative_to(folder).as_posix():p.read_bytes() for p in folder.rglob('*') if p.is_file()}
files['src/config.h']=(ROOT/'src/config.h').read_bytes()
for module in ('core','hal'):
    files.update({p.relative_to(ROOT).as_posix():p.read_bytes() for p in (ROOT/'src'/module).rglob('*') if p.is_file()})
hashes={name:hashlib.sha256(raw).hexdigest() for name,raw in files.items()}
digest=hashlib.sha256()
for name,raw in sorted(files.items()):digest.update(name.encode()+b'\0');digest.update(raw)
assert hashes==data['source_files'] and digest.hexdigest()==data['source_sha256']
record=next(r for r in data['records'] if 'disassembly' in r)
text=record['disassembly']
functions={p.splitlines()[0]:p for p in re.split(r'(?=^\S+ <)',text,flags=re.M) if p.strip()}
markers=('<setup>','<loop>','_GLOBAL__sub_I__ZN13imu_bus_probe3busE','_GLOBAL__sub_I__ZN3imu3Bus13controlsOwnedEb')
startup={name:body for name,body in functions.items() if any(m in name for m in markers)}
assert len(startup)==4 and all(not re.search(r'\sblx?\s',body) for body in startup.values())
assert all(token in text for token in ('0x40008400','0x42020c00','0x46020c00','0x46020800','0xe0000000','0xe100'))
assert all(any('imu::Bus::'+method in name for name in functions) for method in ('begin()','readMotion()','readRegister','writeRegister','disableOwned()','observe','finish','launch'))
exports=re.findall(r'^\$\d+ = (0x[0-9a-f]+)',data['native_exports']['stdout'],re.M)
assert len(exports)==len(data['native_names'])==36 and all(int(v,16) for v in exports)
assert data['returncode']==0 and data['native_exports']['returncode']==0
assert all(v['returncode']==0 for r in data['records'] for v in r.values() if isinstance(v,dict) and 'returncode' in v)
relocs=record['relocations']['stdout']
selected=[line for line in relocs.splitlines() if re.match(r'(00000074|00000078|000024ac|000024b0|000024b4|0000326c|00003270|00003274|000033f4|000033fc|00003400|00003404)\s',line)]
for symbol in ('_ZN13imu_bus_probe5entryE','_ZN13imu_bus_probe8exerciseEv','_ZGVN12RouterBridge3HCIE','_ZN12RouterBridge3HCIE',
               '_ZN3imu3Bus5beginEv','_ZN3imu3Bus12readRegisterENS_8RegisterE','_ZN3imu3Bus13writeRegisterENS_8RegisterEh','_ZN3imu3Bus10readMotionEv'):
    assert any(symbol in line for line in selected)
result=dict(scope='Source and offline target ELF only; no deployed-loader or physical runtime guarantee',
    source_sha256=data['source_sha256'],matched_source_files=len(files),
    raw_receipt_sha256=hashlib.sha256(receipt.read_bytes()).hexdigest(),native_exports=36,
    all_collection_commands_zero=True,startup_functions=startup,selected_relocations=selected,
    elf=[{k:r[k] for k in ('path','bytes','sha256')} for r in data['records']],
    observations=['setup stores only the exercise address; loop returns',
      'new source/probe constructor wrappers contain only inherited RouterBridge HCI memory initialization and no calls',
      'exercise retains actual begin/read/write/burst methods via relocations, never called by setup',
      'I2C4/GPIOD/RCC/PWR literals and finite direct NVIC enable/pending/active reads retained',
      '36 native import exports resolve in the inspected packaged loader, including I2C4 ordinal40',
      'inherited Bridge/Serial/static-library initialization and __loopHook remain F091 runtime qualifications',
      'source clock checks are nominal configuration predicates; SC-AJ remains global'])
(OUT/'target_review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('source_sha256','matched_source_files','native_exports','all_collection_commands_zero')}))
