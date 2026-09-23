"""Reconstruct exact target and existing inert source maps without staging writes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
receipt_path = root / sys.argv[1]
receipt = json.loads(receipt_path.read_text())

def sha(data):
    return hashlib.sha256(data).hexdigest()

def composition(sketch):
    path = root / sketch
    files = {}
    for file in path.rglob('*'):
        if file.is_file() and file.name != '.gitkeep':
            files[file.relative_to(path).as_posix()] = file.read_bytes()
    files['src/config.h'] = (root/'src/config.h').read_bytes()
    for module in ('core', 'hal'):
        for file in (root/'src'/module).rglob('*'):
            if file.is_file():
                files[file.relative_to(root).as_posix()] = file.read_bytes()
    return files

def identity(files):
    digest = hashlib.sha256()
    for name, data in sorted(files.items()):
        digest.update(name.encode() + b'\0')
        digest.update(data)
    return digest.hexdigest()

files = composition('bench/p2_imu_acquisition_compile')
source_map = {name: sha(data) for name, data in files.items()}
assert source_map == receipt['source_files'], 'Target source-map mismatch'
assert identity(files) == receipt['source_sha256'], 'Aggregate target identity mismatch'
baseline = json.loads(subprocess.check_output(
    ['git', 'show', 'eb4ff3a:tools/p0_inert_sources.json'], cwd=root, text=True))
expected_keys = {'bench/p0_matrix', 'bench/p0_timing', 'bench/p0_adc',
                 'bench/p0_gpio', 'bench/p0_qtr'}
assert set(baseline) == expected_keys
inert = {}
for sketch in sorted(expected_keys):
    sources = composition(sketch)
    inert[sketch] = {'old_sha256': baseline[sketch], 'candidate_sha256': identity(sources),
                    'files': {name: sha(data) for name, data in sources.items()}}
audit = {'input_receipt': str(receipt_path.relative_to(root)),
         'input_receipt_sha256': sha(receipt_path.read_bytes()),
         'source_sha256': identity(files), 'source_files': source_map,
         'artifacts': [{'path': r['path'], 'sha256': r['sha256'], 'bytes': r['bytes']}
                       for r in receipt['records']],
         'base_sha256': receipt['base_sha256'], 'existing_inert_candidates': inert,
         'approval': 'PENDING manual actual target-startup and retained-method review'}
(out/'identity_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
text_parts = []
for record in receipt['records']:
    if not record['path'].endswith('.ino.elf'):
        continue
    lines = record['relocations']['stdout'].splitlines()
    startup_addresses = ('00000074 ', '00000078 ', '000024fc ', '00002500 ',
                         '00002504 ', '00002508 ', '0000250c ')
    selected = [line for line in lines if line.startswith(startup_addresses)]
    init = False
    for line in lines:
        if line.startswith('Relocation section '):
            init = "'.rel.init_array'" in line
        if init:
            selected.append(line)
    text_parts.append(record['path']+'\n'+record['disassembly']+'\n'+
                      '\n'.join(selected)+'\n'+record['init_array']['stdout'])
text = '\n\n'.join(text_parts)
(out/'target_disassembly.txt').write_text(text)
print(json.dumps({'source_sha256':identity(files), 'source_files':len(files),
                  'artifacts':len(receipt['records']),
                  'existing_inert_candidates':{key:value['candidate_sha256'] for key,value in inert.items()}}))
