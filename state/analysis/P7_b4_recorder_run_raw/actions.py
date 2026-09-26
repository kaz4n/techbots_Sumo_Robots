# Frames one fixed B4 capture and read-only retrieval without an upload branch.
# Reuses pinned D212 bootstrap guards and binds local completion to exact sources.
# Independent focused fixtures cover framing, replies, retrieval and decoder calls.
import ast
import base64
import builtins
import bz2
import hashlib
import json
from pathlib import Path
import re
import shlex
import stat
import subprocess
from types import ModuleType, SimpleNamespace

ROOT = Path(__file__).absolute().parents[3]
RUN_ID = "b4-recorder-9044ebbb-capture01"
SOURCE = "9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a"
OUTPUT = "/home/arduino/sumox26_codex_build/" + RUN_ID
ADAPTER = OUTPUT + "-adapter/remote.py"
ADAPTER_BYTES = 9769
ADAPTER_SHA = "e28d01312742389737c0ca0d6914ab8593d59f93b1a67ac302029749f11b4189"
ADAPTER_PIN = {"path": ADAPTER, "bytes": ADAPTER_BYTES, "sha256": ADAPTER_SHA}
ADB = "C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe"
BOARD = "2629958581"
INLINE_PINS = {"helper":[33321,"8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8"],"support":[37525,"95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e"]}
HOST_INPUTS = {"validate_csv_bundle":[19324,"1c4781fdd0f77a610998644db610bf6adf5a2373d4f32f3ec7ca486185ff52f2"],"b4_recorder_capture":[9769,"e28d01312742389737c0ca0d6914ab8593d59f93b1a67ac302029749f11b4189"],"decode_b4_recorder":[11743,"43347b569098b78cbdbf32a1e4b06ebbbef245c4c57b91609fa38d8bb3cca8a3"],"decode_b4_capture":[10061,"1c0f75c001b8f66e9b3f5f4ed2be8472c8aaf1991265cfb6f91e4372043f6109"]}
BINDINGS = {"boot_id":"55c386b9-fe6d-4388-a7f4-1d91e0bb49d8","files":{"config":{"bytes":694,"path":"/home/arduino/sumox26-capture-tools/app-default-beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1/p0_mem_read.cfg","sha256":"89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339"},"loader":{"bytes":2303728,"path":"/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf","sha256":"39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd"},"openocd":{"bytes":14435552,"path":"/opt/openocd/bin/openocd","sha256":"04778a80c5c619ee4eef7505db91328f1d7e789107c496f2ddcf96d081f5b0ff"},"sketch":{"bytes":82912,"path":"/home/arduino/sumox26_codex_build/b4-app-m0-static01/build/app.ino.bin-zsk.bin","sha256":"84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28"},"swj":{"bytes":1148,"path":"/opt/openocd/share/openocd/scripts/target/swj-dp.tcl","sha256":"aad132008735bbafea3d18a304632c638f0fb99bfc19530c9f577eda2b10410a"}},"loader_image":{"bytes":263680,"sha256":"e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2"},"output":"/home/arduino/sumox26_codex_build/b4-recorder-9044ebbb-capture01","run_id":"b4-recorder-9044ebbb-capture01","schema":"fixed-b4-recorder-capture-v1","source_sha256":"9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a","uid":1000}
EXPECTED_IDENTITY = {"boot_id":"55c386b9-fe6d-4388-a7f4-1d91e0bb49d8","gid":1000,"home":"/home/arduino","machine":"aarch64","python":[3,13,5],"release":"6.16.7-g0dd6551ae96b","sysname":"Linux","uid":1000,"user":"arduino"}
PLAN = (("before.loader.0",134217728,65536),("before.loader.1",134283264,65536),("before.loader.2",134348800,65536),("before.loader.3",134414336,65536),("before.loader.4",134479872,1536),("before.sketch.0",135266304,65536),("before.sketch.1",135331840,17376),("before.lifecycle",537113200,120),("owner.0",536954120,16384),("owner.1",536970504,16384),("owner.2",536986888,16384),("owner.3",537003272,16384),("owner.4",537019656,16384),("owner.5",537036040,16384),("owner.6",537052424,16384),("owner.7",537068808,16384),("owner.8",537085192,16384),("owner.9",537101576,11744),("after.lifecycle",537113200,120),("after.sketch.0",135266304,65536),("after.sketch.1",135331840,17376),("after.loader.0",134217728,65536),("after.loader.1",134283264,65536),("after.loader.2",134348800,65536),("after.loader.3",134414336,65536),("after.loader.4",134479872,1536),)
_BOOTSTRAP_SOURCE = "\nimport base64,bz2,hashlib,json,os,re,sys,types\nRUN_ID='b4-recorder-9044ebbb-capture01'\nSOURCE='9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'\nPARENT='/home/arduino/sumox26_codex_build/'\nINSTALLED='/home/arduino/sumox26-capture-tools/runtime-a4d58b3cbac8/'\nPINS=(('p0_capture',18880,'885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c'),)\ndef require(ok,message):\n if not ok: raise ValueError(message)\n\ndef canonical(value):\n return (json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False)+'\\n').encode('ascii')\n\ndef sha(raw):\n return hashlib.sha256(raw).hexdigest()\n\ndef keys(value,names):\n require(type(value) is dict and set(value)==set(names),'Wrong object fields')\n\ndef unique(pairs):\n value={}\n for key,item in pairs:\n  require(key not in value,'Duplicate JSON key')\n  value[key]=item\n return value\n\ndef nonfinite(value):\n raise ValueError('Nonfinite JSON number')\n\ndef load(name,source,filename):\n module=types.ModuleType(name)\n module.__file__=filename\n sys.modules[name]=module\n exec(compile(source,filename,'exec'),module.__dict__)\n return module\n\ndef error_record(error):\n return {'type':type(error).__name__,'message':str(error)}\n\ndef remember(envelope,error,check=None):\n record=error_record(error)\n if envelope['first_error'] is None: envelope['first_error']=record\n if check is not None: envelope['postcheck_errors'].append({'check':check,**record})\n\ndef installed_read(helper,root,pin):\n name,size,digest=pin\n raw=helper.logical_read(root,INSTALLED+name+'.py',size)\n require(type(raw) is bytes and len(raw)==size and sha(raw)==digest,'Installed source mismatch: '+name)\n return raw.decode('utf-8')\ndef request():\n require(len(sys.argv)==4 and sys.flags.dont_write_bytecode and sys.dont_write_bytecode is True,'Expected action, hash, payload and Python -B')\n action,digest,token=sys.argv[1:]\n require(type(action) is str and action=='capture','Wrong action')\n require(re.fullmatch('[0-9a-f]{64}',digest) is not None,'Wrong payload digest')\n if token.startswith('b85:'):\n  compressed=base64.b85decode(token[4:])\n  require(base64.b85encode(compressed).decode('ascii')==token[4:],'Noncanonical base85')\n else:\n  compressed=base64.b64decode(token,validate=True)\n  require(base64.b64encode(compressed).decode('ascii')==token,'Noncanonical base64')\n decoder=bz2.BZ2Decompressor()\n raw=decoder.decompress(compressed,max_length=196609)\n require(len(raw)<=196608 and decoder.eof and not decoder.unused_data,'Invalid bounded BZ2 member')\n require(sha(raw)==digest,'Payload hash mismatch')\n payload=json.loads(raw.decode('ascii'),object_pairs_hook=unique,parse_constant=nonfinite)\n require(canonical(payload)==raw,'Noncanonical JSON')\n keys(payload,('run_id','source_sha256','sources','bindings','adapter_pin'))\n require(payload['run_id']==RUN_ID and payload['source_sha256']==SOURCE,'Wrong payload identity')\n sources=payload['sources']\n roles=('helper','support')\n keys(sources,roles)\n for role in roles:\n  item=sources[role]\n  keys(item,('source','sha256'))\n  require(type(item['source']) is str and item['source'],'Empty inline source')\n  require(type(item['sha256']) is str and sha(item['source'].encode('utf-8'))==item['sha256'],'Inline source hash mismatch')\n  require((len(item['source'].encode('utf-8')),item['sha256'])=={'helper': (33321, '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8'), 'support': (37525, '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e')}[role],'Pinned inline source differs')\n bindings=payload['bindings']\n require(type(bindings) is dict,'Wrong bindings type')\n fixed={'schema':'fixed-b4-recorder-capture-v1','run_id':RUN_ID,'source_sha256':SOURCE,'output':PARENT+RUN_ID}\n for name,value in fixed.items():\n  require(type(bindings.get(name)) is str and bindings[name]==value,'Wrong binding: '+name)\n adapter_pin=payload['adapter_pin']\n keys(adapter_pin,('path','bytes','sha256'))\n require(adapter_pin=={'bytes': 9769, 'path': '/home/arduino/sumox26_codex_build/b4-recorder-9044ebbb-capture01-adapter/remote.py', 'sha256': 'e28d01312742389737c0ca0d6914ab8593d59f93b1a67ac302029749f11b4189'} and type(adapter_pin['bytes']) is int,'Wrong adapter pin')\n return action,sources,bindings,adapter_pin\n\ndef staged_read(helper,root,pin):\n raw=helper.logical_read(root,pin['path'],pin['bytes'])\n require(type(raw) is bytes and len(raw)==pin['bytes'] and sha(raw)==pin['sha256'],'Staged adapter mismatch')\n return raw\n\ndef perform(sources,bindings,adapter_pin,envelope):\n root=None;helper=None;parser_read=False\n try:\n  helper=load('fixed_b4_capture_helper',sources['helper']['source'],'/__sumox__/helper.py')\n  root=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)\n  adapter=load('fixed_b4_capture_adapter',staged_read(helper,root,adapter_pin),adapter_pin['path'])\n  parser_read=True\n  parser_raw=installed_read(helper,root,PINS[0]).encode('utf-8')\n  dependencies=adapter.load_dependencies({'helper':sources['helper']['source'].encode('utf-8'),'capture':sources['support']['source'].encode('utf-8'),'p0':parser_raw})\n  envelope['report']=adapter.collect(dependencies,bindings=bindings)\n  envelope['report_origin']='returned'\n except Exception as error:\n  remember(envelope,error)\n finally:\n  if root is not None:\n   if envelope['report'] is None and envelope['first_error'] is not None:\n    try:\n     raw=helper.logical_read(root,envelope['remote_result_path'],65536)\n     envelope['report']=json.loads(raw.decode('ascii'),object_pairs_hook=unique,parse_constant=nonfinite)\n     require(canonical(envelope['report'])==raw,'Noncanonical durable result')\n     envelope['report_origin']='durable_unattributed'\n    except FileNotFoundError: pass\n    except Exception as error: remember(envelope,error,'durable_result')\n   try: staged_read(helper,root,adapter_pin)\n   except Exception as error: remember(envelope,error,'staged_adapter')\n   if parser_read:\n    try: installed_read(helper,root,PINS[0])\n    except Exception as error: remember(envelope,error,'installed:p0_capture')\n   try: os.close(root)\n   except Exception as error: remember(envelope,error,'root_close')\n\ndef main():\n action,sources,bindings,adapter_pin=request()\n envelope={'schema':'b4-recorder-action-v1','action':action,'run_id':RUN_ID,'source_sha256':SOURCE,\n  'report':None,'report_origin':None,'remote_result_path':bindings['output']+'/capture_result.json',\n  'full_result_bytes':None,'full_result_sha256':None,'first_error':None,'postcheck_errors':[]}\n perform(sources,bindings,adapter_pin,envelope)\n if envelope['report'] is not None:\n  full=canonical(envelope['report'])\n  envelope['full_result_bytes']=len(full);envelope['full_result_sha256']=sha(full)\n raw=canonical(envelope)\n require(len(raw)<=65536,'Action reply exceeds bound')\n sys.stdout.write(raw.decode('ascii'))\nmain()\n"
_RETRIEVAL_SOURCE = "EXPECTED={\"boot_id\":\"55c386b9-fe6d-4388-a7f4-1d91e0bb49d8\",\"gid\":1000,\"home\":\"/home/arduino\",\"machine\":\"aarch64\",\"python\":[3,13,5],\"release\":\"6.16.7-g0dd6551ae96b\",\"sysname\":\"Linux\",\"uid\":1000,\"user\":\"arduino\"}\nOUTPUT=\"/home/arduino/sumox26_codex_build/b4-recorder-9044ebbb-capture01\"\nRUN_ID=\"b4-recorder-9044ebbb-capture01\"\nSOURCE=\"9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a\"\nPLAN=((\"before.loader.0\",134217728,65536),(\"before.loader.1\",134283264,65536),(\"before.loader.2\",134348800,65536),(\"before.loader.3\",134414336,65536),(\"before.loader.4\",134479872,1536),(\"before.sketch.0\",135266304,65536),(\"before.sketch.1\",135331840,17376),(\"before.lifecycle\",537113200,120),(\"owner.0\",536954120,16384),(\"owner.1\",536970504,16384),(\"owner.2\",536986888,16384),(\"owner.3\",537003272,16384),(\"owner.4\",537019656,16384),(\"owner.5\",537036040,16384),(\"owner.6\",537052424,16384),(\"owner.7\",537068808,16384),(\"owner.8\",537085192,16384),(\"owner.9\",537101576,11744),(\"after.lifecycle\",537113200,120),(\"after.sketch.0\",135266304,65536),(\"after.sketch.1\",135331840,17376),(\"after.loader.0\",134217728,65536),(\"after.loader.1\",134283264,65536),(\"after.loader.2\",134348800,65536),(\"after.loader.3\",134414336,65536),(\"after.loader.4\",134479872,1536),)\nCOUNTS={'commands':26,'reads':26,'requested_bytes':852624}\nREPORT_KEYS=[\"schema\",\"run_id\",\"source_sha256\",\"status\",\"counts\",\"started_utc\",\"finished_utc\",\"started_monotonic\",\"finished_monotonic\",\"wait\",\"reads\",\"first_error\",\"postcheck_errors\",\"analysis\"]\n\nimport base64,bz2,hashlib,json,os,re,signal,sys,types\nsignal.alarm(60)\ndef require(ok,message):\n if not ok:raise ValueError(message)\ndef unique(pairs):\n value={}\n for key,item in pairs:\n  require(key not in value,'Duplicate key')\n  value[key]=item\n return value\ndef nonfinite(unused):raise ValueError('Nonfinite JSON')\ntoken=sys.argv[1];packed=base64.b64decode(token,validate=True)\nrequire(base64.b64encode(packed).decode()==token,'Noncanonical helper encoding')\ndecoder=bz2.BZ2Decompressor();source=decoder.decompress(packed,max_length=33322)\nrequire(len(source)==33321 and decoder.eof and not decoder.unused_data,'Invalid helper framing')\nrequire(hashlib.sha256(source).hexdigest()=='8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8','Helper changed')\nh=types.ModuleType('fixed_b4_retrieval_helper');h.__file__='/__sumox__/static_remote.py';exec(compile(source,h.__file__,'exec'),h.__dict__)\ndef read_bundle(h,fd):\n before=h.identity(fd)\n require(before==EXPECTED,'Identity changed')\n report_raw=h.logical_read(fd,OUTPUT+'/capture_result.json',65536)\n report=json.loads(report_raw.decode('ascii'),object_pairs_hook=unique,parse_constant=nonfinite)\n require(type(report) is dict and set(report)==set(REPORT_KEYS),'Wrong report fields')\n require(report['schema']=='b4-recorder-capture-result-v1' and report['run_id']==RUN_ID and report['source_sha256']==SOURCE and report['status']=='COLLECTED','Wrong complete report')\n require(report['first_error'] is None and report['postcheck_errors']==[] and report['wait'] is None,'Report failed')\n require(type(report['counts']) is dict and set(report['counts'])=={'commands','reads','requested_bytes'} and all(type(report['counts'][k]) is int and report['counts'][k]==v for k,v in COUNTS.items()),'Wrong counts')\n reads=report['reads'];require(type(reads) is list and len(reads)==26,'Wrong read count')\n for index,((name,address,size),row) in enumerate(zip(PLAN,reads)):\n  require(type(row) is dict and set(row)=={'name','address','bytes','sha256','file'},'Wrong read fields')\n  require(type(row['address']) is int and type(row['bytes']) is int and row['name']==name and row['address']==address and row['bytes']==size and row['file']=='{:02d}-{}.bin'.format(index,name),'Wrong fixed read')\n  require(type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256']) is not None,'Invalid read digest')\n pins=[{'path':OUTPUT+'/capture_result.json','bytes':len(report_raw),'sha256':hashlib.sha256(report_raw).hexdigest()}]\n pins += [{'path':OUTPUT+'/'+reads[i]['file'],'bytes':reads[i]['bytes'],'sha256':reads[i]['sha256']} for i in range(7,19)]\n rows=[]\n for pin in pins:\n  body=h.logical_read(fd,pin['path'],pin['bytes'])\n  require(len(body)==pin['bytes'] and hashlib.sha256(body).hexdigest()==pin['sha256'],'Result pin mismatch')\n  rows.append(dict(pin,data_base64=base64.b64encode(body).decode('ascii')))\n for pin in pins:\n  body=h.logical_read(fd,pin['path'],pin['bytes'])\n  require(len(body)==pin['bytes'] and hashlib.sha256(body).hexdigest()==pin['sha256'],'Closing result pin mismatch')\n after=h.identity(fd);require(after==before,'Closing identity changed')\n packet={'status':'FILE_ONLY_RESULTS_VERIFIED','identity_before':before,'identity_after':after,'files':rows,'closing_file_checks':13}\n return packet\nfd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)\nprimary=None\ntry:\n packet=read_bundle(h,fd)\nexcept BaseException as error:\n primary=error;raise\nfinally:\n try:os.close(fd)\n except BaseException:\n  if primary is None:raise\nraw=json.dumps(packet,separators=(',',':'),allow_nan=False)\nrequire(len(raw.encode())<=1048576,'Retrieval packet exceeds bound')\nprint(raw)\n"
ISOLATED = ["/usr/bin/env", "-i", "HOME=/home/arduino", "USER=arduino",
            "LOGNAME=arduino", "PATH=/usr/bin:/bin", "LANG=C", "LC_ALL=C",
            "/usr/bin/python3", "-I", "-B", "-c"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       allow_nan=False, separators=(",", ":")) + "\n").encode("ascii")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def keys(value, expected):
    require(type(value) is dict and set(value) == set(expected), "Wrong object fields")


def same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(same(left[k], right[k]) for k in right)
    if type(left) in (list, tuple):
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    return left == right


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


def _host():
    snapshots = {name: checked_source(ROOT / "tools" / (name + ".py"), pin[1])
                 for name, pin in HOST_INPUTS.items()}
    require(all(len(snapshots[name]) == pin[0] for name, pin in HOST_INPUTS.items()),
            "Host dependency size changed")
    modules = {}
    def bound_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "tools":
            require(level == 0 and len(fromlist) == 1 and fromlist[0] in modules,
                    "Unexpected private tools import")
            return SimpleNamespace(**modules)
        return builtins.__import__(name, globals, locals, fromlist, level)
    for name, raw in snapshots.items():
        module = ModuleType("_fixed_b4_" + name)
        module.__file__ = str(ROOT / "tools" / (name + ".py"))
        module.__dict__["__builtins__"] = dict(vars(builtins), __import__=bound_import)
        exec(compile(raw, module.__file__, "exec"), module.__dict__)
        modules[name] = module
    return modules["decode_b4_capture"]


def _command_units(remote):
    native = [ADB, "-s", BOARD, "shell", "-T", shlex.join(remote)]
    return len(subprocess.list2cmdline(native).encode("utf-16-le")) // 2 + 1


def _packed_program(source):
    return "import base64,bz2\nexec(bz2.decompress(base64.b64decode(" + repr(
        base64.b64encode(bz2.compress(source.encode(), 9)).decode()) + ")))"


def build_capture_command(sources, bindings):
    keys(sources, INLINE_PINS)
    require(same(bindings, BINDINGS), "Wrong fixed B4 binding")
    inline = {}
    for name, raw in sources.items():
        size, digest = INLINE_PINS[name]
        require(type(name) is str and type(raw) is bytes and len(raw) == size
                and sha(raw) == digest, "Pinned inline source differs: " + str(name))
        inline[name] = {"source": raw.decode("utf-8"), "sha256": digest}
    payload = canonical({"run_id": RUN_ID, "source_sha256": SOURCE, "sources": inline,
                         "bindings": bindings, "adapter_pin": ADAPTER_PIN})
    require(len(payload) <= 196608, "Payload exceeds bound")
    packed = bz2.compress(payload, 9)
    remote = ISOLATED + [_packed_program(_BOOTSTRAP_SOURCE), "capture", sha(payload),
                         base64.b64encode(packed).decode()]
    if _command_units(remote) > 30000:
        remote[-1] = "b85:" + base64.b85encode(packed).decode()
    require(_command_units(remote) <= 30000, "Windows command exceeds bound")
    return remote


def build_retrieval_command(helper_raw, expected_identity):
    size, digest = INLINE_PINS["helper"]
    require(type(helper_raw) is bytes and len(helper_raw) == size
            and sha(helper_raw) == digest, "Retrieval helper changed")
    require(same(expected_identity, EXPECTED_IDENTITY), "Retrieval identity differs")
    remote = ISOLATED + [_packed_program(_RETRIEVAL_SOURCE),
                         base64.b64encode(bz2.compress(helper_raw, 9)).decode()]
    require(_command_units(remote) <= 30000, "Windows retrieval command exceeds bound")
    return remote


def _validate_reads(report):
    rows = report["reads"]
    require(type(rows) is list and len(rows) == 26, "Wrong read count")
    for i, (row, (name, address, size)) in enumerate(zip(rows, PLAN)):
        keys(row, ("name", "address", "bytes", "sha256", "file"))
        expected = {"name": name, "address": address, "bytes": size,
                    "file": "{:02d}-{}.bin".format(i, name)}
        require(all(same(row[k], v) for k, v in expected.items()), "Wrong ordered read")
        require(type(row["sha256"]) is str
                and re.fullmatch("[0-9a-f]{64}", row["sha256"]), "Invalid read digest")


def _validate_analysis(report, decoder):
    value = report["analysis"]
    keys(value, ("schema", "flash", "owner", "lifecycle", "equalities", "coherence"))
    decoder._flash(report)
    require(value["schema"] == "b4-recorder-capture-analysis-v1"
            and value["coherence"] == "UNPROVEN", "Wrong analysis identity")
    keys(value["owner"], ("address", "bytes", "sha256", "chunks"))
    owner = value["owner"]
    require(all(type(owner[k]) is int and owner[k] == v for k, v in
                (("address", 536954120), ("bytes", 159200), ("chunks", 10)))
            and type(owner["sha256"]) is str
            and re.fullmatch("[0-9a-f]{64}", owner["sha256"]), "Wrong complete owner")
    keys(value["lifecycle"], ("before", "body", "after"))
    for row in value["lifecycle"].values():
        keys(row, ("epoch_token", "last_frame_token", "phase"))
        require(all(type(row[k]) is int and 0 <= row[k] < 2 ** bits for k, bits in
                    (("epoch_token", 64), ("last_frame_token", 64), ("phase", 8))),
                "Invalid lifecycle scalar")
    keys(value["equalities"], ("before_body", "body_after", "before_after"))
    for row in value["equalities"].values():
        keys(row, ("epoch_token", "last_frame_token", "phase"))
        require(all(type(v) is bool for v in row.values()), "Invalid equality fields")


def validate_capture_reply(reply):
    try:
        require(type(reply) is dict and len(canonical(reply)) <= 65536,
                "Capture reply exceeds bound")
        decoder = _host()
        decoder._envelope(reply)
        report = decoder._report(reply, canonical(reply["report"]))
        _validate_reads(report)
        _validate_analysis(report, decoder)
        return report
    except Exception as error:
        raise ValueError("Capture reply refused: " + str(error)) from error


def _retrieved_files(packet):
    keys(packet, ("status", "identity_before", "identity_after", "files",
                  "closing_file_checks"))
    require(packet["status"] == "FILE_ONLY_RESULTS_VERIFIED"
            and same(packet["identity_before"], EXPECTED_IDENTITY)
            and same(packet["identity_after"], EXPECTED_IDENTITY)
            and type(packet["closing_file_checks"]) is int
            and packet["closing_file_checks"] == 13, "Retrieval closure differs")
    rows = packet["files"]
    require(type(rows) is list and len(rows) == 13, "Wrong retrieved file count")
    names = ["capture_result.json"] + [
        "{:02d}-{}.bin".format(i, PLAN[i][0]) for i in range(7, 19)]
    sizes = [None] + [PLAN[i][2] for i in range(7, 19)]
    files, total = {}, 0
    for row, name, size in zip(rows, names, sizes):
        keys(row, ("path", "bytes", "sha256", "data_base64"))
        require(type(row["path"]) is str and row["path"] == OUTPUT + "/" + name
                and type(row["bytes"]) is int and 0 < row["bytes"] <= 65536
                and (size is None or row["bytes"] == size), "Retrieval path/size differs")
        token = row["data_base64"]
        require(type(token) is str and len(token) <= 87384, "Invalid encoded file size")
        body = base64.b64decode(token, validate=True)
        require(base64.b64encode(body).decode() == token and len(body) == row["bytes"]
                and type(row["sha256"]) is str and sha(body) == row["sha256"],
                "Retrieved bytes/hash differ")
        files[name] = body
        total += len(body)
    require(total <= 262144, "Retrieved files exceed total bound")
    return files


def decode_retrieval(packet, *, returned_raw, layout_raw):
    try:
        require(type(returned_raw) is bytes and len(returned_raw) <= 65536
                and type(layout_raw) is bytes and len(layout_raw) <= 65536,
                "Invalid local completion byte inputs")
        files = _retrieved_files(packet)
        require(len(canonical(packet)) <= 1048576, "Retrieval packet exceeds bound")
    except Exception as error:
        raise ValueError("Retrieval packet refused: " + str(error)) from error
    return _host().decode_capture(returned_raw, files=files, layout_raw=layout_raw)
