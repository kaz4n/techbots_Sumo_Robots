"""Prepare exact D114 run pins locally; never create the live approval."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
names=('tools/board_tool.py','tools/app_build_policy.py','tools/app_build_pins.json',
       'tools/app_build_commands.json','tools/ui_adc_run.py','tools/ui_adc_capture.py',
       'tools/p0_capture.py','tools/p0_mem_read.cfg','tools/p0_inert_sources.json',
       'state/analysis/P2_ui_adc_capture_contract.md','state/analysis/P2_ui_adc_run_contract.md')
pins={name:sha((ROOT/name).read_bytes()) for name in names}
assert pins['tools/board_tool.py']=='d1fda9649a30679ed9282d3b03e7a244f8c21ea51b3ded2ad6f7a83c4fb9fcc7'
assert pins['tools/ui_adc_run.py']=='1aa109a2ed068ed4d21dc442aa9195b516f8df264c5a04a0b71a75949cb5d8e8'
assert pins['tools/ui_adc_capture.py']=='f4b3db265bdf2d5a5fdada19ed9f51a44304d9ba5da8be78e598365afa2c4444'
for name in names:
    path=ROOT/name
    assert path.is_file() and not any(p.is_symlink() for p in (path,*path.parents))
original=json.loads(subprocess.run(['git','show','bfd4f25:tools/p0_inert_sources.json'],
    cwd=ROOT,capture_output=True,check=True).stdout)
current=json.loads((ROOT/'tools/p0_inert_sources.json').read_text())
source='396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642'
assert len(original)==8 and current=={**original,'bench/ui_adc_probe':source}
evidence_names=('state/reviews/P2_ui_adc_probe_review.md','state/reviews/P2_ui_adc_capture_review.md',
    'state/reviews/P2_ui_adc_run_review.md','state/analysis/P2_ui_adc_probe_run01_plan.md',
    'state/analysis/P2_ui_adc_probe_raw/artifact_preparation.json',
    'state/analysis/P2_ui_adc_probe_raw/reviewer/final_review.json',
    'state/analysis/P2_ui_adc_probe_raw/capture_reviewer/final_review.json',
    'state/analysis/P2_ui_adc_probe_raw/guard_reviewer/prior145_binding.json',
    'state/analysis/P2_app_build_raw/ui_adc_manifest39.json','state/analysis/P2_app_build_raw/ui_adc_manifest39.txt')
evidence={name:sha((ROOT/name).read_bytes()) for name in evidence_names}
assert evidence['state/reviews/P2_ui_adc_run_review.md']=='5d0b88713fec0b3d3829a501b2485769b2450f2692c254a965dfaac9b417f93c'
assert 'Ran 39 tests' in (ROOT/evidence_names[-1]).read_text()
assert json.loads((ROOT/evidence_names[-2]).read_text())['returncode']==0
preparation=json.loads((ROOT/'state/analysis/P2_ui_adc_probe_raw/artifact_preparation.json').read_text())
assert preparation['returncode']==0 and preparation['target']=='2629958581' and preparation['stderr']==''
prepared=json.loads(preparation['stdout'])
assert prepared['destination']=='/home/arduino/sumox26-capture-input/ui_adc_probe_'+source
assert prepared['MCU_actions'] is False and set(prepared['files'])=={'ui_adc_probe.ino.elf','ui_adc_probe.ino.elf-zsk.bin'}
assert prepared['files']['ui_adc_probe.ino.elf']=={'bytes':19840,'sha256':'76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b'}
assert prepared['files']['ui_adc_probe.ino.elf-zsk.bin']=={'bytes':19840,'sha256':'567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9'}
absent=('state/analysis/P2_ui_adc_probe_run01.json',
        'state/analysis/P2_ui_adc_probe_raw/reviewer/run01_approval.json',
        'state/analysis/P2_ui_adc_probe_raw/run01_upload_attempt.json',
        'state/analysis/P2_ui_adc_probe_raw/run01_upload_outcome.json')
assert all(not (ROOT/name).exists() and not (ROOT/name).is_symlink() for name in absent)
record=dict(status='PREPARED_WAITING_SOFTWARE_COMMIT_AND_TOOL_DEPLOYMENT',
    run_id='d114-ui-adc-01',target='2629958581',transport='adb',file_sha256=pins,
    source_sha256=source,manifest='Exactly one key added; original eight values unchanged',
    evidence_sha256=evidence,absent_at_preflight=list(absent),approval_created=False,
    limits='One explicit reviewed default inert upload plus one separately bounded passive capture; no physical/human gate or cross-model claim')
(OUT/'run01_preflight.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':record['status'],'file_pins':len(pins),'approval_created':False}))
