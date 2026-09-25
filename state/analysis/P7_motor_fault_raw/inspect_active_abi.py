# Observes the already compiled active diagnostic and loader ABI without MCU access.
# Reuses pinned transport and child-reap code; only file-reading tool commands run.
# A separate source review and retained native receipts verify this one-shot query.
import base64
import hashlib
import json
import os
from pathlib import Path
import shlex
import sys
import types
import zlib

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P7_motor_fault_raw'
OUT = RAW / 'native_abi01'
CALLER = RAW / 'compile_motor_fault.py'
CALLER_SHA = '84efd00611b3a6a8129655005930ff58e555221f6bd8d88a23c7fa1c4381ac0d'
META_SHA = '45ec0da9fba09fbb97a3d314c46572a847052d3387c6f3ddd8814e15144738d7'
INPUTS_SHA = 'b91cf39c8fec322297181e08d160a987ec4bb8d79da338c61949aa5ae5fa5f14'
PREFIX = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
TOOLS = {PREFIX + 'gdb': '8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778',
         PREFIX + 'readelf': 'c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e'}
TYPES = ('motor_fault::Runner', 'motor_fault::Trace', 'motor_fault::TraceReport',
         'motor_fault::Call', 'motor_fault::Report', 'motors::Port',
         'motors::MotorGate', 'motors::Result', 'motors::HaltResult', 'fsm::PreviousTick')

REMOTE_READ = '''import tempfile,time
def checked(path,expected):
 p=Path(path)
 if p.resolve()!=p or not p.is_file():raise ValueError('Linked/missing pinned file: '+path)
 before=p.stat();h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 after=p.stat()
 if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):raise ValueError('File changed during hash')
 if h.hexdigest()!=expected:raise ValueError('File digest changed: '+path)
 return [before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns]
def output_limit():resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576))
def command(argv):
 record={'argv':argv,'deadline_seconds':60,'reap_seconds':5,'started':time.time()}
 result['commands'].append(record)
 with tempfile.TemporaryFile() as out,tempfile.TemporaryFile() as err:
  try:
   child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=out,stderr=err,
      cwd='/home/arduino',env=ENV,shell=False,start_new_session=True,preexec_fn=output_limit)
   record['execution']=wait_child(child,60)
  except Exception as error:
   record['error']={'type':type(error).__name__,'message':str(error)}
   if hasattr(error,'subprocess_result'):record['execution']=error.subprocess_result
   raise
  finally:
   for name,stream in (('stdout',out),('stderr',err)):
    try:
     stream.seek(0);raw=stream.read(1048577);record[name+'_bytes']=len(raw)
     record[name+'_base64']=base64.b64encode(raw).decode('ascii')
    except Exception as error:
     record.setdefault('error',{'type':type(error).__name__,'message':str(error)})
     record.setdefault('stream_errors',[]).append({'stream':name,'message':str(error)})
   record['finished']=time.time()
 if 'error' in record:raise ValueError('File tool evidence collection failed')
 if record['execution']!={'returncode':0,'timed_out':False,'reaped':True}:raise ValueError('File tool failed')
 if record['stderr_bytes']:raise ValueError('File tool stderr')
 if max(record['stdout_bytes'],record['stderr_bytes'])>1048576:raise ValueError('File tool output exceeded bound')
result={'scope':'D173_FILE_ONLY_ABI','status':'FAILED','identity':identity,'commands':[],
        'first_error':None,'final_checks':[]}
before={}
try:
 for path,digest in pins.items():before[path]=checked(path,digest)
 signal.alarm(0)
 for argv in commands:command(argv)
 result['status']='OBSERVED'
except Exception as error:result['first_error']={'type':type(error).__name__,'message':str(error)}
finally:
 for path,digest in pins.items():
  try:
   after=checked(path,digest)
   if path not in before or after!=before[path]:raise ValueError('File identity changed')
   result['final_checks'].append({'path':path,'status':'PASS'})
  except Exception as error:
   result['status']='FAILED';result['final_checks'].append({'path':path,'status':'FAILED','error':str(error)})
 try:
  if os.getuid()!=1000 or Path('/proc/sys/kernel/random/boot_id').read_text().strip()!=BOOT:raise ValueError('Final identity changed')
  result['final_checks'].append({'path':'board_identity','status':'PASS'})
 except Exception as error:
  result['status']='FAILED';result['final_checks'].append({'path':'board_identity','status':'FAILED','error':str(error)})
print(json.dumps(result))
'''


def gdb(file, expressions):
    argv = [PREFIX + 'gdb', '-nx', '-nh', '-batch', '-iex', 'set auto-load no',
            file, '-ex', 'set language c++', '-ex', 'set may-call-functions off']
    for expression in expressions:
        argv += ['-ex', expression]
    return argv


def queries(meta):
    build = meta['build_path']
    loader = next(p for p in meta['file_sha256'] if p.endswith('/zephyr-arduino_uno_q_stm32u585xx.elf'))
    expressions = []
    for name in TYPES:
        expressions += ['p sizeof(' + name + ')', 'p alignof(' + name + ')', 'ptype /o ' + name]
    for member in ('trace_.report_', 'report_', 'trace_.report_.calls', 'report_.applied'):
        expressions += ['p/d (unsigned long)&((motor_fault::Runner*)0)->' + member]
    return [[PREFIX + 'readelf', '--version'], [PREFIX + 'gdb', '--version'],
            [PREFIX + 'readelf', '-hSWs', build + '/motor_fault.ino.elf'],
            gdb(build + '/motor_fault.ino_debug.elf', expressions),
            gdb(loader, ['info address llext_list', 'p sizeof(llext_list)', 'ptype /o llext_list',
                         'p sizeof(struct llext)', 'p alignof(struct llext)', 'ptype /o struct llext',
                         'p/d (unsigned long)&((struct llext*)0)->mem[3]',
                         'p/d (unsigned long)&((struct llext*)0)->mem_size[3]', 'p/d LLEXT_MEM_BSS'])]


def observe(c, context, command, local_pins):
    closure = {'status': 'FAILED', 'first_error': None, 'final_checks': []}
    failure = None
    try:
        reply, _ = c.CompileOnce.transport(context, ['shell', '-T', shlex.join(command)], 400, 'file-abi')
        result = c.decode(reply.stdout)
        c.write(OUT / 'result.json', result)
        if reply.stderr or result['status'] != 'OBSERVED' or len(result['commands']) != 5:
            raise ValueError('File-only ABI observation failed; retain original receipt')
        closure['status'] = 'OBSERVED'
    except Exception as error:
        failure = error
        closure['first_error'] = {'type': type(error).__name__, 'message': str(error)}
    finally:
        for path, digest in local_pins.items():
            check = {'path': path, 'status': 'PASS'}
            try:
                if c.sha((ROOT / path).read_bytes()) != digest:
                    raise ValueError('Final local input drift: ' + path)
            except Exception as error:
                failure = failure or error
                closure['status'] = 'FAILED'
                closure['first_error'] = closure['first_error'] or {
                    'type': type(error).__name__, 'message': str(error)}
                check.update(status='FAILED', error=str(error))
            closure['final_checks'].append(check)
        c.write(OUT / 'local_result.json', closure)
    if failure is not None:
        raise failure


def run():
    if sys.argv[1:] != ['--execute'] or not sys.dont_write_bytecode:
        raise ValueError('Use Python -B inspect_active_abi.py --execute once')
    source, metadata = CALLER.read_bytes(), (RAW / 'active_verified.json').read_bytes()
    if hashlib.sha256(source).hexdigest() != CALLER_SHA or hashlib.sha256(metadata).hexdigest() != META_SHA:
        raise ValueError('Reviewed source/metadata drift')
    c = types.ModuleType('fixed_d173_transport'); c.__file__ = str(CALLER)
    exec(compile(source, str(CALLER), 'exec'), c.__dict__)
    inputs_raw = (RAW / 'compile_inputs_active01.json').read_bytes()
    if c.sha(inputs_raw) != INPUTS_SHA: raise ValueError('Compile input manifest drift')
    inputs = c.decode(inputs_raw)
    if type(inputs) is not dict or len(inputs) != 117: raise ValueError('Wrong compile input set')
    for path, digest in inputs.items():
        if c.sha((ROOT / path).read_bytes()) != digest: raise ValueError('Compile source drift: ' + path)
    meta = c.decode(metadata); pins = {**meta['file_sha256'], **TOOLS}
    pins[meta['build_path'] + '/motor_fault.ino.elf-zsk.bin'] = pins[meta['artifacts'] + '/motor_fault.ino.elf-zsk.bin']
    context = types.SimpleNamespace(output=OUT, counter=0,
                                   remote='/home/arduino/sumox26_codex_build/motor-fault-active01')
    program = c.CompileOnce.preamble(context) + 'import subprocess,base64\n'
    program += c.extracted_wait((ROOT / c.SUPPORT).read_bytes())
    program += 'pins=' + repr(pins) + '\ncommands=' + repr(queries(meta)) + '\n' + REMOTE_READ
    packed = base64.b64encode(zlib.compress(program.encode(), 9)).decode()
    bootstrap = 'import base64,zlib;exec(zlib.decompress(base64.b64decode(' + repr(packed) + ')))'
    command = ['/usr/bin/env', '-i', *(k + '=' + v for k, v in c.ENV.items()),
               '/usr/bin/python3', '-I', '-B', '-c', bootstrap]
    OUT.mkdir()
    reader_sha = c.sha(Path(__file__).read_bytes())
    local_pins = {**inputs, 'state/analysis/P7_motor_fault_raw/active_verified.json': META_SHA,
                  'state/analysis/P7_motor_fault_raw/compile_inputs_active01.json': INPUTS_SHA,
                  Path(__file__).relative_to(ROOT).as_posix(): reader_sha}
    c.write(OUT / 'inputs.json', {'source_commit': '67aca8ad', 'caller_sha256': CALLER_SHA,
            'reader_sha256': reader_sha, 'metadata_sha256': META_SHA, 'inputs_sha256': INPUTS_SHA,
            'program_sha256': c.sha(program.encode()), 'pins': pins, 'commands': queries(meta)})
    observe(c, context, command, local_pins)
    print('OBSERVED: five file-only commands; no upload/reset/MCU access')


if __name__ == '__main__':
    run()
