"""Run the exact reviewed D091 MEM-AP reader and preserve complete raw evidence."""
import hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
import board_tool as board
raw=Path(__file__).parent/'P2_recorder_bench_raw'
assert board.target()=='2629958581' and board.transport()=='adb'
local=raw/'runtime_run1'; assert not local.exists(), 'Do not overwrite capture evidence'
review=json.loads((Path(__file__).parents[1]/'reviews/P2_recorder_bench_review_raw/final_approval.json').read_text())
assert review['verdict']=='PASS_SCOPED_SOURCE_AND_CAPTURE_REVIEW'
folder='/home/arduino/sumox26-capture/recorder-d091-run1'
artifact=review['artifact_dir']
args=['python3','/home/arduino/sumox26-capture-tools/recorder-06f69258/recorder_capture.py','--artifact-dir',artifact,'--output',folder]
try:
 result=board.remote(board.target(),args,capture=True,timeout=620)
 code,out,err=result.returncode,result.stdout,result.stderr
except subprocess.CalledProcessError as e:
 code,out,err=e.returncode,e.stdout,e.stderr
(raw/'capture_run1_stdout.json').write_text(out,encoding='utf-8')
(raw/'capture_run1_command.json').write_text(json.dumps(dict(argv=args,returncode=code,stderr=err),indent=2)+'\n')
command=[board.adb_executable(),'-s',board.target(),'pull',folder,str(local)]
pulled=subprocess.run(command,capture_output=True,text=True,timeout=90)
(raw/'capture_run1_pull.json').write_text(json.dumps(dict(argv=command,returncode=pulled.returncode,stdout=pulled.stdout,stderr=pulled.stderr),indent=2)+'\n')
assert pulled.returncode==0
record=json.loads((local/'capture.json').read_text())
manifest={p.relative_to(local).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in local.rglob('*') if p.is_file()}
(raw/'capture_run1_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:record.get(k) for k in ['status','error','diagnostics','heap','capture_duration_seconds','memory_read_attempts','memory_bytes_requested']},indent=2))
raise SystemExit(code)
