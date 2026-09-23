"""Execute frozen independent D114 capture tests in an isolated local copy."""
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
label = sys.argv[1] if len(sys.argv)>1 else 'run1'
stage = Path(tempfile.mkdtemp(prefix='d114-capture-author-',dir='/dev/shm'))
for name in ('tools','tests'):
    shutil.copytree(ROOT/name,stage/name,ignore=shutil.ignore_patterns('__pycache__'))
target=Path('state/analysis/P2_ui_adc_probe_raw/target_396bcc45_bench-default_checked')
(stage/target).mkdir(parents=True)
for name in ('ui_adc_probe.ino.elf','ui_adc_probe.ino.elf-zsk.bin'):
    shutil.copyfile(ROOT/target/name,stage/target/name)
inputs=Path('state/analysis/P2_ui_adc_probe_raw/root_capture_inputs')
(stage/inputs).mkdir(parents=True)
for suffix in ('.elf','.bin'):
    name='zephyr-arduino_uno_q_stm32u585xx'+suffix
    shutil.copyfile(ROOT/inputs/name,stage/inputs/name)
paths=['tools/ui_adc_capture.py','tools/p0_capture.py','tools/p0_mem_read.cfg',
       'tests/tooling/test_ui_adc_capture.py',str(target/'ui_adc_probe.ino.elf'),
       str(target/'ui_adc_probe.ino.elf-zsk.bin'),
       str(inputs/'zephyr-arduino_uno_q_stm32u585xx.elf'),str(inputs/'zephyr-arduino_uno_q_stm32u585xx.bin')]
hashes={name:hashlib.sha256((stage/name).read_bytes()).hexdigest() for name in paths}
(RAW/(label+'_source_copy.json')).write_text(json.dumps({'stage':str(stage),'sha256':hashes},indent=2)+'\n')
runner=stage/'run_cases.py'
runner.write_text('''import importlib,json,os,socket,subprocess,sys,unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock
sys.path.insert(0,str(Path.cwd()/'tools'))
with ExitStack() as guard:
 for name in ('run','Popen','call','check_call','check_output'):
  guard.enter_context(mock.patch.object(subprocess,name,side_effect=AssertionError('Import process side effect')))
 for name in ('socket','create_connection'):
  guard.enter_context(mock.patch.object(socket,name,side_effect=AssertionError('Import network side effect')))
 guard.enter_context(mock.patch.object(os,'system',side_effect=AssertionError('Import shell side effect')))
 importlib.import_module('ui_adc_capture')
suite=unittest.defaultTestLoader.loadTestsFromName('tests.tooling.test_ui_adc_capture')
with Path('full.txt').open('w') as output:
 result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
summary={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
 'skipped':len(result.skipped),'success':result.wasSuccessful(),
 'findings':[{'test':str(case),'last_line':trace.strip().splitlines()[-1][:3000]}
             for case,trace in result.failures+result.errors]}
Path('summary.json').write_text(json.dumps(summary,indent=2)+'\\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
''')
command=[sys.executable,str(runner)]
start=time.time_ns()
result=subprocess.run(command,cwd=stage,capture_output=True,timeout=240)
record={'command':command,'cwd':str(stage),'returncode':result.returncode,
        'started_ns':start,'ended_ns':time.time_ns(),'stdout':result.stdout.decode(errors='replace'),
        'stderr':result.stderr.decode(errors='replace')}
(RAW/(label+'_command.json')).write_text(json.dumps(record,indent=2)+'\n')
for name in ('full.txt','summary.json'):
    if (stage/name).exists(): shutil.copyfile(stage/name,RAW/(label+'_'+name))
print((stage/'summary.json').read_text() if (stage/'summary.json').exists() else json.dumps(record))
