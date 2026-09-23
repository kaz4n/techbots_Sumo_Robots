"""Execute independent D115 public-contract cases against isolated opaque sources.

Real MotorGate traces and counted Native/sketch binding have separate oracles.
No board action, production body inspection, private seeding or existing-test edit.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'state/analysis/P2_motor_stand_inhibit_raw/author'
STUB=r'''#pragma once
#include "config.h"
#include "hal/motors.h"
#include <cstdlib>
static_assert(MATCH==0 && MOTORS_ALLOWED==0,"D115 inert flags required");
namespace motor_stand_test {
inline unsigned runners=0,begins=0,polls=0;
inline motors::Port copied{};
inline void require(bool value) { if(!value) std::abort(); }
}
namespace motor_stand {
struct Grants { bool exclusive_motor_outputs=false; };
class Runner {
public:
 explicit Runner(const motors::Port& p) {
  motor_stand_test::require(++motor_stand_test::runners==1);
  motor_stand_test::copied=p;
 }
 bool begin(const Grants& g) {
  motor_stand_test::require(!g.exclusive_motor_outputs && ++motor_stand_test::begins==1 && motor_stand_test::polls==0);
  return TEST_BEGIN_RESULT;
 }
 void poll() { motor_stand_test::require(motor_stand_test::begins==1);++motor_stand_test::polls; }
};
}
'''


def receipt(kind,value):
    RAW.mkdir(parents=True,exist_ok=True)
    with (RAW/f'{kind}_{time.time_ns()}.json').open('x',encoding='utf-8') as output:
        json.dump(value,output,indent=2);output.write('\n')


@unittest.skipUnless(os.name=='posix','Compile profiles run in isolated Linux')
class MotorStandInhibitTests(unittest.TestCase):
    def run_command(self,argv,refusal=False):
        argv=list(map(str,argv))
        result=subprocess.run(argv,capture_output=True,text=True,timeout=180)
        receipt('command',{'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        if refusal:
            self.assertNotEqual(result.returncode,0)
            self.assertIn('static assertion failed',result.stderr)
        else: self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        return result

    def test_actual_gate_normal_sanitized_and_unchanged_locked_regressions(self):
        with tempfile.TemporaryDirectory(prefix='d115-gate-',dir='/dev/shm') as temporary:
            stage=Path(temporary);self.copy_inputs(stage)
            common=self.common(stage)+['-DD115_ALLOCATION_GUARD',
                '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
            sources=[stage/'tests/test_motor_stand_inhibit.cpp',stage/'bench/motor_stand/src/motor_stand.cpp',
                     stage/'src/hal/motors.cpp',*sorted((stage/'src/core').glob('*.cpp'))]
            # These established locked assertions run unchanged in the same inert profile.
            sources += [stage/'tests/locked/test_motor_gate.cpp',stage/'tests/locked/test_motor_halt.cpp']
            for label,flags in (('normal',[]),('asan_ubsan',self.sanitizers())):
                binary=stage/label
                self.run_command([*common,*flags,*sources,stage/'main.cc','-o',binary])
                result=self.run_command([binary,'--no-colors','--order-by=file'])
                self.assertIn('Status: SUCCESS!',result.stdout)
                print(label+': '+' | '.join(line for line in result.stdout.splitlines() if 'test cases:' in line or 'assertions:' in line),flush=True)
            for motor,match in ((1,0),(0,1),(1,1)):
                flags=[f for f in self.common(stage) if f not in ('-DMATCH=0','-DMOTORS_ALLOWED=0')]
                self.run_command([*flags,f'-DMATCH={match}',f'-DMOTORS_ALLOWED={motor}',
                    '-fsyntax-only',stage/'bench/motor_stand/src/motor_stand.cpp'],refusal=True)

    def test_actual_native_binding_and_default_sketch_before_setup_and_loops(self):
        with tempfile.TemporaryDirectory(prefix='d115-native-',dir='/dev/shm') as temporary:
            stage=Path(temporary);self.copy_inputs(stage)
            (stage/'bench/motor_stand/src/motor_stand.h').write_text(STUB)
            shutil.copyfile(stage/'bench/motor_stand/motor_stand.ino',stage/'bench/motor_stand/sketch.cpp')
            sources=[stage/'tests/tooling/motor_stand_native_cases.cc',
                     stage/'bench/motor_stand/src/motor_stand_native.cpp',stage/'bench/motor_stand/sketch.cpp']
            for returned in (0,1):
                for label,flags in (('normal',[]),('asan_ubsan',self.sanitizers())):
                    binary=stage/f'native_{label}_{returned}'
                    self.run_command([*self.common(stage),*flags,f'-DTEST_BEGIN_RESULT={returned}',
                                      '-DARDUINO_ARCH_ZEPHYR',*sources,'-o',binary])
                    result=self.run_command([binary]);self.assertEqual(result.stdout,'');self.assertEqual(result.stderr,'')
            for motor,match in ((1,0),(0,1),(1,1)):
                flags=[f for f in self.common(stage) if f not in ('-DMATCH=0','-DMOTORS_ALLOWED=0')]
                self.run_command([*flags,f'-DMATCH={match}',f'-DMOTORS_ALLOWED={motor}',
                    '-DTEST_BEGIN_RESULT=1','-DARDUINO_ARCH_ZEPHYR','-fsyntax-only',
                    stage/'bench/motor_stand/sketch.cpp'],refusal=True)

    @staticmethod
    def sanitizers():
        return ['-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-no-pie']

    @staticmethod
    def common(stage):
        return ['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror',
                '-fno-exceptions','-fno-rtti','-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                '-DMATCH=0','-DMOTORS_ALLOWED=0','-I',stage/'src','-I',stage/'bench/motor_stand/src',
                '-I',stage,'-isystem',ROOT/'host/third_party']

    def copy_inputs(self,stage):
        for folder in ('src','tests','bench/motor_stand'):
            shutil.copytree(ROOT/folder,stage/folder,ignore=shutil.ignore_patterns('__pycache__'))
        (stage/'Arduino.h').write_text('#pragma once\n')
        (stage/'main.cc').write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
        hashes={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest()
                for folder in (stage/'src',stage/'bench/motor_stand') for p in sorted(folder.rglob('*')) if p.is_file()}
        for name in ('tests/test_motor_stand_inhibit.cpp','tests/tooling/motor_stand_native_cases.cc',
                     'tests/locked/test_motor_gate.cpp','tests/locked/test_motor_halt.cpp'):
            hashes[name]=hashlib.sha256((stage/name).read_bytes()).hexdigest()
        receipt('opaque_source_copy',hashes)


if __name__=='__main__':
    unittest.main(verbosity=2)
