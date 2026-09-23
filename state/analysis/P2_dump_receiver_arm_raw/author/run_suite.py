"""Run frozen D113 and untouched D090 suites in a private Linux source copy."""
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
selected = sys.argv[2:] or ['tests.tooling.test_dump_connection', 'tests.tooling.test_dump_match']
stage = Path(tempfile.mkdtemp(prefix='d113-author-', dir='/dev/shm'))
for name in ('src', 'tools', 'tests', 'docs'):
    shutil.copytree(ROOT / name, stage / name, ignore=shutil.ignore_patterns('__pycache__'))
paths = list((stage / 'tools').rglob('*.py'))
paths += [stage / 'tests/tooling/test_dump_connection.py', stage / 'tests/tooling/test_dump_match.py',
          stage / 'tests/tooling/test_p0_config.py', stage / 'src/config.h']
hashes = {str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
(RAW / (label+'_source_copy.json')).write_text(json.dumps({'stage':str(stage),'sha256':hashes},indent=2)+'\n')
runner = stage / 'run_frozen_cases.py'
runner.write_text('TEST_NAMES = '+repr(selected)+'\n'+'''import io, json, unittest
from pathlib import Path
from unittest import mock
from tests.tooling import test_p0_config as registry
suite = unittest.defaultTestLoader.loadTestsFromNames(TEST_NAMES)
# D093/D096 already approved additive invocation context; all old methods/assertions stay exact.
approved = {'VBAT_SAMPLE_PERIOD_US':10000,'VBAT_SAMPLE_MAX_AGE_US':20000,
            'APP_QTR_SERVICE_US':600,'APP_SERVICE_MAX_PASSES':8192,'APP_CLOCK_STALL_MAX_POLLS':65536}
with Path('unittest_full.txt').open('w') as log:
    with mock.patch.dict(registry.BEHAVIOR_EXTRA_DEFAULTS, approved):
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
summary = {'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
           'skipped':len(result.skipped),'success':result.wasSuccessful(),
           'approved_additive_registry_context':approved,
           'findings':[{'test':str(case),'last_line':text.strip().splitlines()[-1][:1800]}
                       for case,text in result.failures+result.errors]}
Path('summary.json').write_text(json.dumps(summary,indent=2)+'\\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
''')
command = [sys.executable, str(runner)]
started = time.time_ns()
try:
    result = subprocess.run(command, cwd=stage, capture_output=True, timeout=240)
    outcome = {'returncode':result.returncode,'stdout':result.stdout.decode(errors='replace'),
               'stderr':result.stderr.decode(errors='replace'),'timed_out':False}
except subprocess.TimeoutExpired as failure:
    outcome = {'returncode':None,'stdout':(failure.stdout or b'').decode(errors='replace'),
               'stderr':(failure.stderr or b'').decode(errors='replace'),'timed_out':True}
outcome.update(command=command,cwd=str(stage),started_ns=started,ended_ns=time.time_ns())
for name in ('unittest_full.txt','summary.json'):
    if (stage / name).exists():
        shutil.copyfile(stage / name, RAW / (label+'_'+name))
(RAW / (label+'_command.json')).write_text(json.dumps(outcome,indent=2)+'\n')
if (stage / 'summary.json').exists():
    print((stage / 'summary.json').read_text())
else:
    print(json.dumps({'returncode':outcome['returncode'],'timed_out':outcome['timed_out'],
                      'stage':str(stage),'stderr_last_line':outcome['stderr'].strip().splitlines()[-1:]},indent=2))
