# Selects one checked D222 artifact for the unchanged descriptor-bound uploader.
# Keeps profile selection separate from physical qualification and run permission.
# Independent D227 fixtures cover identities, payload bounds and inherited guards.
import ast
import base64
import bz2
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import shlex
import subprocess
import sys
import types


PROFILES = ('b4_stand', 'p3_drive', 'p3_turn', 'p3_stop', 'p4_reactive',
            'p4_timing', 'p5_abort_timing')
SELECTION = ('profile', 'motors_allowed', 'compile_attempt', 'source_sha256', 'run_id')
PARENT = '/home/arduino/sumox26_codex_build'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
SOURCE_PINS = {
    'helper': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8',
    'support': '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e',
    'upload': 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1',
    'inherited_adapter': '777a2f29a326094c34298f07d3597eb603bf3487f8780f18c5da122bb527d9be'}
PAYLOAD_LIMIT, COMMAND_LIMIT, REPLY_LIMIT = 196608, 30000, 65536


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, names):
    require(type(value) is dict and set(value) == set(names) and
            all(type(key) is str for key in value), 'Unexpected object fields')


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON field')
        result[key] = value
    return result


def decode(raw):
    value = json.loads(raw, object_pairs_hook=unique)
    canonical(value)
    return value


def checked_selection(value):
    keys(value, SELECTION)
    require(type(value['profile']) is str and value['profile'] in PROFILES, 'Unknown profile')
    require(type(value['motors_allowed']) is int and value['motors_allowed'] in (0, 1),
            'Explicit motor integer required')
    require(type(value['compile_attempt']) is str and
            re.fullmatch('[a-z][a-z0-9_]{0,23}', value['compile_attempt']), 'Invalid compile attempt')
    for name, width in (('source_sha256', 64), ('run_id', 32)):
        require(type(value[name]) is str and re.fullmatch('[0-9a-f]{' + str(width) + '}', value[name]),
                'Invalid ' + name)
    return dict(value)


def commissioning_profile(uploader, support, *, profile, motors_allowed,
                          compile_attempt, source_sha256, run_id):
    selected = checked_selection(dict(profile=profile, motors_allowed=motors_allowed,
        compile_attempt=compile_attempt, source_sha256=source_sha256, run_id=run_id))
    digest = sha((source_sha256 + '\0' + compile_attempt).encode())[:12]
    owner = 'commission-' + profile + '-m' + str(motors_allowed) + '-' + digest
    build = PARENT + '/' + owner
    sketch = PARENT + '/' + source_sha256 + '/app'
    files = dict(uploader.FILE_PATHS)
    files.update(raw=build + '/build/app.ino.bin', sketch=build + '/build/app.ino.bin-zsk.bin',
                 exported=build + '/artifacts/app.ino.bin-zsk.bin')
    absent = tuple(uploader.ABSENT[:-3]) + tuple(sketch + '/' + name
        for name in ('sketch.yaml', 'sketch.yml', 'sketch.json'))
    return dict(fixed=dict(schema='fixed-commissioning-app-upload-v1', run_id=run_id,
                          source_sha256=source_sha256, output=PARENT + '/commission-upload-' + run_id),
                schema_prefix='commissioning-app-upload-', files=files, absent=absent,
                argv=['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload',
                      '--fqbn', FQBN, '--input-file', files['raw'], sketch])


def checked_sources(sources):
    keys(sources, (*SOURCE_PINS, 'adapter'))
    for name, raw in sources.items():
        require(type(raw) is bytes and 0 < len(raw) <= PAYLOAD_LIMIT, 'Invalid source bytes')
        require(name not in SOURCE_PINS or sha(raw) == SOURCE_PINS[name],
                'Frozen upload source changed: ' + name)
    return sources


def load_module(name, raw):
    module = types.ModuleType('_sumox_commissioning_' + name)
    module.__file__ = '/__sumox__/' + name + '.py'
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def native_upload(payload):
    keys(payload, ('schema', 'selection', 'sources', 'bindings'))
    require(payload['schema'] == 'commissioning-app-upload-payload-v1', 'Invalid payload schema')
    selected = checked_selection(payload['selection'])
    keys(payload['sources'], (*SOURCE_PINS, 'adapter'))
    sources = {}
    for name, record in payload['sources'].items():
        keys(record, ('source', 'sha256'))
        require(type(record['source']) is str, 'Invalid source text')
        raw = record['source'].encode('utf-8')
        require(sha(raw) == record['sha256'], 'Source identity differs')
        sources[name] = raw
    checked_sources(sources)
    modules = {name: load_module(name, sources[name]) for name in SOURCE_PINS}
    uploader, support = modules['upload'], modules['support']
    profile = commissioning_profile(uploader, support, **selected)
    bindings = uploader._checked_bindings(support, payload['bindings'], profile)
    require(all(bindings['files']['sketch'][key] == bindings['files']['exported'][key]
                for key in ('bytes', 'sha256')), 'Packaged/exported artifacts differ')
    attempt = modules['inherited_adapter']._attempt_type(uploader)(
        modules['helper'], support, profile, bindings, Path('/'), None, None)
    attempt.report['schema'] = 'commissioning-app-upload-result-v1'
    return uploader._upload(attempt)


BOOTSTRAP = '''import base64,bz2,hashlib,json,sys,types
if len(sys.argv)!=3 or not sys.flags.isolated or not sys.dont_write_bytecode:raise ValueError('Isolated bounded payload required')
expected,token=sys.argv[1:]
if len(token)>30000:raise ValueError('Token bound exceeded')
packed=base64.b85decode(token)
if base64.b85encode(packed).decode()!=token:raise ValueError('Noncanonical token')
decoder=bz2.BZ2Decompressor();raw=decoder.decompress(packed,max_length=196609)
if len(raw)>196608 or not decoder.eof or decoder.unused_data or hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Payload changed')
def unique(pairs):
 result={}
 for key,value in pairs:
  if key in result:raise ValueError('Duplicate JSON key')
  result[key]=value
 return result
payload=json.loads(raw,object_pairs_hook=unique)
canonical=lambda x:(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\\n').encode('ascii')
if canonical(payload)!=raw:raise ValueError('Noncanonical payload')
record=payload['sources']['adapter'];source=record['source'].encode('utf-8')
if hashlib.sha256(source).hexdigest()!=record['sha256']:raise ValueError('Adapter changed')
module=types.ModuleType('_commissioning_native');module.__file__='/__sumox__/adapter.py'
exec(compile(source,module.__file__,'exec'),module.__dict__)
result=dict(schema='commissioning-app-action-v1',selection=payload['selection'],payload_sha256=expected,remote_result_path=payload['bindings']['output']+'/upload_result.json',full_result_bytes=None,full_result_sha256=None,report=None,first_error=None)
try:
 report=module.native_upload(payload);full=canonical(report)
 if not 0<len(full)<=16777216:raise ValueError('Result bound exceeded')
 result.update(full_result_bytes=len(full),full_result_sha256=hashlib.sha256(full).hexdigest(),report={key:value for key,value in report.items() if key not in ('stdout','stderr')})
except Exception as error:
 result['first_error']=dict(type=type(error).__name__,message=str(error))
reply=canonical(result)
if len(reply)>65536:raise ValueError('Reply bound exceeded')
sys.stdout.write(reply.decode('ascii'))
'''


def build_command(sources, bindings, selection, native_prefix):
    selected, sources = checked_selection(selection), checked_sources(sources)
    validate_bindings(sources, bindings, selected)
    require(type(native_prefix) in (list, tuple) and native_prefix and all(
        type(part) is str and part and '\0' not in part for part in native_prefix), 'Invalid transport prefix')
    sources = dict(sources, adapter=native_source(sources['adapter']))
    payload = canonical(dict(schema='commissioning-app-upload-payload-v1', selection=selected,
        bindings=bindings, sources={name: dict(source=raw.decode('utf-8'), sha256=sha(raw))
                                   for name, raw in sources.items()}))
    require(len(payload) <= PAYLOAD_LIMIT, 'Payload exceeds bound')
    token = base64.b85encode(bz2.compress(payload, compresslevel=9)).decode('ascii')
    boot = base64.b85encode(bz2.compress(BOOTSTRAP.encode(), compresslevel=9)).decode('ascii')
    command = ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino', 'LOGNAME=arduino',
               'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C', '/usr/bin/python3', '-I', '-B', '-c',
               'import base64,bz2\nexec(bz2.decompress(base64.b85decode(' + repr(boot) + ')))',
               sha(payload), token]
    units = len(subprocess.list2cmdline([*native_prefix, shlex.join(command)]).encode('utf-16-le')) // 2 + 1
    require(units <= COMMAND_LIMIT and len(token) <= 30000, 'Windows command exceeds bound including NUL')
    return command


def native_source(raw):
    # The exact prefix contains only the profile and unchanged-uploader adapter.
    marker = b"\nBOOTSTRAP = '''"
    require(raw.count(marker) == 1, 'Native adapter boundary changed')
    prefix = raw.split(marker)[0]
    compile(prefix, '<checked-commissioning-native-prefix>', 'exec')
    return prefix


def validate_bindings(sources, bindings, selection):
    # Same five pure support definitions as frozen match_deploy.binding_support.
    names = ('require', 'keys', 'json_bytes', 'valid_path', 'check_pin')
    tree = ast.parse(sources['support'])
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    require(sorted(node.name for node in definitions) == sorted(names), 'Frozen binding definitions differ')
    namespace = {'json': json, 're': re}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), '<checked-binding-view>', 'exec'), namespace)
    support = types.SimpleNamespace(**{name: namespace[name] for name in names})
    uploader = load_module('binding_view', sources['upload'])
    profile = commissioning_profile(uploader, support, **selection)
    checked = uploader._checked_bindings(support, bindings, profile)
    require(all(checked['files']['sketch'][key] == checked['files']['exported'][key]
                for key in ('bytes', 'sha256')), 'Packaged/exported artifacts differ')


def validate_report(report, selected):
    keys(report, ('schema', 'run_id', 'source_sha256', 'status', 'attempts',
        'started_utc', 'finished_utc', 'started_monotonic', 'finished_monotonic',
        'subprocess', 'first_error', 'postcheck_errors'))
    expected = dict(schema='commissioning-app-upload-result-v1', status='UPLOADED',
                    run_id=selected['run_id'], source_sha256=selected['source_sha256'], attempts=1)
    require(all(type(report[key]) is type(value) and report[key] == value
                for key, value in expected.items()), 'Wrong upload report identity')
    require(report['first_error'] is None and report['postcheck_errors'] == [], 'Upload report errors')
    start, finish = report['started_monotonic'], report['finished_monotonic']
    require(all(type(value) in (int, float) and math.isfinite(value) and value >= 0
                for value in (start, finish)) and finish >= start, 'Invalid monotonic clock')
    stamps = [datetime.fromisoformat(report[key].replace('Z', '+00:00'))
              for key in ('started_utc', 'finished_utc')]
    require(all(value.utcoffset() is not None and value.utcoffset().total_seconds() == 0
                for value in stamps) and stamps[1] >= stamps[0], 'Invalid UTC ordering')
    child = report['subprocess']
    keys(child, ('returncode', 'timed_out', 'reaped'))
    require(type(child['returncode']) is int and child['returncode'] == 0 and
            child['timed_out'] is False and child['reaped'] is True, 'Upload child failed')


def validate_reply(text, selection, payload_sha256):
    selected = checked_selection(selection)
    require(type(payload_sha256) is str and re.fullmatch('[0-9a-f]{64}', payload_sha256),
            'Invalid payload identity')
    require(type(text) is str and len(text) <= REPLY_LIMIT, 'Invalid reply text')
    value = decode(text)
    require(canonical(value) == text.encode('ascii'), 'Noncanonical upload reply')
    keys(value, ('schema', 'selection', 'payload_sha256', 'remote_result_path',
                 'full_result_bytes', 'full_result_sha256', 'report', 'first_error'))
    require(value['schema'] == 'commissioning-app-action-v1' and
            canonical(value['selection']) == canonical(selected) and value['payload_sha256'] == payload_sha256
            and value['remote_result_path'] == PARENT + '/commission-upload-' + selected['run_id'] +
            '/upload_result.json' and value['first_error'] is None, 'Remote action failed or differs')
    require(type(value['full_result_bytes']) is int and 0 < value['full_result_bytes'] <= 16777216 and
            type(value['full_result_sha256']) is str and re.fullmatch('[0-9a-f]{64}', value['full_result_sha256']),
            'Invalid durable result identity')
    validate_report(value['report'], selected)
    return value
