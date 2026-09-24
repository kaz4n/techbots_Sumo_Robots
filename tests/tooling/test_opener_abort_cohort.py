# Checks D136 ownership, declared source identity and ten-slot aggregation.
# Keeps incomplete diagnostics and original failures visible without qualification inflation.
# Deferred public API/CLI tests use only synthetic local bundles and explicit declarations.
from contextlib import redirect_stderr, redirect_stdout
import copy
import io
import json
import subprocess
import sys
from opener_abort_fixture import AbortAnalysisCase, Bundle, Source, ENDPOINTS, TOOL, wire, CLEAN_FRAME


class OpenerAbortCohortTests(AbortAnalysisCase):
    def test_D136_ten_distinct_synthetic_M1_trials_pass_logically_without_physical_acceptance(self):
        for mode in range(1, 7):
            bundles = self.ten(mode)
            report = self.analyze(bundles, mode)
            self.assertEqual((report['input_status'], report['evidence_status'], report['timing_status']),
                             ('VALID', 'COMPLETE', 'PASS'))
            self.assertEqual((report['qualified_attempts'], report['passing_attempts'], report['logical_failures']), (10, 10, 0))
            self.assertEqual((report['minimum_elapsed_us'], report['maximum_elapsed_us']), (1000, 1000))
            self.assertEqual(report['declared_physical_trials_status'], 'NOT_QUALIFIED')
            self.assertEqual(report['mode'], mode)
            self.assertEqual(report['source']['config_values'], self.source.values)
            self.assertEqual(report['source']['binding_status'], 'DECLARED_MATCH')
            self.assertEqual([a['id'] for a in report['attempts']], [b.id for b in bundles])
            for bundle, attempt in zip(bundles, report['attempts']):
                self.assertEqual(attempt['qualification'], 'QUALIFIED')
                self.assertEqual(attempt['binding_status'], 'DECLARED_MATCH')
                self.assertEqual(attempt['validation']['provenance']['declared'], bundle.manifest())
                self.assertEqual(attempt['validation']['provenance']['evidence_kind'], 'SYNTHETIC')

    def test_D136_empty_and_nine_trials_do_not_fill_missing_scheduled_slots(self):
        for count in (0, 1, 9):
            report = self.analyze(self.ten()[:count])
            self.assertEqual(report['qualified_attempts'], count)
            self.assertEqual(report['passing_attempts'], count)
            self.assertEqual(report['evidence_status'], 'INCOMPLETE')
            self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')
            self.assertEqual(len(report['attempts']), count)
            self.assertEqual(report['minimum_elapsed_us'], 1000 if count else None)

    def test_D136_all_original_late_values_survive_ten_trial_FAIL_without_clamping(self):
        bundles = self.ten()
        bundles[3] = Bundle(self.directory, self.source, 3, elapsed=999)
        bundles[6] = Bundle(self.directory, self.source, 6, elapsed=1001)
        bundles[9] = Bundle(self.directory, self.source, 9, elapsed=100000)
        report = self.analyze(bundles)
        self.assertEqual((report['evidence_status'], report['timing_status']), ('COMPLETE', 'FAIL'))
        self.assertEqual((report['qualified_attempts'], report['passing_attempts'], report['logical_failures']), (10, 8, 0))
        self.assertEqual((report['minimum_elapsed_us'], report['maximum_elapsed_us']), (999, 100000))
        self.assertEqual(report['attempts'][6]['elapsed_us'], 1001)
        self.assertEqual(report['attempts'][9]['elapsed_us'], 100000)

    def test_D136_explicit_handover_failure_counts_as_evaluated_failure_not_missing_measurement(self):
        for count in (1, 10):
            bundles = self.ten()
            for bundle in bundles[:count]:
                bundle.set_trace([0, 16, 17, 18, 25]).write()
            report = self.analyze(bundles)
            self.assertEqual((report['evidence_status'], report['timing_status']), ('COMPLETE', 'FAIL'))
            self.assertEqual((report['qualified_attempts'], report['passing_attempts'], report['logical_failures']), (10, 10 - count, count))
            self.assertEqual(report['minimum_elapsed_us'], 1000 if count < 10 else None)
            self.assertEqual(report['maximum_elapsed_us'], 1000 if count < 10 else None)

    def test_D136_excluded_attempt_is_retained_and_cannot_be_replaced_by_a_retry(self):
        bundles = self.ten()
        bundles[4].set_trace([0, 21]).write()
        report = self.analyze(bundles)
        self.assertEqual((report['evidence_status'], report['timing_status']), ('INCOMPLETE', 'NOT_QUALIFIED'))
        self.assertEqual((report['qualified_attempts'], report['passing_attempts']), (9, 9))
        self.assertEqual(report['attempts'][4]['qualification'], 'EXCLUDED')
        bundles.append(Bundle(self.directory, self.source, 10))
        self.invalid_input(self.document(bundles))

    def test_D136_logical_failure_diagnostics_survive_M0_loss_closure_and_another_invalid_member(self):
        for reason in ('M0', 'loss', 'closure', 'other_invalid'):
            self.source = Source(self.directory, motors=reason != 'M0')
            bundles = self.ten()
            bundles[0].set_trace([0, 16, 17, 18, 25])
            if reason == 'loss':
                bundles[0].summary.update(skipped_frames=1, incomplete=1)
            elif reason == 'closure':
                bundles[0].declarations['closure'] = 'open'
            elif reason == 'other_invalid':
                bundles[1].marker(20)['value'] = 2
                bundles[1].write()
            bundles[0].write()
            report = self.analyze(bundles)
            self.assertEqual(report['logical_failures'], 1)
            self.assertEqual(report['attempts'][0]['logical_status'], 'FAIL')
            self.assertEqual(report['timing_status'], 'NOT_QUALIFIED')

    def test_D136_M0_and_each_unsealed_owner_retain_complete_diagnostics_but_never_qualify(self):
        for phase in (0, 1, 2, 3, 4, 255):
            for motors in (False, True):
                self.source = Source(self.directory, motors=motors)
                bundle = Bundle(self.directory, self.source, elapsed=1001)
                bundle.summary['phase'] = phase
                _, attempt = self.one(bundle.write(), 'QUALIFIED' if motors and phase == 3 else 'INCOMPLETE')
                self.assertIs(attempt['motors_allowed'], motors)
                self.assertEqual((attempt['logical_status'], attempt['timing_status']), ('PASS', 'FAIL'))
                self.assertEqual(attempt['elapsed_us'], 1001)

    def test_D136_every_individual_loss_field_disqualifies_visible_success(self):
        for field in wire.LOSS_FIELDS:
            with self.subTest(field=field):
                bundle = Bundle(self.directory, self.source)
                bundle.summary.update({field: 1, 'incomplete': 1})
                if field in ('frame_clamped', 'frame_invalid'):
                    bundle.frames = [wire.frame(CLEAN_FRAME, ordinal=0, status=1 if field == 'frame_clamped' else 2)]
                _, attempt = self.one(bundle.write(), 'INCOMPLETE')
                self.assertEqual(attempt['validation']['consistency'], 'PASS')
                self.assertEqual(attempt['timing_status'], 'PASS')
                self.assertEqual(attempt['elapsed_us'], 1000)
        bundle = Bundle(self.directory, self.source)
        bundle.summary['incomplete'] = 1
        _, attempt = self.invalid_attempt(bundle.write())
        self.assertEqual(attempt['validation']['consistency'], 'FAIL')

    def test_D136_owner_contradictions_are_invalid_in_every_phase_and_clear_arithmetic(self):
        for phase in (0, 1, 2, 3, 4, 255):
            for field in ('epoch_token', 'go_seen'):
                bundle = Bundle(self.directory, self.source)
                bundle.summary.update(phase=phase, **{field: 0})
                self.invalid_attempt(bundle.write(), 'COMPLETE')
        bundle = Bundle(self.directory, self.source).set_trace([0])
        bundle.events.remove(bundle.ordinary(1))
        bundle.summary.update(epoch_token=0, go_seen=0)
        self.invalid_attempt(bundle.renumber().write(), 'INCOMPLETE')

    def test_D136_incomplete_owner_precedence_preserves_trace_status_and_invalid_wins(self):
        for details, trace in (([], 'NOT_RECORDED'), ([0], 'INCOMPLETE'), ([0, 16], 'INCOMPLETE'), ([0, 22], 'EXCLUDED')):
            for reason in ('phase', 'loss', 'closure'):
                bundle = Bundle(self.directory, self.source).set_trace(details)
                if reason == 'phase':
                    bundle.summary['phase'] = 1
                elif reason == 'loss':
                    bundle.summary.update(skipped_frames=1, incomplete=1)
                else:
                    bundle.manifest_present = False
                self.one(bundle.write(), 'INCOMPLETE', trace)
        bundle = Bundle(self.directory, self.source).set_trace([0, 20])
        bundle.summary['phase'] = 1
        self.invalid_attempt(bundle.write())

    def test_D136_each_required_manifest_binding_is_null_incomplete_or_nonnull_mismatch_invalid(self):
        values = dict(firmware_revision='d' * 40, source_sha256='e' * 64, config_sha256='f' * 64,
                      log_hz=50, frame_capacity=10001, event_capacity=4095)
        for field, mismatched in values.items():
            for value in (None, mismatched):
                bundle = Bundle(self.directory, self.source)
                bundle.declarations[field] = value
                if value is None:
                    _, attempt = self.one(bundle.write(), 'INCOMPLETE')
                    self.assertEqual(attempt['binding_status'], 'INCOMPLETE')
                    self.assertEqual(attempt['timing_status'], 'PASS')
                else:
                    report = self.analyze([bundle.write()])
                    attempt = report['attempts'][0]
                    self.assertEqual(attempt['qualification'], 'INVALID')
                    self.assertIn(attempt['trace_status'], ('COMPLETE', 'INVALID'))
                    self.assertEqual(attempt['binding_status'], 'INVALID')
                    self.assertEqual((attempt['logical_status'], attempt['timing_status']), ('NOT_EVALUATED', 'NOT_EVALUATED'))
                    for key in ENDPOINTS:
                        self.assertIsNone(attempt[key])
                    self.assertEqual((report['evidence_status'], report['timing_status']), ('INVALID', 'NOT_QUALIFIED'))
                    self.assertEqual((report['qualified_attempts'], report['passing_attempts']), (0, 0))
                    self.assertTrue(attempt['errors'])

    def test_D136_open_unknown_or_absent_manifest_closure_never_qualifies(self):
        for closure in ('open', 'unknown'):
            bundle = Bundle(self.directory, self.source)
            bundle.declarations['closure'] = closure
            self.one(bundle.write(), 'INCOMPLETE')
        bundle = Bundle(self.directory, self.source)
        bundle.manifest_present = False
        _, attempt = self.one(bundle, 'INCOMPLETE')
        self.assertEqual(attempt['binding_status'], 'INCOMPLETE')

    def test_D136_HEADER_must_match_exact_source_M_declaration(self):
        for motors in (False, True):
            self.source = Source(self.directory, motors=motors)
            bundle = Bundle(self.directory, self.source)
            bundle.marker(0)['value'] = 0x0201 if motors else 0x0205
            self.invalid_attempt(bundle.write())

    def test_D136_identical_hash_triples_invalidate_every_alias_and_copied_member(self):
        first, other = self.ten()[:2]
        document = self.document([first])
        alias = dict(document['attempts'][0], id='alias')
        document['attempts'].append(alias)
        report = self.analyze(document=document)
        self.assertEqual([a['qualification'] for a in report['attempts']], ['INVALID', 'INVALID'])
        for role, path in first.paths.items():
            other.paths[role].write_bytes(path.read_bytes())
        other.manifest_path.write_text(json.dumps(other.manifest()), encoding='ascii')
        report = self.analyze([first, other])
        for attempt in report['attempts']:
            self.assertEqual(attempt['qualification'], 'INVALID')
            for key in ENDPOINTS:
                self.assertIsNone(attempt[key])
        self.assertEqual((report['qualified_attempts'], report['passing_attempts']), (0, 0))

    def test_D136_only_qualified_complete_values_contribute_extrema(self):
        bundles = self.ten()
        bundles[0] = Bundle(self.directory, self.source, 0, elapsed=900)
        bundles[1] = Bundle(self.directory, self.source, 1, elapsed=999999)
        bundles[1].declarations['closure'] = 'open'
        bundles[1].write()
        bundles[2].set_trace([0, 16, 17, 18, 25]).write()
        bundles[3].set_trace([0, 21]).write()
        report = self.analyze(bundles)
        self.assertEqual((report['minimum_elapsed_us'], report['maximum_elapsed_us']), (900, 1000))
        self.assertEqual((report['qualified_attempts'], report['passing_attempts'], report['logical_failures']), (8, 7, 1))
        self.assertEqual(report['attempts'][1]['elapsed_us'], 999999)

    def test_D136_hardware_reported_is_only_declared_physical_review_eligibility(self):
        bundles = self.ten()
        for bundle in bundles:
            bundle.declarations['origin'] = 'hardware_reported'
            bundle.write()
        report = self.analyze(bundles)
        self.assertEqual(report['declared_physical_trials_status'], 'ELIGIBLE')
        for mutation in ('synthetic', 'null', 'late', 'excluded'):
            bundles = self.ten()
            for bundle in bundles:
                bundle.declarations['origin'] = 'hardware_reported'
                bundle.write()
            if mutation in ('synthetic', 'null'):
                bundles[9].declarations['origin'] = 'synthetic' if mutation == 'synthetic' else None
            elif mutation == 'late':
                bundles[9].marker(20)['t_us'] += 1
            else:
                bundles[9].set_trace([0, 21])
            bundles[9].write()
            self.assertEqual(self.analyze(bundles)['declared_physical_trials_status'], 'NOT_QUALIFIED')

    def test_D136_validator_report_is_retained_exactly_and_all_attempts_are_checked(self):
        bundles = self.ten()[:3]
        bundles[0].paths['events'].write_bytes(b'broken\n')
        bundles[1].summary['event_count'] = 99
        bundles[1].write()
        manifest = bundles[2].manifest()
        manifest['files']['events']['sha256'] = '0' * 64
        bundles[2].manifest_path.write_text(json.dumps(manifest), encoding='ascii')
        self.write_cohort(bundles)
        report = self.validated_then(lambda accepted: None, expected_calls=3)
        self.assertEqual([a['qualification'] for a in report['attempts']], ['INVALID'] * 3)
        for attempt in report['attempts']:
            self.assertIsNone(attempt['motors_allowed'])
            self.assertIsNone(attempt['cue'])

    def test_D136_CLI_and_main_return_zero_only_for_complete_PASS_and_emit_one_JSON(self):
        for kind in ('pass', 'late', 'handover', 'missing', 'invalid'):
            bundles = self.ten()
            if kind == 'late':
                bundles[0].marker(20)['t_us'] += 1
                bundles[0].write()
            elif kind == 'handover':
                bundles[0].set_trace([0, 16, 17, 18, 25]).write()
            elif kind == 'missing':
                bundles.pop()
            self.write_cohort(bundles)
            if kind == 'invalid':
                self.path.write_text('{', encoding='ascii')
            expected = 0 if kind == 'pass' else 1
            result = subprocess.run([sys.executable, '-B', str(TOOL), str(self.path)], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, expected, result.stderr)
            report = json.loads(result.stdout)
            self.assert_report(report)
            self.assertEqual(result.stderr, '')
            stdout, stderr = io.StringIO(), io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                returned = self.module.main([str(self.path)])
            self.assertEqual(returned, expected)
            self.assertEqual(json.loads(stdout.getvalue()), report)
            self.assertEqual(stderr.getvalue(), '')

    def test_D136_CLI_usage_rejects_extra_options_and_has_no_transport_or_write_mode(self):
        for arguments in ([], ['--upload'], ['--output', 'x'], ['--repair'], ['a', 'b']):
            result = subprocess.run([sys.executable, '-B', str(TOOL), *arguments], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
        result = subprocess.run([sys.executable, '-B', str(TOOL), '--help'], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)
        self.assertIn('usage:', result.stdout.lower())
