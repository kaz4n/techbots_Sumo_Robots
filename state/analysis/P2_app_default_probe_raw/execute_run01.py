# Executes the separately reviewed exact default-app attempt and one passive capture.
# The tested guard owns upload admission; exclusive receipts consume uncertain work.
# This coordinator script preserves actual outputs and never retries or resets.
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0,str(ROOT/'tools'))
import board_tool as board
import app_default_run as guard

RUN = 'app-default-e820c0e1-run01'
SOURCE = 'e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69'
COLLECTOR = 'beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1'
REMOTE_TOOLS = '/home/arduino/sumox26-capture-tools/app-default-' + COLLECTOR
INPUTS = '/home/arduino/sumox26-capture-input/app_default_' + SOURCE
OUTPUT = '/home/arduino/sumox26-capture/' + RUN
PINS = {'app_default_capture.py':COLLECTOR,
    'p0_capture.py':'885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c',
    'recorder_heap.py':'d661024975925a7d8a83f4b772199bbf59911adb5adb8ea69a2082b69eed4b92',
    'p0_mem_read.cfg':'89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339'}


def utc():
    return datetime.now(timezone.utc).isoformat()


def exclusive(path,value):
    with path.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False); stream.write('\n')
        stream.flush(); os.fsync(stream.fileno())


def capture_once(command):
    try:
        result=board.remote(board.target(),command['argv'],capture=True,timeout=620)
    except subprocess.CalledProcessError as error:
        result=error
    except BaseException as error:
        command.update(returncode=getattr(error,'returncode',None),finish_utc=utc(),error=repr(error))
        save_capture_output(error)
        raise
    command.update(returncode=result.returncode,finish_utc=utc())
    save_capture_output(result)
    return result.returncode


def save_capture_output(result):
    for name in ('stdout','stderr'):
        data=getattr(result,name,None) or ''
        if isinstance(data,bytes): data=data.decode('utf-8',errors='replace')
        with (RAW/('run01_capture_'+name+'.txt')).open('x',encoding='utf-8') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())


def main():
    os.environ.update(SUMO_TRANSPORT='adb',SUMO_ADB_SERIAL='2629958581',
        SUMO_REMOTE_ROOT='/home/arduino/sumox26_codex_build',
        SUMO_ADB_EXECUTABLE=str(Path(os.environ['LOCALAPPDATA'])/'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'),
        PYTHONDONTWRITEBYTECODE='1')
    scope=guard.load_scope(ROOT,board.target(),board.transport())
    trace=dict(run_id=RUN,started_utc=utc(),software_commit=scope['head_commit'],
        run_record_sha256=scope['run_record_sha256'],commands=[],status='STARTED')
    exclusive(RAW/'run01_execution_intent.json',trace)
    try:
        argv=[sys.executable,'-B',str(ROOT/'tools/app_default_run.py'),'--run-id',RUN]
        command=dict(argv=argv,start_utc=utc(),kind='EXACT_GUARDED_UPLOAD'); trace['commands'].append(command)
        with (RAW/'run01_guard_stdout.txt').open('x',encoding='utf-8') as out,(RAW/'run01_guard_stderr.txt').open('x',encoding='utf-8') as err:
            result=subprocess.run(argv,stdout=out,stderr=err,stdin=subprocess.DEVNULL)
        command.update(returncode=result.returncode,finish_utc=utc())
        if result.returncode!=0:
            trace['status']='GUARD_FAILED_NO_CAPTURE'; return 1
        outcome=json.loads((RAW/'run01_upload_outcome.json').read_text())
        if outcome['run_id']!=RUN or outcome['returncode']!=0 or outcome['error'] is not None:
            raise ValueError('Upload result does not permit capture')
        program='\n'.join(['from pathlib import Path','import hashlib,os,sys,stat',
            f'root=Path({REMOTE_TOOLS!r})',f'pins={PINS!r}',
            'assert all(not p.is_symlink() for p in (root,*root.parents))',
            'for name,expected in pins.items():',
            '    p=root/name; assert not p.is_symlink() and stat.S_ISREG(p.stat().st_mode)',
            '    assert hashlib.sha256(p.read_bytes()).hexdigest()==expected',
            f'argv=[sys.executable,"-B",str(root/"app_default_capture.py"),"--artifact-dir",{INPUTS!r},"--output",{OUTPUT!r}]',
            'os.execv(sys.executable,argv)'])
        argv=['python3','-B','-c',program]
        command=dict(argv=argv,start_utc=utc(),kind='ONE_PASSIVE_CAPTURE',timeout_seconds=620)
        trace['commands'].append(command)
        exclusive(RAW/'run01_capture_attempt.json',dict(run_id=RUN,started_utc=utc(),
            software_commit=scope['head_commit'],review_sha256=scope['review_sha256'],
            target=board.target(),source_sha256=SOURCE,collector_sha256=COLLECTOR,argv=argv))
        code=capture_once(command)
        trace['status']='CAPTURE_COMMAND_SUCCEEDED' if code==0 else 'CAPTURE_NONZERO_NO_RETRY'
        return code
    except BaseException as error:
        trace.update(status='FAILED_OR_UNKNOWN_NO_RETRY',error=repr(error))
        raise
    finally:
        trace['finished_utc']=utc()
        exclusive(RAW/'run01_execution_outcome.json',trace)


if __name__=='__main__':
    raise SystemExit(main())
