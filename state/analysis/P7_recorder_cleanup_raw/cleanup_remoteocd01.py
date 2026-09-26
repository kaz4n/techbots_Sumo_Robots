# Removes only three proven D221 temporary upload copies from one fixed directory.
# Retains their installed/build originals and refuses identity, content or use drift.
# Separate source review and exact before/after receipts bound this one cleanup.
import base64
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import sys
import types
import zlib

TARGET = '/tmp/remoteocd'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
EXPECTED = {'user': 'arduino', 'uid': 1000, 'gid': 1000, 'home': '/home/arduino',
            'sysname': 'Linux', 'release': '6.16.7-g0dd6551ae96b', 'machine': 'aarch64',
            'boot_id': BOOT, 'python': [3, 13, 5]}
HELPER_SHA = '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'
CORE = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/'
PINS = {
    'flash_sketch.cfg': (680, '38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c',
                         CORE + 'variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg'),
    'app.ino.bin-zsk.bin': (82912, '84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28',
        '/home/arduino/sumox26_codex_build/b4-app-m0-static01/build/app.ino.bin-zsk.bin'),
    'zephyr-arduino_uno_q_stm32u585xx.elf': (2303728, '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd',
        CORE + 'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf')}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def stamp(info):
    return {name: getattr(info, 'st_' + name) for name in
            ('dev', 'ino', 'mode', 'uid', 'gid', 'nlink', 'size', 'mtime_ns', 'ctime_ns')}


def directory_stamp(info):
    return tuple(getattr(info, 'st_' + name) for name in ('dev', 'ino', 'mode', 'uid', 'gid', 'nlink'))


def checked_bytes(raw, pin):
    require(len(raw) == pin[0] and hashlib.sha256(raw).hexdigest() == pin[1], 'Copy or original differs')


def processes():
    checked, owned = 0, 0
    pids = [p for p in Path('/proc').iterdir() if p.name.isdigit()]
    require(len(pids) <= 4096, 'Process count exceeds bound')
    for pid in pids:
        if int(pid.name) == os.getpid():
            continue
        try:
            name = (pid / 'comm').read_text().strip()
            require(name not in ('arduino-cli', 'remoteocd', 'openocd', 'dfu-util'), 'Native process is active')
            checked += 1
            if pid.stat().st_uid != 1000:
                continue
            owned += 1
            fds = list((pid / 'fd').iterdir())
            require(len(fds) <= 4096, 'File descriptor count exceeds bound')
            for item in [pid / 'cwd', *fds]:
                try:
                    target = os.readlink(item).removesuffix(' (deleted)')
                except FileNotFoundError:
                    continue
                require(target != TARGET and not target.startswith(TARGET + '/'), 'Scratch directory is in use')
        except (FileNotFoundError, ProcessLookupError) as error:
            try:
                pid.stat()
            except (FileNotFoundError, ProcessLookupError):
                continue
            raise error
    return {'process_names_checked': checked, 'same_uid_handles_checked': owned,
            'limitation': 'Other-user FDs are not inspectable; all readable process names are checked'}


def inventory(helper, fd, names):
    require(set(os.listdir(fd)) == set(names), 'Scratch child names changed')
    records = {}
    for name in sorted(names):
        info = os.stat(name, dir_fd=fd, follow_symlinks=False)
        require(stat.S_ISREG(info.st_mode) and info.st_uid == 1000 and info.st_gid == 1000
                and info.st_nlink == 1, 'Unsafe scratch child')
        raw, unused = helper.read_file(fd, name, PINS[name][0])
        checked_bytes(raw, PINS[name])
        require(stamp(os.stat(name, dir_fd=fd, follow_symlinks=False)) == stamp(info), 'Child drift')
        records[name] = {'identity': stamp(info), 'sha256': PINS[name][1]}
    return records


def cleanup(helper, root, out):
    expected = helper.identity(root)
    require(expected == EXPECTED, 'Wrong board identity')
    out['identity_before'] = expected
    for name, pin in PINS.items():
        checked_bytes(helper.logical_read(root, pin[2], pin[0]), pin)
    with helper.directory(root, '/tmp') as parent:
        with helper.child_directory(parent, 'remoteocd', TARGET) as child:
            info = os.fstat(child)
            require(info.st_dev == 34 and info.st_ino == 2281 and info.st_uid == 1000
                    and info.st_gid == 1000, 'Scratch directory identity changed')
            out['directory_before'] = stamp(info)
            original = inventory(helper, child, PINS)
            out['files_before'] = original
            remaining = set(PINS)
            for name in sorted(PINS):
                out['use_checks'].append(processes())
                require(helper.identity(root) == expected, 'Board identity changed')
                observed = inventory(helper, child, remaining)
                require(all(observed[n] == original[n] for n in remaining), 'Scratch replacement detected')
                named = os.stat('remoteocd', dir_fd=parent, follow_symlinks=False)
                require(directory_stamp(named) == directory_stamp(info), 'Directory replaced')
                os.unlink(name, dir_fd=child)
                out['removed'].append(name)
                remaining.remove(name)
                os.fsync(child)
            require(not os.listdir(child), 'Directory is not empty')
        named = os.stat('remoteocd', dir_fd=parent, follow_symlinks=False)
        require(directory_stamp(named) == directory_stamp(info), 'Directory replaced before removal')
        os.rmdir('remoteocd', dir_fd=parent)
        out['directory_removed'] = True
        os.fsync(parent)
        require(not os.path.lexists(TARGET), 'Scratch directory still exists')
    for name, pin in PINS.items():
        checked_bytes(helper.logical_read(root, pin[2], pin[0]), pin)
    out['identity_after'] = helper.identity(root)
    require(out['identity_after'] == expected, 'Closing identity changed')
    out['originals_unchanged'] = True


def expired(*unused):
    raise TimeoutError('Exact cleanup deadline expired')


def main():
    signal.signal(signal.SIGALRM, expired)
    signal.alarm(55)
    out = {'schema': 'recorder-exact-scratch-cleanup-v1', 'target': TARGET, 'status': 'FAILED',
           'removed': [], 'directory_removed': False, 'use_checks': [], 'first_error': None}
    root = None
    try:
        require(len(sys.argv) == 2 and sys.flags.dont_write_bytecode, 'One pinned helper and Python-B required')
        raw = zlib.decompress(base64.b64decode(sys.argv[1], validate=True))
        require(hashlib.sha256(raw).hexdigest() == HELPER_SHA, 'Helper changed')
        helper = types.ModuleType('fixed_scratch_helper')
        exec(compile(raw, '/__sumox__/helper.py', 'exec'), helper.__dict__)
        root = os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        cleanup(helper, root, out)
        out['status'] = 'REMOVED_EXACT_STALE_COPIES'
    except Exception as error:
        out['first_error'] = {'type': type(error).__name__, 'message': str(error)}
    finally:
        if root is not None:
            try:
                os.close(root)
            except Exception as error:
                out['close_error'] = {'type': type(error).__name__, 'message': str(error)}
                out['status'] = 'FAILED'
        print(json.dumps(out, separators=(',', ':')))
    return 0 if out['status'] == 'REMOVED_EXACT_STALE_COPIES' else 1


if __name__ == '__main__':
    sys.exit(main())
