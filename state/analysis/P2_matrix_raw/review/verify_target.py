"""Check actual D088 target identity, native bindings and retained masking sequence."""
from pathlib import Path
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
record = ROOT / 'state/analysis/P2_matrix_raw/target_e50c6da3_bench-default.json'
target = json.loads(record.read_text())
staged = json.loads((OUT / 'staged_sources.json').read_text())
assert target['returncode'] == 0 and target['mode'] == 'bench-default'
assert target['source_sha256'] == staged['source_sha256']['bench/ui_matrix']
assert target['source_files'] == staged['file_maps']['bench/ui_matrix']
for name, digest in target['source_files'].items():
    local = ROOT / (name if name.startswith('src/') else 'bench/ui_matrix/' + name)
    assert hashlib.sha256(local.read_bytes()).hexdigest() == digest, name
assert len(target['records']) == 3 and target['math_missing'] == []
for key in ('native_exports', 'math_exports'):
    value = target[key]
    assert value['returncode'] == 0 and not value['stderr']
    pointers = re.findall(r'= (0x[0-9a-fA-F]+)', value['stdout'])
    assert pointers and all(int(p, 16) != 0 for p in pointers)
    assert len(pointers) == len(target['native_names'] if key == 'native_exports' else target['math_symbols'])
assert {'matrixBegin', 'matrixSetGrayscaleBits', 'matrixGrayscaleWrite',
        '__device_dts_ord_233', 'z_impl_device_is_ready'} <= set(target['native_names'])
elf = next(x for x in target['records'] if x['path'].endswith('.ino.elf'))
assert elf['bytes'] == 80592
assembly = elf['disassembly']
methods = {}
for match in re.finditer(r'(?m)^([0-9a-f]+) <(.+)>:\n', assembly):
    after = assembly[match.end():]
    body = after.split('\n\n', 1)[0]
    methods[match.group(2)] = body
for name in ('ui::UnoQMatrix::begin(ui::MatrixGrant)',
             'ui::UnoQMatrix::submit(unsigned int, ui::Frame const&)'):
    text = methods[name]
    assert re.search(r'mrs\s+\w+, CONTROL', text)
    assert re.search(r'mrs\s+\w+, IPSR', text)
    sequence = re.search(r'mrs\s+(\w+), PRIMASK.*?cpsid\s+i.*?blx\s+\w+.*?dmb\s+sy.*?msr\s+PRIMASK, (\w+)', text, re.S)
    assert sequence and sequence.group(1) == sequence.group(2)
    assert 'cpsie' not in text
assert all(name in methods for name in ('setup', 'loop', 'initVariant', '__loopHook()'))
assert not re.search(r'\bblx?\b', methods['initVariant'])
for name, body in methods.items():
    if name.startswith('_GLOBAL__sub_I_') and any(part in name for part in
        ('uiBench', 'imu', 'line_qtr', 'motors', 'opp_sensors', 'power')):
        assert not re.search(r'\bblx?\b', body), name
relocations = elf['relocations']['stdout']
for symbol in ('matrixBegin', 'matrixSetGrayscaleBits', 'matrixGrayscaleWrite', 'z_impl_device_is_ready'):
    assert symbol in relocations
result = dict(status='PASS', target_receipt=str(record.relative_to(ROOT)),
              target_receipt_sha256=hashlib.sha256(record.read_bytes()).hexdigest(),
              source_sha256=target['source_sha256'], source_file_count=len(target['source_files']),
              native_imports=len(target['native_names']), math_imports=len(target['math_symbols']),
              artifacts=[{k:x[k] for k in ('path','bytes','sha256')} for x in target['records']],
              exact_source_map=True, current_local_bytes=True, paired_PRIMASK_registers=True,
              retained_no_io_project_constructors=True,
              limits='Inherited Bridge constructors/loop hook remain present and unqualified for a control tick; no new motor or external acquisition execution is reachable from the bench. This verifies Linux-produced artifacts, not running MCU identity.')
(OUT / 'target_identity.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
selected = ['setup','loop','ui::UnoQMatrix::begin(ui::MatrixGrant)',
            'ui::UnoQMatrix::submit(unsigned int, ui::Frame const&)', 'initVariant', '__loopHook()']
(OUT / 'target_excerpt.txt').write_text('\n\n'.join(name+'\n'+methods[name] for name in selected)+'\n', encoding='utf-8')
print(json.dumps(result, indent=2))
