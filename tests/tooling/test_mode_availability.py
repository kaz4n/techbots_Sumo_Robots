# Tests B13/D134 literal mode availability, historical compatibility and staging.
# Keeps expected grammar and defaults independent of the opaque production parser.
# Temporary roots exercise direct admission, real stage/flash and copied public headers.
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from . import test_p0_config as registry
from . import test_push_literal_admission as staging

board = staging.board
ROOT = Path(__file__).resolve().parents[2]
ARC = 'MODE_ARC_ENABLED'
WAIT = 'MODE_WAIT_ENABLED'
DEFAULT = 'MODE_DEFAULT'
DECL = 'inline constexpr std::uint32_t {} = {};\n'
PAIRS = ((0, 0), (0, 1), (1, 0), (1, 1))


def configuration(arc=1, wait=1, default=1):
    return (staging.config('0') + '\nnamespace config {\n' +
            ''.join(DECL.format(name, str(value) + 'U') for name, value in
                    ((ARC, arc), (WAIT, wait), (DEFAULT, default))) + '}\n')


def allowed(arc, wait, default):
    return default in (1, 2, 3) or (default in (4, 5) and arc == 1) or (default == 6 and wait == 1)


class ModeLiteralTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='d134-mode-literal-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / 'config.h'

    def check_source(self, source, valid):
        raw = source.encode() if isinstance(source, str) else source
        self.path.write_bytes(raw)
        if valid:
            board.validate_mode_availability_config(self.path)
        else:
            with self.assertRaisesRegex(ValueError, r'MODE_|mode.availability'):
                board.validate_mode_availability_config(self.path)
        self.assertEqual(self.path.read_bytes(), raw)

    def test_all_four_pairs_and_all_six_defaults_have_exact_availability(self):
        for arc, wait in PAIRS:
            for default in range(1, 7):
                with self.subTest(arc=arc, wait=wait, default=default):
                    self.check_source(configuration(arc, wait, default), allowed(arc, wait, default))

    def test_lowercase_suffix_spacing_and_ordinary_comment_separators_are_supported(self):
        source = configuration(0, 1, 6).replace('U;', 'u ;').replace('inline constexpr',
                 'inline /* identifier MODE_ARC_ENABLED */\tconstexpr\n')
        self.check_source(source.replace('std::uint32_t ', 'std::uint32_t\r\n'), True)
        self.check_source(configuration() + '// MODE_WAIT_ENABLED final comment', True)

    def test_both_absent_is_legacy_including_commented_or_quoted_switch_names(self):
        for source in ('', staging.config('0'), '// MODE_ARC_ENABLED\n/* MODE_WAIT_ENABLED */',
                       'const char* note = "' + DECL.format(ARC, '2U').strip() + '";\n',
                       "const auto note = 'MODE_WAIT_ENABLED';\n"):
            with self.subTest(source=source):
                self.check_source(source, True)

    def test_each_missing_partner_or_default_refuses_active_new_contract(self):
        for name in (ARC, WAIT, DEFAULT):
            with self.subTest(missing=name):
                self.check_source(configuration().replace(DECL.format(name, '1U'), ''), False)

    def test_duplicate_and_extra_active_references_are_rejected(self):
        for name in (ARC, WAIT, DEFAULT):
            for suffix in (DECL.format(name, '1U'), 'constexpr auto other = ' + name + ';\n',
                           '#define ALIAS ' + name + '\n', '#if ' + name + '\n#endif\n'):
                with self.subTest(name=name, suffix=suffix):
                    self.check_source(configuration() + suffix, False)

    def test_bool_range_and_unsigned_width_aliases_refuse_before_conversion(self):
        for name in (ARC, WAIT):
            for value in ('2U', '6U', '4294967295U', '4294967296U', '4294967297U',
                          '18446744073709551616U', '9' * 10000 + 'U', '0' * 10000 + 'U'):
                with self.subTest(name=name, length=len(value), prefix=value[:20]):
                    self.check_source(configuration().replace(DECL.format(name, '1U'),
                                                            DECL.format(name, value)), False)

    def test_default_range_and_huge_narrowing_aliases_are_rejected(self):
        for value in ('0U', '7U', '255U', '257U', '4294967297U', '9' * 10000 + 'U'):
            with self.subTest(value=value[:20]):
                self.check_source(configuration().replace(DECL.format(DEFAULT, '1U'),
                                                          DECL.format(DEFAULT, value)), False)

    def test_noncanonical_literals_expressions_and_suffixes_are_rejected(self):
        for name in (ARC, WAIT, DEFAULT):
            for value in ('01U', '+1U', '-0U', '0x1U', '0b1U', '１U', '١U', '1',
                          '1UL', '1ULL', '1UU', '1 U', 'true', '(1U)', '1U + 0U',
                          '1.0', "1'0U", 'OTHER', 'static_cast<unsigned>(1)'):
                with self.subTest(name=name, value=value):
                    self.check_source(configuration().replace(DECL.format(name, '1U'),
                                                              DECL.format(name, value)), False)

    def test_wrong_declaration_shape_is_not_admitted(self):
        for name in (ARC, WAIT, DEFAULT):
            for text in ('constexpr std::uint32_t {} = 1U;', 'inline const std::uint32_t {} = 1U;',
                         'inline constexpr unsigned {} = 1U;', 'inline constexpr uint32_t {} = 1U;',
                         'inline constexpr std::uint32_t {} = 1U', '#define {} 1U'):
                with self.subTest(name=name, text=text):
                    self.check_source(configuration().replace(DECL.format(name, '1U'),
                                                              text.format(name) + '\n'), False)

    def test_all_conditional_branches_are_rejected_including_if_zero_legacy_decoy(self):
        for prefix, suffix in (('#if 0\n', '#endif\n'), ('#if 1\n', '#endif\n'),
                               ('#ifdef ANY\n', '#endif\n'), ('#ifndef ANY\n', '#endif\n'),
                               ('#if 0\n#else\n', '#endif\n'),
                               ('#if 1\n#if 0\n', '#endif\n#endif\n')):
            with self.subTest(prefix=prefix):
                self.check_source(prefix + configuration() + suffix, False)
                self.check_source(prefix + DECL.format(ARC, '0U') + suffix, False)

    def test_completed_unrelated_conditionals_and_quoted_decoys_remain_inactive(self):
        self.check_source('#ifndef OTHER\n#define OTHER 1\n#endif\n' + configuration() +
                          '#if OTHER\nconstexpr int value = 1;\n#endif\n', True)
        for quote in ('"MODE_ARC_ENABLED MODE_WAIT_ENABLED MODE_DEFAULT"', "'MODE_ARC_ENABLED'",
                      '"/* MODE_WAIT_ENABLED */"', '"\\\"MODE_DEFAULT\\\""'):
            self.check_source(configuration() + 'constexpr auto note = ' + quote + ';\n', True)

    def test_quoted_declaration_cannot_supply_missing_active_partner(self):
        source = configuration().replace(DECL.format(WAIT, '1U'), '')
        self.check_source(source + 'const auto note = "' + DECL.format(WAIT, '1U').strip() + '";', False)

    def test_malformed_lexical_text_refuses_even_with_both_switches_absent(self):
        for base in ('', staging.config('0'), configuration()):
            for suffix in ('/* unfinished', '"unfinished', "'unfinished", '"bad\nquote"',
                           "'bad\nquote'", '"dangling\\'):
                with self.subTest(base=bool(base), suffix=suffix):
                    self.check_source(base + suffix, False)

    def test_physical_splices_reject_before_legacy_or_comment_quote_masking(self):
        for base in ('', configuration()):
            for ending in ('\n', '\r\n', ' \n', '\t\r\n', ' \t\r\n'):
                for start, end in (('// comment ', 'still comment\n'), ('/* ', ' */'),
                                   ('"first', 'second"'), ('#define OTHER ', '1\n'), ('', '')):
                    with self.subTest(base=bool(base), ending=repr(ending), start=start):
                        self.check_source(base + start + '\\' + ending + end, False)

    def test_code_digraphs_reject_before_legacy_return_but_comments_and_quotes_do_not(self):
        for base in ('', staging.config('0'), configuration()):
            for prefix in ('', ' ', '\t', '/* prefix */ ', '/* two\nlines */ '):
                self.check_source(base + prefix + '%:if 0\n%:endif\n', False)
            for decoration in ('// %:if 0\n', '/*\n%:if 0\n*/\n',
                               'const auto note = "%:if 0";\n', "const auto note = '%:';\n"):
                self.check_source(base + decoration, True)

    def test_non_utf8_missing_directory_and_read_denial_are_identified_errors(self):
        self.check_source(b'\xff\xfe', False)
        self.path.unlink()
        for path in (self.path, self.root):
            with self.assertRaisesRegex(ValueError, r'MODE_|mode.availability'):
                board.validate_mode_availability_config(path)
        self.path.write_text(configuration(), encoding='utf-8')
        with mock.patch.object(Path, 'open', side_effect=PermissionError('controlled denial')):
            with self.assertRaisesRegex(ValueError, r'MODE_|mode.availability'):
                board.validate_mode_availability_config(self.path)


class ModeStageTests(unittest.TestCase):
    def setUp(self):
        # Composition reuses only the existing public temporary stage/transport fixture.
        self.stage = staging.PushStageTests(methodName='runTest')
        self.addCleanup(self.stage.doCleanups)
        self.stage.setUp()
        self.root = self.stage.root

    def test_actual_app_and_bench_stages_preserve_every_pair_and_supported_default_bytes(self):
        for sketch in staging.SKETCHES:
            for arc, wait in PAIRS:
                for default in range(1, 7):
                    if not allowed(arc, wait, default):
                        continue
                    with self.subTest(sketch=sketch, pair=(arc, wait), default=default):
                        raw = configuration(arc, wait, default).replace('\n', '\r\n').encode()
                        self.stage.write('src/config.h', raw)
                        with self.stage.operations() as calls:
                            output = board.stage(sketch)
                            self.stage.no_board_operations(calls)
                        self.assertEqual(output, self.root / 'build/stage' / Path(sketch).name)
                        self.assertEqual((output / 'src/config.h').read_bytes(), raw)
                        self.assertEqual((self.root / 'src/config.h').read_bytes(), raw)
                        self.assertTrue((output / (Path(sketch).name + '.ino')).is_file())

    def test_stage_calls_mode_validator_on_exact_copied_config_once(self):
        validate = board.validate_mode_availability_config
        for sketch in staging.SKETCHES:
            self.stage.write('src/config.h', configuration(0, 0))
            expected = self.root / 'build/stage' / Path(sketch).name / 'src/config.h'
            seen = []

            def inspect(path):
                self.assertEqual(Path(path), expected)
                self.assertEqual(Path(path).read_bytes(), configuration(0, 0).encode())
                seen.append(Path(path))
                return validate(path)

            with self.subTest(sketch=sketch), self.stage.operations():
                with mock.patch.object(board, 'validate_mode_availability_config', side_effect=inspect):
                    board.stage(sketch)
            self.assertEqual(seen, [expected])

    def test_corrupt_copied_config_refuses_with_zero_remote_calls_despite_valid_root(self):
        validate = board.validate_mode_availability_config
        self.stage.write('src/config.h', configuration())
        expected = self.root / 'build/stage/reactive_test/src/config.h'

        def corrupt(path):
            self.assertEqual(Path(path), expected)
            Path(path).write_text(configuration(0, 0, 6), encoding='utf-8')
            return validate(path)

        with self.stage.operations() as calls:
            with mock.patch.object(board, 'validate_mode_availability_config', side_effect=corrupt):
                with self.assertRaisesRegex(ValueError, r'MODE_|mode.availability'):
                    board.flash(staging.fixture.args('bench/reactive_test'))
            self.stage.no_board_operations(calls)
        self.assertEqual((self.root / 'src/config.h').read_bytes(), configuration().encode())
        self.assertEqual(expected.read_bytes(), configuration(0, 0, 6).encode())

    def test_invalid_availability_and_missing_partner_refuse_actual_flash_before_board_calls(self):
        invalid = (configuration(2, 1), configuration(1, 2), configuration(0, 1, 4),
                   configuration(1, 0, 6), configuration(4294967297, 1),
                   configuration().replace(DECL.format(WAIT, '1U'), ''),
                   '#if 0\n' + configuration() + '#endif\n')
        for sketch in staging.SKETCHES:
            for index, source in enumerate(invalid):
                with self.subTest(sketch=sketch, case=index), self.stage.operations() as calls:
                    self.stage.write('src/config.h', source)
                    with self.assertRaises(ValueError):
                        board.flash(staging.fixture.args(sketch))
                    self.stage.no_board_operations(calls)

    def test_both_absent_historical_stage_still_preserves_original_config(self):
        for sketch in staging.SKETCHES:
            raw = staging.config('0').encode()
            self.stage.write('src/config.h', raw)
            with self.subTest(sketch=sketch), self.stage.operations() as calls:
                output = board.stage(sketch)
                self.stage.no_board_operations(calls)
            self.assertEqual((output / 'src/config.h').read_bytes(), raw)

    def test_real_inert_flash_keeps_profile_flags_hash_and_source_for_all_pairs(self):
        for sketch, flags in (('app', '-DMATCH=0 -DMOTORS_ALLOWED=0'),
                              ('bench/reactive_test', '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P4_REACTIVE=1')):
            for arc, wait in PAIRS:
                with self.subTest(sketch=sketch, pair=(arc, wait)), self.stage.operations() as calls:
                    raw = configuration(arc, wait).encode()
                    self.stage.write('src/config.h', raw)
                    board.flash(staging.fixture.args(sketch))
                    output = self.root / 'build/stage' / Path(sketch).name
                    digest = self.stage.hash_sources(output)
                    calls['source_hash'].assert_called_once_with(output)
                    actual = calls['compile_app'].call_args
                    self.assertIsNotNone(actual)
                    self.assertEqual(actual.args[1], digest)
                    self.assertEqual(actual.args[3:6], ('/fixture/root', staging.fixture.FQBN, flags))
                    self.assertEqual((output / 'src/config.h').read_bytes(), raw)


class ModePublicHeaderTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='d134-mode-headers-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'src/core').mkdir(parents=True)
        (self.root / 'docs').mkdir()
        self.original = (ROOT / 'src/config.h').read_text(encoding='utf-8')
        shutil.copyfile(ROOT / 'src/core/types.h', self.root / 'src/core/types.h')
        shutil.copyfile(ROOT / 'docs/BEHAVIOR.md', self.root / 'docs/BEHAVIOR.md')
        self.probe = self.root / 'probe.cc'
        self.probe.write_text('#include "src/core/types.h"\n'
                              'static_assert(core::modeAvailable(core::Mode::DIRECT));\n', encoding='utf-8')

    def replaced(self, **values):
        source = self.original
        for name, value in values.items():
            pattern = r'(inline constexpr std::uint32_t ' + name + r' = )[^;]+;'
            source, count = re.subn(pattern, lambda m: m[1] + str(value) + 'U;', source)
            self.assertEqual(count, 1)
        return source

    def compile_source(self, source, accepted):
        (self.root / 'src/config.h').write_text(source, encoding='utf-8')
        compiler = shutil.which('g++')
        self.assertIsNotNone(compiler, 'D134 configured host runner requires g++')
        result = subprocess.run([compiler, '-std=c++17', '-fsyntax-only', str(self.probe)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode == 0, accepted, result.stderr)

    def test_new_public_core_accepts_all_pairs_with_available_mandatory_and_optional_defaults(self):
        for arc, wait in PAIRS:
            for default in range(1, 7):
                with self.subTest(pair=(arc, wait), default=default):
                    self.compile_source(self.replaced(MODE_ARC_ENABLED=arc, MODE_WAIT_ENABLED=wait,
                                                      MODE_DEFAULT=default), allowed(arc, wait, default))

    def test_new_core_requires_both_symbols_despite_legacy_tool_admission(self):
        source = self.original
        for name in (ARC, WAIT):
            source, count = re.subn(r'inline constexpr std::uint32_t ' + name + r' = [^;]+;', '', source)
            self.assertEqual(count, 1)
        path = self.root / 'src/config.h'
        path.write_text(source, encoding='utf-8')
        board.validate_mode_availability_config(path)
        self.compile_source(source, False)

    def test_new_core_rejects_typed_switch_two_and_out_of_enum_defaults_before_cast(self):
        for values in ({ARC: 2}, {WAIT: 2}, {DEFAULT: 0}, {DEFAULT: 7}, {DEFAULT: 257}):
            with self.subTest(values=values):
                self.compile_source(self.replaced(**values), False)

    def test_independent_registry_literal_one_rejects_each_shipped_switch_drifting_to_zero_or_two(self):
        self.assertEqual(registry.BEHAVIOR_EXTRA_DEFAULTS[ARC], 1)
        self.assertEqual(registry.BEHAVIOR_EXTRA_DEFAULTS[WAIT], 1)
        method = 'test_explicit_behavior_text_defaults_match_spec'
        for name in (ARC, WAIT):
            for value in (0, 2):
                with self.subTest(name=name, value=value):
                    (self.root / 'src/config.h').write_text(self.replaced(**{name: value}), encoding='utf-8')
                    case = registry.P0ConfigTests(methodName=method)
                    result = unittest.TestResult()
                    with mock.patch.object(registry, 'PROJECT', self.root):
                        case.run(result)
                    self.assertEqual(result.testsRun, 1)
                    self.assertEqual(len(result.errors), 0, result.errors)
                    self.assertEqual(len(result.failures), 1, result.failures)


if __name__ == '__main__':
    unittest.main(verbosity=2)
