"""Execute frozen independent D114 policy tests in an isolated Linux copy."""
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
stage = Path(tempfile.mkdtemp(prefix='d114-author-', dir='/dev/shm'))
for name in ('src', 'tools', 'tests', 'docs', 'bench'):
    shutil.copytree(ROOT/name, stage/name, ignore=shutil.ignore_patterns('__pycache__'))
paths = [stage/'tools/board_tool.py', stage/'tools/app_build_policy.py',
         stage/'bench/ui_adc_probe/ui_adc_probe.ino', stage/'bench/ui/ui.ino',
         stage/'tests/tooling/test_ui_adc_probe_policy.py', stage/'tests/tooling/test_ui_bench_policy.py']
paths += list((stage/'bench/ui/src').glob('*'))
hashes = {str(path.relative_to(stage)):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths if path.is_file()}
(RAW/(label+'_source_copy.json')).write_text(json.dumps({'stage':str(stage),'sha256':hashes},indent=2)+'\n')
runner = stage/'run_cases.py'
runner.write_text('''import json, unittest
from pathlib import Path
suite=unittest.defaultTestLoader.loadTestsFromNames([
    'tests.tooling.test_ui_adc_probe_policy','tests.tooling.test_ui_bench_policy'])
with Path('full.txt').open('w') as output:
    result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
summary={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
         'skipped':len(result.skipped),'success':result.wasSuccessful(),
         'findings':[{'test':str(case),'last_line':trace.strip().splitlines()[-1][:1800]}
                     for case,trace in result.failures+result.errors]}
Path('summary.json').write_text(json.dumps(summary,indent=2)+'\\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
''')
command=[sys.executable,str(runner)]
start=time.time_ns()
result=subprocess.run(command,cwd=stage,capture_output=True,timeout=240)
outcome={'command':command,'cwd':str(stage),'returncode':result.returncode,
         'started_ns':start,'ended_ns':time.time_ns(),
         'stdout':result.stdout.decode(errors='replace'),'stderr':result.stderr.decode(errors='replace')}
(RAW/(label+'_command.json')).write_text(json.dumps(outcome,indent=2)+'\n')
for name in ('full.txt','summary.json'):
    if (stage/name).exists(): shutil.copyfile(stage/name,RAW/(label+'_'+name))
print((stage/'summary.json').read_text() if (stage/'summary.json').exists() else json.dumps(outcome))
