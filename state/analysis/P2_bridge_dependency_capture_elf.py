"""Preserve exact D098 linked ELF bytes read from the already recorded build paths."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'tools'))
import board_tool as board

source, branch = sys.argv[1:]
if not re.fullmatch('[0-9a-f]{64}', source) or branch not in ('control', 'candidate'):
    raise SystemExit('Expected source SHA256 and isolated branch')
raw = root / 'state/analysis/P2_bridge_dependency_raw'
target = json.loads((raw / f'target_{source[:8]}_{branch}.json').read_text())
destination = raw / (branch + '_elf')
if destination.exists():
    raise SystemExit('Preserve previously downloaded ELF evidence')
paths = [r['path'] for r in target['records']]
program = '''import base64,hashlib,json,pathlib,sys
out=[]
for name in json.loads(sys.argv[1]):
    p=pathlib.Path(name); data=p.read_bytes()
    out.append(dict(path=name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),
                    base64=base64.b64encode(data).decode()))
print(json.dumps(out))
'''
args = ['python3', '-c', program, json.dumps(paths)]
result = board.remote(board.target(), args, capture=True, timeout=30)
downloaded = json.loads(result.stdout)
if len(downloaded) != 3:
    raise SystemExit('Expected exactly three ELF files')
destination.mkdir()
records = []
for item, expected in zip(downloaded, target['records']):
    data = base64.b64decode(item['base64'], validate=True)
    digest = hashlib.sha256(data).hexdigest()
    if item['path'] != expected['path'] or digest != item['sha256'] or digest != expected['sha256']:
        raise SystemExit('Downloaded ELF identity differs from target receipt')
    name = Path(item['path']).name
    if not name.endswith('.elf'):
        raise SystemExit('Unexpected artifact name')
    path = destination / name
    path.write_bytes(data)
    records.append(dict(remote_path=item['path'], local_path=path.relative_to(root).as_posix(),
                        bytes=len(data), sha256=digest))
receipt = dict(status='PASS_DOWNLOADED_EXACT', source_sha256=source, branch=branch,
               argv=args, returncode=result.returncode, files=records,
               scope='Board Linux file reads only; no MCU or upload')
(raw / (branch + '_elf_receipt.json')).write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(dict(status=receipt['status'], branch=branch, files=len(records))))
