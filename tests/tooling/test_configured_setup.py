# Checks D180's explicit config declarations against the frozen public contract.
# Keeps setup evidence independent of build flags and observes the actual entry.
# Run Python -B under WSL; only serial C++17 host fixtures execute in owned RAM.
from contextlib import ExitStack
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
FLAGS = (
    ('APP_GRANT_OPPONENTS', 'opponents'),
    ('APP_GRANT_ADC_PAIR', 'adc_pair'),
    ('APP_GRANT_QTR_EXCLUSIVE_PADS', 'qtr_exclusive_pads'),
    ('APP_GRANT_IMU_ENABLED', 'imu_enabled'),
    ('APP_GRANT_IMU_POWER_CONFIRMED', 'imu_power_confirmed'),
    ('APP_GRANT_IMU_MOUNTING_CONFIRMED', 'mounting.confirmed'),
    ('APP_GRANT_DEFAULT_LINE_THRESHOLDS', 'default_line_thresholds_confirmed'),
    ('APP_GRANT_MATRIX_ENABLED', 'matrix_enabled'),
    ('APP_GRANT_MATRIX_NORMAL_STARTUP', 'matrix.normal_startup'),
    ('APP_GRANT_MATRIX_EXCLUSIVE_OWNER', 'matrix.exclusive_boot_owner'),
    ('APP_GRANT_DUMP_ENABLED', 'dump_enabled'),
    ('APP_GRANT_DUMP_SETUP_PHASE', 'dump.setup_phase'),
    ('APP_GRANT_DUMP_EXCLUSIVE_UART', 'dump.exclusive_uart'),
    ('APP_GRANT_DUMP_READY_PIN_OWNED', 'dump.ready_pin_owned'),
    ('APP_GRANT_DUMP_FRAMING_CLEAN', 'dump.framing_clean'),
    ('APP_GRANT_LOCAL_SERVICE_RESET', 'local_service_reset'),
    ('APP_GRANT_CALIBRATION_OUTPUT', 'calibration_output_enabled'),
)
BUILD_FLAGS = ((0, 0), (0, 1), (1, 0), (1, 1))
ORIGINS = ('UNKNOWN', 'SYNTHETIC', 'HARDWARE_REPORTED')

# Typed replacements exercise the unchanged sketch text without native effects.
# Builder tests below independently use the real public SetupGrants definition.
ENTRY_TYPES = r'''
#pragma once
#ifdef EMPTY
#error Native includes must retain the existing EMPTY protection
#endif
#include <cstdint>
namespace fixture {
inline unsigned constructors = 0, builders = 0, begins = 0, steps = 0;
inline bool correct_ports = false;
}
namespace imu {
struct Mounting { std::int8_t body_axis[3] = {}; bool confirmed = false; };
}
namespace ui {
struct MatrixGrant { bool normal_startup = false, exclusive_boot_owner = false; };
}
namespace motors {
struct Port { int identity; };
struct UnoQPort { Port port() { return {11}; } };
}
namespace power { struct InputPort { int identity; }; }
namespace recorder::dump {
enum class Origin : std::uint8_t { UNKNOWN, SYNTHETIC, HARDWARE_REPORTED };
enum class Buffering : std::uint8_t { LEGACY_SINGLE, FIFO8 };
enum class ReceiveStream : std::uint8_t { TRUSTED_FRAMING, UNTRUSTED_RECEIVE_STREAM };
struct SetupGrant {
    bool setup_phase = false, exclusive_uart = false;
    bool ready_pin_owned = false, framing_clean = false;
    ReceiveStream receive_stream = ReceiveStream::TRUSTED_FRAMING;
    std::uint64_t session = 0U;
};
struct UnoQDumpPort {
    explicit UnoQDumpPort(Buffering value) : buffering(value) {}
    Buffering buffering;
};
}
namespace app {
struct SourcePort { int identity; };
struct DumpPort { int identity; };
struct SetupGrants {
    bool opponents = false, adc_pair = false, qtr_exclusive_pads = false;
    bool imu_enabled = false, imu_power_confirmed = false;
    imu::Mounting mounting;
    bool default_line_thresholds_confirmed = false, matrix_enabled = false;
    ui::MatrixGrant matrix;
    bool dump_enabled = false;
    recorder::dump::SetupGrant dump;
    recorder::dump::Origin dump_origin = recorder::dump::Origin::UNKNOWN;
    bool local_service_reset = false, calibration_output_enabled = false;
};
inline SetupGrants received{};
struct NativeSources {
    power::InputPort adcPort() { return {22}; }
    SourcePort port() { return {33}; }
};
inline DumpPort unoQDumpPort(recorder::dump::UnoQDumpPort& owner) {
    return {owner.buffering == recorder::dump::Buffering::FIFO8 ? 44 : -1};
}
struct Runtime {
    Runtime(motors::Port motor, power::InputPort adc, SourcePort source,
            DumpPort dump) {
        ++fixture::constructors;
        fixture::correct_ports = motor.identity == 11 && adc.identity == 22 &&
            source.identity == 33 && dump.identity == 44;
    }
    bool begin(const SetupGrants& grants) {
        ++fixture::begins;
        received = grants;
        return true;
    }
    bool step() { ++fixture::steps; return true; }
};
}
'''


def expected_fields(flags=None, axes=(0, 0, 0), origin=0, stream=0, session=0):
    enabled = flags or {}
    values = {field: 'true' if enabled.get(name, 0) else 'false'
              for name, field in FLAGS}
    values.update({f'mounting.body_axis[{index}]': str(value)
                   for index, value in enumerate(axes)})
    values['dump_origin'] = 'recorder::dump::Origin::' + ORIGINS[origin]
    values['dump.receive_stream'] = ('recorder::dump::ReceiveStream::' +
        ('TRUSTED_FRAMING', 'UNTRUSTED_RECEIVE_STREAM')[stream])
    values['dump.session'] = str(session) + 'ULL'
    return values


def constant_assertions(flags=None, axes=(0, 0, 0), origin=0, defaults=False,
                        stream=0, session=0):
    text = ['#include "src/app/configured_setup.h"', '#include <type_traits>',
            'constexpr app::SetupGrants actual = app::configuredSetupGrants();',
            'static_assert(std::is_same_v<decltype(app::configuredSetupGrants()), '
            'app::SetupGrants>);']
    for name, _ in FLAGS:
        text.append('static_assert(std::is_same_v<std::remove_cv_t<decltype('
                    f'config::{name})>, std::uint32_t>);')
    text.extend((
        'static_assert(std::is_same_v<std::remove_cv_t<decltype('
        'config::APP_IMU_BODY_AXIS)>, std::int32_t[3]>);',
        'static_assert(std::is_same_v<std::remove_cv_t<decltype('
        'config::APP_DUMP_ORIGIN)>, std::uint32_t>);',
        'static_assert(std::is_same_v<std::remove_cv_t<decltype('
        'config::APP_DUMP_RECEIVE_STREAM_ID)>, std::uint32_t>);',
        'static_assert(std::is_same_v<std::remove_cv_t<decltype('
        'config::APP_DUMP_SESSION_ID)>, std::uint64_t>);',
    ))
    if defaults:
        text.append('constexpr app::SetupGrants empty{};')
    for field, value in expected_fields(flags, axes, origin, stream, session).items():
        text.append(f'static_assert(actual.{field} == {value}, "{field}");')
        if defaults:
            text.append(f'static_assert(actual.{field} == empty.{field});')
    return '\n'.join(text) + '\n'


class ConfiguredSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.flags.dont_write_bytecode or not sys.dont_write_bytecode:
            raise RuntimeError('D180 fixtures require Python -B')
        if sys.platform != 'linux' or not hasattr(os, 'memfd_create'):
            raise RuntimeError('D180 fixture execution requires Linux memfd')
        cls.compiler = shutil.which('g++')
        if cls.compiler is None or not Path('/dev/shm').is_dir():
            raise RuntimeError('D180 fixtures require Linux/WSL g++ and /dev/shm')
        if shutil.disk_usage('/dev/shm').free < 32 * 1024 * 1024:
            raise RuntimeError('D180 RAM fixture requires 32 MiB free')
        headers = tuple((ROOT / 'src').rglob('*.h'))
        if sum(path.stat().st_size for path in headers) > 4 * 1024 * 1024:
            raise RuntimeError('D180 header fixture exceeds its 4 MiB bound')
        cls.temporary = tempfile.TemporaryDirectory(prefix='sumo-d180-', dir='/dev/shm')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.ram = Path(cls.temporary.name)
        cls.real = cls.ram / 'real'
        for source in headers:
            target = cls.real / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        cls.config = (cls.real / 'src/config.h').read_text(encoding='utf-8')
        cls.env = dict(os.environ, TMPDIR=str(cls.ram), LC_ALL='C')
        cls.base = [cls.compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
                    '-pedantic', '-fno-exceptions', '-fno-rtti']

    def command(self, argv, success=True, timeout=30, pass_fds=()):
        result = subprocess.run(list(map(str, argv)), cwd=self.ram, env=self.env,
                                text=True, capture_output=True, timeout=timeout,
                                pass_fds=pass_fds)
        detail = ' '.join(map(str, argv)) + '\n' + result.stdout + result.stderr
        if success:
            self.assertEqual(0, result.returncode, detail)
        else:
            self.assertNotEqual(0, result.returncode, detail)
            self.assertIn('static assertion failed', result.stderr, detail)
        return result

    def run_binary(self, binary):
        self.assertLessEqual(binary.stat().st_size, 1024 * 1024)
        descriptor = os.memfd_create('sumox-d180-fixture', flags=0)
        try:
            with os.fdopen(os.dup(descriptor), 'wb') as stream:
                stream.write(binary.read_bytes())
            self.command([f'/proc/self/fd/{descriptor}'], timeout=5,
                         pass_fds=(descriptor,))
        finally:
            os.close(descriptor)

    def configure(self, flags=None, axes=None, origin=None, stream=0, session=0):
        text = self.config
        replacements = dict(flags or {})
        if origin is not None:
            replacements['APP_DUMP_ORIGIN'] = origin
        replacements['APP_DUMP_RECEIVE_STREAM_ID'] = stream
        replacements['APP_DUMP_SESSION_ID'] = session
        for name, value in replacements.items():
            width = '64' if name == 'APP_DUMP_SESSION_ID' else '32'
            pattern = (r'(inline\s+constexpr\s+std::uint' + width + r'_t\s+' + re.escape(name)
                       + r'\s*=\s*)0U(\s*;)')
            text, count = re.subn(pattern, lambda match: match[1] + str(value) +
                                  'U' + match[2], text)
            self.assertEqual(1, count, 'single default declaration for ' + name)
        if axes is not None:
            pattern = (r'(inline\s+constexpr\s+std::int32_t\s+APP_IMU_BODY_AXIS'
                       r'\s*\[3\]\s*=\s*)\{\s*0\s*,\s*0\s*,\s*0\s*\}(\s*;)')
            value = '{' + ', '.join(map(str, axes)) + '}'
            text, count = re.subn(pattern, lambda match: match[1] + value + match[2], text)
            self.assertEqual(1, count, 'single zero mounting declaration')
        (self.real / 'src/config.h').write_text(text, encoding='utf-8')

    def compile_case(self, flags=None, axes=(0, 0, 0), origin=0,
                     build=(0, 0), defaults=False, stream=0, session=0):
        self.configure(flags, axes, origin, stream, session)
        source = self.real / 'case.cc'
        source.write_text(constant_assertions(flags, axes, origin, defaults, stream, session), encoding='utf-8')
        self.command([*self.base, f'-DMATCH={build[0]}', f'-DMOTORS_ALLOWED={build[1]}',
                      '-I', self.real, '-fsyntax-only', source])

    def reject_case(self, flags=None, axes=None, origin=None):
        self.configure(flags, axes, origin)
        source = self.real / 'reject.cc'
        source.write_text('#include "src/app/configured_setup.h"\n', encoding='utf-8')
        self.command([*self.base, '-DMATCH=0', '-DMOTORS_ALLOWED=0', '-I', self.real,
                      '-fsyntax-only', source], success=False)

    def test_00_D180_real_type_constexpr_defaults_in_all_build_combinations(self):
        for build in BUILD_FLAGS:
            with self.subTest(build=build):
                # Do not rewrite defaults: this observes the shipped declarations.
                (self.real / 'src/config.h').write_text(self.config, encoding='utf-8')
                source = self.real / 'defaults.cc'
                source.write_text(constant_assertions(defaults=True), encoding='utf-8')
                self.command([*self.base, f'-DMATCH={build[0]}',
                              f'-DMOTORS_ALLOWED={build[1]}', '-I', self.real,
                              '-fsyntax-only', source])

    def test_01_D180_each_of_seventeen_grants_maps_only_its_declared_field(self):
        for name, field in FLAGS:
            with self.subTest(config=name, destination=field):
                self.compile_case({name: 1})

    def test_02_D180_each_false_survives_all_other_grants_being_true(self):
        for omitted, _ in FLAGS:
            flags = {name: int(name != omitted) for name, _ in FLAGS}
            with self.subTest(omitted=omitted):
                self.compile_case(flags, axes=(1, 2, 3), origin=2)

    def test_03_D180_mixed_grants_are_independent_of_build_flags(self):
        for parity in (0, 1):
            flags = {name: int(index % 2 == parity)
                     for index, (name, _) in enumerate(FLAGS)}
            for build in BUILD_FLAGS:
                with self.subTest(parity=parity, build=build):
                    self.compile_case(flags, axes=(-2, 3, -1), origin=1, build=build)

    def test_04_D180_every_in_range_axis_value_is_preserved_at_every_position(self):
        for value in range(-3, 4):
            with self.subTest(value=value):
                self.compile_case(axes=(value, value, value))
        for axes in ((1, 2, 3), (-1, -2, 3), (2, 3, 1), (3, -2, 1), (-3, 1, -2)):
            with self.subTest(axes=axes):
                self.compile_case(axes=axes)

    def test_05_D180_each_origin_preserves_all_false_grants(self):
        for origin in range(3):
            with self.subTest(origin=origin):
                self.compile_case(origin=origin)

    def test_06_D180_origin_is_independent_of_dump_permissions(self):
        for flags in ({'APP_GRANT_DUMP_ENABLED': 1},
                      {name: 1 for name, _ in FLAGS if name.startswith('APP_GRANT_DUMP_')
                       and name != 'APP_GRANT_DUMP_ENABLED'}):
            for origin in range(3):
                with self.subTest(flags=flags, origin=origin):
                    self.compile_case(flags, origin=origin)

    def test_07_D180_in_range_malformed_and_unconfirmed_mountings_are_not_repaired(self):
        for axes, confirmed in (((1, 1, 1), 1), ((1, 2, -3), 1), ((0, 2, 3), 1),
                                ((1, 2, 3), 0), ((-2, 1, 3), 1)):
            with self.subTest(axes=axes, confirmed=confirmed):
                self.compile_case({'APP_GRANT_IMU_MOUNTING_CONFIRMED': confirmed}, axes=axes)

    def consumer_rejects(self, axes, confirmed, fault):
        flags = {'APP_GRANT_IMU_MOUNTING_CONFIRMED': confirmed}
        self.configure(flags, axes)
        source = self.real / 'consumer.cc'
        source.write_text(constant_assertions(flags, axes) + r'''
int main() {
    imu::Estimator estimator;
    if (estimator.begin(actual.mounting, 0.0F)) return 1;
    return estimator.report().fault == imu::HeadingFault::''' + fault + r''' ? 0 : 2;
}
''', encoding='utf-8')
        consumer = self.real / 'src/hal/imu_heading.cpp'
        shutil.copyfile(ROOT / 'src/hal/imu_heading.cpp', consumer)
        output = self.ram / 'consumer.exe'
        try:
            self.command([*self.base, '-DMATCH=0', '-DMOTORS_ALLOWED=0', '-I', self.real,
                          source, consumer, '-o', output])
            self.run_binary(output)
        finally:
            output.unlink(missing_ok=True)

    def test_08_D180_existing_estimator_retains_unconfirmed_mounting_rejection(self):
        self.consumer_rejects((1, 2, 3), 0, 'MOUNTING_UNCONFIRMED')

    def test_09_D180_existing_estimator_retains_malformed_mounting_rejection(self):
        for axes in ((1, 1, 1), (1, 2, -3), (0, 2, 3)):
            with self.subTest(axes=axes):
                self.consumer_rejects(axes, 1, 'MOUNTING_INVALID')

    def test_10_D180_every_nonbinary_flag_fails_compilation(self):
        for name, _ in FLAGS:
            for value in (2, 4294967295):
                with self.subTest(config=name, value=value):
                    self.reject_case(flags={name: value})

    def test_11_D180_each_out_of_range_axis_fails_before_narrowing(self):
        for index in range(3):
            for value in (-2147483648, -129, -4, 4, 128, 2147483647):
                axes = [0, 0, 0]
                axes[index] = value
                with self.subTest(index=index, value=value):
                    self.reject_case(axes=axes)

    def test_12_D180_invalid_origins_fail_compilation(self):
        for origin in (3, 255, 256, 4294967295):
            with self.subTest(origin=origin):
                self.reject_case(origin=origin)

    def entry_case(self, flags=None, axes=(0, 0, 0), origin=0, build=(0, 0), stream=0, session=0):
        stage = self.ram / 'entry'
        for folder in ('src/app', 'src/hal'):
            (stage / folder).mkdir(parents=True, exist_ok=True)
        (stage / 'types.h').write_text(ENTRY_TYPES, encoding='utf-8')
        for name in ('src/app/native_sources_unoq.h', 'src/hal/motor_port_unoq.h'):
            (stage / name).write_text('#include "types.h"\n', encoding='utf-8')
        values = expected_fields(flags, axes, origin, stream, session)
        assignments = '\n'.join(f'    grants.{field} = {value};' for field, value in values.items())
        builder = '#include "types.h"\nnamespace app {\nSetupGrants configuredSetupGrants() {\n'
        builder += '    ++fixture::builders;\n    SetupGrants grants{};\n' + assignments
        builder += '\n    return grants;\n}\n}\n'
        (stage / 'src/app/configured_setup.h').write_text(builder, encoding='utf-8')
        shutil.copyfile(ROOT / 'src/app/app.ino', stage / 'app.ino')
        checks = '\n'.join(f'    if (app::received.{field} != {value}) return 30;'
                           for field, value in values.items())
        main = r'''
#include "app.ino"
#if EMPTY != 777
#error Sketch must restore EMPTY after protected includes
#endif
int main() {
    if (fixture::constructors != 1 || !fixture::correct_ports) return 10;
    if (fixture::builders || fixture::begins || fixture::steps) return 11;
    setup();
    if (fixture::builders != 1 || fixture::begins != 1 || fixture::steps) return 12;
''' + checks + r'''
    loop(); loop(); loop();
    if (fixture::builders != 1 || fixture::begins != 1 || fixture::steps != 3) return 13;
''' + checks + '\n    return 0;\n}\n'
        source = stage / 'entry.cc'
        source.write_text(main, encoding='utf-8')
        output = self.ram / 'entry.exe'
        try:
            self.command([*self.base, f'-DMATCH={build[0]}', f'-DMOTORS_ALLOWED={build[1]}',
                          '-DEMPTY=777', '-I', stage, source, '-o', output])
            self.run_binary(output)
        finally:
            output.unlink(missing_ok=True)

    def test_13_D180_actual_entry_forwards_defaults_once_and_only_steps_in_loop(self):
        for build in BUILD_FLAGS:
            with self.subTest(build=build):
                self.entry_case(build=build)

    def test_14_D180_actual_entry_forwards_complete_synthetic_nonzero_grants(self):
        for parity in (0, 1):
            flags = {name: int(index % 2 == parity)
                     for index, (name, _) in enumerate(FLAGS)}
            for build in BUILD_FLAGS:
                with self.subTest(parity=parity, build=build):
                    self.entry_case(flags, axes=(-2, 3, -1), origin=1, build=build)

    def test_15_D180_additive_registry_preserves_all_legacy_assertions(self):
        from tests.tooling import test_runtime_config_registry as registry
        additions = {name: 0 for name, _ in FLAGS}
        additions['APP_DUMP_ORIGIN'] = 0
        additions['APP_DUMP_RECEIVE_STREAM_ID'] = 0
        additions['TICK_DISTRIBUTION_LIMIT_US'] = 800  # Accepted D229 diagnostic range.
        additions['APP_MOTOR_OBSERVE_EPOCHS'] = 10000  # Accepted observation contract.
        additions['APP_MOTOR_OBSERVE_MAX_POLLS'] = 10000000
        wrong = self.ram / 'registry_wrong'
        (wrong / 'docs').mkdir(parents=True)
        (wrong / 'src').mkdir()
        shutil.copyfile(ROOT / 'docs/BEHAVIOR.md', wrong / 'docs/BEHAVIOR.md')
        self.configure({'APP_GRANT_OPPONENTS': 1})
        shutil.copyfile(self.real / 'src/config.h', wrong / 'src/config.h')
        with ExitStack() as patches:
            patches.enter_context(mock.patch.dict(registry.legacy.BEHAVIOR_EXTRA_DEFAULTS,
                                                  additions))
            patches.enter_context(mock.patch.dict(registry.legacy.BEHAVIOR_DERIVED_TYPES,
                                                  {'APP_IMU_BODY_AXIS[3]': 'std::int32_t',
                                                   'APP_DUMP_SESSION_ID': 'std::uint64_t'}))
            patches.enter_context(mock.patch.object(registry, 'RAW', self.ram / 'registry_raw'))
            patches.enter_context(mock.patch.object(tempfile, 'tempdir', str(self.ram)))
            case = registry.RuntimeConfigRegistryTests('runTest')
            case.run_registry('D180-approved-defaults')
            case.run_registry('D180-opponents-wrong-value', wrong, expected_failure=True)

    def test_16_D234_session_and_stream_are_exact_without_manufacturing_grants(self):
        for stream, session in ((0, 0), (0, 1), (1, 0), (1, 4294967296),
                                (1, 9223372036854775808), (1, 18446744073709551615)):
            for build in BUILD_FLAGS:
                with self.subTest(stream=stream, session=session, build=build):
                    self.compile_case(stream=stream, session=session, build=build)
        for build in BUILD_FLAGS:
            self.entry_case(stream=1, session=18446744073709551615, build=build)

    def test_17_D234_undefined_receive_stream_is_rejected_before_enum_cast(self):
        for stream in (2, 255, 256, 4294967295):
            self.configure(stream=stream, session=1)
            source = self.real / 'reject-stream.cc'
            source.write_text('#include "src/app/configured_setup.h"\n', encoding='utf-8')
            self.command([*self.base, '-I', self.real, '-fsyntax-only', source], success=False)


if __name__ == '__main__':
    unittest.main()
