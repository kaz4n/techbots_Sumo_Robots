# Tests D198 fixed identities against the frozen contract and prior byte pins.
# Retains all59 D193 caller assertions in privately projected fixture modules.
# Freeze before execution; synthetic endpoints never grant compiler or board work.
import builtins
import hashlib
import json
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = 'tools/compile_motor_settle_probe.py'
SUBJECT_PIN = (7570, 'b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62')
CONTRACT = 'state/analysis/P7_motor_settle_compile_contract.md'
CONTRACT_SHA = 'c0b352810c41c8b3744acdd1c15bc4b21ecb76bc15d76d4fedea4fdde37dc756'
OLD_LAUNCHER = 'tools/compile_app_motor_observe.py'
OLD_LAUNCHER_PIN = (7583, '70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827')
ORACLES = {
    'caller': ('tests/tooling/test_app_motor_observe_compile.py', 29767,
               'ae42938cace40745068421bf6e8e813295b12c16b376c93bd00b019b311b724d'),
    'remote': ('tests/tooling/test_app_motor_observe_compile_remote.py', 8787,
               '897ae6e468aaa619ff72fa03532278458a250cfc440add52fd8eff180d587413'),
}
CALLER_SHA = '9a9d8df4130369eb4a31a348b76ddd7c2b3ca63c1e448250cc7d60dfc1d3158c'
REMOTE_SHA = 'dc359de37aab994e5dfbbadda1997235213da4e50c7f19f44141df18f2df7160'
IDENTITIES = (
    (b'tools/compile_app_motor_observe.py', b'tools/compile_motor_settle_probe.py'),
    (b'P7_app_motor_observe_compile_contract.md', b'P7_motor_settle_compile_contract.md'),
    (b'P7_app_motor_observe_compile_raw', b'P7_motor_settle_compile_raw'),
    (b'app-motor-observe-static', b'app-motor-settle-static'),
)
DERIVED = (
    (b'29904', b'29889'),
    (b'830299e516c9221db35f81e2b01100cd5f0444cd7a78ca6148048805d2078884', CALLER_SHA.encode()),
    (b'6897', b'6895'),
    (b'f7886c869980afc969082b66ce8d3fc35801fe7c11134b406af158f06049160c', REMOTE_SHA.encode()),
)
ORACLE_COUNTS = {'caller': (2, 2, 2, 5, 1, 1, 1, 1, 2),
                 'remote': (1, 0, 0, 2, 0, 0, 1, 1, 1)}
ORACLE_PROJECTED = {
    'caller': (29742, 'dfe165aecd80c4a30e0047ec4c10b175a1290b6cb2119c3d982d51ee82e560fa'),
    'remote': (8785, '9089aebea6be747ecadfd6c79e4d7de8754c596ded163638f7ec09d7c5a2fd46'),
}
FIXTURES = {
    '53d547ad4c9c4df9e55313014e89ab731fddcf8edde6983c5cb535d253f73e96':
        ((1, 1, 1, 4), 45463, '9b5e5e998f6d0222edb227095642c65f71f2baffb47005db4fb7ca41e56f2981'),
    'db0ff0284eb7c528a852f39a57fcb668c72c098543b6d6813298fc2dfeddd80b':
        ((0, 0, 0, 2), 18340, 'da85976fd1abddbc3032aefb2ca5ebb630125730fc6008698ea3706bf6dda6ed'),
    'e6d52ec6b0d72e893511793e9d92003092499280454093c9b6622d0e18547d5c':
        ((0, 0, 0, 0), 36723, 'e7e6f70b9deed177a3afedc35d30c8595501a4987d57dbaa86f9380c7792e592'),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, size, digest):
    raw = path.read_bytes()
    if len(raw) != size or sha(raw) != digest:
        raise AssertionError('Frozen input differs: ' + str(path))
    return raw


def replacements(raw, pairs, counts):
    if len(pairs) != len(counts):
        raise AssertionError('Incomplete independent substitution table')
    for (before, after), count in zip(pairs, counts):
        if raw.count(before) != count:
            raise AssertionError('Independent occurrence mismatch: ' + repr(before))
        raw = raw.replace(before, after)
    return raw


def private_module(raw, path, name):
    result = types.ModuleType(name)
    result.__file__ = str(path)
    result.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), result.__dict__)
    return result


def expected_launcher(raw):
    if (len(raw), sha(raw)) != OLD_LAUNCHER_PIN:
        raise AssertionError('D193 launcher pin differs')
    pairs = ((b'D193', b'D198'), *IDENTITIES,
             (b'_sumox_d193_observe_compile', b'_sumox_d198_settle_compile'), *DERIVED)
    raw = replacements(raw, pairs, (1, 1, 1, 1, 3, 1, 1, 1, 1, 1))
    if (len(raw), sha(raw)) != SUBJECT_PIN:
        raise AssertionError('Contract derivative differs')
    return raw


def private_oracle(kind):
    name, size, digest = ORACLES[kind]
    raw = checked(ROOT / name, size, digest)
    pairs = (*IDENTITIES, *DERIVED,
             (b"REMOTE.replace('observe', 'fault')", b"REMOTE.replace('settle', 'fault')"))
    raw = replacements(raw, pairs, ORACLE_COUNTS[kind])
    if (len(raw), sha(raw)) != ORACLE_PROJECTED[kind]:
        raise AssertionError('Private D193 oracle projection differs')
    oracle = private_module(raw, ROOT / name, '_d198_private_' + kind + '_oracle')
    function = 'metadata_oracle' if kind == 'caller' else 'fixture_metadata'
    inherited = getattr(oracle, function)

    def metadata(raw):
        counts, size, digest = FIXTURES[sha(raw)]
        projected = replacements(inherited(raw), IDENTITIES, counts)
        if (len(projected), sha(projected)) != (size, digest):
            raise AssertionError('Private historical fixture projection differs')
        return projected

    setattr(oracle, function, metadata)
    return oracle


class DerivativeIdentityTests(unittest.TestCase):
    def test_exact_launcher_is_only_the_ten_frozen_metadata_substitutions(self):
        original = checked(ROOT / OLD_LAUNCHER, *OLD_LAUNCHER_PIN)
        self.assertEqual(checked(ROOT / SUBJECT, *SUBJECT_PIN), expected_launcher(original))
        self.assertEqual(sha((ROOT / CONTRACT).read_bytes()), CONTRACT_SHA)

    def test_private_compile_identity_and_adapter_remain_fixed(self):
        launcher = private_module(checked(ROOT / SUBJECT, *SUBJECT_PIN), ROOT / SUBJECT, '_d198_identity')
        old = private_module(checked(ROOT / OLD_LAUNCHER, *OLD_LAUNCHER_PIN),
                             ROOT / OLD_LAUNCHER, '_d193_identity')
        caller = launcher.load_caller(root=ROOT)
        self.assertEqual(caller.__name__, '_sumox_d198_settle_compile')
        self.assertEqual(caller.PROJECT, 'app_motor_observe.ino')
        self.assertEqual(caller.FQBN, 'arduino:zephyr:unoq:link_mode=static')
        self.assertEqual(caller.FLAGS, '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1')
        self.assertEqual(caller.CALLER, SUBJECT)
        self.assertEqual(caller.CONTRACT, CONTRACT)
        self.assertNotIn(OLD_LAUNCHER, caller.REQUIRED)
        self.assertNotIn('state/analysis/P7_app_motor_observe_compile_contract.md', caller.REQUIRED)
        original_adapter = launcher.read_original('tools/app_motor_fault_static_policy.py', root=ROOT)
        self.assertEqual(launcher.project_adapter(original_adapter), old.project_adapter(original_adapter))
        self.assertFalse(any(value is caller for value in sys.modules.values()))


def new_owner_cases(oracle):
    class SettleOwnerTests(oracle.CallerFixture):
        def test_header_is_in_exact_inventory_mapping_source_digest_and_staged_bytes(self):
            name = 'src/hal/motor_settle_probe.h'
            owner = self.owner(); owner.local()
            self.assertIn(name, owner.source_names())
            self.assertEqual(owner.code[name], (ROOT / name).read_bytes())
            self.assertEqual(owner.expected_stage[name], self.files[name])
            self.assertEqual(owner.source_sha256, self.source)
            self.assertTrue(owner.sketch.endswith('/' + self.source + '/app_motor_observe'))
            owner.prepare()
            self.assertEqual((owner.stage_path / name).read_bytes(), owner.code[name])
            self.assertEqual(owner.stage_path.name, 'app_motor_observe')

        def test_header_omission_missing_file_and_byte_drift_refuse(self):
            name = 'src/hal/motor_settle_probe.h'; path = self.root / name
            original = path.read_bytes()
            omitted = dict(self.files); omitted.pop(name)
            self.manifest(files=omitted); self.reject(self.owner().check)
            self.manifest(); path.unlink(); self.reject(self.owner().check)
            path.write_bytes(original + b'\n// controlled drift\n')
            self.reject(self.owner().check)
            self.manifest(files=dict(self.files, **{name: sha(path.read_bytes())}))
            self.reject(self.owner().check)

        def test_consumed_d188_d193_local_owners_are_untouched_by_new_check(self):
            names = ('state/analysis/P7_app_motor_fault_compile_raw/native_static01/retained',
                     'state/analysis/P7_app_motor_observe_compile_raw/native_static01/retained',
                     'build/stage/app-motor-fault-static01/retained',
                     'build/stage/app-motor-observe-static01/retained')
            for name in names:
                path = self.root / name; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'consumed prior evidence: ' + name.encode())
            before = oracle.file_set(self.root)
            report = self.owner().check()
            self.assertEqual(before, oracle.file_set(self.root))
            self.assertEqual(report['schema'], 'app-motor-settle-static-check-v1')
            self.assertEqual(report['remote'], '/home/arduino/sumox26_codex_build/app-motor-settle-static01')
            self.assertEqual(Path(report['stage']), self.root / 'build/stage/app-motor-settle-static01/app_motor_observe')
            self.assertEqual(Path(report['output']), self.root / 'state/analysis/P7_motor_settle_compile_raw/native_static01')

        def test_both_historical_manifest_and_artifact_owner_identities_are_refused(self):
            for old in ('fault', 'observe'):
                self.manifest(schema='app-motor-' + old + '-static-inputs-v1')
                self.reject(self.owner().check)
            self.manifest(); owner = self.owner(); owner.local()
            for old in ('fault', 'observe'):
                for key, value in (
                        ('schema', 'app-motor-' + old + '-static-artifacts-v1'),
                        ('build_path', '/home/arduino/sumox26_codex_build/app-motor-' + old + '-static01/build'),
                        ('artifacts_path', '/home/arduino/sumox26_codex_build/app-motor-' + old + '-static01/artifacts')):
                    reply = self.remote_fixture.synthetic_reply(); reply[key] = value
                    with self.subTest(owner=old, key=key):
                        self.reject(lambda: owner.validate_artifact_reply(json.dumps(reply)))
            self.assertEqual(owner.validate_artifact_reply(json.dumps(
                self.remote_fixture.synthetic_reply()))['schema'], 'app-motor-settle-static-artifacts-v1')

    return SettleOwnerTests


def load_tests(loader, standard, pattern):
    if not sys.dont_write_bytecode:
        raise RuntimeError('D198 independent tests require Python -B')
    oracle = private_oracle('caller')
    inherited = oracle.load_tests(loader, loader.loadTestsFromTestCase(oracle.ProjectionContract), pattern)
    if inherited.countTestCases() != 59:
        raise AssertionError('Expected all59 unchanged D193 caller assertions')
    suite = unittest.TestSuite([standard, inherited])
    suite.addTests(loader.loadTestsFromTestCase(new_owner_cases(oracle.inherited_oracle())))
    if suite.countTestCases() != 65:
        raise AssertionError('Expected59 inherited plus6 new D198 caller methods')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
