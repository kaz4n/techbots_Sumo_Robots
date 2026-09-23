from pathlib import Path
import json,hashlib
root=Path.cwd();raw=root/'state/analysis/P2_tick_timing_raw'
d=json.loads((raw/'target_5451e99d_bench-default.json').read_text())
checks=[]
for p,h in d['source_files'].items():
    origin=root/p if p.startswith(('src/core/','src/hal/')) or p=='src/config.h' else root/'bench/p2_dump_compile'/p
    assert hashlib.sha256(origin.read_bytes()).hexdigest()==h,origin
checks.append('All72 physical source files exactly match retained target file map')
records=[]
for r in d['records']:
    symbols='\n'.join(r['nm'])
    required=['validTimingStart','validTimingReceipt','Robot::receiveTiming','Robot::step','__loopHook']
    assert all(x in symbols for x in required),r['path']
    selected=[line for line in r['nm'] if any(v in line for v in required)]
    result=dict(path=r['path'],sha256=r['sha256'],bytes=r['bytes'],symbols=selected)
    if 'disassembly' in r:
        lines=r['disassembly'].splitlines()
        for i,line in enumerate(lines):
            if '<__loopHook()>:' in line:
                result['hook_disassembly']=lines[i:i+4]
                assert 'bx\tlr' in lines[i+1],lines[i:i+4]
        assert 'hook_disassembly' in result
    records.append(result)
assert d['returncode']==0 and len(records)==3 and not d['math_missing']
assert d['source_files']['src/core/fsm_robot.cpp']=='0e1ddb2057e0cc412529c2c8f1d77e1519edc5243847c0950fc6cda07e9f4e2d'
old=json.loads((root/'state/analysis/P2_dump_raw/target_b8bb9366_bench-default.json').read_text())
assert d['base_sha256']==old['base_sha256']
assert d['native_names']==old['native_names']
assert d['math_symbols']==old['math_symbols']
for current,previous in zip(d['records'],old['records']):
    assert set(current['undefined']['stdout'].splitlines())==set(previous['undefined']['stdout'].splitlines())
checks.append('Loader hash, all3 undefined importsets,40 native names and42 AEABI mappings identical to reviewed D090')
result=dict(source=d['source_sha256'],file_count=len(d['source_files']),loader_sha256=d['base_sha256'],records=records,checks=checks,native_count=len(d['native_names']),aeabi_count=len(d['math_symbols']),hardware_action='none; inspected saved Linux compile-only receipts')
(root/'state/reviews/P2_tick_timing_review_raw/target_review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
