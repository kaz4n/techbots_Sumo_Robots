# Preserves all D198 compile assertions in checked private metadata projections.
# Adds D203 constant-metadata source and consumed-settle ownership coverage.
# Independent contract-only authoring; controlled host endpoints, never board work.
import builtins
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = 'tools/compile_motor_const.py'
SUBJECT_PIN = (7557, '957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247')
CONTRACT = 'state/analysis/P7_motor_const_compile_contract.md'
CONTRACT_PIN = (11305, '318a6267f29a5837d6afe7197d6f86d88230886f1dd8ea0bb1af0345a4c75174')
PRIOR = 'tests/tooling/test_motor_settle_compile.py'
PRIOR_PIN = (11340, '71371f9361ef20ae0a64feb156e10e24e22722b1b31d8d426816d69bd6db962a')
BASELINE = 'tools/compile_motor_settle_probe.py'
BASELINE_PIN = (7570, 'b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62')
MOTOR_SOURCE = 'src/hal/motor_port_unoq.cpp'
MOTOR_PIN = (19906, 'fdbc27d972a59a9c955b67b88072a03df3b90a4629e22fd7833ff5f09e0c8f8b')
PRIOR_PROJECTED = (11314, '6e891d61ad54675498b15dabb120db0c55361ea1412963d3f80967c16928b69a')
PRIOR_REPLACEMENTS = (
    (b'tools/compile_motor_settle_probe.py', b'tools/compile_motor_const.py', 2),
    (b'P7_motor_settle_compile_contract.md', b'P7_motor_const_compile_contract.md', 2),
    (b'P7_motor_settle_compile_raw', b'P7_motor_const_compile_raw', 2),
    (b'app-motor-settle-static', b'app-motor-const-static', 5),
    (b'_sumox_d198_settle_compile', b'_sumox_d203_const_compile', 2),
    (b'D198', b'D203', 4),
    (b'7570', b'7557', 1),
    (b'b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62', b'957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247', 1),
    (b'c0b352810c41c8b3744acdd1c15bc4b21ecb76bc15d76d4fedea4fdde37dc756', b'318a6267f29a5837d6afe7197d6f86d88230886f1dd8ea0bb1af0345a4c75174', 1),
    (b'9a9d8df4130369eb4a31a348b76ddd7c2b3ca63c1e448250cc7d60dfc1d3158c', b'bda40e969dc48d4194f1c391c013cf0853e1fb39dee780a94f4754412d59f41a', 1),
    (b'dc359de37aab994e5dfbbadda1997235213da4e50c7f19f44141df18f2df7160', b'914d4d11057c8982154fbcd80fbea485977cf4952fad045625ca88271052040a', 1),
    (b'29889', b'29874', 1),
    (b'6895', b'6893', 1),
    (b"REMOTE.replace('settle', 'fault')", b"REMOTE.replace('const', 'fault')", 1),
    (b'29742', b'29717', 1),
    (b'dfe165aecd80c4a30e0047ec4c10b175a1290b6cb2119c3d982d51ee82e560fa', b'e4c9c37b7717a7347533e947894a5289733c15c518444778bb4953a5971d14ba', 1),
    (b'8785', b'8775', 1),
    (b'9089aebea6be747ecadfd6c79e4d7de8754c596ded163638f7ec09d7c5a2fd46', b'58b773b4d35c6e7c8971fee5ab9916a83e4cb00a0abad3c325226076ab1ef748', 1),
    (b'45463', b'45450', 1),
    (b'9b5e5e998f6d0222edb227095642c65f71f2baffb47005db4fb7ca41e56f2981', b'61419076917fe2b0fc877d68ece2a299d29d906bd65eec3c75bf9b45446c875c', 1),
    (b'18340', b'18338', 1),
    (b'da85976fd1abddbc3032aefb2ca5ebb630125730fc6008698ea3706bf6dda6ed', b'b4af110de1947141108479fd5fd72d56b68b3631cb26683da9fad4fa8549df71', 1),
)
LAUNCHER_REPLACEMENTS = (
    (b'D198', b'D203', 1),
    (b'tools/compile_motor_settle_probe.py', b'tools/compile_motor_const.py', 1),
    (b'P7_motor_settle_compile_contract.md', b'P7_motor_const_compile_contract.md', 1),
    (b'P7_motor_settle_compile_raw', b'P7_motor_const_compile_raw', 1),
    (b'app-motor-settle-static', b'app-motor-const-static', 3),
    (b'_sumox_d198_settle_compile', b'_sumox_d203_const_compile', 1),
    (b'29889', b'29874', 1),
    (b'9a9d8df4130369eb4a31a348b76ddd7c2b3ca63c1e448250cc7d60dfc1d3158c', b'bda40e969dc48d4194f1c391c013cf0853e1fb39dee780a94f4754412d59f41a', 1),
    (b'6895', b'6893', 1),
    (b'dc359de37aab994e5dfbbadda1997235213da4e50c7f19f44141df18f2df7160', b'914d4d11057c8982154fbcd80fbea485977cf4952fad045625ca88271052040a', 1),
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, size, digest):
    raw = path.read_bytes()
    if (len(raw), sha(raw)) != (size, digest):
        raise AssertionError('Frozen D203 input differs: ' + str(path))
    return raw


def project(raw, replacements):
    for old, new, count in replacements:
        if raw.count(old) != count:
            raise AssertionError('Independent fixture occurrence differs: ' + repr(old))
        raw = raw.replace(old, new)
    return raw


def private_module(raw, path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def prior():
    raw = project(checked(ROOT / PRIOR, *PRIOR_PIN), PRIOR_REPLACEMENTS)
    if (len(raw), sha(raw)) != PRIOR_PROJECTED:
        raise AssertionError('Exact private D198 oracle projection differs')
    return private_module(raw, ROOT / PRIOR, '_d203_private_d198_caller_oracle')


def private_oracle(kind):
    return prior().private_oracle(kind)


class DerivativeContractTests(unittest.TestCase):
    def test_exact_d198_derivative_keeps_all_unsubstituted_bytes_and_runtime_dependencies(self):
        original = checked(ROOT / BASELINE, *BASELINE_PIN)
        expected = project(original, LAUNCHER_REPLACEMENTS)
        actual = checked(ROOT / SUBJECT, *SUBJECT_PIN)
        self.assertEqual(actual, expected)
        checked(ROOT / CONTRACT, *CONTRACT_PIN)
        launcher = private_module(actual, ROOT / SUBJECT, '_d203_exact_identity')
        caller = launcher.load_caller(root=ROOT)
        self.assertEqual(caller.__name__, '_sumox_d203_const_compile')
        for name in (BASELINE, 'state/analysis/P7_motor_settle_compile_contract.md'):
            self.assertNotIn(name, caller.HARD_PINS)
            self.assertNotIn(name, caller.REQUIRED)
        self.assertFalse(any(value is caller for value in sys.modules.values()))


def additional_owner_cases(oracle):
    class ConstOwnerTests(oracle.CallerFixture):
        def test_current_motor_cpp_exact_bytes_mapping_digest_drift_refusal_and_staging(self):
            expected = checked(ROOT / MOTOR_SOURCE, *MOTOR_PIN)
            owner = self.owner(); owner.local()
            self.assertIn(MOTOR_SOURCE, owner.source_names())
            self.assertEqual(owner.code[MOTOR_SOURCE], expected)
            self.assertEqual(owner.expected_stage[MOTOR_SOURCE], self.files[MOTOR_SOURCE])
            self.assertEqual(owner.source_sha256, self.source)
            path = self.root / MOTOR_SOURCE
            path.write_bytes(expected + b'\n// isolated D203 source drift\n')
            self.reject(self.owner().check)
            self.manifest(files=dict(self.files, **{MOTOR_SOURCE: sha(path.read_bytes())}))
            self.reject(self.owner().check)
            path.write_bytes(expected); self.manifest()
            owner = self.controlled(self.owner()); owner.local()
            owner.prepare(); owner.claim(); owner.stage()
            self.assertEqual((owner.stage_path / MOTOR_SOURCE).read_bytes(), expected)
            self.assertEqual(owner.source_sha256, self.source)
            self.assertEqual(owner.stage_path.name, 'app_motor_observe')

        def test_consumed_d198_local_output_and_stage_survive_new_check_unchanged(self):
            names = ('state/analysis/P7_motor_settle_compile_raw/native_static01/retained',
                     'build/stage/app-motor-settle-static01/retained')
            for name in names:
                path = self.root / name; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'consumed D198 evidence: ' + name.encode())
            before = oracle.file_set(self.root)
            report = self.owner().check()
            self.assertEqual(before, oracle.file_set(self.root))
            self.assertEqual(report['schema'], 'app-motor-const-static-check-v1')
            self.assertEqual(report['remote'], '/home/arduino/sumox26_codex_build/app-motor-const-static01')
            self.assertEqual(Path(report['output']), self.root / 'state/analysis/P7_motor_const_compile_raw/native_static01')
            self.assertEqual(Path(report['stage']), self.root / 'build/stage/app-motor-const-static01/app_motor_observe')

        def test_d198_manifest_and_artifact_ownership_cannot_substitute_for_d203(self):
            self.manifest(schema='app-motor-settle-static-inputs-v1')
            self.reject(self.owner().check)
            self.manifest(); owner = self.owner(); owner.local()
            for key, value in (
                    ('schema', 'app-motor-settle-static-artifacts-v1'),
                    ('build_path', '/home/arduino/sumox26_codex_build/app-motor-settle-static01/build'),
                    ('artifacts_path', '/home/arduino/sumox26_codex_build/app-motor-settle-static01/artifacts')):
                reply = self.remote_fixture.synthetic_reply(); reply[key] = value
                with self.subTest(key=key):
                    self.reject(lambda: owner.validate_artifact_reply(json.dumps(reply)))
            self.assertEqual(owner.validate_artifact_reply(json.dumps(
                self.remote_fixture.synthetic_reply()))['schema'], 'app-motor-const-static-artifacts-v1')

    return ConstOwnerTests


def load_tests(loader, standard, pattern):
    if not sys.dont_write_bytecode:
        raise RuntimeError('D203 independent tests require Python -B')
    inherited = prior()
    preserved = inherited.load_tests(loader, loader.loadTestsFromTestCase(inherited.DerivativeIdentityTests), pattern)
    if preserved.countTestCases() != 65:
        raise AssertionError('All 65 D198 caller methods must remain')
    suite = unittest.TestSuite([standard, preserved])
    fixture = inherited.private_oracle('caller').inherited_oracle()
    suite.addTests(loader.loadTestsFromTestCase(additional_owner_cases(fixture)))
    if suite.countTestCases() != 69:
        raise AssertionError('Expected 65 retained and four new caller methods')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
