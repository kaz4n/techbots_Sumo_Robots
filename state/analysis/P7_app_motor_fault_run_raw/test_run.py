# Tests the fixed D189 caller from its public contract, without reading its source.
# Preserves real admission/intent owners while substituting only local inputs and transport.
# Freeze before Python -B execution; fresh metadata/evidence in RAM, source bytes read in place.
import contextlib
import copy
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import test_actions as actions_oracle
import test_remote as remote_oracle

REPO = Path(__file__).resolve().parents[3]
RAW = 'state/analysis/P7_app_motor_fault_run_raw/'
COMPILE = 'state/analysis/P7_app_motor_fault_compile_raw/'
STATIC = 'state/analysis/P7_static_startup_raw/'
REVIEW = 'state/reviews/'
SCOPE, OUTPUT = RAW + 'inert_run01_scope.json', RAW + 'native_inert_run01'
PREPARATION, MANIFEST = RAW + 'preparation.json', COMPILE + 'inputs_static.json'
HEAD = 'a' * 40
RUN, SOURCE = remote_oracle.RUN, remote_oracle.SOURCE
REVIEW_FILES = (REVIEW + 'P7_app_motor_fault_caller_review.md',
                REVIEW + 'P7_app_motor_fault_remote_source_review.md')
SCOPE_FILES = (PREPARATION, RAW + 'run.py', RAW + 'actions.py', RAW + 'remote.py',
               RAW + 'test_run.py', RAW + 'test_actions.py', RAW + 'test_remote.py',
               'state/analysis/P7_app_motor_fault_caller_contract.md',
               'state/analysis/P7_app_motor_fault_run_contract.md', *REVIEW_FILES)
PROVENANCE = (MANIFEST, COMPILE + 'native_static01/result.json',
              COMPILE + 'native_static01/artifacts.json',
              COMPILE + 'native_abi_static01/result.json',
              COMPILE + 'native_abi_static01/local_result.json',
              COMPILE + 'abi_static01_interpreted.json',
              COMPILE + 'native_entry_static01/result.json',
              COMPILE + 'native_entry_static01/local_result.json',
              COMPILE + 'native_entry_static01/entry.json',
              REVIEW + 'P7_app_motor_fault_native_actual_review.md',
              REVIEW + 'P7_app_motor_fault_abi_actual_review.md',
              REVIEW + 'P7_app_motor_fault_entry_actual_review.md')
LABELS = {'adapter-claim', 'adapter-push', 'upload', 'capture',
          'cli-initialization', 'cli-builtin-files', 'capabilities'}
CHECKS = ['cli-initialization', 'cli-builtin-files', 'capabilities']
SEQUENCE = ['adapter-claim', 'adapter-push', *CHECKS, 'upload', *CHECKS, 'capture', *CHECKS]
canonical, sha = actions_oracle.canonical, actions_oracle.sha


def source_projection(manifest):
    """D188 public source mapping, independently applied to real pinned inputs."""
    mapped = {}
    for name, expected in manifest['files'].items():
        raw = (REPO / name).read_bytes()
        if sha(raw) != expected:
            raise AssertionError('Actual D188 input drift: ' + name)
        target = None
        if name.startswith('bench/app_motor_fault/'):
            relative = name[len('bench/app_motor_fault/'):]
            target = relative if relative != '.gitkeep' else None
        elif name == 'src/config.h' or name.startswith(('src/core/', 'src/hal/')):
            target = name
        elif name.startswith('src/app/') and not name.startswith('src/app/src/') and Path(name).suffix in ('.c', '.cc', '.cpp', '.h', '.hpp'):
            target = name
        elif name in ('bench/motor_fault/src/motor_fault.h', 'bench/motor_fault/src/motor_fault.cpp'):
            target = 'src/' + Path(name).name
        if target is not None:
            if target in mapped:
                raise AssertionError('Projection collision')
            mapped[target] = raw
    hasher = actions_oracle.REAL_SHA256()
    for name in sorted(mapped):
        hasher.update(name.encode() + b'\0')
        hasher.update(mapped[name])
    if hasher.hexdigest() != SOURCE:
        raise AssertionError('D188 source projection differs from contract')
    return {name: {'bytes': len(raw), 'sha256': sha(raw)} for name, raw in mapped.items()}


@unittest.skipUnless(sys.platform.startswith('linux'), 'Owned /dev/shm fixture required')
class CallerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (sys.flags.dont_write_bytecode and sys.dont_write_bytecode):
            raise RuntimeError('Frozen oracle requires Python -B')
        manifest_raw = (REPO / MANIFEST).read_bytes()
        if sha(manifest_raw) != 'd4eae97c1c47a1ce0fa24c9d7e3ae44857a565cd7b85b9c17be45143654d3eb5':
            raise AssertionError('Original input manifest changed')
        cls.manifest = json.loads(manifest_raw)
        cls.projected = source_projection(cls.manifest)
        cls.receipts = [json.loads((REPO / STATIC / (name + '.json')).read_bytes())
                        for name in ('cli_initialization_inventory', 'cli_builtin_files_inventory')]
        cls.expected = json.loads(cls.receipts[0]['stdout'])['identity']
        cls.expected['boot_id'] = cls.manifest['boot_id']
        with mock.patch.object(subprocess, 'run', side_effect=AssertionError('Native import')), \
             mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Native import')):
            cls.subject = actions_oracle.load(REPO / RAW / 'run.py', 'd189_run_independent_subject')

    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory(prefix='sumox-d189-run-', dir='/dev/shm')))
        (self.root / RAW).mkdir(parents=True)
        self.output = self.root / OUTPUT
        self.events, self.pin_requests, self.failures, self.mutations, self.drift = [], [], {}, {}, {}
        self.preparation = {'schema': 'app-motor-fault-run-preparation-v1', 'run_id': RUN,
                            'source_sha256': SOURCE, 'bindings': {}, 'files': {}}
        for action in ('upload', 'capture'):
            value = remote_oracle.bindings(action)
            value['boot_id'] = self.expected['boot_id']
            self.preparation['bindings'][action] = value
        for name in PROVENANCE:
            raw = (REPO / name).read_bytes()
            self.preparation['files'][name] = {'bytes': len(raw), 'sha256': sha(raw)}
        self.put(PREPARATION, canonical(self.preparation))
        for name in REVIEW_FILES:
            self.put(name, b'# Independent controlled host review fixture\n')
        self.scope = {'schema': 'app-motor-fault-native-scope-v1', 'run_id': RUN,
                      'board': '2629958581', 'source_sha256': SOURCE,
                      'expected_identity': copy.deepcopy(self.expected),
                      'files': {name: sha(self.bytes_at(name)) for name in SCOPE_FILES}}
        self.scope_raw = canonical(self.scope)
        self.put(SCOPE, self.scope_raw)
        self.git_values = {'head': HEAD.encode() + b'\n', 'status': b'',
                           'untracked': b'', 'scope': self.scope_raw}
        self.real_pinned = self.subject.helpers.pinned_file
        self.stack.enter_context(mock.patch.object(self.subject, 'pinned_file', side_effect=self.pinned))
        self.stack.enter_context(mock.patch.object(self.subject.helpers, 'pinned_file', side_effect=self.pinned))
        self.process = self.stack.enter_context(mock.patch.object(subprocess, 'run', side_effect=AssertionError('Native process forbidden')))
        self.stack.enter_context(mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Native child forbidden')))
        self.run = self.subject.InertRun(HEAD, root=self.root)
        self.source_names = {name for name in self.manifest['files'] if name.startswith(
            ('src/', 'bench/app_motor_fault/', 'bench/motor_fault/src/'))}
        self.stack.enter_context(mock.patch.object(self.run, 'source_inventory',
                                                   return_value=set(self.source_names)))
        self.stack.enter_context(mock.patch.object(self.run, 'git', side_effect=self.git))
        self.adb = self.stack.enter_context(mock.patch.object(self.run, 'check_adb', return_value=None))
        self.transport = self.stack.enter_context(mock.patch.object(self.subject.compiler.CompileOnce,
            'transport', autospec=True, side_effect=self.dispatch))

    def put(self, name, raw):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def bytes_at(self, name):
        local = self.root / name
        return (local if local.exists() else REPO / name).read_bytes()

    def pinned(self, root, name, expected):
        """Guarded overlay: real hash/plain-file reads, never unconditional acceptance."""
        self.assertEqual(Path(root), self.root)
        self.pin_requests.append((name, expected))
        if name in self.drift:
            raw = self.drift[name]
            if sha(raw) != expected:
                raise ValueError('Controlled pinned local file changed: ' + name)
            return raw
        path = self.root / name
        actual_root = self.root if os.path.lexists(path) else REPO
        return self.real_pinned(actual_root, name, expected)

    def git(self, *args):
        if args == ('status', '--porcelain', '--untracked-files=all'):
            owned = ''.join('?? ' + path.relative_to(self.root).as_posix() + '\n'
                            for path in sorted(self.output.rglob('*')) if path.is_file())
            return self.git_values['status'] + self.git_values['untracked'] + owned.encode()
        selectors = {('rev-parse', 'HEAD'): 'head',
                     ('status', '--porcelain', '--untracked-files=no'): 'status',
                     ('show', HEAD + ':' + SCOPE): 'scope'}
        if args not in selectors:
            raise AssertionError('Unexpected Git query: ' + repr(args))
        return self.git_values[selectors[args]]

    def save_scope(self):
        self.scope_raw = canonical(self.scope)
        self.put(SCOPE, self.scope_raw)
        self.git_values['scope'] = self.scope_raw

    def save_preparation(self):
        raw = canonical(self.preparation)
        self.put(PREPARATION, raw)
        self.scope['files'][PREPARATION] = sha(raw)
        self.save_scope()

    def capability(self):
        return {'boot_id': self.expected['boot_id'], 'uid': 1000, 'no_bytecode': True,
                'bz2': True, 'base85': True, 'adapter_bytes': 10518,
                'adapter_sha256': actions_oracle.ADAPTER_PIN['sha256'],
                'source_sha256': SOURCE, 'source_files': copy.deepcopy(self.projected)}

    def dispatch(self, owner, arguments, timeout, label):
        self.assertIs(owner, self.run)
        self.assertIn(label, LABELS)
        self.assertEqual(timeout, {'upload': 195, 'capture': 630}.get(label, 60))
        self.assertTrue((self.output / 'inputs.json').is_file())
        if label.startswith('adapter-'):
            self.assertTrue((self.output / 'adapter_attempt.json').is_file())
        if label in ('upload', 'capture'):
            self.assertTrue((self.output / (label + '_attempt.json')).is_file())
        self.events.append(label)
        if label == 'adapter-push':
            self.assertEqual(tuple(arguments), ('push', str(self.root / RAW / 'remote.py'), actions_oracle.STAGED))
            stdout = b'controlled push complete\n'
        else:
            self.assertEqual(list(arguments[:2]), ['shell', '-T'])
            remote = shlex.split(arguments[2])
            if label == 'adapter-claim':
                value = {'uid': 1000, 'user': 'arduino', 'boot_id': self.expected['boot_id'],
                         'cli_sha256': self.preparation['bindings']['upload']['files']['cli']['sha256'],
                         'free_bytes': 1073741824, 'conflicts': []}
            elif label in CHECKS[:2]:
                index = CHECKS.index(label)
                self.assertEqual(remote, self.receipts[index]['argv'])
                value = json.loads(self.receipts[index]['stdout'])
                value['identity'] = copy.deepcopy(self.expected)
            elif label == 'capabilities':
                value = self.capability()
            else:
                self.assertEqual(remote[-3], label)
                value = actions_oracle.envelope(label)
            stdout = canonical(value)
        reply = subprocess.CompletedProcess(arguments, 0, stdout, b'')
        occurrence = self.events.count(label)
        change = self.mutations.get((label, occurrence))
        if change:
            change(reply)
        owner.counter += 1
        folder = self.output / f'{owner.counter:04d}-{label}'
        folder.mkdir()
        failure = self.failures.get((label, occurrence))
        (folder / 'stdout').write_bytes(getattr(failure, 'stdout', None) or reply.stdout)
        (folder / 'stderr').write_bytes(getattr(failure, 'stderr', None) or reply.stderr)
        (folder / 'result.json').write_bytes(canonical({'controlled': True, 'returncode': reply.returncode}))
        if failure:
            raise failure
        return reply, folder

    def mutate(self, label, operation, occurrence=1):
        def change(reply):
            value = json.loads(reply.stdout)
            operation(value)
            reply.stdout = canonical(value)
        self.mutations[label, occurrence] = change

    def record(self, name):
        return json.loads((self.output / name).read_bytes())

    def claim(self, stage=False):
        self.run.admit()
        self.run.claim()
        if stage:
            self.run.stage()

    def rejected(self):
        with self.assertRaises(Exception):
            self.run.admit()
        self.assertFalse(os.path.lexists(self.output))
        self.assertEqual(self.events, [])

    def test_admission_is_local_read_only_and_rechecks_all_127_original_input_hashes(self):
        before = {str(p.relative_to(self.root)): sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
        self.run.admit()
        self.assertEqual(len(self.manifest['files']), 127)
        for name, expected in self.manifest['files'].items():
            self.assertIn((name, expected), self.pin_requests, name)
        first_count = len(self.pin_requests)
        self.run.local()
        for name, expected in self.manifest['files'].items():
            self.assertIn((name, expected), self.pin_requests[first_count:], name)
        after = {str(p.relative_to(self.root)): sha(p.read_bytes()) for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.events, [])
        self.process.assert_not_called()

    def test_actual_source_inventory_matches_the_original_manifest_without_mutation(self):
        candidate = self.subject.InertRun(HEAD, root=REPO)
        self.assertEqual(set(candidate.source_inventory()), self.source_names)
        self.assertEqual(self.events, [])
        self.transport.assert_not_called()

    def test_missing_scope_wrong_head_dirty_tree_or_uncommitted_scope_never_claims(self):
        original = self.scope_raw
        (self.root / SCOPE).unlink()
        self.rejected()
        self.put(SCOPE, original)
        for key, value in (('head', b'b' * 40), ('status', b' M tracked\n'), ('scope', b'{}')):
            old = self.git_values[key]
            self.git_values[key] = value
            with self.subTest(key=key):
                self.rejected()
            self.git_values[key] = old

    def test_unrelated_untracked_files_fail_and_only_claimed_evidence_is_allowed(self):
        self.git_values['untracked'] = b'?? unrelated-evidence.json\n'
        self.rejected()
        self.git_values['untracked'] = b''
        self.claim()
        self.assertTrue((self.output / 'inputs.json').is_file())
        self.run.local()
        self.git_values['untracked'] = b'?? state/analysis/other-attempt/result.json\n'
        with self.assertRaises(Exception):
            self.run.local()
        self.assertEqual(self.events, [])

    def test_scope_shape_source_caller_and_identity_are_exact(self):
        original = copy.deepcopy(self.scope)
        mutations = [lambda v: v.update(extra=1), lambda v: v.update(source_sha256='0' * 64),
                     lambda v: v.update(run_id=RUN + 'x'), lambda v: v.update(board=2629958581),
                     lambda v: v['files'].pop(RAW + 'test_remote.py'),
                     lambda v: v['files'].update({RAW + 'run.py': '0' * 64}),
                     lambda v: v['files'].update({'unscoped': '0' * 64}),
                     lambda v: v['expected_identity'].update(uid=True),
                     lambda v: v['expected_identity'].update(boot_id='invalid')]
        for mutation in mutations:
            self.scope = copy.deepcopy(original)
            mutation(self.scope)
            self.save_scope()
            with self.subTest(mutation=mutations.index(mutation)):
                self.rejected()

    def test_preparation_manifest_and_source_drift_are_rejected(self):
        original = copy.deepcopy(self.preparation)
        mutations = [lambda v: v.update(extra=1), lambda v: v.update(source_sha256='0' * 64),
                     lambda v: v['files'].pop(MANIFEST),
                     lambda v: v['files'][MANIFEST].update(bytes=True),
                     lambda v: v['bindings']['upload']['files']['sketch'].update(sha256='0' * 64)]
        for mutation in mutations:
            self.preparation = copy.deepcopy(original)
            mutation(self.preparation)
            self.save_preparation()
            with self.subTest(mutation=mutations.index(mutation)):
                self.rejected()
        self.preparation = original
        self.save_preparation()
        for name in (MANIFEST, 'src/config.h', 'bench/app_motor_fault/src/app_motor_fault.cpp'):
            self.drift[name] = self.bytes_at(name) + b'\n'
            with self.subTest(drift=name):
                self.rejected()
            self.drift.pop(name)

    def test_linked_scope_and_source_pin_fail_closed_without_source_copies(self):
        scope = self.root / SCOPE
        scope.unlink()
        target = self.root / 'scope-target.json'
        target.write_bytes(self.scope_raw)
        scope.symlink_to(target)
        self.rejected()
        scope.unlink()
        self.put(SCOPE, self.scope_raw)
        path = self.root / 'src/config.h'
        path.parent.mkdir(parents=True)
        path.symlink_to(REPO / 'src/config.h')
        self.rejected()

    def test_claim_and_stage_are_exclusive_durable_and_use_exact_seven_command_allowlist(self):
        self.claim()
        self.assertIsInstance(self.run.allowed, frozenset)
        self.assertEqual(len(self.run.allowed), 7)
        self.assertEqual({item[2] for item in self.run.allowed}, LABELS)
        for arguments, timeout, label in self.run.allowed:
            self.assertIsInstance(arguments, tuple)
            self.assertEqual(timeout, {'upload': 195, 'capture': 630}.get(label, 60))
        self.run.stage()
        self.assertEqual(self.events, ['adapter-claim', 'adapter-push'])
        before = (self.output / 'adapter_attempt.json').read_bytes()
        with self.assertRaises(Exception):
            self.run.stage()
        self.assertEqual((self.output / 'adapter_attempt.json').read_bytes(), before)
        self.assertEqual(len(self.events), 2)
        with self.assertRaises(Exception):
            self.run.claim()

    def test_success_sequence_has_exactly_13_transports_and_unproven_collection(self):
        value = self.run.run()
        self.assertEqual(value['status'], 'COMPLETED')
        self.assertEqual(self.events, SEQUENCE)
        self.assertEqual(self.run.counter, 13)
        self.assertEqual(self.run.command_counts, {name: 3 if name in CHECKS else 1 for name in LABELS})
        self.assertEqual((value['upload_attempts'], value['capture_attempts']), (1, 1))
        self.assertEqual(value['capture']['report']['analysis']['coherence'], 'UNPROVEN')
        self.assertEqual(value['diagnostics']['staging'], {
            'started': True, 'intent_ready': True, 'claim_verified': True,
            'ready': True, 'dispatched': ['adapter-claim', 'adapter-push']})
        self.assertEqual(value, self.record('result.json'))
        self.assertTrue((self.output / 'final_checks.json').is_file())
        with self.assertRaises(Exception):
            self.run.run()
        self.assertEqual(len(self.events), 13)

    def test_staging_uncertainty_consumes_owner_closes_and_never_uploads(self):
        failure = TimeoutError('adapter push uncertain')
        failure.stdout, failure.stderr = b'partial push', b'push interrupted'
        self.failures['adapter-push', 1] = failure
        value = self.run.run()
        self.assertEqual(value['status'], 'FAILED')
        self.assertEqual(value['first_error']['message'], 'adapter push uncertain')
        self.assertEqual((value['upload_attempts'], value['capture_attempts']), (0, 0))
        self.assertEqual(self.events, ['adapter-claim', 'adapter-push', *CHECKS])
        self.assertEqual(value, self.record('result.json'))
        self.assertTrue((self.output / 'adapter_attempt.json').is_file())
        with self.assertRaises(Exception):
            self.run.stage()
        push = next(item for item in self.run.allowed if item[2] == 'adapter-push')
        with self.assertRaises(Exception):
            self.run.transport(*push)
        self.assertNotIn('upload', self.events)

    def test_staging_transport_cannot_bypass_intent_or_verified_claim(self):
        self.claim()
        entries = {label: (argv, timeout, label) for argv, timeout, label in self.run.allowed}
        for label in ('adapter-claim', 'adapter-push'):
            with self.assertRaises(Exception):
                self.run.transport(*entries[label])
        self.assertEqual(self.events, [])
        original = self.run.transport
        checks = []
        def guarded(arguments, timeout, label):
            if label == 'adapter-claim':
                self.assertTrue((self.output / 'adapter_attempt.json').is_file())
                with self.assertRaises(Exception):
                    original(*entries['adapter-push'])
                checks.append('push refused before verified claim')
            return original(arguments, timeout, label)
        with mock.patch.object(self.run, 'transport', side_effect=guarded):
            self.run.stage()
        self.assertEqual(checks, ['push refused before verified claim'])
        self.assertEqual(self.events, ['adapter-claim', 'adapter-push'])

    def test_invalid_staging_identity_prevents_push_and_attempts_closing_checks(self):
        self.mutate('adapter-claim', lambda value: value.update(uid=True))
        value = self.run.run()
        self.assertEqual(value['status'], 'FAILED')
        self.assertEqual(self.events, ['adapter-claim', *CHECKS])
        self.assertEqual((value['upload_attempts'], value['capture_attempts']), (0, 0))

    def test_capability_staged_hash_or_source_names_drift_prevents_upload(self):
        self.mutate('capabilities', lambda value: value.update(adapter_sha256='0' * 64))
        value = self.run.run()
        self.assertEqual(value['status'], 'FAILED')
        self.assertEqual(self.events, ['adapter-claim', 'adapter-push', *CHECKS, *CHECKS])
        self.assertEqual(value['upload_attempts'], 0)
        self.assertEqual(value['capture_attempts'], 0)

    def test_prerequisites_verify_source_projection_and_attempt_all_three(self):
        self.claim(stage=True)
        self.mutate('cli-initialization', lambda value: value['identity'].update(boot_id='wrong'))
        self.mutate('cli-builtin-files', lambda value: value.update(extra_content='changed'))
        self.mutate('capabilities', lambda value: value['source_files'].pop(next(iter(value['source_files']))))
        with self.assertRaises(Exception):
            self.run.prerequisites()
        self.assertEqual(self.events[-3:], CHECKS)
        self.assertGreaterEqual(len(self.run.prerequisite_errors), 3)

    def test_upload_failure_or_outward_error_never_dispatches_capture(self):
        self.mutate('upload', lambda value: value.update(
            first_error={'type': 'OSError', 'message': 'remote close error'},
            report_origin='durable_unattributed'))
        value = self.run.run()
        self.assertEqual(value['status'], 'FAILED')
        self.assertEqual(value['capture_attempts'], 0)
        self.assertEqual(self.events, ['adapter-claim', 'adapter-push', *CHECKS, 'upload', *CHECKS])
        self.assertFalse((self.output / 'capture_attempt.json').exists())

    def test_intent_and_actual_predecessor_hash_are_required_and_consumed(self):
        self.claim(stage=True)
        with self.assertRaises(Exception):
            self.run.action('upload')
        with self.assertRaises(Exception):
            self.run.intent('capture', actions_oracle.envelope('upload'))
        self.run.intent('upload', None)
        before = (self.output / 'upload_attempt.json').read_bytes()
        with self.assertRaises(Exception):
            self.run.intent('upload', None)
        reply = self.run.action('upload')
        changed = copy.deepcopy(reply)
        changed['full_result_sha256'] = '0' * 64
        with self.assertRaises(Exception):
            self.run.intent('capture', changed)
        self.run.intent('capture', reply)
        expected_hash = sha(json.dumps(reply, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode())
        self.assertEqual(self.record('capture_attempt.json')['predecessor_sha256'], expected_hash)
        self.assertEqual((self.output / 'upload_attempt.json').read_bytes(), before)
        with self.assertRaises(Exception):
            self.run.action('upload')

    def test_allowlist_wrong_command_timeout_and_per_label_counts_reject_before_transport(self):
        self.claim(stage=True)
        initial = len(self.events)
        for arguments, timeout, label in self.run.allowed:
            for wrong in ((tuple(arguments) + ('unexpected',), timeout, label),
                          (arguments, timeout + 1, label), (arguments, timeout, 'other')):
                with self.assertRaises(Exception):
                    self.run.transport(*wrong)
        self.assertEqual(len(self.events), initial)
        for _ in range(3):
            self.run.prerequisites()
        with self.assertRaises(Exception):
            self.run.prerequisites()
        self.assertEqual(len(self.events), initial + 9)

    def test_local_drift_after_intent_refuses_dispatch_and_preserves_owner(self):
        self.claim(stage=True)
        self.run.intent('upload', None)
        self.drift['src/config.h'] = b'changed pinned source'
        with self.assertRaises(Exception):
            self.run.action('upload')
        self.assertEqual(self.events, ['adapter-claim', 'adapter-push'])
        self.assertTrue((self.output / 'upload_attempt.json').is_file())

    def test_primary_transport_error_and_closing_errors_are_all_durable(self):
        failure = TimeoutError('upload outcome uncertain')
        failure.stdout, failure.stderr = b'partial action reply', b'transport stderr'
        self.failures['upload', 1] = failure
        self.failures['cli-initialization', 2] = OSError('closing inventory failed')
        self.mutate('capabilities', lambda value: value.update(source_sha256='0' * 64), 2)
        value = self.run.run()
        self.assertEqual(value['status'], 'FAILED')
        self.assertEqual(value['first_error']['message'], 'upload outcome uncertain')
        self.assertEqual(value['capture_attempts'], 0)
        self.assertEqual(self.events[-3:], CHECKS)
        self.assertIn('closing inventory failed', json.dumps(value))
        self.assertEqual(value, self.record('result.json'))
        self.assertIn(b'partial action reply', [path.read_bytes() for path in self.output.rglob('stdout')])

    def test_cli_check_only_has_no_staging_transport_or_owner_and_bad_modes_fail(self):
        with mock.patch.object(self.subject, 'InertRun', return_value=self.run):
            self.assertEqual(self.subject.main(['--check-only', '--reviewed-head', HEAD]), 0)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.events, [])
        bad = [[], ['--reviewed-head', HEAD], ['--execute', '--check-only', '--reviewed-head', HEAD],
               ['--check-only', '--reviewed-head', 'A' * 40],
               ['--check-only', '--reviewed-head', HEAD, '--run', 'run02']]
        for argv in bad:
            with self.subTest(argv=argv), contextlib.redirect_stderr(__import__('io').StringIO()):
                try:
                    result = self.subject.main(argv)
                except SystemExit as error:
                    self.assertNotEqual(error.code, 0)
                else:
                    self.assertNotEqual(result, 0)
        self.assertEqual(self.events, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
