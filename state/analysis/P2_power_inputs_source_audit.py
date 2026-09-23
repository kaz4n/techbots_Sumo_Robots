"""Compare D093 compiled sources and retained paths without accessing hardware."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'state/analysis/P2_power_inputs_raw'
source = sys.argv[1]
if not re.fullmatch('[0-9a-f]{64}', source):
    raise SystemExit('Expected source SHA256')
data = json.loads((RAW / f'target_{source[:8]}_bench-default.json').read_text())
prior = json.loads((ROOT / 'state/analysis/P2_tick_timing_raw/target_5451e99d_bench-default.json').read_text())
stage = ROOT / 'build/stage/p2_power_inputs_compile'
bench = ROOT / 'bench/p2_power_inputs_compile'
files = {}
digest = hashlib.sha256()
for name, expected in sorted(data['source_files'].items(), key=lambda item: Path(item[0])):
    relative = Path(name)
    original = ROOT / relative if name == 'src/config.h' or name.startswith(('src/core/', 'src/hal/')) else bench / relative
    current = hashlib.sha256(original.read_bytes()).hexdigest()
    staged_bytes = (stage / relative).read_bytes()
    staged = hashlib.sha256(staged_bytes).hexdigest()
    if current != staged or current != expected:
        raise SystemExit(f'Source mismatch: {name}')
    digest.update(name.encode() + b'\0')
    digest.update(staged_bytes)
    files[original.relative_to(ROOT).as_posix()] = current
if digest.hexdigest() != source:
    raise SystemExit('Aggregate source identity mismatch')

symbols = ('power::InputOwner::begin()', 'power::InputOwner::readBatteryIfDue(bool)',
           'power::InputOwner::readButtons(bool)', 'power::InputOwner::applyBattery(',
           'power::InputOwner::applyButtons(', 'power::readerInputPort(',
           'power::Reader::beginWithButtons()', 'power::Reader::read()',
           'power::Reader::readButtons()', 'motors::MotorGate::apply(',
           'motors::UnoQPort::settle(', 'fsm::Robot::step(',
           'recorder::AttemptRecorder::consume(', 'power_inputs_probe::exercise(')
artifacts = []
prior_imports = {line.split()[-1] for line in prior['records'][0]['undefined']['stdout'].splitlines()}
for record in data['records']:
    nm = '\n'.join(record['nm'])
    missing = [symbol for symbol in symbols if symbol not in nm]
    if missing:
        raise SystemExit('Required retained symbols absent: ' + repr(missing))
    imports = {line.split()[-1] for line in record['undefined']['stdout'].splitlines()}
    artifacts.append(dict(path=record['path'], sha256=record['sha256'],
                          retained_symbols=list(symbols), import_count=len(imports),
                          added_imports=sorted(imports-prior_imports),
                          removed_imports=sorted(prior_imports-imports)))

assembly = next(record['disassembly'] for record in data['records'] if 'disassembly' in record)
hook = re.search(r'<__loopHook\(\)>:\n(.*?)(?=\n[0-9a-f]+ <|\Z)', assembly, re.S)
if not hook or not re.search(r'\bbx\s+lr', hook[1]) or re.search(r'\bblx?\s', hook[1]):
    raise SystemExit('Strong empty loop hook not demonstrated')
summary = dict(status='PASS_CURRENT_STAGED_TARGET_EXACT', source_sha256=source,
               files=files, artifacts=artifacts, hook=hook.group(0),
               base_sha256=data['base_sha256'],
               base_unchanged_from_D092=data['base_sha256']==prior['base_sha256'],
               scope='Offline source/ELF identity only; no MCU execution or physical proof')
output = RAW / 'source_integrity.json'
if output.exists():
    raise SystemExit('Preserve earlier source receipt; use a distinct retry artifact')
output.write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(dict(status=summary['status'], source_sha256=source, files=len(files),
                     artifacts=len(artifacts), added_imports=[x['added_imports'] for x in artifacts])))
