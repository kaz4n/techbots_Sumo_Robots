# Tests D169's inert selector, actual sketch activation, and exact policy admission.
# Derives expectations from the contract/public headers without reading production bodies.
# Run Python -B unittest in Linux; compilers run serially in owned RAM, never on a board.
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SELECTOR = 'SUMOX_MOTOR_FAULT_PROBE'
PROJECT = 'motor_fault.ino'
FQBN = 'arduino:zephyr:unoq'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
ACTIVE_FLAGS = FLAGS + ' -DSUMOX_MOTOR_FAULT_PROBE=1'
PLATFORM = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
BUILD = '/fixture/native-app-v1/source/default/run-one/build'
DATA = '/home/arduino/.arduino15'
PROFILES = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
            'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
            'SUMOX_P5_ABORT_TIMING')

STUB = r'''
#pragma once
#include "config.h"
#include <cstdint>
namespace fixture {
inline unsigned native_constructions = 0, port_calls = 0, constructions = 0;
inline unsigned begins = 0, active_reads = 0, polls = 0, clock_reads = 0;
inline bool grant = false, active = false, correct_port = false;
inline std::uint32_t now = 0U, received = 0U;
inline int port_owner = 0;
}
namespace motors {
struct Port { void* context = nullptr; };
class UnoQPort {
public:
    UnoQPort() { ++fixture::native_constructions; }
    Port port() { ++fixture::port_calls; return Port{&fixture::port_owner}; }
};
}
namespace motor_fault {
struct Grants { bool exclusive_motor_outputs = false; };
class Runner {
public:
    explicit Runner(const motors::Port& port) {
        ++fixture::constructions;
        fixture::correct_port = port.context == &fixture::port_owner;
    }
    bool begin(const Grants& grants) {
        ++fixture::begins;
        fixture::grant = grants.exclusive_motor_outputs;
        return false;
    }
    bool active() const { ++fixture::active_reads; return fixture::active; }
    void poll(std::uint32_t now) { ++fixture::polls; fixture::received = now; }
};
}
'''

HARNESS = r'''
#include <cstdio>
#include "motor_fault.ino"
#define REQUIRE(condition) do { if (!(condition)) { \
    std::fprintf(stderr, "D169 sketch check failed line %d: %s\n", __LINE__, #condition); \
    return 1; } } while (false)
int main() {
    REQUIRE(fixture::native_constructions == 1U);
    REQUIRE(fixture::port_calls == 1U);
    REQUIRE(fixture::constructions == 1U && fixture::correct_port);
    REQUIRE(fixture::begins == 0U && fixture::polls == 0U && fixture::clock_reads == 0U);
    setup();
    REQUIRE(fixture::begins == 1U);
    REQUIRE(fixture::grant == (EXPECTED_GRANT != 0));
    REQUIRE(fixture::polls == 0U && fixture::clock_reads == 0U);
    fixture::active = false;
    loop();
    REQUIRE(fixture::active_reads == 1U);
    REQUIRE(fixture::polls == 0U && fixture::clock_reads == 0U);
    fixture::active = true;
    fixture::now = 0xFEDCBA98U;
    loop();
    REQUIRE(fixture::active_reads == 2U);
    REQUIRE(fixture::polls == 1U && fixture::clock_reads == 1U);
    REQUIRE(fixture::received == 0xFEDCBA98U);
    fixture::now = 17U;
    loop();
    REQUIRE(fixture::active_reads == 3U);
    REQUIRE(fixture::polls == 2U && fixture::clock_reads == 2U);
    REQUIRE(fixture::received == 17U);
    fixture::active = false;
    loop();
    REQUIRE(fixture::active_reads == 4U);
    REQUIRE(fixture::polls == 2U && fixture::clock_reads == 2U);
    REQUIRE(fixture::begins == 1U && fixture::constructions == 1U);
    return 0;
}
'''


class ActivationCompileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform != 'linux' or not hasattr(os, 'memfd_create'):
            raise RuntimeError('D169 requires Linux RAM scratch and memfd; no silent skips')
        cls.compiler = shutil.which('g++')
        if cls.compiler is None or not Path('/dev/shm').is_dir():
            raise RuntimeError('D169 requires g++ and /dev/shm; no silent skips')
        if shutil.disk_usage('/dev/shm').free < 16 * 1024 * 1024:
            raise RuntimeError('D169 requires 16 MiB free RAM scratch')
        cls.base = [cls.compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
                    '-fno-exceptions', '-fno-rtti']

    def syntax(self, definitions, assertions=''):
        source = '#include "config.h"\n' + assertions
        result = subprocess.run([*self.base, '-I' + str(ROOT / 'src'),
            *('-D' + value for value in definitions), '-x', 'c++', '-fsyntax-only', '-'],
            input=source, text=True, capture_output=True, timeout=60)
        return result

    def require_compile(self, definitions, expected):
        result = self.syntax(definitions, f'static_assert({SELECTOR} == {expected});\n')
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def require_refusal(self, definitions):
        result = self.syntax(definitions)
        self.assertNotEqual(0, result.returncode, 'unsafe config compiled: ' + repr(definitions))
        self.assertIn('static assertion failed', result.stderr)

    def test_D169_config_default_and_explicit_zero_are_disabled(self):
        for definitions in ([], [SELECTOR + '=0']):
            with self.subTest(definitions=definitions):
                self.require_compile(definitions, 0)

    def test_D169_config_one_preserves_inert_defaults(self):
        checks = ''.join(f'static_assert({name} == 0);\n'
                         for name in ('MATCH', 'MOTORS_ALLOWED', *PROFILES))
        checks += f'static_assert({SELECTOR} == 1);\n'
        result = self.syntax([SELECTOR + '=1'], checks)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_D169_config_rejects_non_boolean_numbers(self):
        for value in (-2, -1, 2, 3, 255):
            with self.subTest(value=value):
                self.require_refusal([f'{SELECTOR}={value}'])

    def test_D169_config_rejects_each_unsafe_match_motor_tuple(self):
        for match, motors in ((1, 0), (0, 1), (1, 1)):
            flags = [f'MATCH={match}', f'MOTORS_ALLOWED={motors}']
            with self.subTest(match=match, motors=motors):
                self.require_compile([*flags, SELECTOR + '=0'], 0)
                self.require_refusal([*flags, SELECTOR + '=1'])

    def test_D169_config_excludes_each_other_profile(self):
        for profile in PROFILES:
            flags = [profile + '=1']
            if profile == 'SUMOX_TIMING_EVIDENCE':
                flags.append('SUMOX_P4_REACTIVE=1')
            with self.subTest(profile=profile):
                self.require_compile([*flags, SELECTOR + '=0'], 0)
                self.require_refusal([*flags, SELECTOR + '=1'])

    def sketch(self, definitions, expected):
        original = ROOT / 'bench/motor_fault/motor_fault.ino'
        opaque = original.read_bytes()
        before = hashlib.sha256(opaque).hexdigest()
        with tempfile.TemporaryDirectory(prefix='sumox-fault-activation-', dir='/dev/shm') as name:
            directory = Path(name)
            (directory / 'src/hal').mkdir(parents=True)
            (directory / 'motor_fault.ino').write_bytes(opaque)
            (directory / 'src/motor_fault.h').write_text(STUB, encoding='utf-8')
            (directory / 'src/hal/motor_port_unoq.h').write_text(
                '#pragma once\n#include "../motor_fault.h"\n', encoding='utf-8')
            (directory / 'config.h').write_text(
                f'#include "{(ROOT / "src/config.h").as_posix()}"\n', encoding='utf-8')
            (directory / 'Arduino.h').write_text(
                '#pragma once\n#include "src/motor_fault.h"\n'
                'inline unsigned long micros() { ++fixture::clock_reads; return fixture::now; }\n',
                encoding='utf-8')
            source, binary = directory / 'contract.cc', directory / 'contract'
            source.write_text(HARNESS, encoding='utf-8')
            self.assertEqual(opaque, (directory / 'motor_fault.ino').read_bytes())
            result = subprocess.run([*self.base, *('-D' + value for value in definitions),
                f'-DEXPECTED_GRANT={expected}', '-I' + name, str(source), '-o', str(binary)],
                text=True, capture_output=True, timeout=60)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            descriptor = os.memfd_create('sumox-fault-activation', flags=0)
            try:
                with os.fdopen(os.dup(descriptor), 'wb') as stream:
                    stream.write(binary.read_bytes())
                result = subprocess.run([f'/proc/self/fd/{descriptor}'],
                    pass_fds=(descriptor,), text=True, capture_output=True, timeout=10)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            finally:
                os.close(descriptor)
            self.assertEqual(before, hashlib.sha256(original.read_bytes()).hexdigest())
        self.assertFalse(directory.exists(), 'owned RAM fixture must be removed')

    def test_D169_actual_sketch_default_keeps_grant_disabled_and_gates_loop(self):
        self.sketch([], 0)

    def test_D169_actual_sketch_explicit_zero_keeps_grant_disabled_and_gates_loop(self):
        self.sketch([SELECTOR + '=0'], 0)

    def test_D169_actual_sketch_explicit_one_grants_runner_and_gates_loop(self):
        self.sketch([SELECTOR + '=1'], 1)


class ActivationPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'tools'))
        cls.policy = importlib.import_module('app_build_policy')

    def expected(self, flags, fqbn=FQBN, project=PROJECT):
        return self.policy.expected_properties(fqbn, flags, PLATFORM, project=project)

    def document(self, flags):
        raw = (ROOT / 'tests/fixtures/app_build_policy/valid_result.json').read_text(encoding='utf-8')
        return json.loads(raw.replace('app.ino', PROJECT).replace(FLAGS, flags))

    def validate(self, document, flags):
        return self.policy.validate_result(json.dumps(document), FQBN, flags, BUILD, project=PROJECT)

    def preflight(self, document, flags):
        return self.policy.validate_preflight(json.dumps(document), FQBN, flags, BUILD, DATA,
                                              project=PROJECT)

    def test_D169_policy_accepts_exact_default_and_active_flags_with_same_properties(self):
        default = self.expected(FLAGS)
        active = self.expected(ACTIVE_FLAGS)
        for flags, properties in ((FLAGS, default), (ACTIVE_FLAGS, active)):
            with self.subTest(flags=flags):
                self.assertEqual(PROJECT, self.policy.selected_project(PROJECT, FQBN, flags))
                self.assertEqual(PROJECT, properties['build.project_name'])
                self.assertEqual(FQBN, properties['build.fqbn'])
                self.assertEqual('wait', properties['build.boot_mode'])
                self.assertEqual('dynamic', properties['build.link_mode'])
                self.assertEqual(flags, properties['compiler.c.extra_flags'])
                self.assertEqual(flags, properties['compiler.cpp.extra_flags'])
                self.assertEqual(self.validate(self.document(flags), flags),
                                 self.preflight(self.document(flags), flags))
        changed = dict(default)
        changed.update({'compiler.c.extra_flags': ACTIVE_FLAGS,
                        'compiler.cpp.extra_flags': ACTIVE_FLAGS})
        self.assertEqual(changed, active)

    def test_D169_policy_rejects_explicit_zero_reorder_duplicates_extra_and_unsafe_flags(self):
        rejected = (FLAGS + ' -DSUMOX_MOTOR_FAULT_PROBE=0',
            '-DMOTORS_ALLOWED=0 -DMATCH=0 -DSUMOX_MOTOR_FAULT_PROBE=1',
            '-DSUMOX_MOTOR_FAULT_PROBE=1 ' + FLAGS,
            ACTIVE_FLAGS + ' -DSUMOX_MOTOR_FAULT_PROBE=1',
            ACTIVE_FLAGS + ' -DMATCH=0', ACTIVE_FLAGS + ' -DOTHER=1',
            ACTIVE_FLAGS + ' ', ' ' + ACTIVE_FLAGS,
            ACTIVE_FLAGS.replace('=1', '=2'), ACTIVE_FLAGS.replace('=1', '=-1'),
            ACTIVE_FLAGS.replace('-DMATCH=0', '-DMATCH=1'),
            ACTIVE_FLAGS.replace('-DMOTORS_ALLOWED=0', '-DMOTORS_ALLOWED=1'),
            FLAGS.replace('-DMATCH=0', '-DMATCH=1'),
            FLAGS.replace('-DMOTORS_ALLOWED=0', '-DMOTORS_ALLOWED=1'), '')
        for flags in rejected:
            for boundary in ('selected_project', 'expected_properties'):
                with self.subTest(flags=flags, boundary=boundary), self.assertRaises(ValueError):
                    if boundary == 'selected_project':
                        self.policy.selected_project(PROJECT, FQBN, flags)
                    else:
                        self.expected(flags)

    def test_D169_policy_rejects_all_alternate_fqbns_for_both_flags(self):
        for fqbn in (FQBN + ':wait_linux_boot=no', FQBN + ':wait_linux_boot=yes',
                     FQBN + ':link_mode=static', FQBN + ':link_mode=dynamic',
                     'arduino:zephyr:other', FQBN + ' ', ''):
            for flags in (FLAGS, ACTIVE_FLAGS):
                with self.subTest(fqbn=fqbn, flags=flags):
                    with self.assertRaises(ValueError):
                        self.policy.selected_project(PROJECT, fqbn, flags)
                    with self.assertRaises(ValueError):
                        self.expected(flags, fqbn)

    def test_D169_policy_denies_new_selector_to_other_projects(self):
        for project in ('app.ino', 'runtime_inert.ino', 'recorder_inert.ino', 'opp_view.ino',
                        'qtr_raw.ino', 'vbat.ino', 'ui.ino', 'ui_adc_probe.ino',
                        'imu_heading.ino', 'motor_stand.ino'):
            for flags in (ACTIVE_FLAGS, FLAGS + ' -DSUMOX_MOTOR_FAULT_PROBE=0'):
                with self.subTest(project=project, flags=flags):
                    with self.assertRaises(ValueError):
                        self.policy.selected_project(project, FQBN, flags)
                    with self.assertRaises(ValueError):
                        self.expected(flags, project=project)

    def test_D169_policy_refuses_c_cpp_mismatch_or_static_immediate_metadata(self):
        for flags in (FLAGS, ACTIVE_FLAGS):
            original = self.document(flags)
            other = ACTIVE_FLAGS if flags == FLAGS else FLAGS
            for key, value in (('compiler.c.extra_flags', other),
                               ('compiler.cpp.extra_flags', other),
                               ('build.link_mode', 'static'), ('build.boot_mode', 'immediate')):
                document = copy.deepcopy(original)
                entries = document['builder_result']['build_properties']
                matches = [i for i, item in enumerate(entries) if item.startswith(key + '=')]
                self.assertEqual(1, len(matches), 'fixture must contain exactly one target property')
                entries[matches[0]] = key + '=' + value
                for boundary in (self.validate, self.preflight):
                    with self.subTest(flags=flags, key=key, boundary=boundary.__name__):
                        with self.assertRaises(ValueError):
                            boundary(document, flags)


if __name__ == '__main__':
    unittest.main(verbosity=2)
