# Retains the 24 D195 action cases through pinned private metadata fixtures.
# Adds exact D201 derivation, shared-plan identity and stale-window refusals.
# All process, descriptor, clock and transport operations remain controlled.
import copy
import hashlib
import json
from pathlib import Path
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
PRIOR = 'tests/tooling/test_app_motor_observe_actions.py'
PRIOR_SHA = '103493975bccdcab094b412a5ba26cf125a6f294a9b5efac167660f6fda8a563'
SUPPORT = 'tests/tooling/test_motor_settle_remote.py'
SUPPORT_SHA = '0b1977444737694e8b39e5d712bd7766bd1db4d6073bf582cbed9e960b4f38b5'
CHANGES = (
    ('P7_app_motor_observe', 'P7_motor_settle', 5),
    ('test_app_motor_observe', 'test_motor_settle', 2),
    ('app-motor-observe', 'app-motor-settle', 1),
    ('11357', '11343', 2), ('11358', '11344', 1),
    ('727152', '727432', 1), ('727153', '727433', 1),
    ('f45218ea3d9fb118adfe796c12fc5f4bab654c843cf33cc531e81d99a3f41fc6', SUPPORT_SHA, 1),
    ('6a730069e2511306459f5c3443976a84351b155fd04660a094606cfd98f2829f',
     '8918231c9c2aaf1b72120539e1677db73ce9103798fa860e9fa2501ac669092a', 1),
    ('98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db',
     '577f2f17ae532db1e21644868b624d0d8a903771309a39b0b3488f8ae4f98cb0', 1),
    ('03b61d0c152fccd69775c458023ffe0a48d307a0a1056d2ea36d7fe2adf81a34',
     '4a07cd9a8d21620896446665edccf5b7ad165c11e8bd97df9784c3a6e618f3f9', 1),
    ('c2563449091f44ccd827b8cbc1173dc3e655614f6bb8d01c091540b99958d9c7',
     '6d245a4e1f0426d5ed54b1ca47d124643ba9b2e3b6c86975294ba6efcd641dd3', 1),
)
_SUPPORT = _PROVIDER = None


def load_support():
    global _SUPPORT
    if _SUPPORT is None:
        raw = (ROOT / SUPPORT).read_bytes()
        if hashlib.sha256(raw).hexdigest() != SUPPORT_SHA:
            raise AssertionError('Remote oracle changed')
        value = types.ModuleType('_d201_actions_remote_support'); value.__file__ = str(ROOT / SUPPORT)
        exec(compile(raw, value.__file__, 'exec'), value.__dict__)
        _SUPPORT = value
    return _SUPPORT


def fixture_projection(raw):
    raw = load_support().replace(raw, CHANGES)
    if (len(raw), hashlib.sha256(raw).hexdigest()) != (13354, '901df0417fbbdde55a7c65919e2ec4980521674dbe2c399d97821815fb946022'):
        raise AssertionError('Projected actions fixture changed')
    return raw


def private_oracle():
    global _PROVIDER
    if _PROVIDER is None:
        support = load_support()
        raw = fixture_projection(support.checked(ROOT / PRIOR, PRIOR_SHA))
        value = types.ModuleType('_d201_private_actions_provider'); value.__file__ = str(ROOT / PRIOR)
        exec(compile(raw, value.__file__ + '<fixed D201 metadata>', 'exec'), value.__dict__)
        _PROVIDER = value
    return _PROVIDER


def private_oracles():
    return private_oracle().private_oracles()


class CurrentActions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        provider = private_oracle(); provider.WaitValidation.setUpClass()
        cls.case_type = provider.WaitValidation
        cls.subject, cls.fixture, cls.remote = cls.case_type.subject, cls.case_type.fixture, cls.case_type.remote

    def setUp(self):
        case = self.case_type('test_valid_wait_receipt_and_inclusive_boundaries')
        case.setUp(); self.addCleanup(case.doCleanups)

    def test_exact_nine_metadata_changes_preserve_other_action_source_bytes(self):
        support = load_support()
        spec = json.loads(support.checked(ROOT / support.BINDING, support.BINDING_SHA))['metadata_derivatives']['actions']
        self.assertEqual(len(spec['replacements']), 9)
        raw = support.checked(ROOT / 'state/analysis/P7_app_motor_observe_run_raw/actions.py', spec['original']['sha256'])
        self.assertEqual(len(raw), spec['original']['bytes'])
        expected = support.replace(raw, [(r['old'], r['new'], r['count']) for r in spec['replacements']])
        actual = private_oracle().SUBJECT.read_bytes()
        self.assertEqual(actual, expected)
        self.assertEqual((len(actual), support.sha(actual)), (12507, spec['output']['sha256']))

    def test_action_plan_matches_current_remote_and_bounded_inline_commands(self):
        self.assertEqual(tuple(self.subject.WINDOWS), load_support().WINDOWS)
        self.assertEqual(tuple(self.subject._plan()), tuple(self.remote.PLAN))
        self.assertEqual((len(self.subject._plan()), sum(row[2] for row in self.subject._plan())), (26, 727432))
        self.assertEqual(self.subject.ADAPTER_BYTES, 11343)
        for action in ('upload', 'capture'):
            command = self.subject.build_command(action, self.fixture.sources(), self.remote.bindings(action), self.fixture.ADAPTER_PIN)
            raw, value = self.fixture.decode_command(command)
            self.assertEqual(value['source_sha256'], load_support().SOURCE)
            self.assertEqual(value['run_id'], load_support().RUN)
            self.assertEqual(value['adapter_pin'], self.fixture.ADAPTER_PIN)
            self.assertLessEqual(len(raw), self.subject.legacy.PAYLOAD_LIMIT)
            self.assertLessEqual(self.subject.legacy._command_units(command) + 1, self.subject.legacy.COMMAND_LIMIT)

    def test_previous_window_and_stale_source_are_refused_without_receipt_mutation(self):
        for kind in ('name', 'address', 'bytes', 'source'):
            value = self.fixture.envelope('capture')
            if kind == 'source':
                value['report']['source_sha256'] = '3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0'
            else:
                replacement = {'name': 'first.previous', 'address': 537115952, 'bytes': 48}[kind]
                value['report']['reads'][11][kind] = replacement
                value['report']['analysis']['snapshots'][4][kind] = replacement
            self.fixture.refresh(value); before = copy.deepcopy(value)
            with self.subTest(kind=kind), self.assertRaises(Exception):
                self.subject.validate_reply('capture', value)
            self.assertEqual(value, before)


def load_tests(loader, tests, pattern):
    provider = private_oracle(); remote, actions = provider.private_oracles()
    suite = unittest.TestSuite()
    for cls in (actions.ActionsContract, provider.WaitValidation, CurrentActions):
        cls.__module__ = __name__; suite.addTests(loader.loadTestsFromTestCase(cls))
    if suite.countTestCases() != 27: raise AssertionError('Expected24 inherited+3 current action methods')
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
