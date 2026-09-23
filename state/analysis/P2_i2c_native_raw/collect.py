# Reads installed Linux files and offline packaged-ELF metadata.
# Records the native I2C4 prerequisites without MCU or peripheral calls.
# The receipt keeps failures and source hashes for independent checking.
from pathlib import Path
import os,sys,json
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.board_tool import remote
os.environ['SUMO_TRANSPORT']='adb'
os.environ['SUMO_ADB_SERIAL']='2629958581'
os.environ['SUMO_ADB_EXECUTABLE']=str(Path(os.environ['LOCALAPPDATA'])/'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
r=remote('2629958581',['python3','-c',Path(sys.argv[1]).read_text()],capture=True,timeout=45)
p=Path(__file__).with_name(sys.argv[2])
p.write_text(json.dumps({'exit':r.returncode,'stderr':r.stderr,'records':json.loads(r.stdout)},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'receipt':str(p),'bytes':p.stat().st_size,'exit':r.returncode}))
