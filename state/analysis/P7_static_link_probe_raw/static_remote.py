# Performs the eight fixed Linux observations and exclusive static-probe claim.
# Preserves source and artifact identity without compilation or target execution.
# Independent descriptor, framing and failure tests are required before use.
import base64
from contextlib import contextmanager, ExitStack
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import pwd
import re
import stat
import sys
import traceback
import zlib

SOURCE = 'fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2'
MANIFEST_SHA256 = '56ab12b990ebe664941677e29dfef783197bc98c3a9de1985b54d57bb30da56a'
VALIDATOR_SHA256 = 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368'
HOME = '/home/arduino'
ROOT = HOME + '/sumox26_codex_build'
SKETCH = ROOT + '/' + SOURCE + '/app'
PARENT = ROOT + '/_app_builds/static-app-probe-v1/' + SOURCE + '/bench-default'
BOOT_ID = '/proc/sys/kernel/random/boot_id'
CHUNK = 262144
SOURCE_LIMIT = 1048576
LIMITS = {'build/app.ino.elf': 16777216,
          'build/app.ino_debug.elf': 16777216,
          'build/app.ino_temp.elf': 16777216,
          'build/app.ino.bin': 786416,
          'build/app.ino.bin-zsk.bin': 786432,
          'build/app.ino.elf-zsk.bin': 16777216,
          'build/app.ino.map': 16777216,
          'artifacts/app.ino.bin-zsk.bin': 786432}
ARG_COUNTS = {'inventory': 2, 'source': 3, 'claim': 2, 'absent': 3,
              'artifacts': 3, 'layout': 4, 'read': 7, 'postcheck': 4}
COMPILER = re.compile(r'(?:.*-)?(?:gcc|g\+\+|cc|c\+\+|cc1|cc1plus|collect2|as|'
                      r'ld|ld\.bfd|ld\.gold|lto1|clang|clang\+\+|rustc)')
HEX = re.compile(r'[0-9a-f]{64}')
UUID = re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}')


class Rejected(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def require(condition, code, message):
    if not condition:
        raise Rejected(code, message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'BAD_REQUEST', 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def invalid_constant(value):
    raise Rejected('BAD_REQUEST', 'Nonfinite JSON constant: ' + value)


def decode_json(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def decode_base64(text):
    raw = base64.b64decode(text, validate=True)
    require(base64.b64encode(raw).decode('ascii') == text,
            'BAD_REQUEST', 'Noncanonical base64')
    return raw


def decode_compressed(text, limit, expected):
    decoder = zlib.decompressobj(zlib.MAX_WBITS)
    raw = decoder.decompress(decode_base64(text), limit + 1)
    require(len(raw) <= limit, 'BAD_REQUEST', 'Decompressed input exceeds limit')
    require(decoder.eof and not decoder.unused_data and not decoder.unconsumed_tail,
            'BAD_REQUEST', 'Incomplete or trailing zlib stream')
    require(sha256(raw) == expected, 'BAD_REQUEST', 'Literal input SHA256 mismatch')
    return raw


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected),
            'BAD_REQUEST', 'Wrong object fields')


def unsigned(value):
    return type(value) is int and value >= 0


def claim_argument(text, run_id):
    raw = decode_base64(text)
    claim = decode_json(raw)
    require(canonical(claim).encode('utf-8') == raw,
            'BAD_REQUEST', 'Noncanonical claim JSON')
    keys(claim, ('run_id', 'boot_id', 'directories'))
    require(claim['run_id'] == run_id and type(claim['boot_id']) is str and
            UUID.fullmatch(claim['boot_id']), 'BAD_REQUEST', 'Invalid claim identity')
    keys(claim['directories'], ('run', 'build', 'artifacts'))
    for identity in claim['directories'].values():
        keys(identity, ('device', 'inode'))
        require(all(unsigned(v) for v in identity.values()),
                'BAD_REQUEST', 'Invalid directory identity')
    return claim


def manifest_argument(text):
    manifest = decode_json(decode_compressed(text, 65536, MANIFEST_SHA256))
    keys(manifest, ('source_sha256', 'files'))
    require(manifest['source_sha256'] == SOURCE and type(manifest['files']) is dict
            and len(manifest['files']) == 102, 'BAD_REQUEST', 'Wrong source manifest')
    for name, digest in manifest['files'].items():
        require(type(name) is str and name and not name.startswith('/') and
                PurePosixPath(name).as_posix() == name and
                all(p not in ('', '.', '..') for p in name.split('/')) and
                '\\' not in name and '\0' not in name and type(digest) is str and
                HEX.fullmatch(digest), 'BAD_REQUEST', 'Invalid manifest file')
    return manifest['files']


def parse_request(argv):
    require(type(argv) is list and all(type(v) is str for v in argv),
            'BAD_REQUEST', 'Arguments must be a list of strings')
    require(len(argv) >= 2 and argv[0] in ARG_COUNTS and
            len(argv) == ARG_COUNTS[argv[0]] and re.fullmatch(r'[0-9a-f]{32}', argv[1]),
            'BAD_REQUEST', 'Invalid action, run ID or argument count')
    action, run_id = argv[:2]
    result = {'action': action, 'run_id': run_id}
    if action in ('absent', 'artifacts', 'layout', 'read', 'postcheck'):
        result['claim'] = claim_argument(argv[2], run_id)
    if action in ('source', 'postcheck'):
        result['manifest'] = manifest_argument(argv[-1])
    if action == 'layout':
        result['validator'] = decode_compressed(argv[3], 32768, VALIDATOR_SHA256).decode('utf-8')
    if action == 'read':
        require(argv[3] == 'app.ino.elf' and HEX.fullmatch(argv[6]),
                'BAD_REQUEST', 'Read accepts only final ELF and a SHA256')
        require(all(re.fullmatch(r'0|[1-9][0-9]*', v) for v in argv[4:6]),
                'BAD_REQUEST', 'Noncanonical read offset or length')
        offset, length = map(int, argv[4:6])
        require(offset < 16777216 and offset % CHUNK == 0 and 0 < length <= CHUNK,
                'BAD_REQUEST', 'Read range exceeds fixed bounds')
        result.update(offset=offset, length=length, expected=argv[6])
    return result


def directory_id(info):
    result = {'device': info.st_dev, 'inode': info.st_ino}
    require(all(unsigned(value) for value in result.values()), 'PATH', 'Invalid directory identity')
    return result


def file_id(info):
    result = dict(directory_id(info), bytes=info.st_size,
                  mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns)
    require(all(unsigned(value) for value in result.values()), 'FILE_READ', 'Invalid file identity')
    return result


def owned(logical):
    return logical == HOME or logical == ROOT or logical.startswith(ROOT + '/')


def directory_info(info, logical):
    require(stat.S_ISDIR(info.st_mode), 'PATH', 'Not a directory: ' + logical)
    if owned(logical):
        uid = os.geteuid()
        try:
            account = pwd.getpwuid(uid)
        except KeyError as error:
            raise Rejected('PATH', 'Effective user has no account record') from error
        require(uid != 0 and account.pw_name == 'arduino' and account.pw_dir == HOME and
                info.st_uid == uid, 'PATH', 'Wrong directory owner: ' + logical)
    return directory_id(info)


@contextmanager
def child_directory(parent_fd, name, logical):
    before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    identity = directory_info(before, logical)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    fd = os.open(name, flags, dir_fd=parent_fd)
    try:
        require(directory_info(os.fstat(fd), logical) == identity,
                'PATH', 'Directory changed while opening: ' + logical)
        yield fd
        current = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        require(directory_info(current, logical) == identity,
                'PATH', 'Directory entry changed: ' + logical)
    finally:
        os.close(fd)


@contextmanager
def directory(root_fd, logical):
    require(logical.startswith('/') and PurePosixPath(logical).as_posix() == logical
            and '..' not in logical.split('/'), 'PATH', 'Invalid fixed directory')
    with ExitStack() as stack:
        current, path = root_fd, ''
        for part in logical.split('/')[1:]:
            if part:
                path += '/' + part
                current = stack.enter_context(child_directory(current, part, path))
        yield current


def read_bounded(fd, limit):
    chunks, count = [], 0
    while count <= limit:
        chunk = os.read(fd, min(65536, limit + 1 - count))
        if not chunk:
            return b''.join(chunks)
        chunks.append(chunk)
        count += len(chunk)
    raise Rejected('FILE_READ', 'File exceeds bounded read')


def read_file(parent_fd, name, limit, proc=False, drift_code='FILE_READ'):
    before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    require(stat.S_ISREG(before.st_mode), 'FILE_READ', 'Not a regular file: ' + name)
    require(before.st_size <= limit, 'FILE_READ', 'Oversize file: ' + name)
    identity = file_id(before)
    fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                 dir_fd=parent_fd)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and file_id(info) == identity,
                drift_code, 'File changed while opening: ' + name)
        raw = read_bounded(fd, limit)
        after = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        require(stat.S_ISREG(after.st_mode) and file_id(after) == identity and
                file_id(os.fstat(fd)) == identity and (proc or len(raw) == identity['bytes']),
                drift_code, 'File changed while reading: ' + name)
        return raw, identity
    finally:
        os.close(fd)


def logical_read(root_fd, logical, limit, proc=False):
    parent, name = logical.rsplit('/', 1)
    with directory(root_fd, parent or '/') as fd:
        return read_file(fd, name, limit, proc)[0]


def boot_id(root_fd):
    value = logical_read(root_fd, BOOT_ID, 128, True).decode('utf-8').strip()
    require(UUID.fullmatch(value), 'IDENTITY', 'Invalid kernel boot UUID')
    return value


def identity(root_fd):
    uid = os.geteuid()
    try:
        account = pwd.getpwuid(uid)
    except KeyError as error:
        raise Rejected('IDENTITY', 'Effective user has no account record') from error
    kernel = os.uname()
    require(uid != 0 and account.pw_name == 'arduino' and account.pw_dir == HOME,
            'IDENTITY', 'Expected the nonroot arduino account')
    require(kernel.sysname == 'Linux' and kernel.machine == 'aarch64' and
            sys.version_info[:2] >= (3, 9), 'IDENTITY', 'Wrong Linux/Python identity')
    return {'user': account.pw_name, 'uid': uid, 'gid': os.getegid(), 'home': account.pw_dir,
            'sysname': kernel.sysname, 'release': kernel.release, 'machine': kernel.machine,
            'boot_id': boot_id(root_fd), 'python': list(sys.version_info[:3])}


def resources(root_fd):
    text = logical_read(root_fd, '/proc/meminfo', 65536, True).decode('utf-8')
    values = [line for line in text.splitlines() if line.startswith('MemAvailable:')]
    require(len(values) == 1, 'RESOURCE_MINIMUM', 'Missing or duplicate MemAvailable')
    match = re.fullmatch(r'MemAvailable:\s+([0-9]+) kB', values[0])
    require(match is not None, 'RESOURCE_MINIMUM', 'Malformed MemAvailable')
    result = {'available_ram_bytes': int(match[1]) * 1024}
    for key, path in (('root_available_bytes', ROOT), ('tmp_available_bytes', '/tmp')):
        with directory(root_fd, path) as fd:
            info = os.statvfs(fd)
            require(info.f_bavail >= 0 and info.f_frsize > 0,
                    'RESOURCE_MINIMUM', 'Invalid available filesystem size')
            result[key] = info.f_bavail * info.f_frsize
    return result


def process_status(text):
    states = [line for line in text.splitlines() if line.startswith('State:')]
    threads = [line for line in text.splitlines() if line.startswith('Kthread:')]
    require(len(states) == len(threads) == 1, 'PROCESS_INSPECTION', 'Missing process status')
    state = re.fullmatch(r'State:\s+([A-Za-z])(?:\s+.*)?', states[0])
    thread = re.fullmatch(r'Kthread:\s+([01])\s*', threads[0])
    require(state is not None and thread is not None,
            'PROCESS_INSPECTION', 'Malformed process status')
    return state[1] == 'Z' or thread[1] == '1'


def inspect_process(root_fd, pid):
    with directory(root_fd, '/proc/' + pid) as fd:
        status = read_file(fd, 'status', 65536, True)[0].decode('utf-8')
        cmdline = read_file(fd, 'cmdline', 65536, True)[0].decode('utf-8')
        comm = read_file(fd, 'comm', 65536, True)[0].decode('utf-8').removesuffix('\n')
        excluded = process_status(status)
        require(not cmdline or cmdline.endswith('\0'),
                'PROCESS_INSPECTION', 'Unterminated process command line')
        require(bool(comm) and '\0' not in comm and (bool(cmdline) or excluded),
                'PROCESS_INSPECTION', 'Incomplete process identity')
        if excluded:
            return None
        args = cmdline[:-1].split('\0')
        require(bool(args[0]), 'PROCESS_INSPECTION', 'Empty process argv[0]')
        try:
            executable = os.readlink('exe', dir_fd=fd).removesuffix(' (deleted)')
        except OSError as error:
            if error.errno not in (errno.EACCES, errno.EPERM):
                raise
            executable = ''
        names = [value.rsplit('/', 1)[-1] for value in (args[0], executable) if value]
        reason = None
        if 'arduino-cli' in names and 'compile' in args[1:]:
            reason = 'arduino-cli compile'
        elif any(COMPILER.fullmatch(name) for name in names):
            reason = 'compiler executable'
        if reason:
            return {'pid': int(pid), 'comm': comm, 'argv0': args[0], 'reason': reason}
        return None


def scan_processes(root_fd):
    with directory(root_fd, '/proc') as fd:
        pids = []
        with os.scandir(fd) as entries:
            for entry in entries:
                if re.fullmatch(r'[0-9]+', entry.name):
                    pids.append(entry.name)
                    require(len(pids) <= 4096, 'PROCESS_INSPECTION', 'Too many process IDs')
        candidates = []
        for pid in sorted(pids, key=int):
            try:
                candidate = inspect_process(root_fd, pid)
                if candidate is not None:
                    candidates.append(candidate)
            except OSError as error:
                if error.errno == errno.ESRCH:
                    continue
                if error.errno == errno.ENOENT:
                    try:
                        os.stat(pid, dir_fd=fd, follow_symlinks=False)
                    except FileNotFoundError:
                        continue
                    except OSError as lookup_error:
                        raise Rejected('PROCESS_INSPECTION', str(lookup_error)) from lookup_error
                raise Rejected('PROCESS_INSPECTION', str(error)) from error
            except (Rejected, UnicodeError) as error:
                raise Rejected('PROCESS_INSPECTION', str(error)) from error
    return candidates


def processes(root_fd):
    try:
        return scan_processes(root_fd)
    except (OSError, Rejected, UnicodeError) as error:
        raise Rejected('PROCESS_INSPECTION', str(error)) from error


def inventory_action(root_fd, request, data):
    data['identity'] = identity(root_fd)
    data['resources'] = resources(root_fd)
    data['compiler_candidates'] = processes(root_fd)
    require(not data['compiler_candidates'], 'COMPILER_PRESENT', 'Compiler already present')
    limits = {'available_ram_bytes': 512 * 1048576,
              'root_available_bytes': 1073741824, 'tmp_available_bytes': 1073741824}
    require(all(data['resources'][name] >= limit for name, limit in limits.items()),
            'RESOURCE_MINIMUM', 'Insufficient available Linux resources')


def source_data():
    return {'path': SKETCH, 'source_sha256': SOURCE, 'file_count': None,
            'total_bytes': 0, 'files': {}}


def walk_source(fd, logical, relative, files, directories, count, depth):
    require(depth <= 64, 'SOURCE_SET', 'Source tree depth exceeds limit')
    directories[relative] = directory_id(os.fstat(fd))
    with os.scandir(fd) as entries:
        for entry in entries:
            count[0] += 1
            require(count[0] <= 4096, 'SOURCE_SET', 'Source tree entry limit exceeded')
            name = relative + '/' + entry.name if relative else entry.name
            info = os.stat(entry.name, dir_fd=fd, follow_symlinks=False)
            if stat.S_ISDIR(info.st_mode):
                with child_directory(fd, entry.name, logical + '/' + entry.name) as child:
                    walk_source(child, logical + '/' + entry.name, name,
                                files, directories, count, depth + 1)
            else:
                require(stat.S_ISREG(info.st_mode), 'SOURCE_SET', 'Nonregular source: ' + name)
                files[name] = file_id(info)


def source_snapshot(fd):
    files, directories = {}, {}
    walk_source(fd, SKETCH, '', files, directories, [0], 0)
    return files, directories


def source_action(root_fd, request, data):
    with directory(root_fd, SKETCH) as fd:
        before, before_dirs = source_snapshot(fd)
        data['file_count'] = len(before)
        require(set(before) == set(request['manifest']), 'SOURCE_SET', 'Source file set differs')
        digest = hashlib.sha256()
        for name in sorted(before):
            parent, filename = (SKETCH + '/' + name).rsplit('/', 1)
            with directory(root_fd, parent) as parent_fd:
                raw, observed = read_file(parent_fd, filename, SOURCE_LIMIT, drift_code='SOURCE_DRIFT')
            data['files'][name] = {'bytes': len(raw), 'sha256': sha256(raw)}
            data['total_bytes'] += len(raw)
            require(observed == before[name] and sha256(raw) == request['manifest'][name],
                    'SOURCE_DRIFT', 'Source bytes or identity changed: ' + name)
            digest.update(name.encode('utf-8') + b'\0' + raw)
        after, after_dirs = source_snapshot(fd)
        require(before == after and before_dirs == after_dirs and digest.hexdigest() == SOURCE,
                'SOURCE_DRIFT', 'Source tree or bound digest changed')


def run_paths(run_id):
    run = PARENT + '/' + run_id
    return {'run': run, 'build': run + '/build', 'artifacts': run + '/artifacts'}


@contextmanager
def claimed(root_fd, claim):
    stack = ExitStack()
    try:
        require(boot_id(root_fd) == claim['boot_id'], 'PATH', 'Claim boot identity changed')
        fds = {}
        for key, path in run_paths(claim['run_id']).items():
            fds[key] = stack.enter_context(directory(root_fd, path))
            require(directory_id(os.fstat(fds[key])) == claim['directories'][key],
                    'PATH', 'Claimed directory identity differs: ' + key)
    except (OSError, Rejected, UnicodeError) as error:
        stack.__exit__(*sys.exc_info())
        raise Rejected('PATH', str(error)) from error
    try:
        yield fds
    except BaseException:
        stack.__exit__(*sys.exc_info())
        raise
    else:
        try:
            require(boot_id(root_fd) == claim['boot_id'], 'PATH', 'Claim boot identity changed')
            stack.close()
        except (OSError, Rejected, UnicodeError) as error:
            stack.__exit__(*sys.exc_info())
            raise Rejected('PATH', str(error)) from error


def checked_claim(root_fd, claim):
    try:
        with claimed(root_fd, claim):
            return claim
    except (OSError, Rejected) as error:
        raise Rejected('PATH', str(error)) from error


def mkdir_owned(parent_fd, name, logical, created):
    os.mkdir(name, 0o700, dir_fd=parent_fd)
    created.append(logical)


def claim_action(root_fd, request, data):
    partial = {'run': None, 'build': None, 'artifacts': None}
    try:
        current_boot = boot_id(root_fd)
        with ExitStack() as stack:
            fd = stack.enter_context(directory(root_fd, ROOT))
            logical = ROOT
            for name in ('_app_builds', 'static-app-probe-v1', SOURCE, 'bench-default'):
                logical += '/' + name
                try:
                    os.stat(name, dir_fd=fd, follow_symlinks=False)
                except FileNotFoundError:
                    mkdir_owned(fd, name, logical, data['created'])
                fd = stack.enter_context(child_directory(fd, name, logical))
            run_id = request['run_id']
            try:
                mkdir_owned(fd, run_id, logical + '/' + run_id, data['created'])
            except FileExistsError as error:
                raise Rejected('CLAIM_EXISTS', 'Run destination already exists') from error
            run_fd = stack.enter_context(child_directory(fd, run_id, logical + '/' + run_id))
            partial['run'] = directory_id(os.fstat(run_fd))
            for key in ('build', 'artifacts'):
                path = logical + '/' + run_id + '/' + key
                mkdir_owned(run_fd, key, path, data['created'])
                child = stack.enter_context(child_directory(run_fd, key, path))
                partial[key] = directory_id(os.fstat(child))
            require(boot_id(root_fd) == current_boot, 'PATH', 'Boot changed during claim')
            data['claim'] = {'run_id': run_id, 'boot_id': current_boot, 'directories': partial}
    except (OSError, Rejected, UnicodeError) as error:
        data['claim'] = None
        data['partial_directories'] = partial
        if isinstance(error, Rejected) and error.code == 'CLAIM_EXISTS':
            raise
        code = 'CLAIM_INCOMPLETE' if data['created'] else 'PATH'
        raise Rejected(code, str(error)) from error


def absent_action(root_fd, request, data):
    with claimed(root_fd, request['claim']) as fds:
        data['claim'] = request['claim']
        failed = False
        for key in LIMITS:
            folder, name = key.split('/')
            try:
                os.stat(name, dir_fd=fds[folder], follow_symlinks=False)
                data['outputs'][key] = 'present'
            except FileNotFoundError:
                data['outputs'][key] = 'absent'
            except OSError:
                failed = True
        require(not failed and all(value == 'absent' for value in data['outputs'].values()),
                'OUTPUT_PRESENT', 'Outputs are present or could not be checked')


def file_record(state, identity=None, digest=None):
    return {'state': state, 'identity': identity, 'sha256': digest}


def observe_file(fd, name, limit):
    try:
        first = os.stat(name, dir_fd=fd, follow_symlinks=False)
    except FileNotFoundError:
        return file_record('missing'), None
    if not stat.S_ISREG(first.st_mode):
        return file_record('nonregular'), None
    observed = file_id(first)
    if first.st_size == 0 or first.st_size > limit:
        try:
            child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                            dir_fd=fd)
            try:
                info = os.fstat(child)
                require(stat.S_ISREG(info.st_mode) and file_id(info) == observed,
                        'FILE_READ', 'Artifact changed while opening')
                current = file_id(info)
                require(file_id(os.stat(name, dir_fd=fd, follow_symlinks=False)) == current,
                        'FILE_READ', 'Artifact entry changed')
            finally:
                os.close(child)
        except (OSError, Rejected):
            return file_record('unstable', observed), None
        return file_record('empty' if current['bytes'] == 0 else 'oversize', current), None
    try:
        raw, current = read_file(fd, name, limit)
        if current != observed:
            return file_record('unstable', observed), None
        return file_record('regular', observed, sha256(raw)), raw
    except (OSError, Rejected):
        return file_record('unstable', observed), None


def scan_artifacts(fds, data, keep=False):
    data['files'], payloads = {}, {}
    errors = []
    for key, limit in LIMITS.items():
        folder, name = key.split('/')
        try:
            record, raw = observe_file(fds[folder], name, limit)
            data['files'][key] = record
            if keep or key.endswith('/app.ino.bin-zsk.bin'):
                payloads[key] = raw
        except OSError as error:
            errors.append(str(error))
    require(not errors and len(data['files']) == 8 and
            all(item['state'] == 'regular' for item in data['files'].values()),
            'ARTIFACT_SET', 'Incomplete or nonregular artifacts' + (': ' + errors[0] if errors else ''))
    require(payloads['build/app.ino.bin-zsk.bin'] == payloads['artifacts/app.ino.bin-zsk.bin'],
            'ARTIFACT_SET', 'Exported flat package differs from build package')
    return payloads


def artifacts_action(root_fd, request, data):
    with claimed(root_fd, request['claim']) as fds:
        data['claim'] = request['claim']
        scan_artifacts(fds, data)


def layout_action(root_fd, request, data):
    with claimed(root_fd, request['claim']) as fds:
        data['claim'] = request['claim']
        payloads = scan_artifacts(fds, data, True)
        before = data['files']
        inputs = {key.split('/')[1]: value for key, value in payloads.items()
                  if key.startswith('build/')}
        namespace = {'__name__': 'static_artifacts'}
        exec(compile(request['validator'], '<static-artifacts>', 'exec'), namespace)
        try:
            report = namespace['validate_artifacts'](inputs)
        except ValueError as error:
            raise Rejected('LAYOUT_REJECTED', str(error)) from error
        data['report'] = report
        expected = {name: {'bytes': len(raw), 'sha256': sha256(raw)} for name, raw in inputs.items()}
        require(report['artifacts'] == expected, 'LAYOUT_REJECTED', 'Report input identities differ')
        scan_artifacts(fds, data)
        require(before == data['files'], 'FILE_READ', 'Artifacts changed during layout validation')


def read_action(root_fd, request, data):
    with claimed(root_fd, request['claim']) as fds:
        data['claim'] = request['claim']
        record, raw = observe_file(fds['build'], 'app.ino.elf', LIMITS['build/app.ino.elf'])
        data['name'], data['file'] = 'app.ino.elf', record
        require(record['state'] == 'regular' and record['sha256'] == request['expected'],
                'FILE_READ', 'Final ELF is missing, changed or unreadable')
        offset, length = request['offset'], request['length']
        require(offset < len(raw) and length == min(CHUNK, len(raw) - offset),
                'BAD_REQUEST', 'Read chunk does not match remaining file extent')
        chunk = raw[offset:offset + length]
        current, unused = observe_file(fds['build'], 'app.ino.elf', LIMITS['build/app.ino.elf'])
        require(record == current, 'FILE_READ', 'Final ELF changed during chunk collection')
        data.update(offset=offset, length=length, chunk_sha256=sha256(chunk),
                    base64=base64.b64encode(chunk).decode('ascii'))


def postcheck_part(name, function, data, failures):
    try:
        function()
    except (Rejected, OSError, UnicodeError) as error:
        code = error.code if isinstance(error, Rejected) else {
            'claim': 'PATH', 'identity': 'IDENTITY', 'resources': 'RESOURCE_MINIMUM',
            'processes': 'PROCESS_INSPECTION', 'source': 'SOURCE_SET', 'files': 'FILE_READ'}[name]
        failures.append({'check': name, 'code': code, 'message': str(error)})


def postcheck_action(root_fd, request, data):
    failures = []
    def check_claim():
        data['claim'] = checked_claim(root_fd, request['claim'])
    def check_identity():
        data['identity'] = identity(root_fd)
    def check_resources():
        data['resources'] = resources(root_fd)
    def check_processes():
        data['compiler_candidates'] = processes(root_fd)
        require(not data['compiler_candidates'], 'COMPILER_PRESENT', 'Compiler already present')
    def check_source():
        data['source'] = source_data()
        source_action(root_fd, request, data['source'])
    def check_files():
        require(data['claim'] is not None, 'PATH', 'Failed claim prevents output reads')
        with claimed(root_fd, request['claim']) as fds:
            scan_artifacts(fds, data)
    for name, function in (('claim', check_claim), ('identity', check_identity),
                           ('resources', check_resources), ('processes', check_processes),
                           ('source', check_source), ('files', check_files)):
        postcheck_part(name, function, data, failures)
    if failures:
        data['failures'] = failures
        raise Rejected('POSTCHECK_FAILED', 'One or more independent postchecks failed')


def initial_data(action):
    fields = {'inventory': ('identity', 'resources', 'compiler_candidates'),
              'claim': ('claim', 'created'), 'absent': ('claim', 'outputs'),
              'artifacts': ('claim', 'files'),
              'layout': ('claim', 'validator_sha256', 'files', 'report'),
              'read': ('claim', 'name', 'file', 'offset', 'length', 'chunk_sha256', 'base64'),
              'postcheck': ('claim', 'identity', 'resources', 'compiler_candidates', 'source', 'files')}
    if action == 'source':
        return source_data()
    data = dict.fromkeys(fields[action])
    if action == 'claim':
        data['created'] = []
    if action == 'absent':
        data['outputs'] = dict.fromkeys(LIMITS)
    if action == 'layout':
        data['validator_sha256'] = VALIDATOR_SHA256
    return data


def dispatch(root_fd, request, data):
    actions = {'inventory': inventory_action, 'source': source_action, 'claim': claim_action,
               'absent': absent_action, 'artifacts': artifacts_action, 'layout': layout_action,
               'read': read_action, 'postcheck': postcheck_action}
    actions[request['action']](root_fd, request, data)


def error_code(action):
    return {'inventory': 'IDENTITY', 'source': 'SOURCE_SET', 'claim': 'PATH',
            'absent': 'PATH', 'artifacts': 'FILE_READ', 'layout': 'FILE_READ',
            'read': 'FILE_READ', 'postcheck': 'POSTCHECK_FAILED'}[action]


def envelope(action, run_id, data, error=None):
    return {'schema': 'static-remote-v1', 'action': action, 'run_id': run_id,
            'ok': error is None, 'data': data, 'error': error}


def failure_fields(action, data, message):
    if action == 'claim':
        data.setdefault('partial_directories', dict.fromkeys(('run', 'build', 'artifacts')))
    if action == 'postcheck' and 'failures' not in data:
        codes = (('claim', 'PATH'), ('identity', 'IDENTITY'),
                 ('resources', 'RESOURCE_MINIMUM'), ('processes', 'PROCESS_INSPECTION'),
                 ('source', 'SOURCE_SET'), ('files', 'PATH'))
        data['failures'] = [{'check': name, 'code': code, 'message': message}
                            for name, code in codes]


def main(argv, *, fs_root=Path('/')):
    supplied = argv if type(argv) is list else []
    action = supplied[0] if supplied and type(supplied[0]) is str else None
    run_id = supplied[1] if len(supplied) > 1 and type(supplied[1]) is str else None
    data, admitted, result, exit_code = {}, False, None, 0
    try:
        try:
            request = parse_request(argv)
        except (ValueError, UnicodeError, zlib.error, RecursionError) as error:
            raise Rejected('BAD_REQUEST', str(error)) from error
        admitted = True
        data = initial_data(action)
        require(isinstance(fs_root, Path) and fs_root.is_absolute(), 'PATH', 'Invalid fixture root')
        fd = os.open(fs_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            dispatch(fd, request, data)
        finally:
            os.close(fd)
        result = envelope(action, run_id, data)
        require(action != 'layout' or len(canonical(result).encode('utf-8')) + 1 <= 1048576,
                'REPORT_LIMIT', 'Layout report exceeds 1 MiB')
    except (Rejected, OSError, UnicodeError) as error:
        code = error.code if isinstance(error, Rejected) else (
            error_code(action) if admitted else 'BAD_REQUEST')
        if admitted:
            failure_fields(action, data, str(error))
        result = envelope(action, run_id, data, {'code': code, 'message': str(error)})
        exit_code = 2
    except Exception as error:
        traceback.print_exc()
        if admitted:
            failure_fields(action, data, str(error))
        result = envelope(action, run_id, data,
                          {'code': 'INTERNAL_ERROR', 'message': str(error)})
        exit_code = 3
    print(canonical(result))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
