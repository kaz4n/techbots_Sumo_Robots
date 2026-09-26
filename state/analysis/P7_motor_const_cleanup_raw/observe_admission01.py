# Observes the last upload scratch and its retained originals exactly once.
# Uses the reviewed descriptor reader without invoking cleanup or MCU tools.
# Saves command, raw streams, identity closure and the process-visibility limit.
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import subprocess
import sys
import time
import zlib

ROOT = Path(__file__).absolute().parents[3]
OUTPUT = Path(__file__).with_name('admission01.json')
ADB = Path('C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
ADB_SHA = 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'
HELPER = ROOT / 'state/analysis/P7_static_link_probe_raw/static_remote.py'
HELPER_SHA = '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'
BODY = r'''
import os,stat,sys,json,hashlib,base64,zlib,types,signal
signal.alarm(45)
def require(ok,message):
 if not ok:raise ValueError(message)
helper_raw=zlib.decompress(base64.b64decode(TOKEN,validate=True))
require(len(helper_raw)==33321 and hashlib.sha256(helper_raw).hexdigest()==HELPER_SHA,'Helper pin changed')
h=types.ModuleType('fixed_read_only_admission');exec(compile(helper_raw,'/__sumox__/static_remote.py','exec'),h.__dict__)
expected={'user':'arduino','uid':1000,'gid':1000,'home':'/home/arduino','sysname':'Linux','release':'6.16.7-g0dd6551ae96b','machine':'aarch64','boot_id':'55c386b9-fe6d-4388-a7f4-1d91e0bb49d8','python':[3,13,5]}
core='/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/'
pins={
 'app_motor_observe.ino.bin-zsk.bin':(95520,'e400078166394d0f8ea44b601e9ba2948992c4f263c5c7ee5fb3942433c143d0','/home/arduino/sumox26_codex_build/app-motor-settle-static01/build/app_motor_observe.ino.bin-zsk.bin'),
 'flash_sketch.cfg':(680,'38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c',core+'variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg'),
 'zephyr-arduino_uno_q_stm32u585xx.elf':(2303728,'39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd',core+'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf')}
def stamp(info):
 return {key:getattr(info,'st_'+key) for key in ('dev','ino','mode','uid','gid','nlink','size','mtime_ns','ctime_ns')}
def read_record(fd,name,limit):
 before=os.stat(name,dir_fd=fd,follow_symlinks=False)
 require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<before.st_size<=limit,'Unsafe observed file')
 raw,identity=h.read_file(fd,name,limit)
 require(stamp(os.stat(name,dir_fd=fd,follow_symlinks=False))==stamp(before),'Full file identity drift')
 return {'identity':stamp(before),'descriptor_identity':identity,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def original(root,path):
 parent,name=path.rsplit('/',1)
 with h.directory(root,parent) as fd:return dict(path=path,**read_record(fd,name,4194304))
r={'scope':'READ_ONLY_D201_UPLOAD_SCRATCH_AND_ORIGINALS','status':'FAILED','target':'/tmp/remoteocd','exists':None,'files':{},'originals':{},'first_error':None,'closing_checks':[],
 'proc_visibility_limitation':'Nonprivileged process-name/command inspection only; protected cwd/fd handles are not inspected. No process-use clearance or deletion authorization is established.'}
root=None
try:
 root=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 r['identity_before']=h.identity(root);require(r['identity_before']==expected,'Board identity differs')
 require(os.getresuid()==(1000,1000,1000) and os.getresgid()==(1000,1000,1000),'Unexpected credential state')
 for name,pin in pins.items():r['originals'][name]=original(root,pin[2])
 with h.directory(root,'/tmp') as parent:
  try:os.stat('remoteocd',dir_fd=parent,follow_symlinks=False)
  except FileNotFoundError:r['exists']=False
  else:
   r['exists']=True
   with h.child_directory(parent,'remoteocd','/tmp/remoteocd') as fd:
    before=stamp(os.fstat(fd));r['directory_before']=before
    require(before['uid']==before['gid']==1000,'Scratch owner differs')
    names=sorted(os.listdir(fd));require(len(names)<=8,'Scratch entry bound exceeded')
    for name in names:r['files'][name]=read_record(fd,name,4194304)
    require(names==sorted(os.listdir(fd)) and stamp(os.fstat(fd))==before,'Scratch changed during observation')
    for name,record in r['files'].items():require(read_record(fd,name,4194304)==record,'Scratch closing file differs')
    require(stamp(os.stat('remoteocd',dir_fd=parent,follow_symlinks=False))==before,'Scratch directory changed')
    r['directory_after']=stamp(os.fstat(fd));r['closing_checks'].append({'name':'scratch','status':'PASS'})
 for name,pin in pins.items():
  require(original(root,pin[2])==r['originals'][name],'Original changed during observation')
  r['closing_checks'].append({'name':pin[2],'status':'PASS'})
 r['expected_originals_match']=all((r['originals'][n]['bytes'],r['originals'][n]['sha256'])==p[:2] for n,p in pins.items())
 r['exact_three_d201_copies']=set(r['files'])==set(pins) and all((r['files'][n]['bytes'],r['files'][n]['sha256'])==p[:2] for n,p in pins.items())
 try:r['compiler_process_candidates']=h.processes(root)
 except Exception as error:r['process_inspection_error']={'type':type(error).__name__,'message':str(error)}
 r['identity_after']=h.identity(root);require(r['identity_after']==r['identity_before'],'Board identity changed')
 r['closing_checks'].append({'name':'board_identity','status':'PASS'})
 r['status']='OBSERVED'
except Exception as error:r['first_error']={'type':type(error).__name__,'message':str(error)}
finally:
 if root is not None:
  try:os.close(root)
  except Exception as error:r['status']='FAILED';r['first_error']=r['first_error'] or {'type':type(error).__name__,'message':str(error)}
raw=json.dumps(r,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
require(len(raw)<=65536,'Inventory reply bound exceeded')
sys.stdout.buffer.write(raw+b'\n')
'''


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, expected, limit):
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        assert (stat.S_ISREG if item == path else stat.S_ISDIR)(info.st_mode)
        assert not getattr(info, 'st_file_attributes', 0) & 1024
    before = path.stat()
    assert before.st_nlink == 1 and 0 < before.st_size <= limit
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(limit + 1)
        closed = os.fstat(stream.fileno())
    stable = lambda value: (value.st_dev, value.st_ino, value.st_nlink, value.st_size, value.st_mtime_ns)
    assert stable(before) == stable(opened) == stable(closed) == stable(path.stat())
    assert len(raw) == before.st_size and sha(raw) == expected
    return raw


def main():
    assert sys.dont_write_bytecode and sys.argv[1:] == []
    assert not os.path.lexists(OUTPUT) and shutil.disk_usage(ROOT).free >= 134217728
    helper = checked(HELPER, HELPER_SHA, 65536)
    adb = checked(ADB, ADB_SHA, 16777216)
    token = base64.b64encode(zlib.compress(helper, 9)).decode()
    program = 'TOKEN=' + repr(token) + '\nHELPER_SHA=' + repr(HELPER_SHA) + '\n' + BODY
    remote = ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino', 'LOGNAME=arduino',
              'PATH=/usr/bin:/bin', 'LANG=C.UTF-8', '/usr/bin/python3', '-I', '-B', '-c', program]
    argv = [str(ADB), '-s', '2629958581', 'shell', '-T', shlex.join(remote)]
    units = len(subprocess.list2cmdline(argv).encode('utf-16-le')) // 2 + 1
    assert units <= 30000
    result = dict(operation='one nonprivileged read-only scratch/original inventory', argv=argv,
                  command_units=units, program_sha256=sha(program.encode()), helper_sha256=HELPER_SHA,
                  adb_sha256=sha(adb), started_utc=datetime.now(timezone.utc).isoformat(),
                  returncode=None, stdout='', stderr='', first_error=None)
    started = time.monotonic()
    try:
        reply = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, timeout=60, check=False)
        result.update(returncode=reply.returncode, stdout=reply.stdout.decode(), stderr=reply.stderr.decode(),
                      stdout_bytes=len(reply.stdout), stdout_sha256=sha(reply.stdout),
                      stderr_bytes=len(reply.stderr), stderr_sha256=sha(reply.stderr))
        assert len(reply.stdout) <= 65536 and len(reply.stderr) <= 65536
        assert reply.returncode == 0 and not reply.stderr
        observed = json.loads(reply.stdout)
        assert observed['status'] == 'OBSERVED' and observed['first_error'] is None
        assert checked(HELPER, HELPER_SHA, 65536) == helper
        assert checked(ADB, ADB_SHA, 16777216) == adb
        result['local_input_closure'] = 'PASS'
    except Exception as error:
        result['first_error'] = {'type': type(error).__name__, 'message': str(error)}
        if isinstance(error, subprocess.TimeoutExpired):
            result.update(stdout=(error.stdout or b'').decode(errors='replace'),
                          stderr=(error.stderr or b'').decode(errors='replace'))
    result.update(finished_utc=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.monotonic()-started)
    with OUTPUT.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'output': str(OUTPUT), 'bytes': OUTPUT.stat().st_size,
                      'sha256': sha(OUTPUT.read_bytes()), 'returncode': result['returncode'],
                      'first_error': result['first_error']}))
    if result['first_error'] is not None:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
