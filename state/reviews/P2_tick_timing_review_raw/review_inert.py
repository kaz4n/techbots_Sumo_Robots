from pathlib import Path
import hashlib,json,subprocess,sys
root=Path.cwd(); sys.path.insert(0,str(root/'tools'))
import board_tool as board
out=root/'state/reviews/P2_tick_timing_review_raw'
registered=json.loads((root/'tools/p0_inert_sources.json').read_text())
baseline=json.loads(subprocess.check_output(['git','show','a57d3b7:tools/p0_inert_sources.json']))
assert set(registered)==set(baseline) and len(registered)==7
rows=[]
for key,old_hash in baseline.items():
    folder=board.stage(key)
    digest=hashlib.sha256(); differences=[]; files={}
    for file in sorted(p for p in folder.rglob('*') if p.is_file()):
        rel=file.relative_to(folder).as_posix()
        origin=rel if rel.startswith(('src/core/','src/hal/')) or rel=='src/config.h' else key+'/'+rel
        old=subprocess.check_output(['git','show','a57d3b7:'+origin])
        digest.update(rel.encode()+b'\0');digest.update(old)
        current=file.read_bytes()
        files[rel]=hashlib.sha256(current).hexdigest()
        if current!=old: differences.append(origin)
    assert digest.hexdigest()==old_hash,(key,'prior registry is not baseline',digest.hexdigest(),old_hash)
    assert set(differences)=={'src/core/fsm.h','src/core/fsm_robot.cpp'},(key,differences)
    rows.append(dict(key=key,old_sha256=old_hash,new_sha256=board.source_hash(folder),files=files,changes=differences))
result=dict(baseline='a57d3b7',scope='Existing seven inert source keys only; local staging, no registry write or upload authority',rows=rows)
(out/'inert_source_review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([{k:v for k,v in row.items() if k!='files'} for row in rows],indent=2))
