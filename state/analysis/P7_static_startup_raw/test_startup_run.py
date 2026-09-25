# Tests D155 orchestration from its public contract, without reading its source.
# Keeps upload uncertainty separate from capture permission and startup progress.
# Freeze before first Python-B run; all callbacks are in-memory, with no board I/O.
import copy
import hashlib
import importlib.util
from pathlib import Path
import random
import shlex
import subprocess
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
SOURCE = 'fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2'
RUN = 'static-fcddbd8e-run01'
CHECKS = ('local', 'packet', 'installed', 'prerequisites')
CALLBACKS = ('admit', 'claim', *CHECKS, 'intent', 'upload', 'capture', 'finish')
RESULT_KEYS = {'status', 'upload', 'capture', 'first_error', 'postcheck_errors',
               'upload_attempts', 'capture_attempts'}


def upload_report():
    return {'schema': 'static-upload-result-v1', 'run_id': RUN, 'source_sha256': SOURCE,
            'status': 'UPLOADED', 'attempts': 1,
            'started_utc': '2026-09-25T00:00:00+00:00',
            'finished_utc': '2026-09-25T00:00:01+00:00',
            'started_monotonic': 100.0, 'finished_monotonic': 101.0,
            'subprocess': {'returncode': 0, 'timed_out': False, 'reaped': True},
            'stdout': 'upload diagnostic', 'stderr': 'ordinary stderr',
            'first_error': None, 'postcheck_errors': []}


def capture_report(observation='RUNNING_COUNTER_ADVANCED'):
    reads = []
    for label, base, length in (('before.loader', 0x08000000, 263680),
                                 ('before.sketch', 0x08100000, 93096)):
        reads.extend((label + '.' + str(i), base + offset, min(65536, length - offset))
                     for i, offset in enumerate(range(0, length, 65536)))
    reads.extend((('first.runtime', 0x2003bc98, 28), ('first.transaction', 0x2003b2b0, 24),
                  ('second.runtime', 0x2003bc98, 28), ('second.transaction', 0x2003b2b0, 24)))
    for label, base, length in (('after.sketch', 0x08100000, 93096),
                                 ('after.loader', 0x08000000, 263680)):
        reads.extend((label + '.' + str(i), base + offset, min(65536, length - offset))
                     for i, offset in enumerate(range(0, length, 65536)))
    flash = dict.fromkeys(('before_loader', 'before_sketch', 'after_loader', 'after_sketch'), True)
    return {'schema': 'static-capture-result-v1', 'run_id': RUN, 'source_sha256': SOURCE,
            'status': 'COLLECTED', 'counts': {'commands': 18, 'reads': 18, 'requested_bytes': 713656},
            'started_utc': '2026-09-25T00:00:02+00:00',
            'finished_utc': '2026-09-25T00:00:06+00:00',
            'started_monotonic': 102.0, 'finished_monotonic': 106.0,
            'wait': {'requested_seconds': 2, 'before': 103.0, 'after': 105.0},
            'reads': [{'name': name, 'address': address, 'bytes': size, 'sha256': 'a' * 64,
                       'file': '{:02d}-{}.bin'.format(index, name)}
                      for index, (name, address, size) in enumerate(reads)],
            'first_error': None, 'postcheck_errors': [],
            'analysis': {'flash': flash, 'observation': observation,
                         'runtime': [{}, {}], 'transaction': [{}, {}],
                         'epoch_delta': 1 if observation == 'RUNNING_COUNTER_ADVANCED' else None,
                         'errors': []}}


class Operations:
    def __init__(self):
        self.events, self.counts, self.failures, self.finished = [], {}, {}, None
        self.upload, self.capture = upload_report(), capture_report()
        self.callbacks = {name: self.callback(name) for name in CALLBACKS}

    def callback(self, name):
        def invoke(*args):
            self.events.append((name, copy.deepcopy(args)))
            self.counts[name] = self.counts.get(name, 0) + 1
            failure = self.failures.get((name, self.counts[name]))
            if failure:
                raise failure
            if name in ('upload', 'capture'):
                return copy.deepcopy(getattr(self, name))
            if name == 'finish':
                self.finished = copy.deepcopy(args[0])
        return invoke


class StartupContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('startup_contract_subject', HERE / 'startup_run.py')
        cls.subject = importlib.util.module_from_spec(spec)
        with mock.patch.object(subprocess, 'run', side_effect=AssertionError('Import cannot dispatch')):
            with mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Import cannot dispatch')):
                with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Import cannot read inputs')):
                    with mock.patch.object(Path, 'read_text', side_effect=AssertionError('Import cannot read inputs')):
                        spec.loader.exec_module(cls.subject)

    def setUp(self):
        self.operations = Operations()
        for name in ('run', 'Popen'):
            patcher = mock.patch.object(subprocess, name, side_effect=AssertionError('Native process forbidden'))
            patcher.start()
            self.addCleanup(patcher.stop)

    def run_operations(self, status='FAILED'):
        result = self.subject.orchestrate(self.operations.callbacks)
        self.assertEqual(set(result), RESULT_KEYS)
        self.assertEqual(result['status'], status)
        self.assertEqual(result, self.operations.finished)
        self.assertEqual(result['upload_attempts'], self.operations.counts.get('upload', 0))
        self.assertEqual(result['capture_attempts'], self.operations.counts.get('capture', 0))
        for error in result['postcheck_errors']:
            self.assertEqual(set(error), {'check', 'type', 'message'})
        if status == 'COMPLETED':
            self.assertIsNone(result['first_error'])
            self.assertEqual(result['postcheck_errors'], [])
        else:
            self.assertEqual(set(result['first_error']), {'type', 'message'})
        return result

    def test_success_has_exact_order_and_capture_intent_links_upload(self):
        result = self.run_operations('COMPLETED')
        expected = ['admit', 'claim', *CHECKS, 'intent', 'upload', *CHECKS,
                    'intent', 'capture', *CHECKS, 'finish']
        self.assertEqual([name for name, args in self.operations.events], expected)
        intents = [args for name, args in self.operations.events if name == 'intent']
        self.assertEqual(intents, [('upload', None), ('capture', self.operations.upload)])
        self.assertEqual(result['upload'], self.operations.upload)
        self.assertEqual(result['capture'], self.operations.capture)

    def test_callback_shape_rejected_without_any_callback(self):
        for change in ('extra', 'missing', 'not callable'):
            callbacks = dict(self.operations.callbacks)
            if change == 'extra':
                callbacks['retry'] = lambda: None
            elif change == 'missing':
                del callbacks['packet']
            else:
                callbacks['capture'] = None
            with self.subTest(change=change), self.assertRaises(Exception):
                self.subject.orchestrate(callbacks)
            self.assertEqual(self.operations.events, [])

    def test_admission_failure_never_claims_or_dispatches(self):
        self.operations.failures[('admit', 1)] = RuntimeError('HEAD differs')
        with self.assertRaisesRegex(RuntimeError, 'HEAD differs'):
            self.subject.orchestrate(self.operations.callbacks)
        self.assertEqual([name for name, args in self.operations.events], ['admit'])

    def test_claim_failure_propagates_without_dispatch_or_recovery(self):
        self.operations.failures[('claim', 1)] = OSError('partial claim failure')
        with self.assertRaisesRegex(OSError, 'partial claim failure'):
            self.subject.orchestrate(self.operations.callbacks)
        self.assertEqual([name for name, args in self.operations.events], ['admit', 'claim'])

    def test_initial_source_failure_still_runs_all_final_checks(self):
        self.operations.failures[('local', 1)] = RuntimeError('source drift')
        result = self.run_operations()
        self.assertEqual(result['first_error']['message'], 'source drift')
        self.assertIsNone(result['upload'])
        self.assertIsNone(result['capture'])
        self.assertEqual([name for name, args in self.operations.events][-5:], [*CHECKS, 'finish'])

    def test_upload_intent_failure_leaves_attempt_zero(self):
        self.operations.failures[('intent', 1)] = OSError('intent fsync failed')
        result = self.run_operations()
        self.assertEqual(result['upload_attempts'], 0)
        self.assertEqual(result['capture_attempts'], 0)
        self.assertEqual(result['first_error']['message'], 'intent fsync failed')

    def test_lost_upload_is_unknown_and_never_permits_capture(self):
        self.operations.failures[('upload', 1)] = TimeoutError('upload transport lost')
        result = self.run_operations()
        self.assertEqual((result['upload_attempts'], result['capture_attempts']), (1, 0))
        self.assertIsNone(result['upload'])
        self.assertIsNone(result['capture'])
        self.assertEqual(result['first_error']['message'], 'upload transport lost')

    def test_failed_upload_report_is_preserved_and_suppresses_capture(self):
        self.operations.upload.update(status='FAILED', first_error={'type': 'Error', 'message': 'nonzero'})
        self.operations.upload['subprocess']['returncode'] = 7
        result = self.run_operations()
        self.assertEqual(result['upload'], self.operations.upload)
        self.assertIsNone(result['capture'])

    def test_intermediate_checks_fail_without_capture_intent(self):
        self.operations.failures[('packet', 2)] = RuntimeError('packet changed after upload')
        result = self.run_operations()
        self.assertEqual(result['upload'], self.operations.upload)
        self.assertEqual(result['capture_attempts'], 0)
        self.assertEqual(self.operations.counts['intent'], 1)
        self.assertEqual(result['first_error']['message'], 'packet changed after upload')

    def test_capture_intent_failure_retains_clean_upload(self):
        self.operations.failures[('intent', 2)] = OSError('capture intent failed')
        result = self.run_operations()
        self.assertEqual((result['upload_attempts'], result['capture_attempts']), (1, 0))
        self.assertEqual(result['upload'], self.operations.upload)
        self.assertIsNone(result['capture'])

    def test_lost_capture_preserves_upload_and_unknown_capture(self):
        self.operations.failures[('capture', 1)] = TimeoutError('capture transport lost')
        result = self.run_operations()
        self.assertEqual((result['upload_attempts'], result['capture_attempts']), (1, 1))
        self.assertEqual(result['upload'], self.operations.upload)
        self.assertIsNone(result['capture'])

    def test_failed_capture_report_remains_visible(self):
        self.operations.capture.update(status='FAILED', first_error={'type': 'Error', 'message': 'partial'})
        self.operations.capture['counts'] = {'commands': 1, 'reads': 0, 'requested_bytes': 65536}
        result = self.run_operations()
        self.assertEqual(result['capture'], self.operations.capture)

    def test_fault_and_no_progress_are_completed_collection_not_startup_claims(self):
        for observation in ('SAMPLED_FAULT', 'NO_RUNNING_PROGRESS', 'MALFORMED_SAMPLES'):
            with self.subTest(observation=observation):
                self.operations = Operations()
                self.operations.capture = capture_report(observation)
                result = self.run_operations('COMPLETED')
                self.assertEqual(result['capture']['analysis']['observation'], observation)

    def test_all_final_checks_run_independently(self):
        for name in CHECKS:
            self.operations.failures[(name, 3)] = RuntimeError(name + ' final failure')
        result = self.run_operations()
        self.assertEqual({item['check'] for item in result['postcheck_errors']}, set(CHECKS))
        self.assertEqual(len(result['postcheck_errors']), 4)
        self.assertEqual(result['first_error']['message'], 'local final failure')
        self.assertEqual((result['upload_attempts'], result['capture_attempts']), (1, 1))

    def test_final_failures_never_replace_primary_transport_failure(self):
        self.operations.failures[('upload', 1)] = OSError('primary transport error')
        for name in CHECKS:
            self.operations.failures[(name, 2)] = RuntimeError(name + ' later error')
        result = self.run_operations()
        self.assertEqual(result['first_error'], {'type': 'OSError', 'message': 'primary transport error'})
        self.assertEqual({item['check'] for item in result['postcheck_errors']}, set(CHECKS))

    def test_finish_persistence_failure_raises_instead_of_success(self):
        self.operations.failures[('finish', 1)] = OSError('result not durable')
        with self.assertRaisesRegex(OSError, 'result not durable'):
            self.subject.orchestrate(self.operations.callbacks)
        self.assertEqual(self.operations.counts['capture'], 1)
        self.assertEqual(self.operations.counts['finish'], 1)

    def reject_changed_fields(self, validator, report, changes):
        for path, value in changes:
            with self.subTest(path=path, value=value):
                candidate = copy.deepcopy(report)
                parent = candidate
                for key in path[:-1]:
                    parent = parent[key]
                parent[path[-1]] = value
                with self.assertRaises(Exception):
                    validator(candidate)

    def test_public_validators_accept_valid_reports_without_mutation(self):
        for validator, report in ((self.subject.check_upload, upload_report()),
                                  (self.subject.check_capture, capture_report())):
            before = copy.deepcopy(report)
            validator(report)
            self.assertEqual(before, report)

    def test_upload_identity_exact_schema_and_success_types(self):
        changes = [((name,), value) for name, value in (
            ('schema', 'other'), ('run_id', 'other'), ('source_sha256', 'a' * 64),
            ('status', 'FAILED'), ('attempts', True), ('attempts', 1.0), ('attempts', 2),
            ('stdout', None), ('stderr', b'bytes'), ('first_error', {}),
            ('postcheck_errors', [{'check': 'source', 'type': 'Error', 'message': 'drift'}]))]
        changes += [(('subprocess', 'returncode'), value) for value in (True, 0.0, None, 3)]
        changes += [(('subprocess', 'timed_out'), True), (('subprocess', 'timed_out'), 0),
                    (('subprocess', 'reaped'), False), (('subprocess', 'reaped'), 1)]
        self.reject_changed_fields(self.subject.check_upload, upload_report(), changes)
        for candidate in (None, [], dict(upload_report(), extra=1),
                          {k: v for k, v in upload_report().items() if k != 'stdout'}):
            with self.subTest(candidate=type(candidate)), self.assertRaises(Exception):
                self.subject.check_upload(candidate)

    def test_malformed_upload_is_preserved_and_never_authorizes_capture(self):
        self.operations.upload['attempts'] = True
        result = self.run_operations()
        self.assertEqual(result['upload'], self.operations.upload)
        self.assertEqual(result['capture_attempts'], 0)

    def test_capture_exact_identity_counts_schema_and_error_absence(self):
        changes = [(('run_id',), 'other'), (('source_sha256',), 'a' * 64),
                   (('schema',), 'other'), (('status',), 'FAILED'),
                   (('counts', 'commands'), 17), (('counts', 'commands'), 18.0),
                   (('counts', 'reads'), True), (('counts', 'reads'), 17),
                   (('counts', 'requested_bytes'), 713655),
                   (('counts', 'requested_bytes'), 713656.0), (('first_error',), {}),
                   (('postcheck_errors',), [{'check': 'file', 'type': 'Error', 'message': 'changed'}])]
        self.reject_changed_fields(self.subject.check_capture, capture_report(), changes)
        for candidate in (None, [], dict(capture_report(), extra=1),
                          {k: v for k, v in capture_report().items() if k != 'wait'}):
            with self.assertRaises(Exception):
                self.subject.check_capture(candidate)

    def test_capture_requires_all_exact_ordered_read_descriptions(self):
        report = capture_report()
        changed = list(reversed(report['reads']))
        changes = [(('reads',), []), (('reads',), report['reads'][:-1]),
                   (('reads',), report['reads'] + [report['reads'][0]]), (('reads',), changed),
                   (('reads', 0, 'name'), 'different'), (('reads', 0, 'address'), 0),
                   (('reads', 0, 'address'), float(report['reads'][0]['address'])),
                   (('reads', 0, 'bytes'), 65535), (('reads', 0, 'sha256'), 'A' * 64),
                   (('reads', 0, 'sha256'), 'a' * 63), (('reads', 0, 'file'), '../other.bin')]
        self.reject_changed_fields(self.subject.check_capture, report, changes)

    def test_capture_requires_finite_ordered_timing_and_two_second_wait(self):
        changes = [(('started_monotonic',), True), (('started_monotonic',), float('nan')),
                   (('finished_monotonic',), float('inf')), (('finished_monotonic',), 101.0),
                   (('wait',), None), (('wait', 'requested_seconds'), 0),
                   (('wait', 'before'), float('nan')), (('wait', 'after'), None),
                   (('wait', 'after'), 104.999), (('wait', 'before'), 107.0)]
        self.reject_changed_fields(self.subject.check_capture, capture_report(), changes)

    def test_capture_analysis_is_required_and_shallow_schema_checked(self):
        changes = [(('analysis',), None), (('analysis',), {}),
                   (('analysis', 'observation'), 'INVENTED_SUCCESS'),
                   (('analysis', 'flash', 'before_loader'), 1),
                   (('analysis', 'runtime'), []), (('analysis', 'transaction'), [1, 2]),
                   (('analysis', 'epoch_delta'), True), (('analysis', 'epoch_delta'), -1),
                   (('analysis', 'errors'), 'not a list')]
        self.reject_changed_fields(self.subject.check_capture, capture_report(), changes)

    def test_flash_mismatch_collection_is_not_relabelled_as_transport_failure(self):
        self.operations.capture['analysis'].update(observation='FLASH_MISMATCH', runtime=[],
                                                    transaction=[], epoch_delta=None)
        self.operations.capture['analysis']['flash']['after_loader'] = False
        result = self.run_operations('COMPLETED')
        self.assertEqual(result['capture']['analysis']['observation'], 'FLASH_MISMATCH')

    def test_command_builder_is_pure_fixed_and_payload_hash_bound(self):
        payload = b'{"synthetic":"payload bytes"}'
        for action in ('upload', 'capture'):
            command = self.subject.build_command(action, payload)
            self.assertIs(type(command), list)
            self.assertTrue(all(type(value) is str for value in command))
            self.assertEqual(command[:4], ['python3', '-I', '-B', '-c'])
            self.assertIn(hashlib.sha256(payload).hexdigest(), ' '.join(command))
            self.assertEqual(command, self.subject.build_command(action, payload))
            adb = ['adb.exe', '-s', '2629958581', 'shell', shlex.join(command)]
            units = len(subprocess.list2cmdline(adb).encode('utf-16-le')) // 2 + 1
            self.assertLessEqual(units, 30000)

    def test_command_builder_rejects_unknown_actions_and_nonbytes(self):
        for action, payload in (('reset', b'{}'), ('compile', b'{}'), ('UPLOAD', b'{}'),
                                ('upload', '{}'), ('capture', bytearray(b'{}'))):
            with self.subTest(action=action, payload_type=type(payload)), self.assertRaises(Exception):
                self.subject.build_command(action, payload)

    def test_command_builder_rejects_incompressible_overlong_payload(self):
        payload = random.Random(155).randbytes(50000)
        for action in ('upload', 'capture'):
            with self.subTest(action=action), self.assertRaises(Exception):
                self.subject.build_command(action, payload)

    def test_command_builder_sizes_raw_bytes_without_executing_or_parsing_json(self):
        command = self.subject.build_command('upload', b'\xff\x00\xfe')
        self.assertIs(type(command), list)

    def test_default_unknown_and_incomplete_cli_never_call_native_run(self):
        cases = ([], ['--execute'], ['--reviewed-head', 'a' * 40], ['--unknown'],
                 ['--execute', '--reviewed-head', 'A' * 40],
                 ['--execute', '--reviewed-head', 'a' * 39],
                 ['--execute', '--reviewed-head', 'a' * 40, '--retry'])
        for argv in cases:
            with self.subTest(argv=argv), mock.patch.object(self.subject, 'native_run') as native:
                try:
                    result = self.subject.main(argv)
                except SystemExit as error:
                    self.assertNotEqual(error.code, 0)
                except (ValueError, RuntimeError):
                    pass
                else:
                    self.assertNotEqual(result, 0)
                native.assert_not_called()

    def test_explicit_valid_cli_passes_exact_reviewed_head_to_fixed_entry(self):
        reviewed = '1234567890abcdef1234567890abcdef12345678'
        with mock.patch.object(self.subject, 'native_run', side_effect=RuntimeError('native entry sentinel')) as native:
            try:
                self.subject.main(['--execute', '--reviewed-head', reviewed])
            except RuntimeError:
                pass
        native.assert_called_once_with(reviewed)


if __name__ == '__main__':
    unittest.main(verbosity=2)
