"""Execute only the exact reviewed D091 inert artifact after byte verification."""
import json, os, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
import board_tool as board
raw=Path(__file__).parent/'P2_recorder_bench_raw'
review=json.loads((Path(__file__).parents[1]/'reviews/P2_recorder_bench_review_raw/source_approval.json').read_text())
assert review['verdict']=='PASS_EXACT_INERT_SOURCE_AND_ELF'
source=review['source_sha256']
assert source=='1502e9484068921fe3f96adef402e12fc85a00093b544e4a6c0dee165476b583'
assert board.target()=='2629958581' and board.transport()=='adb'
record=raw/'upload_run1.json'
assert not record.exists(), 'This run has already been attempted; do not repeat silently'
expected=json.loads((raw/'target_1502e948_bench-default.json').read_text())['source_files']
program=r'''import hashlib,json,pathlib,subprocess,sys,time,datetime
root=pathlib.Path(sys.argv[1]); expected=json.loads(sys.argv[2]); elfhash=sys.argv[3]; binhash=sys.argv[4]
actual={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and 'artifacts' not in p.relative_to(root).parts}
assert actual==expected, 'Staged source bytes changed'
art=root/'artifacts/bench-default'
for name,digest in [('recorder_inert.ino.elf',elfhash),('recorder_inert.ino.elf-zsk.bin',binhash)]:
 assert hashlib.sha256((art/name).read_bytes()).hexdigest()==digest, 'Reviewed artifact bytes changed'
argv=['arduino-cli','upload','--fqbn','arduino:zephyr:unoq','--input-dir',str(art),str(root)]
record=dict(argv=argv,utc_before=datetime.datetime.now(datetime.timezone.utc).isoformat(),linux_monotonic_before=time.monotonic(),source_verified_files=len(actual),elf_sha256=elfhash,zsk_sha256=binhash)
try:
 result=subprocess.run(argv,capture_output=True,text=True,timeout=90,stdin=subprocess.DEVNULL)
 record.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
except subprocess.TimeoutExpired as error:
 record.update(returncode=124,error=str(error))
record.update(utc_after=datetime.datetime.now(datetime.timezone.utc).isoformat(),linux_monotonic_after=time.monotonic())
print(json.dumps(record))
'''
folder='/home/arduino/sumox26_codex_build/'+source+'/recorder_inert'
record.write_text(json.dumps(dict(status='ATTEMPT_STARTED',scope='D091 reviewed inert MCU upload; no native peripheral setup',source=source))+'\n')
args=['python3','-c',program,folder,json.dumps(expected),review['elf_sha256'],review['zsk_sha256']]
try:
 result=board.remote(board.target(),args,capture=True,timeout=100)
 data=json.loads(result.stdout)
 data.update(remote_argv=result.args,remote_returncode=result.returncode,remote_stderr=result.stderr)
 record.write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps(data,indent=2))
 raise SystemExit(data['returncode'])
except Exception as error:
 with record.open('a') as output: output.write(json.dumps(dict(error=str(error)))+'\n')
 raise
