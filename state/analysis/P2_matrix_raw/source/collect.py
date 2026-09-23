# Reads installed Linux source and packaged binaries only; no MCU connection.
# Preserves matrix audit source provenance using the established ADB transport.
# Tested by JSON receipt, source hashes and bounded offline tool results.
import base64
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tools.board_tool import remote

os.environ['SUMO_TRANSPORT'] = 'adb'
os.environ['SUMO_ADB_SERIAL'] = '2629958581'
os.environ['SUMO_ADB_EXECUTABLE'] = str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')

PROGRAM = r'''
from pathlib import Path
import base64,hashlib,json,subprocess
C=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
paths=list(C.glob('libraries/*Matrix*/src/*'))+list(C.glob('variants/arduino_uno_q_stm32u585xx/*'))
out=[]
for p in paths:
 if p.is_file() and (p.suffix in ('.h','.cpp','.c','.inc','.conf','.elf') or 'ELF' in p.name):
  b=p.read_bytes();out.append({'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'base64':base64.b64encode(b).decode() if len(b)<100000 else None})
print(json.dumps({'files':out,'paths':[str(p) for p in paths]}))
'''
if __name__ == '__main__':
 result=remote('2629958581',['python3','-c',PROGRAM],capture=True,timeout=45)
 data=json.loads(result.stdout)
 here=Path(__file__).parent
 for f in data['files']:
  if f.get('base64'):
   b=base64.b64decode(f.pop('base64'));name=Path(f['path']).name
   (here/name).write_bytes(b);f['local']=name
 (here/'installed_receipt.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'exit':result.returncode,'stderr':result.stderr,'paths':data['paths'],'receipt':'installed_receipt.json'}))
