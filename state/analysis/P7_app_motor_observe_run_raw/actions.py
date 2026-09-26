# Composes the fixed static diagnostic actions through the established framing.
# Preserves one-shot sequencing and errors while checking a small staged adapter.
# Independent contract fixtures verify composition, receipts and failure closure.
import ast
import base64
import bz2
import hashlib
import json
from pathlib import Path
import stat
import types

ROOT = Path(__file__).absolute().parents[3]
LEGACY = 'state/analysis/P7_motor_fault_raw/inert_actions.py'
LEGACY_SHA = '8ffb65c0f1284f261ae1237bcf260e866176e83433a3538908780962513f1104'
SOURCE = '3a08ddeb437c47940a1a6b2ba8e63f7843e5b242ca68ae38c27849bd4e33dbb0'
RUN_ID = 'app-motor-observe-3a08ddeb-run01'
PARENT = '/home/arduino/sumox26_codex_build/'
ADAPTER = PARENT + RUN_ID + '-adapter/remote.py'
ADAPTER_SHA = '98b0f5394d64f61178277f701adb81eece3d5f136ea84a8c5fb30534a5b241db'
ADAPTER_BYTES = 11357
SOURCE_HASHES = {
    'helper': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8',
    'support': '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e',
    'upload': 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1'}
WINDOWS = (('trace', 536951180, 2128), ('report', 537119696, 1168),
           ('runtime', 537117984, 600), ('transaction', 537115448, 504),
           ('previous', 537115952, 48), ('gate', 536953520, 88))


def checked_source(path, expected):
    for item in (path, *path.parents):
        info = item.lstat()
        plain = stat.S_ISREG if item == path else stat.S_ISDIR
        if not plain(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 1024:
            raise ValueError('Nonplain dependency: ' + str(item))
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('Changed dependency: ' + str(path))
    return raw


def _legacy():
    raw = checked_source(ROOT / LEGACY, LEGACY_SHA)
    module = types.ModuleType('_app_motor_observe_actions_legacy')
    module.__file__ = str(ROOT / LEGACY)
    source = raw.decode('utf-8').replace('motor-fault-', 'app-motor-observe-')
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    module.RUN_ID, module.SOURCE = RUN_ID, SOURCE
    return module


legacy = _legacy()

_CAPTURE = r'''
def staged_read(helper,root,pin):
 raw=helper.logical_read(root,pin['path'],pin['bytes'])
 require(type(raw) is bytes and len(raw)==pin['bytes'] and sha(raw)==pin['sha256'],'Staged adapter mismatch')
 return raw

def perform(action,sources,bindings,adapter_pin,envelope):
 root=None;helper=None;parser_read=False
 try:
  helper=load('fixed_app_fault_helper',sources['helper']['source'],'/__sumox__/helper.py')
  root=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
  adapter=load('fixed_app_fault_adapter',staged_read(helper,root,adapter_pin),adapter_pin['path'])
  dependencies=adapter.load_dependencies({role:sources[key]['source'].encode('utf-8') for role,key in (('helper','helper'),('capture','support'),('upload','upload'))})
  if action=='capture':
   parser_read=True
   parser=load('p0_capture',installed_read(helper,root,PINS[0]),INSTALLED+'p0_capture.py')
   envelope['report']=adapter.collect(dependencies,parser.loader_image,bindings=bindings)
  else: envelope['report']=adapter.upload(dependencies,bindings=bindings)
  envelope['report_origin']='returned'
 except Exception as error:
  remember(envelope,error)
 finally:
  if root is not None:
   if envelope['report'] is None and envelope['first_error'] is not None:
    try:
     raw=helper.logical_read(root,envelope['remote_result_path'],16777216)
     envelope['report']=json.loads(raw.decode('ascii'),object_pairs_hook=unique,parse_constant=nonfinite)
     require(canonical(envelope['report'])==raw,'Noncanonical durable result')
     envelope['report_origin']='durable_unattributed'
    except FileNotFoundError: pass
    except Exception as error: remember(envelope,error,'durable_result')
   try: staged_read(helper,root,adapter_pin)
   except Exception as error: remember(envelope,error,'staged_adapter')
   if parser_read:
    try: installed_read(helper,root,PINS[0])
    except Exception as error: remember(envelope,error,'installed:p0_capture')
   try: os.close(root)
   except Exception as error: remember(envelope,error,'root_close')
'''

_MAIN = r'''
def main():
 action,sources,bindings,adapter_pin=request()
 envelope={'schema':'app-motor-observe-action-v1','action':action,'run_id':RUN_ID,'source_sha256':SOURCE,
  'report':None,'report_origin':None,'remote_result_path':bindings['output']+'/'+action+'_result.json',
  'full_result_bytes':None,'full_result_sha256':None,'first_error':None,'postcheck_errors':[]}
 perform(action,sources,bindings,adapter_pin,envelope)
 if envelope['report'] is not None:
  full=canonical(envelope['report'])
  envelope['full_result_bytes']=len(full);envelope['full_result_sha256']=sha(full)
  if action=='upload': envelope['report']={key:value for key,value in envelope['report'].items() if key not in ('stdout','stderr')}
 raw=canonical(envelope)
 require(len(raw)<=65536,'Action reply exceeds bound')
 sys.stdout.write(raw.decode('ascii'))
main()
'''


def _bootstrap():
    original = legacy._BOOTSTRAP_SOURCE
    functions = {node.name: ast.get_source_segment(original, node)
                 for node in ast.parse(original).body if isinstance(node, ast.FunctionDef)}
    prefix = original[:original.index('def require(')]
    prefix = prefix[:prefix.index('PINS=')] + (
        "PINS=(('p0_capture',18880,'885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c'),)\n")
    prefix = prefix.replace('app-motor-observe-8f592937-run01', RUN_ID).replace(
        '8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36', SOURCE)
    request = functions['request'].replace(
        "('run_id','source_sha256','sources','bindings')",
        "('run_id','source_sha256','sources','bindings','adapter_pin')").replace(
        "roles=('helper','support','upload') if action=='upload' else ('helper','support')",
        "roles=('helper','support','upload')").replace(
        'return action,sources,bindings',
        "adapter_pin=payload['adapter_pin']\n keys(adapter_pin,('path','bytes','sha256'))\n"
        " require(adapter_pin==" + repr(dict(path=ADAPTER, bytes=ADAPTER_BYTES, sha256=ADAPTER_SHA)) +
        " and type(adapter_pin['bytes']) is int,'Wrong staged adapter pin')\n return action,sources,bindings,adapter_pin")
    source_check = "require(type(item['sha256']) is str and sha(item['source'].encode('utf-8'))==item['sha256'],'Inline source hash mismatch')"
    legacy._require(request.count(source_check) == 1, 'Legacy source-check seam changed')
    fixed_check = "\n  require(item['sha256']==" + repr(SOURCE_HASHES) + "[role],'Pinned inline source differs')"
    request = request.replace(source_check, source_check + fixed_check)
    common = ('require', 'canonical', 'sha', 'keys', 'unique', 'nonfinite', 'load',
              'error_record', 'remember', 'installed_read')
    return prefix + '\n\n'.join(functions[name] for name in common) + '\n' + request + _CAPTURE + _MAIN


_BOOTSTRAP_SOURCE = _bootstrap()
BOOTSTRAP = ('import base64,bz2\nexec(bz2.decompress(base64.b64decode(' + repr(
    base64.b64encode(bz2.compress(_BOOTSTRAP_SOURCE.encode(), 9)).decode()) + ')))')


def build_command(action, sources, bindings, adapter_pin):
    legacy._action(action)
    legacy._identity(action, bindings)
    legacy._keys(sources, SOURCE_HASHES)
    legacy._keys(adapter_pin, ('path', 'bytes', 'sha256'))
    legacy._require(adapter_pin == dict(path=ADAPTER, bytes=ADAPTER_BYTES, sha256=ADAPTER_SHA)
                    and type(adapter_pin['bytes']) is int, 'Wrong staged adapter pin')
    inline = {}
    for role, raw in sources.items():
        legacy._require(type(raw) is bytes and legacy._sha(raw) == SOURCE_HASHES[role],
                        'Changed inline source: ' + role)
        inline[role] = {'source': raw.decode('utf-8'), 'sha256': legacy._sha(raw)}
    payload = legacy._canonical(dict(run_id=RUN_ID, source_sha256=SOURCE, sources=inline,
                                     bindings=bindings, adapter_pin=adapter_pin))
    legacy._require(len(payload) <= legacy.PAYLOAD_LIMIT, 'Payload exceeds bound')
    compressed = bz2.compress(payload, 9)
    remote = ['/usr/bin/env', '-i', 'HOME=/home/arduino', 'USER=arduino', 'LOGNAME=arduino',
              'PATH=/usr/bin:/bin', 'LANG=C', 'LC_ALL=C', '/usr/bin/python3', '-I', '-B',
              '-c', BOOTSTRAP, action, legacy._sha(payload), base64.b64encode(compressed).decode()]
    if legacy._command_units(remote) + 1 > legacy.COMMAND_LIMIT:
        remote[-1] = 'b85:' + base64.b85encode(compressed).decode()
    legacy._require(legacy._command_units(remote) + 1 <= legacy.COMMAND_LIMIT,
                    'Windows command exceeds bound including NUL')
    return remote


def _plan():
    def flash(prefix, region):
        size, base = (263680, 0x08000000) if region == 'loader' else (95360, 0x08100000)
        return [(prefix + '.' + region + '.' + str(index), base + offset, min(65536, size - offset))
                for index, offset in enumerate(range(0, size, 65536))]
    samples = [(prefix + '.' + name, address, size) for prefix in ('first', 'second')
               for name, address, size in WINDOWS]
    return flash('before', 'loader') + flash('before', 'sketch') + samples + flash('after', 'sketch') + flash('after', 'loader')


def _capture(report):
    analysis = report['analysis']
    legacy._keys(analysis, ('schema', 'flash', 'snapshots', 'coherence', 'pre_sample_wait'))
    legacy._require(analysis['schema'] == 'app-motor-observe-capture-analysis-v1' and
                    analysis['coherence'] == 'UNPROVEN', 'Wrong analysis identity')
    legacy._keys(analysis['flash'], ('before_loader', 'before_sketch', 'after_loader', 'after_sketch'))
    legacy._require(all(value is True for value in analysis['flash'].values()), 'Flash was not verified')
    legacy._keys(report['counts'], ('commands', 'reads', 'requested_bytes'))
    for key, expected in (('commands', 26), ('reads', 26), ('requested_bytes', 727152)):
        legacy._integer(report['counts'][key], expected)
    legacy._reads(report['reads'], _plan())
    hashes = {item['name']: item['sha256'] for item in report['reads']}
    for name, digest in hashes.items():
        if name.startswith('before.'):
            legacy._require(digest == hashes['after.' + name[len('before.'):]], 'Flash bracket hash changed')
    snapshots = [item for item in report['reads'] if item['name'].startswith(('first.', 'second.'))]
    legacy._require(type(analysis['snapshots']) is list and
                    legacy._canonical(analysis['snapshots']) == legacy._canonical(snapshots), 'Wrong snapshots')
    wait = report['wait']
    legacy._keys(wait, ('requested_seconds', 'before', 'after'))
    legacy._integer(wait['requested_seconds'], 2)
    legacy._number(wait['before'])
    legacy._number(wait['after'])
    legacy._require(report['started_monotonic'] <= wait['before'] and
                    wait['after'] <= report['finished_monotonic'] and
                    wait['after'] - wait['before'] >= 2, 'Invalid sample separation')
    pre = analysis['pre_sample_wait']
    legacy._keys(pre, ('requested_seconds', 'before', 'after'))
    legacy._integer(pre['requested_seconds'], 30)
    legacy._number(pre['before'])
    legacy._number(pre['after'])
    legacy._require(report['started_monotonic'] <= pre['before'] <= pre['after'] <= wait['before']
                    and pre['after'] - pre['before'] >= 30, 'Invalid initial observation delay')


def validate_reply(action, reply):
    legacy._keys(reply, ('schema', 'action', 'run_id', 'source_sha256', 'report', 'report_origin',
                        'remote_result_path', 'full_result_bytes', 'full_result_sha256',
                        'first_error', 'postcheck_errors'))
    legacy._require(reply['report_origin'] == 'returned', 'Reply is not a successful returned result')
    projected = {key: value for key, value in reply.items() if key != 'report_origin'}
    _original_validate_reply(action, projected)


legacy._capture = _capture
# Save the original validator before supplying the sequence's adapted public seam.
_original_validate_reply = legacy.validate_reply


def run_actions(operations):
    previous = legacy.validate_reply
    legacy.validate_reply = validate_reply
    try:
        return legacy.run_actions(operations)
    finally:
        legacy.validate_reply = previous
