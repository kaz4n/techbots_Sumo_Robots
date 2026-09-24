# Analyzes D129 target-loss intervals in existing local recorder bundles.
# Separates observed timing, evidence qualification and physical acceptance.
# Independent D130 tests cover grammar, owner checks, wrap and bound snapshots.
"""Read-only analysis of ten P4 target-loss acquisition-to-receipt intervals."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat


_spec = importlib.util.spec_from_file_location(
    "sumox_target_loss_csv_validator", Path(__file__).with_name("validate_csv_bundle.py"))
csv_validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(csv_validator)

MAX_COHORT_BYTES = 256 * 1024
MAX_CSV_BYTES = 16 * 1024 * 1024
REQUIRED_ATTEMPTS = 10
BOUND_US = 35000
HALF_RANGE_US = 1 << 31
UINT32_MASK = (1 << 32) - 1
ROLES = ("frames", "events", "summary")
TIME_FIELDS = ("source_start_us", "source_end_us", "brake_decision_us", "zero_applied_us")
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
    uri = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", name)
    _require(not network and not uri, "NONLOCAL_PATH", "Network paths are not local evidence files.")
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
        _local_path(value)


def _load_cohort(path):
    raw = _read_regular(path, MAX_COHORT_BYTES)
    cohort = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_object,
                        parse_int=_json_integer, parse_float=_reject_number,
                        parse_constant=_reject_number)
    _keys(cohort, ("schema_version", "opp_clear_ms", "extra_margin_ms", "attempts"), "Cohort")
    for field, expected in (("schema_version", 1), ("opp_clear_ms", 30), ("extra_margin_ms", 5)):
        _require(type(cohort[field]) is int and cohort[field] == expected,
                 "UNSUPPORTED_CONFIGURATION", "{} must be integer {}.".format(field, expected))
    _require(type(cohort["attempts"]) is list and len(cohort["attempts"]) <= REQUIRED_ATTEMPTS,
             "ATTEMPT_COUNT", "Cohort requires an array of 0 through 10 attempts.")
    identifiers = set()
    for attempt in cohort["attempts"]:
        _check_attempt_schema(attempt, identifiers)
    return cohort


def _new_report():
    return {
        "schema_version": 1, "input_status": "INVALID", "evidence_status": "INVALID",
        "timing_status": "NOT_QUALIFIED", "required_attempts": REQUIRED_ATTEMPTS,
        "bound_us": BOUND_US, "qualified_attempts": 0,
        "minimum_lower_delay_us": None, "maximum_upper_delay_us": None,
        "attempts": [], "errors": [], "hardware_acceptance": False,
        "transport_verified": False, "common_attempt_verified": False,
    }


def _new_attempt(name):
    return {"id": name, "qualification": "INCOMPLETE", "trace_status": "INVALID",
            "motors_allowed": None, **dict.fromkeys(TIME_FIELDS),
            "lower_delay_us": None, "upper_delay_us": None,
            "timing_status": "NOT_EVALUATED", "exclusion_detail": None,
            "errors": [], "validation": None}


def _note(attempt, code, message):
    attempt["errors"].append({"code": code, "message": message})


def _invalidate(attempt, code, message, trace_invalid=False):
    attempt["qualification"] = "INVALID"
    if trace_invalid:
        attempt["trace_status"] = "INVALID"
    for field in (*TIME_FIELDS, "lower_delay_us", "upper_delay_us"):
        attempt[field] = None
    attempt["timing_status"] = "NOT_EVALUATED"
    _note(attempt, code, message)


def _snapshot(path, expected):
    raw = _read_regular(path, MAX_CSV_BYTES)
    _require(len(raw) == expected["bytes"] and
             hashlib.sha256(raw).hexdigest() == expected["sha256"] and
             raw.count(b"\n") - 1 == expected["rows"], "SNAPSHOT_CHANGED",
             "Reopened bytes, hash or row count differ from the validated snapshot.")
    return raw


def _rows(raw, fields):
    # Numeric decoding uses only bytes already validated and bound to their hashes.
    for line in raw.splitlines()[1:]:
        values = line.decode("ascii").split(",")
        yield dict(zip(fields, (value if field == "raw_hex" else int(value)
                               for field, value in zip(fields, values))))


def _marker_payload(event, summary):
    _require(1 <= event["detail"] <= 6 and event["value"] == 0,
             "MARKER_PAYLOAD", "START and GO require mode 1..6 and value zero.")
    _require(event["detail"] == summary["mode"], "OWNER_MODE",
             "START/GO mode disagrees with the owner summary.")
    if event["type"] == 0:
        _require(event["t_us"] == summary["release_us"], "OWNER_RELEASE",
                 "START timestamp disagrees with the owner release timestamp.")


def _timing_payload(event):
    detail, value = event["detail"], event["value"]
    valid = value in (0x0101, 0x0105) if detail == 0 else 1 <= detail <= 12 and value == 1
    _require(valid, "TIMING_PAYLOAD", "Unknown or reserved timing detail/value.")


def _scan_events(raw, summary):
    markers, trace = {}, []
    previous = -1
    for position, event in enumerate(_rows(raw, csv_validator.EVENT_FIELDS)):
        _require(event["ordinal"] > previous, "ORDINAL_ORDER", "Event ordinals must increase strictly.")
        previous = event["ordinal"]
        event["position"] = position
        kind = event["type"]
        if kind in (0, 1):
            _require(kind not in markers, "DUPLICATE_MARKER", "START/GO markers must be unique.")
            _marker_payload(event, summary)
            markers[kind] = event
        elif kind == 10:
            _timing_payload(event)
            _require(len(trace) < 5, "TRACE_GRAMMAR", "A trace cannot exceed five timing records.")
            trace.append(event)
    if 0 in markers and 1 in markers:
        _require(markers[0]["position"] < markers[1]["position"],
                 "GO_ORDER", "GO must follow START in event order.")
        offset = (markers[1]["t_us"] - markers[0]["t_us"]) & UINT32_MASK
        _require(offset < HALF_RANGE_US, "AMBIGUOUS_TIME", "GO chronology is backward or ambiguous from START.")
    return markers, trace


def _trace_classification(sequence):
    if sequence == (0,):
        return "NOT_EXERCISED"
    if sequence in ((0, 1), (0, 1, 2), (0, 1, 2, 3)):
        return "INCOMPLETE"
    if sequence == (0, 1, 2, 3, 4):
        return "COMPLETE"
    before_source = len(sequence) == 2 and sequence[0] == 0 and 6 <= sequence[1] <= 10
    after_source = (len(sequence) == 4 and sequence[:3] == (0, 1, 2) and
                    sequence[3] in (5, 6, 7, 8, 9, 10, 12))
    if before_source or after_source or sequence == (0, 1, 2, 3, 11):
        return "EXCLUDED"
    raise AnalysisError("TRACE_GRAMMAR", "Timing records do not form a permitted trace or prefix.")


def _trace_order(markers, trace):
    header = trace[0]
    _require(header["detail"] == 0 and 0 in markers, "MISSING_HEADER",
             "Timing evidence requires a HEADER immediately after START.")
    start = markers[0]
    _require(header["position"] == start["position"] + 1 and header["t_us"] == start["t_us"],
             "HEADER_ORDER", "HEADER must immediately follow START with the same timestamp.")
    if len(trace) > 1 and 1 in markers:
        _require(start["position"] < markers[1]["position"] < trace[1]["position"],
                 "GO_ORDER", "GO must follow START and precede every non-header timing record.")
    by_detail = {event["detail"]: event for event in trace}
    if 1 in by_detail and 2 in by_detail:
        _require(by_detail[2]["position"] == by_detail[1]["position"] + 1,
                 "SOURCE_PAIR_ORDER", "Source START/END must be adjacent in full event order.")


def _trace_times(attempt, markers, trace):
    start = markers[0]["t_us"]
    times = [markers[1]["t_us"]] if 1 in markers else []
    by_detail = {event["detail"]: event for event in trace}
    for detail, field in enumerate(TIME_FIELDS, 1):
        if detail in by_detail:
            attempt[field] = by_detail[detail]["t_us"]
            times.append(attempt[field])
    offsets = [(value - start) & UINT32_MASK for value in times]
    _require(all(value < HALF_RANGE_US for value in offsets) and offsets == sorted(offsets),
             "AMBIGUOUS_TIME", "Trace prefix chronology is backward or ambiguous from START.")


def _interval(attempt):
    applied = attempt["zero_applied_us"]
    lower = (applied - attempt["source_end_us"]) & UINT32_MASK
    upper = (applied - attempt["source_start_us"]) & UINT32_MASK
    attempt["lower_delay_us"], attempt["upper_delay_us"] = lower, upper
    attempt["timing_status"] = "PASS" if upper <= BOUND_US else (
        "FAIL" if lower > BOUND_US else "INDETERMINATE")


def _decode_trace(attempt, markers, trace):
    if not trace:
        attempt["trace_status"] = "NOT_RECORDED"
        _note(attempt, "NOT_RECORDED", "No D129 timing records were retained.")
        return
    classification = _trace_classification(tuple(event["detail"] for event in trace))
    _trace_order(markers, trace)
    attempt["motors_allowed"] = trace[0]["value"] == 0x0105
    _trace_times(attempt, markers, trace)
    if classification == "EXCLUDED":
        attempt["exclusion_detail"] = trace[-1]["detail"]
        _note(attempt, "TRACE_EXCLUDED", "Candidate ended with timing detail {}.".format(trace[-1]["detail"]))
    if len(trace) > 1 and 1 not in markers:
        classification = "INCOMPLETE"
        _note(attempt, "MISSING_GO", "Non-header trace requires an explicit preceding GO marker.")
    attempt["trace_status"] = classification
    if classification == "COMPLETE":
        _interval(attempt)
    elif classification == "INCOMPLETE" and 1 in markers:
        _note(attempt, "TRACE_INCOMPLETE", "Timing evidence ends at a proper unfinished prefix.")


def _owner_qualification(attempt, summary, markers, trace):
    epoch = summary["epoch_token"] > 0
    needs_go = 1 in markers or len(trace) > 1
    if ((0 in markers or needs_go) and not epoch) or (needs_go and summary["go_seen"] != 1):
        _invalidate(attempt, "OWNER_CONTRADICTION", "Explicit event markers contradict epoch_token or go_seen.")
        return
    incomplete = []
    canceled_countdown = len(trace) == 1 and summary["go_seen"] == 0
    if summary["phase"] != 3 or not epoch or (summary["go_seen"] != 1 and not canceled_countdown):
        incomplete.append(("OWNER_UNFINISHED", "Qualification requires SEALED, positive epoch and observed GO."))
    validation = attempt["validation"]
    if validation["recording"]["loss"] != "NONE_REPORTED" or summary["incomplete"]:
        incomplete.append(("RECORDED_LOSS", "Recorded loss or incomplete data prevents qualification."))
    declared = validation["provenance"]["declared"]
    if declared is None or declared["closure"] != "closed":
        incomplete.append(("CLOSURE_UNCONFIRMED", "A valid supplied manifest must declare closed."))
    if attempt["motors_allowed"] is False:
        incomplete.append(("MOTORS_DISABLED", "M0 timing is diagnostic and cannot qualify a trial."))
    if len(trace) > 1 and 1 not in markers:
        incomplete.append(("OWNER_GO_MISSING", "Qualification requires an explicit GO before the candidate."))
    for code, message in incomplete:
        _note(attempt, code, message)
    classification = attempt["trace_status"]
    attempt["qualification"] = "INCOMPLETE" if incomplete else (
        "QUALIFIED" if classification == "COMPLETE" else classification)


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
        markers, trace = _scan_events(events, summary)
        _decode_trace(attempt, markers, trace)
        _owner_qualification(attempt, summary, markers, trace)
    except INPUT_ERRORS as error:
        detail = _error(error)
        _invalidate(attempt, detail["code"], detail["message"], trace_invalid=True)
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
                _invalidate(attempt, "DUPLICATE_BUNDLE", "This exact three-file bundle is reused in the cohort.")


def _summarize(report):
    attempts = report["attempts"]
    qualified = [attempt for attempt in attempts if attempt["qualification"] == "QUALIFIED"]
    report["qualified_attempts"] = len(qualified)
    if qualified:
        report["minimum_lower_delay_us"] = min(attempt["lower_delay_us"] for attempt in qualified)
        report["maximum_upper_delay_us"] = max(attempt["upper_delay_us"] for attempt in qualified)
    invalid = any(attempt["qualification"] == "INVALID" for attempt in attempts)
    complete = len(qualified) == REQUIRED_ATTEMPTS
    report["evidence_status"] = "INVALID" if invalid else "COMPLETE" if complete else "INCOMPLETE"
    if report["evidence_status"] == "COMPLETE":
        statuses = {attempt["timing_status"] for attempt in qualified}
        report["timing_status"] = "FAIL" if "FAIL" in statuses else (
            "INDETERMINATE" if "INDETERMINATE" in statuses else "PASS")
    for attempt in attempts:
        report["errors"].extend({"code": error["code"], "message": "{}: {}".format(
            attempt["id"], error["message"])} for error in attempt["errors"])


def analyze_cohort(path):
    """Return D130 interval arithmetic and separate evidence qualification."""
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
    """Print one JSON report; exit zero only when all ten qualified intervals pass."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cohort", help="Local D130 cohort JSON")
    args = parser.parse_args(argv)
    report = analyze_cohort(args.cohort)
    print(json.dumps(report, sort_keys=True))
    return 0 if report["timing_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
