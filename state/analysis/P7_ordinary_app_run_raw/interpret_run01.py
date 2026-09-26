# Decodes saved ordinary application windows using the observed flat scalar map.
# Preserves raw receipts and separates structural errors from sampled findings.
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


MAP_RELATIVE = 'state/analysis/P7_ordinary_app_run_raw/ordinary_scalar_map01.json'
MAP_BYTES = 42416
MAP_SHA256 = 'd8f4eb7eb36430cff975e3032168fa61f2c249e55596401a67862b272bb08fb7'
MAP_LIMIT = 65536
PACKET_LIMIT = 1048576
RAW_RELATIVE = 'state/analysis/P7_ordinary_app_run_raw'
RUN_ID = 'ordinary-app-9044ebbb-run01'
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
PARENT = '/home/arduino/sumox26_codex_build'
UPLOAD = PARENT + '/' + RUN_ID + '-upload'
CAPTURE = PARENT + '/' + RUN_ID + '-capture'
UPLOAD_FILE = UPLOAD + '/upload_result.json'
CAPTURE_FILE = CAPTURE + '/capture_result.json'
IDENTITY = dict(user='arduino', uid=1000, gid=1000, home='/home/arduino',
                sysname='Linux', release='6.16.7-g0dd6551ae96b', machine='aarch64',
                boot_id='55c386b9-fe6d-4388-a7f4-1d91e0bb49d8', python=[3, 13, 5])
WINDOWS = (('report', 537115800, 600, 'report'), ('transaction', 537113264, 504, 'transaction'), ('previous', 537113768, 48, 'previous'), ('gate', 536951336, 88, 'gate'), ('grants', 537115776, 21, 'grants'), ('attempted_word', 537117352, 4, 'attempted_word'), ('motor_port', 537117512, 40, 'motor_port'))
SCALARS = {'u8': ('B', 1), 'u16': ('H', 2), 'u32': ('I', 4), 'u64': ('Q', 8), 'f32': ('f', 4), 'bool': ('B', 1), 'i8': ('b', 1)}
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


def _plan():
    def flash(prefix, region):
        base, size = (0x08000000, 263680) if region == 'loader' else (0x08100000, 92944)
        return tuple((prefix + '.' + region + '.' + str(i), base + offset,
                      min(65536, size - offset))
                     for i, offset in enumerate(range(0, size, 65536)))
    samples = tuple((prefix + '.' + name, address, size)
                    for prefix in ('first', 'second') for name, address, size, _ in WINDOWS)
    return (flash('before', 'loader') + flash('before', 'sketch') + samples +
            flash('after', 'sketch') + flash('after', 'loader'))


PLAN = _plan()
SNAPSHOT_FILES = tuple(CAPTURE + '/' + f'{i:02d}-{PLAN[i][0]}.bin' for i in range(7, 21))


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
    _need(type(value) is dict and value.get('schema') == 'ordinary-app-scalar-map-v1'
          and value.get('source_sha256') == SOURCE and value.get('byte_order') == 'little'
          and value.get('scalar_count') == 107, 'layout', 'SHAPE', '/')
    rows, enums, objects = value.get('windows'), value.get('enums'), value.get('objects')
    _need(type(rows) is list and len(rows) == 7 and type(enums) is dict and len(enums) == 7
          and type(objects) is dict and set(objects) == {'runtime', 'motor_port'},
          'layout', 'SHAPE', '/')
    _need(value.get('scalar_widths') == {k: v[1] for k, v in SCALARS.items()},
          'layout', 'SHAPE', '/scalar_widths')
    for name, table in enums.items():
        _need(type(name) is str and type(table) is dict and bool(table) and
              all(type(k) is str and type(v) is int and 0 <= v <= 255
                  for k, v in table.items()) and len(set(table.values())) == len(table),
              'layout', 'SHAPE', '/enums/' + name)
    names, ranges, count = set(), [], 0
    for row, (name, address, size, _) in zip(rows, WINDOWS):
        _need(type(row) is dict and row.get('name') == name and name not in names and
              type(row.get('address')) is int and row['address'] == address and
              type(row.get('bytes')) is int and row['bytes'] == size,
              'layout', 'SHAPE', '/windows')
        obj = objects.get(row.get('object'))
        _need(type(obj) is dict and type(obj.get('address')) is int and
              type(obj.get('bytes')) is int and type(row.get('object_offset')) is int and
              0 <= row['object_offset'] <= obj['bytes'] - size and
              address == obj['address'] + row['object_offset'],
              'layout', 'SHAPE', '/windows/' + name)
        _need(all(address + size <= a or address >= b for a, b in ranges),
              'layout', 'SHAPE', '/windows/' + name)
        names.add(name)
        ranges.append((address, address + size))
        fields = row.get('fields')
        _need(type(fields) is list and 0 < len(fields) <= 107, 'layout', 'SHAPE', name)
        selected, used = set(), set()
        for field in fields:
            _need(type(field) is dict and type(field.get('name')) is str and
                  field['name'] not in selected and type(field.get('offset')) is int,
                  'layout', 'SHAPE', name)
            width = _width(field.get('scalar'), name)
            offset = field['offset']
            _need(type(field.get('bytes')) is int and field['bytes'] == width and
                  0 <= offset <= size - width and not used.intersection(range(offset, offset + width))
                  and (field.get('enum') is None or field.get('enum') in enums),
                  'layout', 'SHAPE', name + '/' + field['name'])
            selected.add(field['name'])
            used.update(range(offset, offset + width))
            count += 1
    _need(count == 107, 'layout', 'SHAPE', '/scalar_count')
    return value


def _scalar(kind, body, offset, path):
    fmt, width = SCALARS[kind]
    _need(0 <= offset <= len(body) - width, 'window', 'FIELD_MAP', path)
    raw = body[offset:offset + width]
    value = struct.unpack('<' + fmt, raw)[0]
    issues = []
    if kind == 'bool':
        if value not in (0, 1):
            value, issues = None, ['INVALID_BOOL']
        else:
            value = bool(value)
    elif kind == 'f32' and not math.isfinite(value):
        value, issues = None, ['NONFINITE_F32']
    return dict(raw_hex=raw.hex(), raw_unsigned=int.from_bytes(raw, 'little'),
                value=value, enum_name=None, issues=issues)


def _width(kind, path):
    _need(type(kind) is str and kind in SCALARS, 'layout', 'FIELD_MAP', path)
    return SCALARS[kind][1]


def _decode_value(field, body, enums, path):
    result = _scalar(field['scalar'], body, field['offset'], path)
    if field['enum'] is not None:
        result['enum_name'] = next((name for name, number in enums[field['enum']].items()
                                    if number == result['value']), None)
        if result['enum_name'] is None:
            result['issues'].append('UNKNOWN_ENUM')
    return result


def _decode(kind, body, layout, path='/'):
    spec = next((row for row in layout['windows'] if row['name'] == kind), None)
    _need(spec is not None, 'window', 'UNKNOWN_TYPE', '/kind')
    _need(len(body) == spec['bytes'], 'window', 'BODY_SIZE', path)
    fields = {}
    for item in sorted(spec['fields'], key=lambda row: (row['offset'], row['name'])):
        fields[item['name']] = _decode_value(item, body, layout['enums'], _child(path, item['name']))
    return dict(raw_hex=body.hex(), fields=fields)


def decode(kind, body, *, field_map_raw):
    _arg(kind, str, 'window', '/kind')
    _arg(body, bytes, 'window', '/body')
    _arg(field_map_raw, bytes, 'layout', '/')
    return _decode(kind, body, _layout(field_map_raw))














def _file_rows(packet):
    _keys(packet, PACKET_KEYS, 'packet', 'KEYS', '/')
    _need(packet['status'] == 'FILE_ONLY_RESULTS_VERIFIED', 'packet', 'STATUS', '/status')
    for name in ('identity_before', 'identity_after'):
        _need(_typed_equal(packet[name], IDENTITY), 'packet', 'IDENTITY', '/' + name)
    rows = packet['files']
    _need(type(rows) is list and 2 <= len(rows) <= 16, 'packet', 'FILE_COUNT', '/files')
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
        for name, expected in (('schema', 'ordinary-app-' + stage + '-result-v1'),
                               ('run_id', RUN_ID), ('source_sha256', SOURCE)):
            _need(receipt[name] == expected, stage, 'IDENTITY', _child(path, name))
    for name, expected in (('schema', 'ordinary-app-capture-analysis-v1'),
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
    _need(0 <= commands <= 28, 'capture', 'COUNTS', path + 'commands')
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
    snapshots = rows[7:min(count, 21)]
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
            (wait, 14, 2, '/capture_result/wait')):
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
    for name, boundary in zip(FLASH_KEYS, (4, 6, 27, 22)):
        path = '/capture_result/analysis/flash/' + name
        _need(not flags[name] or reads > boundary, 'capture', 'FLASH', path)
        _need(commands <= boundary + 1 or flags[name], 'capture', 'FLASH', path)


def _capture_status(capture, commands, reads):
    status = capture['status']
    _need(status in ('COLLECTED', 'FAILED'), 'capture', 'STATUS', '/capture_result/status')
    if status == 'FAILED':
        _need(capture['first_error'] is not None, 'capture', 'STATUS', '/capture_result/first_error')
        return 'PARTIAL'
    _need(commands == reads == 28, 'capture', 'STATUS', '/capture_result/status')
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


def _ordinary_findings(sample, kind, decoded, layout):
    spec = next(row for row in layout['windows'] if row['name'] == kind)
    findings = []
    for field in sorted(spec['fields'], key=lambda row: (row['offset'], row['name'])):
        name = field['name']
        item = decoded['fields'][name]
        value, codes = item['value'], list(item['issues'])
        if not codes:
            if name == 'phase' and ((kind == 'report' and value == 3) or
                                    (kind == 'transaction' and value == 4)):
                codes.append('SAMPLED_FAULT_PHASE')
            if field['enum'] in ('app::RuntimeFault', 'app::Fault', 'motors::Fault',
                                  'edge::EscapeFault') and value != 0:
                codes.append('SAMPLED_FAULT_CODE')
            if kind == 'transaction' and name == 'robot.contract_faults' and value != 0:
                codes.append('SAMPLED_CONTRACT_BITS')
                if value & ~1023:
                    codes.append('UNKNOWN_CONTRACT_BITS')
            if kind == 'grants' and item['raw_unsigned'] != 0:
                codes.append('UNEXPECTED_GRANT_VALUE')
            if ((name.rsplit('.', 1)[-1] in ('duty_l', 'duty_r', 'motors_enabled') and value != 0)
                    or (kind == 'motor_port' and name.startswith('pulses_[') and value != 0)):
                codes.append('SAMPLED_NONZERO_MOTOR_COMMAND')
            if kind == 'attempted_word' and name == 'attempted_' and value is False:
                codes.append('SAMPLED_NOT_ATTEMPTED')
        findings.extend(dict(sample=sample, field=name, code=code,
                             raw_hex=item['raw_hex'], value=value) for code in codes)
    return findings


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
        value = _decode(base_name, body, layout, '/windows/' + name)
        result['windows'][name] = value
        result['application_findings'].extend(_ordinary_findings(name, base_name, value, layout))


def _result(packet_raw, field_map_raw):
    return dict(schema='ordinary-app-observed-fields-v1', status='REJECTED',
                retrieval_sha256=_digest(packet_raw), field_map_sha256=_digest(field_map_raw),
                coherence='UNPROVEN', upload_result=None, capture_result=None,
                decode_first_error=None, verified_files=[], windows={}, application_findings=[],
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
            left, right = (result['windows'][sample]['fields'] for sample in (first, second))
            result['repeated_fields_equal'][name] = all(left[key]['raw_hex'] == right[key]['raw_hex']
                                                       for key in left)
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
