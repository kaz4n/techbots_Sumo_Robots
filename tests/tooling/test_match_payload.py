# Tests D183 MATCH payload framing and replies from the adopted public contract.
# Keeps complete payload identity and bounded success evidence separate from exit zero.
# Freeze before running with Python -B; all bootstrap source modules are inert fixtures.
from contextlib import ExitStack, redirect_stdout
import base64
import bz2
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SOURCE = '1234567890abcdef' * 4
BUILD = '234567890abcdef1' * 2
RUN = '34567890abcdef12' * 2
BOOT = '456789ab-cdef-1234-5678-90abcdef1234'
PARENT = '/home/arduino/sumox26_codex_build'
FQBN = 'arduino:zephyr:unoq:wait_linux_boot=no'
PREFIX = ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino', 'LOGNAME=arduino',
          'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C', '/usr/bin/python3', '-I', '-B', '-c']
NATIVE = ['adb', '-s', 'synthetic-target', 'shell', '-T']
CONTROL = '_d183_payload_test_control'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def output_path(source=SOURCE, run=RUN):
    return PARENT + '/match-' + source[:8] + '-' + run + '-upload'


def bindings(source=SOURCE, build=BUILD, run=RUN):
    uploader = load(ROOT / 'state/analysis/P7_static_startup_raw/upload_remote.py',
                    'd183_fixture_uploader')
    sketch = PARENT + '/' + source + '/app'
    runroot = PARENT + '/_app_builds/native-app-v1/' + source + '/match-immediate/' + build
    files = dict(uploader.FILE_PATHS)
    files.update(raw=runroot + '/build/app.ino.elf',
                 sketch=runroot + '/build/app.ino.elf-zsk.bin',
                 exported=runroot + '/artifacts/app.ino.elf-zsk.bin')
    return {'schema': 'fixed-match-upload-v1', 'run_id': run, 'source_sha256': source,
            'boot_id': BOOT, 'uid': 1000, 'output': output_path(source, run),
            'files': {name: {'path': path, 'bytes': 8, 'sha256': 'a' * 64}
                      for name, path in files.items()},
            'directories': {path: ['fixture'] for path in uploader.DIRECTORIES},
            'absent': list(uploader.ABSENT[:-3]) + [sketch + '/sketch.' + ext
                                                    for ext in ('yaml', 'yml', 'json')]}


def full_report(source=SOURCE, run=RUN):
    return {'schema': 'match-upload-result-v1', 'run_id': run, 'source_sha256': source,
            'status': 'UPLOADED', 'attempts': 1,
            'started_utc': '2026-09-25T10:00:00+00:00',
            'finished_utc': '2026-09-25T10:00:01+00:00',
            'started_monotonic': 10.0, 'finished_monotonic': 11.0,
            'subprocess': {'returncode': 0, 'timed_out': False, 'reaped': True},
            'stdout': 'synthetic upload\n', 'stderr': '', 'first_error': None,
            'postcheck_errors': []}


def reply(payload_sha='b' * 64, source=SOURCE, build=BUILD, run=RUN):
    report = full_report(source, run)
    raw = canonical(report)
    return {'schema': 'match-action-v1', 'source_sha256': source, 'build_id': build,
            'run_id': run, 'payload_sha256': payload_sha,
            'remote_result_path': output_path(source, run) + '/upload_result.json',
            'full_result_bytes': len(raw), 'full_result_sha256': digest(raw),
            'report': {key: value for key, value in report.items()
                       if key not in ('stdout', 'stderr')}, 'first_error': None}


def fixture_sources():
    start = 'import ' + CONTROL + ' as c\nc.events.append("loaded")\n'
    support = start + 'import json\ndef json_bytes(v):\n return c.canonical(v)\n'
    adapter = (start + 'def upload_match(helper, support, uploader, **kwargs):\n'
               ' c.events.append(("upload", kwargs))\n'
               ' if c.error is not None: raise c.error\n'
               ' return c.report\n')
    return {'helper': start.encode(), 'support': support.encode(),
            'upload': start.encode(), 'adapter': adapter.encode()}


class MatchPayloadTests(unittest.TestCase):
    def setUp(self):
        self.subject = load(ROOT / 'tools/match_payload.py', 'd183_payload_subject')
        self.sources, self.bindings = fixture_sources(), bindings()
        self.guard = mock.patch.object(subprocess, 'Popen',
                                       side_effect=AssertionError('Native process forbidden'))
        self.guard.start()
        self.addCleanup(self.guard.stop)

    def command(self, **kwargs):
        options = dict(sources=self.sources, bindings=self.bindings, source_sha256=SOURCE,
                       build_id=BUILD, run_id=RUN, native_prefix=NATIVE)
        options.update(kwargs)
        return self.subject.build_command(**options)

    def validate(self, value, **kwargs):
        options = dict(source_sha256=SOURCE, build_id=BUILD, run_id=RUN,
                       payload_sha256='b' * 64)
        options.update(kwargs)
        text = canonical(value).decode() if not isinstance(value, str) else value
        return self.subject.validate_reply(text, **options)

    def reject(self, value, **kwargs):
        with self.assertRaises((ValueError, TypeError)):
            self.validate(value, **kwargs)

    def payload(self):
        return {'schema': 'match-upload-payload-v1', 'source_sha256': SOURCE,
                'build_id': BUILD, 'run_id': RUN, 'bindings': self.bindings,
                'sources': {role: {'source': raw.decode('utf-8'), 'sha256': digest(raw)}
                            for role, raw in self.sources.items()}}

    def bootstrap(self, *, raw=None, token=None, sha=None, report=None, error=None,
                  isolated=True, bytecode=True):
        command = self.command()
        raw = canonical(self.payload()) if raw is None else raw
        token = base64.b85encode(bz2.compress(raw)).decode() if token is None else token
        sha = digest(raw) if sha is None else sha
        control = types.ModuleType(CONTROL)
        control.events, control.report, control.error = [], full_report(), error
        control.canonical = canonical
        if report is not None:
            control.report = report
        original_flags = sys.flags
        class Flags:
            def __getattr__(self, name):
                if name == 'isolated':
                    return int(isolated)
                if name == 'dont_write_bytecode':
                    return int(bytecode)
                return getattr(original_flags, name)
        class Stream(io.StringIO):
            @property
            def buffer(self):
                return self

            def write(self, text):
                return super().write(text.decode() if isinstance(text, bytes) else text)
        stream, caught = Stream(), None
        with ExitStack() as stack:
            stack.enter_context(mock.patch.dict(sys.modules, {CONTROL: control}))
            stack.enter_context(mock.patch.object(sys, 'argv', ['-c', sha, token]))
            stack.enter_context(mock.patch.object(sys, 'flags', Flags()))
            stack.enter_context(mock.patch.object(sys, 'dont_write_bytecode', bytecode))
            stack.enter_context(mock.patch.object(os, 'open', side_effect=AssertionError('filesystem')))
            stack.enter_context(redirect_stdout(stream))
            try:
                exec(compile(command[len(PREFIX)], '<D183-command-bootstrap>', 'exec'),
                     {'__name__': '__main__'})
            except BaseException as problem:
                if not isinstance(problem, SystemExit) or problem.code not in (None, 0):
                    caught = problem
        return control.events, stream.getvalue(), caught

    def denied_bootstrap(self, **kwargs):
        events, text, error = self.bootstrap(**kwargs)
        self.assertEqual(events, [], 'malformed input must precede every source load')
        self.assertTrue(error is not None or not text or json.loads(text).get('report') is None)

    def test_D183_reply_accepts_exact_projected_success(self):
        value = reply()
        original = copy.deepcopy(value)
        actual = self.validate(value)
        self.assertEqual(actual, original)
        self.assertEqual(value, original)

    def test_D183_reply_all_identity_and_owned_path_bindings_are_exact(self):
        for name in ('schema', 'source_sha256', 'build_id', 'run_id',
                     'payload_sha256', 'remote_result_path'):
            with self.subTest(name=name):
                value = reply()
                value[name] += '0'
                self.reject(value)

    def test_D183_reply_missing_unknown_envelope_fields_rejected(self):
        for name in reply():
            with self.subTest(missing=name):
                value = reply()
                del value[name]
                self.reject(value)
        self.reject({**reply(), 'unexpected': 1})

    def test_D183_reply_missing_unknown_report_fields_rejected(self):
        for name in reply()['report']:
            with self.subTest(missing=name):
                value = reply()
                del value['report'][name]
                self.reject(value)
        for name in ('unexpected', 'stdout', 'stderr'):
            value = reply()
            value['report'][name] = ''
            self.reject(value)

    def test_D183_reply_duplicate_nonfinite_and_trailing_json_rejected(self):
        text = canonical(reply()).decode()
        for altered in (text + '{}', 'prefix' + text,
                        text.replace('"attempts":1', '"attempts":1,"attempts":1'),
                        text.replace('"started_monotonic":10.0', '"started_monotonic":NaN'),
                        text.replace('"started_monotonic":10.0', '"started_monotonic":Infinity')):
            with self.subTest(text=altered[:40]):
                self.reject(altered)

    def test_D183_reply_bound_and_exact_text_type(self):
        for text in (' ' * 65537, [], None, b'{}'):
            with self.subTest(type=type(text)):
                with self.assertRaises((ValueError, TypeError)):
                    self.subject.validate_reply(text, SOURCE, BUILD, RUN, 'b' * 64)

    def test_D183_reply_failed_or_absent_report_cannot_be_success(self):
        for update in ({'report': None, 'full_result_bytes': None, 'full_result_sha256': None,
                        'first_error': {'type': 'ValueError', 'message': 'admission'}},
                       {'first_error': {'type': 'ValueError', 'message': 'failed'}}):
            self.reject({**reply(), **update})
        for name, bad in (('status', 'FAILED'), ('attempts', 0), ('attempts', 2),
                          ('attempts', True), ('schema', 'static-upload-result-v1'),
                          ('source_sha256', 'f' * 64), ('run_id', BUILD),
                          ('first_error', {}), ('postcheck_errors', [{}])):
            value = reply()
            value['report'][name] = bad
            self.reject(value)

    def test_D183_reply_child_exact_types_and_zero_exit_required(self):
        cases = ({'returncode': True}, {'returncode': 1}, {'returncode': None},
                 {'timed_out': 0}, {'timed_out': True}, {'reaped': 1},
                 {'reaped': False}, {'unknown': None})
        for update in cases:
            with self.subTest(update=update):
                value = reply()
                value['report']['subprocess'].update(update)
                self.reject(value)
        for name in ('returncode', 'timed_out', 'reaped'):
            value = reply()
            del value['report']['subprocess'][name]
            self.reject(value)

    def test_D183_reply_monotonic_exact_numeric_nonnegative_and_ordered(self):
        for name in ('started_monotonic', 'finished_monotonic'):
            for bad in (True, '10', None, -1):
                value = reply()
                value['report'][name] = bad
                self.reject(value)
        value = reply()
        value['report']['finished_monotonic'] = 9
        self.reject(value)

    def test_D183_reply_utc_valid_timezone_and_order_required(self):
        for bad in ('not-time', '2026-09-25T10:00:00', '2026-09-25T10:00:00+04:00'):
            value = reply()
            value['report']['started_utc'] = bad
            self.reject(value)
        value = reply()
        value['report']['finished_utc'] = '2026-09-25T09:59:59Z'
        self.reject(value)

    def test_D183_reply_full_result_extent_and_digest_are_typed(self):
        for name, values in (('full_result_bytes', (True, 0, -1, '4', None, 16777217)),
                             ('full_result_sha256', ('', 'A' * 64, 'a' * 63, None))):
            for bad in values:
                value = reply()
                value[name] = bad
                self.reject(value)

    def test_D183_build_rejects_missing_extra_and_nonbyte_sources(self):
        for role in self.sources:
            value = dict(self.sources)
            del value[role]
            with self.assertRaises((ValueError, TypeError)):
                self.command(sources=value)
        for value in ({**self.sources, 'decoder': b'pass'},
                      {**self.sources, 'helper': ''}, {**self.sources, 'helper': b''},
                      {**self.sources, 'helper': b'\xff'}):
            with self.assertRaises((ValueError, TypeError, UnicodeError)):
                self.command(sources=value)

    def test_D183_build_identifiers_are_exact_lowercase_strings(self):
        class Derived(str):
            pass
        for name, good in (('source_sha256', SOURCE), ('build_id', BUILD), ('run_id', RUN)):
            for bad in (good.upper(), good[:-1], good + '0', True, Derived(good)):
                with self.subTest(name=name, bad=bad), self.assertRaises((ValueError, TypeError)):
                    self.command(**{name: bad})

    def test_D183_build_rejects_large_payload_before_any_execution(self):
        with self.assertRaises(ValueError):
            self.command(sources={**self.sources, 'helper': b'#' + b'x' * 196608})

    def test_D183_command_has_fixed_isolated_environment_and_python_flags(self):
        command = self.command()
        self.assertEqual(command[:len(PREFIX)], PREFIX)
        self.assertEqual(shlex.split(shlex.join(command)), command)
        self.assertLessEqual(len(subprocess.list2cmdline(
            NATIVE + [shlex.join(command)]).encode('utf-16-le')) // 2 + 1, 30000)

    def test_D183_native_prefix_participates_in_including_nul_command_bound(self):
        with self.assertRaises(ValueError):
            self.command(native_prefix=['x' * 30000])

    def test_D183_payload_is_canonical_ascii_bound_to_all_sources_and_bindings(self):
        before = copy.deepcopy((self.sources, self.bindings))
        command = self.command()
        compressed = base64.b85decode(command[-1])
        self.assertEqual(base64.b85encode(compressed).decode(), command[-1])
        decoder = bz2.BZ2Decompressor()
        raw = decoder.decompress(compressed, max_length=196609)
        self.assertTrue(decoder.eof)
        self.assertEqual(decoder.unused_data, b'')
        self.assertEqual(raw, canonical(self.payload()))
        self.assertEqual(command[-2], digest(raw))
        self.assertEqual((self.sources, self.bindings), before)
        changed = copy.deepcopy(self.bindings)
        changed['boot_id'] = '56789abc-def0-1234-5678-90abcdef1234'
        self.assertNotEqual(self.command(bindings=changed)[-2], command[-2])

    def test_D183_bootstrap_invokes_only_adapter_once_and_hashes_full_stream_report(self):
        events, text, error = self.bootstrap()
        self.assertIsNone(error)
        uploads = [event for event in events if isinstance(event, tuple)]
        self.assertEqual(len(uploads), 1)
        self.assertEqual(uploads[0][0], 'upload')
        self.assertEqual(uploads[0][1]['bindings'], self.bindings)
        for name, expected in (('source_sha256', SOURCE), ('build_id', BUILD), ('run_id', RUN)):
            self.assertEqual(uploads[0][1][name], expected)
        value = json.loads(text)
        self.assertEqual(value, reply(digest(canonical(self.payload()))))
        self.assertEqual(text.encode('ascii'), canonical(value))

    def test_D183_bootstrap_adapter_failure_cannot_be_accepted(self):
        events, text, error = self.bootstrap(error=RuntimeError('synthetic admission refusal'))
        self.assertEqual(sum(isinstance(event, tuple) for event in events), 1)
        self.assertIsNone(error)
        value = json.loads(text)
        self.assertIsNone(value['report'])
        self.assertIsNone(value['full_result_bytes'])
        self.assertIsNone(value['full_result_sha256'])
        self.assertEqual(value['first_error']['message'], 'synthetic admission refusal')
        self.reject(text, payload_sha256=digest(canonical(self.payload())))

    def test_D183_bootstrap_rejects_digest_truncation_trailing_and_multiple_members(self):
        raw = canonical(self.payload())
        packed = bz2.compress(raw)
        self.denied_bootstrap(sha='f' * 64)
        for value in (packed[:-1], packed + b'x', packed + bz2.compress(b'{}')):
            self.denied_bootstrap(token=base64.b85encode(value).decode())
        self.denied_bootstrap(token=' ' + base64.b85encode(packed).decode())

    def test_D183_bootstrap_requires_isolation_and_no_bytecode_before_source_load(self):
        self.denied_bootstrap(isolated=False)
        self.denied_bootstrap(bytecode=False)

    def test_D183_bootstrap_rejects_bounded_expansion_and_noncanonical_json(self):
        self.denied_bootstrap(raw=b' ' * 196609)
        raw = canonical(self.payload())
        self.denied_bootstrap(raw=raw.rstrip())
        self.denied_bootstrap(raw=b' ' + raw)
        self.denied_bootstrap(raw=raw.replace(b'"schema":', b'"schema":"duplicate","schema":', 1))

    def test_D183_bootstrap_rejects_shape_hash_and_id_errors_before_source_load(self):
        cases = []
        for name in self.payload():
            value = copy.deepcopy(self.payload())
            del value[name]
            cases.append(value)
        value = copy.deepcopy(self.payload())
        value['sources']['adapter']['sha256'] = 'f' * 64
        cases.append(value)
        value = copy.deepcopy(self.payload())
        value['sources']['extra'] = value['sources']['helper']
        cases.append(value)
        for name in ('source_sha256', 'build_id', 'run_id'):
            value = copy.deepcopy(self.payload())
            value[name] = value[name].upper()
            cases.append(value)
        for value in cases:
            self.denied_bootstrap(raw=canonical(value))

    def test_D183_bootstrap_validates_full_binding_shape_before_source_load(self):
        for change in ('extra', 'raw_missing', 'uid_bool', 'package_hash', 'wrong_path'):
            with self.subTest(change=change):
                value = copy.deepcopy(self.payload())
                bound = value['bindings']
                if change == 'extra':
                    bound['extra'] = None
                elif change == 'raw_missing':
                    del bound['files']['raw']
                elif change == 'uid_bool':
                    bound['uid'] = True
                elif change == 'package_hash':
                    bound['files']['exported']['sha256'] = 'f' * 64
                else:
                    bound['files']['raw']['path'] = '/tmp/raw.elf'
                self.denied_bootstrap(raw=canonical(value))

    def test_D183_actual_frozen_source_composition_fits_both_transport_prefixes(self):
        sources = {role: (ROOT / path).read_bytes() for role, path in {
            'helper': 'state/analysis/P7_static_link_probe_raw/static_remote.py',
            'support': 'state/analysis/P7_static_startup_raw/capture_remote.py',
            'upload': 'state/analysis/P7_static_startup_raw/upload_remote.py',
            'adapter': 'tools/match_upload.py'}.items()}
        prefixes = [
            ['C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe',
             '-s', '2629958581', 'shell', '-T'],
            ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
             '-o', 'ConnectTimeout=10', 'arduino@synthetic.local']]
        for prefix in prefixes:
            command = self.command(sources=sources, native_prefix=prefix)
            units = len(subprocess.list2cmdline(prefix + [shlex.join(command)]).encode('utf-16-le')) // 2 + 1
            self.assertLessEqual(units, 30000)


if __name__ == '__main__':
    unittest.main()
