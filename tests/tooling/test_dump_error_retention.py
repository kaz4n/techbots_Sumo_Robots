# Tests D178 primary capture failures when the error journal cannot be saved.
# Independent D090 literal fixtures preserve protocol, transport and byte evidence.
# Run with Python -B and externally selected TMPDIR under /dev/shm; no devices.
import base64
import contextlib
import errno
import importlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
FRAME_HEADER = b"schema_version,ordinal,pack_status,t_ms,state,mode,line_mask,opp_mask,heading_cdeg,gyro_z_dps10,ax_mg,ay_mg,duty_l_127,duty_r_127,vbat_cv,flags,tick_max_us,raw_hex\n"
EVENT_HEADER = b"schema_version,ordinal,t_us,type,detail,value,raw_hex\n"
SUMMARY_HEADER = b"schema_version,epoch_token,last_frame_token,release_us,mode,phase,observed_results,missing_results,rejected_results,identity_rejected,malformed_batches,event_semantic_rejected,upstream_event_rejected,upstream_event_invalid,source_regressions,skipped_frames,ticks,overruns,tick_max_us,ticks_saturated,upstream_event_overflow,timing_incomplete,recording_incomplete,go_seen,final_frame_missing,interrupted,terminal_exhausted,frame_count,frame_overwritten,frame_rejected_status,frame_clamped,frame_invalid,event_count,event_overflow,event_rejected,incomplete\n"
FRAME_ZERO = b"1,0,0,0,2,1,0,0,0,0,0,0,0,0,0,0,0,00000000020100000000000000000000000000000000000000\n"
FRAME_ONE = b"1,1,0,0,10,1,0,0,0,0,0,0,0,0,0,0,0,000000000a0100000000000000000000000000000000000000\n"
EVENT_ZERO = b"1,0,1234,0,1,0,d204000000010000\n"
SUMMARY_VALUES = [1, 1, 2, 1234, 1, 3, 3] + [0] * 20 + [2, 0, 0, 0, 0, 1, 0, 0, 0]
SUMMARY_ROW = (",".join(map(str, SUMMARY_VALUES)) + "\n").encode()
WIRE_PREFIX = (b"SUMOX26_DUMP,1,10,1,1,25,5001,4096,2,1\n"
               + b"SH,10," + SUMMARY_HEADER + b"SR,10," + SUMMARY_ROW
               + b"FH,10," + FRAME_HEADER + b"FR,10," + FRAME_ZERO
               + b"FR,10," + FRAME_ONE + b"EH,10," + EVENT_HEADER
               + b"ER,10," + EVENT_ZERO)
WIRE = WIRE_PREFIX + f"END,10,2,1,{zlib.crc32(WIRE_PREFIX)}\n".encode()
TARGET = "fixture@board.invalid"
TICKET = "0123456789abcdef0123456789abcdef"


class DumpErrorRetentionTests(unittest.TestCase):
    def setUp(self):
        temporary = Path(tempfile.gettempdir()).resolve()
        if not sys.platform.startswith("linux") or not temporary.is_relative_to(Path("/dev/shm")):
            raise RuntimeError("D178 requires external TMPDIR under /dev/shm and Python -B")
        if not sys.dont_write_bytecode:
            raise RuntimeError("D178 requires Python -B")
        self.guards = contextlib.ExitStack()
        self.addCleanup(self.guards.close)
        for owner, name in ((socket, "socket"), (socket, "create_connection"),
                            (subprocess, "Popen"), (subprocess, "run"),
                            (subprocess, "call"), (subprocess, "check_call"),
                            (subprocess, "check_output"), (os, "system"), (os, "popen")):
            guard = self.guards.enter_context(mock.patch.object(
                owner, name, side_effect=AssertionError("D178 forbids network/process access")))
            self.addCleanup(guard.assert_not_called)
        self.module = importlib.import_module("dump_match")
        board_guard = self.guards.enter_context(mock.patch.object(
            self.module.board, "remote", side_effect=AssertionError("D178 forbids board access")))
        self.addCleanup(board_guard.assert_not_called)
        self.temp = tempfile.TemporaryDirectory(prefix="d178-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / "captures"
        self.guards.enter_context(mock.patch.dict(os.environ, {
            "SUMO_TRANSPORT": "ssh", "SUMO_SSH_TARGET": TARGET}))

    @contextlib.contextmanager
    def journal_fault(self, failure=None, prefix=b""):
        """Fail the single public pathlib open boundary for error.json only."""
        original = Path.open
        attempts = []

        def opened(path, *args, **kwargs):
            if path.name == "error.json":
                attempts.append(path)
                if prefix:
                    with original(path, "wb") as stream:
                        stream.write(prefix)
                        stream.flush()
                if failure is not None:
                    raise failure
            return original(path, *args, **kwargs)

        with mock.patch.object(Path, "open", opened):
            yield attempts

    def caught(self, parts, output=None, **kwargs):
        with self.assertRaises(self.module.CaptureError) as caught:
            self.module.save_capture(parts, output or self.output, **kwargs)
        return caught.exception

    def primary_protocol(self, data):
        parser = self.module.Parser()
        with self.assertRaises(self.module.CaptureError) as caught:
            parser.feed(data)
            parser.finish()
        return caught.exception

    def retained(self, error, data, secondary=None, output=None):
        children = list((output or self.output).iterdir())
        self.assertEqual(len(children), 1)
        partial = children[0]
        self.assertTrue(partial.is_dir())
        self.assertIn("partial", partial.name)
        self.assertEqual(error.partial_path, str(partial))
        self.assertIn(str(partial), str(error))
        self.assertEqual((partial / "wire.txt").read_bytes(), data)
        expected = None if secondary is None else {
            "type": type(secondary).__name__, "message": str(secondary)}
        self.assertEqual(error.evidence_write_error, expected)
        if secondary is not None:
            text = str(error)
            self.assertIn("error report", text.lower())
            self.assertIn("could not be saved", text.lower())
            self.assertLess(text.index(str(partial)), text.index(str(secondary)))
            self.assertIn(type(secondary).__name__, text)
            self.assertIsNot(error.__cause__, secondary)
        return partial

    def failing_input(self, failure, prefix=WIRE[:80]):
        yield prefix
        raise failure

    def test_capture_error_defaults_remain_unowned(self):
        error = self.primary_protocol(b"invalid\n")
        self.assertIsInstance(error, ValueError)
        self.assertIsNone(error.partial_path)
        self.assertIsNone(error.evidence_write_error)
        self.assertIsNone(error.connection_evidence)

    def test_protocol_enospc_retains_primary_cause_path_and_raw_bytes(self):
        data = b"invalid\n"
        expected = self.primary_protocol(data)
        secondary = OSError(errno.ENOSPC, "synthetic error journal full")
        with self.journal_fault(secondary) as attempts, \
             mock.patch.object(self.module, "publish") as publication:
            error = self.caught([data])
        self.assertEqual(error.code, expected.code)
        self.assertTrue(str(error).startswith(str(expected)))
        self.assertEqual(str(error.__cause__), str(expected))
        self.assertEqual(error.__cause__.code, expected.code)
        partial = self.retained(error, data, secondary)
        self.assertEqual(attempts, [partial / "error.json"])
        self.assertFalse((partial / "error.json").exists())
        self.assertEqual({p.name for p in partial.iterdir()}, {"wire.txt"})
        publication.assert_not_called()

    def test_input_oserror_is_still_primary_when_journal_also_fails(self):
        primary = OSError(errno.EIO, "synthetic input read failure")
        control = self.caught(self.failing_input(primary), self.root / "control")
        secondary = OSError(errno.ENOSPC, "synthetic journal ENOSPC")
        with self.journal_fault(secondary) as attempts, \
             mock.patch.object(self.module, "publish") as publication:
            error = self.caught(self.failing_input(primary))
        self.assertEqual(error.code, control.code)
        self.assertIn(str(primary), str(error))
        self.assertIs(error.__cause__, primary)
        partial = self.retained(error, WIRE[:80], secondary)
        self.assertEqual(attempts, [partial / "error.json"])
        publication.assert_not_called()

    def test_partial_journal_bytes_are_neither_reopened_nor_deleted(self):
        prefix = b'{"synthetic_partial_journal":'
        secondary = OSError(errno.ENOSPC, "synthetic mid-journal failure")
        with self.journal_fault(secondary, prefix) as attempts, \
             mock.patch.object(self.module, "publish") as publication:
            error = self.caught([WIRE[:-1]])
        partial = self.retained(error, WIRE[:-1], secondary)
        self.assertEqual(attempts, [partial / "error.json"])
        self.assertEqual((partial / "error.json").read_bytes(), prefix)
        self.assertEqual({p.name for p in partial.iterdir()}, {"wire.txt", "error.json"})
        publication.assert_not_called()

    def test_journal_serialization_exception_retains_original_input_failure(self):
        primary = OSError(errno.EIO, "synthetic input before serialization")
        secondary = TypeError("synthetic error journal serialization failure")
        original = json.dump
        prefix = '{"synthetic_partial_serialization":'
        serializations = []

        def dump(value, stream, *args, **kwargs):
            if Path(stream.name).name == "error.json":
                serializations.append(value)
                stream.write(prefix)
                stream.flush()
                raise secondary
            return original(value, stream, *args, **kwargs)

        with mock.patch.object(json, "dump", dump), self.journal_fault() as attempts, \
             mock.patch.object(self.module, "publish") as publication:
            error = self.caught(self.failing_input(primary))
        self.assertIs(error.__cause__, primary)
        self.assertIn(str(primary), str(error))
        partial = self.retained(error, WIRE[:80], secondary)
        self.assertEqual(len(serializations), 1)
        self.assertEqual(attempts, [partial / "error.json"])
        self.assertEqual((partial / "error.json").read_bytes(), prefix.encode("utf-8"))
        publication.assert_not_called()

    def test_journal_interrupts_propagate_without_catching_baseexception(self):
        for index, interruption in enumerate((KeyboardInterrupt("synthetic interrupt"),
                                               SystemExit("synthetic termination"))):
            output = self.root / str(index)
            with self.subTest(kind=type(interruption).__name__), \
                 self.journal_fault(interruption) as attempts, \
                 mock.patch.object(self.module, "publish") as publication:
                with self.assertRaises(type(interruption)) as caught:
                    self.module.save_capture([b"invalid\n"], output)
            self.assertIs(caught.exception, interruption)
            self.assertEqual(len(attempts), 1)
            self.assertEqual((attempts[0].parent / "wire.txt").read_bytes(), b"invalid\n")
            self.assertFalse(attempts[0].exists())
            publication.assert_not_called()

    def test_successful_error_write_keeps_public_json_and_no_secondary_claim(self):
        primary = OSError(errno.EIO, "synthetic ordinary input failure")
        with self.journal_fault() as attempts, \
             mock.patch.object(self.module, "publish") as publication:
            error = self.caught(self.failing_input(primary))
        partial = self.retained(error, WIRE[:80])
        self.assertEqual(attempts, [partial / "error.json"])
        raw = attempts[0].read_bytes()
        payload = json.loads(raw)
        self.assertIsNone(payload["transport_outcome"])
        self.assertIsNone(payload["connection_evidence"])
        self.assertNotIn("partial_path", payload)
        self.assertNotIn("evidence_write_error", payload)
        self.assertIn(str(primary), raw.decode())
        self.assertIs(error.__cause__, primary)
        self.assertNotIn("could not be saved", str(error))
        publication.assert_not_called()

    def test_offline_success_preserves_literal_files_and_manifest_semantics(self):
        fixture = self.root / "input.wire"
        fixture.write_bytes(WIRE)
        with self.journal_fault() as attempts, contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            code = self.module.main(["--input", str(fixture), "--output-dir", str(self.output)])
        self.assertEqual(code, 0)
        self.assertEqual(attempts, [])
        destinations = list(self.output.iterdir())
        self.assertEqual(len(destinations), 1)
        destination = destinations[0]
        self.assertNotIn("partial", destination.name)
        self.assertEqual((destination / "wire.txt").read_bytes(), WIRE)
        for role, expected in (("frames", FRAME_HEADER + FRAME_ZERO + FRAME_ONE),
                               ("events", EVENT_HEADER + EVENT_ZERO),
                               ("summary", SUMMARY_HEADER + SUMMARY_ROW)):
            matches = list(destination.glob("*_" + role + ".csv"))
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0].read_bytes(), expected)
        manifest = json.loads((destination / "manifest.json").read_bytes())
        self.assertEqual(manifest["origin"], "synthetic")
        self.assertEqual(manifest["closure"], "closed")
        self.assertIsNone(manifest["source_sha256"])
        metadata = json.loads((destination / "capture.json").read_bytes())
        self.assertIsNone(metadata["transport_outcome"])
        self.assertIsNone(metadata["connection_evidence"])
        self.assertNotIn("evidence_write_error", metadata)
        self.assertTrue((destination / "validation.json").is_file())
        self.assertFalse((destination / "error.json").exists())

    def test_cli_exits_one_and_reports_primary_path_then_secondary(self):
        data = b"invalid\n"
        primary = self.primary_protocol(data)
        fixture = self.root / "bad.wire"
        fixture.write_bytes(data)
        secondary = OSError(errno.ENOSPC, "synthetic CLI error journal full")
        stderr, stdout = io.StringIO(), io.StringIO()
        with self.journal_fault(secondary) as attempts, \
             contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout), \
             mock.patch.object(self.module, "publish") as publication:
            code = self.module.main(["--input", str(fixture), "--output-dir", str(self.output)])
        self.assertEqual(code, 1)
        self.assertEqual(len(attempts), 1)
        text, partial = stderr.getvalue(), attempts[0].parent
        self.assertIn(primary.code, text)
        self.assertIn(str(primary), text)
        self.assertLess(text.index(str(primary)), text.index(str(partial)))
        self.assertLess(text.index(str(partial)), text.index(str(secondary)))
        self.assertIn("could not be saved", text.lower())
        self.assertIn(type(secondary).__name__, text)
        self.assertEqual((partial / "wire.txt").read_bytes(), data)
        self.assertFalse((partial / "error.json").exists())
        self.assertNotIn("success", stdout.getvalue().lower())
        publication.assert_not_called()

    def test_failed_receive_beats_protocol_and_metadata_before_journal_failure(self):
        for index, data in enumerate((WIRE, b"invalid\n")):
            encoded = base64.b64encode(data).decode() + "\n"
            receive = subprocess.CalledProcessError(9, "synthetic", output=encoded,
                                                    stderr="synthetic preferred receive failure")
            query = subprocess.CompletedProcess([], 0, stdout="{", stderr="")
            secondary = OSError(errno.ENOSPC, "synthetic transport journal full")
            output = self.root / str(index)
            with self.subTest(data=data[:12]), self.journal_fault(secondary) as attempts, \
                 mock.patch.object(self.module.board, "remote", side_effect=[receive, query]) as remote, \
                 mock.patch.object(self.module, "publish") as publication:
                stream = self.module.live_chunks(TARGET, 30, connection_ticket=TICKET)
                error = self.caught(stream, output, receive_mode="ssh", target=TARGET)
            self.assertEqual(error.code, "TRANSPORT")
            self.assertEqual(remote.call_count, 2)
            self.assertEqual(error.connection_evidence, stream.connection_evidence)
            self.assertIsNotNone(error.connection_evidence)
            self.assertEqual(stream.outcome["returncode"], 9)
            self.assertEqual(stream.outcome["stderr"], "synthetic preferred receive failure")
            partial = self.retained(error, data, secondary, output)
            self.assertEqual(attempts, [partial / "error.json"])
            publication.assert_not_called()

    def test_wire_and_connection_failures_keep_existing_precedence_and_evidence(self):
        for index, data in enumerate((WIRE, b"invalid\n")):
            expected = "CONNECTION_METADATA" if data == WIRE else self.primary_protocol(data).code
            receive = subprocess.CompletedProcess([], 0,
                stdout=base64.b64encode(data).decode() + "\n", stderr="")
            query = subprocess.CompletedProcess([], 0, stdout="{", stderr="")
            secondary = OSError(errno.ENOSPC, "synthetic connection journal full")
            output = self.root / str(index)
            with self.subTest(expected=expected), self.journal_fault(secondary) as attempts, \
                 mock.patch.object(self.module.board, "remote", side_effect=[receive, query]) as remote, \
                 mock.patch.object(self.module, "publish") as publication:
                stream = self.module.live_chunks(TARGET, 30, connection_ticket=TICKET)
                error = self.caught(stream, output, receive_mode="ssh", target=TARGET)
            self.assertEqual(error.code, expected)
            self.assertEqual(remote.call_count, 2)
            self.assertEqual(error.connection_evidence, stream.connection_evidence)
            self.assertIsNotNone(error.connection_evidence)
            partial = self.retained(error, data, secondary, output)
            self.assertEqual(attempts, [partial / "error.json"])
            publication.assert_not_called()

    def test_publication_failure_keeps_valid_csvs_and_original_oserror(self):
        primary = OSError(errno.EACCES, "synthetic publication refused")
        with mock.patch.object(self.module, "publish", side_effect=primary):
            control = self.caught([WIRE], self.root / "control")
        secondary = OSError(errno.ENOSPC, "synthetic publish-error journal full")
        with self.journal_fault(secondary) as attempts, \
             mock.patch.object(self.module, "publish", side_effect=primary) as publication:
            error = self.caught([WIRE])
        self.assertEqual(error.code, control.code)
        self.assertIn(str(primary), str(error))
        self.assertIs(error.__cause__, primary)
        partial = self.retained(error, WIRE, secondary)
        self.assertEqual(attempts, [partial / "error.json"])
        publication.assert_called_once()
        self.assertEqual(publication.call_args.args[0], partial)
        self.assertEqual(len(list(partial.glob("*_frames.csv"))), 1)
        self.assertEqual(next(partial.glob("*_frames.csv")).read_bytes(), FRAME_HEADER + FRAME_ZERO + FRAME_ONE)
        self.assertTrue((partial / "manifest.json").is_file())
        self.assertTrue((partial / "validation.json").is_file())

    def test_invalid_options_remain_argument_errors_before_partial_ownership(self):
        occupied = self.root / "occupied"
        occupied.write_bytes(b"existing user evidence")
        with self.journal_fault(OSError(errno.ENOSPC, "must never attempt journal")) as attempts, \
             mock.patch.object(self.module, "publish") as publication, \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                self.module.main(["--output-dir", str(occupied)])
        self.assertEqual(caught.exception.code, 2)
        self.assertEqual(attempts, [])
        self.assertEqual(occupied.read_bytes(), b"existing user evidence")
        self.assertEqual(list(self.root.iterdir()), [occupied])
        publication.assert_not_called()


if __name__ == "__main__":
    unittest.main()
