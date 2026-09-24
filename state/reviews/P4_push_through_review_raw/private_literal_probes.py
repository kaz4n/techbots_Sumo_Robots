"""Independent D132 contract probes frozen before the linked implementation read."""
from pathlib import Path
import importlib.util
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('private_d132_board_tool', ROOT / 'tools/board_tool.py')
BOARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOARD)
NAME = 'EDGE_PUSH_THROUGH_MS'


def declaration(value='0U'):
    return '#include <cstdint>\ninline constexpr std::uint32_t ' + NAME + ' = ' + value + ';\n'


class PrivateLiteralReview(unittest.TestCase):
    def check_text(self, text, accepted):
        with tempfile.TemporaryDirectory(prefix='sumox_private_literal_') as temp:
            path = Path(temp) / 'config.h'
            data = text.encode('utf-8') if isinstance(text, str) else text
            path.write_bytes(data)
            if accepted:
                BOARD.validate_push_through_config(path)
            else:
                with self.assertRaisesRegex(ValueError, NAME):
                    BOARD.validate_push_through_config(path)
            self.assertEqual(path.read_bytes(), data)

    def test_every_bounded_decimal_is_admitted_without_byte_changes(self):
        for value in range(101):
            for suffix in ('U', 'u'):
                with self.subTest(value=value, suffix=suffix):
                    self.check_text(declaration(str(value) + suffix), True)

    def test_large_and_noncanonical_spellings_fail_identified(self):
        for value in ('101U', '4294967295U', '4294967296U', '4294967316U',
                      '20UL', '20ULL', '-0U', '+20U', '020U', '00U', '0x14U',
                      '20', '(20U)', '20U+0U', "2'0U", '9' * 10000 + 'U'):
            with self.subTest(value=value[:35]):
                self.check_text(declaration(value), False)

    def test_comments_and_quoted_decoys_do_not_supply_or_duplicate_declaration(self):
        decoy = declaration('4294967316U').split('\n')[1]
        self.check_text('// ' + decoy + '\n/*' + decoy + '*/\n' + declaration('20U'), True)
        self.check_text('const char* text = "' + decoy + '";\n' + declaration('100U'), True)
        self.check_text('const char* text = "' + decoy + '";\n', False)
        self.check_text('/* ' + declaration('20U') + ' */', False)

    def test_comments_separate_tokens_without_manufacturing_identifier(self):
        self.check_text(declaration('20U').replace(' = ', ' /* why */ =\n'), True)
        self.check_text(declaration('20U').replace(NAME, 'EDGE_PUSH_THROUGH_/**/MS'), False)

    def test_one_identifier_means_no_other_active_reference_or_definition(self):
        for suffix in (declaration('0U'), 'auto alias = ' + NAME + ';\n',
                       '#define ' + NAME + ' 0U\n', '#undef ' + NAME + '\n'):
            with self.subTest(suffix=suffix):
                self.check_text(declaration('20U') + suffix, False)

    def test_conditional_depth_is_local_but_definition_is_never_conditional(self):
        self.check_text('#if OTHER\nconstexpr int elsewhere=1;\n#endif\n' + declaration('20U'), True)
        for conditional in ('#if 0', '#if 1', '#ifdef OTHER', '#ifndef OTHER'):
            self.check_text(conditional + '\n' + declaration('20U') + '#endif\n', False)
        self.check_text('const char* s="#if OTHER";\n' + declaration('20U'), True)

    def test_malformed_lexemes_and_continuations_fail_identified(self):
        for text in (declaration('20U') + '/*', declaration('20U') + '"bad',
                     declaration('20U') + "'bad", declaration('20U').replace('= ', '= \\\n'),
                     '#define OTHER \\\n1\n' + declaration('20U'), b'\xff' + declaration().encode()):
            with self.subTest(text=str(text)[:50]):
                self.check_text(text, False)

    def test_missing_file_is_identified(self):
        with tempfile.TemporaryDirectory(prefix='sumox_private_literal_') as temp:
            with self.assertRaisesRegex(ValueError, NAME):
                BOARD.validate_push_through_config(Path(temp) / 'absent.h')

    def make_stage(self, root):
        for part in ('src/core', 'src/hal', 'src/app'):
            (root / part).mkdir(parents=True, exist_ok=True)
        (root / 'src/app/app.ino').write_text('void setup(){} void loop(){}\n')
        (root / 'src/config.h').write_text(declaration('20U'))

    def test_actual_stage_keeps_exact_bytes_and_checks_copied_destination(self):
        with tempfile.TemporaryDirectory(prefix='sumox_private_stage_') as temp:
            root = Path(temp); self.make_stage(root)
            with patch.object(BOARD, 'ROOT', root):
                result = BOARD.stage('app')
                self.assertEqual((result / 'src/config.h').read_bytes(),
                                 (root / 'src/config.h').read_bytes())
                original_copy = BOARD.shutil.copy2

                def corrupt(source, destination, *args, **kwargs):
                    if Path(source) == root / 'src/config.h':
                        Path(destination).write_text(declaration('4294967316U'))
                        return str(destination)
                    return original_copy(source, destination, *args, **kwargs)

                with patch.object(BOARD.shutil, 'copy2', side_effect=corrupt):
                    with self.assertRaisesRegex(ValueError, NAME):
                        BOARD.stage('app')


if __name__ == '__main__':
    unittest.main(verbosity=2)
