"""Filtered proc metadata only. No cmdline/environ, UART open/read or socket connect."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import stat
import subprocess

out = {'start_utc': datetime.now(timezone.utc).isoformat(), 'errors': []}
show = subprocess.run(['systemctl', 'show', 'arduino-router.service', '--property=MainPID', '--value'],
    capture_output=True, text=True, timeout=10)
out['main_pid_command'] = {'argv': show.args, 'returncode': show.returncode, 'stdout': show.stdout, 'stderr': show.stderr}
main_pid = int(show.stdout.strip()) if show.returncode == 0 and show.stdout.strip().isdigit() else 0
inodes = set()
out['monitor_tcp'] = []
for name in ('tcp', 'tcp6'):
    path = Path('/proc/net') / name
    try:
        lines = path.read_text().splitlines()
        for line in lines[1:]:
            parts = line.split()
            if int(parts[1].split(':')[1], 16) != 7500 and int(parts[2].split(':')[1], 16) != 7500:
                continue
            item = {'table': str(path), 'raw_line': line, 'local_hex': parts[1],
                'remote_hex': parts[2], 'state_hex': parts[3], 'uid': int(parts[7]), 'inode': parts[9]}
            out['monitor_tcp'].append(item)
            inodes.add(parts[9])
    except OSError as error:
        out['errors'].append({'path': str(path), 'error': str(error)})
out['router_unix'] = []
for line in Path('/proc/net/unix').read_text().splitlines()[1:]:
    parts = line.split()
    if len(parts) > 7 and parts[7] in ('/var/run/arduino-router.sock', '/run/arduino-router.sock'):
        out['router_unix'].append({'raw_line': line, 'inode': parts[6], 'path': parts[7]})
        inodes.add(parts[6])
device = Path('/dev/ttyHS1')
try:
    info = device.stat()
    out['uart_metadata'] = {'path': str(device), 'mode': oct(info.st_mode), 'uid': info.st_uid,
        'gid': info.st_gid, 'major': os.major(info.st_rdev), 'minor': os.minor(info.st_rdev),
        'character_device': stat.S_ISCHR(info.st_mode)}
except OSError as error:
    out['errors'].append({'path': str(device), 'error': str(error)})
pids = sorted((path for path in Path('/proc').iterdir() if path.name.isdigit()), key=lambda x: int(x.name))
out['coverage'] = {'pid_count': len(pids), 'pid_limit': 4096, 'fd_limit_per_pid': 4096,
    'pids_scanned': 0, 'fd_links_scanned': 0, 'denied_pid_count': 0, 'transient_errors': 0, 'capped': len(pids) > 4096}
out['relevant_processes'] = []
for path in pids[:4096]:
    try:
        fds = sorted((path / 'fd').iterdir(), key=lambda x: int(x.name))
        out['coverage']['pids_scanned'] += 1
        if len(fds) > 4096:
            out['coverage']['capped'] = True
        hits = []
        for fd in fds[:4096]:
            try:
                target = os.readlink(fd)
                out['coverage']['fd_links_scanned'] += 1
                relevant = target == '/dev/ttyHS1' or target in {'socket:[' + i + ']' for i in inodes}
                if relevant:
                    hits.append({'fd': int(fd.name), 'target': target})
            except OSError:
                out['coverage']['transient_errors'] += 1
        if hits or int(path.name) == main_pid:
            item = {'pid': int(path.name), 'comm': (path / 'comm').read_text().strip(), 'fd_matches': hits}
            item['status_fields'] = [line for line in (path / 'status').read_text().splitlines()
                if line.startswith(('Name:', 'State:', 'Uid:', 'Gid:', 'Threads:', 'PPid:'))]
            item['exe'] = os.readlink(path / 'exe')
            if int(path.name) == main_pid:
                item['exe_sha256'] = hashlib.sha256((path / 'exe').read_bytes()).hexdigest()
            out['relevant_processes'].append(item)
    except PermissionError:
        out['coverage']['denied_pid_count'] += 1
    except OSError:
        out['coverage']['transient_errors'] += 1
out['end_utc'] = datetime.now(timezone.utc).isoformat()
print(json.dumps(out))
