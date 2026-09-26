# Builds only the changed recorder session paths and their independent fixtures.
# Compiler processes run serially; generated executables live in bounded host scratch.
# Uses the supplied v1 session to validate full synthetic output without board I/O.
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
SESSION = 0xF123456789ABCDEF


@unittest.skipUnless(os.name == 'posix', 'UART register fixture requires Linux')
class RecorderSessionHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='sumox-session-')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.stage = Path(cls.temporary.name)
        cls.commands = []

    @classmethod
    def command(cls, args, **kwargs):
        args = list(map(str, args))
        result = subprocess.run(args, capture_output=True, text=True, timeout=240, **kwargs)
        cls.commands.append(dict(argv=args, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr))
        evidence = os.environ.get('SUMOX_SESSION_COMMANDS')
        if evidence:
            Path(evidence).write_text(json.dumps(cls.commands, indent=2) + '\n')
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        return result

    @staticmethod
    def flags():
        return ['g++', '-std=c++17', '-O1', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                '-fno-exceptions', '-fno-rtti', '-DMATCH=0', '-DMOTORS_ALLOWED=0',
                '-I', ROOT/'src', '-I', ROOT, '-isystem', ROOT/'host/third_party']

    def test_real_pipeline_normal_and_sanitized_supplied_session_round_trip(self):
        main = self.stage / 'main.cc'
        main.write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
        sources = [*sorted((ROOT/'src/core').glob('*.cpp')),
                   *sorted((ROOT/'bench/recorder/src').glob('*.cpp'))]
        sources += [ROOT/'src/hal'/name for name in
                    ('motors.cpp','recorder_frames.cpp','recorder.cpp','recorder_csv.cpp','recorder_dump.cpp')]
        sources += [ROOT/'src/app/transaction.cpp', ROOT/'src/app/transaction_service.cpp',
                    ROOT/'tests/test_recorder_session.cpp', main]
        for name, sanitizers in (('normal', []), ('sanitized',
                ['-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie'])):
            with self.subTest(profile=name):
                binary = self.stage/name
                self.command([*self.flags(), '-DDOCTEST_CONFIG_NO_EXCEPTIONS', *sanitizers, *sources, '-o', binary])
                wire = self.stage/(name+'.wire')
                result = self.command([binary, '--no-colors'], env=dict(os.environ, SUMOX_SESSION_WIRE=str(wire)))
                self.assertIn('Status: SUCCESS!', result.stdout)
                module = importlib.import_module('dump_match')
                data = wire.read_bytes()
                parser = module.Parser(expected_session=SESSION)
                for offset in range(0,len(data),257): parser.feed(data[offset:offset+257])
                capture = parser.finish()
                self.assertEqual((capture.session,capture.epoch,capture.frame_count,capture.event_count),
                                 (SESSION,69,5001,8))
                self.assertEqual(capture.origin,1)
                destination = module.save_capture([data], self.stage/(name+'_capture'), expected_session=SESSION)
                evidence = json.loads((destination/'capture.json').read_text())
                self.assertEqual(evidence['expected_session'],SESSION)
                self.assertFalse(evidence['hardware_acceptance'])
                with self.assertRaises(module.CaptureError):
                    stale = module.Parser(expected_session=SESSION-1)
                    stale.feed(data)
                if name == 'normal': original = data
                else: self.assertEqual(data, original)

    def test_native_opt_in_retains_setup_readiness_fifo_ownership_poison_and_timeout(self):
        fixture = ROOT/'tests/fixtures/dump_uart_fifo'
        binary = self.stage/'native'
        flags = [*self.flags(), '-DARDUINO_ARCH_ZEPHYR', '-DCONFIG_UART_INTERRUPT_DRIVEN',
                 '-I', ROOT/'tests/fixtures/dump_uart_native']
        self.command([*flags, fixture/'hardware.cc', fixture/'session_cases.cc',
                      ROOT/'src/hal/dump_uart_unoq.cpp', '-o', binary])
        for bits in range(16):
            for mode in (0,1,2,255):
                for supplied in (0,1):
                    with self.subTest(bits=bits,mode=mode,supplied=supplied):
                        self.command([binary,'admission',bits,mode,supplied])
        for fault in range(8):
            with self.subTest(fault=fault): self.command([binary,'guard',fault])


if __name__ == '__main__':
    unittest.main()
