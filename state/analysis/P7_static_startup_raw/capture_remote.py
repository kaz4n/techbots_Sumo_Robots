# Collects the fixed, passive eighteen-read static startup observation once.
# Keeps durable ownership, bounded child execution and incomplete evidence explicit.
# Independent Linux host fixtures exercise descriptors, failures and process seams.
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import sys
import time

BINDINGS = None
SOURCE = 'fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2'
PARENT = '/home/arduino/sumox26_codex_build'
OUTPUT_NAME = 'static-startup-fcddbd8e-run01-capture'
FILE_NAMES = ('openocd', 'config', 'swj', 'loader', 'sketch')
STREAM_LIMIT = 1048576
ENVIRONMENT = {'HOME': '/home/arduino', 'USER': 'arduino', 'LOGNAME': 'arduino',
               'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected), 'Wrong object fields')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def error_record(error):
    return {'type': type(error).__name__, 'message': str(error)}


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       allow_nan=False, separators=(',', ':')) + '\n').encode('utf-8')


def valid_path(value):
    return (type(value) is str and re.fullmatch(r'/[A-Za-z0-9_./-]+', value)
            and all(part not in ('', '.', '..') for part in value.split('/')[1:]))


def check_pin(pin, has_path=True):
    keys(pin, ('path', 'bytes', 'sha256') if has_path else ('bytes', 'sha256'))
    require(type(pin['bytes']) is int and 0 < pin['bytes'] <= 67108864,
            'Invalid pinned file size')
    require(type(pin['sha256']) is str and re.fullmatch(r'[0-9a-f]{64}', pin['sha256']),
            'Invalid pinned SHA256')
    require(not has_path or valid_path(pin['path']), 'Invalid pinned path')


def checked_bindings():
    value = BINDINGS
    keys(value, ('schema', 'run_id', 'source_sha256', 'boot_id', 'uid',
                 'output', 'files', 'loader_image'))
    fixed = {'schema': 'fixed-static-capture-v1', 'run_id': 'static-fcddbd8e-run01',
             'source_sha256': SOURCE, 'output': PARENT + '/' + OUTPUT_NAME}
    for name, expected in fixed.items():
        require(type(value[name]) is str and value[name] == expected,
                'Wrong binding: ' + name)
    require(type(value['boot_id']) is str and re.fullmatch(
        r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', value['boot_id']),
        'Invalid boot identity')
    require(type(value['uid']) is int and value['uid'] == 1000, 'Wrong bound UID')
    keys(value['files'], FILE_NAMES)
    for pin in value['files'].values():
        check_pin(pin)
    check_pin(value['loader_image'], False)
    require(value['loader_image']['bytes'] == 263680 and
            value['files']['sketch']['bytes'] == 93096, 'Wrong reference extent')
    require(sys.flags.dont_write_bytecode, 'Python -B is required')
    return json.loads(json_bytes(value))


def check_analysis(value):
    keys(value, ('flash', 'observation', 'runtime', 'transaction', 'epoch_delta', 'errors'))
    keys(value['flash'], ('before_loader', 'before_sketch', 'after_loader', 'after_sketch'))
    require(all(type(item) is bool for item in value['flash'].values()),
            'Malformed decoder flash flags')
    statuses = ('FLASH_MISMATCH', 'MALFORMED_SAMPLES', 'SAMPLED_FAULT',
                'RUNNING_COUNTER_ADVANCED', 'NO_RUNNING_PROGRESS')
    require(type(value['observation']) is str and value['observation'] in statuses,
            'Malformed decoder observation')
    count = 0 if value['observation'] == 'FLASH_MISMATCH' else 2
    for name in ('runtime', 'transaction'):
        require(type(value[name]) is list and len(value[name]) == count and
                all(type(item) is dict for item in value[name]), 'Malformed decoder samples')
    delta = value['epoch_delta']
    require(delta is None or (type(delta) is int and 0 <= delta <= 0xffffffff),
            'Malformed decoder epoch delta')
    require(type(value['errors']) is list and
            all(type(item) is str for item in value['errors']), 'Malformed decoder errors')
    json_bytes(value)
    return value


def check_execution(value):
    keys(value, ('returncode', 'timed_out', 'reaped'))
    require(value['returncode'] is None or type(value['returncode']) is int,
            'Malformed executor returncode')
    require(type(value['timed_out']) is bool and type(value['reaped']) is bool,
            'Malformed executor flags')
    require(value['returncode'] == 0 and not value['timed_out'] and value['reaped'],
            'Subprocess did not complete successfully')


def limit_child_output():
    resource.setrlimit(resource.RLIMIT_FSIZE, (STREAM_LIMIT, STREAM_LIMIT))


def stop_child(child, first=None, timed_out=True):
    result = {'returncode': None, 'timed_out': timed_out, 'reaped': False}
    try:
        os.killpg(child.pid, signal.SIGKILL)
    except Exception as error:
        first = first or error
    try:
        result['returncode'] = child.wait(timeout=5)
        result['reaped'] = True
    except subprocess.TimeoutExpired:
        pass
    except Exception as error:
        first = first or error
    if first is not None:
        first.subprocess_result = result
        raise first
    return result


def wait_child(child, timeout):
    try:
        return {'returncode': child.wait(timeout=timeout), 'timed_out': False, 'reaped': True}
    except subprocess.TimeoutExpired:
        return stop_child(child)
    except Exception as error:
        return stop_child(child, error, False)


class Capture:
    def __init__(self, helper, decoder, loader_image, fs_root, executor, clock, sleeper):
        self.helper, self.decoder, self.loader_image = helper, decoder, loader_image
        self.fs_root, self.executor = fs_root, executor
        self.clock, self.sleeper = clock or time.monotonic, sleeper or time.sleep
        self.started = self.now()
        self.report = {'schema': 'static-capture-result-v1', 'run_id': None,
                       'source_sha256': SOURCE, 'status': 'FAILED',
                       'counts': {'commands': 0, 'reads': 0, 'requested_bytes': 0},
                       'started_utc': utc(), 'finished_utc': None,
                       'started_monotonic': self.started, 'finished_monotonic': None,
                       'wait': None, 'reads': [], 'first_error': None,
                       'postcheck_errors': [], 'analysis': None}
        self.root_fd, self.output_fd = None, None
        self.claimed, self.samples = False, []

    def now(self):
        value = self.clock()
        require(type(value) in (int, float) and math.isfinite(value), 'Invalid monotonic clock')
        require(value >= getattr(self, 'latest', value), 'Monotonic clock moved backward')
        self.latest = value
        return value

    def budget(self):
        remaining = 600 - (self.now() - self.started)
        require(remaining > 0, 'Collection deadline expired')
        return remaining

    def remember(self, error):
        if self.report['first_error'] is None:
            self.report['first_error'] = error_record(error)

    def check_identity(self):
        observed = self.helper.identity(self.root_fd)
        expected = {'boot_id': self.bindings['boot_id'], 'uid': self.bindings['uid'],
                    'user': 'arduino', 'home': '/home/arduino',
                    'sysname': 'Linux', 'machine': 'aarch64'}
        require(type(observed) is dict, 'Malformed board identity')
        for name, value in expected.items():
            require(type(observed.get(name)) is type(value) and observed[name] == value,
                    'Board identity differs: ' + name)

    def check_file(self, name):
        pin = self.bindings['files'][name]
        raw = self.helper.logical_read(self.root_fd, pin['path'], pin['bytes'])
        require(type(raw) is bytes and len(raw) == pin['bytes'] and
                digest(raw) == pin['sha256'], 'Pinned file differs: ' + name)
        return raw

    def check_processes(self):
        with self.helper.directory(self.root_fd, '/proc') as proc_fd:
            pids = []
            with os.scandir(proc_fd) as entries:
                for entry in entries:
                    self.budget()
                    if re.fullmatch(r'[0-9]+', entry.name):
                        require(len(pids) < 4096, 'Too many process entries')
                        pids.append(entry.name)
            for pid in pids:
                self.budget()
                try:
                    comm = self.helper.logical_read(
                        self.root_fd, '/proc/' + pid + '/comm', 256, True)
                except FileNotFoundError:
                    try:
                        os.stat(pid, dir_fd=proc_fd, follow_symlinks=False)
                    except FileNotFoundError:
                        continue
                    raise
                name = comm.decode('utf-8').removesuffix('\n')
                require(name not in ('openocd', 'remoteocd', 'arduino-cli'),
                        'Conflicting process: ' + name)
                self.budget()

    def admit(self):
        self.bindings = checked_bindings()
        self.report['run_id'] = self.bindings['run_id']
        require(isinstance(self.fs_root, Path) and self.fs_root.is_absolute(),
                'Invalid filesystem root')
        self.budget()
        self.root_fd = os.open(self.fs_root, os.O_RDONLY | os.O_DIRECTORY |
                               os.O_NOFOLLOW | os.O_CLOEXEC)
        self.check_identity()
        references = {}
        for name in FILE_NAMES:
            self.budget()
            raw = self.check_file(name)
            if name in ('loader', 'sketch'):
                references[name] = raw
            self.budget()
        self.loader = self.loader_image(references['loader'])
        pin = self.bindings['loader_image']
        require(type(self.loader) is bytes and len(self.loader) == pin['bytes'] and
                digest(self.loader) == pin['sha256'], 'Derived loader image differs')
        self.sketch = references['sketch']
        self.budget()
        self.plan = tuple(self.decoder.read_plan())
        require(len(self.plan) == 18 and sum(item[2] for item in self.plan) == 713656,
                'Decoder plan differs from fixed extent')
        self.check_processes()
        self.budget()

    def check_directory(self):
        require(self.output_fd is not None, 'Owned directory descriptor unavailable')
        with self.helper.directory(self.root_fd, PARENT) as parent_fd:
            require(self.helper.directory_id(os.fstat(parent_fd)) == self.parent_identity,
                    'Parent directory identity changed')
            with self.helper.child_directory(parent_fd, OUTPUT_NAME,
                                             self.bindings['output']) as output_fd:
                observed = self.helper.directory_id(os.fstat(output_fd))
                require(observed == self.output_identity and observed ==
                        self.helper.directory_id(os.fstat(self.output_fd)),
                        'Output directory identity changed')

    def open_exclusive(self, name):
        require(type(name) is str and re.fullmatch(r'[A-Za-z0-9_.-]+', name),
                'Invalid output basename')
        return os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                       os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=self.output_fd)

    def write_record(self, name, value, evidence=False):
        require(self.output_fd is not None and self.helper.directory_id(
            os.fstat(self.output_fd)) == self.output_identity, 'Owned descriptor changed')
        if not evidence:
            self.check_directory()
        raw = json_bytes(value)
        with os.fdopen(self.open_exclusive(name), 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.fsync(self.output_fd)
        if not evidence:
            self.check_directory()

    def claim(self):
        self.budget()
        with self.helper.directory(self.root_fd, PARENT) as parent_fd:
            self.parent_identity = self.helper.directory_id(os.fstat(parent_fd))
            os.mkdir(OUTPUT_NAME, 0o700, dir_fd=parent_fd)
            self.claimed = True
            with self.helper.child_directory(parent_fd, OUTPUT_NAME,
                                             self.bindings['output']) as output_fd:
                self.output_identity = self.helper.directory_id(os.fstat(output_fd))
                self.output_fd = os.dup(output_fd)
            os.fsync(parent_fd)
        self.budget()
        self.write_record('capture_attempt.json',
                          {'schema': 'static-capture-attempt-v1',
                           'run_id': self.bindings['run_id'], 'source_sha256': SOURCE,
                           'boot_id': self.bindings['boot_id'], 'bindings': self.bindings,
                           'plan': self.plan, 'created_utc': utc()})
        self.budget()

    def execute(self, argv, stdout_path, stderr_path, timeout):
        self.check_directory()
        with os.fdopen(self.open_exclusive(Path(stdout_path).name), 'wb') as stdout:
            with os.fdopen(self.open_exclusive(Path(stderr_path).name), 'wb') as stderr:
                child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stdout,
                                         stderr=stderr, cwd='/home/arduino',
                                         env=dict(ENVIRONMENT), start_new_session=True,
                                         preexec_fn=limit_child_output, shell=False)
                result = wait_child(child, timeout)
                stdout.flush()
                stderr.flush()
                os.fsync(stdout.fileno())
                os.fsync(stderr.fileno())
        return result

    def absent(self, name):
        try:
            os.stat(name, dir_fd=self.output_fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        raise ValueError('Read destination already exists: ' + name)

    def command(self, index, item):
        name, address, size = item
        basename = '{:02d}-{}.bin'.format(index, name)
        output = self.bindings['output'] + '/' + basename
        files = self.bindings['files']
        argv = [files['openocd']['path'], '-f', files['config']['path'], '-c',
                'dump_image {{{}}} 0x{:08x} {}'.format(output, address, size), '-c', 'shutdown']
        return basename, argv

    def read_outputs(self, index, basename, size, receipt):
        failures = []
        raw = None
        for label in ('stdout', 'stderr', 'raw'):
            filename = basename if label == 'raw' else '{:02d}.{}'.format(index, label)
            limit = size if label == 'raw' else STREAM_LIMIT - 1
            try:
                self.budget()
                blob, unused = self.helper.read_file(self.output_fd, filename, limit)
                if label == 'raw':
                    receipt['raw'] = {'bytes': len(blob), 'sha256': digest(blob)}
                    require(len(blob) == size, 'Raw read length differs')
                    raw = blob
                else:
                    receipt[label] = blob.decode('utf-8', errors='replace')
                self.budget()
            except Exception as error:
                failures.append(error)
                receipt['output_errors'].append({'file': filename, **error_record(error)})
        return raw, failures

    def launch(self, index, argv, size, receipt):
        try:
            self.check_directory()
            timeout = min(30, self.budget())
            prefix = self.fs_root / self.bindings['output'].lstrip('/') / '{:02d}'.format(index)
            execute = self.executor if self.executor is not None else self.execute
            self.report['counts']['commands'] += 1
            self.report['counts']['requested_bytes'] += size
            value = execute(argv, Path(str(prefix) + '.stdout'),
                            Path(str(prefix) + '.stderr'), timeout)
            try:
                json_bytes(value)
                receipt['subprocess'] = value
            except (ValueError, TypeError):
                receipt['subprocess'] = {'invalid_result_repr': repr(value)}
            check_execution(value)
            self.budget()
        except Exception as error:
            receipt['exception'] = error_record(error)
            if hasattr(error, 'subprocess_result'):
                receipt['subprocess'] = error.subprocess_result
            return error
        return None

    def one_read(self, index, item):
        self.budget()
        basename, argv = self.command(index, item)
        self.check_directory()
        self.absent(basename)
        self.write_record('{:02d}.command.json'.format(index),
                          {'index': index, 'name': item[0], 'address': item[1],
                           'bytes': item[2], 'argv': argv, 'planned_utc': utc()})
        self.budget()
        receipt = {'started_utc': utc(), 'started_monotonic': self.now(),
                   'finished_utc': None, 'finished_monotonic': None,
                   'subprocess': None, 'exception': None, 'stdout': None,
                   'stderr': None, 'raw': None, 'output_errors': []}
        failure = self.launch(index, argv, item[2], receipt)
        raw, failures = self.read_outputs(index, basename, item[2], receipt)
        if failure is None and failures:
            failure = failures[0]
        try:
            self.check_directory()
            self.budget()
        except Exception as error:
            failure = failure or error
        if failure is not None:
            receipt['exception'] = receipt['exception'] or error_record(failure)
            self.remember(failure)
        receipt['finished_utc'], receipt['finished_monotonic'] = utc(), self.now()
        self.write_record('{:02d}.result.json'.format(index), receipt, evidence=True)
        if failure is not None:
            raise failure
        self.samples.append((item[0], item[1], raw))
        self.report['reads'].append({'name': item[0], 'address': item[1], 'bytes': len(raw),
                                     'sha256': digest(raw), 'file': basename})
        self.report['counts']['reads'] += 1
        self.budget()

    def pause(self):
        require(self.budget() > 2, 'Insufficient budget for sample separation')
        self.report['wait'] = {'requested_seconds': 2, 'before': self.now(), 'after': None}
        self.sleeper(2)
        self.report['wait']['after'] = self.now()
        require(self.report['wait']['after'] - self.report['wait']['before'] >= 2,
                'Sample separation was shorter than two seconds')
        self.budget()

    def gather(self):
        for index, item in enumerate(self.plan):
            if index == 9:
                self.pause()
            self.one_read(index, item)
            if index == 6:
                require(b''.join(item[2] for item in self.samples[:5]) == self.loader and
                        b''.join(item[2] for item in self.samples[5:7]) == self.sketch,
                        'Initial flash images differ from references')
            self.budget()
        self.report['analysis'] = check_analysis(
            self.decoder.analyze_capture(self.samples, self.loader, self.sketch))
        self.budget()

    def postcheck(self, name, operation):
        try:
            operation()
        except Exception as error:
            self.remember(error)
            self.report['postcheck_errors'].append({'check': name, **error_record(error)})

    def finalize(self):
        for name in FILE_NAMES:
            self.postcheck(name, lambda name=name: self.check_file(name))
        self.postcheck('identity', self.check_identity)
        self.postcheck('directory', self.check_directory)
        counts = self.report['counts']
        complete = counts == {'commands': 18, 'reads': 18, 'requested_bytes': 713656}
        if complete and self.report['analysis'] is not None and self.report['first_error'] is None:
            self.report['status'] = 'COLLECTED'
        self.report['finished_utc'], self.report['finished_monotonic'] = utc(), self.now()
        self.write_record('capture_result.json', self.report, evidence=True)
        return self.report

    def close(self):
        for fd in (self.output_fd, self.root_fd):
            if fd is not None:
                os.close(fd)


def collect(helper, decoder, loader_image, *, fs_root=Path('/'), executor=None,
            clock=None, sleeper=None):
    capture = Capture(helper, decoder, loader_image, fs_root, executor, clock, sleeper)
    try:
        try:
            capture.admit()
            capture.claim()
            capture.gather()
        except Exception as error:
            if not capture.claimed:
                raise
            capture.remember(error)
        return capture.finalize()
    finally:
        capture.close()
