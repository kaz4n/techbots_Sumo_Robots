# Tests D090 framing, receive-only capture and publication against public contracts.
# Uses independent literal wire/CRC fixtures plus actual C++ Robot pipeline output.
# Runs offline under unittest; synthetic data never establishes hardware origin.
import contextlib
import base64
import importlib
import io
import json
import os
from pathlib import Path
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zlib
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
FRAME_HEADER = b"schema_version,ordinal,pack_status,t_ms,state,mode,line_mask,opp_mask,heading_cdeg,gyro_z_dps10,ax_mg,ay_mg,duty_l_127,duty_r_127,vbat_cv,flags,tick_max_us,raw_hex\n"
EVENT_HEADER = b"schema_version,ordinal,t_us,type,detail,value,raw_hex\n"
SUMMARY_HEADER = b"schema_version,epoch_token,last_frame_token,release_us,mode,phase,observed_results,missing_results,rejected_results,identity_rejected,malformed_batches,event_semantic_rejected,upstream_event_rejected,upstream_event_invalid,source_regressions,skipped_frames,ticks,overruns,tick_max_us,ticks_saturated,upstream_event_overflow,timing_incomplete,recording_incomplete,go_seen,final_frame_missing,interrupted,terminal_exhausted,frame_count,frame_overwritten,frame_rejected_status,frame_clamped,frame_invalid,event_count,event_overflow,event_rejected,incomplete\n"
SUMMARY_FIELDS = SUMMARY_HEADER.decode().strip().split(",")
FRAME_ZERO = b"1,0,0,0,2,1,0,0,0,0,0,0,0,0,0,0,0,00000000020100000000000000000000000000000000000000\n"
FRAME_ONE = b"1,1,0,0,10,1,0,0,0,0,0,0,0,0,0,0,0,000000000a0100000000000000000000000000000000000000\n"
EVENT_ZERO = b"1,0,1234,0,1,0,d204000000010000\n"


def summary_row(frames=2, events=1, **updates):
    values = dict.fromkeys(SUMMARY_FIELDS, 0)
    values.update(schema_version=1, epoch_token=1, last_frame_token=2,
                  release_us=1234, mode=1, phase=3, observed_results=3,
                  frame_count=frames, event_count=events)
    values.update(updates)
    return (",".join(str(values[key]) for key in SUMMARY_FIELDS) + "\n").encode()


def wire(frames=None, events=None, summary=None, session=10, epoch=1, origin=1,
         rate=25, frame_capacity=5001, event_capacity=4096):
    frames = [FRAME_ZERO, FRAME_ONE] if frames is None else frames
    events = [EVENT_ZERO] if events is None else events
    summary = summary_row(len(frames), len(events)) if summary is None else summary
    token = str(session).encode()
    prefix = (f"SUMOX26_DUMP,1,{session},{epoch},{origin},{rate},{frame_capacity},"
              f"{event_capacity},{len(frames)},{len(events)}\n").encode()
    records = [b"SH," + token + b"," + SUMMARY_HEADER, b"SR," + token + b"," + summary,
               b"FH," + token + b"," + FRAME_HEADER]
    records += [b"FR," + token + b"," + frame for frame in frames]
    records += [b"EH," + token + b"," + EVENT_HEADER]
    records += [b"ER," + token + b"," + event for event in events]
    prefix += b"".join(records)
    return prefix + f"END,{session},{len(frames)},{len(events)},{zlib.crc32(prefix)}\n".encode()


def rechecksum(data):
    lines = data.splitlines(keepends=True)
    fields = lines[-1].rstrip(b"\n").split(b",")
    fields[-1] = str(zlib.crc32(b"".join(lines[:-1]))).encode()
    return b"".join(lines[:-1]) + b",".join(fields) + b"\n"


def chunks(data, sizes=(1, 3, 17, 64, 7)):
    offset = 0
    count = 0
    while offset < len(data):
        length = sizes[count % len(sizes)]
        yield data[offset:offset + length]
        offset += length
        count += 1


class DumpBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = importlib.import_module("dump_match")

    def parse(self, data, sizes=(1, 3, 17, 64, 7)):
        parser = self.module.Parser()
        for part in chunks(data, sizes):
            self.assertIsNone(parser.feed(part))
        return parser.finish()

    def rejects(self, data):
        with self.assertRaises(self.module.CaptureError) as caught:
            self.parse(data)
        self.assertIsInstance(caught.exception, ValueError)
        self.assertRegex(caught.exception.code, r"^[A-Z][A-Z0-9_]*$")

class DumpParserTests(DumpBase):
    def test_literal_bytes_and_metadata(self):
        data = wire()
        capture = self.parse(data)
        self.assertEqual((capture.session, capture.epoch, capture.origin, capture.log_hz), (10, 1, 1, 25))
        self.assertEqual((capture.frame_capacity, capture.event_capacity), (5001, 4096))
        self.assertEqual((capture.frame_count, capture.event_count, capture.mode), (2, 1, 1))
        self.assertEqual(capture.frames, FRAME_HEADER + FRAME_ZERO + FRAME_ONE)
        self.assertEqual(capture.events, EVENT_HEADER + EVENT_ZERO)
        self.assertEqual(capture.summary, SUMMARY_HEADER + summary_row())
        self.assertEqual(capture.crc32, zlib.crc32(data[:data.rfind(b"END,")]))
        with self.assertRaises((AttributeError, TypeError)):
            capture.session = 999

    def test_every_single_split_and_fixed_seed_fragments(self):
        data = wire()
        for split in range(len(data) + 1):
            parser = self.module.Parser()
            parser.feed(data[:split]); parser.feed(data[split:])
            self.assertEqual(parser.finish().events, EVENT_HEADER + EVENT_ZERO)
        rng = random.Random(9017)
        for _ in range(40):
            sizes = tuple(rng.randint(1, 191) for _ in range(9))
            self.assertEqual(self.parse(data, sizes).frames, FRAME_HEADER + FRAME_ZERO + FRAME_ONE)

    def test_empty_collections_keep_headers_and_interrupted_loss(self):
        row = summary_row(0, 0, last_frame_token=0, phase=4, interrupted=1, incomplete=1)
        capture = self.parse(wire(frames=[], events=[], summary=row))
        self.assertEqual(capture.frames, FRAME_HEADER)
        self.assertEqual(capture.events, EVENT_HEADER)
        self.assertEqual(capture.summary, SUMMARY_HEADER + row)

    def test_maximum_row_collections_are_bounded_and_exact(self):
        frames = [FRAME_ZERO.replace(b"1,0,", f"1,{n},".encode(), 1) for n in range(5001)]
        events = [EVENT_ZERO.replace(b"1,0,", f"1,{n},".encode(), 1) for n in range(4096)]
        row = summary_row(5001, 4096)
        capture = self.parse(wire(frames, events, row), (4093, 65536, 7))
        self.assertEqual(capture.frames, FRAME_HEADER + b"".join(frames))
        self.assertEqual(capture.events, EVENT_HEADER + b"".join(events))

    def test_loss_statuses_raw_signed_extrema_and_unknown_codes_are_preserved(self):
        fields = (4294967295, 255, 255, 255, 255, -2147483648, -32768, 32767, -1,
                  -128, 127, 65535, 255, 65535)
        raw = struct.pack("<IBBBBihhhbbHBH", *fields)
        row = ("1,0,2," + ",".join(map(str, fields)) + "," + raw.hex() + "\n").encode()
        summary = summary_row(1, 1, frame_invalid=1, incomplete=1)
        capture = self.parse(wire([row], summary=summary))
        self.assertEqual(capture.frames, FRAME_HEADER + row)

    def test_envelope_ranges_and_canonical_decimal(self):
        cases = ((2, b"0"), (2, b"01"), (2, b"18446744073709551616"),
                 (3, b"0"), (4, b"3"), (5, b"0"), (5, b"4294967296"),
                 (6, b"5002"), (6, b"1"), (7, b"4097"), (7, b"0"),
                 (8, b"5002"), (9, b"4097"), (8, b"-1"), (9, b"+1"))
        for index, value in cases:
            with self.subTest(index=index, value=value):
                lines = wire().splitlines(keepends=True)
                fields = lines[0].strip().split(b","); fields[index] = value
                lines[0] = b",".join(fields) + b"\n"
                self.rejects(rechecksum(b"".join(lines)))

    def test_all_declared_origins_and_lower_capacity_domains(self):
        for origin in (0, 1, 2):
            capture = self.parse(wire(origin=origin, frame_capacity=2, event_capacity=1))
            self.assertEqual(capture.origin, origin)

    def test_missing_duplicate_and_reordered_record_kinds(self):
        lines = wire().splitlines(keepends=True)
        for index in range(len(lines) - 1):
            with self.subTest(missing=index): self.rejects(rechecksum(b"".join(lines[:index] + lines[index + 1:])))
            with self.subTest(duplicate=index): self.rejects(rechecksum(b"".join(lines[:index] + [lines[index]] + lines[index:])))
        reordered = lines[:]
        reordered[2], reordered[3] = reordered[3], reordered[2]
        self.rejects(rechecksum(b"".join(reordered)))

    def test_every_record_rejects_cross_session_mix(self):
        lines = wire().splitlines(keepends=True)
        for index in range(1, len(lines)):
            modified = lines[:]
            modified[index] = modified[index].replace(b",10,", b",11,", 1)
            with self.subTest(index=index): self.rejects(rechecksum(b"".join(modified)))

    def test_ordinals_are_contiguous_and_begin_at_zero(self):
        for needle, replacement in ((b"FR,10,1,0,", b"FR,10,1,1,"),
                                    (b"FR,10,1,1,", b"FR,10,1,0,"),
                                    (b"ER,10,1,0,", b"ER,10,1,5,")):
            self.rejects(rechecksum(wire().replace(needle, replacement)))

    def test_crc_corruption_and_declared_tail_counts(self):
        data = wire()
        for changed in (data.replace(b"END,10,2,1,", b"END,10,1,1,"),
                        data.replace(b"END,10,2,1,", b"END,10,2,0,"),
                        data[:data.rfind(b",") + 1] + b"0\n",
                        data.replace(b",1234,", b",1235,")):
            self.rejects(changed)

    def test_truncation_at_every_boundary_and_trailing_bytes(self):
        data = wire()
        for stop in range(len(data)):
            with self.subTest(stop=stop): self.rejects(data[:stop])
        for tail in (b"\n", b"X", b"END,10,2,1,0\n", wire()):
            self.rejects(data + tail)

    def test_ascii_line_and_total_size_limits(self):
        for data in (wire().replace(b"\n", b"\r\n"), b"\xef\xbb\xbf" + wire(),
                     wire().replace(b"SH,", b"\x00SH,"), wire().replace(b"SH,", b"\xffSH,"),
                     b"x" * 1152 + b"\n", b"x" * (16 * 1024 * 1024 + 1)):
            self.rejects(data)

    def test_exact_csv_headers_and_raw_bytes_are_checked(self):
        for needle, replacement in ((b"heading_cdeg", b"heading_deg"),
                                    (b"d204000000010000", b"d204000000010001"),
                                    (b"000000000201", b"000000000301"),
                                    (b"schema_version", b"schema_version,extra")):
            self.rejects(rechecksum(wire().replace(needle, replacement)))

    def test_summary_identity_lifecycle_and_terminal_exhaustion(self):
        for values in ({"epoch_token": 2}, {"mode": 0}, {"mode": 7}, {"phase": 0},
                       {"phase": 1}, {"phase": 2}, {"phase": 5},
                       {"frame_count": 1}, {"event_count": 0}, {"terminal_exhausted": 1}):
            with self.subTest(values=values): self.rejects(wire(summary=summary_row(**values)))

    def test_sender_cannot_inject_a_filename_or_path(self):
        for text in (b"../../escape", b"/tmp/escape", b"C:\\escape", b"../manifest.json"):
            self.rejects(rechecksum(wire().replace(b"SH,10,", b"SH," + text + b",", 1)))


class DumpCaptureTests(DumpBase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def csv_path(self, destination, role):
        matches = list(destination.glob("*_" + role + ".csv"))
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_publication_validates_exact_files_and_manifest_without_authentication(self):
        destination = self.module.save_capture(chunks(wire()), self.root)
        self.assertTrue(destination.is_dir())
        self.assertRegex(destination.name, r"^\d{8}_\d{6}_mode1")
        self.assertNotIn("partial", destination.name)
        self.assertEqual(self.csv_path(destination, "frames").read_bytes(), FRAME_HEADER + FRAME_ZERO + FRAME_ONE)
        self.assertEqual(self.csv_path(destination, "events").read_bytes(), EVENT_HEADER + EVENT_ZERO)
        manifest = json.loads((destination / "manifest.json").read_text())
        self.assertEqual(manifest["origin"], "synthetic")
        self.assertEqual(manifest["closure"], "closed")
        self.assertIsNone(manifest["source_sha256"])
        validator = importlib.import_module("validate_csv_bundle")
        report = validator.validate_bundle(self.csv_path(destination, "frames"), self.csv_path(destination, "events"),
                                           self.csv_path(destination, "summary"), destination / "manifest.json")
        self.assertEqual((report["format_integrity"], report["consistency"]), ("PASS", "PASS"))
        self.assertFalse(report["hardware_acceptance"])
        self.assertTrue(any("validation" in path.name for path in destination.iterdir()))

    def test_same_second_captures_do_not_overwrite_existing_files(self):
        first = self.module.save_capture([wire()], self.root)
        original = {path.name: path.read_bytes() for path in first.iterdir() if path.is_file()}
        second = self.module.save_capture([wire()], self.root)
        self.assertNotEqual(first, second)
        for name, contents in original.items(): self.assertEqual((first / name).read_bytes(), contents)

    def test_failed_protocol_and_input_generator_preserve_partial_evidence(self):
        def broken():
            yield wire()[:500]
            raise OSError("independent simulated receive failure")
        for parts in ([wire()[:-1]], broken()):
            with self.assertRaises((self.module.CaptureError, OSError)):
                self.module.save_capture(parts, self.root)
        children = list(self.root.iterdir())
        self.assertEqual(len(children), 2)
        self.assertTrue(all("partial" in path.name for path in children))
        self.assertTrue(all(any(path.iterdir()) for path in children))

    def test_consistency_failure_cannot_publish_but_reported_loss_can(self):
        wrong = wire(summary=summary_row(incomplete=1))
        with self.assertRaises(self.module.CaptureError): self.module.save_capture([wrong], self.root)
        interrupted = wire(summary=summary_row(phase=4, interrupted=1, incomplete=1))
        destination = self.module.save_capture([interrupted], self.root)
        self.assertNotIn("partial", destination.name)

    def test_offline_origin_claim_is_preserved_without_upgrading_it(self):
        for origin, declaration in ((0, None), (1, "synthetic"), (2, "hardware_reported")):
            destination = self.module.save_capture([wire(origin=origin)], self.root)
            manifest = json.loads((destination / "manifest.json").read_text())
            self.assertEqual(manifest["origin"], declaration)

    def test_declared_firmware_and_hash_formats_are_validated(self):
        for arguments in ({"firmware_revision": "../escape"}, {"source_sha256": "A" * 64},
                          {"config_sha256": "0" * 63}, {"target": "bad\ncommand"}):
            with self.subTest(arguments=arguments):
                with self.assertRaises(self.module.CaptureError):
                    self.module.save_capture([wire()], self.root, **arguments)
        destination = self.module.save_capture([wire()], self.root, firmware_revision="a" * 40,
                                               source_sha256="b" * 64, config_sha256="c" * 64)
        manifest = json.loads((destination / "manifest.json").read_text())
        self.assertEqual(manifest["firmware_revision"], "a" * 40)

    def test_symlink_output_and_ancestry_are_rejected(self):
        real = self.root / "real"; real.mkdir()
        link = self.root / "link"
        try: link.symlink_to(real, target_is_directory=True)
        except OSError: self.skipTest("symlink privilege unavailable")
        for path in (link, link / "new"):
            with self.assertRaises(self.module.CaptureError): self.module.save_capture([wire()], path)
        self.assertEqual(list(real.iterdir()), [])

    def test_offline_main_never_opens_network_or_process_and_bad_args_do_not_publish(self):
        fixture = self.root / "input.wire"; fixture.write_bytes(wire())
        output = self.root / "output"
        with mock.patch("socket.create_connection", side_effect=AssertionError("offline network")), \
             mock.patch("subprocess.Popen", side_effect=AssertionError("offline subprocess")), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.module.main(["--input", str(fixture), "--output-dir", str(output)]), 0)
            with self.assertRaises(SystemExit) as caught:
                self.module.main(["--input", str(fixture), "--output-dir", str(output), "--timeout", "0"])
            self.assertEqual(caught.exception.code, 2)
        self.assertEqual(len(list(output.iterdir())), 1)

    def test_cli_symlink_input_is_rejected_without_published_capture(self):
        fixture = self.root / "input.wire"; fixture.write_bytes(wire())
        link = self.root / "linked.wire"
        try: link.symlink_to(fixture)
        except OSError: self.skipTest("symlink privilege unavailable")
        output = self.root / "output"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                self.module.main(["--input", str(link), "--output-dir", str(output)])
            self.assertEqual(caught.exception.code, 2)
        if output.exists(): self.assertTrue(all("partial" in path.name for path in output.iterdir()))

    def test_actual_cpp_pipeline_stream_roundtrip(self):
        compiler = shutil.which("g++")
        if compiler is None: self.skipTest("g++ unavailable; run this check in the host Linux toolchain")
        executable = self.root / "dump_stream"
        sources = sorted((ROOT / "src/core").glob("*.cpp"))
        sources += [ROOT / "src/hal" / name for name in
                    ("recorder_frames.cpp", "recorder.cpp", "recorder_csv.cpp", "recorder_dump.cpp", "motors.cpp")]
        sources += [ROOT / "tests/fixtures/dump_stream.cc"]
        command = [compiler, "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                   "-fno-exceptions", "-fno-rtti", "-I", str(ROOT / "src"),
                   *map(str, sources), "-o", str(executable)]
        built = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=120)
        self.assertEqual(built.returncode, 0, built.stderr.decode(errors="replace"))
        ran = subprocess.run([str(executable)], capture_output=True, timeout=20)
        self.assertEqual(ran.returncode, 0, ran.stderr.decode(errors="replace"))
        capture = self.parse(ran.stdout)
        self.assertGreater(capture.frame_count, 0)
        self.assertGreater(capture.event_count, 0)
        self.assertEqual(capture.origin, 1)
        destination = self.module.save_capture(chunks(ran.stdout), self.root / "captured")
        self.assertEqual(self.csv_path(destination, "frames").read_bytes(), capture.frames)
        self.assertEqual(self.csv_path(destination, "events").read_bytes(), capture.events)
        self.assertEqual(self.csv_path(destination, "summary").read_bytes(), capture.summary)

    def test_live_remote_decodes_exact_receive_only_fragments(self):
        data = wire()
        fragments = list(chunks(data, (5, 71, 512)))
        encoded = "".join(base64.b64encode(part).decode() + "\n" for part in fragments)
        returned = subprocess.CompletedProcess(["synthetic-transport"], 0, stdout=encoded, stderr="")
        with mock.patch.object(self.module.board, "remote", return_value=returned) as remote:
            received = list(self.module.live_chunks("synthetic-target", 33))
        self.assertEqual(b"".join(received), data)
        arguments, options = remote.call_args
        self.assertEqual(arguments[0], "synthetic-target")
        self.assertEqual(arguments[1][:3], ["python3", "-u", "-c"])
        self.assertEqual(arguments[1][-1], "33")
        self.assertTrue(options["capture"])
        self.assertEqual(options["timeout"], 48)
        self.assertEqual(self.parse(b"".join(received)).frame_count, 2)

    def test_live_preserves_carriage_return_so_parser_rejects_it(self):
        data = wire().replace(b"\n", b"\r\n")
        encoded = base64.b64encode(data).decode() + "\n"
        returned = subprocess.CompletedProcess([], 0, stdout=encoded, stderr="")
        with mock.patch.object(self.module.board, "remote", return_value=returned):
            received = b"".join(self.module.live_chunks("synthetic-target", 20))
        self.assertEqual(received, data)
        self.rejects(received)

    def test_failed_remote_retains_prefix_but_never_publishes_even_with_end(self):
        encoded = base64.b64encode(wire()).decode() + "\n" + "truncated-last-fragment"
        failures = (subprocess.CalledProcessError(7, "synthetic", output=encoded),
                    subprocess.TimeoutExpired("synthetic", 20, output=encoded))
        for failure in failures:
            with mock.patch.object(self.module.board, "remote", side_effect=failure):
                with self.assertRaises(self.module.CaptureError) as caught:
                    self.module.save_capture(self.module.live_chunks("synthetic-target", 20),
                                             self.root, receive_mode="ssh", target="synthetic-target")
            self.assertEqual(caught.exception.code, "TRANSPORT")
        self.assertTrue(all("partial" in path.name for path in self.root.iterdir()))

    def test_output_file_and_file_ancestor_are_invalid_arguments_before_transport(self):
        occupied = self.root / "occupied"; occupied.write_bytes(b"keep me")
        for output in (occupied, occupied / "child"):
            with mock.patch.object(self.module.board, "remote", side_effect=AssertionError("premature transport")), \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    self.module.main(["--output-dir", str(output)])
            self.assertEqual(caught.exception.code, 2)
        self.assertEqual(occupied.read_bytes(), b"keep me")

    def test_live_success_and_failure_record_exact_command_outcomes(self):
        encoded = base64.b64encode(wire()).decode() + "\n"
        good = subprocess.CompletedProcess(["test"], 0, stdout=encoded, stderr="diagnostic")
        with mock.patch.object(self.module.board, "remote", return_value=good):
            destination = self.module.save_capture(self.module.live_chunks("test-target", 12), self.root,
                                                   receive_mode="ssh", target="test-target")
        report = json.loads((destination / "capture.json").read_text())
        outcome = report["transport_outcome"]
        self.assertEqual(outcome["returncode"], 0)
        self.assertFalse(outcome["timed_out"])
        self.assertEqual(outcome["timeout_seconds"], 27)
        self.assertEqual(outcome["remote_argv"][:3], ["python3", "-u", "-c"])
        error = subprocess.CalledProcessError(7, "test", output=encoded, stderr="failure detail")
        with mock.patch.object(self.module.board, "remote", side_effect=error):
            with self.assertRaises(self.module.CaptureError):
                self.module.save_capture(self.module.live_chunks("test-target", 12), self.root,
                                         receive_mode="ssh", target="test-target")
        partial = next(path for path in self.root.iterdir() if "partial" in path.name)
        failure = json.loads((partial / "error.json").read_text())["transport_outcome"]
        self.assertEqual(failure["returncode"], 7)
        self.assertIn("failure detail", failure["stderr"])
        self.assertFalse(failure["timed_out"])
        before = set(self.root.iterdir())
        timeout = subprocess.TimeoutExpired("test", 27, output=encoded, stderr="timeout detail")
        with mock.patch.object(self.module.board, "remote", side_effect=timeout):
            with self.assertRaises(self.module.CaptureError):
                self.module.save_capture(self.module.live_chunks("test-target", 12), self.root,
                                         receive_mode="ssh", target="test-target")
        timed_partial = (set(self.root.iterdir()) - before).pop()
        timed = json.loads((timed_partial / "error.json").read_text())["transport_outcome"]
        self.assertIsNone(timed["returncode"])
        self.assertTrue(timed["timed_out"])
        self.assertEqual(timed["timeout_seconds"], 27)

    def test_additive_d088_d089_d090_registry_runs_all_legacy_config_checks(self):
        legacy = importlib.import_module("tests.tooling.test_p0_config")
        integers = {"UI_FRAME_PERIOD_US": 40000, "UI_FAULT_PAGE_MS": 500,
                    "UI_BENCH_SCENE_MS": 2000, "QTR_CAL_SAMPLES": 16,
                    "QTR_CAL_CAPTURE_MS": 1000, "DUMP_PAYLOAD_BYTES": 64,
                    "DUMP_STALL_MS": 2000, "DUMP_TOTAL_MS": 300000,
                    "DUMP_UART_STEP_BYTES": 8, "DUMP_UART_STEP_US": 80,
                    "DUMP_UART_PACKET_MS": 100}
        floats = {"UI_BATTERY_EMPTY_V": Decimal("9.5"), "UI_BATTERY_FULL_V": Decimal("12.6")}
        output = io.StringIO()
        with mock.patch.dict(legacy.BEHAVIOR_EXTRA_DEFAULTS, integers), \
             mock.patch.dict(legacy.BEHAVIOR_EXTRA_FLOAT_DEFAULTS, floats):
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(legacy.P0ConfigTests)
            result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
        self.assertEqual(result.testsRun, 18)
        self.assertTrue(result.wasSuccessful(), output.getvalue())

    def test_atomic_publish_does_not_replace_empty_or_nonempty_destination(self):
        for occupied in (False, True):
            partial = self.root / ("incoming" + str(occupied) + ".partial")
            partial.mkdir(); (partial / "incoming.txt").write_bytes(b"new capture")
            destination = self.root / ("existing" + str(occupied))
            destination.mkdir()
            if occupied: (destination / "keep.txt").write_bytes(b"old capture")
            with self.assertRaises((self.module.CaptureError, OSError)):
                self.module.publish(partial, destination)
            self.assertEqual((partial / "incoming.txt").read_bytes(), b"new capture")
            self.assertFalse((destination / "incoming.txt").exists())
            if occupied: self.assertEqual((destination / "keep.txt").read_bytes(), b"old capture")
        partial = self.root / "ready.partial"; partial.mkdir()
        (partial / "ready.txt").write_bytes(b"verified capture")
        destination = self.root / "published"
        self.module.publish(partial, destination)
        self.assertFalse(partial.exists())
        self.assertEqual((destination / "ready.txt").read_bytes(), b"verified capture")


if __name__ == "__main__":
    unittest.main()
