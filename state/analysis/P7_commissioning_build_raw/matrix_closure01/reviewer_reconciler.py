"""Read-only reconciliation of closed D222 native evidence; writes only Temp summary."""
import ast
import base64
import hashlib
import json
import pathlib
import shlex
import subprocess
import tempfile

ROOT = pathlib.Path('C:/Users/narut/OneDrive/Desktop/Project/techbots_Sumo_Robots')
RAW = ROOT / 'state/analysis/P7_commissioning_build_raw'
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
BASE = 'ee1bdcedf412903445c5076cae5980a43e0dc34e'
PROFILES = dict(b4_stand=(0,), p3_drive=(1,), p3_turn=(2,), p3_stop=(3,), p4_reactive=(4,), p4_timing=(4,5), p5_abort_timing=(6,))
MACROS = ('SUMOX_B4_STAND','SUMOX_P3_DRIVE_TEST','SUMOX_P3_TURN_TRIAL','SUMOX_P3_STOP_TRIAL','SUMOX_P4_REACTIVE','SUMOX_TIMING_EVIDENCE','SUMOX_P5_ABORT_TIMING','SUMOX_MOTOR_FAULT_PROBE')
CHECKS = ('local','identity','initialization','builtins','remote_sources','installed_pins','overrides','artifacts','artifact_sources')
SUFFIXES = ('.elf','_debug.elf','_temp.elf','.bin','.bin-zsk.bin','.elf-zsk.bin','.map')
def read(p): return json.loads(p.read_bytes())
def sha(raw): return hashlib.sha256(raw).hexdigest()
def git(*args, data=None):
    r=subprocess.run(['git','-C',str(ROOT),*args],input=data,capture_output=True,check=True)
    assert not r.stderr, r.stderr
    return r.stdout
def current_head_inputs(value):
    names=sorted(value['files']); head=value['reviewed_head']
    body=git('cat-file','--batch',data=''.join(head+':'+n+'\n' for n in names).encode())
    pos=0
    for name in names:
        end=body.index(b'\n',pos); fields=body[pos:end].split(); assert fields[1]==b'blob'
        size=int(fields[2]); raw=body[end+1:end+1+size];pos=end+size+2
        assert body[pos-1:pos]==b'\n'
        assert sha(raw)==value['files'][name] and (ROOT/name).read_bytes()==raw,name
    assert pos==len(body)
    return len(names)
def flags(profile,motors):
    return ' '.join(['-DMATCH=0','-DMOTORS_ALLOWED='+str(motors)]+['-D'+name+'='+str(int(i in PROFILES[profile])) for i,name in enumerate(MACROS)])

rows=[]; previous_commit=BASE; previous_finished=None
for profile in PROFILES:
  for motors in (0,1):
    p=RAW/f'commission-{profile}-m{motors}-e9e91397f42f'
    if not (p/'result.json').exists(): continue
    result=read(p/'result.json'); intent=read(p/'intent.json'); inputs=read(p/'inputs.json'); packet=read(p/'artifacts.json')
    label=f'{profile}/M{motors}'; selected=flags(profile,motors)
    assert result['status']=='COMPILE_CHECKED' and result['first_error'] is None,label
    assert result['reviewed_head']==previous_commit,(label,'commit sequence')
    assert previous_finished is None or result['started_utc']>=previous_finished,(label,'overlap')
    for v in (result,intent,inputs,packet):
        assert v['profile']==profile and type(v['motors_allowed']) is int and v['motors_allowed']==motors,label
        assert v['attempt']=='native01' and v['source_sha256']==SOURCE,label
    for v in (result,intent,inputs):assert v['boot_id']==BOOT and v['reviewed_head']==result['reviewed_head'],label
    for v in (result,intent,packet['layout']):assert v['flags']==selected and v['fqbn']=='arduino:zephyr:unoq:link_mode=static' and v['project']=='app.ino',label
    assert sha((p/'inputs.json').read_bytes())==intent['inputs_sha256'],label
    count=current_head_inputs(inputs)
    assert (result['query_calls'],result['compiler_calls'],result['transport_calls'])==(1,1,25),label
    assert result['final_checks']==[dict(name=n,status='PASS',error=None) for n in CHECKS],label
    stage=pathlib.Path(intent['stage']); staged=read(p/'staged_files.json'); digest=hashlib.sha256()
    for name in sorted(staged):
        raw=(stage/name).read_bytes();assert sha(raw)==staged[name],(label,name)
        digest.update(name.encode()+b'\0');digest.update(raw)
    assert digest.hexdigest()==SOURCE and len(staged)==104,label
    folders=sorted(d for d in p.iterdir() if d.is_dir() and d.name[:4].isdigit())
    assert len(folders)==25 and [int(d.name[:4]) for d in folders]==list(range(1,26)),label
    children=[]; units=[]
    for d in folders:
        transport=read(d/'result.json'); start=read(d/'intent.json')
        assert transport['returncode']==0 and not (d/'stderr').read_bytes(),(label,d.name)
        assert all(transport[k]==start[k] for k in start),label
        assert transport['argv'][1:5]==['-s','2629958581','shell','-T'],label
        command_units=len(subprocess.list2cmdline(transport['argv']).encode('utf-16-le'))//2+1
        assert command_units==transport['command_units']<=30000,label
        units.append(command_units)
        if (d/'remote_result.json').exists():
            child=read(d/'remote_result.json');assert child==read(d/'stdout'),label
            assert child['status']=='COMPLETED' and child['execution']==dict(returncode=0,timed_out=False,reaped=True),label
            assert not set(child)&{'error','stream_errors'},label
            for stream in ('stdout','stderr'):
                raw=base64.b64decode(child[stream+'_base64'],validate=True)
                assert len(raw)==child[stream+'_bytes'] and raw==(d/('child.'+stream)).read_bytes(),label
            assert not any(a in ('upload','--upload','reset','monitor') for a in child['argv']),label
            children.append(child)
    compilers=[c for c in children if c['argv'][0]=='/usr/bin/arduino-cli' and 'compile' in c['argv']]
    assert len(children)==9 and len(compilers)==2,label
    assert [('--show-properties=expanded' in c['argv']) for c in compilers]==[True,False],label
    for c in compilers:
        a=c['argv'];assert a[a.index('--jobs')+1]=='1' and a[-1]==intent['sketch'],label
        assert 'compiler.cpp.extra_flags='+selected in a and 'compiler.c.extra_flags='+selected in a,label
        assert c['deadline_seconds']==(60 if '--show-properties=expanded' in a else 720),label
    for name,child in zip(('properties','compile'),compilers):
        v=read(p/'compile'/f'{name}.stdout.json')
        child_raw=base64.b64decode(child['stdout_base64'])
        assert (p/'compile'/f'{name}.stdout.json').read_bytes()==child_raw.replace(b'\n',b'\r\n'),label
        assert v['success'] is True and v['upload_result']=={},label
        props=v['builder_result']['build_properties'];pairs=[x.split('=',1) for x in props];m=dict(pairs)
        assert len(m)==len(pairs),label
        expected={'build.boot_mode':'wait','build.link_mode':'static','build.fqbn':'arduino:zephyr:unoq:link_mode=static','build.project_name':'app.ino','build.path':packet['build_path'],'build.source.path':intent['sketch'],'compiler.cpp.extra_flags':selected,'compiler.c.extra_flags':selected}
        assert all(m[k]==v for k,v in expected.items()),label
    for d in ('0001-identity','0007-identity','0018-identity'):
        v=read(p/d/'stdout');assert v['boot_id']==BOOT and v['uid']==1000 and v['user']=='arduino' and v['conflicts']==[] and v['free_bytes']>=1073741824,label
    for a,b in (('0002-cli_initialization_inventory','0019-cli_initialization_inventory'),('0003-cli_builtin_files_inventory','0020-cli_builtin_files_inventory'),('0006-source-set','0021-source-set')):
        assert read(p/a/'stdout')==read(p/b/'stdout'),(label,a)
    assert read(p/'0006-source-set/stdout')==staged,label
    assert read(p/'0017-artifacts/stdout')==packet==read(p/'0024-artifacts-final/stdout'),label
    assert read(p/'0016-artifact-source-second/stdout')==read(p/'0025-artifact-sources-final/stdout'),label
    assert packet['status']=='ARTIFACTS_CHECKED' and packet['first_error'] is None,label
    assert packet['postchecks']==[dict(name=n,status='PASS',error=None) for n in ('loader','tls_source','files')],label
    layout=packet['layout'];native=layout['validator_report'];files=packet['files']
    assert layout['status']=='STATIC_COMMISSIONING_APP_LAYOUT_PACKAGE_PASS' and native['status']=='STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS',label
    assert set(files)=={'build/app.ino'+s for s in SUFFIXES}|{'artifacts/app.ino.bin-zsk.bin'},label
    for suffix in SUFFIXES:
        n='app.ino'+suffix;r=files['build/'+n]
        assert r['state']=='regular' and r['identity']['bytes']>0 and len(r['sha256'])==64,label
        assert layout['artifact_aliases'][n]==n and layout['artifact_sha256'][n]==r['sha256'],label
        assert native['artifacts'][n]==dict(bytes=r['identity']['bytes'],sha256=r['sha256']),label
    for key in ('sha256',):assert files['artifacts/app.ino.bin-zsk.bin'][key]==files['build/app.ino.bin-zsk.bin'][key],label
    assert files['artifacts/app.ino.bin-zsk.bin']['identity']['bytes']==files['build/app.ino.bin-zsk.bin']['identity']['bytes'],label
    for role,digest_value in (('loader','39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'),('tls_source','68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70')):assert packet[role]['sha256']==digest_value,label
    assert native['native_tls']['loader_sha256']==packet['loader']['sha256'] and native['native_tls']['source_sha256']==packet['tls_source']['sha256'],label
    assert native['entry']==0x08100011 and native['weak_undefined']==[],label
    for kind,start,end in (('flash',0x08100010,0x081C0000),('ram',0x20013890,0x20053890)):
        interval=native[kind];assert interval['start']==start and start<=interval['end']<=end and interval['remaining']==end-interval['end'],label
    rel=(p/'result.json').relative_to(ROOT).as_posix()
    commit=git('log','-1','--format=%H','--',rel).decode().strip();assert commit,label
    assert git('rev-parse',commit+'^').decode().strip()==result['reviewed_head'],label
    changed=git('diff-tree','--no-commit-id','--name-only','-r',commit).decode().splitlines()
    unrelated=[n for n in changed if not n.startswith(p.relative_to(ROOT).as_posix()+'/') and n not in ('state/PROGRESS.md','state/DECISIONS.md','state/FACTS.md','state/STORAGE_LOG.md')]
    assert not unrelated,(label,unrelated)
    rows.append(dict(profile=profile,motors=motors,owner=p.name,reviewed_head=result['reviewed_head'],evidence_commit=commit,input_files=count,staged_files=len(staged),transports=len(folders),children=len(children),query=1,compiler=1,closing=9,max_command_units=max(units),elf=files['build/app.ino.elf'],package=files['build/app.ino.bin-zsk.bin'],ram_remaining=native['ram']['remaining'],flash_remaining=native['flash']['remaining'],result_sha256=sha((p/'result.json').read_bytes()),artifacts_sha256=sha((p/'artifacts.json').read_bytes()),started=result['started_utc'],finished=result['finished_utc']))
    previous_commit=commit;previous_finished=result['finished_utc']
summary=dict(status='CLOSED_RECEIPTS_RECONCILED',closed=len(rows),source=SOURCE,base=BASE,last_evidence_commit=previous_commit,rows=rows,limits='No board calls, tests, raw target artifact retrieval, separate outer check-only receipt, runtime or physical qualification. Current/head/stage bytes and retained native command/artifact reports reconciled.')
out=pathlib.Path(tempfile.gettempdir())/'sumox_d222_actual_review_summary.json'
out.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=summary['status'],closed=len(rows),summary=str(out),sha256=sha(out.read_bytes()),max_command_units=max(r['max_command_units'] for r in rows),rows=[dict(profile=r['profile'],motors=r['motors'],elf=r['elf']['sha256'][:12],package=r['package']['sha256'][:12],ram_remaining=r['ram_remaining'],head=r['reviewed_head'][:8]) for r in rows]),indent=2))
