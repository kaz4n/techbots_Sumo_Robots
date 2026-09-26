# Compiles the existing ordinary application in one fixed inhibited B4 profile.
# Reuses the checked D208 loader and lifecycle with privately bound snapshot policy.
# Tested by independent D214 fixtures before any separately admitted native use.
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types

ROOT = Path(__file__).absolute().parents[1]
PREDECESSOR = 'tools/compile_ordinary_app_static.py'
ORIGINALS = {'tools/compile_ordinary_app_static.py': (26136, '40b5c765c01bc1749f6ea4534a4b7f274b681b5fa9295ab6f0c57fbf94d66a89')}
PROJECTED = (35477, '06c42406478eb7222364c2cc97a5fcc17154934e8234fda266cf6340c86180e4')
PROFILE_SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
B4_POLICY = 'tools/b4_app_static_policy.py'
BUNDLE_PATHS = {'helper': 'state/analysis/P7_static_link_probe_raw/static_remote.py', 'policy': 'tools/b4_app_static_policy.py', 'adapter': 'tools/app_motor_fault_static_policy.py', 'common': 'tools/app_build_policy.py', 'static_policy': 'state/analysis/P7_static_link_probe_raw/static_policy.py', 'reference': 'state/analysis/P7_static_link_probe_raw/static_reference.json', 'extension': 'state/analysis/P7_static_link_probe_raw/static_native_artifacts.py', 'base': 'state/analysis/P7_static_link_probe_raw/static_artifacts.py'}
SNAPSHOT_PATHS = {'adapter': 'tools/app_motor_fault_static_policy.py', 'common': 'tools/app_build_policy.py', 'static_policy': 'state/analysis/P7_static_link_probe_raw/static_policy.py', 'reference': 'state/analysis/P7_static_link_probe_raw/static_reference.json', 'extension': 'state/analysis/P7_static_link_probe_raw/static_native_artifacts.py'}
EXTRA_PINS = {'tools/compile_ordinary_app_static.py': '40b5c765c01bc1749f6ea4534a4b7f274b681b5fa9295ab6f0c57fbf94d66a89', 'tools/b4_app_compile_remote.py': '7dc788cbfb92688d3b1a2343f673da1bae3fa3ade1df5836ae437c013750b2d3', 'tools/b4_app_static_policy.py': 'aadccdbb0a92338a90a789251f691a42e029c7f73b312b638b85d04c5d2d4ddf', 'state/analysis/P7_b4_app_compile_contract.md': '76ba6262b2bbdf8ec65359c98488e66befae664d64d5a125c2de65480dda5c06', 'state/analysis/P7_b4_app_policy_contract.md': '1d6ffa2f49ba5a7925e1fbfc70a80a73a22dc0b5cc04a936b318eb97159d52c7', 'state/analysis/P7_ordinary_app_static_compile_contract.md': '06cd96f1c84fb50368050344853e4f5dfe0540a2d9a95b43def853b402b87f5d'}
REQUIRED = {'tools/compile_ordinary_app_static.py', 'state/analysis/P7_static_link_probe_raw/static_reference.json', 'state/analysis/P7_static_link_probe_raw/static_native_artifacts.py', 'state/analysis/P7_static_startup_raw/cli_initialization_inventory.json', 'tools/match_deploy.py', 'tools/compile_b4_app_static.py', 'state/analysis/P7_ordinary_app_static_compile_contract.md', 'state/analysis/P7_static_startup_raw/cli_builtin_files_inventory.json', 'state/analysis/P7_b4_app_compile_contract.md', 'state/analysis/P7_static_link_probe_raw/static_remote.py', 'state/analysis/P7_b4_app_policy_contract.md', 'state/analysis/P7_motor_fault_raw/compile_motor_fault.py', 'tools/compile_app_motor_fault.py', 'state/analysis/P7_static_link_probe_raw/static_policy.py', 'tools/b4_app_static_policy.py', 'state/analysis/P7_static_link_probe_raw/static_artifacts.py', 'tools/board_tool.py', 'state/analysis/P7_static_startup_raw/capture_remote.py', 'tools/app_build_policy.py', 'tools/app_motor_fault_compile_remote.py', 'tools/app_motor_fault_static_policy.py', 'state/analysis/P7_current_app_compile_raw/compile_current_app.py', 'tools/app_build_commands.json', 'tools/app_build_pins.json', 'tools/b4_app_compile_remote.py'}
REPLACEMENTS = (
    (b"CALLER = 'tools/compile_ordinary_app_static.py'", b"CALLER = 'tools/compile_b4_app_static.py'", 1),
    (b"REMOTE_HELPER = 'tools/app_motor_fault_compile_remote.py'", b"REMOTE_HELPER = 'tools/b4_app_compile_remote.py'", 1),
    (b'state/analysis/P7_ordinary_app_static_compile_contract.md', b'state/analysis/P7_b4_app_compile_contract.md', 1),
    (b'state/analysis/P7_ordinary_app_static_compile_raw', b'state/analysis/P7_b4_app_compile_raw', 1),
    (b'ordinary-app-static', b'b4-app-m0-static', 6),
    (b"FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'", b"FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_B4_STAND=1 -DSUMOX_P3_DRIVE_TEST=0 -DSUMOX_P3_TURN_TRIAL=0 -DSUMOX_P3_STOP_TRIAL=0 -DSUMOX_P4_REACTIVE=0 -DSUMOX_TIMING_EVIDENCE=0 -DSUMOX_P5_ABORT_TIMING=0 -DSUMOX_MOTOR_FAULT_PROBE=0'", 1),
    (b"require(source == value['source_sha256'], 'Staged source digest changed')", b"require(source == value['source_sha256'] == PROFILE_SOURCE, 'Staged source digest changed')", 1),
    (b'    def static_policy(self):\n        self.local()\n        return self.base.module_from(self.root, ADAPTER, project_adapter(self.code[ADAPTER]))', b'    def static_policy(self):\n        self.local()\n        policy = self.base.module_from(self.root, B4_POLICY, self.code[B4_POLICY])\n        snapshots = {path: self.code[path] for path in SNAPSHOT_PATHS.values()}\n        return types.SimpleNamespace(\n            validate_preflight=lambda text, *, build_path, data_dir:\n                policy.validate_preflight(text, build_path=build_path, data_dir=data_dir,\n                                          motors_allowed=0, snapshots=snapshots),\n            validate_compile_result=lambda text, *, build_path, data_dir:\n                policy.validate_compile_result(text, build_path=build_path, data_dir=data_dir,\n                                               motors_allowed=0, snapshots=snapshots))', 1),
    (b'        sources = dict(helper=self.code[READER], adapter=project_adapter(self.code[ADAPTER]),\n                       extension=self.code[EXTENSION], base=self.code[BASE_ARTIFACTS])', b'        sources = {name: self.code[path] for name, path in BUNDLE_PATHS.items()}', 1),
    (b'project_remote(self.code[REMOTE_HELPER])', b'self.code[REMOTE_HELPER]', 2),
    (b"'artifact_sha256', 'validator_report'), 'Invalid diagnostic layout fields')", b"'artifact_sha256', 'validator_report', 'motors_allowed'), 'Invalid diagnostic layout fields')", 1),
    (b"value['status'] == 'STATIC_ORDINARY_APP_LAYOUT_PACKAGE_PASS' and", b"value['status'] == 'STATIC_B4_APP_LAYOUT_PACKAGE_PASS' and\n                type(value['motors_allowed']) is int and value['motors_allowed'] == 0 and", 1),
    (b'        self.executor = self.board = self.receipt = self.artifact_receipt = None', b'        self.executor = self.board = self.receipt = self.artifact_receipt = None\n        self.artifact_sources_attempted, self.artifact_sources_identity = False, None', 1),
    (b"        require(self.compiler_calls == self.query_calls == 1, 'Missing checked compile/query')\n        self.observe_artifacts()", b"        require(self.compiler_calls == self.query_calls == 1, 'Missing checked compile/query')\n        self.prepare_artifact_sources()\n        self.observe_artifacts()", 1),
    (b"    def artifact_program(self):\n        sources = {name: self.code[path] for name, path in BUNDLE_PATHS.items()}\n        payload = dict(source=self.code[REMOTE_HELPER].decode('utf-8'),\n            bundle={name: raw.decode('utf-8') for name, raw in sources.items()})\n        raw = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode()\n        require(len(raw) <= 262144, 'Artifact source payload exceeds bound')\n        token = base64.b64encode(zlib.compress(raw, 9)).decode()\n        program = self.preamble() + 'token=' + repr(token) + '\\nexpected=' + repr(sha(raw)) + '\\n'\n        program += 'source_sha=' + repr(sha(self.code[REMOTE_HELPER])) + '\\n'\n        return program + '''import base64,zlib,types\npacked=base64.b64decode(token,validate=True)\nif base64.b64encode(packed).decode()!=token:raise ValueError('Noncanonical source token')\ndecoder=zlib.decompressobj();raw=decoder.decompress(packed,262145)\nif len(raw)>262144 or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:raise ValueError('Invalid compressed sources')\nif hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Source payload changed')\npayload=json.loads(raw);source=payload['source'].encode('utf-8')\nif hashlib.sha256(source).hexdigest()!=source_sha:raise ValueError('Artifact helper changed')\nmodule=types.ModuleType('_sumox_d188_observation')\nexec(compile(source,'<checked-d188-artifacts>','exec'),module.__dict__)\nbundle={name:value.encode('utf-8') for name,value in payload['bundle'].items()}\nresult=module.inspect_artifacts(REMOTE+'/build',REMOTE+'/artifacts',bundle)\ntext=json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False)\nif len(text.encode())>1048576:raise ValueError('Artifact response exceeds bound')\nprint(text)\n'''", b"    def _artifact_payload(self):\n        sources = {name: self.code[path] for name, path in BUNDLE_PATHS.items()}\n        payload = dict(source=self.code[REMOTE_HELPER].decode('utf-8'),\n            bundle={name: raw.decode('utf-8') for name, raw in sources.items()})\n        raw = json.dumps(payload, separators=(',', ':'), sort_keys=True).encode()\n        require(len(raw) <= 262144, 'Artifact source payload exceeds bound')\n        packed = zlib.compress(raw, 9)\n        require(16384 < len(packed) <= 32768, 'Artifact compressed source bound differs')\n        return raw, packed\n\n    def artifact_source_program(self, action, *, token='', previous=None):\n        require(action in ('first', 'second', 'read', 'partial'), 'Unexpected artifact source action')\n        if action == 'partial':\n            require(token == '' and previous is None, 'Partial observation has transfer state')\n            values = dict(ACTION=action, TOKEN='', PREVIOUS=None,\n                          PACKED_SIZE=0, PACKED_SHA='', FIRST_SHA='', SECOND_SHA='')\n        else:\n            raw, packed = self._artifact_payload()\n            values = dict(ACTION=action, TOKEN=token, PREVIOUS=previous,\n                PACKED_SIZE=len(packed), PACKED_SHA=sha(packed),\n                FIRST_SHA=sha(packed[:16384]), SECOND_SHA=sha(packed[16384:]))\n        return self.preamble() + ''.join(name + '=' + repr(value) + '\\n'\n                                        for name, value in values.items()) + ARTIFACT_SOURCE_IO\n\n    def checked_source_reply(self, text, size, digest):\n        value = self.base.decode(text)\n        keys(value, ('identity', 'sha256'), 'Invalid artifact source reply')\n        identity = value['identity']\n        require(type(identity) is list and len(identity) == 9 and\n                all(type(item) is int and 0 <= item <= 0xffffffffffffffff for item in identity) and\n                identity[2:7] == [stat.S_IFREG | 0o600, 1, 1000, 1000, size] and\n                value['sha256'] == digest, 'Artifact source identity or hash differs')\n        return value\n\n    def prepare_artifact_sources(self):\n        require(not self.artifact_sources_attempted, 'Artifact source preparation already attempted')\n        self.artifact_sources_attempted = True\n        self.local()\n        raw, packed = self._artifact_payload()\n        previous = None\n        for action, chunk, size, digest in (\n                ('first', packed[:16384], 16384, sha(packed[:16384])),\n                ('second', packed[16384:], len(packed), sha(packed))):\n            token = base64.b64encode(chunk).decode()\n            program = self.artifact_source_program(action, token=token, previous=previous)\n            reply, _ = self.direct(program + 'print(json.dumps(record))\\n', 'artifact-source-' + action)\n            require(not reply.stderr, 'Artifact source transfer stderr')\n            previous = self.checked_source_reply(reply.stdout, size, digest)\n        self.artifact_sources_identity = previous\n\n    def check_artifact_sources(self):\n        require(self.artifact_sources_attempted, 'Artifact source preparation was not attempted')\n        partial = self.artifact_sources_identity is None\n        program = self.artifact_source_program('partial' if partial else 'read',\n                                               previous=self.artifact_sources_identity)\n        reply, _ = self.direct(program + 'print(json.dumps(record))\\n', 'artifact-sources-final')\n        require(not reply.stderr, 'Artifact source closing stderr')\n        require(not partial, 'Incomplete artifact source preparation')\n        raw, packed = self._artifact_payload()\n        value = self.checked_source_reply(reply.stdout, len(packed), sha(packed))\n        require(value == self.artifact_sources_identity, 'Artifact source closing identity differs')\n\n    def artifact_program(self):\n        require(self.artifact_sources_attempted and self.artifact_sources_identity is not None,\n                'Artifact sources were not prepared')\n        raw, packed = self._artifact_payload()\n        program = self.artifact_source_program('read', previous=self.artifact_sources_identity)\n        program += 'expected=' + repr(sha(raw)) + '\\n'\n        program += 'source_sha=' + repr(sha(self.code[REMOTE_HELPER])) + '\\n'\n        return program + '''import base64,zlib,types\ndecoder=zlib.decompressobj();raw=decoder.decompress(packed,262145)\nif len(raw)>262144 or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:raise ValueError('Invalid compressed sources')\nif hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Source payload changed')\npayload=json.loads(raw);source=payload['source'].encode('utf-8')\nif hashlib.sha256(source).hexdigest()!=source_sha:raise ValueError('Artifact helper changed')\nmodule=types.ModuleType('_sumox_d188_observation')\nexec(compile(source,'<checked-d188-artifacts>','exec'),module.__dict__)\nbundle={name:value.encode('utf-8') for name,value in payload['bundle'].items()}\nresult=module.inspect_artifacts(REMOTE+'/build',REMOTE+'/artifacts',bundle)\ntext=json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False)\nif len(text.encode())>1048576:raise ValueError('Artifact response exceeds bound')\nprint(text)\n'''", 1),
    (b"def closing(self, report, primary):\n        primary = self.base.CompileCurrent.closing(self, report, primary)\n        if self.artifact_receipt is not None:\n            try:\n                self.observe_artifacts(final=True)\n                row = dict(name='artifacts', status='PASS', error=None)\n            except Exception as error:\n                primary = primary or error\n                row = dict(name='artifacts', status='FAILED', error=self.base.error_value(error))\n            report['final_checks'].append(row)\n        return primary", b"def closing(self, report, primary):\n        primary = self.base.CompileCurrent.closing(self, report, primary)\n        if self.artifact_receipt is not None:\n            try:\n                self.observe_artifacts(final=True)\n                row = dict(name='artifacts', status='PASS', error=None)\n            except Exception as error:\n                primary = primary or error\n                row = dict(name='artifacts', status='FAILED', error=self.base.error_value(error))\n            report['final_checks'].append(row)\n        if self.artifact_sources_attempted:\n            try:\n                self.check_artifact_sources()\n                row = dict(name='artifact_sources', status='PASS', error=None)\n            except Exception as error:\n                primary = primary or error\n                row = dict(name='artifact_sources', status='FAILED', error=self.base.error_value(error))\n            report['final_checks'].append(row)\n        return primary", 1),
)


ARTIFACT_SOURCE_IO = "def artifact_source_stamp(info):\n return [info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_uid,info.st_gid,info.st_size,info.st_mtime_ns,info.st_ctime_ns]\ndef artifact_source_check(ok,message):\n if not ok:raise ValueError(message)\ndef artifact_source_io():\n import base64,stat\n stamp,check=artifact_source_stamp,artifact_source_check\n descriptors=[];chain=[];primary=None\n try:\n  folder=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);descriptors.append(folder)\n  for part in REMOTE.strip('/').split('/'):\n   before=stamp(os.stat(part,dir_fd=folder,follow_symlinks=False))\n   child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=folder);descriptors.append(child)\n   check(stat.S_ISDIR(before[2]) and before==stamp(os.fstat(child)),'Payload ancestry changed')\n   chain.append((folder,part,child,before));folder=child\n  owner=stamp(os.fstat(folder))\n  check(owner[4:6]==[1000,1000] and stat.S_IMODE(owner[2])==448,'Payload owner differs')\n  check(ACTION in ('first','second','read','partial'),'Unknown payload action')\n  reading=ACTION in ('read','partial')\n  flags=(os.O_RDONLY if reading else os.O_RDWR)|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK\n  before=None\n  if ACTION=='first':\n   check(PREVIOUS is None,'First payload has prior identity')\n   flags|=os.O_CREAT|os.O_EXCL\n  else:\n   check((PREVIOUS is None) if ACTION=='partial' else (type(PREVIOUS) is dict and set(PREVIOUS)=={'identity','sha256'}),'Missing payload identity')\n   before=stamp(os.stat('artifact-sources.zlib',dir_fd=folder,follow_symlinks=False))\n   check(ACTION=='partial' or before==PREVIOUS['identity'],'Payload path identity changed')\n  fd=os.open('artifact-sources.zlib',flags,384,dir_fd=folder);descriptors.append(fd)\n  opened=stamp(os.fstat(fd))\n  check(stat.S_ISREG(opened[2]) and stat.S_IMODE(opened[2])==384 and opened[3:6]==[1,1000,1000],'Nonordinary payload file')\n  check((before is None and opened[6]==0) or before==opened,'Payload descriptor changed')\n  if ACTION!='first':\n   initial=os.read(fd,32769)\n   check(len(initial)==opened[6] and (len(initial)<=32768 if ACTION=='partial' else hashlib.sha256(initial).hexdigest()==PREVIOUS['sha256']),'Prior payload changed')\n   check(opened==stamp(os.fstat(fd))==stamp(os.stat('artifact-sources.zlib',dir_fd=folder,follow_symlinks=False)),'Prior payload unstable')\n   if ACTION=='second':check(len(initial)==16384 and PREVIOUS['sha256']==FIRST_SHA,'Wrong first payload')\n  if not reading:\n   chunk=base64.b64decode(TOKEN,validate=True)\n   check(base64.b64encode(chunk).decode()==TOKEN,'Noncanonical payload token')\n   size,digest=(16384,FIRST_SHA) if ACTION=='first' else (PACKED_SIZE-16384,SECOND_SHA)\n   check(len(chunk)==size and 0<size<=16384 and hashlib.sha256(chunk).hexdigest()==digest,'Payload chunk changed')\n   os.lseek(fd,0,os.SEEK_END)\n   check(os.write(fd,chunk)==len(chunk),'Short payload write')\n  os.lseek(fd,0,os.SEEK_SET);packed=os.read(fd,32769)\n  closed=stamp(os.fstat(fd))\n  size,digest=(len(initial),hashlib.sha256(initial).hexdigest()) if ACTION=='partial' else ((16384,FIRST_SHA) if ACTION=='first' else (PACKED_SIZE,PACKED_SHA))\n  check(len(packed)==size==closed[6] and hashlib.sha256(packed).hexdigest()==digest,'Complete payload changed')\n  check(opened[:6]==closed[:6] and closed==stamp(os.stat('artifact-sources.zlib',dir_fd=folder,follow_symlinks=False)),'Payload closing identity changed')\n  if reading:check(opened==closed,'Payload changed during read')\n  for parent,name,child,prior in chain:\n   current=stamp(os.fstat(child))\n   check(current==stamp(os.stat(name,dir_fd=parent,follow_symlinks=False)),'Payload closing ancestry changed')\n   check(current==prior or (ACTION=='first' and child==folder and current[:6]==prior[:6]),'Payload ancestry unstable')\n  return packed,dict(identity=closed,sha256=digest)\n except BaseException as error:\n  primary=error;raise\n finally:\n  close_error=None\n  for descriptor in reversed(descriptors):\n   try:os.close(descriptor)\n   except BaseException as error:close_error=close_error or error\n  if primary is None and close_error is not None:raise close_error\npacked,record=artifact_source_io()\n"

def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_request(argv):
    require(type(argv) is list and all(type(item) is str for item in argv),
            'Expected an exact argument list')
    require(len(argv) == 3 and argv[0] in ('--check-only', '--execute') and
            argv[1] == '--reviewed-head' and re.fullmatch('[0-9a-f]{40}', argv[2]),
            'Expected --check-only|--execute --reviewed-head <40lowerhex>')
    return argv[0], argv[2]


def _verify(raw, identity, label):
    require(type(raw) is bytes and len(raw) == identity[0] and
            hashlib.sha256(raw).hexdigest() == identity[1],
            'Fixed source bytes changed: ' + label)


def _stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, getattr(info, 'st_file_attributes', 0), info.st_ctime_ns)


def _plain_chain(path):
    stamps = []
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        expected = stat.S_ISREG if item == path else stat.S_ISDIR
        require(expected(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 1024,
                'Nonplain original source path: ' + str(item))
        require(item != path or info.st_nlink == 1, 'Original source has multiple links')
        stamps.append(_stamp(info))
    return stamps


def _read_handle(path, before, relative):
    descriptor, stream, primary = None, None, None
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_CLOEXEC', 0)
    flags |= getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        descriptor = os.open(path, flags)
        info = os.fstat(descriptor)
        opened = _stamp(info)
        path_identity = before[-1][:-1] if os.name == 'nt' else before[-1]
        handle_identity = opened[:-1] if os.name == 'nt' else opened
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                not getattr(info, 'st_file_attributes', 0) & 1024 and
                path_identity == handle_identity,
                'Original source changed before reading: ' + relative)
        stream = os.fdopen(descriptor, 'rb')
        descriptor = None
        raw = stream.read(65537)
        closed = _stamp(os.fstat(stream.fileno()))
        after = _plain_chain(path)
        require(before == after and path_identity == handle_identity and opened == closed and
                len(raw) == before[-1][4] and len(raw) <= 65536,
                'Original source changed while reading: ' + relative)
        _verify(raw, ORIGINALS[relative], relative)
        return raw
    except BaseException as error:
        primary = error
        raise
    finally:
        try:
            if stream is not None:
                stream.close()
            elif descriptor is not None:
                os.close(descriptor)
        except BaseException:
            if primary is None:
                raise


def read_original(relative, *, root=ROOT):
    require(type(relative) is str and relative in ORIGINALS, 'Unexpected original source')
    path = Path(root).absolute() / relative
    before = _plain_chain(path)
    require(0 < before[-1][4] <= 65536, 'Original source exceeds bootstrap bound')
    return _read_handle(path, before, relative)


def _project_caller(raw):
    for old, new, count in REPLACEMENTS:
        require(raw.count(old) == count, 'B4 caller projection count changed')
        raw = raw.replace(old, new)
    _verify(raw, PROJECTED, 'B4 private caller')
    return raw


def load_caller(*, root=ROOT):
    root = Path(root).absolute()
    raw = read_original(PREDECESSOR, root=root)
    predecessor = types.ModuleType('_sumox_d214_checked_d208')
    predecessor.__file__ = str(root / PREDECESSOR)
    exec(compile(raw, predecessor.__file__, 'exec'), predecessor.__dict__)
    original_project = predecessor.project_caller
    predecessor.project_caller = lambda original: _project_caller(original_project(original))
    caller = predecessor.load_caller(root=root)
    caller.B4_POLICY, caller.PROFILE_SOURCE = B4_POLICY, PROFILE_SOURCE
    caller.ARTIFACT_SOURCE_IO = ARTIFACT_SOURCE_IO
    caller.BUNDLE_PATHS, caller.SNAPSHOT_PATHS = dict(BUNDLE_PATHS), dict(SNAPSHOT_PATHS)
    caller.HARD_PINS = dict(caller.HARD_PINS, **EXTRA_PINS)
    caller.REQUIRED = set(REQUIRED)
    return caller


def main(argv):
    parse_request(argv)
    require(sys.dont_write_bytecode, 'Python -B required')
    return load_caller(root=ROOT).main(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
