"""Offline independent inspection of the root's downloaded target receipt."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[3]
path=ROOT / sys.argv[1]
data=json.loads(path.read_text())
files=data['source_files']
changed=[]; checksum=hashlib.sha256()
for name,wanted in sorted(files.items()):
    original=ROOT / name if name.startswith('src/') else ROOT / 'src/app' / name
    payload=original.read_bytes()
    actual=hashlib.sha256(payload).hexdigest()
    if actual!=wanted: changed.append(name)
    checksum.update(name.encode()+b'\0'); checksum.update(payload)
required=('app::Runtime::begin(', 'app::Runtime::step()', 'app::Transaction::decideFrom(',
    'app::Transaction::finishAfter(', 'app::NativeSources::port()', 'motors::MotorGate::halt()',
    'imu::Acquirer::advanceRead(', 'line_qtr::Reader::advance()', 'power::InputOwner::readButtons(')
artifacts=[]
for item in data['records']:
    names='\n'.join(item['nm'])
    artifacts.append(dict(path=item['path'],sha256=item['sha256'],
        missing=[n for n in required if n not in names],
        imports=len(item['undefined']['stdout'].splitlines())))
actual=next(i for i in data['records'] if 'disassembly' in i)
asm=actual['disassembly']
selected={}
for line in actual['nm_all']['stdout'].splitlines():
    if '_GLOBAL__sub_I' in line: selected[line]=True
blocks={}
for name in ('setup','loop','main','__loopHook()'):
    match=re.search(r'<'+re.escape(name)+r'>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)',asm,re.S)
    blocks[name]=match.group(0) if match else None
native=data.get('native_exports') or {}
math=data.get('math_exports') or {}
def addresses(value): return re.findall(r'= (0x[0-9a-f]+)',value.get('stdout',''))
result=dict(scope='Offline receipt review only; failed RAM check remains failed build',
    input=str(path.relative_to(ROOT)),input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    target_source=data['source_sha256'],current_source=checksum.hexdigest(),
    source_count=len(files),changed_from_current=changed,artifacts=artifacts,
    constructors=list(selected),entrypoints=blocks,
    native_addresses=addresses(native),math_addresses=addresses(math),math_missing=data.get('math_missing'),
    source_exact=not changed and checksum.hexdigest()==data['source_sha256'])
out=Path(__file__).with_name('target_review_'+data['source_sha256'][:8]+'.json')
if out.exists(): raise SystemExit('Preserve earlier target review')
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('entrypoints','constructors','native_addresses','math_addresses')},indent=2))
print('constructors',json.dumps(result['constructors']))
print('native',len(result['native_addresses']),'math',len(result['math_addresses']))
