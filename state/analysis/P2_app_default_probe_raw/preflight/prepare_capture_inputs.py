# Stages two exact retained app files for a later passive observation.
# Exclusive Linux regular-file copies cannot upload or execute MCU firmware.
# The receipt retains command status and hashes; no run authority follows.
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board

SOURCE = 'e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69'
ELF = '8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257'
ZSK = 'c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5'
base = '/home/arduino/sumox26_codex_build/_app_builds/native-app-v1/' + SOURCE + '/bench-default/d92f929c6cc84961bb86dfea3da2ad00'
destination = '/home/arduino/sumox26-capture-input/app_default_' + SOURCE
files = [(base + '/build/app.ino.elf', 'app.ino.elf', ELF),
         (base + '/artifacts/app.ino.elf-zsk.bin', 'app.ino.elf-zsk.bin', ZSK)]
program = '\n'.join([
    'from pathlib import Path', 'import hashlib,json,os,stat',
    'def regular(path):',
    '    assert path.is_absolute() and path.resolve()==path',
    '    assert all(not p.is_symlink() for p in (path,*path.parents))',
    '    assert stat.S_ISREG(path.stat().st_mode)',
    f'items={files!r}', f'out=Path({destination!r})',
    'assert out.parent.is_dir() and out.parent.resolve()==out.parent',
    'assert all(not p.is_symlink() for p in (out.parent,*out.parent.parents))',
    'assert not os.path.lexists(out)', 'blobs=[]',
    'for source,name,expected in items:',
    '    p=Path(source); regular(p); assert p.stat().st_size==176048',
    '    data=p.read_bytes(); assert hashlib.sha256(data).hexdigest()==expected',
    '    blobs.append((name,expected,data))',
    'out.mkdir(mode=0o700)', 'result=[]',
    'for name,expected,data in blobs:',
    '    p=out/name',
    '    with p.open("xb") as stream:',
    '        stream.write(data); stream.flush(); os.fsync(stream.fileno())',
    '    regular(p); digest=hashlib.sha256(p.read_bytes()).hexdigest(); assert digest==expected',
    '    result.append(dict(path=str(p),bytes=p.stat().st_size,sha256=digest))',
    'assert sorted(p.name for p in out.iterdir())==sorted(x[0] for x in blobs)',
    'print(json.dumps(dict(status="PREPARED_FILES_ONLY",files=result)))',
])
os.environ.update(SUMO_TRANSPORT='adb', SUMO_ADB_SERIAL='2629958581',
    SUMO_ADB_EXECUTABLE=str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'))
receipt_path = Path(__file__).with_name('capture_input_staging.json')
with receipt_path.open('x', encoding='utf-8') as stream:
    receipt = dict(scope='EXCLUSIVE_LINUX_FILE_COPY_NO_MCU_ACTION',
        start_utc=datetime.now(timezone.utc).isoformat(), target=board.target(),
        argv=['python3','-c',program], timeout_seconds=30)
    try:
        result = board.remote(board.target(), receipt['argv'], capture=True, timeout=30)
        receipt.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
        receipt['result'] = json.loads(result.stdout)
    except Exception as error:
        receipt.update(error=repr(error),returncode=getattr(error,'returncode',None),
            stdout=getattr(error,'stdout',None),stderr=getattr(error,'stderr',None))
        raise
    finally:
        receipt['finish_utc']=datetime.now(timezone.utc).isoformat()
        json.dump(receipt,stream,indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
print(json.dumps(receipt['result'],indent=2))
