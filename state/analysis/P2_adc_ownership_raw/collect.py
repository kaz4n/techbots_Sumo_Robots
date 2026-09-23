# Reads installed Linux headers and disassembles the packaged ELF only.
# Records ADC ownership evidence without any MCU connection or peripheral call.
# The receipt retains command failures as well as successful source reads.
from pathlib import Path
import os,sys,json
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from tools.board_tool import remote
os.environ['SUMO_TRANSPORT']='adb'
os.environ['SUMO_ADB_SERIAL']='2629958581'
os.environ['SUMO_ADB_EXECUTABLE']=str(Path(os.environ['LOCALAPPDATA'])/'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
program=Path(sys.argv[1]).read_text(encoding='utf-8')
r=remote('2629958581',['python3','-c',program],capture=True,timeout=45)
p=Path(__file__).with_name(sys.argv[2])
p.write_text(json.dumps({'exit':r.returncode,'stderr':r.stderr,'records':json.loads(r.stdout)},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'receipt':str(p),'bytes':p.stat().st_size,'exit':r.returncode,'stderr':r.stderr}))
