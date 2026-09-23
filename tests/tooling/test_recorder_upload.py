"""Check D091 upload boundaries with controlled commands, never real hardware."""
from argparse import Namespace
from contextlib import ExitStack
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
import board_tool as board


class RecorderUploadTests(unittest.TestCase):
    def setUp(self):
        self.scope = ExitStack()
        self.addCleanup(self.scope.close)
        self.root = Path(self.scope.enter_context(tempfile.TemporaryDirectory()))
        (self.root / 'tools').mkdir()
        self.manifest = self.root / 'tools/p0_inert_sources.json'
        self.manifest.write_text(json.dumps({'bench/recorder_inert': 'a' * 64}))
        self.commands = []
        replacements = dict(ROOT=self.root, target=lambda: 'controlled-board',
                            setting=lambda *args: '/controlled-build',
                            require_transport=lambda **kwargs: None,
                            stage=lambda _: self.root / 'recorder_inert',
                            source_hash=lambda _: 'a' * 64,
                            verify_core=lambda _: None,
                            sync_sources=lambda *args: None,
                            remote=lambda target, argv: self.commands.append(argv))
        for name, value in replacements.items():
            self.scope.enter_context(patch.object(board, name, value))

    def run_flash(self, compile_only=False, match=False, startup=None):
        board.flash(Namespace(sketch='bench/recorder_inert', compile_only=compile_only,
                              match=match, startup=startup))

    def test_only_reviewed_default_inert_source_can_upload(self):
        self.run_flash()
        self.assertEqual([c[:2] for c in self.commands],
                         [['mkdir', '-p'], ['arduino-cli', 'compile'], ['arduino-cli', 'upload']])
        self.assertIn('compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0', self.commands[1])
        self.assertIn('/controlled-build/' + 'a' * 64 + '/recorder_inert/artifacts/bench-default',
                      self.commands[2])

    def test_missing_or_changed_source_snapshot_fails_before_board_commands(self):
        for manifest in ({}, {'bench/recorder_inert': 'b' * 64}):
            with self.subTest(manifest=manifest):
                self.manifest.write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    self.run_flash()
                self.assertEqual(self.commands, [])

    def test_match_and_immediate_uploads_fail_before_transport(self):
        with patch.object(board, 'target', side_effect=AssertionError('transport reached')):
            for match, startup in [(True, None), (True, 'immediate'), (True, 'default'),
                                   (False, 'immediate')]:
                with self.subTest(match=match, startup=startup), self.assertRaises(ValueError):
                    self.run_flash(match=match, startup=startup)
        self.assertEqual(self.commands, [])

    def test_compile_only_never_uploads_even_for_match_or_unapproved_source(self):
        self.manifest.write_text('{}')
        for match, startup in [(False, None), (False, 'default'), (False, 'immediate'),
                               (True, None), (True, 'immediate')]:
            with self.subTest(match=match, startup=startup):
                self.commands.clear()
                self.run_flash(compile_only=True, match=match, startup=startup)
                self.assertEqual([c[:2] for c in self.commands],
                                 [['mkdir', '-p'], ['arduino-cli', 'compile']])

    def test_compile_failure_cannot_reach_upload(self):
        def fail_compile(target, command):
            self.commands.append(command)
            if command[:2] == ['arduino-cli', 'compile']:
                raise RuntimeError('controlled compile failure')
        with patch.object(board, 'remote', fail_compile), self.assertRaises(RuntimeError):
            self.run_flash()
        self.assertFalse(any(c[:2] == ['arduino-cli', 'upload'] for c in self.commands))


if __name__ == '__main__':
    unittest.main()
