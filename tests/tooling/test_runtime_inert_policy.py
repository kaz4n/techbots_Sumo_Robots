# Exercises D104's exact native probe build selection and side-effect boundary.
# Uses saved compiler fixtures and controlled calls without a board or upload.
# Coordinator-authored tests are separately inspected by the fresh reviewer.
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import copy
import importlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
policy = importlib.import_module('app_build_policy')
board = importlib.import_module('board_tool')
FQBN = 'arduino:zephyr:unoq'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
BUILD = '/fixture/native-app-v1/source/default/run-one/build'
FIXTURE = ROOT / 'tests/fixtures/app_build_policy/valid_result.json'


def document(probe=True):
    text = FIXTURE.read_text(encoding='utf-8')
    return json.loads(text.replace('app.ino', 'runtime_inert.ino') if probe else text)


class RuntimePolicyTests(unittest.TestCase):
    def validate(self, doc, project='runtime_inert.ino', fqbn=FQBN, flags=FLAGS):
        return policy.validate_result(json.dumps(doc), fqbn, flags, BUILD, project=project)

    def test_exact_selected_project_and_old_default_validate(self):
        self.assertEqual('runtime_inert.ino', self.validate(document())['build.project_name'])
        old = policy.validate_result(json.dumps(document(False)), FQBN, FLAGS, BUILD)
        self.assertEqual('app.ino', old['build.project_name'])
        for doc, project in ((document(), 'app.ino'), (document(False), 'runtime_inert.ino')):
            with self.subTest(project=project), self.assertRaises(ValueError):
                self.validate(doc, project)

    def test_every_mixed_project_reference_is_rejected(self):
        original = document()
        entries = original['builder_result']['build_properties']
        changed = 0
        for index, value in enumerate(entries):
            if 'runtime_inert.ino' not in value:
                continue
            changed += 1
            bad = copy.deepcopy(original)
            bad['builder_result']['build_properties'][index] = value.replace('runtime_inert.ino', 'app.ino')
            with self.subTest(property=value.split('=', 1)[0]), self.assertRaises(ValueError):
                self.validate(bad)
        self.assertGreaterEqual(changed, 6)

    def test_unknown_names_active_flags_and_immediate_are_rejected(self):
        names = ('', 'runtime_inert', '../runtime_inert.ino', 'other.ino',
                 'runtime_inert.ino;true', 'runtime_inert.ino\n', None, 0, [])
        for name in names:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.validate(document(), name)
        for fqbn, flags in ((FQBN + ':wait_linux_boot=no', FLAGS),
                            (FQBN, '-DMATCH=1 -DMOTORS_ALLOWED=1'),
                            (FQBN, '-DMATCH=0 -DMOTORS_ALLOWED=1')):
            with self.subTest(fqbn=fqbn, flags=flags), self.assertRaises(ValueError):
                self.validate(document(), fqbn=fqbn, flags=flags)

    def test_probe_rejects_libraries_and_effective_command_drift(self):
        bad = document()
        bad['builder_result']['used_libraries'] = [{'name': 'Unexpected'}]
        with self.assertRaises(ValueError): self.validate(bad)
        for name in ('compiler.cpp.cmd', 'recipe.c.combine.pattern'):
            bad = document()
            props = bad['builder_result']['build_properties']
            matches = [i for i, p in enumerate(props) if p.startswith(name + '=')]
            self.assertEqual(1, len(matches))
            props[matches[0]] += ' unreviewed'
            with self.subTest(name=name), self.assertRaises(ValueError): self.validate(bad)

    def test_probe_artifact_hashes_bind_the_selected_filename(self):
        props = self.validate(document())
        installed = policy.installed_pins('/home/arduino/.arduino15')
        expected_artifacts = [BUILD + '/runtime_inert.ino' + s for s in
                              ('.elf', '_debug.elf', '_temp.elf')]
        expected_artifacts += ['/fixture/output/runtime_inert.ino.elf-zsk.bin']
        calls = []
        def remote(target, args, capture):
            calls.append((target, args, capture))
            lines = [installed.get(p, '1' * 64) + '  ' + p for p in args[2:]]
            return SimpleNamespace(stdout='\n'.join(lines) + '\n')
        result = policy.verify_files(remote, 'board', props, BUILD, '/fixture/output')
        self.assertEqual(expected_artifacts, calls[0][1][-4:])
        self.assertTrue(all(p in result for p in expected_artifacts))
        self.assertFalse(any('/app.ino' in p for p in result))


class RuntimeFlashBoundaryTests(unittest.TestCase):
    def test_upload_binds_checked_output_and_both_reviewed_artifact_hashes(self):
        import runtime_capture
        folder = '/verified/run/artifacts'
        paths = [folder + '/runtime_inert.ino.elf', folder + '/runtime_inert.ino.elf-zsk.bin']
        hashes = [runtime_capture.ELF_HASH, runtime_capture.BINARY_HASH]
        for bad in (None, 0, 1):
            actual = list(hashes)
            if bad is not None: actual[bad] = '0' * 64
            output = ''.join(h + '  ' + p + '\n' for h, p in zip(actual, paths))
            with mock.patch.object(board, 'remote', return_value=SimpleNamespace(stdout=output)) as remote:
                if bad is None:
                    board.verify_runtime_artifacts('board', folder)
                else:
                    with self.assertRaises(ValueError): board.verify_runtime_artifacts('board', folder)
                remote.assert_called_once_with('board', ['sha256sum', '--', *paths], capture=True)
        for bad in ('/old/generic', '/verified/run/artifacts/other'):
            with mock.patch.object(board, 'remote') as remote, self.assertRaises(ValueError):
                board.verify_runtime_artifacts('board', bad)
            remote.assert_not_called()
        with mock.patch.object(runtime_capture, 'ELF_HASH', None), mock.patch.object(board, 'remote') as remote:
            with self.assertRaises(ValueError): board.verify_runtime_artifacts('board', folder)
            remote.assert_not_called()

    def test_only_verified_source_and_reproduced_checked_bytes_reach_upload(self):
        args = SimpleNamespace(sketch='bench/runtime_inert', match=False, startup=None, compile_only=False)
        with ExitStack() as stack:
            for name, value in (('target', 'board'), ('setting', '/fixture/root'),
                                ('stage', Path('/fixture/runtime_inert')), ('source_hash', 'a' * 64)):
                stack.enter_context(mock.patch.object(board, name, return_value=value))
            for name in ('require_transport', 'verify_core', 'sync_sources'):
                stack.enter_context(mock.patch.object(board, name))
            source = stack.enter_context(mock.patch.object(board, 'verify_inert_source'))
            artifacts = stack.enter_context(mock.patch.object(board, 'verify_runtime_artifacts'))
            remote = stack.enter_context(mock.patch.object(board, 'remote'))
            compile_probe = stack.enter_context(mock.patch.object(board, 'compile_app',
                                                   return_value='/verified/unique/artifacts'))
            with redirect_stdout(io.StringIO()): board.flash(args)
            source.assert_called_once_with('bench/runtime_inert', 'a' * 64)
            artifacts.assert_called_once_with('board', '/verified/unique/artifacts')
            self.assertEqual(mock.call('board', ['arduino-cli', 'upload', '--fqbn', FQBN,
                '--input-dir', '/verified/unique/artifacts',
                '/fixture/root/' + 'a' * 64 + '/runtime_inert']), remote.call_args_list[-1])
            for guard in (source, compile_probe, artifacts):
                remote.reset_mock()
                guard.side_effect = ValueError('controlled refusal')
                with redirect_stdout(io.StringIO()), self.assertRaisesRegex(ValueError, 'controlled refusal'):
                    board.flash(args)
                self.assertFalse(any('upload' in call.args[1] for call in remote.call_args_list))
                guard.side_effect = None

    def test_bad_probe_modes_fail_before_transport(self):
        for compile_only in (False, True):
            for match, startup in ((True, None), (True, 'immediate'), (True, 'default'),
                                   (False, 'immediate')):
                args = SimpleNamespace(sketch='bench/runtime_inert', match=match,
                                       startup=startup, compile_only=compile_only)
                with self.subTest(args=args), mock.patch.object(board, 'target') as target:
                    with redirect_stderr(io.StringIO()), self.assertRaises(ValueError):
                        board.flash(args)
                    target.assert_not_called()

    def test_probe_profile_refuses_before_transport(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            folder = root / 'bench/runtime_inert'
            folder.mkdir(parents=True)
            for name in ('sketch.yaml', 'sketch.yml'):
                p = folder / name; p.write_text('profile: unreviewed')
                args = SimpleNamespace(sketch='bench/runtime_inert', match=False,
                                       startup=None, compile_only=True)
                with mock.patch.object(board, 'ROOT', root), mock.patch.object(board, 'target') as target:
                    with redirect_stderr(io.StringIO()), self.assertRaises(ValueError): board.flash(args)
                    target.assert_not_called()
                p.unlink()

    def test_compile_only_uses_checked_literal_project_and_never_uploads(self):
        args = SimpleNamespace(sketch='bench/runtime_inert', match=False,
                               startup=None, compile_only=True)
        with ExitStack() as stack:
            for name, value in (('target', 'board'), ('setting', '/fixture/root'),
                                ('stage', Path('/fixture/runtime_inert')), ('source_hash', 'a' * 64)):
                stack.enter_context(mock.patch.object(board, name, return_value=value))
            for name in ('require_transport', 'verify_core', 'sync_sources'):
                stack.enter_context(mock.patch.object(board, name))
            remote = stack.enter_context(mock.patch.object(board, 'remote'))
            checked = stack.enter_context(mock.patch.object(board, 'compile_app',
                                            return_value='/verified/unique/artifacts'))
            with redirect_stdout(io.StringIO()): board.flash(args)
            checked.assert_called_once_with('board', 'a' * 64,
                '/fixture/root/' + 'a' * 64 + '/runtime_inert', '/fixture/root',
                FQBN, FLAGS, 'default', project='runtime_inert.ino')
            self.assertEqual([mock.call('board', ['mkdir', '-p',
                '/fixture/root/' + 'a' * 64 + '/runtime_inert'])], remote.call_args_list)
            checked.side_effect = RuntimeError('controlled compile failure')
            with redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError, 'compile failure'):
                board.flash(args)
            self.assertFalse(any('upload' in call.args[1] for call in remote.call_args_list))


if __name__ == '__main__':
    unittest.main()
