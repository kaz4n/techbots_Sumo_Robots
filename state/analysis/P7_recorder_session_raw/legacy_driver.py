# Executes unchanged legacy cases only at the changed recorder/receive boundaries.
# New recorder source and tests remain frozen; all subprocesses are local host work.
# Compact command receipts replace disposable executables and duplicated wire copies.
from pathlib import Path
import hashlib,importlib,json,os,subprocess,sys,tempfile,time,unittest
ROOT=Path.cwd();OUT=ROOT/'state/analysis/P7_recorder_session_raw/legacy01'
OUT.mkdir(exist_ok=False)
sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
commands=[]
def run(argv,**options):
    argv=list(map(str,argv));start=time.monotonic()
    result=subprocess.run(argv,capture_output=True,text=True,timeout=240,**options)
    commands.append(dict(argv=argv,returncode=result.returncode,seconds=time.monotonic()-start,stdout=result.stdout,stderr=result.stderr))
    (OUT/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    return result
names=['tests.tooling.test_dump_match','tests.tooling.test_dump_error_retention',
       'tests.tooling.test_dump_connection.ConnectionHostTests','tests.tooling.test_recorder_session_reuse']
def flatten(suite):
    for value in suite:
        if isinstance(value,unittest.TestSuite):yield from flatten(value)
        else:yield value
excluded=('test_actual_cpp_pipeline_stream_roundtrip','test_additive_d088_d089_d090_registry_runs_all_legacy_config_checks')
suite=unittest.TestSuite(t for t in flatten(unittest.defaultTestLoader.loadTestsFromNames(names))
                         if not t.id().endswith(excluded))
with (OUT/'python.stderr').open('w') as log:
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
(OUT/'python.json').write_text(json.dumps(dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),excluded=list(excluded)),indent=2)+'\n')
if not result.wasSuccessful():raise RuntimeError('Legacy receiver test failure; inspect python.stderr')
with tempfile.TemporaryDirectory(prefix='sumox-session-legacy-') as temporary:
    stage=Path(temporary);main=stage/'main.cc';main.write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
    common=['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror','-fno-exceptions','-fno-rtti','-DDOCTEST_CONFIG_NO_EXCEPTIONS','-DMATCH=0','-DMOTORS_ALLOWED=0','-I',ROOT/'src','-I',ROOT,'-I',stage,'-isystem',ROOT/'host/third_party']
    sources=[*sorted((ROOT/'src/core').glob('*.cpp')),*sorted((ROOT/'bench/recorder/src').glob('*.cpp'))]
    sources += [ROOT/'src/hal'/n for n in ('motors.cpp','recorder_frames.cpp','recorder.cpp','recorder_csv.cpp','recorder_dump.cpp')]
    sources += [ROOT/'src/app/transaction.cpp',ROOT/'src/app/transaction_service.cpp']
    binary=stage/'legacy'
    run([*common,*sources,ROOT/'tests/test_recorder_dump.cpp',ROOT/'tests/test_recorder_transport.cpp',main,'-o',binary])
    run([binary,'--no-colors'])
    (stage/'Arduino.h').write_text('#pragma once\nunsigned long micros();\n')
    binary=stage/'disabled'
    run([*common,'-DARDUINO_ARCH_ZEPHYR',*sources,ROOT/'src/app/dump_port_unoq.cpp',
         '-x','c++',ROOT/'bench/recorder/recorder.ino','-x','none',ROOT/'tests/fixtures/recorder_transport/native.cc','-o',binary])
    run([binary])
print(json.dumps(dict(status='PASS',legacy_python=result.testsRun,compiler_commands=len(commands))))
