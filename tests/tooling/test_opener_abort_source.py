# Checks D136's bounded cohort schema and exact historical configuration admission.
# Prevents current-checkout defaults, preprocessing or partial source binding from qualifying data.
# Deferred public API cases supply independent snapshots and preserve validator observations.
import builtins
import copy
import io
import json
import os
from pathlib import Path
from unittest import mock
from opener_abort_fixture import AbortAnalysisCase, Bundle, Source, VALUES, ENDPOINTS, ROOT, sha


class OpenerAbortSourceTests(AbortAnalysisCase):
    def source_invalid(self, report, extracted=None):
        self.assertEqual((report['input_status'], report['evidence_status'], report['timing_status']),
                         ('VALID', 'INVALID', 'NOT_QUALIFIED'), report)
        self.assertEqual(report['source']['binding_status'], 'INVALID')
        if extracted is not None:
            self.assertEqual(report['source']['config_values'], self.source.values if extracted else None)
        for name in ('qualified_attempts', 'passing_attempts', 'logical_failures'):
            self.assertEqual(report[name], 0)
        for name in ('minimum_elapsed_us', 'maximum_elapsed_us'):
            self.assertIsNone(report[name])
        for attempt in report['attempts']:
            self.assertEqual((attempt['qualification'], attempt['binding_status'], attempt['trace_status']),
                             ('INVALID', 'INVALID', 'INVALID'))
            self.assertEqual((attempt['logical_status'], attempt['timing_status']), ('NOT_EVALUATED', 'NOT_EVALUATED'))
            for field in ENDPOINTS + ('motors_allowed', 'cue', 'handover_state', 'terminal_detail', 'terminal_value'):
                self.assertIsNone(attempt[field])
        self.assertTrue(report['errors'])
        return report

    def unsupported(self, raw):
        self.source.write(raw)
        report = self.source_invalid(self.analyze([]))
        self.assertIn('UNSUPPORTED_CONFIGURATION', [error['code'] for error in report['errors']])
        return report

    def test_D136_exact_cohort_source_and_attempt_keys_reject_missing_and_unknown_keys(self):
        bundle = Bundle(self.directory, self.source)
        for section in ('cohort', 'source', 'attempt'):
            original = self.document([bundle])
            parent = original if section == 'cohort' else original['source'] if section == 'source' else original['attempts'][0]
            for field in list(parent) + ['unknown']:
                document = copy.deepcopy(original)
                target = document if section == 'cohort' else document['source'] if section == 'source' else document['attempts'][0]
                if field == 'unknown':
                    target[field] = 0
                else:
                    del target[field]
                self.invalid_input(document)

    def test_D136_mode_schema_version_and_attempt_container_reject_bool_float_and_bad_ranges(self):
        for field, invalid in (('mode', (0, 7, True, False, 3.0, '3', None)),
                               ('schema_version', (0, 2, True, 1.0, '1', None)),
                               ('attempts', ({}, None, 'x', 10))):
            for value in invalid:
                document = self.document()
                document[field] = value
                self.invalid_input(document)

    def test_D136_source_identity_strings_have_exact_lowercase_hex_lengths(self):
        for field, lengths in (('firmware_revision', (40, 64)), ('source_sha256', (64,)), ('config_sha256', (64,))):
            for invalid in (None, True, 1, '', 'A' * lengths[0], 'g' * lengths[0], 'a' * (lengths[0] - 1), 'a' * 65):
                document = self.document()
                document['source'][field] = invalid
                self.invalid_input(document)
        document = self.document()
        document['source']['firmware_revision'] = 'd' * 64
        report = self.analyze(document=document)
        self.assertEqual(report['source']['binding_status'], 'DECLARED_MATCH')

    def test_D136_only_exact_two_flags_strings_are_admitted(self):
        exact = self.source.descriptor()['flags']
        for flags in ('', None, True, exact + ' ', ' ' + exact, exact.replace(' ', '  '),
                      '-DMOTORS_ALLOWED=1 -DMATCH=0 -DSUMOX_P5_ABORT_TIMING=1',
                      exact.replace('MATCH=0', 'MATCH=1'), exact.replace('MOTORS_ALLOWED=1', 'MOTORS_ALLOWED=2'),
                      exact + ' -DSUMOX_P4_REACTIVE=0', exact.replace(' -DSUMOX_P5_ABORT_TIMING=1', '')):
            document = self.document()
            document['source']['flags'] = flags
            self.invalid_input(document)
        for motors in (False, True):
            self.source = Source(self.directory, motors=motors)
            report = self.analyze([])
            self.assertEqual(report['source']['flags'], self.source.descriptor()['flags'])

    def test_D136_ids_are_unique_bounded_ASCII_and_every_attempt_is_retained(self):
        bundle = Bundle(self.directory, self.source)
        for invalid in ('', 'a' * 97, 'a b', 'é', 'a/b', 'a\\b', True, 1, None, '\n'):
            document = self.document([bundle])
            document['attempts'][0]['id'] = invalid
            self.invalid_input(document)
        document = self.document([bundle])
        document['attempts'].append(copy.deepcopy(document['attempts'][0]))
        self.invalid_input(document)
        for valid in ('A_z-9.0', 'a' * 96):
            document = self.document([bundle])
            document['attempts'][0]['id'] = valid
            self.assertEqual(self.analyze(document=document)['attempts'][0]['id'], valid)

    def test_D136_duplicate_JSON_keys_at_every_level_and_invalid_JSON_roots_fail(self):
        original = json.dumps(self.document())
        texts = ['[]', 'null', 'true', '0', '{', original.replace('"mode": 3', '"mode": 3, "mode": 3'),
                 original.replace('"source_sha256":', '"source_sha256": "' + 'b' * 64 + '", "source_sha256":'),
                 original.replace('"mode": 3', '"mode": NaN'), original.replace('"mode": 3', '"mode": Infinity')]
        bundle = Bundle(self.directory, self.source)
        texts.append(json.dumps(self.document([bundle])).replace('"id":', '"id": "duplicate", "id":'))
        for text in texts:
            self.path.write_text(text, encoding='ascii')
            self.invalid_input()
        self.path.write_bytes(b'\xff')
        self.invalid_input()

    def test_D136_declared_path_types_empty_and_length_are_schema_errors(self):
        bundle = Bundle(self.directory, self.source)
        for role in ('config', 'frames', 'events', 'summary', 'manifest'):
            for invalid in ('', 'x' * 4097, True, 1, [], None):
                if role == 'manifest' and invalid is None:
                    continue
                document = self.document([bundle])
                target = document['source'] if role == 'config' else document['attempts'][0]
                target[role] = invalid
                self.invalid_input(document)

    def test_D136_local_parent_relative_and_absolute_paths_resolve_from_cohort_directory(self):
        bundle = Bundle(self.directory, self.source)
        nested = self.directory / 'nested'
        nested.mkdir()
        self.path = nested / 'cohort.json'
        document = self.document([bundle])
        document['source']['config'] = '../' + self.source.path.name
        for role in ('frames', 'events', 'summary', 'manifest'):
            document['attempts'][0][role] = '../' + document['attempts'][0][role]
        self.assertEqual(self.analyze(document=document)['attempts'][0]['qualification'], 'QUALIFIED')
        document['source']['config'] = str(self.source.path)
        for role, path in bundle.paths.items():
            document['attempts'][0][role] = str(path)
        document['attempts'][0]['manifest'] = str(bundle.manifest_path)
        self.assertEqual(self.analyze(document=document)['attempts'][0]['qualification'], 'QUALIFIED')

    def test_D136_network_paths_are_rejected_before_any_declared_file_access(self):
        bundle = Bundle(self.directory, self.source)
        forbidden = {path.name for path in bundle.paths.values()} | {bundle.manifest_path.name, self.source.path.name}
        original = builtins.open

        def opening(file, *args, **kwargs):
            if isinstance(file, (str, bytes, os.PathLike)):
                text = os.fsdecode(file)
                if Path(text).name in forbidden or text.startswith(('//', '\\\\', 'https:', 'smb:', 'file:')):
                    self.fail('Schema-invalid paths must fail before declared-file access: ' + text)
            return original(file, *args, **kwargs)

        for role in ('config', 'frames', 'events', 'summary', 'manifest'):
            for path in ('//server/share/x', '\\\\server\\share\\x', 'https://example.invalid/x', 'smb://server/x', 'file:///tmp/x'):
                document = self.document([bundle])
                target = document['source'] if role == 'config' else document['attempts'][0]
                target[role] = path
                self.write_cohort(document=document)
                with mock.patch('builtins.open', opening), mock.patch('io.open', opening):
                    self.invalid_input()

    def test_D136_cohort_bounded_regular_nonsymlink_reads_accept_exact_limit_only(self):
        raw = json.dumps(self.document()).encode()
        self.path.write_bytes(raw + b' ' * (256 * 1024 - len(raw)))
        self.assertEqual(self.analyze()['input_status'], 'VALID')
        self.path.write_bytes(self.path.read_bytes() + b' ')
        self.invalid_input()
        for path in (self.directory, self.directory / 'missing.json'):
            original, self.path = self.path, path
            self.invalid_input()
            self.path = original
        self.write_cohort([])
        link = self.directory / 'link.json'
        link.symlink_to(self.path)
        self.path = link
        self.invalid_input()

    def test_D136_current_canonical_header_is_an_explicit_snapshot_not_an_implicit_default(self):
        self.source.write((ROOT / 'src/config.h').read_bytes())
        report = self.analyze([])
        self.assertEqual(report['source']['config_values'], VALUES)
        self.assertEqual(report['source']['config_sha256'], sha(self.source.path.read_bytes()))
        self.assertEqual(report['source']['binding_status'], 'DECLARED_MATCH')

    def test_D136_ordinary_constant_reads_comments_quotes_whitespace_and_lowercase_u_are_supported(self):
        raw = self.source.canonical()
        for accepted in (raw.replace(b'U;', b'u;'), raw.replace(b' = ', b'\t=\n'),
                         b'#if 0\nint unrelated;\n#endif\n' + raw,
                         raw + b'constexpr auto derived = LOG_HZ * LOG_FRAME_WINDOW_MS;\n',
                         b'// TICK_US = 9U;\n/* MODE_ARC_ENABLED */\n' + raw,
                         b'const char* text = "TICK_US MODE_ARC_ENABLED";\n' + raw,
                         b'const char* fake = "inline constexpr std::uint32_t TICK_US = 9U;";\n' + raw):
            self.source.write(accepted)
            report = self.analyze([])
            self.assertEqual(report['source']['config_values'], VALUES)
            self.assertEqual(report['source']['binding_status'], 'DECLARED_MATCH')

    def test_D136_each_literal_is_required_unique_unconditional_and_not_a_macro(self):
        original = self.source.canonical()
        for name, value in VALUES.items():
            declaration = ('inline constexpr std::uint32_t ' + name + ' = ' + str(value) + 'U;\n').encode()
            variants = (original.replace(declaration, b''), original + declaration,
                        original.replace(declaration, b'#if 1\n' + declaration + b'#endif\n'),
                        original + ('#define ' + name + ' 1\n').encode(),
                        ('#if ' + name + '\n#endif\n').encode() + original,
                        original.replace(declaration, b'const char* fake = "' + declaration.rstrip(b'\n') + b'";\n'))
            for raw in variants:
                with self.subTest(name=name, raw=raw):
                    self.unsupported(raw)

    def test_D136_source_literal_grammar_rejects_expressions_suffixes_aliases_and_huge_values(self):
        original = self.source.canonical()
        for literal in ('01000U', '+1000U', '-1000U', '1000', '1000UL', '1000 U', '1\'000U',
                        '0x3e8U', '(1000U)', '500U+500U', '1000.0U', '4294967296U', '9' * 10000 + 'U'):
            self.unsupported(original.replace(b'1000U;', literal.encode() + b';', 1))
        for prefix in (b'constexpr uint32_t', b'static constexpr std::uint32_t', b'inline const std::uint32_t'):
            self.unsupported(original.replace(b'inline constexpr std::uint32_t TICK_US', prefix + b' TICK_US'))

    def test_D136_physical_splices_digraph_directives_and_unterminated_lexical_constructs_reject(self):
        original = self.source.canonical()
        for prefix in (b'// hidden\\\n', b'// hidden\\ \r\n', b'"hidden\\\n"\n',
                       b'#if 1\\\n\n#endif\n', b'/*', b'"unterminated\n', b"'unterminated\n",
                       b'%:if 0\n', b' /* ignored */ %:if 1\n'):
            self.unsupported(prefix + original)
        for prefix in (b'// %:if 0\n', b'/* %:if 0 */\n', b'const char* quoted = "%:if 0";\n'):
            self.source.write(prefix + original)
            self.assertEqual(self.analyze([])['source']['binding_status'], 'DECLARED_MATCH')

    def test_D136_value_ranges_and_fixed_profile_identity_are_independently_enforced(self):
        invalid = dict(TICK_US=(0, 2147483648), ATTACK_ENTER_TICKS=(0, 4294967296),
                       MODE_ARC_ENABLED=(2, 4294967295), MODE_WAIT_ENABLED=(2, 4294967295),
                       LOG_HZ=(0, 50), LOG_EVENT_CAPACITY=(4095, 4097), LOG_FRAME_WINDOW_MS=(199999, 200001))
        for name, values in invalid.items():
            for value in values:
                self.source = Source(self.directory, **{name: value})
                self.source_invalid(self.analyze([]))
        for tick, threshold in ((1, 1), (2147483647, 4294967295)):
            self.source = Source(self.directory, TICK_US=tick, ATTACK_ENTER_TICKS=threshold)
            self.assertEqual(self.analyze([])['source']['config_values'], self.source.values)

    def test_D136_all_four_availability_configs_respect_historical_mode_ids(self):
        for arc, wait in ((0, 0), (0, 1), (1, 0), (1, 1)):
            self.source = Source(self.directory, MODE_ARC_ENABLED=arc, MODE_WAIT_ENABLED=wait)
            for mode in range(1, 7):
                report = self.analyze([], mode=mode)
                self.assertEqual(report['mode'], mode)
                self.assertEqual(report['source']['config_values'], self.source.values)
                if mode in (4, 5) and not arc or mode == 6 and not wait:
                    self.source_invalid(report, extracted=True)
                else:
                    self.assertEqual(report['source']['binding_status'], 'DECLARED_MATCH')

    def test_D136_bad_config_hash_never_decodes_attempts_but_validates_every_bundle(self):
        bundles = self.ten()[:3]
        bundles[1].paths['events'].write_bytes(b'broken\n')
        document = self.document(bundles)
        document['source']['config_sha256'] = '0' * 64
        self.write_cohort(document=document)
        self.source_invalid(self.validated_then(lambda accepted: None, expected_calls=3), extracted=False)

    def test_D136_config_read_failures_and_exact_size_limit_are_source_invalid_even_for_empty_cohort(self):
        original = self.source.canonical()
        for kind in ('missing', 'directory', 'symlink', 'oversized'):
            self.source.write(original)
            document = self.document()
            self.source.path.unlink()
            if kind == 'directory':
                self.source.path.mkdir()
            elif kind == 'symlink':
                target = self.directory / 'target.h'
                target.write_bytes(original)
                self.source.path.symlink_to(target)
            elif kind == 'oversized':
                self.source.path.write_bytes(original + b' ' * (256 * 1024 + 1 - len(original)))
                document['source']['config_sha256'] = sha(self.source.path.read_bytes())
            self.source_invalid(self.analyze(document=document), extracted=False)
            if kind == 'directory':
                self.source.path.rmdir()
            elif self.source.path.exists() or self.source.path.is_symlink():
                self.source.path.unlink()
        self.source.write(original + b' ' * (256 * 1024 - len(original)))
        self.assertEqual(self.analyze([])['source']['config_values'], VALUES)

    def test_D136_unsupported_source_never_falls_back_to_live_repository_config(self):
        self.source.write(self.source.canonical().replace(b'inline constexpr std::uint32_t TICK_US = 1000U;\n', b''))
        self.write_cohort([])
        original = builtins.open

        def opening(file, *args, **kwargs):
            if isinstance(file, (str, bytes, os.PathLike)) and Path(os.fsdecode(file)).resolve() == ROOT / 'src/config.h':
                self.fail('Analyzer must not consult current checkout configuration')
            return original(file, *args, **kwargs)

        with mock.patch('builtins.open', opening), mock.patch('io.open', opening):
            self.source_invalid(self.analyze(), extracted=False)
