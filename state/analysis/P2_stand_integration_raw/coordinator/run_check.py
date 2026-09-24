"""Record exact D120 commands and source hashes; no automatic hardware action."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[4]
out = Path(__file__).resolve().parent
name, *argv = sys.argv[1:]
paths = [*root.glob('src/core/*'), *root.glob('src/app/*'), root/'src/config.h',
         root/'host/CMakeLists.txt', root/'tools/board_tool.py',
         root/'tools/app_build_policy.py', root/'tests/test_stand_integration.cc',
         root/'tests/locked/test_stand_integration_safety.cc',
         root/'tests/tooling/test_motor_direction_policy.py']
def hashes():
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}
record = {'argv': argv, 'cwd': str(root), 'start_utc': datetime.now(timezone.utc).isoformat(),
          'before_sha256': hashes()}
result = subprocess.run(argv, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1200)
(out/(name+'.txt')).write_bytes(result.stdout)
record.update(end_utc=datetime.now(timezone.utc).isoformat(), returncode=result.returncode,
              after_sha256=hashes())
(out/(name+'.json')).write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
print(name, 'exit', result.returncode, flush=True)
print(result.stdout[-5000:].decode('utf-8', 'replace'), flush=True)
raise SystemExit(result.returncode)
