"""Check used imports against the checked packaged loader ELF without execution."""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import re
import shlex
import subprocess

out = Path(__file__).resolve().parent
account = json.loads((out / 'app/loader_account.json').read_text())
receipt = json.loads((out / 'app/receipt/verified.json').read_text())
loader = [p for p in receipt['file_sha256'] if p.endswith('/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf')][0]
gdb = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb'
adb = str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
prefix = [adb, '-s', '2629958581', 'shell', '-T']
hash_args = ['sha256sum', '--', gdb, loader]
hashed = subprocess.run(prefix + [shlex.join(hash_args)], capture_output=True, text=True, timeout=30)
assert hashed.returncode == 0 and hashed.stdout.splitlines()[1].split()[0] == receipt['file_sha256'][loader]
args = [gdb, '-nx', '-nh', '-batch', loader]
for name in account['relocation_used_imports']:
    assert re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', name)
    args.extend(['-ex', 'echo IMPORT ' + name + '\\n', '-ex', 'p/x __llext_sym_' + name + '.addr'])
result = subprocess.run(prefix + [shlex.join(args)], capture_output=True, text=True, timeout=60)
addresses = {name: int(address, 16) for name, address in re.findall(r'IMPORT (\S+)\s+\$\d+ = (0x[0-9a-fA-F]+)', result.stdout)}
record = {'observed_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'File-only packaged ELF export inspection; no inferior or target',
          'argv': args, 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr,
          'hash_argv': hash_args, 'hash_returncode': hashed.returncode, 'hash_stdout': hashed.stdout,
          'expected_loader_sha256': receipt['file_sha256'][loader],
          'used_imports': account['relocation_used_imports'], 'addresses': addresses,
          'missing': [n for n in account['relocation_used_imports'] if n not in addresses],
          'all_used_imports_have_nonzero_export': len(addresses) == len(account['relocation_used_imports']) and all(addresses.values())}
(out / 'import_exports.json').write_text(json.dumps(record, indent=2) + '\n')
print('Import query exit', result.returncode, 'used', len(account['relocation_used_imports']),
      'resolved nonzero', record['all_used_imports_have_nonzero_export'])

if result.returncode or not record['all_used_imports_have_nonzero_export']:
    raise SystemExit(result.returncode or 1)
