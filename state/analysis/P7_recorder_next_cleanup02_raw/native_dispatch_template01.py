# Dispatches only reviewed D228 intents and preserves each single-use receipt.
# It binds observed stage metadata without changing native cleanup logic.
# Root checks exact preparation/review pins before and after every dispatch.
import base64, datetime, getpass, hashlib, json, os, shlex, stat, subprocess, sys, time, warnings
from pathlib import Path
ROOT=Path(r"C:/Users/narut/AppData/Local/Temp/sumox-recorder-next-cleanup-20260927")
RAW=ROOT/"state/analysis/P7_recorder_next_cleanup02_raw"
REVIEW=ROOT/"state/reviews/P7_recorder_next_cleanup02_review.md"
MANIFEST=RAW/"preparation_manifest01.json"
def pin(p):
 b=p.read_bytes();return {"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_bytes())
def snapshot():
 assert pin(MANIFEST)["sha256"]=="__PREPARATION_MANIFEST_SHA256__"
 assert pin(REVIEW)["sha256"]=="__PREPARATION_REVIEW_SHA256__"
 files=read(MANIFEST)["files"]
 for n,v in files.items():assert pin(ROOT/n)==v,n
 return {str(ROOT/n):v for n,v in files.items()}|{str(MANIFEST):pin(MANIFEST),str(REVIEW):pin(REVIEW)}
def load_receipt(name,status):
 x=read(RAW/name);assert x["returncode"]==0 and not x["stderr"] and x["first_error"] is None and x["local_input_closure"]
 r=json.loads(x["stdout"]);assert r["status"]==status
 return r
def stamp(value):
 assert type(value) is dict and set(value)==set("ctime_ns dev gid ino mode mtime_ns nlink size uid".split())
 assert all(type(v) is int and 0<=v<2**63 for v in value.values())
 assert value["uid"]==value["gid"]==1000 and value["mode"]==stat.S_IFDIR|0o700 and value["ino"]>0
 return value
def finalized(action):
 template=read(RAW/("cleanup_"+action+"_intent01.json"))
 source=(RAW/template["program_path"]).read_text(encoding="utf8")
 before=source
 staged=load_receipt("cleanup_stage01.json","STAGED_CHECKED_NOT_EXECUTED")
 identity=stamp(staged["stage_identity"])
 assert staged["stage"]==template["stage"] and staged["originals_unchanged"] is True
 bindings={"__STAGE_IDENTITY_FROM_CHECKED_RECEIPT__":identity}
 if action=="retrieve":
  verified=load_receipt("cleanup_verify01.json","STAGED_FILES_VERIFIED_NOT_EXECUTED")
  assert verified["first_error"] is None and all(r["status"]=="PASS" for r in verified["closing_checks"])
  bindings["__SOURCE_IDENTITIES_FROM_VERIFICATION_RECEIPT__"]=verified["stage_before"]["files"]
 for name,value in bindings.items():
  assert source.count(name)==1
  source=source.replace(name,repr(value))
 argv=template["argv_prefix"]+[shlex.join(template["remote_argv_prefix"]+[source])]
 assert len(subprocess.list2cmdline(argv).encode("utf-16-le"))//2+1<30000
 result={**template,"status":"BOUND_FROM_CHECKED_ACTUAL_RECEIPTS","argv":argv,"bindings_actual":bindings,"template_program_sha256":hashlib.sha256(before.encode()).hexdigest(),"bound_program_sha256":hashlib.sha256(source.encode()).hexdigest()}
 target=RAW/("cleanup_"+action+"_bound_intent01.json")
 with target.open("x",encoding="utf8",newline="\n") as f:json.dump(result,f,indent=2);f.write("\n")
 return target,result
def main():
 assert sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv)==2
 action=sys.argv[1];assert action in ("absence","stage","verify","authenticated","retrieve")
 for profile in ("b4_stand","p3_drive","p3_turn","p3_stop","p4_reactive","p4_timing","p5_abort_timing"):
  for m in (0,1):
   result=read(ROOT/("state/analysis/P7_commissioning_build_raw/commission-"+profile+"-m"+str(m)+"-e9e91397f42f/result.json"))
   assert result["status"]=="COMPILE_CHECKED" and result["first_error"] is None
 inputs=snapshot()
 if action in ("verify","retrieve"):intent_path,intent=finalized(action)
 else:intent_path=RAW/("cleanup_"+action+"_intent01.json");intent=read(intent_path)
 if action=="stage":load_receipt("cleanup_absence01.json","ABSENT_OWNER_READONLY_CHECKED")
 if action=="authenticated":
  verified=load_receipt("cleanup_verify01.json","STAGED_FILES_VERIFIED_NOT_EXECUTED")
  assert verified["first_error"] is None and all(x["status"]=="PASS" for x in verified["closing_checks"])
  inputs[str(RAW/"cleanup_verify01.json")]=pin(RAW/"cleanup_verify01.json")
 inputs[str(intent_path)]=pin(intent_path)
 argv=intent["argv"];adb=Path(argv[0]);assert pin(adb)["sha256"]==intent["adb_sha256"]
 inputs[str(adb)]=pin(adb)
 invocation=RAW/("cleanup_"+action+"_invocation01.json")
 record={"schema":"d228-native-dispatch-v1","action":action,"started_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"intent":pin(intent_path),"inputs":inputs,"first_error":None,"returncode":None,"stdout":"","stderr":""}
 with invocation.open("x",encoding="utf8",newline="\n") as f:json.dump(record,f,indent=2);f.write("\n")
 credential=None;started=time.monotonic()
 try:
  if action=="authenticated":
   warnings.simplefilter("error",getpass.GetPassWarning)
   credential=getpass.getpass("Board cleanup authentication: ")
  reply=subprocess.run(argv,input=None if credential is None else (credential+"\n").encode(),stdin=subprocess.DEVNULL if credential is None else None,capture_output=True,timeout=70)
  record.update(returncode=reply.returncode,stdout=reply.stdout.decode(),stderr=reply.stderr.decode())
  assert len(reply.stdout)<=65536 and len(reply.stderr)<=65536 and reply.returncode==0 and not reply.stderr
 except Exception as e:
  record["first_error"]={"type":type(e).__name__,"message":str(e)}
  if isinstance(e,subprocess.TimeoutExpired):record.update(stdout=(e.stdout or b"").decode(errors="replace"),stderr=(e.stderr or b"").decode(errors="replace"))
 finally:
  credential=None
  record["elapsed_seconds"]=time.monotonic()-started
  record["closing_errors"]=[]
  for source,expected in inputs.items():
   try:
    assert pin(Path(source))==expected, "Local input changed"
   except Exception as error:record["closing_errors"].append({"path":source,"type":type(error).__name__,"message":str(error)})
  record["local_input_closure"]=not record["closing_errors"]
  output=RAW/("cleanup_"+action+"01.json")
  with output.open("x",encoding="utf8",newline="\n") as f:json.dump(record,f,indent=2);f.write("\n")
 print(json.dumps({"output":str(output),"sha256":pin(output)["sha256"],"returncode":record["returncode"],"first_error":record["first_error"],"local_input_closure":record["local_input_closure"],"remote_status":json.loads(record["stdout"]).get("status") if record["stdout"].lstrip().startswith("{") else None}))
 return int(record["first_error"] is not None or not record["local_input_closure"])
if __name__=="__main__":sys.exit(main())
