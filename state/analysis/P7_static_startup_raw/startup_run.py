# Coordinates one reviewed inert upload and a separate conditional passive capture.
# Keeps transport uncertainty, durable attempts and collected evidence distinct.
# Frozen host callback and report fixtures exercise this launcher before native use.
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
import sys
import types
import zlib

SOURCE = 'fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2'
RUN_ID = 'static-fcddbd8e-run01'
ARTIFACT_RUN = 'f0220228320c4b2aa20c3e5e8264c813'
BOARD = '2629958581'
ROOT_TEXT = r'C:\Users\narut\OneDrive\Desktop\Project\techbots_Sumo_Robots'
RAW = 'state/analysis/P7_static_startup_raw/'
PROBE_RAW = 'state/analysis/P7_static_link_probe_raw/'
SCOPE = RAW + 'native_run01_scope.json'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
ADB_SHA = 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'
PARSER = ('/home/arduino/sumox26-capture-tools/app-default-'
          'beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1/p0_capture.py')
PARSER_SHA = '885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c'
SCOPE_FILES = (RAW + 'startup_run.py', RAW + 'test_startup_run.py',
               'state/analysis/P7_static_startup_launcher_contract.md',
               'state/reviews/P7_static_startup_launcher_design_review.md',
               'state/reviews/P7_static_startup_launcher_review.md')
DEPENDENCIES = {
    PROBE_RAW + 'run_static_probe.py': '983e86d7eb68f437c50b4b790e96ca4520e092abe53e4d29e8ffe1a97502b208',
    PROBE_RAW + 'static_remote.py': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8',
    RAW + 'capture_remote.py': '1aa602d03745b6d5654c7c7dca9c6f76ca99af6109b58b5c5c591cdf561a4983',
    RAW + 'upload_remote.py': '81668c798fdb53d9f81083977f098d36f873003041e55720a6170b9c7cf2cf08',
    RAW + 'static_capture.py': 'b7ab979d019814c7d66258346891457e7f09e7698896d8dbf00469f3c58e24fc',
    RAW + 'capture_bindings.json': 'c2c87df6165556602a5a79472caedf0755c070b2e2f3e0b834f17ab0de5c0d32',
    RAW + 'upload_bindings.json': 'a31bca78bb619271e63a321173a68fca072e48bb22111ee20fc9f8c20d5e18fc',
    RAW + 'cli_initialization_inventory.json': 'aaa2c307b7ed1b8d7e00a737447a03a63a78cd4b7fb2145142b20e9501da1e62',
    RAW + 'cli_builtin_files_inventory.json': 'a364beb814b36b9c56328b54a9de5fa0f4ad80a67003d40c7cc994a1917ba2cb',
    PROBE_RAW + 'native_actual/result.json': '806a040d57a791e350b3d10a6bc59967cda67b031169caa3a53ef46aaf0d824d',
    PROBE_RAW + 'native_abi/result.json': '797c84f4cd12266a963802a50d16923f6243666ae6e8151f748fec7b10a10676',
    PROBE_RAW + 'native_init/result.json': '835c427707fa4fbc7c700904773fcd5061bfd8f84bc6d97c1b8cfbfbcd5e5c5f'}
RECEIPTS = {
    '0001': '534da2e8de0d846d850288c956f3c5a51b13f641b3329c6475dc5857930f32a7',
    '0009': '3f57a292649a0d20ddf88daf3f80a8b3d75a90e18460f3c7208c1eb17c6b45d4',
    '0017': '3c8cc9df2256be9967dd71b1afa3ec22215dbfc92cdcd910823efc4eeb78d6df',
    '0021': 'c44e85bcb22dcb69c405b1bddeea74f7c30e4c9e3f1444370995f806162e3127'}
CHECKS = ('local', 'packet', 'installed', 'prerequisites')
OPERATIONS = ('admit', 'claim', *CHECKS, 'intent', 'upload', 'capture', 'finish')
REPORT_COMMON = ('schema', 'run_id', 'source_sha256', 'status', 'started_utc',
                 'finished_utc', 'started_monotonic', 'finished_monotonic',
                 'first_error', 'postcheck_errors')
BOOTSTRAP = '''import base64,hashlib,json,os,sys,types,zlib
def main():
 if len(sys.argv)!=4 or not sys.dont_write_bytecode:raise ValueError('Wrong bootstrap arguments')
 action,expected,token=sys.argv[1:]
 if action not in ('upload','capture'):raise ValueError('Wrong fixed action')
 packed=base64.b64decode(token,validate=True)
 if base64.b64encode(packed).decode('ascii')!=token:raise ValueError('Noncanonical payload')
 d=zlib.decompressobj();raw=d.decompress(packed,196609)
 if len(raw)>196608 or not d.eof or d.unused_data or d.unconsumed_tail:raise ValueError('Payload framing')
 if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Payload hash')
 value=json.loads(raw);sources=value['sources'];modules={}
 for name,source in sources.items():
  if hashlib.sha256(source.encode('utf-8')).hexdigest()!=value['hashes'][name]:raise ValueError('Module hash')
 for name,source in sources.items():
  m=types.ModuleType('fixed_startup_'+name);m.__file__='/__sumox__/'+name+'.py'
  exec(compile(source,m.__file__,'exec'),m.__dict__);modules[name]=m
 h,s=modules['helper'],modules['support']
 bindings=json.loads(value['bindings'])
 if action=='upload':
  u=modules['upload'];u.BINDINGS=bindings;result=u.upload(h,s)
 else:
  path=value['parser_path'];fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
  try:parser=h.logical_read(fd,path,18880)
  finally:os.close(fd)
  if len(parser)!=18880 or hashlib.sha256(parser).hexdigest()!=value['parser_sha256']:raise ValueError('Loader parser drift')
  p=types.ModuleType('fixed_startup_loader');p.__file__=path
  exec(compile(parser,path,'exec'),p.__dict__)
  s.BINDINGS=bindings;result=s.collect(h,modules['decoder'],p.loader_image)
 print(s.json_bytes(result).decode('utf-8'),end='')
if __name__=='__main__':main()
'''


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected) and
            all(type(name) is str for name in value), 'Unexpected object fields')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    value = {}
    for name, item in pairs:
        require(name not in value, 'Duplicate JSON key')
        value[name] = item
    return value


def decode(raw):
    value = json.loads(raw, object_pairs_hook=unique)
    canonical(value)
    return value


def error_record(error):
    return {'type': type(error).__name__, 'message': str(error)}


def finite(value):
    require(type(value) in (int, float) and math.isfinite(value), 'Invalid monotonic value')
    return value


def report_identity(report, schema, status):
    for name, expected in (('schema', schema), ('run_id', RUN_ID),
                           ('source_sha256', SOURCE), ('status', status)):
        require(type(report[name]) is str and report[name] == expected,
                'Wrong report ' + name)
    require(report['first_error'] is None and type(report['postcheck_errors']) is list and
            not report['postcheck_errors'], 'Report contains failures')
    for name in ('started_utc', 'finished_utc'):
        require(type(report[name]) is str and bool(report[name]), 'Missing report timestamp')
    require(finite(report['finished_monotonic']) >= finite(report['started_monotonic']),
            'Reversed report timestamps')


def check_upload(report):
    keys(report, (*REPORT_COMMON, 'attempts', 'subprocess', 'stdout', 'stderr'))
    report_identity(report, 'static-upload-result-v1', 'UPLOADED')
    require(type(report['attempts']) is int and report['attempts'] == 1,
            'Upload attempt count differs')
    value = report['subprocess']
    keys(value, ('returncode', 'timed_out', 'reaped'))
    require(type(value['returncode']) is int and value['returncode'] == 0 and
            value['timed_out'] is False and value['reaped'] is True,
            'Upload process outcome is not known successful')
    require(type(report['stdout']) is str and type(report['stderr']) is str,
            'Upload streams are incomplete')


def read_plan():
    plan = []
    for label, address, size in (('before.loader', 0x08000000, 263680),
                                 ('before.sketch', 0x08100000, 93096)):
        plan.extend((label + '.' + str(i), address + offset, min(65536, size - offset))
                    for i, offset in enumerate(range(0, size, 65536)))
    plan.extend((('first.runtime', 0x2003bc98, 28), ('first.transaction', 0x2003b2b0, 24),
                 ('second.runtime', 0x2003bc98, 28), ('second.transaction', 0x2003b2b0, 24)))
    for label, address, size in (('after.sketch', 0x08100000, 93096),
                                 ('after.loader', 0x08000000, 263680)):
        plan.extend((label + '.' + str(i), address + offset, min(65536, size - offset))
                    for i, offset in enumerate(range(0, size, 65536)))
    return plan


def check_analysis(value):
    keys(value, ('flash', 'observation', 'runtime', 'transaction', 'epoch_delta', 'errors'))
    keys(value['flash'], ('before_loader', 'before_sketch', 'after_loader', 'after_sketch'))
    require(all(type(item) is bool for item in value['flash'].values()), 'Malformed flash flags')
    require(type(value['observation']) is str and value['observation'] in
            ('FLASH_MISMATCH', 'MALFORMED_SAMPLES', 'SAMPLED_FAULT',
             'RUNNING_COUNTER_ADVANCED', 'NO_RUNNING_PROGRESS'), 'Malformed observation')
    count = 0 if value['observation'] == 'FLASH_MISMATCH' else 2
    for name in ('runtime', 'transaction'):
        require(type(value[name]) is list and len(value[name]) == count and
                all(type(item) is dict for item in value[name]), 'Malformed analysis samples')
    delta = value['epoch_delta']
    require(delta is None or (type(delta) is int and 0 <= delta <= 0xffffffff), 'Malformed delta')
    require(type(value['errors']) is list and all(type(item) is str for item in value['errors']),
            'Malformed analysis errors')
    canonical(value)


def check_capture(report):
    keys(report, (*REPORT_COMMON, 'counts', 'wait', 'reads', 'analysis'))
    report_identity(report, 'static-capture-result-v1', 'COLLECTED')
    expected = {'commands': 18, 'reads': 18, 'requested_bytes': 713656}
    keys(report['counts'], expected)
    require(all(type(report['counts'][name]) is int and report['counts'][name] == value
                for name, value in expected.items()), 'Incomplete capture counts')
    require(type(report['reads']) is list and len(report['reads']) == 18, 'Incomplete read records')
    for index, (record, item) in enumerate(zip(report['reads'], read_plan())):
        name, address, size = item
        keys(record, ('name', 'address', 'bytes', 'sha256', 'file'))
        require(type(record['name']) is str and record['name'] == name and
                type(record['address']) is int and record['address'] == address and
                type(record['bytes']) is int and record['bytes'] == size and
                type(record['file']) is str and record['file'] == f'{index:02d}-{name}.bin',
                'Capture read identity differs')
        require(type(record['sha256']) is str and re.fullmatch('[0-9a-f]{64}', record['sha256']),
                'Malformed read hash')
    wait = report['wait']
    keys(wait, ('requested_seconds', 'before', 'after'))
    require(type(wait['requested_seconds']) is int and wait['requested_seconds'] == 2 and
            finite(wait['after']) - finite(wait['before']) >= 2, 'Invalid sample separation')
    require(report['started_monotonic'] <= wait['before'] <= wait['after'] <=
            report['finished_monotonic'], 'Wait outside collection interval')
    check_analysis(report['analysis'])


def command_units(argv):
    line = subprocess.list2cmdline([ADB, '-s', BOARD, 'shell', '-T', shlex.join(argv)])
    return len(line.encode('utf-16-le')) // 2 + 1


def build_command(action, payload):
    require(type(action) is str and action in ('upload', 'capture'), 'Wrong startup action')
    require(type(payload) is bytes and 0 < len(payload) <= 196608, 'Invalid payload bytes')
    token = base64.b64encode(zlib.compress(payload, 9)).decode('ascii')
    argv = ['python3', '-I', '-B', '-c', BOOTSTRAP, action, sha(payload), token]
    require(command_units(argv) <= 30000, 'Windows command limit exceeded')
    return argv


def orchestrate(operations):
    keys(operations, OPERATIONS)
    require(all(callable(operation) for operation in operations.values()), 'Noncallable operation')
    operations['admit']()
    operations['claim']()
    result = {'status': 'FAILED', 'upload': None, 'capture': None, 'first_error': None,
              'postcheck_errors': [], 'upload_attempts': 0, 'capture_attempts': 0}
    try:
        for action, check in (('upload', check_upload), ('capture', check_capture)):
            for name in CHECKS:
                operations[name]()
            operations['intent'](action, result['upload'] if action == 'capture' else None)
            result[action + '_attempts'] += 1
            result[action] = operations[action]()
            check(result[action])
    except Exception as error:
        result['first_error'] = error_record(error)
    for name in CHECKS:
        try:
            operations[name]()
        except Exception as error:
            result['first_error'] = result['first_error'] or error_record(error)
            result['postcheck_errors'].append({'check': name, **error_record(error)})
    if result['first_error'] is None and result['capture'] is not None:
        result['status'] = 'COMPLETED'
    operations['finish'](result)
    return result


def load_module(name, raw, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def safe_path(path, directory=False):
    require(path.is_absolute() and path == path.resolve(strict=True), 'Noncanonical local path')
    for item in (path, *path.parents):
        info = item.lstat()
        require(not stat.S_ISLNK(info.st_mode) and
                not getattr(info, 'st_file_attributes', 0) & 1024, 'Linked local path')
    require((stat.S_ISDIR if directory else stat.S_ISREG)(path.stat().st_mode), 'Wrong local path type')


def pinned_file(root, name, expected):
    path = root / name
    safe_path(path)
    raw = path.read_bytes()
    require(sha(raw) == expected, 'Pinned local file changed: ' + name)
    return raw


def projection(value):
    if type(value) is dict:
        return {name: projection(item) for name, item in value.items()
                if name not in ('mtime_ns', 'ctime_ns')}
    if type(value) is list:
        items = [projection(item) for item in value]
        return sorted(items, key=canonical) if all(type(item) is dict for item in items) else items
    return value


class NativeRun:
    def __init__(self, reviewed_head):
        self.reviewed_head = reviewed_head
        self.root = Path(__file__).resolve().parents[3]
        self.output = self.root / RAW / 'native_run01'
        self.runner, self.probe = None, None
        self.git_checks, self.prerequisite_errors, self.local_errors = [], [], []
        self.intent_actions, self.dispatched_actions = set(), set()

    def git(self, *args):
        argv = ['git', '-C', str(self.root), *args]
        result = subprocess.run(argv, capture_output=True, timeout=10, check=False,
                                stdin=subprocess.DEVNULL)
        self.git_checks.append({'argv': argv, 'returncode': result.returncode,
                                'stdout': result.stdout.decode('utf-8', errors='replace'),
                                'stderr': result.stderr.decode('utf-8', errors='replace')})
        require(result.returncode == 0, 'Local Git check failed')
        return result.stdout

    def head(self):
        observed = self.git('rev-parse', 'HEAD').decode('ascii').strip()
        require(observed == self.reviewed_head, 'Reviewed HEAD changed')
        require(not self.git('status', '--porcelain', '--untracked-files=no').strip(),
                'Tracked files are not clean')
        require(self.git('show', self.reviewed_head + ':' + SCOPE) == self.scope_raw,
                'Run scope is not identical to its committed bytes')

    def check_adb(self):
        safe_path(Path(ADB))
        require(sha(Path(ADB).read_bytes()) == ADB_SHA, 'Pinned ADB changed')
        require(os.environ.get('SUMO_TRANSPORT') == 'adb' and
                os.environ.get('SUMO_ADB_SERIAL') == BOARD and
                os.environ.get('SUMO_ADB_EXECUTABLE') == ADB, 'Transport identity changed')

    def check_scope(self):
        safe_path(self.root / SCOPE)
        require((self.root / SCOPE).read_bytes() == self.scope_raw, 'Run scope changed')

    def local(self):
        checks = [('head', self.head), ('scope', self.check_scope), ('adb', self.check_adb)]
        for name, digest in {**self.scope['files'], **self.fixed_pins}.items():
            checks.append((name, lambda name=name, digest=digest: pinned_file(self.root, name, digest)))
        if self.runner is not None:
            checks.append(('runner_inputs', self.runner.verify_inputs))
        if self.probe is not None:
            checks.append(('working_and_staged_source', self.probe.local_stage))
        first = None
        for name, operation in checks:
            try:
                operation()
            except Exception as error:
                first = first or error
                self.local_errors.append({'check': name, **error_record(error)})
        if first is not None:
            raise first

    def load_scope(self):
        path = self.root / SCOPE
        safe_path(path)
        self.scope_raw = path.read_bytes()
        self.scope = decode(self.scope_raw)
        keys(self.scope, ('schema', 'run_id', 'board', 'source_sha256', 'files'))
        for name, expected in (('schema', 'static-startup-run-scope-v1'), ('run_id', RUN_ID),
                               ('board', BOARD), ('source_sha256', SOURCE)):
            require(type(self.scope[name]) is str and self.scope[name] == expected, 'Wrong run scope')
        keys(self.scope['files'], SCOPE_FILES)
        for digest in self.scope['files'].values():
            require(type(digest) is str and re.fullmatch('[0-9a-f]{64}', digest), 'Invalid scope hash')

    def load_probe(self):
        name = PROBE_RAW + 'run_static_probe.py'
        self.runner = load_module('fixed_startup_runner', self.fixed_bytes[name], self.root / name)
        r = self.runner
        inputs = r.verify_inputs()
        self.probe = r.Probe(ARTIFACT_RUN, self.output, self.transport, inputs)
        old = {}
        for number in ('0001', '0009', '0021'):
            path = PROBE_RAW + 'runs/' + ARTIFACT_RUN + '/' + number + '.json'
            old[number] = r.decode(r.decode(self.fixed_bytes[path])['stdout'])['data']
        self.probe.check_inventory(old['0001'])
        self.probe.check_claim(old['0009']['claim'])
        self.probe.claim = old['0009']['claim']
        r.checked_files(old['0021']['files'])
        self.probe.check_claim(old['0021']['claim'])
        self.probe.files = old['0021']['files']

    def payload(self, action):
        names = {'helper': PROBE_RAW + 'static_remote.py', 'support': RAW + 'capture_remote.py'}
        names['upload' if action == 'upload' else 'decoder'] = RAW + (
            'upload_remote.py' if action == 'upload' else 'static_capture.py')
        value = {'sources': {key: self.fixed_bytes[name].decode('utf-8') for key, name in names.items()},
                 'hashes': {key: self.fixed_pins[name] for key, name in names.items()},
                 'bindings': self.fixed_bytes[RAW + action + '_bindings.json'].decode('utf-8')}
        if action == 'capture':
            value.update(parser_path=PARSER, parser_sha256=PARSER_SHA)
        return canonical(value)

    def prepare_commands(self):
        self.commands = {action: build_command(action, self.payload(action))
                         for action in ('upload', 'capture')}
        self.prerequisite_receipts = []
        for name in ('cli_initialization_inventory.json', 'cli_builtin_files_inventory.json'):
            receipt = decode(self.fixed_bytes[RAW + name])
            require(receipt['returncode'] == 0 and receipt['stderr'] == '', 'Invalid F166 baseline')
            require(decode(receipt['stdout'])['status'] == 'COLLECTED', 'Failed F166 baseline')
            self.prerequisite_receipts.append(receipt)
        p, r = self.probe, self.runner
        packet = ['python3', '-I', '-B', '-c', p.boot, p.helper_encoded, 'postcheck',
                  ARTIFACT_RUN, p.claim_token(), r.encoded(p.stage_raw, True)]
        self.allowed = {(tuple(packet), 90), (tuple(['sha256sum', '--', *p.pins]), 60)}
        self.allowed.update((tuple(item['argv']), 60) for item in self.prerequisite_receipts)
        self.allowed.update((tuple(self.commands[action]), timeout)
                            for action, timeout in (('upload', 195), ('capture', 630)))
        require(len(self.allowed) == 6, 'Unexpected command allowlist')
        for argv, unused in self.allowed:
            require(command_units(argv) <= 30000, 'Windows command limit exceeded')

    def admit(self):
        require(sys.dont_write_bytecode, 'Python -B required')
        require(type(self.reviewed_head) is str and re.fullmatch('[0-9a-f]{40}', self.reviewed_head),
                'Invalid reviewed HEAD')
        require(str(self.root).casefold() == ROOT_TEXT.casefold() and Path.cwd().resolve() == self.root,
                'Wrong repository')
        safe_path(self.output.parent, directory=True)
        require(not os.path.lexists(self.output), 'Host attempt already consumed')
        self.load_scope()
        self.fixed_pins = dict(DEPENDENCIES)
        self.fixed_pins.update({PROBE_RAW + 'runs/' + ARTIFACT_RUN + '/' + number + '.json': digest
                                for number, digest in RECEIPTS.items()})
        self.fixed_bytes = {name: pinned_file(self.root, name, digest)
                            for name, digest in self.fixed_pins.items()}
        os.environ.update(SUMO_TRANSPORT='adb', SUMO_ADB_SERIAL=BOARD, SUMO_ADB_EXECUTABLE=ADB)
        self.local()
        self.load_probe()
        self.prepare_commands()
        self.local()

    def check_output(self):
        safe_path(self.output, directory=True)
        current = self.output.stat()
        require((current.st_dev, current.st_ino) == self.output_identity, 'Local output replaced')

    def write(self, name, value):
        self.check_output()
        with (self.output / name).open('xb') as stream:
            stream.write(canonical(value) + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
        self.check_output()

    def command_identity(self, action):
        return {'argv_sha256': sha(canonical(self.commands[action])),
                'command_utf16_units': command_units(self.commands[action]),
                'timeout': 195 if action == 'upload' else 630}

    def identity_record(self):
        return {'run_id': RUN_ID, 'board': BOARD, 'source_sha256': SOURCE,
                'reviewed_head': self.reviewed_head, 'scope_sha256': sha(self.scope_raw),
                'artifact_run_id': ARTIFACT_RUN, 'claim': self.probe.claim, 'files': self.probe.files}

    def claim(self):
        self.output.mkdir(mode=0o700)
        info = self.output.stat()
        self.output_identity = (info.st_dev, info.st_ino)
        self.write('inputs.json', {**self.identity_record(), 'scope_files': self.scope['files'],
                   'dependency_pins': self.fixed_pins, 'runner_pins': self.runner.PINS,
                   'commands': {action: self.command_identity(action) for action in self.commands},
                   'remote_evidence': {action: decode(self.fixed_bytes[RAW + action + '_bindings.json'])['output']
                                       for action in self.commands}})

    def transport(self, board, argv, *, capture=True, timeout=60):
        require(board == BOARD and capture is True and (tuple(argv), timeout) in self.allowed,
                'Command is outside the fixed startup allowlist')
        self.check_adb()
        self.check_output()
        if any(argv == command for command in self.commands.values()):
            self.local()
        return self.probe.board.remote(board, argv, capture=True, timeout=timeout)

    def packet(self):
        self.probe.remote_postcheck()

    def installed(self):
        self.probe.installed_pins()

    def prerequisites(self):
        first = None
        for index, receipt in enumerate(self.prerequisite_receipts):
            try:
                self.probe.phase = 'cli_prerequisites_' + str(index)
                reply = self.probe.dispatch(BOARD, receipt['argv'], capture=True, timeout=60)
                require(reply.stderr == '' and len(reply.stdout.encode('utf-8')) <= 1048576,
                        'Invalid prerequisite reply')
                value = decode(reply.stdout)
                require(value['status'] == 'COLLECTED' and value['identity'] == self.probe.first_identity,
                        'Prerequisite identity/status changed')
                require(projection(value) == projection(decode(receipt['stdout'])),
                        'CLI initialization prerequisites changed')
            except Exception as error:
                first = first or error
                self.prerequisite_errors.append({'check': str(index), **error_record(error)})
        if first is not None:
            raise first

    def intent(self, action, upload_report):
        require(action not in self.intent_actions and action in self.commands, 'Repeated action intent')
        self.local()
        if action == 'capture':
            check_upload(upload_report)
        else:
            require(upload_report is None, 'Unexpected upload predecessor')
        self.write(action + '_attempt.json', {**self.identity_record(), 'action': action,
                   'command': self.command_identity(action),
                   'created_utc': datetime.now(timezone.utc).isoformat(),
                   'upload_report_sha256': sha(canonical(upload_report)) if action == 'capture' else None})
        self.intent_actions.add(action)

    def action(self, name):
        require(name in self.intent_actions and name not in self.dispatched_actions,
                'Unclaimed or repeated startup dispatch')
        self.dispatched_actions.add(name)
        self.probe.phase = name
        reply = self.probe.dispatch(BOARD, self.commands[name], capture=True,
                                    timeout=195 if name == 'upload' else 630)
        limit = 16777216 if name == 'upload' else 1048576
        require(reply.stderr == '' and len(reply.stdout.encode('utf-8')) <= limit,
                'Invalid startup transport reply')
        return decode(reply.stdout)

    def finish(self, result):
        require(self.probe.query_attempts == self.probe.compile_attempts == 0, 'Unexpected compiler action')
        if result['status'] == 'COMPLETED':
            require(self.probe.sequence == 14, 'Unexpected successful command count')
        for index in range(1, self.probe.sequence + 1):
            path = self.output / f'{index:04d}.json'
            safe_path(path)
            with path.open('r+b') as stream:
                stream.flush()
                os.fsync(stream.fileno())
        self.write('final_checks.json', {'git': self.git_checks, 'local': self.local_errors,
                   'prerequisites': self.prerequisite_errors,
                   'commands': self.probe.sequence, 'query_attempts': self.probe.query_attempts,
                   'compile_attempts': self.probe.compile_attempts})
        self.write('result.json', result)

    def operations(self):
        return {'admit': self.admit, 'claim': self.claim, 'local': self.local,
                'packet': self.packet, 'installed': self.installed, 'prerequisites': self.prerequisites,
                'intent': self.intent, 'upload': lambda: self.action('upload'),
                'capture': lambda: self.action('capture'), 'finish': self.finish}


def native_run(reviewed_head):
    result = orchestrate(NativeRun(reviewed_head).operations())
    if result['status'] != 'COMPLETED':
        raise RuntimeError('Startup evidence collection failed; see the persisted native_run01 result')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='One reviewed fixed inert upload and conditional capture')
    parser.add_argument('--execute', action='store_true', required=True)
    parser.add_argument('--reviewed-head', required=True)
    args = parser.parse_args(argv)
    if not re.fullmatch('[0-9a-f]{40}', args.reviewed_head):
        parser.error('--reviewed-head must be forty lowercase hexadecimal characters')
    return native_run(args.reviewed_head)


if __name__ == '__main__':
    main()
