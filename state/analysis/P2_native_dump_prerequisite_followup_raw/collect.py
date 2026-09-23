from pathlib import Path
from datetime import datetime,timezone
import os,sys,json,subprocess,hashlib,shlex
ROOT=Path(__file__).resolve().parents[3]
RAW=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'tools'))
import board_tool as board
os.environ['SUMO_TRANSPORT']='adb'
os.environ['SUMO_ADB_SERIAL']='2629958581'
os.environ['SUMO_ADB_EXECUTABLE']=str(Path(os.environ['LOCALAPPDATA'])/'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
argv=['python3','-c',(RAW/'remote_inventory.py').read_text(encoding='utf-8')]
dest=RAW/'01_inventory.json'
if dest.exists():raise ValueError('Refuse receipt overwrite')
r={'start_utc':datetime.now(timezone.utc).isoformat(),'remote_argv':argv,'transport_argv':[board.adb_executable(),'-s',board.target(),'shell','-T',shlex.join(argv)],'timeout_seconds':30,'scope':'Read-only kernel/sysfs/process/file metadata; no UART/socket open, RPC, service or MCU operation.'}
try:
 p=board.remote(board.target(),argv,capture=True,timeout=30)
 r.update(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
except subprocess.CalledProcessError as e:r.update(returncode=e.returncode,stdout=e.stdout,stderr=e.stderr)
except subprocess.TimeoutExpired as e:r.update(returncode=None,timed_out=True,stdout=repr(e.stdout),stderr=repr(e.stderr))
finally:
 r['end_utc']=datetime.now(timezone.utc).isoformat()
 for k in ('stdout','stderr'):r[k+'_sha256']=hashlib.sha256(r.get(k,'').encode()).hexdigest()
 dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(r['returncode']);print(r.get('stdout',''));print(r.get('stderr',''))
