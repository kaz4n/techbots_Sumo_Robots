# Decodes one fixed B4 AttemptRecorder byte image without transport or file output.
# Preserves raw evidence while separating CSV format, loss, lifecycle and provenance.
# Independent D216 tests use the observed layout and literal D073 CSV fixtures.
"""Pure decoding for the artifact-bound D215 recorder layout; no capture API."""

import hashlib
import json

from tools import validate_csv_bundle as _csv


MAX_BODY_BYTES = 1_048_576
MAX_LAYOUT_BYTES = 65_536
LAYOUT_SHA256 = "f9b4b1531b9f714fb2b424d9613787449b2172fcc7a0e96292dd51d37d8c0b2d"
_BINDING = {
    "source_sha256": "9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a",
    "artifacts_sha256": "0acaa30a4ba01ac5c9ff8c8fddc66c4bec94e033b1194ec63271f12affb6c085",
    "abi_sha256": "25bf57646977fec8b4614b06cfe2b3df2e3bb94172122b2ee8f5ceaaec6677bc",
    "profile": "b4-app-m0-static",
}
_OWNER = {"type": "recorder::AttemptRecorder", "address": 536954120,
          "bytes": 159200, "alignment": 8}
_ARRAYS = {"frames_.payloads_": (25, 5001),
           "frames_.statuses_": (1, 1251), "events_.events_": (8, 4096)}
_FIELDS = {
    **{"frames_." + key: "u32" for key in
       ("first_", "size_", "overwritten_", "rejected_status_", "clamped_", "invalid_")},
    "events_.size_": "u32", "events_.rejected_": "u32", "events_.overflowed_": "bool",
    "summary_.epoch_token": "u64", "summary_.last_frame_token": "u64",
    "summary_.release_us": "u32", "summary_.mode": "u8",
    **{"summary_." + key: "u32" for key in
       ("observed_results", "missing_results", "rejected_results", "identity_rejected",
        "malformed_batches", "event_semantic_rejected", "upstream_event_rejected",
        "upstream_event_invalid", "source_regressions", "skipped_frames")},
    "summary_.ticks.ticks": "u64", "summary_.ticks.overruns": "u64",
    "summary_.ticks.max_us": "u32", "summary_.ticks.saturated": "bool",
    **{"summary_." + key: "bool" for key in
       ("upstream_event_overflow", "timing_incomplete", "recording_incomplete",
        "go_seen", "final_frame_missing", "interrupted", "terminal_exhausted")},
    "phase_": "u8",
}
_WIDTHS = {"u8": 1, "u32": 4, "u64": 8, "bool": 1}
_SUMMARY_ALIASES = {
    "phase": "phase_", "ticks": "summary_.ticks.ticks",
    "overruns": "summary_.ticks.overruns", "tick_max_us": "summary_.ticks.max_us",
    "ticks_saturated": "summary_.ticks.saturated",
    "frame_count": "frames_.size_", "frame_overwritten": "frames_.overwritten_",
    "frame_rejected_status": "frames_.rejected_status_",
    "frame_clamped": "frames_.clamped_", "frame_invalid": "frames_.invalid_",
    "event_count": "events_.size_", "event_overflow": "events_.overflowed_",
    "event_rejected": "events_.rejected_",
}
_LIFECYCLE = {0: "EMPTY", 1: "UNFINISHED", 2: "UNFINISHED",
              3: "SEALED", 4: "INTERRUPTED"}


class _Refusal(Exception):
    def __init__(self, code, message, category="admission"):
        super().__init__(message)
        self.code, self.category = code, category


def _need(condition, code, message, category="admission"):
    if not condition:
        raise _Refusal(code, message, category)


def _keys(value, expected, label):
    _need(type(value) is dict and set(value) == set(expected),
          "LAYOUT_SCHEMA", label + " has unexpected keys.")


def _object(pairs):
    result = {}
    for key, value in pairs:
        _need(key not in result, "LAYOUT_SCHEMA", "Duplicate layout key: " + key)
        result[key] = value
    return result


def _number(token):
    raise _Refusal("LAYOUT_SCHEMA", "Layout numbers must be integers: " + token)


def _integers(value, names, label):
    _need(all(type(value[key]) is int for key in names),
          "LAYOUT_GEOMETRY", label + " requires exact integer geometry.")


def _geometry(layout):
    owner = layout["owner"]
    _keys(owner, _OWNER, "owner")
    _integers(owner, ("address", "bytes", "alignment"), "owner")
    _need(owner == _OWNER, "LAYOUT_GEOMETRY", "Owner differs from the observed extent.")
    _keys(layout["arrays"], _ARRAYS, "arrays")
    _keys(layout["fields"], _FIELDS, "fields")
    spans = []
    for name, (stride, count) in _ARRAYS.items():
        entry = layout["arrays"][name]
        _keys(entry, ("offset", "bytes", "stride", "count"), name)
        _integers(entry, ("offset", "bytes", "stride", "count"), name)
        _need((entry["stride"], entry["count"], entry["bytes"]) ==
              (stride, count, stride * count), "LAYOUT_GEOMETRY",
              name + " has an unsupported array extent.")
        spans.append((entry["offset"], entry["offset"] + entry["bytes"], name))
    for name, kind in _FIELDS.items():
        entry = layout["fields"][name]
        _keys(entry, ("offset", "bytes", "kind"), name)
        _integers(entry, ("offset", "bytes"), name)
        width = _WIDTHS[kind]
        _need(entry["kind"] == kind and entry["bytes"] == width and
              entry["offset"] % width == 0, "LAYOUT_GEOMETRY",
              name + " has an unsupported kind, width or alignment.")
        spans.append((entry["offset"], entry["offset"] + width, name))
    spans.sort()
    _need(all(0 <= start < end <= owner["bytes"] for start, end, _ in spans),
          "LAYOUT_GEOMETRY", "An interpreted extent leaves the owner.")
    _need(all(left[1] <= right[0] for left, right in zip(spans, spans[1:])),
          "LAYOUT_GEOMETRY", "Interpreted extents overlap.")


def _layout(layout_raw, digest):
    _need(digest == LAYOUT_SHA256, "LAYOUT_IDENTITY",
          "Supplied layout bytes do not match the fixed D215 map.")
    try:
        layout = json.loads(layout_raw.decode("utf-8"), object_pairs_hook=_object,
                            parse_float=_number, parse_constant=_number)
    except (UnicodeDecodeError, ValueError, RecursionError) as error:
        raise _Refusal("LAYOUT_SCHEMA", "Layout is not bounded valid JSON.") from error
    _keys(layout, ("schema", "binding", "byte_order", "owner", "arrays", "fields"),
          "layout")
    _need(layout["schema"] == "b4-recorder-layout-v1" and
          layout["byte_order"] == "little", "LAYOUT_SCHEMA",
          "Layout schema or byte order differs.")
    _keys(layout["binding"], _BINDING, "binding")
    _need(layout["binding"] == _BINDING, "LAYOUT_SCHEMA",
          "Layout source, artifact, ABI or profile binding differs.")
    _geometry(layout)
    return layout


def _report(body, layout_raw):
    report = _csv._new_report()
    report.update(
        schema="b4-recorder-decode-v1", raw_owner=body,
        raw_sha256=hashlib.sha256(body).hexdigest(),
        layout_sha256=hashlib.sha256(layout_raw).hexdigest(),
        layout_binding="FAIL", export_status="REFUSED", native_values={},
        summary=None, csv=dict.fromkeys(_csv.ROLES),
        body_origin="UNPROVEN", coherence="UNPROVEN")
    return report


def _native(body, layout, report):
    values = {}
    for name in _FIELDS:
        entry = layout["fields"][name]
        start = entry["offset"]
        values[name] = int.from_bytes(body[start:start + entry["bytes"]], "little")
    report["native_values"] = values
    phase = values["phase_"]
    report["recording"].update(phase_code=phase, lifecycle=_LIFECYCLE.get(phase, "UNKNOWN"))
    for name, kind in _FIELDS.items():
        _need(kind != "bool" or values[name] in (0, 1), "NATIVE_BOOL",
              name + " is not a canonical native bool.", "native")
    _need(values["frames_.first_"] < 5001, "FRAME_FIRST_RANGE",
          "Frame ring first index exceeds its capacity.", "native")
    _need(values["frames_.size_"] <= 5001, "FRAME_SIZE_RANGE",
          "Retained frame count exceeds its capacity.", "native")
    _need(values["events_.size_"] <= 4096, "EVENT_SIZE_RANGE",
          "Retained event count exceeds its capacity.", "native")
    return values


def _summary(values):
    summary = {"schema_version": 1}
    for field in _csv.SUMMARY_FIELDS[1:-1]:
        summary[field] = values[_SUMMARY_ALIASES.get(field, "summary_." + field)]
    summary["incomplete"] = int(any(summary[field] != 0 for field in _csv.LOSS_FIELDS))
    return summary


def _row(role, values, raw=None):
    parts = [str(value) for value in values]
    if raw is not None:
        parts.append(raw.hex())
    line = (",".join(parts) + "\n").encode("ascii")
    _csv._parse_row(role, _csv._line_text(line))
    return line


def _frames(body, layout, values):
    rows = []
    details = {"clamped": 0, "invalid": 0, "summary": None}
    payload = layout["arrays"]["frames_.payloads_"]["offset"]
    statuses = layout["arrays"]["frames_.statuses_"]["offset"]
    for ordinal in range(values["frames_.size_"]):
        slot = (values["frames_.first_"] + ordinal) % 5001
        status = (body[statuses + slot // 4] >> (2 * (slot % 4))) & 3
        _need(status != 3, "PACK_STATUS",
              "Retained frame ordinal {} has status 3.".format(ordinal), "native")
        raw = body[payload + slot * 25:payload + (slot + 1) * 25]
        rows.append(_row("frames", (1, ordinal, status, *_csv.FRAME_WIRE.unpack(raw)), raw))
        details["clamped"] += status == 1
        details["invalid"] += status == 2
    return rows, details


def _events(body, layout, values):
    rows = []
    start = layout["arrays"]["events_.events_"]["offset"]
    for ordinal in range(values["events_.size_"]):
        raw = body[start + ordinal * 8:start + (ordinal + 1) * 8]
        rows.append(_row("events", (1, ordinal, *_csv.EVENT_WIRE.unpack(raw)), raw))
    return rows


def _export(body, layout, values, report):
    summary = _summary(values)
    report["summary"] = summary
    report["recording"]["loss"] = "REPORTED" if summary["incomplete"] else "NONE_REPORTED"
    frame_rows, frame_details = _frames(body, layout, values)
    role_rows = {"frames": frame_rows, "events": _events(body, layout, values),
                 "summary": [_row("summary", (summary[key] for key in _csv.SUMMARY_FIELDS))]}
    outputs, files = {}, {}
    for role in _csv.ROLES:
        header = (",".join(_csv.HEADERS[role]) + "\n").encode("ascii")
        _csv._line_text(header)
        raw = header + b"".join(role_rows[role])
        _need(len(raw) <= _csv.MAX_CSV_BYTES, "CSV_FORMAT",
              role + " CSV exceeds the existing limit.", "format")
        outputs[role] = raw
        files[role] = {"sha256": hashlib.sha256(raw).hexdigest(),
                       "bytes": len(raw), "rows": len(role_rows[role])}
    report.update(csv=outputs, files=files, export_status="PASS", format_integrity="PASS")
    details = {"frames": frame_details, "events": {},
               "summary": {"summary": summary}}
    _csv._check_owner(report, details)


def decode_recorder(body: bytes, *, layout_raw: bytes) -> dict:
    """Decode the fixed owner bytes; valid CSV does not establish capture provenance."""
    if type(body) is not bytes or type(layout_raw) is not bytes:
        raise TypeError("body and layout_raw must be exact bytes.")
    if len(body) > MAX_BODY_BYTES:
        raise ValueError("body exceeds the 1 MiB input limit.")
    if len(layout_raw) > MAX_LAYOUT_BYTES:
        raise ValueError("layout_raw exceeds the 64 KiB input limit.")
    report = _report(body, layout_raw)
    try:
        layout = _layout(layout_raw, report["layout_sha256"])
        report["layout_binding"] = "PASS"
        _need(len(body) == layout["owner"]["bytes"], "OWNER_SIZE",
              "Body length differs from the observed recorder extent.")
        values = _native(body, layout, report)
        _export(body, layout, values, report)
    except _Refusal as error:
        _csv._error(report, error.category, error.code, str(error))
    except _csv._InvalidInput as error:
        _csv._error(report, "format", "CSV_FORMAT", str(error))
    return report

