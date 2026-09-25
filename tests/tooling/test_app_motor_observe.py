#!/usr/bin/env python3
"""Tests D192 real application observation and sketch binding in owned RAM.
Compiles one host process at a time, executes through memfd, and retains no build.
Run: python3 -B tests/tooling/test_app_motor_observe.py.
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def checked(command, **kwargs):
    result = subprocess.run(command, text=True, capture_output=True, **kwargs)
    if result.returncode:
        raise AssertionError(f"exit={result.returncode}: {' '.join(map(str, command))}\n"
                             f"{result.stdout}{result.stderr}")
    return result


ENTRY_TYPES = r'''
#pragma once
#ifdef EMPTY
#error EMPTY must be protected around native headers
#endif
#include "config.h"
namespace fixture {
inline unsigned constructors = 0U, begins = 0U, polls = 0U;
inline bool correct_ports = false, granted = false, running = false;
}
namespace motors {
struct Port { unsigned identity; };
struct UnoQPort { Port port() { return {11U}; } };
}
namespace power { struct InputPort { unsigned identity; }; }
namespace recorder::dump {
enum class Buffering { LEGACY_SINGLE, FIFO8 };
struct UnoQDumpPort {
    explicit UnoQDumpPort(Buffering b) : buffering(b) {}
    Buffering buffering;
};
}
namespace app {
struct SourcePort { unsigned identity; };
struct DumpPort { unsigned identity; };
struct NativeSources {
    power::InputPort adcPort() { return {22U}; }
    SourcePort port() { return {33U}; }
};
inline DumpPort unoQDumpPort(recorder::dump::UnoQDumpPort& p) {
    return {p.buffering == recorder::dump::Buffering::FIFO8 ? 44U : 0U};
}
}
namespace motor_fault { struct Grants { bool exclusive_motor_outputs = false; }; }
namespace app_motor_observe {
struct Runner {
    Runner(motors::Port m, power::InputPort a, app::SourcePort s, app::DumpPort d) {
        ++fixture::constructors;
        fixture::correct_ports = m.identity == 11U && a.identity == 22U &&
            s.identity == 33U && d.identity == 44U;
    }
    bool begin(motor_fault::Grants g) {
        ++fixture::begins; fixture::granted = g.exclusive_motor_outputs;
        fixture::running = fixture::granted; return true;
    }
    bool active() const { return fixture::running; }
    void poll() { ++fixture::polls; }
};
}
'''

ENTRY_MAIN = r'''
#define EMPTY 731
#include "probe.ino"
static_assert(EMPTY == 731, "EMPTY macro must be restored");
int main() {
    if (fixture::constructors != 1U || !fixture::correct_ports || fixture::begins != 0U)
        return 1;
    setup();
    if (fixture::begins != 1U || fixture::granted != (EXPECTED_GRANT != 0)) return 2;
    loop(); loop();
    if (fixture::polls != (EXPECTED_GRANT ? 2U : 0U)) return 3;
    fixture::running = false; const auto old = fixture::polls;
    loop(); loop();
    if (fixture::polls != old) return 4;
    return 0;
}
'''


class AppMotorObserveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform != 'linux' or not hasattr(os, 'memfd_create'):
            raise unittest.SkipTest('Linux RAM scratch and memfd required')
        cls.compiler = shutil.which('g++')
        if cls.compiler is None:
            raise unittest.SkipTest('g++ required')
        if shutil.disk_usage('/dev/shm').free < 64 * 1024 * 1024:
            raise RuntimeError('at least 64 MiB RAM scratch required')
        cls.scratch = tempfile.TemporaryDirectory(prefix='sumox-d192-', dir='/dev/shm')
        cls.directory = Path(cls.scratch.name)
        cls.environment = dict(os.environ, TMPDIR=str(cls.directory))
        cls.flags = [cls.compiler, '-std=c++17', '-O1', '-g1', '-Wall', '-Wextra',
                     '-Werror', '-fno-exceptions', '-fno-rtti',
                     '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                     '-DMATCH=0', '-DMOTORS_ALLOWED=0',
                     '-ffunction-sections', '-fdata-sections',
                     '-I' + str(ROOT / 'src'), '-I' + str(ROOT / 'host/third_party'),
                     '-I' + str(ROOT / 'bench/motor_fault/src'),
                     '-I' + str(ROOT / 'bench/app_motor_observe/src')]

    @classmethod
    def tearDownClass(cls):
        cls.scratch.cleanup()

    def execute(self, binary, sanitizer=False):
        fd = os.memfd_create('sumox-d192-host', flags=0)
        try:
            with os.fdopen(os.dup(fd), 'wb') as target:
                target.write(binary.read_bytes())
            env = dict(self.environment, ASAN_OPTIONS='detect_leaks=1:halt_on_error=1',
                       UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
            result = checked([f'/proc/self/fd/{fd}'], pass_fds=(fd,), env=env)
            if result.stdout:
                print(('SANITIZED ' if sanitizer else 'NORMAL ') + result.stdout.strip())
        finally:
            os.close(fd)
            binary.unlink(missing_ok=True)

    def build_runtime(self, sanitizer, boundary=False):
        # Names come from host/CMakeLists.txt, without reading implementation bodies.
        hal = ('recorder_frames', 'recorder', 'recorder_csv', 'recorder_dump', 'motors',
               'imu', 'imu_acquisition', 'imu_acquisition_async', 'imu_heading',
               'imu_adapter', 'line_qtr_adapter', 'ui', 'power_inputs', 'ui_display',
               'qtr_cal', 'qtr_cal_format')
        root = self.copied_tree('boundary-' + str(sanitizer), 12, 12) if boundary else ROOT
        sources = [ROOT / 'tests/tooling/app_motor_observe_cases.cc',
                   root / 'bench/app_motor_observe/src/app_motor_observe.cpp',
                   root / 'bench/motor_fault/src/motor_fault.cpp',
                   *sorted((root / 'src/core').glob('*.cpp')),
                   *sorted((root / 'src/app').glob('*.cpp')),
                   *(root / 'src/hal' / (name + '.cpp') for name in hal)]
        options = ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie'] if sanitizer else []
        flags = self.flags
        if boundary:
            flags = [flag.replace(str(ROOT), str(root)) if flag.startswith('-I') else flag
                     for flag in self.flags]
            # The third-party test header is unchanged and need not be duplicated.
            flags += ['-I' + str(ROOT / 'host/third_party'), '-DOBSERVE_BOUNDARY_FIXTURE=1']
        binary = self.directory / ('sanitized' if sanitizer else 'normal')
        checked([*flags, *options, *map(str, sources), '-Wl,--gc-sections',
                 '-o', str(binary)], env=self.environment)
        self.execute(binary, sanitizer)

    def copied_tree(self, name, epochs, polls):
        root = self.directory / name
        # Copy opaquely so quoted relative includes all resolve to the owned config.
        shutil.copytree(ROOT / 'src', root / 'src')
        for bench in ('motor_fault', 'app_motor_observe'):
            shutil.copytree(ROOT / 'bench' / bench, root / 'bench' / bench)
        path = root / 'src/config.h'
        source = path.read_text(encoding='utf-8')
        for bound, value in (('APP_MOTOR_OBSERVE_EPOCHS', epochs),
                             ('APP_MOTOR_OBSERVE_MAX_POLLS', polls)):
            source, count = re.subn(r'(\b' + bound + r'\s*=\s*)[0-9]+U\b',
                                   lambda match: match.group(1) + str(value) + 'U', source)
            self.assertEqual(count, 1, 'Exactly one explicit config bound: ' + bound)
        path.write_text(source, encoding='utf-8')
        return root

    def test_01_normal_real_runtime_contract(self):
        self.build_runtime(False)

    def test_02_sanitized_real_runtime_contract(self):
        self.build_runtime(True)

    def test_03_unsafe_flags_refused_by_public_header(self):
        flags = [f for f in self.flags if not f.startswith(('-DMATCH=', '-DMOTORS_ALLOWED='))]
        for match, motors in ((0, 1), (1, 0), (1, 1)):
            with self.subTest(match=match, motors=motors):
                result = subprocess.run([*flags, f'-DMATCH={match}', f'-DMOTORS_ALLOWED={motors}',
                                         '-x', 'c++', '-fsyntax-only', '-'],
                                        input='#include "app_motor_observe.h"\n',
                                        text=True, capture_output=True, env=self.environment)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Motor fault diagnostic requires inert flags', result.stderr)

    def test_04_default_and_explicit_sketch_binding(self):
        root = self.directory / 'entry'
        root.mkdir()
        (root / 'fixture.h').write_text(ENTRY_TYPES, encoding='utf-8')
        shutil.copyfile(ROOT / 'src/config.h', root / 'config.h')
        shutil.copyfile(ROOT / 'bench/app_motor_observe/app_motor_observe.ino', root / 'probe.ino')
        (root / 'entry.cc').write_text(ENTRY_MAIN, encoding='utf-8')
        for name in ('src/app/native_sources_unoq.h', 'src/hal/motor_port_unoq.h',
                     'src/app_motor_observe.h'):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('#include "fixture.h"\n', encoding='utf-8')
        for macro, grant in ((None, 0), ('0', 0), ('1', 1)):
            with self.subTest(macro=macro):
                flags = [] if macro is None else ['-DSUMOX_MOTOR_FAULT_PROBE=' + macro]
                binary = self.directory / 'entry-binary'
                checked([self.compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
                         '-DMATCH=0', '-DMOTORS_ALLOWED=0', f'-DEXPECTED_GRANT={grant}',
                         *flags, '-I' + str(root), str(root / 'entry.cc'), '-o', str(binary)],
                        env=self.environment)
                self.execute(binary)

    def test_05_invalid_probe_macro_is_rejected(self):
        for value in ('2', '-1'):
            with self.subTest(value=value):
                result = subprocess.run([*self.flags, '-DSUMOX_MOTOR_FAULT_PROBE=' + value,
                                         '-x', 'c++', '-fsyntax-only', '-'],
                                        input='#include "app_motor_observe.h"\n',
                                        text=True, capture_output=True, env=self.environment)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('SUMOX_MOTOR_FAULT_PROBE must be 0 or 1', result.stderr)

    def test_06_small_copied_bounds_normal(self):
        self.build_runtime(False, boundary=True)

    def test_07_small_copied_bounds_sanitized(self):
        self.build_runtime(True, boundary=True)

    def test_08_invalid_bounds_refused_by_public_header(self):
        invalid = ((0, 12), (12, 0), (10000001, 10000001),
                   (12, 10000001), (13, 12))
        for index, (epochs, polls) in enumerate(invalid):
            with self.subTest(epochs=epochs, polls=polls):
                root = self.copied_tree('invalid-' + str(index), epochs, polls)
                flags = [flag.replace(str(ROOT), str(root)) if flag.startswith('-I') else flag
                         for flag in self.flags]
                result = subprocess.run([*flags, '-x', 'c++', '-fsyntax-only', '-'],
                    input='#include "app_motor_observe.h"\n', text=True,
                    capture_output=True, env=self.environment)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('static assertion failed', result.stderr)
                self.assertNotIn('No such file or directory', result.stderr)

    def test_09_probe_is_exclusive_of_other_profiles(self):
        for macro in ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
                      'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
                      'SUMOX_P5_ABORT_TIMING'):
            with self.subTest(macro=macro):
                result = subprocess.run([*self.flags, '-DSUMOX_MOTOR_FAULT_PROBE=1',
                    '-D' + macro + '=1', '-x', 'c++', '-fsyntax-only', '-'],
                    input='#include "app_motor_observe.h"\n', text=True,
                    capture_output=True, env=self.environment)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Motor fault probe is exclusive and requires inert flags', result.stderr)

    def test_10_positive_bound_endpoints_compile(self):
        for index, bound in enumerate((1, 10000000)):
            with self.subTest(bound=bound):
                root = self.copied_tree('valid-' + str(index), bound, bound)
                flags = [flag.replace(str(ROOT), str(root)) if flag.startswith('-I') else flag
                         for flag in self.flags]
                result = subprocess.run([*flags, '-x', 'c++', '-fsyntax-only', '-'],
                    input='#include "app_motor_observe.h"\n', text=True,
                    capture_output=True, env=self.environment)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
