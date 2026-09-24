# Independently admits exact local live records without board or upload operations.
# The only admitted subprocess is the actual bounded local Git HEAD query.
# Records exact live hashes and absence of consumed attempts in an exclusive receipt.
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest import mock

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4]
RAW=ROOT/'state/analysis/P2_app_default_probe_raw'
sys.path.insert(0,str(ROOT/'tools'))
import app_default_run as guard

pins={
    guard.RUN_RECORD:'f7f1898c34d2954b8b06b6b9c677afae84378f03bacaed5fc54d40203bf4165d',
    guard.APPROVAL:'dca4b5cf20a6077b669fe2f0acd98e7badc82a7b3e1b202ed2deba7d593b0c7f',
    guard.REVIEW:'73269d225928f6de39d9c27fc9e64fe1b48b20136780025cc40b2157d329562e',
    'state/analysis/P2_app_default_probe_raw/execute_run01.py':'05648dbe42db6ab0ac21006978379644be52f6d71c3627ebd8d82075c4854e7f',
    'tools/app_default_run.py':'7fbeceb269912321b3b06c2b9ea9cace466c2faf4f06bebf6ec1d4ebf4d5da58',
    'tools/app_default_capture.py':'beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1',
}
receipt=dict(started_utc=datetime.now(timezone.utc).isoformat(),scope='FINAL_LOCAL_READ_ONLY_ADMISSION_NO_BOARD_NO_UPLOAD',run_id=guard.RUN_ID,git_checks=[])
original_run=subprocess.run
def local_git(argv,**kwargs):
    assert argv==['git','-C',str(ROOT),'rev-parse','HEAD']
    assert kwargs['timeout']==10 and kwargs['capture_output'] is True
    result=original_run(argv,**kwargs)
    receipt['git_checks'].append(dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr))
    return result

try:
    actual={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in pins}
    assert actual==pins
    receipt['file_sha256']=actual
    env=dict(SUMO_TRANSPORT='adb',SUMO_ADB_SERIAL=guard.TARGET,SUMO_REMOTE_ROOT=guard.REMOTE_ROOT)
    with mock.patch.dict(os.environ,env),mock.patch('subprocess.run',side_effect=local_git),mock.patch('socket.create_connection',side_effect=AssertionError('network forbidden')):
        scope=guard.load_scope(ROOT,guard.TARGET,'adb')
    assert scope['head_commit']=='9b4afcb22823ce48cb20cb4cb951cd55229ac1f2'
    assert scope['run_record_sha256']==pins[guard.RUN_RECORD]
    assert scope['approval_sha256']==pins[guard.APPROVAL]
    assert scope['review_sha256']==pins[guard.REVIEW]
    receipt.update(software_commit=scope['head_commit'],environment_scope=env,
        run_record_sha256=scope['run_record_sha256'],approval_sha256=scope['approval_sha256'],review_sha256=scope['review_sha256'],
        reviewed_tool_contract_files=len(scope['approval']['file_sha256']),reviewed_source_files=len(scope['approval']['source_file_sha256']))
    names=[guard.ATTEMPT,guard.OUTCOME]+[guard.RAW+'/'+name for name in (
        'run01_execution_intent.json','run01_execution_outcome.json','run01_capture_attempt.json',
        'run01_guard_stdout.txt','run01_guard_stderr.txt','run01_capture_stdout.txt','run01_capture_stderr.txt')]
    absent={name:not os.path.lexists(ROOT/name) for name in names}
    assert all(absent.values())
    receipt['absent_execution_files']=absent
    receipt['verdict']='PASS_FINAL_READ_ONLY_ADMISSION'
except BaseException as error:
    receipt.update(verdict='REFUSED',error=repr(error))
    raise
finally:
    receipt['finished_utc']=datetime.now(timezone.utc).isoformat()
    path=Path(__file__).parent/'run01_final_admission.json'
    with path.open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
print(json.dumps(receipt,indent=2))
