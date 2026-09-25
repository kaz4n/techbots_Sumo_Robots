# Removes only the exact known failed loader-copy fragment after fresh checks.
# Preserves all run evidence and fails closed on identity, file or process drift.
# Separate source review and the actual removal receipt qualify this one-shot task.
import hashlib
import json
import os
from pathlib import Path
import stat

BOOT = '6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6'
NAME = 'zephyr-arduino_uno_q_stm32u585xx.elf'
SHA = 'b6fced5c7a35d75e5e5b681ad9806510bb1f066f8097a198b9186d06867d50cf'


def require(value, message):
    if not value:
        raise ValueError(message)


def identity():
    require(os.getuid() == 1000 and os.uname().machine == 'aarch64', 'Wrong board account')
    require(Path('/proc/sys/kernel/random/boot_id').read_text().strip() == BOOT, 'Wrong boot')


def processes():
    count = 0
    with os.scandir('/proc') as entries:
        for entry in entries:
            if not entry.name.isdigit():
                continue
            count += 1
            require(count <= 4096, 'Process count bound')
            try:
                with open('/proc/' + entry.name + '/comm', 'rb') as stream:
                    name = stream.read(257)
            except FileNotFoundError:
                try:
                    os.stat('/proc/' + entry.name, follow_symlinks=False)
                except FileNotFoundError:
                    continue
                raise
            require(len(name) <= 256, 'Process name bound')
            require(name.rstrip(b'\n') not in (b'openocd', b'remoteocd', b'arduino-cli'),
                    'Conflicting process')


def file_identity(value):
    return (value.st_dev, value.st_ino, value.st_uid, stat.S_IMODE(value.st_mode),
            value.st_size, value.st_mtime_ns, value.st_nlink, stat.S_ISREG(value.st_mode))


def remove():
    result = {'status': 'FAILED', 'unlinked': False, 'directory_removed': False}
    identity()
    processes()
    parent = os.open('/tmp', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        folder = os.open('remoteocd', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)
        try:
            info = os.fstat(folder)
            require((info.st_dev, info.st_ino, info.st_uid) == (34, 800, 1000), 'Folder changed')
            require(os.listdir(folder) == [NAME], 'Unexpected folder contents')
            fd = os.open(NAME, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=folder)
            try:
                expected = (34, 801, 1000, 0o664, 1048576, 1790295081758518138, 1, True)
                require(file_identity(os.fstat(fd)) == expected, 'Fragment changed')
                with os.fdopen(os.dup(fd), 'rb') as stream:
                    raw = stream.read(1048577)
                require(len(raw) == 1048576 and hashlib.sha256(raw).hexdigest() == SHA,
                        'Fragment bytes changed')
                identity()
                processes()
                require(file_identity(os.fstat(fd)) == expected and
                        file_identity(os.stat(NAME, dir_fd=folder, follow_symlinks=False)) == expected,
                        'Fragment identity drift')
                live = os.stat('remoteocd', dir_fd=parent, follow_symlinks=False)
                require(stat.S_ISDIR(live.st_mode) and (live.st_dev, live.st_ino) == (34, 800),
                        'Folder path changed')
                require(os.listdir(folder) == [NAME], 'Folder contents changed')
                os.unlink(NAME, dir_fd=folder)
                result['unlinked'] = True
                require(os.fstat(fd).st_nlink == 0 and os.listdir(folder) == [], 'Unlink not observed')
                live = os.stat('remoteocd', dir_fd=parent, follow_symlinks=False)
                require(stat.S_ISDIR(live.st_mode) and
                        (live.st_dev, live.st_ino, live.st_uid) == (34, 800, 1000),
                        'Folder changed before removal')
                os.rmdir('remoteocd', dir_fd=parent)
                result['directory_removed'] = True
                require(os.fstat(folder).st_nlink == 0, 'Owned folder removal not observed')
                require(not os.path.lexists('/tmp/remoteocd'), 'Folder absence not observed')
                result.update(status='REMOVED', bytes=1048576, sha256=SHA, boot_id=BOOT)
            finally:
                os.close(fd)
        finally:
            os.close(folder)
    except Exception as error:
        result['error'] = {'type': type(error).__name__, 'message': str(error)}
    finally:
        os.close(parent)
    print(json.dumps(result, separators=(',', ':')))
    if result['status'] != 'REMOVED':
        raise SystemExit(1)


if __name__ == '__main__':
    remove()
