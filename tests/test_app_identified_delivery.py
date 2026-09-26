# Tests the new pairing against real D227 Git/compile/qualification fixtures.
# Exercises session ownership, actual receiver composition and unchanged wire checks.
# Every authority record and transport outcome is synthetic; no native command runs.
import copy
import base64
import bz2
from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tools')]
from tests.tooling import test_commissioning_deploy as inherited
NOW, SCOPE = inherited.NOW, inherited.SCOPE
from tests.tooling.test_commissioning_app_upload import RUN, load
from tests.tooling.test_dump_match import wire, summary_row

CALLER = 'tools/run_app_identified_delivery.py'
EXTRA = (CALLER, 'tools/run_recorder_delivery.py', 'tools/dump_match.py',
         'tools/validate_csv_bundle.py', 'state/analysis/P7_app_identified_delivery_contract.md')
SESSION = int(RUN[:16], 16)


class PairedAdmission(inherited.DeployFixture):
    def setUp(self):
        super().setUp()
        self.app = load(ROOT / CALLER, '_d240_app_fixture')
        for name in EXTRA:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())
        body = self.operational_config()
        for name in ('DUMP_ENABLED', 'DUMP_SETUP_PHASE', 'DUMP_EXCLUSIVE_UART', 'DUMP_READY_PIN_OWNED'):
            body = body.replace(('APP_GRANT_' + name + ' = 0U;').encode(),
                                ('APP_GRANT_' + name + ' = 1U;').encode())
        body = body.replace(b'APP_DUMP_RECEIVE_STREAM_ID = 0U;', b'APP_DUMP_RECEIVE_STREAM_ID = 1U;')
        body = body.replace(b'APP_DUMP_SESSION_ID = 0U;', f'APP_DUMP_SESSION_ID = {SESSION}U;'.encode())
        self.identified_config = body
        self.make('p4_reactive', 1, config=body)
        self.request['target'] = self.app.TARGET
        self.refresh()

    def paired(self):
        return self.app.admit(self.root, SCOPE, self.head, now=NOW)

    def test_real_compile_and_qualification_admission_receiver_composition_and_default_refusal(self):
        deploy, scope, board = self.paired()
        self.assertEqual(scope['delivery']['session'], SESSION)
        self.assertFalse(scope['delivery_owner'].exists())
        self.assertEqual(self.app.check_only(self.root, SCOPE, self.head, now=NOW)['status'], 'ADMITTED_LOCAL')
        with self.assertRaisesRegex(ValueError, 'separately qualified'):
            self.subject.load_scope(self.root, SCOPE, self.head, self.app.TARGET, 'adb', now=NOW)
        receiver, owner, commands, dump = self.app.receiver_scope(scope, board)
        self.assertIs(receiver.accept_capture, self.app.accept_capture)
        self.assertEqual(owner.reviewed_head, self.compile_head)
        self.assertEqual(owner.session, SESSION)
        self.assertEqual(len(commands.allowed), 2)
        self.assertEqual([bound for unused, bound in commands.allowed], [915, 5])
        self.assertTrue(all(command[-2:] == ['adb', self.app.TARGET] for command, unused in commands.allowed))
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            commands.remote(self.app.TARGET, ['python3', '-c', 'print(1)'], capture=True, timeout=5)
        command, unused, checks = deploy.prepare(board, scope)
        self.assertEqual(len(checks), 2)
        payload = json.loads(bz2.decompress(base64.b85decode(command[-1])))
        self.assertEqual(payload['selection']['run_id'], RUN)
        self.assertEqual(payload['selection']['source_sha256'], scope['request']['source_sha256'])
        self.assertEqual(payload['bindings'], scope['request']['bindings'])

    def test_all_existing_qualification_and_specific_permission_checks_survive_opt_in(self):
        self.paired()
        original = copy.deepcopy(self.auth)
        self.auth['reply'] = 'STAND OK'
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'Specific human authorization'):
            self.paired()
        self.auth = original
        del self.qual['grants']['APP_GRANT_DUMP_EXCLUSIVE_UART']
        self.refresh()
        with self.assertRaises(ValueError):
            self.paired()

    def test_session_collision_and_changed_claim_refuse_before_any_upload(self):
        deploy, scope, board = self.paired()
        identity = self.app.reserve(deploy, scope)
        self.assertEqual(scope['base'].owner_identity(scope['delivery_owner']), identity)
        with self.assertRaises(ValueError):
            self.paired()
        collision = dict(scope['delivery'], run_id=RUN[:16] + 'fedcba9876543210')
        self.assertEqual(deploy.delivery_owner(scope['base'], self.root, collision), scope['delivery_owner'])
        current = deploy.load_scope(self.root, SCOPE, self.head, self.app.TARGET, 'adb', now=NOW,
                                    _delivery=scope['delivery'])
        self.assertEqual(deploy.output_path(current), scope['delivery_owner'] / 'upload')
        (scope['delivery_owner'] / 'claim.json').write_bytes(b'{}\n')
        with self.assertRaisesRegex(ValueError, 'claim changed'):
            deploy.upload_precompiled(board, SCOPE, self.head, now=NOW, _delivery=scope['delivery'])

    def test_actual_paired_d227_upload_keeps_five_operations_and_nested_consumed_owner(self):
        deploy, scope, unused = self.paired()
        self.app.reserve(deploy, scope)
        board, calls = inherited.LifecycleTests.setup_remote(self)
        board.target = lambda: self.app.TARGET
        result = deploy.upload_precompiled(board, SCOPE, self.head, now=NOW, _delivery=scope['delivery'])
        self.assertEqual((result['status'], result['attempts'], len(calls)), ('ACCEPTED', 1, 5))
        self.assertTrue((scope['delivery_owner'] / 'upload/outcome.json').is_file())
        with self.assertRaises(ValueError):
            deploy.upload_precompiled(board, SCOPE, self.head, now=NOW, _delivery=scope['delivery'])
        self.assertEqual(len(calls), 5)

    def test_m0_does_not_gain_operational_dump_grants(self):
        self.make('p4_reactive', 0, config=self.identified_config)
        self.request['target'] = self.app.TARGET
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'M0 diagnostic requires all setup grants absent'):
            self.paired()


class WireAcceptance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sumox_d240_wire_')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.app = load(ROOT / CALLER, '_d240_wire_subject')
        self.dump = __import__('dump_match')
        self.owner = types.SimpleNamespace(output=self.root, session=SESSION, reviewed_head='1' * 40,
            source_sha256='2' * 64, code={'src/config.h': b'// exact fixture config\n'})

    def save(self, data):
        return self.dump.save_capture([data], self.root / 'run/capture', receive_mode='adb',
            target=self.app.TARGET, expected_session=SESSION, firmware_revision=self.owner.reviewed_head,
            source_sha256=self.owner.source_sha256,
            config_sha256=self.app.hashlib.sha256(self.owner.code['src/config.h']).hexdigest())

    def test_real_variable_count_wire_and_loss_are_preserved_without_synthetic_oracles(self):
        for summary in (None, summary_row(interrupted=1, phase=4, incomplete=1)):
            path = self.save(wire(session=SESSION, summary=summary))
            result = self.app.accept_capture(self.owner, path, self.dump)
            self.assertEqual((result['frames'], result['events']), (2, 1))
            self.assertFalse(result['hardware_acceptance'])
            if summary is not None:
                self.assertEqual(result['recording']['lifecycle'], 'INTERRUPTED')

    def test_wrong_session_missing_envelope_and_changed_csv_remain_refusals(self):
        data = wire(session=SESSION)
        for wrong in (wire(session=SESSION + 1), data.split(b'\n', 1)[1]):
            with self.assertRaises(self.dump.CaptureError):
                self.save(wrong)
        path = self.save(data)
        csv = path / (path.name + '_frames.csv')
        csv.write_bytes(csv.read_bytes() + b'corrupt\n')
        with self.assertRaises((ValueError, self.dump.CaptureError)):
            self.app.accept_capture(self.owner, path, self.dump)

    def test_actual_inherited_receiver_close_calls_application_wire_validator(self):
        path = self.save(wire(session=SESSION))
        receiver = load(ROOT / 'tools/run_recorder_delivery.py', '_d240_real_close')
        receiver.accept_capture = self.app.accept_capture
        worker = types.SimpleNamespace(join=mock.Mock(), is_alive=lambda: False)
        commands = types.SimpleNamespace(stop=mock.Mock(), cleanup_errors=[])
        report = {'closing_errors': []}
        first = receiver.close_receiver(self.owner, self.root / 'run', worker,
            {'destination': str(path), 'error': None}, self.dump, commands, report, time.monotonic(), None)
        self.assertIsNone(first)
        self.assertEqual(report['capture_acceptance']['status'], 'IDENTIFIED_TRANSPORT_PASS')
        self.assertEqual(report['capture_acceptance']['frames'], 2)
        commands.stop.assert_called_once()
        original = ValueError('first receiver failure')
        commands.stop.side_effect = OSError('closing failure')
        first = receiver.close_receiver(self.owner, self.root / 'run', worker,
            {'destination': str(path), 'error': original}, self.dump, commands, report, time.monotonic(), None)
        self.assertIs(first, original)
        self.assertEqual(report['capture_acceptance_error']['message'], 'closing failure')


class RunOrdering(unittest.TestCase):
    def test_receiver_precedes_single_upload_and_failed_upload_still_closes(self):
        app = load(ROOT / CALLER, '_d240_order_subject')
        for failed in (False, True, "connection", "claim", "journal"):
            with self.subTest(failed=failed), tempfile.TemporaryDirectory(prefix='sumox_d240_order_') as tmp:
                root = Path(tmp); events = []
                scope = dict(delivery_owner=root, delivery={'session': SESSION, 'claimed': True},
                    request={'run_id': RUN, 'source_commit': '1' * 40, 'source_sha256': '2' * 64},
                    scope_sha256='3' * 64)
                def write(path, value):
                    if failed == 'journal' and path.name == 'result.json':
                        raise OSError('secondary journal failure')
                    path.write_text(json.dumps(value), encoding='utf8')
                scope['base'] = types.SimpleNamespace(write_exclusive=write, check_owner=lambda *a: None)
                error = OSError('original upload failure')
                def upload(*args, **kw):
                    events.append('upload')
                    if failed is True or failed == 'journal':
                        error.deploy_outcome = dict(attempts=1, status='UNKNOWN')
                        raise error
                    return dict(attempts=1, status='ACCEPTED', first_error=None, postcheck_errors=[])
                deploy = types.SimpleNamespace(upload_precompiled=upload)
                worker = types.SimpleNamespace(is_alive=lambda: True)
                state = dict(destination=None, error=None)
                def arm(*args):
                    events.append('arm'); return worker, state
                def connected(*args):
                    events.append('connected')
                    if failed == 'connection':
                        raise error
                    return {'state': 'CONNECTED'}
                def close(owner, run, thread, saved, dump, commands, report, started, first):
                    events.append('close')
                    report['receiver_cleanup_errors'] = [{'type': 'fixture closing error'}] if failed else []
                    report['capture_acceptance'] = None if failed else {'status': 'IDENTIFIED_TRANSPORT_PASS'}
                    return first
                def checked(*args, **kwargs):
                    events.append('check')
                    if failed == 'claim' and events.count('check') == 2:
                        raise error
                receiver = types.SimpleNamespace(arm_receiver=arm, await_connection=connected, close_receiver=close)
                with mock.patch.object(app, 'admit', return_value=(deploy, scope, object())), \
                     mock.patch.object(app, 'reserve', return_value=(1, 2)), \
                     mock.patch.object(app, 'revalidate', side_effect=checked), \
                     mock.patch.object(app, 'receiver_scope', return_value=(receiver, None, None, None)):
                    if failed:
                        with self.assertRaises(OSError) as caught:
                            app.run(root, 'fixture', '1' * 40)
                        self.assertIs(caught.exception, error)
                    else:
                        self.assertEqual(app.run(root, 'fixture', '1' * 40)['status'], 'DELIVERED')
                self.assertLess(events.index('arm'), events.index('connected'))
                if failed in ('connection', 'claim'):
                    self.assertNotIn('upload', events)
                    self.assertIn('close', events)
                else:
                    self.assertLess(events.index('connected'), events.index('upload'))
                    self.assertEqual(events.count('upload'), 1)
                    self.assertGreater(events.index('close'), events.index('upload'))
                saved = error.delivery_outcome if failed == 'journal' else json.loads((root / 'result.json').read_bytes())
                if failed == 'journal':
                    self.assertEqual(saved['closing_errors'][-1]['message'], 'secondary journal failure')
                self.assertEqual(saved['status'], 'FAILED' if failed else 'DELIVERED')
                if failed:
                    self.assertEqual(saved['first_error']['message'], 'original upload failure')
                    self.assertTrue(saved['receiver_cleanup_errors'])


if __name__ == '__main__':
    unittest.main()
