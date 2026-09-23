"""No elevation retry: inspect only public metadata after the denied attempt."""
from pathlib import Path
program = (Path(__file__).resolve().parent / 'collect.py').read_text(encoding='utf-8')
exec(program.split('run("01_identity"')[0])
run('10_monitor_socket_diag', ['ss', '-ntpe', '( sport = :7500 or dport = :7500 )'])
code = '''from pathlib import Path
import os,json,datetime,subprocess
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'uid':os.getuid(),'groups':os.getgroups(),'processes':[]}
for unit in ['arduino-router.service','arduino-router-serial.service']:
 r=subprocess.run(['systemctl','show',unit,'--property=MainPID','--value'],text=True,capture_output=True,timeout=10)
 item={'unit':unit,'pid_command':{'argv':r.args,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}}
 if r.returncode==0 and r.stdout.strip().isdigit():
  p=Path('/proc')/r.stdout.strip()
  for name in ['comm','cgroup','status']:
   try:
    lines=(p/name).read_text().splitlines()
    item[name]=[x for x in lines if name!='status' or x.startswith(('Name:','State:','Uid:','Gid:','Threads:','PPid:'))]
   except OSError as e:item[name+'_error']=str(e)
 out['processes'].append(item)
out['uart_access_only']={'path':'/dev/ttyHS1','read':os.access('/dev/ttyHS1',os.R_OK),'write':os.access('/dev/ttyHS1',os.W_OK),'opened':False}
print(json.dumps(out))
'''
run('11_public_process_identity', ['python3', '-c', code])
