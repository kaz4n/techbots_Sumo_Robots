"""Independently check captured target source identity and retain startup excerpts."""
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
root = Path(__file__).resolve().parents[3]
raw = Path(__file__).parent
target_path = root / 'state/analysis/P2_imu_resume_raw/target_b495f085_bench-default.json'
target = json.loads(target_path.read_text())
folder = root / 'bench/p2_imu_resume_compile'
files = {p.relative_to(folder).as_posix():p for p in folder.rglob('*') if p.is_file()}
files['src/config.h'] = root / 'src/config.h'
for module in ('core', 'hal'):
    files.update({p.relative_to(root).as_posix():p for p in (root / 'src' / module).rglob('*') if p.is_file()})
actual = {name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in files.items()}
assert actual == target['source_files']
digest = hashlib.sha256()
for name in sorted(files, key=PureWindowsPath):
    digest.update(name.encode() + b'\0'); digest.update(files[name].read_bytes())
assert digest.hexdigest() == target['source_sha256']
assert len(files) == 78 and len(target['records']) == 3
assert not target['math_missing']
exports = {}
for key in ('native_exports', 'math_exports'):
    command = target[key]
    addresses = re.findall(r'^\$\d+ = (0x[0-9a-f]+)$', command['stdout'], re.M)
    assert command['returncode'] == 0 and not command['stderr'] and all(int(a,16) for a in addresses)
    assert len(addresses) == (len(target['native_names']) if key == 'native_exports' else len(target['math_aliases']))
    exports[key] = len(addresses)
required = ('imu::Bus::beginMotion()', 'imu::Bus::advanceMotion()', 'imu::Bus::cancelMotion()',
            'imu::Acquirer::beginRead(', 'imu::Acquirer::advanceRead(', 'imu::Acquirer::cancelRead(',
            'imu::Estimator::observe(', 'fsm::Robot::step(', 'motors::MotorGate::apply(',
            'recorder::AttemptRecorder::consume(', 'imu_resume_probe::exercise(')
for record in target['records']:
    names = '\n'.join(record['nm'])
    assert all(name in names for name in required)
elf = target['records'][0]
assert re.search(r'\bT __loopHook\(\)$', '\n'.join(elf['nm']), re.M)
functions = re.split(r'(?=^[0-9a-f]+ <)', elf['disassembly'], flags=re.M)
selected = [part for part in functions if re.search(r'^[0-9a-f]+ <(?:setup>|loop>|initVariant>|__loopHook\(\)>|_GLOBAL__sub_I|motors::UnoQPort::port\(|motors::MotorGate::MotorGate\()',part)]
startup = '\n'.join(selected)
(raw / 'target_startup_excerpt.txt').write_text(startup + '\n' + elf['relocations']['stdout'])
result = dict(source_sha256=digest.hexdigest(), source_files=len(files), source_match=True,
    target_receipt_sha256=hashlib.sha256(target_path.read_bytes()).hexdigest(), exports=exports,
    artifacts=[{k:r[k] for k in ('path', 'bytes', 'sha256')} for r in target['records']],
    strong_empty_loop_hook=True, exact_required_symbols=True,
    manual_review='Startup excerpts and literal-pool relocations inspected separately; no board command by reviewer')
(raw / 'target_identity.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
