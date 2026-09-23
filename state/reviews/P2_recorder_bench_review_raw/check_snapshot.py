"""Check current/staged/board-retrieved source identity using read-only inputs."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool
RAW = Path(__file__).resolve().parent
target_path = ROOT / 'state/analysis/P2_recorder_bench_raw/target_1502e948_bench-default.json'
data = json.loads(target_path.read_text())
stage = ROOT / 'build/stage/recorder_inert'
observed = {}
for relative, expected in data['source_files'].items():
    if relative == 'recorder_inert.ino' or relative.startswith('src/recorder_'):
        current = ROOT / 'bench/recorder_inert' / relative
    else:
        current = ROOT / relative
    blob = current.read_bytes()
    actual = hashlib.sha256(blob).hexdigest()
    assert expected == actual, f'Current bytes changed: {relative}'
    assert (stage / relative).read_bytes() == blob, f'Staged bytes changed: {relative}'
    observed[relative] = actual
assert set(observed) == {p.relative_to(stage).as_posix() for p in stage.rglob('*') if p.is_file()}
assert board_tool.source_hash(stage) == data['source_sha256']
initializers = []
for record in data['records']:
    assert any(re.match(r'^0000a034 T __loopHook\(\)$', line) for line in record['nm'])
    assert 'z_impl_k_thread_stack_space_get' not in record['undefined']['stdout']
    if record['path'].endswith('.ino.elf'):
        section = record['relocations']['stdout'].split("Relocation section '.rel.init_array'", 1)[1]
        initializers = section.split('Relocation section', 1)[0].splitlines()[2:]
        assert len([line for line in initializers if '_GLOBAL__sub_I' in line]) == 11
        assert '0000e2fc' in record['relocations']['stdout']
        assert '0000a034 <__loopHook()>:\n    a034:\t4770' in record['disassembly']
addresses = re.findall(r'^\$\d+ = (0x[0-9a-f]+)$', data['native_exports']['stdout'], re.M)
assert len(addresses) == len(data['native_names']) == 43 and all(int(x, 16) for x in addresses)
assert int(addresses[data['native_names'].index('z_impl_k_sched_current_thread_query')], 16) == 0x08011ae1
assert data['math_missing'] == []
math_addresses = re.findall(r'^\$\d+ = (0x[0-9a-f]+)$', data['math_exports']['stdout'], re.M)
assert len(math_addresses) == 42 and all(int(x, 16) for x in math_addresses)
report = dict(status='EXACT_SOURCE_AND_TARGET_CHECKED', source_sha256=data['source_sha256'],
              source_files=observed, artifact_records=[{key:r[key] for key in ('path','bytes','sha256')}
                                                        for r in data['records']],
              binary_files=data['binary_files'], native_imports=len(addresses),
              math_imports=len(math_addresses), init_entries=11, strong_empty_loop_hook='0x0000a034',
              source_receipt_sha256=hashlib.sha256(target_path.read_bytes()).hexdigest(),
              board_actions_by_reviewer=False, approval_is_recorded_separately=True)
(RAW / 'source_target_check.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('source_files','artifact_records','binary_files')}, indent=2))
