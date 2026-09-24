"""Record the D119 checked compile-only footprint validation; no upload."""
from pathlib import Path
from datetime import datetime, timezone
import json, os, subprocess, sys
root=Path(__file__).resolve().parents[4]
out=Path(__file__).resolve().parent
env=os.environ.copy()
env.update(SUMO_TRANSPORT="adb", SUMO_ADB_SERIAL="2629958581", SUMO_ADB_EXECUTABLE=str(Path(os.environ["LOCALAPPDATA"])/"Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe"), SUMO_REMOTE_ROOT="/home/arduino/sumox26_codex_build")
argv=[sys.executable,"tools/board_tool.py","flash","app","--compile-only"]
start=datetime.now(timezone.utc).isoformat()
result=subprocess.run(argv,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=900)
(out/"app_compile.txt").write_bytes(result.stdout)
record={"argv":argv,"start_utc":start,"end_utc":datetime.now(timezone.utc).isoformat(),"returncode":result.returncode,"transport":"adb","serial":"2629958581","compile_only":True}
(out/"app_compile.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(json.dumps(record),flush=True)
print(result.stdout[-8000:].decode("utf-8","replace"),flush=True)
raise SystemExit(result.returncode)
