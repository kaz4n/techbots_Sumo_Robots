# Tests D-065 from its frozen contract/header, without reading its implementation.
# Preserves actual calls, clock faults, cleanup, independent datasets and raw records.
# Strict C++17/UBSan runs the opaque sketch; Python decoding never contacts a board.
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
CAPTURE_TOOL = PROJECT / 'tools/p0_qtr_capture.py'
HALF = 1 << 31
MAX = (1 << 32) - 1
PINS = (2, 4, 7, 8)
INTERVALS = ('overhead_us', 'drive_us', 'charge_us', 'release_us',
             'observe_us', 'cleanup_us', 'total_us')
FIELDS = ('mode', 'outcome') + INTERVALS + ('charge_polls', 'polls',
          'low_mask', 'timeout_mask', 'first_low_0', 'first_low_1',
          'first_low_2', 'first_low_3', 'cleanup_calls')
ARDUINO_STUB = '''#pragma once
#include <cstdint>
#ifndef D2
#define D2 2
#endif
#ifndef D4
#define D4 4
#endif
#ifndef D7
#define D7 7
#endif
#ifndef D8
#define D8 8
#endif
#define INPUT 0
#define OUTPUT 1
#define INPUT_PULLUP 2
#define LOW 0
#define HIGH 1
std::uint32_t micros();
void pinMode(std::uint32_t pin, std::uint32_t mode);
void digitalWrite(std::uint32_t pin, std::uint32_t value);
int digitalRead(std::uint32_t pin);
'''
HARNESS = '''#include <cassert>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <type_traits>
#include <vector>
#include "Arduino.h"
#include "bench/p0_qtr/src/qtr_capture.h"
#include "bench/p0_qtr/p0_qtr.ino"

static_assert(sizeof(p0::QtrSample) == 72);
static_assert(sizeof(p0::QtrCapture) == 14424);
static_assert(offsetof(p0::QtrCapture, samples) == 24);
static_assert(offsetof(p0::QtrSample, mode) == 0);
static_assert(offsetof(p0::QtrSample, outcome) == 4);
static_assert(offsetof(p0::QtrSample, overhead_us) == 8);
static_assert(offsetof(p0::QtrSample, total_us) == 32);
static_assert(offsetof(p0::QtrSample, first_low_us) == 52);
static_assert(offsetof(p0::QtrSample, cleanup_calls) == 68);
static_assert(std::is_same_v<decltype(p0Qtr), volatile p0::QtrCapture>);
struct Event { unsigned op, a, b, result, completed; };
std::vector<Event> events;
bool acquisitionRunning = false;
void* operator new(std::size_t bytes) {
    assert(!acquisitionRunning);
    void* pointer = std::malloc(bytes);
    if (pointer == nullptr) std::abort();
    return pointer;
}
void* operator new[](std::size_t bytes) { return ::operator new(bytes); }
void operator delete(void* pointer) noexcept {
    assert(!acquisitionRunning);
    std::free(pointer);
}
void operator delete[](void* pointer) noexcept { ::operator delete(pointer); }
void operator delete(void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
void operator delete[](void* pointer, std::size_t) noexcept { ::operator delete(pointer); }
unsigned cursor = 0;
int stopAt = -1;
std::uint32_t expected[200][18]{};
unsigned checkPrefix = 0;

void checkPublished() {
    assert(p0Qtr.complete == 0);
    assert(p0Qtr.end_us == 0);
    const auto* actual = reinterpret_cast<const volatile unsigned char*>(p0Qtr.samples);
    const auto* wanted = reinterpret_cast<const unsigned char*>(expected);
    for (unsigned i = 0; i < checkPrefix * 72; ++i) assert(actual[i] == wanted[i]);
}

std::uint32_t step(unsigned op, unsigned a = 0, unsigned b = 0) {
    if (cursor >= events.size()) {
        std::fprintf(stderr, "extra call op=%u a=%u b=%u index=%u\\n", op, a, b, cursor);
        std::abort();
    }
    const auto& e = events[cursor];
    if (e.op != op || e.a != a || e.b != b) {
        std::fprintf(stderr, "call[%u] expected %u/%u/%u got %u/%u/%u\\n",
                     cursor, e.op, e.a, e.b, op, a, b);
        std::abort();
    }
    assert(p0Qtr.completed == e.completed);
    checkPrefix = e.completed;
    checkPublished();
    if (static_cast<int>(cursor) == stopAt) std::_Exit(0);
    ++cursor;
    return e.result;
}
std::uint32_t micros() { return step(0); }
void pinMode(std::uint32_t p, std::uint32_t m) { (void)step(1, p, m); }
void digitalWrite(std::uint32_t p, std::uint32_t v) { (void)step(2, p, v); }
int digitalRead(std::uint32_t p) { return static_cast<std::int32_t>(step(3, p)); }
std::uint32_t p0::qtrReadyMask() { return step(4); }

int main() {
    unsigned count = 0, prefix = 0;
    assert(std::scanf("%u %d %u", &count, &stopAt, &prefix) == 3);
    events.resize(count);
    for (auto& e : events)
        assert(std::scanf("%u %u %u %u %u", &e.op, &e.a, &e.b, &e.result, &e.completed) == 5);
    for (unsigned i = 0; i < prefix; ++i)
        for (unsigned j = 0; j < 18; ++j) assert(std::scanf("%u", &expected[i][j]) == 1);
    const auto* bytes = reinterpret_cast<const volatile unsigned char*>(&p0Qtr);
    for (unsigned i = 0; i < sizeof(p0Qtr); ++i) assert(bytes[i] == 0);
    acquisitionRunning = true;
    setup();
    assert(stopAt == -1 && cursor == events.size());
    unsigned char frozen[sizeof(p0Qtr)];
    for (unsigned i = 0; i < sizeof(p0Qtr); ++i) frozen[i] = bytes[i];
    for (unsigned i = 0; i < 10000; ++i) loop();
    for (unsigned i = 0; i < sizeof(p0Qtr); ++i) assert(bytes[i] == frozen[i]);
    acquisitionRunning = false;
    assert(std::fwrite(frozen, 1, sizeof(frozen), stdout) == sizeof(frozen));
}
'''


def sample(mode=0, *, observe=None, low=None, overhead=2, drive=3,
           charge=11, release=4, cleanup=5, charge_polls=1, polls=1):
    observe = (7 if mode == 0 else 1500) if observe is None else observe
    low = (15 if mode == 0 else 0) if low is None else low
    outcome = 2 if observe >= 1500 else 1
    first = [observe if low & (1 << bit) else MAX for bit in range(4)]
    return [mode, outcome, overhead, drive, charge, release, observe, cleanup,
            drive + charge + release + observe + cleanup,
            charge_polls, polls, low, (15 ^ low) if outcome == 2 else 0, *first, 4]


def normal_samples():
    return [sample(int(index >= 100)) for index in range(200)]


def record(samples=None, *, version=1, ready_mask=3, complete=1, completed=200,
           start=0, end=None):
    samples = normal_samples() if samples is None else samples
    if end is None:
        end = (start + sum(row[2] + row[8] for row in samples)) & MAX
    return struct.pack('<6I', version, ready_mask, complete, completed, start, end) + \
        b''.join(struct.pack('<18I', *row) for row in samples)


class Script:
    """An independent sequence of public API calls, generated from D-065."""
    def __init__(self, *, ready=3, start=51, overrides=None, end_gap=9):
        self.events, self.samples = [], []
        self.current, self.start = start, start
        self.finished = 0
        self.event(4, result=ready)
        self.ready = ready
        if ready != 3:
            return
        self.clock(absolute=start)
        for index in range(200):
            options = (overrides or {}).get(index, {})
            good = self.acquisition(int(index >= 100), **options)
            self.finished += 1
            if not good:
                return
        self.end = self.clock(delta=end_gap)

    def event(self, op, a=0, b=0, result=0):
        self.events.append((op, a, b, result & MAX, self.finished))

    def clock(self, *, delta=0, absolute=None):
        self.current = ((self.current + delta) if absolute is None else absolute) & MAX
        self.event(0, result=self.current)
        return self.current

    def acquisition(self, mode, *, charge_steps=(11,), passes=None,
                    overhead=2, drive=3, release=4, cleanup=5):
        if passes is None:
            passes = [(7, (0, 0, 0, 0))] if mode == 0 else [(1500, (1, 1, 1, 1))]
        values = [mode, 0, overhead, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, MAX, MAX, MAX, MAX, 4]
        self.clock(delta=1)
        self.clock(delta=overhead)
        total_start = self.clock(delta=2)
        outcome = 5 if overhead >= HALF else 0
        if not outcome:
            for pin in PINS:
                self.event(1, pin, 1)
                self.event(2, pin, 1)
            drive_end = self.clock(delta=drive)
            values[3] = drive
            if drive >= HALF:
                outcome = 5
            else:
                for count, elapsed in enumerate(charge_steps, 1):
                    self.clock(absolute=drive_end + elapsed)
                    values[4], values[9] = elapsed, count
                    if elapsed >= HALF:
                        outcome = 5
                        break
                    if elapsed >= 11:
                        break
                else:
                    outcome = 3
                if not outcome:
                    for pin in PINS:
                        self.event(1, pin, 0 if mode == 0 else 2)
                    epoch = self.clock(delta=release)
                    values[5] = release
                    if release >= HALF:
                        outcome = 5
                    else:
                        for count, (elapsed, levels) in enumerate(passes, 1):
                            for pin, level in zip(PINS, levels):
                                self.event(3, pin, result=level)
                            self.clock(absolute=epoch + elapsed)
                            values[6], values[10] = elapsed, count
                            if elapsed >= HALF:
                                outcome = 5
                            elif any(level not in (0, 1) for level in levels):
                                outcome = 6
                            else:
                                for bit, level in enumerate(levels):
                                    if level == 0 and not values[11] & (1 << bit):
                                        values[11] |= 1 << bit
                                        values[13 + bit] = elapsed
                                if elapsed >= 1500:
                                    outcome, values[12] = 2, 15 ^ values[11]
                                elif values[11] == 15:
                                    outcome = 1
                            if outcome:
                                break
                        else:
                            outcome = 4
        for pin in PINS:
            self.event(1, pin, 0)
        final = self.clock(delta=cleanup)
        values[7], values[8] = cleanup, (final - total_start) & MAX
        if cleanup >= HALF or values[8] >= HALF:
            outcome = 5
        values[1] = outcome
        self.samples.append(values)
        return outcome in (1, 2)

    def input_bytes(self, stop=-1):
        lines = [f'{len(self.events)} {stop} {len(self.samples)}']
        lines.extend(' '.join(map(str, event)) for event in self.events)
        lines.extend(' '.join(map(str, row)) for row in self.samples)
        return ('\n'.join(lines) + '\n').encode('ascii')


def prohibit_actions(stack):
    forbidden = AssertionError('Pure import/decoder may not run commands or networking')
    for target in ('run', 'Popen', 'call', 'check_call', 'check_output'):
        stack.enter_context(mock.patch.object(subprocess, target, side_effect=forbidden))
    for target in ('socket', 'create_connection'):
        stack.enter_context(mock.patch.object(socket, target, side_effect=forbidden))
    stack.enter_context(mock.patch.object(os, 'system', side_effect=forbidden))
    stack.enter_context(mock.patch('builtins.input', side_effect=forbidden))


def load_decoder():
    name = 'sumo_qtr_contract_fixture'
    spec = importlib.util.spec_from_file_location(name, CAPTURE_TOOL)
    module = importlib.util.module_from_spec(spec)
    out, err = io.StringIO(), io.StringIO()
    with ExitStack() as stack:
        prohibit_actions(stack)
        stack.enter_context(mock.patch.dict(sys.modules, {name: module}))
        stack.enter_context(mock.patch.object(sys, 'path', [str(PROJECT / 'tools'), *sys.path]))
        stack.enter_context(mock.patch.object(sys, 'argv', ['p0_qtr_capture.py', '--invalid']))
        stack.enter_context(redirect_stdout(out))
        stack.enter_context(redirect_stderr(err))
        spec.loader.exec_module(module)
    return module, out.getvalue(), err.getvalue()


class P0QtrSketchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = shutil.which('g++')
        if cls.compiler is None:
            raise RuntimeError('g++ is required; run under WSL')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-p0-qtr-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        (cls.root / 'Arduino.h').write_text(ARDUINO_STUB)
        cls.harness = cls.root / 'qtr.cpp'
        cls.harness.write_text(HARNESS)
        cls.executable = cls.root / 'qtr'
        result = cls.compile()
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    @classmethod
    def compile(cls, *definitions):
        destination = cls.executable if not definitions else cls.root / 'negative'
        return subprocess.run([cls.compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
                               '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                               '-fno-sanitize-recover=all', '-I', str(cls.root),
                               '-I', str(PROJECT), '-I', str(PROJECT / 'src'),
                               *definitions, str(cls.harness), '-o', str(destination)],
                              capture_output=True, text=True, check=False, timeout=30)

    def run_script(self, script, stop=-1):
        result = subprocess.run([str(self.executable)], input=script.input_bytes(stop),
                                capture_output=True, check=False, timeout=10)
        self.assertEqual(0, result.returncode, result.stderr.decode(errors='replace'))
        if stop != -1:
            self.assertEqual(b'', result.stdout)
            return
        self.assertEqual(14424, len(result.stdout))
        words = struct.unpack('<3606I', result.stdout)
        self.assertEqual(1, words[0])
        self.assertEqual(script.ready, words[1])
        self.assertEqual(script.finished, words[3])
        if script.ready != 3:
            self.assertEqual(0, words[2])
        else:
            self.assertEqual(script.start, words[4])
            valid = script.finished == 200 and script.samples[-1][1] in (1, 2)
            if valid:
                valid = ((script.end - script.start) & MAX) < HALF
            self.assertEqual(script.end if valid else 0, words[5])
            self.assertEqual(int(valid), words[2])
            for index, expected in enumerate(script.samples):
                self.assertEqual(expected, list(words[6 + 18 * index:24 + 18 * index]),
                                 f'sample {index}')
        self.assertTrue(all(value == 0 for value in words[6 + 18 * script.finished:]))
        return result.stdout

    def test_d065_exact_order_both_modes_200_complete_samples_and_empty_loop(self):
        self.run_script(Script())

    def test_d065_readiness_zero_or_either_missing_port_never_touches_pins(self):
        for ready in (0, 1, 2):
            with self.subTest(ready=ready):
                self.run_script(Script(ready=ready))

    def test_d065_zero_overhead_and_zero_observe_are_valid_quantization(self):
        self.run_script(Script(overrides={0: {'overhead': 0, 'drive': 0, 'release': 0,
                         'cleanup': 0, 'passes': [(0, (0, 0, 0, 0))]}}))

    def test_d065_charge_10_is_insufficient_11_is_exact(self):
        self.run_script(Script(overrides={0: {'charge_steps': (0, 9, 10, 11)}}))

    def test_d065_charge_last_guard_call_qualifies_before_exhaustion(self):
        self.run_script(Script(overrides={0: {'charge_steps': (10,) * 4095 + (11,)}}))

    def test_d065_stopped_charge_clock_exhausts_exactly_4096_and_cleans(self):
        for index in (0, 100, 199):
            with self.subTest(index=index):
                self.run_script(Script(overrides={index: {'charge_steps': (0,) * 4096}}))

    def test_d065_four_real_reads_include_previously_low_pins_and_sticky_mask(self):
        passes = [(0, (0, 1, 1, 1)), (2, (1, 0, 1, 1)),
                  (5, (1, 1, 0, 1)), (1499, (1, 1, 1, 0))]
        self.run_script(Script(overrides={0: {'passes': passes}}))

    def test_d065_all_low_before_deadline_and_deadline_wins_exact_tie_overshoot(self):
        for elapsed in (1499, 1500, 1501, 2107):
            with self.subTest(elapsed=elapsed):
                self.run_script(Script(overrides={0: {'passes': [(elapsed, (0, 0, 0, 0))]}}))

    def test_d065_each_low_mask_retained_on_deadline_with_actual_late_times(self):
        for mask in range(16):
            with self.subTest(mask=mask):
                levels = tuple(0 if mask & 1 << bit else 1 for bit in range(4))
                self.run_script(Script(overrides={0: {'passes': [(1601, levels)]}}))

    def test_d065_pullup_early_low_does_not_abort_remaining_samples(self):
        for index in (100, 157, 199):
            with self.subTest(index=index):
                self.run_script(Script(overrides={index: {'passes': [
                    (2, (0, 1, 1, 1)), (1500, (1, 1, 1, 1))]}}))

    def test_d065_pullup_all_low_is_retained_and_all_200_still_complete(self):
        self.run_script(Script(overrides={100: {'passes': [(4, (0, 0, 0, 0))]}}))

    def test_d065_stopped_observation_clock_exhausts_exactly_4096_and_cleans(self):
        self.run_script(Script(overrides={0: {'passes': [(0, (1, 1, 1, 1))] * 4096}}))

    def test_d065_last_observation_pass_deadline_or_all_low_wins_guard(self):
        for elapsed, levels in ((1499, (0, 0, 0, 0)), (1500, (1, 1, 1, 1))):
            with self.subTest(elapsed=elapsed):
                passes = [(0, (1, 1, 1, 1))] * 4095 + [(elapsed, levels)]
                self.run_script(Script(overrides={0: {'passes': passes}}))

    def test_d065_bad_levels_finish_all_four_reads_then_cleanup_and_fail(self):
        for bit in range(4):
            for invalid in (-2147483648, -19, -1, 2, 2147483647):
                with self.subTest(bit=bit, invalid=invalid):
                    levels = [1, 1, 1, 1]
                    levels[bit] = invalid
                    self.run_script(Script(overrides={0: {'passes': [(4, levels)]}}))

    def test_d065_bad_level_has_priority_over_deadline(self):
        self.run_script(Script(overrides={0: {'passes': [(1500, (-1, 1, 1, 1))]}}))

    def test_d065_bad_level_discards_only_bad_pass_retains_prior_lows_and_last_sample(self):
        for index in (0, 100, 199):
            with self.subTest(index=index):
                passes = [(3, (0, 1, 1, 1)), (6, (1, 0, -1, 1))]
                self.run_script(Script(overrides={index: {'passes': passes}}))

    def test_d065_clock_fault_has_priority_over_bad_level(self):
        self.run_script(Script(overrides={0: {'passes': [(HALF, (-1, 1, 1, 1))]}}))

    def test_d065_cleanup_clock_fault_has_priority_over_bad_level_and_poll_guard(self):
        for passes in ([(4, (-1, 1, 1, 1))], [(0, (1, 1, 1, 1))] * 4096):
            with self.subTest(passes=len(passes)):
                self.run_script(Script(overrides={0: {'passes': passes, 'cleanup': HALF}}))

    def test_d065_each_measured_interval_detects_ambiguous_half_range_and_cleans(self):
        for value in (HALF, HALF + 1, MAX):
            changes = ({'overhead': value}, {'drive': value}, {'charge_steps': (value,)},
                       {'release': value}, {'passes': [(value, (1, 1, 1, 1))]},
                       {'cleanup': value})
            for change in changes:
                with self.subTest(change=change):
                    self.run_script(Script(overrides={0: change}))

    def test_d065_sample_total_fault_even_when_component_intervals_valid(self):
        self.run_script(Script(overrides={0: {'drive': HALF - 11}}))

    def test_d065_record_total_fault_keeps_200_samples_but_never_complete(self):
        self.run_script(Script(end_gap=HALF))

    def test_d065_all_intervals_and_record_survive_uint32_wrap(self):
        for start in (MAX - 4, MAX - 25, MAX - 2000, MAX):
            with self.subTest(start=start):
                self.run_script(Script(start=start))

    def test_d065_nonreturning_first_and_last_sample_calls_never_publish_complete(self):
        script = Script()
        positions = [i for i, event in enumerate(script.events)
                     if event[4] in (0, 199) and event[0] in (1, 2, 3)]
        for position in positions:
            with self.subTest(position=position):
                self.run_script(script, stop=position)

    def test_d065_motor_enabled_compilation_rejected(self):
        self.assertNotEqual(0, self.compile('-DMOTORS_ALLOWED=1').returncode)

    def test_d065_each_wrong_installed_pin_mapping_rejected(self):
        for pin in PINS:
            with self.subTest(pin=pin):
                self.assertNotEqual(0, self.compile(f'-DD{pin}={pin + 1}').returncode)

    def test_d065_real_sketch_record_decodes_and_real_stimulus_failure_rejects(self):
        module, _, _ = load_decoder()
        good = self.run_script(Script(start=MAX - 5))
        bad = self.run_script(Script(overrides={173: {'passes': [
            (9, (1, 0, 1, 1)), (1500, (1, 1, 1, 1))]}}))
        with ExitStack() as stack:
            prohibit_actions(stack)
            self.assertEqual(200, module.analyze_record(good)['samples'])
            with self.assertRaisesRegex(ValueError, 'pull-up stimulus'):
                module.analyze_record(bad)


class P0QtrDecoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module, cls.import_out, cls.import_err = load_decoder()

    def analyze(self, data):
        with ExitStack() as stack:
            prohibit_actions(stack)
            return self.module.analyze_record(data)

    def reject(self, data, regex=None):
        with self.assertRaisesRegex(ValueError, regex or '.'):
            self.analyze(data)

    def changed(self, index, field, value, **header):
        rows = normal_samples()
        rows[index][FIELDS.index(field)] = value
        return record(rows, **header)

    def test_d065_import_is_quiet_pure_and_has_public_decoder(self):
        self.assertEqual('', self.import_out)
        self.assertEqual('', self.import_err)
        self.assertTrue(callable(self.module.analyze_record))

    def test_d065_separate_datasets_count_first_sample_and_unsubtracted_intervals(self):
        rows = normal_samples()
        for index in range(200):
            mode = int(index >= 100)
            warm_index = index % 100
            rows[index] = sample(mode, overhead=3 if warm_index else 80,
                                 drive=10000 if warm_index == 0 else 100 - warm_index,
                                 release=5 + mode, cleanup=7 + mode)
        result = self.analyze(record(rows))
        self.assertEqual(1, result['version'])
        self.assertEqual(200, result['samples'])
        self.assertEqual(sum(row[2] + row[8] for row in rows), result['total_elapsed_us'])
        for mode, key in enumerate(('neutral', 'diagnostic_pullup')):
            with self.subTest(dataset=key):
                dataset = result[key]
                self.assertEqual(100, dataset['samples'])
                first = {name: rows[100 * mode][pos] for pos, name in enumerate(FIELDS[:13])}
                first.update(first_low_us=rows[100 * mode][13:17], cleanup_calls=4)
                self.assertEqual(first, dataset['first_sample'])
                self.assertEqual(99, dataset['subsequent_samples']['samples'])
                for name in INTERVALS:
                    values = sorted(row[FIELDS.index(name)] for row in rows[100 * mode + 1:100 * mode + 100])
                    expected = {'min_us': values[0], 'max_us': values[-1], 'p99_us': values[98]}
                    self.assertEqual(expected, dataset['subsequent_samples']['intervals'][name])
                self.assertEqual({'min_us': 3, 'max_us': 80, 'p99_us': 3}, dataset['overhead'])
                self.assertEqual(100 if mode == 0 else 0, dataset['all_low_samples'])
                self.assertEqual(100 if mode == 1 else 0, dataset['deadline_samples'])
                self.assertEqual({'0' if mode == 0 else '15': 100}, dataset['timeout_masks'])
                self.assertEqual({'min': 1, 'max': 1}, dataset['poll_range'])

    def test_d065_neutral_all_high_deadlines_are_valid_observations(self):
        rows = [sample(0, observe=1500, low=0)] * 100 + [sample(1)] * 100
        result = self.analyze(record(rows))
        self.assertEqual(100, result['neutral']['deadline_samples'])
        self.assertEqual({'15': 100}, result['neutral']['timeout_masks'])

    def test_d065_neutral_every_mask_and_late_low_retained_in_valid_record(self):
        for mask in range(16):
            with self.subTest(mask=mask):
                rows = normal_samples()
                rows[0] = sample(observe=1501, low=mask)
                result = self.analyze(record(rows))
                self.assertEqual(mask, result['neutral']['first_sample']['low_mask'])
                self.assertEqual(15 ^ mask, result['neutral']['first_sample']['timeout_mask'])

    def test_d065_exact_record_length_required(self):
        data = record()
        self.assertEqual(14424, len(data))
        for malformed in (b'', data[:24], data[:-72], data[:-1], data + b'\0', data * 2):
            with self.subTest(length=len(malformed)):
                self.reject(malformed)

    def test_d065_all_header_acceptance_fields_exact(self):
        for field, values in {'version': (0, 2, MAX), 'ready_mask': (0, 1, 2, 4, MAX),
                              'complete': (0, 2, MAX), 'completed': (0, 1, 100, 199, 201, MAX)}.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.reject(record(**{field: value}))

    def test_d065_modes_must_follow_exact_100_then_100_labels(self):
        for index in (0, 99, 100, 199):
            for value in (1 - int(index >= 100), 2, MAX):
                with self.subTest(index=index, value=value):
                    self.reject(self.changed(index, 'mode', value))

    def test_d065_fault_and_unknown_outcomes_never_accepted(self):
        for index in (0, 99, 100, 199):
            for outcome in (0, 3, 4, 5, 6, 7, MAX):
                with self.subTest(index=index, outcome=outcome):
                    self.reject(self.changed(index, 'outcome', outcome))

    def test_d065_each_interval_excludes_half_range_even_with_wrapping_total(self):
        for field in INTERVALS:
            for value in (HALF, HALF + 1, MAX):
                for index in (0, 199):
                    with self.subTest(field=field, value=value, index=index):
                        self.reject(self.changed(index, field, value, end=HALF - 1))

    def test_d065_charge_at_least_11_and_polls_both_within_guard(self):
        for charge in (0, 9, 10):
            self.reject(self.changed(0, 'charge_us', charge))
        for field in ('charge_polls', 'polls'):
            for value in (0, 4097, MAX):
                with self.subTest(field=field, value=value):
                    self.reject(self.changed(0, field, value))
            for value in (1, 4095, 4096):
                with self.subTest(field=field, value=value):
                    self.analyze(self.changed(0, field, value))

    def test_d065_cleanup_attempt_count_is_exactly_four(self):
        for value in (0, 1, 3, 5, MAX):
            self.reject(self.changed(0, 'cleanup_calls', value))

    def test_d065_masks_must_be_four_bit_disjoint_complementary(self):
        for field in ('low_mask', 'timeout_mask'):
            for value in (16, 17, MAX):
                self.reject(self.changed(0, field, value))
        for value in (0, 1, 7, 14):
            self.reject(self.changed(100, 'timeout_mask', value))
        self.reject(self.changed(0, 'timeout_mask', 15))

    def test_d065_first_low_sentinel_and_mask_must_agree_per_pin(self):
        for bit in range(4):
            self.reject(self.changed(0, f'first_low_{bit}', MAX))
            for value in (0, 1499, 1500):
                self.reject(self.changed(100, f'first_low_{bit}', value))

    def test_d065_low_timestamp_must_not_exceed_observation_timestamp(self):
        for bit in range(4):
            for value in (8, HALF - 1, HALF, MAX - 1):
                with self.subTest(bit=bit, value=value):
                    self.reject(self.changed(0, f'first_low_{bit}', value))

    def test_d065_zero_and_equal_observation_first_low_timestamps_are_valid(self):
        rows = normal_samples()
        rows[0] = sample(observe=0)
        result = self.analyze(record(rows))
        self.assertEqual([0] * 4, result['neutral']['first_sample']['first_low_us'])
        self.analyze(record())

    def test_d065_all_low_requires_all_bits_and_strictly_before_deadline(self):
        for elapsed in (1500, 1501):
            rows = normal_samples()
            rows[0] = sample(observe=elapsed)
            rows[0][1] = 1
            self.reject(record(rows))
        rows = normal_samples()
        rows[0] = sample(observe=4, low=7)
        self.reject(record(rows))

    def test_d065_deadline_requires_real_elapsed_at_least_1500(self):
        rows = normal_samples()
        rows[0] = sample(observe=1499, low=0)
        rows[0][1], rows[0][12] = 2, 15
        self.reject(record(rows))

    def test_d065_pullup_any_early_or_late_low_is_explicit_stimulus_failure(self):
        for index in (100, 150, 199):
            for elapsed, mask in ((0, 15), (1499, 15), (1500, 1), (1501, 15)):
                with self.subTest(index=index, elapsed=elapsed, mask=mask):
                    rows = normal_samples()
                    rows[index] = sample(1, observe=elapsed, low=mask)
                    self.reject(record(rows), 'pull-up stimulus')

    def test_d065_sample_total_equals_all_five_acquisition_intervals(self):
        for delta in (-1, 1, 10000):
            rows = normal_samples()
            rows[0][8] += delta
            self.reject(record(rows))
        for field in ('drive_us', 'charge_us', 'release_us', 'observe_us', 'cleanup_us'):
            rows = normal_samples()
            rows[0][FIELDS.index(field)] += 1
            self.reject(record(rows))

    def test_d065_record_total_covers_sample_totals_plus_overheads_without_subtraction(self):
        rows = normal_samples()
        required = sum(row[2] + row[8] for row in rows)
        self.reject(record(rows, end=required - 1))
        for total in (required, required + 1, required + 9000):
            self.assertEqual(total, self.analyze(record(rows, end=total))['total_elapsed_us'])

    def test_d065_record_total_half_range_and_larger_rejected(self):
        for total in (HALF, HALF + 1, MAX):
            self.reject(record(end=total))

    def test_d065_python_sum_cannot_silently_wrap_uint32(self):
        rows = normal_samples()
        for index in (0, 1, 2):
            rows[index] = sample(drive=HALF - 1000)
        self.reject(record(rows))

    def test_d065_large_valid_intervals_and_maximum_unambiguous_record_total_accepted(self):
        for field in ('overhead_us', 'drive_us', 'charge_us', 'release_us', 'cleanup_us'):
            with self.subTest(field=field):
                rows = normal_samples()
                required = sum(row[2] + row[8] for row in rows)
                increment = HALF - 1 - required
                rows[0][FIELDS.index(field)] += increment
                if field != 'overhead_us':
                    rows[0][8] += increment
                result = self.analyze(record(rows, start=MAX - 29))
                self.assertEqual(HALF - 1, result['total_elapsed_us'])

    def test_d065_valid_uint32_record_wrap_does_not_mutate_and_is_repeatable(self):
        expected = self.analyze(record())['total_elapsed_us']
        for start in (MAX - 7, MAX, MAX - expected):
            data = record(start=start)
            original = bytes(data)
            result = self.analyze(data)
            self.assertEqual(expected, result['total_elapsed_us'])
            self.assertEqual(result, self.analyze(data))
            self.assertEqual(original, data)


if __name__ == '__main__':
    unittest.main()
