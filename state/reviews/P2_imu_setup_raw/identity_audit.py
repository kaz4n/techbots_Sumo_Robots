"""Reproduce staged-source identities from local bytes without modifying staging."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
base = Path(__file__).resolve().parent

def source_map(sketch):
    origin = root / sketch
    result = {}
    for item in origin.rglob('*'):
        if item.is_file() and item.relative_to(origin).as_posix() != '.gitkeep':
            result[item.relative_to(origin).as_posix()] = item.read_bytes()
    for module in ('core', 'hal'):
        for item in (root / 'src' / module).rglob('*'):
            if item.is_file():
                result[item.relative_to(root).as_posix()] = item.read_bytes()
    result['src/config.h'] = (root / 'src/config.h').read_bytes()
    return result

def identity(sketch):
    contents = source_map(sketch)
    digest = hashlib.sha256()
    for name, data in sorted(contents.items()):
        digest.update(name.encode() + b'\0')
        digest.update(data)
    return dict(hash=digest.hexdigest(), files={name: hashlib.sha256(data).hexdigest()
                for name, data in sorted(contents.items())})

manifest = json.loads((root / 'tools/p0_inert_sources.json').read_text())
assert set(manifest) == {'bench/p0_matrix', 'bench/p0_timing', 'bench/p0_adc',
                         'bench/p0_gpio', 'bench/p0_qtr'}
report = dict(baseline='70b52c5', sketches={key: identity(key) for key in sorted(manifest)})
report['protected_diff'] = subprocess.run(['git', 'diff', '70b52c5', '--', 'src/core',
    'src/app', 'tests/locked', 'tools/board_tool.py'], cwd=root, capture_output=True,
    text=True, check=True).stdout
assert not report['protected_diff'], 'Unexpected protected source change'
if len(sys.argv) == 2:
    target_path = root / sys.argv[1]
    target = json.loads(target_path.read_text())
    current = identity('bench/p2_imu_setup_compile')
    assert target['returncode'] == 0
    assert current['hash'] == target['source_sha256']
    assert current['files'] == target['source_files']
    report['target'] = dict(receipt=sys.argv[1],
        receipt_sha256=hashlib.sha256(target_path.read_bytes()).hexdigest(), **current,
        artifacts=[{'path': r['path'], 'bytes': r['bytes'], 'sha256': r['sha256']}
                   for r in target['records']], native_names=target['native_names'],
        base_sha256=target['base_sha256'])
    final = next(r for r in target['records'] if r['path'].endswith('.ino.elf'))
    (base / 'target_disassembly.txt').write_text(final['disassembly'], encoding='utf-8')
(base / 'identity_audit.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: value['hash'] for key, value in report['sketches'].items()}))
if 'target' in report:
    print('Exact target source map matches: ' + report['target']['hash'])
