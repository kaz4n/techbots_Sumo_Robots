# Tests D198 remote owners using all35 frozen D193 artifact/metadata assertions.
# Uses the independent caller-oracle projection table, never shared module aliases.
# Python -B controlled host fixtures only; no actual compiler or board dispatch.
import hashlib
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = 'tests/tooling/test_motor_settle_compile.py'
SUPPORT_SHA = '3093f6dfa45a20d6f5bb05b8f157a90ae4acc9a72bef41e7913e49bfc53cd5e6'


def support():
    raw = (ROOT / SUPPORT).read_bytes()
    if hashlib.sha256(raw).hexdigest() != SUPPORT_SHA:
        raise AssertionError('Frozen independent caller oracle changed')
    module = types.ModuleType('_d198_private_test_support')
    module.__file__ = str(ROOT / SUPPORT)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def additional_cases(fixture):
    class NewRemoteOwnerTests(fixture.RemoteArtifactContract):
        def test_previous_d193_build_and_artifact_paths_are_refused_separately_and_together(self):
            previous = '/home/arduino/sumox26_codex_build/app-motor-observe-static01'
            changes = ({'build': previous + '/build'}, {'artifacts': previous + '/artifacts'},
                       {'build': previous + '/build', 'artifacts': previous + '/artifacts'})
            for fields in changes:
                with self.subTest(fields=fields), self.assertRaises((TypeError, ValueError)):
                    self.inspect(**fields)

        def test_new_owner_keeps_observer_project_and_existing_layout_status(self):
            result = self.inspect()
            self.assertEqual(result['schema'], 'app-motor-settle-static-artifacts-v1')
            self.assertEqual(result['layout']['project'], 'app_motor_observe.ino')
            self.assertEqual(result['layout']['status'], 'STATIC_APP_MOTOR_OBSERVE_LAYOUT_PACKAGE_PASS')
            self.assertEqual(set(result['files']),
                {'build/app_motor_observe.ino' + suffix for suffix in fixture.SUFFIXES} |
                {'artifacts/app_motor_observe.ino.bin-zsk.bin'})
            self.assertIsNone(result['first_error'])
            self.assertTrue(all(item['status'] == 'PASS' for item in result['postchecks']))

    return NewRemoteOwnerTests


def load_tests(loader, standard, pattern):
    if not sys.dont_write_bytecode:
        raise RuntimeError('D198 remote tests require Python -B')
    helper = support(); oracle = helper.private_oracle('remote')
    inherited = oracle.load_tests(loader, unittest.TestSuite(), pattern)
    if inherited.countTestCases() != 35:
        raise AssertionError('Expected all35 D193 remote/adapter assertions')
    launcher = helper.private_module(helper.checked(ROOT / helper.SUBJECT, *helper.SUBJECT_PIN),
                                      ROOT / helper.SUBJECT, '_d198_remote_delta_subject')
    case = additional_cases(oracle.remote_fixture(launcher))
    suite = unittest.TestSuite([standard, inherited])
    suite.addTests(case(name) for name in (
        'test_previous_d193_build_and_artifact_paths_are_refused_separately_and_together',
        'test_new_owner_keeps_observer_project_and_existing_layout_status'))
    if suite.countTestCases() != 37:
        raise AssertionError('Expected35 inherited plus2 new D198 remote methods')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
