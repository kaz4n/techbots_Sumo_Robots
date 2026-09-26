# Compiles and runs one identified, motor-inhibited synthetic recorder delivery.
# Reuses checked static compilation and upload lifecycles without broad admission.
# Focused caller fixtures cover identity, one-use sequencing and retained failures.
from datetime import datetime, timezone
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
import types
import zlib

ROOT = Path(__file__).absolute().parents[1]
CALLER = 'tools/run_recorder_delivery.py'
RAW = 'state/analysis/P7_recorder_delivery_raw'
CONTRACT = 'state/analysis/P7_recorder_delivery_contract.md'
PROJECT = 'recorder.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
PARENT = '/home/arduino/sumox26_codex_build'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
TARGET = '2629958581'
IDENTITY_HEADER = 'src/recorder_run_identity.h'
BOOTSTRAP = 'tools/compile_commissioning_app.py'
BOOTSTRAP_PIN = (17992, '038a74777db7d26a15ff543d311fc4df2503e6f6b8e3b08fabcfb1c853220462')
STATIC = 'state/analysis/P7_static_startup_raw/'
UPLOADER = STATIC + 'upload_remote.py'
UPLOAD_BASELINE = STATIC + 'upload_bindings.json'
UPLOAD_ADAPTER = 'tools/match_upload.py'
EXTRA = {CALLER, CONTRACT, BOOTSTRAP, UPLOADER, UPLOAD_ADAPTER, UPLOAD_BASELINE,
         'tools/dump_match.py', 'tools/validate_csv_bundle.py', 'tools/b4_app_compile_remote.py'}
SNAPSHOT_PATHS = {
    'adapter': 'tools/app_motor_fault_static_policy.py',
    'common': 'tools/app_build_policy.py',
    'static_policy': 'state/analysis/P7_static_link_probe_raw/static_policy.py',
    'reference': 'state/analysis/P7_static_link_probe_raw/static_reference.json',
    'extension': 'state/analysis/P7_static_link_probe_raw/static_native_artifacts.py'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def derive_session(attempt):
    require(type(attempt) is str and re.fullmatch('[0-9a-f]{32}', attempt), 'Exact attempt hex required')
    session = int(attempt[:16], 16)
    require(session != 0, 'Attempt must identify a positive uint64 session')
    return session


def parse_request(argv):
    require(type(argv) is list and all(type(item) is str for item in argv), 'Exact argv required')
    require(len(argv) == 5 and argv[0] in ('--check-only', '--compile', '--run') and
            argv[1::2] == ['--attempt', '--reviewed-head'],
            'Expected action --attempt 32lowerhex --reviewed-head 40lowerhex')
    derive_session(argv[2])
    require(re.fullmatch('[0-9a-f]{40}', argv[4]), 'Exact reviewed HEAD required')
    return dict(action=argv[0], attempt=argv[2], reviewed_head=argv[4])


def checked_request(request):
    require(type(request) is dict and set(request) == {'action', 'attempt', 'reviewed_head'},
            'Unexpected request fields')
    return parse_request([request['action'], '--attempt', request['attempt'],
                          '--reviewed-head', request['reviewed_head']])


def render_identity(session):
    require(type(session) is int and 1 <= session <= 0xffffffffffffffff, 'Exact positive session required')
    return ('// Identifies one reviewed synthetic recorder delivery.\n'
            '// Grants apply only to its staged inert bench owner.\n'
            '// Expected-session reception must validate every record.\n'
            '#pragma once\n#include "hal/dump_uart_unoq.h"\n'
            'namespace recorder_run_identity {\n'
            'inline constexpr bool ENABLED = true;\n'
            'inline constexpr std::uint64_t SESSION = ' + str(session) + 'ULL;\n'
            'inline constexpr recorder::dump::SetupGrant GRANTS{true, true, true, false,\n'
            ' recorder::dump::ReceiveStream::UNTRUSTED_RECEIVE_STREAM, SESSION};\n'
            'static_assert(MATCH == 0 && MOTORS_ALLOWED == 0, "Inert delivery only");\n'
            '} // namespace recorder_run_identity\n').encode()


def build_paths(attempt, source_digest):
    derive_session(attempt)
    require(type(source_digest) is str and re.fullmatch('[0-9a-f]{64}', source_digest), 'Invalid source digest')
    owner = 'recorder-' + attempt[:16]
    remote, stage = PARENT + '/' + owner, 'build/stage/' + owner
    return dict(owner=owner, output=RAW + '/' + owner, remote=remote,
                stage_owner=stage, stage=stage + '/recorder', build=remote + '/build',
                artifacts=remote + '/artifacts', sketch=PARENT + '/' + source_digest + '/recorder')


def module_from(name, raw, path='/sumox-source/tools/run_recorder_delivery.py'):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def artifact_module_source(raw):
    # Send only the pure artifact component, keeping the inherited two bounded
    # source chunks. Native run/control functions are not artifact dependencies.
    names = {'require', 'sha', 'derive_session', 'build_paths', 'module_from',
             'snapshot_policy', 'inspect_artifacts'}
    constants = {'RAW', 'PROJECT', 'FQBN', 'FLAGS', 'PARENT', 'SNAPSHOT_PATHS'}
    lines, selected = raw.decode().splitlines(keepends=True), []
    found = set()
    for node in ast.parse(raw).body:
        name = node.name if isinstance(node, ast.FunctionDef) else (
            node.targets[0].id if isinstance(node, ast.Assign) and len(node.targets) == 1 and
            isinstance(node.targets[0], ast.Name) else None)
        if name in names | constants:
            require(name not in found, 'Duplicate artifact component')
            found.add(name)
            selected.append(''.join(lines[node.lineno - 1:node.end_lineno]))
    require(found == names | constants, 'Missing artifact component')
    return ('import hashlib,re,types\nfrom pathlib import Path\n' + '\n\n'.join(selected)).encode()


def snapshot_policy(snapshots):
    # The D222 snapshot checker owns all five immutable dependency identities.
    checked = dict(snapshots)
    adapter = module_from('_recorder_static_adapter', checked[SNAPSHOT_PATHS['adapter']])
    adapter._checked_source = lambda path: checked[path]
    adapter.PROJECT, adapter.FQBN, adapter.FLAGS = PROJECT, FQBN, FLAGS
    adapter._ALIASES = {PROJECT + suffix: 'app.ino' + suffix for suffix in (
        '.elf', '_debug.elf', '_temp.elf', '.bin', '.bin-zsk.bin', '.elf-zsk.bin', '.map')}
    return adapter


def inspect_artifacts(build_path, artifacts_path, bundle, *, attempt, source_digest, fs_root=Path('/')):
    paths = build_paths(attempt, source_digest)
    primitive = module_from('_recorder_artifact_primitive', bundle['primitive'])
    sources = {key: value for key, value in bundle.items() if key != 'primitive'}
    primitive.PINS = dict(primitive.PINS, policy=sha(sources['policy']))
    primitive.SIZES = dict(primitive.SIZES, policy=len(sources['policy']))
    primitive.PROJECT, primitive.REMOTE = PROJECT, paths['remote']
    primitive.BUILD, primitive.ARTIFACTS = paths['build'], paths['artifacts']
    primitive.FILE_LIMITS = {'build/' + PROJECT + suffix: limit
                            for suffix, limit in primitive.SUFFIX_LIMITS.items()}
    primitive.FILE_LIMITS['artifacts/' + PROJECT + '.bin-zsk.bin'] = 786432

    def first(helper, unused, root_fd, checked, result):
        payloads = primitive.artifact_files(helper, root_fd, build_path, artifacts_path, result['files'])
        _, result['loader'] = primitive.installed(helper, root_fd, primitive.LOADER, 16777216, primitive.LOADER_SHA)
        tls, result['tls_source'] = primitive.installed(helper, root_fd, primitive.TLS, 65536, primitive.TLS_SHA)
        policy = snapshot_policy({path: checked[key] for key, path in SNAPSHOT_PATHS.items()})
        inputs = {key.split('/')[1]: body for key, body in payloads.items() if key.startswith('build/')}
        result['layout'] = policy.validate_artifacts(inputs, tls, checked['base'],
            exported_flat_package=payloads['artifacts/' + PROJECT + '.bin-zsk.bin'])

    primitive.first_observation = first
    result = primitive.inspect_artifacts(build_path, artifacts_path, sources, fs_root=fs_root)
    result.update(schema='recorder-delivery-artifacts-v1', attempt=attempt,
                  session=derive_session(attempt), source_sha256=source_digest)
    return result


class RecorderCompileMixin:
    def __init__(self, reviewed_head, *, root=ROOT):
        super().__init__(reviewed_head, root=root)
        self.attempt = self._request['attempt']
        self.session = derive_session(self.attempt)
        self.manifest_saved = False
        names = self.source_names()
        bodies = {name: self.base.read(self.root / name) for name in names}
        _, self.source_sha256 = self.source_mapping(bodies, names)
        paths = build_paths(self.attempt, self.source_sha256)
        self.stage_attempt = paths['owner']
        self.output, self.stage_owner = self.root / paths['output'], self.root / paths['stage_owner']
        self.stage_path, self.inputs_path = self.root / paths['stage'], self.output / 'inputs.json'
        self.remote, self.build_path, self.artifacts = paths['remote'], paths['build'], paths['artifacts']
        self.sketch, self.boot, self.flags = paths['sketch'], BOOT, FLAGS

    def source_names(self):
        names, pending, count = set(), [self.root / 'src', self.root / 'bench/recorder'], 0
        while pending:
            folder = pending.pop()
            self.base.plain(folder, directory=True)
            for path in folder.iterdir():
                count += 1
                require(count <= 1024, 'Source entry bound exceeded')
                self.base.plain(path, directory=path.is_dir())
                if path.is_dir():
                    pending.append(path)
                else:
                    names.add(self.base.relative(path.relative_to(self.root).as_posix()))
                    require(len(names) <= 512, 'Source count bound exceeded')
        return names

    def source_mapping(self, code, names):
        mapped = {}
        for name in sorted(names):
            target = None
            if name.startswith('bench/recorder/'):
                target = name[len('bench/recorder/'):]
                if target == '.gitkeep':
                    continue
                require(not target.startswith(tuple('src/' + item for item in ('config.h', 'core/', 'hal/', 'app/'))),
                        'Reserved recorder-local source')
            elif name == 'src/config.h' or name.startswith(('src/core/', 'src/hal/')):
                target = name
            elif name.startswith('src/app/') and not name.startswith('src/app/src/') and Path(name).suffix in (
                    '.c', '.cc', '.cpp', '.h', '.hpp'):
                target = name
            if target is not None:
                require(target not in mapped, 'Source collision')
                mapped[target] = code[name]
        require({PROJECT, IDENTITY_HEADER} <= set(mapped), 'Recorder sources missing')
        require(not any(name in mapped for name in ('sketch.yaml', 'sketch.yml', 'sketch.json')), 'Sketch override')
        mapped[IDENTITY_HEADER] = render_identity(self.session)
        require(len(set(name.lower() for name in mapped)) == len(mapped), 'Case collision')
        digest = hashlib.sha256()
        for name in sorted(mapped, key=Path):
            digest.update(name.encode() + b'\0')
            digest.update(mapped[name])
        self.staged_bytes = mapped
        return {name: sha(body) for name, body in mapped.items()}, digest.hexdigest()

    def admission(self):
        names = self.source_names()
        code = {name: self.base.read(self.root / name) for name in sorted(self._module.REQUIRED | names)}
        require(sum(len(code[name]) for name in names) <= 4194304, 'Source byte bound exceeded')
        for name, digest in self._module.HARD_PINS.items():
            require(sha(code[name]) == digest, 'Frozen primitive changed: ' + name)
        require(code == self._bootstrap._head_bytes(self.root, self.reviewed_head, set(code)),
                'Current inputs differ from reviewed HEAD')
        mapped, source = self.source_mapping(code, names)
        require(source == self.source_sha256, 'Staged identity/source changed')
        value = self.identity('recorder-delivery-inputs-v1')
        value['files'] = {name: sha(body) for name, body in code.items()}
        raw = canonical(value)
        require(self.inputs_raw is None or self.inputs_raw == raw, 'Input snapshot changed')
        if self.manifest_saved:
            require(self.base.read(self.inputs_path) == raw, 'Saved inputs changed')
        self.inputs_raw, self.inputs, self.code, self.expected_stage = raw, value, code, mapped
        self.base.checked_wait(code[self._module.SUPPORT])
        self.base.BOOT = self.boot
        if self.executor is not None:
            require(self.executor['BOOT'] == self.boot, 'Executor boot changed')

    def identity(self, schema):
        return dict(schema=schema, attempt=self.attempt, session=self.session,
                    reviewed_head=self.reviewed_head, source_sha256=self.source_sha256,
                    boot_id=BOOT, project=PROJECT, fqbn=FQBN, flags=FLAGS)

    def claim(self):
        self.output.mkdir(mode=0o700)
        self.claimed = True
        # Use exactly canonical bytes so later reads bind the same snapshot.
        with self.inputs_path.open('xb') as target:
            target.write(self.inputs_raw)
        self.manifest_saved = True
        self.save('intent.json', self.identity('recorder-delivery-compile-intent-v1'))

    def stage(self):
        self.local()
        require(not os.path.lexists(self.stage_owner), 'Stage already consumed')
        require(shutil.disk_usage(self.root).free >= 134217728, 'Less than 128 MiB free')
        staged = self.board.stage('bench/recorder', attempt=self.stage_attempt)
        require(staged == self.stage_path, 'Unexpected stage path')
        (staged / IDENTITY_HEADER).write_bytes(render_identity(self.session))
        self.stage_hashes = self.executor['files'](staged)
        require(self.stage_hashes == self.expected_stage and self.board.source_hash(staged) == self.source_sha256,
                'Staged source differs')
        self.local()
        self.save('staged_files.json', self.stage_hashes)
        program = self.preamble() + "Path(REMOTE).mkdir(mode=0o700)\n"
        program += "for name in ('commands','build','artifacts'):(Path(REMOTE)/name).mkdir()\nprint(json.dumps(identity))\n"
        reply, _ = self.direct(program, 'command-owner')
        require(not reply.stderr and self.base.decode(reply.stdout)['boot_id'] == self.boot, 'Owner reply differs')
        self.remote_owned = True
        if not self.source_admission():
            self.inventory()
            self.transport(['push', str(staged), self.sketch.rsplit('/', 1)[0]], 120, 'source-push')
            self.inventory()
        self.sources()
        self.source_available = True

    def source_admission(self):
        self.source_attempted = True
        program = self.source_program() + 'expected=' + repr(self.stage_hashes) + '\n' + '''if os.path.lexists(root.parent):
 if root.parent.resolve()!=root.parent or not root.parent.is_dir():raise ValueError('Invalid source owner')
 if sorted(p.name for p in root.parent.iterdir())!=['recorder']:raise ValueError('Unexpected source owner entries')
 if source_set()!=expected:raise ValueError('Existing source differs')
 reused=True
else:
 root.parent.mkdir(mode=0o700);root.mkdir();reused=False
 for name in expected:(root/name).parent.mkdir(parents=True,exist_ok=True)
print(json.dumps({'reused':reused}))
'''
        reply, _ = self.direct(program, 'source-admission')
        value = self.base.decode(reply.stdout)
        require(not reply.stderr and type(value) is dict and set(value) == {'reused'} and
                type(value['reused']) is bool, 'Invalid source admission reply')
        return value['reused']

    def static_policy(self):
        self.local()
        adapter = snapshot_policy({path: self.code[path] for path in SNAPSHOT_PATHS.values()})
        return adapter

    def check(self):
        value = super().check()
        value.update(self.identity('recorder-delivery-check-v1'), board_observed=False)
        return value

    def artifact_program(self):
        program = super().artifact_program()
        old = "result=module.inspect_artifacts(REMOTE+'/build',REMOTE+'/artifacts',bundle)"
        require(program.count(old) == 1, 'Artifact call seam changed')
        program = program.replace(old, old[:-1] + ',attempt=' + repr(self.attempt) +
                                  ',source_digest=' + repr(self.source_sha256) + ')')
        return program.replace('source_sha=' + repr(sha(self.code[CALLER])),
                               'source_sha=' + repr(sha(artifact_module_source(self.code[CALLER]))))

    def _artifact_payload(self):
        component = artifact_module_source(self.code[CALLER])
        sources = {name: self.code[path] for name, path in self._module.BUNDLE_PATHS.items()}
        sources['policy'] = component
        raw = json.dumps(dict(source=component.decode(), bundle={name: body.decode()
                         for name, body in sources.items()}), sort_keys=True, separators=(',', ':')).encode()
        packed = zlib.compress(raw, 9)
        require(len(raw) <= 262144 and 16384 < len(packed) <= 32768, 'Artifact source bounds differ')
        return raw, packed

    def validate_artifact_reply(self, text):
        value = self.base.decode(text)
        require(value.get('schema') == 'recorder-delivery-artifacts-v1' and
                value.get('attempt') == self.attempt and type(value.get('session')) is int and
                value['session'] == self.session and value.get('source_sha256') == self.source_sha256,
                'Artifact attempt differs')
        normalized = {key: item for key, item in value.items()
                      if key not in ('attempt', 'session', 'source_sha256')}
        normalized['schema'] = 'b4-app-m0-static-artifacts-v1'
        super().validate_artifact_reply(json.dumps(normalized))
        return value

    def validate_layout(self, value, records):
        require(value.get('status') == 'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS' and
                value.get('project') == PROJECT and value.get('fqbn') == FQBN and value.get('flags') == FLAGS,
                'Recorder artifact profile differs')
        aliases = {PROJECT + suffix: 'app.ino' + suffix for suffix in self._module.SUFFIX_LIMITS}
        require(value.get('artifact_aliases') == aliases and value.get('artifact_sha256') ==
                {name: records['build/' + name]['sha256'] for name in aliases}, 'Artifact hashes differ')
        self._module.checked_native_layout(value['validator_report'], records, aliases)

    def run(self):
        self.check()
        self.prepare()
        report = self.identity('recorder-delivery-compile-outcome-v1')
        report.update(started_utc=datetime.now(timezone.utc).isoformat(), final_checks=[])
        try:
            self.claim()
        except Exception as error:
            if self.claimed:
                return self.finish(report, self.closing(report, error))
            raise
        primary = None
        try:
            self.inventory(initial=True)
            self.prerequisites()
            self.stage()
            self.build()
        except Exception as error:
            primary = error
        return self.finish(report, self.closing(report, primary))

    def finish(self, report, primary):
        report['artifact_sources_identity'] = self.artifact_sources_identity
        return super().finish(report, primary)


def make_owner(request, *, root=ROOT):
    request, root = checked_request(request), Path(root).absolute()
    raw = (root / BOOTSTRAP).read_bytes()
    require((len(raw), sha(raw)) == BOOTSTRAP_PIN, 'D222 bootstrap changed')
    bootstrap = module_from('_recorder_checked_compile', raw, root / BOOTSTRAP)
    base = bootstrap._bootstrap(root).load_caller(root=root)
    base.REQUIRED = set(base.REQUIRED) | EXTRA
    base.HARD_PINS = dict(base.HARD_PINS, **{BOOTSTRAP: BOOTSTRAP_PIN[1]})
    base.PROJECT, base.FQBN, base.FLAGS = PROJECT, FQBN, FLAGS
    base.REMOTE_HELPER, base.CONTRACT, base.RAW = CALLER, CONTRACT, RAW
    base.BUNDLE_PATHS = dict(base.BUNDLE_PATHS, policy=CALLER, primitive='tools/b4_app_compile_remote.py')
    cls = type('RecorderCompile', (RecorderCompileMixin, base.CompileDiagnostic),
               dict(_module=base, _bootstrap=bootstrap, _request=request))
    base.CompileDiagnostic = cls
    return cls(request['reviewed_head'], root=root)


def validate_compile(outcome, artifacts, identity):
    require(type(outcome) is dict and type(artifacts) is dict and type(identity) is dict,
            'Compile evidence must be objects')
    for name, value in identity.items():
        if name != 'schema':
            require(type(outcome.get(name)) is type(value) and outcome[name] == value,
                    'Compile identity differs: ' + name)
    require(outcome.get('schema') == 'recorder-delivery-compile-outcome-v1' and
            outcome.get('status') == 'COMPILE_CHECKED' and outcome.get('first_error') is None and
            type(outcome.get('compiler_calls')) is int and outcome['compiler_calls'] == 1 and
            type(outcome.get('query_calls')) is int and outcome['query_calls'] == 1,
            'Compile did not close successfully exactly once')
    checks = outcome.get('final_checks')
    expected_checks = ('local', 'identity', 'initialization', 'builtins', 'remote_sources',
                       'installed_pins', 'overrides', 'artifacts', 'artifact_sources')
    require(checks == [dict(name=name, status='PASS', error=None) for name in expected_checks],
            'Compile closing checks did not pass')
    require(outcome.get('project') == PROJECT and outcome.get('fqbn') == FQBN and
            outcome.get('flags') == FLAGS and artifacts.get('status') == 'ARTIFACTS_CHECKED',
            'Only checked static/default inhibited recorder artifacts are admitted')
    require(type(outcome.get('artifact_sources_identity')) is dict, 'Missing artifact source closure')
    for name in ('attempt', 'session', 'source_sha256'):
        require(type(artifacts.get(name)) is type(identity[name]) and artifacts[name] == identity[name],
                'Artifact identity differs: ' + name)


def claim_session(root, attempt):
    # Full attempts that collide on the uint64 session share the same owner.
    derive_session(attempt)
    root = Path(root).absolute()
    output = root / RAW / ('recorder-' + attempt[:16])
    for path in (*reversed(output.parents), output):
        require(path.is_dir() and not path.is_symlink() and
                not getattr(path.lstat(), 'st_file_attributes', 0) & 1024, 'Nonplain session owner')
    run = output / 'run'
    run.mkdir(mode=0o700)
    with (run / 'attempt.json').open('xb') as target:
        target.write(canonical(dict(attempt=attempt, session=derive_session(attempt))))
    return run


def upload_profile(uploader, attempt, source_digest):
    paths = build_paths(attempt, source_digest)
    files = dict(uploader.FILE_PATHS)
    files['raw'] = paths['build'] + '/' + PROJECT + '.bin'
    files['sketch'] = paths['build'] + '/' + PROJECT + '.bin-zsk.bin'
    files['exported'] = paths['artifacts'] + '/' + PROJECT + '.bin-zsk.bin'
    absent = tuple(uploader.ABSENT[:-3]) + tuple(paths['sketch'] + '/' + name
        for name in ('sketch.yaml', 'sketch.yml', 'sketch.json'))
    return dict(fixed=dict(schema='fixed-recorder-delivery-upload-v1', run_id=attempt,
                          source_sha256=source_digest, output=paths['remote'] + '-upload'),
                schema_prefix='recorder-delivery-upload-', files=files, absent=absent,
                argv=['/usr/bin/arduino-cli', '--config-file', '/dev/null', 'upload',
                      '--fqbn', FQBN, '--input-file', files['raw'], paths['sketch']])


def host_binding_support(owner):
    # Host admission needs the checked pure validators, not Linux resource APIs.
    deploy = module_from('_recorder_binding_view', owner.code['tools/match_deploy.py'])
    return deploy.binding_support(owner.code[STATIC + 'capture_remote.py'])


def upload_bindings(owner, artifacts):
    uploader = module_from('_recorder_upload_contract', owner.code[UPLOADER])
    profile = upload_profile(uploader, owner.attempt, owner.source_sha256)
    value = owner.base.decode(owner.code[UPLOAD_BASELINE])
    value.update(profile['fixed'], boot_id=BOOT, absent=list(profile['absent']))
    for name, key in (('raw', 'build/' + PROJECT + '.bin'),
                      ('sketch', 'build/' + PROJECT + '.bin-zsk.bin'),
                      ('exported', 'artifacts/' + PROJECT + '.bin-zsk.bin')):
        record = artifacts['files'][key]
        value['files'][name] = dict(path=profile['files'][name],
                                   bytes=record['identity']['bytes'], sha256=record['sha256'])
    support = host_binding_support(owner)
    return uploader._checked_bindings(support, value, profile)


def remote_upload(payload, action):
    require(action in ('admit', 'upload'), 'Unknown upload operation')
    require(type(payload) is dict and set(payload) == {'sources', 'bindings', 'attempt', 'source_sha256'},
            'Invalid upload payload')
    modules = {name: module_from('_recorder_native_' + name, body.encode())
               for name, body in payload['sources'].items()}
    require(set(modules) == {'helper', 'support', 'uploader', 'adapter', 'caller'}, 'Invalid upload modules')
    uploader, support, helper = (modules[name] for name in ('uploader', 'support', 'helper'))
    profile = upload_profile(uploader, payload['attempt'], payload['source_sha256'])
    bindings = uploader._checked_bindings(support, payload['bindings'], profile)
    checked = modules['adapter']._attempt_type(uploader)(helper, support, profile, bindings, Path('/'), None, None)
    checked.report['schema'] = 'recorder-delivery-upload-result-v1'
    if action == 'upload':
        return uploader._upload(checked)
    try:
        checked.admit()
        return dict(status='ADMITTED', attempt=payload['attempt'], source_sha256=payload['source_sha256'])
    finally:
        checked.close()


def upload_program(owner, payload_sha, payload_bytes, action):
    require(action in ('admit', 'upload'), 'Unexpected upload action')
    require(type(payload_bytes) is int and 0 < payload_bytes <= 262144, 'Upload input bound')
    path = owner.remote + '/recorder-upload-inputs.json'
    program = owner.preamble() + 'path=' + repr(path) + '\nexpected=' + repr(payload_sha) + '\n'
    program += 'size=' + repr(payload_bytes) + '\naction=' + repr(action) + '\n'
    return program + '''import stat,types
fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
try:
 before=os.fstat(fd);raw=os.read(fd,size+1);after=os.fstat(fd);named=os.stat(path,follow_symlinks=False)
 stamp=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_uid!=1000:raise ValueError('Upload input ownership')
 if stamp(before)!=stamp(after) or stamp(after)!=stamp(named):raise ValueError('Upload inputs changed')
 if len(raw)!=size or hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Upload input bytes changed')
finally:os.close(fd)
payload=json.loads(raw);source=payload['sources']['caller']
module=types.ModuleType('_recorder_delivery_native');module.__file__='/sumox-source/tools/run_recorder_delivery.py'
exec(compile(source,module.__file__,'exec'),module.__dict__)
report=module.remote_upload(payload,action)
text=json.dumps(report,sort_keys=True,separators=(',',':'),allow_nan=False)
if len(text.encode())>3145728:raise ValueError('Upload result exceeds bound')
print(text)
'''


def prepare_upload(owner, artifacts, run):
    paths = dict(helper=owner._module.READER, support=STATIC + 'capture_remote.py',
                 uploader=UPLOADER, adapter=UPLOAD_ADAPTER, caller=CALLER)
    value = dict(sources={name: owner.code[path].decode() for name, path in paths.items()},
                 bindings=upload_bindings(owner, artifacts), attempt=owner.attempt,
                 source_sha256=owner.source_sha256)
    raw = canonical(value)
    require(len(raw) <= 262144, 'Upload payload exceeds bound')
    local = run / 'upload_inputs.json'
    with local.open('xb') as output:
        output.write(raw)
    destination = owner.remote + '/recorder-upload-inputs.json'
    reply, _ = owner.direct(owner.preamble() + 'path=' + repr(destination) + '\n' +
        "if os.path.lexists(path):raise ValueError('Upload payload owner exists')\nprint('{}')\n", 'upload-input-owner')
    require(not reply.stderr, 'Upload input owner stderr')
    owner.transport(['push', str(local), destination], 60, 'upload-inputs')
    reply, _ = owner.direct(upload_program(owner, sha(raw), len(raw), 'admit'), 'upload-admit')
    result = owner.base.decode(reply.stdout)
    require(not reply.stderr and result == dict(status='ADMITTED', attempt=owner.attempt,
            source_sha256=owner.source_sha256), 'Upload admission failed')
    return raw


def restored_owner(request, root=ROOT):
    owner = make_owner(request, root=root)
    owner.claimed = True
    owner.local()
    outcome = owner.base.decode(owner.base.read(owner.output / 'result.json'))
    artifacts = owner.base.decode(owner.base.read(owner.output / 'artifacts.json'))
    validate_compile(outcome, artifacts, owner.identity('ignored'))
    owner.validate_artifact_reply(json.dumps(artifacts))
    require(owner.base.read(owner.inputs_path) == owner.inputs_raw, 'Compile source snapshot differs')
    owner.manifest_saved = True
    owner.prepare()
    owner.stage_hashes = owner.base.decode(owner.base.read(owner.output / 'staged_files.json'))
    require(owner.stage_hashes == owner.expected_stage, 'Compiled source mapping differs')
    owner.artifact_sources_identity = outcome['artifact_sources_identity']
    owner.artifact_sources_attempted = owner.remote_owned = owner.source_available = owner.source_attempted = True
    owner.artifact_receipt = artifacts
    require(type(outcome.get('transport_calls')) is int and outcome['transport_calls'] > 0, 'Missing command sequence')
    owner.counter = outcome['transport_calls']
    owner.local()
    return owner, outcome, artifacts


class ReceiverCommands:
    def __init__(self, owner):
        self.owner, self.lock, self.children = owner, threading.Lock(), set()
        self.counter = 0
        self.closed = False
        self.allowed = ()
        self.cleanup_errors = []

    def evidence_owner(self, argv, timeout):
        with self.lock:
            require(not self.closed, 'Receiver command owner is closed')
            self.counter += 1
            path = self.owner.output / 'run' / ('receive_' + str(self.counter))
            path.mkdir()
        (path / 'intent.json').write_bytes(canonical(dict(argv=argv, timeout_seconds=timeout)))
        return path

    @staticmethod
    def remember(first, details, error, operation):
        details.append(dict(operation=operation, type=type(error).__name__, message=str(error)))
        return first if first is not None else error

    def read_streams(self, evidence, first, details):
        streams = []
        for name, bound in (('stdout', 33554432), ('stderr', 1048576)):
            raw = b''
            try:
                with (evidence / name).open('rb') as stream:
                    raw = stream.read(bound)
            except BaseException as error:
                first = self.remember(first, details, error, 'read_' + name)
            streams.append(raw)
        return streams[0], streams[1], first

    def finish_command(self, evidence, child, argv, timeout, first):
        details = list(getattr(first, 'receiver_secondary_errors', ()))
        stdout, stderr, first = self.read_streams(evidence, first, details)
        code = None
        try:
            code = None if child is None else child.poll()
        except BaseException as error:
            first = self.remember(first, details, error, 'poll')
        if first is None and code != 0:
            first = subprocess.CalledProcessError(code if code is not None else -1, argv, stdout, stderr)
        record = dict(returncode=code, stdout_bytes=len(stdout), stderr_bytes=len(stderr),
                      reaped=child is not None and code is not None, secondary_errors=details,
                      first_error=None if first is None else dict(type=type(first).__name__, message=str(first)))
        journal_error = None
        try:
            (evidence / 'outcome.json').write_bytes(canonical(record))
        except BaseException as error:
            journal_error = dict(type=type(error).__name__, message=str(error))
            first = self.remember(first, details, error, 'journal')
        with self.lock:
            if child is not None and code is not None:
                self.children.discard(child)
        if first is None:
            return subprocess.CompletedProcess(argv, code, stdout, stderr)
        first.receiver_secondary_errors = details
        first.output, first.stderr = stdout, stderr
        if journal_error is not None:
            first.evidence_write_error = journal_error
        wrapper = first if isinstance(first, subprocess.TimeoutExpired) else subprocess.CalledProcessError(
            code if code is not None and code != 0 else -1, argv, stdout, stderr)
        wrapper.primary_error = first
        wrapper.receiver_secondary_errors = details
        if journal_error is not None:
            wrapper.evidence_write_error = journal_error
        if wrapper is first:
            raise first
        raise wrapper from first

    def remote(self, target, args, capture=False, timeout=None):
        require(target == TARGET and capture is True and type(timeout) is int and 1 <= timeout <= 915,
                'Unexpected receive-only command')
        require(type(args) is list and any(args == command and timeout == bound
                for command, bound in self.allowed), 'Unreviewed receive-only operation')
        owner = self.owner
        argv = [owner.base.ADB, '-s', TARGET, 'shell', '-T', shlex.join(args)]
        require(len(subprocess.list2cmdline(argv).encode('utf-16-le')) // 2 + 1 <= 30000,
                'Receiver command too long')
        require(sha(Path(owner.base.ADB).read_bytes()) == owner.base.ADB_SHA, 'ADB changed')
        evidence = self.evidence_owner(argv, timeout)
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        first, child = None, None
        try:
            with (evidence / 'stdout').open('xb') as out, (evidence / 'stderr').open('xb') as err:
                with self.lock:
                    require(not self.closed, 'Receiver command owner closed before launch')
                    child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=out,
                                             stderr=err, creationflags=flags)
                    self.children.add(child)
                first = self.wait(child, out, err, timeout)
        except BaseException as error:
            details = list(getattr(first, 'receiver_secondary_errors', ()))
            first = self.remember(first, details, error, 'launch_or_stream_close')
            first.receiver_secondary_errors = details
        return self.finish_command(evidence, child, argv, timeout, first)

    def wait(self, child, out, err, timeout):
        deadline, failure, details = time.monotonic() + timeout, None, []
        try:
            while child.poll() is None:
                if os.fstat(out.fileno()).st_size > 33554432 or os.fstat(err.fileno()).st_size > 1048576:
                    failure = ValueError('Receiver transport output bound exceeded')
                    break
                if time.monotonic() >= deadline:
                    failure = subprocess.TimeoutExpired(child.args, timeout)
                    break
                time.sleep(0.05)
        except BaseException as error:
            failure = self.remember(failure, details, error, 'monitor')
        if failure is not None:
            try:
                child.kill()
            except BaseException as error:
                failure = self.remember(failure, details, error, 'kill')
        try:
            child.wait(timeout=15)
        except BaseException as error:
            failure = self.remember(failure, details, error, 'wait')
        try:
            if os.fstat(out.fileno()).st_size > 33554432 or os.fstat(err.fileno()).st_size > 1048576:
                failure = failure or ValueError('Receiver transport output bound exceeded')
        except BaseException as error:
            failure = self.remember(failure, details, error, 'output_stat')
        if failure is not None:
            failure.receiver_secondary_errors = details
        self.cleanup_errors.extend(row for row in details if row['operation'] in ('kill', 'wait'))
        return failure

    def stop(self):
        # Last-resort host deadline only. It cannot prove the remote socket closed.
        with self.lock:
            self.closed = True
            children = tuple(self.children)
        first, errors = None, []
        for index, child in enumerate(children):
            try:
                if child.poll() is None:
                    child.kill()
            except BaseException as error:
                first = first or error
                errors.append(dict(child=index, operation='kill', type=type(error).__name__, message=str(error)))
            try:
                child.wait(timeout=15)
            except BaseException as error:
                first = first or error
                errors.append(dict(child=index, operation='wait', type=type(error).__name__, message=str(error)))
        if first is not None:
            self.cleanup_errors.extend(errors)
            first.receiver_cleanup_errors = errors
            raise first


def receiver_modules(owner, commands):
    # Private imports avoid ambient tools or cached module substitution.
    import builtins
    board = types.ModuleType('_recorder_receive_board')
    board.__dict__.update(owner.board.__dict__)
    board.remote = commands.remote
    csv = module_from('_recorder_csv', owner.code['tools/validate_csv_bundle.py'],
                      owner.root / 'tools/validate_csv_bundle.py')
    original = builtins.__import__
    def importer(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and name in ('board_tool', 'validate_csv_bundle'):
            return board if name == 'board_tool' else csv
        return original(name, globals, locals, fromlist, level)
    dump = types.ModuleType('_recorder_receiver')
    dump.__file__ = str(owner.root / 'tools/dump_match.py')
    dump.__dict__['__builtins__'] = dict(vars(builtins), __import__=importer)
    sys.modules[dump.__name__] = dump  # Dataclass resolves its defining module.
    exec(compile(owner.code['tools/dump_match.py'], dump.__file__, 'exec'), dump.__dict__)
    base = dump._CONNECTION_SCHEMA + dump._CONNECTION_REMOTE
    commands.allowed = (
        (['python3', '-u', '-c', base + dump._CONNECTION_RECEIVER,
          '900', owner.attempt, 'adb', TARGET], 915),
        (['python3', '-u', '-c', base + dump._CONNECTION_OBSERVER,
          owner.attempt, 'adb', TARGET], 5))
    return dump


def arm_receiver(owner, run, dump):
    require(os.environ.get('SUMO_TRANSPORT') == 'adb' and owner.board.target() == TARGET,
            'Explicit identified ADB transport required')
    state = dict(destination=None, error=None)
    capture = dump.LiveCapture(TARGET, 900, connection_ticket=owner.attempt)
    def receive():
        try:
            state['destination'] = str(dump.save_capture(capture, run / 'capture',
                receive_mode='adb', target=TARGET, expected_session=owner.session,
                firmware_revision=owner.reviewed_head, source_sha256=owner.source_sha256,
                config_sha256=sha(owner.code['src/config.h'])))
        except BaseException as error:
            state['error'] = error
    worker = threading.Thread(target=receive, name='recorder-delivery-receiver', daemon=True)
    worker.start()
    return worker, state


def await_connection(owner, dump, worker, state):
    deadline = time.monotonic() + 20
    for unused in range(20):
        require(worker.is_alive() and state['error'] is None, 'Receiver ended before upload')
        require(time.monotonic() < deadline, 'Receiver connection deadline')
        evidence = dump.observe_connection(TARGET, owner.attempt)
        if evidence['state'] == 'CONNECTED':
            require(evidence['claim']['boot_id'] == BOOT, 'Receiver boot differs')
            return evidence
        require(evidence['state'] in ('PENDING', 'UNKNOWN'), 'Receiver terminal before upload')
        time.sleep(0.25)
    raise ValueError('Receiver connection was not observed')


def validate_synthetic_capture(capture, manifest, metadata, validation, identity, csv):
    for key in ('firmware_revision', 'source_sha256', 'config_sha256'):
        require(manifest.get(key) == identity[key], 'Capture declaration differs: ' + key)
    require(manifest.get('origin') == 'synthetic' and manifest.get('target') == TARGET and
            manifest.get('log_hz') == 25 and manifest.get('frame_capacity') == 5001 and
            manifest.get('event_capacity') == 4096, 'Unexpected synthetic recorder declaration')
    require(all(type(metadata.get(key)) is int for key in ('session', 'expected_session', 'observed_session')) and
            capture.session == identity['session'] == metadata.get('session') ==
            metadata.get('expected_session') == metadata.get('observed_session') and
            metadata.get('rejected_session') is None, 'Capture session acceptance differs')
    require(capture.origin == 1 and capture.mode == 1 and capture.log_hz == 25 and
            capture.frame_count == 5001 and capture.event_count == 8, 'Not a full synthetic recording')
    require(validation.get('format_integrity') == validation.get('consistency') == 'PASS' and
            validation.get('errors') == [] and validation.get('recording') ==
            dict(loss='NONE_REPORTED', lifecycle='SEALED', phase_code=3), 'Recorder has loss or lifecycle failure')
    summary_lines = capture.summary.decode('ascii').splitlines()
    require(len(summary_lines) == 2, 'Unexpected summary count')
    summary = csv._parse_row('summary', summary_lines[1])
    require(all(summary[name] == 0 for name in csv.LOSS_FIELDS) and summary['incomplete'] == 0 and
            summary['go_seen'] == 1 and summary['phase'] == 3 and summary['overruns'] == 0 and
            0 < summary['ticks'] and summary['tick_max_us'] < 800, 'Synthetic lifecycle/timing failure')
    require(summary['frame_count'] == 5001 and summary['event_count'] == 8 and summary['mode'] == 1,
            'Synthetic summary count/mode differs')
    frames = [csv._parse_row('frames', line) for line in capture.frames.decode('ascii').splitlines()[1:]]
    require(len(frames) == 5001 and all(row['ordinal'] == index and row['pack_status'] == 0 and
            row['mode'] == 1 and row['duty_l_127'] == row['duty_r_127'] == 0 and
            40 * index <= row['t_ms'] <= 40 * index + 2 and row['tick_max_us'] < 800
            for index, row in enumerate(frames)), 'Synthetic frame coverage/inhibition differs')
    events = [csv._parse_row('events', line) for line in capture.events.decode('ascii').splitlines()[1:]]
    expected = ((0, 1, 0, 0), (3, 1, 2, 0), (9, 5, 1, 4500000), (1, 1, 0, 5100000),
                (3, 2, 3, 5100000), (3, 3, 5, 5200000), (3, 5, 6, 5202000), (3, 6, 10, 200000000))
    require(len(events) == len(expected), 'Synthetic event count differs')
    for row, (kind, detail, value, elapsed) in zip(events, expected):
        age = (row['t_us'] - summary['release_us']) & 0xffffffff
        require((row['type'], row['detail'], row['value']) == (kind, detail, value) and
                max(0, elapsed - 2000) <= age <= elapsed + 2000, 'Synthetic event sequence/time differs')
        if kind == 1 or (kind == 3 and detail == 6):
            require(age >= elapsed, 'Countdown or full recording ended early')
    return dict(status='FULL_SYNTHETIC_PASS', frames=5001, events=8, session=capture.session,
                loss='NONE_REPORTED', lifecycle='SEALED', hardware_acceptance=False)


def accept_capture(owner, destination, dump):
    directory = dump.local_path(destination)
    require(directory.parent == owner.output / 'run/capture', 'Capture escaped run owner')
    with dump.csv._regular_input(directory / 'capture.json', 65536) as (stream, unused):
        metadata = json.loads(stream.read())
    manifest = dump.csv._read_manifest(directory / 'manifest.json')
    parser = dump.Parser(expected_session=owner.session)
    for chunk in dump.offline_chunks(directory / 'wire.txt'):
        parser.feed(chunk)
    capture = parser.finish()
    paths = {role: directory / (directory.name + '_' + role + '.csv') for role in dump.csv.ROLES}
    validation = dump.csv.validate_bundle(*(paths[role] for role in dump.csv.ROLES), directory / 'manifest.json')
    for role in dump.csv.ROLES:
        with dump.csv._regular_input(paths[role], 16777216) as (stream, unused):
            require(stream.read() == getattr(capture, role), 'CSV bytes differ from complete wire')
    identity = dict(session=owner.session, firmware_revision=owner.reviewed_head,
                    source_sha256=owner.source_sha256, config_sha256=sha(owner.code['src/config.h']))
    return validate_synthetic_capture(capture, manifest, metadata, validation, identity, dump.csv)


def close_receiver(owner, run, worker, state, dump, commands, report, started, first):
    if worker is None:
        return first
    # Let the bounded receiver preserve terminal/partial evidence, even when the
    # upload failed. The closed command latch prevents any late observer launch.
    worker.join(max(0, 960 - (time.monotonic() - started)))
    if worker.is_alive():
        first = first or TimeoutError('Receiver did not close inside run budget')
        try:
            commands.stop()
        except BaseException as error:
            report['closing_errors'].append(dict(check='receiver_reap', type=type(error).__name__, message=str(error)))
        worker.join(25)
    if worker.is_alive():
        first = first or TimeoutError('Receiver thread did not close after bounded child termination')
        report['closing_errors'].append(dict(check='receiver_thread', status='INDETERMINATE'))
    report['capture'] = state['destination']
    first = first or state['error']
    try:
        commands.stop()
        if state['destination'] is not None:
            report['capture_acceptance'] = accept_capture(owner, state['destination'], dump)
    except BaseException as error:
        first = first or error
        report['capture_acceptance_error'] = dict(type=type(error).__name__, message=str(error))
    report['receiver_cleanup_errors'] = list(commands.cleanup_errors)
    return first


def run_delivery(request, *, root=ROOT):
    owner, compiled, artifacts = restored_owner(request, root=root)
    run = claim_session(owner.root, owner.attempt)
    report = owner.identity('recorder-delivery-result-v1')
    report.update(status='FAILED', upload_attempts=0, first_error=None, closing_errors=[],
                  capture=None, capture_acceptance=None, upload=None, connection=None, framing_clean='UNKNOWN')
    first, worker, state, dump = None, None, None, None
    commands = ReceiverCommands(owner)
    started = time.monotonic()
    try:
        owner.inventory()
        owner.prerequisites()
        owner.sources()
        owner.observe_artifacts(final=True)
        payload = prepare_upload(owner, artifacts, run)
        dump = receiver_modules(owner, commands)
        worker, state = arm_receiver(owner, run, dump)
        report['connection'] = await_connection(owner, dump, worker, state)
        owner.local()
        require(time.monotonic() - started < 180, 'Run admission took too long')
        report['upload_attempts'] = 1
        reply, _ = owner.direct(upload_program(owner, sha(payload), len(payload), 'upload'), 'delivery-upload', 240)
        report['upload'] = owner.base.decode(reply.stdout)
        require(not reply.stderr and report['upload'].get('status') == 'UPLOADED' and
                type(report['upload'].get('attempts')) is int and report['upload']['attempts'] == 1 and
                report['upload'].get('first_error') is None and report['upload'].get('postcheck_errors') == [] and
                report['upload'].get('run_id') == owner.attempt and
                report['upload'].get('source_sha256') == owner.source_sha256 and
                report['upload'].get('subprocess') == dict(returncode=0, timed_out=False, reaped=True),
                'Identified upload failed')
    except BaseException as error:
        first = error
    first = close_receiver(owner, run, worker, state, dump, commands, report, started, first)
    closing = dict(final_checks=[])
    first = owner.closing(closing, first)
    report['closing_errors'].extend(row for row in closing['final_checks'] if row['status'] != 'PASS')
    report['first_error'] = None if first is None else dict(type=type(first).__name__, message=str(first))
    report['status'] = 'DELIVERED' if first is None and report['capture_acceptance'] is not None else 'FAILED'
    with (run / 'result.json').open('xb') as output:
        output.write(canonical(report))
    if first is not None:
        first.delivery_outcome = report
        raise first
    return report


def main(argv):
    request = parse_request(argv)
    require(sys.dont_write_bytecode, 'Python -B required')
    if request['action'] == '--run':
        result = run_delivery(request)
    else:
        owner = make_owner(request)
        result = owner.check() if request['action'] == '--check-only' else owner.run()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
