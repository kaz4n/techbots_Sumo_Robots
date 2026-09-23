from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sources=sorted(ROOT.glob('src/core/*.cpp'))+[ROOT/p for p in ['src/hal/motors.cpp','src/hal/recorder.cpp','src/hal/recorder_frames.cpp','src/app/transaction.cpp']]
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources+[ROOT/'src/app/transaction.h',ROOT/'src/hal/motors.h',ROOT/'src/config.h',OUT/'smoke.cc']}
checks=[]
def run(argv):
 r=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=120)
 path=OUT/f'check_{time.time_ns()}.json';path.write_text(json.dumps({'argv':argv,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'source_hashes':manifest,'capture':'subprocess text=True; newline normalized'},indent=2)+'\n')
 print(r.stdout,end='');print(r.stderr,end='');checks.append({'receipt':path.name,'returncode':r.returncode})
 if r.returncode:raise SystemExit(r.returncode)
for allowed in [0,1]:
 binary=f'/tmp/d095_transaction_worker_{allowed}'
 run(['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror','-fno-exceptions','-fno-rtti','-fsanitize=undefined','-fno-sanitize-recover=all',f'-DMOTORS_ALLOWED={allowed}','-I','src',str(OUT/'smoke.cc'),*map(str,sources),'-o',binary]);run([binary])
frozen=subprocess.check_output(['git','show','c17f6d6:src/app/transaction.h'],cwd=ROOT,text=True)
assert frozen==(ROOT/'src/app/transaction.h').read_text()
(OUT/'summary.json').write_text(json.dumps({'source_hashes':manifest,'checks':checks,'frozen_header_unchanged':True,'scope':'Actual module worker smoke under both motor macros; no hardware.'},indent=2)+'\n')
