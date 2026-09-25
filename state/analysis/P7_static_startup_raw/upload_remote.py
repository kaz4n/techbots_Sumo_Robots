# Performs one fixed existing-packet upload after descriptor-bound admission.
# Preserves consumed ownership and partial evidence without retries or capture.
# Independent host fixtures test the public contract before any native use.
from contextlib import contextmanager, ExitStack
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time

BINDINGS = None
SOURCE = 'fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2'
PARENT = '/home/arduino/sumox26_codex_build'
OUTPUT_NAME = 'static-startup-fcddbd8e-run01-upload'
SKETCH = PARENT + '/' + SOURCE + '/app'
BUILD = (PARENT + '/_app_builds/static-app-probe-v1/' + SOURCE +
         '/bench-default/f0220228320c4b2aa20c3e5e8264c813/build')
DATA = '/home/arduino/.arduino15'
CORE = DATA + '/packages/arduino/hardware/zephyr/1.0.0'
FILE_PATHS = {
    'cli': '/usr/bin/arduino-cli',
    'remoteocd': DATA + '/packages/arduino/tools/remoteocd/0.1.1/remoteocd',
    'adb': DATA + '/packages/arduino/tools/adb/32.0.0/adb',
    'flash_config': CORE + '/variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg',
    'openocd': '/opt/openocd/bin/openocd',
    'gpio_config': '/opt/openocd/openocd_gpiod.cfg',
    'target_config': '/opt/openocd/stm32u5x.cfg',
    'common_config': '/opt/openocd/stm32x5x_common.cfg',
    'swj': '/opt/openocd/share/openocd/scripts/target/swj-dp.tcl',
    'loader': CORE + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf',
    'mem_helper': '/opt/openocd/share/openocd/scripts/mem_helper.tcl',
    'boards': CORE + '/boards.txt', 'platform': CORE + '/platform.txt',
    'installed': CORE + '/installed.json', 'index': DATA + '/package_index.json',
    'sketch': BUILD + '/app.ino.bin-zsk.bin', 'raw': BUILD + '/app.ino.bin'}
DIRECTORIES = (DATA + '/packages', DATA + '/packages/arduino/hardware/zephyr',
               DATA + '/packages/arduino/tools/remoteocd')
ABSENT = (CORE + '/boards.local.txt', CORE + '/platform.local.txt',
          DATA + '/packages/platform.txt', '/home/arduino/Arduino/hardware',
          '/home/arduino/openocd_gpiod.cfg', '/home/arduino/stm32u5x.cfg',
          '/home/arduino/stm32x5x_common.cfg', '/home/arduino/mem_helper.tcl',
          '/home/arduino/target/swj-dp.tcl', '/opt/openocd/mem_helper.tcl',
          '/opt/openocd/target/swj-dp.tcl', SKETCH + '/sketch.yaml',
          SKETCH + '/sketch.yml', SKETCH + '/sketch.json')
ENVIRONMENT = {'HOME': '/home/arduino', 'USER': 'arduino', 'LOGNAME': 'arduino',
               'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C',
               'ARDUINO_DIRECTORIES_DATA': DATA,
               'ARDUINO_DIRECTORIES_USER': '/home/arduino/Arduino',
               'ARDUINO_UPDATER_ENABLE_NOTIFICATION': 'false'}
STREAM_LIMIT = 1048576


def object_keys(support, value, expected):
    support.keys(value, expected)
    support.require(all(type(name) is str for name in value), 'Non-string object key')


def checked_bindings(support, bindings=None, run_id='static-fcddbd8e-run01'):
    support.require(type(run_id) is str and run_id in
                    ('static-fcddbd8e-run01', 'static-fcddbd8e-run02'), 'Wrong run identity')
    value = BINDINGS if bindings is None else bindings
    object_keys(support, value, ('schema', 'run_id', 'source_sha256', 'boot_id',
                                'uid', 'output', 'files', 'directories', 'absent'))
    output_name = 'static-startup-fcddbd8e-' + run_id[-5:] + '-upload'
    fixed = {'schema': 'fixed-static-upload-v1', 'run_id': run_id,
             'source_sha256': SOURCE, 'output': PARENT + '/' + output_name}
    for name, expected in fixed.items():
        support.require(type(value[name]) is str and value[name] == expected,
                        'Wrong binding: ' + name)
    support.require(type(value['boot_id']) is str and re.fullmatch(
        r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', value['boot_id']),
        'Invalid boot identity')
    support.require(type(value['uid']) is int and value['uid'] == 1000, 'Wrong bound UID')
    object_keys(support, value['files'], FILE_PATHS)
    for name, pin in value['files'].items():
        object_keys(support, pin, ('path', 'bytes', 'sha256'))
        support.check_pin(pin)
        support.require(pin['path'] == FILE_PATHS[name], 'Wrong pinned path: ' + name)
    paths = [pin['path'] for pin in value['files'].values()]
    support.require(len(set(paths)) == len(paths), 'Duplicate pinned path')
    object_keys(support, value['directories'], DIRECTORIES)
    for entries in value['directories'].values():
        support.require(type(entries) is list and 1 <= len(entries) <= 64 and all(
            type(name) is str and re.fullmatch(r'[A-Za-z0-9_.-]+', name) and
            name not in ('.', '..') for name in entries), 'Invalid directory entries')
        support.require(len(set(entries)) == len(entries), 'Duplicate directory entry')
    absent = value['absent']
    support.require(type(absent) is list and len(absent) == len(ABSENT) and
                    all(type(path) is str and support.valid_path(path) for path in absent),
                    'Invalid absence list')
    support.require(set(absent) == set(ABSENT), 'Wrong absence selections')
    support.require(sys.flags.dont_write_bytecode, 'Python -B is required')
    return json.loads(support.json_bytes(value))


class Upload:
    def __init__(self, helper, support, fs_root, executor, clock, limit_files=None,
                 bindings=None, run_id='static-fcddbd8e-run01'):
        self.helper, self.support = helper, support
        self.input_bindings, self.run_id = bindings, run_id
        self.limit_files = support.limit_child_output if limit_files is None else limit_files
        self.fs_root, self.executor = fs_root, executor
        self.clock = time.monotonic if clock is None else clock
        self.started = self.now()
        self.report = {'schema': 'static-upload-result-v1', 'run_id': None,
                       'source_sha256': SOURCE, 'status': 'FAILED', 'attempts': 0,
                       'started_utc': support.utc(), 'finished_utc': None,
                       'started_monotonic': self.started, 'finished_monotonic': None,
                       'subprocess': None, 'stdout': None, 'stderr': None,
                       'first_error': None, 'postcheck_errors': []}
        self.root_fd, self.output_fd = None, None
        self.claimed, self.first_exception = False, None
        self.context_failures = []
        self.process_error = None
        self.argv = ['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload',
                     '--fqbn', 'arduino:zephyr:unoq:link_mode=static',
                     '--input-file', BUILD + '/app.ino.bin', SKETCH]

    def now(self):
        value = self.clock()
        self.support.require(type(value) in (int, float) and math.isfinite(value),
                             'Invalid monotonic clock')
        self.support.require(value >= getattr(self, 'latest', value),
                             'Monotonic clock moved backward')
        self.latest = value
        return value

    def budget(self):
        remaining = 180 - (self.now() - self.started)
        self.support.require(remaining > 0, 'Upload deadline expired')
        return remaining

    def remember(self, error, context_check='helper_context', direct=False):
        if direct:
            self.process_error = error
        chain, current = [], error
        while current is not None and not any(current is item for item in chain):
            chain.append(current)
            if (current is self.process_error or current.__cause__ is not None or
                    current.__suppress_context__):
                break
            current = current.__context__
        if self.first_exception is None:
            self.first_exception = chain[-1]
            self.report['first_error'] = self.support.error_record(chain[-1])
        for replacement in reversed(chain[:-1]):
            if not any(replacement is item for item in self.context_failures):
                self.context_failures.append(replacement)
                self.report['postcheck_errors'].append(
                    {'check': context_check, **self.support.error_record(replacement)})

    @contextmanager
    def held(self, manager, name):
        inner = None
        try:
            with manager as fd:
                try:
                    yield fd
                except Exception as error:
                    inner = error
                    if self.claimed:
                        self.remember(error)
                    raise
        except Exception as error:
            if self.claimed and inner is not None and error is not inner:
                self.remember(error, name + '_context')
            raise

    def check_identity(self):
        observed = self.helper.identity(self.root_fd)
        expected = {'boot_id': self.bindings['boot_id'], 'uid': 1000,
                    'user': 'arduino', 'home': '/home/arduino',
                    'sysname': 'Linux', 'machine': 'aarch64'}
        self.support.require(type(observed) is dict, 'Malformed board identity')
        for name, value in expected.items():
            self.support.require(type(observed.get(name)) is type(value) and
                                 observed[name] == value, 'Board identity differs: ' + name)

    def check_file(self, name):
        pin = self.bindings['files'][name]
        raw = self.helper.logical_read(self.root_fd, pin['path'], pin['bytes'])
        self.support.require(type(raw) is bytes and len(raw) == pin['bytes'] and
                             self.support.digest(raw) == pin['sha256'],
                             'Pinned file differs: ' + name)

    def check_entries(self, path):
        with self.held(self.helper.directory(self.root_fd, path), 'entries') as fd:
            observed = []
            with os.scandir(fd) as entries:
                for entry in entries:
                    self.support.require(len(observed) < 64, 'Too many directory entries')
                    observed.append(entry.name)
            expected = self.bindings['directories'][path]
            self.support.require(set(observed) == set(expected), 'Directory entries differ: ' + path)
            for name in expected:
                manager = self.helper.child_directory(fd, name, path + '/' + name)
                with self.held(manager, 'entry'):
                    pass

    def check_absent(self, path):
        parts = path.split('/')[1:]
        with ExitStack() as stack:
            fd, logical = self.root_fd, ''
            for part in parts[:-1]:
                logical += '/' + part
                try:
                    os.stat(part, dir_fd=fd, follow_symlinks=False)
                except FileNotFoundError:
                    return
                manager = self.helper.child_directory(fd, part, logical)
                fd = stack.enter_context(self.held(manager, 'absence_ancestor'))
            try:
                os.stat(parts[-1], dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                return
            raise ValueError('Required absent entry exists: ' + path)

    def check_null(self):
        with self.held(self.helper.directory(self.root_fd, '/dev'), 'null') as fd:
            info = os.stat('null', dir_fd=fd, follow_symlinks=False)
            self.support.require(stat.S_ISCHR(info.st_mode) and
                                 os.major(info.st_rdev) == 1 and os.minor(info.st_rdev) == 3,
                                 '/dev/null is not nonsymlink character device 1/3')

    def check_processes(self):
        with self.held(self.helper.directory(self.root_fd, '/proc'), 'processes') as fd:
            pids = []
            with os.scandir(fd) as entries:
                for entry in entries:
                    if re.fullmatch(r'[0-9]+', entry.name):
                        self.support.require(len(pids) < 4096, 'Too many process entries')
                        pids.append(entry.name)
            for pid in pids:
                try:
                    raw = self.helper.logical_read(self.root_fd, '/proc/' + pid + '/comm',
                                                   256, True)
                except FileNotFoundError:
                    try:
                        os.stat(pid, dir_fd=fd, follow_symlinks=False)
                    except FileNotFoundError:
                        continue
                    raise
                name = raw.decode('utf-8').removesuffix('\n')
                self.support.require(name not in ('openocd', 'remoteocd', 'arduino-cli'),
                                     'Conflicting process: ' + name)

    def admit(self):
        self.bindings = checked_bindings(self.support, self.input_bindings, self.run_id)
        self.output_name = self.bindings['output'].rsplit('/', 1)[1]
        self.report['run_id'] = self.bindings['run_id']
        self.support.require(isinstance(self.fs_root, Path) and self.fs_root.is_absolute(),
                             'Invalid filesystem root')
        self.budget()
        self.root_fd = os.open(self.fs_root, os.O_RDONLY | os.O_DIRECTORY |
                               os.O_NOFOLLOW | os.O_CLOEXEC)
        self.check_identity()
        for name in FILE_PATHS:
            self.budget()
            self.check_file(name)
        for path in DIRECTORIES:
            self.budget()
            self.check_entries(path)
        for path in ABSENT + ('/tmp/remoteocd',):
            self.budget()
            self.check_absent(path)
        self.check_null()
        self.check_processes()
        self.budget()

    def check_directory(self):
        self.support.require(self.output_fd is not None, 'Owned directory descriptor unavailable')
        with self.held(self.helper.directory(self.root_fd, PARENT), 'owned_parent') as parent_fd:
            self.support.require(self.helper.directory_id(os.fstat(parent_fd)) ==
                                 self.parent_identity, 'Parent directory identity changed')
            manager = self.helper.child_directory(parent_fd, self.output_name, self.bindings['output'])
            with self.held(manager, 'owned_output') as output_fd:
                observed = self.helper.directory_id(os.fstat(output_fd))
                self.support.require(observed == self.output_identity and observed ==
                                     self.helper.directory_id(os.fstat(self.output_fd)),
                                     'Output directory identity changed')

    def open_exclusive(self, name):
        self.support.require(type(name) is str and re.fullmatch(r'[A-Za-z0-9_.-]+', name),
                             'Invalid output basename')
        return os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                       os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=self.output_fd)

    def write_record(self, name, value, evidence=False):
        self.support.require(self.output_fd is not None and self.helper.directory_id(
            os.fstat(self.output_fd)) == self.output_identity, 'Owned descriptor changed')
        if not evidence:
            self.check_directory()
        raw = self.support.json_bytes(value)
        with os.fdopen(self.open_exclusive(name), 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.fsync(self.output_fd)
        if not evidence:
            self.check_directory()

    def claim(self):
        self.budget()
        with self.held(self.helper.directory(self.root_fd, PARENT), 'claim_parent') as parent_fd:
            self.parent_identity = self.helper.directory_id(os.fstat(parent_fd))
            os.mkdir(self.output_name, 0o700, dir_fd=parent_fd)
            self.claimed = True
            manager = self.helper.child_directory(parent_fd, self.output_name, self.bindings['output'])
            with self.held(manager, 'claim_output') as fd:
                self.output_identity = self.helper.directory_id(os.fstat(fd))
                self.output_fd = os.dup(fd)
            os.fsync(parent_fd)
        self.budget()
        self.write_record('upload_attempt.json', {
            'schema': 'static-upload-attempt-v1', 'run_id': self.bindings['run_id'],
            'source_sha256': SOURCE, 'boot_id': self.bindings['boot_id'],
            'bindings': self.bindings, 'argv': self.argv, 'environment': dict(ENVIRONMENT),
            'started_utc': self.report['started_utc'], 'started_monotonic': self.started,
            'created_utc': self.support.utc(), 'created_monotonic': self.now()})
        self.budget()

    def retain_outcome(self, value):
        object_keys(self.support, value, ('returncode', 'timed_out', 'reaped'))
        self.support.require(value['returncode'] is None or type(value['returncode']) is int,
                             'Malformed executor returncode')
        self.support.require(type(value['timed_out']) is bool and type(value['reaped']) is bool,
                             'Malformed executor flags')
        self.report['subprocess'] = value

    def process_failure(self, error):
        # The helper's outward error already accounts for handled timeout/kill errors.
        self.remember(error, direct=True)
        if hasattr(error, 'subprocess_result'):
            self.postcheck('subprocess_outcome', lambda: self.retain_outcome(error.subprocess_result))

    def execute(self, argv, stdout_path, stderr_path, timeout):
        self.check_directory()
        with os.fdopen(self.open_exclusive(stdout_path.name), 'wb') as stdout:
            with os.fdopen(self.open_exclusive(stderr_path.name), 'wb') as stderr:
                self.check_directory()
                timeout = min(120, timeout, self.budget())
                try:
                    child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=stdout,
                                             stderr=stderr, cwd='/home/arduino', shell=False,
                                             env=dict(ENVIRONMENT), start_new_session=True,
                                             preexec_fn=self.limit_files)
                    value = self.support.wait_child(child, timeout)
                except Exception as error:
                    self.process_failure(error)
                    raise
                self.retain_outcome(value)
                for stream in (stdout, stderr):
                    stream.flush()
                    os.fsync(stream.fileno())
        return value

    def read_stream(self, label):
        raw, unused = self.helper.read_file(self.output_fd, 'upload.' + label, STREAM_LIMIT - 1)
        self.support.require(type(raw) is bytes and len(raw) < STREAM_LIMIT,
                             'Invalid upload stream: ' + label)
        self.report[label] = raw.decode('utf-8', errors='replace')

    def run(self):
        self.budget()
        self.write_record('upload_command.json', {
            'schema': 'static-upload-command-v1', 'argv': self.argv,
            'environment': dict(ENVIRONMENT), 'cwd': '/home/arduino',
            'run_id': self.bindings['run_id'], 'source_sha256': SOURCE,
            'boot_id': self.bindings['boot_id'], 'planned_utc': self.support.utc(),
            'planned_monotonic': self.now()})
        try:
            self.check_directory()
            timeout = min(120, self.budget())
            output = self.fs_root / self.bindings['output'].lstrip('/')
            execute = self.executor if self.executor is not None else self.execute
            self.report['attempts'] += 1
            value = execute(self.argv, output / 'upload.stdout', output / 'upload.stderr', timeout)
            self.retain_outcome(value)
            self.support.check_execution(value)
            self.budget()
        except Exception as error:
            if self.executor is not None and self.report['attempts'] == 1:
                self.process_failure(error)
            else:
                self.remember(error)
        for label in ('stdout', 'stderr'):
            self.postcheck(label, lambda label=label: self.read_stream(label))

    def postcheck(self, name, operation):
        try:
            operation()
        except Exception as error:
            self.remember(error)
            self.report['postcheck_errors'].append({'check': name, **self.support.error_record(error)})

    def finish_timestamp(self):
        self.report['finished_utc'] = self.support.utc()
        try:
            self.report['finished_monotonic'] = self.now()
        except Exception as error:
            self.report['finished_monotonic'] = self.latest
            self.remember(error)
            self.report['postcheck_errors'].append(
                {'check': 'finished_clock', **self.support.error_record(error)})

    def finalize(self):
        for name in FILE_PATHS:
            self.postcheck(name, lambda name=name: self.check_file(name))
        for path in DIRECTORIES:
            self.postcheck(path, lambda path=path: self.check_entries(path))
        for path in ABSENT:
            self.postcheck(path, lambda path=path: self.check_absent(path))
        self.postcheck('identity', self.check_identity)
        self.postcheck('null', self.check_null)
        self.postcheck('processes', self.check_processes)
        self.postcheck('directory', self.check_directory)
        self.finish_timestamp()
        success = {'returncode': 0, 'timed_out': False, 'reaped': True}
        if (self.report['first_error'] is None and not self.report['postcheck_errors'] and
                self.report['attempts'] == 1 and self.report['subprocess'] == success and
                self.report['stdout'] is not None and self.report['stderr'] is not None):
            self.report['status'] = 'UPLOADED'
        if self.output_fd is None:
            raise self.first_exception
        self.write_record('upload_result.json', self.report, evidence=True)
        return self.report

    def close(self):
        for fd in (self.output_fd, self.root_fd):
            if fd is not None:
                os.close(fd)


def limit_upload_files():
    # This permits the pinned loader copy and transient diagnostic files of this size.
    import resource
    resource.setrlimit(resource.RLIMIT_FSIZE, (2303728, 2303728))


def upload(helper, support, *, fs_root=Path('/'), executor=None, clock=None, bindings=None):
    return _upload(Upload(helper, support, fs_root, executor, clock, bindings=bindings))


def upload_loader(helper, support, *, fs_root=Path('/'), executor=None, clock=None,
                  bindings=None, run_id='static-fcddbd8e-run01'):
    return _upload(Upload(helper, support, fs_root, executor, clock, limit_upload_files,
                          bindings, run_id))


def _upload(attempt):
    try:
        try:
            attempt.admit()
            attempt.claim()
            attempt.run()
        except Exception as error:
            if not attempt.claimed:
                raise
            attempt.remember(error)
        return attempt.finalize()
    finally:
        attempt.close()
