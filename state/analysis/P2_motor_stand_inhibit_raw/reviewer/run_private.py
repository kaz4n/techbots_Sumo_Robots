"""Run frozen D115 expectations in a copied Linux workspace; preserve every result."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
label = sys.argv[1] if len(sys.argv) > 1 else 'run1'
if (RAW/(label+'_source_copy.json')).exists():
    raise SystemExit('Refusing an existing evidence label')
stage = Path(tempfile.mkdtemp(prefix='d115-author-', dir='/dev/shm'))
for name in ('src', 'tools', 'tests', 'docs', 'bench', 'host'):
    shutil.copytree(ROOT/name, stage/name, ignore=shutil.ignore_patterns('__pycache__', 'build'))
contract = 'state/analysis/P2_motor_stand_inhibit_contract.md'
(stage/contract).parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(ROOT/contract, stage/contract)
paths = [stage/'tools/board_tool.py', stage/'tools/app_build_policy.py', stage/contract,
         stage/'tests/test_motor_stand_inhibit.cpp', stage/'tests/tooling/motor_stand_native_cases.cc',
         stage/'tests/tooling/test_motor_stand_inhibit.py', stage/'tests/tooling/test_motor_stand_inhibit_policy.py',
         stage/'tests/locked/test_motor_gate.cpp', stage/'tests/locked/test_motor_halt.cpp',
         stage/'tests/fixtures/app_transaction_fixture.h', stage/'tests/tooling/test_opp_view_policy.py',
         stage/'host/CMakeLists.txt']
paths += list((stage/'src').rglob('*')) + list((stage/'bench/motor_stand').rglob('*'))
hashes = {str(path.relative_to(stage)):hashlib.sha256(path.read_bytes()).hexdigest()
          for path in paths if path.is_file()}
(RAW/(label+'_source_copy.json')).write_text(json.dumps({'stage':str(stage),'sha256':hashes},indent=2)+'\n')
runner = stage/'run_cases.py'
runner.write_text('''import json, unittest
from pathlib import Path
suite=unittest.defaultTestLoader.loadTestsFromNames([
    'tests.tooling.test_motor_stand_inhibit','tests.tooling.test_motor_stand_inhibit_policy'])
with Path('full.txt').open('w') as output:
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
summary={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
         'skipped':len(result.skipped),'success':result.wasSuccessful(),
         'findings':[{'test':str(case),'last_line':trace.strip().splitlines()[-1][:2200]}
                     for case,trace in result.failures+result.errors]}
Path('summary.json').write_text(json.dumps(summary,indent=2)+'\\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
''')
command=[sys.executable,str(runner)]
started=time.time_ns()
result=subprocess.run(command,cwd=stage,capture_output=True,timeout=600)
outcome={'command':command,'cwd':str(stage),'returncode':result.returncode,
         'started_ns':started,'ended_ns':time.time_ns(),
         'stdout':result.stdout.decode(errors='replace'),'stderr':result.stderr.decode(errors='replace')}
(RAW/(label+'_command.json')).write_text(json.dumps(outcome,indent=2)+'\n')
for name in ('full.txt','summary.json'):
    if (stage/name).exists(): shutil.copyfile(stage/name,RAW/(label+'_'+name))
command_raw=stage/'state/analysis/P2_motor_stand_inhibit_raw/author'
if command_raw.exists(): shutil.copytree(command_raw,RAW/(label+'_commands'))
print((stage/'summary.json').read_text() if (stage/'summary.json').exists() else json.dumps(outcome))
print(outcome['stdout'])
