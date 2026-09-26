# Checks the fixed observer actions from frozen contracts and historical oracles.
# Retains all 13 original cases with only checked metadata and wait-fixture changes.
# Host clocks, transports and descriptors are controlled; no device or real sleeping.
import ast
import copy
import hashlib
import os
from pathlib import Path
import subprocess
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
HISTORICAL = ROOT / 'state/analysis/P7_app_motor_fault_run_raw/test_actions.py'
SUBJECT = ROOT / 'state/analysis/P7_app_motor_observe_run_raw/actions.py'
REMOTE_ORACLE = ROOT / 'tests/tooling/test_app_motor_observe_remote.py'
ORACLE_SHA = '2035499ecb3195fdc4bb68f37ada7b88dac0f93abfbc1c70668e6c31d3fe2297'
REMOTE_ORACLE_SHA = 'f45218ea3d9fb118adfe796c12fc5f4bab654c843cf33cc531e81d99a3f41fc6'
SUBJECT_SHA = '6a730069e2511306459f5c3443976a84351b155fd04660a094606cfd98f2829f'
ADAPTER_SHA = '98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db'
PINS = {
    'state/analysis/P7_app_motor_observe_caller_contract.md':
        '03b61d0c152fccd69775c458023ffe0a48d307a0a1056d2ea36d7fe2adf81a34',
    'state/analysis/P7_app_motor_observe_remote_contract.md':
        'c2563449091f44ccd827b8cbc1173dc3e655614f6bb8d01c091540b99958d9c7',
    'state/analysis/P7_app_motor_fault_run_raw/test_actions.py': ORACLE_SHA,
    'tests/tooling/test_app_motor_observe_remote.py': REMOTE_ORACLE_SHA,
    'state/analysis/P7_app_motor_observe_run_raw/actions.py': SUBJECT_SHA,
    'state/analysis/P7_app_motor_observe_run_raw/remote.py': ADAPTER_SHA,
    'state/analysis/P7_app_motor_fault_run_raw/actions_run02.py':
        '4eeb19f1923b5058a3df69ecd196d5f331e9e9f51ca1193f6c7026ca837ee0fb',
    'state/analysis/P7_motor_fault_raw/inert_actions.py':
        '8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104',
}
_ORACLES = None
LINUX_ONLY = (
    'test_bootstrap_rejects_bad_framing_before_root_or_module_execution',
    'test_bootstrap_success_checks_staged_adapter_and_capture_parser_again',
    'test_changed_staged_adapter_and_installed_parser_never_dispatch',
    'test_closure_drift_cannot_be_overridden_by_successful_inner_report',
    'test_outward_close_error_preserves_unattributed_durable_report_and_fails',
)


def checked(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise AssertionError('Frozen oracle input differs: ' + str(path))
    return raw


def replace_exact(raw, before, after, count):
    before, after = before.encode(), after.encode()
    if raw.count(before) != count:
        raise AssertionError('Fixture projection count differs: ' + repr(before))
    return raw.replace(before, after)


def method_names(raw):
    return sorted((node.name, method.name) for node in ast.parse(raw).body
                  if isinstance(node, ast.ClassDef) for method in node.body
                  if isinstance(method, ast.FunctionDef) and method.name.startswith('test_'))


def private_oracles():
    """Return private checked (remote, actions) fixture modules for caller reuse."""
    global _ORACLES
    if _ORACLES is not None:
        return _ORACLES
    source = checked(REMOTE_ORACLE, REMOTE_ORACLE_SHA)
    provider = ModuleType('_d195_checked_remote_oracle_provider')
    provider.__file__ = str(REMOTE_ORACLE)
    exec(compile(source, str(REMOTE_ORACLE), 'exec'), provider.__dict__)
    remote = provider.historical_oracle()
    raw = checked(HISTORICAL, ORACLE_SHA)
    original_methods = method_names(raw)
    replacements = (
        ('import test_remote as remote_oracle', '# remote_oracle is privately injected', 1),
        ('import pwd', 'pwd = PRIVATE_PWD', 1),
        ('10518', '11357', 2), ('10519', '11358', 1),
        ('d796489fc812a509f5ef1edbcd487a4a3afe4adc76960a94ba9c1d3ec075e10a', ADAPTER_SHA, 1),
        ('app-motor-fault', 'app-motor-observe', 4),
        ("HERE / 'actions.py'", 'SUBJECT', 1),
        ('727088', '727152', 1), ('727089', '727153', 1),
        ("    reads = [{'name': name, 'address': address, 'bytes': size,",
         "    value['finished_monotonic'] = 43.0\n"
         "    reads = [{'name': name, 'address': address, 'bytes': size,", 1),
        ("wait={'requested_seconds': 2, 'before': 10.5, 'after': 12.5}",
         "wait={'requested_seconds': 2, 'before': 40.5, 'after': 42.5}", 1),
        ("'coherence': 'UNPROVEN', 'snapshots': copy.deepcopy(reads[7:19]),",
         "'pre_sample_wait': {'requested_seconds': 30, 'before': 10.0, 'after': 40.0},\n"
         "                           'coherence': 'UNPROVEN', 'snapshots': copy.deepcopy(reads[7:19]),", 1),
        ('after=12.499', 'after=42.499', 1),
    )
    for entry in replacements:
        raw = replace_exact(raw, *entry)
    if len(original_methods) != 13 or method_names(raw) != original_methods:
        raise AssertionError('Historical action method inventory changed')
    actions = ModuleType('_d195_private_actions_oracle')
    actions.__file__ = str(HISTORICAL)
    actions.SUBJECT, actions.remote_oracle = SUBJECT, remote
    if sys.platform.startswith('linux'):
        import pwd
        actions.PRIVATE_PWD = pwd
    else:
        actions.PRIVATE_PWD = SimpleNamespace(getpwuid=lambda *args:
            (_ for _ in ()).throw(AssertionError('Linux identity fixture reached on Windows')))
    exec(compile(raw, str(HISTORICAL) + '<D195-fixture>', 'exec'), actions.__dict__)
    actions.ActionsContract.__unittest_skip__ = False
    for name in LINUX_ONLY:
        setattr(actions.ActionsContract, name, unittest.skipUnless(
            sys.platform.startswith('linux'), 'Linux RAM descriptor/bootstrap fixture')(
                getattr(actions.ActionsContract, name)))
    _ORACLES = remote, actions
    return _ORACLES


def forbidden(*args, **kwargs):
    raise AssertionError('Native action or real sleep forbidden')


class WaitValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.remote, cls.fixture = private_oracles()
        checked(SUBJECT, SUBJECT_SHA)
        with mock.patch.object(subprocess, 'Popen', side_effect=forbidden):
            cls.subject = cls.fixture.load(SUBJECT, '_d195_actions_wait_subject')

    def setUp(self):
        for owner, name in ((subprocess, 'Popen'), (subprocess, 'run'), (os, 'system')):
            patch = mock.patch.object(owner, name, side_effect=forbidden)
            patch.start()
            self.addCleanup(patch.stop)
        patch = mock.patch('time.sleep', side_effect=forbidden)
        patch.start()
        self.addCleanup(patch.stop)

    def check_capture(self, mutate=None, valid=False):
        value = self.fixture.envelope('capture')
        if mutate:
            mutate(value['report'])
        # Invalid nonfinite values cannot be canonicalized; validate directly so
        # a serialization failure cannot substitute for the validator's rejection.
        try:
            self.fixture.refresh(value)
        except (ValueError, TypeError):
            pass
        before = copy.deepcopy(value)
        if valid:
            self.subject.validate_reply('capture', value)
        else:
            with self.assertRaises(Exception):
                self.subject.validate_reply('capture', value)
        # repr preserves NaN spelling while equality deliberately does not.
        self.assertEqual(repr(value), repr(before))
        return value

    def test_fixed_inputs_and_retained_method_inventory(self):
        for path, expected in PINS.items():
            with self.subTest(path=path):
                checked(ROOT / path, expected)
        self.assertEqual(len([name for name in vars(self.fixture.ActionsContract) if name.startswith('test_')]), 13)
        self.assertEqual(self.fixture.ADAPTER_PIN['bytes'], 11357)
        self.assertEqual(self.fixture.ADAPTER_PIN['sha256'], ADAPTER_SHA)
        self.assertEqual(self.fixture.report('upload')['finished_monotonic'], 13.0)
        self.assertEqual(self.fixture.report('capture')['finished_monotonic'], 43.0)

    def test_valid_wait_receipt_and_inclusive_boundaries(self):
        self.check_capture(valid=True)
        def boundaries(report):
            report['analysis']['pre_sample_wait'] = {'requested_seconds': 30, 'before': 10, 'after': 40}
            report['wait'] = {'requested_seconds': 2, 'before': 40, 'after': 42}
            report['finished_monotonic'] = 42
        self.check_capture(boundaries, valid=True)
        def longer(report):
            report['analysis']['pre_sample_wait'].update(before=10.25, after=40.5)
        self.check_capture(longer, valid=True)

    def test_wait_requires_exact_present_object_keys(self):
        mutations = [lambda r: r['analysis'].pop('pre_sample_wait')]
        for value in (None, [], '30', {}, {'requested_seconds': 30, 'before': 10},
                      {'requested_seconds': 30, 'before': 10, 'after': 40, 'extra': 0}):
            mutations.append(lambda r, value=value: r['analysis'].update(pre_sample_wait=value))
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                self.check_capture(mutate)

    def test_pre_wait_requested_seconds_is_exact_integer_30(self):
        for value in (True, False, 30.0, 29, 31, '30', None):
            with self.subTest(value=value):
                self.check_capture(lambda r: r['analysis']['pre_sample_wait'].update(requested_seconds=value))

    def test_pre_wait_timestamps_reject_bool_nonfinite_and_nonnumeric(self):
        for key in ('before', 'after'):
            for value in (True, False, float('nan'), float('inf'), -float('inf'), None, '40', []):
                with self.subTest(key=key, value=value):
                    self.check_capture(lambda r: r['analysis']['pre_sample_wait'].update({key: value}))

    def test_short_or_backward_pre_wait_is_not_success(self):
        for before, after in ((10, 39.999), (40, 10), (10, 10)):
            with self.subTest(before=before, after=after):
                self.check_capture(lambda r: r['analysis']['pre_sample_wait'].update(before=before, after=after))

    def test_pre_wait_order_inside_capture_and_before_sample_pause(self):
        for before, after in ((9.999, 40), (11, 41), (10, 41)):
            with self.subTest(before=before, after=after):
                self.check_capture(lambda r: r['analysis']['pre_sample_wait'].update(before=before, after=after))

    def test_sample_pause_and_finished_bounds_remain_independent(self):
        mutations = [lambda r: r['wait'].update(before=39.999, after=42),
                     lambda r: r['wait'].update(before=40.5, after=42.499),
                     lambda r: r.update(finished_monotonic=42.499),
                     lambda r: r['wait'].update(requested_seconds=30),
                     lambda r: r['wait'].update(requested_seconds=True)]
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                self.check_capture(mutation)

    def test_wait_does_not_admit_terminal_or_extra_analysis_claims(self):
        for key, value in (('phase', 'FROZEN'), ('epochs', 10000), ('coherence', 'PROVEN')):
            with self.subTest(key=key):
                self.check_capture(lambda r: r['analysis'].update({key: value}))

    def test_valid_wait_cannot_promote_failed_or_unattributed_outer_result(self):
        for change in ({'report_origin': 'durable_unattributed'},
                       {'first_error': {'type': 'OSError', 'message': 'outer close error'}},
                       {'postcheck_errors': [{'check': 'adapter', 'message': 'changed'}]}):
            value = self.fixture.envelope('capture')
            value.update(change)
            before = copy.deepcopy(value)
            with self.subTest(change=change), self.assertRaises(Exception):
                self.subject.validate_reply('capture', value)
            self.assertEqual(value, before)
        self.check_capture(lambda r: r.update(status='FAILED', first_error={'type': 'ValueError', 'message': 'inner error'}))

    def test_sequence_keeps_invalid_wait_receipt_first_failure_and_closes_once(self):
        case = self.fixture.ActionsContract(methodName='test_success_sequence_is_exact_and_passes_retained_upload_predecessor')
        reply = self.fixture.envelope('capture')
        reply['report']['analysis']['pre_sample_wait']['after'] = 39.0
        self.fixture.refresh(reply)
        operations, events = case.operations(replies={'capture': reply})
        value = self.subject.run_actions(operations)
        self.assertEqual(value['status'], 'FAILED')
        self.assertIsNotNone(value['first_error'])
        self.assertEqual(value['capture'], reply)
        self.assertEqual((value['upload_attempts'], value['capture_attempts']), (1, 1))
        self.assertEqual([name for name, args in events][-3:], ['local', 'prerequisites', 'finish'])
        self.assertEqual(sum(name == 'capture' for name, args in events), 1)


def load_tests(loader, tests, pattern):
    remote, actions = private_oracles()
    actions.ActionsContract.__module__ = __name__
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(actions.ActionsContract))
    suite.addTests(loader.loadTestsFromTestCase(WaitValidation))
    return suite


if __name__ == '__main__':
    unittest.main(verbosity=2)
