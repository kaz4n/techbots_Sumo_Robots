# Captures a D-072 compile-only memory probe from current production source.
# Separates Linux compiler evidence from upload, MCU execution and RAM acceptance.
# Stores exact commands, statuses and staged source hashes for independent review.
from argparse import Namespace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'state/analysis/P2_rate_validation_raw'
sys.path.insert(0,str(ROOT/'tools'))
import board_tool as b
os.environ.update(SUMO_TRANSPORT='adb',SUMO_ADB_SERIAL='2629958581',
                  SUMO_ADB_EXECUTABLE=str(Path.home()/'AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'),
                  SUMO_REMOTE_ROOT='/home/arduino/sumox26-build')
receipt=OUT/'compile.json'
if receipt.exists(): raise SystemExit('Refusing to overwrite compile receipt')
report=dict(utc=datetime.now(timezone.utc).isoformat(),
            command=['python','tools/board_tool.py','flash','bench/p2_recorder_memory','--compile-only'],
            scope='Linux compile only, no upload/reset/MCU action',checks=[])
original=b.remote

def captured_remote(board,args,capture=False,timeout=None):
    row=dict(argv=args,target=board,utc=datetime.now(timezone.utc).isoformat())
    try:
        result=original(board,args,capture=True,timeout=timeout)
        row.update(exit_status=result.returncode,stdout=result.stdout,stderr=result.stderr)
    except subprocess.CalledProcessError as error:
        row.update(exit_status=error.returncode,stdout=error.stdout,stderr=error.stderr)
        raise
    finally:
        report['checks'].append(row)
        receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        if not capture:
            print(row.get('stdout') or '',end='',flush=True)
            print(row.get('stderr') or '',end='',file=sys.stderr,flush=True)
    return result

b.remote=captured_remote
code=0
try:
    b.flash(Namespace(sketch='bench/p2_recorder_memory',match=False,compile_only=True,startup='default'))
except (ValueError,OSError,subprocess.CalledProcessError) as error:
    report['error']=str(error); code=getattr(error,'returncode',2)
finally:
    b.remote=original
    folder=ROOT/'build/stage/p2_recorder_memory'
    report.update(exit_status=code,end_utc=datetime.now(timezone.utc).isoformat(),
                  staged_sha256=b.source_hash(folder),
                  staged_files={p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(folder.rglob('*')) if p.is_file()})
    receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
raise SystemExit(code)
