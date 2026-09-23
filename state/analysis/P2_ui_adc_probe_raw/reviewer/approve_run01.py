"""Seal exact reviewed D114 run scope after local evidence checks; no board operation."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
COMMIT='9bb947b45c3270364fd827734d91d21fe50ad742'
sha=lambda data:hashlib.sha256(data).hexdigest()
preflight=json.loads((OUT/'run01_preflight.json').read_text())
pins=preflight['file_sha256']
assert len(pins)==11
for name,expected in pins.items():
    path=ROOT/name
    assert path.is_file() and not any(p.is_symlink() for p in (path,*path.parents))
    assert sha(path.read_bytes())==expected,name
subprocess.run(['git','cat-file','-e',COMMIT+'^{commit}'],cwd=ROOT,check=True,capture_output=True)
subprocess.run(['git','diff','--quiet',COMMIT,'--',*pins],cwd=ROOT,check=True,capture_output=True)
subprocess.run(['git','diff','--quiet','bfd4f25','--','src','bench'],cwd=ROOT,check=True,capture_output=True)
for name,expected in preflight['evidence_sha256'].items(): assert sha((ROOT/name).read_bytes())==expected,name
deployment=ROOT/'state/analysis/P2_ui_adc_probe_raw/tool_deployment.json'
assert sha(deployment.read_bytes())=='166e766e9893db1d74b59e1e5687554a21b74fe7909dbb7dcda1665cb9c183a6'
d=json.loads(deployment.read_text())
assert d['status']=='VERIFIED_STAGED_NOT_EXECUTED' and d['serial']=='2629958581'
assert len(d['commands'])==8 and all(c['returncode']==0 and c['stderr']=='' for c in d['commands'])
assert d['remote']==json.loads(d['commands'][-1]['stdout'])
assert d['remote']['destination']==d['destination']=='/home/arduino/sumox26-capture-tools/ui_adc_d114_run01'
assert d['remote']['ancestry']==d['created']['ancestry'] and d['created']['files']==[]
assert d['remote']['ancestry'][-1]['mode']==0o700
assert set(d['local'])==set(d['remote']['files'])=={'ui_adc_capture.py','p0_capture.py','p0_mem_read.cfg'}
for name,row in d['remote']['files'].items():
    assert row['mode']==0o600 and row['sha256']==d['local'][name]['sha256']==pins['tools/'+name]
    assert row['bytes']==d['local'][name]['bytes']==(ROOT/'tools'/name).stat().st_size
runner=ROOT/'state/analysis/P2_ui_adc_probe_capture_run01.py'
assert sha(runner.read_bytes())=='46a1fe34ef2e6ab88c1843cae0201781b6e659e474992c77bd16a8b91e61fa6b'
checks=json.loads((OUT/'capture_orchestrator_checks.json').read_text())
assert checks['verdict']=='PASS_SCOPED_OUTER_CAPTURE_FIXES' and len(checks['checks'])==9
assert checks['script_sha256']==sha(runner.read_bytes())
for name in preflight['absent_at_preflight']:
    path=ROOT/name
    assert not path.exists() and not path.is_symlink(),name
approval=dict(schema_version=1,run_id='d114-ui-adc-01',
    verdict='PASS_EXACT_INERT_ADC_SOURCE_TARGET_CAPTURE_GUARD',
    source_sha256=preflight['source_sha256'],
    elf_sha256='76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b',
    binary_sha256='567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9',
    file_sha256=pins)
data=(json.dumps(approval,indent=2)+'\n').encode()
with (OUT/'run01_approval.json').open('xb') as stream: stream.write(data)
supplement=dict(verdict='PASS_EXACT_RUN01_PREFLIGHT',software_commit=COMMIT,
    approval_sha256=sha(data),tool_deployment_sha256=sha(deployment.read_bytes()),
    capture_orchestrator_sha256=sha(runner.read_bytes()),
    capture_orchestrator_checks_sha256=sha((OUT/'capture_orchestrator_checks.json').read_bytes()),
    closed_outer_findings=[
        'MAJOR: preserve attempted pull argv/status/output on timeout/OSError; fixed and controlled success/error checks passed',
        'MAJOR: finite staged-tool hash timeout plus receipt; fixed30s and controlled timeout check passed',
        'MINOR: bound manifest enumeration/file reads before consuming bytes; stops101st entry and reads size+1, checks passed'],
    original_orchestrator_sha256='dc19619935cd4f078afa82b9122532c630527c7e794e626e9e0c70edfa09496a',
    authority='One user-authorized bare-board diagnostic, fixed source/default/M0/ADB serial2629958581; root creates bound run record before action',
    reviewer='Reused separate same-model; authored guard expectations, relied on separate actual guard source reviewer; independently reviewed capture/source/target',
    board_actions_by_reviewer=False,
    limits='Approval binds software and a single plan, not successful execution/native admission, physical acceptance, calibrated time or human gate')
with (OUT/'run01_final_review.json').open('x',encoding='utf-8') as stream:
    stream.write(json.dumps(supplement,indent=2)+'\n')
print(json.dumps({'verdict':approval['verdict'],'approval_sha256':sha(data),'software_commit':COMMIT}))
