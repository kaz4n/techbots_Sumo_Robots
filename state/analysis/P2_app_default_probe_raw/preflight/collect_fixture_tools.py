# Copies three pinned Linux tool files as opaque host-test inputs.
# Exact hashes preserve real identity checks without executing the copied tools.
# The receipt records bounded read-only Linux commands; no MCU operation occurs.
from pathlib import Path
from datetime import datetime, timezone
import base64
import hashlib
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board

os.environ['SUMO_TRANSPORT'] = 'adb'
os.environ['SUMO_ADB_SERIAL'] = '2629958581'
os.environ['SUMO_ADB_EXECUTABLE'] = str(Path(os.environ['LOCALAPPDATA']) /
    'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
PINS = [
    ('openocd.bin', '/opt/openocd/bin/openocd',
     '04778a80c5c619ee4eef7505db91328f1d7e789107c496f2ddcf96d081f5b0ff'),
    ('swj-dp.tcl', '/opt/openocd/share/openocd/scripts/target/swj-dp.tcl',
     'aad132008735bbafea3d18a304632c638f0fb99bfc19530c9f577eda2b10410a'),
    ('readelf.bin', '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-readelf',
     'c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e'),
]
OUT = Path(__file__).resolve().parent.parent / 'fixture_tools'
OUT.mkdir(exist_ok=False)
receipt = {'scope': 'READ_ONLY_LINUX_FILES_NO_TOOL_EXECUTION_NO_MCU', 'files': []}
try:
    for name, source, expected in PINS:
        program = '\n'.join([
            'from pathlib import Path', 'import hashlib,base64,json',
            f'p=Path({source!r})', f'expected={expected!r}',
            'assert p.is_absolute() and p.is_file() and p.resolve()==p',
            'assert all(not q.is_symlink() for q in (p,*p.parents))',
            'assert 0<p.stat().st_size<=16777216', 'b=p.read_bytes()',
            'assert hashlib.sha256(b).hexdigest()==expected',
            'print(json.dumps({"bytes":len(b),"sha256":expected,"data":base64.b64encode(b).decode()}))',
        ])
        entry = {'argv': ['python3', '-c', program], 'timeout_seconds': 30,
                 'start_utc': datetime.now(timezone.utc).isoformat()}
        receipt['files'].append(entry)
        result = board.remote(board.target(), entry['argv'], capture=True, timeout=30)
        entry.update(returncode=result.returncode, stderr=result.stderr,
                     stdout_sha256=hashlib.sha256(result.stdout.encode()).hexdigest())
        data = json.loads(result.stdout)
        blob = base64.b64decode(data['data'], validate=True)
        assert len(blob) == data['bytes'] and hashlib.sha256(blob).hexdigest() == expected
        with (OUT / name).open('xb') as stream:
            stream.write(blob)
        entry.update(path=str((OUT / name).relative_to(ROOT)), bytes=len(blob),
                     sha256=expected, end_utc=datetime.now(timezone.utc).isoformat())
    receipt['status'] = 'PASS_EXACT_OPAQUE_TOOL_FILES'
except Exception as error:
    receipt.update(status='FAILED', error=repr(error))
    raise
finally:
    (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'files': [
    {k: f.get(k) for k in ('path', 'bytes', 'sha256')} for f in receipt['files']]}, indent=2))
