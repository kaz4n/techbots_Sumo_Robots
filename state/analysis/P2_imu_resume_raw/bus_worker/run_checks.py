from pathlib import Path
import hashlib,json,os,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
OLD=Path('/tmp/d094_bus_impl_legacy')
if OLD.exists():
    shutil.copytree(OLD,OUT/'legacy_first',dirs_exist_ok=True)
SOURCES=['src/hal/imu_bus_unoq.cpp','src/hal/imu_bus_async_unoq.cpp','src/hal/imu_bus_unoq.h','src/config.h']
manifest={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in SOURCES}
manifest['smoke.cc']=hashlib.sha256((OUT/'smoke.cc').read_bytes()).hexdigest()
commands=[]
def run(argv,env=None):
    result=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
    record={'argv':list(map(str,argv)),'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'source_hashes':manifest,'capture':'subprocess text=True; newline normalized'}
    path=OUT/f'check_{time.time_ns()}.json'
    path.write_text(json.dumps(record,indent=2)+'\n')
    print(result.stdout,end='');print(result.stderr,end='');commands.append({'receipt':path.name,'returncode':result.returncode})
    if result.returncode: raise SystemExit(result.returncode)
flags=['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror','-fno-exceptions','-fno-rtti','-fsanitize=undefined','-fno-sanitize-recover=all','-DARDUINO_ARCH_ZEPHYR','-I','tests/native_imu_bus','-I','src']
run(flags+[str(OUT/'smoke.cc'),'tests/native_imu_bus/native_fixture.cc','src/hal/imu_bus_unoq.cpp','src/hal/imu_bus_async_unoq.cpp','-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free','-o','/tmp/d094_bus_worker_smoke'])
for args in ([],['none'],['collision']):run(['/tmp/d094_bus_worker_smoke',*args])
env=dict(os.environ,TMPDIR='/dev/shm',SUMO_NATIVE_RECEIPT_DIR=str(OUT/'legacy_final'))
names=['test_b3_transport_contract','test_b3_failures_and_cleanup','test_b3_ownership_and_boot_claim','test_b3_deadlines_wrap_and_frozen_time']
run(['python3','-m','unittest',*[f'tests.tooling.test_imu_bus_unoq.NativeImuBusTests.{n}' for n in names],'-v'],env)
frozen=subprocess.check_output(['git','show','e507c42:src/hal/imu_bus_unoq.h'],cwd=ROOT,text=True)
current=(ROOT/'src/hal/imu_bus_unoq.h').read_text()
assert frozen.split('private:',1)[0]==current.split('private:',1)[0]
(OUT/'summary.json').write_text(json.dumps({'source_hashes':manifest,'checks':commands,'frozen_public_header_unchanged':True,'scope':'Worker smoke and legacy native regressions only; no hardware action or physical acceptance.'},indent=2)+'\n')
