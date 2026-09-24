# Copies the reviewed passive collector and immutable helpers to a fresh Linux folder.
# This stages regular files only; it does not import or execute the collector.
# Exclusive-directory and before/after hash receipts make the later run reviewable.
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board

FILES = {
    'app_default_capture.py':'beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1',
    'p0_capture.py':'885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c',
    'recorder_heap.py':'d661024975925a7d8a83f4b772199bbf59911adb5adb8ea69a2082b69eed4b92',
    'p0_mem_read.cfg':'89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339',
}
DEST = '/home/arduino/sumox26-capture-tools/app-default-' + FILES['app_default_capture.py']
os.environ.update(SUMO_TRANSPORT='adb',SUMO_ADB_SERIAL='2629958581',
    SUMO_ADB_EXECUTABLE=str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'))
receipt = dict(scope='REGULAR_FILE_DEPLOYMENT_NO_COLLECTOR_EXECUTION_NO_MCU',
    start_utc=datetime.now(timezone.utc).isoformat(),target=board.target(),destination=DEST,
    files=FILES,commands=[])
for name,expected in FILES.items():
    path=ROOT/'tools'/name
    assert path.is_file() and not path.is_symlink()
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected
program='\n'.join(['from pathlib import Path','import os',f'p=Path({DEST!r})',
    'assert p.parent.is_dir() and p.parent.resolve()==p.parent',
    'assert all(not a.is_symlink() for a in (p.parent,*p.parent.parents))',
    'assert not os.path.lexists(p)','p.mkdir(mode=0o700)','print("FRESH_EMPTY_TOOL_DIRECTORY")'])
out=Path(__file__).with_name('capture_tool_deployment.json')
with out.open('x',encoding='utf-8') as stream:
    try:
        command=['python3','-c',program]
        entry=dict(argv=command,timeout_seconds=30); receipt['commands'].append(entry)
        result=board.remote(board.target(),command,capture=True,timeout=30)
        entry.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        for name,expected in FILES.items():
            command=[board.adb_executable(),'-s',board.target(),'push',str(ROOT/'tools'/name),DEST+'/'+name]
            entry=dict(argv=command,timeout_seconds=30); receipt['commands'].append(entry)
            result=subprocess.run(command,capture_output=True,text=True,stdin=subprocess.DEVNULL,timeout=30,check=True)
            entry.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        verify='\n'.join(['from pathlib import Path','import hashlib,json,stat',
            f'p=Path({DEST!r})',f'pins={FILES!r}',
            'assert sorted(a.name for a in p.iterdir())==sorted(pins)',
            'actual={}', 'for name,expected in pins.items():',
            '    q=p/name; assert not q.is_symlink() and stat.S_ISREG(q.stat().st_mode)',
            '    value=hashlib.sha256(q.read_bytes()).hexdigest(); assert value==expected',
            '    actual[name]=value','print(json.dumps(actual))'])
        command=['python3','-c',verify]
        entry=dict(argv=command,timeout_seconds=30); receipt['commands'].append(entry)
        result=board.remote(board.target(),command,capture=True,timeout=30)
        entry.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        receipt.update(status='DEPLOYED_BYTES_ONLY',actual_sha256=json.loads(result.stdout))
    except Exception as error:
        receipt.update(status='FAILED',error=repr(error),returncode=getattr(error,'returncode',None))
        raise
    finally:
        receipt['finish_utc']=datetime.now(timezone.utc).isoformat()
        json.dump(receipt,stream,indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
print(json.dumps(dict(status=receipt['status'],destination=DEST),indent=2))
