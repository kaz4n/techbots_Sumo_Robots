# Verifies prospective run identity and coordinator ordering using host substitutes.
# Never executes the coordinator with real process, board or network operations.
# Exclusive evidence binds current software, immutable inputs and five failure cases.
from contextlib import ExitStack
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest import mock

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4]
RAW=ROOT/'state/analysis/P2_app_default_probe_raw'
sys.path.insert(0,str(ROOT/'tools'))
import app_default_run as guard

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

out=Path(__file__).parent/sys.argv[1]
out.mkdir(exist_ok=False)
receipt=dict(started_utc=datetime.now(timezone.utc).isoformat(),scope='LOCAL_FILES_GIT_AND_MOCKED_COORDINATOR_ONLY_NO_BOARD')
try:
    request=json.loads((RAW/'run01_review_request.json').read_text())
    git=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],capture_output=True,text=True,check=True,timeout=10)
    assert git.stdout.strip()==request['software_commit']=='9b4afcb22823ce48cb20cb4cb951cd55229ac1f2'
    receipt['head']=git.stdout.strip()
    receipt['git_head']=dict(argv=git.args,returncode=git.returncode,stdout=git.stdout,stderr=git.stderr)
    assert digest(RAW/'execute_run01.py')==request['coordinator_script_sha256']=='05648dbe42db6ab0ac21006978379644be52f6d71c3627ebd8d82075c4854e7f'
    hashes={name:digest(ROOT/name) for name in guard.FILES}
    receipt['file_sha256']=hashes
    assert hashes['tools/app_default_run.py']=='7fbeceb269912321b3b06c2b9ea9cace466c2faf4f06bebf6ec1d4ebf4d5da58'
    assert hashes['tools/app_default_capture.py']=='beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1'
    assert hashes['tools/p0_inert_sources.json']==guard.MANIFEST_HASH
    manifest=json.loads((ROOT/'tools/p0_inert_sources.json').read_text())
    assert len(manifest)==9 and 'app' not in manifest
    pins=json.loads((RAW/'preflight/guard_route/source_pin_proposal.json').read_text())['staged_relative_sha256']
    combined=hashlib.sha256()
    for name,expected in sorted(pins.items()):
        local='src/app/app.ino' if name=='app.ino' else name
        blob=(ROOT/local).read_bytes()
        assert hashlib.sha256(blob).hexdigest()==expected
        combined.update(name.encode()+b'\0'); combined.update(blob)
    assert len(pins)==91 and combined.hexdigest()==guard.SOURCE==request['source_sha256']
    receipt.update(source_files=len(pins),source_sha256=combined.hexdigest())
    artifact=ROOT/'state/analysis/P2_dump_fifo_raw/target_e820c0e1_bench-default'
    receipt['artifacts']={}
    for name,key in [('app.ino.elf','elf_sha256'),('app.ino.elf-zsk.bin','binary_sha256')]:
        p=artifact/name
        assert p.stat().st_size==176048 and digest(p)==request[key]
        receipt['artifacts'][name]=dict(bytes=p.stat().st_size,sha256=digest(p))
    receipt['references']={name:digest(ROOT/name) for name in request['references']}
    receipt['coordinator_sha256']=digest(RAW/'execute_run01.py')
    capture_input=json.loads((RAW/'preflight/capture_input_staging.json').read_text())
    deployment=json.loads((RAW/'preflight/capture_tool_deployment.json').read_text())
    assert capture_input['target']==deployment['target']==guard.TARGET
    assert capture_input['returncode']==0 and all(c['returncode']==0 for c in deployment['commands'])
    assert deployment['actual_sha256']==deployment['files']
    for name,expected in deployment['files'].items(): assert digest(ROOT/'tools'/name)==expected
    for value in capture_input['result']['files']:
        assert value['bytes']==176048 and digest(artifact/Path(value['path']).name)==value['sha256']
    receipt['staging_receipts_verified']=True
    assert not (ROOT/guard.ATTEMPT).exists() and not (ROOT/guard.OUTCOME).exists()
    assert not (RAW/'run01_execution_intent.json').exists() and not (RAW/'run01_capture_attempt.json').exists()
    protected=['src','tests/locked','tools/board_tool.py','tools/app_build_policy.py','tools/app_build_pins.json','tools/app_build_commands.json','tools/p0_capture.py','tools/recorder_heap.py','tools/p0_mem_read.cfg','tools/p0_inert_sources.json']
    diff=subprocess.run(['git','-C',str(ROOT),'diff','--exit-code','HEAD','--',*protected],capture_output=True,text=True,check=True,timeout=10)
    receipt['protected_diff']=dict(argv=diff.args,returncode=diff.returncode,stdout=diff.stdout,stderr=diff.stderr)
    spec=importlib.util.spec_from_file_location('reviewed_coordinator',RAW/'execute_run01.py')
    coordinator=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(coordinator)
    receipt['coordinator_probes']=[]
    for mode in ('success','guard_failure','capture_nonzero','capture_timeout','capture_launch_failure'):
        with tempfile.TemporaryDirectory(prefix='d118-run-review-') as directory,ExitStack() as stack:
            folder=Path(directory)
            local_calls=[]; remote_calls=[]
            scope=dict(head_commit=receipt['head'],run_record_sha256='a'*64,review_sha256='b'*64)
            stack.enter_context(mock.patch.dict(os.environ,{'LOCALAPPDATA':'/SYNTHETIC'},clear=True))
            stack.enter_context(mock.patch.object(coordinator,'ROOT',folder/'project'))
            stack.enter_context(mock.patch.object(coordinator,'RAW',folder))
            stack.enter_context(mock.patch.object(coordinator.guard,'load_scope',return_value=scope))
            def local(argv,**kwargs):
                local_calls.append(argv)
                assert argv[-2:]==['--run-id',guard.RUN_ID]
                assert (folder/'run01_execution_intent.json').exists()
                if mode!='guard_failure':
                    (folder/'run01_upload_outcome.json').write_text(json.dumps(dict(run_id=guard.RUN_ID,returncode=0,error=None)))
                return SimpleNamespace(returncode=1 if mode=='guard_failure' else 0)
            def remote(target,argv,**kwargs):
                remote_calls.append(argv)
                assert target==guard.TARGET and kwargs==dict(capture=True,timeout=620)
                assert (folder/'run01_capture_attempt.json').exists()
                assert argv[:3]==['python3','-B','-c']
                assert coordinator.INPUTS in argv[3] and coordinator.OUTPUT in argv[3]
                assert coordinator.COLLECTOR in argv[3]
                if mode=='capture_nonzero': raise subprocess.CalledProcessError(7,argv,output='nonzero out',stderr='nonzero err')
                if mode=='capture_timeout': raise subprocess.TimeoutExpired(argv,620,output=b'partial\xff',stderr=b'late')
                if mode=='capture_launch_failure': raise OSError('synthetic launch failure')
                return SimpleNamespace(returncode=0,stdout='captured',stderr='')
            stack.enter_context(mock.patch('subprocess.run',side_effect=local))
            stack.enter_context(mock.patch('subprocess.Popen',side_effect=AssertionError('real subprocess forbidden')))
            stack.enter_context(mock.patch('socket.create_connection',side_effect=AssertionError('real network forbidden')))
            stack.enter_context(mock.patch.object(coordinator.board,'remote',side_effect=remote))
            try: code=coordinator.main(); error=None
            except (subprocess.TimeoutExpired,OSError) as value: code=None; error=type(value).__name__
            assert len(local_calls)==1 and len(remote_calls)==(0 if mode=='guard_failure' else 1)
            if mode=='success': assert code==0
            if mode=='guard_failure': assert code==1 and not (folder/'run01_capture_attempt.json').exists()
            if mode=='capture_nonzero': assert code==7
            if mode=='capture_timeout':
                assert error=='TimeoutExpired'
                assert (folder/'run01_capture_stdout.txt').read_text()=='partial\ufffd'
            if mode=='capture_launch_failure': assert error=='OSError'
            outcome=json.loads((folder/'run01_execution_outcome.json').read_text())
            try: coordinator.main()
            except FileExistsError: pass
            else: raise AssertionError('coordinator replay unexpectedly accepted')
            assert len(local_calls)==1 and len(remote_calls)==(0 if mode=='guard_failure' else 1)
            receipt['coordinator_probes'].append(dict(mode=mode,passed=True,local_guard_calls=len(local_calls),capture_calls=len(remote_calls),status=outcome['status'],returncode=code,error=error))
    receipt['successful']=True
except BaseException as error:
    receipt.update(successful=False,error=repr(error))
    raise
finally:
    receipt['finished_utc']=datetime.now(timezone.utc).isoformat()
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(successful=receipt['successful'],source_files=receipt['source_files'],coordinator_probes=receipt['coordinator_probes']),indent=2))
