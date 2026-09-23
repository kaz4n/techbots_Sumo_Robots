from pathlib import Path
import subprocess,json,hashlib
out=Path(__file__).resolve().parent
root=out.parents[3]
sources=list((root/'src/core').glob('*.cpp'))
sources += [root/'src/hal'/s for s in ['ui.cpp','motors.cpp','recorder.cpp','recorder_frames.cpp']]
sources += [root/'bench/recorder_inert/src/recorder_bench.cpp',out/'smoke.cpp']
cmd=['g++','-std=c++17','-O2','-Wall','-Wextra','-Wpedantic','-Werror','-fno-exceptions','-fno-rtti','-DMATCH=0','-DMOTORS_ALLOWED=0','-I'+str(root/'src'),'-I'+str(root/'bench/recorder_inert/src'),*map(str,sources),'-o',str(out/'smoke')]
a=subprocess.run(cmd,text=True,capture_output=True)
record={'compile_command':cmd,'compile_exit':a.returncode,'stdout':a.stdout,'stderr':a.stderr}
if a.returncode==0:
 b=subprocess.run([str(out/'smoke')],text=True,capture_output=True)
 record.update(run_exit=b.returncode,run_stdout=b.stdout,run_stderr=b.stderr)
record['sha256']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'bench/recorder_inert/src/recorder_bench.cpp',root/'bench/recorder_inert/src/recorder_bench.h']}
(out/'smoke_receipt.json').write_text(json.dumps(record,indent=2))
print(json.dumps(record,indent=2))
raise SystemExit(record.get('run_exit',a.returncode))
