import os,pathlib,json,stat,platform,time,datetime,subprocess,hashlib
P=pathlib.Path
start=time.monotonic()
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'uid':os.getuid(),'gid':os.getgid(),'groups':os.getgroups(),'uname':list(os.uname()),'files':{},'links':{},'commands':[]}
def read(path,limit=262144):
 try:
  with open(path,'rb') as f:b=f.read(limit+1)
  if len(b)>limit:return {'error':'SIZE_LIMIT','limit':limit}
  return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'text':b.decode('utf-8',errors='replace')}
 except OSError as e:return {'error':type(e).__name__,'errno':e.errno}
def link(path):
 try:return str(P(path).resolve(strict=True))
 except OSError as e:return {'error':type(e).__name__,'errno':e.errno}
def command(argv):
 try:
  r=subprocess.run(argv,capture_output=True,text=True,timeout=5)
  return {'argv':argv,'returncode':r.returncode,'stdout':r.stdout[:16384],'stderr':r.stderr[:4096]}
 except Exception as e:return {'argv':argv,'error':type(e).__name__,'message':str(e)}
for name in ['/proc/sys/kernel/random/boot_id','/proc/version','/proc/sys/kernel/yama/ptrace_scope','/proc/tty/drivers','/etc/os-release']:
 out['files'][name]=read(name)
status=read('/proc/self/status');out['self_access']={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in status.get('text','').splitlines() if line.startswith(('Uid:','Gid:','CapInh:','CapPrm:','CapEff:','CapBnd:','NoNewPrivs:','Seccomp:'))}
mounts=read('/proc/mounts');out['proc_mounts']=[line for line in mounts.get('text','').splitlines() if line.split()[1]=='/proc']
dev=os.stat('/dev/ttyHS1');out['device']={'mode':oct(dev.st_mode),'uid':dev.st_uid,'gid':dev.st_gid,'major':os.major(dev.st_rdev),'minor':os.minor(dev.st_rdev),'is_char':stat.S_ISCHR(dev.st_mode),'read_access':os.access('/dev/ttyHS1',os.R_OK),'write_access':os.access('/dev/ttyHS1',os.W_OK)}
for name in ['/sys/class/tty/ttyHS1','/sys/class/tty/ttyHS1/device','/sys/class/tty/ttyHS1/device/driver','/sys/class/tty/ttyHS1/device/driver/module']:
 out['links'][name]=link(name)
resolved=P('/sys/class/tty/ttyHS1/device').resolve(strict=True)
for node in [resolved,*list(resolved.parents)[:7]]:
 for suffix in ['uevent','driver','driver/module','of_node/compatible','of_node/status']:
  q=node/suffix
  if suffix in ('driver','driver/module'):
   if q.is_symlink():out['links'][str(q)]=link(q)
  elif q.exists():out['files'][str(q)]=read(q,4096)
release=platform.release()
for name in ['/usr/src','/lib/modules/'+release,'/boot']:
 try:out.setdefault('directories',{})[name]=sorted(p.name for p in P(name).iterdir())[:100]
 except OSError as e:out.setdefault('directories',{})[name]={'error':type(e).__name__,'errno':e.errno}
for suffix in ['build','source']:
 q='/lib/modules/'+release+'/'+suffix;out['links'][q]=link(q)
for name in ['/lib/modules/'+release+'/modules.builtin','/lib/modules/'+release+'/modules.dep']:
 r=read(name,524288);out['files'][name]={'bytes':r.get('bytes'),'sha256':r.get('sha256'),'error':r.get('error'),'matching_lines':[l for l in r.get('text','').splitlines() if any(s in l.lower() for s in ['serial','uart','geni','msm'])]}
out['commands'].append(command(['dpkg-query','-W','-f=${Package} ${Version} ${Architecture}\n','linux-image*','linux-headers*']))
# Metadata-only fd identity scan. Never open/read UART or fd payloads; omit unrelated targets.
pids=sorted(p.name for p in P('/proc').iterdir() if p.name.isdecimal())
scan={'processes':len(pids),'listed':0,'denied':[],'vanished':0,'fd_stat_denied':0,'fd_vanished':0,'fd_seen':0,'holders':[],'bounded':False}
for pid in pids[:4096]:
 if time.monotonic()-start>15 or scan['fd_seen']>8192:scan['bounded']=True;break
 try:fds=list((P('/proc')/pid/'fd').iterdir());scan['listed']+=1
 except FileNotFoundError:scan['vanished']+=1;continue
 except PermissionError:scan['denied'].append(int(pid));continue
 for fd in fds[:4096]:
  scan['fd_seen']+=1
  try:s=fd.stat()
  except FileNotFoundError:scan['fd_vanished']+=1;continue
  except PermissionError:scan['fd_stat_denied']+=1;continue
  if stat.S_ISCHR(s.st_mode) and s.st_rdev==dev.st_rdev:
   scan['holders'].append({'pid':int(pid),'fd':fd.name,'comm':read('/proc/'+pid+'/comm',256),'exe':link('/proc/'+pid+'/exe')})
 if len(fds)>4096:scan['bounded']=True
scan['pids_after']=sorted(int(p.name) for p in P('/proc').iterdir() if p.name.isdecimal())
scan['pids_before']=[int(p) for p in pids]
out['holder_scan']=scan
out['elapsed_seconds']=time.monotonic()-start
print(json.dumps(out,indent=2))
