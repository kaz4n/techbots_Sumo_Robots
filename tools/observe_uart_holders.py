# Observes Linux UART holders through bounded process and thread metadata.
# It closes visibility gaps without opening the UART or granting readiness.
# Tested with synthetic metadata providers and read-only source review.
import datetime
import hashlib
import json
import os
import signal
import stat
import subprocess
import sys
import time

PID_LIMIT = 4096
TASK_LIMIT = 8192
FD_LIMIT = 4096
FD_STATS_LIMIT = 65536
ERROR_LIMIT = 1024
HOLDER_LIMIT = 4096
SWEEP_SECONDS = 15
OUTPUT_LIMIT = 1048576
DEVICE = '/dev/ttyHS1'
ROUTER_QUERY = ['/usr/bin/systemctl', 'show', 'arduino-router.service',
                '--property=MainPID', '--value']


def read_small(path, limit=65536):
    with open(path, 'rb') as stream:
        body = stream.read(limit + 1)
    if len(body) > limit:
        raise ValueError('Metadata size limit')
    return body.decode('utf-8', 'strict').strip()


def numeric_names(path, limit, omit_directory=None, fd_stat=os.stat):
    names = []
    with os.scandir(path) as entries:
        for index, entry in enumerate(entries):
            if index >= limit + 256:
                return sorted(names), True
            if entry.name.isdecimal():
                if omit_directory is not None:
                    info = fd_stat(entry.path)
                    if (stat.S_ISDIR(info.st_mode) and
                            (info.st_dev, info.st_ino) == omit_directory):
                        continue
                if len(names) == limit:
                    return sorted(names), True
                names.append(int(entry.name))
    return sorted(names), False


def stamp(info):
    return dict(dev=info.st_dev, ino=info.st_ino, mode=info.st_mode,
                uid=info.st_uid, gid=info.st_gid, size=info.st_size,
                mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns)


def process_start(path):
    text = read_small(path + '/stat', 4096)
    end = text.rfind(')')
    fields = text[end + 2:].split()
    if end < 1 or len(fields) < 20:
        raise ValueError('Malformed process stat')
    return int(fields[19])


def executable(pid):
    path = '/proc/' + str(pid) + '/exe'
    target = os.readlink(path)
    with open(path, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > 33554432:
            raise ValueError('Router executable type/size limit')
        digest = hashlib.sha256()
        left = before.st_size
        while left:
            part = stream.read(min(65536, left))
            if not part:
                raise ValueError('Router executable truncated')
            digest.update(part)
            left -= len(part)
        if stream.read(1) or stamp(os.fstat(stream.fileno())) != stamp(before):
            raise ValueError('Router executable changed')
    if os.readlink(path) != target or stamp(os.stat(path)) != stamp(before):
        raise ValueError('Router executable identity changed')
    return dict(target=target, stat=stamp(before), sha256=digest.hexdigest())


class LinuxMetadata:
    def __init__(self):
        self.fd_stats = 0

    def stat_fd(self, path):
        if self.fd_stats >= FD_STATS_LIMIT:
            raise ValueError('FD metadata stat limit')
        self.fd_stats += 1
        return os.stat(path)

    def ids(self, pid=None, tid=None):
        if pid is None:
            return numeric_names('/proc', PID_LIMIT)
        path = '/proc/' + str(pid) + '/task'
        if tid is None:
            return numeric_names(path, TASK_LIMIT)
        path += '/' + str(tid) + '/fd'
        # Our own scandir descriptor is a known directory, never a UART holder.
        # Omit it while still open so closing it does not invent a vanished FD.
        own_directory = None
        if pid == os.getpid():
            info = os.stat(path)
            own_directory = (info.st_dev, info.st_ino)
        return numeric_names(path, FD_LIMIT, own_directory, self.stat_fd)

    def start(self, pid, tid=None):
        path = '/proc/' + str(pid)
        if tid is not None:
            path += '/task/' + str(tid)
        return process_start(path)

    def fd(self, pid, tid, number):
        path = '/proc/' + str(pid) + '/task/' + str(tid) + '/fd/' + str(number)
        info = self.stat_fd(path)
        if not stat.S_ISCHR(info.st_mode):
            return None
        return dict(major=os.major(info.st_rdev), minor=os.minor(info.st_rdev),
                    dev=info.st_dev, ino=info.st_ino)

    def holder_identity(self, pid):
        path = '/proc/' + str(pid)
        status = read_small(path + '/status')
        selected = {line.split(':', 1)[0]: line.split(':', 1)[1].strip()
                    for line in status.splitlines()
                    if line.startswith(('Name:', 'Uid:', 'Gid:'))}
        return dict(status=selected, executable=os.readlink(path + '/exe'),
                    executable_stat=stamp(os.stat(path + '/exe')))

    def boundary(self):
        boot = read_small('/proc/sys/kernel/random/boot_id', 128)
        info = os.stat(DEVICE)
        device = dict(path=DEVICE, stat=stamp(info),
                      character=stat.S_ISCHR(info.st_mode),
                      major=os.major(info.st_rdev), minor=os.minor(info.st_rdev))
        if not device['character'] or (device['major'], device['minor']) != (239, 1):
            raise ValueError('Unexpected UART device identity')
        result = subprocess.run(ROUTER_QUERY, stdin=subprocess.DEVNULL,
                                capture_output=True, timeout=5, check=False)
        if result.returncode or result.stderr or len(result.stdout) > 32:
            raise ValueError('Router PID query failed')
        pid = int(result.stdout.strip())
        if pid <= 0:
            raise ValueError('Router is not running')
        started = self.start(pid)
        router = dict(pid=pid, start=started, executable=executable(pid))
        if self.start(pid) != started:
            raise ValueError('Router process replaced')
        status = read_small('/proc/self/status')
        caps = {line.split(':', 1)[0]: line.split(':', 1)[1].strip()
                for line in status.splitlines() if line.startswith('Cap')}
        return dict(boot_id=boot, kernel=os.uname().release, device=device,
                    router=router, uid=os.getresuid(), gid=os.getresgid(),
                    groups=os.getgroups(), capabilities=caps)


def problem(out, kind, **details):
    out['problem_count'] += 1
    if len(out['problems']) < ERROR_LIMIT:
        out['problems'].append(dict(kind=kind, **details))
    else:
        out['problem_details_truncated'] = True


def attempt(out, label, operation, **identity):
    try:
        return operation()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        problem(out, label, error=type(error).__name__,
                errno=getattr(error, 'errno', None), **identity)
        return None


def names(out, ops, pid=None, tid=None):
    value = attempt(out, 'enumeration', lambda: ops.ids(pid, tid), pid=pid, tid=tid)
    if value is None:
        return None
    rows, capped = value
    if capped:
        problem(out, 'enumeration_limit', pid=pid, tid=tid)
    return rows


def changed(out, label, before, after, **identity):
    if before != after:
        problem(out, label, **identity)


def scan_task(out, ops, clock, deadline, budget, pid, tid, process_token):
    token = attempt(out, 'task_start', lambda: ops.start(pid, tid), pid=pid, tid=tid)
    fds = names(out, ops, pid, tid)
    if token is None or fds is None:
        return
    for fd in fds:
        if clock() >= deadline or budget['fd_stats'] >= FD_STATS_LIMIT:
            problem(out, 'time_or_fd_stat_limit', pid=pid, tid=tid)
            return
        budget['fd_stats'] += 1
        out['fd_stats'] += 1
        row = attempt(out, 'fd_stat', lambda: ops.fd(pid, tid, fd),
                      pid=pid, tid=tid, fd=fd)
        if row is not None and (row['major'], row['minor']) == (239, 1):
            if len(out['holders']) >= HOLDER_LIMIT:
                problem(out, 'holder_limit', pid=pid, tid=tid)
                return
            out['holders'].append(dict(pid=pid, tid=tid, fd=fd,
                process_start=process_token, task_start=token, device=row))
            key = str(pid)
            if key not in out['holder_processes']:
                out['holder_processes'][key] = attempt(out, 'holder_identity',
                    lambda: ops.holder_identity(pid), pid=pid)
    after = names(out, ops, pid, tid)
    end = attempt(out, 'task_start_after', lambda: ops.start(pid, tid), pid=pid, tid=tid)
    changed(out, 'fd_set_changed', fds, after, pid=pid, tid=tid)
    changed(out, 'task_replaced', token, end, pid=pid, tid=tid)


def scan_process(out, ops, clock, deadline, budget, pid):
    token = attempt(out, 'process_start', lambda: ops.start(pid), pid=pid)
    tasks = names(out, ops, pid)
    if token is None or tasks is None:
        return
    for index, tid in enumerate(tasks):
        if clock() >= deadline or out['tasks'] >= TASK_LIMIT:
            problem(out, 'time_or_task_limit', pid=pid)
            return
        out['tasks'] += 1
        scan_task(out, ops, clock, deadline, budget, pid, tid, token)
        if budget['fd_stats'] >= FD_STATS_LIMIT:
            if index + 1 < len(tasks):
                problem(out, 'unvisited_tasks_at_fd_limit', pid=pid,
                        remaining=len(tasks) - index - 1)
            break
    after = names(out, ops, pid)
    end = attempt(out, 'process_start_after', lambda: ops.start(pid), pid=pid)
    changed(out, 'task_set_changed', tasks, after, pid=pid)
    changed(out, 'process_replaced', token, end, pid=pid)


def sweep(ops, clock, budget):
    start = clock()
    out = dict(processes=0, tasks=0, fd_stats=0, holders=[], holder_processes={}, problems=[],
               problem_count=0, problem_details_truncated=False)
    pids = names(out, ops)
    if pids is not None:
        for pid in pids:
            if clock() >= start + SWEEP_SECONDS or budget['fd_stats'] >= FD_STATS_LIMIT:
                problem(out, 'time_or_fd_stat_limit')
                break
            out['processes'] += 1
            scan_process(out, ops, clock, start + SWEEP_SECONDS, budget, pid)
        changed(out, 'pid_set_changed', pids, names(out, ops))
    out['elapsed_seconds'] = clock() - start
    if out['elapsed_seconds'] >= SWEEP_SECONDS:
        problem(out, 'sweep_deadline')
    out['complete'] = out['problem_count'] == 0
    return out


def observe(ops, clock=time.monotonic):
    start = clock()
    out = dict(schema='sumox-uart-holders-v1', utc=datetime.datetime.now(
        datetime.timezone.utc).isoformat(), problems=[], problem_count=0,
        problem_details_truncated=False, continuous_exclusivity='UNKNOWN',
        framing_clean='UNKNOWN', receiver_ready='UNKNOWN')
    out['observer_enumeration_fd_rule'] = (
        'Only own FD-directory handles matching the enumerated directory '
        'device/inode and directory type are omitted; they cannot be UART holders.')
    out['before'] = attempt(out, 'boundary_before', ops.boundary)
    budget = dict(fd_stats=0)
    out['sweeps'] = [sweep(ops, clock, budget), sweep(ops, clock, budget)]
    out['after'] = attempt(out, 'boundary_after', ops.boundary)
    out['boundary_equal'] = out['before'] is not None and out['before'] == out['after']
    out['holders_equal'] = all(out['sweeps'][0][key] == out['sweeps'][1][key]
                               for key in ('holders', 'holder_processes'))
    complete = (out['problem_count'] == 0 and out['boundary_equal'] and
                out['holders_equal'] and all(s['complete'] for s in out['sweeps']))
    out['visibility'] = 'SAMPLED_COMPLETE' if complete else 'INCOMPLETE'
    out['fd_stat_attempts'] = budget['fd_stats']
    out['fd_stats'] = getattr(ops, 'fd_stats', budget['fd_stats'])
    out['elapsed_seconds'] = clock() - start
    return out


def bounded_report(report):
    body = json.dumps(report, separators=(',', ':'), allow_nan=False)
    if len(body.encode()) <= OUTPUT_LIMIT:
        return report, body
    summary = {key: report[key] for key in (
        'schema', 'utc', 'before', 'after', 'boundary_equal', 'holders_equal',
        'fd_stats', 'fd_stat_attempts', 'elapsed_seconds', 'continuous_exclusivity',
        'framing_clean', 'receiver_ready')}
    summary.update(visibility='INCOMPLETE', reason='OUTPUT_LIMIT',
        problem_count=report['problem_count'] + 1, details_omitted=True,
        omitted_boundary_problem_details=len(report['problems']), sweeps=[])
    for sweep_report in report['sweeps']:
        row = {key: sweep_report[key] for key in (
            'processes', 'tasks', 'fd_stats', 'elapsed_seconds', 'problem_count',
            'problem_details_truncated')}
        row.update(complete=False, observed_complete=sweep_report['complete'],
            omitted_problem_details=len(sweep_report['problems']),
            omitted_holders=len(sweep_report['holders']),
            omitted_holder_processes=len(sweep_report['holder_processes']))
        summary['sweeps'].append(row)
    body = json.dumps(summary, separators=(',', ':'), allow_nan=False)
    if len(body.encode()) > OUTPUT_LIMIT:
        raise ValueError('Even bounded metadata summary exceeds output limit')
    return summary, body


def main():
    if len(sys.argv) != 1 or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise SystemExit('Use isolated Python with -B and no arguments')
    if os.geteuid() != 0:
        raise SystemExit('Read-only holder observation requires effective UID 0')
    # Whole-process termination bounds stuck metadata I/O without reopening UART.
    signal.signal(signal.SIGALRM, signal.SIG_DFL)
    signal.alarm(45)
    report, body = bounded_report(observe(LinuxMetadata()))
    print(body, flush=True)
    signal.alarm(0)
    return 0 if report['visibility'] == 'SAMPLED_COMPLETE' else 2


if __name__ == '__main__':
    sys.exit(main())
