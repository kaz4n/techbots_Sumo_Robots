# Analyzes the D127 P3.1 countdown intervals in existing local recorder bundles.
# Separates timing arithmetic from evidence completeness and physical acceptance.
# Independent contract tests cover event semantics, wrap, snapshots and cohort limits.
"""Read-only analysis of 50 receipt-derived countdown intervals."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat


_spec = importlib.util.spec_from_file_location(
    "sumox_countdown_csv_validator", Path(__file__).with_name("validate_csv_bundle.py"))
csv_validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(csv_validator)

MAX_COHORT_BYTES = 256 * 1024
MAX_CSV_BYTES = 16 * 1024 * 1024
REQUIRED_ATTEMPTS = 50
REQUIRED_HOLD_US = 5100000
SPREAD_LIMIT_US = 5000
HALF_RANGE_US = 1 << 31
UINT32_MASK = (1 << 32) - 1
ROLES = ("frames", "events", "summary")
INPUT_ERRORS = (OSError, ValueError, TypeError, OverflowError, RecursionError)


class AnalysisError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _require(condition, code, message):
    if not condition:
        raise AnalysisError(code, message)


def _error(error):
    return {"code": getattr(error, "code", "INPUT_ERROR"),
            "message": str(error) or type(error).__name__}


def _local_path(path):
    _require(isinstance(path, (str, Path)), "INVALID_PATH", "Expected a local file path.")
    name = os.fspath(path)
    _require(bool(name), "INVALID_PATH", "File paths must not be empty.")
    network = len(name) >= 2 and all(char in "\\/" for char in name[:2])
    _require(not network, "NONLOCAL_PATH", "Network paths are not local evidence files.")
    return Path(name)


def _identity(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _read_regular(path, maximum):
    path = _local_path(path)
    initial = os.lstat(path)
    _require(stat.S_ISREG(initial.st_mode), "NOT_REGULAR_FILE",
             "Input must be a regular file, not a directory or symlink.")
    with open(path, "rb") as source:
        before = os.fstat(source.fileno())
        _require(stat.S_ISREG(before.st_mode) and _identity(initial) == _identity(before),
                 "FILE_CHANGED", "File identity changed before reading.")
        _require(before.st_size <= maximum, "FILE_TOO_LARGE", "Input exceeds its byte limit.")
        raw = source.read(maximum + 1)
        _require(len(raw) <= maximum, "FILE_TOO_LARGE", "Input exceeds its byte limit.")
        after = os.fstat(source.fileno())
        current = os.lstat(path)
        _require(stat.S_ISREG(current.st_mode) and len(raw) == before.st_size and
                 _identity(before) == _identity(after) == _identity(current),
                 "FILE_CHANGED", "File identity, size or modification time changed while reading.")
    return raw


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "DUPLICATE_KEY", "Duplicate JSON key: {}.".format(key))
        result[key] = value
    return result


def _json_integer(token):
    _require(len(token.lstrip("-")) <= 10, "JSON_INTEGER", "JSON integer exceeds the supported width.")
    return int(token)


def _reject_number(token):
    raise AnalysisError("JSON_NUMBER", "Only integer JSON numbers are supported: {}.".format(token))


def _keys(value, expected, name):
    _require(type(value) is dict and set(value) == set(expected), "SCHEMA_KEYS",
             "{} requires exactly: {}.".format(name, ", ".join(expected)))


def _check_attempt_schema(attempt, identifiers):
    _keys(attempt, ("id", "frames", "events", "summary", "manifest"), "Attempt")
    name = attempt["id"]
    _require(isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,96}", name),
             "ATTEMPT_ID", "Attempt ID must be 1..96 ASCII identifier characters.")
    _require(name not in identifiers, "DUPLICATE_ID", "Attempt IDs must be unique: {}.".format(name))
    identifiers.add(name)
    for role in (*ROLES, "manifest"):
        value = attempt[role]
        if role == "manifest" and value is None:
            continue
        _require(isinstance(value, str) and 1 <= len(value) <= 4096,
                 "ATTEMPT_PATH", "{} requires a nonempty path of at most 4096 characters.".format(role))


def _load_cohort(path):
    raw = _read_regular(path, MAX_COHORT_BYTES)
    cohort = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_object,
                        parse_int=_json_integer, parse_float=_reject_number,
                        parse_constant=_reject_number)
    _keys(cohort, ("schema_version", "countdown_ms", "countdown_margin_ms", "attempts"), "Cohort")
    for field, expected in (("schema_version", 1), ("countdown_ms", 5000), ("countdown_margin_ms", 100)):
        _require(type(cohort[field]) is int and cohort[field] == expected,
                 "UNSUPPORTED_CONFIGURATION", "{} must be integer {}.".format(field, expected))
    _require(type(cohort["attempts"]) is list and len(cohort["attempts"]) <= REQUIRED_ATTEMPTS,
             "ATTEMPT_COUNT", "Cohort requires an array of 0 through 50 attempts.")
    identifiers = set()
    for attempt in cohort["attempts"]:
        _check_attempt_schema(attempt, identifiers)
    return cohort


def _new_report():
    return {
        "schema_version": 1, "input_status": "INVALID", "evidence_status": "INVALID",
        "timing_status": "NOT_QUALIFIED", "required_attempts": REQUIRED_ATTEMPTS,
        "required_hold_us": REQUIRED_HOLD_US, "spread_limit_us": SPREAD_LIMIT_US,
        "qualified_attempts": 0, "minimum_delay_us": None, "maximum_delay_us": None,
        "spread_us": None, "attempts": [], "errors": [],
        "common_attempt_verified": False, "transport_verified": False, "hardware_acceptance": False,
    }


def _new_attempt(name):
    return {"id": name, "qualification": "QUALIFIED", "release_us": None,
            "go_delay_us": None, "first_delay_us": None, "hold_status": "NOT_EVALUATED",
            "errors": [], "validation": None}


def _mark(attempt, qualification, code, message):
    if qualification == "INVALID" or attempt["qualification"] != "INVALID":
        attempt["qualification"] = qualification
    attempt["errors"].append({"code": code, "message": message})


def _snapshot(path, expected):
    raw = _read_regular(path, MAX_CSV_BYTES)
    _require(len(raw) == expected["bytes"] and
             hashlib.sha256(raw).hexdigest() == expected["sha256"] and
             raw.count(b"\n") - 1 == expected["rows"], "SNAPSHOT_CHANGED",
             "Reopened bytes, hash or row count differ from the validated snapshot.")
    return raw


def _rows(raw, fields):
    # The full bytes were already validated and rebound before numeric decoding.
    for line in raw.splitlines()[1:]:
        values = line.decode("ascii").split(",")
        yield dict(zip(fields, (value if field == "raw_hex" else int(value)
                               for field, value in zip(fields, values))))


def _valid_payload(event, summary):
    if event["type"] in (0, 1):
        _require(1 <= event["detail"] <= 6 and event["value"] == 0,
                 "MARKER_PAYLOAD", "START and GO require mode 1..6 and value zero.")
        _require(event["detail"] == summary["mode"], "OWNER_MODE",
                 "START/GO mode disagrees with the owner summary.")
        if event["type"] == 0:
            _require(event["t_us"] == summary["release_us"], "OWNER_RELEASE",
                     "START timestamp disagrees with the owner release timestamp.")
        return
    mask, value = event["detail"], event["value"]
    left, right = value & 255, value >> 8
    _require(1 <= mask <= 3 and left != 128 and right != 128 and
             (mask & 1 or left == 0) and (mask & 2 or right == 0), "MARKER_PAYLOAD",
             "FIRST requires its wheel mask and compatible signed duty bytes.")


def _markers(raw, summary):
    markers = {}
    previous = -1
    for event in _rows(raw, csv_validator.EVENT_FIELDS):
        _require(event["ordinal"] > previous, "ORDINAL_ORDER", "Event ordinals must increase strictly.")
        previous = event["ordinal"]
        kind = event["type"]
        if kind not in (0, 1, 2):
            continue
        _require(kind not in markers, "DUPLICATE_MARKER", "Countdown marker {} repeats.".format(kind))
        _valid_payload(event, summary)
        markers[kind] = event
    order = [kind for kind in markers]
    _require(order == sorted(order), "MARKER_ORDER", "Countdown markers must occur START, GO, FIRST.")
    return markers


def _intervals(attempt, markers):
    missing = [str(kind) for kind in (0, 1, 2) if kind not in markers]
    if missing:
        _mark(attempt, "INCOMPLETE", "MISSING_MARKER", "Missing countdown markers: {}.".format(", ".join(missing)))
    if 0 not in markers:
        return
    release = markers[0]["t_us"]
    attempt["release_us"] = release
    offsets = {kind: (event["t_us"] - release) & UINT32_MASK
               for kind, event in markers.items() if kind != 0}
    ordered = not (1 in offsets and 2 in offsets and offsets[1] > offsets[2])
    if not ordered or any(value >= HALF_RANGE_US for value in offsets.values()):
        _mark(attempt, "INCOMPLETE", "AMBIGUOUS_TIME", "Countdown chronology is backward or ambiguous.")
        return
    attempt["go_delay_us"] = offsets.get(1)
    attempt["first_delay_us"] = offsets.get(2)
    if 2 in offsets:
        attempt["hold_status"] = "PASS" if offsets[2] >= REQUIRED_HOLD_US else "FAIL"


def _owner_qualification(attempt, summary, markers):
    sealed = summary["phase"] == 3
    complete_markers = len(markers) == 3
    owner_valid = summary["epoch_token"] > 0 and summary["go_seen"] == 1
    if sealed and complete_markers and not owner_valid:
        _mark(attempt, "INVALID", "OWNER_CONTRADICTION", "Sealed countdown markers contradict epoch_token or go_seen.")
    elif not sealed or not owner_valid:
        _mark(attempt, "INCOMPLETE", "OWNER_UNFINISHED", "Qualification requires SEALED, positive epoch and observed GO.")
    validation = attempt["validation"]
    if validation["recording"]["loss"] != "NONE_REPORTED" or summary["incomplete"]:
        _mark(attempt, "INCOMPLETE", "RECORDED_LOSS", "Recorded loss or incomplete data prevents qualification.")
    declared = validation["provenance"]["declared"]
    if declared is None or declared["closure"] != "closed":
        _mark(attempt, "INCOMPLETE", "CLOSURE_UNCONFIRMED", "A valid supplied manifest must declare closed.")


def _analyze_attempt(entry, directory):
    attempt = _new_attempt(entry["id"])
    try:
        paths = {role: None if entry[role] is None else directory / _local_path(entry[role])
                 for role in (*ROLES, "manifest")}
        validation = csv_validator.validate_bundle(
            paths["frames"], paths["events"], paths["summary"], paths["manifest"])
        attempt["validation"] = validation
        _require(validation["format_integrity"] == validation["consistency"] == "PASS" and
                 validation["provenance"]["status"] != "INVALID", "BUNDLE_INVALID",
                 "CSV format, owner consistency or supplied manifest validation failed.")
        events = _snapshot(paths["events"], validation["files"]["events"])
        summary_raw = _snapshot(paths["summary"], validation["files"]["summary"])
        summary = next(_rows(summary_raw, csv_validator.SUMMARY_FIELDS))
        markers = _markers(events, summary)
        _intervals(attempt, markers)
        _owner_qualification(attempt, summary, markers)
    except INPUT_ERRORS as error:
        detail = _error(error)
        _mark(attempt, "INVALID", detail["code"], detail["message"])
    return attempt


def _duplicate_bundles(attempts):
    groups = {}
    for attempt in attempts:
        validation = attempt["validation"]
        if validation is None or any(validation["files"][role] is None for role in ROLES):
            continue
        identity = tuple(validation["files"][role]["sha256"] for role in ROLES)
        groups.setdefault(identity, []).append(attempt)
    for group in groups.values():
        if len(group) > 1:
            for attempt in group:
                _mark(attempt, "INVALID", "DUPLICATE_BUNDLE", "This exact three-file bundle is reused in the cohort.")


def _summarize(report):
    attempts = report["attempts"]
    qualified = [attempt for attempt in attempts if attempt["qualification"] == "QUALIFIED"]
    delays = [attempt["first_delay_us"] for attempt in qualified]
    report["qualified_attempts"] = len(qualified)
    if delays:
        report["minimum_delay_us"] = min(delays)
        report["maximum_delay_us"] = max(delays)
        report["spread_us"] = max(delays) - min(delays)
    invalid = any(attempt["qualification"] == "INVALID" for attempt in attempts)
    complete = len(qualified) == REQUIRED_ATTEMPTS
    report["evidence_status"] = "INVALID" if invalid else "COMPLETE" if complete else "INCOMPLETE"
    if report["evidence_status"] == "COMPLETE":
        passed = min(delays) >= REQUIRED_HOLD_US and report["spread_us"] < SPREAD_LIMIT_US
        report["timing_status"] = "PASS" if passed else "FAIL"
    for attempt in attempts:
        report["errors"].extend({"code": error["code"], "message": "{}: {}".format(
            attempt["id"], error["message"])} for error in attempt["errors"])


def analyze_cohort(path):
    """Return D127 timing arithmetic and separate evidence qualification."""
    report = _new_report()
    try:
        cohort = _load_cohort(path)
        directory = Path(os.path.abspath(_local_path(path))).parent
    except INPUT_ERRORS as error:
        report["errors"].append(_error(error))
        return report
    report["input_status"] = "VALID"
    report["attempts"] = [_analyze_attempt(entry, directory) for entry in cohort["attempts"]]
    _duplicate_bundles(report["attempts"])
    _summarize(report)
    return report


def main(argv=None):
    """Print one JSON report; exit zero only when the timing cohort passes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", help="Local D127 cohort JSON")
    args = parser.parse_args(argv)
    report = analyze_cohort(args.cohort)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["timing_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
