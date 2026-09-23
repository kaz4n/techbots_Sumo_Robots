"""Only socket inode metadata/access checks; never connects or sends."""
from pathlib import Path
program = (Path(__file__).resolve().parent / 'collect.py').read_text(encoding='utf-8')
exec(program.split('run("01_identity"')[0])
code = '''from pathlib import Path
import os,json,stat,datetime
p=Path('/var/run/arduino-router.sock');s=p.stat()
print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),path=str(p),mode=oct(s.st_mode),uid=s.st_uid,gid=s.st_gid,is_socket=stat.S_ISSOCK(s.st_mode),write_access=os.access(p,os.W_OK),connected=False)))
'''
run('12_router_socket_metadata', ['python3', '-c', code])
