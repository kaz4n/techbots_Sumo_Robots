"""Read checked debug ELF type layouts on board Linux; never create an inferior."""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import shlex
import subprocess

out = Path(__file__).resolve().parent
root = out.parents[2]
adb = str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
gdb = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb'
common = ['app::Runtime', 'app::Transaction', 'app::TransactionReport',
          'fsm::Robot', 'fsm::Robot::Pending', 'fsm::Robot::Tick',
          'fsm::RobotInput', 'fsm::RobotResult', 'openers::Result',
          'openers::FlankResult', 'openers::WaitResult', 'openers::Direct',
          'openers::Flank', 'openers::Wait', 'recorder::AttemptRecorder',
          'recorder::FrameBuffer']
profiles = [
    ('D135_opener', out / 'opener_timing/receipt/verified.json', 'opener_timing'),
    ('D134_default', root / 'state/analysis/P5_native_compile_raw/app/receipt/verified.json', 'app'),
]
for label, receipt_path, project in profiles:
    folder = out / label
    folder.mkdir(exist_ok=False)
    receipt = json.loads(receipt_path.read_text())
    elf = receipt['build_path'] + '/' + project + '.ino_debug.elf'
    types = common + (['fsm::OpponentReadWindow', 'openers::AbortEvidence'] if label == 'D135_opener' else [])
    queries = ['set language c++', 'set max-value-size unlimited']
    for typename in types:
        queries += ['echo TYPE ' + typename + '\\n', 'p sizeof(' + typename + ')',
                    'p alignof(' + typename + ')', 'ptype /o ' + typename]
    args = [gdb, '-nx', '-nh', '-batch', elf]
    for query in queries:
        args.extend(['-ex', query])
    hash_argv = [adb, '-s', '2629958581', 'shell', '-T', shlex.join(['sha256sum', '--', gdb, elf])]
    hashed = subprocess.run(hash_argv, capture_output=True, text=True, timeout=30)
    record = {'start_utc': datetime.now(timezone.utc).isoformat(), 'source_sha256': receipt['source_sha256'],
              'scope': 'Read-only existing DWARF/types; no target connection, inferior, MCU or compilation',
              'hash_argv': hash_argv, 'hash_returncode': hashed.returncode,
              'hash_stdout': hashed.stdout, 'hash_stderr': hashed.stderr,
              'expected_debug_elf_sha256': receipt['file_sha256'][elf]}
    assert hashed.returncode == 0
    assert hashed.stdout.splitlines()[1].split()[0] == receipt['file_sha256'][elf]
    argv = [adb, '-s', '2629958581', 'shell', '-T', shlex.join(args)]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    record.update(argv=argv, returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
    (folder / 'abi_stdout.txt').write_text(result.stdout, encoding='utf-8')
    (folder / 'abi_stderr.txt').write_text(result.stderr, encoding='utf-8')
    (folder / 'abi_receipt.json').write_text(json.dumps(record, indent=2) + '\n')
    print(label, 'offline type query exit', result.returncode, 'output bytes', len(result.stdout), flush=True)
    if result.returncode:
        print(result.stderr, flush=True)
