# Checks D136 declaration uniqueness beyond the one supported scalar spelling.
# Separates additional declarations of reserved names from legitimate read expressions.
# Frozen before execution; public API cases reuse existing synthetic fixture APIs only.
from pathlib import Path
import sys

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file())
FIXTURES = str(ROOT / 'tests/tooling')
if FIXTURES not in sys.path:
    sys.path.insert(0, FIXTURES)
from opener_abort_fixture import AbortAnalysisCase, Bundle, ENDPOINTS, VALUES


def extra_declaration(original, declaration, namespace, before=False):
    body = ('inline constexpr std::uint32_t extra_anchor = 1U;\n' + declaration + '\n').encode()
    if namespace == 'same':
        marker = b'namespace config {\n'
        if before:
            return original.replace(marker, marker + body, 1)
        return original[:-2] + body + b'}\n'
    extra = b'namespace other {\n' + body + b'}\n'
    marker = b'namespace config {\n'
    return original.replace(marker, extra + marker, 1) if before else original + extra


class OpenerAbortDeclarationTests(AbortAnalysisCase):
    def assert_rejected(self, raw):
        self.source.write(raw)
        report = self.analyze([])
        self.assertEqual((report['input_status'], report['evidence_status'], report['timing_status']),
                         ('VALID', 'INVALID', 'NOT_QUALIFIED'), report)
        self.assertEqual(report['source']['binding_status'], 'INVALID')
        self.assertIsNone(report['source']['config_values'])
        self.assertIn('UNSUPPORTED_CONFIGURATION', [error['code'] for error in report['errors']])
        self.assertEqual((report['qualified_attempts'], report['passing_attempts'], report['logical_failures']), (0, 0, 0))
        self.assertIsNone(report['minimum_elapsed_us'])
        self.assertIsNone(report['maximum_elapsed_us'])
        self.assertEqual(report['attempts'], [])

    def assert_accepted(self, raw):
        self.source.write(raw)
        report = self.analyze([])
        self.assertEqual((report['input_status'], report['evidence_status'], report['timing_status']),
                         ('VALID', 'INCOMPLETE', 'NOT_QUALIFIED'), report)
        self.assertEqual(report['source']['binding_status'], 'DECLARED_MATCH')
        self.assertEqual(report['source']['config_values'], VALUES)
        self.assertEqual(report['errors'], [])

    def test_D136_extra_scalar_direct_and_list_declarations_reject_each_name_in_both_namespaces(self):
        original = self.source.canonical()
        for name, value in VALUES.items():
            for suffix in ('(' + str(value) + 'U);', '{' + str(value) + 'U};', ' = {' + str(value) + 'U};'):
                declaration = 'inline constexpr std::uint32_t ' + name + suffix
                for namespace in ('same', 'other'):
                    for before in (False, True):
                        with self.subTest(name=name, suffix=suffix, namespace=namespace, before=before):
                            self.assert_rejected(extra_declaration(original, declaration, namespace, before))

    def test_D136_extra_different_scalar_types_do_not_restore_unique_configuration_binding(self):
        original = self.source.canonical()
        forms = ('inline constexpr auto {name}(1U);',
                 'inline constexpr unsigned long {name}{{1UL}};',
                 'inline constexpr std::uint64_t {name} = 1U;',
                 'const std::uint32_t {name}{{1U}};')
        for name in VALUES:
            for form in forms:
                for namespace in ('same', 'other'):
                    with self.subTest(name=name, form=form, namespace=namespace):
                        self.assert_rejected(extra_declaration(original, form.format(name=name), namespace))

    def test_D136_extra_reference_and_array_declarations_cannot_hide_behind_valid_scalar(self):
        original = self.source.canonical()
        forms = ('inline constexpr const std::uint32_t& {name} = extra_anchor;',
                 'inline constexpr const std::uint32_t& {name}{{extra_anchor}};',
                 'inline constexpr std::uint32_t {name}[]{{1U}};',
                 'inline constexpr std::uint32_t {name}[1] = {{1U}};')
        for name in VALUES:
            for form in forms:
                for namespace in ('same', 'other'):
                    with self.subTest(name=name, form=form, namespace=namespace):
                        self.assert_rejected(extra_declaration(original, form.format(name=name), namespace))

    def test_D136_extra_name_in_a_multiple_declarator_statement_is_still_a_declaration(self):
        original = self.source.canonical()
        for name in VALUES:
            for suffix in ('{1U};', '(1U);', ' = 1U;'):
                declaration = 'inline constexpr std::uint32_t another_value = 1U, ' + name + suffix
                for namespace in ('same', 'other'):
                    with self.subTest(name=name, suffix=suffix, namespace=namespace):
                        self.assert_rejected(extra_declaration(original, declaration, namespace))

    def test_D136_direct_and_list_initializers_alone_do_not_satisfy_required_canonical_declaration(self):
        original = self.source.canonical()
        for name, value in VALUES.items():
            prefix = 'inline constexpr std::uint32_t ' + name
            canonical = (prefix + ' = ' + str(value) + 'U;').encode()
            for suffix in ('(' + str(value) + 'U);', '{' + str(value) + 'U};', ' = {' + str(value) + 'U};'):
                with self.subTest(name=name, suffix=suffix):
                    self.assert_rejected(original.replace(canonical, (prefix + suffix).encode(), 1))

    def test_D136_unconditional_scalar_reference_array_and_derived_reads_remain_supported(self):
        original = self.source.canonical()
        forms = ('inline constexpr auto derived({read});',
                 'inline constexpr auto derived{{{read}}};',
                 'inline constexpr const auto& derived_ref = {read};',
                 'inline constexpr const auto& derived_ref{{{read}}};',
                 'inline constexpr std::uint32_t derived_array[]{{{read}}};',
                 'inline constexpr auto derived = ({read} + 0U) * 1U;')
        for name in VALUES:
            for namespace in ('same', 'other'):
                read = name if namespace == 'same' else 'config::' + name
                for form in forms:
                    with self.subTest(name=name, form=form, namespace=namespace):
                        self.assert_accepted(extra_declaration(original, form.format(read=read), namespace))

    def test_D136_fake_extra_declarations_in_comments_and_literals_remain_ignored(self):
        original = self.source.canonical()
        for name in VALUES:
            declaration = 'inline constexpr std::uint32_t ' + name + '{1U};'
            for extra in ('// ' + declaration + '\n', '/* ' + declaration + ' */\n',
                          'const char* text = "' + declaration + '";\n'):
                with self.subTest(name=name, extra=extra):
                    self.assert_accepted(original + extra.encode())

    def test_D136_duplicate_declaration_rejects_source_and_preserves_all_bundle_validation(self):
        raw = extra_declaration(self.source.canonical(), 'inline constexpr std::uint32_t TICK_US{1000U};', 'other')
        self.source.write(raw)
        bundles = [Bundle(self.directory, self.source, index) for index in range(2)]
        self.write_cohort(bundles)
        report = self.validated_then(lambda accepted: None, expected_calls=2)
        self.assertEqual(report['source']['binding_status'], 'INVALID')
        self.assertIsNone(report['source']['config_values'])
        self.assertEqual((report['input_status'], report['evidence_status'], report['timing_status']),
                         ('VALID', 'INVALID', 'NOT_QUALIFIED'))
        self.assertIn('UNSUPPORTED_CONFIGURATION', [error['code'] for error in report['errors']])
        self.assertEqual((report['qualified_attempts'], report['passing_attempts'], report['logical_failures']), (0, 0, 0))
        for attempt in report['attempts']:
            self.assertEqual((attempt['qualification'], attempt['binding_status'], attempt['trace_status']),
                             ('INVALID', 'INVALID', 'INVALID'))
            self.assertEqual((attempt['logical_status'], attempt['timing_status']), ('NOT_EVALUATED', 'NOT_EVALUATED'))
            self.assertEqual(attempt['validation']['format_integrity'], 'PASS')
            self.assertEqual(attempt['validation']['consistency'], 'PASS')
            for field in ENDPOINTS + ('motors_allowed', 'cue', 'handover_state', 'terminal_detail', 'terminal_value'):
                self.assertIsNone(attempt[field])
