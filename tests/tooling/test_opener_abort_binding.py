# Checks D136 bounded local reads and binding to the unchanged validator's accepted bytes.
# Prevents raced snapshots or hidden external actions from becoming accepted evidence.
# Deferred public API tests mutate only temporary synthetic fixture files.
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import builtins
import copy
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from types import SimpleNamespace
from unittest import mock
from opener_abort_fixture import AbortAnalysisCase, BoundedReader, Bundle, ENDPOINTS, ROOT, TOOL, load_analyzer, wire


class OpenerAbortBindingTests(AbortAnalysisCase):
    def assert_untrusted(self, report):
        attempt = report['attempts'][0]
        self.assertEqual((attempt['qualification'], attempt['trace_status']), ('INVALID', 'INVALID'))
        self.assertEqual((attempt['logical_status'], attempt['timing_status']), ('NOT_EVALUATED', 'NOT_EVALUATED'))
        for key in ENDPOINTS:
            self.assertIsNone(attempt[key])

    def test_D136_same_size_restored_mtime_rewrites_fail_hash_binding_on_each_reread(self):
        for role in ('events', 'summary'):
            bundle = Bundle(self.directory, self.source)
            self.write_cohort([bundle])
            path = bundle.paths[role]
            old, identity = path.read_bytes(), path.stat()

            def mutate(_):
                if role == 'events':
                    events = copy.deepcopy(bundle.events)
                    events[-1]['t_us'] += 1
                    data = wire.header('events') + b''.join(wire.event(**event) for event in events)
                else:
                    values = dict(bundle.summary, epoch_token=2, frame_count=0, event_count=len(bundle.events))
                    data = wire.header('summary') + wire.summary(**values)
                self.assertNotEqual(data, old)
                self.assertEqual(len(data), len(old))
                path.write_bytes(data)
                os.utime(path, ns=(identity.st_atime_ns, identity.st_mtime_ns))
                self.assertEqual((path.stat().st_size, path.stat().st_mtime_ns), (identity.st_size, identity.st_mtime_ns))

            self.assert_untrusted(self.validated_then(mutate))

    def test_D136_accepted_hash_bytes_and_row_counts_all_bind_events_and_summary(self):
        for role in ('events', 'summary'):
            for field in ('sha256', 'bytes', 'rows'):
                bundle = Bundle(self.directory, self.source)
                self.write_cohort([bundle])

                def alter(accepted):
                    accepted['files'][role][field] = '0' * 64 if field == 'sha256' else accepted['files'][role][field] + 1

                self.assert_untrusted(self.validated_then(alter))

    def test_D136_accepted_manifest_and_frames_are_not_reopened_after_validation(self):
        bundle = Bundle(self.directory, self.source)
        self.write_cohort([bundle])

        def remove(_):
            bundle.manifest_path.unlink()
            bundle.paths['frames'].unlink()

        report = self.validated_then(remove)
        self.assertEqual(report['attempts'][0]['qualification'], 'QUALIFIED')
        self.assertEqual(report['attempts'][0]['elapsed_us'], 1000)
        self.assertEqual(report['attempts'][0]['validation']['provenance']['closure'], 'DECLARED_CLOSED')

    def test_D136_each_bound_reread_rejects_symlink_substitution_even_with_identical_bytes(self):
        for role in ('events', 'summary'):
            bundle = Bundle(self.directory, self.source)
            self.write_cohort([bundle])
            path = bundle.paths[role]
            target = self.directory / (role + '-copy.csv')
            target.write_bytes(path.read_bytes())

            def substitute(_):
                path.unlink()
                path.symlink_to(target)

            self.assert_untrusted(self.validated_then(substitute))
            path.unlink()

    def test_D136_each_reread_descriptor_rejects_nonregular_or_changed_identity(self):
        original = os.fstat
        for role in ('events', 'summary'):
            for changed in ('st_mode', 'st_size', 'st_mtime_ns', 'st_dev', 'st_ino'):
                bundle = Bundle(self.directory, self.source)
                self.write_cohort([bundle])
                identity, armed, calls = bundle.paths[role].stat(), [False], []

                def arm(_):
                    armed[0] = True

                def altered(fd):
                    actual = original(fd)
                    if not armed[0] or (actual.st_dev, actual.st_ino) != (identity.st_dev, identity.st_ino):
                        return actual
                    calls.append(fd)
                    if changed != 'st_mode' and len(calls) == 1:
                        return actual
                    values = {name: getattr(actual, name) for name in dir(actual) if name.startswith('st_')}
                    values[changed] = stat.S_IFIFO | 0o600 if changed == 'st_mode' else values[changed] + 1
                    return SimpleNamespace(**values)

                with mock.patch('os.fstat', altered):
                    self.assert_untrusted(self.validated_then(arm))
                self.assertGreaterEqual(len(calls), 1 if changed == 'st_mode' else 2)

    def test_D136_cohort_and_config_descriptors_are_bound_before_and_after_read(self):
        original = os.fstat
        for role in ('cohort', 'config'):
            for changed in ('st_mode', 'st_size', 'st_mtime_ns', 'st_dev', 'st_ino'):
                self.write_cohort([])
                identity = (self.path if role == 'cohort' else self.source.path).stat()
                calls = []

                def altered(fd):
                    actual = original(fd)
                    if (actual.st_dev, actual.st_ino) != (identity.st_dev, identity.st_ino):
                        return actual
                    calls.append(fd)
                    if changed != 'st_mode' and len(calls) == 1:
                        return actual
                    values = {name: getattr(actual, name) for name in dir(actual) if name.startswith('st_')}
                    values[changed] = stat.S_IFIFO | 0o600 if changed == 'st_mode' else values[changed] + 1
                    return SimpleNamespace(**values)

                with mock.patch('os.fstat', altered):
                    if role == 'cohort':
                        self.invalid_input()
                    else:
                        report = self.analyze()
                        self.assertEqual((report['input_status'], report['evidence_status']), ('VALID', 'INVALID'))
                        self.assertEqual(report['source']['binding_status'], 'INVALID')
                        self.assertIsNone(report['source']['config_values'])
                self.assertGreaterEqual(len(calls), 1 if changed == 'st_mode' else 2)

    def test_D136_nonregular_missing_and_oversized_CSV_members_fail_without_decoding(self):
        for role in ('frames', 'events', 'summary'):
            for kind in ('missing', 'directory', 'symlink', 'oversized'):
                bundle = Bundle(self.directory, self.source)
                path = bundle.paths[role]
                raw = path.read_bytes()
                path.unlink()
                if kind == 'directory':
                    path.mkdir()
                elif kind == 'symlink':
                    target = self.directory / (role + '-target.csv')
                    target.write_bytes(raw)
                    path.symlink_to(target)
                elif kind == 'oversized':
                    with path.open('wb') as stream:
                        stream.truncate(16 * 1024 * 1024 + 1)
                self.invalid_attempt(bundle)
                if kind == 'directory':
                    path.rmdir()
                elif path.exists() or path.is_symlink():
                    path.unlink()

    def test_D136_invalid_supplied_manifest_is_never_accepted_as_missing(self):
        for kind in ('missing', 'oversized', 'duplicate', 'symlink', 'null_closure', 'missing_closure'):
            bundle = Bundle(self.directory, self.source)
            path = bundle.manifest_path
            if kind == 'missing':
                path.unlink()
            elif kind == 'oversized':
                path.write_bytes(b' ' * (16384 + 1))
            elif kind == 'duplicate':
                path.write_bytes(b'{"schema_version":1,"schema_version":1}')
            elif kind in ('null_closure', 'missing_closure'):
                manifest = bundle.manifest()
                if kind == 'null_closure':
                    manifest['closure'] = None
                else:
                    del manifest['closure']
                path.write_text(json.dumps(manifest), encoding='ascii')
            else:
                target = self.directory / 'manifest-target.json'
                target.write_bytes(path.read_bytes())
                path.unlink()
                path.symlink_to(target)
            self.invalid_attempt(bundle)
            if path.exists() or path.is_symlink():
                path.unlink()

    def test_D136_all_input_reads_are_bounded_config_is_read_once_and_bytes_remain_unchanged(self):
        bundle = Bundle(self.directory, self.source)
        self.write_cohort([bundle])
        before = {path: path.read_bytes() for path in self.directory.iterdir()}
        paths = {path.resolve() for path in before}
        identities = {(path.stat().st_dev, path.stat().st_ino): path for path in paths}
        observed, config_streams = [], []

        def intercept(original):
            def opening(file, *args, **kwargs):
                stream = original(file, *args, **kwargs)
                if isinstance(stream, wire.CheckedReader):
                    return stream
                path = None
                if isinstance(file, (str, bytes, os.PathLike)):
                    path = Path(os.fsdecode(file)).resolve()
                elif isinstance(file, int):
                    info = os.fstat(file)
                    path = identities.get((info.st_dev, info.st_ino))
                if path in paths:
                    self.assertIn('b', stream.mode)
                    limit = 16384 if path == bundle.manifest_path else 16 * 1024 * 1024
                    if path in (self.path, self.source.path):
                        limit = 256 * 1024
                    if path == self.source.path:
                        config_streams.append(stream.fileno())
                    return BoundedReader(stream, observed, limit)
                return stream
            return opening

        with ExitStack() as stack:
            for module, name in ((builtins, 'open'), (io, 'open'), (os, 'fdopen')):
                stack.enter_context(mock.patch.object(module, name, intercept(getattr(module, name))))
            report = self.analyze()
        self.assertEqual(report['attempts'][0]['qualification'], 'QUALIFIED')
        self.assertTrue(observed)
        self.assertEqual(len(config_streams), 1, 'Historical config bytes are read once and retained')
        self.assertEqual(before, {path: path.read_bytes() for path in self.directory.iterdir()})

    def test_D136_import_API_and_cue_helper_are_quiet_read_only_and_never_use_external_actions(self):
        bundle = Bundle(self.directory, self.source)
        self.write_cohort([bundle])
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            module = load_analyzer()
            report = module.analyze_cohort(self.path)
        self.assertEqual((stdout.getvalue(), stderr.getvalue()), ('', ''))
        self.assertEqual(report['attempts'][0]['qualification'], 'QUALIFIED')
        guard = r'''
import importlib.util, os, sys
sys.dont_write_bytecode = True
tool, cohort, live_config = sys.argv[1:]
sys.path.insert(0, os.path.dirname(tool))
def audit(event, args):
    if event == 'open':
        name, mode, flags = args
        if (isinstance(mode, str) and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            raise AssertionError('Analyzer attempted a write')
        if isinstance(name, str) and (os.path.abspath(name) == live_config or name.endswith('board_tool.py')):
            raise AssertionError('Analyzer attempted live configuration or board access')
    if event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.posix_spawn'):
        raise AssertionError('Analyzer attempted an external action')
sys.addaudithook(audit)
spec = importlib.util.spec_from_file_location('d136_guarded', tool)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
assert module.analyze_cohort(cohort)['attempts'][0]['qualification'] == 'QUALIFIED'
def no_files(event, args):
    if event == 'open':
        raise AssertionError('Pure cue decoder attempted file access')
sys.addaudithook(no_files)
assert module.decode_cue(579, 3)['effective_mask'] == 2
'''
        result = subprocess.run([sys.executable, '-B', '-c', guard, str(TOOL), str(self.path), str(ROOT / 'src/config.h')],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((result.stdout, result.stderr), ('', ''))
