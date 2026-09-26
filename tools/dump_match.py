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
        self.connection_evidence = None
        self.partial_path = None
        self.evidence_write_error = None


def require(condition, code, message):
    if not condition:
        raise CaptureError(code, message)


def integer(token, low, high):
    require(len(token) <= len(str(high)) and re.fullmatch(r"0|[1-9][0-9]*", token),
            "INTEGER", "Expected a bounded canonical unsigned decimal.")
    value = int(token)
    require(low <= value <= high, "RANGE", "Wire integer is outside its domain.")
    return value


def validate_expected_session(value):
    require(value is None or (type(value) is int and 1 <= value <= csv.UINT64_MAX),
            "SESSION_ARGUMENT", "Expected session must be an exact positive uint64 integer.")
    return value


def session_argument(token):
    try:
        return integer(token, 1, csv.UINT64_MAX)
    except CaptureError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


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
    def __init__(self, expected_session=None):
        self.expected_session = validate_expected_session(expected_session)
        self.observed_session = self.rejected_session = None
        self.pending = bytearray()
        self.total = self.crc = self.frames_seen = self.events_seen = 0
        self.stage = "BEGIN"
        self.meta = None
        self.summary_row = None
        self.files = {role: bytearray() for role in csv.ROLES}
        self.error = None

    def session_evidence(self):
        return dict(expected_session=self.expected_session, observed_session=self.observed_session,
                    rejected_session=self.rejected_session)

    def _session(self, value, *, begin=False):
        if begin:
            self.observed_session = value
        if self.expected_session is not None and value != self.expected_session:
            self.rejected_session = value
            require(False, "SESSION_MISMATCH", "Wire session differs from the expected attempt.")
        if not begin and value != self.observed_session:
            self.rejected_session = value
            require(False, "SESSION", "Mixed wire sessions.")

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
        self._session(integer(fields[2], 1, csv.UINT64_MAX), begin=True)
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
            self._session(integer(fields[1], 1, csv.UINT64_MAX))
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


WireParser = Parser


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


def _retained_failure(error, chunks, parser, partial):
    failure = error if isinstance(error, CaptureError) else CaptureError("CAPTURE", str(error))
    if failure.code.startswith("CONNECTION_"):
        try:
            parser.finish()
        except CaptureError as wire_error:
            failure = wire_error
    failure = getattr(chunks, "_receive_failure", None) or failure
    evidence = getattr(chunks, "connection_evidence", None)
    journal_error = None
    try:
        write_json(partial / "error.json", dict(code=failure.code, message=str(failure), closure="partial",
                   transport_outcome=getattr(chunks, "outcome", None), connection_evidence=evidence,
                   **parser.session_evidence()))
    except Exception as write_error:
        # A full disk must not hide the capture failure or its retained bytes.
        journal_error = {"type": type(write_error).__name__, "message": str(write_error)}
    message = str(failure) + "; partial evidence: " + str(partial)
    if journal_error is not None:
        message = str(failure) + " (" + failure.code + "); partial evidence: " + str(partial) + \
                  "; error report could not be saved: " + journal_error["type"] + ": " + journal_error["message"]
    raised = CaptureError(failure.code, message)
    raised.connection_evidence = evidence
    raised.partial_path = str(partial)
    raised.evidence_write_error = journal_error
    raised.session_evidence = parser.session_evidence()
    return raised


def save_capture(chunks, output_dir, *, receive_mode="offline", target=None,
                 firmware_revision=None, source_sha256=None, config_sha256=None, expected_session=None):
    parser = Parser(expected_session)
    identities = dict(firmware_revision=firmware_revision, source_sha256=source_sha256, config_sha256=config_sha256)
    declarations(receive_mode, target, identities)
    parent = output_path(output_dir)
    parent.mkdir(parents=True, exist_ok=True)
    local_path(parent)
    capture_id = uuid.uuid4().hex
    stamp = datetime.now(timezone(timedelta(hours=4))).strftime("%Y%m%d_%H%M%S")
    partial = parent / (stamp + "_" + capture_id + ".partial")
    partial.mkdir()
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
                   transport_integrity="PASS", transport_outcome=getattr(chunks, "outcome", None),
                   connection_evidence=getattr(chunks, "connection_evidence", None),
                   **parser.session_evidence()))
        local_path(parent)
        destination = parent / base
        require(not destination.exists(), "EXISTS", "Capture destination already exists.")
        publish(partial, destination)
        return destination
    except (CaptureError, csv._InvalidInput, OSError, ValueError, subprocess.SubprocessError) as error:
        raise _retained_failure(error, chunks, parser, partial) from error


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


# Repository-owned literal only: share the pure schema checks with remote Python.
# Loading these definitions performs no filesystem, clock, socket or transport I/O.
_CONNECTION_SCHEMA = r'''
import json, re
from datetime import datetime, timezone

_U64 = (1 << 64) - 1
_CLAIM_KEYS = set("schema_version ticket transport target boot_id uid directory_device directory_inode receiver_pid receiver_start_ticks started_monotonic_ns claimed_utc claimed_monotonic_ns deadline_monotonic_ns".split())
_CONNECTION_KEYS = set("schema_version claim event local_address local_port peer_address peer_port socket_fd socket_inode connected_utc connected_monotonic_ns".split())
_TERMINAL_KEYS = set("schema_version claim closed_utc closed_monotonic_ns observed_byte_count reason".split())

def _check(condition, message):
    if not condition:
        raise ValueError(message)

def _number(value, low=0, high=_U64):
    _check(type(value) is int and low <= value <= high, "Invalid bounded JSON integer")

def _keys(value, expected):
    _check(type(value) is dict and set(value) == expected, "Unexpected record schema")

def _utc_valid(value):
    _check(type(value) is str and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z", value), "Invalid UTC syntax")
    datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")

def _ticket_valid(ticket):
    _check(type(ticket) is str and re.fullmatch(r"[0-9a-f]{32}", ticket), "Ticket must be 32 lowercase hexadecimal characters")

def _request_valid(target, mode):
    pattern = r"[A-Za-z0-9][A-Za-z0-9_.:-]*" if mode == "adb" else r"[A-Za-z0-9_][A-Za-z0-9_.@-]*"
    _check(mode in ("adb", "ssh") and type(target) is str and len(target) <= 128 and re.fullmatch(pattern, target), "Invalid connection target/transport")

def _pairs(items):
    result = {}
    for key, value in items:
        _check(key not in result, "Duplicate JSON key")
        result[key] = value
    return result

def _json_read(raw, limit):
    if type(raw) is str:
        raw = raw.encode("utf-8", errors="strict")
    _check(type(raw) is bytes and len(raw) <= limit, "Oversized or invalid JSON input")
    def invalid_constant(value):
        raise ValueError("Invalid JSON constant")
    return json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=_pairs,
                      parse_constant=invalid_constant)

def _claim_valid(value, ticket, mode, target, observed, timeout=None):
    _keys(value, _CLAIM_KEYS)
    _number(value["schema_version"], 1, 1)
    _ticket_valid(value["ticket"])
    _request_valid(value["target"], value["transport"])
    _check((value["ticket"], value["transport"], value["target"]) == (ticket, mode, target), "Claim request identity differs")
    _check(type(value["boot_id"]) is str and re.fullmatch(r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}", value["boot_id"]), "Invalid boot identity")
    _number(value["uid"], 0, (1 << 32) - 1)
    _number(value["directory_device"])
    _number(value["directory_inode"], 1)
    _number(value["receiver_pid"], 1, (1 << 31) - 1)
    _number(value["receiver_start_ticks"])
    for key in ("started_monotonic_ns", "claimed_monotonic_ns", "deadline_monotonic_ns"):
        _number(value[key])
    _utc_valid(value["claimed_utc"])
    start, claimed, deadline = (value[key] for key in ("started_monotonic_ns", "claimed_monotonic_ns", "deadline_monotonic_ns"))
    duration = deadline - start
    _check(start <= claimed < deadline and claimed <= observed, "Invalid claim chronology")
    _check(1000000000 <= duration <= 3600000000000 and duration % 1000000000 == 0, "Invalid claim deadline")
    _check(timeout is None or duration == timeout * 1000000000, "Claim timeout differs")

def _connection_valid(value, claim, observed):
    _keys(value, _CONNECTION_KEYS)
    _number(value["schema_version"], 1, 1)
    _claim_valid(value["claim"], claim["ticket"], claim["transport"], claim["target"], observed)
    _check(value["claim"] == claim and value["event"] == "TCP_CONNECTED", "Connection identity/event differs")
    _check(value["local_address"] == value["peer_address"] == "127.0.0.1", "Unexpected connection address")
    _number(value["local_port"], 1, 65535)
    _number(value["peer_port"], 7500, 7500)
    _number(value["socket_fd"], 0, (1 << 31) - 1)
    _number(value["socket_inode"], 1)
    _number(value["connected_monotonic_ns"])
    _utc_valid(value["connected_utc"])
    moment = value["connected_monotonic_ns"]
    _check(claim["claimed_monotonic_ns"] <= moment < claim["deadline_monotonic_ns"] and moment <= observed, "Invalid connection chronology")

def _terminal_valid(value, claim, connection, observed):
    _keys(value, _TERMINAL_KEYS)
    _number(value["schema_version"], 1, 1)
    _claim_valid(value["claim"], claim["ticket"], claim["transport"], claim["target"], observed)
    _check(value["claim"] == claim, "Terminal identity differs")
    _utc_valid(value["closed_utc"])
    _number(value["closed_monotonic_ns"])
    _number(value["observed_byte_count"])
    _check(value["reason"] in ("END_OBSERVED", "EOF", "TIMEOUT", "ERROR"), "Unknown terminal reason")
    earliest = connection["connected_monotonic_ns"] if connection else claim["claimed_monotonic_ns"]
    _check(earliest <= value["closed_monotonic_ns"] <= observed, "Invalid terminal chronology")

def _records_valid(values, retained, ticket, mode, target, observed, timeout=None, environment=None):
    claim, connection, terminal = (values[key] for key in ("claim", "connection", "terminal"))
    if claim is None:
        _check(connection is None and terminal is None, "Receipt exists without claim")
        return
    _claim_valid(claim, ticket, mode, target, observed, timeout)
    if environment is not None:
        actual = (claim["boot_id"], claim["uid"], claim["directory_device"], claim["directory_inode"])
        _check(actual == environment, "Claim environment identity differs")
    retained["claim"] = claim
    if connection is not None:
        _connection_valid(connection, claim, observed)
        retained["connection"] = connection
    if terminal is not None:
        _terminal_valid(terminal, claim, connection, observed)
        retained["terminal"] = terminal
'''
_connection_schema = {}
exec(_CONNECTION_SCHEMA, _connection_schema)


_CONNECTION_REMOTE = r'''
import ctypes, os, socket, stat, sys, time

def _utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def _bounded_file(path, limit):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        parts, total = [], 0
        while total < limit:
            raw = os.read(fd, min(65536, limit - total))
            if not raw:
                return b"".join(parts)
            parts.append(raw)
            total += len(raw)
        raise ValueError("Metadata read bound exhausted")
    finally:
        os.close(fd)

def _boot():
    value = _bounded_file("/proc/sys/kernel/random/boot_id", 64).decode("ascii").strip()
    _check(re.fullmatch(r"[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}", value), "Invalid current boot identity")
    return value

def _process(pid):
    raw = _bounded_file("/proc/%d/stat" % pid, 65536).decode("utf-8", errors="replace")
    match = re.fullmatch(r"([0-9]+) \((.*)\) ([A-Za-z]) (.*)\n?", raw, re.DOTALL)
    _check(match is not None and int(match[1]) == pid, "Invalid process identity")
    fields = match[4].split()
    _check(len(fields) >= 19 and re.fullmatch(r"[0-9]+", fields[18]), "Invalid process start time")
    start = int(fields[18])
    _number(start)
    _check(match[3] not in ("Z", "X", "x"), "Receiver is not live")
    return start

def _file_identity(value):
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)

class _Directory:
    def __init__(self, ticket, create=False):
        self.root = self.tmp = self.fd = None
        self.name = "sumox26-dump-connection-" + ticket
        self.identity = None
        try:
            self.root = os.open("/", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            self.tmp = os.open("tmp", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root)
            self.tmp_identity = os.fstat(self.tmp)
            self.check_tmp(self.tmp_identity)
            if create:
                os.mkdir(self.name, 0o700, dir_fd=self.tmp)
            try:
                self.fd = os.open(self.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.tmp)
            except FileNotFoundError:
                _check(not create, "New ticket directory disappeared")
                return
            self.identity = os.fstat(self.fd)
            self.check_dir(self.identity)
            _check(self.stable(), "Ticket directory changed during admission")
        except BaseException:
            self.close()
            raise

    def check_tmp(self, value):
        _check(stat.S_ISDIR(value.st_mode) and value.st_uid == 0 and value.st_mode & stat.S_ISVTX, "Unsafe /tmp ancestry")

    def check_dir(self, value):
        _check(stat.S_ISDIR(value.st_mode) and value.st_uid == os.getuid() and stat.S_IMODE(value.st_mode) == 0o700, "Unsafe ticket directory")

    def stable(self):
        try:
            tmp = os.stat("tmp", dir_fd=self.root, follow_symlinks=False)
            self.check_tmp(tmp)
            _check((tmp.st_dev, tmp.st_ino) == (self.tmp_identity.st_dev, self.tmp_identity.st_ino), "Changed /tmp")
            current = os.stat(self.name, dir_fd=self.tmp, follow_symlinks=False)
            self.check_dir(current)
            return (current.st_dev, current.st_ino) == (self.identity.st_dev, self.identity.st_ino)
        except (OSError, ValueError):
            return False

    def check_file(self, value):
        _check(stat.S_ISREG(value.st_mode) and value.st_uid == os.getuid() and stat.S_IMODE(value.st_mode) == 0o600 and value.st_nlink == 1 and value.st_size <= 4096, "Unsafe receipt file")

    def read(self, name):
        try:
            fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=self.fd)
        except FileNotFoundError:
            return None
        try:
            before = os.fstat(fd)
            self.check_file(before)
            with os.fdopen(fd, "rb", closefd=False) as stream:
                raw = stream.read(4097)
            after = os.fstat(fd)
            named = os.stat(name, dir_fd=self.fd, follow_symlinks=False)
            self.check_file(after)
            self.check_file(named)
            _check(_file_identity(before) == _file_identity(after) == _file_identity(named) and len(raw) == before.st_size, "Receipt changed during read")
            return _json_read(raw, 4096)
        finally:
            os.close(fd)

    def publish(self, name, value):
        _check(self.stable(), "Ticket directory changed before publication")
        raw = json.dumps(value, separators=(",", ":"), allow_nan=False).encode("utf-8")
        _check(len(raw) <= 4096, "Receipt exceeds bound")
        temporary = "." + name + ".tmp"
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=self.fd)
        try:
            self.check_file(os.fstat(fd))
            offset = 0
            while offset < len(raw):
                count = os.write(fd, raw[offset:])
                _check(count > 0, "Receipt write made no progress")
                offset += count
            written = os.fstat(fd)
            self.check_file(written)
        finally:
            os.close(fd)
        _check(self.stable(), "Ticket directory changed during publication")
        named = os.stat(temporary, dir_fd=self.fd, follow_symlinks=False)
        self.check_file(named)
        _check(_file_identity(named) == _file_identity(written), "Temporary receipt changed")
        library = ctypes.CDLL(None, use_errno=True)
        rename = library.renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        if rename(self.fd, os.fsencode(temporary), self.fd, os.fsencode(name), 1) != 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))
        published = os.stat(name, dir_fd=self.fd, follow_symlinks=False)
        self.check_file(published)
        _check((published.st_dev, published.st_ino, published.st_size, published.st_mtime_ns) ==
               (written.st_dev, written.st_ino, written.st_size, written.st_mtime_ns), "Published receipt changed")
        _check(self.stable(), "Ticket directory changed after publication")

    def close(self):
        for key in ("fd", "tmp", "root"):
            fd = getattr(self, key)
            if fd is not None:
                setattr(self, key, None)
                os.close(fd)

def _socket_identity(pid, connection):
    link = os.readlink("/proc/%d/fd/%d" % (pid, connection["socket_fd"]))
    return link == "socket:[%d]" % connection["socket_inode"]

def _tcp_match(pid, connection):
    raw = _bounded_file("/proc/%d/net/tcp" % pid, 1024 * 1024)
    rows = raw.decode("ascii").splitlines()
    _check(raw.endswith(b"\n") and rows and "local_address" in rows[0] and len(rows) <= 4097, "Invalid or excessive TCP snapshot")
    found = []
    for row in rows[1:]:
        fields = row.split()
        _check(len(fields) >= 10 and re.fullmatch(r"[0-9]+", fields[9]) and re.fullmatch(r"[0-9A-F]{2}", fields[3]), "Malformed TCP row")
        _check(all(re.fullmatch(r"[0-9A-F]{8}:[0-9A-F]{4}", fields[i]) for i in (1, 2)), "Malformed TCP endpoint")
        if int(fields[9]) == connection["socket_inode"]:
            found.append((fields[1], fields[2], fields[3]))
    expected = ("0100007F:%04X" % connection["local_port"], "0100007F:1D4C", "01")
    return found == [expected]

def _live_state(claim, connection):
    try:
        pid, start = claim["receiver_pid"], claim["receiver_start_ticks"]
        _check(_process(pid) == start, "Receiver identity changed")
        if connection is not None:
            _check(_socket_identity(pid, connection), "Socket identity changed")
            _check(_tcp_match(pid, connection), "Socket is not established")
            _check(_socket_identity(pid, connection), "Socket identity changed")
        _check(_process(pid) == start, "Receiver identity changed")
        return "CONNECTED" if connection is not None else "PENDING"
    except (OSError, ValueError, UnicodeError):
        return "UNKNOWN"
'''


_CONNECTION_OBSERVER = r'''
def _observe(ticket, mode, target):
    retained = dict(claim=None, connection=None, terminal=None)
    directory = None
    error = None
    state = "PENDING"
    identity_lost = False
    try:
        _ticket_valid(ticket)
        _request_valid(target, mode)
        boot, uid = _boot(), os.getuid()
        directory = _Directory(ticket)
        if directory.fd is not None:
            values = {key: directory.read(name) for key, name in (("claim", "claim.json"), ("connection", "connected.json"), ("terminal", "terminal.json"))}
            environment = (boot, uid, directory.identity.st_dev, directory.identity.st_ino)
            _records_valid(values, retained, ticket, mode, target, time.monotonic_ns(), environment=environment)
            claim = retained["claim"]
            if claim is not None:
                state = "UNKNOWN"
                if retained["terminal"] is None and time.monotonic_ns() < claim["deadline_monotonic_ns"]:
                    state = _live_state(claim, retained["connection"])
        observed, observed_utc = time.monotonic_ns(), _utc()
        _records_valid(retained, {}, ticket, mode, target, observed)
        claim = retained["claim"]
        if retained["terminal"] is not None:
            state = "TERMINAL"
        elif claim is not None and observed >= claim["deadline_monotonic_ns"]:
            state = "EXPIRED"
        if directory.fd is not None and not directory.stable():
            identity_lost = True
            state = "UNKNOWN"
    except Exception as failure:
        error = dict(code="CONNECTION_METADATA", message=str(failure)[:512])
    finally:
        if directory is not None:
            directory.close()
    # Observation time follows all query work, including directory identity checks.
    observed, observed_utc = time.monotonic_ns(), _utc()
    if error is None:
        try:
            _records_valid(retained, {}, ticket, mode, target, observed)
            if identity_lost:
                state = "UNKNOWN"
            elif retained["terminal"] is not None:
                state = "TERMINAL"
            elif retained["claim"] is not None and observed >= retained["claim"]["deadline_monotonic_ns"]:
                state = "EXPIRED"
        except ValueError as failure:
            error = dict(code="CONNECTION_METADATA", message=str(failure)[:512])
    result = dict(observed_utc=observed_utc, observed_monotonic_ns=observed, **retained)
    result.update(error=error) if error is not None else result.update(state=state)
    encoded = json.dumps(result, separators=(",", ":"), allow_nan=False)
    _check(len(encoded.encode("utf-8")) <= 16384, "Observation exceeds bound")
    print(encoded)

_observe(sys.argv[1], sys.argv[2], sys.argv[3])
'''


_CONNECTION_RECEIVER = r'''
def _new_claim(directory, ticket, mode, target, started, timeout):
    claim = dict(schema_version=1, ticket=ticket, transport=mode, target=target,
                 boot_id=_boot(), uid=os.getuid(), directory_device=directory.identity.st_dev,
                 directory_inode=directory.identity.st_ino, receiver_pid=os.getpid(),
                 receiver_start_ticks=_process(os.getpid()), started_monotonic_ns=started,
                 claimed_utc=_utc(), claimed_monotonic_ns=time.monotonic_ns(),
                 deadline_monotonic_ns=started + timeout * 1000000000)
    _claim_valid(claim, ticket, mode, target, time.monotonic_ns(), timeout)
    directory.publish("claim.json", claim)
    return claim

def _connect(directory, claim, sock):
    moment = time.monotonic_ns()
    if moment >= claim["deadline_monotonic_ns"]:
        raise TimeoutError("capture deadline after connect")
    local, peer = sock.getsockname(), sock.getpeername()
    fd = sock.fileno()
    native = os.fstat(fd)
    _check(stat.S_ISSOCK(native.st_mode), "Connected fd is not a socket")
    connection = dict(schema_version=1, claim=claim, event="TCP_CONNECTED",
        local_address=local[0], local_port=local[1], peer_address=peer[0], peer_port=peer[1],
        socket_fd=fd, socket_inode=native.st_ino, connected_utc=_utc(), connected_monotonic_ns=moment)
    _connection_valid(connection, claim, time.monotonic_ns())
    directory.publish("connected.json", connection)
    return connection

def _receive(sock, deadline, evidence):
    pending = b""
    limit = 16 * 1024 * 1024
    while True:
        remaining = deadline - time.monotonic_ns()
        if remaining <= 0:
            raise TimeoutError("capture deadline")
        sock.settimeout(remaining / 1000000000)
        chunk = sock.recv(min(65536, limit - evidence["total"] + 1))
        evidence["total"] += len(chunk)
        if chunk:
            sys.stdout.buffer.write(base64.b64encode(chunk) + b"\n")
            sys.stdout.buffer.flush()
        if time.monotonic_ns() >= deadline:
            raise TimeoutError("capture deadline after recv")
        if not chunk:
            raise EOFError("Monitor closed before END")
        if evidence["total"] > limit:
            raise ValueError("capture byte limit")
        pending += chunk
        lines = pending.split(b"\n")
        pending = lines.pop()
        if any(len(line) > 1151 for line in lines) or len(pending) > 1151:
            raise ValueError("capture line limit")
        if any(line.startswith(b"END,") for line in lines):
            return

def _receiver(timeout, ticket, mode, target):
    started = time.monotonic_ns()
    _number(timeout, 1, 3600)
    _ticket_valid(ticket)
    _request_valid(target, mode)
    directory = sock = claim = connection = None
    failure = None
    reason = "ERROR"
    evidence = dict(total=0)
    try:
        directory = _Directory(ticket, create=True)
        claim = _new_claim(directory, ticket, mode, target, started, timeout)
        remaining = claim["deadline_monotonic_ns"] - time.monotonic_ns()
        if remaining <= 0:
            raise TimeoutError("capture deadline before connect")
        sock = socket.create_connection(("127.0.0.1", 7500), timeout=min(10, remaining / 1000000000))
        connection = _connect(directory, claim, sock)
        _receive(sock, claim["deadline_monotonic_ns"], evidence)
        reason = "END_OBSERVED"
    except BaseException as error:
        failure = error
        reason = "TIMEOUT" if isinstance(error, TimeoutError) else "EOF" if isinstance(error, EOFError) else "ERROR"
    close_failed = False
    if sock is not None:
        try:
            sock.close()
        except BaseException as error:
            close_failed = True
            failure = RuntimeError("Socket close failed: %s; prior error: %s" % (error, failure))
    try:
        if claim is not None and not close_failed:
            terminal = dict(schema_version=1, claim=claim, closed_utc=_utc(),
                closed_monotonic_ns=time.monotonic_ns(), observed_byte_count=evidence["total"], reason=reason)
            _terminal_valid(terminal, claim, connection, time.monotonic_ns())
            directory.publish("terminal.json", terminal)
    except BaseException as error:
        failure = RuntimeError("Terminal publication failed: %s; prior error: %s" % (error, failure))
    finally:
        if directory is not None:
            directory.close()
    if failure is not None:
        raise failure

import base64
_receiver(int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4])
'''


def _utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _validate_connection_request(target, ticket, timeout=...):
    _connection_schema["_ticket_valid"](ticket)
    mode = board.transport()
    _connection_schema["_request_valid"](target, mode)
    if timeout is not ...:
        _connection_schema["_number"](timeout, 1, 3600)
    return mode


def _connection_command(target, arguments, timeout):
    start, failure = _utc_now(), None
    try:
        result = board.remote(target, arguments, capture=True, timeout=timeout)
        output, stderr, code = result.stdout, result.stderr, result.returncode
        if code != 0:
            failure = subprocess.CalledProcessError(code, arguments, output, stderr)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        output, stderr = error.stdout or b"", error.stderr or b""
        code, failure = getattr(error, "returncode", None), error
    except (OSError, ValueError) as error:
        output, stderr, code, failure = b"", str(error), None, error
    stderr = stderr.decode("utf-8", errors="replace") if isinstance(stderr, bytes) else (stderr or "")
    outcome = dict(target=target, remote_argv=arguments, returncode=code,
                   start_utc=start, end_utc=_utc_now(), timeout_seconds=timeout,
                   timed_out=isinstance(failure, subprocess.TimeoutExpired),
                   stderr=stderr[:4096], stderr_truncated=len(stderr) > 4096)
    return output, outcome, failure


def _connection_envelope(ticket, outcome):
    return dict(schema_version=1, ticket=ticket, state=None, error=None,
                router_registration="UNKNOWN", hardware_permission=False, mcu_permission=False,
                query_start_utc=outcome["start_utc"], query_end_utc=outcome["end_utc"],
                observed_utc=None, observed_monotonic_ns=None,
                claim=None, connection=None, terminal=None, command_outcome=outcome)


def _connection_error(evidence, code, message):
    evidence["state"] = None
    evidence["error"] = dict(code=code, message=message)
    error = CaptureError(code, message)
    error.connection_evidence = evidence
    return error


def _validate_observation(raw, evidence, mode, target):
    schema = _connection_schema
    value = schema["_json_read"](raw, 16384)
    common = {"observed_utc", "observed_monotonic_ns", "claim", "connection", "terminal"}
    is_error = type(value) is dict and "error" in value
    schema["_keys"](value, common | {"error" if is_error else "state"})
    schema["_utc_valid"](value["observed_utc"])
    schema["_number"](value["observed_monotonic_ns"])
    evidence["observed_utc"] = value["observed_utc"]
    evidence["observed_monotonic_ns"] = value["observed_monotonic_ns"]
    schema["_records_valid"](value, evidence, evidence["ticket"], mode, target,
                             value["observed_monotonic_ns"])
    if is_error:
        error = value["error"]
        schema["_keys"](error, {"code", "message"})
        schema["_check"](error["code"] == "CONNECTION_METADATA" and type(error["message"]) is str and
                           len(error["message"]) <= 512, "Invalid remote error")
        raise _connection_error(evidence, "CONNECTION_METADATA", error["message"])
    state, claim, connection, terminal = (value[key] for key in ("state", "claim", "connection", "terminal"))
    schema["_check"](state in ("PENDING", "CONNECTED", "TERMINAL", "EXPIRED", "UNKNOWN"), "Unknown observation state")
    if state == "TERMINAL":
        schema["_check"](terminal is not None, "TERMINAL lacks receipt")
    elif state == "EXPIRED":
        schema["_check"](claim is not None and terminal is None and value["observed_monotonic_ns"] >= claim["deadline_monotonic_ns"], "Invalid EXPIRED state")
    elif state in ("CONNECTED", "PENDING"):
        schema["_check"](terminal is None and (claim is None or value["observed_monotonic_ns"] < claim["deadline_monotonic_ns"]), "Invalid live-state chronology")
        schema["_check"]((state == "PENDING" and connection is None) or
                           (state == "CONNECTED" and claim is not None and connection is not None), "Invalid live-state records")
    evidence["state"] = state


def observe_connection(target, connection_ticket):
    mode = _validate_connection_request(target, connection_ticket)
    program = _CONNECTION_SCHEMA + _CONNECTION_REMOTE + _CONNECTION_OBSERVER
    arguments = ["python3", "-u", "-c", program, connection_ticket, mode, target]
    output, outcome, failure = _connection_command(target, arguments, 5)
    evidence = _connection_envelope(connection_ticket, outcome)
    if failure is not None:
        raise _connection_error(evidence, "CONNECTION_TRANSPORT", "Connection observation command failed or timed out.") from failure
    try:
        _validate_observation(output, evidence, mode, target)
    except CaptureError:
        raise
    except (ValueError, TypeError, KeyError, RecursionError) as error:
        raise _connection_error(evidence, "CONNECTION_METADATA", str(error)) from error
    return evidence


class LiveCapture:
    def __init__(self, target, timeout, *, connection_ticket=None):
        self.target, self.timeout, self.outcome = target, timeout, None
        self.connection_ticket = connection_ticket
        self.connection_evidence = None
        self._receive_failure = None
        if connection_ticket is not None:
            _validate_connection_request(target, connection_ticket, timeout)

    def __iter__(self):
        if self.connection_ticket is not None:
            yield from self._connected_iter()
            return
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

    def _final_connection(self):
        try:
            self.connection_evidence = observe_connection(self.target, self.connection_ticket)
        except CaptureError as error:
            self.connection_evidence = error.connection_evidence
            return error
        evidence = self.connection_evidence
        try:
            require(evidence["state"] == "TERMINAL" and evidence["claim"] is not None and
                    evidence["connection"] is not None and evidence["terminal"] is not None and
                    evidence["terminal"]["reason"] == "END_OBSERVED",
                    "CONNECTION_METADATA", "Capture lacks verified END_OBSERVED terminal evidence.")
            _connection_schema["_claim_valid"](evidence["claim"], self.connection_ticket,
                board.transport(), self.target, evidence["observed_monotonic_ns"], self.timeout)
        except (CaptureError, ValueError) as error:
            return _connection_error(evidence, "CONNECTION_METADATA", str(error))
        return None

    def _connected_iter(self):
        mode = _validate_connection_request(self.target, self.connection_ticket, self.timeout)
        program = _CONNECTION_SCHEMA + _CONNECTION_REMOTE + _CONNECTION_RECEIVER
        arguments = ["python3", "-u", "-c", program, str(self.timeout), self.connection_ticket, mode, self.target]
        output, self.outcome, failure = _connection_command(self.target, arguments, self.timeout + 15)
        if failure is not None:
            self._receive_failure = CaptureError("TRANSPORT", "Receive-only remote command failed or timed out.")
        deferred = self._final_connection()  # Query even when the receive failed or its wire is malformed.
        if self._receive_failure is not None:
            self._receive_failure.connection_evidence = self.connection_evidence
        try:
            require(isinstance(output, (str, bytes)), "TRANSPORT", "Invalid remote capture encoding type.")
            encoded = output if isinstance(output, bytes) else output.encode("ascii", errors="strict")
            require(len(encoded) <= MAX_BYTES * 2, "TRANSPORT", "Remote capture exceeds its encoded limit.")
            for line in encoded.splitlines(keepends=True):
                if not line.endswith(b"\n") and failure is not None:
                    break
                require(line.endswith(b"\n"), "TRANSPORT", "Truncated remote capture encoding.")
                yield base64.b64decode(line.rstrip(b"\r\n"), validate=True)
        except ValueError as error:
            if self._receive_failure is not None:
                raise self._receive_failure from error
            raise
        if self._receive_failure is not None:
            raise self._receive_failure from failure
        if deferred is not None:
            raise deferred


def live_chunks(target, timeout, *, connection_ticket=None):
    return LiveCapture(target, timeout, connection_ticket=connection_ticket)


def _cli_arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=argparse.SUPPRESS,
                        help="Offline wire fixture; never contacts a board")
    parser.add_argument("--output-dir", type=Path, default=argparse.SUPPRESS)
    parser.add_argument("--timeout", type=int, default=argparse.SUPPRESS)
    parser.add_argument("--expected-session", type=session_argument, default=argparse.SUPPRESS,
                        help="Reject every envelope outside this positive uint64 attempt identity")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--connection-ticket", help="Fresh caller-generated UUID hex for this capture")
    modes.add_argument("--observe-connection", help="Observe only this ticket's current TCP connection")
    for key in IDENTITIES:
        parser.add_argument("--" + key.replace("_", "-"), default=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    capture_only = {"input", "output_dir", "timeout", "expected_session", *IDENTITIES}
    if args.observe_connection is not None and capture_only.intersection(vars(args)):
        parser.error("Observer mode cannot include capture-only options.")
    defaults = dict(input=None, output_dir=board.ROOT / "logs", timeout=330, expected_session=None,
                    **{key: None for key in IDENTITIES})
    for key, value in defaults.items():
        if not hasattr(args, key):
            setattr(args, key, value)
    return parser, args


def _validate_cli(parser, args, identities):
    ticket = args.observe_connection if args.observe_connection is not None else args.connection_ticket
    try:
        if ticket is not None:
            _connection_schema["_ticket_valid"](ticket)
            require(args.input is None, "MODE", "Offline input cannot use a connection ticket.")
        if args.observe_connection is None:
            require(1 <= args.timeout <= 3600, "TIMEOUT", "Timeout must be 1..3600 seconds.")
            declarations("offline", None, identities)
            output_path(args.output_dir)
            if args.input is not None:
                path = local_path(args.input)
                require(path.is_file() and stat.S_ISREG(path.stat().st_mode), "INPUT", "Input must be a regular file.")
        if ticket is not None:
            require("SUMO_TRANSPORT" in os.environ, "MODE", "Connection-ticket modes require explicit SUMO_TRANSPORT.")
            target, mode = board.target(), board.transport()
            _validate_connection_request(target, ticket)
            return target, mode
    except (ValueError, OSError) as error:
        parser.error(str(error))
    return None, None


def _observe_cli(target, ticket):
    try:
        evidence = observe_connection(target, ticket)
    except CaptureError as error:
        print(json.dumps(error.connection_evidence, sort_keys=True))
        print("ERROR: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps(evidence, sort_keys=True))
    return 0


def main(argv=None):
    parser, args = _cli_arguments(argv)
    identities = {key: getattr(args, key) for key in IDENTITIES}
    target, mode = _validate_cli(parser, args, identities)
    if args.observe_connection is not None:
        return _observe_cli(target, args.observe_connection)
    try:
        if args.connection_ticket is None:
            target = None if args.input is not None else board.target()
            mode = "offline" if args.input is not None else board.transport()
        if args.input is None and args.connection_ticket is None:
            board.require_transport()
        if args.input is not None:
            chunks = offline_chunks(args.input)
        elif args.connection_ticket is None:
            chunks = live_chunks(target, args.timeout)
        else:
            chunks = live_chunks(target, args.timeout, connection_ticket=args.connection_ticket)
        destination = save_capture(chunks, args.output_dir, receive_mode=mode, target=target,
                                   expected_session=args.expected_session, **identities)
        print(destination)
        return 0
    except (CaptureError, csv._InvalidInput, OSError, ValueError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
