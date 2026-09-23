import json,os,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'tools'))
import board_tool as b
folder=os.environ['SUMO_REMOTE_ROOT']+'/e50c6da38bba5131e426d8c076e7aa7c8aad5961f60a6eb1387b1f2412aab6af/ui_matrix/artifacts/bench-default'
program=r"""
import pathlib,hashlib,json,subprocess,sys
p=pathlib.Path(sys.argv[1]);prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
x={f.name:dict(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in p.iterdir() if f.is_file()}
r=subprocess.run([prefix+'readelf','-sW',str(p/'ui_matrix.ino.elf')],capture_output=True,text=True,check=True)
x['symbol']=[l for l in r.stdout.splitlines() if l.endswith(' uiBench')]
print(json.dumps(x,indent=2))
"""
r=b.remote(b.target(),['python3','-c',program,folder],capture=True)
x=json.loads(r.stdout);(root/'state/analysis/P2_matrix_raw/artifact_metadata.json').write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
print(json.dumps(x,indent=2))
