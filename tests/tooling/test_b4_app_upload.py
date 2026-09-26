# Checks the exact B4 inhibited upload metadata and upload-only caller seams.
# Inherited guard bodies retain accepted coverage; all native work is controlled.
# Root executes the frozen oracle after independent source review and pinning.
import ast
import base64
import builtins
import bz2
import copy
import hashlib
import importlib
import inspect
import io
import json
import os
from pathlib import Path
import shlex
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[2]
RAW = 'state/analysis/P7_b4_app_upload_raw/'
COMPILED = 'state/analysis/P7_b4_app_compile_raw/'
CALLER = 'tools/upload_b4_app.py'
RUN = 'b4-app-m0-9044ebbb-load01'
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
OUTPUT = '/home/arduino/sumox26_codex_build/' + RUN + '-upload'
HEAD = 'a' * 40
CONTRACT = 'state/analysis/P7_b4_app_upload_contract.md'
CONTRACT_PIN = (8925, 'f9ab9c6729fe4ac6504fe6d284086331f680a004976e0e2898fde41a41222ff8')
PLAN_PIN = (8282, '07726511930332b17c49c02c91a1f83df2d22bcc09502fd8255fa573bedee3b8')
MANIFEST_PIN = (13493, 'fc8e6fc1131c1952d5e1809f9dc6fb96763dd5e111749424e9ccfaec9b58d38c')
DEPENDENCIES = {
    'helper': ('state/analysis/P7_static_link_probe_raw/static_remote.py', 33321, '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'),
    'capture': ('state/analysis/P7_static_startup_raw/capture_remote.py', 37525, '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e'),
    'upload': ('state/analysis/P7_static_startup_raw/upload_remote.py', 24710, 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1')}
STUBS = {}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                       separators=(',', ':')) + '\n').encode('ascii')


def checked(path, pin):
    raw = (ROOT / path).read_bytes()
    if (len(raw), sha(raw)) != tuple(pin):
        raise AssertionError('Independent input changed: ' + path)
    return raw


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    exec(compile((ROOT / path).read_bytes(), module.__file__, 'exec'), module.__dict__)
    return module


def forbidden(*args, **kwargs):
    raise AssertionError('Real native operation forbidden')


def setUpModule():
    if not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('D221 oracle requires Python -I -B')
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


def functions(raw, class_name=None):
    text = raw.decode('utf-8') if type(raw) is bytes else raw
    nodes = ast.parse(text).body
    if class_name is not None:
        nodes = next(node.body for node in nodes if isinstance(node, ast.ClassDef) and node.name == class_name)
    return {node.name: ast.get_source_segment(text, node) for node in nodes if isinstance(node, ast.FunctionDef)}


def command_data(command):
    wrapper = command[command.index('-c') + 1]
    decode = next(node for node in ast.walk(ast.parse(wrapper)) if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Attribute) and node.func.attr == 'b64decode')
    program = bz2.decompress(base64.b64decode(ast.literal_eval(decode.args[0]), validate=True)).decode()
    token = command[-1]
    compressed = base64.b85decode(token[4:]) if token.startswith('b85:') else base64.b64decode(token, validate=True)
    decoder = bz2.BZ2Decompressor()
    raw = decoder.decompress(compressed)
    if not decoder.eof or decoder.unused_data:
        raise AssertionError('Expected one complete BZ2 member')
    return program, raw, json.loads(raw)


def full_report():
    return {'schema': 'b4-app-upload-result-v1', 'run_id': RUN, 'source_sha256': SOURCE,
        'status': 'UPLOADED', 'started_utc': '2026-09-26T00:00:00+00:00',
        'finished_utc': '2026-09-26T00:00:01+00:00', 'started_monotonic': 100.0,
        'finished_monotonic': 101.0, 'first_error': None, 'postcheck_errors': [],
        'attempts': 1, 'subprocess': {'returncode': 0, 'timed_out': False, 'reaped': True},
        'stdout': 'controlled upload stdout', 'stderr': ''}


def envelope():
    report = full_report()
    raw = canonical(report)
    return {'schema': 'b4-app-upload-action-v1', 'action': 'upload', 'run_id': RUN,
        'source_sha256': SOURCE, 'report': {k: v for k, v in report.items() if k not in ('stdout', 'stderr')},
        'report_origin': 'returned', 'remote_result_path': OUTPUT + '/upload_result.json',
        'full_result_bytes': len(raw), 'full_result_sha256': sha(raw),
        'first_error': None, 'postcheck_errors': []}


class B4Upload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        checked(CONTRACT, CONTRACT_PIN)
        cls.plan = json.loads(checked(RAW + 'plan01.json', PLAN_PIN))
        cls.sources = {role: checked(path, (size, digest)) for role, (path, size, digest) in DEPENDENCIES.items()}
        cls.inline = {'helper': cls.sources['helper'], 'support': cls.sources['capture'], 'upload': cls.sources['upload']}
        # The coordinator separately binds new subject bytes before this root-scheduled execution.
        remote_raw = (ROOT / RAW / 'remote.py').read_bytes()
        cls.adapter = {'path': cls.plan['adapter_path'], 'bytes': len(remote_raw), 'sha256': sha(remote_raw)}
        cls.remote_raw = remote_raw
        sys.path.insert(0, str(ROOT))
        with mock.patch.object(subprocess, 'Popen', side_effect=forbidden), mock.patch.object(subprocess, 'run', side_effect=forbidden):
            cls.subject = importlib.import_module('tools.upload_b4_app')
            cls.actions = load(RAW + 'actions.py', '_d221_independent_actions')
            cls.remote = load(RAW + 'remote.py', '_d221_independent_remote')

    def setUp(self):
        for target, name in ((subprocess, 'Popen'), (subprocess, 'run'), (socket, 'socket'),
                             (socket, 'create_connection'), (os, 'system')):
            patch = mock.patch.object(target, name, side_effect=forbidden)
            patch.start()
            self.addCleanup(patch.stop)

    def scope(self):
        return {'schema': 'b4-app-upload-native-scope-v1', 'run_id': RUN, 'board': '2629958581',
            'source_sha256': SOURCE, 'expected_identity': copy.deepcopy(self.plan['expected_identity']),
            'files': {name: sha((ROOT / name).read_bytes()) if (ROOT / name).is_file() else '0' * 64
                      for name in self.plan['scope_files']}}

    def loaded_owner(self):
        owner = self.subject.UploadRun(HEAD, root=ROOT)
        owner.scope = self.scope()
        owner.scope_raw = canonical(owner.scope)
        owner.expected_identity = copy.deepcopy(self.plan['expected_identity'])
        owner.load_inputs()
        return owner

    def test_remote_exact_profile_artifacts_pins_and_unchanged_upload_composition(self):
        for role in self.sources:
            changed = dict(self.sources)
            changed[role] += b'\n'
            with self.subTest(role=role), mock.patch.object(builtins, 'exec', side_effect=forbidden) as execute:
                with self.assertRaises(ValueError):
                    self.remote.load_dependencies(changed)
                execute.assert_not_called()
        deps = self.remote.load_dependencies(dict(self.sources))
        profile = self.remote.selected_profile(deps.capture)
        self.assertEqual(profile['argv'], ['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload',
            '--fqbn', 'arduino:zephyr:unoq:link_mode=static', '--input-file',
            '/home/arduino/sumox26_codex_build/b4-app-m0-static01/build/app.ino.bin',
            '/home/arduino/sumox26_codex_build/' + SOURCE + '/app'])
        binding = copy.deepcopy(self.plan['upload_binding'])
        self.assertEqual(self.remote.checked_upload_bindings(deps, binding), binding)
        self.assertEqual((binding['files']['raw']['bytes'], binding['files']['sketch']['bytes']), (82896, 82912))
        for name in ('raw', 'sketch', 'loader'):
            for key, value in (('bytes', True), ('sha256', '0' * 64), ('path', '/tmp/ordinary.bin')):
                altered = copy.deepcopy(binding)
                altered['files'][name][key] = value
                with self.subTest(artifact=name, field=key), self.assertRaises(ValueError):
                    self.remote.checked_upload_bindings(deps, altered)
        old = functions(checked('state/analysis/P7_ordinary_app_run_raw/remote.py',
            (11269, 'a2c2fc9d32694a96a406b6de499bfb04a2a159710443c8b37ca56e92921a536f')))
        for name in ('_artifact', 'checked_upload_bindings', 'upload'):
            self.assertEqual(inspect.getsource(getattr(self.remote, name)).strip(), old[name])
        for name in ('collect', '_capture_type', 'read_plan', 'WINDOWS', 'checked_capture_bindings', '_flash_plan'):
            self.assertFalse(hasattr(self.remote, name))
        expected_profile = old['selected_profile'].replace('fixed-ordinary-app-upload-v1', 'fixed-b4-app-upload-v1').replace('ordinary-app-upload-', 'b4-app-upload-')
        self.assertEqual(inspect.getsource(self.remote.selected_profile).strip(), expected_profile)
        with mock.patch.object(deps.upload, 'upload_loader', return_value={'fixture': 'returned'}) as upload:
            result = self.remote.upload(deps, fs_root=Path('/controlled'), executor=forbidden,
                                        clock=lambda: 100.0, bindings=binding)
            self.assertEqual(result, {'fixture': 'returned'})
            self.assertEqual(upload.call_count, 1)
            args, kwargs = upload.call_args
            self.assertEqual(args, (deps.helper, deps.capture))
            self.assertEqual((kwargs['fs_root'], kwargs['bindings'], kwargs['run_id']), (Path('/controlled'), binding, RUN))
            self.assertIs(kwargs['executor'], forbidden)

    def test_upload_only_command_framing_exact_types_and_preserved_guard_bodies(self):
        command = self.actions.build_command('upload', dict(self.inline), copy.deepcopy(self.plan['upload_binding']), dict(self.adapter))
        program, raw, value = command_data(command)
        self.assertIs(type(command), list)
        self.assertEqual(command[:12], ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino',
            'LOGNAME=arduino', 'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C', '/usr/bin/python3', '-I', '-B', '-c'])
        self.assertEqual(command[-3], 'upload')
        self.assertEqual(command[-2], sha(raw))
        self.assertEqual(raw, canonical(value))
        self.assertEqual(set(value), {'run_id', 'source_sha256', 'sources', 'bindings', 'adapter_pin'})
        self.assertEqual((value['run_id'], value['source_sha256']), (RUN, SOURCE))
        self.assertEqual(value['bindings'], self.plan['upload_binding'])
        self.assertEqual(value['adapter_pin'], self.adapter)
        self.assertEqual(set(value['sources']), {'helper', 'support', 'upload'})
        for role, body in self.inline.items():
            self.assertEqual(value['sources'][role], {'source': body.decode(), 'sha256': sha(body)})
        self.assertLessEqual(len(raw), 196608)
        full = [self.subject.ADB, '-s', '2629958581', 'shell', '-T', shlex.join(command)]
        self.assertLessEqual(len(subprocess.list2cmdline(full).encode('utf-16-le')) // 2 + 1, 30000)
        for action in ('capture', 'retrieve', 'UPLOAD', None):
            with self.assertRaises(ValueError):
                self.actions.build_command(action, self.inline, self.plan['upload_binding'], self.adapter)
        changes = []
        for role in self.inline:
            altered = dict(self.inline)
            altered[role] += b'\n'
            changes.append((altered, copy.deepcopy(self.plan['upload_binding']), dict(self.adapter)))
        for key, value in (('uid', True), ('schema', 'fixed-ordinary-app-upload-v1'), ('run_id', 'ordinary-app-9044ebbb-run01')):
            binding = copy.deepcopy(self.plan['upload_binding'])
            binding[key] = value
            changes.append((dict(self.inline), binding, dict(self.adapter)))
        changes.append((dict(self.inline), copy.deepcopy(self.plan['upload_binding']), {**self.adapter, 'bytes': True}))
        for sources, binding, pin in changes:
            with self.assertRaises(ValueError):
                self.actions.build_command('upload', sources, binding, pin)
        old = checked('state/analysis/P7_motor_fault_raw/inert_actions.py',
            (19120, '8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104')).decode()
        assignment = next(node for node in ast.parse(old).body if isinstance(node, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == '_BOOTSTRAP_SOURCE' for t in node.targets))
        before, after = functions(ast.literal_eval(assignment.value)), functions(program)
        for name in ('require', 'canonical', 'sha', 'keys', 'unique', 'nonfinite', 'load', 'error_record', 'remember'):
            self.assertEqual(after[name], before[name])

    def test_bootstrap_returned_origin_fallback_and_independent_closing_checks(self):
        command = self.actions.build_command('upload', self.inline, self.plan['upload_binding'], self.adapter)
        program, _, payload = command_data(command)
        selected = [node for node in ast.parse(program).body if isinstance(node, ast.FunctionDef)
                    and node.name in ('require', 'canonical', 'sha', 'keys', 'unique', 'nonfinite',
                                      'error_record', 'remember', 'staged_read', 'perform')]
        self.assertEqual(len(selected), 10)
        def invoke(fail_upload=False, fail_reread=False, fail_close=False):
            events = []
            def logical_read(fd, path, limit):
                self.assertEqual(fd, 42)
                events.append(('read', path))
                if path == self.adapter['path']:
                    if fail_reread and events.count(('read', path)) == 2:
                        raise OSError('adapter-close-failed')
                    self.assertEqual(limit, self.adapter['bytes'])
                    return self.remote_raw
                self.assertEqual(path, OUTPUT + '/upload_result.json')
                return canonical(full_report())
            helper = types.SimpleNamespace(logical_read=logical_read, sha256=sha)
            marker = object()
            def dependencies(sources):
                self.assertEqual(sources, self.sources)
                events.append(('dependencies',))
                return marker
            def upload(deps, *, bindings):
                self.assertIs(deps, marker)
                self.assertEqual(bindings, self.plan['upload_binding'])
                events.append(('upload',))
                if fail_upload:
                    raise ValueError('upload-failed')
                return full_report()
            adapter = types.SimpleNamespace(load_dependencies=dependencies, upload=upload)
            def load_module(name, source, filename):
                events.append(('load', filename))
                return helper if filename == '/__sumox__/helper.py' else adapter
            def close(fd):
                self.assertEqual(fd, 42)
                events.append(('close',))
                if fail_close:
                    raise OSError('root-close-failed')
            fake_os = types.SimpleNamespace(O_RDONLY=1, O_DIRECTORY=2, O_NOFOLLOW=4, O_CLOEXEC=8,
                open=lambda *args: 42, close=close)
            ns = {'json': json, 'hashlib': hashlib, 'os': fake_os, 'load': load_module,
                  'RUN_ID': RUN, 'SOURCE': SOURCE}
            exec(compile(ast.Module(body=selected, type_ignores=[]), '<controlled upload bootstrap>', 'exec'), ns)
            reply = envelope()
            reply.update(report=None, report_origin=None, full_result_bytes=None, full_result_sha256=None)
            ns['perform']('upload', payload['sources'], self.plan['upload_binding'], self.adapter, reply)
            self.assertEqual(events.count(('upload',)), 1)
            self.assertEqual(events.count(('close',)), 1)
            self.assertEqual(events.count(('read', self.adapter['path'])), 2)
            self.assertEqual([event[1] for event in events if event[0] == 'load'],
                             ['/__sumox__/helper.py', self.adapter['path']])
            return reply, events
        reply, _ = invoke()
        self.assertEqual(reply['report_origin'], 'returned')
        self.assertEqual(reply['report'], full_report())
        self.assertIsNone(reply['first_error'])
        self.assertEqual(reply['postcheck_errors'], [])
        reply, _ = invoke(fail_upload=True)
        self.assertEqual(reply['report_origin'], 'durable_unattributed')
        self.assertIn('upload-failed', reply['first_error']['message'])
        for reread, close in ((True, False), (False, True), (True, True)):
            reply, _ = invoke(fail_upload=True, fail_reread=reread, fail_close=close)
            self.assertIn('upload-failed', reply['first_error']['message'])
            checks = {error['check'] for error in reply['postcheck_errors']}
            self.assertEqual(checks, ({'staged_adapter'} if reread else set()) | ({'root_close'} if close else set()))
        reply, _ = invoke(fail_close=True)
        self.assertEqual(reply['report_origin'], 'returned')
        self.assertIsNotNone(reply['first_error'])
        self.assertTrue(reply['postcheck_errors'])

    def test_compact_reply_validation_requires_exact_upload_success_and_returned_origin(self):
        reply = envelope()
        self.actions.validate_reply('upload', reply)
        self.assertNotIn('stdout', reply['report'])
        self.assertNotIn('stderr', reply['report'])
        mutations = (lambda r: r.update(report_origin='durable_unattributed'),
            lambda r: r.update(action='capture'), lambda r: r.update(schema='ordinary-app-action-v1'),
            lambda r: r.update(first_error={'type': 'OSError', 'message': 'close'}),
            lambda r: r['report'].update(attempts=True), lambda r: r['report'].update(attempts=0),
            lambda r: r['report']['subprocess'].update(returncode=True),
            lambda r: r['report']['subprocess'].update(timed_out=True),
            lambda r: r['report']['subprocess'].update(reaped=False),
            lambda r: r['report'].update(finished_monotonic=280.0),
            lambda r: r['report'].update(started_monotonic=float('inf')),
            lambda r: r['report'].update(postcheck_errors=[{'type': 'Error', 'message': 'late'}]))
        for mutate in mutations:
            changed = copy.deepcopy(reply)
            mutate(changed)
            before = copy.deepcopy(changed)
            with self.assertRaises(ValueError):
                self.actions.validate_reply('upload', changed)
            self.assertEqual(changed, before)
        with self.assertRaises(ValueError):
            self.actions.validate_reply('capture', reply)

    def test_upload_only_action_sequence_first_errors_and_finish_attachment(self):
        def exercise(primary=None, closing=None, finish_error=False):
            events, counts = [], {}
            def call(name, *args):
                events.append((name, args))
                counts[name] = counts.get(name, 0) + 1
                if name == 'intent':
                    self.assertEqual(args, ('upload', None))
                if primary == name and counts[name] == 1:
                    raise ValueError('primary-' + name)
                if closing == name and counts[name] > 1:
                    raise OSError('closing-' + name)
                if name == 'finish' and finish_error:
                    raise OSError('finish-failed')
                return envelope() if name == 'upload' else None
            operations = {name: (lambda *args, name=name: call(name, *args))
                          for name in ('local', 'prerequisites', 'intent', 'upload', 'finish')}
            return operations, events, counts
        operations, events, counts = exercise()
        result = self.actions.run_actions(operations)
        self.assertEqual(result, {'schema': 'b4-app-upload-sequence-v1', 'status': 'COMPLETED',
            'upload': envelope(), 'upload_attempts': 1, 'first_error': None, 'postcheck_errors': []})
        self.assertEqual([name for name, _ in events], ['local', 'prerequisites', 'intent', 'upload', 'local', 'prerequisites', 'finish'])
        for name in ('local', 'prerequisites', 'intent', 'upload'):
            operations, events, counts = exercise(primary=name, closing='local')
            result = self.actions.run_actions(operations)
            self.assertEqual(result['status'], 'FAILED')
            self.assertIn('primary-' + name, result['first_error']['message'])
            self.assertEqual(counts.get('upload', 0), 1 if name == 'upload' else 0)
            self.assertEqual(counts.get('finish'), 1)
            self.assertEqual([event[0] for event in events][-3:], ['local', 'prerequisites', 'finish'])
            self.assertTrue(result['postcheck_errors'])
        operations, _, _ = exercise(finish_error=True)
        with self.assertRaises(OSError) as caught:
            self.actions.run_actions(operations)
        self.assertEqual(caught.exception.sequence_result['status'], 'FAILED')
        self.assertEqual(caught.exception.sequence_result['postcheck_errors'][-1]['check'], 'finish')
        for ops in ({**exercise()[0], 'capture': lambda: None}, {'upload': lambda: envelope()}):
            with self.assertRaises(ValueError):
                self.actions.run_actions(ops)

    def test_actual_b4_source_and_profile_evidence_admission(self):
        manifest = json.loads(checked(COMPILED + 'inputs_static.json', MANIFEST_PIN))
        self.assertEqual(len(manifest['files']), 130)
        owner = self.loaded_owner()
        self.assertEqual(owner.bindings, {'upload': self.plan['upload_binding']})
        self.assertEqual(owner.source_hashes['app.ino'], manifest['files']['src/app/app.ino'])
        self.assertEqual(sum(name in owner.fixed_bytes for name in manifest['files']), 130)
        owner.check_evidence()
        for name, key, value in (('native_static01/result.json', 'flags', self.plan['profile']['flags'].replace('-DMOTORS_ALLOWED=0', '-DMOTORS_ALLOWED=1')),
            ('native_static01/result.json', 'flags', self.plan['profile']['flags'].replace('-DSUMOX_B4_STAND=1', '-DSUMOX_B4_STAND=0')),
            ('native_static01/result.json', 'fqbn', 'arduino:zephyr:unoq'),
            ('native_static01/result.json', 'project', 'other.ino'),
            ('native_abi_static01/local_result.json', 'status', 'FAILED'),
            ('native_entry_static01/local_result.json', 'first_error', {'message': 'failed'})):
            path = COMPILED + name
            original = owner.fixed_bytes[path]
            changed = json.loads(original)
            changed[key] = value
            owner.fixed_bytes[path] = canonical(changed)
            with self.subTest(evidence=name, field=key), self.assertRaises(ValueError):
                owner.check_evidence()
            owner.fixed_bytes[path] = original
        owner.fixed_bytes[COMPILED + 'inputs_static.json'] = (ROOT / 'state/analysis/P7_ordinary_app_static_compile_raw/inputs_static.json').read_bytes()
        with self.assertRaises(ValueError):
            owner.load_source()
        for field, value in (('bytes', 92944), ('sha256', '7fa9d41da043931e1237712e1e88bda4151c82933af2ecec97ce3a02184d23ad')):
            owner.bindings = {'upload': copy.deepcopy(self.plan['upload_binding'])}
            owner.bindings['upload']['files']['sketch'][field] = value
            with self.assertRaises(ValueError):
                owner.check_bindings()

    def test_scope_commands_once_only_intent_and_nine_call_bounds(self):
        owner = self.loaded_owner()
        owner.prepare_commands()
        self.assertEqual(set(owner.all_commands), {'adapter-claim', 'cli-initialization', 'cli-builtin-files', 'capabilities', 'upload'})
        self.assertEqual(len(owner.allowed), 6)
        self.assertEqual(dict(owner.timeouts), {'adapter-claim': 60, 'adapter-push': 60,
            'cli-initialization': 60, 'cli-builtin-files': 60, 'capabilities': 60, 'upload': 195})
        self.assertEqual(owner.output, ROOT / RAW / 'native_upload01')
        self.assertEqual(len(self.plan['scope_files']), 10)
        owner.local = lambda: None
        owner.stage_ready = owner.claim_ready = True
        writes = []
        owner.write = lambda name, value: writes.append((name, copy.deepcopy(value)))
        for action, predecessor in (('capture', None), ('upload', envelope())):
            with self.assertRaises(ValueError):
                owner.intent(action, predecessor)
        owner.intent('upload', None)
        with self.assertRaises(ValueError):
            owner.intent('upload', None)
        queried = []
        owner.query = lambda label, limit: (queried.append((label, limit)) or envelope())
        self.assertEqual(owner.action('upload'), envelope())
        with self.assertRaises(ValueError):
            owner.action('upload')
        self.assertEqual(queried, [('upload', 65536)])
        self.assertEqual([name for name, _ in writes], ['upload_attempt.json'])
        owner.counter = owner.transport_calls = 9
        owner.command_counts = dict(self.plan['calls']['per_label'])
        owner.stage_started = owner.stage_intent_ready = owner.stage_claim_verified = True
        owner.stage_dispatches = {'adapter-claim', 'adapter-push'}
        owner.check_counters({'status': 'COMPLETED', 'upload_attempts': 1})
        with self.assertRaises(ValueError):
            owner.check_counters({'status': 'COMPLETED', 'upload_attempts': True})
        with self.assertRaises(ValueError):
            owner.transport(self.subject.native_arguments(owner.all_commands['upload']), 195, 'upload')
        owner.counter = owner.transport_calls = 10
        with self.assertRaises(ValueError):
            owner.check_counters({'status': 'FAILED'})
        with tempfile.TemporaryDirectory(prefix='d221-scope-') as directory:
            path = Path(directory) / RAW / 'upload01_scope.json'
            path.parent.mkdir(parents=True)
            scope = self.scope()
            path.write_bytes(canonical(scope))
            local = self.subject.UploadRun(HEAD, root=directory)
            local.load_scope()
            self.assertEqual(local.expected_identity, self.plan['expected_identity'])
            for key, value in (('run_id', 'ordinary-app-9044ebbb-run01'), ('board', 2629958581), ('source_sha256', '0' * 64)):
                changed = copy.deepcopy(scope)
                changed[key] = value
                path.write_bytes(canonical(changed))
                with self.assertRaises(ValueError):
                    local.load_scope()
            changed = copy.deepcopy(scope)
            changed['files']['capture.py'] = '0' * 64
            path.write_bytes(canonical(changed))
            with self.assertRaises(ValueError):
                local.load_scope()

    def test_caller_inherited_bodies_success_order_and_staging_failure(self):
        old = functions(checked('state/analysis/P7_ordinary_app_run_raw/run.py',
            (24859, 'f48a8be9fa380a2a922613d188ae7622eafffdf3dc5fec12edc1372b4f7fc2d2')), 'InertRun')
        for name in ('head', 'source_inventory', 'load_baselines', 'state_bytes', 'check_capability', 'stage', 'diagnostics'):
            self.assertEqual(inspect.getsource(getattr(self.subject.UploadRun, name)).strip(), old[name])
        legacy = functions(checked('state/analysis/P7_motor_fault_raw/inert_run.py',
            (23100, '8b47b1d6e9073179e4f587e09ce04e1a1c0cfc6797daf3151d0a7126d279f56a')), 'InertRun')
        for name in ('check_adb', 'check_state', 'local', 'admit', 'identity_record', 'action', 'failed_finish', 'finish'):
            self.assertEqual(inspect.getsource(getattr(self.subject.UploadRun, name)).strip(), legacy[name])
        parent, check = self.subject.UploadRun, self
        class Controlled(parent):
            def __init__(self, stage_failure=False):
                super().__init__(HEAD, root=ROOT)
                self.events, self.stage_bad = [], stage_failure
            def admit(self):
                self.events.append('admit')
            def claim(self):
                self.events.append('claim')
            def stage(self):
                self.events.append('stage')
                if self.stage_bad:
                    raise ValueError('staging-first-error')
            def local(self):
                self.events.append('local')
            def prerequisites(self):
                self.events.append('prerequisites')
                if self.stage_bad:
                    raise OSError('closing-prerequisite')
            def intent(self, action, predecessor):
                check.assertEqual((action, predecessor), ('upload', None))
                self.events.append('intent')
            def action(self, action):
                check.assertEqual(action, 'upload')
                self.events.append('upload')
                return envelope()
            def finish(self, result):
                self.events.append('finish')
        owner = Controlled()
        result = owner.run()
        self.assertEqual(result['status'], 'COMPLETED')
        self.assertEqual(result['upload_attempts'], 1)
        self.assertEqual(owner.events, ['admit', 'claim', 'stage', 'local', 'prerequisites', 'intent', 'upload', 'local', 'prerequisites', 'finish'])
        with self.assertRaises(ValueError):
            owner.run()
        owner = Controlled(stage_failure=True)
        result = owner.run()
        self.assertEqual((result['status'], result['upload_attempts']), ('FAILED', 0))
        self.assertIn('staging-first-error', result['first_error']['message'])
        self.assertEqual(result['postcheck_errors'][0]['check'], 'prerequisites')
        self.assertEqual(owner.events[-3:], ['local', 'prerequisites', 'finish'])
        self.assertNotIn('upload', owner.events)
        self.assertNotIn('capture', result)

    def test_cli_check_only_and_canonical_head_selection(self):
        fake = mock.Mock()
        with mock.patch.object(self.subject, 'UploadRun', return_value=fake) as constructor:
            self.assertEqual(self.subject.main(['--check-only', '--reviewed-head', HEAD]), 0)
            constructor.assert_called_once_with(HEAD)
            fake.admit.assert_called_once_with()
            fake.run.assert_not_called()
        for argv in (['--reviewed-head', HEAD], ['--check-only', '--execute', '--reviewed-head', HEAD],
                     ['--check-only', '--reviewed-head', 'A' * 40], ['--check-only', '--reviewed-head', 'a' * 39]):
            with mock.patch.object(self.subject, 'UploadRun') as constructor, mock.patch.object(sys, 'stderr', io.StringIO()):
                with self.assertRaises(SystemExit):
                    self.subject.main(argv)
                constructor.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
