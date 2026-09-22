# Exercises the D-063 default-only inert ADC upload boundary with fake transports.
# Keeps compile-only, source identity and failed-build checks distinct from board evidence.
# This coordinator-authored extension reuses existing independent SSH/ADB fixtures.
import itertools
import shutil
import unittest

import test_tools as ssh_fixture
import test_adb_transport as adb_fixture


class AdcUploadTests(unittest.TestCase):
    def fixture(self, transport):
        kind = (ssh_fixture.ToolContractTests if transport == 'ssh'
                else adb_fixture.AdbTransportTests)
        fixture = kind(methodName='runTest')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.use_reviewed_sources()
        shutil.copytree(ssh_fixture.PROJECT / 'bench/p0_adc',
                        fixture.root / 'bench/p0_adc')
        return fixture

    def test_default_upload_follows_compile_and_uses_same_inert_artifact(self):
        for transport in ('ssh', 'adb'):
            with self.subTest(transport=transport):
                fixture = self.fixture(transport)
                result = fixture.run_tool('bench/p0_adc')
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                compile_args, = fixture.commands('compile')
                upload_args, = fixture.commands('upload')
                self.assertIn('compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0',
                              compile_args)
                self.assertIn('compiler.c.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0',
                              compile_args)
                self.assertEqual(compile_args[compile_args.index('--output-dir') + 1],
                                 upload_args[upload_args.index('--input-dir') + 1])
                self.assertEqual('arduino:zephyr:unoq',
                                 upload_args[upload_args.index('--fqbn') + 1])
                calls = [event['args'][0] for event in fixture.events
                         if event['kind'] == 'arduino']
                self.assertLess(calls.index('compile'), calls.index('upload'))

    def test_compile_only_all_orders_never_uploads_even_with_match(self):
        for transport in ('ssh', 'adb'):
            fixture = self.fixture(transport)
            for flags in ((), ('--match',), ('--startup', 'immediate')):
                orders = (list(itertools.permutations(('bench/p0_adc', '--compile-only', *flags)))
                          if '--startup' not in flags else
                          [('bench/p0_adc', '--compile-only', *flags)])
                for args in orders:
                    with self.subTest(transport=transport, args=args):
                        result = fixture.run_tool(*args)
                        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                        self.assertEqual([], fixture.commands('upload'))

    def test_unreviewed_immediate_or_motor_upload_rejected_before_transport(self):
        for transport in ('ssh', 'adb'):
            fixture = self.fixture(transport)
            for flags in (('--match',), ('--startup', 'immediate')):
                result = fixture.run_tool('bench/p0_adc', *flags)
                self.assertNotEqual(0, result.returncode)
                self.assertEqual([], fixture.events)

    def test_changed_adc_source_rejected_before_transport(self):
        for transport in ('ssh', 'adb'):
            fixture = self.fixture(transport)
            fixture.write('bench/p0_adc/src/extra.cpp', 'int changed_source;\n')
            result = fixture.run_tool('bench/p0_adc')
            self.assertNotEqual(0, result.returncode)
            self.assertEqual([], fixture.events)

    def test_adc_compile_failure_prevents_upload(self):
        for transport in ('ssh', 'adb'):
            fixture = self.fixture(transport)
            result = fixture.run_tool('bench/p0_adc', changes={'FAKE_FAIL': 'compile'})
            self.assertNotEqual(0, result.returncode)
            self.assertEqual([], fixture.commands('upload'))


if __name__ == '__main__':
    unittest.main()
