# Tests D-063 startup ADC acquisition and decoding from the public contract/header.
# Separates raw signed API returns and first-use cost from accepted timing evidence.
# Uses the opaque real sketch with host stubs and synthetic bytes; no board commands.
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
CAPTURE_TOOL = PROJECT / 'tools/p0_adc_capture.py'
SAMPLES = 1000
RECORD_BYTES = 12020
HALF_RANGE = 1 << 31
UINT32_MAX = (1 << 32) - 1
ARDUINO_STUB = '''#pragma once
#include <cstdint>
#ifndef A0
#define A0 14
#endif
std::uint32_t micros();
int analogRead(std::uint32_t pin);
'''
ADC_HARNESS = '''#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <limits>
#include <string>
#include <type_traits>
#include "Arduino.h"
#include "bench/p0_adc/src/adc_capture.h"
#include "bench/p0_adc/p0_adc.ino"

static_assert(sizeof(p0::AdcCapture) == 12020);
static_assert(sizeof(p0::AdcSample) == 12);
static_assert(offsetof(p0::AdcCapture, samples) == 20);
static_assert(offsetof(p0::AdcSample, value) == 8);
static_assert(std::is_same_v<decltype(p0Adc), volatile p0::AdcCapture>);
static_assert(std::is_same_v<decltype(p0::AdcSample::value), std::int32_t>);
std::uint32_t times[4002]{};
unsigned clockCalls = 0;
unsigned readCalls = 0;
bool signedReturns = false;
int stopAt = -1;

std::uint32_t overhead(unsigned i) { return 1U + i % 7U; }
std::uint32_t elapsed(unsigned i) { return i == 0 ? 11000U : 7U + i * 37U % 991U; }
std::int32_t rawValue(unsigned i) {
    if (!signedReturns) return static_cast<std::int32_t>(i % 1024U);
    if (i == 0) return std::numeric_limits<std::int32_t>::min();
    if (i == 1) return std::numeric_limits<std::int32_t>::max();
    return -static_cast<std::int32_t>(i);
}

void checkSample(unsigned i) {
    assert(p0Adc.samples[i].overhead_us == overhead(i));
    assert(p0Adc.samples[i].elapsed_us == elapsed(i));
    assert(p0Adc.samples[i].value == rawValue(i));
}

std::uint32_t micros() {
    assert(clockCalls < 4002);
    assert(p0Adc.version == 1 && p0Adc.complete == 0);
    const unsigned expectedReads = clockCalls / 4;
    assert(readCalls == expectedReads);
    if (clockCalls == 4001 || (clockCalls != 0 && (clockCalls - 1) % 4 == 0)) {
        assert(p0Adc.completed == readCalls);
        if (readCalls != 0) checkSample(readCalls - 1);
    }
    return times[clockCalls++];
}

int analogRead(std::uint32_t pin) {
    assert(pin == 14 && pin == A0);
    assert(readCalls < 1000 && clockCalls == 4 + 4 * readCalls);
    assert(p0Adc.version == 1 && p0Adc.complete == 0);
    assert(p0Adc.completed == readCalls);
    if (static_cast<int>(readCalls) == stopAt) {
        assert(p0Adc.end_us == 0);
        for (unsigned i = 0; i < readCalls; ++i) checkSample(i);
        // End the fixture without returning from this API call: no liveness claim.
        std::exit(0);
    }
    return rawValue(readCalls++);
}

void prepare(std::uint32_t start) {
    const auto* bytes = reinterpret_cast<const volatile unsigned char*>(&p0Adc);
    for (unsigned i = 0; i < sizeof(p0Adc); ++i) assert(bytes[i] == 0);
    times[0] = start;
    std::uint32_t current = start;
    for (unsigned i = 0; i < 1000; ++i) {
        times[1 + 4 * i] = current + 3;
        times[2 + 4 * i] = times[1 + 4 * i] + overhead(i);
        times[3 + 4 * i] = times[2 + 4 * i] + 5;
        times[4 + 4 * i] = times[3 + 4 * i] + elapsed(i);
        current = times[4 + 4 * i];
    }
    times[4001] = current + 9;
}

void verifyFinished() {
    assert(clockCalls == 4002 && readCalls == 1000);
    assert(p0Adc.version == 1 && p0Adc.complete == 1 && p0Adc.completed == 1000);
    assert(p0Adc.start_us == times[0] && p0Adc.end_us == times[4001]);
    for (unsigned i = 0; i < 1000; ++i) checkSample(i);
}

void verifyFrozenLoop() {
    unsigned char saved[sizeof(p0Adc)];
    const auto* bytes = reinterpret_cast<const volatile unsigned char*>(&p0Adc);
    for (unsigned i = 0; i < sizeof(p0Adc); ++i) saved[i] = bytes[i];
    for (unsigned i = 0; i < 10000; ++i) loop();
    assert(clockCalls == 4002 && readCalls == 1000);
    for (unsigned i = 0; i < sizeof(p0Adc); ++i) assert(bytes[i] == saved[i]);
}

int main(int argc, char** argv) {
    assert(argc == 2);
    const std::string scenario = argv[1];
    signedReturns = scenario == "signed";
    if (scenario == "pending-first") stopAt = 0;
    if (scenario == "pending-last") stopAt = 999;
    prepare(scenario == "wrap" ? 0xfffffff0U : 51U);
    setup();
    assert(stopAt == -1);
    verifyFinished();
    if (scenario == "freeze") verifyFrozenLoop();
}
'''


def load_capture_without_actions():
    name = 'sumo_adc_capture_contract_fixture'
    specification = importlib.util.spec_from_file_location(name, CAPTURE_TOOL)
    module = importlib.util.module_from_spec(specification)
    stdout, stderr = io.StringIO(), io.StringIO()
    forbidden = AssertionError('Import/decoding must not run commands or networking')
    with ExitStack() as stack:
        for target in ('run', 'Popen', 'call', 'check_call', 'check_output'):
            stack.enter_context(mock.patch.object(subprocess, target, side_effect=forbidden))
        for target in ('socket', 'create_connection'):
            stack.enter_context(mock.patch.object(socket, target, side_effect=forbidden))
        stack.enter_context(mock.patch.object(os, 'system', side_effect=forbidden))
        stack.enter_context(mock.patch('builtins.input', side_effect=forbidden))
        stack.enter_context(mock.patch.object(sys, 'argv', ['p0_adc_capture.py', '--invalid']))
        stack.enter_context(mock.patch.dict(sys.modules, {name: module}))
        stack.enter_context(mock.patch.object(sys, 'path', [str(PROJECT / 'tools'), *sys.path]))
        stack.enter_context(redirect_stdout(stdout))
        stack.enter_context(redirect_stderr(stderr))
        specification.loader.exec_module(module)
    return module, stdout.getvalue(), stderr.getvalue()


def record(samples=None, *, start=0, end=None, version=1, complete=1, completed=1000):
    # Independent literal layout, not capture-tool format/constants.
    if samples is None:
        samples = [(2, 31, 17)] * SAMPLES
    if end is None:
        end = (start + sum(overhead + elapsed for overhead, elapsed, _ in samples)) & UINT32_MAX
    header = struct.pack('<IIIII', version, complete, completed, start, end)
    return header + b''.join(struct.pack('<IIi', *sample) for sample in samples)


class P0AdcSketchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = shutil.which('g++')
        if cls.compiler is None:
            raise RuntimeError('g++ is required; run these host tests under WSL')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-p0-adc-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        (cls.root / 'Arduino.h').write_text(ARDUINO_STUB)
        cls.harness = cls.root / 'adc.cpp'
        cls.harness.write_text(ADC_HARNESS)
        cls.executable = cls.root / 'adc'
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

    def run_scenario(self, scenario):
        result = subprocess.run([str(self.executable), scenario],
                                capture_output=True, text=True, check=False, timeout=5)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_d063_zero_bss_exact_a0_count_order_and_first_warm_costs(self):
        self.run_scenario('ordinary')

    def test_d063_preserves_signed_wrapper_returns_without_clamping(self):
        self.run_scenario('signed')

    def test_d063_adjacent_overhead_and_adc_intervals_survive_uint32_wrap(self):
        self.run_scenario('wrap')

    def test_d063_empty_loop_freezes_all_record_bytes_and_calls_no_api(self):
        self.run_scenario('freeze')

    def test_d063_nonreturning_first_call_cannot_publish_complete(self):
        self.run_scenario('pending-first')

    def test_d063_nonreturning_last_call_retains_only_completed_prefix(self):
        self.run_scenario('pending-last')

    def test_d063_motor_enabled_compilation_is_rejected(self):
        result = self.compile('-DMOTORS_ALLOWED=1')
        self.assertNotEqual(0, result.returncode, 'Motor-enabled ADC sketch compiled')

    def test_d063_wrong_installed_a0_index_is_rejected_at_compile_time(self):
        result = self.compile('-DA0=15')
        self.assertNotEqual(0, result.returncode, 'Mismatched A0 mapping compiled')


class P0AdcAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.import_stdout, cls.import_stderr = load_capture_without_actions()

    def analyze(self, data):
        forbidden = AssertionError('Pure decoder must not run commands or networking')
        with ExitStack() as stack:
            for target in ('run', 'Popen', 'call', 'check_call', 'check_output'):
                stack.enter_context(mock.patch.object(subprocess, target, side_effect=forbidden))
            stack.enter_context(mock.patch.object(socket, 'socket', side_effect=forbidden))
            stack.enter_context(mock.patch.object(os, 'system', side_effect=forbidden))
            return self.module.analyze_record(data)

    def assert_rejected(self, data):
        with self.assertRaises(ValueError):
            self.analyze(data)

    def test_d063_import_is_quiet_and_executes_no_capture_or_board_commands(self):
        self.assertEqual('', self.import_stdout)
        self.assertEqual('', self.import_stderr)
        self.assertTrue(callable(self.module.analyze_record))

    def test_d063_public_summary_preserves_unadjusted_first_and_warm_results(self):
        samples = [(8, 17000, 0)] + [(3, i, i) for i in range(999, 0, -1)]
        result = self.analyze(record(samples))
        expected = {
            'version': 1, 'samples': 1000, 'total_elapsed_us': 519505,
            'first_call': {'elapsed_us': 17000, 'overhead_us': 8, 'value': 0},
            'subsequent_calls': {'samples': 999, 'min_us': 1, 'max_us': 999, 'p99_us': 990},
            'overhead': {'min_us': 3, 'max_us': 8, 'p99_us': 3},
            'zero_results': 1, 'nonzero_results': 999, 'value_min': 0, 'value_max': 999,
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertIn(key, result)
                self.assertEqual(value, result[key])

    def test_d063_zero_adc_code_is_valid_and_counted_without_voltage_conversion(self):
        result = self.analyze(record([(0, 0, 0)] * SAMPLES))
        self.assertEqual(1000, result['zero_results'])
        self.assertEqual(0, result['nonzero_results'])
        self.assertEqual(0, result['value_min'])
        self.assertEqual(0, result['value_max'])
        self.assertEqual(0, result['total_elapsed_us'])
        self.assertNotIn('volts', result)

    def test_d063_adc_highest_valid_code_1023_is_accepted(self):
        result = self.analyze(record([(1, 10, 1023)] * SAMPLES))
        self.assertEqual(0, result['zero_results'])
        self.assertEqual(1000, result['nonzero_results'])
        self.assertEqual(1023, result['value_min'])
        self.assertEqual(1023, result['value_max'])

    def test_d063_nearest_rank_990_of_999_subsequent_calls_is_inclusive(self):
        for below, expected in ((988, 27), (989, 27), (990, 4)):
            with self.subTest(below=below):
                warm = [4] * below + [27] * (990 - below) + [900] * 9
                samples = [(0, 19000, 17)] + [(0, value, 17) for value in reversed(warm)]
                result = self.analyze(record(samples))
                self.assertEqual(expected, result['subsequent_calls']['p99_us'])
                self.assertEqual(900, result['subsequent_calls']['max_us'])

    def test_d063_nearest_rank_990_of_all_1000_overhead_samples_is_inclusive(self):
        for below, expected in ((989, 17), (990, 2), (991, 2)):
            with self.subTest(below=below):
                costs = [2] * below + [17] + [80] * (999 - below)
                samples = [(value, 200, 17) for value in reversed(costs)]
                result = self.analyze(record(samples))
                self.assertEqual(expected, result['overhead']['p99_us'])
                self.assertEqual(2, result['overhead']['min_us'])
                self.assertEqual(80, result['overhead']['max_us'])

    def test_d063_record_length_must_be_exactly_12020_bytes(self):
        data = record()
        self.assertEqual(RECORD_BYTES, len(data))
        for invalid in (b'', data[:20], data[:-12], data[:-1], data + b'\0', data + data):
            with self.subTest(length=len(invalid)):
                self.assert_rejected(invalid)

    def test_d063_version_complete_and_count_are_exact(self):
        invalid_values = {
            'version': (0, 2, UINT32_MAX),
            'complete': (0, 2, UINT32_MAX),
            'completed': (0, 1, 999, 1001, UINT32_MAX),
        }
        for field, values in invalid_values.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assert_rejected(record(**{field: value}))

    def test_d063_negative_error_and_above_10_bit_codes_rejected_at_any_position(self):
        for position in (0, 500, 999):
            for value in (-(1 << 31), -19, -5, -1, 1024, (1 << 31) - 1):
                with self.subTest(position=position, value=value):
                    samples = [(0, 1, 17)] * SAMPLES
                    samples[position] = (0, 1, value)
                    self.assert_rejected(record(samples))

    def test_d063_each_overhead_and_elapsed_interval_must_be_below_half_range(self):
        for field in (0, 1):
            for position in (0, 500, 999):
                for interval in (HALF_RANGE, HALF_RANGE + 1, UINT32_MAX):
                    with self.subTest(field=field, position=position, interval=interval):
                        samples = [(0, 0, 17)] * SAMPLES
                        sample = [0, 0, 17]
                        sample[field] = interval
                        samples[position] = tuple(sample)
                        self.assert_rejected(record(samples, end=HALF_RANGE - 1))

    def test_d063_largest_valid_interval_and_total_are_accepted_without_signed_wrap(self):
        for field in (0, 1):
            with self.subTest(field=field):
                samples = [(0, 0, 17)] * SAMPLES
                sample = [0, 0, 17]
                sample[field] = HALF_RANGE - 1
                samples[1] = tuple(sample)
                result = self.analyze(record(samples, start=UINT32_MAX - 19))
                self.assertEqual(HALF_RANGE - 1, result['total_elapsed_us'])

    def test_d063_total_half_range_and_larger_are_rejected(self):
        for total in (HALF_RANGE, HALF_RANGE + 1, UINT32_MAX):
            with self.subTest(total=total):
                self.assert_rejected(record([(0, 0, 17)] * SAMPLES, end=total))

    def test_d063_total_covers_both_interval_sums_and_allows_unmeasured_gaps(self):
        # Every sample contributes 2 overhead + 31 elapsed = 33000 overall.
        self.assert_rejected(record(end=32999))
        for total in (33000, 33001, 45000):
            with self.subTest(total=total):
                self.assertEqual(total, self.analyze(record(end=total))['total_elapsed_us'])

    def test_d063_interval_sum_is_not_allowed_to_overflow_uint32(self):
        samples = [(0, HALF_RANGE - 1, 17)] * 3 + [(0, 0, 17)] * 997
        self.assert_rejected(record(samples, end=HALF_RANGE - 3))

    def test_d063_uint32_start_end_wrap_preserves_total(self):
        for start in (0, UINT32_MAX - 32999, UINT32_MAX - 7, UINT32_MAX):
            with self.subTest(start=start):
                self.assertEqual(33000, self.analyze(record(start=start))['total_elapsed_us'])

    def test_d063_decode_is_repeatable_and_does_not_mutate_bytes(self):
        data = record(start=UINT32_MAX - 7)
        original = bytes(data)
        first = self.analyze(data)
        self.assertEqual(first, self.analyze(data))
        self.assertEqual(original, data)


if __name__ == '__main__':
    unittest.main()
