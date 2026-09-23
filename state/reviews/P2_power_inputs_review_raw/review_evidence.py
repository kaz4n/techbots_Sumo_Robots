"""Freeze inspected final coordinator/author receipts without rerunning hardware."""
from pathlib import Path
import hashlib,json,re
root=Path.cwd(); out=root/'state/reviews/P2_power_inputs_review_raw'; raw=root/'state/analysis/P2_power_inputs_raw'
author=json.loads((raw/'author/final_sha256.json').read_text())
for path,digest in author.items(): assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
frozen=json.loads((out/'frozen_source.json').read_text())
for path,digest in frozen['snapshot'].items(): assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
receipts={}
for name in ['full_host_include_retry1','full_sanitizer_include_retry1','target_compile','target_audit','source_audit','tools_regression']:
    receipt=json.loads((raw/(name+'.json')).read_text()); assert receipt['returncode']==0,name
    receipts[name]=dict(receipt=receipt,output_sha256=hashlib.sha256((raw/(name+'.txt')).read_bytes()).hexdigest())
for folder,name in [('host','full_host_lasttest.txt'),('host-sanitize','full_sanitizer_lasttest.txt')]:
    data=(root/'build'/folder/'Testing/Temporary/LastTest.log').read_bytes()
    text=data.decode(); assert '1327 |     1327 passed' in text and '111 |     111 passed' in text
    assert '24484165 | 24484165 passed' in text and '3850460 | 3850460 passed' in text
    assert text.count('Test Passed.')==2
    (out/name).write_bytes(data)
flags=(root/'build/host-sanitize/CMakeFiles/sumox26_tests.dir/flags.make').read_bytes()
assert b'-fsanitize=address,undefined' in flags
(out/'sanitizer_flags.txt').write_bytes(flags)
commands=[json.loads(line) for line in (raw/'author/commands.jsonl').read_text().splitlines()]
final={}
for row in commands:
    if '--no-colors' in row['argv']: final[Path(row['argv'][0]).name]=row
expected=['native','limits','probe0','probe1','host0','host1']+['config_case'+str(i) for i in range(15)]
for name in expected: assert final[name]['returncode']==0,name
summary={name:[line for line in final[name]['stdout'].splitlines() if 'test cases:' in line or 'assertions:' in line] for name in expected}
refusals=[json.loads(line) for line in (raw/'author/upload_refusals.jsonl').read_text().splitlines()]
assert len(refusals)==8 and all(not r['target_calls'] and not r['remote_calls'] and not r['transport_calls'] for r in refusals)
registry=[json.loads(line) for line in (raw/'author/registry.jsonl').read_text().splitlines()]
assert registry[-1]['success']
target=json.loads((raw/'target_4d5e21cc_bench-default.json').read_text())
relocs=target['records'][0]['relocations']['stdout']
selected=[line for line in relocs.splitlines() if line.startswith(('0000cf18','0000cf1c','0000cf28','0000cf2c','0000c4b8','0000c4bc','0000c4c0'))]
assert len(selected)==7
(out/'startup_relocations.txt').write_text('\n'.join(selected)+'\n')
result=dict(status='PASS_FINAL_D093_SOFTWARE_EVIDENCE',author_final_sha256=author,
            coordinator_receipts=receipts,author_final_runs=summary,
            preserved_author_failed_commands=sum(r['returncode']!=0 for r in commands),
            upload_refusals=len(refusals),registry_wrapper=registry[-1],
            scope='No current-image runtime or physical/gate claim')
(out/'evidence_review.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['status'])
