"""Preserve independently decoded D107 generic-build rejection witnesses."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
RAW=ROOT/'state/analysis/P2_opp_view_raw'
def sha(data):return hashlib.sha256(data).hexdigest()
name=sys.argv[1]
assert name.startswith('target_') and '/' not in name and '\\' not in name
folder=RAW/name
audit=json.loads((folder/'audit.json').read_text())
manifest=json.loads((RAW/('target_sources_'+audit['source_sha256'][:8])/'manifest.json').read_text())
assert audit['source_files']==manifest['source_files']
digest=hashlib.sha256()
for path,expected in sorted(audit['source_files'].items()):
    data=(RAW/('target_sources_'+audit['source_sha256'][:8])/path).read_bytes()
    assert sha(data)==expected,path
    digest.update(path.encode());digest.update(b'\0');digest.update(data)
assert digest.hexdigest()==audit['source_sha256']==manifest['source_sha256']
spec=importlib.util.spec_from_file_location('reviewed_elf',ROOT/'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
records=[]
for row in audit['records']:
    assert sha((folder/row['name']).read_bytes())==row['sha256']
    if row['name'].endswith('.elf'):
        elf=module.Elf(folder/row['name']);account=elf.account()
        records.append(dict(file=row['name'],sha256=row['sha256'],bytes=len(elf.raw),
            compiler_payload=account['compiler_payload'],conditional_peak=account['conditional_pristine_peak_consumption'],
            init=account['init'],fini=account['fini'],
            used_imports=sorted({r['name'] for r in elf.relocations if r['symbol_section']==''}),
            sized_bss=[s for s in elf.symbols if s['section']=='.bss' and s['size']],
            empty_strong_loop_hook=elf.functions()['_Z10__loopHookv']==bytes.fromhex('7047')))
final=next(r for r in records if r['file']=='opp_view.ino.elf')
assert any(r['name']=='_GLOBAL__sub_I_Bridge' for r in final['init'])
assert any(s['name']=='Serial1' for s in final['sized_bss'])
assert 'z_impl_k_sem_init' in final['used_imports']
row=next(r for r in audit['records'] if r['name']=='opp_view.ino.elf')
disassembly=next(c['stdout'] for c in row['commands'] if 'objdump' in c['argv'][0])
selected=['_GLOBAL__sub_I_setup','_GLOBAL__sub_I__ZN11native_pins5TABLEE',
          '_GLOBAL__sub_I_Bridge','_GLOBAL__sub_I__ZN7arduino12ZephyrSerial5beginEmt',
          '_ZN7arduino12ZephyrSerial18ZephyrSerialBufferILi1024EEC1Ev','_Z10__loopHookv']
witnesses=[]
for symbol in selected:
    marker=' <'+symbol+'>:';position=disassembly.find(marker)
    assert position>=0,symbol
    start=disassembly.rfind('\n',0,position)
    end=disassembly.find('\n\n',position)
    witnesses.append(disassembly[start:end])
(OUT/(name+'_startup_witness.txt')).write_text('\n'.join(witnesses))
result=dict(verdict='BLOCKER_D107_R3_UNRELATED_NATIVE_STARTUP_DEPENDENCIES',
    source_sha256=audit['source_sha256'],source_files=len(audit['source_files']),artifacts=records,
    packages=[dict(name=r['name'],sha256=r['sha256'],bytes=r['bytes']) for r in audit['records'] if r['name'].endswith('.bin')],
    actual_abi=audit['abi']['stdout'].split('/* offset')[0],
    boundary='No upload or target execution; heap figures exclude extra constructor allocations and are not acceptance',
    finding='Bridge/Serial and their initializers survive generic library discovery despite all-false bench setup; no claim that every retained import executes')
(OUT/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(verdict=result['verdict'],source_sha256=result['source_sha256'],elf_sha256=final['sha256'],
    init=len(final['init']),fini=len(final['fini']),compiler_payload=final['compiler_payload'],
    conditional_peak=final['conditional_peak']),indent=2))
