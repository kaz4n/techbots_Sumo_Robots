# Tests D-064 startup GPIO acquisition and decoding from its contract/header.
# Preserves raw timing, signed observations, early failure and incomplete evidence.
# Uses the opaque real sketch and host substitutes; never runs board commands.
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import importlib.util
import io
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


PROJECT = Path(__file__).resolve().parents[2]
CAPTURE_TOOL = PROJECT / 'tools/p0_gpio_capture.py'
SAMPLES = 400
RECORD_BYTES = 14428
HALF_RANGE = 1 << 31
UINT32_MAX = (1 << 32) - 1
INTERVAL_NAMES = ('overhead_us', 'pin_mode_us', 'write_high_us',
                  'read_low_us', 'read_high_us', 'pair_us')
LEVEL_NAMES = ('low_level', 'high_level', 'pair_level')
FIELD_NAMES = INTERVAL_NAMES + LEVEL_NAMES
ARDUINO_STUB = '''#pragma once
#include <cstdint>
#ifndef LED_BUILTIN
#define LED_BUILTIN 50
#endif
#ifndef LED3_R
#define LED3_R 50
#endif
#define OUTPUT 1
#define HIGH 1
#define LOW 0
std::uint32_t micros();
void pinMode(std::uint32_t pin, std::uint32_t mode);
void digitalWrite(std::uint32_t pin, std::uint32_t value);
int digitalRead(std::uint32_t pin);
'''
GPIO_HARNESS = '''#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <type_traits>
#include "Arduino.h"
#include "bench/p0_gpio/src/gpio_capture.h"
#include "bench/p0_gpio/p0_gpio.ino"

static_assert(sizeof(p0::GpioCapture) == 14428);
static_assert(sizeof(p0::GpioSample) == 36);
static_assert(offsetof(p0::GpioCapture, samples) == 28);
static_assert(offsetof(p0::GpioCapture, final_level) == 24);
static_assert(offsetof(p0::GpioSample, overhead_us) == 0);
static_assert(offsetof(p0::GpioSample, pin_mode_us) == 4);
static_assert(offsetof(p0::GpioSample, write_high_us) == 8);
static_assert(offsetof(p0::GpioSample, read_low_us) == 12);
static_assert(offsetof(p0::GpioSample, read_high_us) == 16);
static_assert(offsetof(p0::GpioSample, pair_us) == 20);
static_assert(offsetof(p0::GpioSample, low_level) == 24);
static_assert(offsetof(p0::GpioSample, high_level) == 28);
static_assert(offsetof(p0::GpioSample, pair_level) == 32);
static_assert(std::is_same_v<decltype(p0Gpio), volatile p0::GpioCapture>);
static_assert(std::is_same_v<decltype(p0::GpioCapture::final_level), std::int32_t>);
static_assert(std::is_same_v<decltype(p0::GpioSample::low_level), std::int32_t>);
static_assert(std::is_same_v<decltype(p0::GpioSample::high_level), std::int32_t>);
static_assert(std::is_same_v<decltype(p0::GpioSample::pair_level), std::int32_t>);
std::uint32_t times[4802]{};
unsigned clockCalls = 0;
unsigned gpioCalls = 0;
unsigned readyCalls = 0;
bool ready = true;
int badSample = -1;
unsigned badField = 0;
int badValue = -19;
int finalValue = 1;
int pendingCall = -1;
unsigned finishCount = 400;

std::uint32_t duration(unsigned i, unsigned field) {
    if (i == 0) return 1000U + 101U * field;
    return 1U + (i * 37U + 103U * field) % 991U;
}

int level(unsigned i, unsigned field) {
    if (static_cast<int>(i) == badSample && field == badField) return badValue;
    return field == 0 ? 0 : 1;
}

void checkSample(unsigned i) {
    const auto& sample = p0Gpio.samples[i];
    assert(sample.overhead_us == duration(i, 0));
    assert(sample.pin_mode_us == duration(i, 1));
    assert(sample.write_high_us == duration(i, 2));
    assert(sample.read_low_us == duration(i, 3));
    assert(sample.read_high_us == duration(i, 4));
    assert(sample.pair_us == duration(i, 5));
    assert(sample.low_level == level(i, 0));
    assert(sample.high_level == level(i, 1));
    assert(sample.pair_level == level(i, 2));
}

void checkPublished(unsigned completed) {
    assert(p0Gpio.version == 1 && p0Gpio.ready == 1 && p0Gpio.complete == 0);
    assert(p0Gpio.completed == completed && p0Gpio.end_us == 0);
    for (unsigned i = 0; i < completed; ++i) checkSample(i);
}

bool p0::gpioReady() {
    assert(readyCalls == 0 && gpioCalls == 0);
    ++readyCalls;
    return ready;
}

std::uint32_t micros() {
    assert(readyCalls == 1 && ready);
    assert(clockCalls <= 12 * finishCount + 1);
    if (clockCalls == 0) {
        assert(gpioCalls == 0);
        checkPublished(0);
    } else if (clockCalls == 12 * finishCount + 1) {
        assert(gpioCalls == 7 * finishCount + 2);
        checkPublished(finishCount);
        assert(p0Gpio.final_level == finalValue);
    } else {
        const unsigned i = (clockCalls - 1) / 12;
        const unsigned phase = (clockCalls - 1) % 12;
        constexpr unsigned completedGpio[] = {0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 6};
        assert(gpioCalls == 7 * i + completedGpio[phase]);
        checkPublished(i);
    }
    return times[clockCalls++];
}

void checkGpio(std::uint32_t pin, unsigned operation) {
    assert(readyCalls == 1 && ready && pin == 50);
    assert(gpioCalls < finishCount * 7 + 2);
    const unsigned i = gpioCalls / 7;
    if (gpioCalls < finishCount * 7) {
        const unsigned phase = gpioCalls % 7;
        constexpr unsigned operations[] = {0, 2, 1, 2, 0, 1, 2};
        constexpr unsigned clocks[] = {4, 6, 8, 10, 12, 12, 13};
        assert(operation == operations[phase]);
        assert(clockCalls == 12 * i + clocks[phase]);
        checkPublished(i);
    } else {
        assert(operation == (gpioCalls == finishCount * 7 ? 1U : 2U));
        assert(clockCalls == 12 * finishCount + 1);
        checkPublished(finishCount);
    }
    if (static_cast<int>(gpioCalls) == pendingCall) std::exit(0);
    ++gpioCalls;
}

void pinMode(std::uint32_t pin, std::uint32_t mode) {
    assert(mode == OUTPUT);
    checkGpio(pin, 0);
}

void digitalWrite(std::uint32_t pin, std::uint32_t value) {
    assert(value == HIGH);
    checkGpio(pin, 1);
}

int digitalRead(std::uint32_t pin) {
    const unsigned i = gpioCalls / 7;
    const unsigned phase = gpioCalls % 7;
    const bool finalRead = gpioCalls == finishCount * 7 + 1;
    checkGpio(pin, 2);
    return finalRead ? finalValue : level(i, phase == 1 ? 0 : phase == 3 ? 1 : 2);
}

void prepare(std::uint32_t start) {
    const auto* bytes = reinterpret_cast<const volatile unsigned char*>(&p0Gpio);
    for (unsigned i = 0; i < sizeof(p0Gpio); ++i) assert(bytes[i] == 0);
    times[0] = start;
    std::uint32_t current = start;
    constexpr unsigned fields[] = {0, 1, 3, 2, 4, 5};
    for (unsigned i = 0; i < finishCount; ++i) {
        for (unsigned pair = 0; pair < 6; ++pair) {
            times[1 + 12 * i + 2 * pair] = current + 3;
            times[2 + 12 * i + 2 * pair] = current + 3 + duration(i, fields[pair]);
            current = times[2 + 12 * i + 2 * pair];
        }
    }
    times[12 * finishCount + 1] = current + 9;
}

void verifyFrozenLoop() {
    unsigned char saved[sizeof(p0Gpio)];
    const auto* bytes = reinterpret_cast<const volatile unsigned char*>(&p0Gpio);
    for (unsigned i = 0; i < sizeof(p0Gpio); ++i) saved[i] = bytes[i];
    const unsigned savedClock = clockCalls, savedGpio = gpioCalls;
    for (unsigned i = 0; i < 10000; ++i) loop();
    assert(clockCalls == savedClock && gpioCalls == savedGpio && readyCalls == 1);
    for (unsigned i = 0; i < sizeof(p0Gpio); ++i) assert(bytes[i] == saved[i]);
}

void verifyFinished() {
    assert(readyCalls == 1);
    if (!ready) {
        assert(gpioCalls == 0);
        assert(p0Gpio.version == 1 && p0Gpio.ready == 0);
        assert(p0Gpio.complete == 0 && p0Gpio.completed == 0);
    } else {
        assert(clockCalls == 12 * finishCount + 2 && gpioCalls == 7 * finishCount + 2);
        assert(p0Gpio.version == 1 && p0Gpio.ready == 1);
        assert(p0Gpio.complete == (badSample == -1 && finalValue == 1 ? 1U : 0U));
        assert(p0Gpio.completed == finishCount && p0Gpio.final_level == finalValue);
        assert(p0Gpio.start_us == times[0] && p0Gpio.end_us == times[12 * finishCount + 1]);
        for (unsigned i = 0; i < finishCount; ++i) checkSample(i);
    }
    const unsigned savedCount = ready ? finishCount : 0;
    const auto* rest = reinterpret_cast<const volatile unsigned char*>(&p0Gpio.samples[savedCount]);
    for (unsigned i = 0; i < (400 - savedCount) * 36; ++i) assert(rest[i] == 0);
    verifyFrozenLoop();
}

int main(int argc, char** argv) {
    assert(argc >= 2);
    const std::string scenario = argv[1];
    ready = scenario != "not-ready";
    if (scenario == "mismatch") {
        assert(argc == 5);
        badSample = std::stoi(argv[2]);
        badField = static_cast<unsigned>(std::stoi(argv[3]));
        badValue = std::stoi(argv[4]);
        finishCount = static_cast<unsigned>(badSample) + 1;
    }
    if (scenario == "final") {
        assert(argc == 3);
        finalValue = std::stoi(argv[2]);
    }
    if (scenario == "pending") {
        assert(argc == 3);
        pendingCall = std::stoi(argv[2]);
    }
    prepare(scenario == "wrap" ? 0xfffffff0U : 51U);
    setup();
    assert(pendingCall == -1);
    verifyFinished();
}
'''


def load_capture_without_actions():
    name = 'sumo_gpio_capture_contract_fixture'
    specification = importlib.util.spec_from_file_location(name, CAPTURE_TOOL)
    module = importlib.util.module_from_spec(specification)
    stdout, stderr = io.StringIO(), io.StringIO()
    with ExitStack() as stack:
        prohibit_actions(stack)
        stack.enter_context(mock.patch.object(sys, 'argv', ['p0_gpio_capture.py', '--invalid']))
        stack.enter_context(mock.patch.dict(sys.modules, {name: module}))
        stack.enter_context(mock.patch.object(sys, 'path', [str(PROJECT / 'tools'), *sys.path]))
        stack.enter_context(redirect_stdout(stdout))
        stack.enter_context(redirect_stderr(stderr))
        specification.loader.exec_module(module)
    return module, stdout.getvalue(), stderr.getvalue()


def prohibit_actions(stack):
    forbidden = AssertionError('Fixture import/decoder/readout must not run real transport')
    for target in ('run', 'Popen', 'call', 'check_call', 'check_output'):
        stack.enter_context(mock.patch.object(subprocess, target, side_effect=forbidden))
    for target in ('socket', 'create_connection'):
        stack.enter_context(mock.patch.object(socket, target, side_effect=forbidden))
    stack.enter_context(mock.patch.object(os, 'system', side_effect=forbidden))
    stack.enter_context(mock.patch('builtins.input', side_effect=forbidden))


def record(samples=None, *, start=0, end=None, version=1, ready=1, complete=1,
           completed=400, final_level=1):
    # Literal layout and packing from D-064, independent of decoder constants.
    if samples is None:
        samples = [(2, 3, 5, 7, 11, 13, 0, 1, 1)] * SAMPLES
    if end is None:
        end = (start + sum(sum(sample[:6]) for sample in samples)) & UINT32_MAX
    header = struct.pack('<IIIIIIi', version, ready, complete, completed, start, end, final_level)
    return header + b''.join(struct.pack('<IIIIIIiii', *sample) for sample in samples)


class P0GpioSketchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = shutil.which('g++')
        if cls.compiler is None:
            raise RuntimeError('g++ is required; run these host tests under WSL')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-p0-gpio-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        (cls.root / 'Arduino.h').write_text(ARDUINO_STUB)
        cls.harness = cls.root / 'gpio.cpp'
        cls.harness.write_text(GPIO_HARNESS)
        cls.executable = cls.root / 'gpio'
        result = cls.compile()
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)

    @classmethod
    def compile(cls, *definitions):
        return subprocess.run(
            [cls.compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
             '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
             '-fno-sanitize-recover=all', '-I', str(cls.root), '-I', str(PROJECT),
             '-I', str(PROJECT / 'src'), *definitions,
             str(cls.harness), '-o', str(cls.executable)],
            capture_output=True, text=True, check=False, timeout=30)

    def run_scenario(self, *args):
        result = subprocess.run([str(self.executable), *map(str, args)],
                                capture_output=True, text=True, check=False, timeout=5)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_d064_bss_layout_exact_400_order_pin_first_and_warm_intervals(self):
        self.run_scenario('ordinary')

    def test_d064_all_unsigned_intervals_survive_micros_wrap(self):
        self.run_scenario('wrap')

    def test_d064_readiness_failure_never_touches_gpio_or_completes(self):
        self.run_scenario('not-ready')

    def test_d064_low_mismatch_is_signed_stops_after_bad_sample_and_attempts_high(self):
        for index in (0, 197, 399):
            for value in (-(1 << 31), -19, -1, 1, 2, (1 << 31) - 1):
                with self.subTest(index=index, value=value):
                    self.run_scenario('mismatch', index, 0, value)

    def test_d064_high_mismatch_is_signed_stops_after_bad_sample_and_attempts_high(self):
        for index in (0, 197, 399):
            for value in (-(1 << 31), -19, -1, 0, 2, (1 << 31) - 1):
                with self.subTest(index=index, value=value):
                    self.run_scenario('mismatch', index, 1, value)

    def test_d064_pair_mismatch_is_signed_stops_after_bad_sample_and_attempts_high(self):
        for index in (0, 197, 399):
            for value in (-(1 << 31), -19, -1, 0, 2, (1 << 31) - 1):
                with self.subTest(index=index, value=value):
                    self.run_scenario('mismatch', index, 2, value)

    def test_d064_failed_final_high_observation_retains_raw_value_and_incomplete(self):
        for value in (-(1 << 31), -19, -1, 0, 2, (1 << 31) - 1):
            with self.subTest(value=value):
                self.run_scenario('final', value)

    def test_d064_nonreturning_api_at_each_first_and_last_sample_step_stays_incomplete(self):
        for index in (0, 399):
            for step in range(7):
                with self.subTest(index=index, step=step):
                    self.run_scenario('pending', index * 7 + step)

    def test_d064_nonreturning_final_high_or_final_read_never_publishes_complete(self):
        for call in (2800, 2801):
            with self.subTest(call=call):
                self.run_scenario('pending', call)

    def test_d064_motor_enabled_compilation_is_rejected(self):
        result = self.compile('-DMOTORS_ALLOWED=1')
        self.assertNotEqual(0, result.returncode, 'Motor-enabled GPIO sketch compiled')

    def test_d064_mismatched_led_builtin_mapping_is_rejected_at_compile_time(self):
        result = self.compile('-DLED_BUILTIN=49')
        self.assertNotEqual(0, result.returncode, 'Mismatched LED_BUILTIN mapping compiled')

    def test_d064_mismatched_led3_r_mapping_is_rejected_at_compile_time(self):
        result = self.compile('-DLED3_R=51')
        self.assertNotEqual(0, result.returncode, 'Mismatched LED3_R mapping compiled')


class P0GpioAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.import_stdout, cls.import_stderr = load_capture_without_actions()

    def analyze(self, data):
        with ExitStack() as stack:
            prohibit_actions(stack)
            return self.module.analyze_record(data)

    def assert_rejected(self, data):
        with self.assertRaises(ValueError):
            self.analyze(data)

    def test_d064_import_is_quiet_and_runs_no_transport(self):
        self.assertEqual('', self.import_stdout)
        self.assertEqual('', self.import_stderr)
        self.assertTrue(callable(self.module.analyze_record))

    def test_d064_valid_fixed_record_reports_every_first_field_warm_metric_and_readback(self):
        sample = (2, 3, 5, 7, 11, 13, 0, 1, 1)
        result = self.analyze(record())
        self.assertEqual(1, result['version'])
        self.assertEqual(400, result['samples'])
        self.assertEqual(16400, result['total_elapsed_us'])
        self.assertEqual(dict(zip(FIELD_NAMES, sample)), result['first_call'])
        self.assertEqual(399, result['subsequent_calls']['samples'])
        for field, value in zip(INTERVAL_NAMES, sample[:6]):
            self.assertEqual({'min_us': value, 'max_us': value, 'p99_us': value},
                             result['subsequent_calls'][field])
        self.assertEqual({'min_us': 2, 'max_us': 2, 'p99_us': 2}, result['overhead'])
        self.assertEqual({'low_matches': 400, 'high_matches': 400,
                          'pair_matches': 400, 'final_high': True}, result['readbacks'])

    def test_d064_first_call_is_separate_and_no_interval_subtracts_overhead(self):
        samples = [(80, 1001, 1002, 1003, 1004, 1005, 0, 1, 1)]
        samples += [(5, 1, 2, 3, 4, 6, 0, 1, 1)] * 399
        result = self.analyze(record(samples))
        self.assertEqual(dict(zip(FIELD_NAMES, samples[0])), result['first_call'])
        for field, value in zip(INTERVAL_NAMES, samples[1][:6]):
            self.assertEqual({'min_us': value, 'max_us': value, 'p99_us': value},
                             result['subsequent_calls'][field])
        self.assertEqual({'min_us': 5, 'max_us': 80, 'p99_us': 5}, result['overhead'])

    def test_d064_nearest_rank_p99_for_399_warm_and_all_400_overhead_values(self):
        for order in (range(1, 400), range(399, 0, -1)):
            with self.subTest(reverse=order.start == 399):
                samples = [(9000,) * 6 + (0, 1, 1)]
                samples += [tuple(i + 500 * f for f in range(6)) + (0, 1, 1) for i in order]
                result = self.analyze(record(samples))
                for field, offset in zip(INTERVAL_NAMES, range(0, 3000, 500)):
                    self.assertEqual({'min_us': 1 + offset, 'max_us': 399 + offset,
                                      'p99_us': 396 + offset}, result['subsequent_calls'][field])
                self.assertEqual({'min_us': 1, 'max_us': 9000, 'p99_us': 396}, result['overhead'])

    def test_d064_zero_intervals_are_valid_microsecond_quantization(self):
        data = record([(0,) * 6 + (0, 1, 1)] * 400)
        result = self.analyze(data)
        self.assertEqual(0, result['total_elapsed_us'])
        for field in INTERVAL_NAMES:
            self.assertEqual({'min_us': 0, 'max_us': 0, 'p99_us': 0},
                             result['subsequent_calls'][field])

    def test_d064_record_length_must_be_exactly_14428_bytes(self):
        data = record()
        self.assertEqual(RECORD_BYTES, len(data))
        for invalid in (b'', data[:28], data[:-36], data[:-1], data + b'\0', data + data):
            with self.subTest(length=len(invalid)):
                self.assert_rejected(invalid)

    def test_d064_every_header_acceptance_field_is_exact(self):
        fields = {'version': (0, 2, UINT32_MAX), 'ready': (0, 2, UINT32_MAX),
                  'complete': (0, 2, UINT32_MAX),
                  'completed': (0, 1, 399, 401, UINT32_MAX),
                  'final_level': (-(1 << 31), -19, -1, 0, 2, (1 << 31) - 1)}
        for field, values in fields.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assert_rejected(record(**{field: value}))

    def test_d064_all_signed_readbacks_require_exact_0_1_1_at_any_position(self):
        for position in (0, 197, 399):
            for field in range(6, 9):
                values = (-(1 << 31), -19, -1, 2, (1 << 31) - 1, 1 if field == 6 else 0)
                for value in values:
                    with self.subTest(position=position, field=field, value=value):
                        samples = [(0,) * 6 + (0, 1, 1)] * 400
                        sample = list(samples[position])
                        sample[field] = value
                        samples[position] = tuple(sample)
                        self.assert_rejected(record(samples))

    def test_d064_each_of_six_intervals_must_be_below_unsigned_half_range(self):
        for field in range(6):
            for position in (0, 197, 399):
                for interval in (HALF_RANGE, HALF_RANGE + 1, UINT32_MAX):
                    with self.subTest(field=field, position=position, interval=interval):
                        samples = [(0,) * 6 + (0, 1, 1)] * 400
                        sample = list(samples[position])
                        sample[field] = interval
                        samples[position] = tuple(sample)
                        self.assert_rejected(record(samples, end=HALF_RANGE - 1))

    def test_d064_largest_valid_interval_and_total_are_accepted_without_signed_wrap(self):
        for field in range(6):
            with self.subTest(field=field):
                samples = [(0,) * 6 + (0, 1, 1)] * 400
                sample = list(samples[1])
                sample[field] = HALF_RANGE - 1
                samples[1] = tuple(sample)
                result = self.analyze(record(samples, start=UINT32_MAX - 19))
                self.assertEqual(HALF_RANGE - 1, result['total_elapsed_us'])

    def test_d064_total_half_range_and_larger_are_rejected(self):
        for total in (HALF_RANGE, HALF_RANGE + 1, UINT32_MAX):
            with self.subTest(total=total):
                self.assert_rejected(record([(0,) * 6 + (0, 1, 1)] * 400, end=total))

    def test_d064_total_covers_all_six_interval_sums_and_allows_unmeasured_gaps(self):
        self.assert_rejected(record(end=16399))
        for total in (16400, 16401, 21000):
            with self.subTest(total=total):
                self.assertEqual(total, self.analyze(record(end=total))['total_elapsed_us'])
        for field in range(6):
            with self.subTest(field=field):
                samples = [(0,) * 6 + (0, 1, 1)] * 400
                sample = list(samples[0])
                sample[field] = 1
                samples[0] = tuple(sample)
                self.assert_rejected(record(samples, end=0))

    def test_d064_interval_sum_must_not_overflow_uint32(self):
        samples = [(HALF_RANGE - 1, 0, 0, 0, 0, 0, 0, 1, 1)] * 3
        samples += [(0,) * 6 + (0, 1, 1)] * 397
        self.assert_rejected(record(samples, end=HALF_RANGE - 3))

    def test_d064_uint32_start_end_wrap_preserves_total(self):
        for start in (0, UINT32_MAX - 16399, UINT32_MAX - 7, UINT32_MAX):
            with self.subTest(start=start):
                self.assertEqual(16400, self.analyze(record(start=start))['total_elapsed_us'])

    def test_d064_decode_is_repeatable_and_does_not_mutate_bytes(self):
        data = record(start=UINT32_MAX - 7)
        original = bytes(data)
        first = self.analyze(data)
        self.assertEqual(first, self.analyze(data))
        self.assertEqual(original, data)


if __name__ == '__main__':
    unittest.main()
