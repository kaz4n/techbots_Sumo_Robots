"""Bind the independently checked local D104 files; never executes a board action."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
target = json.loads((RAW/'target_2bd817c4.json').read_text())
tests = json.loads((RAW/'host_1790189478371120650.json').read_text())
guards = json.loads((RAW/'capture_guards.json').read_text())
assert guards['successful'] and all(result['returncode']==0 for result in tests['results'])
for name in ('tools/board_tool.py','tools/runtime_capture.py','tools/app_build_policy.py'):
    assert sha(ROOT/name)==tests['copied_hashes'][name]
assert sha(ROOT/'tools/runtime_capture.py')==guards['source_sha256']
old = json.loads(subprocess.check_output(['git','show','6d2ae96:tools/p0_inert_sources.json'],cwd=ROOT,text=True))
current = json.loads((ROOT/'tools/p0_inert_sources.json').read_text())
assert set(current)-set(old)=={'bench/runtime_inert'}
assert all(current[key]==value for key,value in old.items())
assert current['bench/runtime_inert']==target['source_sha256']
pins = json.loads((ROOT/'state/analysis/P2_runtime_inert_raw/target_capture_pins.json').read_text())
assert pins['source_sha256']==target['source_sha256']
assert pins['elf_sha256']==target['elfs'][0]['sha256']
assert pins['package_sha256']==target['package_sha256']
approval = dict(verdict='PASS_SCOPED_SOURCE_AND_CAPTURE_REVIEW',
    source_sha256=target['source_sha256'],elf_sha256=pins['elf_sha256'],
    zsk_sha256=pins['package_sha256'],artifact_dir=pins['artifact_path'],
    capture_sha256=sha(ROOT/'tools/runtime_capture.py'),
    board_tool_sha256=sha(ROOT/'tools/board_tool.py'),
    orchestrator_sha256=sha(ROOT/'state/analysis/P2_runtime_inert_capture_run.py'),
    manifest_sha256=sha(ROOT/'tools/p0_inert_sources.json'),
    serial='2629958581',startup='default',match=0,motors_allowed=0,
    scope='Exact inert absent-source BOOT image and bounded read-only capture only',
    prerequisite='Dated specific run record/source commit before upload; newly compiled ELF/ZSK must reproduce both pins',
    physical_acceptance='Not measured or approved by this review; decode capture separately',
    evidence=['target_2bd817c4.json','host_1790189023168288082.json',
              'host_1790189478371120650.json','capture_guards.json','policy_mutations.json'])
(RAW/'final_approval.json').write_text(json.dumps(approval,indent=2)+'\n')
print(json.dumps(approval,indent=2))
