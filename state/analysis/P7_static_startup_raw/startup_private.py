# Reviews the real D155 adapter after inspecting its implementation.
# Exercises scope, fixed transport and evidence boundaries with controlled seams.
# Freeze before Python-B execution; no Git, ADB, CLI or MCU process may run.
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from types import SimpleNamespace
from unittest import mock


HERE = Path(__file__).resolve().parent
HEAD = 'a' * 40
BASE = '/home/arduino/sumox26_codex_build/static-startup-fcddbd8e-run01-'


class StartupAdapterReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('startup_review_subject', HERE / 'startup_run.py')
        cls.subject = importlib.util.module_from_spec(spec)
        with mock.patch.object(subprocess, 'run', side_effect=AssertionError('No native process')):
            with mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('No native process')):
                spec.loader.exec_module(cls.subject)

    def setUp(self):
        for name in ('run', 'Popen'):
            patcher = mock.patch.object(subprocess, name, side_effect=AssertionError('No native process'))
            patcher.start()
            self.addCleanup(patcher.stop)
        self.adapter = self.subject.NativeRun(HEAD)
        self.adapter.check_output = mock.Mock()

    def test_head_requires_exact_commit_clean_tree_and_committed_scope_bytes(self):
        scope = b'{"fixed":"scope"}'
        self.adapter.scope_raw = scope
        for replies in ([HEAD.encode(), b'', scope], [b'b' * 40, b'', scope],
                        [HEAD.encode(), b' M changed.py', scope],
                        [HEAD.encode(), b'', b'{"different":"scope"}']):
            with self.subTest(replies=replies):
                self.adapter.git = mock.Mock(side_effect=replies)
                if replies == [HEAD.encode(), b'', scope]:
                    self.adapter.head()
                    self.assertEqual(self.adapter.git.call_args_list,
                                     [mock.call('rev-parse', 'HEAD'),
                                      mock.call('status', '--porcelain', '--untracked-files=no'),
                                      mock.call('show', HEAD + ':' + self.subject.SCOPE)])
                else:
                    with self.assertRaises(Exception):
                        self.adapter.head()

    def test_scope_rejects_identity_shape_and_unpinned_digest(self):
        scope = {'schema': 'static-startup-run-scope-v1', 'run_id': self.subject.RUN_ID,
                 'board': self.subject.BOARD, 'source_sha256': self.subject.SOURCE,
                 'files': dict.fromkeys(self.subject.SCOPE_FILES, 'b' * 64)}
        candidates = [(scope, True)]
        for field in ('schema', 'run_id', 'board', 'source_sha256'):
            changed = copy.deepcopy(scope)
            changed[field] = 'wrong'
            candidates.append((changed, False))
        changed = copy.deepcopy(scope)
        changed['files'][self.subject.SCOPE_FILES[0]] = 'B' * 64
        candidates.append((changed, False))
        changed = copy.deepcopy(scope)
        changed['files']['extra.py'] = 'b' * 64
        candidates.append((changed, False))
        for candidate, accepted in candidates:
            with self.subTest(candidate=candidate), mock.patch.object(self.subject, 'safe_path'):
                with mock.patch.object(Path, 'read_bytes', return_value=json.dumps(candidate).encode()):
                    if accepted:
                        self.adapter.load_scope()
                        self.assertEqual(self.adapter.scope, candidate)
                    else:
                        with self.assertRaises(Exception):
                            self.adapter.load_scope()

    def prepare_transport(self):
        self.adapter.commands = {'upload': ['fixed-upload'], 'capture': ['fixed-capture']}
        self.adapter.allowed = {(('fixed-file-check',), 60), (('fixed-upload',), 195),
                            (('fixed-capture',), 630)}
        self.adapter.check_adb, self.adapter.local = mock.Mock(), mock.Mock()
        remote = mock.Mock(return_value=SimpleNamespace(returncode=0))
        self.adapter.probe = SimpleNamespace(board=SimpleNamespace(remote=remote))
        return remote

    def test_transport_rejects_unlisted_command_identity_timeout_and_capture_mode(self):
        remote = self.prepare_transport()
        for board, argv, timeout, capture in ((self.subject.BOARD, ['other'], 60, True),
                ('other', ['fixed-file-check'], 60, True),
                (self.subject.BOARD, ['fixed-upload'], 60, True),
                (self.subject.BOARD, ['fixed-file-check'], 60, False)):
            with self.subTest(argv=argv, board=board, timeout=timeout, capture=capture):
                with self.assertRaises(Exception):
                    self.adapter.transport(board, argv, timeout=timeout, capture=capture)
        remote.assert_not_called()
        self.adapter.check_adb.assert_not_called()

    def test_only_fixed_file_checks_survive_separate_local_failure(self):
        remote = self.prepare_transport()
        self.adapter.local.side_effect = RuntimeError('HEAD drift')
        self.adapter.transport(self.subject.BOARD, ['fixed-file-check'], timeout=60)
        remote.assert_called_once_with(self.subject.BOARD, ['fixed-file-check'], capture=True, timeout=60)
        self.adapter.local.assert_not_called()
        remote.reset_mock()
        for action, timeout in (('upload', 195), ('capture', 630)):
            with self.subTest(action=action), self.assertRaisesRegex(RuntimeError, 'HEAD drift'):
                self.adapter.transport(self.subject.BOARD, self.adapter.commands[action], timeout=timeout)
        remote.assert_not_called()
        self.assertEqual(self.adapter.check_adb.call_count, 3)

    def test_output_drift_rejected_before_probe_can_write_numbered_receipts(self):
        for operation in ('packet', 'installed', 'prerequisites', 'action'):
            with self.subTest(operation=operation):
                run = self.subject.NativeRun(HEAD)
                run.check_output = mock.Mock(side_effect=RuntimeError('output replaced'))
                run.probe = SimpleNamespace(remote_postcheck=mock.Mock(), installed_pins=mock.Mock(),
                                            dispatch=mock.Mock())
                run.prerequisite_receipts = [{'argv': ['first']}, {'argv': ['second']}]
                run.intent_actions = {'upload'}
                run.commands = {'upload': ['fixed-upload']}
                with self.assertRaisesRegex(RuntimeError, 'output replaced'):
                    if operation == 'action':
                        run.action('upload')
                    else:
                        getattr(run, operation)()
                run.probe.remote_postcheck.assert_not_called()
                run.probe.installed_pins.assert_not_called()
                run.probe.dispatch.assert_not_called()

    def test_prerequisites_attempt_second_inventory_after_first_failure(self):
        value = {'status': 'COLLECTED', 'identity': {'boot_id': 'fixture'}, 'files': []}
        raw = json.dumps(value)
        self.adapter.prerequisite_receipts = [{'argv': ['first'], 'stdout': raw},
                                         {'argv': ['second'], 'stdout': raw}]
        dispatch = mock.Mock(side_effect=[TimeoutError('first inventory lost'),
                                         SimpleNamespace(stdout=raw, stderr='')])
        self.adapter.probe = SimpleNamespace(dispatch=dispatch, first_identity=value['identity'])
        with self.assertRaisesRegex(TimeoutError, 'first inventory lost'):
            self.adapter.prerequisites()
        self.assertEqual(dispatch.call_args_list,
                         [mock.call(self.subject.BOARD, ['first'], capture=True, timeout=60),
                          mock.call(self.subject.BOARD, ['second'], capture=True, timeout=60)])
        self.assertEqual(self.adapter.prerequisite_errors,
                         [{'check': '0', 'type': 'TimeoutError', 'message': 'first inventory lost'}])

    def test_prerequisite_projection_preserves_pins_types_modes_and_absences(self):
        baseline = {'status': 'COLLECTED', 'identity': {'boot_id': 'fixture'},
                    'file': {'bytes': 10, 'sha256': 'a' * 64, 'mode': 33261,
                             'identity': {'device': 7, 'inode': 8, 'mtime_ns': 1, 'ctime_ns': 2}},
                    'entries': [{'name': 'tools', 'directory': True}], 'absent': True}
        changes = [(('file', 'bytes'), 11), (('file', 'sha256'), 'b' * 64),
                   (('file', 'mode'), 33188), (('file', 'identity', 'inode'), 9),
                   (('entries',), [{'name': 'hardware', 'directory': True}]), (('absent',), False)]
        for path, value in changes:
            candidate = copy.deepcopy(baseline)
            target = candidate
            for part in path[:-1]:
                target = target[part]
            target[path[-1]] = value
            with self.subTest(path=path):
                self.adapter.prerequisite_receipts = [{'argv': ['fixed'], 'stdout': json.dumps(baseline)}]
                self.adapter.probe = SimpleNamespace(first_identity=baseline['identity'],
                    dispatch=mock.Mock(return_value=SimpleNamespace(stdout=json.dumps(candidate), stderr='')))
                with self.assertRaises(Exception):
                    self.adapter.prerequisites()
        only_times = copy.deepcopy(baseline)
        only_times['file']['identity'].update(mtime_ns=100, ctime_ns=200)
        self.assertEqual(self.subject.projection(baseline), self.subject.projection(only_times))

    def test_claim_records_exact_bound_remote_evidence_paths(self):
        self.adapter.output = mock.Mock()
        self.adapter.output.stat.return_value = SimpleNamespace(st_dev=1, st_ino=2)
        self.adapter.write, self.adapter.identity_record = mock.Mock(), mock.Mock(return_value={})
        self.adapter.command_identity = mock.Mock(return_value={})
        self.adapter.commands = {'upload': ['fixed-upload'], 'capture': ['fixed-capture']}
        self.adapter.scope, self.adapter.fixed_pins = {'files': {}}, {}
        self.adapter.runner = SimpleNamespace(PINS={})
        self.adapter.fixed_bytes = {self.subject.RAW + action + '_bindings.json':
                               json.dumps({'output': BASE + action}).encode()
                               for action in self.adapter.commands}
        self.adapter.claim()
        self.adapter.output.mkdir.assert_called_once_with(mode=0o700)
        self.adapter.write.assert_called_once()
        name, value = self.adapter.write.call_args.args
        self.assertEqual(name, 'inputs.json')
        self.assertEqual(value['remote_evidence'], {action: BASE + action for action in self.adapter.commands})

    def test_lost_action_consumes_dispatch_without_retry(self):
        self.adapter.intent_actions = {'upload'}
        self.adapter.commands = {'upload': ['fixed-upload']}
        self.adapter.probe = SimpleNamespace(dispatch=mock.Mock(side_effect=TimeoutError('transport lost')))
        with self.assertRaisesRegex(TimeoutError, 'transport lost'):
            self.adapter.action('upload')
        with self.assertRaises(Exception):
            self.adapter.action('upload')
        self.adapter.probe.dispatch.assert_called_once()

    def test_native_entry_propagates_persisted_failed_outcome_as_failure(self):
        native = SimpleNamespace(operations=mock.Mock(return_value={'fixed': 'callbacks'}))
        with mock.patch.object(self.subject, 'NativeRun', return_value=native):
            with mock.patch.object(self.subject, 'orchestrate', return_value={'status': 'FAILED'}) as run:
                with self.assertRaises(Exception):
                    self.subject.native_run(HEAD)
                run.assert_called_once_with({'fixed': 'callbacks'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
