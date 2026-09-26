# Tests D197 from its frozen contract with unchanged native hardware fixtures.
# Compares original/probe0/probe1 behavior and complete ordered observations.
# Linux host only; RAM scratch, serial compilers, memfd execution, no board access.
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/locked/native_motor_port'
CASES = ROOT / 'tests/native_motor_settle_probe_cases.cc'
CONTRACT = 'state/analysis/P7_motor_settle_probe_contract.md'
CONTRACT_SHA = '3346b11970814ce7703c48f56cb38405449453964bb79d1740d5a49e78610f7c'
ORIGINAL_BLOB = 'a28f93cf3c004a4a6cbfb2847b1686d244451a4a'
ORIGINAL_SHA = '04803c88dc51e62dee4c1be15f4c1c8392df01d84893155bc10644cf7afd694a'
RECEIPT_ENV = 'SUMO_SETTLE_PROBE_RECEIPT_DIR'
UNCHANGED = {
    "bench/app_motor_observe/app_motor_observe.ino": "1df77ff537ef354bcb6bae9141ad117881216df125581f0d4ade3e286a6f007b",
    "bench/app_motor_observe/src/app_motor_observe.cpp": "eec10eacd250590f4eb4a6b1c01b0cac925411c1f126fe45fda9401de3de4bb3",
    "bench/app_motor_observe/src/app_motor_observe.h": "25bf299be1e2b917a0f91e7ad933eec5179cbfe6d92273bed0a8d9f5ce97d77e",
    "bench/motor_fault/src/motor_fault.cpp": "a5e3624ec89cf37f8344e069fed2e2f25bce1be8e0e6911b7aee774297c2f8c6",
    "bench/motor_fault/src/motor_fault.h": "0b6daf206692baab509fba12ff1afb17b812caf1ff36817883b6ee9d358c1728",
    "src/config.h": "34d6d6bce215fc098c3c4ae8e2c4436cb66e50e4f73db81a7ef8da964ba242c6",
    "src/core/opp_fusion.cpp": "693cfa4e900783d0d7bff7995623862f67296e7223b9c31157cbf620bc316d85",
    "src/hal/motor_port_unoq.h": "7f09a544a032b35207de7c5f074f3f1fd3de9e74c3b482579f819eaa39020ef5",
    "src/hal/motors.cpp": "2e6f560fca84c1ed77356299e6442afaff8dff05fcf34d51cd59c9454553198b",
    "src/hal/motors.h": "8128aa9fdbfc2bde8c811dbd82c4c79a75e625dd5714facfae44bffbe92bf149",
    "src/hal/native_pins.cpp": "222a95a33995065596ec4a08bc1a4fe925b7743aa2bb7b27c24195230376b008",
    "src/hal/native_pins.h": "34b4fb42e33ec2232f4574c997d4a701ec5a75efcbb12f37d5040e266c13022c",
    "tests/locked/native_motor_port/Arduino.h": "15e697c1fc030df2f4a0a4b83412e0c3ae017ae8bb5bbba4f8632e38798c9e14",
    "tests/locked/native_motor_port/cases.cc": "7d01821ab2ccc042140e9433bb3207b943331868726e41f644d45ca2006de312",
    "tests/locked/native_motor_port/installed_tim_bits.h": "bcff4119b6a4458e750bf793654de316fa1a1b1e9213cf74d8b5c3b3ec31fa56",
    "tests/locked/native_motor_port/mapping.h": "2a091472935328cc96c80ca50b0aac7485d036319ed63967df7e5cb743f614d9",
    "tests/locked/native_motor_port/metadata_cases.cc": "278d733f2d2ff226fdd08a8e6f4d9ab2579b48ada2c9304c966dc74f16d0ae58",
    "tests/locked/native_motor_port/native_fixture.cc": "8119661047e90a5d1aff4b946986385591f6a5b5fdcee92a4f2f302a1e3d2aa2",
    "tests/locked/native_motor_port/native_fixture.h": "2dad212ae2eb1d116e79f450345f6d171a8da15d1a5408ff34fc10921510cae5",
    "tests/locked/native_motor_port/probe_cases.cc": "2ea1dc4df62bbfb03563857ac3f4142703d2074712b021ac04bba24b3222084d",
    "tests/locked/native_motor_port/stm32_ll_gpio.h": "284e0a6136097a252e55b4ce766c8985ba856770009afe424c5e393afbfb82c2",
    "tests/locked/native_motor_port/stm32u5xx_ll_gpio.h": "5d6f325082b382e6929892c5bb08d69fed38a8cd2a51967c5568184a4fcd444c",
    "tests/locked/native_motor_port/stm32u5xx_ll_tim.h": "cb25f2a713753e7ac4c361e1ea7962a6feec25d6701d32cf97faa57a69dba388",
    "tests/locked/native_motor_port/test_main.cc": "b0277646bed186fb2567028ff5a58f57f0f0b0ecf014bb1d7879a889dce27640",
    "tests/locked/native_motor_port/wiring_private.h": "ccb299f460b3132a5b8016789158255aebc8b5860d3ae0dca329318558336391",
    "tests/locked/native_motor_port/zephyr/device.h": "dd3d0eb520f810ce7a2bb6159e6c52f0835a93e98027e4dee38e39bdcf88fb51",
    "tests/locked/native_motor_port/zephyr/devicetree.h": "04780c7a52eee68278b2f03e36a3063c25ac1dfd29490345acf1782e06cd705c",
    "tests/locked/native_motor_port/zephyr/drivers/clock_control/stm32_clock_control.h": "8983398006cfe0bcdf3504807f405df4c3da8dcd8c99f0ece20087373c4d077d",
    "tests/locked/native_motor_port/zephyr/drivers/gpio.h": "3318427099a7d0d48b9bc4f5b8d353e7a43903eed43569ec6f8b4c066f171524",
    "tests/locked/native_motor_port/zephyr/drivers/pwm.h": "15d2d808364c7a1cd988f99d502a53f569ccc58f6a688ab5f3f1c32d5e5dd2af",
    "tests/locked/native_motor_port/zephyrPinctrl.h": "7d2ab5bf595539610eca1f988ed822d68283bf004891af71a5a70e1629e18472",
    "tests/tooling/test_motor_port_unoq.py": "71b25cce8042dfcb2cd49b1fe35f0c6f548185fff836f987fa42faba416cd152"
}
SCENARIOS = (
    'null', 'unconfigured', 'missing0', 'missing1', 'missing2', 'missing3',
    'enable_readback', 'initial_rate', 'initial_register', 'loop_ready',
    'loop_register', 'final149', 'final150', 'final151', 'wrap149', 'wrap150',
    'loop_deadline', 'limit_zero', 'limit_partial', 'first_failure', 'gate_cleanup')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def settle_body(preprocessed):
    text = preprocessed.decode('utf-8')
    pattern = r'bool\s+UnoQPort::settle\s*\(\s*void\s*\*\s*context\s*\)\s*\{'
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise AssertionError('Expected one real native settle definition')
    begin = matches[0].end() - 1
    depth = 0
    for index in range(begin, len(text)):
        depth += (text[index] == '{') - (text[index] == '}')
        if depth == 0:
            return re.sub(r'\s+', '', text[begin:index + 1])
    raise AssertionError('Unclosed native settle body')


class MotorSettleProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform != 'linux' or not hasattr(os, 'memfd_create'):
            raise RuntimeError('Linux fixture mmap and memfd execution required; no silent skip')
        if not sys.flags.dont_write_bytecode or not sys.dont_write_bytecode:
            raise RuntimeError('Use Python -B for frozen independent oracle')
        cls.compiler, cls.nm = shutil.which('g++'), shutil.which('nm')
        if not cls.compiler or not cls.nm:
            raise RuntimeError('Host g++ and nm are required')
        if shutil.disk_usage('/dev/shm').free < 64 * 1024 * 1024:
            raise RuntimeError('At least64MiB RAM scratch is required')
        cls.verify_unchanged()
        cls.temp = tempfile.TemporaryDirectory(prefix='sumox-d197-', dir='/dev/shm')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.environment = dict(os.environ, TMPDIR=str(cls.stage), UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        cls.sequence = 0
        cls.subject_pins = {name: {'bytes': len((ROOT / name).read_bytes()),
                                  'sha256': sha((ROOT / name).read_bytes())} for name in (
            'src/hal/motor_port_unoq.cpp', 'src/hal/motor_settle_probe.h',
            'tests/native_motor_settle_probe_cases.cc', 'tests/tooling/test_motor_settle_probe.py')}
        original = cls.command(['git', 'cat-file', 'blob', ORIGINAL_BLOB], label='original-git-blob').stdout
        if len(original) != 16448 or sha(original) != ORIGINAL_SHA:
            raise AssertionError('Frozen original Git source differs')
        cls.original = cls.stage / 'original_native.cpp'
        cls.original.write_bytes(original)
        cls.common = []
        for index, source in enumerate((FIXTURE / 'native_fixture.cc', ROOT / 'src/hal/native_pins.cpp', ROOT / 'src/hal/motors.cpp', ROOT / 'src/core/opp_fusion.cpp')):
            target = cls.stage / f'common-{index}.o'
            cls.command([*cls.flags(0), '-c', str(source), '-o', str(target)], label=f'build-common-{index}')
            cls.common.append(target)
        cls.objects, cls.binaries = {}, {}
        for name, probe, source in (('original', 0, cls.original),
                                    ('probe0', 0, ROOT / 'src/hal/motor_port_unoq.cpp'),
                                    ('probe1', 1, ROOT / 'src/hal/motor_port_unoq.cpp')):
            cls.build_variant(name, probe, source)

    @classmethod
    def flags(cls, probe, match=0, motors=0):
        return [cls.compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                '-fno-sanitize-recover=all', '-DARDUINO_ARCH_ZEPHYR',
                f'-DMATCH={match}', f'-DMOTORS_ALLOWED={motors}',
                f'-DSUMOX_MOTOR_FAULT_PROBE={probe}', '-I', str(FIXTURE),
                '-I', str(ROOT / 'src'), '-iquote', str(ROOT / 'src/hal')]

    @classmethod
    def verify_unchanged(cls):
        for name, expected in {CONTRACT: CONTRACT_SHA, **UNCHANGED}.items():
            if sha((ROOT / name).read_bytes()) != expected:
                raise AssertionError('Protected input changed: ' + name)
        fixture_names = {p.relative_to(ROOT).as_posix() for p in FIXTURE.rglob('*') if p.is_file()}
        if fixture_names != {p for p in UNCHANGED if p.startswith('tests/locked/native_motor_port/')}:
            raise AssertionError('Locked fixture inventory changed')

    @classmethod
    def receipt(cls, label, command, result, elapsed):
        cls.sequence += 1
        folder = os.environ.get(RECEIPT_ENV)
        if not folder:
            return
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        record = {'schema': 'd197-independent-host-command-v1', 'label': label,
                  'argv': list(map(str, command)), 'returncode': result.returncode,
                  'elapsed_seconds': elapsed, 'inputs': cls.subject_pins,
                  'stdout_bytes': len(result.stdout), 'stdout_sha256': sha(result.stdout),
                  'stderr_bytes': len(result.stderr), 'stderr_sha256': sha(result.stderr),
                  'stdout_prefix': result.stdout[:2000].decode('utf-8', 'replace') if result.returncode else '',
                  'stderr_prefix': result.stderr[:8000].decode('utf-8', 'replace'),
                  'capture': 'Exact bytes compared in RAM; compact hashes retained, not a target receipt'}
        with (path / f'{cls.sequence:03d}-{label}.json').open('x', encoding='utf-8', newline='\n') as target:
            json.dump(record, target, sort_keys=True, indent=2)
            target.write('\n')

    @classmethod
    def command(cls, command, *, label, success=True, **kwargs):
        start = time.monotonic()
        try:
            result = subprocess.run(list(map(str, command)), cwd=ROOT, capture_output=True,
                                    env=cls.environment, timeout=120, **kwargs)
        except subprocess.TimeoutExpired as error:
            result = subprocess.CompletedProcess(command, -1, error.stdout or b'', error.stderr or b'')
            cls.receipt(label, command, result, time.monotonic() - start)
            raise
        cls.receipt(label, command, result, time.monotonic() - start)
        if success and result.returncode:
            raise AssertionError(f'{label}: exit {result.returncode}\n' +
                                 result.stdout[-4000:].decode('utf-8', 'replace') +
                                 result.stderr[-8000:].decode('utf-8', 'replace'))
        return result

    @classmethod
    def build_variant(cls, name, probe, source):
        obj, cases = cls.stage / (name + '.o'), cls.stage / (name + '-cases.o')
        cls.command([*cls.flags(probe), '-c', source, '-o', obj], label='build-' + name)
        cls.command([*cls.flags(probe), '-c', CASES, '-o', cases], label='build-cases-' + name)
        binary = cls.stage / name
        wrappers = '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free,--wrap=_Z6microsv'
        cls.command([*cls.flags(probe), obj, cases, *cls.common, wrappers, '-o', binary], label='link-' + name)
        cls.objects[name], cls.binaries[name] = obj, binary

    def test_probe0_preprocessed_settle_body_is_exact_original(self):
        original = self.command([*self.flags(0), '-E', '-P', self.original], label='preprocess-original').stdout
        current = self.command([*self.flags(0), '-E', '-P', ROOT / 'src/hal/motor_port_unoq.cpp'],
                               label='preprocess-probe0').stdout
        self.assertEqual(settle_body(current), settle_body(original))

    def test_probe0_symbols_unchanged_and_report_exists_only_in_probe1(self):
        observed = {}
        for name, obj in self.objects.items():
            raw = self.command([self.nm, '-C', '--defined-only', obj], label='symbols-' + name).stdout.decode()
            observed[name] = sorted(re.sub(r'^[0-9a-fA-F]+\s+', '', line) for line in raw.splitlines())
        self.assertEqual(observed['original'], observed['probe0'])
        self.assertNotRegex('\n'.join(observed['probe0']), r'settle[Pp]robe|settle_probe')
        self.assertTrue(any('settleProbeReport()' in line for line in observed['probe1']))
        self.assertEqual(sum('settle_probe_report' in line for line in observed['probe1']), 1)

    def test_public_interface_exclusion_and_existing_inert_guards(self):
        include = b'#include "hal/motor_settle_probe.h"\n'
        use = include + b'auto pointer = &motors::settleProbeReport;\n'
        excluded = self.command([*self.flags(0), '-x', 'c++', '-fsyntax-only', '-'],
                                input=use, success=False, label='guard-probe0-interface')
        self.assertNotEqual(excluded.returncode, 0)
        self.assertIn(b'settleProbeReport', excluded.stderr)
        for match, motors in ((1, 0), (0, 1), (1, 1)):
            with self.subTest(match=match, motors=motors):
                result = self.command([*self.flags(1, match, motors), '-x', 'c++', '-fsyntax-only', '-'],
                    input=include, success=False, label=f'guard-inert-{match}-{motors}')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b'Motor fault probe is exclusive and requires inert flags', result.stderr)

    def test_all_exit_reports_and_exact_original_probe0_probe1_native_clock_hardware_sequences(self):
        for scenario in SCENARIOS:
            observations = {}
            for variant, binary in self.binaries.items():
                with self.subTest(scenario=scenario, variant=variant):
                    fd = os.memfd_create('sumox-d197-' + variant, flags=0)
                    try:
                        with os.fdopen(os.dup(fd), 'wb') as target:
                            target.write(binary.read_bytes())
                        reply = self.command([f'/proc/self/fd/{fd}', scenario], pass_fds=(fd,),
                                             label='scenario-' + scenario + '-' + variant)
                    finally:
                        os.close(fd)
                    self.assertIn(b'SEGMENT ', reply.stdout)
                    self.assertEqual(reply.stderr, b'')
                    observations[variant] = reply.stdout
            self.assertEqual(set(observations), {'original', 'probe0', 'probe1'}, scenario)
            self.assertEqual(observations['original'], observations['probe0'], scenario)
            self.assertEqual(observations['original'], observations['probe1'], scenario)
            print(f'{scenario}: exact 3-way transcript {len(observations["original"])}B '
                  f'SHA256 {sha(observations["original"])}', flush=True)

    def test_unchanged_config_trace_runner_and_all_locked_fixture_bytes(self):
        self.verify_unchanged()


if __name__ == '__main__':
    unittest.main(verbosity=2)
