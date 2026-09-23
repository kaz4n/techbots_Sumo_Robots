# Validates local D-073 CSV bytes and D-074 owner/provenance declarations.
# Keeps offline file integrity separate from recording and physical acceptance.
# Independent D-074 tooling tests cover wire fixtures, bounded reads and reports.
"""Read-only local evidence validation; no transport or hardware qualification."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct


MAX_CSV_BYTES = 16 * 1024 * 1024
MAX_LINE_BYTES = 1023
MAX_MANIFEST_BYTES = 16384
UINT32_MAX = (1 << 32) - 1
UINT64_MAX = (1 << 64) - 1
ROLES = ("frames", "events", "summary")

FRAME_FIELDS = (
    "schema_version", "ordinal", "pack_status", "t_ms", "state", "mode",
    "line_mask", "opp_mask", "heading_cdeg", "gyro_z_dps10", "ax_mg", "ay_mg",
    "duty_l_127", "duty_r_127", "vbat_cv", "flags", "tick_max_us", "raw_hex",
)
EVENT_FIELDS = (
    "schema_version", "ordinal", "t_us", "type", "detail", "value", "raw_hex",
)
SUMMARY_FIELDS = (
    "schema_version", "epoch_token", "last_frame_token", "release_us", "mode",
    "phase", "observed_results", "missing_results", "rejected_results",
    "identity_rejected", "malformed_batches", "event_semantic_rejected",
    "upstream_event_rejected", "upstream_event_invalid", "source_regressions",
    "skipped_frames", "ticks", "overruns", "tick_max_us", "ticks_saturated",
    "upstream_event_overflow", "timing_incomplete", "recording_incomplete",
    "go_seen", "final_frame_missing", "interrupted", "terminal_exhausted",
    "frame_count", "frame_overwritten", "frame_rejected_status", "frame_clamped",
    "frame_invalid", "event_count", "event_overflow", "event_rejected", "incomplete",
)
HEADERS = {"frames": FRAME_FIELDS, "events": EVENT_FIELDS, "summary": SUMMARY_FIELDS}
BOOLEAN_FIELDS = frozenset((
    "ticks_saturated", "upstream_event_overflow", "timing_incomplete",
    "recording_incomplete", "go_seen", "final_frame_missing", "interrupted",
    "terminal_exhausted", "event_overflow", "incomplete",
))
U64_FIELDS = frozenset(("epoch_token", "last_frame_token", "ticks", "overruns"))
LOSS_FIELDS = (
    "missing_results", "rejected_results", "identity_rejected", "malformed_batches",
    "event_semantic_rejected", "upstream_event_rejected", "upstream_event_invalid",
    "source_regressions", "skipped_frames", "frame_overwritten",
    "frame_rejected_status", "frame_clamped", "frame_invalid", "event_rejected",
    "event_overflow", "ticks_saturated", "upstream_event_overflow",
    "timing_incomplete", "recording_incomplete", "final_frame_missing",
    "interrupted", "terminal_exhausted",
)
FRAME_RANGES = (
    (1, 1), (0, UINT64_MAX), (0, 2), (0, UINT32_MAX),
    (0, 255), (0, 255), (0, 255), (0, 255), (-(1 << 31), (1 << 31) - 1),
    (-32768, 32767), (-32768, 32767), (-32768, 32767),
    (-128, 127), (-128, 127), (0, 65535), (0, 255), (0, 65535),
)
EVENT_RANGES = (
    (1, 1), (0, UINT64_MAX), (0, UINT32_MAX), (0, 255), (0, 255), (0, 65535),
)
FRAME_WIRE = struct.Struct("<IBBBBihhhbbHBH")
EVENT_WIRE = struct.Struct("<IBBH")
UNSIGNED_DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)\Z", re.ASCII)
SIGNED_DECIMAL = re.compile(r"(?:0|-?[1-9][0-9]*)\Z", re.ASCII)
NULLABLE_FIELDS = (
    "session_id", "origin", "firmware_revision", "source_sha256", "config_sha256",
    "log_hz", "frame_capacity", "event_capacity", "target",
)
MANIFEST_FIELDS = frozenset(("schema_version", "closure", "files") + NULLABLE_FIELDS)


class _InvalidInput(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _require(condition, code, message):
    if not condition:
        raise _InvalidInput(code, message)


def _identity(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _local_path(path):
    _require(isinstance(path, (str, Path)), "INVALID_PATH", "Path must be str or Path.")
    name = os.fspath(path)
    _require(bool(name), "INVALID_PATH", "Path must not be empty.")
    network_prefix = len(name) >= 2 and all(char in "\\/" for char in name[:2])
    _require(not network_prefix, "NONLOCAL_PATH",
             "Network paths are not local input files.")
    return name


@contextmanager
def _regular_input(path, maximum):
    name = _local_path(path)
    initial = os.lstat(name)
    _require(stat.S_ISREG(initial.st_mode), "NOT_REGULAR_FILE",
             "Input must be a regular file, not a directory or symlink.")
    with open(name, "rb") as source:
        before = os.fstat(source.fileno())
        _require(stat.S_ISREG(before.st_mode), "NOT_REGULAR_FILE",
                 "Opened input is not a regular file.")
        _require(_identity(initial) == _identity(before), "FILE_CHANGED",
                 "File identity, size or modification time changed before reading.")
        _require(before.st_size <= maximum, "FILE_TOO_LARGE",
                 "Input exceeds the {} byte limit.".format(maximum))
        yield source, before.st_size
        after = os.fstat(source.fileno())
        current = os.lstat(name)
        _require(stat.S_ISREG(current.st_mode) and
                 _identity(before) == _identity(after) == _identity(current),
                 "FILE_CHANGED", "File identity, size or modification time changed while reading.")


def _integer(token, minimum, maximum, field):
    limit = max(len(str(minimum)), len(str(maximum)))
    pattern = SIGNED_DECIMAL if minimum < 0 else UNSIGNED_DECIMAL
    _require(len(token) <= limit and pattern.fullmatch(token) is not None,
             "NONCANONICAL_INTEGER", "{} must be a bounded canonical decimal integer.".format(field))
    value = int(token)
    _require(minimum <= value <= maximum, "INTEGER_RANGE",
             "{} is outside {}..{}.".format(field, minimum, maximum))
    return value


def _summary_range(field):
    if field == "schema_version":
        return 1, 1
    if field in BOOLEAN_FIELDS:
        return 0, 1
    if field in U64_FIELDS:
        return 0, UINT64_MAX
    if field in ("mode", "phase"):
        return 0, 255
    return 0, UINT32_MAX


def _parse_row(role, text):
    fields = HEADERS[role]
    tokens = text.split(",")
    _require(len(tokens) == len(fields), "FIELD_COUNT",
             "{} row requires exactly {} fields.".format(role, len(fields)))
    if role == "summary":
        return {field: _integer(token, *_summary_range(field), field)
                for field, token in zip(fields, tokens)}
    ranges = FRAME_RANGES if role == "frames" else EVENT_RANGES
    values = [_integer(token, low, high, field)
              for field, token, (low, high) in zip(fields, tokens, ranges)]
    wire = FRAME_WIRE if role == "frames" else EVENT_WIRE
    raw = tokens[-1]
    _require(len(raw) == wire.size * 2 and
             re.fullmatch(r"[0-9a-f]+", raw, re.ASCII) is not None,
             "RAW_HEX", "raw_hex must contain exactly {} lowercase hex digits.".format(wire.size * 2))
    first = 3 if role == "frames" else 2
    _require(tuple(values[first:]) == wire.unpack(bytes.fromhex(raw)),
             "RAW_MISMATCH", "Payload numeric fields disagree with raw_hex wire bytes.")
    return dict(zip(fields[:-1], values))


def _line_text(line):
    _require(len(line) <= MAX_LINE_BYTES, "LINE_TOO_LONG",
             "Physical line exceeds {} bytes including LF.".format(MAX_LINE_BYTES))
    _require(line.endswith(b"\n"), "MISSING_LF", "Every physical line must end with LF.")
    _require(b"\r" not in line, "CR_NOT_ALLOWED", "CSV uses LF only; CR is not allowed.")
    try:
        return line[:-1].decode("ascii")
    except UnicodeDecodeError as error:
        raise _InvalidInput("NON_ASCII", "CSV contains non-ASCII bytes.") from error


def _read_csv(path, role):
    digest = hashlib.sha256()
    total = rows = line_number = 0
    details = {"clamped": 0, "invalid": 0, "summary": None}
    with _regular_input(path, MAX_CSV_BYTES) as (source, expected_size):
        while True:
            line = source.readline(min(MAX_LINE_BYTES + 1, MAX_CSV_BYTES - total + 1))
            if not line:
                break
            total += len(line)
            digest.update(line)
            line_number += 1
            _require(total <= MAX_CSV_BYTES, "FILE_TOO_LARGE", "CSV exceeds the byte limit.")
            try:
                text = _line_text(line)
                if line_number == 1:
                    _require(text == ",".join(HEADERS[role]), "HEADER_MISMATCH",
                             "CSV header does not match the exact D-073 {} schema.".format(role))
                    continue
                _require(role != "summary" or rows == 0, "SUMMARY_ROW_COUNT",
                         "Summary requires exactly one data row.")
                parsed = _parse_row(role, text)
            except _InvalidInput as error:
                raise _InvalidInput(error.code, "Line {}: {}".format(line_number, error)) from error
            rows += 1
            if role == "summary":
                details["summary"] = parsed
            elif role == "frames":
                details["clamped"] += parsed["pack_status"] == 1
                details["invalid"] += parsed["pack_status"] == 2
        _require(total == expected_size, "FILE_CHANGED", "Read byte count differs from initial size.")
        _require(line_number > 0, "MISSING_HEADER", "CSV requires its exact header.")
        _require(role != "summary" or rows == 1, "SUMMARY_ROW_COUNT",
                 "Summary requires exactly one data row.")
    return {"sha256": digest.hexdigest(), "bytes": total, "rows": rows}, details


def _error(report, category, code, message):
    report["errors"].append({"category": category, "code": code, "message": message})


def _consistency_check(report, condition, code, message):
    if not condition:
        _error(report, "consistency", code, message)
        report["consistency"] = "FAIL"


def _check_owner(report, details):
    summary = details["summary"]["summary"]
    retained = details["frames"]
    report["consistency"] = "PASS"
    for role, field in (("frames", "frame_count"), ("events", "event_count")):
        _consistency_check(report, report["files"][role]["rows"] == summary[field],
                           "RETAINED_COUNT", "Retained {} rows disagree with {}.".format(role, field))
    for status in ("clamped", "invalid"):
        lifetime = summary["frame_" + status]
        count = retained[status]
        _consistency_check(report, lifetime >= count, "STATUS_LIFETIME",
                           "Lifetime {} count is below its retained count.".format(status))
        if summary["frame_overwritten"] == 0:
            _consistency_check(report, lifetime == count, "STATUS_WITHOUT_OVERWRITE",
                               "Without overwrites, lifetime and retained {} counts must agree.".format(status))
    excess = sum(summary["frame_" + key] - retained[key] for key in ("clamped", "invalid"))
    if summary["frame_overwritten"] < UINT32_MAX:
        _consistency_check(report, excess <= summary["frame_overwritten"],
                           "STATUS_OVERWRITE_BOUND", "Unretained status counts exceed recorded overwrites.")
    detailed_loss = any(summary[field] != 0 for field in LOSS_FIELDS)
    _consistency_check(report, bool(summary["incomplete"]) == detailed_loss,
                       "INCOMPLETE_CONTRADICTION", "Aggregate incomplete disagrees with detailed owner loss.")
    loss = detailed_loss or bool(summary["incomplete"]) or retained["clamped"] or retained["invalid"]
    phase = summary["phase"]
    lifecycle = {0: "EMPTY", 1: "UNFINISHED", 2: "UNFINISHED", 3: "SEALED", 4: "INTERRUPTED"}
    report["recording"] = {"loss": "REPORTED" if loss else "NONE_REPORTED",
                           "lifecycle": lifecycle.get(phase, "UNKNOWN"), "phase_code": phase}


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "DUPLICATE_KEY", "Manifest contains duplicate JSON key {}.".format(key))
        result[key] = value
    return result


def _json_integer(token):
    _require(len(token.lstrip("-")) <= 10, "MANIFEST_INTEGER", "Manifest integer exceeds the u32 width.")
    return int(token)


def _reject_json_number(token):
    raise _InvalidInput("MANIFEST_NUMBER", "Manifest requires integer numbers; {} is not allowed.".format(token))


def _exact_keys(value, keys, name):
    _require(isinstance(value, dict) and set(value) == set(keys), "MANIFEST_KEYS",
             "{} requires exactly these keys: {}.".format(name, ", ".join(sorted(keys))))


def _manifest_string(value, pattern, name):
    _require(isinstance(value, str) and re.fullmatch(pattern, value, re.ASCII) is not None,
             "MANIFEST_VALUE", "Manifest {} has an invalid string value.".format(name))


def _manifest_u32(value, minimum, name):
    _require(type(value) is int and minimum <= value <= UINT32_MAX, "MANIFEST_INTEGER",
             "Manifest {} must be an integer in {}..{}.".format(name, minimum, UINT32_MAX))


def _check_manifest_schema(manifest):
    _exact_keys(manifest, MANIFEST_FIELDS, "Manifest")
    _require(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
             "MANIFEST_VERSION", "Manifest schema_version must be integer 1.")
    _require(manifest["closure"] in ("unknown", "open", "closed"), "MANIFEST_CLOSURE",
             "Manifest closure must be unknown, open or closed.")
    patterns = {"session_id": r"[A-Za-z0-9_.-]{1,96}",
                "origin": r"(?:synthetic|hardware_reported)",
                "firmware_revision": r"(?:[0-9a-f]{40}|[0-9a-f]{64})",
                "source_sha256": r"[0-9a-f]{64}", "config_sha256": r"[0-9a-f]{64}",
                "target": r"[\x20-\x7e]{1,128}"}
    for field in NULLABLE_FIELDS:
        value = manifest[field]
        if value is None:
            continue
        if field in patterns:
            _manifest_string(value, patterns[field], field)
            _require(field != "target" or bool(value.strip()), "MANIFEST_TARGET",
                     "Manifest target must not be blank.")
        else:
            _manifest_u32(value, 1, field)
    _exact_keys(manifest["files"], ROLES, "Manifest files")
    for role in ROLES:
        entry = manifest["files"][role]
        _exact_keys(entry, ("sha256", "rows"), "Manifest files." + role)
        _manifest_string(entry["sha256"], r"[0-9a-f]{64}", role + ".sha256")
        _manifest_u32(entry["rows"], 0, role + ".rows")
    _require(manifest["files"]["summary"]["rows"] == 1, "MANIFEST_SUMMARY_ROWS",
             "Manifest summary rows must equal 1.")


def _read_manifest(path):
    with _regular_input(path, MAX_MANIFEST_BYTES) as (source, expected_size):
        raw = source.read(MAX_MANIFEST_BYTES + 1)
        _require(len(raw) <= MAX_MANIFEST_BYTES, "FILE_TOO_LARGE", "Manifest exceeds its byte limit.")
        _require(len(raw) == expected_size, "FILE_CHANGED", "Manifest byte count differs from initial size.")
    manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_object,
                          parse_int=_json_integer, parse_float=_reject_json_number,
                          parse_constant=_reject_json_number)
    _check_manifest_schema(manifest)
    return manifest


def _check_manifest_files(manifest, files):
    for role in ROLES:
        actual = files[role]
        _require(actual is not None, "MANIFEST_FILE_UNAVAILABLE",
                 "Cannot accept manifest without complete valid {} bytes and rows.".format(role))
        declared = manifest["files"][role]
        _require(declared["sha256"] == actual["sha256"], "MANIFEST_HASH",
                 "Manifest {} SHA-256 does not match the supplied file.".format(role))
        _require(declared["rows"] == actual["rows"], "MANIFEST_ROWS",
                 "Manifest {} row count does not match the supplied file.".format(role))
    for role, field in (("frames", "frame_capacity"), ("events", "event_capacity")):
        capacity = manifest[field]
        _require(capacity is None or files[role]["rows"] <= capacity, "MANIFEST_CAPACITY",
                 "Retained {} rows exceed the declared capacity.".format(role))


def _provenance(manifest):
    partial = any(manifest[field] is None for field in NULLABLE_FIELDS)
    kind = {None: "UNKNOWN", "synthetic": "SYNTHETIC", "hardware_reported": "HARDWARE_REPORTED"}
    closure = {"unknown": "UNKNOWN", "open": "DECLARED_OPEN", "closed": "DECLARED_CLOSED"}
    return {"status": "PARTIAL_DECLARATION" if partial else "DECLARED",
            "evidence_kind": kind[manifest["origin"]],
            "closure": closure[manifest["closure"]], "declared": manifest}


def _new_report():
    return {
        "schema_version": 1, "format_integrity": "FAIL", "consistency": "NOT_CHECKED",
        "errors": [], "files": dict.fromkeys(ROLES),
        "recording": {"loss": "UNKNOWN", "lifecycle": "UNKNOWN", "phase_code": None},
        "provenance": {"status": "ABSENT", "evidence_kind": "UNKNOWN",
                       "closure": "UNKNOWN", "declared": None},
        "common_attempt_verified": False, "transport_verified": False,
        "hardware_acceptance": False,
    }


def _input_error(report, category, role, error):
    code = error.code if isinstance(error, _InvalidInput) else "INPUT_ERROR"
    message = str(error) or type(error).__name__
    _error(report, category, code, "{}: {}".format(role, message))


def validate_bundle(frames_path, events_path, summary_path, manifest_path=None):
    """Return local format, owner consistency and caller declaration results."""
    report = _new_report()
    details = {}
    errors = (_InvalidInput, OSError, ValueError, TypeError, OverflowError, RecursionError)
    for role, path in zip(ROLES, (frames_path, events_path, summary_path)):
        try:
            report["files"][role], details[role] = _read_csv(path, role)
        except errors as error:
            _input_error(report, "format", role, error)
    if all(report["files"][role] is not None for role in ROLES):
        report["format_integrity"] = "PASS"
        _check_owner(report, details)
    if manifest_path is not None:
        try:
            manifest = _read_manifest(manifest_path)
            _check_manifest_files(manifest, report["files"])
            report["provenance"] = _provenance(manifest)
        except errors as error:
            _input_error(report, "manifest", "manifest", error)
            report["provenance"]["status"] = "INVALID"
            report["consistency"] = "FAIL"
    return report


def main(argv=None):
    """Print one sorted JSON report; argparse alone handles usage and help."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", required=True, help="Local D-073 frames CSV")
    parser.add_argument("--events", required=True, help="Local D-073 events CSV")
    parser.add_argument("--summary", required=True, help="Local D-073 summary CSV")
    parser.add_argument("--manifest", help="Optional caller-declared manifest v1")
    args = parser.parse_args(argv)
    report = validate_bundle(args.frames, args.events, args.summary, args.manifest)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["format_integrity"] == report["consistency"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
