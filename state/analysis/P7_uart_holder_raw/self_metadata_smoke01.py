import os,json,hashlib
from pathlib import Path
body=Path('tools/observe_uart_holders.py').read_bytes()
ns={'__name__':'uart_holder_host_self_smoke'}
exec(compile(body,'observe_uart_holders.py','exec'),ns)
class SelfOnly(ns['LinuxMetadata']):
 def ids(self,pid=None,tid=None):
  return ([os.getpid()],False) if pid is None else super().ids(pid,tid)
 def boundary(self):
  return {'synthetic_boundary':True,'pid':os.getpid()}
r=ns['observe'](SelfOnly())
assert r['visibility']=='SAMPLED_COMPLETE' and all(not s['holders'] for s in r['sweeps'])
print(json.dumps({'scope':'host self-process proc metadata only; synthetic boundary; no board/device/UART operation','source_sha256':hashlib.sha256(body).hexdigest(),'result':r}))
