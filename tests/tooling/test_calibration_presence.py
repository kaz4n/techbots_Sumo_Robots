# Compiles independent D083 tests against opaque actual countdown implementation.
# Isolated host runs verify admission, inert sketch startup and upload refusal.
# Commands, source hashes, stdout, stderr and statuses are retained as author receipts.
from contextlib import ExitStack, redirect_stderr
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
MAIN = '#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n'
COUNTERS = r'''
// Counts linked allocation and clock entry across constructors and runtime.
// True constant initialization retains startup evidence without a counter reset.
// Checks surround only the target body, excluding final diagnostic printing.
#include <cstddef>
#include <cstdlib>
#include <new>
bool guard_allocations = true;
unsigned allocations, io_calls;
extern "C" void* __real_malloc(std::size_t);
extern "C" void* __real_calloc(std::size_t,std::size_t);
extern "C" void* __real_realloc(void*,std::size_t);
extern "C" void __real_free(void*);
extern "C" void* __wrap_malloc(std::size_t n) { if(guard_allocations) ++allocations; return __real_malloc(n); }
extern "C" void* __wrap_calloc(std::size_t n,std::size_t s) { if(guard_allocations) ++allocations; return __real_calloc(n,s); }
extern "C" void* __wrap_realloc(void* p,std::size_t n) { if(guard_allocations) ++allocations; return __real_realloc(p,n); }
extern "C" void __wrap_free(void* p) { if(guard_allocations) ++allocations; __real_free(p); }
void* operator new(std::size_t n) { auto p=__wrap_malloc(n); if(!p) std::abort(); return p; }
void* operator new[](std::size_t n) { return operator new(n); }
void operator delete(void* p) noexcept { __wrap_free(p); }
void operator delete[](void* p) noexcept { __wrap_free(p); }
void operator delete(void* p,std::size_t) noexcept { __wrap_free(p); }
void operator delete[](void* p,std::size_t) noexcept { __wrap_free(p); }
unsigned long micros() { ++io_calls; return 0U; }
unsigned long millis() { ++io_calls; return 0U; }
void delay(unsigned long) { ++io_calls; }
void delayMicroseconds(unsigned int) { ++io_calls; }
'''

PROBE = r'''
// Verifies the actual compile-only sketch never calls its retained exercise entry.
// Checks all exposed default inputs and result fields in both build modes.
// Constructors, setup and 10000 loops retain zero allocation and clock counts.
#include "src/core/countdown.h"
#include <cstdio>
#include <cstdlib>
extern bool guard_allocations;
extern unsigned allocations, io_calls;
void setup(); void loop();
namespace calibration_probe {
extern countdown::Lifecycle lifecycle;
extern countdown::ServiceSample sample;
extern countdown::LifecycleResult result;
extern core::ButtonLevel button;
extern float previous_bias_dps;
extern bool stop_requested;
extern unsigned exercise_calls;
extern void (*volatile entry)();
void exercise();
}
#define VERIFY(x) do { if(!(x)) { std::fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); std::exit(1); } } while(false)
void verifyDefaults() {
    using namespace calibration_probe;
    VERIFY(exercise_calls==0U); VERIFY(allocations==0U); VERIFY(io_calls==0U);
    VERIFY(sample.t_us==0U && sample.raw_gyro_z_dps==0.0F && !sample.imu_ok);
    VERIFY(sample.line_mask==0U && sample.confirmed_opp_mask==0U);
    VERIFY(sample.gyro_presence==countdown::GyroPresence::LEGACY);
    VERIFY(sample.gyro_observation_us==0U && sample.gyro_sequence==0U);
    VERIFY(button==core::ButtonLevel::NONE && previous_bias_dps==0.0F && !stop_requested);
    VERIFY(result.gate.phase==countdown::Phase::IDLE && !result.gate.motion_permitted);
    VERIFY(!result.gate.start_release && !result.gate.go && result.gate.release_us==0U);
    VERIFY(!result.services.active && !result.services.finished);
    VERIFY(!result.services.calibration_finished && !result.services.calibration_rejected);
    VERIFY(result.services.calibration_samples==0U && result.services.bias_dps==0.0F);
    VERIFY(!result.services.line_warning && result.services.opponent_snapshot==0U);
    VERIFY(!result.heading_reset_requested && !result.service_start_failed);
}
int main() {
    VERIFY(calibration_probe::entry==nullptr); verifyDefaults();
    setup(); VERIFY(calibration_probe::entry==&calibration_probe::exercise); verifyDefaults();
    for(unsigned i=0U;i<10000U;++i) { loop(); verifyDefaults(); }
    VERIFY(calibration_probe::entry==&calibration_probe::exercise);
    guard_allocations=false;
    std::puts("PASS inert constructors setup 10000 loops exercise_calls=0 allocations=0 clock_calls=0");
}
'''

ALLOCATION = r'''
// Runs actual Services and Lifecycle through explicit calibration and cancellation.
// Exercises admitted, absent, duplicate, invalid, rejection and reset paths.
// Counts ordinary C/C++ allocation and clock calls across 10000 attempts.
#include "core/countdown.h"
#include <cstdio>
#include <cstdlib>
#include <limits>
extern bool guard_allocations;
extern unsigned allocations, io_calls;
#define VERIFY(x) do { if(!(x)) { std::fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); std::exit(1); } } while(false)
int main() {
    {
        countdown::Services services;
        countdown::Lifecycle lifecycle;
        for(std::uint32_t i=0U;i<10000U;++i) {
            const auto release=i*10000000U;
            VERIFY(services.start(release,-7.0F));
            countdown::ServiceSample s;
            s.t_us=release+config::CAL_START_MS*1000U;
            s.gyro_presence=countdown::GyroPresence::ABSENT;
            services.step(s);
            s.t_us+=1U; s.gyro_observation_us=s.t_us; s.gyro_sequence=0U;
            s.gyro_presence=countdown::GyroPresence::VALID;
            VERIFY(services.step(s).calibration_samples==1U);
            s.t_us+=1U; VERIFY(services.step(s).calibration_samples==1U);
            s.t_us+=1U; s.gyro_observation_us=s.t_us; s.gyro_sequence=1U;
            VERIFY(services.step(s).calibration_samples==2U);
            s.t_us+=1U; s.gyro_presence=countdown::GyroPresence::INVALID;
            services.step(s);
            s.t_us=release+config::CAL_END_MS*1000U;
            VERIFY(services.step(s).calibration_rejected);
            services.cancel(); services.reset();
            VERIFY(!services.start(release,std::numeric_limits<float>::quiet_NaN()));
            lifecycle.step(s,core::ButtonLevel::NONE,0.0F,true);
            VERIFY(lifecycle.buttonEvents().start_release==false);
            lifecycle.reset();
        }
    }
    VERIFY(allocations==0U); VERIFY(io_calls==0U); guard_allocations=false;
    std::puts("PASS 10000 attempts allocations=0 clock_calls=0");
}
'''


class CalibrationPresenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++')
        if compiler is None:
            raise RuntimeError('D083 requires Linux/WSL g++')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-d083-', dir='/dev/shm')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.receipts = Path(os.environ.get('SUMO_CALIBRATION_RECEIPT_DIR',
            ROOT/'state/analysis/P2_calibration_presence_raw/author'))
        cls.receipts.mkdir(parents=True, exist_ok=True)
        cls.base = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti']
        cls.ordinal = 0
        cls.link_wrap = ['-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']

    def command(self, argv, paths):
        manifest = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        result = subprocess.run(list(map(str, argv)), text=True, capture_output=True, timeout=120)
        payload = {'argv': list(map(str, argv)), 'returncode': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr, 'sha256': manifest,
                   'capture': 'subprocess text=True; newline normalized'}
        (self.receipts/f'command_{time.time_ns()}.json').write_text(json.dumps(payload, indent=2)+'\n')
        self.assertEqual(result.returncode, 0, (result.stdout+result.stderr)[:8000])
        return result

    def stage_sources(self):
        self.__class__.ordinal += 1
        stage = self.stage/f'case-{self.ordinal}'
        (stage/'src/core').mkdir(parents=True)
        # Production source is copied and hashed opaquely, never opened for derivation.
        for name in ('countdown.cpp', 'countdown.h', 'types.h'):
            shutil.copyfile(ROOT/'src/core'/name, stage/'src/core'/name)
        shutil.copyfile(ROOT/'src/config.h', stage/'src/config.h')
        return stage

    def focused(self, sanitizer):
        stage = self.stage_sources()
        main = stage/'main.cc'; main.write_text(MAIN)
        case = ROOT/'tests/test_calibration_presence.cpp'
        sources = [main, case, stage/'src/core/countdown.cpp']
        inputs = [p for p in stage.rglob('*') if p.is_file()] + [case]
        binary = stage/'focused'
        flags = ['-fsanitize=address,undefined', '-fno-sanitize-recover=all'] if sanitizer else []
        self.command([*self.base, *flags, '-DDOCTEST_CONFIG_NO_EXCEPTIONS',
            '-I', stage/'src', '-isystem', ROOT/'host/third_party', *sources, '-o', binary], inputs)
        result = self.command([binary, '--no-colors'], inputs)
        self.assertIn('Status: SUCCESS!', result.stdout)
        print(result.stdout, flush=True)

    def test_b3_d083_spec_derived_focused_host(self):
        self.focused(False)

    def test_b3_d083_spec_derived_focused_address_undefined_sanitizers(self):
        self.focused(True)

    def test_b3_d083_actual_probe_inert_constructors_setup_and10000loops(self):
        for enabled in (0, 1):
            with self.subTest(enabled=enabled):
                stage = self.stage_sources()
                shutil.copyfile(ROOT/'bench/p2_calibration_compile/p2_calibration_compile.ino',
                                stage/'probe.ino')
                case = stage/'check.cc'; case.write_text(PROBE)
                counters = stage/'counters.cc'; counters.write_text(COUNTERS)
                inputs = [p for p in stage.rglob('*') if p.is_file()]
                binary = stage/'probe'
                self.command([*self.base, '-fsanitize=undefined', '-fno-sanitize-recover=all',
                    f'-DMATCH={enabled}', f'-DMOTORS_ALLOWED={enabled}',
                    '-I', stage, '-I', stage/'src', '-x', 'c++', stage/'probe.ino',
                    stage/'src/core/countdown.cpp', case, counters, *self.link_wrap, '-o', binary], inputs)
                self.assertIn('exercise_calls=0 allocations=0 clock_calls=0',
                              self.command([binary], inputs).stdout)

    def test_b3_d083_actual_runtime10000attempts_have_no_allocation_or_clock(self):
        stage = self.stage_sources()
        case = stage/'allocation.cc'; case.write_text(ALLOCATION)
        counters = stage/'counters.cc'; counters.write_text(COUNTERS)
        inputs = [p for p in stage.rglob('*') if p.is_file()]
        binary = stage/'allocation'
        self.command([*self.base, '-fsanitize=undefined', '-fno-sanitize-recover=all',
            '-I', stage/'src', stage/'src/core/countdown.cpp', case, counters,
            *self.link_wrap, '-o', binary], inputs)
        self.assertIn('10000 attempts allocations=0 clock_calls=0',
                      self.command([binary], inputs).stdout)

    def test_b3_d083_all_eight_upload_modes_refuse_before_board_or_transport(self):
        spec = importlib.util.spec_from_file_location('d083_board_tool', ROOT/'tools/board_tool.py')
        board = importlib.util.module_from_spec(spec); spec.loader.exec_module(board)
        evidence = []
        for transport in ('adb', 'ssh'):
            for match in (False, True):
                for startup in ('default', 'immediate'):
                    with self.subTest(transport=transport, match=match, startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict(os.environ, {'SUMO_TRANSPORT': transport}))
                        target = stack.enter_context(mock.patch.object(board, 'target'))
                        remote = stack.enter_context(mock.patch.object(board, 'remote'))
                        require_transport = stack.enter_context(mock.patch.object(board, 'require_transport'))
                        stderr = io.StringIO()
                        with redirect_stderr(stderr), self.assertRaises(ValueError) as refusal:
                            board.flash(SimpleNamespace(sketch='bench/p2_calibration_compile',
                                match=match, startup=startup, compile_only=False))
                        target.assert_not_called(); remote.assert_not_called(); require_transport.assert_not_called()
                        evidence.append({'transport': transport, 'match': match, 'startup': startup,
                                         'refusal': str(refusal.exception), 'stderr': stderr.getvalue(),
                                         'target_calls': target.call_count, 'remote_calls': remote.call_count,
                                         'transport_calls': require_transport.call_count})
        (self.receipts/f'upload_refusals_{time.time_ns()}.json').write_text(json.dumps(evidence, indent=2)+'\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
