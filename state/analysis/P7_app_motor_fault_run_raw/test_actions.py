# Tests D189 action framing and replies from the caller contract, implementation unread.
# Keeps staged code identity, bounded decoding and conditional capture independently checked.
# Freeze before Python -B execution; RAM fixtures and controlled modules only, no native calls.
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
import pwd
import shlex
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

import test_remote as remote_oracle

HERE = Path(__file__).resolve().parent
RUN, SOURCE = remote_oracle.RUN, remote_oracle.SOURCE
STAGED = remote_oracle.PARENT + '/' + RUN + '-adapter/remote.py'
ADAPTER_PIN = {'path': STAGED, 'bytes': 10518,
               'sha256': 'd796489fc812a509f5ef1edbcd487a4a3afe4adc76960a94ba9c1d3ec075e10a'}
P0 = '/home/arduino/sumox26-capture-tools/runtime-a4d58b3cbac8/p0_capture.py'
P0_HASH = '885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
PREFIX = ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino',
          'LOGNAME=arduino', 'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C',
          '/usr/bin/python3', '-I', '-B', '-c']
ENVELOPE_KEYS = {'schema', 'action', 'run_id', 'source_sha256', 'report',
                 'remote_result_path', 'full_result_bytes', 'full_result_sha256',
                 'first_error', 'postcheck_errors', 'report_origin'}
REAL_SHA256 = hashlib.sha256
CONTROL = '_d189_independent_action_control'


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def sha(raw):
    return REAL_SHA256(raw).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sources():
    raw = remote_oracle.dependency_sources()
    return {'helper': raw['helper'], 'support': raw['capture'], 'upload': raw['upload']}


def common_report(action):
    return {'schema': 'app-motor-fault-' + action + '-result-v1',
            'run_id': RUN, 'source_sha256': SOURCE,
            'status': 'UPLOADED' if action == 'upload' else 'COLLECTED',
            'started_utc': '2026-09-25T15:00:00Z', 'finished_utc': '2026-09-25T15:00:03Z',
            'started_monotonic': 10.0, 'finished_monotonic': 13.0,
            'first_error': None, 'postcheck_errors': []}


def report(action, streams=False):
    value = common_report(action)
    if action == 'upload':
        value.update(attempts=1, subprocess=dict(remote_oracle.SUCCESS))
        if streams:
            value.update(stdout='full controlled stdout\n', stderr='full controlled stderr\n')
        return value
    reads = [{'name': name, 'address': address, 'bytes': size,
              'sha256': sha(name.replace('before.', '').replace('after.', '').encode()),
              'file': f'{index:02d}-{name}.bin'}
             for index, (name, address, size) in enumerate(remote_oracle.PLAN)]
    value.update(counts={'commands': 26, 'reads': 26, 'requested_bytes': 727088},
                 wait={'requested_seconds': 2, 'before': 10.5, 'after': 12.5}, reads=reads,
                 analysis={'schema': 'app-motor-fault-capture-analysis-v1',
                           'coherence': 'UNPROVEN', 'snapshots': copy.deepcopy(reads[7:19]),
                           'flash': dict.fromkeys(('before_loader', 'before_sketch',
                                                  'after_loader', 'after_sketch'), True)})
    return value


def envelope(action):
    full = report(action, streams=True)
    compact = {key: value for key, value in full.items() if key not in ('stdout', 'stderr')}
    raw = canonical(full)
    return {'schema': 'app-motor-fault-action-v1', 'action': action, 'run_id': RUN,
            'source_sha256': SOURCE, 'report': compact, 'report_origin': 'returned',
            'remote_result_path': remote_oracle.PARENT + '/' + RUN + '-' + action + '/' + action + '_result.json',
            'full_result_bytes': len(raw), 'full_result_sha256': sha(raw),
            'first_error': None, 'postcheck_errors': []}


def refresh(value):
    raw = canonical(value['report'])
    value.update(full_result_bytes=len(raw), full_result_sha256=sha(raw))
    return value


def decode_command(command):
    token = command[-1]
    compressed = base64.b85decode(token[4:]) if token.startswith('b85:') else base64.b64decode(token, validate=True)
    decoder = bz2.BZ2Decompressor()
    raw = decoder.decompress(compressed)
    if not decoder.eof or decoder.unused_data:
        raise AssertionError('Not one complete BZ2 member')
    return raw, json.loads(raw)


class Bootstrap:
    """Real inline helper, synthetic exact-length staged adapter and p0 module.

    Only those two synthetic blobs map to their contract hashes. Descriptor reads
    traverse a real RAM filesystem; board ownership is the only stat substitution.
    """
    def __init__(self, case, action):
        self.case, self.action = case, action
        self.events, self.opens = [], []
        self.outward, self.drift = None, None
        self.saved = report(action, streams=True)
        self.control = ModuleType(CONTROL)
        self.control.invoke, self.control.dependencies = self.invoke, self.dependencies
        self.control.loader_image = object()
        adapter = ('import ' + CONTROL + ' as c\n'
                   'def load_dependencies(sources): return c.dependencies(sources)\n'
                   'def upload(dependencies, **kwargs): return c.invoke("upload", kwargs)\n'
                   'def collect(dependencies, loader_image, **kwargs):\n'
                   ' assert loader_image is c.loader_image\n'
                   ' return c.invoke("capture", kwargs)\n').encode()
        parser = ('import ' + CONTROL + ' as c\nloader_image=c.loader_image\n').encode()
        self.blobs = {STAGED: adapter + b'#' + b' ' * (10518 - len(adapter) - 2) + b'\n',
                      P0: parser + b'#' + b' ' * (18880 - len(parser) - 2) + b'\n'}

    def dependencies(self, supplied):
        expected = remote_oracle.dependency_sources()
        self.case.assertEqual(supplied, expected)
        self.events.append('dependencies')
        return SimpleNamespace()

    def invoke(self, action, kwargs):
        self.case.assertEqual(action, self.action)
        self.case.assertEqual(kwargs['bindings'], remote_oracle.bindings(action))
        self.events.append(action)
        target = self.root / envelope(action)['remote_result_path'].lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(canonical(self.saved))
        if self.drift:
            (self.root / self.drift.lstrip('/')).write_bytes(b'changed after action')
        if self.outward:
            raise self.outward
        return copy.deepcopy(self.saved)

    def run(self, command=None, corrupt_before=None):
        command = self.case.command(self.action) if command is None else command
        with tempfile.TemporaryDirectory(prefix='sumox-d189-bootstrap-', dir='/dev/shm') as folder:
            self.root = Path(folder)
            for logical, raw in self.blobs.items():
                path = self.root / logical.lstrip('/')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'corrupt' if logical == corrupt_before else raw)
            real_open, real_stat, real_fstat = os.open, os.stat, os.fstat
            pinned = {self.blobs[STAGED]: ADAPTER_PIN['sha256'], self.blobs[P0]: P0_HASH}
            class Hash:
                def __init__(self, data=b'', **kwargs):
                    self.raw = bytes(data)
                def update(self, data):
                    self.raw += bytes(data)
                def hexdigest(self):
                    return pinned.get(self.raw, sha(self.raw))
                def digest(self):
                    return bytes.fromhex(self.hexdigest())
            def opened(path, flags, *args, **kwargs):
                if str(path) == '/':
                    self.opens.append('/')
                    return real_open(self.root, flags, *args, **kwargs)
                if str(path) in ('remote.py', 'p0_capture.py'):
                    self.opens.append(str(path))
                return real_open(path, flags, *args, **kwargs)
            def owned(info):
                fields = {key: getattr(info, key) for key in dir(info) if key.startswith('st_')}
                return SimpleNamespace(**dict(fields, st_uid=1000))
            class CapturedStdout(io.StringIO):
                @property
                def buffer(self):
                    return self
                def write(self, value):
                    return super().write(value.decode() if isinstance(value, bytes) else value)
            before, stream, failure = dict(sys.modules), CapturedStdout(), None
            sys.modules[CONTROL] = self.control
            try:
                with contextlib.ExitStack() as stack:
                    stack.enter_context(mock.patch.object(sys, 'argv', ['-c', *command[-3:]]))
                    stack.enter_context(mock.patch.object(hashlib, 'sha256', Hash))
                    stack.enter_context(mock.patch.object(os, 'open', opened))
                    stack.enter_context(mock.patch.object(os, 'stat', side_effect=lambda *a, **k: owned(real_stat(*a, **k))))
                    stack.enter_context(mock.patch.object(os, 'fstat', side_effect=lambda *a, **k: owned(real_fstat(*a, **k))))
                    stack.enter_context(mock.patch.object(os, 'geteuid', return_value=1000))
                    stack.enter_context(mock.patch.object(pwd, 'getpwuid', return_value=SimpleNamespace(pw_name='arduino', pw_dir='/home/arduino')))
                    stack.enter_context(contextlib.redirect_stdout(stream))
                    try:
                        exec(compile(command[-4], '<public-build-command-bootstrap>', 'exec'), {'__name__': '__main__'})
                    except BaseException as error:
                        if not isinstance(error, SystemExit) or error.code not in (0, None):
                            failure = error
            finally:
                for key in set(sys.modules) - set(before):
                    sys.modules.pop(key, None)
                for key, value in before.items():
                    if sys.modules.get(key) is not value:
                        sys.modules[key] = value
            return stream.getvalue(), failure


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux controlled descriptor fixtures')
class ActionsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.flags.dont_write_bytecode or not sys.dont_write_bytecode:
            raise RuntimeError('Frozen oracle requires Python -B')
        with mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('Native import')):
            cls.subject = load(HERE / 'actions.py', 'd189_actions_independent_subject')

    def setUp(self):
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        for owner, name in ((subprocess, 'Popen'), (subprocess, 'run'), (os, 'system')):
            self.stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('Native action forbidden')))

    def command(self, action='upload', **changes):
        arguments = dict(action=action, sources=sources(), bindings=remote_oracle.bindings(action), adapter_pin=dict(ADAPTER_PIN))
        arguments.update(changes)
        return self.subject.build_command(**arguments)

    def test_commands_bind_exact_sources_adapter_identity_canonical_payload_and_windows_limit(self):
        for action in ('upload', 'capture'):
            with self.subTest(action=action):
                command = self.command(action)
                self.assertEqual(command[:len(PREFIX)], PREFIX)
                self.assertEqual(command[-3], action)
                raw, value = decode_command(command)
                self.assertEqual(raw, canonical(value))
                self.assertEqual(command[-2], sha(raw))
                self.assertLessEqual(len(raw), 196608)
                self.assertEqual(value['run_id'], RUN)
                self.assertEqual(value['source_sha256'], SOURCE)
                self.assertEqual(value['bindings'], remote_oracle.bindings(action))
                self.assertIn(ADAPTER_PIN, value.values())
                self.assertEqual(set(value['sources']), {'helper', 'support', 'upload'})
                for role, expected in sources().items():
                    self.assertEqual(value['sources'][role], {'source': expected.decode(), 'sha256': sha(expected)})
                native = [ADB, '-s', '2629958581', 'shell', '-T', shlex.join(command)]
                self.assertLessEqual(len(subprocess.list2cmdline(native).encode('utf-16-le')) // 2 + 1, 30000)

    def test_build_rejects_wrong_roles_bytes_identities_and_staging_pins(self):
        bad = [dict(action='reset'), dict(action=True), dict(sources={}),
               dict(sources=dict(sources(), extra=b'x'))]
        for role in sources():
            for raw in (b'', sources()[role] + b'\n', bytearray(sources()[role]), None):
                bad.append(dict(sources=dict(sources(), **{role: raw})))
        for key, value in (('schema', 'wrong'), ('run_id', RUN + 'x'),
                           ('source_sha256', '0' * 64), ('output', '/tmp/other')):
            bad.append(dict(bindings=dict(remote_oracle.bindings('upload'), **{key: value})))
        for key, value in (('path', STAGED + '/'), ('bytes', True), ('bytes', 10519),
                           ('sha256', '0' * 64), ('extra', 1)):
            bad.append(dict(adapter_pin=dict(ADAPTER_PIN, **{key: value})))
        for changes in bad:
            with self.subTest(fields=list(changes)), self.assertRaises(Exception):
                self.command(**changes)

    def test_bootstrap_rejects_bad_framing_before_root_or_module_execution(self):
        command = self.command()
        raw, value = decode_command(command)
        changed = copy.deepcopy(value)
        changed['sources']['helper']['source'] += '\n'
        changed['sources']['helper']['sha256'] = sha(changed['sources']['helper']['source'].encode())
        frames = [b'{"run_id":0,"run_id":1}', b'{"x":NaN}', b' ' + raw,
                  raw + b'{}', b' ' * 196609, canonical(changed)]
        variants = []
        for frame in frames:
            variants.append((sha(frame), base64.b64encode(bz2.compress(frame)).decode()))
        compressed = bz2.compress(raw)
        variants += [('0' * 64, command[-1]),
                     (sha(raw), base64.b64encode(compressed + bz2.compress(b'{}')).decode()),
                     (sha(raw), base64.b64encode(compressed[:-1]).decode()),
                     (sha(raw), 'b85:!'), (sha(raw), '%%%')]
        for digest, token in variants:
            with self.subTest(token=token[:20]):
                selected = command[:-2] + [digest, token]
                fixture = Bootstrap(self, 'upload')
                text, failure = fixture.run(selected)
                self.assertIsNotNone(failure)
                self.assertEqual(text, '')
                self.assertEqual(fixture.opens, [])
                self.assertEqual(fixture.events, [])

    def test_bootstrap_success_checks_staged_adapter_and_capture_parser_again(self):
        for action in ('upload', 'capture'):
            with self.subTest(action=action):
                fixture = Bootstrap(self, action)
                text, failure = fixture.run()
                self.assertIsNone(failure, repr(failure))
                value = json.loads(text)
                self.assertEqual(set(value), ENVELOPE_KEYS)
                self.assertEqual(text.encode(), canonical(value))
                self.assertLessEqual(len(text.encode()), 65536)
                self.subject.validate_reply(action, value)
                self.assertEqual(value['report_origin'], 'returned')
                self.assertEqual(fixture.events, ['dependencies', action])
                self.assertGreaterEqual(fixture.opens.count('remote.py'), 2)
                self.assertEqual(fixture.opens.count('p0_capture.py'), 0 if action == 'upload' else 2)
                self.assertEqual(value['full_result_sha256'], sha(canonical(fixture.saved)))

    def test_changed_staged_adapter_and_installed_parser_never_dispatch(self):
        for action, path in (('upload', STAGED), ('capture', STAGED), ('capture', P0)):
            fixture = Bootstrap(self, action)
            text, failure = fixture.run(corrupt_before=path)
            if failure is None:
                value = json.loads(text)
                self.assertIsNotNone(value['first_error'])
                with self.assertRaises(Exception):
                    self.subject.validate_reply(action, value)
            self.assertNotIn(action, fixture.events)

    def test_closure_drift_cannot_be_overridden_by_successful_inner_report(self):
        for action, path in (('upload', STAGED), ('capture', STAGED), ('capture', P0)):
            fixture = Bootstrap(self, action)
            fixture.drift = path
            text, failure = fixture.run()
            self.assertIsNone(failure, repr(failure))
            value = json.loads(text)
            self.assertEqual(value['report']['status'], 'UPLOADED' if action == 'upload' else 'COLLECTED')
            self.assertIsNotNone(value['first_error'])
            self.assertTrue(value['postcheck_errors'])
            with self.assertRaises(Exception):
                self.subject.validate_reply(action, value)

    def test_outward_close_error_preserves_unattributed_durable_report_and_fails(self):
        for action in ('upload', 'capture'):
            fixture = Bootstrap(self, action)
            fixture.outward = OSError('outward descriptor close failure')
            fixture.saved.update(status='FAILED', first_error={'type': 'ValueError', 'message': 'original inner failure'})
            text, failure = fixture.run()
            self.assertIsNone(failure, repr(failure))
            value = json.loads(text)
            self.assertEqual(value['first_error']['message'], 'outward descriptor close failure')
            self.assertEqual(value['report_origin'], 'durable_unattributed')
            self.assertEqual(value['report']['first_error']['message'], 'original inner failure')
            self.assertEqual(value['full_result_sha256'], sha(canonical(fixture.saved)))
            with self.assertRaises(Exception):
                self.subject.validate_reply(action, value)

    def test_reply_requires_exact_envelope_origin_identity_and_clean_errors(self):
        for action in ('upload', 'capture'):
            good = envelope(action)
            self.subject.validate_reply(action, good)
            mutations = [lambda v: v.update(extra=1), lambda v: v.pop('report_origin'),
                         lambda v: v.update(report_origin='durable_unattributed'),
                         lambda v: v.update(source_sha256='0' * 64),
                         lambda v: v.update(remote_result_path='/tmp/result.json'),
                         lambda v: v.update(first_error={'type': 'OSError', 'message': 'close'}),
                         lambda v: v.update(postcheck_errors=[{'check': 'source', 'message': 'changed'}]),
                         lambda v: v.update(full_result_bytes=True),
                         lambda v: v.update(full_result_sha256='A' * 64)]
            for mutation in mutations:
                value = copy.deepcopy(good)
                mutation(value)
                with self.subTest(action=action, mutation=mutations.index(mutation)), self.assertRaises(Exception):
                    self.subject.validate_reply(action, value)

    def test_upload_reply_rejects_partial_ambiguous_or_expired_process(self):
        mutations = [lambda r: r.update(attempts=0), lambda r: r.update(attempts=True),
                     lambda r: r['subprocess'].update(returncode=False),
                     lambda r: r['subprocess'].update(returncode=1),
                     lambda r: r['subprocess'].update(timed_out=True),
                     lambda r: r['subprocess'].update(reaped=False),
                     lambda r: r.update(finished_monotonic=190),
                     lambda r: r.update(started_monotonic=float('nan'))]
        for mutation in mutations:
            value = envelope('upload')
            mutation(value['report'])
            with self.subTest(mutation=mutations.index(mutation)), self.assertRaises(Exception):
                self.subject.validate_reply('upload', value)

    def test_capture_reply_rejects_any_wrong_read_bracket_snapshot_count_or_wait(self):
        mutations = [lambda r: r['counts'].update(commands=25),
                     lambda r: r['counts'].update(requested_bytes=727089),
                     lambda r: r['counts'].update(reads=True),
                     lambda r: r['reads'][7].update(address=536951184),
                     lambda r: r['reads'][0].update(bytes=65535),
                     lambda r: r['reads'][19].update(sha256='0' * 64),
                     lambda r: r['reads'][0].update(file='../outside'),
                     lambda r: r['reads'].append(copy.deepcopy(r['reads'][0])),
                     lambda r: r['analysis']['snapshots'].pop(),
                     lambda r: r['analysis']['snapshots'][0].update(sha256='0' * 64),
                     lambda r: r['analysis']['flash'].update(after_loader=1),
                     lambda r: r['analysis']['flash'].update(before_sketch=False),
                     lambda r: r['analysis'].update(coherence='PROVEN'),
                     lambda r: r['analysis'].update(relocation={}),
                     lambda r: r['wait'].update(after=12.499),
                     lambda r: r['wait'].update(before=9, after=11),
                     lambda r: r['wait'].update(requested_seconds=True)]
        for mutation in mutations:
            value = envelope('capture')
            mutation(value['report'])
            refresh(value)
            with self.subTest(mutation=mutations.index(mutation)), self.assertRaises(Exception):
                self.subject.validate_reply('capture', value)
        for key, invalid in (('full_result_bytes', 1), ('full_result_sha256', '0' * 64)):
            value = envelope('capture')
            value[key] = invalid
            with self.assertRaises(Exception):
                self.subject.validate_reply('capture', value)

    def operations(self, failures=None, replies=None):
        events, counts, failures = [], {}, failures or {}
        replies = {'upload': envelope('upload'), 'capture': envelope('capture'), **(replies or {})}
        def invoke(name, *args):
            events.append((name, copy.deepcopy(args)))
            counts[name] = counts.get(name, 0) + 1
            error = failures.get((name, counts[name]))
            if error:
                raise error
            return copy.deepcopy(replies.get(name))
        return {name: lambda *args, name=name: invoke(name, *args)
                for name in ('local', 'prerequisites', 'intent', 'upload', 'capture', 'finish')}, events

    def test_success_sequence_is_exact_and_passes_retained_upload_predecessor(self):
        operations, events = self.operations()
        value = self.subject.run_actions(operations)
        self.assertEqual(value['schema'], 'app-motor-fault-sequence-v1')
        self.assertEqual(value['status'], 'COMPLETED')
        self.assertEqual([event[0] for event in events], ['local', 'prerequisites', 'intent', 'upload',
                         'local', 'prerequisites', 'intent', 'capture', 'local', 'prerequisites', 'finish'])
        self.assertEqual(events[2][1], ('upload', None))
        self.assertEqual(events[6][1], ('capture', value['upload']))
        self.assertEqual((value['upload_attempts'], value['capture_attempts']), (1, 1))

    def test_upload_error_or_unattributed_success_suppresses_capture_and_keeps_closing_errors(self):
        uncertain = envelope('upload')
        uncertain['report_origin'] = 'durable_unattributed'
        for error, replies in ((OSError('first upload error'), {}), (None, {'upload': uncertain})):
            failures = {('local', 2): OSError('local closure error'),
                        ('prerequisites', 2): OSError('prerequisite closure error')}
            if error:
                failures['upload', 1] = error
            operations, events = self.operations(failures, replies)
            value = self.subject.run_actions(operations)
            self.assertEqual(value['status'], 'FAILED')
            self.assertEqual(value['capture_attempts'], 0)
            self.assertNotIn('capture', [event[0] for event in events])
            self.assertEqual([event[0] for event in events[-3:]], ['local', 'prerequisites', 'finish'])
            self.assertEqual(len(value['postcheck_errors']), 2)
            if error:
                self.assertEqual(value['first_error']['message'], 'first upload error')

    def test_finish_failure_retains_original_sequence_error_without_retry(self):
        finish = OSError('finish receipt failure')
        operations, events = self.operations({('upload', 1): TimeoutError('uncertain upload'), ('finish', 1): finish})
        with self.assertRaises(OSError) as caught:
            self.subject.run_actions(operations)
        self.assertIs(caught.exception, finish)
        result = caught.exception.sequence_result
        self.assertEqual(result['first_error']['message'], 'uncertain upload')
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(sum(event[0] == 'upload' for event in events), 1)
        self.assertEqual(sum(event[0] == 'capture' for event in events), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
