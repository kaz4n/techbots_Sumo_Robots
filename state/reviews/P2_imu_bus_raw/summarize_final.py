"""Counts completed independent replay receipts without changing prior evidence."""
from pathlib import Path
import hashlib,json,re
OUT=Path(__file__).resolve().parent
folder=OUT/'native_1790149071791499865'
full=json.loads((folder/'full_unittest.json').read_text())
receipts=[];cases=assertions=0;sentinels=[]
for path in sorted(folder.glob('native_imu_bus_*.json')):
    data=json.loads(path.read_text())
    receipts.append(dict(path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),returncode=data['returncode']))
    if data['returncode']:
        assert data['returncode']==1 and any(arg in ('--test-case=*assertion*','--test-case=*signal*') for arg in data['argv'])
        assert 'Status: FAILURE!' in data['stdout'];sentinels.append(path.name)
    elif 'Status: SUCCESS!' in data['stdout']:
        counts=re.search(r'test cases:\s*(\d+)\s*\|\s*(\d+) passed\s*\|\s*0 failed\s*\|\s*0 skipped',data['stdout'])
        checks=re.search(r'assertions:\s*(\d+)\s*\|\s*(\d+) passed\s*\|\s*0 failed',data['stdout'])
        assert counts and checks and counts[1]==counts[2] and checks[1]==checks[2]
        cases+=int(counts[1]);assertions+=int(checks[1])
assert full['returncode']==0 and full['manifest_unchanged'] and len(sentinels)==2
result=dict(unittest_methods=10,seconds=full['seconds'],returncode=full['returncode'],manifest_unchanged=full['manifest_unchanged'],
    subprocesses=len(receipts),positive_native_cases=cases,parent_doctest_assertions=assertions,
    assertion_count_note='Forked child checks propagate failure but are not included in parent doctest totals',
    expected_failure_sentinels=sentinels,receipts=receipts)
(OUT/'final_receipt_summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='receipts'}))
