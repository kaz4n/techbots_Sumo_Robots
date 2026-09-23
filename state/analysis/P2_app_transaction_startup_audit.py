"""Read omitted startup disassembly from the compiled ELF on board Linux only."""
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board
raw = ROOT / 'state/analysis/P2_app_transaction_raw'
target = json.loads((raw / 'target_9d6c0005_bench-default.json').read_text())
elf = next(r['path'] for r in target['records'] if r['path'].endswith('.ino.elf'))
program = r'''
import json,subprocess,sys
prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
def run(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=30)
 if p.returncode: raise RuntimeError(p.stderr)
 return dict(argv=args,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
assembly=run([prefix+'objdump','-dr','-C',sys.argv[1]])
selected=[]; retain=False
for line in assembly['stdout'].splitlines():
 if line.endswith('>:'):
  retain=any(k in line for k in ('<main>','<__aeabi_atexit>','candidatePeriod','_GLOBAL__sub_I','<setup>','<loop>','__loopHook'))
 if retain: selected.append(line)
assembly['stdout']='\n'.join(selected)
print(json.dumps(dict(disassembly_with_relocations=assembly),indent=2))
'''
args = ['python3', '-c', program, elf]
result = board.remote(board.target(), args, capture=True, timeout=60)
receipt = raw / 'target_startup_additive.json'
if receipt.exists():
    raise SystemExit('Preserve existing additive startup receipt')
receipt.write_text(json.dumps(dict(argv=args, returncode=result.returncode,
    source_sha256=target['source_sha256'], scope='Offline ELF only; no MCU access',
    **json.loads(result.stdout)), indent=2) + '\n')
print(str(receipt.relative_to(ROOT)))
