# Admits one D222 commissioning upload against exact source and external evidence.
# Separates inhibited diagnostics from physically qualified, authorized motor runs.
# Independent D227 tests cover Git blobs, closed profiles and consumed attempts.
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
CALLER = 'tools/deploy_commissioning_app.py'
ADAPTER = 'tools/commissioning_app_upload.py'
CONTRACT = 'state/analysis/P7_commissioning_deploy_contract.md'
COMPILER = 'tools/compile_commissioning_app.py'
BASE = 'tools/match_deploy.py'
STATIC = 'state/analysis/P7_static_startup_raw/'
UPLOADER = STATIC + 'upload_remote.py'
INHERITED = 'tools/match_upload.py'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
FROZEN = {
    BASE: '3acacad6e95aff1012e9d0d1f8ef60905c026ebe865569fdb71384abd607d2a9',
    COMPILER: '038a74777db7d26a15ff543d311fc4df2503e6f6b8e3b08fabcfb1c853220462',
    INHERITED: '777a2f29a326094c34298f07d3597eb603bf3487f8780f18c5da122bb527d9be'}
RECEIPTS = dict(inputs='inputs.json', intent='intent.json', staged_files='staged_files.json',
    result='result.json', artifacts='artifacts.json', compile_command='compile/compile.command.json',
    compile_stdout='compile/compile.stdout.json', compile_stderr='compile/compile.stderr.txt',
    properties_command='compile/properties.command.json', properties_stdout='compile/properties.stdout.json',
    properties_stderr='compile/properties.stderr.txt')
GRANTS = ('OPPONENTS', 'ADC_PAIR', 'QTR_EXCLUSIVE_PADS', 'IMU_ENABLED',
    'IMU_POWER_CONFIRMED', 'IMU_MOUNTING_CONFIRMED', 'DEFAULT_LINE_THRESHOLDS',
    'MATRIX_ENABLED', 'MATRIX_NORMAL_STARTUP', 'MATRIX_EXCLUSIVE_OWNER', 'DUMP_ENABLED',
    'DUMP_SETUP_PHASE', 'DUMP_EXCLUSIVE_UART', 'DUMP_READY_PIN_OWNED', 'DUMP_FRAMING_CLEAN',
    'LOCAL_SERVICE_RESET', 'CALIBRATION_OUTPUT')
CHECKS = ('pinmap', 'electrical', 'buttons', 'battery', 'line_calibration',
          'motor_inhibition', 'profile_parameters', 'source_clock')
GATES = dict(b4_stand='GATE P1 PASS', p3_drive='GATE P2 PASS', p3_turn='GATE P2 PASS',
    p3_stop='GATE P2 PASS', p4_reactive='GATE P3 PASS', p4_timing='GATE P3 PASS',
    p5_abort_timing='GATE P4 PASS')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_request(argv):
    require(type(argv) is list and all(type(item) is str for item in argv) and len(argv) == 5 and
            argv[0] in ('--check-only', '--execute') and argv[1::2] == ['--scope', '--reviewed-head'],
            'Expected action --scope RELATIVE_JSON --reviewed-head HEAD')
    require(re.fullmatch('[0-9a-f]{40}', argv[4]), 'Invalid reviewed HEAD')
    require(argv[2] and not Path(argv[2]).is_absolute(), 'Relative scope required')
    return dict(action=argv[0], scope=argv[2], reviewed_head=argv[4])


def bootstrap(root):
    path = root / BASE
    for node in (path, *path.parents):
        info = node.lstat()
        require((stat.S_ISREG(info.st_mode) if node == path else stat.S_ISDIR(info.st_mode)) and
                not getattr(info, 'st_file_attributes', 0) & 1024, 'Nonplain bootstrap path')
    before = path.stat()
    require(before.st_nlink == 1 and 0 < before.st_size <= 65536, 'Invalid bootstrap size/link')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(65537)
        after = os.fstat(stream.fileno())
    stamp = lambda item: (item.st_dev, item.st_ino, item.st_mode, item.st_nlink,
                          item.st_size, item.st_mtime_ns)
    require(stamp(before) == stamp(opened) == stamp(after) == stamp(path.stat()) and
            hashlib.sha256(raw).hexdigest() == FROZEN[BASE], 'Frozen bootstrap changed')
    module = types.ModuleType('_commissioning_deploy_primitives')
    module.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def pinned(base, root, pin, *, empty=False, limit=4194304):
    base.keys(pin, ('path', 'bytes', 'sha256'))
    base.hexadecimal(pin['sha256'], 64)
    require(type(pin['bytes']) is int and (0 if empty else 1) <= pin['bytes'] <= limit,
            'Invalid evidence size')
    raw = base.read_file(root, pin['path'], limit)
    require((root / pin['path']).stat().st_nlink == 1 and len(raw) == pin['bytes'] and
            base.sha(raw) == pin['sha256'], 'Pinned evidence changed')
    return raw


def checked_code(base, root, reviewed_head):
    names = {CALLER, ADAPTER, CONTRACT, COMPILER, INHERITED, BASE, 'tools/board_tool.py'} | set(base.FIXED)
    code = {name: base.read_file(root, name) for name in names}
    for name, expected in {**base.FIXED, **FROZEN}.items():
        require(base.sha(code[name]) == expected, 'Frozen source changed: ' + name)
    compiler = base.load_module(root, COMPILER, code[COMPILER])
    require(code == compiler._head_bytes(root, reviewed_head, names), 'Deployment software HEAD differs')
    return code, compiler


def git_clean(root, reviewed_head, output=None):
    def git(args):
        value = subprocess.run(['git', '-C', str(root), *args], stdin=subprocess.DEVNULL,
                               capture_output=True, timeout=30, check=True)
        require(not value.stderr and len(value.stdout) <= 1048576, 'Invalid Git response')
        return value.stdout.decode('utf-8')
    require(git(['rev-parse', 'HEAD']).strip() == reviewed_head, 'Reviewed deployment HEAD changed')
    rows = [row for row in git(['status', '--porcelain=v1', '-z', '--untracked-files=all']).split('\0') if row]
    prefix = None if output is None else output.relative_to(root).as_posix() + '/'
    require(all(prefix and row.startswith('?? ' + prefix) for row in rows), 'Deployment tree is not clean')


def checked_request(base, adapter, request, target, transport):
    base.keys(request, ('profile', 'motors_allowed', 'mode', 'compile_attempt', 'run_id',
        'source_commit', 'source_sha256', 'config_sha256', 'startup', 'target', 'transport',
        'bindings', 'build_receipts', 'qualification'))
    selection = adapter.checked_selection({name: request[name] for name in adapter.SELECTION})
    base.hexadecimal(request['source_commit'], 40)
    base.hexadecimal(request['config_sha256'], 64)
    mode = 'inhibited_diagnostic' if request['motors_allowed'] == 0 else 'operational_commissioning'
    require(type(request['mode']) is str and request['mode'] == mode and request['startup'] == 'default',
            'Wrong commissioning mode/startup')
    pattern = r'[A-Za-z0-9][A-Za-z0-9_.:-]*' if transport == 'adb' else r'[A-Za-z0-9_][A-Za-z0-9_.@-]*'
    require(type(target) is str and re.fullmatch(pattern, target) and type(transport) is str and
            transport in ('adb', 'ssh') and request['target'] == target and request['transport'] == transport,
            'Configured target/transport differs')
    return selection


def compile_owner(base, compiler, root, request):
    args = dict(action='--check-only', profile=request['profile'], motors_allowed=request['motors_allowed'],
                attempt=request['compile_attempt'], reviewed_head=request['source_commit'])
    owner = compiler.make_owner(args, root=root)
    owner.admission()
    require(owner.source_sha256 == request['source_sha256'] and owner.boot == BOOT and
            base.sha(owner.code['src/config.h']) == request['config_sha256'], 'Compiled source/config differs')
    # admission compares the complete current input set to actual commit blobs.
    return owner


def checked_receipts(base, root, request, owner):
    base.keys(request['build_receipts'], RECEIPTS)
    documents, prefix = {}, owner.output.relative_to(root).as_posix() + '/'
    for role, leaf in RECEIPTS.items():
        pin = request['build_receipts'][role]
        require(type(pin) is dict and pin.get('path') == prefix + leaf, 'Wrong compile receipt path')
        documents[role] = pinned(base, root, pin, empty=role.endswith('_stderr'))
    require(documents['inputs'] == owner.inputs_raw, 'Complete compile input manifest differs')
    require(base.decode(documents['staged_files']) == owner.expected_stage, 'Compiled source mapping differs')
    require(not documents['compile_stderr'] and not documents['properties_stderr'], 'Compile stderr not empty')
    identity = owner.identity('commissioning-app-static-compile-outcome-v1')
    result = base.decode(documents['result'])
    require(all(type(result.get(key)) is type(value) and result[key] == value
                for key, value in identity.items()), 'Compile result identity differs')
    require(result.get('status') == 'COMPILE_CHECKED' and result.get('first_error') is None and
            all(type(result.get(key)) is int and result[key] == 1 for key in ('query_calls', 'compiler_calls')),
            'Compile did not close successfully exactly once')
    checks = ('local', 'identity', 'initialization', 'builtins', 'remote_sources',
              'installed_pins', 'overrides', 'artifacts', 'artifact_sources')
    require(result.get('final_checks') == [dict(name=name, status='PASS', error=None) for name in checks] and
            result.get('artifacts') == owner.artifacts,
            'Incomplete compile closure')
    intent = base.decode(documents['intent'])
    expected = owner.identity('commissioning-app-static-intent-v1')
    expected.update(inputs_sha256=base.sha(documents['inputs']), remote=owner.remote, sketch=owner.sketch)
    base.keys(intent, (*expected, 'stage', 'started_utc'))
    require(all(type(intent[key]) is type(value) and intent[key] == value for key, value in expected.items()),
            'Compile intent differs')
    require(type(intent['stage']) is str and intent['stage'].replace('\\', '/').endswith(
        '/build/stage/' + owner.stage_attempt + '/app'), 'Compile stage intent differs')
    base.utc(intent['started_utc'])
    require(base.utc(result['finished_utc']) >= base.utc(result['started_utc']), 'Compile UTC ordering differs')
    artifacts = owner.validate_artifact_reply(documents['artifacts'].decode('utf-8'))
    checked_compile_metadata(base, root, owner, documents)
    return artifacts


def checked_compile_metadata(base, root, owner, documents):
    common = base.policy_snapshot(root, owner.code)
    command = ['arduino-cli', 'compile', '--json', '--fqbn', owner.fqbn,
        '--build-path', owner.build_path, '--output-dir', owner.artifacts,
        '--build-property', 'compiler.cpp.extra_flags=' + owner.flags,
        '--build-property', 'compiler.c.extra_flags=' + owner.flags,
        '--build-property', 'build.library_discovery_phase_flag=' + common.DISCOVERY, owner.sketch]
    require(base.decode(documents['compile_command']) == command and
            base.decode(documents['properties_command']) == [*command[:-1], '--show-properties=expanded', command[-1]],
            'Compile/query commands differ')
    policy = base.load_module(root, 'tools/commissioning_app_static_policy.py',
                              owner.code['tools/commissioning_app_static_policy.py'])
    snapshots = {name: owner.code[name] for name in policy.SNAPSHOT_PINS}
    args = dict(build_path=owner.build_path, data_dir='/home/arduino/.arduino15',
                profile=owner.profile, motors_allowed=owner.motors_allowed, snapshots=snapshots)
    policy.validate_preflight(documents['properties_stdout'].decode('utf-8'), **args)
    policy.validate_compile_result(documents['compile_stdout'].decode('utf-8'), **args)


def config_literals(raw):
    text = re.sub(r'/\*.*?\*/|//[^\n]*', '', raw.decode('utf-8'), flags=re.S)
    require(not re.search(r'^\s*#\s*(?:define|undef).*\b(?:APP_GRANT_|APP_IMU_BODY_AXIS|APP_DUMP_ORIGIN|BUTTON_WINDOWS)',
                          text, re.M), 'Config macro override is unsupported')
    expected = {'APP_GRANT_' + name for name in GRANTS}
    require(set(re.findall(r'\bAPP_GRANT_[A-Z0-9_]+\b', text)) == expected, 'Unsupported setup grant set')
    values = {}
    for name in (*sorted(expected), 'APP_DUMP_ORIGIN', 'BUTTON_WINDOWS_CONFIGURED'):
        rows = re.findall(r'\binline\s+constexpr\s+std::uint32_t\s+' + name + r'\s*=\s*([0-9]+)U\s*;', text)
        require(len(rows) == 1, 'Unsupported or duplicate config literal: ' + name)
        values[name] = int(rows[0])
    require(all(values[name] in (0, 1) for name in expected) and values['APP_DUMP_ORIGIN'] in (0, 1, 2)
            and values['BUTTON_WINDOWS_CONFIGURED'] in (0, 1), 'Invalid config literal values')
    rows = re.findall(r'\binline\s+constexpr\s+std::int32_t\s+APP_IMU_BODY_AXIS\[3\]\s*=\s*'
                      r'\{\s*(-?[0-3])\s*,\s*(-?[0-3])\s*,\s*(-?[0-3])\s*\}\s*;', text)
    require(len(rows) == 1, 'Unsupported or duplicate mounting literal')
    values['APP_IMU_BODY_AXIS'] = [int(item) for item in rows[0]]
    return values


def evidence_list(base, root, value):
    require(type(value) is list and 1 <= len(value) <= 16, 'Missing bounded physical evidence')
    for pin in value:
        pinned(base, root, pin, limit=1048576)


def physical_check(base, root, value):
    base.keys(value, ('verdict', 'evidence'))
    require(value['verdict'] == 'PHYSICALLY_ACCEPTED', 'Physical acceptance is absent')
    evidence_list(base, root, value['evidence'])


def checked_qualification(base, root, request, config):
    enabled = {name for name, value in config.items() if name.startswith('APP_GRANT_') and value == 1}
    if request['motors_allowed'] == 0:
        require(request['qualification'] is None and not enabled and config['APP_IMU_BODY_AXIS'] == [0, 0, 0]
                and config['APP_DUMP_ORIGIN'] == 0, 'M0 diagnostic requires all setup grants absent')
        return None
    require({'APP_GRANT_OPPONENTS', 'APP_GRANT_ADC_PAIR', 'APP_GRANT_QTR_EXCLUSIVE_PADS'} <= enabled and
            config['BUTTON_WINDOWS_CONFIGURED'] == 1, 'Operational setup remains unconfigured')
    value = base.decode(pinned(base, root, request['qualification'], limit=65536))
    base.keys(value, ('schema', 'operation_image_sha256', 'operation', 'verdict', 'reviewer',
                     'limitations', 'checks', 'grants', 'gate', 'turn_basis'))
    operation = 'stand' if request['profile'] == 'b4_stand' else 'ring'
    image = {key: item for key, item in request.items() if key != 'qualification'}
    require(value['schema'] == 'commissioning-operation-qualification-v1' and
            value['verdict'] == 'QUALIFIED_FOR_IDENTIFIED_OPERATION' and value['operation'] == operation and
            value['operation_image_sha256'] == base.sha(base.canonical(image)), 'Qualification operation/image differs')
    require(type(value['reviewer']) is str and value['reviewer'].strip() and
            type(value['limitations']) is list and all(type(item) is str for item in value['limitations']),
            'Missing qualification disposition')
    base.keys(value['checks'], CHECKS)
    base.keys(value['grants'], enabled)
    for check in (*value['checks'].values(), *value['grants'].values()):
        physical_check(base, root, check)
    gate = value['gate']
    base.keys(gate, ('reply', 'message_ref', 'evidence'))
    require(gate['reply'] == GATES[request['profile']] and type(gate['message_ref']) is str and
            gate['message_ref'].strip(), 'Required human phase gate is absent')
    evidence_list(base, root, gate['evidence'])
    checked_turn(request['profile'], value['turn_basis'], enabled, config)
    return value


def checked_turn(profile, basis, enabled, config):
    require(type(basis) is str and basis in (('imu_accuracy', 'timed_fallback') if profile == 'p3_turn'
                                           else ('not_applicable',)), 'Turn evidence basis is missing')
    if basis == 'imu_accuracy':
        require({'APP_GRANT_IMU_ENABLED', 'APP_GRANT_IMU_POWER_CONFIRMED',
                 'APP_GRANT_IMU_MOUNTING_CONFIRMED'} <= enabled and
                sorted(abs(item) for item in config['APP_IMU_BODY_AXIS']) == [1, 2, 3],
                'IMU accuracy needs accepted power/mounting/axis configuration')


def checked_authorization(base, root, scope, now):
    request = scope['request']
    if request['motors_allowed'] == 0:
        require(scope['authorization'] is None, 'M0 diagnostic carries no motor authority')
        return
    value = base.decode(pinned(base, root, scope['authorization'], limit=65536))
    base.keys(value, ('schema', 'request_sha256', 'reply', 'message_ref', 'issued_utc', 'expires_utc'))
    reply = 'STAND OK' if request['profile'] == 'b4_stand' else 'RING OK'
    require(value['schema'] == 'commissioning-human-authorization-v1' and value['reply'] == reply and
            value['request_sha256'] == base.sha(base.canonical(request)) and
            type(value['message_ref']) is str and value['message_ref'].strip(), 'Specific human authorization absent')
    issued, expires = base.utc(value['issued_utc']), base.utc(value['expires_utc'])
    require(0 < (expires - issued).total_seconds() <= 3600 and issued <= now < expires,
            'Specific human authorization is stale, future or too long-lived')


def checked_bindings(base, root, code, adapter, request, selection, artifacts, owner):
    uploader = base.load_module(root, UPLOADER, code[UPLOADER])
    support = base.binding_support(code[STATIC + 'capture_remote.py'])
    profile = adapter.commissioning_profile(uploader, support, **selection)
    bindings = uploader._checked_bindings(support, request['bindings'], profile)
    require(bindings['boot_id'] == BOOT, 'Compile/upload boot differs')
    for role, leaf in (('raw', 'build/app.ino.bin'), ('sketch', 'build/app.ino.bin-zsk.bin'),
                       ('exported', 'artifacts/app.ino.bin-zsk.bin')):
        record, pin = artifacts['files'][leaf], bindings['files'][role]
        require(pin['sha256'] == record['sha256'] and pin['bytes'] == record['identity']['bytes'],
                'Upload artifact differs from complete D222 receipt')
    loader, pin = artifacts['loader'], bindings['files']['loader']
    require(pin['sha256'] == loader['sha256'] and pin['bytes'] == loader['identity']['bytes'],
            'Upload loader differs from compile layout')
    common = base.policy_snapshot(root, owner.code)
    installed = common.installed_pins('/home/arduino/.arduino15')
    for pin in bindings['files'].values():
        require(pin['path'] not in installed or pin['sha256'] == installed[pin['path']],
                'Upload installed dependency differs from compile inputs')
    require(all(bindings['files']['sketch'][key] == bindings['files']['exported'][key]
                for key in ('bytes', 'sha256')), 'Packaged/exported bytes differ')
    return profile


def load_scope(root, relative, reviewed_head, target, transport, *, now=None, _output=None):
    root = Path(root).absolute()
    base = bootstrap(root)
    base.hexadecimal(reviewed_head, 40)
    git_clean(root, reviewed_head, _output)
    raw = base.read_file(root, relative, 65536)
    scope = base.decode(raw)
    base.keys(scope, ('schema', 'request', 'authorization'))
    require(scope['schema'] == 'commissioning-app-deploy-v1', 'Unknown deployment schema')
    code, compiler = checked_code(base, root, reviewed_head)
    adapter = base.load_module(root, ADAPTER, code[ADAPTER])
    request = scope['request']
    selection = checked_request(base, adapter, request, target, transport)
    owner = compile_owner(base, compiler, root, request)
    artifacts = checked_receipts(base, root, request, owner)
    profile = checked_bindings(base, root, code, adapter, request, selection, artifacts, owner)
    config = config_literals(owner.code['src/config.h'])
    for name, body in owner.code.items():
        if name.startswith('src/'):
            require(not re.search(rb'^\s*#\s*(?:define|undef)\s+(?:APP_GRANT_[A-Z0-9_]+|APP_IMU_BODY_AXIS|APP_DUMP_ORIGIN)\b',
                                  body, re.M), 'Source overrides setup declarations')
    qualification = checked_qualification(base, root, request, config)
    checked_authorization(base, root, scope, base.current_time(now))
    return dict(root=root, relative=relative, reviewed_head=reviewed_head, request=request,
        selection=selection, profile=profile, scope_sha256=base.sha(raw),
        request_sha256=base.sha(base.canonical(request)), code=code, compiler_owner=owner,
        qualification=qualification, base=base, adapter=adapter)


def output_path(scope):
    return scope['root'] / 'state/analysis' / ('commissioning_deploy_' + scope['request']['run_id'])


def check_only(board, relative, reviewed_head, *, now=None):
    scope = load_scope(board.ROOT, relative, reviewed_head, board.target(), board.transport(), now=now)
    base, request = scope['base'], scope['request']
    require(not os.path.lexists(output_path(scope)), 'Commissioning deployment attempt is consumed')
    base.plain(output_path(scope).parent, directory=True)
    require(shutil.disk_usage(scope['root']).free >= 134217728, 'Less than 128MiB free for evidence')
    return dict(schema='commissioning-app-deploy-check-v1', status='ADMITTED_LOCAL', board_observed=False,
        **{key: request[key] for key in ('mode', 'profile', 'motors_allowed', 'source_sha256', 'run_id')},
        **{key: scope[key] for key in ('scope_sha256', 'request_sha256', 'reviewed_head')})


def prepare(board, scope):
    base, code, request = scope['base'], scope['code'], scope['request']
    sources = dict(helper=code[base.HELPER], support=code[STATIC + 'capture_remote.py'],
                   upload=code[UPLOADER], inherited_adapter=code[INHERITED], adapter=code[ADAPTER])
    native = ([board.adb_executable(), '-s', request['target'], 'shell', '-T']
              if request['transport'] == 'adb' else ['ssh', *board.SSH_OPTIONS, request['target']])
    command = scope['adapter'].build_command(sources, request['bindings'], scope['selection'], native)
    helpers = base.load_module(scope['root'], STATIC + 'startup_run.py', code[STATIC + 'startup_run.py'])
    return command, helpers.projection, base.prerequisites(scope)


def revalidate(board, scope, output, now):
    current = load_scope(board.ROOT, scope['relative'], scope['reviewed_head'], board.target(), board.transport(),
                         now=now, _output=output)
    require(current['scope_sha256'] == scope['scope_sha256'] and
            current['request_sha256'] == scope['request_sha256'] and current['code'] == scope['code'],
            'Deployment inputs changed after admission')


def closing(board, scope, items, projection, output, identity, outcome, now):
    base, errors = scope['base'], []
    operations = [('local', lambda: revalidate(board, scope, output, now)),
                  ('owner', lambda: base.check_owner(output, identity))]
    operations.extend((item[0], lambda item=item: base.check_prerequisite(
        board, scope, item, 'after', outcome, projection)) for item in items)
    for name, operation in operations:
        try:
            operation()
        except BaseException as error:
            outcome['postcheck_errors'].append(dict(check=name, **base.error_record(error)))
            errors.append(error)
    return errors


def upload_precompiled(board, relative, reviewed_head, *, now=None):
    check_only(board, relative, reviewed_head, now=now)
    scope = load_scope(board.ROOT, relative, reviewed_head, board.target(), board.transport(), now=now)
    base, request = scope['base'], scope['request']
    command, projection, items = prepare(board, scope)
    board.require_transport(sync=False)
    revalidate(board, scope, None, now)
    output = output_path(scope)
    output.mkdir(mode=0o700)
    identity = base.owner_identity(output)
    outcome = base.new_outcome(scope, now)
    outcome.update(schema='commissioning-app-deploy-outcome-v1',
                   **{key: request[key] for key in ('profile', 'motors_allowed', 'mode')})
    first = None
    try:
        base.write_exclusive(output / 'attempt.json', dict(schema='commissioning-app-attempt-v1',
            request=request, request_sha256=scope['request_sha256'], scope_sha256=scope['scope_sha256'],
            reviewed_head=reviewed_head, argv_sha256=base.sha(base.canonical(command)),
            started_utc=base.current_time(now).isoformat()))
        for item in items:
            base.check_prerequisite(board, scope, item, 'before', outcome, projection)
        revalidate(board, scope, output, now)
        base.check_owner(output, identity)
        outcome['attempts'] = 1
        text = base.command(board, request['target'], command, 240, 'upload', outcome)
        outcome['remote_result'] = scope['adapter'].validate_reply(text, scope['selection'], command[-2])
    except BaseException as error:
        first = error
    errors = closing(board, scope, items, projection, output, identity, outcome, now)
    first = first or (errors[0] if errors else None)
    outcome.update(first_error=None if first is None else base.error_record(first),
                   finished_utc=base.current_time(now).isoformat())
    outcome['status'] = ('ACCEPTED' if first is None and outcome['remote_result'] is not None else
                         ('UNKNOWN' if outcome['attempts'] else 'FAILED'))
    base.save_outcome(board, output, identity, outcome, first)
    return outcome


def main(argv):
    request = parse_request(argv)
    require(sys.flags.isolated and sys.dont_write_bytecode, 'Python -I -B required')
    base = bootstrap(ROOT)
    code, _ = checked_code(base, ROOT, request['reviewed_head'])
    board = base.load_module(ROOT, 'tools/board_tool.py', code['tools/board_tool.py'])
    operation = check_only if request['action'] == '--check-only' else upload_precompiled
    result = operation(board, request['scope'], request['reviewed_head'])
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
