# Tests actual native B2 source with an independent installed-shaped hardware model.
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
FIXTURE = ROOT / 'tests/native_qtr'

class NativeQtrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = shutil.which('g++')
        if cls.compiler is None:
            raise RuntimeError('Run native QTR tests under Linux/WSL with g++')
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-native-qtr-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        cls.binary_manifests = {}
        cls.base = [cls.compiler, '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic',
                    '-Werror', '-fno-exceptions', '-fno-rtti', '-fsanitize=undefined',
                    '-fno-sanitize-recover=all', '-DARDUINO_ARCH_ZEPHYR',
                    '-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS', '-I', str(FIXTURE),
                    '-isystem', str(ROOT / 'host/third_party')]
        cls.main = cls.stage / 'main.o'
        freeze = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in FIXTURE.rglob('*') if p.is_file()}
        receipt_path = ROOT / 'state/analysis/P2_qtr_native_raw/author'
        receipt_path.mkdir(parents=True,exist_ok=True)
        (receipt_path/f'freeze_{time.time_ns()}.json').write_text(json.dumps(freeze,indent=2)+'\n')
        cls.command([*cls.base, '-c', str(FIXTURE / 'test_main.cc'), '-o', str(cls.main)])

    @classmethod
    def receipt(cls, argv, result):
        folder = os.environ.get('SUMO_NATIVE_RECEIPT_DIR')
        if not folder:
            folder = ROOT / 'state/analysis/P2_qtr_native_raw/author'
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        native_source = next((Path(x) for x in argv if str(x).endswith('/hal/line_qtr.cpp')), None)
        manifest = cls.binary_manifests.get(str(argv[0]))
        if native_source is not None:
            manifest = {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in {
                'production': native_source, 'header': native_source.with_suffix('.h'),
                'config': native_source.parent.parent / 'config.h'}.items()}
        staged = next((Path(x).parent.parent for x in argv if str(x).endswith('/hal/line_qtr.cpp') or str(x).endswith('/hal/line_qtr_adapter.cpp')), None)
        if staged is not None:
            manifest = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in staged.rglob('*') if p.is_file()}
        payload = {'staged_source_manifest': manifest, 'argv': list(map(str, argv)), 'returncode': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr,
                   'capture': 'subprocess text=True; newline normalized',
                   'production_sha256': hashlib.sha256(next((Path(x) for x in argv if str(x).endswith('/hal/line_qtr.cpp')), ROOT / 'src/hal/line_qtr.cpp').read_bytes()).hexdigest(),
                   'public_header_sha256': hashlib.sha256((ROOT / 'src/hal/line_qtr.h').read_bytes()).hexdigest(),
                   'config_sha256': hashlib.sha256((ROOT / 'src/config.h').read_bytes()).hexdigest()}
        (path / ('native_qtr_' + str(time.time_ns()) + '.json')).write_text(
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
        for name in ('line_qtr.cpp', 'line_qtr.h'):
            shutil.copyfile(ROOT / 'src/hal' / name, source / 'hal' / name)
        shutil.copyfile(ROOT / 'src/config.h', source / 'config.h')
        if edits:
            config = (source / 'config.h').read_text()
            for name, value in edits.items():
                config, n = re.subn(r'(\b' + re.escape(name) + r'\s*=\s*)[^;]+;', r'\g<1>' + value + ';', config)
                if n != 1:
                    raise AssertionError('Fixture could not select config name: ' + name)
            (source / 'config.h').write_text(config)
        binary = slot / 'native-qtr'
        argv = [*cls.base, '-I', str(source), *definitions, str(FIXTURE / case),
                str(FIXTURE / 'native_fixture.cc'), str(FIXTURE / 'isolation.cc'), str(source / 'hal/line_qtr.cpp'), str(cls.main),
                '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
        if probe:
            shutil.copytree(ROOT / 'src/core', source / 'core')
            for header in (ROOT / 'src/hal').glob('*.h'):
                shutil.copyfile(header, source / 'hal' / header.name)
            shutil.copyfile(ROOT / 'src/hal/line_qtr_adapter.cpp', source / 'hal/line_qtr_adapter.cpp')
            argv += [str(source / 'hal/line_qtr_adapter.cpp'), *map(str,sorted((source / 'core').glob('*.cpp')))]
            sketch = slot / 'qtr_sketch.cpp'
            shutil.copyfile(ROOT / 'bench/p2_qtr_native_compile/p2_qtr_native_compile.ino', sketch)
            argv += ['-I', str(ROOT / 'bench/p2_qtr_native_compile/src'),
                     '-I', str(ROOT / 'bench/p2_qtr_native_compile'),
                     str(ROOT / 'bench/p2_qtr_native_compile/src/qtr_native_probe.cpp'), str(sketch)]
        cls.command([*argv, '-o', str(binary)])
        cls.binary_manifests[str(binary)] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()}
        return binary

    def execute(self, binary):
        result = self.command([str(binary), '--no-colors'], timeout=35)
        self.assertIn('Status: SUCCESS!', result.stdout)
        print(' | '.join(line for line in result.stdout.splitlines()
                         if 'test cases:' in line or 'assertions:' in line), flush=True)

    def test_b2_isolation_propagates_child_assertions_and_crashes(self):
        binary = self.variant(case="isolation_selftest.cc")
        for name in ("*assertion*", "*signal*"):
            result = self.command([str(binary), "--no-colors", "--test-case=" + name], expected_returncode=1)
            self.assertIn("Status: FAILURE!", result.stdout)

    def test_b2_native_contract(self):
        self.execute(self.variant())

    def test_b2_fault_and_timing_boundaries(self):
        self.execute(self.variant(case='boundaries.cc'))

    def test_b2_invalid_metadata(self):
        for kind in range(1, 6):
            with self.subTest(kind=kind):
                self.execute(self.variant(definitions=(f'-DNATIVE_BAD_MAP={kind}',), case='metadata_cases.cc'))
        for index in (3,5,6,9,10,11,12,13,14,16,17,18,19):
            with self.subTest(alias=index):
                self.execute(self.variant(definitions=('-DNATIVE_BAD_MAP=6',f'-DNATIVE_ALIAS_INDEX={index}'),case='metadata_cases.cc'))
        self.execute(self.variant(definitions=('-DNATIVE_BAD_MAP=7',),case='metadata_cases.cc'))
        for size in (8,19):
            self.execute(self.variant(definitions=(f'-DNATIVE_TABLE_SIZE={size}',),case='metadata_cases.cc'))
        self.execute(self.variant(definitions=('-DNATIVE_GPIOA_ADDRESS=0x42020400UL',),case='metadata_cases.cc'))

    def test_b2_invalid_config(self):
        for name,value in [('QTR_CHARGE_US','0U'),('QTR_TIMEOUT_US','0U'),('QTR_QUANTIZATION_US','0U'),('QTR_START_PERIOD_US','0U'),('QTR_FRAME_MAX_US','0U'),('QTR_CALL_MAX_US','0U'),('QTR_CLEANUP_MAX_US','0U'),('QTR_CHARGE_MAX_US','0U'),('QTR_MAX_ADVANCES','0U'),('QTR_CALL_MAX_US','0x80000000U'),('QTR_FRAME_MAX_US','0x80000000U')]:
            with self.subTest(name=name,value=value):
                self.execute(self.variant(case='metadata_cases.cc',edits={name:value}))

    def test_b2_adapter_and_controller_contract(self):
        self.run_core_cases(False)

    def test_b2_adapter_and_controller_sanitized(self):
        self.run_core_cases(True)

    def test_b2_confirmation_count_three(self):
        self.run_core_cases(False, 3)

    def run_core_cases(self, sanitize, confirmations=None):
        slot=self.stage/(('core-sanitized' if sanitize else 'core-normal')+str(confirmations or ''))
        shutil.copytree(ROOT/'src/core',slot/'src/core')
        (slot/'src/hal').mkdir()
        for header in (ROOT/'src/hal').glob('*.h'):
            shutil.copyfile(header,slot/'src/hal'/header.name)
        shutil.copyfile(ROOT/'src/hal/line_qtr_adapter.cpp',slot/'src/hal/line_qtr_adapter.cpp')
        shutil.copyfile(ROOT/'src/config.h',slot/'src/config.h')
        if confirmations is not None:
            config_file=slot/'src/config.h'
            config_file.write_text(re.sub(r'(QTR_CONFIRM_TICKS\s*=\s*)[^;]+;',r'\g<1>'+str(confirmations)+'U;',config_file.read_text()))
        (slot/'tests').mkdir()
        for name in ('test_qtr_adapter.cpp','test_qtr_integration.cpp','robot_scenario.h'):
            shutil.copyfile(ROOT/'tests'/name,slot/'tests'/name)
        binary=slot/'core'
        options=['-fsanitize=address,undefined','-fno-omit-frame-pointer'] if sanitize else []
        core_flags=[flag for flag in self.base if flag!='-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS']
        self.command([*core_flags,'-DDOCTEST_CONFIG_NO_EXCEPTIONS',*options,'-I',str(slot/'src'),str(slot/'tests/test_qtr_adapter.cpp'),str(slot/'tests/test_qtr_integration.cpp'),str(self.main),str(slot/'src/hal/line_qtr_adapter.cpp'),*map(str,sorted((slot/'src/core').glob('*.cpp'))),'-o',str(binary)])
        self.binary_manifests[str(binary)]={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in slot.rglob("*") if p.is_file() and p!=binary}
        if confirmations is None:
            self.execute(binary)
        else:
            result=self.command([str(binary),"--no-colors","--test-case=*configurable confirmation*"])
            self.assertIn("Status: SUCCESS!",result.stdout)

    def test_b2_native_adapter_robot_pipeline(self):
        self.execute(self.variant(case="pipeline.cc",probe=True))

    def test_b2_probe_startup_and_10000_loops_are_inert(self):
        for allowed in (0, 1):
            with self.subTest(allowed=allowed):
                self.execute(self.variant(definitions=(f'-DMATCH={allowed}', f'-DMOTORS_ALLOWED={allowed}'), case='probe_cases.cc', probe=True))

    def test_b2_probe_all_upload_modes_refuse_before_transport_lookup(self):
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
                        require_transport=stack.enter_context(mock.patch.object(module,'require_transport'))
                        with self.assertRaises(ValueError) as caught:
                            module.flash(SimpleNamespace(sketch='bench/p2_qtr_native_compile', match=match,
                                                         startup=startup, compile_only=False))
                        target.assert_not_called()
                        remote.assert_not_called()
                        require_transport.assert_not_called()
                        folder=ROOT/'state/analysis/P2_qtr_native_raw/author'
                        payload={'transport':transport,'match':match,'startup':startup,'error':str(caught.exception),'target_calls':target.call_count,'remote_calls':remote.call_count,'require_transport_calls':require_transport.call_count,'board_tool_sha256':hashlib.sha256((ROOT/'tools/board_tool.py').read_bytes()).hexdigest()}
                        (folder/f'upload_refusal_{time.time_ns()}.json').write_text(json.dumps(payload,indent=2)+'\n')

if __name__ == '__main__':
    unittest.main(verbosity=2)
