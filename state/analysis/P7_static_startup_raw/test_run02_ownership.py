# Tests explicit run02 ownership from the public contract and frozen fixtures.
# Keeps consumed run01 evidence and module globals separate from new instances.
# Select only new cases; existing suites run unchanged as separate legacy coverage.
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
RAW = 'state/analysis/P7_static_startup_raw/'
RUN01, RUN02 = 'static-fcddbd8e-run01', 'static-fcddbd8e-run02'


def load_fixture(name):
    spec = importlib.util.spec_from_file_location('ownership_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


upload_fixture = load_fixture('test_upload_loader')
capture_fixture = load_fixture('test_capture_remote')
launcher_fixture = load_fixture('test_startup_run')


def projected(bindings):
    result = copy.deepcopy(bindings)
    result['run_id'] = RUN02
    result['output'] = result['output'].replace('-run01-', '-run02-')
    return result


def select_run02(case):
    case.legacy_bindings = copy.deepcopy(case.bindings)
    case.legacy_output_name = getattr(case.subject, 'OUTPUT_NAME', None)
    case.bindings = projected(case.bindings)
    case.output = case.logical(case.bindings['output'])
    case.receipt_dir = case.output


def unchanged_globals(case):
    case.assertEqual(case.subject.BINDINGS, case.legacy_bindings)
    case.assertEqual(getattr(case.subject, 'OUTPUT_NAME', None), case.legacy_output_name)


class UploadOwnership(upload_fixture.UploadLoaderContract):
    def setUp(self):
        super().setUp()
        select_run02(self)

    def upload(self, **kwargs):
        options = dict(fs_root=self.root, executor=self.execute, clock=self.clock,
                       bindings=self.bindings, run_id=RUN02)
        options.update(kwargs)
        return self.subject.upload_loader(self.helper, self.support, **options)

    def test_run02_success_owns_only_fresh_output_and_keeps_globals(self):
        self.assert_report(self.upload(), 'UPLOADED')
        self.assertFalse(self.logical(self.legacy_bindings['output']).exists())
        unchanged_globals(self)
        with self.assertRaises(Exception):
            self.upload()
        self.assertEqual(len(self.calls), 1)

    def test_wrong_run_binding_output_or_source_rejected_before_claim(self):
        for run in ('static-fcddbd8e-run03', 'run02', None, 2, True, RUN01):
            with self.subTest(run=run), self.assertRaises(Exception):
                self.upload(run_id=run)
        for field, value in (('run_id', RUN01), ('output', self.legacy_bindings['output']),
                              ('output', '/tmp/alternative'), ('source_sha256', 'a' * 64)):
            candidate = copy.deepcopy(self.bindings)
            candidate[field] = value
            with self.subTest(field=field), self.assertRaises(Exception):
                self.upload(bindings=candidate)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.output.exists())
        unchanged_globals(self)

    def test_legacy_upload_rejects_run02_and_has_no_run_id_override(self):
        options = dict(fs_root=self.root, executor=self.execute, clock=self.clock)
        with self.assertRaises(Exception):
            self.subject.upload(self.helper, self.support, bindings=self.bindings, **options)
        with self.assertRaises(TypeError):
            self.subject.upload(self.helper, self.support, run_id=RUN02, **options)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.output.exists())

    def test_explicit_legacy_bindings_still_work_without_global_rebinding(self):
        self.bindings = copy.deepcopy(self.legacy_bindings)
        self.output = self.logical(self.bindings['output'])
        self.receipt_dir = self.output
        result = self.subject.upload(self.helper, self.support, fs_root=self.root,
                                     executor=self.execute, clock=self.clock, bindings=self.bindings)
        self.assert_report(result, 'UPLOADED')
        unchanged_globals(self)

    def test_caller_mutation_does_not_change_admitted_instance_pins(self):
        self.after_execute = lambda: self.bindings['files']['cli'].update(sha256='0' * 64)
        self.assert_report(self.upload(), 'UPLOADED')
        unchanged_globals(self)

    def test_nested_legacy_instance_does_not_change_active_run02(self):
        inner_results, inner_calls = [], []
        def inner_execute(argv, stdout, stderr, timeout):
            unchanged_globals(self)
            self.assertEqual(argv, upload_fixture.legacy.ARGV)
            inner_calls.append(argv)
            for path in (stdout, stderr):
                self.local_argument(path).write_bytes(b'')
            return dict(upload_fixture.legacy.SUCCESS)
        def nested():
            unchanged_globals(self)
            inner_results.append(self.subject.upload_loader(
                self.helper, self.support, fs_root=self.root, executor=inner_execute,
                clock=self.clock, bindings=self.legacy_bindings, run_id=RUN01))
        self.after_execute = nested
        self.assert_report(self.upload(), 'UPLOADED')
        self.assertEqual(len(inner_calls), 1)
        self.assertEqual(inner_results[0]['status'], 'UPLOADED')
        self.assertEqual(inner_results[0]['run_id'], RUN01)
        unchanged_globals(self)


class CaptureOwnership(capture_fixture.CaptureRemoteContract):
    def setUp(self):
        super().setUp()
        select_run02(self)

    def collect(self, **kwargs):
        options = dict(fs_root=self.root, executor=self.execute, clock=self.clock,
                       sleeper=self.clock.sleep, bindings=self.bindings, run_id=RUN02)
        options.update(kwargs)
        return self.subject.collect(self.helper, self.decoder, self.loader_image, **options)

    def test_run02_collection_has_distinct_consumed_owner_and_no_global_change(self):
        self.assert_report(self.collect(), 'COLLECTED')
        self.assertFalse(self.logical(self.legacy_bindings['output']).exists())
        unchanged_globals(self)
        with self.assertRaises(Exception):
            self.collect()
        self.assertEqual(len(self.calls), 18)

    def test_capture_wrong_identity_output_source_rejected_before_claim(self):
        for run in ('static-fcddbd8e-run03', None, 2, True, RUN01):
            with self.subTest(run=run), self.assertRaises(Exception):
                self.collect(run_id=run)
        for field, value in (('run_id', RUN01), ('output', self.legacy_bindings['output']),
                              ('source_sha256', 'a' * 64)):
            candidate = copy.deepcopy(self.bindings)
            candidate[field] = value
            with self.subTest(field=field), self.assertRaises(Exception):
                self.collect(bindings=candidate)
        self.assertEqual(self.calls, [])
        self.assertFalse(self.output.exists())
        unchanged_globals(self)

    def test_capture_uses_private_bindings_copy(self):
        def mutate(index):
            if index == 0:
                self.bindings['files']['openocd']['sha256'] = '0' * 64
        self.after_execute = mutate
        self.assert_report(self.collect(), 'COLLECTED')
        unchanged_globals(self)

    def test_nested_capture_instances_do_not_share_ownership_state(self):
        inner = SimpleNamespace(assertEqual=self.assertEqual, triples=[])
        decoder = capture_fixture.Decoder(inner)
        reports = []
        output = self.logical(self.legacy_bindings['output'])
        def execute(argv, stdout, stderr, timeout):
            unchanged_globals(self)
            index = len(inner.triples)
            name, address, size = capture_fixture.PLAN[index]
            logical = self.legacy_bindings['output'] + '/{:02d}-{}.bin'.format(index, name)
            self.assertIn('dump_image {{{}}} 0x{:08x} {}'.format(logical, address, size), argv)
            for path in (stdout, stderr):
                self.local_argument(path).write_bytes(b'')
            raw = self.bytes_for((name, address, size))
            (output / '{:02d}-{}.bin'.format(index, name)).write_bytes(raw)
            inner.triples.append((name, address, raw))
            return dict(capture_fixture.SUCCESS)
        def nested(index):
            if index == 0:
                reports.append(self.subject.collect(self.helper, decoder, self.loader_image,
                    fs_root=self.root, executor=execute, clock=self.clock, sleeper=self.clock.sleep,
                    bindings=self.legacy_bindings, run_id=RUN01))
        self.after_execute = nested
        self.assert_report(self.collect(), 'COLLECTED')
        self.assertEqual(len(inner.triples), 18)
        self.assertEqual(reports[0]['run_id'], RUN01)
        self.assertEqual(reports[0]['status'], 'COLLECTED')
        unchanged_globals(self)


class LauncherOwnership(launcher_fixture.StartupContract):
    def run02_reports(self):
        self.operations.upload['run_id'] = RUN02
        self.operations.capture['run_id'] = RUN02

    def test_profiles_retain_historical_pins_and_change_only_two_for_run02(self):
        raw = (HERE / 'native_run01/inputs.json').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         'a129da28f028624edd684025b444b0809042712ad5affaecd7c98b990254a4c4')
        baseline = json.loads(raw)['dependency_pins']
        prefix = 'state/analysis/P7_static_link_probe_raw/runs/f0220228320c4b2aa20c3e5e8264c813/'
        excluded = {prefix + name + '.json' for name in ('0001', '0009', '0017', '0021')}
        self.assertTrue(excluded.issubset(baseline))
        expected = {key: value for key, value in baseline.items() if key not in excluded}
        self.assertEqual(len(expected), 12)
        old, new = self.subject.run_profile('run01'), self.subject.run_profile('run02')
        self.assertEqual(set(old), {'run_id', 'output_name', 'scope', 'dependencies', 'scope_files'})
        self.assertEqual(old['dependencies'], expected)
        self.assertEqual(set(new['dependencies']), set(expected))
        changed = {key for key in expected if new['dependencies'][key] != expected[key]}
        self.assertEqual(changed, {RAW + 'upload_remote.py', RAW + 'capture_remote.py'})
        for key in changed:
            self.assertEqual(new['dependencies'][key], hashlib.sha256((HERE.parents[2] / key).read_bytes()).hexdigest())
        self.assertEqual(old['run_id'], RUN01)
        self.assertEqual(new['run_id'], RUN02)
        self.assertEqual((old['output_name'], new['output_name']), ('native_run01', 'native_run02'))
        self.assertEqual(str(old['scope']).replace('\\', '/'), RAW + 'native_run01_scope.json')
        self.assertEqual(str(new['scope']).replace('\\', '/'), RAW + 'native_run02_scope.json')

    def test_profiles_are_fresh_and_scope_files_are_exact(self):
        old_files = tuple(json.loads((HERE / 'native_run01_scope.json').read_text())['files'])
        old, new = self.subject.run_profile('run01'), self.subject.run_profile('run02')
        self.assertEqual(set(old['scope_files']), set(old_files))
        self.assertIs(type(new['scope_files']), tuple)
        self.assertEqual(new['scope_files'], (RAW + 'startup_run.py', RAW + 'test_run02_ownership.py',
            'state/analysis/P7_startup_run02_contract.md', 'state/reviews/P7_startup_run02_review.md'))
        original = copy.deepcopy(new)
        new['dependencies'].clear()
        new['output_name'] = 'arbitrary'
        self.assertEqual(self.subject.run_profile('run02'), original)
        self.assertEqual(self.subject.run_profile('run01'), old)

    def test_binding_projection_changes_only_identity_and_output_and_is_deep(self):
        for action in ('upload', 'capture'):
            original = json.loads((HERE / (action + '_bindings.json')).read_text())
            before = copy.deepcopy(original)
            result = self.subject.project_bindings(action, original, run_id=RUN02)
            self.assertEqual(result, projected(original))
            self.assertEqual(original, before)
            next(iter(result['files'].values()))['bytes'] = 1
            self.assertEqual(original, before)
            self.assertEqual(self.subject.project_bindings(action, original), original)

    def test_projection_rejects_wrong_action_run_and_original_identity(self):
        original = json.loads((HERE / 'upload_bindings.json').read_text())
        for action, run in (('erase', RUN02), ('upload', None), ('upload', 'run02'),
                             ('upload', 'static-fcddbd8e-run03')):
            with self.assertRaises(Exception):
                self.subject.project_bindings(action, original, run_id=run)
        for name, value in (('run_id', RUN02), ('source_sha256', 'a' * 64), ('output', '/tmp/other')):
            candidate = copy.deepcopy(original)
            candidate[name] = value
            with self.assertRaises(Exception):
                self.subject.project_bindings('upload', candidate, run_id=RUN02)

    def test_validators_and_orchestration_require_selected_report_identity(self):
        self.run02_reports()
        self.subject.check_upload(self.operations.upload, run_id=RUN02)
        self.subject.check_capture(self.operations.capture, run_id=RUN02)
        self.subject.report_identity(self.operations.upload, 'static-upload-result-v1', 'UPLOADED', run_id=RUN02)
        with self.assertRaises(Exception):
            self.subject.check_upload(self.operations.upload)
        with self.assertRaises(Exception):
            self.subject.check_capture(self.operations.capture)
        result = self.subject.orchestrate(self.operations.callbacks, run_id=RUN02)
        self.assertEqual(result['status'], 'COMPLETED')
        self.assertEqual((result['upload']['run_id'], result['capture']['run_id']), (RUN02, RUN02))

    def test_cross_run_upload_never_permits_capture(self):
        self.operations.capture['run_id'] = RUN02
        result = self.subject.orchestrate(self.operations.callbacks, run_id=RUN02)
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['capture_attempts'], 0)
        self.assertEqual(result['upload']['run_id'], RUN01)
        self.assertIsNone(result['capture'])

    def test_cross_run_capture_is_preserved_as_failed_collection(self):
        self.operations.upload['run_id'] = RUN02
        result = self.subject.orchestrate(self.operations.callbacks, run_id=RUN02)
        self.assertEqual(result['status'], 'FAILED')
        self.assertEqual(result['capture_attempts'], 1)
        self.assertEqual(result['capture']['run_id'], RUN01)

    def test_invalid_run_rejected_before_callbacks_or_native_constructor_io(self):
        for run in ('run03', '', None, 2, True):
            with self.assertRaises(Exception):
                self.subject.run_profile(run)
            with mock.patch.object(Path, 'read_bytes') as read_bytes:
                with mock.patch.object(Path, 'read_text') as read_text:
                    with mock.patch.object(Path, 'mkdir') as mkdir:
                        with self.assertRaises(Exception):
                            self.subject.NativeRun('a' * 40, run=run)
                        mkdir.assert_not_called()
                    read_text.assert_not_called()
                read_bytes.assert_not_called()
        with self.assertRaises(Exception):
            self.subject.orchestrate(self.operations.callbacks, run_id='static-fcddbd8e-run03')
        self.assertEqual(self.operations.events, [])

    def test_closed_cli_run02_selection_and_invalid_rejection(self):
        with mock.patch.object(self.subject, 'native_run', side_effect=RuntimeError('sentinel')) as native:
            try:
                self.subject.main(['--execute', '--reviewed-head', 'a' * 40, '--run', 'run02'])
            except RuntimeError:
                pass
        native.assert_called_once_with('a' * 40, run='run02')
        with mock.patch.object(self.subject, 'native_run') as native:
            try:
                self.subject.main(['--execute', '--reviewed-head', 'a' * 40, '--run', 'run03'])
            except (SystemExit, ValueError):
                pass
        native.assert_not_called()

    def bootstrap_payload(self, action, run_id):
        parser = b'def loader_image(raw):\n    return b"parser-sentinel"\n'
        parser += b' ' * (18880 - len(parser))
        helper = 'def logical_read(*args, **kwargs):\n    return ' + repr(parser) + '\n'
        support = ('import json\nBINDINGS = "unchanged"\n'
                   'def json_bytes(value):\n    return json.dumps(value).encode("utf-8")\n')
        sources = {'helper': helper, 'support': support}
        signature = ('def collect(helper, decoder, loader_image, *, bindings=None, run_id=None):\n'
                     '    assert BINDINGS == "unchanged"\n'
                     '    return {"entry":"collect", "run_id":run_id, "bindings":bindings, '
                     '"parser":loader_image(b"x").decode()}\n')
        if action == 'capture':
            sources.update(support=support + signature, decoder='MARKER = "decoder"\n')
        else:
            sources['upload'] = ('BINDINGS = "unchanged"\n'
                'def upload(helper, support, *, bindings=None):\n'
                '    assert BINDINGS == "unchanged"\n'
                '    return {"entry":"upload", "run_id":bindings["run_id"], "bindings":bindings}\n'
                'def upload_loader(helper, support, *, bindings=None, run_id=None):\n'
                '    assert BINDINGS == "unchanged"\n'
                '    return {"entry":"upload_loader", "run_id":run_id, "bindings":bindings}\n')
        bindings = json.loads((HERE / (action + '_bindings.json')).read_text())
        if run_id == RUN02:
            bindings = projected(bindings)
        payload = dict(sources=sources, hashes={key: hashlib.sha256(value.encode()).hexdigest()
                       for key, value in sources.items()}, bindings=json.dumps(bindings), run_id=run_id)
        if action == 'capture':
            payload.update(parser_path='/fixture/parser.py', parser_sha256=hashlib.sha256(parser).hexdigest())
        return json.dumps(payload).encode(), bindings

    def test_bootstrap_explicit_api_dispatch_and_no_binding_global_assignment(self):
        for action in ('upload', 'capture'):
            for run in (RUN01, RUN02):
                with self.subTest(action=action, run=run):
                    payload, bindings = self.bootstrap_payload(action, run)
                    command = self.subject.build_command(action, payload)
                    output = io.StringIO()
                    with mock.patch.object(sys, 'argv', ['-c', *command[5:]]):
                        with mock.patch.object(sys, 'stdout', output):
                            exec(compile(command[4], '<controlled-bootstrap>', 'exec'), {'__name__': '__main__'})
                    result = json.loads(output.getvalue())
                    expected = 'collect' if action == 'capture' else 'upload' if run == RUN01 else 'upload_loader'
                    self.assertEqual(result['entry'], expected)
                    self.assertEqual(result['run_id'], run)
                    self.assertEqual(result['bindings'], bindings)
                    if action == 'capture':
                        self.assertEqual(result['parser'], 'parser-sentinel')


def load_tests(loader, suite, pattern):
    result = unittest.TestSuite()
    for case in (UploadOwnership, CaptureOwnership, LauncherOwnership):
        for name in sorted(case.__dict__):
            if name.startswith('test_'):
                result.addTest(case(name))
    return result


if __name__ == '__main__':
    unittest.main(verbosity=2)
