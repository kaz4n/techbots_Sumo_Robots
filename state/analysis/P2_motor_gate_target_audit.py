"""Read and disassemble compiled D075 ELF files on board Linux; never attach to MCU."""
import json
import os
from pathlib import Path
import sys

repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo / 'tools'))
import board_tool as board

source = board.source_hash(repo / 'build/stage/p2_motor_gate_compile')
remote_folder = os.environ['SUMO_REMOTE_ROOT'] + '/' + source + '/p2_motor_gate_compile/artifacts'
program = r'''
import hashlib, json, pathlib, subprocess, sys
root = pathlib.Path(sys.argv[1])
prefix = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
results = []
for mode in ('bench-default', 'match-immediate'):
    files = sorted((root / mode).glob('*.elf'))
    if not files:
        raise SystemExit('Missing ELF artifacts for ' + mode)
    for path in files:
        nm = subprocess.run([prefix+'nm', '-C', str(path)], capture_output=True, text=True, check=True)
        obj = subprocess.run([prefix+'objdump', '-d', '-C', str(path)], capture_output=True, text=True, check=True)
        markers = ('motors::MotorGate', 'motorGateProbe', 'p2_motor_gate',
                   'setup()', 'loop()', '<setup>', '<loop>', ' setup', ' loop', '_GLOBAL__sub_I')
        selected = []
        retaining = False
        for line in obj.stdout.splitlines():
            if line.endswith('>:'):
                retaining = any(marker in line for marker in markers)
            if retaining:
                selected.append(line)
        results.append(dict(mode=mode, path=str(path), bytes=path.stat().st_size,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            nm=[line for line in nm.stdout.splitlines() if any(m in line for m in markers)],
            disassembly='\n'.join(selected)))
print(json.dumps(results, indent=2))
'''
result = board.remote(board.target(), ['python3', '-c', program, remote_folder],
                      capture=True, timeout=60)
records = json.loads(result.stdout)
path = repo / 'state/analysis/P2_motor_gate_raw/target_elf_symbols.json'
path.write_text(json.dumps(dict(source_sha256=source, remote_folder=remote_folder,
    command_scope='Linux file read/nm/objdump only; no MCU attach/run',
    returncode=result.returncode, records=records), indent=2) + '\n', encoding='utf-8')
print(json.dumps([dict(mode=r['mode'], bytes=r['bytes'], sha256=r['sha256']) for r in records]))
