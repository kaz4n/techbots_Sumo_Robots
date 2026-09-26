# Validates one fixed B4 capture bundle and passes its complete owner to D216.
# Keeps supplied raw evidence and structural success separate from hardware origin.
# Independent focused fixtures cover closure, flash, partials and pure decoding.
from datetime import datetime, timezone
import hashlib
import json
import math
import re

from tools import b4_recorder_capture as _capture
from tools import decode_b4_recorder as _decoder

MAX_RETURNED_BYTES = 65536
MAX_LAYOUT_BYTES = 65536
MAX_FILE_BYTES = 65536
MAX_FILES = 13
MAX_FILES_BYTES = 262144
LAYOUT_SHA256 = "f9b4b1531b9f714fb2b424d9613787449b2172fcc7a0e96292dd51d37d8c0b2d"
_REPORT_KEYS = ("schema", "run_id", "source_sha256", "status", "counts",
                "started_utc", "finished_utc", "started_monotonic",
                "finished_monotonic", "wait", "reads", "first_error",
                "postcheck_errors", "analysis")
_ENVELOPE_KEYS = ("schema", "action", "run_id", "source_sha256", "report",
                  "report_origin", "remote_result_path", "full_result_bytes",
                  "full_result_sha256", "first_error", "postcheck_errors")


class _Refusal(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _need(condition, code, message):
    if not condition:
        raise _Refusal(code, message)


def _keys(value, expected, code):
    _need(type(value) is dict and set(value) == set(expected), code,
          "Unexpected object fields.")


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _sha(value):
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _bounds(returned_raw, files, layout_raw):
    if (type(returned_raw) is not bytes or type(layout_raw) is not bytes
            or type(files) is not dict):
        raise TypeError("Reply/layout must be exact bytes and files an exact dict.")
    if len(returned_raw) > MAX_RETURNED_BYTES or len(layout_raw) > MAX_LAYOUT_BYTES:
        raise ValueError("Reply or layout exceeds its bound.")
    if len(files) > MAX_FILES:
        raise ValueError("Too many supplied files.")
    total = 0
    for name, raw in files.items():
        if type(name) is not str or type(raw) is not bytes:
            raise TypeError("File keys/values must be exact str/bytes.")
        if len(name) > 96 or len(raw) > MAX_FILE_BYTES:
            raise ValueError("File name or body exceeds its bound.")
        total += len(raw)
    if total > MAX_FILES_BYTES:
        raise ValueError("Supplied files exceed their total bound.")


def _object(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("Duplicate JSON key.")
        result[name] = value
    return result


def _constant(token):
    raise ValueError("Non-finite JSON number: " + token)


def _float(token):
    value = float(token)
    if not math.isfinite(value):
        raise ValueError("Non-finite JSON float.")
    return value


def _parse(raw):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_object,
                          parse_constant=_constant, parse_float=_float)
    except (ValueError, UnicodeError, TypeError, OverflowError, RecursionError) as error:
        raise _Refusal("INPUT_JSON", "Invalid bounded JSON: " + str(error)) from error


def _envelope(value):
    _keys(value, _ENVELOPE_KEYS, "ENVELOPE")
    bindings = _capture.fixed_bindings()
    expected = {"schema": "b4-recorder-action-v1", "action": "capture",
                "run_id": _capture.RUN_ID, "source_sha256": _capture.SOURCE,
                "report_origin": "returned",
                "remote_result_path": bindings["output"] + "/capture_result.json",
                "first_error": None, "postcheck_errors": []}
    _need(all(_capture._same(value[key], item) for key, item in expected.items()),
          "ENVELOPE", "Envelope identity or returned-close evidence differs.")
    _need(type(value["full_result_bytes"]) is int
          and 0 < value["full_result_bytes"] <= MAX_FILE_BYTES
          and _sha(value["full_result_sha256"]), "ENVELOPE",
          "Invalid durable report identity.")


def _utc(value):
    _need(type(value) is str and bool(value), "REPORT", "Invalid UTC timestamp.")
    try:
        result = datetime.fromisoformat(value)
        _need(result.utcoffset() == timezone.utc.utcoffset(None), "REPORT",
              "Timestamp is not timezone-aware UTC.")
        return result
    except (ValueError, OverflowError) as error:
        raise _Refusal("REPORT", "Invalid UTC timestamp.") from error


def _number(value):
    try:
        valid = type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        valid = False
    _need(valid, "REPORT", "Invalid monotonic timestamp.")
    return value


def _report(reply, raw):
    _need(len(raw) == reply["full_result_bytes"]
          and _digest(raw) == reply["full_result_sha256"], "REPORT",
          "Durable report bytes differ from the returned envelope.")
    value = _parse(raw)
    _keys(value, _REPORT_KEYS, "REPORT")
    _need(_capture._same(reply["report"], value), "REPORT",
          "Embedded and durable reports differ.")
    expected = {"schema": "b4-recorder-capture-result-v1",
                "run_id": _capture.RUN_ID, "source_sha256": _capture.SOURCE,
                "status": "COLLECTED", "wait": None, "first_error": None,
                "postcheck_errors": [], "counts": _capture.COUNTS}
    _need(all(_capture._same(value[key], item) for key, item in expected.items()),
          "REPORT", "Native completion, counts or closing checks differ.")
    started = _number(value["started_monotonic"])
    finished = _number(value["finished_monotonic"])
    _need(0 <= finished - started < 600, "REPORT", "Collection duration is invalid.")
    _need(_utc(value["started_utc"]) <= _utc(value["finished_utc"]),
          "REPORT", "UTC timestamps moved backward.")
    return value


def _reads(report, files, plan, result):
    rows = report["reads"]
    _need(type(rows) is list and len(rows) == 26, "READS", "Wrong read count.")
    samples = []
    for index, ((name, address, size), row) in enumerate(zip(plan, rows)):
        _keys(row, ("name", "address", "bytes", "sha256", "file"), "READS")
        expected = {"name": name, "address": address, "bytes": size,
                    "file": "{:02d}-{}.bin".format(index, name)}
        _need(all(_capture._same(row[key], val) for key, val in expected.items())
              and _sha(row["sha256"]), "READS", "Read identity/order differs.")
        if 7 <= index <= 18:
            raw = files[row["file"]]
            _need(len(raw) == size and _digest(raw) == row["sha256"], "READS",
                  "SRAM bytes differ: " + name)
            samples.append((name, address, raw))
            if index == 17:
                result["raw_owner"] = b"".join(item[2] for item in samples[1:])
    return samples


def _flash(report):
    analysis = report["analysis"]
    _need(type(analysis) is dict and type(analysis.get("flash")) is dict,
          "FLASH", "Missing flash evidence.")
    flash = analysis["flash"]
    _keys(flash, _capture.FLASH_KEYS, "FLASH")
    _need(all(value is True for value in flash.values()), "FLASH",
          "A complete flash comparison failed.")
    rows = {row["name"]: row for row in report["reads"]}
    for region, count in (("loader", 5), ("sketch", 2)):
        for index in range(count):
            tail = region + "." + str(index)
            _need(rows["before." + tail]["sha256"] == rows["after." + tail]["sha256"],
                  "FLASH", "Before/after flash hashes differ.")
    return flash


def _new_result(returned_raw, files, layout_raw):
    return {"schema": "b4-recorder-capture-decode-v1", "bundle_status": "REFUSED",
            "errors": [], "raw_returned": returned_raw,
            "returned_sha256": _digest(returned_raw), "raw_layout": layout_raw,
            "layout_sha256": _digest(layout_raw), "raw_files": dict(files),
            "file_hashes": {name: _digest(raw) for name, raw in files.items()},
            "raw_owner": None, "analysis": None, "decoder": None,
            "coherence": "UNPROVEN", "body_origin": "UNPROVEN",
            "common_attempt_verified": False, "transport_verified": False,
            "hardware_acceptance": False}


def decode_capture(returned_raw: bytes, *, files: dict, layout_raw: bytes) -> dict:
    _bounds(returned_raw, files, layout_raw)
    result = _new_result(returned_raw, files, layout_raw)
    files = result["raw_files"]
    stage = "INPUT_JSON"
    try:
        reply = _parse(returned_raw)
        stage = "ENVELOPE"
        _envelope(reply)
        stage = "FILES"
        plan = _capture.read_plan()
        expected = {"capture_result.json"} | {
            "{:02d}-{}.bin".format(i, plan[i][0]) for i in range(7, 19)}
        _need(set(files) == expected, "FILES", "Wrong complete retrieved file set.")
        stage = "REPORT"
        report = _report(reply, files["capture_result.json"])
        stage = "READS"
        samples = _reads(report, files, plan, result)
        stage = "FLASH"
        flash = _flash(report)
        stage = "ANALYSIS"
        analysis = _capture._analysis(samples, flash)
        _need(_capture._same(report["analysis"], analysis), "ANALYSIS",
              "Native analysis differs from the verified bytes.")
        result["analysis"] = analysis
        stage = "LAYOUT"
        _need(result["layout_sha256"] == LAYOUT_SHA256, "LAYOUT",
              "Fixed D215 layout bytes differ.")
        result["decoder"] = _decoder.decode_recorder(
            result["raw_owner"], layout_raw=layout_raw)
        result["bundle_status"] = "PASS"
    except _Refusal as error:
        result["errors"].append({"code": error.code, "message": str(error)})
    except (ValueError, TypeError, KeyError, IndexError, OverflowError,
            RecursionError, UnicodeError) as error:
        result["errors"].append({"code": stage, "message": str(error)})
    return result
