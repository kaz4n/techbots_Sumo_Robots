"""Summarize final reviewer receipts without promoting software to physical proof."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
receipt = json.loads((OUT / 'pair_final/receipt.json').read_text())
assert receipt['returncode'] == 0
unchanged = []
for name, digest in receipt['frozen_files'].items():
    if name == 'tools/p0_inert_sources.json':
        continue
    assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    unchanged.append(name)
approval = json.loads((OUT / 'inert_approval.json').read_text())
assert json.loads((ROOT / 'tools/p0_inert_sources.json').read_text()) == approval['approved_existing_keys']
target = json.loads((ROOT / 'state/analysis/P2_adc_pair_raw/target_5f2c2329_bench-default.json').read_text())
upload_elf = next(x for x in target['records'] if 'disassembly' in x)
assembly = upload_elf['disassembly']
blocks = {}
for match in re.finditer(r'^([0-9a-f]+) <(.+)>:\n', assembly, re.M):
    end = re.search(r'^[0-9a-f]+ <.+>:\n', assembly[match.end():], re.M)
    blocks[match.group(2)] = assembly[match.end():match.end()+end.start() if end else len(assembly)]
for name in ('setup', 'loop', '_GLOBAL__sub_I__ZN14adc_pair_probe6readerE',
             '_GLOBAL__sub_I__ZNK5power6Reader13controlsOwnedEv'):
    assert not re.search(r'\sblx?\s', blocks[name]), name
relocations = upload_elf['relocations']['stdout']
selected_relocations = [line for line in relocations.splitlines() if any(s in line for s in (
    '000024ac ', '000024b0 ', '000024b4 ', '00002560 ', '00002564 ', '00002568 ', '0000256c ',
    '0000353c ', '00003540 ', '00003544 ', '.rel.init_array', '_GLOBAL__sub_I'))]
(OUT / 'startup_relocations.txt').write_text('\n'.join(selected_relocations) + '\n')
records = [json.loads(p.read_text()) for p in (OUT / 'pair_final/pair_native').glob('native_power_*.json')]
codes = Counter(r['returncode'] for r in records)
assert set(codes) == {0, 1} and codes[1] == 2
negative = [r for r in records if r['returncode'] == 1]
assert all('Status: FAILURE!' in r['stdout'] for r in negative)
positive_cases = 0
positive_parent_assertions = 0
executions = 0
for r in records:
    if r['returncode'] == 0 and 'Status: SUCCESS!' in r['stdout']:
        executions += 1
        positive_cases += sum(int(x) for x in re.findall(r'test cases:\s+(\d+)\s+\|', r['stdout']))
        positive_parent_assertions += sum(int(x) for x in re.findall(r'assertions:\s+(\d+)\s+\|', r['stdout']))
refusals = [json.loads(p.read_text()) for p in (OUT / 'pair_final/pair_native').glob('upload_refusal_*.json')]
assert len(refusals) == 8 and all(r['target_calls'] == r['remote_calls'] == r['require_transport_calls'] == 0 for r in refusals)
root_checks = {}
for label in ('host_final', 'sanitizer_final', 'tooling_final', 'staging_discovery_final', 'target_final'):
    p = ROOT / 'state/analysis/P2_adc_pair_raw' / (label + '.json')
    data = json.loads(p.read_text())
    assert data['returncode'] == 0
    root_checks[label] = data
assert not subprocess.check_output(['git', 'diff', '--name-only', 'd483268', '--', 'src/core', 'src/app', 'src/hal/motors.cpp', 'tests/locked'], cwd=ROOT, text=True).strip()
record = {'scope': 'Final software evidence only; no board/MCU execution by reviewer',
          'final_native_methods': 15, 'unchanged_frozen_files': len(unchanged),
          'only_excluded_drift': 'tools/p0_inert_sources.json; exact reviewed five-key map adopted',
          'native_command_statuses': dict(codes), 'successful_native_executables': executions,
          'positive_native_cases': positive_cases, 'parent_assertions': positive_parent_assertions,
          'counting_note': 'Parent doctest assertions exclude child-local assertions; no inferred child total',
          'intentional_negative_executions': 2, 'new_probe_upload_refusals': len(refusals),
          'target_source': target['source_sha256'], 'root_success_receipts': root_checks,
          'reviewed_startup': 'setup retains exercise address; loop returns; added translation units only inherited HCI/Bridge memory initialization, no calls',
          'verdict': 'PASS_WITHIN_D086_SOFTWARE_SCOPE_NO_OPEN_FINDING'}
(OUT / 'final_evidence_audit.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k: v for k, v in record.items() if k != 'root_success_receipts'}))
