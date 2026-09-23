"""Test D104 decoding from the frozen public contract and literal ABI only.

The author did not read tools/runtime_capture.py before authoring or freezing
these tests. The author also implemented the C++ Runner, so this is independent
of the Python decoder implementation, not a fresh-context C++ review.
All values below are synthetic local fixtures; external operations are forbidden.
"""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import importlib.util
import io
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
UINT32_MAX = 0xFFFFFFFF
HALF_RANGE = 0x80000000
REPORT_FIELDS = """schema_version byte_size phase failure boot_us first_s_us
first_d_us first_c_us last_s_us last_d_us last_a_us last_c_us elapsed_us epochs
missed_releases maximum_execution_us maximum_runner_us token_lo token_hi
runtime_phase runtime_fault transaction_phase transaction_fault robot_state
contract_faults escape_fault gate_fault receipt_flags input_absent_mask
initialization_complete recorder_phase frame_count event_count setup_enable_calls
setup_pwm_calls enable_low_calls pwm_zero_calls settle_calls clock_calls
enabled_requests nonzero_requests invalid_requests""".split()
STACK_FIELDS = """valid region_start region_size region_delta minimum_sp samples
sampled_headroom_bytes fault""".split()
REASONS = ["probe_failed", "runtime_state", "owner_fault", "source_state",
           "recorder_state", "nonzero_activity", "counts", "timing", "stack_invalid"]


def diagnostics(report=None, stack=None, sequence=2, tail=None, boot=10000):
    """Build exact little-endian words, independently of decoder implementation."""
    values = dict.fromkeys(REPORT_FIELDS, 0)
    values.update(schema_version=1, byte_size=192, phase=2, boot_us=boot,
                  first_s_us=(boot + 50) & UINT32_MAX,
                  first_d_us=(boot + 70) & UINT32_MAX,
                  first_c_us=(boot + 90) & UINT32_MAX,
                  last_s_us=(boot + 199999980) & UINT32_MAX,
                  last_d_us=(boot + 199999990) & UINT32_MAX,
                  last_a_us=(boot + 200000005) & UINT32_MAX,
                  last_c_us=(boot + 200000020) & UINT32_MAX,
                  elapsed_us=200000030, epochs=200001, maximum_execution_us=40,
                  maximum_runner_us=80, token_lo=200001, runtime_phase=1,
                  transaction_phase=1, receipt_flags=15, input_absent_mask=31,
                  setup_enable_calls=1, setup_pwm_calls=4, enable_low_calls=200002,
                  pwm_zero_calls=800008, settle_calls=200002, clock_calls=2400021)
    values.update(report or {})
    stack_values = dict(valid=1, region_start=0x20010000, region_size=32768,
                        region_delta=64, minimum_sp=0x20017530, samples=2400021,
                        sampled_headroom_bytes=30000, fault=0)
    stack_values.update(stack or {})
    words = [sequence] + [values[field] for field in REPORT_FIELDS] + [0] * 6
    words.extend(stack_values[field] for field in STACK_FIELDS)
    words.append(sequence if tail is None else tail)
    assert len(words) == 58
    return struct.pack("<58I", *words), values, stack_values


def import_without_actions():
    name = "independent_runtime_capture_test_module"
    specification = importlib.util.spec_from_file_location(name, ROOT / "tools/runtime_capture.py")
    module = importlib.util.module_from_spec(specification)
    stdout, stderr = io.StringIO(), io.StringIO()
    forbidden = AssertionError("Decoder import must not perform external actions")
    with ExitStack() as context:
        for action in ("run", "Popen", "call", "check_call", "check_output"):
            context.enter_context(mock.patch.object(subprocess, action, side_effect=forbidden))
        context.enter_context(mock.patch.object(socket, "socket", side_effect=forbidden))
        context.enter_context(mock.patch.object(socket, "create_connection", side_effect=forbidden))
        context.enter_context(mock.patch.object(os, "system", side_effect=forbidden))
        context.enter_context(mock.patch("builtins.input", side_effect=forbidden))
        context.enter_context(mock.patch.object(sys, "path", [str(ROOT / "tools"), *sys.path]))
        context.enter_context(mock.patch.object(sys, "argv", ["runtime_capture.py", "--not-a-run"]))
        context.enter_context(mock.patch.dict(sys.modules, {name: module}))
        context.enter_context(redirect_stdout(stdout))
        context.enter_context(redirect_stderr(stderr))
        specification.loader.exec_module(module)
    return module, stdout.getvalue(), stderr.getvalue()


class RuntimeDiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject, cls.stdout, cls.stderr = import_without_actions()

    def decode(self, report=None, stack=None, **kwargs):
        return self.subject.decode_diagnostics(diagnostics(report, stack, **kwargs)[0])

    def reasons(self, expected, report=None, stack=None, **kwargs):
        result = self.decode(report, stack, **kwargs)
        self.assertEqual(result["acceptance"], {"passed": not expected, "failures": expected})
        return result

    def reject(self, blob):
        with self.assertRaises(ValueError):
            self.subject.decode_diagnostics(blob)

    def test_import_is_passive(self):
        self.assertEqual(self.stdout, "")
        self.assertEqual(self.stderr, "")

    def test_decoder_performs_no_io_and_returns_repeatable_values(self):
        blob, expected_report, expected_stack = diagnostics()
        forbidden = AssertionError("Pure decode must not perform I/O")
        with ExitStack() as context:
            for action in ("run", "Popen", "call", "check_call", "check_output"):
                context.enter_context(mock.patch.object(subprocess, action, side_effect=forbidden))
            for action in ("read_bytes", "read_text", "write_bytes", "write_text"):
                context.enter_context(mock.patch.object(Path, action, side_effect=forbidden))
            context.enter_context(mock.patch("builtins.open", side_effect=forbidden))
            context.enter_context(mock.patch.object(socket, "socket", side_effect=forbidden))
            context.enter_context(mock.patch.object(os, "system", side_effect=forbidden))
            first = self.subject.decode_diagnostics(blob)
            first["report"]["epochs"] = 99
            first["stack"]["samples"] = 0
            second = self.subject.decode_diagnostics(blob)
        self.assertEqual(second["report"], expected_report)
        self.assertEqual(second["stack"], expected_stack)

    def test_literal_232_byte_fixture_preserves_every_public_field(self):
        blob, expected_report, expected_stack = diagnostics()
        self.assertEqual(len(REPORT_FIELDS), 42)
        self.assertEqual(len(blob), 232)
        result = self.subject.decode_diagnostics(blob)
        self.assertEqual(set(result), {"sequence", "report", "stack", "acceptance"})
        self.assertEqual(result["sequence"], 2)
        self.assertEqual(result["report"], expected_report)
        self.assertEqual(result["stack"], expected_stack)
        self.assertEqual(result["acceptance"], {"passed": True, "failures": []})

    def test_exact_immutable_bytes_and_exact_length_required(self):
        blob = diagnostics()[0]
        for bad in (None, "text", 232, True, list(blob), bytearray(blob), memoryview(blob),
                    blob[:-1], blob + b"\0", b"", blob * 2):
            with self.subTest(kind=type(bad).__name__, size=getattr(bad, "__len__", lambda: 0)()):
                self.reject(bad)

    def test_matching_nonzero_even_sequences_required(self):
        for front, tail in ((0, 0), (1, 1), (3, 3), (2, 4), (4, 2),
                            (2, 0), (UINT32_MAX, UINT32_MAX)):
            with self.subTest(front=front, tail=tail):
                self.reject(diagnostics(sequence=front, tail=tail)[0])
        for sequence in (2, 4, 0x10000000, 0xFFFFFFFE):
            with self.subTest(sequence=sequence):
                self.assertEqual(self.decode(sequence=sequence)["sequence"], sequence)

    def test_schema_size_reserved_words_and_endian_are_structural(self):
        for change in ({"schema_version": 0}, {"schema_version": 2},
                       {"byte_size": 188}, {"byte_size": 196}, {"byte_size": 232}):
            with self.subTest(change=change):
                self.reject(diagnostics(report=change)[0])
        original = diagnostics()[0]
        for word in range(43, 49):
            for value in (1, UINT32_MAX):
                with self.subTest(word=word, value=value):
                    changed = bytearray(original)
                    struct.pack_into("<I", changed, 4 * word, value)
                    self.reject(bytes(changed))
        self.reject(struct.pack(">58I", *struct.unpack("<58I", original)))

    def test_only_matching_terminal_phase_failure_pairs_decode(self):
        for phase in (0, 1, 4, UINT32_MAX):
            with self.subTest(phase=phase):
                self.reject(diagnostics(report={"phase": phase})[0])
        for failure in (1, 12, 13, UINT32_MAX):
            with self.subTest(frozen_failure=failure):
                self.reject(diagnostics(report={"failure": failure})[0])
        for failure in (0, 13, UINT32_MAX):
            with self.subTest(failed_failure=failure):
                self.reject(diagnostics(report={"phase": 3, "failure": failure})[0])
        for failure in range(1, 13):
            with self.subTest(valid_failure=failure):
                result = self.reasons(["probe_failed"], {"phase": 3, "failure": failure})
                self.assertEqual(result["report"]["failure"], failure)

    def test_unknown_report_enum_mask_and_boolean_domains_reject(self):
        maxima = {"runtime_phase": 4, "runtime_fault": 5, "transaction_phase": 4,
                  "transaction_fault": 6, "robot_state": 11, "contract_faults": 1023,
                  "escape_fault": 4, "gate_fault": 6, "receipt_flags": 15,
                  "input_absent_mask": 31, "initialization_complete": 1, "recorder_phase": 4}
        for name, maximum in maxima.items():
            for value in (maximum + 1, UINT32_MAX):
                with self.subTest(field=name, invalid=value):
                    self.reject(diagnostics(report={name: value})[0])
            for value in (0, maximum):
                with self.subTest(field=name, boundary=value):
                    self.assertEqual(self.decode({name: value})["report"][name], value)

    def test_unknown_stack_boolean_and_fault_domains_reject(self):
        for name, maximum in (("valid", 1), ("fault", 5)):
            for value in (maximum + 1, UINT32_MAX):
                with self.subTest(field=name, invalid=value):
                    self.reject(diagnostics(stack={name: value})[0])
        for value in range(1, 6):
            with self.subTest(fault=value):
                self.reasons(["stack_invalid"], stack={"fault": value})

    def test_runtime_owner_and_source_reasons_are_distinct(self):
        groups = {"runtime_state": {"runtime_phase": [0, 2, 3, 4],
                                    "transaction_phase": [0, 2, 3, 4],
                                    "robot_state": range(1, 12)},
                  "owner_fault": {"runtime_fault": range(1, 6),
                                  "transaction_fault": range(1, 7),
                                  "contract_faults": [1 << bit for bit in range(10)] + [1023],
                                  "escape_fault": range(1, 5), "gate_fault": range(1, 7),
                                  "receipt_flags": range(15)},
                  "source_state": {"input_absent_mask": range(31),
                                   "initialization_complete": [1]}}
        for reason, fields in groups.items():
            for name, values in fields.items():
                for value in values:
                    with self.subTest(reason=reason, field=name, value=value):
                        self.reasons([reason], {name: value})

    def test_recorder_and_nonzero_request_failures_preserve_values(self):
        for name, values in {"recorder_phase": range(1, 5), "frame_count": [1, UINT32_MAX],
                             "event_count": [1, UINT32_MAX]}.items():
            for value in values:
                with self.subTest(field=name, value=value):
                    result = self.reasons(["recorder_state"], {name: value})
                    self.assertEqual(result["report"][name], value)
        for name in ("enabled_requests", "nonzero_requests", "invalid_requests"):
            for value in (1, UINT32_MAX):
                with self.subTest(field=name, value=value):
                    self.reasons(["nonzero_activity"], {name: value})

    def test_exact_epoch_token_setup_and_write_counts(self):
        for name, values in {"epochs": [0, 1, 199999, UINT32_MAX],
                             "missed_releases": [1, UINT32_MAX],
                             "token_lo": [0, 200000, 200002], "token_hi": [1, UINT32_MAX],
                             "setup_enable_calls": [0, 2, UINT32_MAX],
                             "setup_pwm_calls": [0, 3, 5],
                             "enable_low_calls": [0, 200001, 200003],
                             "pwm_zero_calls": [0, 800004, 800009],
                             "settle_calls": [0, 200001, 200003],
                             "clock_calls": [0, UINT32_MAX]}.items():
            for value in values:
                with self.subTest(field=name, value=value):
                    self.reasons(["counts"], {name: value})
        for epochs in (200000, 200001, 200123):
            with self.subTest(valid_epochs=epochs):
                self.reasons([], {"epochs": epochs, "token_lo": epochs,
                                  "enable_low_calls": epochs + 1,
                                  "pwm_zero_calls": 4 * (epochs + 1),
                                  "settle_calls": epochs + 1})
        self.reasons([], {"clock_calls": 1})
        self.reasons([], {"clock_calls": UINT32_MAX - 1})

    def test_count_products_do_not_wrap_into_false_success(self):
        epochs = 0x40000000
        self.reasons(["counts"], {"epochs": epochs, "token_lo": epochs,
                                  "enable_low_calls": epochs + 1,
                                  "settle_calls": epochs + 1, "pwm_zero_calls": 4})

    def test_elapsed_and_completion_window_boundaries(self):
        for elapsed in (0, 199999999, 200000019, 201000000, HALF_RANGE, UINT32_MAX):
            with self.subTest(elapsed=elapsed):
                self.reasons(["timing"], {"elapsed_us": elapsed})
        self.reasons([], {"elapsed_us": 200000020})
        self.reasons([], {"elapsed_us": 200999999})
        for completed in (199999999, 201000000, HALF_RANGE):
            with self.subTest(final_offset=completed):
                self.reasons(["timing"], {"last_c_us": (10000 + completed) & UINT32_MAX})
        self.reasons([], {"last_a_us": 200009995, "last_c_us": 200010000,
                          "elapsed_us": 200000000})

    def test_first_epoch_deadline_exact_boundary(self):
        self.reasons([], {"first_s_us": 1009959, "first_d_us": 1009970,
                          "first_c_us": 1009999})
        self.reasons(["timing"], {"first_s_us": 1009960, "first_d_us": 1009980,
                                  "first_c_us": 1010000})

    def test_every_first_and_last_clock_order_is_checked(self):
        changes = [{"first_s_us": 10071}, {"first_d_us": 10049},
                   {"first_d_us": 10091}, {"first_c_us": 10069},
                   {"last_s_us": 200009991}, {"last_d_us": 200009979},
                   {"last_d_us": 200010006}, {"last_a_us": 200009989},
                   {"last_a_us": 200010021}, {"last_c_us": 200010004},
                   {"first_s_us": 10000 + 199999970,
                    "first_d_us": 10000 + 199999990, "first_c_us": 10000 + 200000010}]
        for change in changes:
            with self.subTest(change=change):
                self.reasons(["timing"], change)

    def test_every_timestamp_must_be_forward_from_boot_within_half_range(self):
        for name in ("first_s_us", "first_d_us", "first_c_us", "last_s_us",
                     "last_d_us", "last_a_us", "last_c_us"):
            for offset in (UINT32_MAX, HALF_RANGE, HALF_RANGE + 1):
                with self.subTest(field=name, offset=offset):
                    self.reasons(["timing"], {name: (10000 + offset) & UINT32_MAX})

    def test_timing_maxima_nonzero_cover_both_transactions_and_runner(self):
        for name, values in {"maximum_execution_us": [0, 1, 39, HALF_RANGE, UINT32_MAX],
                             "maximum_runner_us": [0, 1, 39, HALF_RANGE, UINT32_MAX]}.items():
            for value in values:
                with self.subTest(field=name, value=value):
                    self.reasons(["timing"], {name: value})
        self.reasons([], {"maximum_runner_us": 40})
        self.reasons(["timing"], {"first_c_us": 10100})
        self.reasons(["timing"], {"last_s_us": 200009970})
        self.reasons([], {"maximum_execution_us": HALF_RANGE - 1,
                          "maximum_runner_us": HALF_RANGE - 1})

    def test_natural_wrap_and_boundary_zero_timestamps_are_valid(self):
        for boot in (0, 1, 0xF8000000, 0xFFFFFF00, UINT32_MAX):
            with self.subTest(boot=boot):
                blob, expected, _ = diagnostics(boot=boot)
                result = self.subject.decode_diagnostics(blob)
                self.assertEqual(result["report"], expected)
                self.assertEqual(result["acceptance"], {"passed": True, "failures": []})
        self.reasons([], boot=0, report={"first_s_us": 0, "first_d_us": 20,
                                        "first_c_us": 40})

    def test_stack_metadata_and_headroom_each_fail_without_normalization(self):
        changes = [{"valid": 0}, {"fault": 1}, {"region_start": 0x20010001},
                   {"region_start": 0x1FFFFFFC}, {"region_start": 0x200C0000},
                   {"region_size": 0}, {"region_size": 0xC0000},
                   {"region_size": UINT32_MAX}, {"region_delta": 32769},
                   {"region_delta": UINT32_MAX}, {"minimum_sp": 0x20017531},
                   {"minimum_sp": 0x2000FFFC}, {"minimum_sp": 0x20017FC4},
                   {"samples": 0}, {"samples": UINT32_MAX},
                   {"sampled_headroom_bytes": 29999}, {"sampled_headroom_bytes": 30001}]
        for change in changes:
            with self.subTest(change=change):
                result = self.reasons(["stack_invalid"], stack=change)
                for name, value in change.items():
                    self.assertEqual(result["stack"][name], value)

    def test_stack_sram_and_stack_pointer_inclusive_boundaries(self):
        for stack in ({"region_start": 0x20000000, "region_size": 0xC0000,
                       "region_delta": 0, "minimum_sp": 0x200C0000,
                       "sampled_headroom_bytes": 0xC0000},
                      {"region_start": 0x200BFFFC, "region_size": 4,
                       "region_delta": 4, "minimum_sp": 0x200BFFFC,
                       "sampled_headroom_bytes": 0},
                      {"minimum_sp": 0x20010000, "sampled_headroom_bytes": 0},
                      {"minimum_sp": 0x20017FC0, "sampled_headroom_bytes": 32704},
                      {"samples": 1}, {"samples": UINT32_MAX - 1}):
            with self.subTest(stack=stack):
                self.reasons([], stack=stack)

    def test_all_reasons_have_deterministic_order_and_no_duplicates(self):
        report = {"phase": 3, "failure": 7, "runtime_phase": 3,
                  "transaction_phase": 4, "robot_state": 10, "runtime_fault": 2,
                  "transaction_fault": 6, "contract_faults": 1023, "gate_fault": 6,
                  "receipt_flags": 0, "input_absent_mask": 0, "initialization_complete": 1,
                  "recorder_phase": 4, "frame_count": 1, "event_count": 2,
                  "enabled_requests": 1, "nonzero_requests": 1, "invalid_requests": 1,
                  "epochs": 1, "clock_calls": 0, "elapsed_us": 0}
        self.reasons(REASONS, report, {"valid": 0, "fault": 4, "samples": 0})

    def test_failed_partial_transaction_decodes_and_retains_first_firmware_failure(self):
        changes = {"phase": 3, "failure": 1, "runtime_phase": 3, "runtime_fault": 2,
                   "transaction_phase": 4, "transaction_fault": 6, "gate_fault": 6,
                   "last_s_us": 1234567, "last_d_us": 0, "last_a_us": 0,
                   "last_c_us": 0, "epochs": 3, "token_lo": 0, "token_hi": 0,
                   "receipt_flags": 12, "elapsed_us": 1234567}
        expected = ["probe_failed", "runtime_state", "owner_fault", "counts", "timing"]
        result = self.reasons(expected, changes)
        for name, value in changes.items():
            self.assertEqual(result["report"][name], value)

    def test_structural_error_is_rejected_even_when_semantic_failure_exists(self):
        for report in ({"phase": 3, "failure": 1, "gate_fault": 7},
                       {"phase": 3, "failure": 12, "receipt_flags": 16},
                       {"phase": 3, "failure": 3, "runtime_phase": 5}):
            with self.subTest(report=report):
                self.reject(diagnostics(report=report)[0])


if __name__ == "__main__":
    unittest.main()
