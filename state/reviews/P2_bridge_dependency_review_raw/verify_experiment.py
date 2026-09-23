"""Validate already captured D098 commands/source bytes without using board_tool."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P2_bridge_dependency_raw'
OUT = Path(__file__).resolve().parent
SOURCE = '570ef35fa0ed25601b5f04097d5e5361545c357d958530d62092c5c5c77c6d84'

def sha(data): return hashlib.sha256(data).hexdigest()

rows = []
for branch in ('control', 'candidate'):
    path = RAW / f'{SOURCE[:8]}_{branch}.json'
    if not path.exists():
        continue
    record = json.loads(path.read_text())
    assert record['source_sha256'] == SOURCE
    assert record['branch'] == branch
    aggregate = hashlib.sha256()
    for name, wanted in sorted(record['source_files'].items()):
        actual_path = ROOT / ('src/app/app.ino' if name == 'app.ino' else name)
        data = actual_path.read_bytes()
        assert sha(data) == wanted, name
        aggregate.update(name.encode()+b'\0')
        aggregate.update(data)
    assert aggregate.hexdigest() == SOURCE
    args = record['argv']
    assert args[:5] == ['arduino-cli','compile','--fqbn','arduino:zephyr:unoq','--verbose']
    assert args[-1].endswith('/'+SOURCE+'/app')
    normalized = []
    i = 0
    while i < len(args):
        if args[i] in ('--build-path','--output-dir'):
            suffix = '/build' if args[i]=='--build-path' else '/artifacts'
            expected = '/_dependency_probes/'+SOURCE+'/'+branch+suffix
            assert args[i+1].endswith(expected)
            normalized += [args[i], '<ISOLATED>'+suffix]
            i += 2
        else:
            normalized.append(args[i]); i += 1
    assert record['source_verification']['output_absent'] is True
    assert record['source_verification']['source_files'] == len(record['source_files'])
    rows.append(dict(branch=branch,source_sha256=SOURCE,source_files=len(record['source_files']),
        receipt_sha256=sha(path.read_bytes()),returncode=record['returncode'],
        argv=normalized,stdout_sha256=sha(path.with_suffix('.stdout.txt').read_bytes()),
        stderr_sha256=sha(path.with_suffix('.stderr.txt').read_bytes())))

if len(rows)==2:
    candidate = rows[1]['argv'][:]
    i = candidate.index('build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=0')
    assert candidate[i-1] == '--build-property'
    del candidate[i-1:i+1]
    assert candidate == rows[0]['argv']
    assert rows[0]['returncode'] == 1
    assert rows[1]['returncode'] == 0

result = dict(scope='Independent local source/command comparison; remote completeness separate',
              branches=rows)
(OUT/'experiment_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({b['branch']:dict(source_files=b['source_files'],returncode=b['returncode']) for b in rows}))
