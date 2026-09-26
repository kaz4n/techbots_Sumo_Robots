# Decodes fixed saved SETTLE evidence with file-observed little-endian layouts.
# Preserves raw receipts and separates structural errors from numeric annotations.
# Independent synthetic fixtures check all selected fields, prefixes and closure.
import base64
import binascii
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys


MAP_RELATIVE = 'state/analysis/P7_motor_settle_compile_raw/abi_static01_decode_fields.json'
MAP_BYTES = 16346
MAP_SHA256 = '0faba2433fd812508a6b9ac974d75a18e65cf360a123eb009306e3b75ae49bbd'
MAP_LIMIT = 65536
PACKET_LIMIT = 1048576
RAW_RELATIVE = 'state/analysis/P7_motor_settle_run_raw'
RUN_ID = 'app-motor-settle-117cc0e7-run01'
SOURCE = '117cc0e777341c893f4e618a97e3f196fd0bbf2427cb2a4b02543eb37d6522da'
PARENT = '/home/arduino/sumox26_codex_build'
UPLOAD = PARENT + '/' + RUN_ID + '-upload'
CAPTURE = PARENT + '/' + RUN_ID + '-capture'
UPLOAD_FILE = UPLOAD + '/upload_result.json'
CAPTURE_FILE = CAPTURE + '/capture_result.json'
IDENTITY = dict(user='arduino', uid=1000, gid=1000, home='/home/arduino',
                sysname='Linux', release='6.16.7-g0dd6551ae96b', machine='aarch64',
                boot_id='55c386b9-fe6d-4388-a7f4-1d91e0bb49d8', python=[3, 13, 5])
WINDOWS = (
    ('trace', 536951180, 2128, 'motor_fault::TraceReport'),
    ('report', 537119696, 1168, 'app_motor_observe::Report'),
    ('runtime', 537117984, 600, 'app::RuntimeReport'),
    ('transaction', 537115448, 504, 'app::TransactionReport'),
    ('settle', 537121768, 28, 'motors::SettleProbeReport'),
    ('gate', 536953520, 88, 'motors::MotorGate'),
)
SCALARS = {'u8': ('B', 1), 'u16': ('H', 2), 'u32': ('I', 4),
           'u64': ('Q', 8), 'f32': ('f', 4), 'bool': ('B', 1)}
ALIASES = {
    'Call': 'motor_fault::Call', 'CountdownResult': 'countdown::Result',
    'HaltResult': 'motors::HaltResult', 'LifecycleResult': 'countdown::LifecycleResult',
    'Outputs': 'core::Outputs', 'PreviousTick': 'fsm::PreviousTick',
    'Result': 'motors::Result', 'RobotResult': 'fsm::RobotResult',
    'RuntimeReport': 'app::RuntimeReport', 'SettleProbeSample': 'motors::SettleProbeSample',
    'Snapshot': 'app_motor_observe::Snapshot', 'TransactionReport': 'app::TransactionReport',
}
REASONS = ('NONE', 'SUCCESS', 'NULL_CONTEXT', 'PRECONDITION', 'INITIAL_BANK',
           'POLL_DEADLINE', 'POLL_BANK', 'FINAL_DEADLINE', 'POLL_LIMIT')
PACKET_KEYS = ('status', 'identity_before', 'identity_after', 'files', 'closing_file_checks')
UPLOAD_KEYS = ('attempts', 'finished_monotonic', 'finished_utc', 'first_error',
               'postcheck_errors', 'run_id', 'schema', 'source_sha256',
               'started_monotonic', 'started_utc', 'status', 'stderr', 'stdout', 'subprocess')
CAPTURE_KEYS = ('analysis', 'counts', 'finished_monotonic', 'finished_utc',
                'first_error', 'postcheck_errors', 'reads', 'run_id', 'schema',
                'source_sha256', 'started_monotonic', 'started_utc', 'status', 'wait')
ANALYSIS_KEYS = ('coherence', 'flash', 'pre_sample_wait', 'schema', 'snapshots')
FLASH_KEYS = ('before_loader', 'before_sketch', 'after_loader', 'after_sketch')
COUNT_KEYS = ('commands', 'reads', 'requested_bytes')
READ_KEYS = ('name', 'address', 'bytes', 'sha256', 'file')
SAMPLE_KEYS = ('elapsed_us', 'poll_index', 'reason', 'fresh_mask', 'valid', 'reserved')


def _plan():
    def flash(prefix, region):
        base, size = (0x08000000, 263680) if region == 'loader' else (0x08100000, 95520)
        return tuple((prefix + '.' + region + '.' + str(i), base + offset,
                      min(65536, size - offset))
                     for i, offset in enumerate(range(0, size, 65536)))
    samples = tuple((prefix + '.' + name, address, size)
                    for prefix in ('first', 'second') for name, address, size, _ in WINDOWS)
    return (flash('before', 'loader') + flash('before', 'sketch') + samples +
            flash('after', 'sketch') + flash('after', 'loader'))


PLAN = _plan()
SNAPSHOT_FILES = tuple(CAPTURE + '/' + f'{i:02d}-{PLAN[i][0]}.bin' for i in range(7, 19))


def _error(stage, code, path, kind=ValueError):
    raise kind(stage, code, path)


def _need(condition, stage, code, path):
    if not condition:
        _error(stage, code, path)


def _arg(value, kind, stage, path):
    if type(value) is not kind:
        _error(stage, 'ARG_TYPE', path, TypeError)


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _child(path, name):
    return path.rstrip('/') + '/' + str(name)


def _keys(value, names, stage, code, path):
    _need(type(value) is dict and set(value) == set(names), stage, code, path)


def _finite(value):
    return type(value) in (int, float) and (type(value) is int or math.isfinite(value))


def _hash(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def _typed_equal(left, right):
    if type(left) is not type(right):
        return False
    if type(right) is dict:
        return set(left) == set(right) and all(_typed_equal(left[k], v) for k, v in right.items())
    if type(right) is list:
        return len(left) == len(right) and all(_typed_equal(a, b) for a, b in zip(left, right))
    return left == right


def _pairs(rows):
    result = {}
    for key, value in rows:
        if key in result:
            raise ValueError()
        result[key] = value
    return result


def _json_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError()
    return value


def _json_constant(unused):
    raise ValueError()


def _json(raw, stage, path):
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                          parse_float=_json_float, parse_constant=_json_constant)
    except (UnicodeError, ValueError, OverflowError, RecursionError):
        _error(stage, 'JSON', path)


def _layout(raw):
    _need(0 < len(raw) == MAP_BYTES <= MAP_LIMIT, 'layout', 'MAP_SIZE', '/')
    _need(_digest(raw) == MAP_SHA256, 'layout', 'MAP_HASH', '/')
    value = _json(raw, 'layout', '/')
    _need(type(value) is dict and type(value.get('types')) is dict,
          'layout', 'SHAPE', '/')
    _need(value.get('schema') == 'motor-settle-observed-decode-fields-v1' and
          value.get('selected_types') == 16 and value.get('selected_fields') == 115 and
          len(value['types']) == 16, 'layout', 'SHAPE', '/')
    return value


def _scalar(kind, body, offset, path):
    fmt, width = SCALARS[kind]
    _need(0 <= offset <= len(body) - width, 'window', 'FIELD_MAP', path)
    value = struct.unpack_from('<' + fmt, body, offset)[0]
    if kind == 'bool':
        _need(value in (0, 1), 'window', 'INVALID_BOOL', path)
        return bool(value)
    if kind == 'f32':
        _need(math.isfinite(value), 'window', 'NONFINITE_F32', path)
    return value


def _width(kind, fields, path):
    if kind in SCALARS:
        return SCALARS[kind][1]
    if kind in ('u8[2]', 'Call[64]'):
        return 2 if kind == 'u8[2]' else 2048
    name = ALIASES.get(kind, kind)
    _need(name in fields and type(fields[name].get('bytes')) is int,
          'window', 'FIELD_MAP', path)
    return fields[name]['bytes']


def _decode_value(kind, body, offset, fields, path, depth=0):
    _need(depth <= 16, 'window', 'FIELD_MAP', path)
    if kind in SCALARS:
        return _scalar(kind, body, offset, path)
    if kind == 'u8[2]':
        return [_scalar('u8', body, offset + i, _child(path, i)) for i in range(2)]
    if kind == 'Call[64]':
        return [_decode_value('motor_fault::Call', body, offset + i * 32, fields,
                              _child(path, i), depth + 1) for i in range(64)]
    name = ALIASES.get(kind, kind)
    _need(name in fields, 'window', 'FIELD_MAP', path)
    spec = fields[name]
    _need(type(spec) is dict and type(spec.get('bytes')) is int and
          type(spec.get('fields')) is dict and 0 <= offset <= len(body) - spec['bytes'],
          'window', 'FIELD_MAP', path)
    result = {}
    for member, item in sorted(spec['fields'].items(), key=lambda row: (row[1]['offset'], row[0])):
        target = _child(path, member)
        _need(type(item) is dict and type(item.get('offset')) is int and
              type(item.get('kind')) is str and 0 <= item['offset'] < spec['bytes'],
              'window', 'FIELD_MAP', target)
        _need(item['offset'] + _width(item['kind'], fields, target) <= spec['bytes'],
              'window', 'FIELD_MAP', target)
        result[member] = _decode_value(item['kind'], body, offset + item['offset'],
                                       fields, target, depth + 1)
    return result


def _decode(kind, body, layout, path='/'):
    _need(kind in layout['types'], 'window', 'UNKNOWN_TYPE', '/kind')
    _need(len(body) == layout['types'][kind]['bytes'], 'window', 'BODY_SIZE', path)
    return _decode_value(kind, body, 0, layout['types'], path)


def decode(kind, body, *, field_map_raw):
    _arg(kind, str, 'window', '/kind')
    _arg(body, bytes, 'window', '/body')
    _arg(field_map_raw, bytes, 'layout', '/')
    return _decode(kind, body, _layout(field_map_raw))


def _annotation_int(value, maximum, path):
    _arg(value, int, 'annotation', path)
    _need(0 <= value <= maximum, 'annotation', 'SHAPE', path)


def _annotation_shape(report):
    _arg(report, dict, 'annotation', '/')
    _keys(report, ('current', 'first_failure', 'has_current', 'has_failure', 'reserved'),
          'annotation', 'SHAPE', '/')
    for name in ('current', 'first_failure'):
        value = report[name]
        _arg(value, dict, 'annotation', '/' + name)
        _keys(value, SAMPLE_KEYS, 'annotation', 'SHAPE', '/' + name)
        for member in SAMPLE_KEYS:
            maximum = 0xffffffff if member in ('elapsed_us', 'poll_index') else 255
            _annotation_int(value[member], maximum, '/' + name + '/' + member)
    for name in ('has_current', 'has_failure'):
        _annotation_int(report[name], 255, '/' + name)
    _arg(report['reserved'], list, 'annotation', '/reserved')
    _need(len(report['reserved']) == 2, 'annotation', 'SHAPE', '/reserved')
    for i, value in enumerate(report['reserved']):
        _annotation_int(value, 255, '/reserved/' + str(i))


def _issue(issues, condition, code, path):
    if condition:
        issues.append(dict(code=code, path=path))


def _branch_issues(sample, path, issues):
    reason, valid = sample['reason'], sample['valid']
    elapsed, poll, fresh = sample['elapsed_us'], sample['poll_index'], sample['fresh_mask']
    if reason in (2, 3, 4):
        for name in ('elapsed_us', 'poll_index', 'fresh_mask'):
            _issue(issues, sample[name] != 0, 'EARLY_NONZERO', _child(path, name))
    if reason not in (1, 5, 6, 7, 8):
        return
    if valid & 1:
        okay = elapsed >= 150 if reason in (5, 7) else elapsed < 150
        _issue(issues, not okay, 'ELAPSED_CONDITION', _child(path, 'elapsed_us'))
    if valid & 2:
        okay = poll == 4095 if reason == 8 else poll <= 4095
        _issue(issues, not okay, 'POLL_CONDITION', _child(path, 'poll_index'))
    if valid & 4:
        okay = fresh == 7 if reason in (1, 7) else fresh < 7 if reason in (5, 8) else fresh <= 7
        if reason == 5 and valid & 2 and poll == 0:
            okay = okay and fresh == 0
        _issue(issues, not okay, 'FRESH_CONDITION', _child(path, 'fresh_mask'))


def _sample_annotation(sample, flag, path, first_failure):
    presence = 'ABSENT' if flag == 0 else 'PRESENT' if flag == 1 else 'UNKNOWN'
    available = {name: False if flag == 0 else bool(sample['valid'] & bit) if flag == 1 else None
                 for name, bit in (('elapsed_us', 1), ('poll_index', 2), ('fresh_mask', 4))}
    reason = sample['reason']
    label = REASONS[reason] if reason < len(REASONS) else None
    result = dict(presence=presence, reason_label=label, available=available,
                  status='UNAVAILABLE' if flag == 0 else 'INCONCLUSIVE')
    issues = []
    if flag != 1:
        return result, issues
    _issue(issues, sample['reserved'] != 0, 'NONZERO_RESERVED', _child(path, 'reserved'))
    _issue(issues, bool(sample['valid'] & ~7), 'UNKNOWN_VALID_BITS', _child(path, 'valid'))
    _issue(issues, bool(sample['fresh_mask'] & ~7), 'UNKNOWN_FRESH_BITS', _child(path, 'fresh_mask'))
    _issue(issues, label is None, 'UNKNOWN_REASON', _child(path, 'reason'))
    _issue(issues, reason == 0, 'PRESENT_NONE', _child(path, 'reason'))
    if 1 <= reason <= 8:
        expected = 0 if reason in (2, 3, 4) else 7
        _issue(issues, sample['valid'] != expected, 'VALID_MASK_MISMATCH', _child(path, 'valid'))
    _branch_issues(sample, path, issues)
    _issue(issues, first_failure and reason in (0, 1),
           'FIRST_FAILURE_NOT_FAILURE', _child(path, 'reason'))
    result['status'] = 'INCONCLUSIVE' if issues else 'CONSISTENT'
    return result, issues


def annotate_settle(report):
    _annotation_shape(report)
    issues = []
    for name in ('has_current', 'has_failure'):
        _issue(issues, report[name] not in (0, 1), 'NON_BINARY_PRESENCE', '/' + name)
    for index, value in enumerate(report['reserved']):
        _issue(issues, value != 0, 'NONZERO_RESERVED', '/reserved/' + str(index))
    current, current_issues = _sample_annotation(report['current'], report['has_current'],
                                                '/current', False)
    first, first_issues = _sample_annotation(report['first_failure'], report['has_failure'],
                                            '/first_failure', True)
    issues.extend(current_issues)
    issues.extend(first_issues)
    _issue(issues, report['has_failure'] == 1 and report['has_current'] == 0,
           'FLAG_RELATION', '/has_current')
    _issue(issues, report['has_current'] == 1 and 2 <= report['current']['reason'] <= 8 and
           report['has_failure'] == 0, 'FLAG_RELATION', '/has_failure')
    unknown = 'UNKNOWN' in (current['presence'], first['presence'])
    status = 'INCONCLUSIVE' if issues or unknown else (
        'UNAVAILABLE' if report['has_current'] == report['has_failure'] == 0 else 'CONSISTENT')
    return dict(raw=copy.deepcopy(report), current=current, first_failure=first,
                issues=issues, status=status)


def _file_rows(packet):
    _keys(packet, PACKET_KEYS, 'packet', 'KEYS', '/')
    _need(packet['status'] == 'FILE_ONLY_RESULTS_VERIFIED', 'packet', 'STATUS', '/status')
    for name in ('identity_before', 'identity_after'):
        _need(_typed_equal(packet[name], IDENTITY), 'packet', 'IDENTITY', '/' + name)
    rows = packet['files']
    _need(type(rows) is list and 2 <= len(rows) <= 14, 'packet', 'FILE_COUNT', '/files')
    _need(type(packet['closing_file_checks']) is int and
          packet['closing_file_checks'] == len(rows), 'packet', 'CLOSURE_COUNT',
          '/closing_file_checks')
    allowed = (UPLOAD_FILE, CAPTURE_FILE, *SNAPSHOT_FILES)
    files = {}
    for index, row in enumerate(rows):
        path = '/files/' + str(index)
        _keys(row, ('path', 'bytes', 'sha256', 'data_base64'), 'files', 'ROW_KEYS', path)
        checks = (('path', type(row['path']) is str),
                  ('bytes', type(row['bytes']) is int and 0 < row['bytes'] <= PACKET_LIMIT),
                  ('sha256', _hash(row['sha256'])),
                  ('data_base64', type(row['data_base64']) is str))
        for name, okay in checks:
            _need(okay, 'files', 'ROW_TYPE', _child(path, name))
        _need(row['path'] in allowed, 'files', 'PATH', _child(path, 'path'))
        _need(row['path'] not in files, 'files', 'DUPLICATE_FILE', _child(path, 'path'))
        files[row['path']] = (index, row)
    for path in (UPLOAD_FILE, CAPTURE_FILE):
        _need(path in files, 'files', 'MISSING_FILE', path)
    return files


def _verified_file(item, result):
    index, row = item
    path = '/files/' + str(index)
    try:
        body = base64.b64decode(row['data_base64'], validate=True)
        canonical = base64.b64encode(body).decode('ascii')
    except (ValueError, binascii.Error):
        _error('files', 'BASE64', _child(path, 'data_base64'))
    _need(canonical == row['data_base64'], 'files', 'BASE64', _child(path, 'data_base64'))
    _need(len(body) == row['bytes'], 'files', 'FILE_SIZE', _child(path, 'bytes'))
    _need(_digest(body) == row['sha256'], 'files', 'FILE_HASH', _child(path, 'sha256'))
    result['verified_files'].append({name: row[name] for name in ('path', 'bytes', 'sha256')})
    return body


def _object_keys(value, names, stage, path):
    _need(type(value) is dict, stage, 'TYPE', path)
    _keys(value, names, stage, 'KEYS', path)


def _receipt_keys(upload, capture):
    _object_keys(upload, UPLOAD_KEYS, 'upload', '/upload_result')
    _object_keys(capture, CAPTURE_KEYS, 'capture', '/capture_result')
    _object_keys(upload['subprocess'], ('reaped', 'returncode', 'timed_out'),
                 'upload', '/upload_result/subprocess')
    _object_keys(capture['analysis'], ANALYSIS_KEYS, 'capture', '/capture_result/analysis')
    _object_keys(capture['analysis']['flash'], FLASH_KEYS, 'capture', '/capture_result/analysis/flash')
    _object_keys(capture['counts'], COUNT_KEYS, 'capture', '/capture_result/counts')


def _value_type(value, kind, stage, path):
    _need(type(value) is kind, stage, 'TYPE', path)


def _analysis_types(value):
    path = '/capture_result/analysis'
    for name in ANALYSIS_KEYS:
        if name in ('coherence', 'schema'):
            _value_type(value[name], str, 'capture', _child(path, name))
        elif name == 'flash':
            for field in FLASH_KEYS:
                _value_type(value[name][field], bool, 'capture', _child(_child(path, name), field))
        elif name == 'snapshots':
            _value_type(value[name], list, 'capture', _child(path, name))


def _read_types(rows):
    for index, row in enumerate(rows):
        path = '/capture_result/reads/' + str(index)
        _keys(row, READ_KEYS, 'capture', 'READ_PLAN', path)
        for field, kind in (('name', str), ('address', int), ('bytes', int),
                             ('sha256', str), ('file', str)):
            _value_type(row[field], kind, 'capture', _child(path, field))


def _receipt_types(upload, capture):
    strings = ('run_id', 'schema', 'source_sha256', 'status', 'stderr', 'stdout')
    for stage, receipt, names in (('upload', upload, UPLOAD_KEYS),
                                  ('capture', capture, CAPTURE_KEYS)):
        path = '/' + stage + '_result'
        for name in names:
            value = receipt[name]
            target = _child(path, name)
            if name == 'attempts':
                _value_type(value, int, stage, target)
            elif name in strings:
                _value_type(value, str, stage, target)
            elif name == 'first_error':
                _need(value is None or type(value) is dict, stage, 'TYPE', target)
            elif name in ('postcheck_errors', 'reads'):
                _value_type(value, list, stage, target)
                if name == 'reads':
                    _read_types(value)
            elif name == 'subprocess':
                for field, kind in (('reaped', bool), ('returncode', int), ('timed_out', bool)):
                    _value_type(value[field], kind, stage, _child(target, field))
            elif name == 'analysis':
                _analysis_types(value)


def _identities(upload, capture):
    for stage, receipt in (('upload', upload), ('capture', capture)):
        path = '/' + stage + '_result'
        for name, expected in (('schema', 'app-motor-settle-' + stage + '-result-v1'),
                               ('run_id', RUN_ID), ('source_sha256', SOURCE)):
            _need(receipt[name] == expected, stage, 'IDENTITY', _child(path, name))
    for name, expected in (('schema', 'app-motor-settle-capture-analysis-v1'),
                           ('coherence', 'UNPROVEN')):
        _need(capture['analysis'][name] == expected, 'capture', 'IDENTITY',
              '/capture_result/analysis/' + name)


def _error_object(value, names, stage, path):
    _keys(value, names, stage, 'ERROR_SHAPE', path)
    for name in names:
        item = value[name]
        _need(type(item) is str and (name == 'message' or bool(item)),
              stage, 'ERROR_SHAPE', _child(path, name))


def _error_shapes(receipt, stage):
    path = '/' + stage + '_result'
    if receipt['first_error'] is not None:
        _error_object(receipt['first_error'], ('type', 'message'), stage, path + '/first_error')
    for index, value in enumerate(receipt['postcheck_errors']):
        _error_object(value, ('check', 'type', 'message'), stage,
                      path + '/postcheck_errors/' + str(index))


def _clocks(receipt, stage):
    path = '/' + stage + '_result'
    for name in ('finished_monotonic', 'finished_utc', 'started_monotonic', 'started_utc'):
        value = receipt[name]
        okay = type(value) is str and bool(value) if name.endswith('_utc') else _finite(value)
        _need(okay, stage, 'CLOCK', _child(path, name))
    _need(receipt['finished_monotonic'] >= receipt['started_monotonic'],
          stage, 'CLOCK', path + '/finished_monotonic')


def _span(after, before):
    try:
        return after - before
    except OverflowError:
        # Only compared after finite, ordered endpoints; never serialized.
        return math.inf


def _upload_admission(upload):
    _need(upload['attempts'] == 1, 'upload', 'STATUS', '/upload_result/attempts')
    _need(upload['status'] == 'UPLOADED', 'upload', 'STATUS', '/upload_result/status')
    for name, expected in (('reaped', True), ('returncode', 0), ('timed_out', False)):
        _need(upload['subprocess'][name] == expected, 'upload', 'STATUS',
              '/upload_result/subprocess/' + name)
    _error_shapes(upload, 'upload')
    _need(upload['first_error'] is None, 'upload', 'STATUS', '/upload_result/first_error')
    _need(not upload['postcheck_errors'], 'upload', 'STATUS', '/upload_result/postcheck_errors')
    _clocks(upload, 'upload')


def _counts(capture):
    values = capture['counts']
    path = '/capture_result/counts/'
    for name in COUNT_KEYS:
        _need(type(values[name]) is int, 'capture', 'COUNTS', path + name)
    commands, reads, requested = (values[name] for name in COUNT_KEYS)
    _need(0 <= commands <= 26, 'capture', 'COUNTS', path + 'commands')
    _need(0 <= reads <= commands and commands in (reads, reads + 1),
          'capture', 'COUNTS', path + 'reads')
    _need(requested == sum(item[2] for item in PLAN[:commands]),
          'capture', 'COUNTS', path + 'requested_bytes')
    return commands, reads


def _read_rows(capture, count):
    rows = capture['reads']
    _need(len(rows) == count, 'capture', 'READ_PLAN', '/capture_result/reads')
    for index, row in enumerate(rows):
        path = '/capture_result/reads/' + str(index)
        name, address, size = PLAN[index]
        for field, expected in (('name', name), ('address', address), ('bytes', size)):
            _need(row[field] == expected, 'capture', 'READ_PLAN', _child(path, field))
        _need(_hash(row['sha256']), 'capture', 'READ_PLAN', _child(path, 'sha256'))
        _need(row['file'] == f'{index:02d}-{name}.bin',
              'capture', 'READ_PLAN', _child(path, 'file'))
    snapshots = rows[7:min(count, 19)]
    _need(_typed_equal(capture['analysis']['snapshots'], snapshots),
          'capture', 'SNAPSHOTS', '/capture_result/analysis/snapshots')
    return snapshots


def _file_set(files, snapshots):
    expected = [UPLOAD_FILE, CAPTURE_FILE] + [CAPTURE + '/' + row['file'] for row in snapshots]
    for path in expected:
        _need(path in files, 'files', 'MISSING_FILE', path)
    for path in files:
        _need(path in expected, 'files', 'FILE_SET', path)


def _wait_record(value, seconds, path, capture):
    if value is None:
        return
    _keys(value, ('requested_seconds', 'before', 'after'), 'capture', 'WAIT', path)
    _need(type(value['requested_seconds']) is int and value['requested_seconds'] == seconds,
          'capture', 'WAIT', path + '/requested_seconds')
    start, finish = capture['started_monotonic'], capture['finished_monotonic']
    _need(_finite(value['before']) and start <= value['before'] <= finish,
          'capture', 'WAIT', path + '/before')
    after = value['after']
    _need(after is None or (_finite(after) and value['before'] <= after <= finish),
          'capture', 'WAIT', path + '/after')


def _waits(capture, commands, reads):
    pre, wait = capture['analysis']['pre_sample_wait'], capture['wait']
    for value, boundary, seconds, path in (
            (pre, 7, 30, '/capture_result/analysis/pre_sample_wait'),
            (wait, 13, 2, '/capture_result/wait')):
        _wait_record(value, seconds, path, capture)
        if reads < boundary:
            _need(value is None, 'capture', 'WAIT', path)
        if commands > boundary:
            _need(value is not None, 'capture', 'WAIT', path)
            _need(value['after'] is not None, 'capture', 'WAIT', path + '/after')
            _need(_span(value['after'], value['before']) >= seconds,
                  'capture', 'WAIT', path + '/after')
    if pre is not None and wait is not None and pre['after'] is not None:
        _need(pre['after'] <= wait['before'], 'capture', 'WAIT', '/capture_result/wait/before')


def _flash(capture, commands, reads):
    flags = capture['analysis']['flash']
    for name, boundary in zip(FLASH_KEYS, (4, 6, 25, 20)):
        path = '/capture_result/analysis/flash/' + name
        _need(not flags[name] or reads > boundary, 'capture', 'FLASH', path)
        _need(commands <= boundary + 1 or flags[name], 'capture', 'FLASH', path)


def _capture_status(capture, commands, reads):
    status = capture['status']
    _need(status in ('COLLECTED', 'FAILED'), 'capture', 'STATUS', '/capture_result/status')
    if status == 'FAILED':
        _need(capture['first_error'] is not None, 'capture', 'STATUS', '/capture_result/first_error')
        return 'PARTIAL'
    _need(commands == reads == 26, 'capture', 'STATUS', '/capture_result/status')
    _need(all(capture['analysis']['flash'].values()), 'capture', 'STATUS',
          '/capture_result/analysis/flash')
    _need(capture['first_error'] is None, 'capture', 'STATUS', '/capture_result/first_error')
    _need(not capture['postcheck_errors'], 'capture', 'STATUS', '/capture_result/postcheck_errors')
    _need(_span(capture['finished_monotonic'], capture['started_monotonic']) < 600,
          'capture', 'STATUS', '/capture_result/finished_monotonic')
    rows = capture['reads']
    hashes = {row['name']: row['sha256'] for row in rows}
    for index, row in enumerate(rows):
        if row['name'].startswith('after.'):
            before = 'before.' + row['name'][len('after.'):]
            _need(row['sha256'] == hashes[before], 'capture', 'STATUS', '/capture_result')
    return 'DECODED'


def _admission(upload, capture, files):
    _receipt_keys(upload, capture)
    _receipt_types(upload, capture)
    _identities(upload, capture)
    _upload_admission(upload)
    _error_shapes(capture, 'capture')
    _clocks(capture, 'capture')
    commands, reads = _counts(capture)
    snapshots = _read_rows(capture, reads)
    _file_set(files, snapshots)
    _waits(capture, commands, reads)
    _flash(capture, commands, reads)
    status = _capture_status(capture, commands, reads)
    return snapshots, status


def _windows(snapshots, files, layout, result):
    for record in snapshots:
        name = record['name']
        item = files[CAPTURE + '/' + record['file']]
        body = _verified_file(item, result)
        index, row = item
        path = '/files/' + str(index)
        _need(row['bytes'] == record['bytes'], 'files', 'FILE_SIZE', path + '/bytes')
        _need(row['sha256'] == record['sha256'], 'files', 'FILE_HASH', path + '/sha256')
        base_name = name.split('.', 1)[1]
        kind = next(kind for key, _, _, kind in WINDOWS if key == base_name)
        value = _decode(kind, body, layout, '/windows/' + name)
        result['windows'][name] = value
        if base_name == 'settle':
            result['settle_annotations'][name] = annotate_settle(value)


def _result(packet_raw, field_map_raw):
    return dict(schema='motor-settle-observed-fields-v1', status='REJECTED',
                retrieval_sha256=_digest(packet_raw), field_map_sha256=_digest(field_map_raw),
                coherence='UNPROVEN', upload_result=None, capture_result=None,
                decode_first_error=None, verified_files=[], windows={}, settle_annotations={},
                repeated_fields_equal={name: None for name, _, _, _ in WINDOWS})


def _interpret(packet_raw, field_map_raw, result):
    layout = _layout(field_map_raw)
    _need(0 < len(packet_raw) <= PACKET_LIMIT, 'packet', 'PACKET_SIZE', '/')
    packet = _json(packet_raw, 'packet', '/')
    files = _file_rows(packet)
    upload_raw = _verified_file(files[UPLOAD_FILE], result)
    upload = _json(upload_raw, 'upload', '/upload_result')
    result['upload_result'] = upload
    capture_raw = _verified_file(files[CAPTURE_FILE], result)
    capture = _json(capture_raw, 'capture', '/capture_result')
    result['capture_result'] = capture
    snapshots, status = _admission(upload, capture, files)
    _windows(snapshots, files, layout, result)
    result['status'] = status


def interpret(packet_raw, *, field_map_raw):
    _arg(packet_raw, bytes, 'packet', '/')
    _arg(field_map_raw, bytes, 'layout', '/')
    result = _result(packet_raw, field_map_raw)
    try:
        _interpret(packet_raw, field_map_raw, result)
    except ValueError as error:
        if len(error.args) != 3 or any(type(item) is not str for item in error.args):
            raise
        result['decode_first_error'] = dict(zip(('stage', 'code', 'path'), error.args))
    for name, _, _, _ in WINDOWS:
        first, second = 'first.' + name, 'second.' + name
        if first in result['windows'] and second in result['windows']:
            result['repeated_fields_equal'][name] = result['windows'][first] == result['windows'][second]
    return result


def _bounded_read(path, limit):
    with path.open('rb') as stream:
        return stream.read(limit + 1)


def main(argv):
    _need(type(argv) is list and len(argv) == 2 and all(type(item) is str for item in argv)
          and argv[0] == '--packet-sha256' and _hash(argv[1]), 'main', 'CLI', '/')
    _need(sys.dont_write_bytecode, 'main', 'BYTECODE', '/')
    root = Path(__file__).absolute().parents[3]
    raw = root / RAW_RELATIVE / 'retrieved_inert_run01'
    packet = _bounded_read(raw / '0001-read-saved-results/stdout', PACKET_LIMIT)
    _need(0 < len(packet) <= PACKET_LIMIT, 'packet', 'PACKET_SIZE', '/')
    _need(_digest(packet) == argv[1], 'packet', 'PACKET_HASH', '/')
    field_map = _bounded_read(root / MAP_RELATIVE, MAP_LIMIT)
    result = interpret(packet, field_map_raw=field_map)
    with (raw / 'decoded.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
    return {'DECODED': 0, 'PARTIAL': 1, 'REJECTED': 2}[result['status']]


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
