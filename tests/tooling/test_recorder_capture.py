"""Exercise D091 capture APIs from literal public diagnostic layout and bounds.

Independent author reads contracts and headers, never the new implementation body.
All inputs are local fixtures and all external operations are forbidden or mocked.
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
import tempfile
import unittest
from unittest import mock
from tests.fixtures import recorder_heap_vectors as heap_fixture

ROOT = Path(__file__).resolve().parents[2]

REPORT_FIELDS = """schema_version byte_size phase failure boot_us last_us release_us stop_us
elapsed_us ticks missed_slots max_lateness_us max_step_us nonzero_pwm enabled_en
configure_calls crc32 checksum_rows source_phase frame_count event_count epoch_lo
epoch_hi last_frame_lo last_frame_hi mode observed_results missing_results
rejected_results identity_rejected malformed_batches event_semantic_rejected
upstream_event_rejected upstream_event_invalid source_regressions skipped_frames
timing_ticks_lo timing_ticks_hi timing_overruns_lo timing_overruns_hi timing_max_us
timing_saturated upstream_event_overflow timing_incomplete recording_incomplete
go_seen final_frame_missing interrupted terminal_exhausted frame_overwritten
frame_rejected_status frame_clamped frame_invalid event_overflow event_rejected
incomplete robot_faults gate_fault""".split()
STACK_FIELDS = "valid region_start region_size region_delta minimum_sp samples sampled_headroom_bytes fault".split()
BOOLEAN_FIELDS = "timing_saturated upstream_event_overflow timing_incomplete recording_incomplete go_seen final_frame_missing interrupted terminal_exhausted event_overflow incomplete".split()


def diagnostics(report=None, stack=None, sequence=2, tail=None):
    words = [0] * 74
    words[0] = sequence
    words[73] = sequence if tail is None else tail
    values = dict.fromkeys(REPORT_FIELDS, 0)
    values.update(schema_version=1, byte_size=256, phase=4, boot_us=1000,
                  release_us=69000, stop_us=200069000, last_us=200070000,
                  elapsed_us=200000000, ticks=200070, configure_calls=5,
                  crc32=0x12345678, checksum_rows=5011, source_phase=3,
                  frame_count=5001, event_count=10, epoch_lo=69,
                  last_frame_lo=200069, mode=1, observed_results=200002,
                  timing_ticks_lo=194901, go_seen=1)
    values.update(report or {})
    for index, name in enumerate(REPORT_FIELDS, 1):
        words[index] = values[name]
    stack_values = dict(valid=1, region_start=0x20002000, region_size=32768,
                        region_delta=0, minimum_sp=0x20009000, samples=42,
                        sampled_headroom_bytes=28672, fault=0)
    stack_values.update(stack or {})
    for index, name in enumerate(STACK_FIELDS, 65):
        words[index] = stack_values[name]
    return struct.pack("<74I", *words), values, stack_values


def import_without_actions():
    name = "independent_recorder_capture_test_module"
    specification = importlib.util.spec_from_file_location(name, ROOT / "tools/recorder_capture.py")
    module = importlib.util.module_from_spec(specification)
    stdout, stderr = io.StringIO(), io.StringIO()
    forbidden = AssertionError("No external action is allowed during import")
    with ExitStack() as context:
        for target in ("run", "Popen", "call", "check_call", "check_output"):
            context.enter_context(mock.patch.object(subprocess, target, side_effect=forbidden))
        context.enter_context(mock.patch.object(socket, "socket", side_effect=forbidden))
        context.enter_context(mock.patch.object(socket, "create_connection", side_effect=forbidden))
        context.enter_context(mock.patch.object(os, "system", side_effect=forbidden))
        context.enter_context(mock.patch("builtins.input", side_effect=forbidden))
        context.enter_context(mock.patch.object(sys, "path", [str(ROOT / "tools"), *sys.path]))
        context.enter_context(mock.patch.object(sys, "argv", ["recorder_capture.py", "--not-a-run"]))
        context.enter_context(mock.patch.dict(sys.modules, {name: module}))
        context.enter_context(redirect_stdout(stdout))
        context.enter_context(redirect_stderr(stderr))
        specification.loader.exec_module(module)
    return module, stdout.getvalue(), stderr.getvalue()


class RecorderDiagnosticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject, cls.stdout, cls.stderr = import_without_actions()

    def reject(self, blob):
        with self.assertRaises((ValueError, TypeError)):
            self.subject.decode_diagnostics(blob)

    def test_import_has_no_output_commands_network_or_main(self):
        self.assertEqual(self.stdout, "")
        self.assertEqual(self.stderr, "")

    def test_literal_296_byte_fixture_preserves_all_named_words(self):
        blob, report, stack = diagnostics()
        result = self.subject.decode_diagnostics(blob)
        self.assertEqual(result["sequence"], 2)
        for field, value in report.items():
            self.assertEqual(result["report"][field], value, field)
        self.assertEqual(result["stack"], stack)

    def test_exact_type_and_size_required(self):
        blob, _, _ = diagnostics()
        for bad in (None, "text", 296, list(blob), bytearray(blob), blob[:-1], blob + b"\0", b""):
            with self.subTest(type=type(bad).__name__):
                self.reject(bad)

    def test_nonzero_even_matching_sequence_required(self):
        for front, tail in ((0, 0), (1, 1), (3, 3), (2, 4), (4, 2), (2, 0), (0xFFFFFFFF, 0xFFFFFFFF)):
            with self.subTest(front=front, tail=tail):
                self.reject(diagnostics(sequence=front, tail=tail)[0])
        self.assertEqual(self.subject.decode_diagnostics(diagnostics(sequence=0xFFFFFFFE)[0])["sequence"],
                         0xFFFFFFFE)

    def test_schema_size_and_reserved_words_reject(self):
        for changes in ({"schema_version": 0}, {"schema_version": 2}, {"byte_size": 252}, {"byte_size": 296}):
            with self.subTest(changes=changes):
                self.reject(diagnostics(report=changes)[0])
        blob, _, _ = diagnostics()
        for index in range(59, 65):
            with self.subTest(reserved_word=index):
                changed = bytearray(blob)
                struct.pack_into("<I", changed, index * 4, 1)
                self.reject(bytes(changed))

    def test_only_terminal_phase_and_matching_failure_accepted(self):
        for phase in (0, 1, 2, 3, 6, 0xFFFFFFFF):
            with self.subTest(phase=phase):
                self.reject(diagnostics(report={"phase": phase})[0])
        self.reject(diagnostics(report={"failure": 1})[0])
        self.reject(diagnostics(report={"phase": 5, "failure": 0})[0])
        self.reject(diagnostics(report={"phase": 5, "failure": 9})[0])
        for failure in range(1, 9):
            with self.subTest(failure=failure):
                result = self.subject.decode_diagnostics(diagnostics(report={"phase": 5, "failure": failure})[0])
                self.assertEqual(result["report"]["failure"], failure)

    def test_bool_words_and_known_enums_only(self):
        for name in BOOLEAN_FIELDS:
            for value in (2, 0xFFFFFFFF):
                with self.subTest(field=name, value=value):
                    self.reject(diagnostics(report={name: value})[0])
        for name, value in (("source_phase", 5), ("mode", 7), ("gate_fault", 8)):
            with self.subTest(field=name):
                self.reject(diagnostics(report={name: value})[0])
        self.reject(diagnostics(stack={"valid": 2})[0])

    def test_storage_capacity_boundaries_are_not_expected_frame_counts(self):
        for frames, events in ((0, 0), (1, 1), (5000, 4095), (5001, 4096)):
            with self.subTest(frames=frames, events=events):
                result = self.subject.decode_diagnostics(diagnostics(report={
                    "frame_count": frames, "event_count": events,
                    "checksum_rows": frames + events})[0])
                self.assertEqual(result["report"]["frame_count"], frames)
                self.assertEqual(result["report"]["event_count"], events)
        for changes in ({"frame_count": 5002}, {"event_count": 4097}):
            self.reject(diagnostics(report=changes)[0])

    def test_frozen_requires_sealed_source_and_complete_checksum_but_failed_may_be_partial(self):
        for source_phase in (0, 1, 2, 4):
            with self.subTest(source_phase=source_phase):
                self.reject(diagnostics(report={"source_phase": source_phase})[0])
        for rows in (0, 5010, 5012, 0xFFFFFFFF):
            with self.subTest(rows=rows):
                self.reject(diagnostics(report={"checksum_rows": rows})[0])
        for source_phase in range(5):
            with self.subTest(failed_source=source_phase):
                result = self.subject.decode_diagnostics(diagnostics(report={
                    "phase": 5, "failure": 7, "source_phase": source_phase, "checksum_rows": 0})[0])
                self.assertEqual(result["report"]["checksum_rows"], 0)
                self.assertEqual(result["report"]["source_phase"], source_phase)

    def test_losses_and_failed_experiment_are_preserved_not_reported_clean(self):
        updates = {name: index + 1 for index, name in enumerate([
            "missed_slots", "max_lateness_us", "nonzero_pwm", "enabled_en", "missing_results",
            "rejected_results", "identity_rejected", "malformed_batches", "event_semantic_rejected",
            "upstream_event_rejected", "upstream_event_invalid", "source_regressions", "skipped_frames",
            "frame_overwritten", "frame_rejected_status", "frame_clamped", "frame_invalid", "event_rejected"])}
        updates.update(phase=5, failure=3, incomplete=1, timing_incomplete=1,
                       recording_incomplete=1, event_overflow=1, upstream_event_overflow=1,
                       final_frame_missing=1, interrupted=1, terminal_exhausted=1)
        result = self.subject.decode_diagnostics(diagnostics(report=updates)[0])
        for name, value in updates.items():
            self.assertEqual(result["report"][name], value, name)

    def test_valid_stack_bounds_alignment_and_consistency(self):
        cases = [
            {"fault": 1}, {"samples": 0}, {"region_start": 0x20002001},
            {"region_size": 32767}, {"region_delta": 32769},
            {"region_start": 0x1FFFFFF8}, {"region_start": 0x200BF000},
            {"minimum_sp": 0x20001FFC}, {"minimum_sp": 0x2000A004},
            {"minimum_sp": 0x20009001}, {"sampled_headroom_bytes": 28671},
            {"region_delta": 8192},
        ]
        for change in cases:
            with self.subTest(change=change):
                self.reject(diagnostics(stack=change)[0])

    def test_stack_boundary_samples_and_unavailable_stack_remain_explicit(self):
        for sp, headroom in ((0x20002000, 0), (0x2000A000, 32768)):
            with self.subTest(sp=sp):
                result = self.subject.decode_diagnostics(diagnostics(stack={
                    "minimum_sp": sp, "sampled_headroom_bytes": headroom})[0])
                self.assertEqual(result["stack"]["sampled_headroom_bytes"], headroom)
        unavailable = dict.fromkeys(STACK_FIELDS, 0)
        unavailable["fault"] = 1
        result = self.subject.decode_diagnostics(diagnostics(stack=unavailable)[0])
        self.assertEqual(result["stack"], unavailable)


class FakeCapture:
    """Literal public capture_values fixture, never a real memory reader."""
    def __init__(self, folder, overrides=None):
        self.folder = Path(folder)
        self.base = 0x20060000
        self.symbols = {"recorderDiagnostics": {"offset": 128, "size": 296}}
        self.report = {"flash_identity_verified": True,
                       "extension": {"bss_address": self.base},
                       "layout": {"bss_size": 4096, "symbols": self.symbols}}
        self.calls = []
        self.overrides = overrides or {}

    def read(self, label, address, size, region="ram"):
        self.calls.append((label, address, size, region))
        if label in self.overrides:
            return self.overrides[label]
        if label.startswith("diagnostics-"):
            assert (address, size, region) == (self.base + 128, 296, "ram")
            return diagnostics()[0]
        if label.startswith("heap-descriptor-"):
            assert (address, size, region) == (0x2000112C, 24, "ram")
            return struct.pack("<6I", 0x20013890, 0x20013890, 262144, 0, 0, 0)
        parts = label.split("-")
        assert len(parts) == 3 and parts[0] == "pool" and parts[1] in ("1", "2")
        block = int(parts[2])
        assert 0 <= block <= 15
        assert (address, size, region) == (0x20013890 + block * 16384, 16384, "ram")
        return heap_fixture.all_free()[block * 16384:(block + 1) * 16384]


class RecorderCaptureSequenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject, _, _ = import_without_actions()

    def test_exact_bounded_sequence_and_raw_pool_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = FakeCapture(folder)
            self.assertIsNone(self.subject.capture_values(capture, capture.base, capture.symbols))
            self.assertEqual(len(capture.calls), 36)
            self.assertEqual(capture.calls[0][0], "diagnostics-first")
            self.assertEqual(capture.calls[1][0], "heap-descriptor-first")
            self.assertEqual([call[0] for call in capture.calls[2:18]],
                             [f"pool-1-{index:02d}" for index in range(16)])
            self.assertEqual([call[0] for call in capture.calls[18:34]],
                             [f"pool-2-{index:02d}" for index in range(16)])
            self.assertEqual([call[0] for call in capture.calls[-2:]],
                             ["heap-descriptor-last", "diagnostics-last"])
            self.assertEqual((Path(folder) / "pool-first.bin").read_bytes(), heap_fixture.all_free())
            self.assertEqual((Path(folder) / "pool-second.bin").read_bytes(), heap_fixture.all_free())
            self.assertEqual(capture.report["heap"]["free_payload_bytes"], 262052)
            self.assertEqual(capture.report["heap"]["consistency"], "CONSISTENT_SAMPLED")
            self.assertEqual(capture.report["diagnostics"]["report"]["frame_count"], 5001)

    def test_nonterminal_or_torn_first_diagnostic_prevents_heap_reads(self):
        for value in (diagnostics(report={"phase": 1})[0], diagnostics(sequence=3)[0]):
            with self.subTest(value=value[:4]), tempfile.TemporaryDirectory() as folder:
                capture = FakeCapture(folder, {"diagnostics-first": value})
                with self.assertRaises(ValueError):
                    self.subject.capture_values(capture, capture.base, capture.symbols)
                self.assertEqual(len(capture.calls), 1)

    def test_descriptor_fields_each_bound_to_pinned_pool_before_pool_reads(self):
        for field, value in ((0, 0), (0, 0x20013898), (1, 0x2000AF90), (2, 262136)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as folder:
                words = [0x20013890, 0x20013890, 262144, 0, 0, 0]
                words[field] = value
                capture = FakeCapture(folder, {"heap-descriptor-first": struct.pack("<6I", *words)})
                with self.assertRaises(ValueError):
                    self.subject.capture_values(capture, capture.base, capture.symbols)
                self.assertEqual(len(capture.calls), 2)

    def test_changed_metadata_rejects_and_retains_both_raw_pool_snapshots(self):
        overrides = {f"pool-2-{index:02d}": heap_fixture.all_used()[index * 16384:(index + 1) * 16384]
                     for index in range(16)}
        with tempfile.TemporaryDirectory() as folder:
            capture = FakeCapture(folder, overrides)
            with self.assertRaises(ValueError):
                self.subject.capture_values(capture, capture.base, capture.symbols)
            self.assertEqual((Path(folder) / "pool-first.bin").read_bytes(), heap_fixture.all_free())
            self.assertEqual((Path(folder) / "pool-second.bin").read_bytes(), heap_fixture.all_used())

    def test_payload_change_allows_sampled_metadata_consistency(self):
        second = bytearray(heap_fixture.all_free())
        second[100] = 0xA5
        with tempfile.TemporaryDirectory() as folder:
            capture = FakeCapture(folder, {"pool-2-00": bytes(second[:16384])})
            self.subject.capture_values(capture, capture.base, capture.symbols)
            self.assertEqual(capture.report["heap"]["consistency"], "CONSISTENT_SAMPLED")
            self.assertNotEqual(capture.report["heap"]["snapshot_sha256"],
                                capture.report["heap"]["second_snapshot_sha256"])

    def test_last_descriptor_or_diagnostic_must_match_exactly(self):
        variants = [
            {"heap-descriptor-last": struct.pack("<6I", 0x20013890, 0x20013890, 262144, 1, 0, 0)},
            {"diagnostics-last": diagnostics(sequence=4)[0]},
            {"diagnostics-last": diagnostics(report={"missed_slots": 1})[0]},
        ]
        for overrides in variants:
            with self.subTest(labels=list(overrides)), tempfile.TemporaryDirectory() as folder:
                capture = FakeCapture(folder, overrides)
                with self.assertRaises(ValueError):
                    self.subject.capture_values(capture, capture.base, capture.symbols)
                self.assertTrue((Path(folder) / "pool-first.bin").exists())
                self.assertTrue((Path(folder) / "pool-second.bin").exists())

    def test_failed_experiment_with_loss_is_still_captured_as_failed_evidence(self):
        blob = diagnostics(report={"phase": 5, "failure": 7, "incomplete": 1,
                                   "skipped_frames": 13, "final_frame_missing": 1})[0]
        with tempfile.TemporaryDirectory() as folder:
            capture = FakeCapture(folder, {"diagnostics-first": blob, "diagnostics-last": blob})
            self.subject.capture_values(capture, capture.base, capture.symbols)
            self.assertEqual(capture.report["diagnostics"]["report"]["failure"], 7)
            self.assertEqual(capture.report["diagnostics"]["report"]["skipped_frames"], 13)
            self.assertEqual(capture.report["diagnostics"]["report"]["incomplete"], 1)


class RecorderReadBoundsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject, _, _ = import_without_actions()

    def capture(self, folder, verified=True):
        reference = FakeCapture(folder)
        result = self.subject.Capture(Path(folder), reference.report)
        result.identities_verified = verified
        result.binary_size = 65536
        return result

    @staticmethod
    def write_fixture(argv, attach=False):
        # Public command shape: dump_image {local_path} address size.
        del attach
        command = argv[4]
        path_text, address_size = command[len("dump_image {"):].split("} ", 1)
        _, size = address_size.split()
        Path(path_text).write_bytes(bytes(int(size)))

    def test_ram_requires_identity_and_flash_proof_before_external_command(self):
        with tempfile.TemporaryDirectory() as folder:
            for identity, flash in ((False, True), (True, False), (False, False)):
                with self.subTest(identity=identity, flash=flash):
                    capture = self.capture(folder, identity)
                    capture.report["flash_identity_verified"] = flash
                    with mock.patch.object(capture, "run", side_effect=AssertionError("forbidden")):
                        with self.assertRaises(ValueError):
                            capture.read("heap-descriptor-first", 0x2000112C, 24)

    def test_exact_allowed_descriptor_diagnostic_and_pool_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder)
            with mock.patch.object(capture, "run", side_effect=self.write_fixture):
                for label, address, size in [("heap-descriptor-first", 0x2000112C, 24),
                                              ("diagnostics-first", 0x20060080, 296),
                                              ("pool-1-00", 0x20013890, 16384),
                                              ("pool-2-15", 0x2004F890, 16384)]:
                    with self.subTest(label=label):
                        self.assertEqual(capture.read(label, address, size), bytes(size))
            self.assertEqual(capture.read_count, 4)
            self.assertEqual(capture.read_bytes, 33088)

    def test_unknown_labels_wrong_addresses_sizes_and_regions_reject(self):
        cases = [
            ("arbitrary", 0x20013890, 16384, "ram"),
            ("heap-descriptor-first", 0x20001130, 24, "ram"),
            ("heap-descriptor-first", 0x2000112C, 28, "ram"),
            ("diagnostics-first", 0x20060084, 296, "ram"),
            ("diagnostics-first", 0x20060080, 300, "ram"),
            ("pool-1-00", 0x20013898, 16384, "ram"),
            ("pool-1-00", 0x20013890, 16385, "ram"),
            ("pool-1-00", 0x20013890, 16380, "ram"),
            ("pool-1-16", 0x20053890, 16384, "ram"),
            ("pool-3-00", 0x20013890, 16384, "ram"),
            ("pool-1-00", 0x20013890, 16384, "flash"),
            ("pool-1-00", -1, 16384, "ram"),
            ("pool-1-00", 1 << 64, 16384, "ram"),
        ]
        with tempfile.TemporaryDirectory() as folder:
            for label, address, size, region in cases:
                with self.subTest(label=label, address=address, size=size, region=region):
                    capture = self.capture(folder)
                    with mock.patch.object(capture, "run", side_effect=AssertionError("forbidden")):
                        with self.assertRaises(ValueError):
                            capture.read(label, address, size, region=region)

    def test_read_count_and_total_bytes_have_inclusive_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder)
            capture.read_count = 47
            with mock.patch.object(capture, "run", side_effect=self.write_fixture) as run:
                capture.read("heap-descriptor-first", 0x2000112C, 24)
                self.assertEqual(capture.read_count, 48)
                with self.assertRaises(ValueError):
                    capture.read("heap-descriptor-last", 0x2000112C, 24)
                self.assertEqual(run.call_count, 1)
            capture = self.capture(folder)
            capture.read_bytes = 2097152 - 24
            with mock.patch.object(capture, "run", side_effect=self.write_fixture) as run:
                capture.read("heap-descriptor-first", 0x2000112C, 24)
                self.assertEqual(capture.read_bytes, 2097152)
                with self.assertRaises(ValueError):
                    capture.read("heap-descriptor-last", 0x2000112C, 24)
                self.assertEqual(run.call_count, 1)

    def test_failed_memory_command_still_consumes_read_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder)
            with mock.patch.object(capture, "run", side_effect=ValueError("synthetic command failure")):
                with self.assertRaises(ValueError):
                    capture.read("pool-1-00", 0x20013890, 16384)
            self.assertEqual(capture.read_count, 1)
            self.assertEqual(capture.read_bytes, 16384)

    def test_each_read_purpose_is_admitted_once_even_if_first_command_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            for fails in (False, True):
                with self.subTest(first_command_fails=fails):
                    isolated = Path(folder) / str(fails)
                    isolated.mkdir()
                    capture = self.capture(isolated)
                    effect = ValueError("synthetic failure") if fails else self.write_fixture
                    with mock.patch.object(capture, "run", side_effect=effect) as run:
                        if fails:
                            with self.assertRaises(ValueError):
                                capture.read("heap-descriptor-first", 0x2000112C, 24)
                        else:
                            capture.read("heap-descriptor-first", 0x2000112C, 24)
                        with self.assertRaises(ValueError):
                            capture.read("heap-descriptor-first", 0x2000112C, 24)
                        self.assertEqual(run.call_count, 1)

    def test_short_read_is_rejected_without_erasing_raw_fragment(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder)
            expected = Path(folder) / "00-heap-descriptor-first.bin"
            def short_read(argv, attach=False):
                del argv, attach
                expected.write_bytes(b"X" * 23)
            with mock.patch.object(capture, "run", side_effect=short_read):
                with self.assertRaises(ValueError):
                    capture.read("heap-descriptor-first", 0x2000112C, 24)
            self.assertEqual(expected.read_bytes(), b"X" * 23)
            self.assertEqual(capture.read_count, 1)
            self.assertEqual(capture.read_bytes, 24)

    def test_unset_review_pins_fail_before_external_action_or_memory_read(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder, verified=False)
            with mock.patch.multiple(self.subject, ARTIFACT_DIR=None, ELF_HASH=None, BINARY_HASH=None), \
                 mock.patch.object(capture, "run", side_effect=AssertionError("forbidden command")), \
                 mock.patch.object(capture, "read", side_effect=AssertionError("forbidden read")):
                with self.assertRaises(ValueError):
                    self.subject.check_identities(capture, Path(folder) / "unpinned-artifact")

    def test_arbitrary_or_mutating_commands_never_reach_subprocess(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder)
            for argv in (["sh", "-c", "echo synthetic"], [self.subject.OPENOCD, "-c", "reset halt"],
                         [self.subject.OPENOCD, "-c", "mww 0x20000000 1"],
                         ["systemctl", "restart", "arduino-router"],
                         [self.subject.OPENOCD, "-c", "flash write_image x.bin"]):
                with self.subTest(argv=argv), mock.patch.object(subprocess, "run", side_effect=AssertionError("forbidden")):
                    with self.assertRaises(ValueError):
                        capture.run(argv)

    def test_command_count_limit_and_per_command_deadline(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder)
            with mock.patch.object(subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
                for _ in range(64):
                    capture.run([self.subject.OPENOCD, "--version"])
                with self.assertRaises(ValueError):
                    capture.run([self.subject.OPENOCD, "--version"])
                self.assertEqual(run.call_count, 64)
                for call in run.call_args_list:
                    self.assertGreater(call.kwargs["timeout"], 0)
                    self.assertLessEqual(call.kwargs["timeout"], 30)

    def test_sequence_deadline_blocks_commands_and_timeout_preserves_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            capture = self.capture(folder)
            capture.deadline = 0.0
            with mock.patch.object(subprocess, "run", side_effect=AssertionError("forbidden")):
                with self.assertRaises(ValueError):
                    capture.run([self.subject.OPENOCD, "--version"])
            capture = self.capture(folder)
            argv = [self.subject.OPENOCD, "--version"]
            def timeout(arguments, **options):
                # Commands preserve streams through file handles, so emulate a
                # child writing partial output before its subprocess deadline.
                for key, value in (("stdout", b"partial"), ("stderr", b"timeout")):
                    try:
                        options[key].write(value)
                    except TypeError:
                        options[key].write(value.decode())
                    options[key].flush()
                raise subprocess.TimeoutExpired(arguments, 30)
            with mock.patch.object(subprocess, "run", side_effect=timeout):
                with self.assertRaises(ValueError):
                    capture.run(argv)
            self.assertTrue(capture.report.get("commands"))
            receipt = capture.report["commands"][-1]
            self.assertIsNone(receipt["returncode"])
            self.assertTrue(receipt["timeout"])
            self.assertIn("partial", str(receipt))


class LinkedExtensions:
    """Source-layout fixture for the preexisting bounded LLEXT list walker."""
    def __init__(self, count=4):
        self.report = {"flash_identity_verified": True}
        self.calls = []
        self.addresses = [0x20020000 + index * 4096 for index in range(count)]
        self.nodes = {}
        for index, address in enumerate(self.addresses):
            data = bytearray(196)
            struct.pack_into("<I", data, 0, self.addresses[index + 1] if index + 1 < count else 0)
            name = b"sketch" if index == count - 1 else f"other{index}".encode()
            data[4:4 + len(name)] = name
            struct.pack_into("<I", data, 32, 0x20060000)
            struct.pack_into("<I", data, 92, 4096)
            self.nodes[address] = bytes(data)
        self.list_bytes = struct.pack("<II", self.addresses[0], self.addresses[-1])
        self.confirm = self.list_bytes

    def read(self, label, address, size, region="ram"):
        self.calls.append((label, address, size, region))
        if label in ("llext-list", "llext-list-confirm"):
            assert (address, size, region) == (0x200017BC, 8, "ram")
            return self.confirm if label == "llext-list-confirm" else self.list_bytes
        assert label.startswith("node-") and size == 196 and region == "ram"
        return self.nodes[address]


class RecorderExtensionBoundsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject, _, _ = import_without_actions()

    def test_four_nodes_one_sketch_match_and_identical_list_confirmation(self):
        capture = LinkedExtensions()
        result = self.subject.find_bss(capture, 4096)
        self.assertEqual(result, 0x20060000)
        self.assertEqual([call[0] for call in capture.calls],
                         ["llext-list", "node-1", "node-2", "node-3", "node-4", "llext-list-confirm"])

    def test_cycles_fifth_node_wrong_tail_and_changed_confirmation_reject(self):
        cycle = LinkedExtensions()
        last = bytearray(cycle.nodes[cycle.addresses[-1]])
        struct.pack_into("<I", last, 0, cycle.addresses[0])
        cycle.nodes[cycle.addresses[-1]] = bytes(last)
        fifth = LinkedExtensions(5)
        wrong_tail = LinkedExtensions()
        wrong_tail.list_bytes = struct.pack("<II", wrong_tail.addresses[0], wrong_tail.addresses[0])
        changed = LinkedExtensions()
        changed.confirm = bytes(8)
        for capture in (cycle, fifth, wrong_tail, changed):
            with self.subTest(list=capture.list_bytes, count=len(capture.nodes)):
                with self.assertRaises(ValueError):
                    self.subject.find_bss(capture, 4096)
                self.assertLessEqual(sum(call[0].startswith("node-") for call in capture.calls), 4)

    def test_duplicate_sketch_wrong_size_and_invalid_bss_bounds_reject(self):
        duplicate = LinkedExtensions()
        first = bytearray(duplicate.nodes[duplicate.addresses[0]])
        first[4:20] = b"sketch" + bytes(10)
        duplicate.nodes[duplicate.addresses[0]] = bytes(first)
        wrong_size = LinkedExtensions()
        wrong_base = LinkedExtensions()
        for capture, offset, value in ((wrong_size, 92, 4095), (wrong_base, 32, 0x200BFF00)):
            last = bytearray(capture.nodes[capture.addresses[-1]])
            struct.pack_into("<I", last, offset, value)
            capture.nodes[capture.addresses[-1]] = bytes(last)
        for capture in (duplicate, wrong_size, wrong_base):
            with self.subTest(kind=capture.nodes):
                with self.assertRaises(ValueError):
                    self.subject.find_bss(capture, 4096)


# Literal target1502e948 readelf section and symbol fields. GNU nm presents
# 00037a58 by adding the section VMA; ELF32 REL st_value stays section-relative.
ELF_HEADER = """ELF Header:
  Class:                             ELF32
  Data:                              2's complement, little endian
  Type:                              REL (Relocatable file)
  Machine:                           ARM
Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 9] .bss              NOBITS          0000f130 00fad0 02a744 00  WA  0   0  8
"""
DIAGNOSTIC_SYMBOL = "  2045: 00028928   296 OBJECT  GLOBAL DEFAULT    9 recorderDiagnostics\n"


class LayoutTranscript:
    def __init__(self, header=ELF_HEADER, symbols=DIAGNOSTIC_SYMBOL):
        self.report = {}
        self.calls = []
        self.header = header
        self.symbols = symbols

    def run(self, argv):
        self.calls.append([str(value) for value in argv])
        if "-hSW" in argv:
            return self.header
        if "-sW" in argv:
            return self.symbols
        raise AssertionError("Layout may only invoke readelf header/section and symbol reads")


class RecorderElfLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject, _, _ = import_without_actions()

    def layout(self, fixture):
        return self.subject.read_layout(fixture, Path("/literal/recorder_inert.ino.elf"))

    def test_actual_target_nonzero_section_vma_preserves_relative_st_value(self):
        fixture = LayoutTranscript()
        size, symbols = self.layout(fixture)
        self.assertEqual(size, 0x2A744)
        self.assertEqual(symbols, {"recorderDiagnostics": {"offset": 0x28928, "size": 296}})
        self.assertEqual(fixture.report["layout"]["bss_size"], 0x2A744)
        self.assertEqual(fixture.report["layout"]["symbols"], symbols)
        self.assertEqual([call[1] for call in fixture.calls], ["-hSW", "-sW"])

    def test_valid_section_relative_boundaries_do_not_subtract_section_vma(self):
        for offset in (0, 0xF12C, 0x2A61C):
            with self.subTest(offset=offset):
                line = DIAGNOSTIC_SYMBOL.replace("00028928", f"{offset:08x}")
                size, symbols = self.layout(LayoutTranscript(symbols=line))
                self.assertEqual(size, 0x2A744)
                self.assertEqual(symbols["recorderDiagnostics"]["offset"], offset)

    def test_nm_vma_value_and_section_overruns_are_rejected(self):
        for offset in (0x37A58, 0x2A620, 0x2A744, 0xFFFFFFFF):
            with self.subTest(offset=offset):
                line = DIAGNOSTIC_SYMBOL.replace("00028928", f"{offset:08x}")
                with self.assertRaises(ValueError):
                    self.layout(LayoutTranscript(symbols=line))

    def test_duplicate_sections_and_duplicate_diagnostic_symbols_reject(self):
        duplicate_section = ELF_HEADER + (
            "  [10] .bss              NOBITS          00000000 00fad0 02a744 00  WA  0   0  8\n")
        for fixture in (LayoutTranscript(header=duplicate_section),
                        LayoutTranscript(symbols=DIAGNOSTIC_SYMBOL + DIAGNOSTIC_SYMBOL),
                        LayoutTranscript(symbols=DIAGNOSTIC_SYMBOL +
                                         DIAGNOSTIC_SYMBOL.replace("00028928", "00000000"))):
            with self.subTest(header=fixture.header, symbols=fixture.symbols):
                with self.assertRaises(ValueError):
                    self.layout(fixture)

    def test_diagnostic_object_size_type_section_and_presence_are_required(self):
        variants = ["", DIAGNOSTIC_SYMBOL.replace("296", "295"),
                    DIAGNOSTIC_SYMBOL.replace("296", "300"),
                    DIAGNOSTIC_SYMBOL.replace("OBJECT", "FUNC"),
                    DIAGNOSTIC_SYMBOL.replace("    9 ", "    8 "),
                    DIAGNOSTIC_SYMBOL.replace("recorderDiagnostics", "anotherSymbol")]
        for symbols in variants:
            with self.subTest(symbols=symbols):
                with self.assertRaises(ValueError):
                    self.layout(LayoutTranscript(symbols=symbols))

    def test_only_pinned_elf32_little_endian_arm_relocatable_layout_accepted(self):
        for original, replacement in (("ELF32", "ELF64"), ("little endian", "big endian"),
                                      ("REL (Relocatable file)", "EXEC (Executable file)"),
                                      ("Machine:                           ARM", "Machine:                           AArch64")):
            with self.subTest(replacement=replacement):
                with self.assertRaises(ValueError):
                    self.layout(LayoutTranscript(header=ELF_HEADER.replace(original, replacement)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
