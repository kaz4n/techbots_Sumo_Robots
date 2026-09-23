"""Independently compare downloaded failed-link evidence; never access the board."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).parent
before_path = ROOT / 'state/analysis/P2_app_runtime_raw/target_4cb637f9_bench-default.json'
after_path = Path(sys.argv[1]).resolve()
before = json.loads(before_path.read_text())
after = json.loads(after_path.read_text())
paths = {'app.ino': ROOT / 'src/app/app.ino', 'src/config.h': ROOT / 'src/config.h'}
for directory in ('core', 'hal'):
    paths.update({p.relative_to(ROOT).as_posix(): p for p in (ROOT / 'src' / directory).rglob('*') if p.is_file()})
for p in (ROOT / 'src/app').rglob('*'):
    if p.is_file() and p.relative_to(ROOT / 'src/app').parts[0] != 'src' and p.suffix in ('.h', '.hpp', '.c', '.cc', '.cpp'):
        paths[p.relative_to(ROOT).as_posix()] = p
actual = {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in paths.items()}
assert actual == after['source_files'] and len(actual) == 82
digest = hashlib.sha256()
for n, p in sorted(paths.items()): digest.update(n.encode() + b'\0'); digest.update(p.read_bytes())
assert digest.hexdigest() == after['source_sha256']
changed = sorted(n for n in actual if actual[n] != before['source_files'][n])
assert changed == ['src/app/native_sources_unoq.cpp', 'src/hal/imu_acquisition.cpp', 'src/hal/imu_acquisition.h']
assert before['base_sha256'] == after['base_sha256']
assert before['native_names'] == after['native_names']
assert before['math_aliases'] == after['math_aliases']
assert not after['math_missing']
addresses = {}
for kind in ('native_exports', 'math_exports'):
    addresses[kind] = re.findall(r'^\$\d+ = (0x[0-9a-f]+)$', after[kind]['stdout'], re.M)
    assert addresses[kind] == re.findall(r'^\$\d+ = (0x[0-9a-f]+)$', before[kind]['stdout'], re.M)
    assert all(int(a, 16) for a in addresses[kind])
required = ('imu::Acquirer::setupFailure() const', 'imu::Acquirer::beginRead(',
            'imu::Acquirer::advanceRead(', 'imu::Acquirer::cancelRead(',
            'imu::Bus::beginMotion()', 'imu::Bus::advanceMotion()', 'imu::Bus::cancelMotion()',
            'imu::Setup::advance(', 'imu::Bus::readMotion()', 'imu::Bus::readRegister(',
            'imu::Bus::writeRegister(', 'app::Runtime::step()', 'app::NativeSources::port()',
            'motors::MotorGate::apply(', 'recorder::AttemptRecorder::consume(')
removed = ('imu::Acquirer::read(unsigned int)', 'imu::Bus::acquireMotion()')
def sections(r):
    return {m[0]: int(m[1]) for m in re.findall(r'^(\.[\w.]+)\s+(\d+)\s+\d+$', r['size_sections']['stdout'], re.M)}
def inits(r):
    block = re.search(r"Relocation section '\.rel.init_array'.*?(?=\nRelocation section|\Z)", r['relocations']['stdout'], re.S)
    assert block
    return [line.split()[-1] for line in block[0].splitlines() if 'R_ARM_' in line]
records = []
assert len(before['records']) == len(after['records']) == 3
for old, new in zip(before['records'], after['records']):
    imports_old = old['undefined']['stdout'].splitlines()
    imports_new = new['undefined']['stdout'].splitlines()
    assert imports_old == imports_new and len(imports_new) == 188
    names = '\n'.join(new['nm'])
    assert all(name in names for name in required)
    assert not any(name in names for name in removed)
    assert all(name in '\n'.join(old['nm']) for name in removed)
    assert inits(old) == inits(new) and len(inits(new)) == 12
    so, sn = sections(old), sections(new)
    records.append(dict(path=new['path'], sha256=new['sha256'], imports=len(imports_new),
                        sections_before=so, sections_after=sn,
                        deltas={k: sn.get(k, 0) - so.get(k, 0) for k in so.keys() | sn.keys()},
                        required_paths_retained=True, legacy_paths_removed=list(removed),
                        init_targets=inits(new)))
elf = after['records'][0]
assert re.search(r'\bT __loopHook\(\)$', '\n'.join(elf['nm']), re.M)
selected = {}
for name in ('setup', 'loop', 'main', '__loopHook()', '_GLOBAL__sub_I_setup', 'imu::Acquirer::setupFailure() const', 'app::NativeSources::imuSetupFailure(void*, unsigned int)'):
    match = re.search(r'^([0-9a-f]+) <' + re.escape(name) + r'>:(.*?)(?=\n[0-9a-f]+ <|\Z)', elf['disassembly'], re.M | re.S)
    assert match, name
    selected[name] = match[0]
memory_sections = ('.text', '.rodata', '.data', '.bss', '.exported_sym', '.init_array', '.fini_array')
old_memory = sum(records[0]['sections_before'][s] for s in memory_sections)
new_memory = sum(records[0]['sections_after'][s] for s in memory_sections)
result = dict(scope='Offline source and linked cache review only; target size acceptance remains separate',
              target_source_sha256=digest.hexdigest(), source_files=len(actual), changed_from_D096=changed,
              inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (before_path, after_path)},
              base_loader_unchanged=after['base_sha256'], native_exports=len(addresses['native_exports']),
              aeabi_exports=len(addresses['math_exports']), records=records, startup_excerpts=selected,
              memory_before=old_memory, memory_after=new_memory, memory_saved=old_memory-new_memory,
              ram_limit=262144, ram_excess=new_memory-262144,
              target_compile_accepted=False if new_memory > 262144 else None)
out = RAW / 'target_comparison.json'
assert not out.exists(), 'Preserve earlier evidence'
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('records', 'startup_excerpts')}, indent=2))
