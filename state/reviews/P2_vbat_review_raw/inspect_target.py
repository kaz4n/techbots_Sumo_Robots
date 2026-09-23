"""Read exact D110 collected ELF references and ABI for independent audit."""
import importlib.util
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
folder = ROOT / 'state/analysis/P2_vbat_raw/target_8e3efb92_bench-default_checked'
audit = json.loads((folder / 'audit.json').read_text())
spec = importlib.util.spec_from_file_location('elf_review', ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
elf = module.Elf(folder / 'vbat.ino.elf')
print(audit['abi']['stdout'])
print('Imports', sorted({r['name'] for r in elf.relocations if r['symbol_section'] == ''}))
print('Account', json.dumps(elf.account(), indent=2))
names = [s for s in elf.symbols if s['size'] and ('vbat' in s['name'] or 'nativeE' in s['name'] or 'runnerE' in s['name'] or '_ZN5power' in s['name'] or s['name'] == '_GLOBAL__sub_I_setup')]
for sym in names:
    start = sym['value'] & ~1
    refs = [r['name'] for r in elf.relocations if r['section'] == sym['section'] and start <= r['offset'] < start + sym['size']]
    print(sym['name'], sym['size'], sym['section'], refs)
row = next(r for r in audit['records'] if r['name'] == 'vbat.ino.elf')
dis = next(c['stdout'] for c in row['commands'] if 'objdump' in c['argv'][0])
(OUT / 'default_disassembly.txt').write_text(dis)
