# Checks D136 uniqueness when declarators have parentheses or leading attributes.
# Keeps actual declarations distinct from equally decorated ordinary read expressions.
# Independent follow-up is frozen before execution and preserves the original eight cases.
from pathlib import Path
import sys

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file())
FIXTURES = str(ROOT / 'tests/tooling')
if FIXTURES not in sys.path:
    sys.path.insert(0, FIXTURES)
from opener_abort_fixture import AbortAnalysisCase, VALUES
from test_opener_abort_declarations import extra_declaration


class OpenerAbortDeclaratorPrefixTests(AbortAnalysisCase):
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

    def assert_accepted(self, raw):
        self.source.write(raw)
        report = self.analyze([])
        self.assertEqual((report['input_status'], report['evidence_status'], report['timing_status']),
                         ('VALID', 'INCOMPLETE', 'NOT_QUALIFIED'), report)
        self.assertEqual(report['source']['binding_status'], 'DECLARED_MATCH')
        self.assertEqual(report['source']['config_values'], VALUES)
        self.assertEqual(report['errors'], [])

    def reject_extras(self, forms):
        original = self.source.canonical()
        for name in VALUES:
            for form in forms:
                for namespace in ('same', 'other'):
                    for before in (False, True):
                        with self.subTest(name=name, form=form, namespace=namespace, before=before):
                            raw = extra_declaration(original, form.format(name=name), namespace, before)
                            self.assert_rejected(raw)

    def accept_reads(self, forms):
        original = self.source.canonical()
        for name in VALUES:
            for namespace in ('same', 'other'):
                read = name if namespace == 'same' else 'config::' + name
                for form in forms:
                    with self.subTest(name=name, form=form, namespace=namespace):
                        raw = extra_declaration(original, form.format(read=read), namespace)
                        self.assert_accepted(raw)

    def test_D136_parenthesized_extra_declarators_reject_all_seven_reserved_names(self):
        self.reject_extras(('inline constexpr std::uint32_t ({name}) = 2000U;',
                            'inline constexpr std::uint32_t ({name}){{2000U}};'))

    def test_D136_leading_maybe_unused_attributes_do_not_hide_extra_direct_or_list_declarations(self):
        self.reject_extras(('[[maybe_unused]] inline constexpr std::uint32_t {name}(2000U);',
                            '[[maybe_unused]] inline constexpr std::uint32_t {name}{{2000U}};'))

    def test_D136_alignas_prefix_does_not_hide_extra_scalar_declarations(self):
        self.reject_extras(('alignas(8) inline constexpr std::uint32_t {name} = 2000U;',
                            'alignas(8) inline constexpr std::uint32_t {name}(2000U);',
                            'alignas(8) inline constexpr std::uint32_t {name}{{2000U}};'))

    def test_D136_parenthesized_declarations_of_other_names_and_parenthesized_reads_remain_allowed(self):
        self.accept_reads(('inline constexpr std::uint32_t (derived) = {read};',
                           'inline constexpr std::uint32_t derived = ({read});',
                           'inline constexpr std::uint32_t (derived){{({read})}};'))

    def test_D136_attributed_ordinary_read_declarations_remain_allowed(self):
        self.accept_reads(('[[maybe_unused]] inline constexpr std::uint32_t derived = {read};',
                           '[[maybe_unused]] inline constexpr std::uint32_t derived({read});',
                           '[[maybe_unused]] inline constexpr std::uint32_t derived{{{read}}};'))

    def test_D136_aligned_ordinary_read_declarations_remain_allowed(self):
        self.accept_reads(('alignas(8) inline constexpr std::uint32_t derived = {read};',
                           'alignas(8) inline constexpr std::uint32_t derived({read});',
                           'alignas(8) inline constexpr std::uint32_t derived{{{read}}};'))
