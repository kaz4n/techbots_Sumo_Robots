# Compiles the fixed ordinary application with static linking and inhibited flags.
# Preserves bounded compilation while checking canonical ordinary source mapping.
# Independent D208 contract tests verify projection, mapping and guarded lifecycle.
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[1]
CALLER_SOURCE = 'tools/compile_app_motor_fault.py'
ADAPTER_SOURCE = 'tools/app_motor_fault_static_policy.py'
REMOTE_SOURCE = 'tools/app_motor_fault_compile_remote.py'
ORIGINALS = {
    CALLER_SOURCE: (29802, 'cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a'),
    ADAPTER_SOURCE: (8262, '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270'),
    REMOTE_SOURCE: (6891, '1428b9345d5f524b6c79ede2c30eabb240b6a45ef6a30a593063c3902054fec2'),
}
PROJECTED = {'tools/compile_app_motor_fault.py': (30744, '412121c6b6b8efc363a93f80762e29db7ad0671c23c19b2c1f2f281798b69a6e'), 'tools/app_motor_fault_static_policy.py': (8219, 'd1a78ad713d0550ed52805a6751640823a31ce4e96edafc3c058a7587c5e4863'), 'tools/app_motor_fault_compile_remote.py': (6845, '71c189ea3c354b7ccb969b35ae3f1a92a517380735059d00ff4c735b45cf4389')}
CALLER_REPLACEMENTS = (
    (b"CALLER = 'tools/compile_app_motor_fault.py'", b"CALLER = 'tools/compile_ordinary_app_static.py'", 1),
    (b'P7_app_motor_fault_compile_contract.md', b'P7_ordinary_app_static_compile_contract.md', 1),
    (b'P7_app_motor_fault_compile_raw', b'P7_ordinary_app_static_compile_raw', 1),
    (b'app-motor-fault-static', b'ordinary-app-static', 6),
    (b"'app_motor_fault.ino'", b"'app.ino'", 1),
    (b'-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1', b'-DMATCH=0 -DMOTORS_ALLOWED=0', 1),
    (b'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS', b'STATIC_ORDINARY_APP_LAYOUT_PACKAGE_PASS', 1),
    (b'self.code[ADAPTER]', b'project_adapter(self.code[ADAPTER])', 2),
    (b'self.code[REMOTE_HELPER]', b'project_remote(self.code[REMOTE_HELPER])', 2),
)
ADAPTER_REPLACEMENTS = (
    (b"'app_motor_fault.ino'", b"'app.ino'", 1),
    (b'-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1', b'-DMATCH=0 -DMOTORS_ALLOWED=0', 1),
    (b'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS', b'STATIC_ORDINARY_APP_LAYOUT_PACKAGE_PASS', 1),
)
REMOTE_REPLACEMENTS = (
    (b'app-motor-fault-static01', b'ordinary-app-static01', 1),
    (b"'app_motor_fault.ino'", b"'app.ino'", 1),
    (b'-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1', b'-DMATCH=0 -DMOTORS_ALLOWED=0', 1),
    (b'app-motor-fault-static-artifacts-v1', b'ordinary-app-static-artifacts-v1', 1),
    (b'3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270', b'd1a78ad713d0550ed52805a6751640823a31ce4e96edafc3c058a7587c5e4863', 1),
)


CALLER_INTERMEDIATE = (29819, '402fea3fdb0f2b1af99dff3f4a80afebf63529ae05466958b957ac1bd6038275')
CALLER_METHOD_REPLACEMENTS = (
    (b"    def source_names(self):\n        pending = [self.root / name for name in ('src', 'bench/app_motor_fault', 'bench/motor_fault/src')]\n        names, count = set(), 0\n        while pending:\n            folder = pending.pop()\n            self.base.plain(folder, directory=True)\n            for path in folder.iterdir():\n                count += 1\n                require(count <= 1024, 'Source entry bound exceeded')\n                self.base.plain(path, directory=path.is_dir())\n                if path.is_dir():\n                    pending.append(path)\n                else:\n                    names.add(self.base.relative(path.relative_to(self.root).as_posix()))\n                    require(len(names) <= 512, 'Source file bound exceeded')\n        return names\n", b"    def source_names(self):\n        pending = [self.root / 'src']\n        names, count = set(), 0\n        while pending:\n            folder = pending.pop()\n            self.base.plain(folder, directory=True)\n            for path in folder.iterdir():\n                count += 1\n                require(count <= 1024, 'Source entry bound exceeded')\n                self.base.plain(path, directory=path.is_dir())\n                if path.is_dir():\n                    pending.append(path)\n                else:\n                    names.add(self.base.relative(path.relative_to(self.root).as_posix()))\n                    require(len(names) <= 512, 'Source file bound exceeded')\n        return names\n"),
    (b"    def source_mapping(self, code, names):\n        mapped = {}\n        for name in sorted(names):\n            target = None\n            if name.startswith('bench/app_motor_fault/'):\n                relative = name[len('bench/app_motor_fault/'):]\n                target = relative if relative != '.gitkeep' else None\n            elif name == 'src/config.h' or name.startswith(('src/core/', 'src/hal/')):\n                target = name\n            elif name.startswith('src/app/') and not name.startswith('src/app/src/') and Path(name).suffix in (\n                    '.c', '.cc', '.cpp', '.h', '.hpp'):\n                target = name\n            elif name in ('bench/motor_fault/src/motor_fault.h', 'bench/motor_fault/src/motor_fault.cpp'):\n                target = 'src/' + Path(name).name\n            if target is not None:\n                require(target not in mapped, 'Stage source collision: ' + target)\n                mapped[target] = code[name]\n        require({PROJECT, 'src/motor_fault.h', 'src/motor_fault.cpp'} <= set(mapped), 'Missing diagnostic sources')\n        digest = hashlib.sha256()\n        for name in sorted(mapped):\n            digest.update(name.encode() + b'\\0')\n            digest.update(mapped[name])\n        return {name: sha(raw) for name, raw in mapped.items()}, digest.hexdigest()\n", b"    def source_mapping(self, code, names):\n        extensions = ('.c', '.cc', '.cpp', '.h', '.hpp')\n        reserved = ('config.h', 'core', 'hal', 'app')\n        for name in reserved:\n            require(not os.path.lexists(self.root / 'src/app/src' / name),\n                    'Reserved sketch-local source')\n        mapped = {}\n        for name in sorted(names):\n            name = self.base.relative(name)\n            require(name.startswith('src/'), 'Nonordinary source input')\n            target = None\n            if name == 'src/config.h' or name.startswith(('src/core/', 'src/hal/')):\n                target = name\n            elif name.startswith('src/app/'):\n                tail = PurePosixPath(name).relative_to('src/app')\n                if tail.parts[0] == 'src':\n                    require(len(tail.parts) > 1 and tail.parts[1] not in reserved,\n                            'Reserved sketch-local source')\n                    target = tail.as_posix()\n                elif tail.suffix in extensions:\n                    target = 'src/app/' + tail.as_posix()\n                elif len(tail.parts) == 1 and tail.name != '.gitkeep':\n                    target = tail.name\n            if target is not None:\n                target = self.base.relative(target)\n                require(target not in mapped, 'Stage source collision: ' + target)\n                mapped[target] = code[name]\n        require(PROJECT in mapped and not any(name in mapped for name in\n                ('sketch.yaml', 'sketch.yml', 'sketch.json')), 'Missing app or sketch override')\n        folded = [name.lower() for name in mapped]\n        require(len(mapped) <= 512 and len(set(folded)) == len(folded),\n                'Source count/case collision')\n        digest, total = hashlib.sha256(), 0\n        for name in sorted(mapped, key=Path):\n            total += len(mapped[name])\n            require(total <= 4194304, 'Mapped source byte bound exceeded')\n            digest.update(name.encode('utf-8') + b'\\0')\n            digest.update(mapped[name])\n        return {name: sha(body) for name, body in mapped.items()}, digest.hexdigest()\n"),
    (b"    def __init__(self, reviewed_head, *, root=ROOT):\n        parse_request(['--check-only', '--reviewed-head', reviewed_head])\n        self.root, self.reviewed_head = Path(root).absolute(), reviewed_head\n        self.base = load_legacy(self.root)\n        borrowed = ('git_state', 'load_board', 'prepare', 'save', 'transport',\n                    'direct', 'preamble', 'inventory', 'prerequisite', 'prerequisites',\n                    'command_runner', 'policy', 'final_policy')\n        for name in borrowed:\n            setattr(self, name, types.MethodType(getattr(self.base.CompileCurrent, name), self))\n        self.output, self.inputs_path = self.root / RAW / 'native_static01', self.root / RAW / 'inputs_static.json'\n        self.stage_attempt = ATTEMPT\n        self.stage_owner = self.root / 'build/stage' / ATTEMPT\n        self.stage_path = self.stage_owner / 'app_motor_fault'\n        self.remote_root, self.remote = PARENT, REMOTE\n        self.build_path, self.artifacts = REMOTE + '/build', REMOTE + '/artifacts'\n        self.fqbn, self.flags, self.startup = FQBN, FLAGS, 'default'\n        self.counter = self.query_calls = self.compiler_calls = 0\n        self.claimed = self.remote_owned = self.source_attempted = self.source_available = False\n        self.inputs_raw = self.inputs = self.code = self.stage_hashes = self.expected_stage = None\n        self.boot = self.source_sha256 = self.sketch = None\n        self.executor = self.board = self.receipt = self.artifact_receipt = None\n", b"    def __init__(self, reviewed_head, *, root=ROOT):\n        parse_request(['--check-only', '--reviewed-head', reviewed_head])\n        self.root, self.reviewed_head = Path(root).absolute(), reviewed_head\n        self.base = load_legacy(self.root)\n        borrowed = ('git_state', 'load_board', 'prepare', 'save', 'transport',\n                    'direct', 'preamble', 'inventory', 'prerequisite', 'prerequisites',\n                    'command_runner', 'policy', 'final_policy')\n        for name in borrowed:\n            setattr(self, name, types.MethodType(getattr(self.base.CompileCurrent, name), self))\n        self.output, self.inputs_path = self.root / RAW / 'native_static01', self.root / RAW / 'inputs_static.json'\n        self.stage_attempt = ATTEMPT\n        self.stage_owner = self.root / 'build/stage' / ATTEMPT\n        self.stage_path = self.stage_owner / 'app'\n        self.remote_root, self.remote = PARENT, REMOTE\n        self.build_path, self.artifacts = REMOTE + '/build', REMOTE + '/artifacts'\n        self.fqbn, self.flags, self.startup = FQBN, FLAGS, 'default'\n        self.counter = self.query_calls = self.compiler_calls = 0\n        self.claimed = self.remote_owned = self.source_attempted = self.source_available = False\n        self.inputs_raw = self.inputs = self.code = self.stage_hashes = self.expected_stage = None\n        self.boot = self.source_sha256 = self.sketch = None\n        self.executor = self.board = self.receipt = self.artifact_receipt = None\n"),
    (b"    def admission(self):\n        raw = self.base.read(self.inputs_path, 262144)\n        require(self.inputs_raw is None or raw == self.inputs_raw, 'Input manifest changed')\n        value = self.base.decode(raw)\n        keys(value, ('schema', 'source_sha256', 'boot_id', 'files'), 'Invalid manifest fields')\n        require(value['schema'] == 'ordinary-app-static-inputs-v1' and\n                type(value['source_sha256']) is str and re.fullmatch('[0-9a-f]{64}', value['source_sha256']) and\n                type(value['boot_id']) is str and re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', value['boot_id']),\n                'Invalid source or boot identity')\n        names, code, total = self.source_names(), {}, 0\n        pins = value['files']\n        keys(pins, REQUIRED | names, 'Input filename set changed')\n        for name, expected in pins.items():\n            require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected), 'Invalid input digest')\n            code[name] = self.base.read(self.root / self.base.relative(name))\n            require(sha(code[name]) == expected, 'Pinned input changed: ' + name)\n            total += len(code[name]) if name in names else 0\n        require(total <= 4194304, 'Source byte bound exceeded')\n        for name, expected in HARD_PINS.items():\n            require(pins[name] == expected, 'Hard pin changed: ' + name)\n        self.base.checked_wait(code[SUPPORT])\n        mapped, source = self.source_mapping(code, names)\n        require(source == value['source_sha256'], 'Staged source digest changed')\n        self.inputs_raw, self.inputs, self.code = raw, value, code\n        self.boot, self.source_sha256, self.expected_stage = value['boot_id'], source, mapped\n        self.sketch = PARENT + '/' + source + '/app_motor_fault'\n        self.base.BOOT = self.boot\n        if self.executor is not None:\n            require(self.executor['BOOT'] == self.boot, 'Executor boot changed')\n", b"    def admission(self):\n        raw = self.base.read(self.inputs_path, 262144)\n        require(self.inputs_raw is None or raw == self.inputs_raw, 'Input manifest changed')\n        value = self.base.decode(raw)\n        keys(value, ('schema', 'source_sha256', 'boot_id', 'files'), 'Invalid manifest fields')\n        require(value['schema'] == 'ordinary-app-static-inputs-v1' and\n                type(value['source_sha256']) is str and re.fullmatch('[0-9a-f]{64}', value['source_sha256']) and\n                type(value['boot_id']) is str and re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', value['boot_id']),\n                'Invalid source or boot identity')\n        names, code, total = self.source_names(), {}, 0\n        pins = value['files']\n        keys(pins, REQUIRED | names, 'Input filename set changed')\n        for name, expected in pins.items():\n            require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected), 'Invalid input digest')\n            code[name] = self.base.read(self.root / self.base.relative(name))\n            require(sha(code[name]) == expected, 'Pinned input changed: ' + name)\n            total += len(code[name]) if name in names else 0\n        require(total <= 4194304, 'Source byte bound exceeded')\n        for name, expected in HARD_PINS.items():\n            require(pins[name] == expected, 'Hard pin changed: ' + name)\n        self.base.checked_wait(code[SUPPORT])\n        mapped, source = self.source_mapping(code, names)\n        require(source == value['source_sha256'], 'Staged source digest changed')\n        view = self.base.module_from(self.root, 'tools/match_deploy.py',\n                                     code['tools/match_deploy.py'])\n        require(view.app_source_hash(self.root) == source, 'Ordinary helper digest changed')\n        self.inputs_raw, self.inputs, self.code = raw, value, code\n        self.boot, self.source_sha256, self.expected_stage = value['boot_id'], source, mapped\n        self.sketch = PARENT + '/' + source + '/app'\n        self.base.BOOT = self.boot\n        if self.executor is not None:\n            require(self.executor['BOOT'] == self.boot, 'Executor boot changed')\n"),
    (b"    def source_admission(self):\n        self.source_attempted = True\n        program = self.source_program() + 'expected=' + repr(self.stage_hashes) + '\\n' + '''if os.path.lexists(root.parent):\n if root.parent.resolve()!=root.parent or not root.parent.is_dir():raise ValueError('Invalid source owner')\n if sorted(p.name for p in root.parent.iterdir())!=['app_motor_fault']:raise ValueError('Unexpected source owner entries')\n if checked_source_set()!=expected:raise ValueError('Existing source differs')\n reused=True\nelse:\n root.parent.mkdir(mode=0o700);root.mkdir();reused=False\n for name in expected:(root/name).parent.mkdir(parents=True,exist_ok=True)\nprint(json.dumps({'reused':reused}))\n'''\n        reply, _ = self.direct(program, 'source-admission')\n        value = self.base.decode(reply.stdout)\n        require(not reply.stderr and type(value) is dict and set(value) == {'reused'} and\n                type(value['reused']) is bool, 'Invalid source admission reply')\n        return value['reused']\n", b"    def source_admission(self):\n        self.source_attempted = True\n        program = self.source_program() + 'expected=' + repr(self.stage_hashes) + '\\n' + '''if os.path.lexists(root.parent):\n if root.parent.resolve()!=root.parent or not root.parent.is_dir():raise ValueError('Invalid source owner')\n if sorted(p.name for p in root.parent.iterdir())!=['app']:raise ValueError('Unexpected source owner entries')\n if checked_source_set()!=expected:raise ValueError('Existing source differs')\n reused=True\nelse:\n root.parent.mkdir(mode=0o700);root.mkdir();reused=False\n for name in expected:(root/name).parent.mkdir(parents=True,exist_ok=True)\nprint(json.dumps({'reused':reused}))\n'''\n        reply, _ = self.direct(program, 'source-admission')\n        value = self.base.decode(reply.stdout)\n        require(not reply.stderr and type(value) is dict and set(value) == {'reused'} and\n                type(value['reused']) is bool, 'Invalid source admission reply')\n        return value['reused']\n"),
    (b'    def stage(self):\n        self.local()\n        require(not os.path.lexists(self.stage_owner), \'Local stage owner already exists\')\n        require(shutil.disk_usage(self.root).free >= 134217728, \'Less than 128MiB local free space\')\n        staged = self.board.stage(\'bench/app_motor_fault\', attempt=ATTEMPT)\n        require(staged == self.stage_path, \'Unexpected stage destination\')\n        self.stage_hashes = self.executor[\'files\'](staged)\n        require(self.stage_hashes == self.expected_stage and\n                self.board.source_hash(staged) == self.source_sha256, \'Stage differs from reviewed source\')\n        actual_dirs = {path.relative_to(staged).as_posix() for path in staged.rglob(\'*\') if path.is_dir()}\n        require(actual_dirs == directories(self.expected_stage), \'Stage directories differ\')\n        self.local()\n        self.save(\'staged_files.json\', self.stage_hashes)\n        program = self.preamble() + "Path(REMOTE).mkdir(mode=0o700)\\n"\n        program += "for name in (\'commands\',\'build\',\'artifacts\'):(Path(REMOTE)/name).mkdir()\\nprint(json.dumps(identity))\\n"\n        reply, _ = self.direct(program, \'command-owner\')\n        require(not reply.stderr and self.base.decode(reply.stdout)[\'boot_id\'] == self.boot,\n                \'Invalid command owner reply\')\n        self.remote_owned = True\n        if not self.source_admission():\n            for name in self.stage_hashes:\n                self.inventory()\n                self.transport([\'push\', str(self.stage_path / name), self.sketch + \'/\' + name], 60, \'push\')\n        self.sources()\n        self.source_available = True\n', b'    def stage(self):\n        self.local()\n        require(not os.path.lexists(self.stage_owner), \'Local stage owner already exists\')\n        require(shutil.disk_usage(self.root).free >= 134217728, \'Less than 128MiB local free space\')\n        staged = self.board.stage(\'app\', attempt=ATTEMPT)\n        require(staged == self.stage_path, \'Unexpected stage destination\')\n        self.stage_hashes = self.executor[\'files\'](staged)\n        require(self.stage_hashes == self.expected_stage and\n                self.board.source_hash(staged) == self.source_sha256, \'Stage differs from reviewed source\')\n        actual_dirs = {path.relative_to(staged).as_posix() for path in staged.rglob(\'*\') if path.is_dir()}\n        require(actual_dirs == directories(self.expected_stage), \'Stage directories differ\')\n        self.local()\n        self.save(\'staged_files.json\', self.stage_hashes)\n        program = self.preamble() + "Path(REMOTE).mkdir(mode=0o700)\\n"\n        program += "for name in (\'commands\',\'build\',\'artifacts\'):(Path(REMOTE)/name).mkdir()\\nprint(json.dumps(identity))\\n"\n        reply, _ = self.direct(program, \'command-owner\')\n        require(not reply.stderr and self.base.decode(reply.stdout)[\'boot_id\'] == self.boot,\n                \'Invalid command owner reply\')\n        self.remote_owned = True\n        if not self.source_admission():\n            for name in self.stage_hashes:\n                self.inventory()\n                self.transport([\'push\', str(self.stage_path / name), self.sketch + \'/\' + name], 60, \'push\')\n        self.sources()\n        self.source_available = True\n'),
)


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


def _project(raw, relative, replacements):
    _verify(raw, ORIGINALS[relative], relative)
    for old, new, count in replacements:
        require(raw.count(old) == count, 'Projection occurrence count changed: ' + relative)
        raw = raw.replace(old, new)
    _verify(raw, PROJECTED[relative], 'projected ' + relative)
    return raw


def project_caller(raw):
    _verify(raw, ORIGINALS[CALLER_SOURCE], CALLER_SOURCE)
    for old, new, count in CALLER_REPLACEMENTS:
        require(raw.count(old) == count, 'Caller metadata occurrence count changed')
        raw = raw.replace(old, new)
    _verify(raw, CALLER_INTERMEDIATE, 'intermediate ' + CALLER_SOURCE)
    for old, new in CALLER_METHOD_REPLACEMENTS:
        require(raw.count(old) == 1, 'Caller method span changed')
        raw = raw.replace(old, new)
    _verify(raw, PROJECTED[CALLER_SOURCE], 'projected ' + CALLER_SOURCE)
    return raw


def project_adapter(raw):
    return _project(raw, ADAPTER_SOURCE, ADAPTER_REPLACEMENTS)


def project_remote(raw):
    return _project(raw, REMOTE_SOURCE, REMOTE_REPLACEMENTS)


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


def load_caller(*, root=ROOT):
    root = Path(root).absolute()
    originals = {name: read_original(name, root=root) for name in ORIGINALS}
    caller = project_caller(originals[CALLER_SOURCE])
    project_adapter(originals[ADAPTER_SOURCE])
    project_remote(originals[REMOTE_SOURCE])
    module = types.ModuleType('_sumox_d208_ordinary_app_static_compile')
    module.__file__ = str(root / CALLER_SOURCE)
    module.project_adapter, module.project_remote = project_adapter, project_remote
    exec(compile(caller, module.__file__, 'exec'), module.__dict__)
    # Pin the immutable sources behind the projection, not generated disk copies.
    module.HARD_PINS = dict(module.HARD_PINS)
    for name in (CALLER_SOURCE, REMOTE_SOURCE):
        module.HARD_PINS[name] = ORIGINALS[name][1]
    module.HARD_PINS['tools/match_deploy.py'] = '3acacad6e95aff1012e9d0d1f8ef60905c026ebe865569fdb71384abd607d2a9'
    module.REQUIRED = set(module.REQUIRED) | set(module.HARD_PINS)
    return module


def main(argv):
    parse_request(argv)
    require(sys.dont_write_bytecode, 'Python -B required')
    return load_caller(root=ROOT).main(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
