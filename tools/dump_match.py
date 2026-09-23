# Receives the bounded D090 IDLE stream and publishes a validated CSV bundle.
# Keeps transport integrity and declared origin separate from physical acceptance.
# Independent tooling tests exercise fragments, hostile input and actual C++ output.
"""Receive only: this command never requests motion, resets or starts firmware."""
import argparse
import base64
import ctypes
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import uuid
import zlib

import board_tool as board
import validate_csv_bundle as csv

MAX_BYTES = 16 * 1024 * 1024
MAX_LINE = 1151
IDENTITIES = {"firmware_revision": r"(?:[0-9a-f]{40}|[0-9a-f]{64})",
              "source_sha256": r"[0-9a-f]{64}", "config_sha256": r"[0-9a-f]{64}"}


class CaptureError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def require(condition, code, message):
    if not condition:
        raise CaptureError(code, message)


def integer(token, low, high):
    require(len(token) <= len(str(high)) and re.fullmatch(r"0|[1-9][0-9]*", token),
            "INTEGER", "Expected a bounded canonical unsigned decimal.")
    value = int(token)
    require(low <= value <= high, "RANGE", "Wire integer is outside its domain.")
    return value


@dataclass(frozen=True)
class Capture:
    session: int
    epoch: int
    origin: int
    log_hz: int
    frame_capacity: int
    event_capacity: int
    frame_count: int
    event_count: int
    crc32: int
    mode: int
    frames: bytes
    events: bytes
    summary: bytes


class Parser:
    def __init__(self):
        self.pending = bytearray()
        self.total = self.crc = self.frames_seen = self.events_seen = 0
        self.stage = "BEGIN"
        self.meta = None
        self.summary_row = None
        self.files = {role: bytearray() for role in csv.ROLES}
        self.error = None

    def feed(self, chunk):
        if self.error is not None:
            raise self.error
        try:
            require(isinstance(chunk, bytes), "TYPE", "Parser accepts bytes only.")
            self.total += len(chunk)
            require(self.total <= MAX_BYTES, "SIZE", "Wire stream exceeds 16 MiB.")
            require(not chunk or self.stage != "DONE", "TRAILING", "Bytes follow END.")
            require(all(b == 10 or 32 <= b <= 126 for b in chunk), "ASCII", "Wire uses printable ASCII and LF only.")
            self.pending.extend(chunk)
            while b"\n" in self.pending:
                end = self.pending.index(10)
                require(end <= MAX_LINE, "LINE", "Wire line exceeds its limit.")
                line = bytes(self.pending[:end + 1])
                del self.pending[:end + 1]
                self._line(line)
            require(len(self.pending) <= MAX_LINE, "LINE", "Unterminated line exceeds its limit.")
            require(not self.pending or self.stage != "DONE", "TRAILING", "Bytes follow END.")
        except (CaptureError, csv._InvalidInput) as error:
            self.error = error if isinstance(error, CaptureError) else CaptureError(error.code, str(error))
            raise self.error

    def _begin(self, text):
        fields = text.split(",")
        require(len(fields) == 10 and fields[:2] == ["SUMOX26_DUMP", "1"], "BEGIN", "Missing exact version-1 envelope.")
        bounds = ((1, csv.UINT64_MAX), (1, csv.UINT64_MAX), (0, 2),
                  (1, csv.UINT32_MAX), (1, 5001), (1, 4096), (0, 5001), (0, 4096))
        self.meta = tuple(integer(t, *bound) for t, bound in zip(fields[2:], bounds))
        require(self.meta[6] <= self.meta[4] and self.meta[7] <= self.meta[5], "CAPACITY", "Retained count exceeds capacity.")
        self.stage = "SH"

    def _row(self, tag, payload):
        role = {"SH": "summary", "SR": "summary", "FH": "frames",
                "FR": "frames", "EH": "events", "ER": "events"}[tag]
        csv._line_text(payload.encode("ascii") + b"\n")
        if tag.endswith("H"):
            require(payload == ",".join(csv.HEADERS[role]), "HEADER", "CSV header mismatch.")
        else:
            parsed = csv._parse_row(role, payload)
            if tag == "SR":
                self._summary(parsed)
            else:
                seen = self.frames_seen if tag == "FR" else self.events_seen
                require(parsed["ordinal"] == seen, "ORDINAL", "Missing, duplicate or reordered row.")
                if tag == "FR":
                    self.frames_seen += 1
                else:
                    self.events_seen += 1
        self.files[role].extend(payload.encode("ascii") + b"\n")
        following = {"SH": "SR", "SR": "FH", "FH": "FR", "FR": "FR", "EH": "ER", "ER": "ER"}
        self.stage = following[tag]
        if self.stage == "FR" and self.frames_seen == self.meta[6]:
            self.stage = "EH"
        if self.stage == "ER" and self.events_seen == self.meta[7]:
            self.stage = "END"

    def _summary(self, row):
        require(row["epoch_token"] == self.meta[1], "EPOCH", "Summary epoch differs from envelope.")
        require(row["frame_count"] == self.meta[6] and row["event_count"] == self.meta[7],
                "COUNT", "Summary retained counts differ from envelope.")
        require(row["phase"] in (3, 4) and row["terminal_exhausted"] == 0,
                "LIFECYCLE", "Dump source must be retained and nonterminal.")
        require(1 <= row["mode"] <= 6, "MODE", "Unknown attempt mode.")
        self.summary_row = row

    def _line(self, line):
        text = line[:-1].decode("ascii")
        if self.stage == "BEGIN":
            self._begin(text)
        else:
            fields = text.split(",", 2)
            require(len(fields) == 3 and fields[0] == self.stage, "ORDER", "Unexpected wire record.")
            require(integer(fields[1], 1, csv.UINT64_MAX) == self.meta[0], "SESSION", "Mixed wire sessions.")
            if self.stage == "END":
                tail = fields[2].split(",")
                require(len(tail) == 3, "END", "Malformed END.")
                values = tuple(integer(v, 0, csv.UINT32_MAX) for v in tail)
                require(values == (self.frames_seen, self.events_seen, self.crc), "CRC", "END counts or CRC disagree.")
                self.stage = "DONE"
                return
            self._row(fields[0], fields[2])
        self.crc = zlib.crc32(line, self.crc)

    def finish(self):
        if self.error is not None:
            raise self.error
        require(self.stage == "DONE" and not self.pending, "TRUNCATED", "Capture lacks a complete valid END.")
        return Capture(*self.meta, self.crc, self.summary_row["mode"],
                       *(bytes(self.files[role]) for role in csv.ROLES))


def local_path(value):
    require(isinstance(value, (str, Path)) and bool(os.fspath(value)), "PATH", "Expected a local path.")
    name = os.fspath(value)
    require(not (len(name) >= 2 and all(c in "/\\" for c in name[:2])), "PATH", "Network paths are not supported.")
    path = Path(os.path.abspath(name))
    for item in (path, *path.parents):
        require(not item.is_symlink() and not (hasattr(item, "is_junction") and item.is_junction()),
                "SYMLINK", "Symlink/junction path ancestry is not permitted.")
    return path


def declarations(receive_mode, target, identities):
    require(receive_mode in ("offline", "ssh", "adb"), "MODE", "Unknown receive mode.")
    require(target is None or (isinstance(target, str) and bool(target.strip()) and
            re.fullmatch(r"[\x20-\x7e]{1,128}", target)), "TARGET", "Invalid target declaration.")
    for key, value in identities.items():
        require(value is None or (isinstance(value, str) and re.fullmatch(IDENTITIES[key], value)),
                "IDENTITY", "Invalid " + key + " declaration.")


def output_path(value):
    path = local_path(value)
    for item in (path, *path.parents):
        require(not item.exists() or item.is_dir(), "PATH", "Output path and existing ancestors must be directories.")
    return path


def publish(partial, destination):
    # POSIX rename can replace an empty directory; use Linux's no-replace flag.
    if os.name == "nt":
        os.rename(partial, destination)  # Windows fails if the destination exists.
        return
    require(sys.platform.startswith("linux"), "PUBLISH", "Atomic no-replace publication needs Windows or Linux.")
    library = ctypes.CDLL(None, use_errno=True)
    rename = getattr(library, "renameat2", None)
    require(rename is not None, "PUBLISH", "libc lacks atomic no-replace renameat2.")
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    if rename(-100, os.fsencode(partial), -100, os.fsencode(destination), 1) != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(destination))


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write("\n")


def bundle(capture, directory, base, capture_id, target, identities):
    paths = {role: directory / (base + "_" + role + ".csv") for role in csv.ROLES}
    files = {}
    for role in csv.ROLES:
        data = getattr(capture, role)
        with paths[role].open("xb") as output:
            output.write(data)
        files[role] = {"sha256": hashlib.sha256(data).hexdigest(), "rows": data.count(b"\n") - 1}
    manifest = dict(schema_version=1, closure="closed", files=files,
                    session_id=capture_id + "." + str(capture.session),
                    origin=(None, "synthetic", "hardware_reported")[capture.origin],
                    log_hz=capture.log_hz, frame_capacity=capture.frame_capacity,
                    event_capacity=capture.event_capacity, target=target, **identities)
    manifest_path = directory / "manifest.json"
    write_json(manifest_path, manifest)
    report = csv.validate_bundle(*(paths[role] for role in csv.ROLES), manifest_path)
    write_json(directory / "validation.json", report)
    require(report["format_integrity"] == "PASS" and report["consistency"] == "PASS" and not report["errors"],
            "BUNDLE", "Reconstructed CSV bundle failed integrity/owner validation.")


def save_capture(chunks, output_dir, *, receive_mode="offline", target=None,
                 firmware_revision=None, source_sha256=None, config_sha256=None):
    identities = dict(firmware_revision=firmware_revision, source_sha256=source_sha256, config_sha256=config_sha256)
    declarations(receive_mode, target, identities)
    parent = output_path(output_dir)
    parent.mkdir(parents=True, exist_ok=True)
    local_path(parent)
    capture_id = uuid.uuid4().hex
    stamp = datetime.now(timezone(timedelta(hours=4))).strftime("%Y%m%d_%H%M%S")
    partial = parent / (stamp + "_" + capture_id + ".partial")
    partial.mkdir()
    parser = Parser()
    try:
        with (partial / "wire.txt").open("xb") as raw:
            written = 0
            for chunk in chunks:
                require(isinstance(chunk, bytes), "TYPE", "Capture chunks must be bytes.")
                retained = chunk[:max(0, MAX_BYTES - written)]
                raw.write(retained)
                written += len(retained)
                parser.feed(chunk)
        capture = parser.finish()
        base = stamp + "_mode" + str(capture.mode) + "_" + capture_id
        bundle(capture, partial, base, capture_id, target, identities)
        write_json(partial / "capture.json", dict(session=capture.session, epoch=capture.epoch,
                   crc32=capture.crc32, receive_mode=receive_mode, target=target,
                   hardware_acceptance=False, origin_is_caller_declaration=True,
                   transport_integrity="PASS", transport_outcome=getattr(chunks, "outcome", None)))
        local_path(parent)
        destination = parent / base
        require(not destination.exists(), "EXISTS", "Capture destination already exists.")
        publish(partial, destination)
        return destination
    except (CaptureError, csv._InvalidInput, OSError, ValueError, subprocess.SubprocessError) as error:
        failure = error if isinstance(error, CaptureError) else CaptureError("CAPTURE", str(error))
        write_json(partial / "error.json", dict(code=failure.code, message=str(failure), closure="partial",
                   transport_outcome=getattr(chunks, "outcome", None)))
        raise CaptureError(failure.code, str(failure) + "; partial evidence: " + str(partial)) from error


def offline_chunks(path):
    path = local_path(path)
    with csv._regular_input(path, MAX_BYTES) as (source, _):
        while True:
            chunk = source.read(65536)
            if not chunk:
                return
            yield chunk


# The board program only receives. The router's own mon/write server supplies bytes.
REMOTE_RECEIVER = r'''
import base64, socket, sys, time
limit = 16 * 1024 * 1024
deadline = time.monotonic() + int(sys.argv[1])
total = 0
pending = b""
with socket.create_connection(("127.0.0.1", 7500), timeout=min(10, int(sys.argv[1]))) as sock:
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0: raise TimeoutError("capture deadline")
        sock.settimeout(remaining)
        chunk = sock.recv(min(65536, limit - total + 1))
        if not chunk: raise EOFError("Monitor closed before END")
        total += len(chunk)
        if total > limit: raise ValueError("capture byte limit")
        # Preserve exact bytes across ADB/SSH text capture and universal newlines.
        sys.stdout.buffer.write(base64.b64encode(chunk) + b"\n")
        sys.stdout.buffer.flush()
        pending += chunk
        lines = pending.split(b"\n")
        pending = lines.pop()
        if any(len(line) > 1151 for line in lines) or len(pending) > 1151:
            raise ValueError("capture line limit")
        if any(line.startswith(b"END,") for line in lines): break
'''


class LiveCapture:
    def __init__(self, target, timeout):
        self.target, self.timeout, self.outcome = target, timeout, None

    def __iter__(self):
        arguments = ["python3", "-u", "-c", REMOTE_RECEIVER, str(self.timeout)]
        failure = None
        start = datetime.now(timezone.utc).isoformat()
        try:
            result = board.remote(self.target, arguments, capture=True, timeout=self.timeout + 15)
            output, stderr, code = result.stdout, result.stderr, result.returncode
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            output, stderr = error.stdout or b"", error.stderr or b""
            code, failure = getattr(error, "returncode", None), error
        except OSError as error:
            output, stderr, code, failure = b"", str(error), None, error
        stderr = stderr.decode("utf-8", errors="replace") if isinstance(stderr, bytes) else (stderr or "")
        self.outcome = dict(target=self.target, remote_argv=arguments, returncode=code,
                            start_utc=start, end_utc=datetime.now(timezone.utc).isoformat(),
                            timeout_seconds=self.timeout + 15, timed_out=isinstance(failure, subprocess.TimeoutExpired),
                            stderr=stderr[:4096], stderr_truncated=len(stderr) > 4096)
        encoded = output if isinstance(output, bytes) else output.encode("ascii", errors="strict")
        require(len(encoded) <= (MAX_BYTES * 2), "TRANSPORT", "Remote capture exceeds its encoded limit.")
        for line in encoded.splitlines(keepends=True):
            if not line.endswith(b"\n") and failure is not None:
                break  # A killed process can leave one incomplete encoded fragment.
            require(line.endswith(b"\n"), "TRANSPORT", "Truncated remote capture encoding.")
            yield base64.b64decode(line.rstrip(b"\r\n"), validate=True)
        if failure is not None:
            raise CaptureError("TRANSPORT", "Receive-only remote command failed or timed out.") from failure


def live_chunks(target, timeout):
    return LiveCapture(target, timeout)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Offline wire fixture; never contacts a board")
    parser.add_argument("--output-dir", type=Path, default=board.ROOT / "logs")
    parser.add_argument("--timeout", type=int, default=330)
    for key in IDENTITIES:
        parser.add_argument("--" + key.replace("_", "-"))
    args = parser.parse_args(argv)
    identities = {key: getattr(args, key) for key in IDENTITIES}
    try:
        require(1 <= args.timeout <= 3600, "TIMEOUT", "Timeout must be 1..3600 seconds.")
        declarations("offline", None, identities)
        output_path(args.output_dir)
        if args.input is not None:
            path = local_path(args.input)
            require(path.is_file() and stat.S_ISREG(path.stat().st_mode), "INPUT", "Input must be a regular file.")
    except (CaptureError, OSError) as error:
        parser.error(str(error))
    try:
        target = None if args.input is not None else board.target()
        mode = "offline" if args.input is not None else board.transport()
        if args.input is None:
            board.require_transport()
        chunks = offline_chunks(args.input) if args.input is not None else live_chunks(target, args.timeout)
        destination = save_capture(chunks, args.output_dir, receive_mode=mode, target=target, **identities)
        print(destination)
        return 0
    except (CaptureError, csv._InvalidInput, OSError, ValueError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
