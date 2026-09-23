# Compiles actual D080 setup/decoder against independent configuration variants.
# Exercises finite caps and invalid configuration without a board or native Bus.
# Every compiler and executable command retains output plus staged-source hashes.
import hashlib
from contextlib import ExitStack, redirect_stderr
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
import unittest
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
CASE = r'''
// Tests D080 boundary configurations through the public interface.
// Keeps variant expectations independent of the implementation source.
// Compiled by test_imu_setup.py with a host-only concrete Bus substitute.
#include "config.h"
#include "hal/imu.h"
#include "imu_bus_fake.h"
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#define VERIFY(expression) do { if (!(expression)) { \
    std::fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #expression); \
    std::exit(1); } ++assertions; } while (false)
unsigned assertions = 0U;

void checkZero(const imu::CoherentMotion& result) {
    VERIFY(!result.coherent);
    VERIFY(result.started_us == 0U && result.completed_us == 0U);
    VERIFY(result.interrupt_status == 0U && result.rail_mask == 0U);
    VERIFY(result.temperature_raw == 0);
    for (unsigned axis = 0; axis < 3U; ++axis) {
        VERIFY(result.accel_raw[axis] == 0 && result.gyro_raw[axis] == 0);
        VERIFY(result.accel_g[axis] == 0.0F && result.gyro_dps[axis] == 0.0F);
    }
}

void invalidConfiguration() {
    imu_fake::reset();
    imu::Bus bus;
    imu::Setup setup{bus};
    const auto first = setup.start(123U, true);
    VERIFY(first.state == imu::SetupState::FAULT);
    VERIFY(first.fault == imu::SetupFault::INVALID_CONFIG);
    VERIFY(first.requests == 0U && first.advances == 0U);
    VERIFY(setup.advance(900000U).fault == imu::SetupFault::INVALID_CONFIG);
    VERIFY(setup.start(456U, true).fault == imu::SetupFault::INVALID_CONFIG);
    VERIFY(imu_fake::script.count == 0U);
    imu::BusTransfer sample{};
    sample.status = imu::BusStatus::OK;
    sample.complete = true;
    sample.count = 15U;
    sample.started_us = 17U;
    sample.completed_us = 17U;
    for (unsigned i = 1U; i < 15U; ++i) sample.bytes[i] = 0x80U;
    const auto result = imu::decodeMotion(sample);
#if DECODE_INVALID
    VERIFY(result.status == imu::DecodeStatus::INVALID_CONFIG);
    checkZero(result);
    sample.status = imu::BusStatus::NACK;
    const auto precedence = imu::decodeMotion(sample);
    VERIFY(precedence.status == imu::DecodeStatus::INVALID_CONFIG);
    checkZero(precedence);
#else
    VERIFY(result.status == imu::DecodeStatus::OK);
    VERIFY(result.coherent);
    VERIFY(result.started_us == 17U && result.completed_us == 17U);
#endif
}

void frozenAdvanceLimit() {
    imu_fake::reset();
    imu::Bus bus;
    imu::Setup setup{bus};
    VERIFY(setup.start(123U, true).state == imu::SetupState::IN_PROGRESS);
    for (std::uint32_t call = 1U; call <= config::IMU_SETUP_MAX_ADVANCES; ++call) {
        const auto report = setup.advance(123U);
        VERIFY(report.state == imu::SetupState::IN_PROGRESS);
        VERIFY(report.advances == call);
        VERIFY(report.requests == 0U);
    }
    const auto report = setup.advance(123U);
    VERIFY(report.fault == imu::SetupFault::ADVANCE_LIMIT);
    VERIFY(report.advances == config::IMU_SETUP_MAX_ADVANCES);
    VERIFY(imu_fake::script.count == 0U);
    VERIFY(setup.advance(123U).advances == report.advances);
}

void seedProfile() {
    // count/byte pairs are the literal 48-operation D080 acceptance recipe.
    const std::uint8_t pairs[][2] = {
        {0,0},{1,0x68},{0,0x80},{1,0x40},{1,0x68},
        {1,0},{1,0},{1,0},{1,0},{1,0},{1,0},{1,0},{1,0},{1,0},
        {0,0},{1,0},{0,0},{1,0},{0,1},{1,1},
        {0,0},{1,0},{0,0},{1,0},{0,0},{1,0},{0,1},{1,1},
        {0,0},{1,0},{0,0x10},{1,0x10},{0,0x10},{1,0x10},{0,1},{1,1},
        {1,0x68},{1,1},{1,0},{1,0},{1,0},{1,1},{1,0},{1,0x10},
        {1,0x10},{1,0},{1,1},{15,1}
    };
    static_assert(sizeof(pairs) / sizeof(pairs[0]) == 48U);
    for (unsigned index = 0; index < 48U; ++index) {
        auto& reply = imu_fake::script.replies[index];
        reply.start_offset_us = 0U;
        reply.duration_us = 0U;
        reply.transfer.status = imu::BusStatus::OK;
        reply.transfer.complete = true;
        reply.transfer.count = pairs[index][0];
        reply.transfer.bytes[0] = pairs[index][1];
    }
}

std::uint32_t nextTime(unsigned index, std::uint32_t last) {
    switch (index) {
    case 0: return 123U + config::IMU_POWER_WAIT_US;
    case 3: return last + config::IMU_RESET_WAIT_US;
    case 18: return last + config::IMU_GYRO_WAIT_US;
    case 20: return last + config::IMU_PLL_WAIT_US;
    case 36: return last + config::IMU_FILTER_WAIT_US;
    default: return last;
    }
}

void requestLimit() {
    imu_fake::reset();
    seedProfile();
    imu::Bus bus;
    imu::Setup setup{bus};
    VERIFY(setup.start(123U, true).state == imu::SetupState::IN_PROGRESS);
    std::uint32_t now = 123U;
    for (unsigned index = 0U; index < 48U; ++index) {
        now = nextTime(index, now);
        imu_fake::script.now_us = now;
        const auto report = setup.advance(now);
        const bool capped = index == config::IMU_SETUP_MAX_REQUESTS;
        VERIFY(imu_fake::script.count == index + (capped ? 0U : 1U));
        VERIFY(report.requests == imu_fake::script.count);
        if (capped) {
            VERIFY(report.fault == imu::SetupFault::REQUEST_LIMIT);
            VERIFY(report.state == imu::SetupState::FAULT);
            VERIFY(setup.advance(now).requests == config::IMU_SETUP_MAX_REQUESTS);
            VERIFY(imu_fake::script.count == index);
            return;
        }
        VERIFY(report.state == (index == 47U ? imu::SetupState::PROFILE_READY :
            imu::SetupState::IN_PROGRESS));
    }
    VERIFY(setup.report().requests == 48U);
    VERIFY(setup.advance(now).requests == 48U);
    VERIFY(imu_fake::script.count == 48U);
}

void progressAdvanceLimit() {
    imu_fake::reset();
    seedProfile();
    imu::Bus bus;
    imu::Setup setup{bus};
    VERIFY(setup.start(123U, true).state == imu::SetupState::IN_PROGRESS);
    std::uint32_t now = 123U;
    for (unsigned index = 0U; index < 48U; ++index) {
        now = nextTime(index, now);
        imu_fake::script.now_us = now;
        const auto report = setup.advance(now);
        if (index == config::IMU_SETUP_MAX_ADVANCES) {
            VERIFY(report.fault == imu::SetupFault::ADVANCE_LIMIT);
            VERIFY(report.advances == config::IMU_SETUP_MAX_ADVANCES);
            VERIFY(imu_fake::script.count == index);
            VERIFY(report.requests == index);
            return;
        }
        VERIFY(report.advances == index + 1U);
        VERIFY(report.requests == index + 1U);
        VERIFY(report.state == (index == 47U ? imu::SetupState::PROFILE_READY :
            imu::SetupState::IN_PROGRESS));
    }
    VERIFY(setup.report().state == imu::SetupState::PROFILE_READY);
    VERIFY(imu_fake::script.count == 48U);
}

int main() {
#if MODE == 0
    invalidConfiguration();
#elif MODE == 1
    frozenAdvanceLimit();
#elif MODE == 2
    requestLimit();
#else
    progressAdvanceLimit();
#endif
    std::printf("PASS %u assertions\n", assertions);
    return 0;
}
'''

PROBE_CASE = r'''
// Counts every concrete Bus entry from static startup through repeated loops.
// Primitive zero initialization precedes dynamic constructors and cannot reset evidence.
// Compiles actual D080 .ino, probe and Setup sources without calling retained entry.
#include "src/imu_setup_probe.h"
#include <cstdio>
#include <cstdlib>
unsigned bus_calls;
namespace imu {
BusInit Bus::begin() { ++bus_calls; return {}; }
BusTransfer Bus::readRegister(Register) { ++bus_calls; return {}; }
BusTransfer Bus::writeRegister(Register, std::uint8_t) { ++bus_calls; return {}; }
BusTransfer Bus::readMotion() { ++bus_calls; return {}; }
}
void setup();
void loop();
#define VERIFY(expression) do { if (!(expression)) { \
    std::fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #expression); \
    std::exit(1); } } while (false)
int main() {
    VERIFY(bus_calls == 0U);
    VERIFY(imu_setup_probe::entry == nullptr);
    VERIFY(imu_setup_probe::setup_driver.report().state == imu::SetupState::NOT_STARTED);
    setup();
    VERIFY(bus_calls == 0U);
    VERIFY(imu_setup_probe::entry == &imu_setup_probe::exercise);
    for (unsigned i = 0U; i < 10000U; ++i) {
        loop();
        VERIFY(bus_calls == 0U);
    }
    VERIFY(imu_setup_probe::entry == &imu_setup_probe::exercise);
    VERIFY(imu_setup_probe::setup_driver.report().state == imu::SetupState::NOT_STARTED);
    VERIFY(imu_setup_probe::setup_driver.report().requests == 0U);
    VERIFY(imu_setup_probe::setup_driver.report().advances == 0U);
    std::puts("PASS inert constructors setup and 10000 loops");
    return 0;
}
'''


class ImuSetupVariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++')
        if compiler is None:
            raise RuntimeError('Use Linux/WSL with g++ for D080 variants')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-d080-', dir='/dev/shm')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.base = [compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                    '-fno-sanitize-recover=all']
        cls.ordinal = 0

    def command(self, argv, manifest):
        result = subprocess.run(argv, capture_output=True, text=True, timeout=90)
        folder = Path(os.environ.get('SUMO_IMU_SETUP_RECEIPT_DIR',
                      ROOT/'state/analysis/P2_imu_setup_raw/author'))
        folder.mkdir(parents=True, exist_ok=True)
        payload = {'argv': list(map(str, argv)), 'returncode': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr,
                   'capture': 'subprocess text=True; newline normalized',
                   'sha256': manifest}
        (folder/f'variant_{time.time_ns()}.json').write_text(json.dumps(payload, indent=2)+'\n')
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result

    def variant(self, edits, mode, decode_invalid=False):
        self.__class__.ordinal += 1
        slot = self.stage/f'variant-{self.ordinal}'
        source = slot/'src'
        (source/'hal').mkdir(parents=True)
        for name in ('imu.cpp', 'imu.h', 'imu_bus_unoq.h'):
            shutil.copyfile(ROOT/'src/hal'/name, source/'hal'/name)
        config = (ROOT/'src/config.h').read_text()
        for name, value in edits.items():
            config, count = re.subn(r'(\b'+re.escape(name)+r'\s*=\s*)[^;]+;',
                                   r'\g<1>'+str(value)+'U;', config)
            self.assertEqual(1, count, name)
        (source/'config.h').write_text(config)
        case = slot/'variant.cpp'
        case.write_text(CASE)
        binary = slot/'imu-variant'
        inputs = [source/'hal/imu.cpp', source/'hal/imu.h', source/'hal/imu_bus_unoq.h',
                  source/'config.h', case, ROOT/'tests/support/imu_bus_fake.cpp',
                  ROOT/'tests/support/imu_bus_fake.h']
        manifest = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
        argv = [*self.base, '-I', str(source), '-I', str(ROOT/'tests/support'),
                f'-DMODE={mode}', f'-DDECODE_INVALID={int(decode_invalid)}', str(case),
                str(ROOT/'tests/support/imu_bus_fake.cpp'), str(source/'hal/imu.cpp'),
                '-o', str(binary)]
        self.command(argv, manifest)
        result = self.command([str(binary)], manifest)
        self.assertRegex(result.stdout, r'^PASS [1-9][0-9]* assertions\n$')

    def test_b3_d080_rejects_each_unsupported_fixed_profile_field(self):
        for name, value in {'IMU_GYRO_RANGE_DPS': 2000, 'IMU_ACCEL_RANGE_G': 16,
                            'IMU_DLPF_CFG': 0, 'IMU_SAMPLE_DIVIDER': 1}.items():
            with self.subTest(name=name):
                self.variant({name: value}, 0, decode_invalid=True)

    def test_b3_d080_rejects_zero_or_half_range_transfer_bounds(self):
        for value in (0, 0x80000000):
            with self.subTest(value=value):
                self.variant({'IMU_I2C_TRANSFER_US': value}, 0, decode_invalid=True)

    def test_b3_d080_each_setup_wait_must_be_positive_and_strictly_within_deadline(self):
        for name in ('IMU_POWER_WAIT_US', 'IMU_RESET_WAIT_US', 'IMU_GYRO_WAIT_US',
                     'IMU_PLL_WAIT_US', 'IMU_FILTER_WAIT_US'):
            for value in (0, 1000000, 0x80000000):
                with self.subTest(name=name, value=value):
                    self.variant({name: value}, 0)

    def test_b3_d080_deadline_requires_a_positive_forward_half_range_interval(self):
        for value in (0, 0x80000000, 0xFFFFFFFF):
            with self.subTest(value=value):
                self.variant({'IMU_SETUP_DEADLINE_US': value}, 0)

    def test_b3_d080_count_caps_reject_zero_and_more_than_65535(self):
        for name in ('IMU_SETUP_MAX_ADVANCES', 'IMU_SETUP_MAX_REQUESTS'):
            for value in (0, 65536):
                with self.subTest(name=name, value=value):
                    self.variant({name: value}, 0)

    def test_b3_d080_frozen_time_counts_the_last_allowed_advance_before_fault(self):
        for value in (1, 2, 48, 1024, 65535):
            with self.subTest(value=value):
                self.variant({'IMU_SETUP_MAX_ADVANCES': value}, 1)

    def test_b3_d080_request_limit_includes_begin_and_allows_exactly_48_for_success(self):
        for value in (1, 2, 3, 47, 48, 64, 65535):
            with self.subTest(value=value):
                self.variant({'IMU_SETUP_MAX_REQUESTS': value}, 2)

    def test_b3_d080_last_allowed_advance_can_finish_and_next_advance_cannot_call_bus(self):
        for value in (1, 2, 47, 48):
            with self.subTest(value=value):
                self.variant({'IMU_SETUP_MAX_ADVANCES': value}, 3)

    def test_b3_d080_actual_probe_constructors_setup_and_10000_loops_never_call_bus(self):
        for enabled in (0, 1):
            with self.subTest(enabled=enabled):
                sketch = self.stage/f'probe-{enabled}'
                shutil.copytree(ROOT/'bench/p2_imu_setup_compile', sketch)
                (sketch/'src/hal').mkdir(exist_ok=True)
                for name in ('imu.cpp', 'imu.h', 'imu_bus_unoq.h'):
                    shutil.copyfile(ROOT/'src/hal'/name, sketch/'src/hal'/name)
                shutil.copyfile(ROOT/'src/config.h', sketch/'src/config.h')
                harness = sketch/'harness.cpp'
                harness.write_text(PROBE_CASE)
                binary = sketch/'inert-probe'
                inputs = [path for path in sketch.rglob('*') if path.is_file()]
                manifest = {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in inputs}
                argv = [*self.base, f'-DMATCH={enabled}', f'-DMOTORS_ALLOWED={enabled}',
                        '-I', str(sketch), '-I', str(sketch/'src'), '-x', 'c++',
                        str(sketch/'p2_imu_setup_compile.ino'),
                        str(sketch/'src/imu_setup_probe.cpp'), str(sketch/'src/hal/imu.cpp'),
                        str(harness), '-o', str(binary)]
                self.command(argv, manifest)
                result = self.command([str(binary)], manifest)
                self.assertEqual('PASS inert constructors setup and 10000 loops\n', result.stdout)

    def test_b3_d080_all_eight_probe_upload_modes_refuse_before_transport(self):
        spec = importlib.util.spec_from_file_location('imu_setup_board_tool', ROOT/'tools/board_tool.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for transport in ('adb', 'ssh'):
            for match in (False, True):
                for startup in ('default', 'immediate'):
                    with self.subTest(transport=transport, match=match, startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict(os.environ, {'SUMO_TRANSPORT': transport}))
                        target = stack.enter_context(mock.patch.object(module, 'target'))
                        remote = stack.enter_context(mock.patch.object(module, 'remote'))
                        require_transport = stack.enter_context(mock.patch.object(module, 'require_transport'))
                        with redirect_stderr(io.StringIO()), self.assertRaises(ValueError):
                            module.flash(SimpleNamespace(sketch='bench/p2_imu_setup_compile',
                                match=match, startup=startup, compile_only=False))
                        target.assert_not_called()
                        remote.assert_not_called()
                        require_transport.assert_not_called()


if __name__ == '__main__':
    unittest.main()
