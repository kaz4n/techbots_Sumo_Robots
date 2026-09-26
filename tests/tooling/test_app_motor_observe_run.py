# Tests fixed observer admission against independent source and ABI02 evidence.
# Preserves the historical 20 caller methods with exact metadata fixture changes.
# Freeze before subject load; all subprocesses and board transport are controlled.
import ast
from contextlib import contextmanager
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
HISTORICAL = ROOT / 'state/analysis/P7_app_motor_fault_run_raw/test_run.py'
HISTORICAL_SHA = '83c5fea689bac3f5eac0e83cf76137774d8e1a02d401017079e014ea1a0c0d8e'
ACTION_ORACLE = ROOT / 'tests/tooling/test_app_motor_observe_actions.py'
ACTION_ORACLE_SHA = '103493975bccdcab094b412a5ba26cf125a6f294a9b5efac167660f6fda8a563'
RAW = 'state/analysis/P7_app_motor_observe_run_raw/'
COMPILED = 'state/analysis/P7_app_motor_observe_compile_raw/'
MANIFEST = COMPILED + 'inputs_static.json'
MANIFEST_SHA = 'aa350c657fbff328dc139793c4ccd09c86ce45e05bdc7acaa20822498beb7d6e'
SUBJECT = ROOT / RAW / 'run.py'
LAUNCHER_SHA = '70e1f016cec041b40c98c7c5dd5ee20223d75c4a876c76d2fcdea3d790d63827'
_ORACLE = None


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, expected):
    raw = path.read_bytes()
    if sha(raw) != expected:
        raise AssertionError('Independent source changed: ' + str(path))
    return raw


def replace_exact(raw, old, new, count):
    old, new = old.encode(), new.encode()
    if raw.count(old) != count:
        raise AssertionError('Fixture replacement count differs: ' + repr(old))
    return raw.replace(old, new)


def inventory(raw):
    return sorted((node.name, method.name) for node in ast.parse(raw).body
                  if isinstance(node, ast.ClassDef) for method in node.body
                  if isinstance(method, ast.FunctionDef) and method.name.startswith('test_'))


def caller_oracle():
    global _ORACLE
    if _ORACLE is not None:
        return _ORACLE
    action_raw = checked(ACTION_ORACLE, ACTION_ORACLE_SHA)
    action_module = ModuleType('_d195_caller_action_oracle')
    action_module.__file__ = str(ACTION_ORACLE)
    exec(compile(action_raw, str(ACTION_ORACLE), 'exec'), action_module.__dict__)
    remote, actions = action_module.private_oracles()
    raw = checked(HISTORICAL, HISTORICAL_SHA)
    before = inventory(raw)
    replacements = (
        ('import test_actions as actions_oracle', 'actions_oracle = INJECTED_ACTIONS', 1),
        ('import test_remote as remote_oracle', 'remote_oracle = INJECTED_REMOTE', 1),
        ('app_motor_fault', 'app_motor_observe', 14),
        ('app-motor-fault', 'app-motor-observe', 2),
        ('P7_app_motor_observe_remote_source_review.md', 'P7_app_motor_observe_remote_review.md', 1),
        ('P7_app_motor_observe_run_contract.md', 'P7_app_motor_observe_remote_contract.md', 1),
        ('P7_app_motor_observe_native_actual_review.md', 'P7_app_motor_observe_compile_actual_review.md', 1),
        ('P7_app_motor_observe_abi_actual_review.md', 'P7_app_motor_observe_abi02_actual_review.md', 1),
        ('native_abi_static01', 'native_abi_static02', 2),
        ('abi_static01_interpreted.json', 'native_abi_static02/abi.json', 1),
        ("RAW + 'test_run.py'", "'tests/tooling/test_app_motor_observe_run.py'", 1),
        ("RAW + 'test_actions.py'", "'tests/tooling/test_app_motor_observe_actions.py'", 1),
        ("RAW + 'test_remote.py'", "'tests/tooling/test_app_motor_observe_remote.py'", 2),
        ('d4eae97c1c47a1ce0fa24c9d7e3ae44857a565cd7b85b9c17be45143654d3eb5', MANIFEST_SHA, 1),
        ('self.assertEqual(len(self.manifest[\'files\']), 127)',
         'self.assertEqual(len(self.manifest[\'files\']), 128)', 1),
        ("'adapter_bytes': 10518", "'adapter_bytes': 11357", 1))
    for entry in replacements:
        raw = replace_exact(raw, *entry)
    if inventory(raw) != before or len(before) != 20:
        raise AssertionError('Historical caller method inventory changed')
    module = ModuleType('_d195_private_caller_oracle')
    module.__dict__.update(__file__=str(HISTORICAL), INJECTED_ACTIONS=actions, INJECTED_REMOTE=remote)
    exec(compile(raw, str(HISTORICAL) + '<D195-fixture>', 'exec'), module.__dict__)
    module.CallerContract.__module__ = __name__
    _ORACLE = module
    return module


@contextmanager
def no_native():
    with mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Native child forbidden')), \
         mock.patch.object(subprocess, 'run', side_effect=AssertionError('Native process forbidden')):
        yield


class ObserverEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = caller_oracle()
        with no_native():
            cls.subject = cls.oracle.actions_oracle.load(SUBJECT, '_d195_evidence_subject')
        cls.manifest = json.loads(checked(ROOT / MANIFEST, MANIFEST_SHA))
        cls.code = {name: checked(ROOT / name, expected) for name, expected in cls.manifest['files'].items()}
        cls.expected = cls.oracle.source_projection(cls.manifest)

    def setUp(self):
        self.guard = no_native()
        self.guard.__enter__()
        self.addCleanup(self.guard.__exit__, None, None, None)

    def test_projected_d193_source_inventory_and_mapping_are_exact(self):
        subject = self.subject
        self.assertEqual(subject.diagnostic.PROJECT, 'app_motor_observe.ino')
        self.assertEqual(subject.PINS['tools/compile_app_motor_observe.py'], LAUNCHER_SHA)
        self.assertEqual(subject.SOURCE, self.manifest['source_sha256'])
        self.assertEqual(len(self.code), 128)
        owner = SimpleNamespace(root=ROOT, base=subject.current)
        names = subject.diagnostic.CompileDiagnostic.source_names(owner)
        expected_names = {name for name in self.code if name.startswith(
            ('src/', 'bench/app_motor_observe/', 'bench/motor_fault/src/'))}
        self.assertEqual(set(names), expected_names)
        mapped, digest = subject.diagnostic.CompileDiagnostic.source_mapping(owner, self.code, names)
        self.assertEqual(digest, self.manifest['source_sha256'])
        self.assertEqual(mapped, {name: pin['sha256'] for name, pin in self.expected.items()})
        self.assertIn('app_motor_observe.ino', mapped)
        self.assertNotIn('app_motor_fault.ino', mapped)
        self.assertEqual(subject.InertRun(self.oracle.HEAD, root=ROOT).source_inventory(), names)

    def evidence_owner(self):
        names = ('native_static01/result.json', 'native_static01/artifacts.json',
                 'native_abi_static02/local_result.json', 'native_abi_static02/abi.json',
                 'native_entry_static01/local_result.json', 'native_entry_static01/entry.json')
        data = {COMPILED + name: (ROOT / COMPILED / name).read_bytes() for name in names}
        return SimpleNamespace(fixed_bytes=data, expected_identity={'boot_id': self.manifest['boot_id']})

    def test_successful_abi02_and_entry_evidence_accepts_without_native_work(self):
        owner = self.evidence_owner()
        self.subject.InertRun.check_evidence(owner)
        self.assertEqual(set(self.subject.PROVENANCE), set(self.oracle.PROVENANCE))
        self.assertEqual(len(self.subject.PROVENANCE), 12)
        self.assertIn(COMPILED + 'native_abi_static02/result.json', self.subject.PROVENANCE)
        self.assertNotIn(COMPILED + 'native_abi_static01/result.json', self.subject.PROVENANCE)
        self.assertEqual(set(self.subject.SCOPE_FILES), set(self.oracle.SCOPE_FILES))
        self.assertEqual(len(self.subject.SCOPE_FILES), 11)

    def test_wrong_abi_status_error_and_failed_predecessor_are_rejected(self):
        mutations = (
            ('native_abi_static02/local_result.json', {'status': 'FAILED'}),
            ('native_abi_static02/local_result.json', {'first_error': {'message': 'failed'}}),
            ('native_abi_static02/abi.json', {'status': 'OFFLINE_ABI_INTERPRETED'}),
            ('native_abi_static02/abi.json', {'status': 'FAILED'}),
            ('native_entry_static01/local_result.json', {'first_error': {'message': 'failed'}}),
            ('native_entry_static01/entry.json', {'status': 'FAILED'}),
            ('native_static01/result.json', {'source_sha256': '0' * 64}),
            ('native_static01/result.json', {'boot_id': 'wrong'}),
            ('native_static01/result.json', {'first_error': {'message': 'failed'}}),
            ('native_static01/artifacts.json', {'status': 'FAILED'}))
        for name, update in mutations:
            with self.subTest(name=name, update=update):
                owner = self.evidence_owner()
                key = COMPILED + name
                value = json.loads(owner.fixed_bytes[key])
                value.update(update)
                owner.fixed_bytes[key] = self.oracle.canonical(value)
                with self.assertRaises(Exception):
                    self.subject.InertRun.check_evidence(owner)
        owner = self.evidence_owner()
        owner.fixed_bytes[COMPILED + 'native_abi_static02/local_result.json'] = (
            ROOT / COMPILED / 'native_abi_static01/local_result.json').read_bytes()
        with self.assertRaises(Exception):
            self.subject.InertRun.check_evidence(owner)

    def test_old_manifest_refused_before_projection_and_any_transport(self):
        owner = self.subject.InertRun(self.oracle.HEAD, root=ROOT)
        owner.fixed_bytes = {MANIFEST: (ROOT / 'state/analysis/P7_app_motor_fault_compile_raw/inputs_static.json').read_bytes()}
        owner.expected_identity = {'boot_id': self.manifest['boot_id']}
        with mock.patch.object(self.subject.diagnostic.CompileDiagnostic, 'source_mapping') as mapping:
            with self.assertRaises(Exception):
                owner.load_source()
            mapping.assert_not_called()

    def test_fixed_new_scope_owners_and_cli_signature_preserve_old_owners(self):
        self.assertEqual(self.subject.SCOPE, RAW + 'inert_run01_scope.json')
        self.assertEqual(self.subject.OUTPUT, RAW + 'native_inert_run01')
        self.assertEqual(self.subject.PREPARATION, RAW + 'preparation.json')
        self.assertEqual(self.subject.RUN_ID, 'app-motor-observe-3a08ddeb-run01')
        self.assertEqual(self.subject.BOARD, '2629958581')
        self.assertEqual(self.subject.actions.ADAPTER_BYTES, 11357)
        self.assertEqual(self.subject.actions.ADAPTER_SHA,
                         '98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db')
        self.assertEqual(self.subject.actions.ADAPTER,
                         '/home/arduino/sumox26_codex_build/app-motor-observe-3a08ddeb-run01-adapter/remote.py')


def load_tests(loader, tests, pattern):
    oracle = caller_oracle()
    return unittest.TestSuite((loader.loadTestsFromTestCase(oracle.CallerContract),
                               loader.loadTestsFromTestCase(ObserverEvidence)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
