"""Collect bounded installed static-link sources and file-only binary metadata.
No compiler, image-processing tool, target, upload, or runtime is invoked.
Every read retains its argv, exit code, and output hash.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import shlex
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
ADB = str(Path(os.environ['LOCALAPPDATA']) / 'Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
PREFIX = [ADB, '-s', '2629958581', 'shell', '-T']
CORE = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
BIN = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/'
LOADER = CORE + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
TOOLS = ['/home/arduino/.arduino15/packages/arduino/tools/' + p for p in (
    'gen-rodata-ld/0.1.1/gen-rodata-ld',
    'zephyr-sketch-tool/0.4.1/zephyr-sketch-tool',
    'zephyr-check-size/0.1.0/zephyr-check-size')]


def run(label, argv, remote=True):
    command = PREFIX + [shlex.join(argv)] if remote else argv
    result = subprocess.run(command, capture_output=True, timeout=60)
    (OUT / (label + '.stdout')).write_bytes(result.stdout)
    (OUT / (label + '.stderr')).write_bytes(result.stderr)
    row = {'utc': datetime.now(timezone.utc).isoformat(), 'argv': command,
           'remote_argv': argv if remote else None, 'returncode': result.returncode,
           'stdout_bytes': len(result.stdout),
           'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(),
           'stderr_sha256': hashlib.sha256(result.stderr).hexdigest()}
    (OUT / (label + '.json')).write_text(json.dumps(row, indent=2) + '\n')
    return result


def main():
    devices = run('devices', [ADB, 'devices', '-l'], remote=False)
    assert devices.returncode == 0
    assert any(line.split()[:2] == ['2629958581', 'device']
               for line in devices.stdout.decode().splitlines())
    assert run('identity', ['id', '-un']).stdout.strip() == b'arduino'
    paths = [CORE + '/' + p for p in (
        'variants/_ldscripts/memory-static.ld',
        'variants/_ldscripts/build-static.ld',
        'variants/arduino_uno_q_stm32u585xx/syms-static.ld')]
    hashed = run('installed_hashes', ['sha256sum', '--', *paths, LOADER,
                                    BIN + 'arm-zephyr-eabi-gdb', *TOOLS])
    assert hashed.returncode == 0
    hashes = {line.split('  ', 1)[1]: line.split('  ', 1)[0]
              for line in hashed.stdout.decode().splitlines()}
    assert hashes[LOADER] == '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
    for path in paths:
        result = run(Path(path).name, ['cat', '--', path])
        assert result.returncode == 0
        assert hashlib.sha256(result.stdout).hexdigest() == hashes[path]
    rg = run('rg_available', ['sh', '-c', 'command -v rg'])
    if rg.returncode == 0:
        args = ['rg', '-n', '--max-count', '20', '--glob', '*.c', '--glob', '*.cpp',
                '--glob', '*.h', '--glob', '!**/llext-edk/**',
                r'\b__wrap_(random|calloc|free|malloc|realloc)\b', CORE]
    else:
        args = ['grep', '-RInE', '--include=*.c', '--include=*.cpp', '--include=*.h',
                '--exclude-dir=llext-edk', r'\b__wrap_(random|calloc|free|malloc|realloc)\b', CORE]
    found = run('wrapper_locations', args)
    assert found.returncode in (0, 1) and len(found.stdout) < 100000


if __name__ == '__main__':
    main()
