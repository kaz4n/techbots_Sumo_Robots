# Tests D132 raw-literal admission from its adopted source and staging contract.
# Keeps malformed push durations away from every mocked board-operation boundary.
# Independent temporary-root tests invoke opaque helper, actual stage and flash APIs.
from contextlib import ExitStack, contextmanager, redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from . import test_opp_view_policy as fixture

board = fixture.board
IDENTIFIER = 'EDGE_PUSH_THROUGH_MS'
DECLARATION = 'inline constexpr std::uint32_t EDGE_PUSH_THROUGH_MS = {}U;'
CONFIG = '#pragma once\n#include <cstdint>\nnamespace config {{\n{}\n}}\n'
SKETCHES = ('app', 'bench/p0_matrix', 'bench/reactive_test')


def config(value='0'):
    return CONFIG.format(DECLARATION.format(value))


class PushLiteralTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='d132-literal-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / 'config.h'

    def write(self, text):
        data = text.encode('utf-8') if isinstance(text, str) else text
        self.path.write_bytes(data)
        return data

    def accepts(self, text):
        original = self.write(text)
        board.validate_push_through_config(self.path)
        self.assertEqual(self.path.read_bytes(), original)

    def rejects(self, text):
        original = self.write(text)
        with self.assertRaisesRegex(ValueError, IDENTIFIER):
            board.validate_push_through_config(self.path)
        self.assertEqual(self.path.read_bytes(), original)

    def test_all_101_canonical_values_are_accepted_without_rewriting(self):
        for value in range(101):
            with self.subTest(value=value):
                self.accepts(config(str(value)))

    def test_lowercase_suffix_and_cpp_whitespace_are_supported(self):
        for declaration in (
            'inline\tconstexpr\nstd::uint32_t\r\nEDGE_PUSH_THROUGH_MS\t=\n20u\t;',
            'inline constexpr std::uint32_t EDGE_PUSH_THROUGH_MS=0U;',
            'inline  constexpr  std::uint32_t  EDGE_PUSH_THROUGH_MS = 100u ;',
        ):
            with self.subTest(declaration=declaration):
                self.accepts(CONFIG.format(declaration))

    def test_ordinary_comments_can_separate_tokens_or_contain_decoy_identifiers(self):
        declaration = ('inline /* comment */ constexpr std::uint32_t\n'
                       'EDGE_PUSH_THROUGH_MS /* = 999U */ = 20U;')
        self.accepts('// EDGE_PUSH_THROUGH_MS = 4294967316U;\n' +
                     CONFIG.format(declaration) +
                     '/* EDGE_PUSH_THROUGH_MS\nEDGE_PUSH_THROUGH_MS = 101U; */\n')
        self.accepts(CONFIG.format(DECLARATION.format('100')) + '// final no-newline comment')

    def test_comment_delimiters_inside_comments_do_not_create_active_declarations(self):
        self.accepts('/* // EDGE_PUSH_THROUGH_MS = 101U; */\n' + config('20'))
        self.accepts('// /* EDGE_PUSH_THROUGH_MS = 101U;\n' + config('0'))

    def test_unrelated_preprocessor_blocks_do_not_invalidate_unconditional_declaration(self):
        self.accepts('#ifndef MATCH\n#define MATCH 0\n#endif\n' + config('20') +
                     '#if MATCH\nconstexpr int ordinary = 1;\n#else\n'
                     'constexpr int ordinary = 0;\n#endif\n')

    def test_out_of_range_and_truncation_alias_values_are_rejected(self):
        for value in ('101', '4294967295', '4294967296', '4294967316',
                      '18446744073709551616', '999999999999999999999'):
            with self.subTest(value=value):
                self.rejects(config(value))

    def test_excessively_long_digits_are_identified_errors_not_parser_exceptions(self):
        for value in ('9' * 10000, '0' * 10000, '1' + '0' * 100000):
            with self.subTest(length=len(value), first=value[0]):
                self.rejects(config(value))

    def test_noncanonical_decimal_and_nonascii_digits_are_rejected(self):
        for value in ('00', '020', '0100', '+20', '-0', '-1', '0x14', '0X64',
                      '0b10100', "2'0", '20.0', '2e1', '２０', '٢٠', '²⁰'):
            with self.subTest(value=value):
                self.rejects(config(value))

    def test_unsigned_suffix_is_required_and_only_one_u_is_supported(self):
        for literal in ('20', '20UL', '20ULL', '20UU', '20ul', '20uL', '20 U'):
            with self.subTest(literal=literal):
                self.rejects(CONFIG.format(DECLARATION.format('20').replace('20U', literal)))

    def test_expression_macro_cast_alias_and_parentheses_are_rejected(self):
        for expression in ('10U + 10U', '(20U)', 'static_cast<std::uint32_t>(20U)',
                           'std::uint32_t{20U}', 'PUSH_WINDOW', 'OTHER',
                           '20U << 0U', 'true ? 20U : 0U', 'sizeof(int)', '20U, ignored=0U'):
            with self.subTest(expression=expression):
                text = DECLARATION.format('20').replace('20U', expression)
                self.rejects('#define PUSH_WINDOW 20U\nconstexpr auto OTHER=20U;\n' +
                             CONFIG.format(text))

    def test_declared_type_qualifiers_name_and_terminator_must_be_exact(self):
        original = DECLARATION.format('20')
        for declaration in (original.replace('inline ', ''), original.replace('constexpr ', ''),
                            original.replace('inline constexpr', 'constexpr inline'),
                            original.replace('std::uint32_t', 'uint32_t'),
                            original.replace('std::uint32_t', 'std::uint64_t'),
                            original.replace('std::uint32_t', 'auto'),
                            original.replace('constexpr', 'const'), original[:-1],
                            original.replace('20U', ''), original.replace('=', '==')):
            with self.subTest(declaration=declaration):
                self.rejects(CONFIG.format(declaration))

    def test_missing_or_only_commented_identifier_never_infers_a_default(self):
        for text in ('', '#pragma once\n#include <cstdint>\n',
                     '// ' + DECLARATION.format('0'), '/* ' + DECLARATION.format('0') + ' */',
                     config('0').replace(IDENTIFIER, 'OTHER_EDGE_PUSH_THROUGH_MS')):
            with self.subTest(text=text):
                self.rejects(text)

    def test_duplicate_declarations_references_and_macro_uses_are_rejected(self):
        for extra in (DECLARATION.format('0'), DECLARATION.format('20'),
                      'static_assert(EDGE_PUSH_THROUGH_MS <= 100U);',
                      'constexpr auto OTHER = EDGE_PUSH_THROUGH_MS;',
                      '#define EDGE_PUSH_THROUGH_MS 20U', '#undef EDGE_PUSH_THROUGH_MS',
                      '#define OTHER EDGE_PUSH_THROUGH_MS'):
            with self.subTest(extra=extra):
                self.rejects(config('0') + extra + '\n')

    def test_declaration_under_if_ifdef_ifndef_else_or_nested_branch_is_unsupported(self):
        for prefix, suffix in (
            ('#if 0\n', '#endif\n'), ('#if 1\n', '#endif\n'),
            ('#ifdef ANY\n', '#endif\n'), ('#ifndef ANY\n', '#endif\n'),
            ('#if 0\n#else\n', '#endif\n'), ('#if 0\n#elif 1\n', '#endif\n'),
            ('#if 1\n#ifdef ANY\n', '#endif\n#endif\n'),
            ('  # if 0\n', '  # endif\n'),
        ):
            with self.subTest(prefix=prefix):
                self.rejects(prefix + config('20') + suffix)

    def test_commented_conditionals_are_not_active_and_conditionals_cannot_hide_duplicates(self):
        self.accepts('// #if 0\n/* #ifdef ANY */\n' + config('20'))
        self.rejects(config('0') + '#if 0\n' + DECLARATION.format('20') + '\n#endif\n')

    def test_unterminated_block_comments_refuse_even_after_a_valid_declaration(self):
        for text in ('/* unfinished', config('20') + '/* unfinished',
                     '/* ' + DECLARATION.format('0')):
            with self.subTest(text=text):
                self.rejects(text)

    def test_quoted_identifiers_are_inactive_and_quoted_declarations_cannot_satisfy_admission(self):
        quoted = 'constexpr auto note = "' + DECLARATION.format('101') + '";\n'
        self.accepts(config('20') + quoted)
        self.accepts(config('20') + "constexpr auto note = 'EDGE_PUSH_THROUGH_MS';\n")
        self.accepts(config('0') + 'constexpr auto note = "\\\"EDGE_PUSH_THROUGH_MS\\\"";\n')
        self.accepts(config('0') + 'constexpr auto note = "/* EDGE_PUSH_THROUGH_MS */";\n')
        self.rejects(quoted)
        self.rejects('constexpr auto note = "' + DECLARATION.format('0') + '";\n')

    def test_unterminated_or_physically_broken_quotes_are_identified_errors(self):
        for tail in ('"unfinished', "'unfinished", '"dangling\\',
                     '"broken\nstring";', "'broken\ncharacter';"):
            with self.subTest(tail=tail):
                self.rejects(config('0') + tail)

    def test_declaration_and_preprocessor_backslash_continuations_are_unsupported(self):
        for text in (
            CONFIG.format('inline \\\nconstexpr std::uint32_t EDGE_PUSH_THROUGH_MS = 20U;'),
            CONFIG.format('inline constexpr std::uint32_t EDGE_PUSH_THROUGH_MS = 2\\\n0U;'),
            '#if \\\n0\n' + config('0') + '#endif\n',
            '#define OTHER \\\n1\n' + config('0'),
        ):
            with self.subTest(text=text):
                self.rejects(text)

    def test_all_physical_splices_refuse_before_comments_or_quotes_can_hide_them(self):
        for ending in ('\n', '\r\n', ' \n', '\t\n', ' \t\r\n'):
            splice = '\\' + ending
            cases = (
                config('0') + '// comment ' + splice + 'continued comment\n',
                config('0') + '/* comment ' + splice + 'continued comment */\n',
                config('0') + 'constexpr auto note = "first' + splice + 'second";\n',
                config('0') + "constexpr auto note = 'a" + splice + "b';\n",
                config('0') + '#define OTHER ' + splice + '1\n',
                config('0') + splice,
                '// a splice must not expose this declaration\n'.replace('\n', splice) +
                    DECLARATION.format('0') + '\n',
            )
            for index, text in enumerate(cases):
                with self.subTest(ending=repr(ending), case=index):
                    self.rejects(text)

    def test_code_level_digraph_directive_lines_are_rejected_without_macro_evaluation(self):
        for indentation in ('', ' ', '\t', '/* prefix comment */ ', '/* first\nsecond */\t'):
            for directive in ('%:if 0', '%: if 1', '%:ifdef ANY', '%:ifndef ANY',
                              '%:define OTHER 1', '%:else', '%:elif 0', '%:endif', '%:%:', '%:'):
                with self.subTest(indentation=indentation, directive=directive):
                    self.rejects(indentation + directive + '\n' + config('20'))
        self.rejects('%:if 0\r\n' + config('0').replace('\n', '\r\n') + '%:endif\r\n')

    def test_digraph_text_inside_ordinary_comments_and_quoted_literals_is_inactive(self):
        for decoration in (
            '// %:if 0\n', '/* %:if 0 */\n', '/* first\n%:if 0\n%:endif\n*/\n',
            'constexpr auto note = "%:if 0";\n', "constexpr auto note = '%:';\n",
            'constexpr auto note = "\\\"%:if 0\\\"";\n',
        ):
            with self.subTest(decoration=decoration):
                self.accepts(decoration + config('20'))

    def test_non_utf8_config_is_an_identified_error(self):
        self.rejects(config('0').encode() + b'\xff\xfe')

    def test_missing_directory_and_unreadable_config_are_identified_errors(self):
        with self.assertRaisesRegex(ValueError, IDENTIFIER):
            board.validate_push_through_config(self.path)
        with self.assertRaisesRegex(ValueError, IDENTIFIER):
            board.validate_push_through_config(self.root)
        self.write(config('0'))
        with mock.patch.object(Path, 'open', side_effect=PermissionError('controlled read denial')):
            with self.assertRaisesRegex(ValueError, IDENTIFIER):
                board.validate_push_through_config(self.path)


class PushStageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='d132-stage-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.hash_sources = board.source_hash
        patch = mock.patch.object(board, 'ROOT', self.root)
        patch.start()
        self.addCleanup(patch.stop)
        self.write('src/config.h', config('0'))
        for module in ('core', 'hal', 'app'):
            self.write('src/' + module + '/shared.h', '// independent source ' + module + '\n')
        for sketch in SKETCHES:
            folder = 'src/app' if sketch == 'app' else sketch
            self.write(folder + '/' + Path(sketch).name + '.ino',
                       '#include "src/config.h"\nvoid setup() {}\nvoid loop() {}\n')
            self.write(folder + '/local.h', '// sketch local bytes\r\n')

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode() if isinstance(text, str) else text)
        return path

    @contextmanager
    def operations(self):
        with ExitStack() as stack:
            calls = {}
            for name, result in (('target', 'fixture-board'), ('setting', '/fixture/root'),
                                 ('compile_app', '/checked/unique/artifacts')):
                calls[name] = stack.enter_context(mock.patch.object(board, name, return_value=result))
            for name in ('require_transport', 'verify_core', 'sync_sources', 'remote',
                         'verify_inert_source', 'verify_runtime_artifacts'):
                calls[name] = stack.enter_context(mock.patch.object(board, name))
            calls['source_hash'] = stack.enter_context(mock.patch.object(
                board, 'source_hash', wraps=board.source_hash))
            stack.enter_context(redirect_stdout(io.StringIO()))
            yield calls

    def no_board_operations(self, calls):
        for name in ('verify_core', 'remote', 'sync_sources', 'compile_app',
                     'verify_runtime_artifacts'):
            calls[name].assert_not_called()

    def test_actual_app_and_bench_stages_keep_supported_config_bytes_and_layout(self):
        for sketch in SKETCHES:
            for value in ('0', '20', '100'):
                with self.subTest(sketch=sketch, value=value), self.operations() as calls:
                    raw = config(value).replace('\n', '\r\n').encode()
                    self.write('src/config.h', raw)
                    output = board.stage(sketch)
                    self.assertEqual(output, self.root / 'build/stage' / Path(sketch).name)
                    self.assertEqual((output / 'src/config.h').read_bytes(), raw)
                    self.assertTrue((output / (Path(sketch).name + '.ino')).is_file())
                    self.assertTrue((output / 'local.h').is_file())
                    self.no_board_operations(calls)

    def test_actual_stage_always_validates_the_copied_destination_not_the_root(self):
        validate = board.validate_push_through_config
        for sketch in SKETCHES:
            seen = []
            expected = self.root / 'build/stage' / Path(sketch).name / 'src/config.h'

            def check(path):
                self.assertEqual(Path(path), expected)
                self.assertEqual(Path(path).read_bytes(), config('0').encode())
                seen.append(Path(path))
                return validate(path)

            with self.subTest(sketch=sketch), self.operations():
                with mock.patch.object(board, 'validate_push_through_config', side_effect=check):
                    board.stage(sketch)
                self.assertEqual(seen, [expected])

    def test_malformed_copied_bytes_are_rejected_even_when_root_config_is_valid(self):
        validate = board.validate_push_through_config
        root_config = self.root / 'src/config.h'
        expected = self.root / 'build/stage/reactive_test/src/config.h'

        def corrupt_copy(path):
            self.assertEqual(Path(path), expected)
            self.assertEqual(Path(path).read_bytes(), root_config.read_bytes())
            Path(path).write_text(config('4294967316'), encoding='utf-8')
            return validate(path)

        with self.operations() as calls:
            with mock.patch.object(board, 'validate_push_through_config', side_effect=corrupt_copy):
                with self.assertRaisesRegex(ValueError, IDENTIFIER):
                    board.flash(fixture.args('bench/reactive_test'))
            self.no_board_operations(calls)
        self.assertEqual(root_config.read_bytes(), config('0').encode())
        self.assertEqual(expected.read_bytes(), config('4294967316').encode())

    def test_invalid_root_values_fail_actual_stage_for_app_and_bench(self):
        for sketch in SKETCHES:
            for value in ('101', '4294967295', '4294967296', '4294967316', '20 + 0'):
                with self.subTest(sketch=sketch, value=value), self.operations() as calls:
                    self.write('src/config.h', config(value))
                    with self.assertRaisesRegex(ValueError, IDENTIFIER):
                        board.stage(sketch)
                    self.no_board_operations(calls)

    def test_invalid_flash_configs_make_zero_board_calls_before_refusal(self):
        invalid = (config('101'), config('4294967316'), '', config('020'),
                   config('0') + DECLARATION.format('20'), '#if 0\n' + config('0') + '#endif\n',
                   config('0') + '/* unterminated', b'\xff')
        for sketch in SKETCHES:
            for index, text in enumerate(invalid):
                with self.subTest(sketch=sketch, case=index), self.operations() as calls:
                    self.write('src/config.h', text)
                    with self.assertRaisesRegex(ValueError, IDENTIFIER):
                        board.flash(fixture.args(sketch))
                    self.no_board_operations(calls)

    def test_digraph_conditional_cannot_hide_a_push_declaration_on_actual_flash_path(self):
        for sketch in SKETCHES:
            with self.subTest(sketch=sketch), self.operations() as calls:
                self.write('src/config.h', '%:if 0\n' + config('20') + '%:endif\n')
                with self.assertRaisesRegex(ValueError, IDENTIFIER):
                    board.flash(fixture.args(sketch))
                self.no_board_operations(calls)

    def test_restage_rechecks_new_bytes_and_does_not_reuse_prior_valid_admission(self):
        for sketch in SKETCHES:
            with self.subTest(sketch=sketch), self.operations() as calls:
                self.write('src/config.h', config('20'))
                output = board.stage(sketch)
                self.write('src/config.h', config('4294967316'))
                with self.assertRaisesRegex(ValueError, IDENTIFIER):
                    board.stage(sketch)
                self.assertEqual((output / 'src/config.h').read_bytes(), config('4294967316').encode())
                self.no_board_operations(calls)

    def test_valid_app_and_reactive_flash_preserve_exact_inert_profile_and_hash(self):
        for sketch, flags in (('app', '-DMATCH=0 -DMOTORS_ALLOWED=0'),
                              ('bench/reactive_test', '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P4_REACTIVE=1')):
            for value in ('0', '20', '100'):
                with self.subTest(sketch=sketch, value=value), self.operations() as calls:
                    self.write('src/config.h', config(value))
                    board.flash(fixture.args(sketch))
                    staged = self.root / 'build/stage' / Path(sketch).name
                    digest = self.hash_sources(staged)
                    calls['source_hash'].assert_called_once_with(staged)
                    actual = calls['compile_app'].call_args
                    self.assertIsNotNone(actual)
                    self.assertEqual(actual.args[0], 'fixture-board')
                    self.assertRegex(actual.args[1], r'^[0-9a-f]{64}$')
                    self.assertEqual(actual.args[1], digest)
                    self.assertEqual(actual.args[2], '/fixture/root/' + actual.args[1] + '/' + Path(sketch).name)
                    self.assertEqual(actual.args[3:6], ('/fixture/root', fixture.FQBN, flags))
                    self.assertEqual(actual.args[6], 'default')
                    self.assertEqual(actual.kwargs.get('project', 'app.ino'), Path(sketch).name + '.ino')
                    self.assertEqual(calls['remote'].call_args_list,
                                     [mock.call('fixture-board', ['mkdir', '-p', actual.args[2]])])
                    self.assertEqual((staged / 'src/config.h').read_bytes(), config(value).encode())
                    self.assertEqual((self.root / 'src/config.h').read_bytes(), config(value).encode())


if __name__ == '__main__':
    unittest.main(verbosity=2)
