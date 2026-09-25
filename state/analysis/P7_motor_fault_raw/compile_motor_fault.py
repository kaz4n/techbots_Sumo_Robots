# Performs one fixed inert compile through the existing checked build policy.
# Pins local inputs and board identity, preserving each command and failed output.
# Requires source review and controlled host checks before its single native use.
# Launch: python -B -X pycache_prefix=<absolute selected output/pycache> compile_motor_fault.py --execute [--run compile02]
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
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P7_motor_fault_raw'
OUTPUT = RAW / 'native_compile01'
INPUTS = RAW / 'compile_inputs.json'
STAGE = ROOT / 'build/stage/motor_fault'
REMOTE = '/home/arduino/sumox26_codex_build/motor-fault-compile01'
SKETCH = REMOTE + '/motor_fault'
BOARD = '2629958581'
BOOT = '6d4aca1b-ac1f-4caf-b1ef-e127ce3956f6'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
ADB_SHA = 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'
CLI = '/usr/bin/arduino-cli'
CLI_SHA = 'b878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433'
SUPPORT = 'state/analysis/P7_static_startup_raw/capture_remote.py'
SUPPORT_SHA = 'ab0bb32031c1986cc58db1f410a0bdca59449a9dae237672085a81e291b33458'
BASELINES = tuple('state/analysis/P7_static_startup_raw/' + name for name in (
    'cli_initialization_inventory.json', 'cli_builtin_files_inventory.json'))
ENV = {'HOME': '/home/arduino', 'USER': 'arduino', 'LOGNAME': 'arduino',
       'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}

# This preamble performs reads only. The first board command runs just this code.
IDENTITY = '''import hashlib,json,os,pwd,re,resource,signal,sys
from pathlib import Path
signal.alarm(60)
if os.getuid()!=1000 or pwd.getpwuid(os.getuid()).pw_name!='arduino':raise ValueError('UID changed')
if Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=BOOT:raise ValueError('Boot changed')
if hashlib.sha256(Path(CLI).read_bytes()).hexdigest()!=CLI_SHA:raise ValueError('CLI changed')
if resource.getrlimit(resource.RLIMIT_FSIZE)!=(resource.RLIM_INFINITY,resource.RLIM_INFINITY):raise ValueError('Inherited file-size limit')
for p in (Path('/home/arduino'),Path(REMOTE).parent):
 if p.resolve()!=p:raise ValueError('Linked remote ancestry')
space=os.statvfs('/home/arduino');free=space.f_bavail*space.f_frsize
conflicts=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit():continue
 try:
  args=(p/'cmdline').read_bytes().split(b'\\0');name=Path(os.fsdecode(args[0])).name if args[0] else ''
 except FileNotFoundError:continue
 if name in ('arduino-cli','openocd','remoteocd') or re.fullmatch(r'(?:.*-)?(?:gcc|g\\+\\+|cc|c\\+\\+|cc1|cc1plus|collect2|as|ld|ld.bfd|lto-wrapper|lto1)',name):conflicts.append({'pid':int(p.name),'argv0':os.fsdecode(args[0])})
if conflicts:raise ValueError('Conflicting processes: '+repr(conflicts))
identity={'uid':os.getuid(),'user':pwd.getpwuid(os.getuid()).pw_name,'boot_id':BOOT,'cli_sha256':CLI_SHA,'free_bytes':free,'conflicts':conflicts}
'''

REMOTE_CHILD = '''import base64,signal,subprocess,time
signal.alarm(0)
folder=Path(REMOTE)/'commands'/packet['name'];folder.mkdir()
record={'argv':packet['argv'],'env':ENV,'deadline_seconds':packet['deadline'],'reap_seconds':5,'started':time.time(),'status':'FAILED'}
(folder/'intent.json').write_text(json.dumps(record))
streams=[]
try:
 for name in ('stdout','stderr'):streams.append((folder/name).open('x+b'))
 child=subprocess.Popen(packet['argv'],stdin=subprocess.DEVNULL,stdout=streams[0],stderr=streams[1],env=ENV,cwd='/home/arduino',shell=False,start_new_session=True)
 record['pid']=child.pid;record['execution']=wait_child(child,packet['deadline'])
except Exception as error:
 record['error']={'type':type(error).__name__,'message':str(error)}
 if hasattr(error,'subprocess_result'):record['execution']=error.subprocess_result
finally:
 for name,stream in zip(('stdout','stderr'),streams):
  try:
   stream.flush();os.fsync(stream.fileno());stream.seek(0);raw=stream.read(33554433)
   record[name+'_bytes']=os.fstat(stream.fileno()).st_size
   record[name+'_base64']=base64.b64encode(raw).decode()
  except Exception as error:
   record.setdefault('error',{'type':type(error).__name__,'message':str(error)})
   record.setdefault('stream_errors',[]).append({'stream':name,'message':str(error)})
  finally:
   try:stream.close()
   except Exception as error:
    record.setdefault('error',{'type':type(error).__name__,'message':str(error)})
    record.setdefault('stream_errors',[]).append({'stream':name,'message':str(error)})
 if record.get('execution')=={'returncode':0,'timed_out':False,'reaped':True} and 'error' not in record:record['status']='COMPLETED'
 record['finished']=time.time();(folder/'result.json').write_text(json.dumps(record));print(json.dumps(record))
'''


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
    return json.loads(raw, object_pairs_hook=unique)


def parse_request(argv):
    require(type(argv) is list and all(type(item) is str for item in argv),
            'Expected an exact argument list')
    if argv == ['--execute']:
        return 'compile01'
    if argv == ['--execute', '--run', 'compile02']:
        return 'compile02'
    raise ValueError('Expected --execute or --execute --run compile02')


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def files(folder):
    require(folder.is_dir() and not folder.is_symlink(), 'Missing/linked source directory')
    result = {}
    for path in sorted(folder.rglob('*')):
        require(not path.is_symlink(), 'Linked source path')
        if path.is_file():
            result[path.relative_to(folder).as_posix()] = sha(path.read_bytes())
        else:
            require(path.is_dir(), 'Nonregular source path')
    return result


def projection(value):
    if type(value) is dict:
        return {name: projection(item) for name, item in value.items()
                if name not in ('mtime_ns', 'ctime_ns')}
    if type(value) is list:
        items = [projection(item) for item in value]
        return sorted(items, key=lambda x: json.dumps(x, sort_keys=True)) if all(
            type(item) is dict for item in items) else items
    return value


def extracted_wait(raw):
    require(sha(raw) == SUPPORT_SHA, 'Wait/reap source changed')
    source = raw.decode('utf-8')
    definitions = {node.name: ast.get_source_segment(source, node) for node in
                   ast.parse(source).body if isinstance(node, ast.FunctionDef)}
    return '\n\n'.join(definitions[name] for name in ('stop_child', 'wait_child')) + '\n'


class CompileOnce:
    def __init__(self, *, run_id='compile01'):
        require(type(run_id) is str and run_id in ('compile01', 'compile02'),
                'Expected compile01 or compile02')
        self.run_id = run_id
        self.output = OUTPUT if run_id == 'compile01' else RAW / 'native_compile02'
        self.inputs_path = INPUTS if run_id == 'compile01' else RAW / 'compile_inputs02.json'
        self.remote = REMOTE if run_id == 'compile01' else REMOTE.rsplit('/', 1)[0] + '/motor-fault-compile02'
        self.sketch = self.remote + '/motor_fault'
        self.inputs_raw = self.inputs_path.read_bytes()
        self.inputs = decode(self.inputs_raw)
        self.counter, self.compiler_calls, self.query_calls = 0, 0, 0
        self.claimed, self.remote_owned, self.stage_hashes = False, False, None
        self.report = {'status': 'FAILED', 'board': BOARD, 'remote': self.remote,
                       'run_id': self.run_id,
                       'started_utc': datetime.now(timezone.utc).isoformat(),
                       'inputs_sha256': sha(self.inputs_raw), 'first_error': None,
                       'final_checks': []}

    def local(self):
        require(sys.dont_write_bytecode and sys.pycache_prefix == str(self.output / 'pycache') and
                not os.path.lexists(self.output / 'pycache'), 'Isolated empty pycache prefix required')
        require(self.inputs_path.read_bytes() == self.inputs_raw, 'Input manifest changed')
        required = {'tools/board_tool.py', 'tools/app_build_policy.py',
                    'tools/app_build_commands.json', 'tools/app_build_pins.json',
                    SUPPORT, *BASELINES, Path(__file__).relative_to(ROOT).as_posix()}
        for tree in ('src', 'bench/motor_fault'):
            current = {tree + '/' + name for name in files(ROOT / tree)}
            require(current == {name for name in self.inputs if name.startswith(tree + '/')},
                    'Source filename set changed: ' + tree)
            required.update(current)
        require(type(self.inputs) is dict and required <= set(self.inputs), 'Missing input pins')
        for name, expected in self.inputs.items():
            relative = PurePosixPath(name)
            require(not relative.is_absolute() and '..' not in relative.parts and
                    relative.as_posix() == name and re.fullmatch('[0-9a-f]{64}', expected),
                    'Invalid input pin')
            path = ROOT / name
            require(path.resolve() == path.absolute() and path.is_file(), 'Linked/missing input')
            require(sha(path.read_bytes()) == expected, 'Input changed: ' + name)
        require(sha(Path(ADB).read_bytes()) == ADB_SHA, 'ADB changed')
        require(not os.path.lexists(importlib.util.cache_from_source(
            str(ROOT / 'tools/app_build_policy.py'))), 'Nested policy bytecode cache exists')
        if self.stage_hashes is not None:
            require(files(STAGE) == self.stage_hashes, 'Local stage changed')

    def transport(self, arguments, timeout, label):
        require(sha(Path(ADB).read_bytes()) == ADB_SHA, 'ADB changed')
        self.counter += 1
        folder = self.output / f'{self.counter:04d}-{label}'
        folder.mkdir()
        argv = [ADB, '-s', BOARD, *arguments]
        units = len(subprocess.list2cmdline(argv).encode('utf-16-le')) // 2 + 1
        require(units <= 30000, 'Windows command exceeds 30000 units')
        record = {'argv': argv, 'timeout_seconds': timeout, 'command_units': units}
        write(folder / 'intent.json', record)
        out = err = b''
        try:
            result = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                                    timeout=timeout, check=False)
            record['returncode'] = result.returncode
            out, err = result.stdout, result.stderr
        except Exception as error:
            record['error'] = {'type': type(error).__name__, 'message': str(error)}
            out, err = getattr(error, 'stdout', None) or b'', getattr(error, 'stderr', None) or b''
            raise
        finally:
            (folder / 'stdout').write_bytes(out)
            (folder / 'stderr').write_bytes(err)
            write(folder / 'result.json', record)
        if result.returncode:
            raise subprocess.CalledProcessError(result.returncode, argv, out, err)
        return result, folder

    def direct(self, program, label, timeout=90):
        argv = ['/usr/bin/env', '-i', *(key + '=' + value for key, value in ENV.items()),
                '/usr/bin/python3', '-I', '-B', '-c', program]
        return self.transport(['shell', '-T', shlex.join(argv)], timeout, label)

    def preamble(self):
        values = {'BOOT': BOOT, 'CLI': CLI, 'CLI_SHA': CLI_SHA, 'REMOTE': self.remote, 'ENV': ENV}
        return '\n'.join(name + '=' + repr(value) for name, value in values.items()) + '\n' + IDENTITY

    def inventory(self, initial=False):
        extra = "if free<1073741824:raise ValueError('Less than 1GiB free')\n"
        if initial:
            extra += "if os.path.lexists(REMOTE):raise ValueError('Remote attempt already exists')\n"
        reply, _ = self.direct(self.preamble() + extra + 'print(json.dumps(identity))\n', 'identity')
        return decode(reply.stdout)

    def prerequisites(self, names=BASELINES):
        for name in names:
            baseline = decode((ROOT / name).read_bytes())
            require(baseline['returncode'] == 0 and not baseline['stderr'], 'Failed baseline')
            reply, _ = self.transport(['shell', '-T', shlex.join(baseline['argv'])],
                                      60, Path(name).stem)
            require(not reply.stderr and len(reply.stdout) <= 1048576, 'Invalid prerequisite output')
            value, expected = decode(reply.stdout), decode(baseline['stdout'])
            require(value['status'] == 'COLLECTED' and value['identity'] == expected['identity'] and
                    value['identity']['uid'] == 1000 and value['identity']['boot_id'] == BOOT,
                    'Prerequisite identity/status changed')
            require(projection(value) == projection(expected), 'CLI initialization prerequisites changed')

    def sources(self):
        program = self.preamble() + '''root=Path(REMOTE)/'motor_fault';result={}
if root.resolve()!=root:raise ValueError('Linked source root')
for p in sorted(root.rglob('*')):
 if p.is_symlink():raise ValueError('Linked source entry')
 if p.is_file():result[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
 elif not p.is_dir():raise ValueError('Nonregular source entry')
print(json.dumps(result))
'''
        reply, _ = self.direct(program, 'source-set')
        require(decode(reply.stdout) == self.stage_hashes, 'Remote source filename/hash set changed')

    def stage(self, board):
        require(not os.path.lexists(STAGE), 'Local motor_fault stage already exists')
        require(shutil.disk_usage(ROOT).free >= 134217728, 'Less than 128MiB local free space')
        stage = board.stage('bench/motor_fault')
        require(stage == STAGE, 'Wrong stage')
        self.stage_hashes = files(stage)
        expected = {}
        for name, digest in self.inputs.items():
            if name.startswith('bench/motor_fault/'):
                relative = name[len('bench/motor_fault/'):]
                if relative != '.gitkeep':
                    expected[relative] = digest
            elif name == 'src/config.h' or name.startswith(('src/core/', 'src/hal/')):
                expected[name] = digest
            elif name.startswith('src/app/') and not name.startswith('src/app/src/') and Path(name).suffix in ('.c', '.cc', '.cpp', '.h', '.hpp'):
                expected[name] = digest
        require(self.stage_hashes == expected, 'Stage differs from reviewed inputs')
        self.local()
        write(self.output / 'staged_files.json', self.stage_hashes)
        parents = sorted({str(PurePosixPath(name).parent) for name in self.stage_hashes})
        program = self.preamble() + 'Path(REMOTE).mkdir(mode=0o700)\n'
        program += "(Path(REMOTE)/'commands').mkdir()\n(Path(REMOTE)/'motor_fault').mkdir()\n"
        program += 'for name in ' + repr(parents) + ":(Path(REMOTE)/'motor_fault'/name).mkdir(parents=True,exist_ok=True)\nprint(json.dumps(identity))\n"
        # Attempt ownership survives an uncertain transport result.
        self.claimed = True
        self.direct(program, 'claim')
        self.remote_owned = True
        for name in self.stage_hashes:
            self.transport(['push', str(STAGE / name), self.sketch + '/' + name], 60, 'push')
        self.sources()

    def command_runner(self, board, argv, capture=False, timeout=None):
        require(board == BOARD and capture is True and timeout is None, 'Unexpected checked command interface')
        argv = list(argv)
        deadline = 60
        if argv[0] == 'arduino-cli':
            require(argv[1] in ('version', 'config', 'compile'), 'Unexpected CLI command')
            if argv[1] == 'compile':
                query = '--show-properties=expanded' in argv
                self.query_calls += int(query)
                self.compiler_calls += int(not query)
                require(self.query_calls <= 1 and self.compiler_calls <= 1, 'Repeated compile/query')
                argv[-1:-1] = ['--jobs', '1']
                deadline = 60 if query else 720
            argv = [CLI, '--config-file', '/dev/null', *argv[1:]]
        else:
            require(argv[0] in ('sha256sum', 'sh'), 'Unexpected checked executable')
            argv[0] = {'sha256sum': '/usr/bin/sha256sum', 'sh': '/bin/sh'}[argv[0]]
        self.local()
        packet = {'name': f'{self.counter + 1:04d}', 'argv': argv, 'deadline': deadline}
        program = self.preamble() + 'packet=' + repr(packet) + '\n'
        program += extracted_wait((ROOT / SUPPORT).read_bytes()) + REMOTE_CHILD
        reply, folder = self.direct(program, 'checked-command', deadline + 90)
        require(not reply.stderr, 'Remote wrapper stderr')
        record = decode(reply.stdout)
        write(folder / 'remote_result.json', record)
        out, err = (base64.b64decode(record[key + '_base64'], validate=True) for key in ('stdout', 'stderr'))
        (folder / 'child.stdout').write_bytes(out)
        (folder / 'child.stderr').write_bytes(err)
        require(len(out) == record['stdout_bytes'] and len(err) == record['stderr_bytes'], 'Child output exceeds receipt bound; full remote files retained')
        execution = record['execution']
        require(execution['reaped'] and not execution['timed_out'], 'Child deadline/reap failed')
        result = subprocess.CompletedProcess(argv, execution['returncode'], out.decode('utf-8'), err.decode('utf-8'))
        if result.returncode:
            raise subprocess.CalledProcessError(result.returncode, argv, result.stdout, result.stderr)
        require(record['status'] == 'COMPLETED', 'Remote child wrapper failed')
        return result

    def final_policy(self, overrides=False):
        require(self.remote_owned, 'Remote attempt ownership was not confirmed')
        name = 'tools/app_build_policy.py'
        raw = (ROOT / name).read_bytes()
        require(sha(raw) == self.inputs[name], 'Final policy source changed')
        policy = types.ModuleType('fixed_motor_fault_final_policy')
        policy.__file__ = str(ROOT / name)
        exec(compile(raw, policy.__file__, 'exec'), policy.__dict__)
        if overrides:
            policy.check_overrides(self.command_runner, BOARD, '/home/arduino/.arduino15',
                                   '/home/arduino/Arduino', self.sketch)
        else:
            policy.verify_hashes(self.command_runner, BOARD,
                                 policy.installed_pins('/home/arduino/.arduino15'))

    def run(self):
        require(sys.dont_write_bytecode and sys.pycache_prefix == str(self.output / 'pycache') and
                parse_request(sys.argv[1:]) == self.run_id,
                'Use the selected output/pycache prefix and matching --execute [--run compile02]')
        self.local()
        require(not os.path.lexists(STAGE), 'Local motor_fault stage already exists')
        self.output.mkdir()
        write(self.output / 'intent.json', self.report)
        try:
            self.report['initial_identity'] = self.inventory(initial=True)
            self.prerequisites()
            board = types.ModuleType('fixed_motor_fault_board')
            board.__file__ = str(ROOT / 'tools/board_tool.py')
            exec(compile(Path(board.__file__).read_bytes(), board.__file__, 'exec'), board.__dict__)
            self.stage(board)
            self.report['source_sha256'] = board.source_hash(STAGE)
            self.report['artifacts'] = board.compile_app(
                BOARD, self.report['source_sha256'], self.sketch, self.remote, 'arduino:zephyr:unoq',
                '-DMATCH=0 -DMOTORS_ALLOWED=0', 'default', project='motor_fault.ino',
                command_runner=self.command_runner)
            require(self.compiler_calls == self.query_calls == 1, 'Missing checked compile/query')
            self.report['status'] = 'COMPILE_CHECKED'
        except Exception as error:
            self.report['first_error'] = {'type': type(error).__name__, 'message': str(error)}
        finally:
            checks = [('local', self.local), ('identity', self.inventory)]
            checks.extend((Path(name).stem, lambda name=name: self.prerequisites((name,)))
                          for name in BASELINES)
            if self.claimed:
                checks.append(('remote_sources', self.sources))
            if self.stage_hashes is not None:
                checks.extend([('installed_pins', self.final_policy),
                               ('overrides', lambda: self.final_policy(overrides=True))])
            for name, operation in checks:
                try:
                    operation()
                    self.report['final_checks'].append({'name': name, 'status': 'PASS'})
                except Exception as error:
                    self.report['status'] = 'FAILED'
                    self.report['final_checks'].append({'name': name, 'status': 'FAILED', 'error': str(error)})
            self.report.update(finished_utc=datetime.now(timezone.utc).isoformat(),
                               commands=self.counter, compiler_calls=self.compiler_calls,
                               query_calls=self.query_calls)
            write(self.output / 'result.json', self.report)
        print(json.dumps(self.report, indent=2))
        return 0 if self.report['status'] == 'COMPILE_CHECKED' else 1


if __name__ == '__main__':
    sys.exit(CompileOnce(run_id=parse_request(sys.argv[1:])).run())
