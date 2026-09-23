"""Stage three pinned D114 capture files on board Linux without executing them.

The fresh private directory and exact bytes are verified after every ADB push.
Every command/result is retained; existing directories and retries are refused.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT/'state/analysis/P2_ui_adc_probe_raw/tool_deployment.json'
DESTINATION = '/home/arduino/sumox26-capture-tools/ui_adc_d114_run01'
SERIAL = '2629958581'
PINS = {
    'ui_adc_capture.py':'f4b3db265bdf2d5a5fdada19ed9f51a44304d9ba5da8be78e598365afa2c4444',
    'p0_capture.py':'885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c',
    'p0_mem_read.cfg':'89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339',
}
REMOTE_COMMON = '''import os,stat,hashlib,json
target="/home/arduino/sumox26-capture-tools/ui_adc_d114_run01"
flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW
def open_chain(path):
    fd=os.open('/',flags)
    observed=[]
    prefix=''
    for part in path.strip('/').split('/'):
        prefix+='/'+part
        before=os.stat(part,dir_fd=fd,follow_symlinks=False)
        if not stat.S_ISDIR(before.st_mode): raise ValueError('Nondirectory ancestry')
        nextfd=os.open(part,flags,dir_fd=fd)
        after=os.fstat(nextfd)
        if (before.st_dev,before.st_ino)!=(after.st_dev,after.st_ino):
            raise ValueError('Ancestry identity changed')
        observed.append(dict(path=prefix,device=after.st_dev,inode=after.st_ino,
                             mode=stat.S_IMODE(after.st_mode),uid=after.st_uid))
        os.close(fd)
        fd=nextfd
    return fd,observed
'''
REMOTE_CREATE = REMOTE_COMMON + '''
parent,name=target.rsplit('/',1)
rootfd,unused=open_chain('/home/arduino')
parent_created=False
try:
    os.stat('sumox26-capture-tools',dir_fd=rootfd,follow_symlinks=False)
except FileNotFoundError:
    os.mkdir('sumox26-capture-tools',0o700,dir_fd=rootfd)
    parent_created=True
os.close(rootfd)
fd,ancestry=open_chain(parent)
try:
    os.mkdir(name,0o700,dir_fd=fd)
    child=os.open(name,flags,dir_fd=fd)
    os.fchmod(child,0o700)
    result=os.fstat(child)
    if not stat.S_ISDIR(result.st_mode) or stat.S_IMODE(result.st_mode)!=0o700:
        raise ValueError('Private directory creation failed')
    if os.listdir(child): raise ValueError('New directory is not empty')
    ancestry.append(dict(path=target,device=result.st_dev,inode=result.st_ino,
                         mode=stat.S_IMODE(result.st_mode),uid=result.st_uid))
    print(json.dumps(dict(destination=target,parent_created=parent_created,ancestry=ancestry,files=[])))
finally:
    os.close(fd)
'''
REMOTE_VERIFY = REMOTE_COMMON + '''
expected=EXPECTED
prior=PRIOR
fd,ancestry=open_chain(target)
if ancestry!=prior: raise ValueError('Destination ancestry identity changed')
if set(os.listdir(fd))!=set(expected): raise ValueError('Unexpected file set')
files={}
for name,wanted in expected.items():
    handle=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd)
    try:
        before=os.fstat(handle)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1:
            raise ValueError('Not a single regular file')
        if before.st_size!=wanted['bytes']: raise ValueError('Unexpected file extent')
        os.fchmod(handle,0o600)
        digest=hashlib.sha256()
        remaining=wanted['bytes']
        while remaining:
            data=os.read(handle,min(65536,remaining))
            if not data: raise ValueError('Truncated staged file')
            digest.update(data)
            remaining-=len(data)
        after=os.fstat(handle)
        named=os.stat(name,dir_fd=fd,follow_symlinks=False)
        identity=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        if identity(after)!=identity(named): raise ValueError('File replaced while hashing')
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
            raise ValueError('File changed while hashing')
        if (after.st_size,digest.hexdigest())!=(wanted['bytes'],wanted['sha256']):
            raise ValueError('Pinned byte identity mismatch')
        if stat.S_IMODE(after.st_mode)!=0o600: raise ValueError('Wrong file permissions')
        files[name]=dict(bytes=after.st_size,sha256=digest.hexdigest(),mode=stat.S_IMODE(after.st_mode),
                         device=after.st_dev,inode=after.st_ino,uid=after.st_uid)
    finally:
        os.close(handle)
os.close(fd)
print(json.dumps(dict(destination=target,ancestry=ancestry,files=files)))
'''


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(report):
    RECEIPT.write_bytes((json.dumps(report,indent=2)+'\n').encode())


def local_identities():
    result={}
    for name,expected in PINS.items():
        path=ROOT/'tools'/name
        if any(item.is_symlink() for item in (path,*path.parents)):
            raise ValueError('Local source symlink refused')
        if not path.is_file(): raise ValueError('Local source is not regular')
        value=path.read_bytes()
        digest=hashlib.sha256(value).hexdigest()
        if digest!=expected: raise ValueError('Local source identity mismatch: '+name)
        result[name]={'path':str(path),'bytes':len(value),'sha256':digest}
    return result


def command(report,argv):
    item={'argv':[str(value) for value in argv],'started_utc':now(),'status':'STARTED'}
    report['commands'].append(item)
    save(report)
    try:
        result=subprocess.run(argv,capture_output=True,timeout=60,check=False)
        item.update(returncode=result.returncode,stdout=result.stdout.decode('utf-8','replace'),
                    stderr=result.stderr.decode('utf-8','replace'),status='FINISHED',ended_utc=now())
        save(report)
        if result.returncode: raise RuntimeError('Staging command failed; no retry')
        return item['stdout']
    except BaseException as error:
        item.update(exception=type(error).__name__,message=str(error),ended_utc=now())
        if isinstance(error,subprocess.TimeoutExpired):
            item.update(stdout=(error.stdout or b'').decode('utf-8','replace'),
                        stderr=(error.stderr or b'').decode('utf-8','replace'))
        save(report)
        raise


def remote(report,adb,program):
    argv=[adb,'-s',SERIAL,'shell','python3','-c',shlex.quote(program)]
    return json.loads(command(report,argv))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb',required=True,type=Path)
    args=parser.parse_args(argv)
    if not args.adb.is_file(): raise ValueError('ADB executable is absent')
    with RECEIPT.open('x',encoding='utf-8') as stream: stream.write('{}\n')
    report={'status':'STARTED','started_utc':now(),'serial':SERIAL,'destination':DESTINATION,
            'scope':'Linux file transfer and hashing only; capture scripts not executed; no MCU action',
            'commands':[],'local':{},'remote':None}
    try:
        report['local']=local_identities()
        report['adb']={'path':str(args.adb),'sha256':hashlib.sha256(args.adb.read_bytes()).hexdigest()}
        report['stager_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        save(report)
        if command(report,[str(args.adb),'-s',SERIAL,'get-state']).strip()!='device':
            raise ValueError('Exact selected ADB target is not ready')
        created=remote(report,str(args.adb),REMOTE_CREATE)
        report['created']=created
        save(report)
        transferred={}
        for name in PINS:
            if local_identities()!=report['local']: raise ValueError('Local inputs changed before push')
            command(report,[str(args.adb),'-s',SERIAL,'push',str(ROOT/'tools'/name),DESTINATION+'/'+name])
            transferred[name]={key:report['local'][name][key] for key in ('bytes','sha256')}
            script=REMOTE_VERIFY.replace('EXPECTED',repr(transferred)).replace('PRIOR',repr(created['ancestry']))
            report['remote']=remote(report,str(args.adb),script)
            save(report)
        if set(report['remote']['files'])!=set(PINS): raise ValueError('Final file set differs')
        report.update(status='VERIFIED_STAGED_NOT_EXECUTED',ended_utc=now())
        save(report)
        print(json.dumps({'status':report['status'],'destination':DESTINATION,'files':report['remote']['files']}))
        return 0
    except BaseException as error:
        report.update(status='FAILED_NO_RETRY',error=type(error).__name__+': '+str(error),ended_utc=now())
        save(report)
        raise


if __name__=='__main__':
    sys.exit(main())
