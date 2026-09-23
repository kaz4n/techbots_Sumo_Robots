"""Bind D112 source findings to the second freeze, unchanged public API and protected files."""
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
RAW=OUT.parent
def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return json.loads(path.read_text())
freeze=read(RAW/'worker/second_source_freeze.json')
source={}
for row in freeze['files']:
    blob=(ROOT/row['path']).read_bytes()
    assert sha(blob)==row['sha256']
    assert blob==(RAW/'worker/second_sources'/row['path']).read_bytes()
    source[row['path']]=row['sha256']
first=(RAW/'worker/first_sources/bench/ui/src/ui_bench.cpp').read_bytes()
current=(ROOT/'bench/ui/src/ui_bench.cpp').read_bytes()
newline=b'\r\n' if b'\r\n' in first else b'\n'
old=b'    const auto returned = port_.clockUs(port_.context);'+newline+b'    report_.sample_seen = true;'
new=b'    report_.sample_seen = true;'+newline+b'    const auto returned = port_.clockUs(port_.context);'
assert first.count(old)==1 and first.replace(old,new)==current
contract=sha((ROOT/'state/analysis/P2_ui_bench_contract.md').read_bytes())
clarification=read(RAW/'sample_seen_clarification.json')
assert contract==clarification['after_contract_sha256']=='2adfd43546f2deba17ff852352d1c6b5c1c3f98bb32e7e75042bea0227bc00a2'
binding=read(RAW/'worker/second_clarified_contract_binding.json')
assert binding['clarified_contract_sha256']==contract
assert binding['original_contract_sha256']==freeze['contract_sha256']
assert {row['path']:row['sha256'] for row in binding['source_files_unchanged']}==source
def git(path):
    return subprocess.run(['git','show','e898cf3:'+path],cwd=ROOT,capture_output=True,check=True).stdout.replace(b'\r\n',b'\n')
public='bench/ui/src/ui_bench.h'
actual=(ROOT/public).read_bytes().replace(b'\r\n',b'\n').replace(b'#include "config.h"\n',b'')
assert actual.split(b'private:')[0]==git(public).split(b'private:')[0]
native='bench/ui/src/ui_bench_native.h'
assert (ROOT/native).read_bytes().replace(b'\r\n',b'\n')==git(native)
prior_dir=ROOT/'state/analysis/P2_imu_heading_bench_raw/target_sources_9520e473'
prior=read(prior_dir/'manifest.json')['source_files']
shared={p:h for p,h in prior.items() if p.startswith('src/') and (ROOT/p).is_file()}
assert len(shared)==90
assert [p for p,h in shared.items() if sha((ROOT/p).read_bytes())!=h]==['src/config.h']
addition=b'inline constexpr std::uint32_t UI_BENCH_SAMPLES = 128U; // D112 finite raw/decoder capture; count exception\r\n'
assert (ROOT/'src/config.h').read_bytes().replace(addition,b'')==(prior_dir/'src/config.h').read_bytes()
before=(RAW/'registry/test_p0_config_before.py').read_bytes()
after=(ROOT/'tests/tooling/test_p0_config.py').read_bytes()
literal=b"    'UI_BENCH_SAMPLES': 128,  # D112 finite A1 raw/decoder evidence count.\n"
assert after.count(literal)==1 and after.replace(literal,b'')==before
assert after==(RAW/'registry/test_p0_config_after.py').read_bytes()
old_tests=read(ROOT/'state/analysis/P2_imu_heading_bench_raw/reviewer/firmware_1790197445705089414.json')['copied_hashes']
# Later reviewed D111 startup-only addition and the separate two-path registry repair.
old_tests['tests/tooling/imu_heading_bench_cases.cc']='ffc0a59640a5f82cb27fc09aff231aafc4c4fda46eca6f425019c6e3bcee1fed'
old_tests['tests/tooling/test_imu_heading_bench.py']='cb9413f1f752420b8f281443b29c48484f9d413aaab0d8c24ee7dc6b891068e0'
old_tests['tests/tooling/test_vbat.py']='365318a6a0990dbf342ba6221a6034c706dc05463632ccae0537ff60eb747841'
unchanged=[]
for path,expected in old_tests.items():
    if path.startswith('tests/') and path!='tests/tooling/test_p0_config.py':
        assert sha((ROOT/path).read_bytes())==expected,path
        unchanged.append(path)
result=dict(verdict='PASS_SCOPED_SECOND_FREEZE_SOURCE_REVIEW_PENDING_TESTS_TARGET',source_sha256=source,
    contract_sha256=contract,freeze_reported_contract_sha256=freeze['contract_sha256'],public_API_unchanged=True,
    clarified_binding_sha256=sha((RAW/'worker/second_clarified_contract_binding.json').read_bytes()),
    private_config_header_include=True,unchanged_shared_source_files=89,unchanged_prior_test_files=len(unchanged),
    registry=dict(before_sha256=sha(before),after_sha256=sha(after),exact_added_bytes=len(literal)),
    resolved_ordering='Actual sample and sample_seen committed before A callback; exact two-line reorder only. No decoder/validation before A.',
    inspected=['single Reader beginWithButtons/readButtons, passive default grant and no cleanup API',
        'setup/grant/port/config precedence; raw enum/shape faults selected before A chronology',
        'actual decoder exactly once for admitted A even on raw failure; bad A retains older decode with pairing false',
        'first/contiguous sequence and S..source..A strict source duration',
        'old source era retained through C; cumulative half-range checks and reanchor only after healthy publication',
        'missed count at S, early/no-read historical fields, distinct setup/read/poll timing',
        'bounded fixed captures and immutable published prefix; failed C hides tentative slot',
        'attempted-overflow saturation arithmetic, terminal fresh clearing and no invented stop'],
    limits='Independent executable tests and exact checked targets pending; no hardware or future artifact approval.')
(OUT/'source_review.json').write_text(json.dumps(result,indent=2)+'\n')
print(result['verdict']);print('Unchanged prior tests:',len(unchanged))
