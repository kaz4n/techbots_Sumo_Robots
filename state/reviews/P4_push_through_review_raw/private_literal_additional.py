"""Source-review-driven D132 physical-splice and directive-token probes."""
from pathlib import Path
import runpy
import tempfile
import unittest

BASE = runpy.run_path(str(Path(__file__).with_name('private_literal_probes.py')))
BOARD = BASE['BOARD']
DECL = BASE['declaration']


class LiteralLexicalSupplement(unittest.TestCase):
    def rejects(self, text):
        with tempfile.TemporaryDirectory(prefix='sumox_literal_extra_') as temp:
            path = Path(temp) / 'config.h'
            path.write_bytes(text.encode())
            with self.assertRaisesRegex(ValueError, 'EDGE_PUSH_THROUGH_MS'):
                BOARD.validate_push_through_config(path)

    def test_comment_splicing_precedes_comment_removal(self):
        for padding in ('', ' ', '\t', '\v', '\f'):
            for newline in ('\n', '\r\n'):
                with self.subTest(padding=repr(padding), newline=repr(newline)):
                    self.rejects('// continue\\' + padding + newline + DECL('20U'))

    def test_digraph_cannot_hide_conditional_declaration(self):
        for condition in ('0', '1'):
            self.rejects('%:if ' + condition + '\nnamespace config {\n' +
                         DECL('20U') + '}\n%:endif\n')

    def test_formfeed_is_whitespace_not_a_physical_line(self):
        self.rejects('#\fif 0\nnamespace config {\n' + DECL('20U') + '}\n#endif\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
