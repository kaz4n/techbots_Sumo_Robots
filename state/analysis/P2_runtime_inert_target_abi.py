# Inspect the completed D104 ELF's actual diagnostic and owner layouts offline.
# Recheck installed thread/loader ABI and file hashes for separate capture review.
# No inferior, MCU, compilation, upload, reset or hardware command is executed.
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board

assert len(sys.argv) == 2, 'Pass the exact completed final build receipt directory'
receipt = (ROOT / sys.argv[1]).resolve()
checked = json.loads((receipt / 'verified.json').read_text())
assert checked['source_sha256'] == '2bd817c4e535324964a031cdd44720f26fd145a3cd317ab7b3ced089f35db7e5'
assert checked['compiler_returncode'] == 0 and checked['precompile_checks'] is True
output = ROOT / 'state/analysis/P2_runtime_inert_raw/target_abi_2bd817c4'
output.mkdir(parents=True, exist_ok=False)
program = r'''
import hashlib,json,pathlib,subprocess,sys
debug,final=sys.argv[1:]
core='/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/'
base=core+'firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'
binary=core+'firmwares/zephyr-arduino_uno_q_stm32u585xx.bin'
config=core+'variants/arduino_uno_q_stm32u585xx/llext-edk/include/zephyr/include/generated/zephyr/autoconf.h'
prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
records=[]
def run(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=30)
    result=dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
    records.append(result); return result
def gdb(elf,queries):
    args=[prefix+'gdb','-nx','-nh','-batch',elf]
    for query in queries: args+=['-ex',query]
    return run(args)
gdb(debug,['set language c++','set max-value-size unlimited',
    'p sizeof(runtime_bench::Diagnostics)','p alignof(runtime_bench::Diagnostics)',
    'p sizeof(runtime_bench::Report)','p sizeof(runtime_bench::StackSample)',
    'p sizeof(runtime_bench::Runner)','p alignof(runtime_bench::Runner)',
    'p sizeof(app::Runtime)','p sizeof(app::Transaction)','p sizeof(fsm::Robot)',
    'p sizeof(recorder::AttemptRecorder)',
    'ptype /o runtime_bench::Diagnostics','ptype /o runtime_bench::Report',
    'ptype /o runtime_bench::StackSample','ptype /o runtime_bench::Runner'])
gdb(base,['set max-value-size unlimited','p sizeof(struct k_thread)',
    'p (unsigned)&((struct k_thread *)0)->stack_info','p sizeof(z_main_stack)',
    'p sizeof(struct k_heap)','p sizeof(kheap_llext_heap)',
    'info address llext_heap','info address kheap_llext_heap','p llext_heap',
    'p/x __llext_sym_z_impl_k_sched_current_thread_query.addr',
    'p/x __llext_sym_z_impl_k_thread_stack_space_get.addr'])
run([prefix+'objdump','-d','-C',final])
run([prefix+'objdump','-d','--disassemble=z_impl_k_sched_current_thread_query',base])
paths=[debug,final,base,binary,config,prefix+'gdb',prefix+'objdump',prefix+'readelf',
    '/opt/openocd/bin/openocd','/opt/openocd/share/openocd/scripts/target/swj-dp.tcl']
hashes={p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in paths}
text=pathlib.Path(config).read_text()
print(json.dumps(dict(file_sha256=hashes,config_selected=[l for l in text.splitlines()
    if any(k in l for k in ('CONFIG_MAIN_STACK_SIZE','CONFIG_USERSPACE','CONFIG_INIT_STACKS','CONFIG_THREAD_STACK_INFO'))],
    commands=records),indent=2))
'''
args = ['python3', '-c', program, checked['build_path']+'/runtime_inert.ino_debug.elf',
        checked['build_path']+'/runtime_inert.ino.elf']
run = dict(argv=args, source_sha256=checked['source_sha256'], start_utc=datetime.now(timezone.utc).isoformat(),
           scope='Board Linux files/offline GDB and objdump only; no MCU operation')
(output / 'receipt.json').write_text(json.dumps(run, indent=2)+'\n')
result = board.remote(board.target(), args, capture=True, timeout=60)
(output / 'stdout.json').write_text(result.stdout, encoding='utf-8')
(output / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
run.update(returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
(output / 'receipt.json').write_text(json.dumps(run, indent=2)+'\n')
data = json.loads(result.stdout)
for path, digest in data['file_sha256'].items():
    if path in checked['file_sha256']:
        assert digest == checked['file_sha256'][path]
assert result.returncode == 0 and all(c['returncode'] == 0 for c in data['commands'])
(output / 'target_disassembly.txt').write_text(data['commands'][2]['stdout'])
print(json.dumps(dict(path=str(output.relative_to(ROOT)), types=data['commands'][0]['stdout'].splitlines()[:10],
                     loader=data['commands'][1]['stdout'])))
