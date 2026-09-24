# Archives already collected Linux files after the single observation ends.
# No MCU access, collector execution, retry, reset or firmware action is performed.
# Fixed-path bounds, exclusive local writes and hashes preserve the raw evidence.
from datetime import datetime, timezone
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0,str(ROOT/'tools'))
import board_tool as board

REMOTE = '/home/arduino/sumox26-capture/app-default-e820c0e1-run01'
program='\n'.join(['from pathlib import Path','import base64,hashlib,json,re,stat',
    f'root=Path({REMOTE!r})',
    'assert root.is_dir() and all(not p.is_symlink() for p in (root,*root.parents))',
    'paths=sorted(root.iterdir()); assert 0<len(paths)<=256',
    'total=0; files=[]',
    'for path in paths:',
    '    assert re.fullmatch(r"[A-Za-z0-9_.-]+",path.name) and path.name not in (".","..")',
    '    assert not path.is_symlink() and stat.S_ISREG(path.stat().st_mode)',
    '    size=path.stat().st_size; total+=size; assert size<=4194304 and total<=16777216',
    '    data=path.read_bytes(); assert len(data)==size',
    '    files.append(dict(name=path.name,bytes=size,sha256=hashlib.sha256(data).hexdigest(),base64=base64.b64encode(data).decode()))',
    'print(json.dumps(dict(root=str(root),bytes=total,files=files)))'])
os.environ.update(SUMO_TRANSPORT='adb',SUMO_ADB_SERIAL='2629958581',
    SUMO_ADB_EXECUTABLE=str(Path(os.environ['LOCALAPPDATA'])/'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'))
assert (RAW/'run01_execution_outcome.json').is_file(), 'Observation must finish first'
out=RAW/'actual_capture'; out.mkdir(exist_ok=False)
receipt=dict(scope='READ_ONLY_LINUX_FILE_ARCHIVE_NO_MCU',start_utc=datetime.now(timezone.utc).isoformat(),
    target=board.target(),argv=['python3','-c',program],timeout_seconds=30)
try:
    result=board.remote(board.target(),receipt['argv'],capture=True,timeout=30)
    receipt.update(returncode=result.returncode,stderr=result.stderr,stdout_sha256=hashlib.sha256(result.stdout.encode()).hexdigest())
    bundle=json.loads(result.stdout); assert bundle['root']==REMOTE and len(bundle['files'])<=256
    names=set(); receipt['files']=[]
    for item in bundle['files']:
        name=item['name']; assert re.fullmatch(r'[A-Za-z0-9_.-]+',name) and name not in ('.','..') and name not in names
        names.add(name); data=base64.b64decode(item['base64'],validate=True)
        assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
        with (out/name).open('xb') as stream: stream.write(data)
        receipt['files'].append({k:item[k] for k in ('name','bytes','sha256')})
    receipt.update(status='ARCHIVED',bytes=bundle['bytes'])
except BaseException as error:
    receipt.update(status='FAILED',error=repr(error)); raise
finally:
    receipt['finish_utc']=datetime.now(timezone.utc).isoformat()
    with (RAW/'run01_file_archive.json').open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,indent=2); stream.write('\n')
print(json.dumps({k:receipt[k] for k in ('status','bytes','returncode')},indent=2))
