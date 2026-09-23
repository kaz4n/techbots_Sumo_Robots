"""Compare startup machine words and relocations, allowing only image address movement."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).parent
old = json.loads((ROOT / 'state/analysis/P2_app_runtime_raw/target_4cb637f9_bench-default.json').read_text())['records'][0]
new = json.loads((ROOT / 'state/analysis/P2_imu_fault_access_raw/target_570ef35f_bench-default.json').read_text())['records'][0]
def function(r, name):
    match = re.search(r'^([0-9a-f]+) ([0-9a-f]+) [tTwW] ' + re.escape(name) + '$', r['sizes']['stdout'], re.M)
    assert match, name
    start, size = map(lambda s:int(s,16), match.groups())
    block = re.search(r'^' + format(start, '08x') + ' <' + re.escape(name) + r'>:(.*?)(?=\n[0-9a-f]+ <|\Z)', r['disassembly'], re.S | re.M)
    assert block
    words = re.findall(r'^\s*[0-9a-f]+:\s+((?:[0-9a-f]{4,8}\s+)+)\s*\S', block[1], re.M)
    text_reloc = re.search(r"Relocation section '\.rel.text'.*?(?=\nRelocation section|\Z)", r['relocations']['stdout'], re.S)
    relocations=[]
    for line in text_reloc[0].splitlines():
        parts=line.split()
        if len(parts)<5 or not parts[2].startswith('R_ARM_'): continue
        addr=int(parts[0],16)
        if start<=addr<start+size: relocations.append([addr-start,parts[2],parts[4]])
    return dict(size=size,machine_words=[' '.join(v.split()) for v in words],relocations=relocations)
names=('setup','loop','main','__loopHook()','_GLOBAL__sub_I_setup')
checks={}
for name in names:
    a,b=function(old,name),function(new,name)
    assert a==b, name
    checks[name]=b
getter=function(new,'imu::Acquirer::setupFailure() const')
callback=function(new,'app::NativeSources::imuSetupFailure(void*, unsigned int)')
assert {r[2] for r in getter['relocations']} == {'memcpy','memset'}
assert {r[2] for r in callback['relocations']} == {'_ZNK3imu8Acquirer12setupFailureEv'}
out=RAW/'startup_comparison.json'
assert not out.exists()
out.write_text(json.dumps(dict(scope='Same startup words and relocation targets after adjusting symbol start addresses',
                              startup=checks, getter=getter, callback=callback),indent=2)+'\n')
print(json.dumps(dict(startup_unchanged=list(checks),getter_bytes=getter['size'],getter_dependencies=getter['relocations'],callback_dependencies=callback['relocations']),indent=2))
