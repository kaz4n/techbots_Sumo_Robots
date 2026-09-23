"""Independently validate local target evidence; never contact its recorded board."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
receipt = ROOT / 'state/analysis/P2_app_transaction_raw/target_9d6c0005_bench-default.json'
data = json.loads(receipt.read_text())
prior_path = ROOT / 'state/analysis/P2_imu_resume_raw/target_b495f085_bench-default.json'
prior = json.loads(prior_path.read_text())
digest = hashlib.sha256()
# board_tool computes its source identity using native Path ordering on Windows.
# README.md therefore sorts after p2_...ino; byte identity remains unchanged.
for name, expected in sorted(data['source_files'].items(), key=lambda pair: Path(pair[0])):
    path = ROOT / name if name.startswith(('src/app/', 'src/core/', 'src/hal/')) or name == 'src/config.h' else ROOT / 'bench/p2_app_transaction_compile' / name
    content = path.read_bytes()
    assert hashlib.sha256(content).hexdigest() == expected, name
    digest.update(name.encode() + b'\0'); digest.update(content)
assert digest.hexdigest() == data['source_sha256']
def imports(record):
    return sorted({line.split()[-1] for line in record['undefined']['stdout'].splitlines()})
old_imports = imports(prior['records'][0])
artifacts = []
required = ('app::Transaction::initialize()', 'app::Transaction::open()',
            'app::Transaction::decide(', 'app::Transaction::finish()',
            'app::Transaction::abort()', 'motors::MotorGate::halt()',
            'motors::MotorGate::apply(', 'fsm::Robot::step(',
            'recorder::AttemptRecorder::consume(', 'app_transaction_probe::exercise(')
for record in data['records']:
    assert all(name in '\n'.join(record['nm']) for name in required)
    assert ' T __loopHook()' in '\n'.join(record['nm'])
    assert imports(record) == old_imports
    artifacts.append(dict(path=record['path'], bytes=record['bytes'], sha256=record['sha256'],
                          imports=len(old_imports), new_imports=[]))
assert data['base_sha256'] == prior['base_sha256']
exports = {}
for key, count in (('native_exports', 40), ('math_exports', 42)):
    result = data[key]
    values = re.findall(r'= 0x([0-9a-f]+)', result['stdout'])
    assert result['returncode'] == 0 and len(values) == count
    assert all(int(value, 16) != 0 for value in values)
    exports[key] = len(values)
assert not data['math_missing']
record = data['records'][0]
rel = re.search(r"Relocation section '\.rel.init_array'.*?(?=\nRelocation section|\Z)", record['relocations']['stdout'], re.S).group(0)
assert 'contains 13 entries' in rel
selected = []
keep = False
for line in record['disassembly'].splitlines():
    if line.endswith('>:'):
        keep = any(name in line for name in ('<setup>', '<loop>', '<__loopHook()>',
                     '_GLOBAL__sub_I', '<app::Transaction::Transaction',
                     '<motors::UnoQPort::port()', '<__aeabi_atexit>'))
    if keep:
        selected.append(line)
(RAW / 'target_startup_excerpt.txt').write_text('\n'.join(selected) + '\n\n' + rel + '\n')
summary = dict(status='PASS_SOURCE_SYMBOL_IMPORT_EXPORT_COMPARISON',
    source_sha256=data['source_sha256'], source_count=len(data['source_files']),
    parent_receipt_sha256=hashlib.sha256(receipt.read_bytes()).hexdigest(),
    prior_receipt_sha256=hashlib.sha256(prior_path.read_bytes()).hexdigest(),
    artifacts=artifacts, exports=exports, unchanged_loader_sha256=data['base_sha256'],
    init_relocations=rel, scope='Local review of captured target compile-only evidence; no MCU action',
    remaining='Actual main disassembly requested in separate additive parent receipt')
(RAW / 'target_review_checks.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('artifacts', 'init_relocations')}, indent=2))
