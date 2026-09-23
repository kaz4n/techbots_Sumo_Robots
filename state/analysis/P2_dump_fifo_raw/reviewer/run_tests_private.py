"""Run independently frozen D117 and unchanged D090/D116 tests in Linux RAM."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[4]
RAW=Path(__file__).resolve().parent
label=sys.argv[1] if len(sys.argv)>1 else 'run1'
selection=sys.argv[2:] or ['tests.tooling.test_dump_uart_fifo',
    'tests.tooling.test_dump_uart_unoq','tests.tooling.test_recorder_transport']
if (RAW/(label+'_source_copy.json')).exists():raise SystemExit('Existing evidence label')
stage=Path(tempfile.mkdtemp(prefix='d117-author-',dir='/dev/shm'))
for name in ('src','tools','tests','docs','bench','host'):
    shutil.copytree(ROOT/name,stage/name,ignore=shutil.ignore_patterns('__pycache__','build'))
for name in ('P2_dump_fifo_contract.md','P2_dump_native_contract.md','P2_recorder_transport_contract.md'):
    target=stage/'state/analysis'/name;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/'state/analysis'/name,target)
wire=Path('state/analysis/P2_recorder_transport_raw/author/run1_commands/normal_exports_1790205416118983952/positive.wire')
(stage/wire).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/wire,stage/wire)
paths=list((stage/'src').rglob('*'))+list((stage/'bench/recorder').rglob('*'))
paths+=list((stage/'tests/fixtures/dump_uart_fifo').rglob('*'))
paths+=list((stage/'tests/fixtures/dump_uart_native').rglob('*'))
paths+=list((stage/'tests/fixtures/recorder_transport').rglob('*'))
paths+=[stage/p for p in ('tools/dump_match.py','tools/validate_csv_bundle.py',
    'tests/tooling/test_dump_uart_fifo.py','tests/tooling/test_dump_uart_unoq.py',
    'tests/tooling/test_recorder_transport.py','tests/test_recorder_transport.cpp')]
paths+=list((stage/'state/analysis').rglob('*'))
hashes={str(path.relative_to(stage)):hashlib.sha256(path.read_bytes()).hexdigest()
    for path in paths if path.is_file()}
(RAW/(label+'_source_copy.json')).write_text(json.dumps({'stage':str(stage),'sha256':hashes},indent=2)+'\n')
runner=stage/'run_cases.py'
runner.write_text('''import json,sys,unittest
from pathlib import Path
suite=unittest.defaultTestLoader.loadTestsFromNames(sys.argv[1:])
with Path('full.txt').open('w') as output:
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
summary={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
    'skipped':len(result.skipped),'success':result.wasSuccessful(),
    'findings':[{'test':str(case),'last_line':trace.strip().splitlines()[-1][:2200]}
        for case,trace in result.failures+result.errors]}
Path('summary.json').write_text(json.dumps(summary,indent=2)+'\\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
''')
command=[sys.executable,str(runner),*selection];started=time.time_ns()
env=dict(os.environ,TMPDIR='/dev/shm')
result=subprocess.run(command,cwd=stage,capture_output=True,timeout=1200,env=env)
outcome={'argv':command,'cwd':str(stage),'returncode':result.returncode,'started_ns':started,
    'ended_ns':time.time_ns(),'stdout':result.stdout.decode(errors='replace'),
    'stderr':result.stderr.decode(errors='replace')}
(RAW/(label+'_command.json')).write_text(json.dumps(outcome,indent=2)+'\n')
for name in ('full.txt','summary.json'):
    if(stage/name).exists():shutil.copyfile(stage/name,RAW/(label+'_'+name))
for name,path in (('new','P2_dump_fifo_raw/author'),('legacy','P2_dump_raw/author'),
                  ('d116','P2_recorder_transport_raw/author')):
    source=stage/'state/analysis'/path
    if source.exists():shutil.copytree(source,RAW/(label+'_'+name))
print((stage/'summary.json').read_text() if (stage/'summary.json').exists() else json.dumps(outcome))
print(outcome['stdout'])
raise SystemExit(result.returncode)
