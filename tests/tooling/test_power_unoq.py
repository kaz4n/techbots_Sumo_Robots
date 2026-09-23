# Tests actual native B5 source with an independent installed-shaped hardware model.
# Compiler and execution receipts retain status, streams and opaque production hashes.
# Linux/WSL only; local tests never access a board, transport or firmware upload.
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/native_power'

class NativePowerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = shutil.which('g++')
        if cls.compiler is None:
            raise RuntimeError('Run native power tests under Linux/WSL with g++')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-native-power-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.binary_manifests = {}
        cls.base = [cls.compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                    '-fno-sanitize-recover=all', '-DARDUINO_ARCH_ZEPHYR',
                    '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS', '-I', str(FIXTURE),
                    '-isystem', str(ROOT / 'host/third_party')]
        cls.main = cls.stage / 'main.o'
        cls.command([*cls.base, '-c', str(FIXTURE / 'test_main.cc'), '-o', str(cls.main)])

    @classmethod
    def receipt(cls, argv, result):
        folder = os.environ.get('SUMO_NATIVE_RECEIPT_DIR')
        if not folder:
            folder = cls.stage / 'receipts'
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        native_source = next((Path(x) for x in argv if str(x).endswith('/hal/power.cpp')), None)
        manifest = cls.binary_manifests.get(str(argv[0]))
        if native_source is not None:
            manifest = {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in {
                'production': native_source, 'header': native_source.with_suffix('.h'),
                'config': native_source.parent.parent / 'config.h'}.items()}
        payload = {'staged_source_manifest': manifest, 'argv': list(map(str, argv)), 'returncode': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr,
                   'capture': 'subprocess text=True; newline normalized',
                   'production_sha256': hashlib.sha256(next((Path(x) for x in argv if str(x).endswith('/hal/power.cpp')), ROOT / 'src/hal/power.cpp').read_bytes()).hexdigest(),
                   'public_header_sha256': hashlib.sha256((ROOT / 'src/hal/power.h').read_bytes()).hexdigest(),
                   'config_sha256': hashlib.sha256((ROOT / 'src/config.h').read_bytes()).hexdigest()}
        (path / ('native_power_' + str(time.time_ns()) + '.json')).write_text(
            json.dumps(payload, indent=2) + '\n', encoding='utf-8')

    @classmethod
    def command(cls, argv, timeout=120, expected_returncode=0):
        try:
            result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as e:
            result = SimpleNamespace(returncode=124, stdout=str(e.stdout or ''), stderr=str(e.stderr or '')+'\nTIMEOUT')
        cls.receipt(argv, result)
        if result.returncode != expected_returncode:
            raise AssertionError('Opaque native command failed:\n' + result.stdout + result.stderr)
        return result

    @classmethod
    def variant(cls, definitions=(), case='cases.cc', edits=None, probe=False):
        slot = cls.stage / ('variant-' + str(len(list(cls.stage.glob('variant-*')))))
        slot.mkdir()
        source = slot / 'src'
        (source / 'hal').mkdir(parents=True)
        for name in ('power.cpp', 'power.h'):
            shutil.copyfile(ROOT / 'src/hal' / name, source / 'hal' / name)
        shutil.copyfile(ROOT / 'src/config.h', source / 'config.h')
        if edits:
            config = (source / 'config.h').read_text()
            for name, value in edits.items():
                config, n = re.subn(r'(\b' + re.escape(name) + r'\s*=\s*)[^;]+;', r'\g<1>' + value + ';', config)
                if n != 1:
                    raise AssertionError('Fixture could not select config name: ' + name)
            (source / 'config.h').write_text(config)
        binary = slot / 'native-power'
        argv = [*cls.base, '-I', str(source), *definitions, str(FIXTURE / case),
                str(FIXTURE / 'native_fixture.cc'), str(FIXTURE / 'isolation.cc'), str(source / 'hal/power.cpp'), str(cls.main),
                '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
        if probe:
            sketch = slot / 'power_sketch.cpp'
            shutil.copyfile(ROOT / 'bench/p2_power_compile/p2_power_compile.ino', sketch)
            argv += ['-I', str(ROOT / 'bench/p2_power_compile/src'),
                     '-I', str(ROOT / 'bench/p2_power_compile'),
                     str(ROOT / 'bench/p2_power_compile/src/power_probe.cpp'), str(sketch)]
        cls.command([*argv, '-o', str(binary)])
        cls.binary_manifests[str(binary)] = {name: hashlib.sha256(p.read_bytes()).hexdigest()
            for name, p in {'production': source / 'hal/power.cpp',
                            'header': source / 'hal/power.h', 'config': source / 'config.h'}.items()}
        return binary

    def execute(self, binary):
        result = self.command([str(binary), '--no-colors'], timeout=35)
        self.assertIn('Status: SUCCESS!', result.stdout)
        print(' | '.join(line for line in result.stdout.splitlines()
                         if 'test cases:' in line or 'assertions:' in line), flush=True)

    def test_b5_isolation_propagates_child_assertions_and_crashes(self):
        binary = self.variant(case="isolation_selftest.cc")
        for name in ("*assertion*", "*signal*"):
            result = self.command([str(binary), "--no-colors", "--test-case=" + name], expected_returncode=1)
            self.assertIn("Status: FAILURE!", result.stdout)

    def test_b5_exact_deadlines_and_clock_transition_guards(self):
        self.execute(self.variant(case="timing_cases.cc"))

    def test_b5_all_ownership_guards(self):
        self.execute(self.variant(case="ownership_cases.cc"))

    def test_b5_partial_claim_is_reset_only(self):
        self.execute(self.variant(case="takeover_cases.cc"))

    def test_b5_native_contract(self):
        self.execute(self.variant())

    def test_b5_invalid_pad_metadata_and_conflicting_proposals(self):
        for kind in range(1, 5):
            with self.subTest(kind=kind):
                self.execute(self.variant(definitions=(f'-DNATIVE_BAD_MAP={kind}',), case='metadata_cases.cc'))
        for index in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 17, 18, 19):
            with self.subTest(alias_index=index):
                self.execute(self.variant(definitions=('-DNATIVE_BAD_MAP=5', f'-DNATIVE_ALIAS_INDEX={index}'), case='metadata_cases.cc'))
        for size in (14, 19):
            with self.subTest(table_size=size):
                self.execute(self.variant(definitions=(f'-DNATIVE_TABLE_SIZE={size}',), case='metadata_cases.cc'))

    def test_b5_config_rejects_unsupported_scaling_and_bounds_before_io(self):
        variants = [('VBAT_INPUT_PIN', '999U'), ('VBAT_ADC_REFERENCE_V', '0.0F'),
                    ('VBAT_ADC_REFERENCE_V', '2.4F'), ('VBAT_ADC_REFERENCE_V', '3.61F'),
                    ('VBAT_ADC_REFERENCE_V', '__builtin_nanf("")'),
                    ('VBAT_DIVIDER_RATIO', '0.99F'), ('VBAT_DIVIDER_RATIO', '__builtin_inff()'),
                    ('VBAT_ADC_POST_CAL_US', '1U')]
        for name in ('VBAT_ADC_REGULATOR_US', 'VBAT_ADC_CALIBRATION_US',
                     'VBAT_ADC_ENABLE_US', 'VBAT_ADC_CONVERSION_US', 'VBAT_ADC_SHUTDOWN_US',
                     'VBAT_ADC_SETUP_MAX_POLLS', 'VBAT_ADC_READ_MAX_POLLS'):
            variants += [(name, '0U'), (name, '0x80000000U')]
        for name, value in variants:
            with self.subTest(name=name, value=value):
                self.execute(self.variant(case='config_cases.cc', edits={name: value}))

    def test_b5_probe_startup_and_10000_loops_are_inert(self):
        for allowed in (0, 1):
            with self.subTest(allowed=allowed):
                self.execute(self.variant(definitions=(f'-DMATCH={allowed}', f'-DMOTORS_ALLOWED={allowed}'), case='probe_cases.cc', probe=True))

    def test_b5_probe_all_upload_modes_refuse_before_transport_lookup(self):
        spec = importlib.util.spec_from_file_location('power_board_tool', ROOT / 'tools/board_tool.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for transport in ('adb', 'ssh'):
            for match in (False, True):
                for startup in ('default', 'immediate'):
                    with self.subTest(transport=transport, match=match, startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict('os.environ', {'SUMO_TRANSPORT': transport}))
                        target = stack.enter_context(mock.patch.object(module, 'target'))
                        remote = stack.enter_context(mock.patch.object(module, 'remote'))
                        with self.assertRaises(ValueError):
                            module.flash(SimpleNamespace(sketch='bench/p2_power_compile', match=match,
                                                         startup=startup, compile_only=False))
                        target.assert_not_called()
                        remote.assert_not_called()

if __name__ == '__main__':
    unittest.main(verbosity=2)
