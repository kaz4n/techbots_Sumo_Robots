# Retains all 25 D195 caller cases with checked D201 evidence metadata.
# Preserves the prior failed ABI receipt and excluded historical provenance.
# Adds exact caller derivation and the current 129-input/header admission check.
import copy
import hashlib
import json
from pathlib import Path
import types
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
PRIOR = 'tests/tooling/test_app_motor_observe_run.py'
PRIOR_SHA = '7af304d06b85de0f835856ecbd241d957c193b7d252c2849eea474e6043fbb9c'
SUPPORT = 'tests/tooling/test_motor_const_actions.py'
SUPPORT_SHA = '05a8c43509e7ba4b3cb0752214a7163f64718300bc310f2e9b5805151394a2ff'
CHANGES = (('P7_app_motor_observe', 'P7_motor_settle', 10), ('test_app_motor_observe', 'test_motor_settle', 4), ('app-motor-observe-3a08ddeb-run01', 'app-motor-settle-117cc0e7-run01', 2), ('app-motor-observe', 'app-motor-settle', 1), ('11357', '11343', 2), ('128', '129', 2), ('native_abi_static02', 'native_abi_static01', 10), ('abi02_actual_review', 'abi_actual_review', 1), ('compile_app_motor_observe', 'compile_motor_settle_probe', 1), ('103493975bccdcab094b412a5ba26cf125a6f294a9b5efac167660f6fda8a563', '448b05c2353af00fb3114c5f49acd64c18e8b9387e4c45fcff45a2fcc44abc49', 1), ('aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e', 'aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282', 1), ('70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827', 'b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62', 1), ('98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db', '577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0', 1), ("        ('app_motor_fault', 'app_motor_observe', 14),\n", "        ('app_motor_fault', 'app_motor_observe', 14),\n        ('P7_app_motor_observe', 'P7_motor_settle', 9),\n", 1), ("self.assertNotIn(COMPILED + 'native_abi_static01/result.json', self.subject.PROVENANCE)", "self.assertNotIn('state/analysis/P7_app_motor_observe_compile_raw/native_abi_static02/result.json', self.subject.PROVENANCE)", 1), ("ROOT / COMPILED / 'native_abi_static01/local_result.json').read_bytes()", "ROOT / 'state/analysis/P7_app_motor_observe_compile_raw/native_abi_static01/local_result.json').read_bytes()", 1))
_SUPPORT = _PROVIDER = None


def load_support():
    global _SUPPORT
    if _SUPPORT is None:
        raw = (ROOT / SUPPORT).read_bytes()
        if hashlib.sha256(raw).hexdigest() != SUPPORT_SHA:
            raise AssertionError('Action oracle changed')
        value = types.ModuleType('_d201_caller_action_support'); value.__file__ = str(ROOT / SUPPORT)
        exec(compile(raw, value.__file__, 'exec'), value.__dict__)
        _SUPPORT = value
    return _SUPPORT


def fixture_projection(raw):
    raw = load_support().load_support().replace(raw, CHANGES)
    if (len(raw), hashlib.sha256(raw).hexdigest()) != (11031, 'd3ab296290774a4bc9cf623e8fa6d7360b8fce6cea7159b6fd6c8ed378c42b4a'):
        raise AssertionError('Projected caller fixture changed')
    raw = load_support().load_support().replace(raw, (('P7_motor_settle', 'P7_motor_const', 11), ('test_motor_settle', 'test_motor_const', 4), ('app-motor-settle-117cc0e7-run01', 'app-motor-const-4bc3a2e6-run01', 2), ('app-motor-settle', 'app-motor-const', 1), ('11343', '11331', 2), ('compile_motor_settle_probe', 'compile_motor_const', 1), ('448b05c2353af00fb3114c5f49acd64c18e8b9387e4c45fcff45a2fcc44abc49', '05a8c43509e7ba4b3cb0752214a7163f64718300bc310f2e9b5805151394a2ff', 1), ('aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282', '1b847d96bb21fa72ed19138cb93f803b56b74224dffd7019dd930d99ff7bac95', 1), ('b98a5f54e2be122162e76074673190f52ef4218c766d517125b48127bb4b8b62', '957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247', 1), ('577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0', '51c60cd5ac87b823b84b2c7d993933690f0a3110e4d89c7cb958549fb5f111bc', 1), ('("\'adapter_bytes\': 10518", "\'adapter_bytes\': 11331", 1))', '("\'adapter_bytes\': 10518", "\'adapter_bytes\': 11331", 1),\n        (\'state/analysis/P7_motor_const_caller_contract.md\', \'state/analysis/P7_motor_const_run_contract.md\', 1),\n        (\'state/analysis/P7_motor_const_remote_contract.md\', \'state/analysis/P7_motor_const_run_raw/run_derivation01.json\', 1))', 1)))
    if (len(raw), hashlib.sha256(raw).hexdigest()) != (11248, '1ba880d2b0c29e1e7d38f243848ff4ec1b91be59a3b49645d62f86bc808a65af'):
        raise AssertionError('D207 projected fixture changed')
    return raw


def private_oracle():
    global _PROVIDER
    if _PROVIDER is None:
        support = load_support().load_support()
        raw = fixture_projection(support.checked(ROOT / PRIOR, PRIOR_SHA))
        value = types.ModuleType('_d201_private_caller_provider'); value.__file__ = str(ROOT / PRIOR)
        exec(compile(raw, value.__file__ + '<fixed D201 metadata>', 'exec'), value.__dict__)
        _PROVIDER = value
    return _PROVIDER


class CurrentCaller(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        provider = private_oracle(); provider.ObserverEvidence.setUpClass()
        cls.case_type = provider.ObserverEvidence
        cls.subject, cls.oracle = cls.case_type.subject, cls.case_type.oracle
        cls.manifest, cls.code = cls.case_type.manifest, cls.case_type.code

    def setUp(self):
        case = self.case_type('test_old_manifest_refused_before_projection_and_any_transport')
        case.setUp(); self.addCleanup(case.doCleanups)

    def test_exact_seventeen_metadata_changes_preserve_other_caller_source_bytes(self):
        support = load_support().load_support()
        spec = json.loads(support.checked(ROOT / support.BINDING, support.BINDING_SHA))['metadata_derivatives']['caller']
        self.assertEqual(len(spec['steps']), 15)
        raw = support.checked(ROOT / 'state/analysis/P7_motor_settle_run_raw/run.py', spec['input']['sha256'])
        self.assertEqual(len(raw), spec['input']['bytes'])
        expected = support.replace(raw, [(r['old'], r['new'], r['count']) for r in spec['steps']])
        actual = private_oracle().SUBJECT.read_bytes()
        self.assertEqual(actual, expected)
        self.assertEqual((len(actual), support.sha(actual)), (24862, spec['expected']['sha256']))

    def test_current_header_in_129_inputs_and_D193_manifest_rejected_before_mapping(self):
        provider = private_oracle(); support = load_support().load_support()
        self.assertEqual(len(self.manifest['files']), 129)
        self.assertIn('src/hal/motor_settle_probe.h', self.code)
        self.assertEqual(support.sha(self.code['src/hal/motor_settle_probe.h']),
                         '2eced554fce20ff938daf44866ee0bad6d99fa28e377af762bb0f037376b75a8')
        self.assertEqual(self.manifest['source_sha256'], support.SOURCE)
        old = ROOT / 'state/analysis/P7_app_motor_observe_compile_raw/inputs_static.json'
        old_raw = support.checked(old, 'aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e')
        self.assertEqual(len(json.loads(old_raw)['files']), 128)
        owner = self.subject.InertRun(self.oracle.HEAD, root=ROOT)
        owner.fixed_bytes = {provider.MANIFEST: old_raw}
        owner.expected_identity = {'boot_id': self.manifest['boot_id']}
        before = copy.deepcopy(owner.fixed_bytes)
        with mock.patch.object(self.subject.diagnostic.CompileDiagnostic, 'source_mapping') as mapping:
            with self.assertRaises(Exception): owner.load_source()
            mapping.assert_not_called()
        self.assertEqual(owner.fixed_bytes, before)


    def test_D201_manifest_is_refused_before_real_source_mapping(self):
        provider = private_oracle()
        old_raw = (ROOT / 'state/analysis/P7_motor_settle_compile_raw/inputs_static.json').read_bytes()
        self.assertEqual(hashlib.sha256(old_raw).hexdigest(),
            'aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282')
        owner = self.subject.InertRun(self.oracle.HEAD, root=ROOT)
        owner.fixed_bytes = {provider.MANIFEST: old_raw}
        owner.expected_identity = {'boot_id': self.manifest['boot_id']}
        before = copy.deepcopy(owner.fixed_bytes)
        with mock.patch.object(self.subject.diagnostic.CompileDiagnostic, 'source_mapping') as mapping:
            with self.assertRaises(Exception): owner.load_source()
            mapping.assert_not_called()
        self.assertEqual(owner.fixed_bytes, before)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Owned /dev/shm admission fixture required')
    def test_D201_artifacts_ABI_entry_source_and_consumed_owner_fail_real_admission(self):
        cls = self.oracle.CallerContract
        cls.setUpClass()
        paths = ('native_static01/artifacts.json', 'native_abi_static01/abi.json',
                 'native_entry_static01/entry.json')
        for relative in (*paths, 'scope-source', 'scope-owner'):
            case = cls('test_preparation_manifest_and_source_drift_are_rejected')
            case.setUp()
            try:
                if relative in paths:
                    current = private_oracle().COMPILED + relative
                    old = (ROOT / 'state/analysis/P7_motor_settle_compile_raw' / relative).read_bytes()
                    self.assertNotEqual(hashlib.sha256(old).hexdigest(), case.preparation['files'][current]['sha256'])
                    case.drift[current] = old
                else:
                    key, value = ('source_sha256', '117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da') if relative == 'scope-source' else ('run_id', 'app-motor-settle-117cc0e7-run01')
                    case.scope[key] = value
                    case.save_scope()
                with self.subTest(relative=relative):
                    case.rejected()
                    case.transport.assert_not_called()
                    case.process.assert_not_called()
            finally:
                case.doCleanups()

    def test_current_private_recipes_and_scope_roles_are_exact(self):
        support = load_support().load_support()
        spec = json.loads(support.checked(ROOT / support.BINDING, support.BINDING_SHA))
        for name, size, digest in (
                ('inert_caller', 22983, '3bd88946372ae637acdcfce2170a385e92dc313665bc75ed268c4aaa9ba1af75'),
                ('inert_actions', 19156, 'cd3a28e82de554358e1a4855a76b5dc316f0007158bdac846fcb464e9130c3ab')):
            projection = spec['private_runtime_projections'][name]
            raw = support.checked(ROOT / projection['input']['path'], projection['input']['sha256'])
            raw = support.replace(raw, [(r['old'], r['new'], r['count']) for r in projection['steps']])
            self.assertEqual((len(raw), support.sha(raw)), (size, digest))
        self.assertEqual(self.subject.legacy.RUN_ID, 'app-motor-const-4bc3a2e6-run01')
        self.assertEqual(self.subject.legacy.SOURCE, support.SOURCE)
        self.assertIn('state/analysis/P7_motor_const_run_contract.md', self.subject.SCOPE_FILES)
        self.assertIn('state/analysis/P7_motor_const_run_raw/run_derivation01.json', self.subject.SCOPE_FILES)
        self.assertNotIn('state/analysis/P7_motor_settle_run_raw/native_inert_run01', (self.subject.OUTPUT,))
        self.assertEqual(self.subject.diagnostic.PROJECT, 'app_motor_observe.ino')
        self.assertEqual(self.subject.PINS['tools/compile_motor_const.py'],
            '957666a83c6fa36408dd6616f93d9cdc583622b29a51a6f6c6e960dd4cd1f247')


def load_tests(loader, tests, pattern):
    provider = private_oracle(); historical = provider.caller_oracle()
    suite = unittest.TestSuite()
    for cls in (historical.CallerContract, provider.ObserverEvidence, CurrentCaller):
        cls.__module__ = __name__; suite.addTests(loader.loadTestsFromTestCase(cls))
    if suite.countTestCases() != 30: raise AssertionError('Expected27 retained+3 D207 caller methods')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
