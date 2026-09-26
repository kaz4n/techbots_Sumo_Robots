# Preserves all D198 remote/adapter methods with checked private metadata only.
# Adds explicit rejection of the consumed settle build and artifact owner.
# Frozen host fixtures retain every original platform skip and avoid board work.
import hashlib
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
PRIOR = 'tests/tooling/test_motor_settle_compile_remote.py'
PRIOR_PIN = (3412, 'b2da457db6da3d01412dd300d495f075a8631294c75627f66b91dc1ee9fbd2e7')
PRIOR_PROJECTED = (3410, 'd620e92092b65f500de3f6df28c72d6c79f591ed686968b99ebfb1b142535d8a')
PRIOR_REPLACEMENTS = (
    (b'tests/tooling/test_motor_settle_compile.py', b'tests/tooling/test_motor_const_compile.py', 1),
    (b'71371f9361ef20ae0a64feb156e10e24e22722b1b31d8d426816d69bd6db962a', b'647a98ea97438e67860a8bc9794cbd4685127f494c5e3d123bca73c8e2894129', 1),
    (b'app-motor-settle-static', b'app-motor-const-static', 1),
    (b'D198', b'D203', 3),
    (b'_d198_private_test_support', b'_d203_private_test_support', 1),
)


def prior():
    raw = (ROOT / PRIOR).read_bytes()
    if (len(raw), hashlib.sha256(raw).hexdigest()) != PRIOR_PIN:
        raise AssertionError('Frozen D198 remote oracle differs')
    for old, new, count in PRIOR_REPLACEMENTS:
        if raw.count(old) != count:
            raise AssertionError('Remote fixture metadata occurrence differs')
        raw = raw.replace(old, new)
    if (len(raw), hashlib.sha256(raw).hexdigest()) != PRIOR_PROJECTED:
        raise AssertionError('Exact private D198 remote oracle projection differs')
    module = types.ModuleType('_d203_private_d198_remote_oracle')
    module.__file__ = str(ROOT / PRIOR)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def additional_case(fixture):
    class ConsumedSettleOwner(fixture.RemoteArtifactContract):
        def test_consumed_d198_build_artifacts_and_combined_paths_are_refused(self):
            previous = '/home/arduino/sumox26_codex_build/app-motor-settle-static01'
            changes = ({'build': previous + '/build'}, {'artifacts': previous + '/artifacts'},
                       {'build': previous + '/build', 'artifacts': previous + '/artifacts'})
            for fields in changes:
                with self.subTest(fields=fields), self.assertRaises((TypeError, ValueError)):
                    self.inspect(**fields)
    return ConsumedSettleOwner


def load_tests(loader, standard, pattern):
    if not sys.dont_write_bytecode:
        raise RuntimeError('D203 remote tests require Python -B')
    inherited = prior()
    preserved = inherited.load_tests(loader, unittest.TestSuite(), pattern)
    if preserved.countTestCases() != 37:
        raise AssertionError('All 37 D198 remote and adapter methods must remain')
    helper = inherited.support(); oracle = helper.private_oracle('remote')
    launcher = helper.private_module(helper.checked(ROOT / helper.SUBJECT, *helper.SUBJECT_PIN),
                                     ROOT / helper.SUBJECT, '_d203_remote_delta_subject')
    case = additional_case(oracle.remote_fixture(launcher))
    suite = unittest.TestSuite([standard, preserved])
    suite.addTest(case('test_consumed_d198_build_artifacts_and_combined_paths_are_refused'))
    if suite.countTestCases() != 38:
        raise AssertionError('Expected 37 retained and one new remote method')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
