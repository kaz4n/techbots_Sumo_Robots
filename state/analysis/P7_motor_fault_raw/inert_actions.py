# Composes and admits the fixed inert diagnostic upload and capture actions.
# Reuses existing remote APIs while keeping native ownership with a later caller.
# Independent host oracles cover framing, receipts and conditional failure paths.
import base64
import bz2
import hashlib
import json
import math
import re
import shlex
import subprocess

RUN_ID = 'motor-fault-8f592937-run01'
SOURCE = '8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36'
PARENT = '/home/arduino/sumox26_codex_build/'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
BOARD = '2629958581'
PAYLOAD_LIMIT = 196608
COMMAND_LIMIT = 30000

# Only this fixed, trusted bootstrap is compressed for command-line space.
# Its separate untrusted payload still receives bounded, single-member decoding.
_BOOTSTRAP_SOURCE = r'''
import base64,bz2,hashlib,json,os,re,sys,types
RUN_ID='motor-fault-8f592937-run01'
SOURCE='8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36'
PARENT='/home/arduino/sumox26_codex_build/'
INSTALLED='/home/arduino/sumox26-capture-tools/runtime-a4d58b3cbac8/'
PINS=(('p0_capture',18880,'885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c'),
 ('recorder_heap',11002,'d661024975925a7d8a83f4b772199bbf59911adb5adb8ea69a2082b69eed4b92'),
 ('runtime_capture',28644,'a4d58b3cbac8b0a3cf96ce6d4f53bc17e935b9aee9bc1c09809ee20ea806fdae'))
def require(ok,message):
 if not ok: raise ValueError(message)
def canonical(value):
 return (json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('ascii')
def sha(raw):
 return hashlib.sha256(raw).hexdigest()
def keys(value,names):
 require(type(value) is dict and set(value)==set(names),'Wrong object fields')
def unique(pairs):
 value={}
 for key,item in pairs:
  require(key not in value,'Duplicate JSON key')
  value[key]=item
 return value
def nonfinite(value):
 raise ValueError('Nonfinite JSON number')
def load(name,source,filename):
 module=types.ModuleType(name)
 module.__file__=filename
 sys.modules[name]=module
 exec(compile(source,filename,'exec'),module.__dict__)
 return module
def error_record(error):
 return {'type':type(error).__name__,'message':str(error)}
def remember(envelope,error,check=None):
 record=error_record(error)
 if envelope['first_error'] is None: envelope['first_error']=record
 if check is not None: envelope['postcheck_errors'].append({'check':check,**record})
def installed_read(helper,root,pin):
 name,size,digest=pin
 raw=helper.logical_read(root,INSTALLED+name+'.py',size)
 require(type(raw) is bytes and len(raw)==size and sha(raw)==digest,'Installed source mismatch: '+name)
 return raw.decode('utf-8')
def capture(helper,sources,bindings,envelope):
 root=None
 try:
  root=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
  installed=[installed_read(helper,root,pin) for pin in PINS]
  support=load('fixed_motor_fault_support',sources['support']['source'],'/__sumox__/support.py')
  modules=[load(pin[0],source,INSTALLED+pin[0]+'.py') for pin,source in zip(PINS,installed)]
  envelope['report']=support.collect_motor_fault(helper,modules[2],modules[0].loader_image,bindings=bindings,run_id=RUN_ID)
 except Exception as error:
  remember(envelope,error)
 finally:
  if root is not None:
   for pin in PINS:
    try: installed_read(helper,root,pin)
    except Exception as error: remember(envelope,error,'installed:'+pin[0])
   try: os.close(root)
   except Exception as error: remember(envelope,error,'root_close')
def request():
 require(len(sys.argv)==4 and sys.flags.dont_write_bytecode,'Expected action, hash, payload and Python -B')
 action,digest,token=sys.argv[1:]
 require(type(action) is str and action in ('upload','capture'),'Wrong action')
 require(re.fullmatch('[0-9a-f]{64}',digest) is not None,'Wrong payload digest')
 compressed=base64.b64decode(token,validate=True)
 require(base64.b64encode(compressed).decode('ascii')==token,'Noncanonical base64')
 decoder=bz2.BZ2Decompressor()
 raw=decoder.decompress(compressed,max_length=196609)
 require(len(raw)<=196608 and decoder.eof and not decoder.unused_data,'Invalid bounded BZ2 member')
 require(sha(raw)==digest,'Payload hash mismatch')
 payload=json.loads(raw.decode('ascii'),object_pairs_hook=unique,parse_constant=nonfinite)
 require(canonical(payload)==raw,'Noncanonical JSON')
 keys(payload,('run_id','source_sha256','sources','bindings'))
 require(payload['run_id']==RUN_ID and payload['source_sha256']==SOURCE,'Wrong payload identity')
 sources=payload['sources']
 roles=('helper','support','upload') if action=='upload' else ('helper','support')
 keys(sources,roles)
 for role in roles:
  item=sources[role]
  keys(item,('source','sha256'))
  require(type(item['source']) is str and item['source'],'Empty inline source')
  require(type(item['sha256']) is str and sha(item['source'].encode('utf-8'))==item['sha256'],'Inline source hash mismatch')
 bindings=payload['bindings']
 require(type(bindings) is dict,'Wrong bindings type')
 fixed={'schema':'fixed-motor-fault-'+action+'-v1','run_id':RUN_ID,'source_sha256':SOURCE,'output':PARENT+RUN_ID+'-'+action}
 for name,value in fixed.items():
  require(type(bindings.get(name)) is str and bindings[name]==value,'Wrong binding: '+name)
 return action,sources,bindings
def main():
 action,sources,bindings=request()
 envelope={'schema':'motor-fault-action-v1','action':action,'run_id':RUN_ID,'source_sha256':SOURCE,
  'report':None,'remote_result_path':bindings['output']+'/'+action+'_result.json',
  'full_result_bytes':None,'full_result_sha256':None,'first_error':None,'postcheck_errors':[]}
 try:
  helper=load('fixed_motor_fault_helper',sources['helper']['source'],'/__sumox__/helper.py')
  if action=='capture': capture(helper,sources,bindings,envelope)
  else:
   support=load('fixed_motor_fault_support',sources['support']['source'],'/__sumox__/support.py')
   upload=load('fixed_motor_fault_upload',sources['upload']['source'],'/__sumox__/upload.py')
   envelope['report']=upload.upload_loader(helper,support,bindings=bindings,run_id=RUN_ID)
 except Exception as error:
  remember(envelope,error)
 if envelope['report'] is not None:
  full=canonical(envelope['report'])
  envelope['full_result_bytes']=len(full)
  envelope['full_result_sha256']=sha(full)
  if action=='upload': envelope['report']={key:value for key,value in envelope['report'].items() if key not in ('stdout','stderr')}
 raw=canonical(envelope)
 require(len(raw)<=65536,'Action reply exceeds bound')
 sys.stdout.write(raw.decode('ascii'))
main()
'''
BOOTSTRAP = ('import base64,bz2\nexec(bz2.decompress(base64.b64decode(' +
             repr(base64.b64encode(bz2.compress(
                 _BOOTSTRAP_SOURCE.encode('utf-8'), compresslevel=9)).decode('ascii')) + ')))')


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _keys(value, names):
    _require(type(value) is dict and set(value) == set(names), 'Wrong object fields')


def _canonical(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, allow_nan=False,
                       separators=(',', ':')) + '\n').encode('ascii')


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _action(action):
    _require(type(action) is str and action in ('upload', 'capture'), 'Wrong action')


def _identity(action, bindings):
    _require(type(bindings) is dict, 'Wrong bindings type')
    fixed = {'schema': 'fixed-motor-fault-' + action + '-v1', 'run_id': RUN_ID,
             'source_sha256': SOURCE, 'output': PARENT + RUN_ID + '-' + action}
    for name, value in fixed.items():
        _require(type(bindings.get(name)) is str and bindings[name] == value,
                 'Wrong binding: ' + name)


def build_command(action, sources, bindings):
    _action(action)
    _keys(sources, ('helper', 'support', 'upload') if action == 'upload'
          else ('helper', 'support'))
    _identity(action, bindings)
    inline = {}
    for role, raw in sources.items():
        _require(type(raw) is bytes and raw, 'Expected nonempty source bytes')
        inline[role] = {'source': raw.decode('utf-8'), 'sha256': _sha(raw)}
    payload = _canonical({'run_id': RUN_ID, 'source_sha256': SOURCE,
                          'sources': inline, 'bindings': bindings})
    _require(len(payload) <= PAYLOAD_LIMIT, 'Payload exceeds bound')
    token = base64.b64encode(bz2.compress(payload, compresslevel=9)).decode('ascii')
    remote = ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino',
              'LOGNAME=arduino', 'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C',
              '/usr/bin/python3', '-I', '-B', '-c', BOOTSTRAP, action, _sha(payload), token]
    native = [ADB, '-s', BOARD, 'shell', '-T', shlex.join(remote)]
    units = len(subprocess.list2cmdline(native).encode('utf-16-le')) // 2
    _require(units <= COMMAND_LIMIT, 'Windows command exceeds bound')
    return remote


def _digest(value):
    _require(type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value),
             'Invalid SHA256')


def _integer(value, expected):
    _require(type(value) is int and value == expected, 'Wrong integer value')


def _number(value):
    _require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
             'Invalid nonnegative clock')


def _clean(value):
    _require(value['first_error'] is None and type(value['postcheck_errors']) is list
             and not value['postcheck_errors'], 'Action contains errors')


def _report(action, report):
    common = ('schema', 'run_id', 'source_sha256', 'status', 'started_utc',
              'finished_utc', 'started_monotonic', 'finished_monotonic',
              'first_error', 'postcheck_errors')
    extra = ('attempts', 'subprocess') if action == 'upload' else (
        'counts', 'wait', 'reads', 'analysis')
    _keys(report, common + extra)
    expected = {'schema': 'motor-fault-' + action + '-result-v1', 'run_id': RUN_ID,
                'source_sha256': SOURCE,
                'status': 'UPLOADED' if action == 'upload' else 'COLLECTED'}
    for key, value in expected.items():
        _require(type(report[key]) is str and report[key] == value, 'Wrong report identity')
    for key in ('started_utc', 'finished_utc'):
        _require(type(report[key]) is str and report[key], 'Missing UTC timestamp')
    start, finish = report['started_monotonic'], report['finished_monotonic']
    _number(start)
    _number(finish)
    _require(0 <= finish - start < (180 if action == 'upload' else 600),
             'Report duration exceeds bound or reverses time')
    _clean(report)


def _upload(report):
    _integer(report['attempts'], 1)
    child = report['subprocess']
    _keys(child, ('returncode', 'timed_out', 'reaped'))
    _integer(child['returncode'], 0)
    _require(child['timed_out'] is False and child['reaped'] is True,
             'Upload subprocess did not succeed')


def _ram(address, size, alignment):
    _require(type(address) is int and address % alignment == 0 and
             0x20000000 <= address and address + size <= 0x200c0000,
             'Invalid SRAM extent')


def _relocation(value):
    _keys(value, ('node_address', 'bss_address', 'bss_size', 'visited_nodes'))
    nodes = value['visited_nodes']
    _require(type(nodes) is list and 1 <= len(nodes) <= 3, 'Invalid node list')
    for address in nodes:
        _ram(address, 196, 4)
    _require(len(set(nodes)) == len(nodes), 'Repeated extension node')
    _require(type(value['node_address']) is int and value['node_address'] in nodes,
             'Selected node is absent')
    _integer(value['bss_size'], 2632)
    _ram(value['bss_address'], 2632, 8)


def _plan(extension):
    def flash(prefix, region):
        size, base = (263680, 0x08000000) if region == 'loader' else (29836, 0x08100000)
        return [(prefix + '.' + region + '.' + str(index), base + offset,
                 min(65536, size - offset))
                for index, offset in enumerate(range(0, size, 65536))]

    def traversal(prefix):
        return ([(prefix + '.llext-list', 0x200017bc, 8)] +
                [(prefix + '.node-' + str(index + 1), address, 196)
                 for index, address in enumerate(extension['visited_nodes'])] +
                [(prefix + '.llext-list-confirm', 0x200017bc, 8)])

    snapshots = [(name + '.diagnostic', extension['bss_address'], 2592)
                 for name in ('first', 'second')]
    return (flash('before', 'loader') + flash('before', 'sketch') + traversal('before') +
            snapshots + traversal('after') + flash('after', 'sketch') + flash('after', 'loader'))


def _reads(reads, plan):
    _require(type(reads) is list and len(reads) == len(plan), 'Wrong read count')
    for index, (item, expected) in enumerate(zip(reads, plan)):
        _keys(item, ('name', 'address', 'bytes', 'sha256', 'file'))
        name, address, size = expected
        _require(type(item['name']) is str and item['name'] == name, 'Wrong read name')
        _integer(item['address'], address)
        _integer(item['bytes'], size)
        _digest(item['sha256'])
        _require(type(item['file']) is str and item['file'] == f'{index:02d}-{name}.bin',
                 'Wrong read basename')


def _capture(report):
    analysis = report['analysis']
    _keys(analysis, ('schema', 'flash', 'relocation', 'snapshots', 'coherence'))
    _require(type(analysis['schema']) is str and
             analysis['schema'] == 'motor-fault-capture-analysis-v1' and
             type(analysis['coherence']) is str and analysis['coherence'] == 'UNPROVEN',
             'Wrong analysis identity')
    _keys(analysis['flash'], ('before_loader', 'before_sketch', 'after_loader', 'after_sketch'))
    _require(all(value is True for value in analysis['flash'].values()), 'Flash was not verified')
    _keys(analysis['relocation'], ('before', 'after'))
    before, after = (analysis['relocation'][name] for name in ('before', 'after'))
    _relocation(before)
    _relocation(after)
    _require(before == after, 'Relocation changed')
    nodes = len(before['visited_nodes'])
    _keys(report['counts'], ('commands', 'reads', 'requested_bytes'))
    for key, value in (('commands', 18 + 2 * nodes), ('reads', 18 + 2 * nodes),
                       ('requested_bytes', 592248 + 392 * nodes)):
        _integer(report['counts'][key], value)
    _reads(report['reads'], _plan(before))
    snapshots = [item for item in report['reads'] if item['name'] in
                 ('first.diagnostic', 'second.diagnostic')]
    _require(type(analysis['snapshots']) is list and
             _canonical(analysis['snapshots']) == _canonical(snapshots), 'Wrong snapshots')
    wait = report['wait']
    _keys(wait, ('requested_seconds', 'before', 'after'))
    _integer(wait['requested_seconds'], 2)
    _number(wait['before'])
    _number(wait['after'])
    _require(report['started_monotonic'] <= wait['before'] and
             wait['after'] <= report['finished_monotonic'] and
             wait['after'] - wait['before'] >= 2, 'Invalid sample separation')


def validate_reply(action, reply):
    try:
        _validate_reply(action, reply)
    except (TypeError, OverflowError, RecursionError) as error:
        raise ValueError('Malformed action reply') from error


def _validate_reply(action, reply):
    _action(action)
    _keys(reply, ('schema', 'action', 'run_id', 'source_sha256', 'report',
                  'remote_result_path', 'full_result_bytes', 'full_result_sha256',
                  'first_error', 'postcheck_errors'))
    expected = {'schema': 'motor-fault-action-v1', 'action': action, 'run_id': RUN_ID,
                'source_sha256': SOURCE, 'remote_result_path':
                PARENT + RUN_ID + '-' + action + '/' + action + '_result.json'}
    for key, value in expected.items():
        _require(type(reply[key]) is str and reply[key] == value, 'Wrong envelope identity')
    _clean(reply)
    _require(type(reply['full_result_bytes']) is int and
             0 < reply['full_result_bytes'] <= 16777216, 'Invalid full result size')
    _digest(reply['full_result_sha256'])
    report = reply['report']
    _report(action, report)
    if action == 'upload':
        _upload(report)
    else:
        _capture(report)
        raw = _canonical(report)
        _require(len(raw) == reply['full_result_bytes'] and
                 _sha(raw) == reply['full_result_sha256'], 'Capture result hash or size mismatch')


def _remember(report, error, check=None):
    record = {'type': type(error).__name__, 'message': str(error)}
    if report['first_error'] is None:
        report['first_error'] = record
    if check is not None:
        report['postcheck_errors'].append({'check': check, **record})


def run_actions(operations):
    _keys(operations, ('local', 'prerequisites', 'intent', 'upload', 'capture', 'finish'))
    _require(all(callable(operation) for operation in operations.values()),
             'Expected six callable operations')
    report = {'schema': 'motor-fault-sequence-v1', 'status': 'FAILED',
              'upload': None, 'capture': None, 'upload_attempts': 0,
              'capture_attempts': 0, 'first_error': None, 'postcheck_errors': []}
    try:
        for action in ('upload', 'capture'):
            operations['local']()
            operations['prerequisites']()
            predecessor = None if action == 'upload' else report['upload']
            operations['intent'](action, predecessor)
            report[action + '_attempts'] += 1
            report[action] = operations[action]()
            validate_reply(action, report[action])
    except Exception as error:
        _remember(report, error)
    for check in ('local', 'prerequisites'):
        try:
            operations[check]()
        except Exception as error:
            _remember(report, error, check)
    if report['first_error'] is None and not report['postcheck_errors']:
        report['status'] = 'COMPLETED'
    try:
        operations['finish'](report)
    except Exception as error:
        report['status'] = 'FAILED'
        _remember(report, error, 'finish')
        error.sequence_result = report
        raise
    return report
