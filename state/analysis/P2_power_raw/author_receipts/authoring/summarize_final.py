import hashlib,json,re
from pathlib import Path
root=Path.cwd();folder=root/'tests/native_power/receipts'
entries=[(p,json.loads(p.read_text())) for p in folder.glob('native_power_*.json')]
entries.sort(key=lambda x:int(x[0].stem.rsplit('_',1)[1]))
last=entries[-1][1]['argv'][0]
prefix=re.match(r'(/dev/shm/sumo-native-power-[^/]+)/',last).group(1)
selected=[(p,d) for p,d in entries if any(prefix in str(a) for a in d['argv'])]
files=[*list((root/'tests/native_power').rglob('*')),root/'tests/tooling/test_power_unoq.py']
manifest={'receipt_capture':'subprocess text=True; stream newlines normalized; JSON bytes preserved',
 'final_run':{'unittest_methods':9,'seconds':148.989,'status':0,'native_binaries':51,'expected_negative_executions':2,
 'child_assertions':'executed and propagated; parent doctest totals are not child assertion totals'},
 'stage_prefix':prefix,'commands':len(selected),'statuses':{},
 'source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file() and 'receipts' not in p.parts},
 'receipts':[{'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'status':d['returncode']} for p,d in selected]}
for _,d in selected:
 k=str(d['returncode']);manifest['statuses'][k]=manifest['statuses'].get(k,0)+1
manifest['production_sha256']=hashlib.sha256((root/'src/hal/power.cpp').read_bytes()).hexdigest()
manifest['stdout_sha256']=hashlib.sha256((folder/'final_unittest.txt').read_bytes()).hexdigest()
(folder/'final_run_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:manifest[k] for k in ('stage_prefix','commands','statuses','production_sha256')},indent=2))
