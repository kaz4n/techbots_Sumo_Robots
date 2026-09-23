"""Explicit installed public router unit/generator/config files; no execution."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import stat

paths = ['/etc/systemd/system/arduino-router-serial.path',
    '/etc/systemd/system/arduino-router-serial.service',
    '/usr/lib/systemd/system-generators/systemd-arduino-router.sh',
    '/var/lib/arduino-router/config/10-imola.conf']
out = []
for name in paths:
    item = {'path': name}
    try:
        path = Path(name)
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > 131072:
            raise ValueError('Not an admitted small regular file')
        blob = path.read_bytes()
        item.update(size=len(blob), sha256=hashlib.sha256(blob).hexdigest(), text=blob.decode())
    except (OSError, ValueError, UnicodeError) as error:
        item['error'] = type(error).__name__ + ': ' + str(error)
    out.append(item)
print(json.dumps({'utc': datetime.now(timezone.utc).isoformat(), 'files': out}))
