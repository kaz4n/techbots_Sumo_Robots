"""D093 independent native, config and inert-probe checks; production is opaque.

Existing tests are unchanged. Every subprocess result and staged source hash is
preserved, including failures, under the additive author evidence directory.
"""
from contextlib import ExitStack
import hashlib
import importlib.util
import io
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
RAW = ROOT / 'state/analysis/P2_power_inputs_raw/author'
NATIVE = ROOT / 'tests/native_power'


class PowerInputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        RAW.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(prefix='sumox_d093_author_')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.stage = Path(cls.temporary.name)
        cls.sources = cls.stage / 'src'
        shutil.copytree(ROOT / 'src', cls.sources)
        cls.base = ['g++', '-std=c++17', '-O1', '-g', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                    '-fno-sanitize-recover=all', '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                    '-isystem', str(ROOT / 'host/third_party')]
        cls.main = cls.stage / 'main.o'
        cls.command([*cls.base, '-c', str(NATIVE / 'test_main.cc'), '-o', str(cls.main)])

    @classmethod
    def command(cls, argv):
        try:
            result = subprocess.run(list(map(str, argv)), cwd=ROOT, text=True, capture_output=True, timeout=180)
        except subprocess.TimeoutExpired as error:
            result = SimpleNamespace(returncode=124, stdout=str(error.stdout or ''), stderr=str(error.stderr or '')+'\nTIMEOUT')
        manifest = {str(path.relative_to(cls.stage)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in cls.stage.rglob('*') if path.is_file() and path.suffix in ('.h', '.cpp', '.ino')}
        receipt = {'time_ns': time.time_ns(), 'argv': list(map(str, argv)), 'returncode': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr, 'staged_sha256': manifest}
        with (RAW / 'commands.jsonl').open('a', encoding='utf-8') as output:
            output.write(json.dumps(receipt) + '\n')
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        if 'test cases:' in result.stdout:
            print(' | '.join(line for line in result.stdout.splitlines() if 'test cases:' in line or 'assertions:' in line), flush=True)
        return result

    def build(self, name, case, native=False, full=False, definitions=(), source=None, extras=()):
        source = source or self.sources
        sources = [source / 'hal/power_inputs.cpp', source / 'hal/ui.cpp']
        if full:
            sources += sorted((source / 'core').glob('*.cpp'))
            sources += [source / 'hal' / name for name in ('motors.cpp', 'recorder.cpp', 'recorder_frames.cpp')]
        if native:
            sources += [source / 'hal/power.cpp', source / 'hal/native_pins.cpp', source / 'hal/power_inputs_unoq.cpp',
                        NATIVE / 'native_fixture.cc', NATIVE / 'isolation.cc']
        command = [*self.base, '-I', source, *definitions]
        if native:
            command += ['-DARDUINO_ARCH_ZEPHYR', '-I', NATIVE,
                        '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
        binary = self.stage / name
        self.command([*command, case, *sources, *extras, self.main, '-o', binary])
        self.command([binary, '--no-colors'])

    def test_host_owner_contract_both_motor_settings(self):
        for allowed in (0, 1):
            self.build('host'+str(allowed), ROOT/'tests/test_power_inputs.cpp', full=True,
                       definitions=(f'-DMOTORS_ALLOWED={allowed}',))

    def test_actual_native_reader_binding_and_no_allocation(self):
        self.build('native', NATIVE/'input_owner_cases.cc', native=True)

    def test_seeded_counter_and_button_sequence_limits(self):
        self.build('limits', NATIVE/'input_owner_limits.cc')

    def test_configuration_boundaries_before_callbacks(self):
        invalid = [({'VBAT_ADC_CONVERSION_US':'0U'}), ({'VBAT_ADC_CONVERSION_US':'10001U'}),
                   ({'VBAT_SAMPLE_PERIOD_US':'0U'}), ({'VBAT_SAMPLE_PERIOD_US':'20000U'}),
                   ({'VBAT_SAMPLE_MAX_AGE_US':'10000U'}), ({'VBAT_SAMPLE_MAX_AGE_US':'0x80000000U'}),
                   ({'VBAT_ADC_REFERENCE_V':'2.4F'}), ({'VBAT_ADC_REFERENCE_V':'3.6001F'}),
                   ({'VBAT_ADC_REFERENCE_V':'__builtin_nanf("")'}),
                   ({'VBAT_DIVIDER_RATIO':'0.999F'}), ({'VBAT_DIVIDER_RATIO':'__builtin_inff()'})]
        valid = [({'VBAT_ADC_CONVERSION_US':'10000U'}), ({'VBAT_ADC_REFERENCE_V':'3.6F'}),
                 ({'VBAT_ADC_REFERENCE_V':'2.4001F', 'VBAT_DIVIDER_RATIO':'1.0F'}),
                 ({'VBAT_SAMPLE_MAX_AGE_US':'0x7fffffffU'})]
        for index, (edits, good) in enumerate([(item,False) for item in invalid]+[(item,True) for item in valid]):
            with self.subTest(edits=edits):
                source = self.stage / ('config'+str(index)) / 'src'; shutil.copytree(self.sources, source)
                path = source / 'config.h'; config = path.read_text()
                for name, value in edits.items():
                    config, count = re.subn(r'(\b'+name+r'\s*=\s*)[^;]+;', r'\g<1>'+value+';', config)
                    self.assertEqual(count, 1, name)
                path.write_text(config)
                self.build('config_case'+str(index), NATIVE/'input_owner_limits.cc', source=source,
                           definitions=('-DINPUT_CONFIG_GOOD' if good else '-DINPUT_CONFIG_BAD',))

    def test_additive_config_registry_preserves_all_existing_assertions(self):
        from . import test_p0_config as legacy
        from . import test_dump_match
        additions = {'VBAT_SAMPLE_PERIOD_US':10000, 'VBAT_SAMPLE_MAX_AGE_US':20000}
        with mock.patch.dict(legacy.BEHAVIOR_EXTRA_DEFAULTS, additions):
            suite = unittest.TestSuite([test_dump_match.DumpCaptureTests(
                'test_additive_d088_d089_d090_registry_runs_all_legacy_config_checks')])
            output = io.StringIO(); result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
        with (RAW / 'registry.jsonl').open('a') as stream:
            stream.write(json.dumps({'success':result.wasSuccessful(),'tests_run':result.testsRun,'output':output.getvalue()})+'\n')
        self.assertTrue(result.wasSuccessful(), output.getvalue())

    def test_real_probe_startup_is_inert_in_both_macro_modes(self):
        probe = self.stage / 'probe'; shutil.copytree(ROOT/'bench/p2_power_inputs_compile', probe)
        sketch = probe/'sketch.cpp'; shutil.copyfile(probe/'p2_power_inputs_compile.ino', sketch)
        for allowed in (0, 1):
            self.build('probe'+str(allowed), NATIVE/'input_owner_probe.cc', native=True, full=True,
                       definitions=(f'-DMOTORS_ALLOWED={allowed}',f'-DMATCH={allowed}',
                                    '-I',str(probe),'-I',str(probe/'src')),
                       extras=(probe/'src/power_inputs_probe.cpp',sketch))

    def test_compile_only_probe_refuses_upload_before_transport(self):
        spec = importlib.util.spec_from_file_location('d093_board_tool', ROOT/'tools/board_tool.py')
        board = importlib.util.module_from_spec(spec); spec.loader.exec_module(board)
        for transport in ('adb','ssh'):
            for match in (False,True):
                for startup in ('default','immediate'):
                    with self.subTest(transport=transport,match=match,startup=startup), ExitStack() as stack:
                        stack.enter_context(mock.patch.dict(os.environ, {'SUMO_TRANSPORT':transport}))
                        target=stack.enter_context(mock.patch.object(board,'target'))
                        remote=stack.enter_context(mock.patch.object(board,'remote'))
                        require=stack.enter_context(mock.patch.object(board,'require_transport'))
                        with self.assertRaises(ValueError) as caught:
                            board.flash(SimpleNamespace(sketch='bench/p2_power_inputs_compile',match=match,startup=startup,compile_only=False))
                        target.assert_not_called(); remote.assert_not_called(); require.assert_not_called()
                        with (RAW/'upload_refusals.jsonl').open('a') as stream:
                            stream.write(json.dumps({'transport':transport,'match':match,'startup':startup,
                                                     'error':str(caught.exception),'target_calls':target.call_count,
                                                     'remote_calls':remote.call_count,'transport_calls':require.call_count})+'\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
