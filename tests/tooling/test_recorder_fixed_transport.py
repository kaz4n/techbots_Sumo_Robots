# Tests the D228 receiver route without ambient transport configuration.
# Exact private ADB selection must match the existing bounded command owner.
# Controlled connection/thread boundaries prevent every native board action.
import os
from pathlib import Path
import unittest
from unittest import mock

from tests.tooling import test_recorder_delivery_receiver as prior


class FixedReceiverTests(prior.ReceiverOwnershipTests):
    @classmethod
    def setUpClass(cls):
        source = Path(os.environ.get('D228_BASELINE_SOURCE',
                                     prior.ROOT / 'tools/run_recorder_delivery.py'))
        cls.subject = prior.load(source, '_d228_fixed_receiver')

    def test_missing_or_conflicting_environment_cannot_select_the_private_route(self):
        self.owner.board.transport = mock.Mock(return_value='ssh')
        self.owner.board.target = mock.Mock(return_value='unrelated-host')
        original = dict(self.owner.board.__dict__)
        for ambient in ({}, {'SUMO_TRANSPORT': 'ssh', 'SUMO_HOST': 'unrelated-host'},
                        {'SUMO_TRANSPORT': 'adb', 'SUMO_ADB_SERIAL': 'other-board'},
                        {'SUMO_TRANSPORT': 'invalid'}):
            with self.subTest(ambient=ambient), mock.patch.dict(os.environ, ambient, clear=True):
                before = dict(os.environ)
                dump = self.subject.receiver_modules(self.owner, self.commands)
                self.assertEqual(dump.board.transport(), 'adb')
                self.assertEqual(dump.board.target(), '2629958581')
                self.assertEqual(dump._validate_connection_request(
                    '2629958581', prior.ATTEMPT, 900), 'adb')
                self.assertEqual(dict(os.environ), before)
                self.assertEqual(self.owner.board.__dict__, original)
                self.assertIs(dump.board.remote.__self__, self.commands)
        self.owner.board.transport.assert_not_called()
        self.owner.board.target.assert_not_called()

    def test_real_connected_iterator_constructs_only_the_fixed_adb_command(self):
        class StopBeforeNative(Exception):
            pass
        with mock.patch.dict(os.environ, {'SUMO_TRANSPORT': 'ssh'}, clear=True), \
                mock.patch.object(self.dump, '_connection_command',
                                  side_effect=StopBeforeNative) as boundary, \
                mock.patch.object(prior.subprocess, 'Popen',
                                  side_effect=AssertionError('Native spawn forbidden')) as spawn:
            capture = self.dump.LiveCapture('2629958581', 900,
                                            connection_ticket=prior.ATTEMPT)
            with self.assertRaises(StopBeforeNative):
                next(iter(capture))
            boundary.assert_called_once_with('2629958581', *self.commands.allowed[0])
            spawn.assert_not_called()

    def test_arm_with_no_environment_uses_private_identity_without_owner_settings(self):
        class Thread:
            def __init__(self, target, **unused):
                self.target = target
            def start(self):
                self.target()
        self.owner.board.target = mock.Mock(side_effect=AssertionError('Ambient owner target used'))
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(self.subject.threading, 'Thread', Thread), \
                mock.patch.object(self.dump, 'save_capture',
                                  return_value=self.owner.output / 'run/capture/complete') as save:
            unused, state = self.subject.arm_receiver(
                self.owner, self.owner.output / 'run', self.dump)
        self.assertIsNone(state['error'])
        self.assertTrue(state['destination'].endswith('complete'))
        capture = save.call_args.args[0]
        self.assertEqual((capture.target, capture.timeout, capture.connection_ticket),
                         ('2629958581', 900, prior.ATTEMPT))
        self.assertEqual(save.call_args.kwargs['receive_mode'], 'adb')
        self.assertEqual(save.call_args.kwargs['expected_session'], prior.SESSION)
        self.owner.board.target.assert_not_called()

    def test_changed_private_binding_is_refused_before_capture_or_thread(self):
        for mode, target in (('ssh', '2629958581'), ('adb', 'wrong'), ('invalid', '2629958581')):
            with self.subTest(mode=mode, target=target):
                dump = self.subject.receiver_modules(self.owner, self.commands)
                dump.board.transport = lambda: mode
                dump.board.target = lambda: target
                with mock.patch.object(dump, 'LiveCapture') as capture, \
                        mock.patch.object(self.subject.threading, 'Thread') as thread, \
                        self.assertRaises(ValueError):
                    self.subject.arm_receiver(self.owner, self.owner.output / 'run', dump)
                capture.assert_not_called()
                thread.assert_not_called()


if __name__ == '__main__':
    unittest.main()
