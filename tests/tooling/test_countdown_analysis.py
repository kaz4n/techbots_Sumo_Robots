# Checks P3.1/D127 arithmetic and evidence qualification through public APIs only.
# Prevents incomplete or changed local records from becoming physical countdown proof.
# Independent synthetic fixtures cover CLI, snapshots, event semantics and boundaries.
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import builtins
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock

from countdown_analysis_fixture import BoundedReader, Bundle, CLEAN_FRAME, HOLD, ROOT, U32, cohort, wire


TOOL = ROOT / 'tools/analyze_countdown.py'
TOOLS = str(ROOT / 'tools')
REPORT_KEYS = {'schema_version', 'input_status', 'evidence_status', 'timing_status',
               'required_attempts', 'required_hold_us', 'spread_limit_us',
               'qualified_attempts', 'minimum_delay_us', 'maximum_delay_us', 'spread_us',
               'attempts', 'errors', 'common_attempt_verified', 'transport_verified',
               'hardware_acceptance'}
ATTEMPT_KEYS = {'id', 'qualification', 'release_us', 'go_delay_us', 'first_delay_us',
                'hold_status', 'errors', 'validation'}


def load_analyzer():
    # Import only for later test execution; no implementation source inspection.
    spec = importlib.util.spec_from_file_location('d127_public_analyzer', TOOL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CountdownAnalysisContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, TOOLS)
        cls.addClassCleanup(lambda: sys.path.remove(TOOLS))
        cls.validator = importlib.import_module('validate_csv_bundle')
        cls.module = load_analyzer()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='sumo-countdown-oracle-')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.path = self.directory / 'cohort.json'

    def write_cohort(self, bundles=(), document=None):
        value = cohort(bundles) if document is None else document
        self.path.write_text(json.dumps(value), encoding='ascii')
        return self.path

    def analyze(self, bundles=None, document=None, module=None):
        if bundles is not None or document is not None:
            self.write_cohort(() if bundles is None else bundles, document)
        report = (module or self.module).analyze_cohort(self.path)
        self.assert_report(report)
        return report

    def assert_report(self, report):
        self.assertTrue(REPORT_KEYS <= report.keys())
        self.assertEqual(report['schema_version'], 1)
        self.assertEqual(report['required_attempts'], 50)
        self.assertEqual(report['required_hold_us'], HOLD)
        self.assertEqual(report['spread_limit_us'], 5000)
        self.assertIn(report['input_status'], ('VALID', 'INVALID'))
        self.assertIn(report['evidence_status'], ('COMPLETE', 'INCOMPLETE', 'INVALID'))
        self.assertIn(report['timing_status'], ('PASS', 'FAIL', 'NOT_QUALIFIED'))
        for key in ('common_attempt_verified', 'transport_verified', 'hardware_acceptance'):
            self.assertIs(report[key], False)
        self.assert_errors(report['errors'])
        for attempt in report['attempts']:
            self.assertTrue(ATTEMPT_KEYS <= attempt.keys())
            self.assertIn(attempt['qualification'], ('QUALIFIED', 'INCOMPLETE', 'INVALID'))
            self.assertIn(attempt['hold_status'], ('PASS', 'FAIL', 'NOT_EVALUATED'))
            self.assert_errors(attempt['errors'])

    def assert_errors(self, errors):
        self.assertIsInstance(errors, list)
        for error in errors:
            self.assertTrue({'code', 'message'} <= error.keys())
            self.assertIsInstance(error['code'], str)
            self.assertTrue(error['code'])
            self.assertIsInstance(error['message'], str)
            self.assertTrue(error['message'].strip())

    def one(self, bundle, qualification='QUALIFIED'):
        report = self.analyze([bundle])
        self.assertEqual(report['input_status'], 'VALID')
        self.assertEqual(len(report['attempts']), 1)
        attempt = report['attempts'][0]
        self.assertEqual(attempt['id'], bundle.id)
        self.assertEqual(attempt['qualification'], qualification, attempt)
        self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
        self.assertEqual(report['evidence_status'],
                         'INVALID' if qualification == 'INVALID' else 'INCOMPLETE')
        self.assertEqual(report['qualified_attempts'], int(qualification == 'QUALIFIED'))
        return report, attempt

    def invalid_input(self, document=None):
        result = self.analyze(document=document) if document is not None else self.analyze()
        self.assertEqual(result['input_status'], 'INVALID', result)
        self.assertEqual(result['timing_status'], 'NOT_QUALIFIED')
        self.assertTrue(result['errors'])
        return result

    def cohort50(self, delays=None):
        delays = [HOLD] * 50 if delays is None else delays
        return [Bundle(self.directory, index, delay) for index, delay in enumerate(delays)]

    def validated_then(self, action):
        module = load_analyzer()
        validator_path = (ROOT / 'tools/validate_csv_bundle.py').resolve()
        dependencies = [value for value in vars(module).values()
                        if isinstance(value, ModuleType)
                        and callable(getattr(value, 'validate_bundle', None))
                        and isinstance(getattr(value, '__file__', None), str)
                        and Path(value.__file__).resolve() == validator_path]
        self.assertEqual(len(dependencies), 1, 'Exactly one actual public validator dependency')
        validator = dependencies[0]
        original = validator.validate_bundle
        injected = []

        def boundary(*args, **kwargs):
            accepted = original(*args, **kwargs)
            self.assertEqual(accepted['format_integrity'], 'PASS', accepted)
            self.assertEqual(accepted['consistency'], 'PASS', accepted)
            injected.append(True)
            action(accepted)
            return accepted

        with mock.patch.object(validator, 'validate_bundle', boundary):
            result = self.analyze(module=module)
        self.assertEqual(len(injected), 1, 'Actual validator boundary must inject exactly once')
        return result

    def test_B3_fifty_distinct_synthetic_attempts_pass_exact_hold_with_explicit_limits(self):
        bundles = self.cohort50()
        report = self.analyze(bundles)
        self.assertEqual(report['input_status'], 'VALID')
        self.assertEqual(report['evidence_status'], 'COMPLETE')
        self.assertEqual(report['timing_status'], 'PASS')
        self.assertEqual(report['qualified_attempts'], 50)
        self.assertEqual((report['minimum_delay_us'], report['maximum_delay_us'],
                          report['spread_us']), (HOLD, HOLD, 0))
        self.assertEqual([a['id'] for a in report['attempts']], [b.id for b in bundles])
        for attempt in report['attempts']:
            self.assertEqual(attempt['qualification'], 'QUALIFIED')
            self.assertEqual(attempt['hold_status'], 'PASS')
            self.assertEqual(attempt['first_delay_us'], HOLD)
            self.assertEqual(attempt['validation']['provenance']['evidence_kind'], 'SYNTHETIC')

    def test_B3_every_delay_and_strict_spread_boundary_control_only_complete_cohorts(self):
        cases = [([HOLD - 1] + [HOLD] * 49, 'FAIL', 1),
                 ([HOLD] * 49 + [HOLD + 4999], 'PASS', 4999),
                 ([HOLD] * 49 + [HOLD + 5000], 'FAIL', 5000),
                 ([HOLD] * 49 + [HOLD + 5001], 'FAIL', 5001),
                 ([HOLD + 8000] * 50, 'PASS', 0)]
        for delays, status, spread in cases:
            with self.subTest(status=status, spread=spread, minimum=min(delays)):
                report = self.analyze(self.cohort50(delays))
                self.assertEqual(report['evidence_status'], 'COMPLETE')
                self.assertEqual(report['qualified_attempts'], 50)
                self.assertEqual(report['timing_status'], status)
                self.assertEqual(report['minimum_delay_us'], min(delays))
                self.assertEqual(report['maximum_delay_us'], max(delays))
                self.assertEqual(report['spread_us'], spread)

    def test_B3_empty_and_49_attempts_cannot_qualify_or_discard_observations(self):
        empty = self.analyze([])
        self.assertEqual(empty['input_status'], 'VALID')
        self.assertEqual(empty['evidence_status'], 'INCOMPLETE')
        self.assertEqual(empty['timing_status'], 'NOT_QUALIFIED')
        self.assertEqual(empty['qualified_attempts'], 0)
        self.assertEqual(empty['attempts'], [])
        for key in ('minimum_delay_us', 'maximum_delay_us', 'spread_us'):
            self.assertIsNone(empty[key])
        report = self.analyze(self.cohort50()[:49])
        self.assertEqual(len(report['attempts']), 49)
        self.assertEqual(report['qualified_attempts'], 49)
        self.assertEqual(report['evidence_status'], 'INCOMPLETE')
        self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
        self.assertEqual(report['minimum_delay_us'], HOLD)

    def test_B3_wrap_zero_timestamps_equal_markers_and_all_six_modes(self):
        for release in (0, U32 - HOLD + 1, U32 - 100):
            for mode in range(1, 7):
                with self.subTest(release=release, mode=mode):
                    bundle = Bundle(self.directory, release=release, mode=mode)
                    _, attempt = self.one(bundle)
                    self.assertEqual(attempt['release_us'], release)
                    self.assertEqual(attempt['go_delay_us'], HOLD)
                    self.assertEqual(attempt['first_delay_us'], HOLD)
                    self.assertEqual(attempt['hold_status'], 'PASS')
        bundle = Bundle(self.directory, delay=0, release=0)
        _, attempt = self.one(bundle)
        self.assertEqual(attempt['first_delay_us'], 0)
        self.assertEqual(attempt['go_delay_us'], 0)
        self.assertEqual(attempt['hold_status'], 'FAIL')

    def test_B3_chronology_ambiguity_never_creates_an_early_delay_conclusion(self):
        for go, first in ((0x80000000, 0x80000000), (HOLD, 0x80000000),
                          (U32, 0), (HOLD + 1, HOLD)):
            with self.subTest(go=go, first=first):
                bundle = Bundle(self.directory, release=123)
                bundle.events[1]['t_us'] = (123 + go) & U32
                bundle.events[2]['t_us'] = (123 + first) & U32
                _, attempt = self.one(bundle.write(), 'INCOMPLETE')
                self.assertEqual(attempt['release_us'], 123)
                self.assertIsNone(attempt['go_delay_us'])
                self.assertIsNone(attempt['first_delay_us'])
                self.assertEqual(attempt['hold_status'], 'NOT_EVALUATED')
        _, below = self.one(Bundle(self.directory, release=123, delay=0x7fffffff))
        self.assertEqual(below['first_delay_us'], 0x7fffffff)

    def test_B3_missing_each_marker_and_GO_alone_preserve_only_available_diagnostics(self):
        for missing in (0, 1, 2):
            bundle = Bundle(self.directory, delay=HOLD - 1)
            bundle.events = [event for event in bundle.events if event['kind'] != missing]
            _, attempt = self.one(bundle.write(), 'INCOMPLETE')
            if missing == 1:
                self.assertEqual(attempt['first_delay_us'], HOLD - 1)
                self.assertEqual(attempt['hold_status'], 'FAIL')
                self.assertIsNone(attempt['go_delay_us'])
            else:
                self.assertIsNone(attempt['first_delay_us'])
                self.assertEqual(attempt['hold_status'], 'NOT_EVALUATED')

    def test_B3_frames_and_GO_never_substitute_for_receipt_FIRST(self):
        bundle = Bundle(self.directory)
        bundle.events.pop()
        values = CLEAN_FRAME.copy()
        values[9] = values[10] = 127
        bundle.frames = [wire.frame(values, ordinal=0)]
        _, attempt = self.one(bundle.write(), 'INCOMPLETE')
        self.assertIsNone(attempt['first_delay_us'])
        self.assertEqual(attempt['hold_status'], 'NOT_EVALUATED')
        bundle = Bundle(self.directory)
        bundle.events[1]['t_us'] = bundle.summary['release_us'] + 1
        _, attempt = self.one(bundle.write())
        self.assertEqual(attempt['go_delay_us'], 1)
        self.assertEqual(attempt['first_delay_us'], HOLD)
        self.assertEqual(attempt['hold_status'], 'PASS')

    def test_B15_marker_duplicates_wrong_order_and_all_ordinal_regressions_are_invalid(self):
        for kind in range(3):
            bundle = Bundle(self.directory)
            duplicate = dict(bundle.events[kind], ordinal=3)
            bundle.events.append(duplicate)
            self.one(bundle.write(), 'INVALID')
        for order in ((1, 0, 2), (0, 2, 1), (2, 1, 0)):
            bundle = Bundle(self.directory)
            bundle.events = [dict(bundle.events[kind], ordinal=index)
                             for index, kind in enumerate(order)]
            self.one(bundle.write(), 'INVALID')
        for ordinal in (0, 1, 2):
            bundle = Bundle(self.directory)
            bundle.events.append(dict(t_us=1, ordinal=ordinal, kind=254, detail=255, value=65535))
            self.one(bundle.write(), 'INVALID')

    def test_B15_irrelevant_types_and_sparse_increasing_ordinals_do_not_become_markers(self):
        bundle = Bundle(self.directory)
        for event, ordinal in zip(bundle.events, (5, 100, (1 << 64) - 2)):
            event['ordinal'] = ordinal
        bundle.events.append(dict(t_us=0, ordinal=(1 << 64) - 1, kind=254, detail=255, value=65535))
        _, attempt = self.one(bundle.write())
        self.assertEqual(attempt['first_delay_us'], HOLD)

    def test_B15_START_GO_modes_values_and_release_identity_must_match_owner(self):
        for marker in (0, 1):
            for field, value in (('detail', 0), ('detail', 7), ('detail', 2), ('value', 1)):
                with self.subTest(marker=marker, field=field, value=value):
                    bundle = Bundle(self.directory)
                    bundle.events[marker][field] = value
                    self.one(bundle.write(), 'INVALID')
        bundle = Bundle(self.directory)
        bundle.summary['release_us'] += 1
        self.one(bundle.write(), 'INVALID')

    def test_B15_FIRST_signed_bytes_wheel_presence_and_tiny_nonzero_quantization(self):
        for detail, value in ((1, 0), (2, 0), (3, 0), (1, 0x007f),
                              (1, 0x00ff), (2, 0x8100), (3, 0x817f)):
            with self.subTest(detail=detail, value=value):
                bundle = Bundle(self.directory)
                bundle.events[2].update(detail=detail, value=value)
                _, attempt = self.one(bundle.write())
                self.assertEqual(attempt['first_delay_us'], HOLD)
        for detail, value in ((0, 0), (4, 0), (255, 0), (1, 0x0100),
                              (2, 0x0001), (1, 0x0080), (2, 0x8000), (3, 0x8080)):
            with self.subTest(invalid_detail=detail, value=value):
                bundle = Bundle(self.directory)
                bundle.events[2].update(detail=detail, value=value)
                self.one(bundle.write(), 'INVALID')

    def test_B15_every_reported_loss_preserves_early_interval_but_excludes_qualification(self):
        for field in wire.LOSS_FIELDS:
            with self.subTest(field=field):
                bundle = Bundle(self.directory, delay=HOLD - 1)
                bundle.summary.update({field: 1, 'incomplete': 1})
                if field in ('frame_clamped', 'frame_invalid'):
                    status = 1 if field == 'frame_clamped' else 2
                    bundle.frames = [wire.frame(CLEAN_FRAME, ordinal=0, status=status)]
                report, attempt = self.one(bundle.write(), 'INCOMPLETE')
                self.assertEqual(attempt['validation']['recording']['loss'], 'REPORTED')
                self.assertEqual(attempt['first_delay_us'], HOLD - 1)
                self.assertEqual(attempt['hold_status'], 'FAIL')
                self.assertIsNone(report['minimum_delay_us'])

    def test_B15_unfinished_unknown_and_interrupted_owner_phases_cannot_qualify(self):
        for phase in (0, 1, 2, 4, 255):
            bundle = Bundle(self.directory)
            bundle.summary['phase'] = phase
            _, attempt = self.one(bundle.write(), 'INCOMPLETE')
            self.assertEqual(attempt['first_delay_us'], HOLD)
        for field in ('go_seen', 'epoch_token'):
            bundle = Bundle(self.directory)
            bundle.summary[field] = 0
            self.one(bundle.write(), 'INVALID')

    def test_B15_absent_open_unknown_closure_keeps_early_timing_diagnostic(self):
        for closure in (None, 'open', 'unknown'):
            bundle = Bundle(self.directory, delay=HOLD - 1)
            if closure is None:
                bundle.manifest_present = False
            else:
                bundle.declarations['closure'] = closure
            _, attempt = self.one(bundle.write(), 'INCOMPLETE')
            self.assertEqual(attempt['first_delay_us'], HOLD - 1)
            self.assertEqual(attempt['hold_status'], 'FAIL')

    def test_B15_partial_or_hardware_declared_provenance_never_becomes_verified_origin(self):
        bundle = Bundle(self.directory)
        bundle.declarations = dict(origin='hardware_reported')
        _, attempt = self.one(bundle.write())
        self.assertEqual(attempt['validation']['provenance']['evidence_kind'], 'HARDWARE_REPORTED')
        for key in ('session_id', 'origin', 'firmware_revision', 'source_sha256', 'config_sha256',
                    'log_hz', 'frame_capacity', 'event_capacity', 'target'):
            bundle.declarations[key] = None
        _, attempt = self.one(bundle.write())
        self.assertEqual(attempt['validation']['provenance']['status'], 'PARTIAL_DECLARATION')
        self.assertEqual(attempt['validation']['provenance']['closure'], 'DECLARED_CLOSED')

    def test_B15_validator_report_is_unchanged_and_format_consistency_manifest_fail_separately(self):
        for failure in ('none', 'format', 'consistency', 'manifest'):
            bundle = Bundle(self.directory)
            if failure == 'format':
                bundle.paths['frames'].write_bytes(b'broken\n')
            if failure == 'consistency':
                bundle.summary['event_count'] = 99
                bundle.write()
            if failure == 'manifest':
                declared = bundle.manifest()
                declared['files']['events']['sha256'] = '0' * 64
                bundle.manifest_path.write_text(json.dumps(declared), encoding='ascii')
            expected = self.validator.validate_bundle(*bundle.paths.values(), bundle.manifest_path)
            _, attempt = self.one(bundle, 'QUALIFIED' if failure == 'none' else 'INVALID')
            self.assertEqual(attempt['validation'], expected)

    def test_B15_any_invalid_attempt_invalidates_evidence_but_qualified_stats_remain_exact(self):
        bundles = self.cohort50([HOLD + 20] * 49 + [HOLD - 1])
        bundles[-1].events[2]['detail'] = 0
        bundles[-1].write()
        report = self.analyze(bundles)
        self.assertEqual(report['evidence_status'], 'INVALID')
        self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
        self.assertEqual(report['qualified_attempts'], 49)
        self.assertEqual(len(report['attempts']), 50)
        self.assertEqual((report['minimum_delay_us'], report['maximum_delay_us'],
                          report['spread_us']), (HOLD + 20, HOLD + 20, 0))
        bundles[-1] = Bundle(self.directory, 49, delay=HOLD - 1)
        bundles[-1].declarations['closure'] = 'open'
        bundles[-1].write()
        report = self.analyze(bundles)
        self.assertEqual(report['evidence_status'], 'INCOMPLETE')
        self.assertEqual(report['qualified_attempts'], 49)
        self.assertEqual(report['attempts'][-1]['hold_status'], 'FAIL')
        self.assertEqual(report['minimum_delay_us'], HOLD + 20)

    def test_B15_reused_hash_triples_invalidate_every_alias_not_just_later_entries(self):
        original = Bundle(self.directory)
        other = Bundle(self.directory, 1)
        reused = dict(original.entry(), id='different-id')
        document = cohort([original, other])
        document['attempts'].append(reused)
        report = self.analyze(document=document)
        self.assertEqual([a['qualification'] for a in report['attempts']],
                         ['INVALID', 'QUALIFIED', 'INVALID'])
        self.assertEqual(report['qualified_attempts'], 1)
        self.assertEqual(report['evidence_status'], 'INVALID')
        for role, path in original.paths.items():
            other.paths[role].write_bytes(path.read_bytes())
        other.manifest_path.write_text(json.dumps(other.manifest()), encoding='ascii')
        report = self.analyze([original, other])
        self.assertEqual([a['qualification'] for a in report['attempts']], ['INVALID', 'INVALID'])
        self.assertEqual(report['qualified_attempts'], 0)

    def test_B3_schema_versions_supported_historical_hold_and_strict_integer_types(self):
        for key, values in [('schema_version', (0, 2, True, 1.0, '1', None)),
                            ('countdown_ms', (4999, 5100, True, 5000.0, '5000', None)),
                            ('countdown_margin_ms', (0, 101, False, 100.0, '100', None))]:
            for value in values:
                with self.subTest(key=key, value=value):
                    document = cohort([])
                    document[key] = value
                    self.invalid_input(document)
        for key in cohort([]):
            document = cohort([])
            del document[key]
            self.invalid_input(document)
        self.invalid_input(dict(cohort([]), unexpected=1))
        for attempts in (None, {}, 'attempts', 1, True, [None], [True], [[]]):
            self.invalid_input(dict(cohort([]), attempts=attempts))

    def test_B3_attempt_keys_ids_uniqueness_count_and_path_field_types_are_strict(self):
        bundle = Bundle(self.directory)
        for identifier in ('', 'a' * 97, 'space id', 'é', '../x', 'x/y', 'x\\y', 1, None):
            value = cohort([bundle])
            value['attempts'][0]['id'] = identifier
            self.invalid_input(value)
        for identifier in ('A', 'A_z.9-0', '.', '..', 'a' * 96):
            value = cohort([bundle])
            value['attempts'][0]['id'] = identifier
            result = self.analyze(document=value)
            self.assertEqual(result['input_status'], 'VALID')
        for key in bundle.entry():
            value = cohort([bundle])
            del value['attempts'][0][key]
            self.invalid_input(value)
        value = cohort([bundle]); value['attempts'][0]['extra'] = True
        self.invalid_input(value)
        value = cohort([bundle]); value['attempts'] *= 2
        self.invalid_input(value)
        self.invalid_input(dict(cohort([]), attempts=[dict(bundle.entry(), id=str(i)) for i in range(51)]))
        for role in ('frames', 'events', 'summary', 'manifest'):
            for bad in ('', 'x' * 4097, 1, [], False, None):
                if role == 'manifest' and bad is None:
                    continue
                value = cohort([bundle]); value['attempts'][0][role] = bad
                self.invalid_input(value)

    def test_B3_duplicate_JSON_keys_nonfinite_numbers_wrong_roots_and_malformed_data(self):
        bundle = Bundle(self.directory)
        valid = json.dumps(cohort([bundle]))
        bad_json = ['{', '', '[]', 'null', 'true', '42', '{} {}',
                    valid.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1', 1),
                    valid.replace('"id": "synthetic-0"', '"id": "synthetic-0", "id": "x"', 1)]
        for bad in bad_json:
            self.path.write_text(bad, encoding='ascii')
            self.invalid_input()
        for value in (float('nan'), float('inf'), -float('inf')):
            self.invalid_input(dict(cohort([]), countdown_ms=value))
        self.path.write_bytes(b'\xff')
        self.invalid_input()

    def test_B3_relative_paths_resolve_at_cohort_directory_not_current_working_directory(self):
        bundle = Bundle(self.directory)
        self.write_cohort([bundle])
        previous = Path.cwd()
        try:
            os.chdir(ROOT)
            result = self.module.analyze_cohort(str(self.path))
        finally:
            os.chdir(previous)
        self.assert_report(result)
        self.assertEqual(result['attempts'][0]['qualification'], 'QUALIFIED')
        value = cohort([bundle])
        for role in ('frames', 'events', 'summary'):
            value['attempts'][0][role] = str(bundle.paths[role])
        value['attempts'][0]['manifest'] = str(bundle.manifest_path)
        self.assertEqual(self.analyze(document=value)['attempts'][0]['qualification'], 'QUALIFIED')

    def test_B3_cohort_limit_missing_directory_and_symlink_inputs_fail_explicitly(self):
        raw = json.dumps(cohort([])).encode('ascii')
        self.path.write_bytes(raw + b' ' * (256 * 1024 - len(raw)))
        self.assertEqual(self.analyze()['input_status'], 'VALID')
        self.path.write_bytes(self.path.read_bytes() + b' ')
        self.invalid_input()
        for path in (self.directory, self.directory / 'missing.json'):
            result = self.module.analyze_cohort(path)
            self.assert_report(result)
            self.assertEqual(result['input_status'], 'INVALID')
        self.write_cohort([])
        link = self.directory / 'linked.json'
        try:
            link.symlink_to(self.path)
        except OSError as error:
            self.fail('Symlink coverage requires the POSIX tooling environment: ' + str(error))
        result = self.module.analyze_cohort(link)
        self.assert_report(result)
        self.assertEqual(result['input_status'], 'INVALID')

    def test_B15_changed_postvalidation_event_or_summary_bytes_are_not_new_accepted_evidence(self):
        for role in ('events', 'summary'):
            bundle = Bundle(self.directory)
            self.write_cohort([bundle])
            path = bundle.paths[role]
            old = path.read_bytes()
            identity = path.stat()

            def change(_):
                if role == 'events':
                    bundle.events[2]['t_us'] += 1
                    data = wire.header('events') + b''.join(wire.event(**e) for e in bundle.events)
                else:
                    values = dict(bundle.summary, epoch_token=2, frame_count=0, event_count=3)
                    data = wire.header('summary') + wire.summary(**values)
                self.assertEqual(len(data), len(old))
                path.write_bytes(data)
                os.utime(path, ns=(identity.st_atime_ns, identity.st_mtime_ns))

            result = self.validated_then(change)
            self.assertEqual(result['attempts'][0]['qualification'], 'INVALID')
            self.assertEqual(result['evidence_status'], 'INVALID')

    def test_B15_exact_validator_byte_and_row_counts_are_bound_alongside_hashes(self):
        for role in ('events', 'summary'):
            for field in ('bytes', 'rows'):
                bundle = Bundle(self.directory)
                self.write_cohort([bundle])

                def altered_report(accepted):
                    accepted['files'][role][field] += 1

                result = self.validated_then(altered_report)
                self.assertEqual(result['attempts'][0]['qualification'], 'INVALID')

    def test_B15_manifest_and_frames_are_not_reopened_after_accepted_validation(self):
        bundle = Bundle(self.directory)
        self.write_cohort([bundle])

        def remove_accepted_sources(_):
            bundle.manifest_path.unlink()
            bundle.paths['frames'].unlink()

        result = self.validated_then(remove_accepted_sources)
        attempt = result['attempts'][0]
        self.assertEqual(attempt['qualification'], 'QUALIFIED')
        self.assertEqual(attempt['validation']['provenance']['closure'], 'DECLARED_CLOSED')

    def test_B15_postvalidation_symlink_substitution_is_rejected_even_with_identical_bytes(self):
        for role in ('events', 'summary'):
            bundle = Bundle(self.directory)
            self.write_cohort([bundle])
            path = bundle.paths[role]
            target = self.directory / (role + '-target.csv')
            target.write_bytes(path.read_bytes())

            def substitute(_):
                path.unlink()
                try:
                    path.symlink_to(target)
                except OSError as error:
                    self.fail('Symlink coverage requires the POSIX tooling environment: ' + str(error))

            result = self.validated_then(substitute)
            self.assertEqual(result['attempts'][0]['qualification'], 'INVALID')
            path.unlink()
            path.write_bytes(target.read_bytes())

    def test_B15_reopened_snapshots_check_regular_type_size_and_mtime_before_and_after(self):
        original = os.fstat
        for role in ('events', 'summary'):
            for changed in ('st_mode', 'st_size', 'st_mtime_ns', 'st_dev', 'st_ino'):
                bundle = Bundle(self.directory)
                self.write_cohort([bundle])
                identity = bundle.paths[role].stat()
                armed = [False]
                calls = []

                def arm(_):
                    armed[0] = True

                def altered(fd):
                    actual = original(fd)
                    if not armed[0] or (actual.st_dev, actual.st_ino) != (identity.st_dev, identity.st_ino):
                        return actual
                    calls.append(fd)
                    if changed != 'st_mode' and len(calls) == 1:
                        return actual
                    values = {name: getattr(actual, name) for name in dir(actual) if name.startswith('st_')}
                    values[changed] = (stat.S_IFIFO | 0o600) if changed == 'st_mode' else values[changed] + 1
                    return SimpleNamespace(**values)

                with self.subTest(role=role, changed=changed), mock.patch('os.fstat', altered):
                    result = self.validated_then(arm)
                self.assertTrue(calls, 'Reopened files must be inspected through their actual descriptor')
                self.assertEqual(result['attempts'][0]['qualification'], 'INVALID')

    def test_B3_cohort_descriptor_is_regular_and_stable_across_bounded_read(self):
        original = os.fstat
        for changed in ('st_mode', 'st_size', 'st_mtime_ns', 'st_dev', 'st_ino'):
            self.write_cohort([])
            identity = self.path.stat()
            calls = []

            def altered(fd):
                actual = original(fd)
                if (actual.st_dev, actual.st_ino) != (identity.st_dev, identity.st_ino):
                    return actual
                calls.append(fd)
                if changed != 'st_mode' and len(calls) == 1:
                    return actual
                values = {name: getattr(actual, name) for name in dir(actual) if name.startswith('st_')}
                values[changed] = (stat.S_IFIFO | 0o600) if changed == 'st_mode' else values[changed] + 1
                return SimpleNamespace(**values)

            with mock.patch('os.fstat', altered):
                self.invalid_input()
            self.assertTrue(calls)

    def test_B15_all_actual_input_stream_reads_are_bounded_and_sources_stay_unchanged(self):
        bundle = Bundle(self.directory)
        self.write_cohort([bundle])
        before = {path: path.read_bytes() for path in self.directory.iterdir()}
        paths = {path.resolve() for path in before}
        identities = {(path.stat().st_dev, path.stat().st_ino): path for path in paths}
        observed = []

        def intercept(original):
            def opening(file, *args, **kwargs):
                stream = original(file, *args, **kwargs)
                if isinstance(stream, wire.CheckedReader):
                    return stream
                path = None
                if isinstance(file, (str, bytes, os.PathLike)):
                    path = Path(os.fsdecode(file)).resolve()
                elif isinstance(file, int):
                    info = os.fstat(file)
                    path = identities.get((info.st_dev, info.st_ino))
                if path in paths:
                    self.assertIn('b', stream.mode)
                    limit = 256 * 1024 if path == self.path else 16 * 1024 * 1024
                    if path == bundle.manifest_path:
                        limit = 16384
                    return BoundedReader(stream, observed, limit)
                return stream
            return opening

        with ExitStack() as stack:
            for module, name in ((builtins, 'open'), (io, 'open'), (os, 'fdopen')):
                stack.enter_context(mock.patch.object(module, name, intercept(getattr(module, name))))
            result = self.analyze()
        self.assertEqual(result['attempts'][0]['qualification'], 'QUALIFIED')
        self.assertTrue(observed)
        self.assertEqual(before, {path: path.read_bytes() for path in self.directory.iterdir()})

    def test_B3_import_API_and_main_are_quiet_read_only_and_no_external_action_is_attempted(self):
        bundle = Bundle(self.directory)
        self.write_cohort([bundle])
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            module = load_analyzer()
            result = module.analyze_cohort(self.path)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), '')
        self.assertEqual(result['timing_status'], 'NOT_QUALIFIED')
        guard = r'''
import importlib.util, os, sys
sys.dont_write_bytecode = True
tool, cohort = sys.argv[1:]
sys.path.insert(0, os.path.dirname(tool))
def audit(event, args):
    if event == 'open':
        name, mode, flags = args
        if (isinstance(mode, str) and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            raise AssertionError('Analyzer attempted a write')
        if isinstance(name, str) and name.endswith(('config.h', 'board_tool.py')):
            raise AssertionError('Historical evidence must not depend on current config or board')
    if event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.posix_spawn'):
        raise AssertionError('Analyzer attempted an external action')
sys.addaudithook(audit)
spec = importlib.util.spec_from_file_location('d127_guarded', tool)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
assert module.analyze_cohort(cohort)['input_status'] == 'VALID'
'''
        run = subprocess.run([sys.executable, '-B', '-c', guard, str(TOOL), str(self.path)],
                             capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(run.stdout, '')
        self.assertEqual(run.stderr, '')

    def test_B3_CLI_and_main_report_one_JSON_with_exit0_only_for_qualified_PASS(self):
        for delays, code in (([HOLD] * 50, 0), ([HOLD - 1] * 50, 1), ([HOLD], 1), ([], 1)):
            self.write_cohort(self.cohort50(delays))
            run = subprocess.run([sys.executable, '-B', str(TOOL), str(self.path)],
                                 capture_output=True, text=True, timeout=20)
            self.assertEqual(run.returncode, code, run.stdout + run.stderr)
            self.assertEqual(run.stderr, '')
            report = json.loads(run.stdout)
            self.assert_report(report)
            self.assertEqual(code == 0, report['timing_status'] == 'PASS')
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = self.module.main([str(self.path)])
            self.assertEqual(exit_code, code)
            self.assertEqual(json.loads(stdout.getvalue()), report)
        self.path.write_text('{', encoding='ascii')
        run = subprocess.run([sys.executable, '-B', str(TOOL), str(self.path)],
                             capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)['input_status'], 'INVALID')

    def test_B3_CLI_help_usage_and_no_output_repair_or_tuning_modes(self):
        output = self.directory / 'must-not-exist'
        for args, code in ((['--help'], 0), ([], 2), (['one', 'two'], 2),
                           (['--output', str(output)], 2), (['--repair'], 2),
                           (['--countdown-ms', '0'], 2), (['--upload'], 2)):
            run = subprocess.run([sys.executable, '-B', str(TOOL), *args],
                                 capture_output=True, text=True, timeout=20)
            self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
