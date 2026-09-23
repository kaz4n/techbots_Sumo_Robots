"""Bind the completed D112 scoped review to preserved exact evidence."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
subprocess.run(['python','-B',str(OUT/'review_source.py')],check=True,cwd=ROOT)
source=read(OUT/'source_review.json')
firmware=read(OUT/'firmware_review.json')
policy=read(OUT/'policy_source_review.json')
for p,h in {**policy['hashes'],**policy['unchanged_from_D111']}.items(): assert sha(ROOT/p)==h
for p,h in firmware['frozen_inputs_sha256'].items(): assert sha(ROOT/p)==h
policy_run=read(OUT/'policy_1790198274646835890.json')
assert all(c['returncode']==0 for c in policy_run['commands'])
targets=[read(OUT/('target_bf67d46d_'+mode+'.json')) for mode in ('bench-default','bench-immediate')]
for target in targets: assert target['verdict']=='PASS_EXACT_CHECKED_UI_TARGET_AND_CONDITIONAL_FIT'
assert targets[0]['source_sha256']==targets[1]['source_sha256']
finals=[next(r for r in t['artifacts'] if r['file']=='ui.ino.elf') for t in targets]
assert finals[0]['sha256']==finals[1]['sha256']
evidence=['source_review.json','firmware_review.json','policy_source_review.json',
    'firmware_1790198614083708719.json','policy_1790198274646835890.json',
    'target_bf67d46d_bench-default.json','target_bf67d46d_bench-immediate.json']
superseded=OUT.parent/'target_0b6a559e_bench-default_checked/disposition.json'
assert read(superseded)['status']=='SUPERSEDED_NOT_ACCEPTED_D112_FINAL'
result=dict(verdict='PASS_SCOPED_D112_SOURCE_TESTS_CHECKED_TARGETS',
    utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    independence='Reused separate same-model read-only reviewer; contract-only same-model independent author reused earlier context. Coordinator-authored policy cases separately executed. No human gate claim.',
    source_sha256=source['source_sha256'],contract_sha256=source['contract_sha256'],
    target_source_sha256=targets[0]['source_sha256'],elf_sha256=finals[0]['sha256'],
    targets=[dict(mode=t['mode'],zsk_sha256=t['zsk_sha256'],abi=t['abi'],final=f) for t,f in zip(targets,finals)],
    evidence_sha256={p:sha(OUT/p) for p in evidence},
    superseded_disposition_sha256=sha(superseded),
    closed_findings=[dict(severity='MINOR',issue='sample_seen visibility at A callback',
        disposition='Literal clarified contract and exact two-line reorder before executable freeze; first target preserved superseded.'),
        dict(severity='MINOR',issue='Second freeze predates saved clarified contract',
        disposition='Original retained; later binding addendum verifies unchanged exact sources against clarified contract.')],
    reviewer_harness_failure='Initial source-verifier CRLF assumption failed; LF-aware exact-byte comparison corrected, first script and failure preserved. No product failure/test change.',
    open_findings=[],
    limits=['No MCU upload, reset, readout, active ADC run, wiring approval, loaded-RAM or WCET measurement.',
        'Default and Immediate artifact grants false; no new upload key. Native counted-host substitution is not register behavior.',
        'Synthetic decoder windows do not establish electrical START/BOTH distinction; no long-gesture/matrix/full B6 or phase gate.',
        'Unobserved whole clock wraps and unreachable giant counters remain outside dynamic evidence.',
        'Conditional pristine262144-byte loader model only; historical D109 full-host CTest 2/2 is not a new D112 full-host run.'])
(OUT/'final_review.json').write_text(json.dumps(result,indent=2)+'\n')
report='''# D112 UI raw/decoder bench review

**PASS, scoped source, host tests, checked targets and conditional loader fit. No open BLOCKER/MAJOR/MINOR.**
Reused separate same-model reviewer; production/tests unchanged by review. Separate reused contract-only author; coordinator-authored policy cases. No physical or human gate approval.

- MINOR closed: `bench/ui/src/ui_bench.cpp:158` now saves sample and sample_seen before A. Exact two-line correction `bc2def36` matches clarified contract `2adfd435`; first source/default target retained superseded. Original second-freeze dependency predates the saved clarification and is qualified by the verified later binding addendum.
- Source: one existing Reader, actual decoder once after admitted A, semantic/clock first-cause precedence, truthful failed-read decode pairing, contiguous sequence/source brackets, old-source era through C, immutable publication and bounded saturation. No invented cleanup; disabled/default/terminal paths passive.
- Protected scope: public declarations preserved; 89 other shared sources and 337 prior tests byte-identical. Config/registry each gain only the approved UI_BENCH_SAMPLES = 128 line. Upload manifest unchanged.
- Private WSL tests: unchanged frozen cases/harness, all 30 executed profiles PASS; normal/ASan/UBSan 35 cases/21,759 assertions each; Native 2/27 each; all 16,384 codes in each synthetic configured/overlap profile; capacities/configs/saturation and 3 forbidden-flag refusals. Live registry 5 x 18 checks. Named selection filters intentionally exclude unrelated cases.
- Tooling: private 7 new + 121 previous cases PASS. Literal ui.ino routing only, inert default/Immediate compile, early MATCH/upload/profile refusals and installed recipe/library/artifact verification retained.
- Exact 96-source `bf67d46d`, both checked profiles: ELF `4fa8171d`, 19,840 bytes; one 32 B Native, 9,892 B Runner, 128 x 76 B captures at 148. Sole passive constructor chain; false grant; only beginWithButtons/readButtons rank 10 without voltage computation. No motor/runtime/other sensor/transport owner; empty core thread list and aborting exception stub audited.
- Both target sets: payload 16,245 B; ordered pristine-loader peak 17,128 B; remaining span 245,016 B / largest 245,012 B. Actual source, all 3 ELFs, package bytes, receipts, installed pins and read-only pin-table identity verified. Loader figures are conditional, not loaded-MCU evidence.
- Reviewer verifier correction: preserved initial CRLF assumption failure; LF-aware exact-byte check corrected. No implementation/test amendment resulted.
- Historical full-host `tools/test_host.sh`: D109 private CTest 2/2 PASS retained; no redundant D112 whole-suite claim. No upload/ADC hardware, physical windows, START/BOTH distinction, long gestures, matrix optics, WCET, loaded RAM or phase acceptance established.

Exact identities, commands, test receipts, ELF witnesses, supersession and limitations: `state/analysis/P2_ui_bench_raw/reviewer/final_review.json` and its hashed evidence.
'''
(ROOT/'state/reviews/P2_ui_bench_review.md').write_text(report)
print(result['verdict']); print(sha(OUT/'final_review.json'))
