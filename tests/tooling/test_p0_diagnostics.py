# Executes the real P0 diagnostic loops with synthetic clocks and matrix output.
# Tests boundary, delayed-call and wrap behavior without involving any board.
# Run under WSL with Python unittest and g++; no target timing is measured here.
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[2]
ARDUINO_STUB = '''#pragma once
#include <cstdint>
inline std::uint32_t fakeNow = 0;
inline std::uint32_t micros() { return fakeNow; }
inline std::uint32_t millis() { return fakeNow; }
'''
MATRIX_STUB = '''#pragma once
#include "Arduino.h"
#include <array>
#include <algorithm>
struct Arduino_LED_Matrix {
    unsigned draws = 0;
    unsigned begins = 0;
    int bits = 0;
    std::array<std::uint8_t, 104> shown{};
    void begin() { ++begins; }
    void setGrayscaleBits(int value) { bits = value; }
    void draw(const std::uint8_t* pixels) {
        std::copy_n(pixels, shown.size(), shown.begin());
        ++draws;
    }
};
'''
TIMING_HARNESS = '''#include <cassert>
#include <string>
#include "Arduino.h"
#include "bench/p0_timing/p0_timing.ino"

void thresholdAndWrap() {
    const std::uint32_t start = 0xfffffe0cU;
    fakeNow = start;
    setup();
    fakeNow = start + 999U;
    loop();
    assert(p0Samples == 0);
    fakeNow = start + 1000U;
    loop();
    assert(p0Samples == 1 && p0Histogram[0] == 1);
    loop();
    assert(p0Samples == 1);
    fakeNow = start + 2017U;
    loop();
    assert(p0Samples == 2 && p0Histogram[17] == 1);
    assert(p0MaxLateUs == 17 && p0OverPeriod == 0);
}

void lateAndOverflow() {
    setup();
    fakeNow = 1999;
    loop();
    assert(p0Histogram[999] == 1 && p0OverPeriod == 0);
    fakeNow = 3000;
    loop();
    assert(p0Histogram[1000] == 1 && p0OverPeriod == 1);
    fakeNow = 6500;
    loop();
    assert(p0Samples == 3 && p0Histogram[1000] == 2);
    assert(p0MaxLateUs == 2500 && p0OverPeriod == 2);
    loop();
    assert(p0Samples == 3);
    fakeNow = 7499;
    loop();
    assert(p0Samples == 3);
    fakeNow = 7500;
    loop();
    assert(p0Samples == 4 && p0Histogram[0] == 1);
}

void finishAndFreeze() {
    setup();
    for (unsigned tick = 1; tick <= 60000; ++tick) {
        fakeNow = tick * 1000U;
        loop();
    }
    assert(p0Samples == 60000 && p0Histogram[0] == 60000);
    assert(p0MaxLateUs == 0 && p0OverPeriod == 0);
    fakeNow = 0xffffffffU;
    loop();
    assert(p0Samples == 60000 && p0Histogram[0] == 60000);
    unsigned total = 0;
    for (unsigned bin = 0; bin <= config::P0_JITTER_HISTOGRAM_US; ++bin) {
        total += p0Histogram[bin];
    }
    assert(total == p0Samples && p0MaxLateUs == 0 && p0OverPeriod == 0);
}

int main(int argc, char** argv) {
    assert(argc == 2);
    const std::string scenario = argv[1];
    if (scenario == "wrap") thresholdAndWrap();
    else if (scenario == "late") lateAndOverflow();
    else if (scenario == "finish") finishAndFreeze();
    else return 2;
}
'''
MATRIX_HARNESS = '''#include <cassert>
#include <string>
#include "Arduino.h"
#include "bench/p0_matrix/src/counter_uart.h"

// Scheduling fixture only; separate opaque adapter tests verify real transport.
namespace transportStub {
unsigned begins = 0;
unsigned services = 0;
unsigned submissions = 0;
std::uint32_t lastCounter = 0;
std::uint32_t lastSubmitUs = 0;
}
namespace p0 {
bool beginCounterTransport() {
    ++transportStub::begins;
    return true;
}
void serviceCounter(std::uint32_t now_us) {
    assert(transportStub::begins == 1);
    assert(now_us == fakeNow);
    ++transportStub::services;
}
bool submitCounter(std::uint32_t counter, std::uint32_t now_us) {
    assert(transportStub::begins == 1);
    assert(now_us == fakeNow);
    ++transportStub::submissions;
    transportStub::lastCounter = counter;
    transportStub::lastSubmitUs = now_us;
    return true;
}
}
#include "bench/p0_matrix/p0_matrix.ino"

void counterWrap() {
    const std::uint32_t start = 0xfffffe0cU;
    fakeNow = start;
    setup();
    assert(transportStub::begins == 1 && transportStub::submissions == 0);
    fakeNow = start + 999U;
    loop();
    assert(p0Seconds == 0);
    assert(transportStub::submissions == 0 && transportStub::services == 1);
    fakeNow = start + 1000U;
    loop();
    assert(p0Seconds == 1);
    assert(transportStub::submissions == 1 && transportStub::lastCounter == 1);
    assert(transportStub::lastSubmitUs == start + 1000U);
    fakeNow = start + 2000U;
    loop();
    assert(p0Seconds == 2);
    assert(transportStub::submissions == 2 && transportStub::lastCounter == 2);
    assert(transportStub::lastSubmitUs == start + 2000U);
    assert(transportStub::services == 3);
}

void delayedCounter() {
    setup();
    fakeNow = 1500;
    loop();
    assert(p0Seconds == 1);
    assert(transportStub::submissions == 1 && transportStub::lastCounter == 1);
    fakeNow = 2100;
    loop();
    assert(p0Seconds == 2);
    assert(transportStub::submissions == 2 && transportStub::lastCounter == 2);
    fakeNow = 5500;
    loop();
    assert(p0Seconds == 5);
    assert(transportStub::submissions == 3 && transportStub::lastCounter == 5);
    loop();
    assert(p0Seconds == 5);
    assert(transportStub::submissions == 3);
    fakeNow = 6000;
    loop();
    assert(p0Seconds == 6);
    assert(transportStub::submissions == 4 && transportStub::lastCounter == 6);
    assert(transportStub::lastSubmitUs == 6000 && transportStub::services == 5);
}

void visibleAndBounded() {
    setup();
    assert(matrix.begins == 1 && matrix.bits == 3);
    fakeNow = 99;
    loop();
    assert(matrix.draws == 0);
    const char* expectedS[5] = {"111", "100", "111", "001", "111"};
    for (unsigned update = 1; update <= 31; ++update) {
        fakeNow = update * 100;
        loop();
        assert(matrix.draws == update);
        loop();
        assert(matrix.draws == update);
        for (unsigned row = 0; row < 8; ++row) {
            for (unsigned col = 0; col < 13; ++col) {
                const auto pixel = matrix.shown[row * 13 + col];
                assert(pixel <= 1);
                if (row == 0 || row >= 6) assert(pixel == 0);
                if (update == 14 && row >= 1 && row <= 5 && col < 3) {
                    assert(pixel == expectedS[row - 1][col] - '0');
                }
            }
        }
    }
    fakeNow = 100000;
    loop();
    assert(matrix.draws == 32);
}

int main(int argc, char** argv) {
    assert(argc == 2);
    const std::string scenario = argv[1];
    if (scenario == "wrap") counterWrap();
    else if (scenario == "delay") delayedCounter();
    else if (scenario == "frame") visibleAndBounded();
    else return 2;
}
'''


class P0DiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('g++')
        if compiler is None:
            raise RuntimeError('g++ is required; run these host tests under WSL')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-p0-diagnostics-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        (cls.root / 'Arduino.h').write_text(ARDUINO_STUB)
        (cls.root / 'Arduino_LED_Matrix.h').write_text(MATRIX_STUB)
        for name, source in (('timing', TIMING_HARNESS), ('matrix', MATRIX_HARNESS)):
            harness = cls.root / f'{name}.cpp'
            harness.write_text(source)
            result = subprocess.run(
                [compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
                 '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                 '-fno-sanitize-recover=all', '-I', str(cls.root), '-I', str(PROJECT),
                 str(harness), '-o', str(cls.root / name)],
                capture_output=True, text=True, check=False, timeout=30)
            if result.returncode != 0:
                raise AssertionError(result.stdout + result.stderr)

    def run_scenario(self, sketch, scenario):
        result = subprocess.run([str(self.root / sketch), scenario],
                                capture_output=True, text=True, check=False, timeout=5)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_timing_deadline_boundary_and_uint32_wrap(self):
        self.run_scenario('timing', 'wrap')

    def test_timing_late_bins_and_missed_period_restart(self):
        self.run_scenario('timing', 'late')

    def test_timing_60000_samples_then_results_stop_changing(self):
        self.run_scenario('timing', 'finish')

    def test_matrix_counter_uint32_wrap(self):
        self.run_scenario('matrix', 'wrap')

    def test_matrix_counter_preserves_elapsed_seconds_after_delayed_calls(self):
        self.run_scenario('matrix', 'delay')

    def test_matrix_has_valid_glyph_pixels_and_at_most_one_draw_per_call(self):
        self.run_scenario('matrix', 'frame')


if __name__ == '__main__':
    unittest.main()
