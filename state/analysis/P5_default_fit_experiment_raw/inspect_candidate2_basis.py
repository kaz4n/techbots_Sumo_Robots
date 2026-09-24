"""Inspect existing checked Thumb code only; no compiler or target connection."""
from pathlib import Path
import json
import os
import shlex
import subprocess

out = Path(__file__).resolve().parent
root = out.parents[2]
adb = str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
gdb = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb'
receipts = [('candidate1', out / 'app_attempt02/receipt/verified.json'),
            ('D134', root / 'state/analysis/P5_native_compile_raw/app/receipt/verified.json'),
            ('D128', root / 'state/analysis/P4_reactive_profile_raw/app/receipt/verified.json')]
records = []
for label, path in receipts:
    receipt = json.loads(path.read_text())
    elf = receipt['build_path'] + '/app.ino_debug.elf'
    prefix = [adb, '-s', '2629958581', 'shell', '-T']
    hashed = subprocess.run(prefix + [shlex.join(['sha256sum', '--', gdb, elf])],
                            capture_output=True, text=True, timeout=30)
    assert hashed.returncode == 0
    assert hashed.stdout.splitlines()[1].split()[0] == receipt['file_sha256'][elf]
    args = [gdb, '-nx', '-nh', '-batch', elf, '-ex', 'set arm force-mode thumb']
    for name in ('_ZN3fsm5Robot11startOpenerEv', '_ZN7openers6Direct4stepEjfbh'):
        args.extend(['-ex', 'disassemble /r ' + name])
    result = subprocess.run(prefix + [shlex.join(args)], capture_output=True, text=True, timeout=30)
    records.append({'label': label, 'source_sha256': receipt['source_sha256'],
        'argv': args, 'returncode': result.returncode, 'hash_stdout': hashed.stdout,
        'stderr': result.stderr})
    (out / (label + '_candidate2_basis.txt')).write_text(result.stdout)
    assert result.returncode == 0
(out / 'candidate2_basis_receipts.json').write_text(json.dumps(records, indent=2) + '\n')
print('Checked existing Thumb disassembly collected for', ', '.join(label for label, _ in receipts))
