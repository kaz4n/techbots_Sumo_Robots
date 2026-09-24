"""D134 contract-only private probes; freeze before new implementation/test reads."""
from pathlib import Path
import importlib.util
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('private_d134_board', ROOT / 'tools/board_tool.py')
BOARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOARD)
ARC = 'MODE_ARC_ENABLED'
WAIT = 'MODE_WAIT_ENABLED'


def decl(name, token):
    return 'inline constexpr std::uint32_t ' + name + ' = ' + token + ';\n'


def config(arc='1U', wait='1U', default='1U'):
    return '#include <cstdint>\nnamespace config {\n' + \
        decl('EDGE_PUSH_THROUGH_MS', '0U') + decl(ARC, arc) + \
        decl(WAIT, wait) + decl('MODE_DEFAULT', default) + '}\n'


class ModeLiteralContract(unittest.TestCase):
    def check_text(self, text, accepted):
        with tempfile.TemporaryDirectory(prefix='sumox_private_modes_') as temp:
            path = Path(temp) / 'config.h'
            data = text.encode('utf-8') if isinstance(text, str) else text
            path.write_bytes(data)
            if accepted:
                BOARD.validate_mode_availability_config(path)
            else:
                with self.assertRaises(ValueError) as caught:
                    BOARD.validate_mode_availability_config(path)
                self.assertTrue(str(caught.exception).strip())
            self.assertEqual(path.read_bytes(), data)

    def test_all_four_pairs_and_six_defaults_use_literal_availability(self):
        for arc in (0, 1):
            for wait in (0, 1):
                for mode in range(1, 7):
                    accepted = mode <= 3 or (mode in (4, 5) and arc == 1) or (mode == 6 and wait == 1)
                    for suffix in ('U', 'u'):
                        with self.subTest(arc=arc, wait=wait, mode=mode, suffix=suffix):
                            self.check_text(config(str(arc)+suffix, str(wait)+suffix, str(mode)+suffix), accepted)

    def test_boolean_and_default_spelling_and_raw_overflows_fail(self):
        for token in ('2U', '4294967296U', '4294967297U', '18446744073709551617U',
                      '-0U', '+1U', '01U', '0x1U', '1', '1UL', '(1U)', '1U+0U',
                      'true', 'FLAG', '9'*10000+'U'):
            with self.subTest(token=token[:30]):
                self.check_text(config(arc=token), False)
                self.check_text(config(wait=token), False)
        for token in ('0U', '7U', '256U', '4294967297U', '01U', '-1U', '1UL', '1U+0U'):
            self.check_text(config(default=token), False)

    def test_exactly_one_of_each_switch_and_default_is_required(self):
        text = config()
        for name in (ARC, WAIT, 'MODE_DEFAULT'):
            with self.subTest(name=name):
                self.check_text(text.replace(decl(name, '1U'), ''), False)
                self.check_text(text + decl(name, '1U'), False)
                self.check_text(text + 'auto alias = ' + name + ';\n', False)
                self.check_text(text.replace('std::uint32_t ' + name, 'unsigned ' + name), False)

    def test_both_absent_is_legacy_only_after_lexical_validation(self):
        legacy = '#include <cstdint>\n' + decl('EDGE_PUSH_THROUGH_MS', '0U')
        self.check_text(legacy, True)
        self.check_text('/* '+decl(ARC, '0U')+' */\n// '+decl(WAIT, '0U')+legacy, True)
        self.check_text('const char* s="'+ARC+' '+WAIT+'";\n'+legacy, True)
        for suffix in ('/*', '"unfinished', "'unfinished", '// splice\\\n',
                       '// splice\\ \r\n', '%:if 0\n%:endif\n'):
            with self.subTest(suffix=suffix):
                self.check_text(legacy+suffix, False)

    def test_conditional_or_macro_spelling_is_not_absent_legacy(self):
        for name in (ARC, WAIT, 'MODE_DEFAULT'):
            wrapped = config().replace(decl(name, '1U'), '#if 0\n'+decl(name, '1U')+'#endif\n')
            self.check_text(wrapped, False)
        self.check_text('#if 0\n'+decl(ARC, '1U')+'#endif\n', False)
        self.check_text('#define '+ARC+' 1U\n', False)
        self.check_text('%:if 0\n'+config()+'%:endif\n', False)
        self.check_text('#\fif 0\n'+config()+'#endif\n', False)

    def test_comments_quotes_and_raw_literals_neither_hide_nor_supply_switches(self):
        noisy = '// '+ARC+'\n/* '+WAIT+' */\nconst char* s="'+ARC+'";\n'
        noisy += 'const char* r=R"tag('+WAIT+')tag";\n'
        self.check_text(noisy+config('0U', '0U'), True)
        self.check_text(config().replace(' = ', ' /* why */ =\n'), True)
        self.check_text(config().replace(ARC, 'MODE_ARC_/**/ENABLED'), False)
        self.check_text(config()+'#undef '+WAIT+'\n', False)

    def test_malformed_source_and_unrelated_splices_fail_before_legacy_or_new(self):
        for text in (b'\xff', config()+'/*', config()+'"bad',
                     '#define OTHER \\\n1\n'+config(),
                     '// hidden\\\n'+config(), config().replace(' = ', ' = \\\r\n')):
            self.check_text(text, False)
        with tempfile.TemporaryDirectory(prefix='sumox_private_mode_missing_') as temp:
            with self.assertRaises(ValueError):
                BOARD.validate_mode_availability_config(Path(temp)/'missing.h')

    def test_actual_stage_validates_copied_bytes_without_root_substitution(self):
        with tempfile.TemporaryDirectory(prefix='sumox_private_mode_stage_') as temp:
            root = Path(temp)
            for part in ('src/core', 'src/hal', 'src/app'):
                (root/part).mkdir(parents=True, exist_ok=True)
            (root/'src/app/app.ino').write_text('void setup(){} void loop(){}\n')
            (root/'src/config.h').write_text(config('0U', '0U', '3U'))
            with patch.object(BOARD, 'ROOT', root):
                output = BOARD.stage('app')
                self.assertEqual((output/'src/config.h').read_bytes(), (root/'src/config.h').read_bytes())
                copy = BOARD.shutil.copy2

                def corrupt(source, destination, *args, **kwargs):
                    if Path(source) == root/'src/config.h':
                        Path(destination).write_text(config('0U', '0U', '4U'))
                        return str(destination)
                    return copy(source, destination, *args, **kwargs)

                with patch.object(BOARD.shutil, 'copy2', side_effect=corrupt):
                    with self.assertRaises(ValueError):
                        BOARD.stage('app')


if __name__ == '__main__':
    unittest.main(verbosity=2)
