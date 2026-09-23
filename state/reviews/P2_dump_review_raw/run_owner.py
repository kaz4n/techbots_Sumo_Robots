from pathlib import Path
import subprocess, json, hashlib, tempfile, os
root=Path.cwd(); base=root/'state/reviews/P2_dump_review_raw'
sources=sorted((root/'src/core').glob('*.cpp'))
sources += [root/'src/hal'/name for name in ('recorder_frames.cpp','recorder.cpp','recorder_csv.cpp','recorder_dump.cpp','motors.cpp')]
sources += [root/'tests/test_recorder_dump.cpp',root/'tests/fixtures/dump_main.cc']
freeze={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
with (base/'owner_freeze.json').open('x') as f: json.dump(freeze,f,indent=2)
results=[]
with tempfile.TemporaryDirectory(prefix='sumo-dump-review-owner-') as work:
 for name,extra in [('normal',[]),('san',['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
  exe=Path(work)/name
  command=['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror','-fno-exceptions','-fno-rtti','-DDOCTEST_CONFIG_NO_EXCEPTIONS','-I',str(root/'src'),'-isystem',str(root/'host/third_party'),*extra,*map(str,sources),'-o',str(exe)]
  for stage,argv in [('build',command),('test',[str(exe)])]:
   with (base/('owner_'+name+'_'+stage+'.txt')).open('x') as log:
    result=subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT)
   results.append(dict(name=name,stage=stage,argv=argv,returncode=result.returncode))
   if result.returncode: break
with (base/'owner_results.json').open('x') as f: json.dump(results,f,indent=2)
print(json.dumps(results))
