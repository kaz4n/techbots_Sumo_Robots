# Encodes one checked MATCH upload and validates its bounded result envelope.
# Keeps transport and native execution in the existing caller and uploader.
# Independent contract-derived tests cover framing, identities and reply guards.
import base64
import bz2
from datetime import datetime, timedelta
import hashlib
import json
import math
import re
import shlex
import subprocess

PAYLOAD_LIMIT = 196608
COMMAND_LIMIT = 30000
REPLY_LIMIT = 65536
RESULT_LIMIT = 16777216
PARENT = '/home/arduino/sumox26_codex_build'
DATA = '/home/arduino/.arduino15'
CORE = DATA + '/packages/arduino/hardware/zephyr/1.0.0'
ROLES = ('helper', 'support', 'upload', 'adapter')
FILES = {
    'cli': '/usr/bin/arduino-cli',
    'remoteocd': DATA + '/packages/arduino/tools/remoteocd/0.1.1/remoteocd',
    'adb': DATA + '/packages/arduino/tools/adb/32.0.0/adb',
    'flash_config': CORE + '/variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg',
    'openocd': '/opt/openocd/bin/openocd',
    'gpio_config': '/opt/openocd/openocd_gpiod.cfg',
    'target_config': '/opt/openocd/stm32u5x.cfg',
    'common_config': '/opt/openocd/stm32x5x_common.cfg',
    'swj': '/opt/openocd/share/openocd/scripts/target/swj-dp.tcl',
    'loader': CORE + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf',
    'mem_helper': '/opt/openocd/share/openocd/scripts/mem_helper.tcl',
    'boards': CORE + '/boards.txt', 'platform': CORE + '/platform.txt',
    'installed': CORE + '/installed.json', 'index': DATA + '/package_index.json'}
DIRECTORIES = (DATA + '/packages', DATA + '/packages/arduino/hardware/zephyr',
               DATA + '/packages/arduino/tools/remoteocd')
ABSENT = (CORE + '/boards.local.txt', CORE + '/platform.local.txt',
          DATA + '/packages/platform.txt', '/home/arduino/Arduino/hardware',
          '/home/arduino/openocd_gpiod.cfg', '/home/arduino/stm32u5x.cfg',
          '/home/arduino/stm32x5x_common.cfg', '/home/arduino/mem_helper.tcl',
          '/home/arduino/target/swj-dp.tcl', '/opt/openocd/mem_helper.tcl',
          '/opt/openocd/target/swj-dp.tcl')


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _keys(value, expected):
    _require(type(value) is dict and set(value) == set(expected) and
             all(type(key) is str for key in value), 'Wrong object fields')


def _canonical(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('ascii')


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _hex(value, width):
    _require(type(value) is str and re.fullmatch('[0-9a-f]{' + str(width) + '}', value),
             'Invalid lowercase hexadecimal identity')


def _ids(source_sha256, build_id, run_id):
    for value, width in ((source_sha256, 64), (build_id, 32), (run_id, 32)):
        _hex(value, width)


def _output(source_sha256, run_id):
    return PARENT + '/match-' + source_sha256[:8] + '-' + run_id + '-upload'


def _paths(source_sha256, build_id):
    root = (PARENT + '/_app_builds/native-app-v1/' + source_sha256 +
            '/match-immediate/' + build_id)
    files = dict(FILES)
    files.update(raw=root + '/build/app.ino.elf',
                 sketch=root + '/build/app.ino.elf-zsk.bin',
                 exported=root + '/artifacts/app.ino.elf-zsk.bin')
    sketch = PARENT + '/' + source_sha256 + '/app'
    absent = ABSENT + tuple(sketch + '/' + name for name in
                            ('sketch.yaml', 'sketch.yml', 'sketch.json'))
    return files, absent


def _pin(pin, path):
    _keys(pin, ('path', 'bytes', 'sha256'))
    _require(type(pin['path']) is str and pin['path'] == path, 'Wrong pinned path')
    _require(type(pin['bytes']) is int and 0 < pin['bytes'] <= 67108864,
             'Invalid pinned file size')
    _hex(pin['sha256'], 64)


def _bindings(value, source_sha256, build_id, run_id):
    _keys(value, ('schema', 'run_id', 'source_sha256', 'boot_id', 'uid',
                  'output', 'files', 'directories', 'absent'))
    expected = dict(schema='fixed-match-upload-v1', run_id=run_id,
                    source_sha256=source_sha256, output=_output(source_sha256, run_id))
    for key, item in expected.items():
        _require(type(value[key]) is str and value[key] == item, 'Wrong binding: ' + key)
    _require(type(value['boot_id']) is str and re.fullmatch(
        r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', value['boot_id']),
        'Invalid boot identity')
    _require(type(value['uid']) is int and value['uid'] == 1000, 'Wrong bound UID')
    files, absent = _paths(source_sha256, build_id)
    _keys(value['files'], files)
    for role, path in files.items():
        _pin(value['files'][role], path)
    package, exported = value['files']['sketch'], value['files']['exported']
    _require(all(package[key] == exported[key] for key in ('bytes', 'sha256')),
             'Build and exported MATCH packages differ')
    _keys(value['directories'], DIRECTORIES)
    for entries in value['directories'].values():
        _require(type(entries) is list and 1 <= len(entries) <= 64 and all(
            type(name) is str and re.fullmatch(r'[A-Za-z0-9_.-]+', name) and
            name not in ('.', '..') for name in entries), 'Invalid directory entries')
        _require(len(set(entries)) == len(entries), 'Duplicate directory entry')
    _require(type(value['absent']) is list and len(value['absent']) == len(absent) and
             all(type(path) is str for path in value['absent']) and
             set(value['absent']) == set(absent), 'Wrong absence selections')


# This trusted bootstrap is compressed independently of the bounded request.
# Request validation is repeated remotely before any supplied module is loaded.
_BOOTSTRAP_SOURCE = r'''
import base64,bz2,hashlib,json,re,sys,types

def require(ok,message):
 if not ok: raise ValueError(message)

def keys(value,names):
 require(type(value) is dict and set(value)==set(names) and all(type(k) is str for k in value),'Wrong object fields')

def canonical(value):
 return (json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('ascii')

def sha(raw):
 return hashlib.sha256(raw).hexdigest()

def hex_id(value,width):
 require(type(value) is str and re.fullmatch('[0-9a-f]{'+str(width)+'}',value),'Invalid hexadecimal identity')

def unique(pairs):
 result={}
 for key,value in pairs:
  require(key not in result,'Duplicate JSON key')
  result[key]=value
 return result

def nonfinite(value):
 raise ValueError('Nonfinite JSON number')

def paths(source,build):
 root=PARENT+'/_app_builds/native-app-v1/'+source+'/match-immediate/'+build
 files=dict(FILES)
 files.update(raw=root+'/build/app.ino.elf',sketch=root+'/build/app.ino.elf-zsk.bin',exported=root+'/artifacts/app.ino.elf-zsk.bin')
 sketch=PARENT+'/'+source+'/app'
 return files,ABSENT+tuple(sketch+'/'+name for name in ('sketch.yaml','sketch.yml','sketch.json'))

def bindings(value,source,build,run):
 keys(value,('schema','run_id','source_sha256','boot_id','uid','output','files','directories','absent'))
 fixed={'schema':'fixed-match-upload-v1','run_id':run,'source_sha256':source,'output':PARENT+'/match-'+source[:8]+'-'+run+'-upload'}
 for key,item in fixed.items():
  require(type(value[key]) is str and value[key]==item,'Wrong binding: '+key)
 require(type(value['boot_id']) is str and re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',value['boot_id']),'Invalid boot identity')
 require(type(value['uid']) is int and value['uid']==1000,'Wrong bound UID')
 files,absent=paths(source,build)
 keys(value['files'],files)
 for role,path in files.items():
  pin=value['files'][role]
  keys(pin,('path','bytes','sha256'))
  require(type(pin['path']) is str and pin['path']==path,'Wrong pinned path')
  require(type(pin['bytes']) is int and 0<pin['bytes']<=67108864,'Invalid pinned file size')
  hex_id(pin['sha256'],64)
 package,exported=value['files']['sketch'],value['files']['exported']
 require(all(package[k]==exported[k] for k in ('bytes','sha256')),'Build and exported MATCH packages differ')
 keys(value['directories'],DIRECTORIES)
 for entries in value['directories'].values():
  require(type(entries) is list and 1<=len(entries)<=64 and all(type(name) is str and re.fullmatch(r'[A-Za-z0-9_.-]+',name) and name not in ('.','..') for name in entries),'Invalid directory entries')
  require(len(set(entries))==len(entries),'Duplicate directory entry')
 require(type(value['absent']) is list and len(value['absent'])==len(absent) and all(type(path) is str for path in value['absent']) and set(value['absent'])==set(absent),'Wrong absence selections')

def request():
 require(len(sys.argv)==3 and sys.flags.isolated and sys.flags.dont_write_bytecode and sys.dont_write_bytecode is True,'Expected digest, payload and Python -I -B')
 digest,token=sys.argv[1:]
 hex_id(digest,64)
 require(0<len(token)<=30000,'Invalid payload encoding')
 compressed=base64.b85decode(token)
 require(base64.b85encode(compressed).decode('ascii')==token,'Noncanonical base85')
 decoder=bz2.BZ2Decompressor()
 raw=decoder.decompress(compressed,max_length=196609)
 require(len(raw)<=196608 and decoder.eof and not decoder.unused_data,'Invalid bounded BZ2 member')
 require(sha(raw)==digest,'Payload hash mismatch')
 payload=json.loads(raw.decode('ascii'),object_pairs_hook=unique,parse_constant=nonfinite)
 require(canonical(payload)==raw,'Noncanonical JSON')
 keys(payload,('schema','source_sha256','build_id','run_id','sources','bindings'))
 require(type(payload['schema']) is str and payload['schema']=='match-upload-payload-v1','Wrong payload schema')
 for key,width in (('source_sha256',64),('build_id',32),('run_id',32)):
  hex_id(payload[key],width)
 keys(payload['sources'],('helper','support','upload','adapter'))
 for item in payload['sources'].values():
  keys(item,('source','sha256'))
  require(type(item['source']) is str and item['source'],'Empty inline source')
  hex_id(item['sha256'],64)
  require(sha(item['source'].encode('utf-8'))==item['sha256'],'Inline source hash mismatch')
 bindings(payload['bindings'],payload['source_sha256'],payload['build_id'],payload['run_id'])
 return payload,digest

def load(role,item):
 name='fixed_match_'+role
 module=types.ModuleType(name)
 module.__file__='/__sumox__/'+name+'.py'
 exec(compile(item['source'],module.__file__,'exec'),module.__dict__)
 return module

def main():
 payload,digest=request()
 envelope={key:payload[key] for key in ('source_sha256','build_id','run_id')}
 envelope.update(schema='match-action-v1',payload_sha256=digest,remote_result_path=payload['bindings']['output']+'/upload_result.json',full_result_bytes=None,full_result_sha256=None,report=None,first_error=None)
 try:
  modules={role:load(role,payload['sources'][role]) for role in ('helper','support','upload','adapter')}
  report=modules['adapter'].upload_match(modules['helper'],modules['support'],modules['upload'],bindings=payload['bindings'],source_sha256=payload['source_sha256'],build_id=payload['build_id'],run_id=payload['run_id'])
  require(type(report) is dict,'Missing full upload result')
  full=modules['support'].json_bytes(report)
  require(type(full) is bytes and full==canonical(report) and 0<len(full)<=16777216,'Invalid full result encoding')
  envelope['full_result_bytes']=len(full)
  envelope['full_result_sha256']=sha(full)
  envelope['report']={key:value for key,value in report.items() if key not in ('stdout','stderr')}
 except Exception as error:
  envelope['first_error']={'type':type(error).__name__,'message':str(error)}
 raw=canonical(envelope)
 require(len(raw)<=65536,'Action reply exceeds bound')
 sys.stdout.write(raw.decode('ascii'))

main()
'''


def _bootstrap():
    definitions = '\n'.join(name + '=' + repr(value) for name, value in
                            (('PARENT', PARENT), ('FILES', FILES),
                             ('DIRECTORIES', DIRECTORIES), ('ABSENT', ABSENT)))
    raw = (definitions + '\n' + _BOOTSTRAP_SOURCE).encode('utf-8')
    token = base64.b85encode(bz2.compress(raw, compresslevel=9)).decode('ascii')
    return 'import base64,bz2\nexec(bz2.decompress(base64.b85decode(' + repr(token) + ')))'


BOOTSTRAP = _bootstrap()


def _command_units(remote, native_prefix):
    _require(type(native_prefix) in (list, tuple) and native_prefix and all(
        type(part) is str and part and '\0' not in part for part in native_prefix),
        'Invalid native transport prefix')
    command = subprocess.list2cmdline([*native_prefix, shlex.join(remote)])
    return len(command.encode('utf-16-le')) // 2 + 1


def build_command(sources, bindings, source_sha256, build_id, run_id, native_prefix):
    _ids(source_sha256, build_id, run_id)
    _keys(sources, ROLES)
    _bindings(bindings, source_sha256, build_id, run_id)
    inline = {}
    for role, raw in sources.items():
        _require(type(raw) is bytes and 0 < len(raw) <= PAYLOAD_LIMIT,
                 'Expected bounded nonempty source bytes')
        inline[role] = {'source': raw.decode('utf-8'), 'sha256': _sha(raw)}
    payload = _canonical(dict(schema='match-upload-payload-v1', source_sha256=source_sha256,
                              build_id=build_id, run_id=run_id, sources=inline, bindings=bindings))
    _require(len(payload) <= PAYLOAD_LIMIT, 'Payload exceeds bound')
    token = base64.b85encode(bz2.compress(payload, compresslevel=9)).decode('ascii')
    command = ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino',
               'LOGNAME=arduino', 'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C',
               '/usr/bin/python3', '-I', '-B', '-c', BOOTSTRAP, _sha(payload), token]
    _require(_command_units(command, native_prefix) <= COMMAND_LIMIT,
             'Windows command exceeds bound including NUL')
    return command


def _unique(pairs):
    value = {}
    for key, item in pairs:
        _require(key not in value, 'Duplicate JSON key')
        value[key] = item
    return value


def _nonfinite(value):
    raise ValueError('Nonfinite JSON number')


def _utc(value):
    _require(type(value) is str and re.fullmatch(
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)', value),
        'Invalid UTC timestamp')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    _require(result.utcoffset() == timedelta(0), 'Timestamp is not UTC')
    return result


def _report(report, source_sha256, run_id):
    _keys(report, ('schema', 'run_id', 'source_sha256', 'status', 'attempts',
                   'started_utc', 'finished_utc', 'started_monotonic',
                   'finished_monotonic', 'subprocess', 'first_error', 'postcheck_errors'))
    expected = dict(schema='match-upload-result-v1', source_sha256=source_sha256,
                    run_id=run_id, status='UPLOADED')
    for key, value in expected.items():
        _require(type(report[key]) is str and report[key] == value,
                 'Wrong upload report identity')
    _require(type(report['attempts']) is int and report['attempts'] == 1,
             'Upload must have exactly one attempt')
    _require(report['first_error'] is None and type(report['postcheck_errors']) is list
             and not report['postcheck_errors'], 'Upload report contains errors')
    start, finish = report['started_monotonic'], report['finished_monotonic']
    _require(all(type(value) in (int, float) and math.isfinite(value) and value >= 0
                 for value in (start, finish)) and finish >= start,
             'Invalid monotonic clock ordering')
    _require(_utc(report['finished_utc']) >= _utc(report['started_utc']),
             'UTC clock moved backwards')
    child = report['subprocess']
    _keys(child, ('returncode', 'timed_out', 'reaped'))
    _require(type(child['returncode']) is int and child['returncode'] == 0 and
             child['timed_out'] is False and child['reaped'] is True,
             'Upload child did not exit cleanly')


def _reply(text, source_sha256, build_id, run_id, payload_sha256):
    _ids(source_sha256, build_id, run_id)
    _hex(payload_sha256, 64)
    _require(type(text) is str and len(text) <= REPLY_LIMIT, 'Invalid reply text')
    raw = text.encode('ascii')
    reply = json.loads(text, object_pairs_hook=_unique, parse_constant=_nonfinite)
    _require(raw == _canonical(reply), 'Noncanonical reply JSON')
    _keys(reply, ('schema', 'source_sha256', 'build_id', 'run_id', 'payload_sha256',
                  'remote_result_path', 'full_result_bytes', 'full_result_sha256',
                  'report', 'first_error'))
    expected = dict(schema='match-action-v1', source_sha256=source_sha256,
                    build_id=build_id, run_id=run_id, payload_sha256=payload_sha256,
                    remote_result_path=_output(source_sha256, run_id) + '/upload_result.json')
    for key, value in expected.items():
        _require(type(reply[key]) is str and reply[key] == value,
                 'Wrong action reply identity')
    _require(reply['first_error'] is None, 'Remote action contains an error')
    _require(type(reply['full_result_bytes']) is int and
             0 < reply['full_result_bytes'] <= RESULT_LIMIT, 'Invalid full result size')
    _hex(reply['full_result_sha256'], 64)
    _report(reply['report'], source_sha256, run_id)
    return reply


def validate_reply(text, source_sha256, build_id, run_id, payload_sha256):
    try:
        return _reply(text, source_sha256, build_id, run_id, payload_sha256)
    except (TypeError, OverflowError, RecursionError) as error:
        raise ValueError('Malformed MATCH action reply') from error
