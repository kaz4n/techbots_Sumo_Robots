# Records the exact D105 duplicate tables and their installed native source.
# Read-only board Linux file inspection does not touch the MCU or build firmware.
# The D106 reviewer can reproduce byte and normalized relocation identity locally.
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / 'tools'))
import board_tool as board

def sha(data):
    return hashlib.sha256(data).hexdigest()

spec = importlib.util.spec_from_file_location('elf_read',
    REPO / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
path = REPO / 'state/analysis/P2_calibration_delivery_raw/target_4c3487f4_bench-default/app.ino.elf'
elf = module.Elf(path)
tables = []
for symbol in elf.symbols:
    if symbol['name'] != '_ZN6zephyr7arduinoL12arduino_pinsE':
        continue
    section = elf.sections[symbol['section_index']]
    offset = symbol['value'] - section['address']
    data = elf.section_bytes(section)[offset:offset + symbol['size']]
    relocations = [dict(offset=r['offset'] - offset, type=r['type'], name=r['name'],
        symbol_section=r['symbol_section'], symbol_value=r['symbol_value'])
        for r in elf.relocations if r['section'] == symbol['section'] and
        offset <= r['offset'] < offset + symbol['size']]
    tables.append(dict(section=symbol['section'], offset=offset, size=symbol['size'],
        sha256=sha(data), relocations=relocations,
        relocations_sha256=sha(json.dumps(relocations, sort_keys=True).encode())))
assert len(tables) == 4 and all(t['size'] == 560 for t in tables)
assert len({t['sha256'] for t in tables}) == 1
assert len({t['relocations_sha256'] for t in tables}) == 1
assert all(len(t['relocations']) == 70 for t in tables)
proof = dict(elf=str(path.relative_to(REPO)), elf_sha256=sha(path.read_bytes()),
    tables=tables, removed_duplicate_payload_bytes=1680,
    limitation='Gross copied table payload only; final net model and actual RAM not inferred')
(OUT / 'duplicate_tables.json').write_text(json.dumps(proof, indent=2) + '\n')
sources = {}
for name in ['motor_port_unoq.cpp', 'line_qtr.cpp', 'opp_sensors.cpp', 'power.cpp']:
    path = REPO / 'src/hal' / name
    snapshot = OUT / ('before_' + name)
    data = snapshot.read_bytes() if snapshot.exists() else path.read_bytes()
    sources[str(path.relative_to(REPO))] = sha(data)
    if not snapshot.exists():
        snapshot.write_bytes(data)
(OUT / 'before_sources.json').write_text(json.dumps(sources, indent=2) + '\n')

program = r'''
import hashlib,json,pathlib
core=pathlib.Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0')
names=['cores/arduino/wiring_private.h']
files=[]
for name in names:
 p=core/name;raw=p.read_bytes()
 files.append(dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),text=raw.decode()))
print(json.dumps(dict(files=files),indent=2))
'''
args = ['python3', '-c', program]
receipt = dict(argv=args, started_utc=datetime.now(timezone.utc).isoformat(),
    scope='Read-only installed board Linux headers; no compile/upload/reset/MCU')
try:
    result = board.remote(board.target(), args, capture=True, timeout=30)
except subprocess.CalledProcessError as failure:
    result = failure
receipt.update(returncode=result.returncode, ended_utc=datetime.now(timezone.utc).isoformat())
(OUT / 'installed_receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
(OUT / 'installed_stdout.json').write_text(result.stdout, encoding='utf-8')
(OUT / 'installed_stderr.txt').write_text(result.stderr, encoding='utf-8')
assert result.returncode == 0, result.stderr
installed = json.loads(result.stdout)
for file in installed['files']:
    print(file['path'], file['sha256'], file['bytes'])
print('Duplicate tables: 4 x 560 bytes with identical bytes and 70 relocations each')
