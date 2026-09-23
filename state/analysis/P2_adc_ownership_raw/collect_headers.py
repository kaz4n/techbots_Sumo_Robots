# Retains actual installed public headers as source evidence for native tests.
# Reads board Linux files only; no MCU access or compiler execution.
# Each saved byte stream is checked against its remotely computed SHA-256.
from pathlib import Path
import os,sys,json,hashlib,base64
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.board_tool import remote
os.environ['SUMO_TRANSPORT']='adb'
os.environ['SUMO_ADB_SERIAL']='2629958581'
os.environ['SUMO_ADB_EXECUTABLE']=str(Path(os.environ['LOCALAPPDATA'])/'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
program='''from pathlib import Path
import json,hashlib,base64
I=Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/variants/arduino_uno_q_stm32u585xx/llext-edk/include')
H=I/'modules/hal/stm32/stm32cube/stm32u5xx'
ps=[H/'soc/stm32u585xx.h',I/'modules/hal/cmsis_6/CMSIS/Core/Include/core_cm33.h']+[H/'drivers/include'/('stm32u5xx_ll_'+n+'.h') for n in ['adc','gpio','bus','rcc','pwr','dac','exti']]
out=[]
for p in ps:
 b=p.read_bytes();out.append({'source':str(p),'name':p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'data':base64.b64encode(b).decode()})
print(json.dumps(out))
'''
r=remote('2629958581',['python3','-c',program],capture=True,timeout=45)
if r.returncode:raise SystemExit(r.stderr)
target=Path(__file__).with_name('headers');target.mkdir(exist_ok=True)
manifest=[]
for entry in json.loads(r.stdout):
 b=base64.b64decode(entry.pop('data'));assert hashlib.sha256(b).hexdigest()==entry['sha256']
 (target/entry['name']).write_bytes(b);manifest.append(entry)
(target/'manifest.json').write_text(json.dumps({'exit':r.returncode,'stderr':r.stderr,'files':manifest},indent=2)+'\n')
print(json.dumps({'files':len(manifest),'bytes':sum(x['bytes'] for x in manifest),'path':str(target)}))
