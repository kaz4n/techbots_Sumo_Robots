# Tests D179's fixed inert caller from its frozen public contract.
# Keeps fresh admission, single-use ownership and error evidence independently checked.
# Freeze before execution; Python -B, small owned RAM fixtures, no real device/process.
"""Authored without reading, importing or executing inert_run.py during drafting."""

import base64
import bz2
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[3]
RAW = 'state/analysis/P7_motor_fault_raw/'
STATIC = 'state/analysis/P7_static_startup_raw/'
HEAD = 'a' * 40
BOOT = '12345678-1234-4234-8234-123456789abc'
RUN = 'motor-fault-8f592937-run01'
SOURCE = '8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
SCOPE = RAW + 'inert_run01_scope.json'
OUTPUT = RAW + 'native_inert_run01'
SCOPED = (RAW + 'inert_run.py', RAW + 'test_inert_run.py',
          'state/analysis/P7_motor_fault_caller_contract.md',
          'state/reviews/P7_motor_fault_caller_review.md')
PINS = {
    STATIC + 'startup_run.py': 'c95888353c9d85c5d9b0e545553a9e9dcde372b5b313102dd14240ce38db4e0c',
    RAW + 'compile_motor_fault.py': '84efd00611b3a6a8129655005930ff58e555221f6bd8d88a23c7fa1c4381ac0d',
    RAW + 'inert_actions.py': '8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104',
    RAW + 'action_preparation.json': '6b5df73026e11914c811ab274054bf4d26ff6b8438e8c9a86ad1ba9bce802835',
    'state/analysis/P7_static_link_probe_raw/static_remote.py': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8',
    STATIC + 'capture_remote.py': '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e',
    STATIC + 'upload_remote.py': 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1',
    STATIC + 'cli_initialization_inventory.json': 'aaa2c307b7ed1b8d7e00a737447a03a63a78cd4b7fb2145142b20e9501da1e62',
    STATIC + 'cli_builtin_files_inventory.json': 'a364beb814b36b9c56328b54a9de5fa0f4ad80a67003d40c7cc994a1917ba2cb',
}
BASELINES = (STATIC + 'cli_initialization_inventory.json', STATIC + 'cli_builtin_files_inventory.json')
PREFIX = ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino',
          'LOGNAME=arduino', 'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C',
          '/usr/bin/python3', '-I', '-B', '-c']


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('ascii')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def local_hash(value):
    # D179 clarification 35f51823 preserves the reused helper's no-LF identity bytes.
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'),
                     ensure_ascii=True, allow_nan=False).encode('utf-8')
    return sha(raw)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def values(value):
    if isinstance(value, dict):
        yield from value.keys()
        for item in value.values():
            yield from values(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from values(item)
    else:
        yield value


class InertCallerContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (sys.flags.dont_write_bytecode and sys.dont_write_bytecode is True):
            raise RuntimeError('Run the frozen oracle with Python -B')
        if not Path('/dev/shm').is_dir():
            raise RuntimeError('This oracle requires an owned /dev/shm RAM fixture')
        cls.fixed = {name: (REPO / name).read_bytes() for name in PINS}
        for name, digest in PINS.items():
            if sha(cls.fixed[name]) != digest:
                raise RuntimeError('Established input pin changed: ' + name)
        cls.preparation = json.loads(cls.fixed[RAW + 'action_preparation.json'])
        for name, record in cls.preparation['provenance'].items():
            cls.fixed[name] = (REPO / name).read_bytes()
            if len(cls.fixed[name]) != record['bytes'] or sha(cls.fixed[name]) != record['sha256']:
                raise RuntimeError('Established provenance changed: ' + name)
        cls.scoped_bytes = {name: (REPO / name).read_bytes() for name in SCOPED[:-1]}
        cls.scoped_bytes[SCOPED[-1]] = b'# Controlled host-only review fixture\n'
        cls.receipts = [json.loads(cls.fixed[name]) for name in BASELINES]
        cls.expected = copy.deepcopy(json.loads(cls.receipts[0]['stdout'])['identity'])
        cls.expected['boot_id'] = BOOT
        before = dict(os.environ)
        with mock.patch.object(subprocess, 'run', side_effect=AssertionError('Import process')), \
             mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Import child')):
            cls.subject = load('d179_independent_subject', REPO / RAW / 'inert_run.py')
            cls.replies = load('d179_established_envelope_fixture', REPO / RAW / 'test_inert_actions.py')
        if dict(os.environ) != before:
            raise AssertionError('Import modified the environment')

    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.temp = self.stack.enter_context(tempfile.TemporaryDirectory(prefix='sumox-d179-', dir='/dev/shm'))
        self.root = Path(self.temp)
        self.output = self.root / OUTPUT
        for name, raw in {**self.fixed, **self.scoped_bytes}.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        self.scope = {'schema': 'motor-fault-native-scope-v1', 'run_id': RUN,
                      'board': '2629958581', 'source_sha256': SOURCE,
                      'expected_identity': copy.deepcopy(self.expected),
                      'files': {name: sha(raw) for name, raw in self.scoped_bytes.items()}}
        self.scope_raw = canonical(self.scope)
        (self.root / SCOPE).write_bytes(self.scope_raw)
        self.events, self.failures, self.reply_changes = [], {}, {}
        self.git_values = {'head': HEAD.encode() + b'\n', 'status': b'', 'scope': self.scope_raw}
        self.process = self.stack.enter_context(mock.patch.object(
            subprocess, 'run', side_effect=AssertionError('No real process')))
        self.stack.enter_context(mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('No real child')))
        self.env_before = dict(os.environ)
        self.run = self.subject.InertRun(HEAD, root=self.root)
        self.assertEqual(self.env_before, dict(os.environ))
        self.assertFalse(self.output.exists())
        self.stack.enter_context(mock.patch.object(self.run, 'git', side_effect=self.git))
        self.adb = self.stack.enter_context(mock.patch.object(self.run, 'check_adb', return_value=None))
        self.transport = self.stack.enter_context(mock.patch.object(
            self.subject.compiler.CompileOnce, 'transport', autospec=True, side_effect=self.dispatch))

    def git(self, *args):
        if args == ('rev-parse', 'HEAD'):
            return self.git_values['head']
        if args == ('status', '--porcelain', '--untracked-files=no'):
            return self.git_values['status']
        if args == ('show', HEAD + ':' + SCOPE):
            return self.git_values['scope']
        raise AssertionError('Unexpected Git request: ' + repr(args))

    def save_scope(self, value=None, raw=None):
        self.scope_raw = canonical(self.scope if value is None else value) if raw is None else raw
        (self.root / SCOPE).write_bytes(self.scope_raw)
        self.git_values['scope'] = self.scope_raw

    def dispatch(self, owner, arguments, timeout, label):
        self.assertIs(owner, self.run)
        self.assertEqual(['shell', '-T'], list(arguments[:2]))
        remote = shlex.split(arguments[2])
        kind = next((str(i) for i, item in enumerate(self.receipts) if remote == item['argv']), None)
        if kind is None:
            kind = remote[-3] if len(remote) >= 3 and remote[-3] in ('upload', 'capture') else 'capability'
        self.events.append(kind)
        expected_label = {'0': 'cli-initialization', '1': 'cli-builtin-files',
                          'capability': 'capabilities', 'upload': 'upload', 'capture': 'capture'}[kind]
        self.assertEqual(expected_label, label)
        self.assertTrue((self.output / 'inputs.json').is_file(), 'Transport preceded durable inputs')
        if kind in ('upload', 'capture'):
            self.assertTrue((self.output / (kind + '_attempt.json')).is_file())
            self.assertEqual(195 if kind == 'upload' else 630, timeout)
            value = self.replies.envelope(kind)
        elif kind == 'capability':
            self.assertEqual(PREFIX, remote[:len(PREFIX)])
            self.assertEqual(60, timeout)
            value = {'boot_id': BOOT, 'uid': 1000, 'no_bytecode': True, 'bz2': True, 'base85': True}
        else:
            self.assertEqual(60, timeout)
            value = json.loads(self.receipts[int(kind)]['stdout'])
            value['identity'] = copy.deepcopy(self.expected)
        occurrence = self.events.count(kind)
        reply = subprocess.CompletedProcess(arguments, 0, canonical(value), b'')
        change = self.reply_changes.get((kind, occurrence))
        if change:
            change(reply)
        owner.counter += 1
        folder = self.output / f'{owner.counter:04d}-{label}'
        folder.mkdir()
        failure = self.failures.get((kind, occurrence))
        raw_stdout = getattr(failure, 'stdout', None) or reply.stdout
        (folder / 'stdout').write_bytes(raw_stdout if type(raw_stdout) is bytes else repr(raw_stdout).encode())
        (folder / 'stderr').write_bytes(getattr(failure, 'stderr', None) or reply.stderr)
        (folder / 'result.json').write_bytes(canonical({'controlled': True, 'returncode': reply.returncode}))
        if failure:
            raise failure
        return reply, folder

    def claim(self):
        self.run.admit()
        self.run.claim()

    def rejected_admit(self):
        with self.assertRaises(Exception):
            self.run.admit()
        self.assertFalse(os.path.lexists(self.output))
        self.assertEqual([], self.events)
        self.process.assert_not_called()

    def record(self, name):
        return json.loads((self.output / name).read_bytes())

    def mutate_reply(self, kind, mutate, occurrence=1):
        def change(reply):
            value = json.loads(reply.stdout)
            mutate(value)
            reply.stdout = canonical(value)
        self.reply_changes[(kind, occurrence)] = change

    def test_missing_scope_stops_before_claim_adb_or_transport(self):
        (self.root / SCOPE).unlink()
        with self.assertRaises(Exception):
            self.run.run()
        self.assertFalse(self.output.exists())
        self.adb.assert_not_called()
        self.transport.assert_not_called()

    def test_admit_fresh_boot_is_local_read_only_and_leaves_environment(self):
        before = {str(path.relative_to(self.root)): sha(path.read_bytes())
                  for path in self.root.rglob('*') if path.is_file()}
        self.run.admit()
        after = {str(path.relative_to(self.root)): sha(path.read_bytes())
                 for path in self.root.rglob('*') if path.is_file()}
        self.assertEqual(before, after)
        self.assertEqual(self.env_before, dict(os.environ))
        self.assertNotEqual(BOOT, self.preparation['bindings']['upload']['boot_id'])
        self.assertFalse(self.output.exists())
        self.transport.assert_not_called()

    def test_scope_rejects_nonclosed_types_identity_hash_and_noncanonical_boot(self):
        changes = [lambda v: v.update(extra=1), lambda v: v.pop('board'),
                   lambda v: v.update(schema='wrong'), lambda v: v.update(board=2629958581),
                   lambda v: v.update(run_id='other'), lambda v: v.update(source_sha256='b' * 64),
                   lambda v: v['files'].pop(SCOPED[0]),
                   lambda v: v['files'].update({'unexpected': 'a' * 64}),
                   lambda v: v['files'].update({SCOPED[0]: 'A' * 64}),
                   lambda v: v['expected_identity'].update(extra=1),
                   lambda v: v['expected_identity'].update(uid=True),
                   lambda v: v['expected_identity'].update(machine='x86_64'),
                   lambda v: v['expected_identity'].update(boot_id=''),
                   lambda v: v['expected_identity'].update(boot_id=BOOT.upper()),
                   lambda v: v['expected_identity'].update(boot_id=BOOT.replace('-', ''))]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                value = copy.deepcopy(self.scope)
                change(value)
                self.save_scope(value)
                self.rejected_admit()

    def test_scope_rejects_duplicate_nonfinite_and_oversize_json(self):
        for raw in (b'{"schema":0,"schema":1}', b'{"schema":NaN}', b' ' * 65537,
                    canonical(self.scope).rstrip() + b'{}'):
            with self.subTest(raw=raw[:40]):
                self.save_scope(raw=raw)
                self.rejected_admit()

    def test_reviewed_head_clean_tree_committed_scope_and_B_are_required(self):
        for key, bad in (('head', b'b' * 40), ('status', b' M tracked.py\n'), ('scope', b'{}')):
            with self.subTest(key=key):
                old = self.git_values[key]
                self.git_values[key] = bad
                self.rejected_admit()
                self.git_values[key] = old
        with mock.patch.object(sys, 'dont_write_bytecode', False):
            self.rejected_admit()
        for bad in ('A' * 40, 'a' * 39, None, True):
            with self.subTest(head=bad), self.assertRaises(Exception):
                candidate = self.subject.InertRun(bad, root=self.root)
                candidate.admit()

    def test_each_fixed_scoped_and_provenance_pin_is_checked(self):
        for name in (*self.fixed, *SCOPED):
            with self.subTest(name=name):
                path = self.root / name
                original = path.read_bytes()
                path.write_bytes(original + b'\n')
                self.rejected_admit()
                path.write_bytes(original)

    def test_claim_rechecks_pins_and_keeps_existing_or_dangling_owners(self):
        self.run.admit()
        path = self.root / SCOPED[1]
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaises(Exception):
            self.run.claim()
        self.assertFalse(self.output.exists())
        path.write_bytes(self.scoped_bytes[SCOPED[1]])
        self.output.symlink_to(self.root / 'missing-owner', target_is_directory=True)
        self.rejected_admit()
        self.assertTrue(self.output.is_symlink())

    def test_linked_scope_and_pin_are_rejected_without_following(self):
        for name in (SCOPE, SCOPED[1], STATIC + 'capture_remote.py'):
            with self.subTest(name=name):
                path = self.root / name
                raw = path.read_bytes()
                target = self.root / 'symlink-target'
                target.write_bytes(raw)
                path.unlink()
                path.symlink_to(target)
                self.rejected_admit()
                path.unlink()
                path.write_bytes(raw)
                target.unlink()

    def test_claim_is_exclusive_and_inputs_bind_all_local_and_command_identities(self):
        self.claim()
        record_values = list(values(self.record('inputs.json')))
        for required in (RUN, SOURCE, HEAD, sha(self.scope_raw), BOOT, '2629958581'):
            self.assertIn(required, record_values)
        for name, raw in {**self.fixed, **self.scoped_bytes}.items():
            self.assertIn(sha(raw), record_values, name)
        self.assertEqual(set(self.run.commands), {'upload', 'capture'})
        for action, command in self.run.commands.items():
            native = [ADB, '-s', '2629958581', 'shell', '-T', shlex.join(command)]
            units = len(subprocess.list2cmdline(native).encode('utf-16-le')) // 2 + 1
            self.assertLessEqual(units, 30000)
            self.assertIn(units, record_values)
            self.assertIn(local_hash(command), record_values)
        before = (self.output / 'inputs.json').read_bytes()
        with self.assertRaises(Exception):
            self.run.claim()
        self.assertEqual(before, (self.output / 'inputs.json').read_bytes())
        self.assertEqual([], self.events)

    def test_claim_write_failure_retains_owner_and_never_calls_device(self):
        self.run.admit()
        failure = OSError('inputs fsync denied')
        with mock.patch.object(self.run, 'write', side_effect=failure), self.assertRaises(OSError) as caught:
            self.run.claim()
        self.assertIs(failure, caught.exception)
        self.assertTrue(self.output.is_dir())
        self.transport.assert_not_called()
        with self.assertRaises(Exception):
            self.run.claim()

    def test_actual_commands_use_exact_sources_and_only_replace_binding_boot(self):
        self.run.admit()
        original = copy.deepcopy(self.preparation)
        roles = {'helper': 'state/analysis/P7_static_link_probe_raw/static_remote.py',
                 'support': STATIC + 'capture_remote.py', 'upload': STATIC + 'upload_remote.py'}
        for action, command in self.run.commands.items():
            self.assertEqual(PREFIX, list(command[:len(PREFIX)]))
            self.assertEqual(action, command[-3])
            token = command[-1]
            compressed = base64.b85decode(token[4:]) if token.startswith('b85:') else base64.b64decode(token, validate=True)
            raw = bz2.decompress(compressed)
            self.assertEqual(command[-2], sha(raw))
            payload = json.loads(raw)
            self.assertEqual(raw, canonical(payload))
            wanted = copy.deepcopy(self.preparation['bindings'][action])
            wanted['boot_id'] = BOOT
            self.assertEqual(wanted, payload['bindings'])
            self.assertEqual({'helper', 'support', 'upload'} if action == 'upload' else {'helper', 'support'}, set(payload['sources']))
            for role, item in payload['sources'].items():
                self.assertEqual(self.fixed[roles[role]], item['source'].encode('utf-8'))
                self.assertEqual(PINS[roles[role]], item['sha256'])
        self.assertEqual(original, self.preparation)

    def test_fresh_binding_does_not_mutate_historical_module_globals(self):
        compiler, helpers = self.subject.compiler, self.subject.helpers
        before = (compiler.BOOT, compiler.ROOT, compiler.ADB, compiler.ADB_SHA,
                  copy.deepcopy(helpers.DEPENDENCIES), helpers.SOURCE, helpers.RUN_ID)
        self.run.admit()
        after = (compiler.BOOT, compiler.ROOT, compiler.ADB, compiler.ADB_SHA,
                 copy.deepcopy(helpers.DEPENDENCIES), helpers.SOURCE, helpers.RUN_ID)
        self.assertEqual(before, after)
        self.assertEqual(self.env_before, dict(os.environ))

    def test_windows_ceiling_includes_trailing_nul(self):
        compose = self.subject.actions.build_command
        def exactly_without_nul(action, sources, bindings):
            command = list(compose(action, sources, bindings))
            native = [ADB, '-s', '2629958581', 'shell', '-T', shlex.join(command)]
            units = len(subprocess.list2cmdline(native).encode('utf-16-le')) // 2
            command[-1] += 'x' * (30000 - units)
            self.assertEqual(30000, len(subprocess.list2cmdline(
                [ADB, '-s', '2629958581', 'shell', '-T', shlex.join(command)]).encode('utf-16-le')) // 2)
            return command
        with mock.patch.object(self.subject.actions, 'build_command', side_effect=exactly_without_nul):
            self.rejected_admit()

    def test_prerequisites_accept_fresh_identity_and_ignored_timestamps(self):
        self.claim()
        def timestamps(value):
            value['mtime_ns'] = 987654321
            value['ctime_ns'] = 123456789
        self.mutate_reply('0', timestamps)
        self.mutate_reply('1', timestamps)
        self.run.prerequisites()
        self.assertEqual(['0', '1', 'capability'], self.events)

    def test_prerequisites_attempt_all_three_and_preserve_every_failure(self):
        self.claim()
        failures = [OSError('first prerequisite'), ValueError('second prerequisite'), TimeoutError('capability timeout')]
        for kind, failure in zip(('0', '1', 'capability'), failures):
            self.failures[(kind, 1)] = failure
        with self.assertRaises(Exception) as caught:
            self.run.prerequisites()
        self.assertIs(caught.exception, failures[0])
        self.assertEqual(['0', '1', 'capability'], self.events)
        diagnostic = json.dumps(self.run.prerequisite_errors)
        for failure in failures:
            self.assertIn(str(failure), diagnostic)

    def test_prerequisites_reject_identity_status_and_non_timestamp_content_drift(self):
        self.claim()
        mutations = [lambda v: v['identity'].update(boot_id=self.preparation['bindings']['upload']['boot_id']),
                     lambda v: v['identity'].update(machine='x86_64'),
                     lambda v: v.update(status='FAILED')]
        for index, mutation in enumerate(mutations, 1):
            with self.subTest(case=index):
                self.mutate_reply('0', mutation, index)
                with self.assertRaises(Exception):
                    self.run.prerequisites()
                self.assertEqual(['0', '1', 'capability'], self.events[-3:])

    def test_prerequisites_compare_all_content_after_removing_checked_identity(self):
        self.claim()
        self.mutate_reply('0', lambda value: value.update(unexpected_remaining_content=1))
        self.mutate_reply('1', lambda value: value.update(unexpected_remaining_content=2))
        with self.assertRaises(Exception):
            self.run.prerequisites()
        self.assertEqual(2, len(self.run.prerequisite_errors))
        self.assertEqual(['0', '1', 'capability'], self.events)

    def test_baseline_replies_require_int_zero_bytes_no_stderr_and_bounded_json(self):
        self.claim()
        cases = [(True, b'{}', b''), (0, b'{}', b'warning'),
                 (0, b'x' * 1048577, b''), (0, b'{"x":0,"x":1}', b''),
                 (0, b'{"x":NaN}', b''), (0, '{}', b'')]
        # Both baseline replies are tested in each independent query set; at most nine calls.
        for index in range(3):
            errors_before = len(self.run.prerequisite_errors)
            for kind, spec in zip(('0', '1'), cases[index * 2:index * 2 + 2]):
                def change(reply, spec=spec):
                    reply.returncode, reply.stdout, reply.stderr = spec
                self.reply_changes[(kind, index + 1)] = change
            with self.subTest(case=index), self.assertRaises(Exception):
                self.run.prerequisites()
            self.assertEqual(['0', '1', 'capability'], self.events[-3:])
            self.assertEqual(errors_before + 2, len(self.run.prerequisite_errors))

    def test_capability_rejects_wrong_boot_bool_uid_and_nonliteral_flags(self):
        self.claim()
        for index, mutation in enumerate((lambda v: v.update(boot_id='old'),
                                          lambda v: v.update(uid=True),
                                          lambda v: v.update(bz2=1)), 1):
            self.mutate_reply('capability', mutation, index)
            with self.subTest(case=index), self.assertRaises(Exception):
                self.run.prerequisites()

    def test_capability_rejects_extra_keys_no_bytecode_and_oversize(self):
        self.claim()
        self.mutate_reply('capability', lambda v: v.update(extra=True), 1)
        self.mutate_reply('capability', lambda v: v.update(no_bytecode=False), 2)
        self.reply_changes[('capability', 3)] = lambda reply: setattr(reply, 'stdout', b' ' * 4097)
        for index in range(3):
            with self.subTest(case=index), self.assertRaises(Exception):
                self.run.prerequisites()

    def test_local_checks_continue_after_head_failure_and_record_independent_errors(self):
        self.claim()
        self.git_values['head'] = b'b' * 40
        (self.root / SCOPE).write_bytes(b'changed scope')
        path = self.root / STATIC / 'capture_remote.py'
        path.write_bytes(path.read_bytes() + b'\n')
        self.adb.side_effect = OSError('ADB local drift')
        with self.assertRaises(Exception):
            self.run.local()
        recorded = json.dumps(self.run.local_errors)
        for text in ('head', 'scope', 'ADB local drift', 'capture_remote.py'):
            self.assertIn(text, recorded)
        self.assertEqual([], self.events)

    def test_intent_requires_order_valid_predecessor_and_never_overwrites(self):
        self.claim()
        for action, predecessor in (('capture', self.replies.envelope('upload')),
                                    ('upload', {}), ('reset', None)):
            with self.subTest(action=action), self.assertRaises(Exception):
                self.run.intent(action, predecessor)
        self.run.intent('upload', None)
        before = (self.output / 'upload_attempt.json').read_bytes()
        with self.assertRaises(Exception):
            self.run.intent('upload', None)
        self.assertEqual(before, (self.output / 'upload_attempt.json').read_bytes())
        self.assertEqual([], self.events)
        self.run.action('upload')
        broken = self.replies.envelope('upload')
        broken['report']['subprocess']['returncode'] = 1
        with self.assertRaises(Exception):
            self.run.intent('capture', broken)
        predecessor = self.replies.envelope('upload')
        self.run.intent('capture', predecessor)
        record_values = list(values(self.record('capture_attempt.json')))
        self.assertIn(local_hash(predecessor), record_values)
        for value in (SOURCE, sha(self.scope_raw)):
            self.assertIn(value, record_values)

    def test_action_requires_durable_intent_and_is_consumed_before_transport_failure(self):
        self.claim()
        with self.assertRaises(Exception):
            self.run.action('upload')
        self.assertEqual([], self.events)
        self.run.intent('upload', None)
        failure = TimeoutError('native dispatch uncertain')
        failure.stdout, failure.stderr = b'partial remote stdout', b'partial remote stderr'
        self.failures[('upload', 1)] = failure
        with self.assertRaises(TimeoutError) as caught:
            self.run.action('upload')
        self.assertIs(failure, caught.exception)
        with self.assertRaises(Exception):
            self.run.action('upload')
        self.assertEqual(['upload'], self.events)
        self.assertIn(b'partial remote stdout', [p.read_bytes() for p in self.output.rglob('stdout')])
        self.assertIn(b'partial remote stderr', [p.read_bytes() for p in self.output.rglob('stderr')])
        self.assertIn('native dispatch uncertain', json.dumps(self.run.transport_errors))

    def test_action_rechecks_local_drift_without_dispatch(self):
        self.claim()
        self.run.intent('upload', None)
        path = self.root / SCOPED[2]
        path.write_bytes(path.read_bytes() + b'\n')
        with self.assertRaises(Exception):
            self.run.action('upload')
        self.assertEqual([], self.events)

    def test_action_command_mutation_is_immutable_or_rejected_before_transport(self):
        self.claim()
        self.run.intent('upload', None)
        changed = list(self.run.commands['upload'])
        changed[-1] += 'x'
        try:
            self.run.commands['upload'] = changed
        except (TypeError, AttributeError):
            pass
        else:
            with self.assertRaises(Exception):
                self.run.action('upload')
        self.assertEqual([], self.events)

    def test_replaced_owner_inode_is_rejected_and_original_files_survive(self):
        self.claim()
        retained = self.output.with_name('retained-controlled-owner')
        self.output.rename(retained)
        self.output.mkdir()
        with self.assertRaises(Exception):
            self.run.write('extra.json', {})
        self.assertTrue((retained / 'inputs.json').is_file())
        self.assertFalse((self.output / 'extra.json').exists())
        self.assertEqual([], self.events)

    def test_exact_successful_sequence_has_eleven_transports_and_two_actions(self):
        result = self.run.run()
        self.assertEqual('COMPLETED', result['status'])
        self.assertEqual(['0', '1', 'capability', 'upload', '0', '1', 'capability',
                          'capture', '0', '1', 'capability'], self.events)
        self.assertEqual(11, self.run.counter)
        self.assertEqual((1, 1), (result['upload_attempts'], result['capture_attempts']))
        self.assertEqual(result, self.record('result.json'))
        self.assertTrue((self.output / 'final_checks.json').is_file())
        self.assertEqual('UNPROVEN', result['capture']['report']['analysis']['coherence'])
        with self.assertRaises(Exception):
            self.run.run()
        self.assertEqual(11, len(self.events))

    def test_upload_transport_failure_skips_capture_and_runs_final_prerequisites(self):
        failure = OSError('upload primary failure')
        self.failures[('upload', 1)] = failure
        result = self.run.run()
        self.assertEqual('FAILED', result['status'])
        self.assertEqual('upload primary failure', result['first_error']['message'])
        self.assertEqual((1, 0), (result['upload_attempts'], result['capture_attempts']))
        self.assertEqual(['0', '1', 'capability', 'upload', '0', '1', 'capability'], self.events)
        self.assertIsNone(result['capture'])
        self.assertFalse((self.output / 'capture_attempt.json').exists())
        self.assertEqual(result, self.record('result.json'))

    def test_capture_transport_failure_preserves_checked_upload_and_closes(self):
        self.failures[('capture', 1)] = TimeoutError('capture transport lost')
        result = self.run.run()
        self.assertEqual('FAILED', result['status'])
        self.assertEqual('UPLOADED', result['upload']['report']['status'])
        self.assertIsNone(result['capture'])
        self.assertEqual(11, len(self.events))
        self.assertEqual(['0', '1', 'capability'], self.events[-3:])
        self.assertEqual(result, self.record('result.json'))

    def test_upload_bad_envelope_preserves_raw_reply_and_never_captures(self):
        self.mutate_reply('upload', lambda value: value['report'].update(status='FAILED'))
        result = self.run.run()
        self.assertEqual('FAILED', result['status'])
        self.assertEqual('FAILED', result['upload']['report']['status'])
        self.assertEqual(0, result['capture_attempts'])
        self.assertNotIn('capture', self.events)

    def test_action_rejects_duplicate_json_with_raw_retention(self):
        self.claim()
        self.run.intent('upload', None)
        raw = b'{"schema":"a","schema":"b"}'
        self.reply_changes[('upload', 1)] = lambda reply: setattr(reply, 'stdout', raw)
        with self.assertRaises(Exception):
            self.run.action('upload')
        self.assertIn(raw, [path.read_bytes() for path in self.output.rglob('stdout')])
        self.assertEqual(['upload'], self.events)

    def test_action_nonzero_returncode_is_rejected_without_capture(self):
        self.reply_changes[('upload', 1)] = lambda reply: setattr(reply, 'returncode', 7)
        result = self.run.run()
        self.assertEqual('FAILED', result['status'])
        self.assertNotIn('capture', self.events)

    def test_action_stderr_is_rejected_without_capture(self):
        self.reply_changes[('upload', 1)] = lambda reply: setattr(reply, 'stderr', b'unexpected warning')
        result = self.run.run()
        self.assertEqual('FAILED', result['status'])
        self.assertNotIn('capture', self.events)
        self.assertIn(b'unexpected warning', [path.read_bytes() for path in self.output.rglob('stderr')])

    def test_capture_invalid_envelope_retains_both_raw_reports(self):
        self.mutate_reply('capture', lambda value: value['report']['analysis'].update(coherence='PROVEN'))
        result = self.run.run()
        self.assertEqual('FAILED', result['status'])
        self.assertEqual('UPLOADED', result['upload']['report']['status'])
        self.assertEqual('PROVEN', result['capture']['report']['analysis']['coherence'])
        self.assertEqual(11, len(self.events))

    def test_action_oversize_reply_cannot_admit_capture(self):
        self.reply_changes[('upload', 1)] = lambda reply: setattr(reply, 'stdout', b' ' * 65537)
        result = self.run.run()
        self.assertEqual('FAILED', result['status'])
        self.assertNotIn('capture', self.events)
        self.assertIn(b' ' * 65537, [path.read_bytes() for path in self.output.rglob('stdout')])

    def test_finish_preserves_primary_and_attempts_both_writes_after_final_write_error(self):
        self.failures[('upload', 1)] = RuntimeError('first action error')
        original = self.run.write
        attempts = []
        failure = OSError('final checks disk error')
        def write(name, value):
            attempts.append(name)
            if name == 'final_checks.json':
                raise failure
            return original(name, value)
        with mock.patch.object(self.run, 'write', side_effect=write), self.assertRaises(OSError) as caught:
            self.run.run()
        self.assertIs(failure, caught.exception)
        self.assertEqual(['final_checks.json', 'result.json'], attempts[-2:])
        saved = self.record('result.json')
        self.assertEqual('FAILED', saved['status'])
        self.assertEqual('first action error', saved['first_error']['message'])
        self.assertIn('final checks disk error', json.dumps(saved))
        self.assertEqual('first action error', caught.exception.sequence_result['first_error']['message'])

    def test_success_is_failed_before_result_write_when_final_checks_write_fails(self):
        original = self.run.write
        def write(name, value):
            if name == 'final_checks.json':
                raise OSError('first closure failure')
            return original(name, value)
        with mock.patch.object(self.run, 'write', side_effect=write), self.assertRaises(OSError) as caught:
            self.run.run()
        self.assertEqual('FAILED', self.record('result.json')['status'])
        self.assertEqual('FAILED', caught.exception.sequence_result['status'])

    def test_wrong_final_counter_fails_after_both_closure_writes(self):
        original = self.run.finish
        def finish(result):
            self.run.counter -= 1
            return original(result)
        with mock.patch.object(self.run, 'finish', side_effect=finish), self.assertRaises(Exception) as caught:
            self.run.run()
        self.assertEqual('FAILED', self.record('result.json')['status'])
        self.assertTrue((self.output / 'final_checks.json').is_file())
        self.assertEqual('FAILED', caught.exception.sequence_result['status'])

    def test_both_closure_write_failures_retain_first_exception_and_partial_owner(self):
        original = self.run.write
        failures = {'final_checks.json': OSError('first journal failure'),
                    'result.json': ValueError('second journal failure')}
        attempts = []
        def write(name, value):
            attempts.append(name)
            if name in failures:
                raise failures[name]
            return original(name, value)
        with mock.patch.object(self.run, 'write', side_effect=write), self.assertRaises(OSError) as caught:
            self.run.run()
        self.assertIs(failures['final_checks.json'], caught.exception)
        self.assertEqual(['final_checks.json', 'result.json'], attempts[-2:])
        self.assertEqual('FAILED', caught.exception.sequence_result['status'])
        self.assertIn('second journal failure', json.dumps(caught.exception.sequence_result))
        self.assertTrue((self.output / 'inputs.json').is_file())

    def test_final_prerequisite_errors_do_not_replace_first_action_failure(self):
        self.failures[('upload', 1)] = RuntimeError('original upload error')
        for kind in ('0', '1', 'capability'):
            self.failures[(kind, 2)] = OSError('closing ' + kind)
        result = self.run.run()
        self.assertEqual('original upload error', result['first_error']['message'])
        diagnostics = json.dumps(self.record('final_checks.json'))
        for kind in ('0', '1', 'capability'):
            self.assertIn('closing ' + kind, diagnostics)
        self.assertEqual(['0', '1', 'capability'], self.events[-3:])

    def test_transport_retains_causal_chain_without_replacing_thrown_exception(self):
        self.claim()
        self.run.intent('upload', None)
        error = OSError('deep cause 0')
        for index in range(1, 10):
            outer = RuntimeError('deep cause ' + str(index))
            outer.__cause__ = error
            error = outer
        self.failures[('upload', 1)] = error
        with self.assertRaises(RuntimeError) as caught:
            self.run.action('upload')
        self.assertIs(error, caught.exception)
        records = json.dumps(self.run.transport_errors)
        for index in range(2, 10):
            self.assertIn('deep cause ' + str(index), records)
        self.assertNotIn('deep cause 0', records)
        self.assertIn('truncat', records.lower())
        self.assertEqual(['upload'], self.events)

    def test_transport_allowlist_rejects_changed_command_timeout_label_and_twelfth_call(self):
        self.claim()
        arguments = ['shell', '-T', shlex.join(self.receipts[0]['argv'])]
        # Obtain the exact admitted printable label from an ordinary prerequisite query.
        self.run.prerequisites()
        label = self.transport.call_args_list[0].args[-1]
        self.assertRegex(label, r'^[A-Za-z0-9_-]+$')
        bad_calls = [(arguments + ['extra'], 60, label), (arguments, 61, label),
                     (arguments, 60, '../escape'), (['shell', '-T', 'echo injected'], 60, label)]
        for args, timeout, selected_label in bad_calls:
            with self.subTest(args=args, timeout=timeout, label=selected_label), self.assertRaises(Exception):
                self.run.transport(args, timeout, selected_label)
        self.assertEqual(3, len(self.events))
        for _ in range(8):
            self.run.transport(arguments, 60, label)
        with self.assertRaises(Exception):
            self.run.transport(arguments, 60, label)
        self.assertEqual(11, len(self.events))

    def call_main(self, arguments):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                return self.subject.main(arguments)
            except SystemExit as error:
                return error.code

    def test_cli_exact_modes_invalid_arguments_and_check_only_never_claims(self):
        with mock.patch.object(self.subject, 'InertRun', return_value=self.run):
            code = self.call_main(['--check-only', '--reviewed-head', HEAD])
            self.assertEqual(0, code)
            self.assertFalse(self.output.exists())
            self.assertEqual([], self.events)
            for args in ([], ['--execute'], ['--reviewed-head', HEAD],
                         ['--execute', '--check-only', '--reviewed-head', HEAD],
                         ['--execute', '--reviewed-head', 'A' * 40],
                         ['--execute', '--reviewed-head', HEAD, '--run', 'run02'],
                         ['--exe', '--reviewed-head', HEAD]):
                with self.subTest(arguments=args):
                    self.assertEqual(2, self.call_main(args))
        self.assertFalse(self.output.exists())

    def test_cli_missing_scope_exits_one_and_operational_failure_exits_one(self):
        with mock.patch.object(self.subject, 'InertRun', return_value=self.run):
            (self.root / SCOPE).unlink()
            self.assertEqual(1, self.call_main(['--check-only', '--reviewed-head', HEAD]))
            self.save_scope()
            self.failures[('upload', 1)] = OSError('controlled CLI action failure')
            self.assertEqual(1, self.call_main(['--execute', '--reviewed-head', HEAD]))
        self.assertEqual('FAILED', self.record('result.json')['status'])


if __name__ == '__main__':
    unittest.main()
