BOOT='55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
CLI='/usr/bin/arduino-cli'
CLI_SHA='b878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433'
REMOTE='/home/arduino/sumox26_codex_build/ordinary-app-static01'
import hashlib,json,os,pwd,re,resource,signal,sys
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
  args=(p/'cmdline').read_bytes().split(b'\0');name=Path(os.fsdecode(args[0])).name if args[0] else ''
 except FileNotFoundError:continue
 if name in ('arduino-cli','openocd','remoteocd') or re.fullmatch(r'(?:.*-)?(?:gcc|g\+\+|cc|c\+\+|cc1|cc1plus|collect2|as|ld|ld.bfd|lto-wrapper|lto1)',name):conflicts.append({'pid':int(p.name),'argv0':os.fsdecode(args[0])})
if conflicts:raise ValueError('Conflicting processes: '+repr(conflicts))
identity={'uid':os.getuid(),'user':pwd.getpwuid(os.getuid()).pw_name,'boot_id':BOOT,'cli_sha256':CLI_SHA,'free_bytes':free,'conflicts':conflicts}

identity['resuid']=list(os.getresuid());identity['resgid']=list(os.getresgid())
identity['remote_owner_exists']=os.path.lexists(REMOTE)
if identity['resuid']!=[1000]*3 or identity['resgid']!=[1000]*3 or identity['remote_owner_exists']:raise ValueError('Closing identity or owner changed')
print(json.dumps(identity))
