# Compiles actual D081 acquisition against specification-derived native and Bus fakes.
# Uses isolated WSL builds and additive variants without inheriting old test methods.
# Every process retains output and exact source hashes under the D081 author path.
from contextlib import ExitStack, redirect_stderr
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]

CASE = r'''
// Checks D081 silence configuration and D080 guarded-profile admission.
// Exercises real owned setup through independently specified Bus responses.
// Invalid runtime configuration must fail without acquiring any sample.
#include "config.h"
#include "hal/imu_acquisition.h"
#include "imu_acquisition_fake.h"
#include <cstdio>
#include <cstdlib>
#define VERIFY(x) do { if (!(x)) { std::fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); \
    std::exit(1); } ++assertions; } while (false)
unsigned assertions = 0U;
int main() {
    imu_acq_fake::reset(); imu_acq_fake::seedSetup(); imu::Acquirer acquirer;
    const auto started = acquirer.start(123U, true);
#if MODE == 2
    VERIFY(started.state == imu::SetupState::FAULT);
    VERIFY(started.fault == imu::SetupFault::INVALID_CONFIG);
    const auto sample = acquirer.read(123U);
    VERIFY(sample.state == imu::SampleState::FAULT);
    VERIFY(sample.fault == imu::SampleFault::SETUP);
    VERIFY(imu_fake::script.count == 0U);
#else
    VERIFY(started.state == imu::SetupState::IN_PROGRESS);
    std::uint32_t now = 123U;
    for (unsigned index = 0; index < 48U; ++index) {
        now = imu_acq_fake::setupTime(index, 123U, now);
        imu_fake::script.now_us = now;
        const auto report = acquirer.advanceSetup(now);
        VERIFY(report.state == (index == 47U ? imu::SetupState::PROFILE_READY :
                               imu::SetupState::IN_PROGRESS));
    }
#if MODE == 0
    const auto sample = acquirer.read(now);
    VERIFY(sample.state == imu::SampleState::FAULT);
    VERIFY(sample.fault == imu::SampleFault::INVALID_CONFIG);
    VERIFY(!sample.motion.coherent && sample.sequence == 0U);
    VERIFY(acquirer.read(now+1U).fault == imu::SampleFault::INVALID_CONFIG);
#else
    imu_acq_fake::script.reply = imu_acq_fake::noNew(now, 0U);
    VERIFY(acquirer.read(now).state == imu::SampleState::NO_NEW);
    VERIFY(imu_acq_fake::script.calls == 1U);
    const auto sample = acquirer.read(now + config::IMU_SILENCE_US);
    VERIFY(sample.fault == imu::SampleFault::SILENCE);
    VERIFY(sample.checked_us == now + config::IMU_SILENCE_US);
    VERIFY(imu_acq_fake::script.calls == 1U);
#endif
    VERIFY(imu_fake::script.count == 48U);
#endif
#if MODE != 1
    VERIFY(imu_acq_fake::script.calls == 0U);
#endif
    std::printf("PASS %u assertions\n", assertions);
}
'''

PROBE_CASE = r'''
// Counts every Bus entry before startup and through repeated inert sketch loops.
// Zero-initialized counters precede dynamic constructors and never reset evidence.
// The retained D081 exercise function must remain linked and never called.
#include "src/imu_acquisition_probe.h"
#include <cstdio>
#include <cstdlib>
unsigned bus_calls;
namespace imu {
BusInit Bus::begin() { ++bus_calls; return {}; }
BusTransfer Bus::readRegister(Register) { ++bus_calls; return {}; }
BusTransfer Bus::writeRegister(Register, std::uint8_t) { ++bus_calls; return {}; }
BusTransfer Bus::readMotion() { ++bus_calls; return {}; }
BusAcquisition Bus::acquireMotion() { ++bus_calls; return {}; }
}
void setup(); void loop();
#define VERIFY(x) do { if (!(x)) { std::fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x); \
    std::exit(1); } } while (false)
int main() {
    VERIFY(bus_calls == 0U); VERIFY(imu_acquisition_probe::entry == nullptr);
    VERIFY(imu_acquisition_probe::acquirer.setupReport().state == imu::SetupState::NOT_STARTED);
    setup(); VERIFY(bus_calls == 0U);
    VERIFY(imu_acquisition_probe::entry == &imu_acquisition_probe::exercise);
    for (unsigned i = 0U; i < 10000U; ++i) { loop(); VERIFY(bus_calls == 0U); }
    VERIFY(imu_acquisition_probe::entry == &imu_acquisition_probe::exercise);
    const auto report = imu_acquisition_probe::acquirer.setupReport();
    VERIFY(report.state == imu::SetupState::NOT_STARTED);
    VERIFY(report.requests == 0U && report.advances == 0U);
    std::puts("PASS inert constructors setup and 10000 loops");
}
'''


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ImuAcquisitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++')
        if compiler is None:
            raise RuntimeError('Use Linux/WSL g++ for D081 source tests')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-d081-', dir='/dev/shm')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.receipts = Path(os.environ.get('SUMO_IMU_ACQUISITION_RECEIPT_DIR',
                            ROOT/'state/analysis/P2_imu_acquisition_raw/author'))
        cls.receipts.mkdir(parents=True, exist_ok=True)
        cls.base = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                    '-fno-sanitize-recover=all']
        cls.ordinal = 0

    def command(self, argv, paths):
        manifest = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        result = subprocess.run(list(map(str, argv)), text=True, capture_output=True, timeout=120)
        payload = {'argv': list(map(str, argv)), 'returncode': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr, 'sha256': manifest,
                   'capture': 'subprocess text=True; newline normalized'}
        (self.receipts/f'command_{time.time_ns()}.json').write_text(json.dumps(payload, indent=2)+'\n')
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result

    def stage_sources(self, edits=None):
        self.__class__.ordinal += 1
        slot = self.stage/f'case-{self.ordinal}'
        (slot/'src/hal').mkdir(parents=True)
        for name in ('imu.cpp', 'imu.h', 'imu_bus_unoq.h', 'imu_acquisition.cpp', 'imu_acquisition.h'):
            shutil.copyfile(ROOT/'src/hal'/name, slot/'src/hal'/name)
        config = (ROOT/'src/config.h').read_text()
        for name, value in (edits or {}).items():
            config, count = re.subn(r'(\b'+re.escape(name)+r'\s*=\s*)[^;]+;',
                                   r'\g<1>'+str(value)+'U;', config)
            self.assertEqual(count, 1, name)
        (slot/'src/config.h').write_text(config)
        return slot

    def variant(self, edits, mode):
        slot = self.stage_sources(edits)
        case = slot/'variant.cc'; case.write_text(CASE)
        support = ROOT/'tests/support'
        inputs = [p for p in slot.rglob('*') if p.is_file()] + [
            support/name for name in ('imu_bus_fake.h', 'imu_bus_fake.cpp',
                                      'imu_acquisition_fake.h', 'imu_acquisition_fake.cpp')]
        binary = slot/'variant'
        argv = [*self.base, '-I', slot/'src', '-I', support, f'-DMODE={mode}', case,
                support/'imu_bus_fake.cpp', support/'imu_acquisition_fake.cpp',
                slot/'src/hal/imu.cpp', slot/'src/hal/imu_acquisition.cpp', '-o', binary]
        self.command(argv, inputs)
        result = self.command([binary], inputs)
        self.assertRegex(result.stdout, r'^PASS [1-9][0-9]* assertions\n$')

    def test_b3_d081_actual_acquirer_and_setup_contract(self):
        slot = self.stage_sources()
        case = ROOT/'tests/test_imu_acquisition.cpp'
        support = ROOT/'tests/support'
        main = ROOT/'tests/native_imu_bus/test_main.cc'
        inputs = [p for p in slot.rglob('*') if p.is_file()] + [case, main] + [
            support/name for name in ('imu_bus_fake.h', 'imu_bus_fake.cpp',
                                      'imu_acquisition_fake.h', 'imu_acquisition_fake.cpp')]
        binary = slot/'acquirer'
        self.command([*self.base, '-DDOCTEST_CONFIG_NO_EXCEPTIONS', '-I', slot/'src',
            '-I', ROOT/'tests', '-isystem', ROOT/'host/third_party', case, main,
            support/'imu_bus_fake.cpp', support/'imu_acquisition_fake.cpp',
            slot/'src/hal/imu.cpp', slot/'src/hal/imu_acquisition.cpp', '-o', binary], inputs)
        result = self.command([binary, '--no-colors'], inputs)
        self.assertIn('Status: SUCCESS!', result.stdout)
        print(result.stdout, flush=True)

    def test_b3_d081_native_shared_budget_order_and_terminal_cleanup(self):
        native = module_at('d081_native_runner', ROOT/'tests/tooling/test_imu_bus_unoq.py')
        harness = native.NativeImuBusTests
        with mock.patch.dict(os.environ, {'SUMO_NATIVE_RECEIPT_DIR': str(self.receipts),
                                         'TMPDIR': '/dev/shm'}):
            harness.setUpClass()
            try:
                binary = harness.variant('acquisition_cases.cc')
                result = harness.command([str(binary), '--no-colors'])
                self.assertIn('Status: SUCCESS!', result.stdout)
                print(result.stdout, flush=True)
            finally:
                harness.doClassCleanups()

    def test_b14_d081_invalid_silence_bounds_fail_before_acquisition(self):
        for value in (0, 0x80000000, 0xffffffff):
            with self.subTest(value=value):
                self.variant({'IMU_SILENCE_US': value}, 0)

    def test_b14_d081_smallest_and_largest_forward_silence_bounds(self):
        for value in (1, 0x7fffffff):
            with self.subTest(value=value):
                self.variant({'IMU_SILENCE_US': value}, 1)

    def test_b3_d081_unsupported_profile_cannot_bypass_owned_setup(self):
        for name, value in {'IMU_GYRO_RANGE_DPS': 2000, 'IMU_ACCEL_RANGE_G': 16,
                            'IMU_DLPF_CFG': 0, 'IMU_SAMPLE_DIVIDER': 1}.items():
            with self.subTest(name=name):
                self.variant({name: value}, 2)

    def test_b3_d081_actual_probe_startup_and_10000_loops_are_inert_in_both_modes(self):
        for enabled in (0, 1):
            with self.subTest(enabled=enabled):
                slot = self.stage_sources()
                sketch = ROOT/'bench/p2_imu_acquisition_compile'
                shutil.copytree(sketch, slot, dirs_exist_ok=True)
                harness = slot/'harness.cc'; harness.write_text(PROBE_CASE)
                inputs = [p for p in slot.rglob('*') if p.is_file()]
                binary = slot/'probe'
                self.command([*self.base, f'-DMATCH={enabled}', f'-DMOTORS_ALLOWED={enabled}',
                    '-I', slot, '-I', slot/'src', '-x', 'c++',
                    slot/'p2_imu_acquisition_compile.ino', slot/'src/imu_acquisition_probe.cpp',
                    slot/'src/hal/imu.cpp', slot/'src/hal/imu_acquisition.cpp', harness,
                    '-o', binary], inputs)
                result = self.command([binary], inputs)
                self.assertEqual('PASS inert constructors setup and 10000 loops\n', result.stdout)

    def test_b3_d081_all_eight_upload_modes_refuse_before_board_or_transport_lookup(self):
        board = module_at('d081_board_tool', ROOT/'tools/board_tool.py')
        for transport in ('adb', 'ssh'):
            for match in (False, True):
                for startup in ('default', 'immediate'):
                    with self.subTest(transport=transport, match=match, startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict(os.environ, {'SUMO_TRANSPORT': transport}))
                        target = stack.enter_context(mock.patch.object(board, 'target'))
                        remote = stack.enter_context(mock.patch.object(board, 'remote'))
                        require_transport = stack.enter_context(mock.patch.object(board, 'require_transport'))
                        with redirect_stderr(io.StringIO()), self.assertRaises(ValueError):
                            board.flash(SimpleNamespace(sketch='bench/p2_imu_acquisition_compile',
                                match=match, startup=startup, compile_only=False))
                        target.assert_not_called(); remote.assert_not_called(); require_transport.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
