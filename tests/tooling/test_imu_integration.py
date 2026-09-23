# Exercises actual D084 sources with frozen independent specification tests.
# Source bodies are copied and hashed opaquely; no board or transport is contacted.
# Commands, exits, output, source hashes and all failed attempts remain as receipts.
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
CASES = ('test_imu_adapter.cpp', 'test_imu_provenance.cpp', 'test_imu_integration.cpp')

COUNTERS = r'''
// Counts dynamic allocation and unexpected external clock or bus calls.
// A runtime guard includes production construction and every exercised method.
// Link wrappers observe all ordinary allocation forms on this host build.
#include <cstddef>
#include <cstdlib>
#include <new>
#include "hal/imu_bus_unoq.h"
bool guard_allocations = true;
unsigned allocations, io_calls;
extern "C" void* __real_malloc(std::size_t);
extern "C" void* __real_calloc(std::size_t,std::size_t);
extern "C" void* __real_realloc(void*,std::size_t);
extern "C" void __real_free(void*);
extern "C" void* __wrap_malloc(std::size_t n) { if(guard_allocations) ++allocations; return __real_malloc(n); }
extern "C" void* __wrap_calloc(std::size_t n,std::size_t size) { if(guard_allocations) ++allocations; return __real_calloc(n,size); }
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
namespace imu {
BusInit Bus::begin() { ++io_calls; return {}; }
BusTransfer Bus::readRegister(Register) { ++io_calls; return {}; }
BusTransfer Bus::writeRegister(Register,std::uint8_t) { ++io_calls; return {}; }
BusTransfer Bus::readMotion() { ++io_calls; return {}; }
BusAcquisition Bus::acquireMotion() { ++io_calls; return {}; }
}
'''

ALLOCATIONS = r'''
// Runs actual estimator mapping and Robot transactions while allocation is watched.
// Explicit matched disabled receipts avoid replacing application evidence with wishes.
// Ten thousand pure updates include fresh and retained reports and future bias.
#include "hal/imu_adapter.h"
#include <cstdio>
#include <cstdlib>
extern bool guard_allocations;
extern unsigned allocations, io_calls;
#define VERIFY(x) do { if(!(x)) { std::fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); std::exit(1); } } while(false)
int main() {
    guard_allocations=true;
    {
        imu::Estimator estimator; fsm::Robot robot; fsm::RobotInput in;
        VERIFY(estimator.begin(imu::Mounting{{1,2,3},true},0.0F));
        in.initialization_complete=true; in.observations_fresh=true;
        in.opp_raw_mask=0x78U; in.vbat_v=11.1F; in.vbat_valid=true;
        for(auto& qtr:in.line_raw_us) qtr=1000U;
        fsm::RobotResult prior; unsigned sequence=0U;
        for(unsigned index=0U;index<10000U;++index) {
            imu::Sample s; s.checked_us=index*1000U;
            if(index%2U==0U) {
                s.state=imu::SampleState::OBSERVATION; s.bus_status=imu::BusStatus::OK;
                s.sequence=++sequence; s.had_previous_observation=index!=0U;
                s.observation_gap_us=index==0U?0U:2000U;
                s.motion.status=imu::DecodeStatus::OK; s.motion.coherent=true;
                s.motion.started_us=s.motion.completed_us=s.checked_us;
            } else {
                s.state=imu::SampleState::NO_NEW;
                s.bus_status=imu::BusStatus::OK; s.sequence=sequence;
            }
            const auto estimate=estimator.observe(s);
            VERIFY(estimate.state==imu::HeadingState::READY);
            in.t_us=s.checked_us;
            VERIFY(imu::applyEstimate(in,estimate));
            if(index!=0U) in.previous={true,prior.token,in.t_us-1000U,false,0.0F,0.0F,true,in.t_us-1000U,0U};
            prior=robot.step(in);
            VERIFY(prior.fresh && prior.contract_faults==0U);
            VERIFY(!prior.outputs.motors_enabled);
            VERIFY(estimator.applyBias(0.0F));
        }
        robot.reset();
    }
    guard_allocations=false;
    VERIFY(allocations==0U && io_calls==0U);
    std::puts("PASS no allocations or I/O across constructors and 10000 estimator adapter Robot transactions");
}
'''

PROBE = r'''
// Executes the real inert sketch startup while retaining static constructor evidence.
// Macro values cannot turn setup or loop into execution of the retained probe.
// Allocation and I/O counters cover setup and ten thousand subsequent loops.
#include "src/imu_integration_probe.h"
#include <cstdio>
#include <cstdlib>
extern bool guard_allocations;
extern unsigned allocations, io_calls;
void setup(); void loop();
#define VERIFY(x) do { if(!(x)) { std::fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); std::exit(1); } } while(false)
int main() {
    using namespace imu_integration_probe;
    VERIFY(allocations==0U && io_calls==0U && exercise_calls==0U && entry==nullptr);
    VERIFY(estimator.report().state==imu::HeadingState::NOT_STARTED);
    VERIFY(!candidate_mounting.confirmed);
    for(auto axis:candidate_mounting.body_axis) VERIFY(axis==0);
    VERIFY(candidate_sample.state==imu::SampleState::NOT_READY);
    VERIFY(candidate_bias_dps==0.0F && !candidate_input.initialization_complete);
    guard_allocations=true; setup();
    VERIFY(entry==&exercise);
    for(unsigned index=0;index<10000U;++index) {
        loop(); VERIFY(io_calls==0U && exercise_calls==0U);
    }
    guard_allocations=false;
    VERIFY(allocations==0U && io_calls==0U && exercise_calls==0U);
    VERIFY(estimator.report().state==imu::HeadingState::NOT_STARTED);
    VERIFY(entry==&exercise);
    std::puts("PASS inert constructors setup and 10000 loops");
}
'''


class ImuIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = shutil.which('g++')
        if cls.compiler is None:
            raise RuntimeError('Use Linux/WSL g++ for D084 tests')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-d084-', dir='/dev/shm')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.receipts = Path(os.environ.get('SUMO_IMU_INTEGRATION_RECEIPT_DIR',
                            ROOT/'state/analysis/P2_imu_integration_raw/author'))
        cls.receipts.mkdir(parents=True, exist_ok=True)
        cls.base = [cls.compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti']
        cls.ordinal = 0
        paths = [ROOT/'tests'/name for name in CASES] + [Path(__file__),
                 ROOT/'state/analysis/P2_imu_integration_contract.md']
        receipt = {'purpose': 'Independent contract/header-derived tests frozen before first execution in this run',
                   'time_ns': time.time_ns(), 'sha256': cls.hashes(paths)}
        (cls.receipts/f'freeze_{time.time_ns()}.json').write_text(json.dumps(receipt, indent=2)+'\n')

    @staticmethod
    def hashes(paths):
        return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

    def command(self, argv, paths, timeout=180):
        manifest = self.hashes(paths)
        try:
            result = subprocess.run(list(map(str, argv)), text=True, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired as error:
            result = SimpleNamespace(returncode=124, stdout=str(error.stdout or ''),
                                     stderr=str(error.stderr or '')+'\nTIMEOUT')
        receipt = {'argv': list(map(str, argv)), 'returncode': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr, 'sha256': manifest,
                   'capture': 'subprocess text=True; newline normalized'}
        (self.receipts/f'command_{time.time_ns()}.json').write_text(json.dumps(receipt, indent=2)+'\n')
        self.assertEqual(0, result.returncode, (result.stdout + result.stderr)[-15000:])
        return result

    def sources(self):
        self.__class__.ordinal += 1
        slot = self.stage/f'case-{self.ordinal}'
        for folder in ('src/core', 'src/hal', 'tests', 'include'):
            (slot/folder).mkdir(parents=True, exist_ok=True)
        for path in (ROOT/'src/core').glob('*'):
            if path.suffix in ('.h', '.cpp'): shutil.copyfile(path, slot/'src/core'/path.name)
        for path in (ROOT/'src/hal').glob('*.h'): shutil.copyfile(path, slot/'src/hal'/path.name)
        for name in ('imu_heading.cpp', 'imu_adapter.cpp'):
            shutil.copyfile(ROOT/'src/hal'/name, slot/'src/hal'/name)
        shutil.copyfile(ROOT/'src/config.h', slot/'src/config.h')
        for name in (*CASES, 'robot_scenario.h'):
            shutil.copyfile(ROOT/'tests'/name, slot/'tests'/name)
        shutil.copyfile(ROOT/'host/third_party/doctest.h', slot/'include/doctest.h')
        shutil.copyfile(ROOT/'tests/native_imu_bus/test_main.cc', slot/'test_main.cc')
        sources = sorted((slot/'src/core').glob('*.cpp')) + [slot/'src/hal/imu_heading.cpp', slot/'src/hal/imu_adapter.cpp']
        return slot, sources

    def run_cases(self, sanitize=False):
        slot, sources = self.sources()
        binary = slot/'integration'
        options = ['-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer'] if sanitize else []
        paths = [p for p in slot.rglob('*') if p.is_file()]
        self.command([*self.base, *options, '-DDOCTEST_CONFIG_NO_EXCEPTIONS', '-I', slot/'src',
            '-isystem', slot/'include', *[slot/'tests'/name for name in CASES], slot/'test_main.cc',
            *sources, '-o', binary], paths)
        result = self.command([binary, '--no-colors'], paths)
        self.assertIn('Status: SUCCESS!', result.stdout)
        print(result.stdout, flush=True)

    def test_b3_d084_independent_contract_cases_normal(self):
        self.run_cases()

    def test_b3_d084_independent_contract_cases_asan_ubsan(self):
        self.run_cases(sanitize=True)

    def test_b3_d084_runtime_has_no_allocation_or_io(self):
        slot, sources = self.sources()
        case = slot/'allocation.cc'; case.write_text(ALLOCATIONS)
        counters = slot/'counters.cc'; counters.write_text(COUNTERS)
        binary = slot/'allocation'; paths = [p for p in slot.rglob('*') if p.is_file()]
        self.command([*self.base, '-fsanitize=undefined', '-fno-sanitize-recover=all', '-I', slot/'src',
            case, counters, *sources, '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free',
            '-o', binary], paths)
        self.assertIn('PASS no allocations or I/O', self.command([binary], paths).stdout)

    def test_b3_d084_actual_probe_is_inert_in_both_macro_modes(self):
        for enabled in (0, 1):
            with self.subTest(enabled=enabled):
                slot, sources = self.sources()
                shutil.copytree(ROOT/'bench/p2_imu_integration_compile', slot, dirs_exist_ok=True)
                case = slot/'probe.cc'; case.write_text(PROBE)
                counters = slot/'counters.cc'; counters.write_text(COUNTERS)
                binary = slot/'probe'; paths = [p for p in slot.rglob('*') if p.is_file()]
                self.command([*self.base, '-fsanitize=undefined', '-fno-sanitize-recover=all',
                    f'-DMATCH={enabled}', f'-DMOTORS_ALLOWED={enabled}', '-I', slot, '-I', slot/'src',
                    '-x', 'c++', slot/'p2_imu_integration_compile.ino', slot/'src/imu_integration_probe.cpp',
                    case, counters, *sources,
                    '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free', '-o', binary], paths)
                self.assertEqual('PASS inert constructors setup and 10000 loops\n', self.command([binary], paths).stdout)

    def test_b3_d084_all_eight_upload_modes_refuse_before_transport(self):
        spec = importlib.util.spec_from_file_location('d084_board_tool', ROOT/'tools/board_tool.py')
        board = importlib.util.module_from_spec(spec); spec.loader.exec_module(board)
        outcomes = []
        for transport in ('adb', 'ssh'):
            for match in (False, True):
                for startup in ('default', 'immediate'):
                    with self.subTest(transport=transport, match=match, startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict(os.environ, {'SUMO_TRANSPORT': transport}))
                        target = stack.enter_context(mock.patch.object(board, 'target'))
                        remote = stack.enter_context(mock.patch.object(board, 'remote'))
                        require_transport = stack.enter_context(mock.patch.object(board, 'require_transport'))
                        output = io.StringIO(); rejected = False
                        try:
                            with redirect_stderr(output):
                                board.flash(SimpleNamespace(sketch='bench/p2_imu_integration_compile',
                                    match=match, startup=startup, compile_only=False))
                        except ValueError as error:
                            rejected = True; error_text = str(error)
                        else:
                            error_text = ''
                        outcomes.append({'transport': transport, 'match': match, 'startup': startup,
                            'rejected': rejected, 'error': error_text, 'stderr': output.getvalue(),
                            'target_calls': target.call_count, 'remote_calls': remote.call_count,
                            'require_transport_calls': require_transport.call_count})
                        payload = {'cases': outcomes, 'sha256': self.hashes([ROOT/'tools/board_tool.py'])}
                        (self.receipts/f'upload_refusals_{time.time_ns()}.json').write_text(json.dumps(payload, indent=2)+'\n')
                        self.assertTrue(rejected)
                        target.assert_not_called(); remote.assert_not_called(); require_transport.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
