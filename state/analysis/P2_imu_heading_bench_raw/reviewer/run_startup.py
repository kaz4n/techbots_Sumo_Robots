"""Run only amended native startup/default profiles after the original full suite passed."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import time
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
RAW=OUT.parent
def sha(data): return hashlib.sha256(data).hexdigest()
amendment=json.loads((RAW/'author/startup_amendment.json').read_text())
cases=(ROOT/'tests/tooling/imu_heading_bench_cases.cc').read_bytes()
assert sha(cases)==amendment['after_sha256']=='ffc0a59640a5f82cb27fc09aff231aafc4c4fda46eca6f425019c6e3bcee1fed'
added=amendment['added_case'].encode()
assert cases.count(added)==1 and sha(cases.replace(added,b''))==amendment['before_sha256']
assert sha((ROOT/'tests/tooling/test_imu_heading_bench.py').read_bytes())==amendment['harness_unchanged_sha256']
folder=OUT/('startup_'+str(time.time_ns()));folder.mkdir()
with tempfile.TemporaryDirectory(prefix='d111-startup-review-') as temporary:
    stage=Path(temporary)
    for source,destination in [('src','src'),('bench/imu_heading','bench'),('host/third_party','third_party')]:
        shutil.copytree(ROOT/source,stage/destination)
    (stage/'cases.cc').write_bytes(cases)
    (stage/'harness.py').write_bytes((ROOT/'tests/tooling/test_imu_heading_bench.py').read_bytes())
    (stage/'Arduino.h').write_text('#pragma once\nunsigned long micros();\n')
    (stage/'main.cc').write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
    shutil.copyfile(stage/'bench/imu_heading.ino',stage/'bench/sketch.cpp')
    copied={p.relative_to(stage).as_posix():sha(p.read_bytes()) for p in stage.rglob('*') if p.is_file()}
    assert copied['bench/src/imu_heading_bench.cpp']=='6d3c6c5f5234d995689cc265c65de7848e2bc2dd6b8fa0748e6b2f1cec8ce61f'
    (folder/'source.json').write_text(json.dumps(copied,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('frozen_d111',stage/'harness.py')
    harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
    harness.ROOT=stage;harness.RAW=folder
    case=harness.ImuHeadingBenchTests()
    common=['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror','-fno-exceptions','-fno-rtti',
        '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS','-DD111_TEST_SEPARATE_MAIN','-DMOTORS_ALLOWED=0','-DMATCH=0',
        '-I',stage/'src','-I',stage/'bench/src','-I',stage,'-isystem',stage/'third_party',
        '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
    sources=[stage/'cases.cc',stage/'bench/src/imu_heading_bench.cpp',stage/'src/hal/imu_heading.cpp',
        stage/'src/core/countdown.cpp',stage/'bench/src/imu_heading_bench_native.cpp',stage/'bench/sketch.cpp']
    for label,flags in [('native_normal',[]),('native_san',['-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-no-pie'])]:
        case.execute(common,[*flags,'-DARDUINO_ARCH_ZEPHYR','-DTEST_NATIVE_BINDING'],sources,stage/label,'D111 default sketch*,D111 Native*')
record=dict(verdict='PASS_PRIVATE_ADDITIVE_STARTUP_NATIVE_PROFILES',source_sha256=copied['bench/src/imu_heading_bench.cpp'],
    original_cases=amendment['before_sha256'],amended_cases=amendment['after_sha256'],harness_sha256=amendment['harness_unchanged_sha256'],
    exact_addition_only=True,scope='Both actual Native and default sketch profiles; original full suite retained unchanged.',receipts=str(folder.relative_to(ROOT)))
(OUT/'startup_review.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
