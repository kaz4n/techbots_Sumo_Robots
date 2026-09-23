"""One identified D113 Linux timeout smoke; root inspects before execution.

No transmitter, UART open, RPC, service mutation, MCU access or retry. Only the
existing receive socket and its immutable receipts are created on board Linux.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import ast
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SERIAL = '2629958581'
PYTHON = Path('C:/Users/narut/AppData/Local/Programs/Python/Python313/python.exe')
ADB = Path('C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
PINS = {
    'dump_match.py': '5a78257ac02733231958477ff7e139bb3a0987ce0fb893446132cc9b05853717',
    'board_tool.py': 'cce5ef3baa8430c26192ee6627d093af02a73a80293f87511b2dcca56168387d',
    'validate_csv_bundle.py': '1c4781fdd0f77a610998644db610bf6adf5a2373d4f32f3ec7ca486185ff52f2',
}
EXECUTABLE_PINS = {
    PYTHON: '29d6486dc5fa86c9d19db9d390fdbb62c4830e2b305761723c0b42e6f3596954',
    ADB: 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982',
    ADB.parent/'AdbWinApi.dll': 'd60103a5e99bc9888f786ee916f5d6e45493c3247972cb053833803de7e95cf9',
    ADB.parent/'AdbWinUsbApi.dll': '25207c506d29c4e8dceb61b4bd50e8669ba26012988a43fbf26a890b1e60fc97',
    ADB.parent/'libwinpthread-1.dll': '6cd4726956f3487453f151b847affad442a81acfcc4cb816b9bcb5ad5e7b6f7c',
}

# Fixed, bounded read-only pre/post inventory; exposes only Monitor TCP rows.
INVENTORY = r'''
import ctypes,json,os,re,stat,subprocess,sys,time
def bounded(path,limit):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        with os.fdopen(fd,'rb',closefd=False) as stream: data=stream.read(limit+1)
        assert len(data)<=limit,path
        return data
    finally: os.close(fd)
ticket=sys.argv[1]
assert re.fullmatch('[0-9a-f]{32}',ticket)
boot=bounded('/proc/sys/kernel/random/boot_id',64).decode('ascii').strip()
assert re.fullmatch('[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}',boot)
tmp=os.lstat('/tmp')
assert stat.S_ISDIR(tmp.st_mode) and tmp.st_uid==0 and tmp.st_mode & stat.S_ISVTX
assert hasattr(ctypes.CDLL(None),'renameat2')
units=['arduino-router.service','arduino-router-serial.service']
properties=['Id','MainPID','ActiveState','SubState','NRestarts','ExecMainStartTimestampMonotonic']
command=['systemctl','show','--no-pager','--property='+','.join(properties),*units]
status=subprocess.run(command,capture_output=True,text=True,timeout=2,stdin=subprocess.DEVNULL)
assert status.returncode==0 and len(status.stdout.encode())<=8192,status.stderr[:512]
services={}
for block in status.stdout.strip().split('\n\n'):
    values=dict(line.split('=',1) for line in block.splitlines())
    assert set(values)==set(properties)
    assert values['ActiveState']=='active' and values['SubState']=='running'
    assert int(values['MainPID'])>0 and int(values['ExecMainStartTimestampMonotonic'])>0
    assert int(values['NRestarts'])>=0
    services[values['Id']]=values
assert set(services)==set(units)
data=bounded('/proc/net/tcp',1048576).decode('ascii')
rows=data.splitlines()
assert data.endswith('\n') and rows and 'local_address' in rows[0] and len(rows)<=4097
selected=[]
for line in rows[1:]:
    fields=line.split()
    assert len(fields)>=10 and re.fullmatch('[0-9]+',fields[9])
    assert all(re.fullmatch('[0-9A-F]{8}:[0-9A-F]{4}',fields[i]) for i in (1,2))
    if fields[1]=='0100007F:1D4C' or fields[2]=='0100007F:1D4C':
        selected.append(dict(local=fields[1],peer=fields[2],state=fields[3],inode=int(fields[9])))
assert any(row['local']=='0100007F:1D4C' and row['state']=='0A' for row in selected)
assert any(row['state']=='01' for row in selected)
print(json.dumps(dict(boot_id=boot,uid=os.getuid(),python=sys.version,
    monotonic_ns=time.monotonic_ns(),services=services,monitor_tcp=selected,
    ticket_path_exists=os.path.lexists('/tmp/sumox26-dump-connection-'+ticket))))
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def source_snapshot(folder):
    for path, expected in EXECUTABLE_PINS.items():
        assert sha(path)==expected, str(path)
    assert os.name=='nt' and Path(sys.executable).resolve()==PYTHON.resolve()
    source={'board_tool.py':HERE/'board_tool.py.baseline',
            'dump_match.py':ROOT/'tools/dump_match.py',
            'validate_csv_bundle.py':ROOT/'tools/validate_csv_bundle.py'}
    folder.mkdir()
    for name, path in source.items():
        assert sha(path)==PINS[name], name
        shutil.copyfile(path, folder/name)
        assert sha(folder/name)==PINS[name], name
    def functions(path):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_bytes()).body
                if isinstance(n,ast.FunctionDef)}
    baseline, current=functions(source['board_tool.py']),functions(ROOT/'tools/board_tool.py')
    names=('fail','setting','target','transport','adb_executable','remote')
    assert all(baseline[name]==current[name] for name in names)
    def imports_and_options(path):
        return [ast.dump(n,include_attributes=False) for n in ast.parse(path.read_bytes()).body
                if isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id in ('ROOT','SSH_OPTIONS') for t in n.targets)]
    assert imports_and_options(source['board_tool.py'])==imports_and_options(ROOT/'tools/board_tool.py')
    return dict(snapshot=PINS,transport_functions_identical=list(names),
                compared_current_helper_sha256=sha(ROOT/'tools/board_tool.py'),
                executables={str(p):expected for p,expected in EXECUTABLE_PINS.items()})


def command(run, label, argv, timeout, env):
    start=datetime.now(timezone.utc).isoformat()
    record=dict(argv=[str(x) for x in argv],timeout_seconds=timeout,start_utc=start,
                start_monotonic_ns=time.monotonic_ns(),returncode=None,timed_out=False)
    try:
        result=subprocess.run(argv,capture_output=True,text=True,timeout=timeout,env=env,
                              stdin=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
        record.update(returncode=result.returncode,stdout=result.stdout,stderr=result.stderr)
    except subprocess.TimeoutExpired as error:
        def text(value): return value.decode('utf-8',errors='replace') if isinstance(value,bytes) else value or ''
        record.update(timed_out=True,stdout=text(error.stdout),stderr=text(error.stderr))
    except OSError as error:
        record.update(stdout='',stderr=str(error))
    record.update(end_utc=datetime.now(timezone.utc).isoformat(),end_monotonic_ns=time.monotonic_ns())
    write(run/(label+'.json'),record)
    return record


def inventory(run, label, ticket, env):
    argv=[str(ADB),'-s',SERIAL,'shell','-T',shlex.join(['python3','-u','-c',INVENTORY,ticket])]
    receipt=command(run,label,argv,5,env)
    assert receipt['returncode']==0 and not receipt['timed_out'], label
    assert len(receipt['stdout'].encode())<=16384,label
    return json.loads(receipt['stdout'])


def assess(run, ticket, before, after, capture, live, terminal):
    problems=[]
    def check(condition, name):
        if not condition: problems.append(name)
    check(capture['returncode']==1 and not capture['timed_out'],'expected capture CLI1 without outer timeout')
    check(before['boot_id']==after['boot_id'] and before['uid']==after['uid'],'Linux identity stable')
    check(before['services']==after['services'],'router and socat service identity stable')
    for row in before['monitor_tcp']:
        if row['state'] in ('01','0A'): check(row in after['monitor_tcp'],'existing Monitor socket unchanged')
    live_json=json.loads(live['stdout']) if live['returncode']==0 else {}
    terminal_json=json.loads(terminal['stdout']) if terminal['returncode']==0 else {}
    check(live_json.get('state')=='CONNECTED','one live observation CONNECTED')
    check(terminal_json.get('state')=='TERMINAL','one post-capture observation TERMINAL')
    for item in (live_json,terminal_json):
        check(item.get('ticket')==ticket and item.get('router_registration')=='UNKNOWN','ticket and unknown registration')
        check(item.get('hardware_permission') is False and item.get('mcu_permission') is False,'permission stays false')
    check(live_json.get('claim')==terminal_json.get('claim') and live_json.get('connection')==terminal_json.get('connection'),'same receiver identity')
    partial=list((run/'capture').glob('*.partial'))
    check(len(partial)==1,'one retained partial capture')
    if len(partial)==1:
        error=json.loads((partial[0]/'error.json').read_text())
        check((partial[0]/'wire.txt').read_bytes()==b'','no unexpected receive bytes')
        check(not list(partial[0].glob('*.csv')) and not (partial[0]/'capture.json').exists(),'no successful log bundle')
        check(error['code']=='TRANSPORT','receive failure remains primary')
        check(error['transport_outcome']['returncode']==1 and not error['transport_outcome']['timed_out'],'remote receiver exits itself')
        evidence=error['connection_evidence']
        check(evidence['state'] is None and evidence['error']['code']=='CONNECTION_METADATA','expected missing-END capture evidence')
        check(evidence['command_outcome']['returncode']==0 and not evidence['command_outcome']['timed_out'],'automatic final query delivered')
        check(evidence['terminal']==terminal_json.get('terminal'),'same automatic and explicit terminal receipt')
    final=terminal_json.get('terminal') or {}
    check(final.get('reason')=='TIMEOUT' and final.get('observed_byte_count')==0,'actual empty timeout terminal')
    claim=terminal_json.get('claim') or {}
    check(claim.get('deadline_monotonic_ns',0)-claim.get('started_monotonic_ns',0)==12000000000,'original 12-second deadline')
    check(claim.get('boot_id')==before['boot_id'] and claim.get('uid')==before['uid'],'claim matches fresh Linux preflight')
    check(final.get('closed_monotonic_ns',-1)>=claim.get('deadline_monotonic_ns',0),'terminal follows actual deadline')
    connection=terminal_json.get('connection') or {}
    check(not any(row['inode']==connection.get('socket_inode') and row['state']=='01' for row in after['monitor_tcp']),'own socket no longer established')
    return dict(verdict='PASS_SCOPED_LINUX_TIMEOUT_SMOKE' if not problems else 'FAIL_OR_INCONCLUSIVE',
                problems=problems,ticket=ticket,hardware_permission=False,mcu_permission=False,
                router_registration='UNKNOWN',scope='Linux TCP/receipt observation only; not UART, firmware or gate acceptance')


def main():
    ticket=uuid.uuid4().hex
    run=HERE/'smoke_runs'/ticket
    run.mkdir(parents=True,exist_ok=False)
    write(run/'intent.json',dict(ticket=ticket,serial=SERIAL,receiver_timeout_seconds=12,
          live_observe_delay_seconds=3,runner_sha256=sha(Path(__file__)),no_retries=True,
          utc=datetime.now(timezone.utc).isoformat()))
    env=dict(os.environ,SUMO_TRANSPORT='adb',SUMO_ADB_SERIAL=SERIAL,SUMO_ADB_EXECUTABLE=str(ADB),
             PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(run/'tools'))
    try:
        write(run/'source_snapshot.json',source_snapshot(run/'tools'))
        state=command(run,'adb_state',[str(ADB),'-s',SERIAL,'get-state'],5,env)
        assert state['returncode']==0 and state['stdout'].strip()=='device' and not state['stderr'].strip()
        before=inventory(run,'before',ticket,env)
        assert not before['ticket_path_exists'],'Fresh ticket path already exists; no reuse'
        tool=[str(PYTHON),'-B',str(run/'tools/dump_match.py')]
        with ThreadPoolExecutor(max_workers=1) as executor:
            future=executor.submit(command,run,'capture_command',tool+['--connection-ticket',ticket,
                '--timeout','12','--output-dir',str(run/'capture')],40,env)
            time.sleep(3)
            live=command(run,'live_observation',tool+['--observe-connection',ticket],10,env)
            capture=future.result()
        terminal=command(run,'terminal_observation',tool+['--observe-connection',ticket],10,env)
        after=inventory(run,'after',ticket,env)
        result=assess(run,ticket,before,after,capture,live,terminal)
    except Exception as error:
        result=dict(verdict='FAIL_OR_INCONCLUSIVE',ticket=ticket,error=repr(error),
                    no_retry=True,hardware_permission=False,mcu_permission=False)
    write(run/'result.json',result)
    write(run/'manifest.json',{p.relative_to(run).as_posix():sha(p) for p in run.rglob('*') if p.is_file()})
    print(json.dumps(dict(path=str(run),**result)))
    return 0 if result['verdict']=='PASS_SCOPED_LINUX_TIMEOUT_SMOKE' else 1


if __name__=='__main__':
    raise SystemExit(main())
