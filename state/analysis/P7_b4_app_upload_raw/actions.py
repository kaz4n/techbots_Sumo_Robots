# Composes only the fixed inhibited B4 upload through accepted bounded framing.
# Retains exact source and returned-report checks with no capture predecessor.
# Focused independent fixtures cover profile admission and one-shot failure closure.
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
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
RUN_ID = 'b4-app-m0-9044ebbb-load01'
PARENT = "/home/arduino/sumox26_codex_build/"
ADAPTER = '/home/arduino/sumox26_codex_build/b4-app-m0-9044ebbb-load01-adapter/remote.py'
ADAPTER_SHA = 'c2f0a4423839f9b3444c2949587486248d3a0af9578ae8188fd478bb55868b57'
ADAPTER_BYTES = 5115
SOURCE_HASHES = {'helper': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8', 'support': '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e', 'upload': 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1'}
BINDINGS = {'absent': ['/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/boards.local.txt', '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/platform.local.txt', '/home/arduino/.arduino15/packages/platform.txt', '/home/arduino/Arduino/hardware', '/home/arduino/openocd_gpiod.cfg', '/home/arduino/stm32u5x.cfg', '/home/arduino/stm32x5x_common.cfg', '/home/arduino/mem_helper.tcl', '/home/arduino/target/swj-dp.tcl', '/opt/openocd/mem_helper.tcl', '/opt/openocd/target/swj-dp.tcl', '/home/arduino/sumox26_codex_build/9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a/app/sketch.yaml', '/home/arduino/sumox26_codex_build/9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a/app/sketch.yml', '/home/arduino/sumox26_codex_build/9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a/app/sketch.json'], 'boot_id': '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8', 'directories': {'/home/arduino/.arduino15/packages': ['SiliconLabs', 'arduino', 'builtin', 'zephyr'], '/home/arduino/.arduino15/packages/arduino/hardware/zephyr': ['1.0.0'], '/home/arduino/.arduino15/packages/arduino/tools/remoteocd': ['0.1.1']}, 'files': {'adb': {'bytes': 7916376, 'path': '/home/arduino/.arduino15/packages/arduino/tools/adb/32.0.0/adb', 'sha256': 'ed62ac1ec90ef305cf0c8fa317284cd75b7cda88ecd8dbdd097044101072d164'}, 'boards': {'bytes': 6101, 'path': '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/boards.txt', 'sha256': 'bd4f03904d8fe16bf845baf09d0435e79f5a46c6e6a4f445f3ee592994652b84'}, 'cli': {'bytes': 34651734, 'path': '/usr/bin/arduino-cli', 'sha256': 'b878632298958d61fd1eb19e70ac5d2e803d83db8930bc72dc6915eee6e8f433'}, 'common_config': {'bytes': 8468, 'path': '/opt/openocd/stm32x5x_common.cfg', 'sha256': '139a2c4167e4fc649ab0057560858e03a24dcafeb5b0b3a3bcb7b9373e0869e4'}, 'flash_config': {'bytes': 680, 'path': '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/variants/arduino_uno_q_stm32u585xx/flash_sketch.cfg', 'sha256': '38706cee1f9ff2e53364a47129d1c1aea9bb9687ed26d7d70b4a9f9bc5bca60c'}, 'gpio_config': {'bytes': 194, 'path': '/opt/openocd/openocd_gpiod.cfg', 'sha256': '58c0c341ba2a0c758bb044683884fb4af01ff6c9cf292bec6b2115c44f7ff836'}, 'index': {'bytes': 1691790, 'path': '/home/arduino/.arduino15/package_index.json', 'sha256': '3cb9691dc81453f0ad429c721af4aaf87ff18d9431408f4cd75c8bb479419c3e'}, 'installed': {'bytes': 303397, 'path': '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/installed.json', 'sha256': '985d3ba102ebf440eca4fb9a9f767b35134e3d827919224bb7635b4b106f86f9'}, 'loader': {'bytes': 2303728, 'path': '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf', 'sha256': '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'}, 'mem_helper': {'bytes': 1021, 'path': '/opt/openocd/share/openocd/scripts/mem_helper.tcl', 'sha256': '01794a37e9a8bdc20e2304ee64e9d70549c0872f5f6c40fa032a165bcbba1fd2'}, 'openocd': {'bytes': 14435552, 'path': '/opt/openocd/bin/openocd', 'sha256': '04778a80c5c619ee4eef7505db91328f1d7e789107c496f2ddcf96d081f5b0ff'}, 'platform': {'bytes': 20947, 'path': '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/platform.txt', 'sha256': 'd4c824fceb2f4cf0057da4df3235d3aee195bbbd71f59a48d344c818fcd5e638'}, 'raw': {'bytes': 82896, 'path': '/home/arduino/sumox26_codex_build/b4-app-m0-static01/build/app.ino.bin', 'sha256': '6fcad2f09c90bbc7dd72760e7a794305811d042a9d2e578e03d5154cc368a471'}, 'remoteocd': {'bytes': 6451057, 'path': '/home/arduino/.arduino15/packages/arduino/tools/remoteocd/0.1.1/remoteocd', 'sha256': '2a3f820b867d113a82a86470f2caa128bc15b52303ad4ce0a5cbd62002cb2b60'}, 'sketch': {'bytes': 82912, 'path': '/home/arduino/sumox26_codex_build/b4-app-m0-static01/build/app.ino.bin-zsk.bin', 'sha256': '84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28'}, 'swj': {'bytes': 1148, 'path': '/opt/openocd/share/openocd/scripts/target/swj-dp.tcl', 'sha256': 'aad132008735bbafea3d18a304632c638f0fb99bfc19530c9f577eda2b10410a'}, 'target_config': {'bytes': 1762, 'path': '/opt/openocd/stm32u5x.cfg', 'sha256': '8c0ffc41eadd0593168b825d60d6736329c08974c047fdac722fabb93c0ee46a'}}, 'output': '/home/arduino/sumox26_codex_build/b4-app-m0-9044ebbb-load01-upload', 'run_id': 'b4-app-m0-9044ebbb-load01', 'schema': 'fixed-b4-app-upload-v1', 'source_sha256': '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a', 'uid': 1000}
EXPECTED_IDENTITY = {'boot_id': '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8', 'gid': 1000, 'home': '/home/arduino', 'machine': 'aarch64', 'python': [3, 13, 5], 'release': '6.16.7-g0dd6551ae96b', 'sysname': 'Linux', 'uid': 1000, 'user': 'arduino'}

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
    module = types.ModuleType('_ordinary_app_actions_legacy')
    module.__file__ = str(ROOT / LEGACY)
    source = raw.decode('utf-8').replace('motor-fault-action-v1', 'b4-app-upload-action-v1').replace('motor-fault-', 'b4-app-')
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    module.RUN_ID, module.SOURCE = RUN_ID, SOURCE
    return module

legacy = _legacy()

def same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return set(left) == set(right) and all(same(k, next(k2 for k2 in right if k2 == k))
            and same(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    return left == right

_BOOTSTRAP_SOURCE = "\nimport base64,bz2,hashlib,json,os,re,sys,types\nRUN_ID='b4-app-m0-9044ebbb-load01'\nSOURCE='9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'\nPARENT='/home/arduino/sumox26_codex_build/'\ndef require(ok,message):\n if not ok: raise ValueError(message)\n\ndef canonical(value):\n return (json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False)+'\\n').encode('ascii')\n\ndef sha(raw):\n return hashlib.sha256(raw).hexdigest()\n\ndef keys(value,names):\n require(type(value) is dict and set(value)==set(names),'Wrong object fields')\n\ndef unique(pairs):\n value={}\n for key,item in pairs:\n  require(key not in value,'Duplicate JSON key')\n  value[key]=item\n return value\n\ndef nonfinite(value):\n raise ValueError('Nonfinite JSON number')\n\ndef load(name,source,filename):\n module=types.ModuleType(name)\n module.__file__=filename\n sys.modules[name]=module\n exec(compile(source,filename,'exec'),module.__dict__)\n return module\n\ndef error_record(error):\n return {'type':type(error).__name__,'message':str(error)}\n\ndef remember(envelope,error,check=None):\n record=error_record(error)\n if envelope['first_error'] is None: envelope['first_error']=record\n if check is not None: envelope['postcheck_errors'].append({'check':check,**record})\ndef same(left, right):\n    if type(left) is not type(right):\n        return False\n    if type(left) is dict:\n        return set(left) == set(right) and all(same(k, next(k2 for k2 in right if k2 == k))\n            and same(left[k], right[k]) for k in left)\n    if type(left) is list:\n        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))\n    return left == right\n\ndef request():\n require(len(sys.argv)==4 and sys.flags.dont_write_bytecode and sys.dont_write_bytecode is True,'Expected action, hash, payload and Python -B')\n action,digest,token=sys.argv[1:]\n require(type(action) is str and action == 'upload','Wrong action')\n require(re.fullmatch('[0-9a-f]{64}',digest) is not None,'Wrong payload digest')\n if token.startswith('b85:'):\n  compressed=base64.b85decode(token[4:])\n  require(base64.b85encode(compressed).decode('ascii')==token[4:],'Noncanonical base85')\n else:\n  compressed=base64.b64decode(token,validate=True)\n  require(base64.b64encode(compressed).decode('ascii')==token,'Noncanonical base64')\n decoder=bz2.BZ2Decompressor()\n raw=decoder.decompress(compressed,max_length=196609)\n require(len(raw)<=196608 and decoder.eof and not decoder.unused_data,'Invalid bounded BZ2 member')\n require(sha(raw)==digest,'Payload hash mismatch')\n payload=json.loads(raw.decode('ascii'),object_pairs_hook=unique,parse_constant=nonfinite)\n require(canonical(payload)==raw,'Noncanonical JSON')\n keys(payload,('run_id','source_sha256','sources','bindings','adapter_pin'))\n require(payload['run_id']==RUN_ID and payload['source_sha256']==SOURCE,'Wrong payload identity')\n sources=payload['sources']\n roles=('helper','support','upload')\n keys(sources,roles)\n for role in roles:\n  item=sources[role]\n  keys(item,('source','sha256'))\n  require(type(item['source']) is str and item['source'],'Empty inline source')\n  require(type(item['sha256']) is str and sha(item['source'].encode('utf-8'))==item['sha256'],'Inline source hash mismatch')\n  require(item['sha256']=={'helper': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8', 'support': '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e', 'upload': 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1'}[role],'Pinned inline source differs')\n bindings=payload['bindings']\n require(type(bindings) is dict,'Wrong bindings type')\n fixed={'schema':'fixed-b4-app-'+action+'-v1','run_id':RUN_ID,'source_sha256':SOURCE,'output':PARENT+RUN_ID+'-'+action}\n for name,value in fixed.items():\n  require(type(bindings.get(name)) is str and bindings[name]==value,'Wrong binding: '+name)\n require(sha(canonical(bindings))=='2faf9ab12b685ec07a556aa63c8dd68d380ba6efe4e3f6b7d5f246b848441a41','Wrong fixed upload bindings')\n adapter_pin=payload['adapter_pin']\n require(same(adapter_pin,{'path': '/home/arduino/sumox26_codex_build/b4-app-m0-9044ebbb-load01-adapter/remote.py', 'bytes': 5115, 'sha256': 'c2f0a4423839f9b3444c2949587486248d3a0af9578ae8188fd478bb55868b57'}),'Wrong staged adapter pin')\n return action,sources,bindings,adapter_pin\ndef staged_read(helper,root,pin):\n raw=helper.logical_read(root,pin['path'],pin['bytes'])\n require(type(raw) is bytes and len(raw)==pin['bytes'] and sha(raw)==pin['sha256'],'Staged adapter mismatch')\n return raw\n\ndef perform(action,sources,bindings,adapter_pin,envelope):\n root=None\n try:\n  helper=load('fixed_b4_upload_helper',sources['helper']['source'],'/__sumox__/helper.py')\n  root=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)\n  adapter=load('fixed_b4_upload_adapter',staged_read(helper,root,adapter_pin),adapter_pin['path'])\n  dependencies=adapter.load_dependencies({role:sources[key]['source'].encode('utf-8') for role,key in (('helper','helper'),('capture','support'),('upload','upload'))})\n  envelope['report']=adapter.upload(dependencies,bindings=bindings)\n  envelope['report_origin']='returned'\n except Exception as error:\n  remember(envelope,error)\n finally:\n  if root is not None:\n   if envelope['report'] is None:\n    try:\n     raw=helper.logical_read(root,envelope['remote_result_path'],16777216)\n     envelope['report']=json.loads(raw.decode('ascii'),object_pairs_hook=unique,parse_constant=nonfinite)\n     require(canonical(envelope['report'])==raw,'Noncanonical durable result')\n     envelope['report_origin']='durable_unattributed'\n    except FileNotFoundError: pass\n    except Exception as error: remember(envelope,error,'durable_result')\n   try: staged_read(helper,root,adapter_pin)\n   except Exception as error: remember(envelope,error,'staged_adapter')\n   try: os.close(root)\n   except Exception as error: remember(envelope,error,'root_close')\n\ndef main():\n action,sources,bindings,adapter_pin=request()\n envelope={'schema':'b4-app-upload-action-v1','action':action,'run_id':RUN_ID,'source_sha256':SOURCE,\n  'report':None,'report_origin':None,'remote_result_path':bindings['output']+'/'+action+'_result.json',\n  'full_result_bytes':None,'full_result_sha256':None,'first_error':None,'postcheck_errors':[]}\n perform(action,sources,bindings,adapter_pin,envelope)\n if envelope['report'] is not None:\n  full=canonical(envelope['report'])\n  envelope['full_result_bytes']=len(full);envelope['full_result_sha256']=sha(full)\n  envelope['report']={key:value for key,value in envelope['report'].items() if key not in ('stdout','stderr')}\n raw=canonical(envelope)\n require(len(raw)<=65536,'Action reply exceeds bound')\n sys.stdout.write(raw.decode('ascii'))\nmain()\n"
BOOTSTRAP = "import base64,bz2\nexec(bz2.decompress(base64.b64decode('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')))"

def build_command(action, sources, bindings, adapter_pin):
    legacy._require(type(action) is str and action == 'upload', 'Only upload is permitted')
    legacy._require(same(bindings, BINDINGS), 'Wrong fixed upload bindings')
    legacy._identity(action, bindings)
    legacy._keys(sources, SOURCE_HASHES)
    legacy._keys(adapter_pin, ('path', 'bytes', 'sha256'))
    legacy._require(same(adapter_pin, dict(path=ADAPTER, bytes=ADAPTER_BYTES, sha256=ADAPTER_SHA)),
                    'Wrong staged adapter pin')
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

_original_validate_reply = legacy.validate_reply

def validate_reply(action, reply):
    legacy._require(type(action) is str and action == 'upload', 'Only upload is permitted')
    legacy._keys(reply, ('schema', 'action', 'run_id', 'source_sha256', 'report', 'report_origin',
                        'remote_result_path', 'full_result_bytes', 'full_result_sha256',
                        'first_error', 'postcheck_errors'))
    legacy._require(reply['report_origin'] == 'returned', 'Reply is not a successful returned result')
    projected = {key: value for key, value in reply.items() if key != 'report_origin'}
    _original_validate_reply(action, projected)

def run_actions(operations):
    legacy._keys(operations, ('local', 'prerequisites', 'intent', 'upload', 'finish'))
    legacy._require(all(callable(operation) for operation in operations.values()),
             'Expected five callable operations')
    report = {'schema': 'b4-app-upload-sequence-v1', 'status': 'FAILED',
              'upload': None, 'upload_attempts': 0, 'first_error': None, 'postcheck_errors': []}
    try:
        for action in ('upload',):
            operations['local']()
            operations['prerequisites']()
            predecessor = None
            operations['intent'](action, predecessor)
            report[action + '_attempts'] += 1
            report[action] = operations[action]()
            validate_reply(action, report[action])
    except Exception as error:
        legacy._remember(report, error)
    for check in ('local', 'prerequisites'):
        try:
            operations[check]()
        except Exception as error:
            legacy._remember(report, error, check)
    if report['first_error'] is None and not report['postcheck_errors']:
        report['status'] = 'COMPLETED'
    try:
        operations['finish'](report)
    except Exception as error:
        report['status'] = 'FAILED'
        legacy._remember(report, error, 'finish')
        error.sequence_result = report
        raise
    return report
