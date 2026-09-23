"""Runs the frozen independent author suite into separate reviewer receipts."""
from pathlib import Path
import hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
folder=OUT/('native_'+str(time.time_ns()))
folder.mkdir()
paths=[ROOT/'src/hal/imu_bus_unoq.cpp',ROOT/'src/hal/imu_bus_unoq.h',ROOT/'src/config.h',
       ROOT/'tests/tooling/test_imu_bus_unoq.py',*sorted((ROOT/'tests/native_imu_bus').rglob('*'))]
before={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
env=os.environ.copy();env['SUMO_NATIVE_RECEIPT_DIR']=str(folder);env['TMPDIR']='/dev/shm'
argv=['python3','-m','unittest','tests.tooling.test_imu_bus_unoq','-v']
started=time.monotonic()
result=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True,timeout=1800)
after={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
report=dict(argv=argv,returncode=result.returncode,seconds=time.monotonic()-started,
    stdout=result.stdout,stderr=result.stderr,capture='subprocess text=True; newline normalized',
    source_fixture_manifest=before,manifest_unchanged=before==after,receipt_directory=folder.relative_to(ROOT).as_posix())
(folder/'full_unittest.json').write_text(json.dumps(report,indent=2)+'\n')
print(result.stdout+result.stderr)
print(json.dumps(dict(returncode=result.returncode,manifest_unchanged=before==after,receipt=str(folder))))
raise SystemExit(result.returncode or int(before!=after))
