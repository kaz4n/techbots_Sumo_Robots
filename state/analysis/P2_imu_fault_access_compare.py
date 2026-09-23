"""Compare actual D097 app memory and retained dependencies to the final D096 image."""
import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[2]
raw = root / 'state/analysis/P2_imu_fault_access_raw'
source = sys.argv[1]
if not re.fullmatch('[0-9a-f]{64}', source):
    raise SystemExit('Expected exact D097 source hash')
before = json.loads((root / 'state/analysis/P2_app_runtime_raw/target_4cb637f9_bench-default.json').read_text())
after = json.loads((raw / f'target_{source[:8]}_bench-default.json').read_text())

def upload_elf(data):
    records = [r for r in data['records'] if r['path'].endswith('.ino.elf')]
    if len(records) != 1:
        raise SystemExit('Expected one upload-format linked cache ELF')
    return records[0]

def regions(record):
    return {line.split()[0]: int(line.split()[1])
            for line in record['size_sections']['stdout'].splitlines()
            if re.fullmatch(r'\.[A-Za-z0-9_.]+\s+\d+\s+\d+', line.strip())}

old, new = upload_elf(before), upload_elf(after)
old_regions, new_regions = regions(old), regions(new)
allocated = ('.rodata', '.text', '.data', '.bss', '.exported_sym', '.init_array',
             '.fini_array', '.static_thread_data_area')
old_bytes = sum(old_regions.get(n, 0) for n in allocated)
new_bytes = sum(new_regions.get(n, 0) for n in allocated)
if old_bytes != 276456:
    raise SystemExit('D096 allocation accounting differs from actual size check')
symbols = '\n'.join(new['nm'])
for name in ('imu::Acquirer::read(', 'imu::Bus::acquireMotion()'):
    if name in symbols:
        raise SystemExit('Legacy runtime dependency still retained: ' + name)
if 'imu::Acquirer::setupFailure() const' not in symbols:
    raise SystemExit('Actual accessor missing')
for name in ('imu::Setup::advance(', 'imu::Bus::transfer(',
             'imu::Bus::advanceMotion()', 'imu::Acquirer::advanceRead('):
    if name not in symbols:
        raise SystemExit('Required setup/async path missing: ' + name)
report = dict(status='PASS_EXACT_DEPENDENCY_COMPARISON', source_sha256=source,
              before_source=before['source_sha256'], old_bytes=old_bytes,
              new_bytes=new_bytes, bytes_saved=old_bytes-new_bytes,
              remaining_excess=max(0, new_bytes-262144),
              old_sections=old_regions, new_sections=new_regions,
              loader_unchanged=before['base_sha256']==after['base_sha256'],
              imports_unchanged=old['undefined']['stdout']==new['undefined']['stdout'],
              target_compile_accepted=not after['failed_compile_cache'],
              scope='Actual linked image comparison, not execution, loaded RAM or physical acceptance')
path = raw / 'dependency_comparison.json'
if path.exists():
    raise SystemExit('Preserve earlier comparison receipt')
path.write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report))
