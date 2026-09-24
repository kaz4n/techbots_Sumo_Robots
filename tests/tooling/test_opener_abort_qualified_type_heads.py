# Checks D136 reserved-name uniqueness for a finite set of qualified type heads.
# Separates leading/trailing cv and pointer/reference declarators from ordinary reads.
# Two spec-derived matrices are frozen before execution; no existing oracle is edited.
from pathlib import Path
import sys

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file())
FIXTURES = str(ROOT / 'tests/tooling')
if FIXTURES not in sys.path:
    sys.path.insert(0, FIXTURES)
from opener_abort_fixture import AbortAnalysisCase, VALUES
from test_opener_abort_declarations import extra_declaration


SCALAR_HEADS = (
    'std::uint32_t const', 'std::uint32_t volatile', 'std::uint32_t const volatile',
    'std::uint32_t volatile const', 'const std::uint32_t', 'volatile std::uint32_t',
    'const volatile std::uint32_t', '::std::uint32_t', '::std::uint32_t const',
    '::std::uint32_t volatile', '::std::uint32_t const volatile',
    'const ::std::uint32_t', 'volatile ::std::uint32_t', 'const volatile ::std::uint32_t',
)
INDIRECT_HEADS = (
    ('std::uint32_t const&', False),
    ('const ::std::uint32_t&', False),
    ('::std::uint32_t const volatile&', False),
    ('std::uint32_t const*', True),
    ('::std::uint32_t const* const', True),
    ('std::uint32_t const* volatile', True),
    ('const ::std::uint32_t* const volatile', True),
    ('std::uint32_t const* const&', True),
)
GROUPED_DECLARATORS = (
    ('std::uint32_t (* const TICK_US) = nullptr;',
     'std::uint32_t const (* const derived) = &{read};'),
    ('std::uint32_t (*(TICK_US)) = nullptr;',
     'std::uint32_t const (*(derived)) = &{read};'),
    ('std::uint32_t const (&(TICK_US)) = 2000U;',
     'std::uint32_t const (&(derived)) = {read};'),
    ('::std::uint32_t (* volatile TICK_US) = nullptr;',
     '::std::uint32_t const (* volatile derived) = &{read};'),
    ('::std::uint32_t const (* const (TICK_US)) = nullptr;',
     '::std::uint32_t const (* const (derived)) = &{read};'),
    ('std::uint32_t const (* const volatile (TICK_US)) = nullptr;',
     'std::uint32_t const (* const volatile (derived)) = &{read};'),
)


class OpenerAbortQualifiedTypeHeadTests(AbortAnalysisCase):
    def check_source(self, raw, accepted):
        self.source.write(raw)
        report = self.analyze([])
        self.assertEqual(report['input_status'], 'VALID')
        self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
        self.assertEqual(report['evidence_status'], 'INCOMPLETE' if accepted else 'INVALID', report)
        self.assertEqual(report['source']['binding_status'], 'DECLARED_MATCH' if accepted else 'INVALID')
        self.assertEqual(report['source']['config_values'], VALUES if accepted else None)
        self.assertEqual((report['qualified_attempts'], report['passing_attempts'], report['logical_failures']), (0, 0, 0))
        self.assertIsNone(report['minimum_elapsed_us'])
        self.assertIsNone(report['maximum_elapsed_us'])
        self.assertEqual(report['attempts'], [])
        if accepted:
            self.assertEqual(report['errors'], [])
        else:
            self.assertIn('UNSUPPORTED_CONFIGURATION', [error['code'] for error in report['errors']])

    def test_D136_qualified_scalar_heads_with_leading_or_trailing_cv_reject_extra_name_allow_reads(self):
        original = self.source.canonical()
        for head in SCALAR_HEADS:
            for namespace in ('same', 'other'):
                read = 'TICK_US' if namespace == 'same' else 'config::TICK_US'
                extra = head + ' (TICK_US) = 2000U;'
                with self.subTest(head=head, namespace=namespace, extra=extra):
                    self.check_source(extra_declaration(original, extra, namespace), False)
                controls = (head + ' (derived) = (' + read + ');',
                            head + ' derived((' + read + '));')
                for declaration in controls:
                    with self.subTest(head=head, namespace=namespace, read=declaration):
                        self.check_source(extra_declaration(original, declaration, namespace), True)

    def test_D136_qualified_pointer_reference_and_cv_combinations_reject_extra_name_allow_reads(self):
        original = self.source.canonical()
        for head, pointer in INDIRECT_HEADS:
            for namespace in ('same', 'other'):
                read = 'TICK_US' if namespace == 'same' else 'config::TICK_US'
                # The helper's constexpr anchor and the canonical constant are const lvalues.
                initializer = '&extra_anchor' if pointer else 'extra_anchor'
                operand = '&' + read if pointer else read
                extra = head + ' (TICK_US) = ' + initializer + ';'
                with self.subTest(head=head, namespace=namespace, extra=extra):
                    self.check_source(extra_declaration(original, extra, namespace), False)
                controls = (head + ' (derived) = (' + operand + ');',
                            head + ' derived((' + operand + '));')
                for declaration in controls:
                    with self.subTest(head=head, namespace=namespace, read=declaration):
                        self.check_source(extra_declaration(original, declaration, namespace), True)
        for extra, control in GROUPED_DECLARATORS:
            for namespace in ('same', 'other'):
                read = 'TICK_US' if namespace == 'same' else 'config::TICK_US'
                with self.subTest(namespace=namespace, grouped_extra=extra):
                    self.check_source(extra_declaration(original, extra, namespace), False)
                declaration = control.format(read=read)
                with self.subTest(namespace=namespace, grouped_read=declaration):
                    self.check_source(extra_declaration(original, declaration, namespace), True)
