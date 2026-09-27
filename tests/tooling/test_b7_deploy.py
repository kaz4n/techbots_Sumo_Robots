"""Exercise D245 against synthetic Git/compiler/qualification records only.

Expectations derive from the B7 contract and accepted D227 fixtures.
All board transports are refused or controlled callbacks; no actual upload.
"""
from contextlib import ExitStack
import copy
from datetime import timedelta
import inspect
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

from . import test_commissioning_deploy as old
from . import test_commissioning_app_upload as upload

ROOT = old.ROOT
CALLER = 'tools/deploy_b7_app.py'
ADAPTER = 'tools/b7_app_upload.py'
CONTRACT = 'state/analysis/P2_b7_deploy_contract.md'
LEGACY_PINS = {
    'tools/compile_commissioning_app.py': '038a74777db7d26a15ff543d311fc4df2503e6f6b8e3b08fabcfb1c853220462',
    'tools/compile_b7_app.py': '267efb9f3f661a12411a41ac75761be2d5a571a59f48e1b965abc4210139330a',
}
MACROS = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
          'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
          'SUMOX_P5_ABORT_TIMING', 'SUMOX_MOTOR_FAULT_PROBE')


def flags(profile, motors):
    assert profile == 'b7_brownout' and type(motors) is int and motors in (0, 1)
    return ' '.join(['-DMATCH=0', '-DMOTORS_ALLOWED=' + str(motors)] +
                    ['-D' + macro + '=0' for macro in MACROS] + ['-DSUMOX_B7_BROWNOUT=1'])


def paths(selection):
    result = upload.paths(selection)
    result['output'] = 'state/analysis/P2_b7_build_raw/' + result['owner']
    return result


class AdapterTests(unittest.TestCase):
    def test_closed_b7_identity_and_preserved_native_paths(self):
        subject = upload.load(ROOT / ADAPTER, '_d245_adapter')
        uploader = upload.load(ROOT / (upload.STATIC + 'upload_remote.py'), '_d245_frozen_upload')
        base = upload.load(ROOT / 'tools/match_deploy.py', '_d245_bindings')
        support = base.binding_support((ROOT / upload.SOURCE_PATHS['support']).read_bytes())
        for motors in (0, 1):
            selected = upload.selection('b7_brownout', motors)
            self.assertEqual(subject.commissioning_profile(uploader, support, **selected),
                             upload.expected_profile(uploader, selected))
            for profile in (*upload.PROFILES, 'B7_BROWNOUT', '', True):
                with self.subTest(profile=profile), self.assertRaises((TypeError, ValueError)):
                    subject.commissioning_profile(uploader, support, **dict(selected, profile=profile))
            for bad in (True, 2, -1, '1'):
                with self.subTest(motors=bad), self.assertRaises((TypeError, ValueError)):
                    subject.commissioning_profile(uploader, support, **dict(selected, motors_allowed=bad))

    def test_private_namespaces_and_public_delivery_refusal(self):
        subject = upload.load(ROOT / CALLER, '_d245_caller')
        first, second = subject.load_deployer(root=ROOT), subject.load_deployer(root=ROOT)
        self.assertIsNot(first, second)
        self.assertEqual(first.GATES, {'b7_brownout': 'GATE P1 PASS'})
        first.GATES['synthetic-change'] = 'INVALID'
        self.assertEqual(second.GATES, {'b7_brownout': 'GATE P1 PASS'})
        legacy = upload.load(ROOT / 'tools/deploy_commissioning_app.py', '_d245_old_caller')
        self.assertEqual(legacy.GATES, old.GATES)
        for name in ('load_scope', 'check_only', 'upload_precompiled'):
            self.assertNotIn('_delivery', inspect.signature(getattr(subject, name)).parameters)
        for name, digest in LEGACY_PINS.items():
            self.assertEqual(upload.sha((ROOT / name).read_bytes()), digest)
        good = ['--check-only', '--scope', old.SCOPE, '--reviewed-head', 'a' * 40]
        subject.parse_request(good)
        for value in (good + ['--upload'], good + ['--delivery', 'x'], ['--execute']):
            with self.assertRaises((TypeError, ValueError)):
                subject.parse_request(value)


class Fixture(old.DeployFixture):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        compiler = upload.load(ROOT / 'tools/compile_b7_app.py', '_d245_compiler_fixture')
        request = dict(action='--check-only', profile='b7_brownout', motors_allowed=0,
                       attempt='fixture01', reviewed_head='a' * 40)
        required = compiler.load_caller(request).REQUIRED | {
            'tools/deploy_commissioning_app.py', 'tools/commissioning_app_upload.py'}
        cls.compiler = SimpleNamespace(REQUIRED=required, make_owner=compiler.make_owner)
        cls.policy = upload.load(ROOT / 'tools/b7_app_static_policy.py', '_d245_policy_fixture')

    def setUp(self):
        patches = ExitStack(); self.addCleanup(patches.close)
        for name, value in dict(SUBJECT=CALLER, CONTRACT=CONTRACT,
            SOURCE_PATHS=dict(upload.SOURCE_PATHS, adapter=ADAPTER), expected_flags=flags,
            paths=paths, GATES={'b7_brownout': 'GATE P1 PASS'}).items():
            patches.enter_context(mock.patch.object(old, name, value))
        self.constructing = False
        super().setUp()

    def make(self, profile='b7_brownout', motors=0, **options):
        self.assertEqual(profile, 'b7_brownout')
        self.constructing = True
        try:
            super().make(profile, motors, **options)
        finally:
            self.constructing = False

    def refresh(self, **options):
        if self.constructing and self.qual is not None:
            self.qual['operation'] = 'stand'
            self.auth['reply'] = 'STAND OK'
        super().refresh(**options)
        self.scope['schema'] = 'b7-app-deploy-v1'
        old.put_json(self.root, old.SCOPE, self.scope)
        self.head = self.commit()


class AdmissionTests(Fixture):
    def test_exact_m0_and_qualified_m1_stand_with_real_git_closure(self):
        for motors in (0, 1):
            self.make(motors=motors); admitted = self.admit()
            self.assertEqual(admitted['request'], self.request)
            self.assertEqual(admitted['selection'], self.selected)
            self.assertEqual(admitted['request_sha256'], upload.sha(upload.canonical(self.request)))
            board = self.board(); result = self.subject.check_only(board, old.SCOPE, self.head, now=old.NOW)
            self.assertEqual(result['status'], 'ADMITTED_LOCAL'); self.assertFalse(result['board_observed'])
            board.remote.assert_not_called(); board.require_transport.assert_not_called()
            self.assertFalse((self.root / ('state/analysis/b7_deploy_' + old.RUN)).exists())
            if motors:
                self.assertEqual(self.qual['operation'], 'stand')
                self.assertEqual(self.qual['gate']['reply'], 'GATE P1 PASS')
                self.assertEqual(self.auth['reply'], 'STAND OK')

    def test_b7_cannot_use_ring_wrong_gate_or_stale_authority(self):
        self.make(motors=1); self.admit()
        for object_, key, bad in ((self.qual, 'operation', 'ring'),
                                  (self.qual['gate'], 'reply', 'GATE P2 PASS'),
                                  (self.auth, 'reply', 'RING OK'),
                                  (self.auth, 'message_ref', ''),
                                  (self.auth, 'expires_utc', old.NOW.isoformat()),
                                  (self.auth, 'expires_utc', (old.NOW + timedelta(hours=2)).isoformat()),
                                  (self.auth, 'issued_utc', (old.NOW + timedelta(seconds=1)).isoformat())):
            original = object_[key]; object_[key] = bad; self.refresh()
            with self.subTest(key=key, bad=bad): self.reject()
            object_[key] = original
        self.request['run_id'] = 'a' * 32
        self.refresh(image=False, authorization=False); self.reject()

    def test_all_physical_checks_grants_buttons_and_profile_are_required(self):
        self.make(motors=1, config=self.config); self.reject()
        self.make(motors=1); self.admit()
        for mapping, names in ((self.qual['checks'], old.CHECKS), (self.qual['grants'], old.GRANTS[:3])):
            for name in names:
                original = mapping.pop(name); self.refresh()
                with self.subTest(missing=name): self.reject()
                mapping[name] = original
        self.make(motors=1, config=self.operational_config().replace(
            b'BUTTON_LOW_RAW[4] = {0U, 100U, 200U, 300U};',
            b'BUTTON_LOW_RAW[4] = {0U, 49U, 200U, 300U};'))
        self.reject()
        self.make()
        for profile in upload.PROFILES:
            self.request['profile'] = profile; self.refresh()
            with self.subTest(profile=profile): self.reject()

    def test_inhibited_truth_and_complete_compile_receipt_semantics(self):
        old.AdmissionTests.test_inhibited_source_requires_exact_disabled_grants_axes_origin_and_syntax(self)
        self.make()
        old.AdmissionTests.test_compile_counts_closures_commands_properties_and_stderr_are_semantic(self)

    def test_source_commit_must_match_actual_git_blobs(self):
        old.AdmissionTests.test_source_commit_must_be_actual_matching_blob_even_if_manifest_is_coherent(self)

    def test_identified_delivery_fields_remain_unavailable(self):
        for motors in (0, 1):
            baseline = self.operational_config() if motors else self.config
            for name in (b'APP_DUMP_RECEIVE_STREAM_ID', b'APP_DUMP_SESSION_ID'):
                self.make(motors=motors, config=baseline.replace(name + b' = 0U;', name + b' = 1U;'))
                self.reject()


class LifecycleTests(Fixture):
    setup_remote = old.LifecycleTests.setup_remote

    def test_controlled_upload_once_and_consumed_b7_owner(self):
        self.make(motors=1)
        board, calls = self.setup_remote()
        outcome = self.subject.upload_precompiled(board, old.SCOPE, self.head, now=old.NOW)
        self.assertEqual(outcome['status'], 'ACCEPTED'); self.assertEqual(outcome['attempts'], 1)
        self.assertEqual(outcome['schema'], 'b7-app-deploy-outcome-v1'); self.assertEqual(len(calls), 5)
        path = self.root / ('state/analysis/b7_deploy_' + old.RUN)
        self.assertTrue((path / 'outcome.json').is_file())
        with self.assertRaises((ValueError, OSError)):
            self.subject.upload_precompiled(board, old.SCOPE, self.head, now=old.NOW)
        self.assertEqual(len(calls), 5)

    def test_controlled_timeout_retains_unknown_and_never_retries(self):
        old.LifecycleTests.test_timeout_unknown_preserves_primary_runs_closing_and_never_retries(self)

    def test_controlled_closing_failure_is_not_success(self):
        old.LifecycleTests.test_closing_failures_are_independent_and_never_accept(self)

    def test_controlled_evidence_failure_is_not_success(self):
        old.LifecycleTests.test_outcome_write_failure_cannot_be_success(self)


def load_tests(loader, standard, pattern):
    return unittest.TestSuite(loader.loadTestsFromTestCase(case)
        for case in (AdapterTests, AdmissionTests, LifecycleTests))


if __name__ == '__main__':
    unittest.main(verbosity=2)
