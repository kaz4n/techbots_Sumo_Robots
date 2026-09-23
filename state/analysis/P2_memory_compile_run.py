# Captures one D-071 compile-only experiment and its exact remote build commands.
# Preserves failures without treating a generated ELF as successful compilation.
# Run with python state/analysis/P2_memory_compile_run.py 25 (or 50).
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'state/analysis/P2_memory_validation_raw'
sys.path.insert(0, str(ROOT / 'tools'))
import recorder_memory_build
board_tool = recorder_memory_build.board_tool

rate = int(sys.argv[1])
if rate not in (25, 50):
    raise SystemExit('rate must be25 or50')
os.environ.update(SUMO_TRANSPORT='adb', SUMO_ADB_SERIAL='2629958581',
                  SUMO_ADB_EXECUTABLE=str(Path.home() / 'AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'),
                  SUMO_REMOTE_ROOT='/home/arduino/sumox26-build')
OUT.mkdir(exist_ok=True)
suffix = sys.argv[2] if len(sys.argv) > 2 else ''
if suffix and not re.fullmatch(r'_retry[1-9][0-9]*', suffix):
    raise SystemExit('invalid receipt suffix')
receipt = OUT / f'compile_{rate}{suffix}.json'
if receipt.exists():
    raise SystemExit('Refusing to overwrite a compile receipt')
original = board_tool.remote
report = dict(start_utc=datetime.now(timezone.utc).isoformat(), rate_hz=rate,
              scope='Linux compile only; no upload/reset/MCU or probe execution',
              command=[sys.executable, 'tools/recorder_memory_build.py', '--log-hz', str(rate), '--compile-only'],
              before_config_sha256=hashlib.sha256((ROOT/'src/config.h').read_bytes()).hexdigest(),
              remote_commands=[])

def captured_remote(board, args, capture=False, timeout=None):
    row = dict(target=board, argv=args, start_utc=datetime.now(timezone.utc).isoformat())
    try:
        result = original(board, args, capture=True, timeout=timeout)
        row.update(exit_status=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except subprocess.CalledProcessError as error:
        row.update(exit_status=error.returncode, stdout=error.stdout, stderr=error.stderr)
        raise
    finally:
        row['end_utc'] = datetime.now(timezone.utc).isoformat()
        report['remote_commands'].append(row)
        receipt.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        if not capture:
            print(row.get('stdout') or '', end='', flush=True)
            print(row.get('stderr') or '', end='', file=sys.stderr, flush=True)
    return result

board_tool.remote = captured_remote
code = 2
try:
    code = recorder_memory_build.main(['--log-hz', str(rate), '--compile-only'])
    code = 0 if code is None else code
except Exception as error:
    report['exception'] = repr(error)
    code = error.returncode if isinstance(error, subprocess.CalledProcessError) else 2
finally:
    board_tool.remote = original
    report.update(exit_status=code, end_utc=datetime.now(timezone.utc).isoformat(),
                  after_config_sha256=hashlib.sha256((ROOT/'src/config.h').read_bytes()).hexdigest())
    receipt.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
raise SystemExit(code)
