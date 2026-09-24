# Checks D135/D136 metadata, event grammar and unsigned chronology independently.
# Rejects invented handovers, repaired prefixes and physical timing claims.
# Deferred unittest cases use public decode_cue/analyze_cohort and synthetic CSV bytes.
import copy
from opener_abort_fixture import AbortAnalysisCase, Bundle, Source, ENDPOINTS, U32, expected_cue, packed, wire, CLEAN_FRAME


class OpenerAbortWireTests(AbortAnalysisCase):
    def test_D135_all_65536_cue_words_follow_literal_metadata_table_and_attempt_mode(self):
        for value in range(65536):
            expected = expected_cue(value)
            mode = value & 7
            self.assertEqual(self.module.decode_cue(value, mode if 1 <= mode <= 6 else 3), expected, value)
            if expected is not None:
                decoded = self.module.decode_cue(value, mode)
                self.assertIs(type(decoded['snapshot_front_present']), bool)
                for field in ('mode', 'phase', 'cause', 'effective_mask'):
                    self.assertIs(type(decoded[field]), int)
                for other in range(1, 7):
                    if other != mode:
                        self.assertIsNone(self.module.decode_cue(value, other), (value, other))

    def test_D136_cue_helper_rejects_bool_noninteger_ranges_without_coercion(self):
        valid = packed(3)
        for value in (True, False, None, '579', 579.0, -1, 65536, 2 ** 100, [], {}):
            self.assertIsNone(self.module.decode_cue(value, 3), repr(value))
        for mode in (True, False, None, '3', 3.0, -1, 0, 7, 2 ** 100, [], {}):
            self.assertIsNone(self.module.decode_cue(valid, mode), repr(mode))

    def test_D136_all_modes_preserve_exact_decoded_cue_and_source_bound_handover(self):
        for mode in range(1, 7):
            bundle = Bundle(self.directory, self.source, mode=mode)
            _, attempt = self.one(bundle)
            self.assertEqual(attempt['cue'], expected_cue(bundle.cue_value))
            self.assertEqual(attempt['handover_state'], bundle.handover)
            self.assertEqual(attempt['logical_status'], 'PASS')
            self.assertEqual(attempt['timing_status'], 'PASS')
            self.assertEqual([attempt[key] for key in ENDPOINTS],
                             [bundle.times[n] for n in (16, 17, 18, 19, 20)] + [1000])
            self.assertEqual((attempt['terminal_detail'], attempt['terminal_value']), (20, 1))

    def test_D136_every_supported_prefix_and_absent_trace_has_exact_status(self):
        for details in ([], [0], [0, 16], [0, 16, 17], [0, 16, 17, 18], [0, 16, 17, 18, 19]):
            with self.subTest(details=details):
                bundle = Bundle(self.directory, self.source).set_trace(details).write()
                status = 'INCOMPLETE' if details else 'NOT_RECORDED'
                _, attempt = self.one(bundle, status, status)
                self.assertEqual((attempt['logical_status'], attempt['timing_status']), ('NOT_EVALUATED', 'NOT_EVALUATED'))
                for detail, key in zip((16, 17, 18, 19, 20), ENDPOINTS):
                    self.assertEqual(attempt[key], bundle.times[detail] if detail in details else None)
                self.assertIsNone(attempt['elapsed_us'])

    def test_D136_all_exclusion_sequences_keep_terminal_payload_without_elapsed(self):
        cases = [([0, 21], 1), ([0, 21], 2), ([0, 22], 1), ([0, 22], 2), ([0, 23], 1),
                 ([0, 16, 17, 18, 22], 1), ([0, 16, 17, 18, 22], 2),
                 ([0, 16, 17, 18, 19, 22], 2), ([0, 16, 17, 18, 19, 24], 1)]
        for details, value in cases:
            with self.subTest(details=details, value=value):
                bundle = Bundle(self.directory, self.source).set_trace(details)
                bundle.events[-1]['value'] = value
                _, attempt = self.one(bundle.write(), 'EXCLUDED', 'EXCLUDED')
                self.assertEqual((attempt['terminal_detail'], attempt['terminal_value']), (details[-1], value))
                self.assertEqual((attempt['logical_status'], attempt['timing_status']), ('NOT_EVALUATED', 'NOT_EVALUATED'))
                self.assertIsNone(attempt['applied_us'])
                self.assertIsNone(attempt['elapsed_us'])

    def test_D136_invalid_source_and_receipt_clocks_cannot_create_arithmetic_requirements(self):
        for details in ([0, 23], [0, 16, 17, 18, 19, 24]):
            for clock in (0, U32, 0x80000000):
                bundle = Bundle(self.directory, self.source).set_trace(details)
                bundle.events[-1]['t_us'] = clock
                _, attempt = self.one(bundle.write(), 'EXCLUDED', 'EXCLUDED')
                self.assertIsNone(attempt['elapsed_us'])

    def test_D136_handover_failed_is_explicit_logical_failure_even_with_correct_numeric_state(self):
        for state in range(12):
            bundle = Bundle(self.directory, self.source).set_trace([0, 16, 17, 18, 25])
            bundle.marker(25)['value'] = state
            report, attempt = self.one(bundle.write(), 'QUALIFIED', 'HANDOVER_FAILED')
            self.assertEqual(attempt['logical_status'], 'FAIL')
            self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')
            self.assertEqual((attempt['terminal_detail'], attempt['terminal_value']), (25, state))
            self.assertEqual(attempt['handover_state'], state)
            self.assertIsNone(attempt['applied_us'])
            self.assertIsNone(attempt['elapsed_us'])
            self.assertEqual(report['logical_failures'], 1)

    def test_D136_illegal_orders_duplicates_terminal_tails_and_P4_trace_never_retry(self):
        cases = ([16, 17, 18, 19, 20], [0, 0], [0, 17], [0, 18], [0, 19], [0, 20], [0, 24], [0, 25],
                 [0, 16, 16], [0, 16, 18], [0, 16, 17, 19], [0, 16, 17, 18, 20],
                 [0, 16, 17, 18, 19, 25], [0, 16, 17, 18, 25, 20],
                 [0, 16, 17, 18, 19, 20, 20], [0, 23, 16, 17, 18, 19],
                 [0, 21, 16, 17, 18, 19, 20], [0, 1, 2, 3, 4])
        for details in cases:
            with self.subTest(details=details):
                self.invalid_attempt(Bundle(self.directory, self.source).set_trace(details).write())
        bundle = Bundle(self.directory, self.source).set_trace([0, 16, 17, 18, 19, 22])
        bundle.events[-1]['value'] = 1
        self.invalid_attempt(bundle.write())

    def test_D136_detail_values_are_exact_and_unknown_details_are_not_ordinary_events(self):
        cases = {0: (0, 1, 0x0101, 0x0105, 0x0200, 0x0204, 0x0207, 65535),
                 16: (0, 2, 65535), 17: (0, 2, 65535), 19: (0, 4, 8, 65535),
                 20: (0, 2, 65535), 21: (0, 3, 65535), 22: (0, 3, 65535),
                 23: (0, 2, 65535), 24: (0, 2, 65535), 25: (12, 65535)}
        for detail, values in cases.items():
            for value in values:
                bundle = Bundle(self.directory, self.source)
                if detail in (21, 22, 23):
                    bundle.set_trace([0, detail])
                elif detail == 24:
                    bundle.set_trace([0, 16, 17, 18, 19, 24])
                elif detail == 25:
                    bundle.set_trace([0, 16, 17, 18, 25])
                bundle.marker(detail)['value'] = value
                self.invalid_attempt(bundle.write())
        for detail in tuple(range(1, 16)) + tuple(range(26, 256)):
            self.invalid_attempt(Bundle(self.directory, self.source).set_trace([0, detail]).write())

    def test_D136_header_and_every_retained_decision_suffix_prefix_require_full_order_adjacency(self):
        for details in ([0], [0, 16, 17], [0, 16, 17, 18], [0, 16, 17, 18, 19],
                        [0, 16, 17, 18, 25], [0, 16, 17, 18, 22]):
            for gap in range(1, len(details)):
                bundle = Bundle(self.directory, self.source).set_trace(details)
                right = bundle.marker(details[gap])
                if details[gap] == 16:
                    continue  # No adjacency obligation joins HEADER to the later read pair.
                bundle.events.insert(bundle.events.index(right), dict(t_us=0, ordinal=0, kind=9, detail=0, value=0))
                self.invalid_attempt(bundle.renumber().write())
        bundle = Bundle(self.directory, self.source)
        bundle.events.insert(1, dict(t_us=0, ordinal=0, kind=9, detail=0, value=0))
        self.invalid_attempt(bundle.renumber().write())

    def test_D136_receipt_terminal_can_follow_ordinary_events_without_invented_batch_boundaries(self):
        for terminal, value, qualification, trace in ((20, 1, 'QUALIFIED', 'COMPLETE'),
                (24, 1, 'EXCLUDED', 'EXCLUDED'), (22, 2, 'EXCLUDED', 'EXCLUDED')):
            bundle = Bundle(self.directory, self.source).set_trace([0, 16, 17, 18, 19, terminal])
            bundle.events[-1]['value'] = value
            bundle.events.insert(-1, dict(t_us=U32, ordinal=0, kind=9, detail=0, value=0))
            self.one(bundle.renumber().write(), qualification, trace)

    def test_D136_all_ordinals_increase_even_for_ordinary_events_but_times_do_not_sort_records(self):
        bundle = Bundle(self.directory, self.source)
        bundle.events.insert(3, dict(t_us=U32, ordinal=0, kind=254, detail=253, value=65535))
        self.one(bundle.renumber().write())
        for ordinal in (bundle.events[2]['ordinal'], bundle.events[2]['ordinal'] - 1):
            bundle.events[3]['ordinal'] = ordinal
            self.invalid_attempt(bundle.write())

    def test_D136_START_GO_values_modes_uniqueness_and_release_are_checked(self):
        for kind in (0, 1):
            for field, value in (('detail', 0), ('detail', 1), ('detail', 7), ('value', 1)):
                bundle = Bundle(self.directory, self.source)
                bundle.ordinary(kind)[field] = value
                self.invalid_attempt(bundle.write())
            bundle = Bundle(self.directory, self.source)
            bundle.events.append(copy.copy(bundle.ordinary(kind)))
            self.invalid_attempt(bundle.renumber().write())
        bundle = Bundle(self.directory, self.source)
        bundle.summary['release_us'] += 1
        self.invalid_attempt(bundle.write())
        bundle = Bundle(self.directory, self.source)
        bundle.marker(0)['t_us'] += 1
        self.invalid_attempt(bundle.write())
        bundle = Bundle(self.directory, self.source)
        bundle.events.remove(bundle.ordinary(0))
        self.invalid_attempt(bundle.renumber().write())

    def test_D136_GO_missing_is_incomplete_late_is_invalid_and_header_only_cancellation_is_incomplete(self):
        bundle = Bundle(self.directory, self.source)
        bundle.events.remove(bundle.ordinary(1))
        _, attempt = self.one(bundle.renumber().write(), 'INCOMPLETE', 'INCOMPLETE')
        self.assertIsNone(attempt['elapsed_us'])
        self.assertEqual(attempt['timing_status'], 'NOT_EVALUATED')
        bundle = Bundle(self.directory, self.source)
        bundle.events.append(bundle.events.pop(bundle.events.index(bundle.ordinary(1))))
        self.invalid_attempt(bundle.renumber().write())
        bundle = Bundle(self.directory, self.source).set_trace([0])
        bundle.events.remove(bundle.ordinary(1))
        bundle.summary['go_seen'] = 0
        self.one(bundle.renumber().write(), 'INCOMPLETE', 'INCOMPLETE')

    def test_D136_GO_time_DIRECT_allows_read_pair_before_GO_with_decision_at_GO(self):
        bundle = Bundle(self.directory, self.source)
        go = bundle.ordinary(1)['t_us']
        for detail, time in ((16, go - 50), (17, go - 10), (18, go), (19, go), (20, go + 1000)):
            bundle.marker(detail)['t_us'] = time & U32
        _, attempt = self.one(bundle.write())
        self.assertEqual(attempt['elapsed_us'], 1000)
        self.assertLess(attempt['read_start_us'], go)

    def test_D136_routing_uses_current_front_even_for_ignored_front_side_cause_and_WAIT_hold(self):
        for mode, phase, mask in ((1, 1, 18), (2, 1, 10), (6, 1, 18), (6, 4, 10), (3, 0, 16)):
            bundle = Bundle(self.directory, self.source, mode=mode)
            bundle.marker(18)['value'] = packed(mode, phase, 2, mask)
            bundle.marker(19)['value'] = 5 if mask & 7 else 7
            self.one(bundle.write())
            bundle.marker(19)['value'] = 7 if mask & 7 else 5
            self.invalid_attempt(bundle.write())

    def test_D136_historical_center_threshold_one_requires_ATTACK_for_five_centered_front_patterns(self):
        for threshold in (1, 3, 4294967295):
            self.source = Source(self.directory, ATTACK_ENTER_TICKS=threshold)
            for front in range(1, 8):
                bundle = Bundle(self.directory, self.source)
                bundle.marker(18)['value'] = packed(3, mask=front)
                expected = 6 if threshold == 1 and front in (2, 3, 5, 6, 7) else 5
                bundle.marker(19)['value'] = expected
                self.one(bundle.write())
                bundle.marker(19)['value'] = 5 if expected == 6 else 6
                self.invalid_attempt(bundle.write())

    def test_D136_elapsed_boundary_and_different_historical_tick_are_exact_without_clamping(self):
        for bound in (1000, 500, 2147483647):
            self.source = Source(self.directory, TICK_US=bound)
            for elapsed in (0, 499, 500, 999, 1000, 1001, 100000):
                _, attempt = self.one(Bundle(self.directory, self.source, elapsed=elapsed))
                self.assertEqual(attempt['elapsed_us'], elapsed)
                self.assertEqual(attempt['timing_status'], 'PASS' if elapsed <= bound else 'FAIL')

    def test_D136_timestamp_zero_equal_endpoints_and_natural_wrap_are_valid(self):
        for release in (0, U32 - 100, (U32 - 5200000 + 1) & U32):
            self.one(Bundle(self.directory, self.source, release=release))
        bundle = Bundle(self.directory, self.source, release=0)
        for event in bundle.events:
            event['t_us'] = 0
        _, attempt = self.one(bundle.write())
        self.assertEqual([attempt[key] for key in ENDPOINTS], [0] * 6)

    def test_D136_unsigned_source_anchor_rejects_reversed_and_half_range_offsets(self):
        for detail, offset in ((17, U32), (17, 0x80000000), (18, 9), (18, 0x80000000),
                               (20, 99), (20, 0x80000000)):
            bundle = Bundle(self.directory, self.source)
            bundle.marker(detail)['t_us'] = (bundle.times[16] + offset) & U32
            if detail == 18:
                bundle.marker(19)['t_us'] = bundle.marker(18)['t_us']
            self.invalid_attempt(bundle.write())
        for details in ([0, 16, 17], [0, 16, 17, 18], [0, 16, 17, 18, 19, 24]):
            bundle = Bundle(self.directory, self.source).set_trace(details)
            bundle.marker(17)['t_us'] = (bundle.times[16] - 1) & U32
            self.invalid_attempt(bundle.write())

    def test_D136_START_GO_and_GO_decision_chronology_apply_to_all_trace_dispositions(self):
        for details in ([], [0], [0, 16, 17, 18, 19, 20]):
            bundle = Bundle(self.directory, self.source).set_trace(details)
            go = bundle.events.pop(bundle.events.index(bundle.ordinary(1)))
            bundle.events.insert(0, go)
            self.invalid_attempt(bundle.renumber().write())
            for offset in (U32, 0x80000000):
                bundle = Bundle(self.directory, self.source).set_trace(details)
                bundle.ordinary(1)['t_us'] = bundle.absolute(offset)
                self.invalid_attempt(bundle.write())
        for offset in (U32, 0x80000000):
            bundle = Bundle(self.directory, self.source)
            decision = (bundle.ordinary(1)['t_us'] + offset) & U32
            for detail in (16, 17, 18, 19, 20):
                bundle.marker(detail)['t_us'] = decision
            self.invalid_attempt(bundle.write())

    def test_D136_handover_failed_and_final_preemption_timestamps_equal_qualification(self):
        for terminal in (19, 25, 22):
            details = [0, 16, 17, 18, terminal] + ([20] if terminal == 19 else [])
            for delta in (-1, 1):
                bundle = Bundle(self.directory, self.source).set_trace(details)
                bundle.marker(terminal)['t_us'] = (bundle.times[18] + delta) & U32
                self.invalid_attempt(bundle.write())

    def test_D136_frames_duty_and_ordinary_state_events_cannot_repair_missing_timing_tail(self):
        bundle = Bundle(self.directory, self.source).set_trace([0, 16, 17, 18])
        frame = list(CLEAN_FRAME)
        frame[1], frame[2], frame[9], frame[10] = 6, 3, 127, 127
        bundle.frames = [wire.frame(frame, ordinal=0)]
        bundle.events.extend([dict(t_us=bundle.times[19], ordinal=99, kind=3, detail=6, value=5),
                              dict(t_us=bundle.times[20], ordinal=100, kind=2, detail=3, value=0x7f7f)])
        _, attempt = self.one(bundle.renumber().write(), 'INCOMPLETE', 'INCOMPLETE')
        self.assertIsNone(attempt['handover_us'])
        self.assertIsNone(attempt['applied_us'])
        self.assertIsNone(attempt['elapsed_us'])

    def test_D136_invalid_packed_metadata_is_rejected_through_full_cohort_not_only_helper(self):
        for cue in (0, 65535, packed(1, 2, 1, 2), packed(3, 0, 1, 0), packed(3, 0, 2, 18),
                    packed(3, 0, 2, 16, True), packed(3, 1, 1, 2)):
            bundle = Bundle(self.directory, self.source)
            bundle.marker(18)['value'] = cue
            self.invalid_attempt(bundle.write())
        bundle = Bundle(self.directory, self.source, mode=1)
        bundle.marker(18)['value'] = packed(1, 1, 1, 2)
        self.invalid_attempt(bundle.write())
        bundle = Bundle(self.directory, self.source, mode=4)
        bundle.marker(18)['value'] = packed(4, 2, 2, 16)
        self.invalid_attempt(bundle.write())

    def test_D136_WAIT_zero_duty_and_DIRECT_current_front_with_snapshot_are_valid_cues(self):
        bundle = Bundle(self.directory, self.source, mode=6)
        frame = list(CLEAN_FRAME)
        frame[1], frame[2], frame[9], frame[10] = 4, 6, 0, 0
        bundle.frames = [wire.frame(frame, ordinal=0)]
        _, attempt = self.one(bundle.write())
        self.assertEqual(attempt['cue'], dict(mode=6, phase=4, cause=2, effective_mask=16, snapshot_front_present=False))
        bundle = Bundle(self.directory, self.source)
        bundle.marker(18)['value'] = packed(3, 0, 1, 2, True)
        _, attempt = self.one(bundle.write())
        self.assertIs(attempt['cue']['snapshot_front_present'], True)
        self.assertEqual(attempt['qualification'], 'QUALIFIED')
