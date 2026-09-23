"""Independently check locally captured D088 raw bytes, identities and scalar progress."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import struct

OUT=Path(__file__).resolve().parent
RAW=OUT.parent
report=json.loads((RAW/'runtime_report.json').read_text())
folder=RAW/'runtime_run1'
assert report==json.loads((folder/'capture.json').read_text())
assert report['status']=='COUNTER-ADVANCED'
assert report['flash_identity_verified'] and report['extension_confirmed_after_counters']
assert len(report['reads'])==9 and len(report['commands'])==13
assert 0<report['capture_duration_seconds']<120
for command in report['commands']:
    assert command['returncode']==0 and not command.get('timeout')
    for field in ('stdout','stderr'):
        data=(folder/command[field+'_file']).read_bytes()
        assert command[field]==data[:65536].decode('utf-8',errors='replace')
        assert command[field+'_truncated']==(len(data)>65536)
    if '-c' in command['argv']:
        assert len(command['argv'])==7
        assert command['argv'][3]=='-c' and command['argv'][5:] == ['-c','shutdown']
        assert re.fullmatch(r'dump_image \{[^{}]+\} 0x[0-9a-f]{8} [0-9]+',command['argv'][4])
byfile={}
for item in report['reads']:
    data=(folder/item['file']).read_bytes()
    assert len(data)==item['size']
    assert hashlib.sha256(data).hexdigest()==item['sha256']
    byfile[item['file']]=(item,data)
loader=byfile['00-loader.bin'];sketch=byfile['01-sketch.bin']
assert (loader[0]['address'],len(loader[1]))==(0x08000000,263680)
assert hashlib.sha256(loader[1]).hexdigest()=='e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2'
assert hashlib.sha256(loader[1]).hexdigest()==report['loader_identity']['expected_sha256']
assert loader[1]==(RAW.parents[0]/'P0_qtr_run1_raw/00-loader.bin').read_bytes()
assert (sketch[0]['address'],len(sketch[1]))==(0x08100000,80592)
assert hashlib.sha256(sketch[1]).hexdigest()=='6de9d536572132fc8f4fa1d7962aecf15a479da7564221df4512944db2066a69'
listing=byfile['02-llext-list.bin'];node=byfile['03-node-1.bin']
assert listing[0]['address']==0x200017bc
head,tail=struct.unpack('<II',listing[1]);assert head==tail==node[0]['address']
assert struct.unpack_from('<I',node[1])[0]==0 and node[1][4:20].split(b'\0',1)[0]==b'sketch'
base=struct.unpack_from('<I',node[1],32)[0];size=struct.unpack_from('<I',node[1],92)[0]
assert size==0x1e1c and base==report['extension']['bss_address']
assert 0x20000000<=base and base+size<=0x200c0000
assert listing[1]==byfile['04-llext-list-confirm.bin'][1]==byfile['07-llext-list-after-counters.bin'][1]
final=byfile['08-sketch-node-after-counters.bin']
assert final[0]['address']==head
assert node[1][:20]+node[1][32:36]+node[1][92:96]==final[1][:20]+final[1][32:36]+final[1][92:96]
names=('magic','version','initialized','submissions','failures','scene','last_status','last_render','last_us','max_call_us')
snapshots=[]
for index,name in enumerate(('05-counter-first.bin','06-counter-second.bin')):
    item,data=byfile[name];assert item['address']==base+0x78 and len(data)==40
    values=dict(zip(names,struct.unpack('<10I',data)))
    assert values==report['counter_reads'][index]['values']
    assert (values['magic'],values['version'],values['initialized'],values['failures'],values['last_status'],values['last_render'])==(0x55494d58,1,1,0,2,0)
    assert values['scene']<12
    snapshots.append(values)
advance=(snapshots[1]['submissions']-snapshots[0]['submissions'])&0xffffffff
assert 0<advance<0x80000000 and advance==77
assert report['counter']==dict(first=3341,second=3418,advance=77)
first,second=report['counter_reads']
minimum=second['monotonic_start']-first['monotonic_end']
maximum=second['monotonic_end']-first['monotonic_start']
assert report['between_read_bounds_seconds']==dict(minimum=minimum,maximum=maximum)
assert 3.0<=minimum<=maximum
receipt=dict(status='PASS',checked_utc=datetime.now(timezone.utc).isoformat(),
    exact_local_report_copy=True,verified_raw_reads=9,verified_command_outputs=26,
    loader_expected_image_sha256=loader[0]['sha256'],loader_matches_prior_pinned_capture=True,
    exact_deployed_sketch_sha256=sketch[0]['sha256'],extension_mapping_unchanged=True,
    first=snapshots[0],second=snapshots[1],submission_advance=advance,
    between_read_bounds_seconds=dict(minimum=minimum,maximum=maximum),
    capture_duration_seconds=report['capture_duration_seconds'],
    interpretation='Actual pinned diagnostic execution and unconfirmed submission progress. No optical, calibrated clock, interrupt-mask timing, full-control WCET or external sensor claim. Multiword reads are not atomic; progress uses one aligned scalar. Board UTC and Windows UTC are not a shared chronology; bounds above are from one board monotonic clock.')
path=OUT/'runtime_identity.json';assert not path.exists()
path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2))
