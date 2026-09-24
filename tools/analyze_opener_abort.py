# Analyzes source-bound D135 opener-abort records in local CSV bundles.
# Separates wire diagnostics and declared qualification from physical acceptance.
# Independent frozen D136 tests cover cue metadata, chronology, binding and loss.
"""Read-only analysis of one ten-attempt P5 qualified-opener-abort cohort."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat


_spec = importlib.util.spec_from_file_location(
    "sumox_opener_abort_csv_validator", Path(__file__).with_name("validate_csv_bundle.py"))
csv_validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(csv_validator)

MAX_COHORT_BYTES = 256 * 1024
MAX_CONFIG_BYTES = 256 * 1024
MAX_CSV_BYTES = 16 * 1024 * 1024
REQUIRED_ATTEMPTS = 10
HALF_RANGE_US = 1 << 31
UINT32_MASK = (1 << 32) - 1
ROLES = ("frames", "events", "summary")
TIME_FIELDS = ("read_start_us", "read_end_us", "qualified_us", "handover_us", "applied_us")
CONFIG_NAMES = ("TICK_US", "ATTACK_ENTER_TICKS", "MODE_ARC_ENABLED", "MODE_WAIT_ENABLED",
                "LOG_HZ", "LOG_EVENT_CAPACITY", "LOG_FRAME_WINDOW_MS")
SOURCE_KEYS = ("firmware_revision", "source_sha256", "config", "config_sha256", "flags")
FLAGS = {"-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_P5_ABORT_TIMING=1": False,
         "-DMATCH=0 -DMOTORS_ALLOWED=1 -DSUMOX_P5_ABORT_TIMING=1": True}
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
    _require(1 <= len(name) <= 4096, "INVALID_PATH", "Paths require 1..4096 characters.")
    network = len(name) >= 2 and all(char in "\\/" for char in name[:2])
    scheme = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", name)
    drive = re.match(r"^[A-Za-z]:", name)
    uri = scheme is not None and drive is None or "://" in name
    _require(not network and not uri, "NONLOCAL_PATH", "Network and URI paths are unsupported.")
    return Path(name)


def _identity(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def _read_regular(path, maximum):
    path = _local_path(path)
    initial = os.lstat(path)
    _require(stat.S_ISREG(initial.st_mode), "NOT_REGULAR_FILE", "Input must be regular and nonsymlink.")
    with open(path, "rb") as source:
        before = os.fstat(source.fileno())
        _require(stat.S_ISREG(before.st_mode) and _identity(initial) == _identity(before),
                 "FILE_CHANGED", "File identity changed before reading.")
        _require(before.st_size <= maximum, "FILE_TOO_LARGE", "Input exceeds its byte limit.")
        raw = source.read(maximum + 1)
        _require(len(raw) <= maximum, "FILE_TOO_LARGE", "Input exceeds its byte limit.")
        after, current = os.fstat(source.fileno()), os.lstat(path)
        _require(stat.S_ISREG(current.st_mode) and len(raw) == before.st_size and
                 _identity(before) == _identity(after) == _identity(current),
                 "FILE_CHANGED", "File identity, size or modification time changed during reading.")
    return raw


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "DUPLICATE_KEY", "Duplicate JSON key: {}.".format(key))
        result[key] = value
    return result


def _json_integer(token):
    _require(len(token.lstrip("-")) <= 10, "JSON_INTEGER", "JSON integer exceeds supported width.")
    return int(token)


def _reject_number(token):
    raise AnalysisError("JSON_NUMBER", "Only integer JSON numbers are supported: {}.".format(token))


def _keys(value, expected, name):
    _require(type(value) is dict and set(value) == set(expected), "SCHEMA_KEYS",
             "{} requires exactly: {}.".format(name, ", ".join(expected)))


def _source_schema(source):
    _keys(source, SOURCE_KEYS, "Source")
    patterns = {"firmware_revision": r"(?:[0-9a-f]{40}|[0-9a-f]{64})",
                "source_sha256": r"[0-9a-f]{64}", "config_sha256": r"[0-9a-f]{64}"}
    for name, pattern in patterns.items():
        _require(isinstance(source[name], str) and re.fullmatch(pattern, source[name]),
                 "SOURCE_IDENTITY", "Source {} has an invalid declaration.".format(name))
    _require(isinstance(source["flags"], str) and source["flags"] in FLAGS,
             "UNSUPPORTED_CONFIGURATION", "Only the exact D135 M0/M1 flag strings are supported.")
    _require(isinstance(source["config"], str), "SOURCE_PATH", "Config must be a local path string.")
    _local_path(source["config"])


def _attempt_schema(attempt, identifiers):
    _keys(attempt, ("id", "frames", "events", "summary", "manifest"), "Attempt")
    name = attempt["id"]
    _require(isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9_.-]{1,96}", name),
             "ATTEMPT_ID", "Attempt ID must be 1..96 ASCII identifier characters.")
    _require(name not in identifiers, "DUPLICATE_ID", "Attempt IDs must be unique.")
    identifiers.add(name)
    for role in (*ROLES, "manifest"):
        value = attempt[role]
        if role == "manifest" and value is None:
            continue
        _require(isinstance(value, str), "ATTEMPT_PATH", "Attempt paths must be strings.")
        _local_path(value)


def _load_cohort(path):
    raw = _read_regular(path, MAX_COHORT_BYTES)
    cohort = json.loads(raw.decode("utf-8"), object_pairs_hook=_json_object,
                        parse_int=_json_integer, parse_float=_reject_number,
                        parse_constant=_reject_number)
    _keys(cohort, ("schema_version", "mode", "source", "attempts"), "Cohort")
    _require(type(cohort["schema_version"]) is int and cohort["schema_version"] == 1,
             "SCHEMA_VERSION", "schema_version must be integer 1.")
    _require(type(cohort["mode"]) is int and 1 <= cohort["mode"] <= 6,
             "MODE", "Cohort mode must be an integer in 1..6.")
    _source_schema(cohort["source"])
    _require(type(cohort["attempts"]) is list and len(cohort["attempts"]) <= REQUIRED_ATTEMPTS,
             "ATTEMPT_COUNT", "Cohort requires an array of 0 through 10 attempts.")
    identifiers = set()
    for attempt in cohort["attempts"]:
        _attempt_schema(attempt, identifiers)
    return cohort


def _configuration(condition, message):
    _require(condition, "UNSUPPORTED_CONFIGURATION", message)


def _config_code(text):
    # Preserve boundaries; comments and literals cannot declare supported constants.
    token = re.compile(r'//|/\*|(?:u8|[uUL])?R"|["\']')
    output, cursor = [], 0
    while match := token.search(text, cursor):
        start, kind = match.start(), match.group()
        output.append(text[cursor:start])
        if kind == '//':
            end = text.find('\n', match.end())
            end = len(text) if end < 0 else end
        elif kind == '/*':
            end = text.find('*/', match.end())
            _configuration(end >= 0, "Unterminated configuration comment.")
            end += 2
        elif kind.endswith('R"'):
            opener = re.match(r'([^ ()\\\t\r\n]{0,16})\(', text[match.end():match.end() + 17])
            _configuration(opener is not None, "Unsupported configuration raw literal.")
            closing = ')' + opener.group(1) + '"'
            end = text.find(closing, match.end() + opener.end())
            _configuration(end >= 0, "Unterminated configuration raw literal.")
            end += len(closing)
        else:
            end = match.end()
            while end < len(text) and text[end] != kind:
                _configuration(text[end] not in '\r\n', "Unterminated configuration literal.")
                end += 2 if text[end] == '\\' else 1
            _configuration(end < len(text), "Unterminated configuration literal.")
            end += 1
        output.append(re.sub(r'[^\n]', ' ', text[start:end]))
        cursor = end
    output.append(text[cursor:])
    return ''.join(output)


def _config_directives(code):
    output, depth = [], 0
    for line in code.split('\n'):
        directive = re.match(r'^\s*#\s*([A-Za-z_][A-Za-z0-9_]*)', line)
        mentioned = any(re.search(r'\b' + name + r'\b', line) for name in CONFIG_NAMES)
        _configuration(not (mentioned and (depth or directive)),
                       "Supported constants cannot occur in macros or conditionals.")
        if directive:
            kind = directive.group(1)
            if kind in ('if', 'ifdef', 'ifndef'):
                depth += 1
            elif kind == 'endif':
                depth -= 1
                _configuration(depth >= 0, "Unmatched configuration conditional.")
            elif kind in ('else', 'elif'):
                _configuration(depth > 0, "Unmatched configuration conditional.")
        output.append(re.sub(r'[^\n]', ' ', line) if directive else line)
    _configuration(depth == 0, "Unterminated configuration conditional.")
    return '\n'.join(output)


def _without_declaration_decorations(prefix):
    # Decorations cannot hide an extra declaration; this never relaxes canonical spelling.
    output, cursor = [], 0
    pattern = re.compile(r'\[\[|\balignas\s*\(')
    while match := pattern.search(prefix, cursor):
        output.append(prefix[cursor:match.start()])
        start = match.start() if match.group() == '[[' else match.end() - 1
        opening = prefix[start]
        closing, depth, end = (']' if opening == '[' else ')'), 1, start + 1
        while end < len(prefix) and depth:
            depth += int(prefix[end] == opening) - int(prefix[end] == closing)
            end += 1
        _configuration(depth == 0, "Unterminated declaration decoration.")
        output.append(' ')
        cursor = end
    return ''.join(output) + prefix[cursor:]


def _parenthesized_declarator(prefix, suffix):
    opening = re.search(r'(?:\(\s*)+[\s*&]*$', prefix)
    if opening is None:
        return False
    count = opening.group().count('(')
    closing = re.match(r'(?:\s*\)){' + str(count) + r'}\s*(?:=(?!=)|[;\[({])', suffix)
    if closing is None:
        return False
    head = prefix[:opening.start()].strip()
    storage = r'(?:(?:inline|constexpr|consteval|constinit|static|extern|const|volatile|register|thread_local)\s+)*'
    qualified_type = r'(?:[A-Za-z_]\w*\s*::\s*)*[A-Za-z_]\w*'
    builtin_type = r'(?:(?:unsigned|signed|short|long)\s+)+(?:int|double|char|long)'
    # A direct initializer has both a type and another variable name before '('.
    typed = re.fullmatch(storage + r'(?:' + qualified_type + '|' + builtin_type + r')[\s*&]*', head)
    return typed is not None or _subsequent_declarator(head)


def _subsequent_declarator(prefix):
    # A comma outside an expression can start another declarator in the same statement.
    parentheses, brackets, comma = 0, 0, -1
    for index, char in enumerate(prefix):
        if char == '(':
            parentheses += 1
        elif char == ')':
            parentheses -= 1
        elif char == '[':
            brackets += 1
        elif char == ']':
            brackets -= 1
        elif char == ',' and parentheses == brackets == 0:
            comma = index
    return comma >= 0 and re.fullmatch(r'[\s*&]*', prefix[comma + 1:]) is not None


def _extra_declarator(prefix, suffix):
    prefix = _without_declaration_decorations(prefix)
    if _parenthesized_declarator(prefix, suffix):
        return True
    separate = ('=' not in prefix and re.fullmatch(r'[\w:\s*&]+', prefix) is not None)
    return (separate or _subsequent_declarator(prefix)) and re.match(r'\s*(?:;|\[|\(|\{)', suffix) is not None


def _config_value(code, name):
    pattern = (r'\binline\s+constexpr\s+std\s*::\s*uint32_t\s+' + name +
               r'\s*=\s*([0-9]+)[Uu]\s*;')
    matches = list(re.finditer(pattern, code))
    _configuration(len(matches) == 1, name + " requires one canonical unsigned declaration.")
    declaration = matches[0]
    prefix = code[:declaration.start()]
    boundary = max(prefix.rfind(';'), prefix.rfind('{'), prefix.rfind('}')) + 1
    _configuration(not prefix[boundary:].strip(), name + " has an unsupported declaration prefix.")
    for use in re.finditer(r'\b' + name + r'\b', code):
        if declaration.start() <= use.start() < declaration.end():
            continue
        prefix = code[:use.start()]
        boundary = max(prefix.rfind(';'), prefix.rfind('{'), prefix.rfind('}')) + 1
        prefix, suffix = prefix[boundary:], code[use.end():]
        assigned = re.match(r'\s*=(?!=)', suffix) is not None
        redeclared = _extra_declarator(prefix, suffix)
        _configuration(not assigned and not redeclared, name + " has a duplicate or unsupported declaration.")
    digits = declaration.group(1)
    _configuration(len(digits) <= 10 and (len(digits) == 1 or digits[0] != '0'),
                   name + " requires a bounded canonical decimal literal.")
    return int(digits)


def _extract_config(raw):
    text = raw.decode('utf-8')
    _configuration(re.search(r'\\[ \t\v\f]*\r?\n', text) is None,
                   "Physical configuration line splices are unsupported.")
    code = _config_code(text)
    _configuration(re.search(r'(?m)^[ \t\v\f\r]*%:', code) is None,
                   "Configuration digraph directives are unsupported.")
    code = _config_directives(code)
    values = {name: _config_value(code, name) for name in CONFIG_NAMES}
    _configuration(1 <= values['TICK_US'] < HALF_RANGE_US, "TICK_US is outside the supported range.")
    _configuration(1 <= values['ATTACK_ENTER_TICKS'] <= UINT32_MASK,
                   "ATTACK_ENTER_TICKS is outside the supported range.")
    _configuration(all(values[name] in (0, 1) for name in ('MODE_ARC_ENABLED', 'MODE_WAIT_ENABLED')),
                   "Mode availability constants require 0 or 1.")
    _configuration((values['LOG_HZ'], values['LOG_EVENT_CAPACITY'], values['LOG_FRAME_WINDOW_MS']) ==
                   (25, 4096, 200000), "Recorder constants do not identify the supported D135 profile.")
    return values


def _bind_source(descriptor, mode, directory, errors):
    source = {**descriptor, "config_values": None, "binding_status": "INVALID"}
    try:
        raw = _read_regular(directory / _local_path(descriptor['config']), MAX_CONFIG_BYTES)
        _require(hashlib.sha256(raw).hexdigest() == descriptor['config_sha256'],
                 "CONFIG_HASH", "Historical configuration bytes do not match their declaration.")
        source['config_values'] = _extract_config(raw)
        values = source['config_values']
        available = mode <= 3 or (mode in (4, 5) and values['MODE_ARC_ENABLED'] == 1)
        available = available or (mode == 6 and values['MODE_WAIT_ENABLED'] == 1)
        _configuration(available, "Requested mode is disabled by the historical configuration.")
        source['binding_status'] = 'DECLARED_MATCH'
    except INPUT_ERRORS as error:
        detail = _error(error)
        if isinstance(error, UnicodeError):
            detail['code'] = 'UNSUPPORTED_CONFIGURATION'
        errors.append(detail)
    return source


def decode_cue(value, mode):
    """Decode only combinations admitted by the D135 wire table; no source or I/O."""
    if type(value) is not int or not 0 <= value <= 65535 or type(mode) is not int or not 1 <= mode <= 6:
        return None
    encoded_mode, phase, cause = value & 7, (value >> 3) & 7, (value >> 6) & 3
    mask, snapshot = (value >> 8) & 127, bool(value & 32768)
    if encoded_mode != mode or cause not in (1, 2):
        return None
    front = mask & 7
    if mode == 3:
        valid = phase == 0 and ((cause == 1 and front != 0) or
                 (cause == 2 and front == 0 and mask & 0x78 != 0 and not snapshot))
    elif snapshot:
        valid = False
    elif mode in (4, 5):
        valid = phase in (2, 3) and cause == 1 and front != 0
    elif mode == 6 and phase == 4:
        valid = cause == 2 and mask & 0x78 != 0
    else:
        outer = 0x28 if mode == 2 else 0x50
        valid = phase in (1, 2, 3) and ((cause == 1 and phase != 1 and front != 0) or
                 (cause == 2 and mask & outer != 0 and (phase == 1 or front == 0)))
    if not valid:
        return None
    return {"mode": mode, "phase": phase, "cause": cause, "effective_mask": mask,
            "snapshot_front_present": snapshot}


def _new_report():
    return {"schema_version": 1, "input_status": "INVALID", "evidence_status": "INVALID",
            "timing_status": "NOT_QUALIFIED", "mode": None, "source": None,
            "required_attempts": REQUIRED_ATTEMPTS, "qualified_attempts": 0,
            "passing_attempts": 0, "logical_failures": 0, "minimum_elapsed_us": None,
            "maximum_elapsed_us": None, "attempts": [], "errors": [],
            "declared_physical_trials_status": "NOT_QUALIFIED", "hardware_acceptance": False,
            "transport_verified": False, "common_attempt_verified": False,
            "producer_semantics_verified": False}


def _new_attempt(name):
    return {"id": name, "qualification": "INCOMPLETE", "trace_status": "INVALID",
            "motors_allowed": None, "binding_status": "INVALID", **dict.fromkeys(TIME_FIELDS),
            "elapsed_us": None, "cue": None, "handover_state": None,
            "logical_status": "NOT_EVALUATED", "timing_status": "NOT_EVALUATED",
            "terminal_detail": None, "terminal_value": None, "errors": [], "validation": None}


def _note(attempt, code, message):
    attempt['errors'].append({"code": code, "message": message})


def _invalidate(attempt, code, message, trace_invalid=False):
    attempt['qualification'] = 'INVALID'
    if trace_invalid:
        attempt['trace_status'] = 'INVALID'
    for name in (*TIME_FIELDS, 'elapsed_us'):
        attempt[name] = None
    attempt['logical_status'] = attempt['timing_status'] = 'NOT_EVALUATED'
    _note(attempt, code, message)


def _snapshot(path, expected):
    raw = _read_regular(path, MAX_CSV_BYTES)
    _require(len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256']
             and raw.count(b'\n') - 1 == expected['rows'], "SNAPSHOT_CHANGED",
             "Reopened bytes, hash or row count differ from the accepted CSV snapshot.")
    return raw


def _rows(raw, fields):
    for line in raw.splitlines()[1:]:
        values = line.decode('ascii').split(',')
        yield dict(zip(fields, (value if field == 'raw_hex' else int(value)
                               for field, value in zip(fields, values))))


def _manifest_binding(attempt, source):
    declared = attempt['validation']['provenance']['declared']
    expected = {name: source[name] for name in ('firmware_revision', 'source_sha256', 'config_sha256')}
    expected.update(log_hz=25, frame_capacity=5001, event_capacity=4096)
    attempt['binding_status'] = 'INCOMPLETE' if declared is None else 'DECLARED_MATCH'
    if declared is None:
        _note(attempt, 'BINDING_MISSING', 'Qualification requires a matching declared source manifest.')
        return
    for name, value in expected.items():
        if declared[name] is None:
            attempt['binding_status'] = 'INCOMPLETE'
            _note(attempt, 'BINDING_MISSING', 'Manifest {} is undeclared.'.format(name))
        elif declared[name] != value:
            attempt['binding_status'] = 'INVALID'
            raise AnalysisError('BINDING_MISMATCH', 'Manifest {} differs from cohort source.'.format(name))


def _marker_payload(event, summary, mode):
    _require(event['detail'] == mode == summary['mode'] and event['value'] == 0,
             'MARKER_PAYLOAD', 'START/GO require the cohort and owner mode with value zero.')
    if event['type'] == 0:
        _require(event['t_us'] == summary['release_us'], 'OWNER_RELEASE',
                 'START timestamp differs from the owner release timestamp.')


def _timing_payload(event, mode):
    detail, value = event['detail'], event['value']
    if detail == 0:
        valid = value in (0x0201, 0x0205)
    elif detail == 18:
        event['cue'] = decode_cue(value, mode)
        valid = event['cue'] is not None
    elif detail in (16, 17, 20, 23, 24):
        valid = value == 1
    elif detail == 19:
        valid = value in (5, 6, 7)
    elif detail in (21, 22):
        valid = value in (1, 2)
    else:
        valid = detail == 25 and 0 <= value <= 11
    _require(valid, 'TIMING_PAYLOAD', 'Unknown or invalid D135 timing metadata.')


def _scan_events(raw, summary, mode):
    markers, trace, previous = {}, [], -1
    _require(summary['mode'] == mode, 'OWNER_MODE', 'Owner mode differs from cohort mode.')
    for position, event in enumerate(_rows(raw, csv_validator.EVENT_FIELDS)):
        _require(event['ordinal'] > previous, 'ORDINAL_ORDER', 'All event ordinals must strictly increase.')
        previous, event['position'] = event['ordinal'], position
        kind = event['type']
        if kind in (0, 1):
            _require(kind not in markers, 'DUPLICATE_MARKER', 'START and GO markers must be unique.')
            _marker_payload(event, summary, mode)
            markers[kind] = event
        elif kind == 10:
            _timing_payload(event, mode)
            _require(len(trace) < 6, 'TRACE_GRAMMAR', 'At most six timing records are permitted.')
            trace.append(event)
    if 0 in markers and 1 in markers:
        _require(markers[0]['position'] < markers[1]['position'], 'GO_ORDER', 'GO must follow START.')
        _require((markers[1]['t_us'] - markers[0]['t_us']) & UINT32_MASK < HALF_RANGE_US,
                 'AMBIGUOUS_TIME', 'GO chronology is backward or ambiguous from START.')
    return markers, trace


def _trace_classification(trace):
    sequence = tuple(event['detail'] for event in trace)
    prefix = (0, 16, 17, 18, 19)
    if sequence and len(sequence) <= len(prefix) and sequence == prefix[:len(sequence)]:
        return 'INCOMPLETE'
    if sequence == (0, 16, 17, 18, 19, 20):
        return 'COMPLETE'
    if sequence == (0, 16, 17, 18, 25):
        return 'HANDOVER_FAILED'
    excluded = ((0, 21), (0, 22), (0, 23), (0, 16, 17, 18, 22), (0, 16, 17, 18, 19, 24))
    if sequence in excluded or (sequence == (0, 16, 17, 18, 19, 22) and trace[-1]['value'] == 2):
        return 'EXCLUDED'
    raise AnalysisError('TRACE_GRAMMAR', 'Timing records do not form an admitted trace or prefix.')


def _trace_order(markers, trace):
    header = trace[0]
    _require(header['detail'] == 0 and 0 in markers, 'MISSING_HEADER',
             'A D135 HEADER immediately following START is required.')
    start = markers[0]
    _require(header['position'] == start['position'] + 1 and header['t_us'] == start['t_us'],
             'HEADER_ORDER', 'HEADER must immediately follow START with the same timestamp.')
    if len(trace) > 1 and 1 in markers:
        _require(start['position'] < markers[1]['position'] < trace[1]['position'],
                 'GO_ORDER', 'GO must precede all non-header timing records in full event order.')
    for earlier, later in zip(trace, trace[1:]):
        adjacent = earlier['detail'] in (16, 17, 18)
        if adjacent:
            _require(later['position'] == earlier['position'] + 1, 'SUFFIX_ORDER',
                     'The retained decision suffix must be adjacent in full event order.')


def _trace_times(attempt, markers, trace):
    by_detail = {event['detail']: event for event in trace}
    for detail, field in ((16, 'read_start_us'), (17, 'read_end_us'), (18, 'qualified_us'),
                          (19, 'handover_us'), (25, 'handover_us'), (20, 'applied_us')):
        if detail in by_detail:
            attempt[field] = by_detail[detail]['t_us']
    if 16 in by_detail:
        anchor = by_detail[16]['t_us']
        offsets = [(by_detail[d]['t_us'] - anchor) & UINT32_MASK for d in (16, 17, 18, 20)
                   if d in by_detail]
        _require(all(value < HALF_RANGE_US for value in offsets) and offsets == sorted(offsets),
                 'AMBIGUOUS_TIME', 'Source/decision/application chronology is backward or ambiguous.')
    if 18 in by_detail:
        decision = by_detail[18]['t_us']
        if 1 in markers:
            _require((decision - markers[1]['t_us']) & UINT32_MASK < HALF_RANGE_US,
                     'AMBIGUOUS_TIME', 'Qualified decision precedes GO or has an ambiguous offset.')
        for detail in (19, 25):
            if detail in by_detail:
                _require(by_detail[detail]['t_us'] == decision, 'DECISION_TIME',
                         'Handover success/failure must share the qualified decision timestamp.')
        if tuple(event['detail'] for event in trace) == (0, 16, 17, 18, 22):
            _require(trace[-1]['t_us'] == decision, 'DECISION_TIME',
                     'Final preemption must share the qualified decision timestamp.')


def _trace_observations(attempt, trace, values):
    by_detail = {event['detail']: event for event in trace}
    if 18 in by_detail:
        attempt['cue'] = by_detail[18]['cue']
    if 19 in by_detail or 25 in by_detail:
        handover = by_detail.get(19, by_detail.get(25))
        attempt['handover_state'] = handover['value']
    if 19 in by_detail:
        front = attempt['cue']['effective_mask'] & 7
        expected = 7 if not front else (6 if values['ATTACK_ENTER_TICKS'] == 1 and
                                        front in (2, 3, 5, 6, 7) else 5)
        _require(by_detail[19]['value'] == expected, 'HANDOVER_STATE',
                 'Success metadata contradicts source-bound normal current-mask routing.')


def _decode_trace(attempt, markers, trace, source):
    if not trace:
        attempt['trace_status'] = 'NOT_RECORDED'
        return
    classification = _trace_classification(trace)
    _trace_order(markers, trace)
    attempt['motors_allowed'] = trace[0]['value'] == 0x0205
    if attempt['motors_allowed'] != FLAGS[source['flags']]:
        attempt['binding_status'] = 'INVALID'
        raise AnalysisError('HEADER_PROFILE', 'P5 HEADER motor profile differs from declared flags.')
    _trace_times(attempt, markers, trace)
    _trace_observations(attempt, trace, source['config_values'])
    if classification in ('COMPLETE', 'HANDOVER_FAILED', 'EXCLUDED'):
        attempt['terminal_detail'], attempt['terminal_value'] = trace[-1]['detail'], trace[-1]['value']
    if len(trace) > 1 and 1 not in markers:
        classification = 'INCOMPLETE'
        _note(attempt, 'MISSING_GO', 'An explicit preceding GO is required for a timing result.')
    attempt['trace_status'] = classification
    if classification == 'COMPLETE':
        elapsed = (attempt['applied_us'] - attempt['qualified_us']) & UINT32_MASK
        attempt['elapsed_us'], attempt['logical_status'] = elapsed, 'PASS'
        attempt['timing_status'] = 'PASS' if elapsed <= source['config_values']['TICK_US'] else 'FAIL'
    elif classification == 'HANDOVER_FAILED':
        attempt['logical_status'] = 'FAIL'


def _owner_qualification(attempt, summary, markers, trace):
    epoch, needs_go = summary['epoch_token'] > 0, 1 in markers or len(trace) > 1
    if ((0 in markers or needs_go) and not epoch) or (needs_go and summary['go_seen'] != 1):
        _invalidate(attempt, 'OWNER_CONTRADICTION', 'Events contradict owner epoch_token or go_seen.')
        return
    incomplete = []
    if summary['phase'] != 3 or not epoch or summary['go_seen'] != 1 or 1 not in markers:
        incomplete.append(('OWNER_UNFINISHED', 'Qualification requires SEALED, positive epoch and explicit GO.'))
    validation = attempt['validation']
    if validation['recording']['loss'] != 'NONE_REPORTED' or summary['incomplete']:
        incomplete.append(('RECORDED_LOSS', 'Any recorded loss or aggregate incomplete prevents qualification.'))
    declared = validation['provenance']['declared']
    if declared is None or declared['closure'] != 'closed':
        incomplete.append(('CLOSURE_UNCONFIRMED', 'A valid manifest must explicitly declare closed.'))
    if attempt['motors_allowed'] is False:
        incomplete.append(('MOTORS_DISABLED', 'M0 observations are diagnostic only.'))
    if attempt['binding_status'] != 'DECLARED_MATCH':
        incomplete.append(('BINDING_INCOMPLETE', 'Qualification requires all declared identities to match.'))
    for code, message in incomplete:
        _note(attempt, code, message)
    classification = attempt['trace_status']
    attempt['qualification'] = 'INCOMPLETE' if incomplete else (
        'QUALIFIED' if classification in ('COMPLETE', 'HANDOVER_FAILED') else classification)


def _analyze_attempt(entry, directory, mode, source):
    attempt = _new_attempt(entry['id'])
    try:
        paths = {role: None if entry[role] is None else directory / _local_path(entry[role])
                 for role in (*ROLES, 'manifest')}
        validation = csv_validator.validate_bundle(
            paths['frames'], paths['events'], paths['summary'], paths['manifest'])
        attempt['validation'] = validation
        valid = (validation['format_integrity'] == validation['consistency'] == 'PASS' and
                 validation['provenance']['status'] != 'INVALID')
        if source['binding_status'] == 'INVALID':
            if not valid:
                _note(attempt, 'BUNDLE_INVALID', 'CSV or supplied manifest validation also failed.')
            raise AnalysisError('SOURCE_INVALID', 'Historical source/config binding is invalid; no trace decoded.')
        _require(valid, 'BUNDLE_INVALID', 'CSV format, owner consistency or supplied manifest validation failed.')
        _manifest_binding(attempt, source)
        events = _snapshot(paths['events'], validation['files']['events'])
        summary_raw = _snapshot(paths['summary'], validation['files']['summary'])
        summary = next(_rows(summary_raw, csv_validator.SUMMARY_FIELDS))
        markers, trace = _scan_events(events, summary, mode)
        _decode_trace(attempt, markers, trace, source)
        _owner_qualification(attempt, summary, markers, trace)
    except INPUT_ERRORS as error:
        detail = _error(error)
        _invalidate(attempt, detail['code'], detail['message'], trace_invalid=True)
    return attempt


def _duplicate_bundles(attempts):
    groups = {}
    for attempt in attempts:
        validation = attempt['validation']
        if validation is None or any(validation['files'][role] is None for role in ROLES):
            continue
        identity = tuple(validation['files'][role]['sha256'] for role in ROLES)
        groups.setdefault(identity, []).append(attempt)
    for group in groups.values():
        if len(group) > 1:
            for attempt in group:
                _invalidate(attempt, 'DUPLICATE_BUNDLE', 'This exact three-file bundle is reused in the cohort.')


def _summarize(report):
    attempts = report['attempts']
    qualified = [a for a in attempts if a['qualification'] == 'QUALIFIED']
    report['qualified_attempts'] = len(qualified)
    report['passing_attempts'] = sum(a['logical_status'] == a['timing_status'] == 'PASS' for a in qualified)
    report['logical_failures'] = sum(a['logical_status'] == 'FAIL' and a['qualification'] != 'INVALID'
                                     for a in attempts)
    elapsed = [a['elapsed_us'] for a in qualified if a['trace_status'] == 'COMPLETE']
    if elapsed:
        report['minimum_elapsed_us'], report['maximum_elapsed_us'] = min(elapsed), max(elapsed)
    invalid = report['source']['binding_status'] == 'INVALID' or any(
        a['qualification'] == 'INVALID' for a in attempts)
    report['evidence_status'] = 'INVALID' if invalid else (
        'COMPLETE' if len(qualified) == REQUIRED_ATTEMPTS else 'INCOMPLETE')
    if report['evidence_status'] == 'COMPLETE':
        report['timing_status'] = 'PASS' if report['passing_attempts'] == REQUIRED_ATTEMPTS else 'FAIL'
    if report['timing_status'] == 'PASS' and all(
            a['validation']['provenance']['declared']['origin'] == 'hardware_reported' for a in qualified):
        report['declared_physical_trials_status'] = 'ELIGIBLE'
    for attempt in attempts:
        report['errors'].extend({'code': e['code'], 'message': '{}: {}'.format(attempt['id'], e['message'])}
                                for e in attempt['errors'])


def analyze_cohort(path):
    """Return D136 logical timing, declared source binding and separate qualification."""
    report = _new_report()
    try:
        cohort = _load_cohort(path)
        directory = Path(os.path.abspath(_local_path(path))).parent
    except INPUT_ERRORS as error:
        report['errors'].append(_error(error))
        return report
    report['input_status'], report['mode'] = 'VALID', cohort['mode']
    report['source'] = _bind_source(cohort['source'], cohort['mode'], directory, report['errors'])
    report['attempts'] = [_analyze_attempt(entry, directory, cohort['mode'], report['source'])
                          for entry in cohort['attempts']]
    _duplicate_bundles(report['attempts'])
    _summarize(report)
    return report


def main(argv=None):
    """Print one JSON report; only a complete passing logical cohort exits zero."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cohort', help='Local D136 cohort JSON')
    args = parser.parse_args(argv)
    report = analyze_cohort(args.cohort)
    print(json.dumps(report, sort_keys=True))
    return 0 if report['timing_status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
