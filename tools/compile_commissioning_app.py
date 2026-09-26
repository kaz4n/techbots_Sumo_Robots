# Compiles one closed commissioning application profile without uploading it.
# Binds fresh owners and all current sources to a reviewed clean Git commit.
# Tested by independent D222 policy, command and controlled lifecycle cases.
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import types


ROOT = Path(__file__).absolute().parents[1]
PREDECESSOR = 'tools/compile_b4_app_static.py'
PREDECESSOR_PIN = (24356, 'b21527e2cbdb50304ef18d8edd982a5bb8eec6f633d75043bd4e323b7cc59e80')
CALLER = 'tools/compile_commissioning_app.py'
POLICY = 'tools/commissioning_app_static_policy.py'
REMOTE_HELPER = 'tools/commissioning_app_compile_remote.py'
PRIMITIVE = 'tools/b4_app_compile_remote.py'
CONTRACT = 'state/analysis/P7_commissioning_build_contract.md'
RAW = 'state/analysis/P7_commissioning_build_raw'
PARENT = '/home/arduino/sumox26_codex_build'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
PROFILES = ('b4_stand', 'p3_drive', 'p3_turn', 'p3_stop', 'p4_reactive',
            'p4_timing', 'p5_abort_timing')
REQUEST_KEYS = {'action', 'profile', 'motors_allowed', 'attempt', 'reviewed_head'}
ADDITIONAL = {CALLER, POLICY, REMOTE_HELPER, PRIMITIVE, PREDECESSOR, CONTRACT}
REQUIRED = {'state/analysis/P7_static_link_probe_raw/static_artifacts.py', 'state/analysis/P7_static_link_probe_raw/static_policy.py', 'tools/b4_app_static_policy.py', 'tools/app_motor_fault_static_policy.py', 'state/analysis/P7_b4_app_compile_contract.md', 'tools/app_motor_fault_compile_remote.py', 'state/analysis/P7_ordinary_app_static_compile_contract.md', 'tools/board_tool.py', 'state/analysis/P7_motor_fault_raw/compile_motor_fault.py', 'state/analysis/P7_static_link_probe_raw/static_remote.py', 'tools/compile_b4_app_static.py', 'state/analysis/P7_static_link_probe_raw/static_reference.json', 'tools/app_build_commands.json', 'state/analysis/P7_static_startup_raw/cli_initialization_inventory.json', 'state/analysis/P7_b4_app_policy_contract.md', 'state/analysis/P7_static_startup_raw/capture_remote.py', 'tools/compile_app_motor_fault.py', 'tools/app_build_policy.py', 'tools/b4_app_compile_remote.py', 'state/analysis/P7_static_startup_raw/cli_builtin_files_inventory.json', 'state/analysis/P7_current_app_compile_raw/compile_current_app.py', 'state/analysis/P7_static_link_probe_raw/static_native_artifacts.py', 'tools/compile_ordinary_app_static.py', 'tools/app_build_pins.json', 'tools/match_deploy.py'} | ADDITIONAL


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _selection(profile, motors_allowed, attempt):
    require(type(profile) is str and profile in PROFILES, 'Exact commissioning profile required')
    require(type(motors_allowed) is int and motors_allowed in (0, 1), 'Exact motor integer required')
    require(type(attempt) is str and re.fullmatch('[a-z][a-z0-9_]{0,23}', attempt), 'Invalid attempt')


def checked_request(value):
    require(type(value) is dict and set(value) == REQUEST_KEYS and
            all(type(key) is str for key in value), 'Invalid request fields')
    require(type(value['action']) is str and value['action'] in ('--check-only', '--execute'),
            'Invalid action')
    _selection(value['profile'], value['motors_allowed'], value['attempt'])
    require(type(value['reviewed_head']) is str and re.fullmatch('[0-9a-f]{40}', value['reviewed_head']),
            'Invalid reviewed HEAD')
    return dict(value)


def parse_request(argv):
    require(type(argv) is list and all(type(item) is str for item in argv), 'Exact argument list required')
    require(len(argv) == 9 and argv[1::2] ==
            ['--profile', '--motors-allowed', '--attempt', '--reviewed-head'],
            'Expected action --profile ID --motors-allowed 0|1 --attempt TOKEN --reviewed-head HEAD')
    require(argv[4] in ('0', '1'), 'Explicit motor integer required')
    return checked_request(dict(action=argv[0], profile=argv[2], motors_allowed=int(argv[4]),
                                attempt=argv[6], reviewed_head=argv[8]))


def build_paths(profile, motors_allowed, attempt, source_digest):
    _selection(profile, motors_allowed, attempt)
    require(type(source_digest) is str and re.fullmatch('[0-9a-f]{64}', source_digest),
            'Invalid source digest')
    digest = hashlib.sha256((source_digest + '\0' + attempt).encode('utf-8')).hexdigest()
    owner = 'commission-' + profile + '-m' + str(motors_allowed) + '-' + digest[:12]
    require(len(owner) <= 48, 'Stage owner exceeds inherited bound')
    remote, stage = PARENT + '/' + owner, 'build/stage/' + owner
    return dict(owner=owner, output=RAW + '/' + owner, stage_owner=stage, stage=stage + '/app',
                remote=remote, build=remote + '/build', artifacts=remote + '/artifacts',
                sketch=PARENT + '/' + source_digest + '/app')


def _bootstrap(root):
    path = root / PREDECESSOR
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        require((stat.S_ISREG(info.st_mode) if item == path else stat.S_ISDIR(info.st_mode)) and
                not getattr(info, 'st_file_attributes', 0) & 1024, 'Nonplain bootstrap path')
    before = path.stat()
    require(before.st_nlink == 1 and before.st_size == PREDECESSOR_PIN[0], 'Invalid bootstrap identity')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(PREDECESSOR_PIN[0] + 1)
        closed = os.fstat(stream.fileno())
    stamp = lambda info: (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
                         info.st_size, info.st_mtime_ns)
    require(stamp(before) == stamp(opened) == stamp(closed) == stamp(path.stat()) and
            len(raw) == PREDECESSOR_PIN[0] and hashlib.sha256(raw).hexdigest() == PREDECESSOR_PIN[1],
            'Checked D214 bootstrap changed')
    module = types.ModuleType('_sumox_commissioning_checked_d214')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def _head_bytes(root, head, names):
    ordered = sorted(names)
    request = ''.join(head + ':' + name + '\n' for name in ordered).encode('utf-8')
    result = subprocess.run(['git', '-C', str(root), 'cat-file', '--batch'], input=request,
                            capture_output=True, timeout=30, check=True)
    require(not result.stderr and len(result.stdout) <= 8388608, 'Invalid reviewed Git blob response')
    offset, bodies = 0, {}
    for name in ordered:
        end = result.stdout.find(b'\n', offset)
        require(end >= offset, 'Missing reviewed Git blob header')
        fields = result.stdout[offset:end].split()
        require(len(fields) == 3 and fields[1] == b'blob' and fields[2].isdigit(),
                'Missing ordinary reviewed file: ' + name)
        size = int(fields[2])
        require(0 <= size <= 1048576, 'Reviewed file exceeds bound')
        start, offset = end + 1, end + 2 + size
        require(offset <= len(result.stdout) and result.stdout[offset - 1:offset] == b'\n',
                'Truncated reviewed file')
        bodies[name] = result.stdout[start:offset - 1]
    require(offset == len(result.stdout), 'Trailing reviewed Git blob response')
    return bodies


def _flags(profile, motors_allowed):
    macros = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
              'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
              'SUMOX_P5_ABORT_TIMING', 'SUMOX_MOTOR_FAULT_PROBE')
    active = dict(b4_stand=(0,), p3_drive=(1,), p3_turn=(2,), p3_stop=(3,),
                  p4_reactive=(4,), p4_timing=(4, 5), p5_abort_timing=(6,))[profile]
    values = [('MATCH', 0), ('MOTORS_ALLOWED', motors_allowed)]
    values.extend((name, int(index in active)) for index, name in enumerate(macros))
    return ' '.join('-D' + name + '=' + str(value) for name, value in values)


class CommissioningMixin:
    def __init__(self, reviewed_head, *, root=ROOT):
        module, request = self._module, self._request
        require(type(reviewed_head) is str and reviewed_head == request['reviewed_head'],
                'Constructor reviewed HEAD differs')
        super().__init__(reviewed_head, root=root)
        self.profile, self.motors_allowed = request['profile'], request['motors_allowed']
        self.attempt, self.manifest_saved = request['attempt'], False
        names = self.source_names()
        bodies = {name: self.base.read(self.root / name) for name in names}
        _, source = self.source_mapping(bodies, names)
        paths = build_paths(self.profile, self.motors_allowed, self.attempt, source)
        require(module.CONFIGURED_SOURCE in (None, source), 'Configured source changed')
        module.CONFIGURED_SOURCE = source
        module.ATTEMPT, module.REMOTE = paths['owner'], paths['remote']
        self.stage_attempt, self.source_sha256 = paths['owner'], source
        self.output, self.stage_owner = self.root / paths['output'], self.root / paths['stage_owner']
        self.stage_path, self.inputs_path = self.root / paths['stage'], self.output / 'inputs.json'
        self.remote, self.build_path, self.artifacts = paths['remote'], paths['build'], paths['artifacts']
        self.sketch, self.boot, self.flags = paths['sketch'], BOOT, module.FLAGS

    def admission(self):
        module, request = self._module, self._request
        names = self.source_names()
        code = {name: self.base.read(self.root / self.base.relative(name))
                for name in sorted(module.REQUIRED | names)}
        require(sum(len(code[name]) for name in names) <= 4194304, 'Source byte bound exceeded')
        for name, expected in module.HARD_PINS.items():
            require(module.sha(code[name]) == expected, 'Frozen primitive changed: ' + name)
        if self.inputs_raw is None:
            require(code == _head_bytes(self.root, self.reviewed_head, set(code)),
                    'Current input bytes differ from reviewed HEAD')
        mapped, source = self.source_mapping(code, names)
        require(source == self.source_sha256 == module.CONFIGURED_SOURCE, 'Selected source changed')
        self.base.checked_wait(code[module.SUPPORT])
        view = self.base.module_from(self.root, 'tools/match_deploy.py', code['tools/match_deploy.py'])
        require(view.app_source_hash(self.root) == source, 'Source helper digest differs')
        value = dict(schema='commissioning-app-static-inputs-v1', profile=self.profile,
            motors_allowed=self.motors_allowed, attempt=self.attempt, reviewed_head=self.reviewed_head,
            source_sha256=source, boot_id=BOOT, files={name: module.sha(body) for name, body in code.items()})
        raw = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode('utf-8')
        require(self.inputs_raw is None or self.inputs_raw == raw, 'Input manifest changed')
        if self.manifest_saved:
            require(self.base.read(self.inputs_path) == self.inputs_raw, 'Saved input bytes changed')
        self.inputs_raw, self.inputs, self.code, self.expected_stage = raw, value, code, mapped
        self.base.BOOT = self.boot
        if self.executor is not None:
            require(self.executor['BOOT'] == self.boot, 'Executor boot changed')

    def identity(self, schema):
        module, request = self._module, self._request
        return dict(schema=schema, profile=self.profile, motors_allowed=self.motors_allowed,
            attempt=self.attempt, project=module.PROJECT, fqbn=module.FQBN, flags=self.flags,
            reviewed_head=self.reviewed_head, source_sha256=self.source_sha256, boot_id=self.boot)

    def check(self):
        module, request = self._module, self._request
        result = super().check()
        result.update(self.identity('commissioning-app-static-check-v1'), board_observed=False)
        return result

    def claim(self):
        module, request = self._module, self._request
        self.output.mkdir(mode=0o700)
        self.claimed = True
        self.save('inputs.json', self.inputs)
        self.manifest_saved = True
        intent = self.identity('commissioning-app-static-intent-v1')
        intent.update(inputs_sha256=module.sha(self.inputs_raw), stage=str(self.stage_path),
                      remote=self.remote, sketch=self.sketch, started_utc=datetime.now(timezone.utc).isoformat())
        self.save('intent.json', intent)

    def static_policy(self):
        module, request = self._module, self._request
        self.local()
        policy = self.base.module_from(self.root, POLICY, self.code[POLICY])
        require(policy.safety_flags(self.profile, motors_allowed=self.motors_allowed) == self.flags,
                'Caller and checked policy flags differ')
        snapshots = {path: self.code[path] for path in module.SNAPSHOT_PATHS.values()}
        values = dict(profile=self.profile, motors_allowed=self.motors_allowed, snapshots=snapshots)
        return types.SimpleNamespace(
            validate_preflight=lambda text, **kwargs: policy.validate_preflight(text, **kwargs, **values),
            validate_compile_result=lambda text, **kwargs: policy.validate_compile_result(text, **kwargs, **values))

    def artifact_program(self):
        module, request = self._module, self._request
        program = super().artifact_program()
        old = "result=module.inspect_artifacts(REMOTE+'/build',REMOTE+'/artifacts',bundle)"
        require(program.count(old) == 1, 'Inherited artifact call changed')
        args = dict(profile=self.profile, motors_allowed=self.motors_allowed,
                    attempt=self.attempt, source_digest=self.source_sha256)
        return program.replace(old, old[:-1] + ',**' + repr(args) + ')')

    def validate_layout(self, value, records):
        module, request = self._module, self._request
        require(type(value) is dict and value.get('status') == 'STATIC_COMMISSIONING_APP_LAYOUT_PACKAGE_PASS'
                and type(value.get('profile')) is str and value['profile'] == self.profile
                and type(value.get('motors_allowed')) is int and value['motors_allowed'] == self.motors_allowed,
                'Artifact profile identity differs')
        normalized = dict(value, status='STATIC_B4_APP_LAYOUT_PACKAGE_PASS', motors_allowed=0)
        del normalized['profile']
        return super().validate_layout(normalized, records)

    def validate_artifact_reply(self, text):
        module, request = self._module, self._request
        require(type(text) is str and len(text.encode()) <= 1048576, 'Invalid artifact response')
        value = self.base.decode(text)
        require(type(value) is dict and value.get('schema') == 'commissioning-app-static-artifacts-v1',
                'Invalid artifact schema')
        expected = dict(profile=self.profile, motors_allowed=self.motors_allowed,
                        attempt=self.attempt, source_sha256=self.source_sha256)
        require(all(type(value.get(key)) is type(item) and value[key] == item
                    for key, item in expected.items()), 'Artifact request identity differs')
        normalized = {key: item for key, item in value.items() if key not in expected}
        normalized['schema'] = 'b4-app-m0-static-artifacts-v1'
        super().validate_artifact_reply(json.dumps(normalized, separators=(',', ':')))
        return value

    def run(self):
        module, request = self._module, self._request
        self.check()
        self.prepare()
        report = self.identity('commissioning-app-static-compile-outcome-v1')
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


def _owner_type(module, request):
    return type('CompileDiagnostic', (CommissioningMixin, module.CompileDiagnostic),
                dict(_module=module, _request=dict(request)))


def load_caller(request, *, root=ROOT):
    request, root = checked_request(request), Path(root).absolute()
    bootstrap = _bootstrap(root)
    module = bootstrap.load_caller(root=root)
    require(set(module.REQUIRED) | ADDITIONAL == REQUIRED, 'Inherited dependency set changed')
    module.REQUIRED = set(REQUIRED)
    module.HARD_PINS = dict(module.HARD_PINS, **{PREDECESSOR: PREDECESSOR_PIN[1]})
    module.BUNDLE_PATHS = dict(module.BUNDLE_PATHS, policy=POLICY, primitive=PRIMITIVE)
    module.REMOTE_HELPER, module.RAW, module.CONTRACT = REMOTE_HELPER, RAW, CONTRACT
    module.FLAGS = _flags(request['profile'], request['motors_allowed'])
    module.CONFIGURED_SOURCE = None
    module.CompileDiagnostic = _owner_type(module, request)
    return module


def make_owner(request, *, root=ROOT):
    request = checked_request(request)
    return load_caller(request, root=root).CompileDiagnostic(request['reviewed_head'], root=root)


def main(argv):
    request = parse_request(argv)
    require(sys.dont_write_bytecode, 'Python -B required')
    owner = make_owner(request, root=ROOT)
    try:
        result = owner.check() if request['action'] == '--check-only' else owner.run()
    except Exception as error:
        print(json.dumps(getattr(error, 'compile_outcome', dict(status='FAILED', first_error=dict(
            type=type(error).__name__, message=str(error)))), indent=2), file=sys.stderr)
        raise
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
