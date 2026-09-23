"""Compare captured native object section digests and relocation targets independently."""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[3]
RAW=ROOT/'state/analysis/P2_bridge_dependency_raw'
OUT=Path(__file__).resolve().parent

def load(branch):
    path=RAW/f'target_570ef35f_{branch}.json'
    return json.loads(path.read_text()), hashlib.sha256(path.read_bytes()).hexdigest()

def relocations(text):
    result={}
    section=None
    for line in text.splitlines():
        m=re.match(r"Relocation section '\.rel([^']+)'",line)
        if m:
            section=m[1];result[section]=[]
            continue
        m=re.match(r'([0-9a-f]+)\s+[0-9a-f]+\s+(R_ARM_\S+)\s+([0-9a-f]+)\s+(.+)',line)
        if m and section is not None:
            result[section].append((int(m[1],16),m[2],int(m[3],16),m[4]))
    return result

a, ah=load('control');b,bh=load('candidate')
assert a['source_files']==b['source_files']
assert a['source_files']==json.loads((RAW/'570ef35f_control.json').read_text())['source_files']
assert b['source_files']==json.loads((RAW/'570ef35f_candidate.json').read_text())['source_files']
assert a['base_sha256']==b['base_sha256']
assert a['metadata']['sketch/app.ino.cpp']==b['metadata']['sketch/app.ino.cpp']
candidate_commands=json.loads(b['metadata']['compile_commands.json']['text'])
for row in candidate_commands:
    args=row['arguments']
    assert '-DMATCH=0' in args and '-DMOTORS_ALLOWED=0' in args
    if not row['file'].endswith('/tls-syms.S'):
        assert '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0' in args
    assert not any('/Arduino/libraries/' in arg for arg in args)
for name,row in b['metadata'].items():
    if name.endswith('.d'):
        assert not any(x in row['text'] for x in ('Arduino_RouterBridge','Arduino_RPClite',
            'MsgPack','DebugLog','ArxTypeTraits','ArxContainer')),name
objects_a={x['path']:x for x in a['objects']}
objects_b={x['path']:x for x in b['objects']}
assert objects_a.keys()-objects_b.keys()=={'libraries/Arduino_RouterBridge/singletons.cpp.o'}
assert not objects_b.keys()-objects_a.keys()
details=[]
sections_checked=0
relocations_checked=0
for name in sorted(objects_b):
    x={s['name']:s for s in objects_a[name]['alloc_sections']}
    y={s['name']:s for s in objects_b[name]['alloc_sections']}
    rx=relocations(objects_a[name]['relocations']['stdout'])
    ry=relocations(objects_b[name]['relocations']['stdout'])
    common=x.keys()&y.keys()
    changed=[s for s in sorted(common) if x[s]!=y[s]]
    relocation_changes=[s for s in sorted(common) if rx.get(s,[])!=ry.get(s,[])]
    expected=['.text._GLOBAL__sub_I_setup'] if name=='sketch/app.ino.cpp.o' else []
    assert changed==expected,(name,changed)
    assert relocation_changes==expected,(name,relocation_changes)
    assert not y.keys()-x.keys(),name
    sections_checked+=len(common)
    relocations_checked+=sum(len(ry.get(s,[])) for s in common if s not in changed)
    details.append(dict(path=name,common_sections=len(common),changed_sections=changed,
        relocation_changes=relocation_changes,removed_sections=sorted(x.keys()-y.keys())))

for owner in (a,b):
    for record in owner['records']:
        for k,v in record.items():
            if isinstance(v,dict) and 'returncode' in v:
                assert v['returncode']==0,(k,v['returncode'])
    for name,record in owner['metadata'].items():
        payload=record['text'].encode()
        assert len(payload)==record['bytes'],name
        assert hashlib.sha256(payload).hexdigest()==record['sha256'],name
    assert not owner['math_missing']
    for key in ('native_exports','math_exports'):
        record=owner[key]
        assert record['returncode']==0
        values=re.findall(r'^\$\d+ = (0x[0-9a-f]+)$',record['stdout'],re.M)
        count=len(owner['native_names']) if key=='native_exports' else len(owner['math_symbols'])
        assert len(values)==count and all(int(v,16)>0 for v in values),(key,values)

assert a['math_aliases']==b['math_aliases']
assert a['math_exports']['stdout']==b['math_exports']['stdout']
assert a['base_static_threads']==b['base_static_threads']
undefined_a=set(a['records'][0]['undefined']['stdout'].split())-{'U','w'}
undefined_b=set(b['records'][0]['undefined']['stdout'].split())-{'U','w'}
assert not undefined_b-undefined_a
result=dict(scope='Comparison of actual captured object section bytes digests and relocation records',
    target_receipt_sha256=dict(control=ah,candidate=bh),source_files=len(a['source_files']),
    unchanged_loader=a['base_sha256'],common_objects=len(objects_b),
    candidate_expanded_compile_commands=len(candidate_commands),
    unchanged_generated_sketch_sha256=b['metadata']['sketch/app.ino.cpp']['sha256'],
    candidate_dependency_files_without_removed_libraries=sum(n.endswith('.d') for n in b['metadata']),
    removed_objects=sorted(objects_a.keys()-objects_b.keys()),
    common_alloc_sections_checked=sections_checked,unchanged_relocations_checked=relocations_checked,
    metadata_payloads_checked=len(a['metadata'])+len(b['metadata']),
    control_imports=len(undefined_a),candidate_imports=len(undefined_b),
    removed_imports=sorted(undefined_a-undefined_b),added_imports=sorted(undefined_b-undefined_a),
    control_native_names=a['native_names'],candidate_native_names=b['native_names'],
    retained_math_aliases=b['math_aliases'],details=details)
result['reviewer_harness_correction']='The phase-flag command assertion initially included unchanged assembly tls-syms.S, whose installed recipe does not consume discovery flags. The assertion now covers all C/C++ commands; the assembly object remains in the common-object byte/relocation comparison.'
(OUT/'object_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('details','control_native_names','candidate_native_names','retained_math_aliases')},indent=2))
