# Compiles one fixed current-app profile through the existing checked policy.
# Reuses the pinned transport and child lifecycle without loading historical owners.
# Verified by separately frozen controlled tests before any reviewed native use.
import ast
import base64
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import stat
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[3]
CALLER = 'state/analysis/P7_current_app_compile_raw/compile_current_app.py'
CONTRACT = 'state/analysis/P7_current_app_compile_contract.md'
RAW = str(PurePosixPath(CALLER).parent)
SOURCE = '37a2099f6938baf6430cfed2b5a002793d9748820fe0876e9cd039fd94330c29'
BOARD = '2629958581'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
PARENT = '/home/arduino/sumox26_codex_build'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
ADB_SHA = 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'
CLI = '/usr/bin/arduino-cli'
CLI_SHA = 'b878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433'
EXECUTOR = 'state/analysis/P7_motor_fault_raw/compile_motor_fault.py'
SUPPORT = 'state/analysis/P7_static_startup_raw/capture_remote.py'
SUPPORT_SHA = '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e'
BASELINES = dict(initialization='state/analysis/P7_static_startup_raw/cli_initialization_inventory.json',
                 builtins='state/analysis/P7_static_startup_raw/cli_builtin_files_inventory.json')
HARD_PINS = {
    EXECUTOR: '84efd00611b3a6a8129655005930ff58e555221f6bd8d88a23c7fa1c4381ac0d',
    SUPPORT: SUPPORT_SHA,
    BASELINES['initialization']: 'aaa2c307b7ed1b8d7e00a737447a03a63a78cd4b7fb2145142b20e9501da1e62',
    BASELINES['builtins']: 'a364beb814b36b9c56328b54a9de5fa0f4ad80a67003d40c7cc994a1917ba2cb'}
REQUIRED = {CALLER, CONTRACT, 'tools/board_tool.py', 'tools/app_build_policy.py',
            'tools/app_build_commands.json', 'tools/app_build_pins.json',
            'tools/match_deploy.py', *HARD_PINS}
WAIT_PINS = {'stop_child': 'c6545967d8236164af2570a15573810ea9ccb43773e45c49364f5b494b6a4d44',
             'wait_child': '65512632a53799f2b33ae43623f36c697623901e6b24ce1cdddf5b223a671259'}
ENV = {'HOME': '/home/arduino', 'USER': 'arduino', 'LOGNAME': 'arduino',
       'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    value = {}
    for key, item in pairs:
        require(key not in value, 'Duplicate JSON key')
        value[key] = item
    return value


def decode(raw):
    def invalid(value):
        raise ValueError('Nonfinite JSON value: ' + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def parse_request(argv):
    require(type(argv) is list and all(type(value) is str for value in argv),
            'Expected an exact argument list')
    require(len(argv) == 5 and argv[0] in ('--check-only', '--execute') and
            argv[1] == '--profile' and argv[2] in ('bench', 'match') and
            argv[3] == '--reviewed-head' and re.fullmatch('[0-9a-f]{40}', argv[4]),
            'Expected --check-only|--execute --profile bench|match --reviewed-head <40lowerhex>')
    return argv[0], argv[2], argv[4]


def relative(name):
    require(type(name) is str and bool(name), 'Relative input path required')
    reserved = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)),
                *(f'lpt{i}' for i in range(1, 10))}
    for part in name.split('/'):
        require(re.fullmatch('[A-Za-z0-9_.-]+', part) and part not in ('.', '..') and
                not part.endswith('.') and part.split('.')[0].lower() not in reserved,
                'Invalid relative input path')
    return name


def plain(path, directory=False):
    require(path.is_absolute(), 'Absolute local path required')
    for item in (path, *path.parents):
        info = item.lstat()
        require(not stat.S_ISLNK(info.st_mode) and
                not getattr(info, 'st_file_attributes', 0) & 1024, 'Linked local path')
        expected = stat.S_ISDIR if item != path or directory else stat.S_ISREG
        require(expected(info.st_mode), 'Unexpected local path type')


def read(path, limit=1048576):
    plain(path)
    before = path.stat()
    require(before.st_size <= limit, 'Local input exceeds bound')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(limit + 1)
    identity = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)
    require(identity(before) == identity(opened) == identity(path.stat()) and
            len(raw) == before.st_size and len(raw) <= limit, 'Local input changed while reading')
    return raw


def source_names(root):
    pending, result, count = [root / 'src'], set(), 0
    while pending:
        folder = pending.pop()
        plain(folder, directory=True)
        for path in folder.iterdir():
            count += 1
            require(count <= 1024, 'Source entry count exceeds bound')
            plain(path, directory=path.is_dir())
            if path.is_dir():
                pending.append(path)
            else:
                result.add(relative(path.relative_to(root).as_posix()))
                require(len(result) <= 512, 'Source file count exceeds bound')
    return result


def module_from(root, name, raw):
    module = types.ModuleType('current_compile_' + Path(name).stem)
    module.__file__ = str(root / name)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def checked_wait(raw):
    require(sha(raw) == SUPPORT_SHA, 'Wait source changed')
    source = raw.decode('utf-8')
    nodes = [node for node in ast.parse(source).body
             if isinstance(node, ast.FunctionDef) and node.name in WAIT_PINS]
    require(sorted(node.name for node in nodes) == sorted(WAIT_PINS), 'Wait definitions changed')
    for node in nodes:
        require(sha(ast.get_source_segment(source, node).encode()) == WAIT_PINS[node.name],
                'Wait/reap body changed')


def executor_namespace(root, raw):
    require(sha(raw) == HARD_PINS[EXECUTOR], 'Original executor changed')
    tree = ast.parse(raw)
    functions = {'require', 'sha', 'unique', 'decode', 'write', 'files', 'projection', 'extracted_wait'}
    methods = {'transport', 'direct', 'command_runner'}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in functions]
    owners = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'CompileOnce']
    require(len(owners) == 1, 'Original owner definition changed')
    nodes.extend(node for node in owners[0].body if isinstance(node, ast.FunctionDef) and node.name in methods)
    require(sorted(node.name for node in nodes) == sorted(functions | methods), 'Executor definitions changed')
    namespace = dict(ast=ast, base64=base64, hashlib=hashlib, json=json, os=os,
                     Path=Path, PurePosixPath=PurePosixPath, re=re, shlex=shlex,
                     subprocess=subprocess, ROOT=root, BOARD=BOARD, BOOT=BOOT,
                     ADB=ADB, ADB_SHA=ADB_SHA, CLI=CLI, CLI_SHA=CLI_SHA,
                     SUPPORT=SUPPORT, SUPPORT_SHA=SUPPORT_SHA, ENV=ENV)
    for name in ('IDENTITY', 'REMOTE_CHILD'):
        values = [node.value for node in tree.body if isinstance(node, ast.Assign) and
                  len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == name]
        require(len(values) == 1, 'Executor constant changed')
        namespace[name] = ast.literal_eval(values[0])
        require(type(namespace[name]) is str, 'Executor constant is not text')
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(root / EXECUTOR), 'exec'), namespace)
    return namespace


def error_value(error):
    return {'type': type(error).__name__, 'message': str(error)}


def failure_guard(error, method):
    # A failed receipt write must not hide a child result already obtained.
    if isinstance(error, subprocess.SubprocessError):
        return error
    primary, context = error, error.__context__
    while context is not None:
        if isinstance(context, (subprocess.SubprocessError, OSError)):
            primary = context
        context = context.__context__
    if not isinstance(error, OSError):
        return primary
    trace = error.__traceback__
    while primary is error and trace is not None:
        local = trace.tb_frame.f_locals
        if trace.tb_frame.f_code.co_name == method:
            result = local.get('result')
            if isinstance(result, subprocess.CompletedProcess) and result.returncode:
                primary = subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
            record = local.get('record', {})
            execution = record.get('execution', {}) if type(record) is dict else {}
            if method == 'command_runner' and type(execution.get('returncode')) is int and execution['returncode']:
                primary = subprocess.CalledProcessError(execution['returncode'], local.get('argv'),
                    base64.b64decode(record.get('stdout_base64', ''), validate=True).decode('utf-8'),
                    base64.b64decode(record.get('stderr_base64', ''), validate=True).decode('utf-8'))
        trace = trace.tb_next
    if primary is not error:
        failures = getattr(primary, 'evidence_write_errors', [])
        primary.evidence_write_errors = [*failures, error_value(error)]
    return primary


class CompileCurrent:
    def __init__(self, profile, reviewed_head, *, root=ROOT):
        parse_request(['--check-only', '--profile', profile, '--reviewed-head', reviewed_head])
        self.profile, self.reviewed_head, self.root = profile, reviewed_head, Path(root).absolute()
        self.output = self.root / RAW / ('native_' + profile + '01')
        self.inputs_path = self.root / RAW / ('inputs_' + profile + '.json')
        self.stage_attempt = 'current-app-' + profile + '01'
        self.stage_owner = self.root / 'build/stage' / self.stage_attempt
        self.stage_path = self.stage_owner / 'app'
        self.remote_root, self.remote = PARENT, PARENT + '/' + self.stage_attempt
        self.sketch = PARENT + '/' + SOURCE + '/app'
        self.startup = 'immediate' if profile == 'match' else 'default'
        self.fqbn = 'arduino:zephyr:unoq' + (':wait_linux_boot=no' if profile == 'match' else '')
        self.flags = '-DMATCH=1 -DMOTORS_ALLOWED=1' if profile == 'match' else '-DMATCH=0 -DMOTORS_ALLOWED=0'
        self.counter = self.compiler_calls = self.query_calls = 0
        self.claimed = self.remote_owned = self.source_available = self.source_attempted = False
        self.inputs_raw = self.inputs = self.code = self.stage_hashes = None
        self.executor = self.board = self.artifacts = self.receipt = None

    def git_state(self):
        def git(arguments):
            result = subprocess.run(['git', '-C', str(self.root), *arguments],
                                    stdin=subprocess.DEVNULL, capture_output=True, timeout=30, check=True)
            require(len(result.stdout) <= 1048576 and not result.stderr, 'Invalid Git output')
            return result.stdout.decode('utf-8')
        head = git(['rev-parse', 'HEAD']).strip()
        rows = git(['status', '--porcelain=v1', '-z', '--untracked-files=all']).split('\0')
        require(all(len(row) >= 4 and row[2] == ' ' for row in rows if row), 'Malformed Git status')
        return head, [(row[:2], row[3:]) for row in rows if row]

    def admission(self):
        raw = read(self.inputs_path, 262144)
        if self.inputs_raw is not None:
            require(raw == self.inputs_raw, 'Input manifest changed')
        value = decode(raw)
        require(type(value) is dict and set(value) ==
                {'schema', 'profile', 'source_sha256', 'boot_id', 'files'}, 'Invalid manifest schema')
        require(value['schema'] == 'current-app-compile-inputs-v1' and value['profile'] == self.profile and
                value['source_sha256'] == SOURCE and value['boot_id'] == BOOT, 'Manifest identity changed')
        pins = value['files']
        names = source_names(self.root)
        require(type(pins) is dict and set(pins) == REQUIRED | names, 'Input filename set changed')
        code, total = {}, 0
        for name, expected in pins.items():
            require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected), 'Invalid input digest')
            code[name] = read(self.root / relative(name))
            require(sha(code[name]) == expected, 'Pinned input changed: ' + name)
            if name in names:
                total += len(code[name])
        require(total <= 4194304, 'Source bytes exceed bound')
        for name, expected in HARD_PINS.items():
            require(pins[name] == expected, 'Hard pin changed: ' + name)
        checked_wait(code[SUPPORT])
        view = module_from(self.root, 'tools/match_deploy.py', code['tools/match_deploy.py'])
        require(view.app_source_hash(self.root) == SOURCE, 'Current app source changed')
        self.inputs_raw, self.inputs, self.code = raw, value, code

    def local(self):
        require(sys.dont_write_bytecode, 'Python -B required')
        require(not os.path.lexists(self.output / 'pycache'), 'Pycache owner must remain absent')
        head, changes = self.git_state()
        require(head == self.reviewed_head, 'Reviewed HEAD changed')
        prefix = self.output.relative_to(self.root).as_posix() + '/'
        require(all(self.claimed and status == '??' and name.startswith(prefix)
                    for status, name in changes), 'Reviewed working tree is not clean')
        self.admission()
        plain(Path(ADB))
        require(sha(Path(ADB).read_bytes()) == ADB_SHA, 'ADB changed')
        require(not os.path.lexists(importlib.util.cache_from_source(
            str(self.root / 'tools/app_build_policy.py'))), 'Nested policy bytecode cache exists')
        if self.stage_hashes is not None:
            for path in self.stage_path.rglob('*'):
                plain(path, directory=path.is_dir())
            require(self.executor['files'](self.stage_path) == self.stage_hashes, 'Local stage changed')

    def check(self):
        self.local()
        require(not os.path.lexists(self.output), 'Local output owner already exists')
        require(not os.path.lexists(self.stage_owner), 'Local stage owner already exists')
        plain(self.output.parent, directory=True)
        for path in (self.root / 'build', self.root / 'build/stage', self.root / 'build/app-receipts'):
            if os.path.lexists(path):
                plain(path, directory=True)
        require(shutil.disk_usage(self.root).free >= 134217728, 'Less than 128MiB local free space')
        return dict(schema='current-app-compile-check-v1', profile=self.profile,
                    reviewed_head=self.reviewed_head, source_sha256=SOURCE, boot_id=BOOT,
                    output=str(self.output), stage=str(self.stage_path), remote=self.remote, sketch=self.sketch)

    def load_board(self):
        return module_from(self.root, 'tools/board_tool.py', self.code['tools/board_tool.py'])

    def prepare(self):
        self.executor = executor_namespace(self.root, self.code[EXECUTOR])
        self.board = self.load_board()

    def save(self, name, value):
        require(type(name) is str and re.fullmatch(r'[a-z_]+\.json', name), 'Invalid evidence name')
        self.executor['write'](self.output / name, value)

    def claim(self):
        self.output.mkdir(mode=0o700)
        self.claimed = True
        self.save('intent.json', dict(schema='current-app-compile-intent-v1', profile=self.profile,
            reviewed_head=self.reviewed_head, source_sha256=SOURCE, boot_id=BOOT,
            inputs_sha256=sha(self.inputs_raw), stage=str(self.stage_path), remote=self.remote,
            sketch=self.sketch, started_utc=datetime.now(timezone.utc).isoformat()))

    def transport(self, arguments, timeout, label):
        self.local()
        try:
            return self.executor['transport'](self, arguments, timeout, label)
        except Exception as error:
            primary = failure_guard(error, 'transport')
            if primary is error:
                raise
            raise primary from error

    def direct(self, program, label, timeout=90):
        return self.executor['direct'](self, program, label, timeout)

    def preamble(self):
        values = dict(BOOT=BOOT, CLI=CLI, CLI_SHA=CLI_SHA, REMOTE=self.remote, ENV=ENV)
        return '\n'.join(name + '=' + repr(value) for name, value in values.items()) + '\n' + self.executor['IDENTITY']

    def inventory(self, initial=False):
        extra = "if free<1073741824:raise ValueError('Less than 1GiB free')\n"
        if initial:
            extra += "if os.path.lexists(REMOTE):raise ValueError('Remote command owner exists')\n"
        reply, _ = self.direct(self.preamble() + extra + 'print(json.dumps(identity))\n', 'identity')
        value = decode(reply.stdout)
        require(not reply.stderr and type(value) is dict and set(value) ==
                {'uid', 'user', 'boot_id', 'cli_sha256', 'free_bytes', 'conflicts'}, 'Invalid identity reply')
        require(type(value['uid']) is int and value['uid'] == 1000 and value['user'] == 'arduino' and
                value['boot_id'] == BOOT and value['cli_sha256'] == CLI_SHA and value['conflicts'] == [] and
                type(value['free_bytes']) is int and value['free_bytes'] >= 1073741824, 'Board identity changed')
        return value

    def prerequisite(self, name):
        require(name in BASELINES, 'Unknown prerequisite')
        baseline = decode(self.code[BASELINES[name]])
        require(baseline['returncode'] == 0 and not baseline['stderr'], 'Failed baseline')
        reply, _ = self.transport(['shell', '-T', shlex.join(baseline['argv'])], 60, Path(BASELINES[name]).stem)
        require(not reply.stderr and len(reply.stdout) <= 1048576, 'Invalid prerequisite output')
        value, expected = decode(reply.stdout), decode(baseline['stdout'])
        expected['identity']['boot_id'] = BOOT
        require(value['status'] == 'COLLECTED' and value['identity'] == expected['identity'] and
                type(value['identity']['uid']) is int and value['identity']['uid'] == 1000,
                'Prerequisite identity/status changed')
        require(self.executor['projection'](value) == self.executor['projection'](expected),
                'CLI initialization prerequisites changed')
        return value

    def prerequisites(self):
        for name in BASELINES:
            self.prerequisite(name)

    def source_program(self):
        return self.preamble() + 'root=Path(' + repr(self.sketch) + ')\n' + '''def source_set():
 if not root.is_dir() or root.resolve()!=root:raise ValueError('Missing/linked source root')
 result={};count=0
 for p in root.rglob('*'):
  count+=1
  if count>1024:raise ValueError('Source entry bound')
  if p.is_symlink():raise ValueError('Linked source entry')
  if p.is_file():
   if p.stat().st_size>1048576:raise ValueError('Source file bound')
   result[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
  elif not p.is_dir():raise ValueError('Nonregular source entry')
 return result
'''

    def source_admission(self):
        self.source_attempted = True
        program = self.source_program() + 'expected=' + repr(self.stage_hashes) + '\n' + '''if os.path.lexists(root.parent):
 if root.parent.resolve()!=root.parent or not root.parent.is_dir():raise ValueError('Invalid source owner')
 if sorted(p.name for p in root.parent.iterdir())!=['app']:raise ValueError('Unexpected source owner entries')
 if source_set()!=expected:raise ValueError('Existing source differs')
 reused=True
else:
 root.parent.mkdir(mode=0o700);root.mkdir();reused=False
 for name in expected:(root/name).parent.mkdir(parents=True,exist_ok=True)
print(json.dumps({'reused':reused}))
'''
        reply, _ = self.direct(program, 'source-admission')
        value = decode(reply.stdout)
        require(not reply.stderr and type(value) is dict and set(value) == {'reused'} and
                type(value['reused']) is bool, 'Invalid source admission reply')
        return value['reused']

    def sources(self):
        reply, _ = self.direct(self.source_program() + 'print(json.dumps(source_set()))\n', 'source-set')
        require(not reply.stderr and decode(reply.stdout) == self.stage_hashes,
                'Remote source filename/hash set changed')

    def stage(self):
        self.local()
        require(not os.path.lexists(self.stage_owner), 'Local stage owner already exists')
        require(shutil.disk_usage(self.root).free >= 134217728, 'Less than 128MiB local free space')
        staged = self.board.stage('app', attempt=self.stage_attempt)
        require(staged == self.stage_path, 'Wrong stage')
        self.stage_hashes = self.executor['files'](staged)
        require(self.board.source_hash(staged) == SOURCE, 'Stage differs from current source')
        self.local()
        self.save('staged_files.json', self.stage_hashes)
        program = self.preamble() + "Path(REMOTE).mkdir(mode=0o700)\n(Path(REMOTE)/'commands').mkdir()\nprint(json.dumps(identity))\n"
        reply, _ = self.direct(program, 'command-owner')
        require(not reply.stderr and decode(reply.stdout)['boot_id'] == BOOT, 'Invalid command owner reply')
        self.remote_owned = True
        if not self.source_admission():
            for name in self.stage_hashes:
                self.inventory()
                self.transport(['push', str(self.stage_path / name), self.sketch + '/' + name], 60, 'push')
        self.sources()
        self.source_available = True

    def command_runner(self, board, argv, capture=False, timeout=None):
        require(self.remote_owned and self.source_available, 'Compile source ownership unconfirmed')
        try:
            return self.executor['command_runner'](self, board, argv, capture, timeout)
        except Exception as error:
            primary = failure_guard(error, 'command_runner')
            if primary is error:
                raise
            raise primary from error

    def policy(self):
        self.local()
        return module_from(self.root, 'tools/app_build_policy.py', self.code['tools/app_build_policy.py'])

    def verify_receipt(self, artifacts):
        prefix = PARENT + '/_app_builds/native-app-v1/' + SOURCE + '/' + self.profile + '-' + self.startup + '/'
        require(type(artifacts) is str and artifacts.startswith(prefix), 'Unexpected artifact root')
        tail = artifacts[len(prefix):]
        require(re.fullmatch('[0-9a-f]{32}/artifacts', tail), 'Unexpected build identity')
        receipt = 'build/app-receipts/' + tail.split('/')[0] + '/verified.json'
        value = decode(read(self.root / receipt))
        build_path = artifacts.rsplit('/', 1)[0] + '/build'
        expected = dict(policy='native-app-v1', source_sha256=SOURCE, fqbn=self.fqbn,
                        build_path=build_path, artifacts=artifacts, compiler_returncode=0,
                        used_libraries=[], resolved_directories=dict(data='/home/arduino/.arduino15',
                        user='/home/arduino/Arduino'), precompile_checks=True)
        require(type(value) is dict and set(value) == {*expected, 'file_sha256'} and
                all(value[name] == item for name, item in expected.items()) and
                type(value['compiler_returncode']) is int and value['precompile_checks'] is True,
                'Checked receipt identity changed')
        policy = self.policy()
        pins = policy.installed_pins('/home/arduino/.arduino15')
        outputs = [build_path + '/app.ino' + suffix for suffix in ('.elf', '_debug.elf', '_temp.elf')]
        outputs.append(artifacts + '/app.ino.elf-zsk.bin')
        hashes = value['file_sha256']
        require(type(hashes) is dict and set(hashes) == {*pins, *outputs}, 'Receipt file set changed')
        require(all(type(digest) is str and re.fullmatch('[0-9a-f]{64}', digest) and digest != sha(b'')
                    for digest in hashes.values()), 'Invalid receipt file digest')
        require(all(hashes[name] == digest for name, digest in pins.items()), 'Receipt installed pin changed')
        command = ['arduino-cli', 'compile', '--json', '--fqbn', self.fqbn,
                   '--build-path', build_path, '--output-dir', artifacts,
                   '--build-property', 'compiler.cpp.extra_flags=' + self.flags,
                   '--build-property', 'compiler.c.extra_flags=' + self.flags,
                   '--build-property', 'build.library_discovery_phase_flag=' + policy.DISCOVERY, self.sketch]
        require(decode(read((self.root / receipt).with_name('command.json'))) == command,
                'Checked compile command changed')
        return receipt

    def build(self):
        self.local()
        self.inventory()
        self.artifacts = self.board.compile_app(BOARD, SOURCE, self.sketch, self.remote_root,
            self.fqbn, self.flags, self.startup, project='app.ino', command_runner=self.command_runner)
        require(self.compiler_calls == self.query_calls == 1, 'Missing checked compile/query')
        self.receipt = self.verify_receipt(self.artifacts)

    def final_policy(self, overrides=False):
        require(self.remote_owned and self.source_available, 'Source ownership unconfirmed')
        policy = self.policy()
        if overrides:
            policy.check_overrides(self.command_runner, BOARD, '/home/arduino/.arduino15',
                                   '/home/arduino/Arduino', self.sketch)
        else:
            policy.verify_hashes(self.command_runner, BOARD, policy.installed_pins('/home/arduino/.arduino15'))

    def closing(self, report, primary):
        checks = [('local', self.local), ('identity', self.inventory)]
        checks.extend((name, lambda name=name: self.prerequisite(name)) for name in BASELINES)
        if self.source_attempted:
            checks.append(('remote_sources', self.sources))
        if self.source_available:
            checks.extend([('installed_pins', self.final_policy),
                           ('overrides', lambda: self.final_policy(overrides=True))])
        for name, operation in checks:
            try:
                operation()
                row = dict(name=name, status='PASS', error=None)
            except Exception as error:
                primary = primary or error
                row = dict(name=name, status='FAILED', error=error_value(error))
            report['final_checks'].append(row)
        return primary

    def finish(self, report, primary):
        report.update(status='FAILED' if primary else 'COMPILE_CHECKED',
                      first_error=error_value(primary) if primary else None,
                      compiler_calls=self.compiler_calls, query_calls=self.query_calls,
                      transport_calls=self.counter, artifacts=self.artifacts, receipt=self.receipt,
                      finished_utc=datetime.now(timezone.utc).isoformat())
        try:
            self.save('result.json', report)
        except Exception as error:
            primary = primary or error
            report.update(status='FAILED', first_error=error_value(primary))
            report['final_checks'].append(dict(name='result_write', status='FAILED', error=error_value(error)))
        if primary:
            primary.compile_outcome = report
            raise primary
        return report

    def run(self):
        self.check()
        require(sys.pycache_prefix == str(self.output / 'pycache'), 'Use isolated selected output/pycache prefix')
        self.prepare()
        report = dict(schema='current-app-compile-outcome-v1', profile=self.profile,
                      reviewed_head=self.reviewed_head, source_sha256=SOURCE, boot_id=BOOT,
                      started_utc=datetime.now(timezone.utc).isoformat(), final_checks=[])
        try:
            self.claim()
        except Exception as error:
            if self.claimed:
                return self.finish(report, error)
            raise
        primary = None
        try:
            self.inventory(initial=True)
            self.prerequisites()
            self.stage()
            self.build()
        except Exception as error:
            primary = error
        primary = self.closing(report, primary)
        return self.finish(report, primary)


def main(argv):
    action, profile, head = parse_request(argv)
    owner = CompileCurrent(profile, head)
    try:
        result = owner.check() if action == '--check-only' else owner.run()
    except Exception as error:
        print(json.dumps(getattr(error, 'compile_outcome', {'status': 'FAILED', 'first_error': error_value(error)}),
                         indent=2), file=sys.stderr)
        raise
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
