# Interprets the already captured static diagnostic ABI without board access.
# Projects only readelf's one hexadecimal diagnostic size into decimal in memory.
# Reuses the unchanged reviewed parser; controlled format cases verify projection.
import base64
import hashlib
import json
from pathlib import Path
import re
import stat
import sys
import types

ROOT = Path(__file__).absolute().parents[3]
RAW = 'state/analysis/P7_app_motor_fault_compile_raw/'
READER = RAW + 'inspect_static_abi.py'
RESULT = RAW + 'native_abi_static01/result.json'
INPUTS = RAW + 'native_abi_static01/inputs.json'
CLOSURE = RAW + 'native_abi_static01/local_result.json'
ARTIFACTS = RAW + 'native_static01/artifacts.json'
PINS = {
    READER: '0eec2ffd91958831ab0541477a5277187bb7e9179fdca1096276dda01efb6f4c',
    RESULT: '684670c538bb032ab3b4b4ebc68ffd6cbecb743f0209aacc154af58b244101d2',
    INPUTS: '75427e4a3218411916d74f7697c2e670f1dd8954fd00add488ffebeb06344bb8',
    CLOSURE: 'db885da2b94098c06f3a10bafb7914727c6bb2861d7a914f6dc3a4029ccd1516',
    ARTIFACTS: '57b98c00db1ed5d90394812fcbb3fb28effedd4381f6e2fc03a6e7c04b45a6ce',
}
SYMBOL = '_ZN12_GLOBAL__N_110diagnosticE'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(name):
    path = ROOT / name
    for item in (path, *path.parents):
        info = item.lstat()
        kind = stat.S_ISREG if item == path else stat.S_ISDIR
        require(kind(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 1024,
                'Linked or nonplain input')
    before = path.stat()
    require(0 < before.st_size <= 1048576, 'Input exceeds bound')
    raw = path.read_bytes()
    after = path.stat()
    stamp = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    require(stamp(before) == stamp(after) and len(raw) == before.st_size and sha(raw) == PINS[name],
            'Pinned input differs: ' + name)
    return raw


def normalize(text):
    lines = text.splitlines(keepends=True)
    candidates = [index for index, line in enumerate(lines) if line.split() and line.split()[-1] == SYMBOL]
    require(len(candidates) == 1, 'Expected unique diagnostic symbol row')
    index = candidates[0]
    pattern = (r'(\s*\d+:\s+[0-9a-fA-F]+\s+)([0-9]+|0x[0-9a-fA-F]+)'
               r'(\s+OBJECT\s+LOCAL\s+DEFAULT\s+\d+\s+' + SYMBOL + r'\s*)')
    match = re.fullmatch(pattern, lines[index])
    require(match is not None, 'Malformed diagnostic symbol row or size')
    token = match.group(2)
    value = int(token, 16 if token.startswith('0x') else 10)
    require(0 < value <= 1048576, 'Diagnostic size exceeds ABI bound')
    projected = str(value) if token.startswith('0x') else token
    lines[index] = match.group(1) + projected + match.group(3)
    result = ''.join(lines)
    return result, dict(symbol=SYMBOL, original_token=token, size_bytes=value,
        projected_token=projected, changed=result != text,
        original_stdout_sha256=sha(text.encode()), projected_stdout_sha256=sha(result.encode()),
        original_stdout_bytes=len(text.encode()), projected_stdout_bytes=len(result.encode()))


def interpret():
    require(sys.dont_write_bytecode, 'Python -B required')
    snapshots = {name: read(name) for name in PINS}
    reader = types.ModuleType('_reviewed_static_abi_parser')
    reader.__file__ = str(ROOT / READER)
    exec(compile(snapshots[READER], reader.__file__, 'exec'), reader.__dict__)
    result, inputs, closure, artifacts = (json.loads(snapshots[name]) for name in
                                         (RESULT, INPUTS, CLOSURE, ARTIFACTS))
    require(result['scope'] == 'D188_STATIC_FILE_ONLY_ABI' and result['status'] == 'OBSERVED' and
            result['first_error'] is None and len(result['commands']) == len(inputs['commands']) == 4,
            'Original native file observation did not succeed')
    require(closure['status'] == 'FAILED' and closure['transport_calls'] == 1 and
            closure['first_error'] == dict(type='ValueError', message='Expected exactly one static diagnostic OBJECT') and
            closure['final_checks'] == [dict(name='local', status='PASS')], 'Original parser failure differs')
    checks = result['final_checks']
    require(len(checks) == len(inputs['remote_pins']) + 1 and
            {row['path'] for row in checks} == {*inputs['remote_pins'], 'board_identity'} and
            all(row == dict(path=row['path'], status='PASS') for row in checks), 'Remote closure differs')
    for record, command in zip(result['commands'], inputs['commands']):
        reader.checked_command(record, command)
    original = base64.b64decode(result['commands'][2]['stdout_base64'], validate=True).decode('utf-8')
    projected, projection = normalize(original)
    private = {**result, 'commands': [dict(row) for row in result['commands']]}
    private['commands'][2].update(stdout_base64=base64.b64encode(projected.encode()).decode(),
                                  stdout_bytes=len(projected.encode()))
    abi = reader.summarize(private, artifacts['layout']['validator_report'])
    final = []
    for name, raw in snapshots.items():
        require(read(name) == raw, 'Input changed during interpretation')
        final.append(dict(path=name, status='PASS'))
    return dict(schema='app-motor-fault-static-abi-interpretation-v1', status='OFFLINE_ABI_INTERPRETED',
                source_pins=PINS, projection=projection, abi=abi, final_checks=final,
                native_operations=0, original_attempt_status='FAILED',
                limitation='Only readelf symbol-size spelling projected; original raw attempt remains unchanged')


def main(argv):
    require(argv == ['--interpret'], 'Expected --interpret; no native mode exists')
    print(json.dumps(interpret(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main(sys.argv[1:])
