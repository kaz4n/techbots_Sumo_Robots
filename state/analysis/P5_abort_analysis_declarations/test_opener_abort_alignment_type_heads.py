# Checks D136 ordinary alignment reads and extra parenthesized integer declarations.
# Keeps valid read expressions distinct from unsupported declarations of a reserved name.
# Two independent spec-derived matrices are hashed before execution; prior tests stay exact.
from pathlib import Path
import sys

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / 'AGENTS.md').is_file())
FIXTURES = str(ROOT / 'tests/tooling')
if FIXTURES not in sys.path:
    sys.path.insert(0, FIXTURES)
from opener_abort_fixture import AbortAnalysisCase, VALUES
from test_opener_abort_declarations import extra_declaration


INTEGER_HEADS = (
    'short', 'short int', 'signed short', 'signed short int',
    'unsigned short', 'unsigned short int', 'int', 'signed', 'signed int',
    'unsigned', 'unsigned int', 'long', 'long int', 'signed long', 'signed long int',
    'unsigned long', 'unsigned long int', 'long long', 'long long int',
    'signed long long', 'signed long long int', 'unsigned long long', 'unsigned long long int',
)


class OpenerAbortAlignmentTypeHeadTests(AbortAnalysisCase):
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

    def test_D136_unconditional_alignas_constant_reads_are_allowed_with_valid_byte_alignment(self):
        original = self.source.canonical()
        # Both constants are1 in this historical snapshot; unsigned char needs only1.
        for name in ('MODE_ARC_ENABLED', 'MODE_WAIT_ENABLED'):
            self.assertEqual(self.source.values[name], 1)
            for namespace in ('same', 'other'):
                read = name if namespace == 'same' else 'config::' + name
                for expression in (read, '(' + read + ')'):
                    for declaration in (
                            'alignas(' + expression + ') unsigned char derived = 0U;',
                            'alignas(' + expression + ') inline constexpr unsigned char (derived) = 0U;'):
                        with self.subTest(name=name, namespace=namespace, declaration=declaration):
                            self.check_source(extra_declaration(original, declaration, namespace), True)

    def test_D136_integer_type_heads_const_and_references_reject_extra_names_but_allow_read_initializers(self):
        original = self.source.canonical()
        for head in INTEGER_HEADS:
            for namespace in ('same', 'other'):
                read = 'TICK_US' if namespace == 'same' else 'config::TICK_US'
                # 2000 fits every listed integer type; const-reference temporaries are valid.
                extras = (head + ' (TICK_US) = 2000U;',
                          'const ' + head + ' (TICK_US) = 2000U;',
                          'const ' + head + ' &(TICK_US) = 2000U;',
                          'const ' + head + ' (&TICK_US) = 2000U;')
                for declaration in extras:
                    with self.subTest(head=head, namespace=namespace, extra=declaration):
                        self.check_source(extra_declaration(original, declaration, namespace), False)
                controls = (head + ' derived((' + read + '));',
                            'const ' + head + ' (derived) = (' + read + ');',
                            'const ' + head + ' (&derived) = (' + read + ');')
                for declaration in controls:
                    with self.subTest(head=head, namespace=namespace, read=declaration):
                        self.check_source(extra_declaration(original, declaration, namespace), True)
