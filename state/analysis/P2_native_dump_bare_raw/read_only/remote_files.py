"""Explicit known source/service regular files; device nodes are never opened."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import stat

core = Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
paths = [Path('/usr/bin/arduino-router'), Path('/usr/bin/arduino-router-cli'),
    Path('/etc/systemd/system/arduino-router.service'),
    Path('/run/systemd/generator/arduino-router.service.d/10-imola.conf')]
paths += [core / path for path in ('boards.txt', 'platform.txt', 'cores/arduino/main.cpp',
    'cores/arduino/zephyrSerial.h', 'cores/arduino/zephyrSerial.cpp',
    'variants/arduino_uno_q_stm32u585xx/arduino_uno_q_stm32u585xx.overlay')]
out = []
for path in paths:
    item = {'path': str(path)}
    try:
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > 64 * 1024 * 1024:
            raise ValueError('Not an admitted regular file')
        blob = path.read_bytes()
        item.update(size=len(blob), sha256=hashlib.sha256(blob).hexdigest(), mtime_ns=info.st_mtime_ns,
            mode=oct(info.st_mode), uid=info.st_uid, gid=info.st_gid)
        if path.suffix in ('.service', '.conf'):
            allowed = ('[', '#', 'Description=', 'After=', 'Wants=', 'Requires=', 'ExecStart=',
                'ExecStartPre=', 'ExecStopPost=', 'Restart=', 'RestartSec=', 'User=', 'Group=')
            item['selected_lines'] = [{'line': i, 'text': line} for i, line in enumerate(blob.decode().splitlines(), 1)
                if line.startswith(allowed)]
        elif path.suffix in ('.cpp', '.h', '.overlay'):
            item['text'] = blob.decode()
    except (OSError, ValueError, UnicodeError) as error:
        item['error'] = type(error).__name__ + ': ' + str(error)
    out.append(item)
print(json.dumps({'utc': datetime.now(timezone.utc).isoformat(), 'files': out}))
