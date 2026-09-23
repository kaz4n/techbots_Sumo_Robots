# Inspect actual D103 target types, reset code and installed thread reservations.
# Offline ELF/DWARF reads never attach, run an inferior or invoke a target API.
# Hash every inspected ELF/tool/config and preserve command output including errors.
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
import board_tool as board

receipt = REPO / 'build/app-receipts/147ff7c62e974466a115cc42e75a5637'
checked = json.loads((receipt / 'verified.json').read_text())
output = REPO / 'state/analysis/P2_service_reset_raw/target_abi'
if len(sys.argv) > 1:
    assert sys.argv[1] == 'caller_path'
    output = output.with_name('target_abi_caller_path')
output.mkdir(parents=True, exist_ok=False)
program = r'''
import hashlib,json,pathlib,subprocess,sys
debug=sys.argv[1]; final=sys.argv[2]
core='/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/'
base=core+'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
config=core+'variants/arduino_uno_q_stm32u585xx/llext-edk/include/zephyr/include/generated/zephyr/autoconf.h'
prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
records=[]
def run(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=30)
    v=dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
    records.append(v); return v
def gdb(elf,queries):
    args=[prefix+'gdb','-nx','-nh','-batch',elf]
    for query in queries: args+=['-ex',query]
    return run(args)
gdb(debug,['set language c++','set max-value-size unlimited',
    'p sizeof(app::Runtime)','p alignof(app::Runtime)',
    'p sizeof(app::Transaction)','p alignof(app::Transaction)',
    'p sizeof(fsm::Robot)','p alignof(fsm::Robot)',
    'p sizeof(recorder::AttemptRecorder)','p sizeof(recorder::FrameBuffer)',
    'ptype /o fsm::Robot'])
gdb(base,['set max-value-size unlimited','p sizeof(z_main_stack)',
    'p sizeof(kheap_llext_heap)','info address z_main_stack','info address z_main_thread',
    'p __llext_sym_z_impl_k_thread_stack_space_get.addr'])
run([prefix+'objdump','-d','--disassemble=_ZN3fsm5Robot5resetEv',final])
run([prefix+'objdump','-d','--disassemble=_ZN3app11Transaction27resetStoppedRobotForServiceEv',final])
run([prefix+'objdump','-d','--disassemble=_ZN3app7Runtime17applyServiceResetEv',final])
run([prefix+'objdump','-d','--disassemble=_ZN3app7Runtime4stepEv',final])
run([prefix+'objdump','-d','--disassemble=llext_bootstrap',base])
names=run([prefix+'nm','-S','-C',base])['stdout'].splitlines()
for line in names:
    symbol=line.split()[-1] if line.split() else ''
    if symbol in ('loader','main') or symbol.startswith('loader.'):
        run([prefix+'objdump','-d','--disassemble='+symbol,base])
paths=[debug,final,base,config,prefix+'gdb',prefix+'objdump',prefix+'nm']
hashes={p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in paths}
text=pathlib.Path(config).read_text()
print(json.dumps(dict(file_sha256=hashes,config_selected=[l for l in text.splitlines()
    if any(k in l for k in ('CONFIG_MAIN_STACK_SIZE','CONFIG_ISR_STACK_SIZE','CONFIG_SYSTEM_WORKQUEUE_STACK_SIZE',
        'CONFIG_IDLE_STACK_SIZE','CONFIG_USERSPACE','CONFIG_INIT_STACKS','CONFIG_THREAD_STACK_INFO'))],
    selected_symbols=[l for l in names if any(k in l for k in ('z_main_stack','z_main_thread',' loader',' main'))],
    commands=records),indent=2))
'''
args = ['python3', '-c', program, checked['build_path'] + '/app.ino_debug.elf',
        checked['build_path'] + '/app.ino.elf']
run = dict(argv=args, source_sha256=checked['source_sha256'],
           start_utc=datetime.now(timezone.utc).isoformat(),
           scope='Board Linux file/offline GDB/objdump only; no compile/upload/reset/MCU')
(output / 'receipt.json').write_text(json.dumps(run, indent=2)+'\n')
result = board.remote(board.target(), args, capture=True, timeout=60)
(output / 'stdout.json').write_text(result.stdout, encoding='utf-8')
(output / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
run.update(returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
(output / 'receipt.json').write_text(json.dumps(run, indent=2)+'\n')
data = json.loads(result.stdout)
for name, digest in data['file_sha256'].items():
    if name in checked['file_sha256']:
        assert digest == checked['file_sha256'][name]
assert all(command['returncode'] == 0 for command in data['commands'])
print(json.dumps(dict(path=str(output.relative_to(REPO)),
                     values=data['commands'][0]['stdout'].splitlines()[:8],
                     stack=data['commands'][1]['stdout'],config=data['config_selected'])))
