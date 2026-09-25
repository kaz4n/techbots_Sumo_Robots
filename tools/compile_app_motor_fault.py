# Compiles the fixed inhibited full-application static diagnostic once.
# Reuses checked execution while keeping fresh ownership separate from old scopes.
# Tested by independent D188 controlled cases before any reviewed native use.
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import types
import zlib


ROOT = Path(__file__).absolute().parents[1]
CALLER = 'tools/compile_app_motor_fault.py'
REMOTE_HELPER = 'tools/app_motor_fault_compile_remote.py'
CONTRACT = 'state/analysis/P7_app_motor_fault_compile_contract.md'
RAW = 'state/analysis/P7_app_motor_fault_compile_raw'
LEGACY = 'state/analysis/P7_current_app_compile_raw/compile_current_app.py'
ADAPTER = 'tools/app_motor_fault_static_policy.py'
OLD_RAW = 'state/analysis/P7_static_link_probe_raw/'
READER = OLD_RAW + 'static_remote.py'
EXTENSION = OLD_RAW + 'static_native_artifacts.py'
BASE_ARTIFACTS = OLD_RAW + 'static_artifacts.py'
COMMON = 'tools/app_build_policy.py'
EXECUTOR = 'state/analysis/P7_motor_fault_raw/compile_motor_fault.py'
SUPPORT = 'state/analysis/P7_static_startup_raw/capture_remote.py'
BASELINES = {'initialization': 'state/analysis/P7_static_startup_raw/cli_initialization_inventory.json',
             'builtins': 'state/analysis/P7_static_startup_raw/cli_builtin_files_inventory.json'}
HARD_PINS = {
    LEGACY: 'aed3fbf4db5c962761affd5a3e2e52b1002feaaefe4e44f9f34df6ec78ba5ede',
    ADAPTER: '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270',
    READER: '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8',
    BASE_ARTIFACTS: 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368',
    COMMON: 'adc7f42a3325381c3cf15122409dfe9d92db7ca187cb242e416fef356be667f8',
    OLD_RAW + 'static_policy.py': 'ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775',
    OLD_RAW + 'static_reference.json': '1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b',
    EXTENSION: 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0',
    EXECUTOR: '84efd00611b3a6a8129655005930ff58e555221f6bd8d88a23c7fa1c4381ac0d',
    SUPPORT: '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e',
    BASELINES['initialization']: 'aaa2c307b7ed1b8d7e00a737447a03a63a78cd4b7fb2145142b20e9501da1e62',
    BASELINES['builtins']: 'a364beb814b36b9c56328b54a9de5fa0f4ad80a67003d40c7cc994a1917ba2cb',
}
REQUIRED = {CALLER, REMOTE_HELPER, CONTRACT, 'tools/board_tool.py',
            'tools/app_build_commands.json', 'tools/app_build_pins.json', *HARD_PINS}
PROJECT = 'app_motor_fault.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1'
PARENT = '/home/arduino/sumox26_codex_build'
ATTEMPT = 'app-motor-fault-static01'
REMOTE = PARENT + '/' + ATTEMPT
DATA = '/home/arduino/.arduino15'
USER = '/home/arduino/Arduino'
LOADER_SHA = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
TLS_SHA = '68bb147615813666d528b9bd650e02fb8e240f0db841939e8460d7a52fd2ee70'
SUFFIX_LIMITS = {'.elf': 16777216, '_debug.elf': 16777216,
                 '_temp.elf': 16777216, '.bin': 786416,
                 '.bin-zsk.bin': 786432, '.elf-zsk.bin': 16777216, '.map': 16777216}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse_request(argv):
    require(type(argv) is list and all(type(item) is str for item in argv),
            'Expected an exact argument list')
    require(len(argv) == 3 and argv[0] in ('--check-only', '--execute') and
            argv[1] == '--reviewed-head' and re.fullmatch('[0-9a-f]{40}', argv[2]),
            'Expected --check-only|--execute --reviewed-head <40lowerhex>')
    return argv[0], argv[2]


def load_legacy(root):
    path = root / LEGACY
    for item in (path, *path.parents):
        info = item.lstat()
        expected = stat.S_ISREG if item == path else stat.S_ISDIR
        require(expected(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 1024,
                'Nonplain legacy caller path')
    before = path.lstat()
    require(0 < before.st_size <= 1048576, 'Legacy caller exceeds input bound')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(1048577)
        closed = os.fstat(stream.fileno())
    after = path.lstat()
    identity = lambda value: (value.st_dev, value.st_ino, value.st_mode, value.st_size,
                               value.st_mtime_ns, getattr(value, 'st_file_attributes', 0))
    require(identity(before) == identity(opened) == identity(closed) == identity(after) and
            before.st_ctime_ns == after.st_ctime_ns and opened.st_ctime_ns == closed.st_ctime_ns and
            len(raw) == before.st_size and len(raw) <= 1048576, 'Legacy caller changed while reading')
    require(sha(raw) == HARD_PINS[LEGACY], 'Legacy caller changed')
    module = types.ModuleType('_sumox_d188_private_legacy')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def directories(files):
    result = set()
    for name in files:
        for parent in PurePosixPath(name).parents:
            if str(parent) != '.':
                result.add(parent.as_posix())
    return result


def keys(value, expected, message):
    require(type(value) is dict and set(value) == set(expected), message)


def exact(value, expected):
    if type(value) is not type(expected):
        return False
    if type(expected) is dict:
        return value.keys() == expected.keys() and all(exact(value[name], item) for name, item in expected.items())
    if type(expected) is list:
        return len(value) == len(expected) and all(exact(a, b) for a, b in zip(value, expected))
    return value == expected


def checked_record(value, limit):
    keys(value, ('state', 'identity', 'sha256'), 'Invalid artifact record fields')
    keys(value['identity'], ('device', 'inode', 'bytes', 'mtime_ns', 'ctime_ns'),
         'Invalid artifact identity fields')
    require(value['state'] == 'regular' and all(type(item) is int and item >= 0
            for item in value['identity'].values()) and 0 < value['identity']['bytes'] <= limit,
            'Invalid artifact state, identity or size')
    require(type(value['sha256']) is str and re.fullmatch('[0-9a-f]{64}', value['sha256']) and
            value['sha256'] != sha(b''), 'Invalid artifact digest')


def checked_interval(value, start, end):
    keys(value, ('start', 'end', 'remaining'), 'Invalid layout interval fields')
    require(all(type(item) is int and item >= 0 for item in value.values()) and
            value['start'] == start and start <= value['end'] <= end and
            value['remaining'] == end - value['end'], 'Invalid layout interval')


def checked_native_layout(layout, records, aliases):
    keys(layout, ('status', 'entry', 'flash', 'ram', 'data_copy', 'bss_zero',
                 'sections', 'weak_undefined', 'artifacts', 'native_tls'), 'Invalid native layout fields')
    require(layout['status'] == 'STATIC_NATIVE_TLS_LAYOUT_PACKAGE_PASS' and
            type(layout['entry']) is int and layout['entry'] == 0x08100011, 'Invalid native layout identity')
    checked_interval(layout['flash'], 0x08100010, 0x081C0000)
    checked_interval(layout['ram'], 0x20013890, 0x20053890)
    expected = {old: {'bytes': records['build/' + new]['identity']['bytes'],
                     'sha256': records['build/' + new]['sha256']} for new, old in aliases.items()}
    require(exact(layout['artifacts'], expected), 'Native layout artifact identities differ')
    tls_values = {'_TLS_MODULE_BASE_': 8, '_rand_next': 8, 'z_tls_current': 16,
                  'errno': 20, '_strtok_last': 24, '_localtime_buf': 28}
    tls = dict(source_sha256=TLS_SHA, loader_sha256=LOADER_SHA,
        symbols=[dict(name=name, value=tls_values[name], size=0, bind=1, type=6,
                      other=0, section=65521) for name in sorted(tls_values)])
    require(exact(layout['native_tls'], tls), 'Native TLS layout differs')
    for name, fields in (('data_copy', ('source', 'destination', 'bytes')),
                         ('bss_zero', ('start', 'end', 'bytes'))):
        keys(layout[name], fields, 'Invalid initialization fields')
        require(all(type(item) is int and item >= 0 for item in layout[name].values()),
                'Invalid initialization values')
    require(type(layout['sections']) is list and 3 <= len(layout['sections']) <= 64,
            'Invalid section report')
    for row in layout['sections']:
        keys(row, ('name', 'type', 'flags', 'address', 'size', 'alignment', 'load_address'),
             'Invalid section fields')
        require(type(row['name']) is str and 0 < len(row['name']) <= 128 and
                all(type(row[name]) is int and row[name] >= 0 for name in
                    ('type', 'flags', 'address', 'size', 'alignment')) and
                (row['load_address'] is None or type(row['load_address']) is int and row['load_address'] >= 0),
                'Invalid section values')
    weak = layout['weak_undefined']
    require(type(weak) is list and len(weak) <= 4096 and
            all(type(item) is str and 0 < len(item) <= 4096 for item in weak) and
            weak == sorted(set(weak)), 'Invalid weak symbol report')


class CompileDiagnostic:
    def __init__(self, reviewed_head, *, root=ROOT):
        parse_request(['--check-only', '--reviewed-head', reviewed_head])
        self.root, self.reviewed_head = Path(root).absolute(), reviewed_head
        self.base = load_legacy(self.root)
        borrowed = ('git_state', 'load_board', 'prepare', 'save', 'transport',
                    'direct', 'preamble', 'inventory', 'prerequisite', 'prerequisites',
                    'command_runner', 'policy', 'final_policy')
        for name in borrowed:
            setattr(self, name, types.MethodType(getattr(self.base.CompileCurrent, name), self))
        self.output, self.inputs_path = self.root / RAW / 'native_static01', self.root / RAW / 'inputs_static.json'
        self.stage_attempt = ATTEMPT
        self.stage_owner = self.root / 'build/stage' / ATTEMPT
        self.stage_path = self.stage_owner / 'app_motor_fault'
        self.remote_root, self.remote = PARENT, REMOTE
        self.build_path, self.artifacts = REMOTE + '/build', REMOTE + '/artifacts'
        self.fqbn, self.flags, self.startup = FQBN, FLAGS, 'default'
        self.counter = self.query_calls = self.compiler_calls = 0
        self.claimed = self.remote_owned = self.source_attempted = self.source_available = False
        self.inputs_raw = self.inputs = self.code = self.stage_hashes = self.expected_stage = None
        self.boot = self.source_sha256 = self.sketch = None
        self.executor = self.board = self.receipt = self.artifact_receipt = None

    def source_names(self):
        pending = [self.root / name for name in ('src', 'bench/app_motor_fault', 'bench/motor_fault/src')]
        names, count = set(), 0
        while pending:
            folder = pending.pop()
            self.base.plain(folder, directory=True)
            for path in folder.iterdir():
                count += 1
                require(count <= 1024, 'Source entry bound exceeded')
                self.base.plain(path, directory=path.is_dir())
                if path.is_dir():
                    pending.append(path)
                else:
                    names.add(self.base.relative(path.relative_to(self.root).as_posix()))
                    require(len(names) <= 512, 'Source file bound exceeded')
        return names

    def source_mapping(self, code, names):
        mapped = {}
        for name in sorted(names):
            target = None
            if name.startswith('bench/app_motor_fault/'):
                relative = name[len('bench/app_motor_fault/'):]
                target = relative if relative != '.gitkeep' else None
            elif name == 'src/config.h' or name.startswith(('src/core/', 'src/hal/')):
                target = name
            elif name.startswith('src/app/') and not name.startswith('src/app/src/') and Path(name).suffix in (
                    '.c', '.cc', '.cpp', '.h', '.hpp'):
                target = name
            elif name in ('bench/motor_fault/src/motor_fault.h', 'bench/motor_fault/src/motor_fault.cpp'):
                target = 'src/' + Path(name).name
            if target is not None:
                require(target not in mapped, 'Stage source collision: ' + target)
                mapped[target] = code[name]
        require({PROJECT, 'src/motor_fault.h', 'src/motor_fault.cpp'} <= set(mapped), 'Missing diagnostic sources')
        digest = hashlib.sha256()
        for name in sorted(mapped):
            digest.update(name.encode() + b'\0')
            digest.update(mapped[name])
        return {name: sha(raw) for name, raw in mapped.items()}, digest.hexdigest()

    def admission(self):
        raw = self.base.read(self.inputs_path, 262144)
        require(self.inputs_raw is None or raw == self.inputs_raw, 'Input manifest changed')
        value = self.base.decode(raw)
        keys(value, ('schema', 'source_sha256', 'boot_id', 'files'), 'Invalid manifest fields')
        require(value['schema'] == 'app-motor-fault-static-inputs-v1' and
                type(value['source_sha256']) is str and re.fullmatch('[0-9a-f]{64}', value['source_sha256']) and
                type(value['boot_id']) is str and re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', value['boot_id']),
                'Invalid source or boot identity')
        names, code, total = self.source_names(), {}, 0
        pins = value['files']
        keys(pins, REQUIRED | names, 'Input filename set changed')
        for name, expected in pins.items():
            require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected), 'Invalid input digest')
            code[name] = self.base.read(self.root / self.base.relative(name))
            require(sha(code[name]) == expected, 'Pinned input changed: ' + name)
            total += len(code[name]) if name in names else 0
        require(total <= 4194304, 'Source byte bound exceeded')
        for name, expected in HARD_PINS.items():
            require(pins[name] == expected, 'Hard pin changed: ' + name)
        self.base.checked_wait(code[SUPPORT])
        mapped, source = self.source_mapping(code, names)
        require(source == value['source_sha256'], 'Staged source digest changed')
        self.inputs_raw, self.inputs, self.code = raw, value, code
        self.boot, self.source_sha256, self.expected_stage = value['boot_id'], source, mapped
        self.sketch = PARENT + '/' + source + '/app_motor_fault'
        self.base.BOOT = self.boot
        if self.executor is not None:
            require(self.executor['BOOT'] == self.boot, 'Executor boot changed')

    def local(self):
        self.base.CompileCurrent.local(self)
        if self.stage_hashes is not None:
            actual = {path.relative_to(self.stage_path).as_posix()
                      for path in self.stage_path.rglob('*') if path.is_dir()}
            require(actual == directories(self.expected_stage), 'Local stage directories changed')

    def check(self):
        self.local()
        require(not os.path.lexists(self.output) and not os.path.lexists(self.stage_owner),
                'Local output or stage owner already exists')
        self.base.plain(self.output.parent, directory=True)
        for path in (self.root / 'build', self.root / 'build/stage'):
            if os.path.lexists(path):
                self.base.plain(path, directory=True)
        require(shutil.disk_usage(self.root).free >= 134217728, 'Less than 128MiB local free space')
        return dict(schema='app-motor-fault-static-check-v1', reviewed_head=self.reviewed_head,
            source_sha256=self.source_sha256, boot_id=self.boot, project=PROJECT, fqbn=FQBN,
            flags=FLAGS, output=str(self.output), stage=str(self.stage_path), remote=self.remote, sketch=self.sketch)

    def claim(self):
        self.output.mkdir(mode=0o700)
        self.claimed = True
        self.save('intent.json', dict(schema='app-motor-fault-static-intent-v1',
            reviewed_head=self.reviewed_head, source_sha256=self.source_sha256, boot_id=self.boot,
            project=PROJECT, fqbn=FQBN, flags=FLAGS, inputs_sha256=sha(self.inputs_raw),
            stage=str(self.stage_path), remote=self.remote, sketch=self.sketch,
            started_utc=datetime.now(timezone.utc).isoformat()))

    def source_program(self):
        program = self.base.CompileCurrent.source_program(self)
        return program + 'expected_directories=' + repr(sorted(directories(self.expected_stage))) + '\n' + '''def checked_source_set():
 files=source_set()
 actual=sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_dir())
 if actual!=expected_directories:raise ValueError('Remote source directories differ')
 return files
'''

    def source_admission(self):
        self.source_attempted = True
        program = self.source_program() + 'expected=' + repr(self.stage_hashes) + '\n' + '''if os.path.lexists(root.parent):
 if root.parent.resolve()!=root.parent or not root.parent.is_dir():raise ValueError('Invalid source owner')
 if sorted(p.name for p in root.parent.iterdir())!=['app_motor_fault']:raise ValueError('Unexpected source owner entries')
 if checked_source_set()!=expected:raise ValueError('Existing source differs')
 reused=True
else:
 root.parent.mkdir(mode=0o700);root.mkdir();reused=False
 for name in expected:(root/name).parent.mkdir(parents=True,exist_ok=True)
print(json.dumps({'reused':reused}))
'''
        reply, _ = self.direct(program, 'source-admission')
        value = self.base.decode(reply.stdout)
        require(not reply.stderr and type(value) is dict and set(value) == {'reused'} and
                type(value['reused']) is bool, 'Invalid source admission reply')
        return value['reused']

    def sources(self):
        reply, _ = self.direct(self.source_program() + 'print(json.dumps(checked_source_set()))\n', 'source-set')
        require(not reply.stderr and self.base.decode(reply.stdout) == self.stage_hashes,
                'Remote source filename/hash set changed')

    def stage(self):
        self.local()
        require(not os.path.lexists(self.stage_owner), 'Local stage owner already exists')
        require(shutil.disk_usage(self.root).free >= 134217728, 'Less than 128MiB local free space')
        staged = self.board.stage('bench/app_motor_fault', attempt=ATTEMPT)
        require(staged == self.stage_path, 'Unexpected stage destination')
        self.stage_hashes = self.executor['files'](staged)
        require(self.stage_hashes == self.expected_stage and
                self.board.source_hash(staged) == self.source_sha256, 'Stage differs from reviewed source')
        actual_dirs = {path.relative_to(staged).as_posix() for path in staged.rglob('*') if path.is_dir()}
        require(actual_dirs == directories(self.expected_stage), 'Stage directories differ')
        self.local()
        self.save('staged_files.json', self.stage_hashes)
        program = self.preamble() + "Path(REMOTE).mkdir(mode=0o700)\n"
        program += "for name in ('commands','build','artifacts'):(Path(REMOTE)/name).mkdir()\nprint(json.dumps(identity))\n"
        reply, _ = self.direct(program, 'command-owner')
        require(not reply.stderr and self.base.decode(reply.stdout)['boot_id'] == self.boot,
                'Invalid command owner reply')
        self.remote_owned = True
        if not self.source_admission():
            for name in self.stage_hashes:
                self.inventory()
                self.transport(['push', str(self.stage_path / name), self.sketch + '/' + name], 60, 'push')
        self.sources()
        self.source_available = True

    def static_policy(self):
        self.local()
        return self.base.module_from(self.root, ADAPTER, self.code[ADAPTER])

    def compile_command(self):
        return ['arduino-cli', 'compile', '--json', '--fqbn', FQBN,
            '--build-path', self.build_path, '--output-dir', self.artifacts,
            '--build-property', 'compiler.cpp.extra_flags=' + FLAGS,
            '--build-property', 'compiler.c.extra_flags=' + FLAGS,
            '--build-property', 'build.library_discovery_phase_flag=' + self.policy().DISCOVERY, self.sketch]

    def capture(self, command, name):
        return self.board.capture_app_command(self.base.BOARD, command, self.output / 'compile', name,
                                               command_runner=self.command_runner)

    def preflight(self, command):
        common = self.policy()
        common.validate_cli(self.capture(['arduino-cli', 'version'], 'version').stdout)
        for name, expected in (('data', DATA), ('user', USER)):
            reply = self.capture(['arduino-cli', 'config', 'get', 'directories.' + name, '--json'], name + '_directory')
            require(common.resolved_directory(reply.stdout) == expected, 'Resolved directory differs: ' + name)
        reader = lambda board, argv, **kwargs: self.capture(argv, 'overrides')
        common.check_overrides(reader, self.base.BOARD, DATA, USER, self.sketch)
        reader = lambda board, argv, **kwargs: self.capture(argv, 'precompile_pins')
        common.verify_hashes(reader, self.base.BOARD, common.installed_pins(DATA))
        query = [*command[:-1], '--show-properties=expanded', command[-1]]
        reply = self.capture(query, 'properties')
        self.static_policy().validate_preflight(reply.stdout, build_path=self.build_path, data_dir=DATA)

    def build(self):
        self.local()
        self.inventory()
        (self.output / 'compile').mkdir()
        command = self.compile_command()
        self.preflight(command)
        reply = self.capture(command, 'compile')
        self.static_policy().validate_compile_result(reply.stdout, build_path=self.build_path, data_dir=DATA)
        require(self.compiler_calls == self.query_calls == 1, 'Missing checked compile/query')
        self.observe_artifacts()

    def artifact_program(self):
        sources = dict(helper=self.code[READER], adapter=self.code[ADAPTER],
                       extension=self.code[EXTENSION], base=self.code[BASE_ARTIFACTS])
        payload = dict(source=self.code[REMOTE_HELPER].decode('utf-8'),
            bundle={name: raw.decode('utf-8') for name, raw in sources.items()})
        raw = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode()
        require(len(raw) <= 262144, 'Artifact source payload exceeds bound')
        token = base64.b64encode(zlib.compress(raw, 9)).decode()
        program = self.preamble() + 'token=' + repr(token) + '\nexpected=' + repr(sha(raw)) + '\n'
        program += 'source_sha=' + repr(sha(self.code[REMOTE_HELPER])) + '\n'
        return program + '''import base64,zlib,types
packed=base64.b64decode(token,validate=True)
if base64.b64encode(packed).decode()!=token:raise ValueError('Noncanonical source token')
decoder=zlib.decompressobj();raw=decoder.decompress(packed,262145)
if len(raw)>262144 or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:raise ValueError('Invalid compressed sources')
if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Source payload changed')
payload=json.loads(raw);source=payload['source'].encode('utf-8')
if hashlib.sha256(source).hexdigest()!=source_sha:raise ValueError('Artifact helper changed')
module=types.ModuleType('_sumox_d188_observation')
exec(compile(source,'<checked-d188-artifacts>','exec'),module.__dict__)
bundle={name:value.encode('utf-8') for name,value in payload['bundle'].items()}
result=module.inspect_artifacts(REMOTE+'/build',REMOTE+'/artifacts',bundle)
text=json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False)
if len(text.encode())>1048576:raise ValueError('Artifact response exceeds bound')
print(text)
'''

    def validate_artifact_reply(self, text):
        require(type(text) is str and len(text.encode()) <= 1048576, 'Invalid artifact response text')
        value = self.base.decode(text)
        keys(value, ('schema', 'status', 'build_path', 'artifacts_path', 'files', 'loader',
                     'tls_source', 'layout', 'postchecks', 'first_error'), 'Invalid artifact reply fields')
        require(value['schema'] == 'app-motor-fault-static-artifacts-v1' and
                value['status'] == 'ARTIFACTS_CHECKED' and value['first_error'] is None and
                value['build_path'] == self.build_path and value['artifacts_path'] == self.artifacts,
                'Artifact observation failed or paths differ')
        limits = {'build/' + PROJECT + suffix: limit for suffix, limit in SUFFIX_LIMITS.items()}
        limits['artifacts/' + PROJECT + '.bin-zsk.bin'] = 786432
        keys(value['files'], limits, 'Artifact file set differs')
        for name, limit in limits.items():
            checked_record(value['files'][name], limit)
        for name, limit, digest in (('loader', 16777216, LOADER_SHA), ('tls_source', 65536, TLS_SHA)):
            checked_record(value[name], limit)
            require(value[name]['sha256'] == digest, 'Installed artifact hash differs')
        flat = [value['files'][group + '/' + PROJECT + '.bin-zsk.bin'] for group in ('build', 'artifacts')]
        require(flat[0]['sha256'] == flat[1]['sha256'] and
                flat[0]['identity']['bytes'] == flat[1]['identity']['bytes'], 'Exported flat package differs')
        self.validate_layout(value['layout'], value['files'])
        require(value['postchecks'] == [dict(name=name, status='PASS', error=None)
                for name in ('loader', 'tls_source', 'files')], 'Artifact postchecks failed or differ')
        return value

    def validate_layout(self, value, files):
        keys(value, ('status', 'project', 'fqbn', 'flags', 'artifact_aliases',
                     'artifact_sha256', 'validator_report'), 'Invalid diagnostic layout fields')
        require(value['status'] == 'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS' and
                value['project'] == PROJECT and value['fqbn'] == FQBN and value['flags'] == FLAGS,
                'Diagnostic layout profile differs')
        aliases = {PROJECT + suffix: 'app.ino' + suffix for suffix in SUFFIX_LIMITS}
        expected = {name: files['build/' + name]['sha256'] for name in aliases}
        require(value['artifact_aliases'] == aliases and value['artifact_sha256'] == expected,
                'Diagnostic layout artifact identities differ')
        checked_native_layout(value['validator_report'], files, aliases)

    def observe_artifacts(self, final=False):
        reply, _ = self.direct(self.artifact_program(), 'artifacts-final' if final else 'artifacts')
        require(not reply.stderr, 'Artifact observation stderr')
        value = self.validate_artifact_reply(reply.stdout.decode() if isinstance(reply.stdout, bytes) else reply.stdout)
        if final:
            require(value == self.artifact_receipt, 'Artifact packet changed after compilation')
        else:
            self.artifact_receipt = value
            self.save('artifacts.json', value)
            self.receipt = str(self.output / 'artifacts.json')
        return value

    def closing(self, report, primary):
        primary = self.base.CompileCurrent.closing(self, report, primary)
        if self.artifact_receipt is not None:
            try:
                self.observe_artifacts(final=True)
                row = dict(name='artifacts', status='PASS', error=None)
            except Exception as error:
                primary = primary or error
                row = dict(name='artifacts', status='FAILED', error=self.base.error_value(error))
            report['final_checks'].append(row)
        return primary

    def finish(self, report, primary):
        if primary is None and (self.query_calls != 1 or self.compiler_calls != 1 or self.artifact_receipt is None):
            primary = ValueError('Missing compile/query or checked artifact receipt')
        return self.base.CompileCurrent.finish(self, report, primary)

    def run(self):
        self.check()
        require(sys.pycache_prefix == str(self.output / 'pycache'), 'Use isolated selected output/pycache prefix')
        self.prepare()
        report = dict(schema='app-motor-fault-static-compile-outcome-v1',
            project=PROJECT, fqbn=FQBN, flags=FLAGS, reviewed_head=self.reviewed_head,
            source_sha256=self.source_sha256, boot_id=self.boot,
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
    action, head = parse_request(argv)
    owner = CompileDiagnostic(head)
    try:
        result = owner.check() if action == '--check-only' else owner.run()
    except Exception as error:
        value = getattr(error, 'compile_outcome', {'status': 'FAILED', 'first_error': owner.base.error_value(error)})
        print(json.dumps(value, indent=2), file=sys.stderr)
        raise
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
