# Collects fixed, passive static and diagnostic startup observations once.
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


def checked_bindings(bindings=None, run_id='static-fcddbd8e-run01'):
    require(type(run_id) is str and run_id in
            ('static-fcddbd8e-run01', 'static-fcddbd8e-run02'), 'Wrong run identity')
    value = BINDINGS if bindings is None else bindings
    keys(value, ('schema', 'run_id', 'source_sha256', 'boot_id', 'uid',
                 'output', 'files', 'loader_image'))
    output_name = 'static-startup-fcddbd8e-' + run_id[-5:] + '-capture'
    fixed = {'schema': 'fixed-static-capture-v1', 'run_id': run_id,
             'source_sha256': SOURCE, 'output': PARENT + '/' + output_name}
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
    source = SOURCE
    result_schema = 'static-capture-result-v1'
    attempt_schema = 'static-capture-attempt-v1'

    def __init__(self, helper, decoder, loader_image, fs_root, executor, clock, sleeper,
                 bindings=None, run_id='static-fcddbd8e-run01'):
        self.helper, self.decoder, self.loader_image = helper, decoder, loader_image
        self.input_bindings, self.run_id = bindings, run_id
        self.fs_root, self.executor = fs_root, executor
        self.clock, self.sleeper = clock or time.monotonic, sleeper or time.sleep
        self.started = self.now()
        self.report = {'schema': self.result_schema, 'run_id': None,
                       'source_sha256': self.source, 'status': 'FAILED',
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
            self.first_exception = error

    def context_error(self, name, error):
        self.remember(error)
        if error is not self.first_exception:
            self.report['postcheck_errors'].append({'check': name, **error_record(error)})

    def timestamp(self, target, prefix):
        target[prefix + '_utc'] = utc()
        try:
            target[prefix + '_monotonic'] = self.now()
        except Exception as error:
            target[prefix + '_monotonic'] = getattr(self, 'latest', None)
            self.remember(error)
            record = {'check': prefix + '_clock', **error_record(error)}
            self.report['postcheck_errors'].append(record)
            if target is not self.report:
                target['clock_errors'].append(record)
            return error
        return None

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

    def profile_bindings(self):
        return checked_bindings(self.input_bindings, self.run_id)

    def prepare_plan(self):
        self.plan = tuple(self.decoder.read_plan())
        require(len(self.plan) == 18 and sum(item[2] for item in self.plan) == 713656,
                'Decoder plan differs from fixed extent')

    def admit(self):
        self.bindings = self.profile_bindings()
        self.output_name = self.bindings['output'].rsplit('/', 1)[1]
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
        self.prepare_plan()
        self.check_processes()
        self.budget()

    def check_directory(self):
        require(self.output_fd is not None, 'Owned directory descriptor unavailable')
        with self.helper.directory(self.root_fd, PARENT) as parent_fd:
            require(self.helper.directory_id(os.fstat(parent_fd)) == self.parent_identity,
                    'Parent directory identity changed')
            with self.helper.child_directory(parent_fd, self.output_name,
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

    def create_directory(self, parent_fd):
        self.parent_identity = self.helper.directory_id(os.fstat(parent_fd))
        os.mkdir(self.output_name, 0o700, dir_fd=parent_fd)
        self.claimed = True
        try:
            with self.helper.child_directory(parent_fd, self.output_name,
                                             self.bindings['output']) as output_fd:
                try:
                    self.output_identity = self.helper.directory_id(os.fstat(output_fd))
                    self.output_fd = os.dup(output_fd)
                except Exception as error:
                    self.remember(error)
                    raise
        except Exception as error:
            self.context_error('claim_output_context', error)
            raise
        os.fsync(parent_fd)

    def claim(self):
        self.budget()
        try:
            with self.helper.directory(self.root_fd, PARENT) as parent_fd:
                try:
                    self.create_directory(parent_fd)
                except Exception as error:
                    self.remember(error)
                    raise
        except Exception as error:
            if self.claimed:
                self.context_error('claim_parent_context', error)
            raise
        self.budget()
        self.write_record('capture_attempt.json',
                          {'schema': self.attempt_schema,
                           'run_id': self.bindings['run_id'], 'source_sha256': self.source,
                           'boot_id': self.bindings['boot_id'], 'bindings': self.bindings,
                           'plan': self.plan, 'created_utc': utc()})
        self.budget()

    def execute(self, argv, stdout_path, stderr_path, timeout):
        streams, result, first = [], None, None
        try:
            self.check_directory()
            for path in (stdout_path, stderr_path):
                name = Path(path).name
                streams.append((name, self.open_stream(name)))
            self.check_directory()
            timeout = min(timeout, self.budget())
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=streams[0][1],
                                     stderr=streams[1][1], cwd='/home/arduino',
                                     env=dict(ENVIRONMENT), start_new_session=True,
                                     preexec_fn=limit_child_output, shell=False)
            result = wait_child(child, timeout)
            # A failed child precedes every subsequent stream cleanup failure.
            check_execution(result)
        except Exception as error:
            first = error
            result = getattr(error, 'subprocess_result', result)
        finally:
            failures = self.cleanup_streams(streams)
        if failures:
            first = first or failures[0][1]
            first.stream_cleanup_errors = getattr(first, 'stream_cleanup_errors', []) + [
                {'file': name, **error_record(error)} for name, error in failures]
        if first is not None:
            if result is not None:
                first.subprocess_result = result
            raise first
        return result

    def open_stream(self, name):
        descriptor = self.open_exclusive(name)
        try:
            return os.fdopen(descriptor, 'wb')
        except Exception as error:
            try:
                os.close(descriptor)
            except Exception as cleanup_error:
                error.stream_cleanup_errors = [{'file': name, **error_record(cleanup_error)}]
            raise

    def cleanup_streams(self, streams):
        failures = []
        for name, stream in streams:
            for operation in (stream.flush, lambda: os.fsync(stream.fileno()), stream.close):
                try:
                    operation()
                except Exception as error:
                    failures.append((name, error))
        return failures

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
                blob, unused = self.helper.read_file(self.output_fd, filename, limit)
                if label == 'raw':
                    receipt['raw'] = {'bytes': len(blob), 'sha256': digest(blob)}
                    require(len(blob) == size, 'Raw read length differs')
                    raw = blob
                else:
                    receipt[label] = blob.decode('utf-8', errors='replace')
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
            receipt['output_errors'].extend(getattr(error, 'stream_cleanup_errors', []))
            return error
        return None

    def one_read(self, index, item):
        self.budget()
        basename, argv = self.command(index, item)
        self.check_directory()
        self.absent(basename)
        receipt = {'started_utc': utc(), 'started_monotonic': self.latest,
                   'finished_utc': None, 'finished_monotonic': None,
                   'subprocess': None, 'exception': None, 'stdout': None,
                   'stderr': None, 'raw': None, 'output_errors': [], 'clock_errors': []}
        failure = None
        try:
            self.write_record('{:02d}.command.json'.format(index),
                              {'index': index, 'name': item[0], 'address': item[1],
                               'bytes': item[2], 'argv': argv, 'planned_utc': utc()})
            failure = self.timestamp(receipt, 'started')
            if failure is None:
                self.budget()
                failure = self.launch(index, argv, item[2], receipt)
        except Exception as error:
            failure = error
        if failure is not None:
            self.remember(failure)
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
        clock_error = self.timestamp(receipt, 'finished')
        failure = failure or clock_error
        if failure is not None:
            receipt['exception'] = receipt['exception'] or error_record(failure)
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
        self.timestamp(self.report, 'finished')
        self.postcheck('deadline', self.budget)
        if self.complete() and self.report['analysis'] is not None and self.report['first_error'] is None:
            self.report['status'] = 'COLLECTED'
        self.write_record('capture_result.json', self.report, evidence=True)
        return self.report

    def complete(self):
        return self.report['counts'] == {'commands': 18, 'reads': 18,
                                         'requested_bytes': 713656}

    def close(self):
        for fd in (self.output_fd, self.root_fd):
            if fd is not None:
                os.close(fd)


def collect(helper, decoder, loader_image, *, fs_root=Path('/'), executor=None,
            clock=None, sleeper=None, bindings=None, run_id='static-fcddbd8e-run01'):
    capture = Capture(helper, decoder, loader_image, fs_root, executor, clock, sleeper,
                      bindings, run_id)
    return _collect(capture)


def _collect(capture):
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


def _motor_fault_bindings(bindings, run_id):
    require(type(run_id) is str and run_id == 'motor-fault-8f592937-run01',
            'Wrong diagnostic run identity')
    value = BINDINGS if bindings is None else bindings
    keys(value, ('schema', 'run_id', 'source_sha256', 'boot_id', 'uid',
                 'output', 'files', 'loader_image'))
    source = '8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36'
    fixed = {'schema': 'fixed-motor-fault-capture-v1', 'run_id': run_id,
             'source_sha256': source, 'output': PARENT + '/' + run_id + '-capture'}
    for name, expected in fixed.items():
        require(type(value[name]) is str and value[name] == expected,
                'Wrong binding: ' + name)
    require(type(value['boot_id']) is str and re.fullmatch(
        r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', value['boot_id']),
        'Invalid boot identity')
    require(type(value['uid']) is int and value['uid'] == 1000, 'Wrong bound UID')
    keys(value['files'], FILE_NAMES)
    paths = {
        'openocd': '/opt/openocd/bin/openocd',
        'config': '/home/arduino/sumox26-capture-tools/app-default-'
                  'beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1'
                  '/p0_mem_read.cfg',
        'swj': '/opt/openocd/share/openocd/scripts/target/swj-dp.tcl',
        'loader': '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/'
                  'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf',
        'sketch': PARENT + '/motor-fault-active01/_app_builds/native-app-v1/' + source +
                  '/bench-default/3aafdd0129f64799b4db51efe78e5c44/build/'
                  'motor_fault.ino.elf-zsk.bin'}
    for name, pin in value['files'].items():
        check_pin(pin)
        require(pin['path'] == paths[name], 'Wrong diagnostic file path: ' + name)
    check_pin(value['loader_image'], False)
    require(value['loader_image']['bytes'] == 263680 and
            value['files']['sketch']['bytes'] == 29836, 'Wrong reference extent')
    require(sys.flags.dont_write_bytecode, 'Python -B is required')
    return json.loads(json_bytes(value))


def _motor_fault_ram(address, size):
    require(type(address) is int and type(size) is int and address % 4 == 0 and
            0 < size <= 2632 and 0x20000000 <= address < 0x200c0000 and
            address + size <= 0x200c0000, 'Invalid diagnostic SRAM region')


class _RelocationAdapter:
    def __init__(self, capture, prefix):
        self.capture, self.prefix = capture, prefix
        flags = capture.report['analysis']['flash']
        self.report = {'flash_identity_verified':
                       flags['before_loader'] is True and flags['before_sketch'] is True}
        self.records, self.nodes = [], []
        self.next_address, self.confirmed = None, False

    def read(self, name, address, size):
        try:
            return self._read(name, address, size)
        except Exception as error:
            self.capture.remember(error)
            raise

    def _read(self, name, address, size):
        require(type(name) is str and type(address) is int and type(size) is int,
                'Invalid relocation read types')
        require(not self.confirmed, 'Relocation traversal already ended')
        if not self.records:
            expected = ('llext-list', 0x200017bc, 8)
        elif self.next_address:
            require(len(self.nodes) < 3, 'Too many extension nodes')
            expected = ('node-' + str(len(self.nodes) + 1), self.next_address, 196)
            _motor_fault_ram(address, size)
        else:
            require(self.nodes, 'Empty relocation traversal')
            expected = ('llext-list-confirm', 0x200017bc, 8)
        require((name, address, size) == expected, 'Unexpected relocation read')
        if self.prefix == 'after':
            before = self.capture.before_relocation
            require(len(self.records) < len(before) and
                    before[len(self.records)][:2] == (name, address),
                    'Relocation bracket read sequence changed')
        raw = self.capture.read_region(self.prefix + '.' + name, address, size)
        self.records.append((name, address, raw))
        if self.prefix == 'after':
            require(self.records[-1] == before[len(self.records) - 1],
                    'Relocation bracket raw bytes changed')
        if name == 'llext-list-confirm':
            self.confirmed = True
        else:
            self.next_address = int.from_bytes(raw[:4], 'little')
            if name.startswith('node-'):
                self.nodes.append(address)
        return raw

    def finish(self, base):
        require(self.confirmed, 'Incomplete relocation traversal')
        extension = self.report.get('extension')
        keys(extension, ('node_address', 'bss_address', 'bss_size', 'visited_nodes'))
        require(all(type(extension[key]) is int for key in
                    ('node_address', 'bss_address', 'bss_size')) and
                type(extension['visited_nodes']) is list and
                all(type(node) is int for node in extension['visited_nodes']),
                'Invalid relocation metadata types')
        require(type(base) is int and base == extension['bss_address'] and base % 8 == 0
                and extension['bss_size'] == 2632 and
                extension['visited_nodes'] == self.nodes and
                extension['node_address'] in self.nodes, 'Invalid selected BSS metadata')
        _motor_fault_ram(base, 2632)
        selected = next(raw for name, address, raw in self.records
                        if name.startswith('node-') and address == extension['node_address'])
        require(selected[4:20].split(b'\0', 1)[0] == b'sketch' and
                int.from_bytes(selected[32:36], 'little') == base and
                int.from_bytes(selected[92:96], 'little') == 2632,
                'Selected BSS differs from raw node')
        return json.loads(json_bytes(extension))


class _MotorFaultCapture(Capture):
    source = '8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36'
    result_schema = 'motor-fault-capture-result-v1'
    attempt_schema = 'motor-fault-capture-attempt-v1'

    def profile_bindings(self):
        return _motor_fault_bindings(self.input_bindings, self.run_id)

    def prepare_plan(self):
        self.plan = {'profile': 'motor-fault-v1', 'max_reads': 24,
                     'max_requested_bytes': 593424, 'loader_bytes': 263680,
                     'sketch_bytes': 29836, 'bss_bytes': 2632,
                     'snapshot_bytes': 2592, 'extension_nodes': 3, 'sample_gap_seconds': 2}
        self.report['analysis'] = {
            'schema': 'motor-fault-capture-analysis-v1',
            'flash': {'before_loader': False, 'before_sketch': False,
                      'after_loader': False, 'after_sketch': False},
            'relocation': {'before': None, 'after': None},
            'snapshots': [], 'coherence': 'UNPROVEN'}
        self.bss, self.gathered, self.before_relocation = None, False, None

    def check_limits(self, size):
        require(self.report['first_error'] is None, 'Earlier capture read failed')
        counts = self.report['counts']
        require(counts['commands'] < 24 and counts['reads'] < 24 and
                counts['requested_bytes'] + size <= 593424,
                'Diagnostic capture read or byte ceiling exceeded')

    def launch(self, index, argv, size, receipt):
        self.check_limits(size)
        return super().launch(index, argv, size, receipt)

    def check_region(self, name, address, size):
        require(type(name) is str and type(address) is int and type(size) is int,
                'Invalid diagnostic read types')
        flash = re.fullmatch(r'(before|after)\.(loader|sketch)\.([0-4])', name)
        if flash:
            region, index = flash[2], int(flash[3])
            extent, base = (263680, 0x08000000) if region == 'loader' else (29836, 0x08100000)
            offset = index * 65536
            require(offset < extent and address == base + offset and
                    size == min(65536, extent - offset), 'Wrong named flash region')
            return
        flags = self.report['analysis']['flash']
        require(flags['before_loader'] and flags['before_sketch'],
                'Complete flash identity required before SRAM')
        _motor_fault_ram(address, size)
        if name in ('first.diagnostic', 'second.diagnostic'):
            require(self.bss is not None and address == self.bss and size == 2592,
                    'Wrong diagnostic snapshot region')
        elif re.fullmatch(r'(before|after)\.llext-list(?:-confirm)?', name):
            require(address == 0x200017bc and size == 8, 'Wrong extension list region')
        else:
            require(re.fullmatch(r'(before|after)\.node-[1-3]', name) and size == 196,
                    'Wrong extension node region')

    def read_region(self, name, address, size):
        self.check_region(name, address, size)
        self.check_limits(size)
        try:
            self.one_read(len(self.samples), (name, address, size))
        finally:
            # A later clock failure cannot hide a raw snapshot already retained.
            self.report['analysis']['snapshots'] = [dict(item) for item in self.report['reads']
                if item['name'] in ('first.diagnostic', 'second.diagnostic')]
        return self.samples[-1][2]

    def flash_image(self, prefix, region):
        reference, base = (self.loader, 0x08000000) if region == 'loader' else (self.sketch, 0x08100000)
        blocks = [self.read_region(prefix + '.' + region + '.' + str(index),
                                   base + offset, min(65536, len(reference) - offset))
                  for index, offset in enumerate(range(0, len(reference), 65536))]
        matches = b''.join(blocks) == reference
        self.report['analysis']['flash'][prefix + '_' + region] = matches
        require(matches, 'Captured flash image differs: ' + prefix + '.' + region)

    def relocate(self, prefix):
        adapter = _RelocationAdapter(self, prefix)
        base = self.decoder.find_bss(adapter, 2632)
        extension = adapter.finish(base)
        self.report['analysis']['relocation'][prefix] = extension
        return base, adapter.records

    def gather(self):
        self.flash_image('before', 'loader')
        self.flash_image('before', 'sketch')
        self.bss, before = self.relocate('before')
        self.before_relocation = before
        self.read_region('first.diagnostic', self.bss, 2592)
        self.pause()
        self.read_region('second.diagnostic', self.bss, 2592)
        after_base, after = self.relocate('after')
        relocation = self.report['analysis']['relocation']
        require(after_base == self.bss and before == after and
                relocation['before'] == relocation['after'], 'Relocation bracket changed')
        self.flash_image('after', 'sketch')
        self.flash_image('after', 'loader')
        self.gathered = True
        self.budget()

    def complete(self):
        if not self.gathered:
            return False
        analysis = self.report['analysis']
        nodes = len(analysis['relocation']['before']['visited_nodes'])
        return (1 <= nodes <= 3 and all(analysis['flash'].values()) and
                len(analysis['snapshots']) == 2 and self.report['counts'] ==
                {'commands': 18 + 2 * nodes, 'reads': 18 + 2 * nodes,
                 'requested_bytes': 592248 + 392 * nodes})


def collect_motor_fault(helper, relocation, loader_image, *, fs_root=Path('/'),
                        executor=None, clock=None, sleeper=None, bindings=None,
                        run_id='motor-fault-8f592937-run01'):
    capture = _MotorFaultCapture(helper, relocation, loader_image, fs_root, executor,
                                 clock, sleeper, bindings, run_id)
    return _collect(capture)
