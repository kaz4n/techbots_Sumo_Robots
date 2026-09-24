# Checks D130 target-loss interval and qualification rules through public APIs.
# Keeps synthetic CSV arithmetic separate from hardware and physical acceptance.
# Independent fixtures exercise grammar, owner evidence, file binding and CLI.
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import builtins
import copy
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

from target_loss_fixture import BoundedReader, BOUND, Bundle, GO, ROOT, SOURCE, U32, cohort, wire
from countdown_analysis_fixture import CLEAN_FRAME


TOOL = ROOT / 'tools/analyze_target_loss.py'
TOOLS = str(ROOT / 'tools')
REPORT_KEYS = {'schema_version', 'input_status', 'evidence_status', 'timing_status',
               'required_attempts', 'bound_us', 'qualified_attempts',
               'minimum_lower_delay_us', 'maximum_upper_delay_us', 'attempts', 'errors',
               'common_attempt_verified', 'transport_verified', 'hardware_acceptance'}
ATTEMPT_KEYS = {'id', 'qualification', 'trace_status', 'motors_allowed', 'source_start_us',
                'source_end_us', 'brake_decision_us', 'zero_applied_us', 'lower_delay_us',
                'upper_delay_us', 'timing_status', 'exclusion_detail', 'errors', 'validation'}
TIMES = ('source_start_us', 'source_end_us', 'brake_decision_us', 'zero_applied_us')
DELAYS = ('lower_delay_us', 'upper_delay_us')


def load_analyzer():
    # Load only during later execution; no implementation source inspection.
    spec = importlib.util.spec_from_file_location('d130_independent_public', TOOL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TargetLossAnalysisContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, TOOLS)
        cls.addClassCleanup(lambda: sys.path.remove(TOOLS))
        cls.validator = importlib.import_module('validate_csv_bundle')
        cls.module = load_analyzer()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='sumo-d130-synthetic-')
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.path = self.directory / 'cohort.json'

    def write_cohort(self, bundles=(), document=None):
        self.path.write_text(json.dumps(cohort(bundles) if document is None else document), encoding='ascii')
        return self.path

    def analyze(self, bundles=None, document=None, module=None):
        if bundles is not None or document is not None:
            self.write_cohort(() if bundles is None else bundles, document)
        report = (module or self.module).analyze_cohort(self.path)
        self.assert_report(report)
        return report

    def assert_errors(self, errors):
        self.assertIsInstance(errors, list)
        for error in errors:
            self.assertTrue({'code', 'message'} <= error.keys())
            self.assertIsInstance(error['code'], str)
            self.assertTrue(error['code'])
            self.assertIsInstance(error['message'], str)
            self.assertTrue(error['message'].strip())

    def assert_report(self, report):
        self.assertTrue(REPORT_KEYS <= report.keys())
        self.assertEqual(report['schema_version'], 1)
        self.assertEqual(report['required_attempts'], 10)
        self.assertEqual(report['bound_us'], 35000)
        self.assertIn(report['input_status'], ('VALID', 'INVALID'))
        self.assertIn(report['evidence_status'], ('COMPLETE', 'INCOMPLETE', 'INVALID'))
        self.assertIn(report['timing_status'], ('PASS', 'FAIL', 'INDETERMINATE', 'NOT_QUALIFIED'))
        for key in ('common_attempt_verified', 'transport_verified', 'hardware_acceptance'):
            self.assertIs(report[key], False)
        self.assert_errors(report['errors'])
        self.assertIsInstance(report['attempts'], list)
        for attempt in report['attempts']:
            self.assertTrue(ATTEMPT_KEYS <= attempt.keys())
            self.assertIn(attempt['qualification'], ('QUALIFIED', 'INCOMPLETE', 'INVALID',
                                                    'EXCLUDED', 'NOT_EXERCISED', 'NOT_RECORDED'))
            self.assertIn(attempt['trace_status'], ('COMPLETE', 'INCOMPLETE', 'INVALID',
                                                   'EXCLUDED', 'NOT_EXERCISED', 'NOT_RECORDED'))
            self.assertIn(attempt['timing_status'], ('PASS', 'FAIL', 'INDETERMINATE', 'NOT_EVALUATED'))
            self.assertTrue(attempt['motors_allowed'] is None or type(attempt['motors_allowed']) is bool)
            self.assert_errors(attempt['errors'])

    def one(self, bundle, qualification='QUALIFIED', trace='COMPLETE'):
        report = self.analyze([bundle])
        self.assertEqual(report['input_status'], 'VALID', report)
        self.assertEqual(len(report['attempts']), 1)
        attempt = report['attempts'][0]
        self.assertEqual(attempt['id'], bundle.id)
        self.assertEqual(attempt['qualification'], qualification, attempt)
        self.assertEqual(attempt['trace_status'], trace, attempt)
        self.assertEqual(report['qualified_attempts'], int(qualification == 'QUALIFIED'))
        self.assertEqual(report['evidence_status'], 'INVALID' if qualification == 'INVALID' else 'INCOMPLETE')
        self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
        if qualification != 'QUALIFIED':
            self.assertIsNone(report['minimum_lower_delay_us'])
            self.assertIsNone(report['maximum_upper_delay_us'])
        return report, attempt

    def invalid_attempt(self, bundle, trace='INVALID'):
        report, attempt = self.one(bundle, 'INVALID', trace)
        for key in TIMES + DELAYS:
            self.assertIsNone(attempt[key], (key, attempt))
        self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')
        self.assertTrue(attempt['errors'])
        return report, attempt

    def invalid_input(self, document=None):
        report = self.analyze(document=document) if document is not None else self.analyze()
        self.assertEqual(report['input_status'], 'INVALID', report)
        self.assertEqual(report['evidence_status'], 'INVALID')
        self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
        self.assertTrue(report['errors'])
        return report

    def ten(self, lower=34950, upper=35000):
        return [Bundle(self.directory, index, lower, upper) for index in range(10)]

    def validated_then(self, action):
        module = load_analyzer()
        path = (ROOT / 'tools/validate_csv_bundle.py').resolve()
        dependencies = []
        for name, value in vars(module).items():
            if (isinstance(value, ModuleType) and callable(getattr(value, 'validate_bundle', None))
                    and isinstance(getattr(value, '__file__', None), str)
                    and Path(value.__file__).resolve() == path):
                dependencies.append((value, 'validate_bundle'))
            elif (callable(value) and getattr(value, '__name__', None) == 'validate_bundle'
                  and getattr(value, '__code__', None) is not None
                  and Path(value.__code__.co_filename).resolve() == path):
                dependencies.append((module, name))
        self.assertEqual(len(dependencies), 1, 'Exactly one actual public validator dependency')
        owner, name = dependencies[0]
        original = getattr(owner, name)
        injected = []

        def boundary(*args, **kwargs):
            accepted = original(*args, **kwargs)
            self.assertEqual(accepted['format_integrity'], 'PASS', accepted)
            self.assertEqual(accepted['consistency'], 'PASS', accepted)
            injected.append(True)
            action(accepted)
            return accepted

        with mock.patch.object(owner, name, boundary):
            report = self.analyze(module=module)
        self.assertEqual(len(injected), 1, 'Mutation hook must actually run exactly once')
        return report

    def test_B15_ten_distinct_synthetic_M1_intervals_pass_without_physical_claims(self):
        bundles = self.ten()
        report = self.analyze(bundles)
        self.assertEqual(report['input_status'], 'VALID')
        self.assertEqual(report['evidence_status'], 'COMPLETE')
        self.assertEqual(report['timing_status'], 'PASS')
        self.assertEqual(report['qualified_attempts'], 10)
        self.assertEqual((report['minimum_lower_delay_us'], report['maximum_upper_delay_us']), (34950, 35000))
        self.assertEqual([a['id'] for a in report['attempts']], [b.id for b in bundles])
        for bundle, attempt in zip(bundles, report['attempts']):
            self.assertEqual(attempt['qualification'], 'QUALIFIED')
            self.assertEqual(attempt['trace_status'], 'COMPLETE')
            self.assertIs(attempt['motors_allowed'], True)
            self.assertEqual(attempt['timing_status'], 'PASS')
            self.assertIsNone(attempt['exclusion_detail'])
            self.assertEqual([attempt[key] for key in TIMES], [bundle.times[i] for i in range(1, 5)])
            self.assertEqual(attempt['validation']['provenance']['evidence_kind'], 'SYNTHETIC')

    def test_B9_interval_thresholds_are_inclusive_with_FAIL_before_straddle_at_cohort_level(self):
        for lower, upper, expected in ((34999, 35000, 'PASS'), (35000, 35000, 'PASS'),
                                        (35000, 35001, 'INDETERMINATE'), (34999, 35001, 'INDETERMINATE'),
                                        (35001, 35001, 'FAIL'), (35001, 50000, 'FAIL'), (0, 0, 'PASS')):
            with self.subTest(lower=lower, upper=upper):
                report = self.analyze(self.ten(lower, upper))
                self.assertEqual(report['evidence_status'], 'COMPLETE')
                self.assertEqual(report['timing_status'], expected)
                self.assertEqual((report['minimum_lower_delay_us'], report['maximum_upper_delay_us']), (lower, upper))
                for attempt in report['attempts']:
                    self.assertEqual((attempt['lower_delay_us'], attempt['upper_delay_us']), (lower, upper))
                    self.assertEqual(attempt['timing_status'], expected)
        bundles = self.ten()
        bundles[8] = Bundle(self.directory, 8, 35000, 35001)
        bundles[9] = Bundle(self.directory, 9, 35001, 35002)
        self.assertEqual(self.analyze(bundles)['timing_status'], 'FAIL')

    def test_B15_empty_and_nine_attempts_retain_data_but_cannot_qualify_a_cohort(self):
        empty = self.analyze([])
        self.assertEqual(empty['input_status'], 'VALID')
        self.assertEqual(empty['evidence_status'], 'INCOMPLETE')
        self.assertEqual(empty['qualified_attempts'], 0)
        self.assertEqual(empty['attempts'], [])
        self.assertIsNone(empty['minimum_lower_delay_us'])
        self.assertIsNone(empty['maximum_upper_delay_us'])
        report = self.analyze(self.ten()[:9])
        self.assertEqual(len(report['attempts']), 9)
        self.assertEqual(report['qualified_attempts'], 9)
        self.assertEqual(report['evidence_status'], 'INCOMPLETE')
        self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
        self.assertEqual(report['maximum_upper_delay_us'], BOUND)

    def test_B15_natural_wrap_zero_timestamps_equal_boundaries_and_all_modes_are_valid(self):
        for release in (0, U32 - SOURCE + 1, U32 - 100):
            for mode in range(1, 7):
                with self.subTest(release=release, mode=mode):
                    bundle = Bundle(self.directory, release=release, mode=mode)
                    _, attempt = self.one(bundle)
                    self.assertEqual(attempt['source_start_us'], bundle.absolute(SOURCE))
                    self.assertEqual((attempt['lower_delay_us'], attempt['upper_delay_us']), (34950, 35000))
        bundle = Bundle(self.directory, release=0)
        for event in bundle.events:
            event['t_us'] = 0
        _, attempt = self.one(bundle.write())
        self.assertEqual([attempt[key] for key in TIMES + DELAYS], [0] * 6)
        self.assertEqual(attempt['timing_status'], 'PASS')

    def test_B15_full_chronology_rejects_every_half_range_or_reversed_boundary(self):
        for marker in ('GO', 1, 2, 3, 4):
            for bad_offset in (0x80000000, U32):
                with self.subTest(marker=marker, offset=bad_offset):
                    bundle = Bundle(self.directory)
                    event = bundle.ordinary(1) if marker == 'GO' else bundle.marker(marker)
                    event['t_us'] = bundle.absolute(bad_offset)
                    self.invalid_attempt(bundle.write())
        for marker, offset in ((1, GO - 1), (2, SOURCE - 1), (3, SOURCE + 49), (4, SOURCE + 29999)):
            bundle = Bundle(self.directory)
            bundle.marker(marker)['t_us'] = bundle.absolute(offset)
            self.invalid_attempt(bundle.write())

    def test_B15_every_proper_prefix_and_absent_trace_has_its_exact_classification(self):
        cases = [([], 'NOT_RECORDED'), ([0], 'NOT_EXERCISED'), ([0, 1], 'INCOMPLETE'),
                 ([0, 1, 2], 'INCOMPLETE'), ([0, 1, 2, 3], 'INCOMPLETE')]
        for details, status in cases:
            with self.subTest(details=details):
                bundle = Bundle(self.directory).set_trace(details).write()
                _, attempt = self.one(bundle, status, status)
                self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')
                self.assertIsNone(attempt['exclusion_detail'])
                for detail, key in enumerate(TIMES, 1):
                    self.assertEqual(attempt[key], bundle.times[detail] if detail in details else None)
                for key in DELAYS:
                    self.assertIsNone(attempt[key])

    def test_B15_every_legal_exclusion_preserves_prefix_and_ignores_cancellation_clock(self):
        sequences = [[0, detail] for detail in range(6, 11)]
        sequences += [[0, 1, 2, detail] for detail in (*range(5, 11), 12)]
        sequences += [[0, 1, 2, 3, 11]]
        for details in sequences:
            for time in (0, U32, 0x80000000):
                with self.subTest(details=details, time=time):
                    bundle = Bundle(self.directory).set_trace(details)
                    bundle.events[-1]['t_us'] = time
                    _, attempt = self.one(bundle.write(), 'EXCLUDED', 'EXCLUDED')
                    self.assertEqual(attempt['exclusion_detail'], details[-1])
                    self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')
                    for key in DELAYS:
                        self.assertIsNone(attempt[key])
                    for detail, key in enumerate(TIMES, 1):
                        self.assertEqual(attempt[key], bundle.times[detail] if detail in details else None)

    def test_B15_invalid_sequences_never_borrow_missing_or_later_markers(self):
        sequences = ([1, 2, 3, 4], [0, 0], [0, 2], [0, 3], [0, 4], [0, 5], [0, 11], [0, 12],
                     [0, 1, 1], [0, 1, 3], [0, 1, 2, 2], [0, 1, 2, 4], [0, 1, 2, 11],
                     [0, 1, 2, 3, 3], [0, 1, 2, 3, 5], [0, 1, 2, 3, 12],
                     [0, 1, 2, 3, 4, 4], [0, 8, 1, 2], [0, 1, 2, 5, 3, 4])
        for details in sequences:
            with self.subTest(details=details):
                self.invalid_attempt(Bundle(self.directory).set_trace(details).write())
        bundle = Bundle(self.directory).set_trace([0, 1, 2])
        bundle.frames = [wire.frame(CLEAN_FRAME, ordinal=0)]
        bundle.events += [dict(t_us=bundle.absolute(SOURCE + 30000), ordinal=99,
                               kind=2, detail=3, value=0),
                          dict(t_us=bundle.absolute(SOURCE + 35000), ordinal=100,
                               kind=3, detail=6, value=4)]
        _, attempt = self.one(bundle.renumber().write(), 'INCOMPLETE', 'INCOMPLETE')
        self.assertIsNone(attempt['brake_decision_us'])
        self.assertIsNone(attempt['zero_applied_us'])

    def test_B15_header_and_every_timing_payload_enforce_exact_version_and_wire_ID(self):
        for value in (0, 1, 0x0100, 0x0102, 0x0104, 0x0106, 0x0201, 65535):
            bundle = Bundle(self.directory)
            bundle.marker(0)['value'] = value
            self.invalid_attempt(bundle.write())
        for detail in range(1, 13):
            details = ([0, 1, 2, 3, 4] if detail <= 4 else
                       [0, 1, 2, 3, 11] if detail == 11 else [0, 1, 2, detail])
            for value in (0, 2, 0x0101, 65535):
                bundle = Bundle(self.directory).set_trace(details)
                bundle.marker(detail)['value'] = value
                self.invalid_attempt(bundle.write())
        for detail in range(13, 256):
            self.invalid_attempt(Bundle(self.directory).set_trace([0, detail]).write())

    def test_B15_header_and_source_pair_must_be_adjacent_in_full_event_order(self):
        for after in ('START', 1):
            bundle = Bundle(self.directory)
            index = next(i for i, e in enumerate(bundle.events)
                         if (e['kind'] == 0 if after == 'START' else e['kind'] == 10 and e['detail'] == after))
            bundle.events.insert(index + 1, dict(t_us=bundle.absolute(SOURCE), ordinal=0,
                                                kind=9, detail=1, value=1))
            self.invalid_attempt(bundle.renumber().write())
        bundle = Bundle(self.directory)
        bundle.marker(0)['t_us'] += 1
        self.invalid_attempt(bundle.write())

    def test_B15_all_ordinals_increase_but_unrelated_event_codes_and_timestamps_remain_opaque(self):
        for duplicate in (False, True):
            bundle = Bundle(self.directory)
            bundle.events.insert(3, dict(t_us=0, ordinal=1 if duplicate else 0, kind=254, detail=255, value=65535))
            self.invalid_attempt(bundle.write())
        bundle = Bundle(self.directory)
        bundle.events.insert(3, dict(t_us=bundle.absolute(SOURCE + 31000), ordinal=0,
                                    kind=9, detail=255, value=65535))
        bundle.events.append(dict(t_us=0, ordinal=0, kind=2, detail=0, value=65535))
        bundle.renumber()
        for event in bundle.events:
            event['ordinal'] = event['ordinal'] * 3 + 7
        _, attempt = self.one(bundle.write())
        self.assertEqual(attempt['upper_delay_us'], 35000)

    def test_B3_START_GO_payloads_uniqueness_mode_and_release_are_checked(self):
        for kind in (0, 1):
            for key, value in (('detail', 0), ('detail', 7), ('detail', 2), ('value', 1)):
                bundle = Bundle(self.directory)
                bundle.ordinary(kind)[key] = value
                self.invalid_attempt(bundle.write())
            bundle = Bundle(self.directory)
            bundle.events.append(dict(bundle.ordinary(kind)))
            self.invalid_attempt(bundle.renumber().write())
        bundle = Bundle(self.directory)
        bundle.summary['release_us'] += 1
        self.invalid_attempt(bundle.write())
        bundle = Bundle(self.directory)
        bundle.events = [e for e in bundle.events if e['kind'] != 0]
        self.invalid_attempt(bundle.renumber().write())

    def test_B3_GO_after_nonheader_trace_is_invalid_and_missing_GO_is_incomplete_without_interval(self):
        for details in ([0, 1], [0, 1, 2, 3, 4], [0, 1, 2, 10]):
            bundle = Bundle(self.directory).set_trace(details)
            go = bundle.ordinary(1)
            bundle.events.remove(go)
            bundle.events.append(go)
            self.invalid_attempt(bundle.renumber().write())
            bundle.events.remove(go)
            _, attempt = self.one(bundle.renumber().write(), 'INCOMPLETE', 'INCOMPLETE')
            self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')
            self.assertIsNone(attempt['lower_delay_us'])
            self.assertIsNone(attempt['upper_delay_us'])

    def test_B3_START_GO_order_and_release_anchor_apply_even_without_a_candidate(self):
        for details in ([], [0]):
            for failure in ('order', 'half', 'backward'):
                bundle = Bundle(self.directory).set_trace(details)
                go = bundle.ordinary(1)
                if failure == 'order':
                    bundle.events.remove(go)
                    bundle.events.insert(0, go)
                else:
                    go['t_us'] = bundle.absolute(0x80000000 if failure == 'half' else U32)
                self.invalid_attempt(bundle.renumber().write())

    def test_B15_present_prefix_chronology_is_checked_for_incomplete_excluded_and_missing_GO(self):
        for details in ([0, 1], [0, 1, 2], [0, 1, 2, 3], [0, 1, 2, 10], [0, 1, 2, 3, 11]):
            for missing_go in (False, True):
                for marker, offset in ((1, 0x80000000), (1, U32), (2, SOURCE - 1), (3, SOURCE + 49)):
                    if marker not in details:
                        continue
                    bundle = Bundle(self.directory).set_trace(details)
                    if missing_go:
                        bundle.events = [e for e in bundle.events if e['kind'] != 1]
                    bundle.marker(marker)['t_us'] = bundle.absolute(offset)
                    self.invalid_attempt(bundle.renumber().write())

    def test_B3_closed_header_only_cancellation_with_go_seen_zero_is_legitimate_not_exercised(self):
        bundle = Bundle(self.directory).set_trace([0])
        bundle.events = [e for e in bundle.events if e['kind'] != 1]
        bundle.summary['go_seen'] = 0
        _, attempt = self.one(bundle.renumber().write(), 'NOT_EXERCISED', 'NOT_EXERCISED')
        self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')
        self.assertIs(attempt['motors_allowed'], True)

    def test_B15_M0_and_unsealed_owners_retain_diagnostic_intervals_but_never_qualify(self):
        for phase in (0, 1, 2, 3, 4, 255):
            for motors in (False, True):
                bundle = Bundle(self.directory, lower=35001, upper=35050, motors=motors)
                bundle.summary['phase'] = phase
                qualification = 'QUALIFIED' if phase == 3 and motors else 'INCOMPLETE'
                _, attempt = self.one(bundle.write(), qualification)
                self.assertIs(attempt['motors_allowed'], motors)
                self.assertEqual((attempt['lower_delay_us'], attempt['upper_delay_us']), (35001, 35050))
                self.assertEqual(attempt['timing_status'], 'FAIL')

    def test_B15_every_reported_loss_field_prevents_qualification_without_hiding_valid_interval(self):
        for field in wire.LOSS_FIELDS:
            with self.subTest(field=field):
                bundle = Bundle(self.directory)
                bundle.summary[field] = 1
                bundle.summary['incomplete'] = 1
                if field in ('frame_clamped', 'frame_invalid'):
                    bundle.frames = [wire.frame(CLEAN_FRAME, ordinal=0,
                                                status=1 if field == 'frame_clamped' else 2)]
                _, attempt = self.one(bundle.write(), 'INCOMPLETE')
                self.assertEqual(attempt['validation']['consistency'], 'PASS')
                self.assertEqual(attempt['validation']['recording']['loss'], 'REPORTED')
                self.assertEqual(attempt['upper_delay_us'], BOUND)
                self.assertEqual(attempt['timing_status'], 'PASS')

    def test_B15_closure_and_declared_provenance_are_independent_of_arithmetic_and_hardware(self):
        for closure in (None, 'open', 'unknown', 'closed'):
            bundle = Bundle(self.directory)
            if closure is None:
                bundle.manifest_present = False
            else:
                bundle.declarations['closure'] = closure
            _, attempt = self.one(bundle.write(), 'QUALIFIED' if closure == 'closed' else 'INCOMPLETE')
            self.assertEqual(attempt['timing_status'], 'PASS')
            self.assertEqual(attempt['lower_delay_us'], 34950)
        bundle = Bundle(self.directory)
        bundle.declarations['origin'] = 'hardware_reported'
        report, attempt = self.one(bundle.write())
        self.assertEqual(attempt['validation']['provenance']['evidence_kind'], 'HARDWARE_REPORTED')
        self.assertIs(report['hardware_acceptance'], False)
        for field in ('session_id', 'origin', 'firmware_revision', 'source_sha256', 'config_sha256',
                      'log_hz', 'frame_capacity', 'event_capacity', 'target'):
            bundle.declarations[field] = None
        _, attempt = self.one(bundle.write())
        self.assertEqual(attempt['validation']['provenance']['status'], 'PARTIAL_DECLARATION')
        self.assertEqual(attempt['validation']['provenance']['closure'], 'DECLARED_CLOSED')

    def test_B15_explicit_markers_contradict_zero_epoch_or_go_seen_in_every_owner_phase(self):
        for phase in (0, 1, 2, 3, 4, 255):
            for field in ('epoch_token', 'go_seen'):
                bundle = Bundle(self.directory)
                bundle.summary.update(phase=phase, **{field: 0})
                _, attempt = self.invalid_attempt(bundle.write(), 'COMPLETE')
                self.assertEqual(attempt['validation']['consistency'], 'PASS')
        bundle = Bundle(self.directory)
        bundle.events = [e for e in bundle.events if e['kind'] != 1]
        bundle.summary['go_seen'] = 0
        self.invalid_attempt(bundle.renumber().write(), 'INCOMPLETE')
        bundle = Bundle(self.directory).set_trace([])
        bundle.events = [e for e in bundle.events if e['kind'] != 1]
        bundle.summary.update(epoch_token=0, go_seen=0)
        self.invalid_attempt(bundle.renumber().write(), 'NOT_RECORDED')

    def test_B15_owner_incomplete_precedes_trace_categories_but_never_overrides_invalid_grammar(self):
        for details, trace in (([], 'NOT_RECORDED'), ([0], 'NOT_EXERCISED'),
                               ([0, 1, 2], 'INCOMPLETE'), ([0, 8], 'EXCLUDED')):
            for incomplete in ('phase', 'closure', 'loss'):
                bundle = Bundle(self.directory).set_trace(details)
                if incomplete == 'phase':
                    bundle.summary['phase'] = 1
                elif incomplete == 'closure':
                    bundle.manifest_present = False
                else:
                    bundle.summary.update(skipped_frames=1, incomplete=1)
                self.one(bundle.write(), 'INCOMPLETE', trace)
        bundle = Bundle(self.directory, motors=False).set_trace([0, 8])
        self.one(bundle.write(), 'INCOMPLETE', 'EXCLUDED')
        bundle = Bundle(self.directory).set_trace([0, 4])
        bundle.summary['phase'] = 1
        self.invalid_attempt(bundle.write())

    def test_B15_validator_report_remains_unchanged_and_untrusted_input_prevents_trace_decoding(self):
        for failure in ('none', 'format', 'consistency', 'manifest'):
            bundle = Bundle(self.directory)
            if failure == 'format':
                bundle.paths['events'].write_bytes(b'broken\n')
            if failure == 'consistency':
                bundle.summary['event_count'] = 99
                bundle.write()
            if failure == 'manifest':
                declaration = bundle.manifest()
                declaration['files']['events']['sha256'] = '0' * 64
                bundle.manifest_path.write_text(json.dumps(declaration), encoding='ascii')
            expected = self.validator.validate_bundle(*bundle.paths.values(), bundle.manifest_path)
            if failure == 'none':
                _, attempt = self.one(bundle)
            else:
                _, attempt = self.invalid_attempt(bundle)
            self.assertEqual(attempt['validation'], expected)

    def test_B15_qualified_extrema_exclude_diagnostics_and_invalid_attempts_without_discarding_any(self):
        bundles = self.ten(34000, 34050)
        bundles[8] = Bundle(self.directory, 8, 89000, 90000, motors=False)
        bundles[9] = Bundle(self.directory, 9, 0, 0)
        bundles[9].summary['epoch_token'] = 0
        bundles[9].write()
        report = self.analyze(bundles)
        self.assertEqual(len(report['attempts']), 10)
        self.assertEqual(report['qualified_attempts'], 8)
        self.assertEqual(report['evidence_status'], 'INVALID')
        self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
        self.assertEqual((report['minimum_lower_delay_us'], report['maximum_upper_delay_us']), (34000, 34050))
        self.assertEqual(report['attempts'][8]['timing_status'], 'FAIL')
        self.assertEqual(report['attempts'][8]['upper_delay_us'], 90000)
        self.assertEqual(report['attempts'][9]['trace_status'], 'COMPLETE')
        self.assertTrue(all(report['attempts'][9][key] is None for key in TIMES + DELAYS))

    def test_B15_reused_hash_triples_invalidate_all_aliases_and_identical_copies(self):
        first = Bundle(self.directory)
        unique = Bundle(self.directory, 1)
        document = cohort([first, unique])
        document['attempts'].append(dict(first.entry(), id='synthetic-alias'))
        report = self.analyze(document=document)
        self.assertEqual([a['qualification'] for a in report['attempts']], ['INVALID', 'QUALIFIED', 'INVALID'])
        self.assertEqual(report['qualified_attempts'], 1)
        self.assertEqual(report['evidence_status'], 'INVALID')
        for index in (0, 2):
            self.assertEqual(report['attempts'][index]['trace_status'], 'COMPLETE')
            self.assertTrue(all(report['attempts'][index][key] is None for key in TIMES + DELAYS))
        for role, path in first.paths.items():
            unique.paths[role].write_bytes(path.read_bytes())
        unique.manifest_path.write_text(json.dumps(unique.manifest()), encoding='ascii')
        report = self.analyze([first, unique])
        self.assertEqual([a['qualification'] for a in report['attempts']], ['INVALID', 'INVALID'])
        self.assertEqual(report['qualified_attempts'], 0)
        self.assertIsNone(report['minimum_lower_delay_us'])
        self.assertIsNone(report['maximum_upper_delay_us'])

    def test_B15_exact_cohort_schema_and_historical_values_reject_bool_float_and_unknown_fields(self):
        for key, values in (('schema_version', (0, 2, True, 1.0, '1', None)),
                            ('opp_clear_ms', (0, 29, 31, True, 30.0, '30', None)),
                            ('extra_margin_ms', (0, 4, 6, False, 5.0, '5', None))):
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

    def test_B15_attempt_exact_keys_unique_ASCII_ids_count_and_path_types_are_enforced(self):
        bundle = Bundle(self.directory)
        for identifier in ('', 'a' * 97, 'space id', 'é', '../x', 'x/y', 'x\\y', 1, None):
            value = cohort([bundle])
            value['attempts'][0]['id'] = identifier
            self.invalid_input(value)
        for identifier in ('A', 'A_z.9-0', '.', '..', 'a' * 96):
            value = cohort([bundle])
            value['attempts'][0]['id'] = identifier
            self.assertEqual(self.analyze(document=value)['input_status'], 'VALID')
        for key in bundle.entry():
            value = cohort([bundle])
            del value['attempts'][0][key]
            self.invalid_input(value)
        value = cohort([bundle])
        value['attempts'][0]['extra'] = True
        self.invalid_input(value)
        value = cohort([bundle])
        value['attempts'] *= 2
        self.invalid_input(value)
        self.invalid_input(dict(cohort([]), attempts=[dict(bundle.entry(), id=str(i)) for i in range(11)]))
        for role in ('frames', 'events', 'summary', 'manifest'):
            for bad in ('', 'x' * 4097, 1, [], False, None):
                if role == 'manifest' and bad is None:
                    continue
                value = cohort([bundle])
                value['attempts'][0][role] = bad
                self.invalid_input(value)

    def test_B15_duplicate_JSON_keys_wrong_roots_nonfinite_numbers_and_bad_encoding_fail(self):
        bundle = Bundle(self.directory)
        valid = json.dumps(cohort([bundle]))
        texts = ['{', '', '[]', 'null', 'true', '42', '{} {}',
                 valid.replace('"schema_version": 1', '"schema_version": 1, "schema_version": 1', 1),
                 valid.replace('"id": "synthetic-0"', '"id": "synthetic-0", "id": "second"', 1)]
        for text in texts:
            self.path.write_text(text, encoding='ascii')
            self.invalid_input()
        for value in (float('nan'), float('inf'), -float('inf')):
            self.invalid_input(dict(cohort([]), opp_clear_ms=value))
        self.path.write_bytes(b'\xff')
        self.invalid_input()

    def test_B15_relative_parent_and_absolute_paths_are_local_and_resolve_from_cohort_directory(self):
        bundle = Bundle(self.directory)
        nested = self.directory / 'nested'
        nested.mkdir()
        self.path = nested / 'cohort.json'
        value = cohort([bundle])
        for role in ('frames', 'events', 'summary', 'manifest'):
            value['attempts'][0][role] = '../' + value['attempts'][0][role]
        self.write_cohort(document=value)
        previous = Path.cwd()
        try:
            os.chdir(ROOT)
            report = self.module.analyze_cohort(str(self.path))
        finally:
            os.chdir(previous)
        self.assert_report(report)
        self.assertEqual(report['attempts'][0]['qualification'], 'QUALIFIED')
        for role in ('frames', 'events', 'summary'):
            value['attempts'][0][role] = str(bundle.paths[role])
        value['attempts'][0]['manifest'] = str(bundle.manifest_path)
        self.assertEqual(self.analyze(document=value)['attempts'][0]['qualification'], 'QUALIFIED')

    def test_B15_UNC_and_network_URI_declared_paths_are_invalid_before_bundle_access(self):
        bundle = Bundle(self.directory)
        local_names = {path.name for path in bundle.paths.values()} | {bundle.manifest_path.name}
        accessed = []

        def intercept(original):
            def opening(file, *args, **kwargs):
                if isinstance(file, (str, bytes, os.PathLike)):
                    path = os.fsdecode(file)
                    if (Path(path).name in local_names or path.startswith(('//', '\\\\', 'https:', 'smb:'))):
                        accessed.append(path)
                        raise AssertionError('Invalid cohort must reject paths before bundle access')
                return original(file, *args, **kwargs)
            return opening

        for role in ('frames', 'events', 'summary', 'manifest'):
            for path in ('//server/share/data.csv', '\\\\server\\share\\data.csv',
                         'https://example.invalid/evidence.csv', 'smb://server/share/evidence.csv'):
                value = cohort([bundle])
                value['attempts'][0][role] = path
                with ExitStack() as stack:
                    for module, name in ((builtins, 'open'), (io, 'open'), (os, 'open')):
                        stack.enter_context(mock.patch.object(module, name, intercept(getattr(module, name))))
                    self.invalid_input(value)
                self.assertEqual(accessed, [])
        for path in ('//server/share/cohort.json', '\\\\server\\share\\cohort.json',
                     'https://example.invalid/cohort.json', 'smb://server/share/cohort.json'):
            with ExitStack() as stack:
                for module, name in ((builtins, 'open'), (io, 'open'), (os, 'open')):
                    stack.enter_context(mock.patch.object(module, name, intercept(getattr(module, name))))
                report = self.module.analyze_cohort(path)
            self.assert_report(report)
            self.assertEqual(report['input_status'], 'INVALID')
            self.assertEqual(accessed, [])

    def test_B15_cohort_size_boundary_missing_directory_and_symlinks_fail_explicitly(self):
        raw = json.dumps(cohort([])).encode('ascii')
        self.path.write_bytes(raw + b' ' * (256 * 1024 - len(raw)))
        self.assertEqual(self.analyze()['input_status'], 'VALID')
        self.path.write_bytes(self.path.read_bytes() + b' ')
        self.invalid_input()
        for path in (self.directory, self.directory / 'missing.json'):
            report = self.module.analyze_cohort(path)
            self.assert_report(report)
            self.assertEqual(report['input_status'], 'INVALID')
        self.write_cohort([])
        for dangling in (False, True):
            link = self.directory / ('dangling.json' if dangling else 'linked.json')
            link.symlink_to(self.directory / 'absent.json' if dangling else self.path)
            report = self.module.analyze_cohort(link)
            self.assert_report(report)
            self.assertEqual(report['input_status'], 'INVALID')

    def test_B15_nonregular_missing_and_oversized_CSV_members_cannot_be_decoded(self):
        for role in ('frames', 'events', 'summary'):
            for issue in ('missing', 'directory', 'symlink', 'oversize'):
                bundle = Bundle(self.directory)
                path = bundle.paths[role]
                raw = path.read_bytes()
                path.unlink()
                if issue == 'directory':
                    path.mkdir()
                elif issue == 'symlink':
                    target = self.directory / (role + '-regular.csv')
                    target.write_bytes(raw)
                    path.symlink_to(target)
                elif issue == 'oversize':
                    with path.open('wb') as stream:
                        stream.seek(16 * 1024 * 1024)
                        stream.write(b'\n')
                self.invalid_attempt(bundle)
                if issue == 'directory':
                    path.rmdir()
                elif path.exists() or path.is_symlink():
                    path.unlink()

    def test_B15_postvalidation_same_size_restored_mtime_mutation_is_rejected_for_each_reread(self):
        for role in ('events', 'summary'):
            bundle = Bundle(self.directory)
            self.write_cohort([bundle])
            path = bundle.paths[role]
            old = path.read_bytes()
            identity = path.stat()

            def mutate(_):
                if role == 'events':
                    events = copy.deepcopy(bundle.events)
                    events[-1]['t_us'] += 1
                    data = wire.header('events') + b''.join(wire.event(**event) for event in events)
                else:
                    values = dict(bundle.summary, epoch_token=2, frame_count=0, event_count=7)
                    data = wire.header('summary') + wire.summary(**values)
                self.assertNotEqual(data, old)
                self.assertEqual(len(data), len(old))
                path.write_bytes(data)
                os.utime(path, ns=(identity.st_atime_ns, identity.st_mtime_ns))
                self.assertEqual(path.stat().st_size, identity.st_size)
                self.assertEqual(path.stat().st_mtime_ns, identity.st_mtime_ns)

            report = self.validated_then(mutate)
            attempt = report['attempts'][0]
            self.assertEqual(attempt['qualification'], 'INVALID')
            self.assertEqual(attempt['trace_status'], 'INVALID')
            self.assertTrue(all(attempt[key] is None for key in TIMES + DELAYS))
            self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')

    def test_B15_accepted_hash_byte_count_and_row_count_all_bind_the_exact_reread(self):
        for role in ('events', 'summary'):
            for field in ('sha256', 'bytes', 'rows'):
                bundle = Bundle(self.directory)
                self.write_cohort([bundle])

                def alter(accepted):
                    accepted['files'][role][field] = ('0' * 64 if field == 'sha256' else
                                                     accepted['files'][role][field] + 1)

                report = self.validated_then(alter)
                self.assertEqual(report['attempts'][0]['qualification'], 'INVALID')
                self.assertEqual(report['attempts'][0]['trace_status'], 'INVALID')

    def test_B15_accepted_manifest_and_frames_are_not_reopened_or_reinterpreted(self):
        bundle = Bundle(self.directory)
        self.write_cohort([bundle])

        def remove(_):
            bundle.manifest_path.unlink()
            bundle.paths['frames'].unlink()

        report = self.validated_then(remove)
        attempt = report['attempts'][0]
        self.assertEqual(attempt['qualification'], 'QUALIFIED')
        self.assertEqual(attempt['trace_status'], 'COMPLETE')
        self.assertEqual(attempt['upper_delay_us'], BOUND)
        self.assertEqual(attempt['validation']['provenance']['closure'], 'DECLARED_CLOSED')

    def test_B15_postvalidation_symlink_substitution_fails_even_when_bytes_are_identical(self):
        for role in ('events', 'summary'):
            bundle = Bundle(self.directory)
            self.write_cohort([bundle])
            path = bundle.paths[role]
            target = self.directory / (role + '-accepted-copy.csv')
            target.write_bytes(path.read_bytes())

            def substitute(_):
                path.unlink()
                path.symlink_to(target)

            report = self.validated_then(substitute)
            self.assertTrue(path.is_symlink())
            self.assertEqual(report['attempts'][0]['qualification'], 'INVALID')
            self.assertEqual(report['attempts'][0]['trace_status'], 'INVALID')
            path.unlink()
            path.write_bytes(target.read_bytes())

    def test_B15_each_reread_descriptor_must_be_regular_and_keep_identity_size_and_mtime(self):
        original = os.fstat
        for role in ('events', 'summary'):
            for changed in ('st_mode', 'st_size', 'st_mtime_ns', 'st_dev', 'st_ino'):
                bundle = Bundle(self.directory)
                self.write_cohort([bundle])
                identity = bundle.paths[role].stat()
                armed, calls = [False], []

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
                    values[changed] = stat.S_IFIFO | 0o600 if changed == 'st_mode' else values[changed] + 1
                    return SimpleNamespace(**values)

                with self.subTest(role=role, changed=changed), mock.patch('os.fstat', altered):
                    report = self.validated_then(arm)
                self.assertGreaterEqual(len(calls), 1 if changed == 'st_mode' else 2,
                                        'The actual reread descriptor must reach the injected check')
                self.assertEqual(report['attempts'][0]['qualification'], 'INVALID')
                self.assertEqual(report['attempts'][0]['trace_status'], 'INVALID')

    def test_B15_cohort_descriptor_is_regular_and_bound_before_and_after_its_read(self):
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
                values[changed] = stat.S_IFIFO | 0o600 if changed == 'st_mode' else values[changed] + 1
                return SimpleNamespace(**values)

            with mock.patch('os.fstat', altered):
                self.invalid_input()
            self.assertGreaterEqual(len(calls), 1 if changed == 'st_mode' else 2)

    def test_B15_all_input_stream_reads_are_bounded_and_no_source_bytes_change(self):
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
            report = self.analyze()
        self.assertEqual(report['attempts'][0]['qualification'], 'QUALIFIED')
        self.assertTrue(observed, 'A real input stream must pass the bound observer')
        self.assertEqual(before, {path: path.read_bytes() for path in self.directory.iterdir()})

    def test_B15_import_and_public_API_are_quiet_read_only_and_do_not_consult_live_configuration(self):
        bundle = Bundle(self.directory)
        self.write_cohort([bundle])
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            module = load_analyzer()
            report = module.analyze_cohort(self.path)
        self.assertEqual(stdout.getvalue(), '')
        self.assertEqual(stderr.getvalue(), '')
        self.assertEqual(report['input_status'], 'VALID')
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
            raise AssertionError('Historical evidence must not read current firmware config or board tools')
    if event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.posix_spawn'):
        raise AssertionError('Analyzer attempted an external action')
sys.addaudithook(audit)
spec = importlib.util.spec_from_file_location('d130_guarded', tool)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
assert module.analyze_cohort(cohort)['attempts'][0]['qualification'] == 'QUALIFIED'
'''
        run = subprocess.run([sys.executable, '-B', '-c', guard, str(TOOL), str(self.path)],
                             capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(run.stdout, '')
        self.assertEqual(run.stderr, '')

    def test_B15_CLI_and_main_emit_one_JSON_and_return_zero_only_for_complete_PASS(self):
        for lower, upper, count, code in ((34950, 35000, 10, 0), (35001, 35002, 10, 1),
                                         (35000, 35001, 10, 1), (34950, 35000, 1, 1), (0, 0, 0, 1)):
            self.write_cohort(self.ten(lower, upper)[:count])
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
            self.assertIs(type(exit_code), int)
            self.assertEqual(exit_code, code)
            self.assertEqual(json.loads(stdout.getvalue()), report)
        self.path.write_text('{', encoding='ascii')
        run = subprocess.run([sys.executable, '-B', str(TOOL), str(self.path)],
                             capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)['input_status'], 'INVALID')

    def test_B15_CLI_help_usage_errors_and_no_output_repair_upload_or_tuning_modes(self):
        output = self.directory / 'must-not-exist'
        for args, code in ((['--help'], 0), ([], 2), (['one', 'two'], 2),
                           (['--output', str(output)], 2), (['--repair'], 2),
                           (['--opp-clear-ms', '0'], 2), (['--upload'], 2)):
            run = subprocess.run([sys.executable, '-B', str(TOOL), *args],
                                 capture_output=True, text=True, timeout=20)
            self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
