# Read D102 target ABI from existing debug information on board Linux.
# Never create an inferior, connect to the MCU or execute a target expression.
# Preserve offline GDB type/sizeof/alignof output and the debug/tool identities.
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
import board_tool as board

receipt = REPO / 'build/app-receipts/39fedf763646445b8a7db864916e1121'
checked = json.loads((receipt / 'verified.json').read_text())
elf = checked['build_path'] + '/app.ino_debug.elf'
gdb = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb'
output = REPO / 'state/analysis/P2_frame_packing_raw/target_abi_retry'
output.mkdir(parents=True, exist_ok=False)
queries = ['set language c++', 'set max-value-size unlimited', 'p sizeof(recorder::FrameBuffer)',
    'p alignof(recorder::FrameBuffer)', 'p sizeof(recorder::StoredFrame)',
    'p alignof(recorder::StoredFrame)', 'p sizeof(recorder::AttemptRecorder)',
    'p alignof(recorder::AttemptRecorder)', 'p sizeof(app::Runtime)',
    'p alignof(app::Runtime)', 'ptype /o recorder::FrameBuffer']
args = [gdb, '-nx', '-nh', '-batch', elf]
for query in queries:
    args.extend(['-ex', query])
run = dict(argv=args, start_utc=datetime.now(timezone.utc).isoformat(),
           source_sha256=checked['source_sha256'],
           expected_debug_elf_sha256=checked['file_sha256'][elf],
           scope='Read-only existing DWARF/type expressions; no inferior/target/MCU or new compilation')
try:
    hashes = board.remote(board.target(), ['sha256sum', '--', gdb, elf], capture=True)
    run['hash_argv'] = ['sha256sum', '--', gdb, elf]
    run['hash_stdout'] = hashes.stdout
    run['hash_stderr'] = hashes.stderr
    assert hashes.stdout.splitlines()[1].split()[0] == checked['file_sha256'][elf]
    result = board.remote(board.target(), args, capture=True, timeout=30)
except subprocess.CalledProcessError as error:
    result = error
finally:
    if 'result' in globals():
        run.update(returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
        (output / 'stdout.txt').write_text(result.stdout or '', encoding='utf-8')
        (output / 'stderr.txt').write_text(result.stderr or '', encoding='utf-8')
    (output / 'receipt.json').write_text(json.dumps(run, indent=2)+'\n')
print(json.dumps(run))
print(result.stdout)
if result.returncode:
    raise SystemExit(result.returncode)
