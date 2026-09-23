from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
names=['motors','recorder','recorder_frames','power_inputs','ui','imu_heading','imu_adapter','line_qtr_adapter','qtr_cal','ui_display']
sources=sorted(ROOT.glob('src/core/*.cpp'))+sorted(ROOT.glob('src/app/*.cpp'))
sources=[p for p in sources if p.name!='native_sources_unoq.cpp']
sources += [ROOT/'src/hal'/f'{name}.cpp' for name in names]
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources+[ROOT/'src/app/runtime.h',ROOT/'src/config.h',OUT/'smoke.cc']}
checks=[]
def run(argv):
    result=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=120)
    receipt=OUT/f'check_{time.time_ns()}.json'
    receipt.write_text(json.dumps({'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'source_hashes':manifest},indent=2)+'\n')
    print(result.stdout,end='');print(result.stderr,end='')
    checks.append({'receipt':receipt.name,'returncode':result.returncode})
    if result.returncode: raise SystemExit(result.returncode)
for allowed in [0,1]:
    binary=f'/tmp/d096_runtime_worker_{allowed}'
    run(['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror','-fno-exceptions','-fno-rtti','-fsanitize=undefined','-fno-sanitize-recover=all',f'-DMOTORS_ALLOWED={allowed}','-I','src',str(OUT/'smoke.cc'),*map(str,sources),'-o',binary])
    run([binary])
(OUT/'summary.json').write_text(json.dumps({'source_hashes':manifest,'checks':checks,'scope':'Production Runtime with synthetic callbacks under both motor modes and UBSan; no hardware.'},indent=2)+'\n')
