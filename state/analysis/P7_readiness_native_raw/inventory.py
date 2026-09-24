"""Capture a bounded read-only Linux/toolchain inventory before a native-build decision."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shlex
import shutil
import subprocess

out = Path(__file__).resolve().parent
root = out.parents[2]
adb = str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
serial = '2629958581'
prior_path = root / 'state/analysis/P5_match_native_raw/app/receipt/verified.json'
prior = json.loads(prior_path.read_text())
gdb = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb'
pins = {name: digest for name, digest in prior['file_sha256'].items()
        if name.startswith('/home/arduino/.arduino15/')}
record = {
    'start_utc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Read-only Linux inventory and file hashes; no staging, compilation, upload, reset, MCU or runtime access.',
    'adb_sha256': hashlib.sha256(Path(adb).read_bytes()).hexdigest(),
    'prior_receipt_sha256': hashlib.sha256(prior_path.read_bytes()).hexdigest(),
    'local_disk': dict(zip(('total', 'used', 'free'), shutil.disk_usage(root))),
    'commands': [],
}


def run(argv, timeout=30):
    result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    row = {'argv': argv, 'returncode': result.returncode,
           'stdout': result.stdout, 'stderr': result.stderr}
    record['commands'].append(row)
    (out / 'inventory.json').write_text(json.dumps(record, indent=2) + '\n')
    return result


devices = run([adb, 'devices', '-l'])
assert devices.returncode == 0
assert any(line.split()[:2] == [serial, 'device'] for line in devices.stdout.splitlines())
commands = [
    ['id', '-un'], ['uname', '-r'], ['arduino-cli', 'version'],
    ['arduino-cli', 'core', 'list'],
    ['df', '-B1', '/home/arduino', '/tmp', '/dev/shm'], ['free', '-b'],
    ['ps', '-eo', 'pid,comm'],
    ['du', '-sk', '/home/arduino/sumox26_codex_build'],
    ['stat', '-c', '%n %s %U %G', '/home/arduino/sumox26_codex_build',
     prior['build_path'] + '/app.ino_debug.elf'],
    ['sha256sum', '--', *pins, gdb],
]
for args in commands:
    result = run([adb, '-s', serial, 'shell', '-T', shlex.join(args)], timeout=60)
    if result.returncode:
        raise SystemExit(result.returncode)
hashes = {line.split(maxsplit=1)[1].strip(): line.split()[0]
          for line in result.stdout.splitlines()}
record['installed_pin_comparison'] = {name: hashes.get(name) == digest
                                      for name, digest in pins.items()}
record['gdb_sha256'] = hashes.get(gdb)
record['end_utc'] = datetime.now(timezone.utc).isoformat()
(out / 'inventory.json').write_text(json.dumps(record, indent=2) + '\n')
assert all(record['installed_pin_comparison'].values())
print(json.dumps({'commands': len(record['commands']),
                  'installed_pins_match': len(pins), 'gdb_sha256': record['gdb_sha256'],
                  'local_disk_free': record['local_disk']['free']}, indent=2))
