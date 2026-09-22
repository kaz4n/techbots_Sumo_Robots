# Checks D-067 from its frozen contract and public header, without reading probe code.
# Proves inert host startup and upload refusal without executing any probe function.
# Uses counted API/allocator substitutes, strict C++17, and undefined-behavior checks.
from contextlib import ExitStack
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
ARDUINO = '''#pragma once
#include <cstdint>
using pin_size_t = std::uint8_t;
enum PinStatus { LOW, HIGH, CHANGE, FALLING, RISING };
inline unsigned api_calls = 0;
inline void analogWriteResolution(int) { ++api_calls; }
inline int analogWriteResolution() { ++api_calls; return 8; }
inline void analogWrite(pin_size_t, int) { ++api_calls; }
inline int digitalPinToInterrupt(pin_size_t) { ++api_calls; return 0; }
inline void attachInterrupt(pin_size_t, void (*)(), PinStatus) { ++api_calls; }
inline void detachInterrupt(pin_size_t) { ++api_calls; }
'''
PINCTRL = '''#pragma once
#include <Arduino.h>
#include <cstddef>
#include <cerrno>
struct device {};
namespace zephyr::arduino {
inline int init_dev_apply_channel_pinctrl(const device*, std::size_t) {
    ++api_calls;
    return 0;
}
}
'''
PWM = '''#pragma once
#include <zephyrPinctrl.h>
struct pwm_dt_spec {
    const device* dev;
    std::uint32_t channel;
    std::uint32_t period;
    std::uint16_t flags;
};
inline bool pwm_is_ready_dt(const pwm_dt_spec*) { ++api_calls; return true; }
inline int pwm_get_cycles_per_sec(const device*, std::uint32_t, std::uint64_t*) {
    ++api_calls;
    return 0;
}
inline int pwm_set_dt(const pwm_dt_spec*, std::uint32_t, std::uint32_t) {
    ++api_calls;
    return 0;
}
'''
HARNESS = '''#include "src/api_probe.h"
#include <cassert>
#include <cstdlib>
#include <new>
#include <type_traits>
static unsigned allocations = 0;
extern "C" void* __real_malloc(std::size_t);
extern "C" void* __real_calloc(std::size_t, std::size_t);
extern "C" void* __real_realloc(void*, std::size_t);
extern "C" void* __real_aligned_alloc(std::size_t, std::size_t);
extern "C" void* __wrap_malloc(std::size_t n) {
    ++allocations;
    return __real_malloc(n);
}
extern "C" void* __wrap_calloc(std::size_t n, std::size_t size) {
    ++allocations;
    return __real_calloc(n, size);
}
extern "C" void* __wrap_realloc(void* p, std::size_t n) {
    ++allocations;
    return __real_realloc(p, n);
}
extern "C" void* __wrap_aligned_alloc(std::size_t alignment, std::size_t n) {
    ++allocations;
    return __real_aligned_alloc(alignment, n);
}
void* operator new(std::size_t n) {
    ++allocations;
    void* result = __real_malloc(n ? n : 1);
    if (!result) std::abort();
    return result;
}
void* operator new[](std::size_t n) { return ::operator new(n); }
void* operator new(std::size_t n, const std::nothrow_t&) noexcept {
    return ::operator new(n);
}
void* operator new[](std::size_t n, const std::nothrow_t&) noexcept {
    return ::operator new(n);
}
void* operator new(std::size_t n, std::align_val_t alignment) {
    ++allocations;
    const auto align = static_cast<std::size_t>(alignment);
    const auto rounded = ((n ? n : 1) + align - 1) / align * align;
    void* result = __real_aligned_alloc(align, rounded);
    if (!result) std::abort();
    return result;
}
void* operator new[](std::size_t n, std::align_val_t alignment) {
    return ::operator new(n, alignment);
}
void* operator new(std::size_t n, std::align_val_t a, const std::nothrow_t&) noexcept {
    return ::operator new(n, a);
}
void* operator new[](std::size_t n, std::align_val_t a, const std::nothrow_t&) noexcept {
    return ::operator new(n, a);
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
void operator delete[](void* p, std::size_t) noexcept { std::free(p); }
void operator delete(void* p, std::align_val_t) noexcept { std::free(p); }
void operator delete[](void* p, std::align_val_t) noexcept { std::free(p); }
void operator delete(void* p, std::size_t, std::align_val_t) noexcept { std::free(p); }
void operator delete[](void* p, std::size_t, std::align_val_t) noexcept { std::free(p); }
static_assert(std::is_same_v<p0::PwmProbe,
    int (*)(const pwm_dt_spec*, size_t, uint32_t, uint32_t, uint64_t*)>);
static_assert(std::is_same_v<p0::AnalogProbe, int (*)(pin_size_t, int, int)>);
static_assert(std::is_same_v<p0::InterruptProbe,
    int (*)(pin_size_t, void (*)(), PinStatus)>);
static_assert(std::is_same_v<decltype(p0PwmProbe), p0::PwmProbe volatile>);
static_assert(std::is_same_v<decltype(p0AnalogProbe), p0::AnalogProbe volatile>);
static_assert(std::is_same_v<decltype(p0InterruptProbe), p0::InterruptProbe volatile>);
void setup();
void loop();
static void assertInertAnchors() {
    assert(p0PwmProbe == &p0::probePwm);
    assert(p0AnalogProbe == &p0::probeAnalog);
    assert(p0InterruptProbe == &p0::probeInterrupt);
    assert(api_calls == 0);
    assert(allocations == 0);
}
int main() {
    assert(p0PwmProbe == nullptr);
    assert(p0AnalogProbe == nullptr);
    assert(p0InterruptProbe == nullptr);
    assert(api_calls == 0);
    assert(allocations == 0);
    setup();
    assertInertAnchors();
    for (unsigned i = 0; i < 10000; ++i) {
        loop();
        assertInertAnchors();
    }
}
'''


class PwmIrqCompileProbeTests(unittest.TestCase):
    def build(self, motors):
        temporary = tempfile.TemporaryDirectory(prefix='sumo-pwm-irq-probe-')
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        sketch = folder / 'probe'
        shutil.copytree(ROOT / 'bench/p0_pwm_irq_compile', sketch)
        shutil.copy2(ROOT / 'src/config.h', sketch / 'src/config.h')
        (sketch / 'Arduino.h').write_text(ARDUINO)
        (sketch / 'zephyrPinctrl.h').write_text(PINCTRL)
        (sketch / 'zephyr/drivers').mkdir(parents=True)
        (sketch / 'zephyr/drivers/pwm.h').write_text(PWM)
        (sketch / 'harness.cpp').write_text(HARNESS)
        sources = [sketch / 'p0_pwm_irq_compile.ino',
                   *sorted((sketch / 'src').rglob('*.cpp')), sketch / 'harness.cpp']
        command = ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                   '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                   '-fno-sanitize-recover=all', '-DMATCH=0',
                   f'-DMOTORS_ALLOWED={motors}', '-I', str(sketch),
                   '-I', str(sketch / 'src'), '-x', 'c++', *map(str, sources),
                   '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=aligned_alloc',
                   '-o', str(folder / 'probe-test')]
        return folder, subprocess.run(command, text=True, capture_output=True, timeout=30)

    def test_d067_setup_and_10000_loops_retain_exact_addresses_without_api_or_heap(self):
        folder, result = self.build(0)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        run = subprocess.run([str(folder / 'probe-test')], text=True,
                             capture_output=True, timeout=5)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)

    def test_d067_motor_enabled_probe_build_is_rejected(self):
        _, result = self.build(1)
        self.assertNotEqual(0, result.returncode)
        self.assertIn('static assertion', result.stderr)

    def assertUploadRefused(self, match, startup, expected):
        spec = importlib.util.spec_from_file_location(
            'pwm_irq_probe_board_tool', ROOT / 'tools/board_tool.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        args = type('Args', (), dict(sketch='bench/p0_pwm_irq_compile',
                                    match=match, compile_only=False, startup=startup))()
        with ExitStack() as stack:
            forbidden = [stack.enter_context(mock.patch.object(
                module, name, side_effect=AssertionError(f'{name} forbidden')))
                for name in ('target', 'setting', 'require_transport', 'stage',
                             'remote', 'sync_sources', 'verify_core', 'verify_inert_source')]
            forbidden.append(stack.enter_context(mock.patch.object(
                module.subprocess, 'run', side_effect=AssertionError('subprocess forbidden'))))
            with self.assertRaisesRegex(ValueError, expected):
                module.flash(args)
            for blocked in forbidden:
                blocked.assert_not_called()

    def test_d067_upload_unspecified_startup_refused_before_board_lookup(self):
        self.assertUploadRefused(False, None, 'P0 uploads allow only reviewed inert')

    def test_d067_upload_default_startup_refused_before_board_lookup(self):
        self.assertUploadRefused(False, 'default', 'P0 uploads allow only reviewed inert')

    def test_d067_upload_immediate_startup_refused_before_board_lookup(self):
        self.assertUploadRefused(False, 'immediate', 'P0 uploads allow only reviewed inert')

    def test_d067_match_unspecified_startup_refused_before_board_lookup(self):
        self.assertUploadRefused(True, None, 'motor-capable uploads disabled in P0')

    def test_d067_match_default_startup_refused_before_board_lookup(self):
        self.assertUploadRefused(True, 'default', '--match requires Immediate startup')

    def test_d067_match_immediate_startup_refused_before_board_lookup(self):
        self.assertUploadRefused(True, 'immediate', 'motor-capable uploads disabled in P0')


if __name__ == '__main__':
    unittest.main()
