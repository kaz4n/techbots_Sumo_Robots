# Checks the fixed capture-only caller against independent D218 packet fixtures.
# Keeps inherited guard coverage by body identity and tests only the new seams.
# Root executes this sealed host suite; subprocess and board calls are forbidden.
import ast
import base64
import bz2
from contextlib import ExitStack
import copy
import hashlib
import importlib
import inspect
import io
import json
import os
from pathlib import Path
import re
import shlex
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[2]
RAW = 'state/analysis/P7_b4_recorder_run_raw/'
COMPILED = 'state/analysis/P7_b4_app_compile_raw/'
CALLER = 'tools/capture_b4_recorder.py'
HEAD = 'a' * 40
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
RUN = 'b4-recorder-9044ebbb-capture01'
REMOTE = '/home/arduino/sumox26_codex_build/' + RUN
LAYOUT = 'state/analysis/P7_b4_recorder_decode_raw/layout01.json'
FIXTURE = 'tests/tooling/test_b4_recorder_capture.py'
FIXTURE_PIN = (31592, 'd0476af156990efcc182750584e9d2af451937c3ef450c72efba0cf82ac828dd')
PLAN_PIN = (11356, 'd48af05673d47d787b4eeaa3f1301f2dbc8b7e6ed9a3555401ade30d21f39604')
CONTRACT_PIN = (13808, 'b205280afdc8b4ce4be2b6dea498e1494b50d698bf4bea266cafa4199a716590')
MANIFEST_PIN = (13493, 'fc8e6fc1131c1952d5e1809f9dc6fb96763dd5e111749424e9ccfaec9b58d38c')
SCOPE_FILES = (CALLER, RAW + 'actions.py', RAW + 'preparation.json', RAW + 'derivation01.json',
    'state/analysis/P7_b4_recorder_run_contract.md', 'tests/tooling/test_b4_recorder_run.py',
    RAW + 'run_oracle01.json', 'state/reviews/P7_b4_recorder_run_review.md')
INHERITED = ('head', 'source_inventory', 'load_baselines', 'state_bytes', 'check_capability', 'stage', 'diagnostics')
LEGACY_METHODS = ('check_adb', 'check_state', 'local', 'admit', 'identity_record', 'action', 'failed_finish', 'finish')
STUBS = {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                       separators=(',', ':')) + '\n').encode('ascii')


def checked(path, pin):
    raw = (ROOT / path).read_bytes()
    if (len(raw), sha(raw)) != tuple(pin):
        raise AssertionError('Independent basis changed: ' + path)
    return raw


def load_file(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    exec(compile((ROOT / path).read_bytes(), module.__file__, 'exec'), module.__dict__)
    return module


def forbidden(*args, **kwargs):
    raise AssertionError('Real native operation forbidden')


def setUpModule():
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('D219 oracle requires Python -I -B')
    if not sys.platform.startswith('linux'):
        for name in ('resource', 'pwd'):
            if name not in sys.modules:
                value = types.ModuleType(name)
                value.RLIMIT_FSIZE, value.setrlimit, value.getpwuid = 1, forbidden, forbidden
                STUBS[name] = value
                sys.modules[name] = value


def tearDownModule():
    for name, value in STUBS.items():
        if sys.modules.get(name) is value:
            del sys.modules[name]


def methods(raw, class_name):
    text = raw.decode('utf-8')
    cls = next(node for node in ast.parse(text).body if isinstance(node, ast.ClassDef) and node.name == class_name)
    return {node.name: ast.get_source_segment(text, node) for node in cls.body if isinstance(node, ast.FunctionDef)}


def bootstrap(argv):
    program = argv[argv.index('-c') + 1]
    tree = ast.parse(program)
    call = next(node for node in ast.walk(tree) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute) and node.func.attr == 'b64decode')
    return bz2.decompress(base64.b64decode(ast.literal_eval(call.args[0]), validate=True)).decode('utf-8')


class CaptureOnlyCaller(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        checked(FIXTURE, FIXTURE_PIN)
        cls.fixture = load_file(FIXTURE, '_d219_literal_d218_fixture')
        checked('state/analysis/P7_b4_recorder_run_contract.md', CONTRACT_PIN)
        cls.plan = json.loads(checked(RAW + 'plan02.json', PLAN_PIN))
        cls.layout = checked(LAYOUT, (4443, 'f9b4b1531b9f714fb2b424d9613787449b2172fcc7a0e96292dd51d37d8c0b2d'))
        cls.sources = {role: (ROOT / path).read_bytes() for role, path in (
            ('helper', 'state/analysis/P7_static_link_probe_raw/static_remote.py'),
            ('support', 'state/analysis/P7_static_startup_raw/capture_remote.py'))}
        sys.path.insert(0, str(ROOT))
        with mock.patch.object(subprocess, 'Popen', side_effect=forbidden), \
             mock.patch.object(subprocess, 'run', side_effect=forbidden):
            cls.subject = importlib.import_module('tools.capture_b4_recorder')
            cls.actions = load_file(RAW + 'actions.py', '_d219_independent_actions')

    def setUp(self):
        for target, name in ((subprocess, 'Popen'), (subprocess, 'run'), (socket, 'socket'),
                             (socket, 'create_connection'), (os, 'system')):
            patch = mock.patch.object(target, name, side_effect=forbidden)
            patch.start()
            self.addCleanup(patch.stop)

    def bundle(self, *, malformed_owner=False):
        if malformed_owner:
            owner = bytearray(self.fixture.owner_bytes())
            owner[159171] = 2
            value = self.fixture.Bundle(owner=bytes(owner))
        else:
            value = self.fixture.Bundle()
        raw = value.seal()
        leaves = ('capture_result.json', *self.fixture.LEAVES)
        packet = {'status': 'FILE_ONLY_RESULTS_VERIFIED',
            'identity_before': copy.deepcopy(self.plan['expected_identity']),
            'identity_after': copy.deepcopy(self.plan['expected_identity']), 'closing_file_checks': 13,
            'files': [{'path': REMOTE + '/' + leaf, 'bytes': len(value.files[leaf]),
                       'sha256': sha(value.files[leaf]),
                       'data_base64': base64.b64encode(value.files[leaf]).decode('ascii')} for leaf in leaves]}
        return value, raw, packet

    def scope(self):
        return {'schema': 'b4-recorder-native-scope-v1', 'run_id': RUN, 'board': '2629958581',
            'source_sha256': SOURCE, 'expected_identity': copy.deepcopy(self.plan['expected_identity']),
            'files': {path: sha((ROOT / path).read_bytes()) if (ROOT / path).is_file() else '0' * 64
                      for path in SCOPE_FILES}}

    def loaded_owner(self):
        owner = self.subject.CaptureRun(HEAD, root=ROOT)
        owner.scope = self.scope()
        owner.scope_raw = canonical(owner.scope)
        owner.expected_identity = copy.deepcopy(self.plan['expected_identity'])
        owner.load_inputs()
        return owner

    def test_inherited_body_identity_and_capture_command_framing(self):
        ordinary = checked('state/analysis/P7_ordinary_app_run_raw/run.py',
            (24859, 'f48a8be9fa380a2a922613d188ae7622eafffdf3dc5fec12edc1372b4f7fc2d2'))
        inherited = methods(ordinary, 'InertRun')
        for name in INHERITED:
            with self.subTest(inherited=name):
                self.assertEqual(inspect.getsource(getattr(self.subject.CaptureRun, name)).strip(), inherited[name])
        legacy = methods(checked('state/analysis/P7_motor_fault_raw/inert_run.py',
            (23100, '8b47b1d6e9073179e4f587e09ce04e1a1c0cfc6797daf3151d0a7126d279f56a')), 'InertRun')
        for name in LEGACY_METHODS:
            with self.subTest(legacy=name):
                self.assertEqual(inspect.getsource(getattr(self.subject.CaptureRun, name)).strip(), legacy[name])
        command = self.actions.build_capture_command(dict(self.sources), copy.deepcopy(self.plan['capture_binding']))
        self.assertIs(type(command), list)
        self.assertTrue(all(type(item) is str for item in command))
        self.assertEqual(command[:12], ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino',
            'LOGNAME=arduino', 'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C', '/usr/bin/python3', '-I', '-B', '-c'])
        self.assertEqual(command[-3], 'capture')
        token = command[-1]
        compressed = base64.b85decode(token[4:]) if token.startswith('b85:') else base64.b64decode(token, validate=True)
        dec = bz2.BZ2Decompressor()
        payload = dec.decompress(compressed)
        self.assertTrue(dec.eof)
        self.assertEqual(dec.unused_data, b'')
        self.assertEqual(sha(payload), command[-2])
        value = json.loads(payload)
        self.assertEqual(payload, canonical(value))
        self.assertEqual(set(value), {'run_id', 'source_sha256', 'sources', 'bindings', 'adapter_pin'})
        self.assertEqual((value['run_id'], value['source_sha256']), (RUN, SOURCE))
        self.assertEqual(set(value['sources']), {'helper', 'support'})
        self.assertEqual(value['bindings'], self.plan['capture_binding'])
        self.assertEqual(value['adapter_pin'], self.plan['adapter'])
        for role in self.sources:
            self.assertEqual(value['sources'][role], {'source': self.sources[role].decode(), 'sha256': sha(self.sources[role])})
        self.assertLessEqual(len(payload), 196608)
        full = [self.subject.ADB, '-s', '2629958581', 'shell', '-T', shlex.join(command)]
        self.assertLessEqual(len(subprocess.list2cmdline(full).encode('utf-16-le')) // 2 + 1, 30000)
        program = bootstrap(command)
        old = checked('state/analysis/P7_motor_fault_raw/inert_actions.py',
            (19120, '8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104')).decode()
        assignment = next(node for node in ast.parse(old).body if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == '_BOOTSTRAP_SOURCE' for target in node.targets))
        old_program = ast.literal_eval(assignment.value)
        bodies = lambda text: {node.name: ast.get_source_segment(text, node) for node in ast.parse(text).body if isinstance(node, ast.FunctionDef)}
        before, after = bodies(old_program), bodies(program)
        for name in ('require', 'canonical', 'sha', 'keys', 'unique', 'nonfinite', 'load', 'error_record', 'remember', 'installed_read'):
            self.assertEqual(after[name], before[name])

    def test_command_admission_rejects_stale_roles_sources_bindings_and_identity(self):
        binding = self.plan['capture_binding']
        cases = []
        for role in self.sources:
            changed = dict(self.sources)
            changed[role] += b'\n'
            cases.append((changed, copy.deepcopy(binding)))
        cases.append(({**self.sources, 'upload': b'x'}, copy.deepcopy(binding)))
        for key, value in (('schema', 'fixed-ordinary-app-capture-v1'), ('run_id', 'ordinary-app-9044ebbb-run01'),
                           ('source_sha256', '0' * 64), ('uid', True), ('output', REMOTE + '-other')):
            changed = copy.deepcopy(binding)
            changed[key] = value
            cases.append((dict(self.sources), changed))
        for sources, changed in cases:
            original = copy.deepcopy((sources, changed))
            with self.subTest(binding=changed.get('schema'), roles=tuple(sources)), self.assertRaises(ValueError):
                self.actions.build_capture_command(sources, changed)
            self.assertEqual((sources, changed), original)
        for helper, identity in ((self.sources['helper'] + b'\n', self.plan['expected_identity']),
            (self.sources['helper'], {**self.plan['expected_identity'], 'uid': True}),
            (self.sources['helper'], {**self.plan['expected_identity'], 'boot_id': 'wrong'})):
            with self.assertRaises(ValueError):
                self.actions.build_retrieval_command(helper, identity)
        command = self.actions.build_retrieval_command(self.sources['helper'], copy.deepcopy(self.plan['expected_identity']))
        self.assertIs(type(command), list)
        self.assertEqual(command[:12], ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino',
            'LOGNAME=arduino', 'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C', '/usr/bin/python3', '-I', '-B', '-c'])
        full = [self.subject.ADB, '-s', '2629958581', 'shell', '-T', shlex.join(command)]
        self.assertLessEqual(len(subprocess.list2cmdline(full).encode('utf-16-le')) // 2 + 1, 30000)

    def test_capture_reply_success_and_partial_or_unattributed_refusals(self):
        bundle, raw, _ = self.bundle()
        self.assertEqual(self.actions.validate_capture_reply(bundle.envelope), bundle.report)
        mutations = (lambda r: r.update(report_origin='durable_unattributed'),
            lambda r: r.update(action='upload'), lambda r: r.update(run_id='ordinary-app-9044ebbb-run01'),
            lambda r: r.update(first_error={'type': 'Error', 'message': 'close'}),
            lambda r: r['report'].update(status='FAILED'), lambda r: r['report']['counts'].update(reads=25),
            lambda r: r['report']['counts'].update(commands=True), lambda r: r['report'].update(wait={}),
            lambda r: r['report']['analysis']['flash'].update(before_sketch=False),
            lambda r: r['report']['reads'][8].update(address=536951336),
            lambda r: r['report']['reads'].pop())
        for mutate in mutations:
            value = json.loads(raw)
            mutate(value)
            durable = canonical(value['report'])
            value.update(full_result_bytes=len(durable), full_result_sha256=sha(durable))
            original = copy.deepcopy(value)
            with self.subTest(mutation=repr(mutate)), self.assertRaises(ValueError):
                self.actions.validate_capture_reply(value)
            self.assertEqual(value, original)

    def test_retrieval_program_uses_only_fixed_paths_and_rechecks_all_pins_and_identity(self):
        bundle, _, expected_packet = self.bundle()
        argv = self.actions.build_retrieval_command(self.sources['helper'], copy.deepcopy(self.plan['expected_identity']))
        source = bootstrap(argv)
        selected = [node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)
                    and node.name in ('require', 'unique', 'nonfinite', 'read_bundle')]
        self.assertEqual({node.name for node in selected}, {'require', 'unique', 'nonfinite', 'read_bundle'})
        namespace = {'EXPECTED': copy.deepcopy(self.plan['expected_identity']), 'OUTPUT': REMOTE,
            'RUN_ID': RUN, 'SOURCE': SOURCE, 'PLAN': self.fixture.PLAN,
            'COUNTS': {'commands': 26, 'reads': 26, 'requested_bytes': 852624},
            'REPORT_KEYS': set(bundle.report), 'json': json, 'hashlib': hashlib, 'base64': base64, 're': re}
        exec(compile(ast.Module(body=selected, type_ignores=[]), '<fixed retrieval function fixture>', 'exec'), namespace)
        leaves = ('capture_result.json', *self.fixture.LEAVES)
        def invoke(changed_leaf=None, identity_drift=False):
            calls, identities, seen = [], [], {}
            def identity(fd):
                self.assertEqual(fd, 42)
                identities.append(fd)
                value = copy.deepcopy(self.plan['expected_identity'])
                if identity_drift and len(identities) == 2:
                    value['uid'] = 0
                return value
            def logical_read(fd, path, limit):
                self.assertEqual(fd, 42)
                self.assertIn(path, [REMOTE + '/' + leaf for leaf in leaves])
                self.assertIs(type(limit), int)
                self.assertLessEqual(limit, 65536)
                leaf = path.removeprefix(REMOTE + '/')
                calls.append((leaf, limit))
                seen[leaf] = seen.get(leaf, 0) + 1
                raw = bundle.files[leaf]
                self.assertLessEqual(len(raw), limit)
                closing_read = 3 if leaf == 'capture_result.json' else 2
                if leaf == changed_leaf and seen[leaf] == closing_read:
                    return bytes([raw[0] ^ 1]) + raw[1:]
                return raw
            helper = types.SimpleNamespace(identity=identity, logical_read=logical_read)
            result = namespace['read_bundle'](helper, 42)
            return result, calls, identities
        actual, calls, identities = invoke()
        self.assertEqual(actual, expected_packet)
        self.assertEqual(len(calls), 27)
        self.assertEqual(identities, [42, 42])
        self.assertEqual(calls[0], ('capture_result.json', 65536))
        self.assertEqual(tuple(leaf for leaf, _ in calls[1:14]), leaves)
        self.assertEqual(tuple(leaf for leaf, _ in calls[14:]), leaves)
        for leaf in ('capture_result.json', '08-owner.0.bin', '18-after.lifecycle.bin'):
            with self.subTest(closing_leaf=leaf), self.assertRaises(ValueError):
                invoke(changed_leaf=leaf)
        with self.assertRaises(ValueError):
            invoke(identity_drift=True)

    def test_fixed_retrieval_packet_decode_and_each_leaf_corruption(self):
        bundle, raw, packet = self.bundle()
        self.assertEqual((len(canonical(packet)), sum(len(value) for value in bundle.files.values())), (222909, 164833))
        self.assertLess(len(canonical(packet)), 1048576)
        original = copy.deepcopy(packet)
        result = self.actions.decode_retrieval(packet, returned_raw=raw, layout_raw=self.layout)
        self.assertEqual(packet, original)
        self.assertEqual(result['bundle_status'], 'PASS')
        self.assertEqual(result['raw_owner'], bundle.owner)
        self.assertEqual(result['raw_returned'], raw)
        self.assertEqual(result['raw_files'], bundle.files)
        self.assertEqual(result['decoder']['csv']['frames'], self.fixture.FRAME_HEADER + self.fixture.FRAME_LITERAL)
        self.assertEqual(result['coherence'], 'UNPROVEN')
        for flag in ('common_attempt_verified', 'transport_verified', 'hardware_acceptance'):
            self.assertIs(result[flag], False)
        mutations = [lambda p: p.update(closing_file_checks=True), lambda p: p.update(status='OTHER'),
            lambda p: p['identity_after'].update(uid=True), lambda p: p['identity_before'].update(boot_id='wrong'),
            lambda p: p['files'].pop(), lambda p: p['files'].append(copy.deepcopy(p['files'][0])),
            lambda p: p['files'].reverse()]
        for index in range(13):
            mutations.extend((lambda p, i=index: p['files'][i].update(path=REMOTE + '/../elsewhere'),
                lambda p, i=index: p['files'][i].update(bytes=True),
                lambda p, i=index: p['files'][i].update(sha256='0' * 64),
                lambda p, i=index: p['files'][i].update(data_base64=p['files'][i]['data_base64'] + '\n')))
        for mutate in mutations:
            changed = copy.deepcopy(packet)
            mutate(changed)
            before = copy.deepcopy(changed)
            with self.assertRaises(ValueError):
                self.actions.decode_retrieval(changed, returned_raw=raw, layout_raw=self.layout)
            self.assertEqual(changed, before)
        refused = self.actions.decode_retrieval(packet, returned_raw=raw, layout_raw=self.layout + b' ')
        self.assertEqual(refused['bundle_status'], 'REFUSED')
        self.assertEqual(refused['errors'][0]['code'], 'LAYOUT')
        self.assertEqual(refused['raw_owner'], bundle.owner)
        self.assertIsNone(refused['decoder'])

    def test_actual_b4_source_evidence_and_closed_scope_admission(self):
        manifest = json.loads(checked(COMPILED + 'inputs_static.json', MANIFEST_PIN))
        self.assertEqual(len(manifest['files']), 130)
        owner = self.loaded_owner()
        self.assertEqual(set(owner.bindings), {'capture'})
        self.assertEqual(owner.bindings['capture'], self.plan['capture_binding'])
        self.assertEqual(owner.source_hashes['app.ino'], manifest['files']['src/app/app.ino'])
        self.assertNotIn('app_motor_observe.ino', owner.source_hashes)
        self.assertEqual(len([name for name in owner.fixed_bytes if name in manifest['files']]), 130)
        owner.check_evidence()
        stale = (ROOT / 'state/analysis/P7_ordinary_app_static_compile_raw/inputs_static.json').read_bytes()
        original = owner.fixed_bytes[COMPILED + 'inputs_static.json']
        owner.fixed_bytes[COMPILED + 'inputs_static.json'] = stale
        with self.assertRaises(ValueError):
            owner.load_source()
        owner.fixed_bytes[COMPILED + 'inputs_static.json'] = original
        for name, key, value in (('native_static01/result.json', 'source_sha256', '0' * 64),
            ('native_abi_static01/local_result.json', 'status', 'FAILED'),
            ('native_entry_static01/local_result.json', 'first_error', {'message': 'failed'})):
            path = COMPILED + name
            original = owner.fixed_bytes[path]
            altered = json.loads(original)
            altered[key] = value
            owner.fixed_bytes[path] = canonical(altered)
            with self.subTest(evidence=name), self.assertRaises(ValueError):
                owner.check_evidence()
            owner.fixed_bytes[path] = original
        with tempfile.TemporaryDirectory(prefix='d219-scope-') as directory:
            scope = self.scope()
            path = Path(directory) / self.plan['scope']
            path.parent.mkdir(parents=True)
            local = self.subject.CaptureRun(HEAD, root=directory)
            path.write_bytes(canonical(scope))
            local.load_scope()
            self.assertEqual(local.expected_identity, self.plan['expected_identity'])
            changes = (('run_id', 'ordinary-app-9044ebbb-run01'), ('source_sha256', '0' * 64), ('board', 2629958581))
            for key, value in changes:
                bad = copy.deepcopy(scope)
                bad[key] = value
                path.write_bytes(canonical(bad))
                with self.assertRaises(ValueError):
                    local.load_scope()
            bad = copy.deepcopy(scope)
            bad['files']['tools/b4_recorder_capture.py'] = self.plan['adapter']['sha256']
            path.write_bytes(canonical(bad))
            with self.assertRaises(ValueError):
                local.load_scope()

    def test_predeclared_commands_capture_intent_and_retrieval_are_consumed_once(self):
        owner = self.loaded_owner()
        owner.prepare_commands()
        self.assertEqual(set(owner.all_commands), {'adapter-claim', 'cli-initialization', 'cli-builtin-files', 'capabilities', 'capture', 'retrieve'})
        self.assertEqual(len(owner.allowed), 7)
        self.assertEqual(dict(owner.timeouts), {'adapter-claim': 60, 'adapter-push': 60,
            'cli-initialization': 60, 'cli-builtin-files': 60, 'capabilities': 60, 'capture': 630, 'retrieve': 60})
        before = owner.state_bytes()
        self.assertEqual(before, owner.input_state)
        owner.claim_ready = owner.stage_ready = True
        owner.local = lambda: None
        written = []
        owner.write = lambda name, value: written.append((name, copy.deepcopy(value)))
        bundle, raw, packet = self.bundle()
        owner.intent('capture', None)
        with self.assertRaises(ValueError):
            owner.intent('capture', None)
        with self.assertRaises(ValueError):
            owner.intent('upload', None)
        replies = []
        def query(label, limit):
            replies.append((label, limit))
            return copy.deepcopy(bundle.envelope if label == 'capture' else packet)
        owner.query = query
        reply = owner.action('capture')
        owner.retrieval_intent(reply)
        self.assertEqual(owner.retrieve(), packet)
        self.assertEqual(replies, [('capture', 65536), ('retrieve', 1048576)])
        self.assertEqual([name for name, _ in written], ['capture_attempt.json', 'retrieve_attempt.json'])
        for operation in (lambda: owner.action('capture'), lambda: owner.retrieval_intent(reply), owner.retrieve):
            with self.assertRaises(ValueError):
                operation()
        self.assertEqual(replies, [('capture', 65536), ('retrieve', 1048576)])
        owner.counter = owner.transport_calls = 10
        owner.command_counts = dict(self.plan['calls']['per_label'])
        owner.stage_started = owner.stage_intent_ready = owner.stage_claim_verified = True
        owner.stage_dispatches = {'adapter-claim', 'adapter-push'}
        complete = {'status': 'COMPLETED', 'capture_attempts': 1, 'retrieval_attempts': 1}
        owner.check_counters(complete)
        for changed in ({**complete, 'capture_attempts': True}, {**complete, 'retrieval_attempts': 0}):
            with self.assertRaises(ValueError):
                owner.check_counters(changed)
        owner.counter = owner.transport_calls = 11
        with self.assertRaises(ValueError):
            owner.check_counters({'status': 'FAILED'})

    def test_capture_only_sequence_order_failures_and_final_checks(self):
        bundle, _, packet = self.bundle()
        parent, check = self.subject.CaptureRun, self
        class Controlled(parent):
            def __init__(self, failure=None, closing=None):
                super().__init__(HEAD, root=ROOT)
                self.events, self.failure, self.closing = [], failure, closing
                self.prerequisite_passes = 0
            def observe(self, name):
                self.events.append(name)
                if self.failure == name:
                    raise ValueError('primary-' + name)
            def admit(self):
                self.observe('admit')
                self.admitted = True
            def claim(self):
                self.observe('claim')
                self.claimed = self.claim_ready = True
            def stage(self):
                self.observe('stage')
                self.stage_ready = True
            def local(self):
                self.events.append('local')
                if self.closing == 'local' and ('retrieve' in self.events or self.failure in self.events):
                    raise ValueError('closing-local')
            def prerequisites(self):
                self.events.append('prerequisites')
                self.prerequisite_passes += 1
                if self.closing == 'prerequisites' and (self.prerequisite_passes > 1 or self.failure == 'stage'):
                    raise ValueError('closing-prerequisites')
            def intent(self, action, predecessor):
                check.assertEqual((action, predecessor), ('capture', None))
                self.observe('capture-intent')
            def action(self, name):
                check.assertEqual(name, 'capture')
                self.observe('capture')
                return copy.deepcopy(bundle.envelope)
            def retrieval_intent(self, reply):
                check.assertEqual(reply, bundle.envelope)
                self.observe('retrieve-intent')
            def retrieve(self):
                self.observe('retrieve')
                return copy.deepcopy(packet)
            def export_bundle(self, captured, reply):
                check.assertEqual(captured, packet)
                check.assertEqual(reply, bundle.envelope)
                self.observe('export')
                return {'fixture': 'exported'}
            def finish(self, result):
                self.observe('finish')
        owner = Controlled()
        result = owner.run()
        self.assertEqual((result['schema'], result['status']), ('b4-recorder-sequence-v1', 'COMPLETED'))
        self.assertEqual((result['capture_attempts'], result['retrieval_attempts']), (1, 1))
        self.assertEqual(result['capture'], bundle.envelope)
        self.assertEqual(result['export'], {'fixture': 'exported'})
        self.assertEqual(owner.prerequisite_passes, 2)
        key_order = [item for item in owner.events if item != 'local' and item != 'prerequisites']
        self.assertEqual(key_order, ['admit', 'claim', 'stage', 'capture-intent', 'capture', 'retrieve-intent', 'retrieve', 'export', 'finish'])
        self.assertLess(max(i for i, item in enumerate(owner.events) if item == 'prerequisites'), owner.events.index('export'))
        with self.assertRaises(ValueError):
            owner.run()
        for failure in ('stage', 'capture', 'retrieve', 'export'):
            owner = Controlled(failure=failure, closing='prerequisites' if failure != 'export' else None)
            result = owner.run()
            self.assertEqual(result['status'], 'FAILED')
            self.assertIn('primary-' + failure, result['first_error']['message'])
            self.assertEqual(owner.events.count(failure), 1)
            self.assertEqual(owner.events.count('finish'), 1)
            if failure in ('stage', 'capture', 'retrieve'):
                self.assertNotIn('export', owner.events)
                self.assertTrue(result['postcheck_errors'])
            if failure == 'capture':
                self.assertNotIn('retrieve', owner.events)
            if failure == 'stage':
                self.assertEqual((result['capture_attempts'], result['retrieval_attempts']), (0, 0))
        owner = Controlled(closing='local')
        result = owner.run()
        self.assertEqual(result['status'], 'FAILED')
        self.assertNotIn('export', owner.events)
        self.assertIn('closing-local', result['first_error']['message'])

    def test_local_export_preserves_exact_leaves_suppresses_invalid_csv_and_never_overwrites(self):
        for malformed in (False, True):
            bundle, raw, packet = self.bundle(malformed_owner=malformed)
            with self.subTest(malformed_owner=malformed), tempfile.TemporaryDirectory(prefix='d219-export-') as directory:
                owner = self.subject.CaptureRun(HEAD, root=directory)
                owner.output.mkdir(parents=True)
                owner.fixed_bytes = {LAYOUT: self.layout, **{path: (ROOT / path).read_bytes() for path in (
                    'tools/validate_csv_bundle.py', 'tools/b4_recorder_capture.py',
                    'tools/decode_b4_recorder.py', 'tools/decode_b4_capture.py')}}
                checks = []
                owner.check_output = lambda: checks.append('checked')
                owner.local = lambda: None
                value = owner.export_bundle(packet, bundle.envelope)
                self.assertEqual((owner.output / 'capture_envelope.json').read_bytes(), raw)
                for name, data in bundle.files.items():
                    self.assertEqual((owner.output / name).read_bytes(), data)
                expected = {'capture_envelope.json', 'export.json', *bundle.files}
                if not malformed:
                    expected.update(('frames.csv', 'events.csv', 'summary.csv'))
                    self.assertEqual((owner.output / 'frames.csv').read_bytes(), self.fixture.FRAME_HEADER + self.fixture.FRAME_LITERAL)
                    self.assertEqual((owner.output / 'events.csv').read_bytes(), self.fixture.EVENT_HEADER + self.fixture.EVENT_LITERAL)
                self.assertEqual({path.name for path in owner.output.iterdir()}, expected)
                self.assertEqual(json.loads((owner.output / 'export.json').read_bytes()), value)
                self.assertGreaterEqual(len(checks), 2 * (len(expected) - 1))
                before = {path.name: path.read_bytes() for path in owner.output.iterdir()}
                with self.assertRaises((FileExistsError, ValueError)):
                    owner.export_bundle(packet, bundle.envelope)
                self.assertEqual({path.name: path.read_bytes() for path in owner.output.iterdir()}, before)

    def test_cli_check_only_creates_no_execution_and_rejects_ambiguous_selection(self):
        fake = mock.Mock()
        fake.run.return_value = {'status': 'COMPLETED'}
        with mock.patch.object(self.subject, 'CaptureRun', return_value=fake) as constructor:
            self.assertEqual(self.subject.main(['--check-only', '--reviewed-head', HEAD]), 0)
            constructor.assert_called_once_with(HEAD)
            fake.admit.assert_called_once_with()
            fake.run.assert_not_called()
        for argv in (['--reviewed-head', HEAD], ['--check-only', '--execute', '--reviewed-head', HEAD],
                     ['--check-only', '--reviewed-head', 'A' * 40], ['--check-only', '--reviewed-head', 'a' * 39]):
            with mock.patch.object(self.subject, 'CaptureRun') as constructor, mock.patch.object(sys, 'stderr', io.StringIO()):
                with self.assertRaises(SystemExit):
                    self.subject.main(argv)
                constructor.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
