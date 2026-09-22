# Checks the D-066 never-called compatibility probe using inert API substitutes.
# Detects accidental setup/loop execution and prevents an upload capability claim.
# Coordinator authored expectations from the contract before reading implementation.
from contextlib import redirect_stderr
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
ARDUINO = '''#pragma once
#include <cstdint>
using std::uint8_t;
struct TwoWire {};
inline TwoWire Wire1;
'''
MPU = '''#pragma once
#include <Arduino.h>
enum mpu6050_gyro_range_t { MPU6050_RANGE_1000_DEG };
enum mpu6050_bandwidth_t { MPU6050_BAND_184_HZ };
struct sensors_event_t { float value; };
inline unsigned probe_calls = 0;
struct Adafruit_MPU6050 {
    Adafruit_MPU6050() { ++probe_calls; }
    ~Adafruit_MPU6050() { ++probe_calls; }
    bool begin(uint8_t, TwoWire*) { ++probe_calls; return true; }
    void setGyroRange(mpu6050_gyro_range_t) { ++probe_calls; }
    void setSampleRateDivisor(uint8_t) { ++probe_calls; }
    void setFilterBandwidth(mpu6050_bandwidth_t) { ++probe_calls; }
    bool getEvent(sensors_event_t*, sensors_event_t*, sensors_event_t*) {
        ++probe_calls; return true;
    }
};
'''
HARNESS = '''#include "src/imu_probe.h"
#include <cassert>
#include <cstdlib>
#include <new>
static unsigned allocations = 0;
void* operator new(std::size_t n) {
    ++allocations;
    void* result = std::malloc(n);
    if (!result) std::abort();
    return result;
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }
void setup();
void loop();
int main() {
    assert(p0ImuProbe == nullptr && p0ImuBus == nullptr);
    assert(probe_calls == 0);
    const auto before = allocations;
    setup();
    assert(p0ImuProbe == &p0::probeMpu && p0ImuBus == &Wire1);
    assert(probe_calls == 0 && allocations == before);
    for (unsigned i = 0; i < 10000; ++i) loop();
    assert(p0ImuProbe == &p0::probeMpu && p0ImuBus == &Wire1);
    assert(probe_calls == 0 && allocations == before);
}
'''


class ImuCompileProbeTests(unittest.TestCase):
    def build(self, motors):
        temporary = tempfile.TemporaryDirectory(prefix='sumo-imu-probe-')
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        sketch = folder / 'probe'
        shutil.copytree(ROOT / 'bench/p0_imu_compile', sketch)
        shutil.copy2(ROOT / 'src/config.h', sketch / 'src/config.h')
        (sketch / 'Arduino.h').write_text(ARDUINO)
        (sketch / 'Wire.h').write_text('#pragma once\n#include <Arduino.h>\n')
        (sketch / 'Adafruit_MPU6050.h').write_text(MPU)
        (sketch / 'harness.cpp').write_text(HARNESS)
        sources = [sketch / 'p0_imu_compile.ino', *sorted((sketch / 'src').rglob('*.cpp')),
                   sketch / 'harness.cpp']
        command = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                   '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                   '-fno-sanitize-recover=all', f'-DMOTORS_ALLOWED={motors}',
                   '-I', str(sketch), '-I', str(sketch / 'src'), '-x', 'c++',
                   *map(str, sources), '-o', str(folder / 'probe-test')]
        return folder, subprocess.run(command, text=True, capture_output=True, timeout=30)

    def test_d066_setup_and_loop_retain_addresses_without_api_or_allocation(self):
        folder, result = self.build(0)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        run = subprocess.run([str(folder / 'probe-test')], text=True,
                             capture_output=True, timeout=5)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)

    def test_d066_motor_capable_probe_build_is_rejected(self):
        _, result = self.build(1)
        self.assertNotEqual(0, result.returncode)
        self.assertIn('static assertion', result.stderr)

    def test_d066_probe_upload_rejected_before_any_board_lookup(self):
        spec = importlib.util.spec_from_file_location('imu_probe_board_tool', ROOT / 'tools/board_tool.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        args = type('Args', (), dict(sketch='bench/p0_imu_compile', match=False,
                                    compile_only=False, startup=None))()
        with mock.patch.object(module, 'target', side_effect=AssertionError('Board lookup forbidden')):
            with redirect_stderr(io.StringIO()), self.assertRaisesRegex(ValueError, 'P0 uploads allow only reviewed inert'):
                module.flash(args)


if __name__ == '__main__':
    unittest.main()
