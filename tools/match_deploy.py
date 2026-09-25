# Admits one precompiled MATCH upload using source-bound external evidence.
# Keeps compilation, physical qualification and human permission separate.
# Independent host fixtures exercise admission, existing transport and failures.
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import types

FQBN = 'arduino:zephyr:unoq:wait_linux_boot=no'
FLAGS = '-DMATCH=1 -DMOTORS_ALLOWED=1'
PARENT = '/home/arduino/sumox26_codex_build'
STATIC = 'state/analysis/P7_static_startup_raw/'
HELPER = 'state/analysis/P7_static_link_probe_raw/static_remote.py'
SOFTWARE = tuple('tools/' + name for name in (
    'board_tool.py', 'app_build_policy.py', 'app_build_pins.json',
    'app_build_commands.json', 'match_upload.py', 'match_payload.py', 'match_deploy.py'))
FIXED = {
    HELPER: '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8',
    STATIC + 'capture_remote.py': '95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e',
    STATIC + 'upload_remote.py': 'e926b7ba5586475664b0541370e7cfb5c50e40d8dc8b47b18e35db3e0a0a25c1',
    STATIC + 'startup_run.py': 'c95888353c9d85c5d9b0e545553a9e9dcde372b5b313102dd14240ce38db4e0c',
    STATIC + 'cli_initialization_inventory.json': 'aaa2c307b7ed1b8d7e00a737447a03a63a78cd4b7fb2145142b20e9501da1e62',
    STATIC + 'cli_builtin_files_inventory.json': 'a364beb814b36b9c56328b54a9de5fa0f4ad80a67003d40c7cc994a1917ba2cb'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, names):
    require(type(value) is dict and set(value) == set(names), 'Unexpected object fields')


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for name, value in pairs:
        require(name not in result, 'Duplicate JSON field')
        result[name] = value
    return result


def decode(raw):
    value = json.loads(raw, object_pairs_hook=unique)
    canonical(value)
    return value


def hexadecimal(value, width):
    require(type(value) is str and re.fullmatch('[0-9a-f]{' + str(width) + '}', value),
            'Invalid hexadecimal identity')


def relative_name(value):
    require(type(value) is str and value, 'Missing relative path')
    reserved = {'con', 'prn', 'aux', 'nul', *(f'com{i}' for i in range(1, 10)),
                *(f'lpt{i}' for i in range(1, 10))}
    for part in value.split('/'):
        require(re.fullmatch('[A-Za-z0-9_.-]+', part) and part not in ('.', '..') and
                not part.endswith('.') and part.split('.')[0].lower() not in reserved,
                'Invalid portable relative path')
    return value


def plain(path, directory=False):
    require(path.is_absolute(), 'Absolute local root required')
    for item in (path, *path.parents):
        info = item.lstat()
        require(not stat.S_ISLNK(info.st_mode) and
                not getattr(info, 'st_file_attributes', 0) & 1024, 'Linked local path')
        expected = stat.S_ISDIR if item != path or directory else stat.S_ISREG
        require(expected(info.st_mode), 'Unexpected local path type')


def read_file(root, name, limit=1048576):
    path = root / relative_name(name)
    plain(path)
    before = path.stat()
    require(before.st_size <= limit, 'Local file exceeds bound: ' + name)
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(limit + 1)
    after = path.stat()
    identity = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns)
    require(identity(before) == identity(opened) == identity(after) and
            len(raw) == before.st_size and len(raw) <= limit, 'Local file changed: ' + name)
    return raw


def pinned(root, pin, limit=1048576):
    keys(pin, ('path', 'bytes', 'sha256'))
    hexadecimal(pin['sha256'], 64)
    require(type(pin['bytes']) is int and 0 < pin['bytes'] <= limit, 'Invalid pin size')
    raw = read_file(root, pin['path'], limit)
    require(len(raw) == pin['bytes'] and sha(raw) == pin['sha256'], 'Pinned file changed')
    return raw


def load_module(root, name, raw):
    module = types.ModuleType('sumox_match_' + Path(name).stem)
    module.__file__ = str(root / name)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def utc(value):
    require(type(value) is str, 'UTC timestamp required')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    require(result.utcoffset() is not None and result.utcoffset().total_seconds() == 0,
            'Timestamp must be UTC')
    return result


def current_time(now):
    value = datetime.now(timezone.utc) if now is None else now
    require(isinstance(value, datetime) and value.utcoffset() is not None and
            value.utcoffset().total_seconds() == 0, 'Current time must be aware UTC')
    return value


def source_files(root, folder):
    plain(root / folder, directory=True)
    pending = [root / folder]
    count = 0
    while pending:
        parent = pending.pop()
        for item in parent.iterdir():
            count += 1
            require(count <= 1024, 'Source tree exceeds entry bound')
            plain(item, directory=item.is_dir())
            if item.is_dir():
                pending.append(item)
            else:
                yield item.relative_to(root).as_posix()


def app_source_hash(root):
    root = Path(root).absolute()
    extensions = ('.c', '.cc', '.cpp', '.h', '.hpp')
    for reserved in ('config.h', 'core', 'hal', 'app'):
        require(not os.path.lexists(root / 'src/app/src' / reserved), 'Reserved sketch-local source')
    mapped = {'src/config.h': 'src/config.h'}
    for folder in ('src/core', 'src/hal'):
        mapped.update((name, name) for name in source_files(root, folder))
    for name in source_files(root, 'src/app'):
        tail = Path(name).relative_to('src/app')
        if tail.parts[0] == 'src':
            require(len(tail.parts) > 1 and tail.parts[1] not in
                    ('config.h', 'core', 'hal', 'app'), 'Reserved sketch-local source')
            destination = tail.as_posix()
        elif tail.suffix in extensions:
            destination = 'src/app/' + tail.as_posix()
        elif len(tail.parts) == 1 and tail.name != '.gitkeep':
            destination = tail.name
        else:
            continue
        require(destination not in mapped, 'Staged destination collision')
        mapped[destination] = name
    require('app.ino' in mapped and not any(name in mapped for name in
            ('sketch.yaml', 'sketch.yml', 'sketch.json')), 'Missing app or sketch override')
    folded = [name.lower() for name in mapped]
    require(len(mapped) <= 512 and len(set(folded)) == len(folded), 'Source count/case collision')
    digest, total = hashlib.sha256(), 0
    for name in sorted(mapped, key=Path):
        relative_name(name)
        raw = read_file(root, mapped[name])
        total += len(raw)
        require(total <= 4194304, 'App source bytes exceed bound')
        digest.update(name.encode('utf-8') + b'\0')
        digest.update(raw)
    return digest.hexdigest()


def validate_request(args):
    value = getattr(args, 'deploy_scope', None)
    if value is None:
        return False
    require(type(value) is str and value and args.sketch == 'app' and args.match is True and
            not args.compile_only and getattr(args, 'startup', None) in (None, 'immediate') and
            getattr(args, 'run_ui_adc_probe', None) is None,
            'Identified MATCH deployment requires app --match, Immediate and no compile-only/ADC')
    relative_name(value)
    return True


def checked_code(root, request):
    keys(request['software'], SOFTWARE)
    raw = {}
    for name, pin in request['software'].items():
        require(type(pin) is dict and pin.get('path') == name, 'Software pin path differs')
        raw[name] = pinned(root, pin)
    for name, digest in FIXED.items():
        raw[name] = read_file(root, name)
        require(sha(raw[name]) == digest, 'Frozen dependency changed: ' + name)
    return raw


def checked_build(root, request, profile, policy):
    receipts = request['build_receipts']
    keys(receipts, ('verified', 'command', 'result'))
    prefix = 'build/app-receipts/' + request['build_id'] + '/'
    documents = {}
    for role, name in (('verified', 'verified.json'), ('command', 'command.json'),
                       ('result', 'compile.stdout.json')):
        require(type(receipts[role]) is dict and receipts[role].get('path') == prefix + name,
                'Build receipt path differs')
        documents[role] = pinned(root, receipts[role], 4194304 if role == 'result' else 1048576)
    verified = decode(documents['verified'])
    keys(verified, ('policy', 'source_sha256', 'fqbn', 'build_path', 'artifacts',
                    'file_sha256', 'compiler_returncode', 'used_libraries',
                    'resolved_directories', 'precompile_checks'))
    build = profile['files']['raw'].rsplit('/', 1)[0]
    artifacts = profile['files']['exported'].rsplit('/', 1)[0]
    expected = dict(policy='native-app-v1', source_sha256=request['source_sha256'],
                    fqbn=FQBN, build_path=build, artifacts=artifacts,
                    compiler_returncode=0, used_libraries=[], precompile_checks=True,
                    resolved_directories={'data': '/home/arduino/.arduino15',
                                          'user': '/home/arduino/Arduino'})
    require(all(canonical(verified[k]) == canonical(v) for k, v in expected.items()),
            'Checked build identity differs')
    command = ['arduino-cli', 'compile', '--json', '--fqbn', FQBN, '--build-path', build,
               '--output-dir', artifacts, '--build-property', 'compiler.cpp.extra_flags=' + FLAGS,
               '--build-property', 'compiler.c.extra_flags=' + FLAGS, '--build-property',
               'build.library_discovery_phase_flag=' + policy.DISCOVERY, profile['argv'][-1]]
    require(decode(documents['command']) == command, 'Compile command differs')
    policy.validate_result(documents['result'].decode('utf-8'), FQBN, FLAGS, build)
    pins = policy.installed_pins('/home/arduino/.arduino15')
    paths = [build + '/app.ino' + suffix for suffix in ('.elf', '_debug.elf', '_temp.elf')]
    paths.append(profile['files']['exported'])
    keys(verified['file_sha256'], (*pins, *paths))
    for path, digest in verified['file_sha256'].items():
        hexadecimal(digest, 64)
        require(digest != sha(b''), 'Empty build artifact')
        require(path not in pins or pins[path] == digest, 'Build installed dependency differs')
    for pin in request['bindings']['files'].values():
        if pin['path'] in verified['file_sha256']:
            require(verified['file_sha256'][pin['path']] == pin['sha256'], 'Upload/build bytes differ')


def checked_qualification(root, request):
    value = decode(pinned(root, request['qualification'], 65536))
    keys(value, ('schema', 'source_sha256', 'raw_sha256', 'package_sha256',
                 'operation_image_sha256', 'operation', 'verdict', 'reviewer', 'limitations', 'evidence'))
    require(value['schema'] == 'match-operation-qualification-v1' and value['verdict'] ==
            'QUALIFIED_FOR_IDENTIFIED_OPERATION' and value['operation'] in ('stand', 'ring'),
            'Missing artifact operation qualification')
    require(type(value['reviewer']) is str and value['reviewer'].strip() and
            type(value['limitations']) is list and all(type(v) is str for v in value['limitations']),
            'Malformed reviewer disposition')
    require(value['source_sha256'] == request['source_sha256'] and
            value['raw_sha256'] == request['bindings']['files']['raw']['sha256'] and
            value['package_sha256'] == request['bindings']['files']['sketch']['sha256'],
            'Qualification artifact differs')
    image = {k: request[k] for k in ('target', 'transport', 'source_sha256')}
    image.update(fqbn=FQBN, operation=value['operation'])
    image.update({k: request['bindings'][k] for k in ('files', 'directories', 'absent')})
    require(value['operation_image_sha256'] == sha(canonical(image)), 'Qualification target/runtime differs')
    require(type(value['evidence']) is list and 1 <= len(value['evidence']) <= 16,
            'Missing qualification evidence')
    for pin in value['evidence']:
        pinned(root, pin)
    return value


def checked_authorization(root, scope, qualification, request_digest, now):
    value = decode(pinned(root, scope['authorization'], 65536))
    keys(value, ('schema', 'request_sha256', 'reply', 'message_ref', 'issued_utc', 'expires_utc'))
    reply = 'STAND OK' if qualification['operation'] == 'stand' else 'RING OK'
    require(value['schema'] == 'match-human-authorization-v1' and
            value['request_sha256'] == request_digest and value['reply'] == reply and
            type(value['message_ref']) is str and value['message_ref'].strip(),
            'Missing identified human authorization evidence')
    issued, expires = utc(value['issued_utc']), utc(value['expires_utc'])
    require(0 < (expires - issued).total_seconds() <= 3600 and issued <= now < expires,
            'Human authorization is stale, future or too long-lived')


def load_scope(root, relative, target, transport, *, now=None):
    root, observed_time = Path(root).absolute(), current_time(now)
    raw_scope = read_file(root, relative, 65536)
    scope = decode(raw_scope)
    keys(scope, ('schema', 'request', 'authorization'))
    require(scope['schema'] == 'match-deploy-v1', 'Unknown deployment scope')
    request = scope['request']
    keys(request, ('run_id', 'build_id', 'source_sha256', 'source_commit', 'target',
                   'transport', 'bindings', 'build_receipts', 'software', 'qualification'))
    for name, width in (('run_id', 32), ('build_id', 32), ('source_sha256', 64), ('source_commit', 40)):
        hexadecimal(request[name], width)
    require(type(target) is str and target and request['target'] == target and
            type(transport) is str and transport in ('ssh', 'adb') and request['transport'] == transport,
            'Configured target/transport differs')
    code = checked_code(root, request)
    support = load_module(root, STATIC + 'capture_remote.py', code[STATIC + 'capture_remote.py'])
    uploader = load_module(root, STATIC + 'upload_remote.py', code[STATIC + 'upload_remote.py'])
    adapter = load_module(root, 'tools/match_upload.py', code['tools/match_upload.py'])
    profile = adapter.match_profile(uploader, support, request['source_sha256'],
                                    request['build_id'], request['run_id'])
    bindings = uploader._checked_bindings(support, request['bindings'], profile)
    require(all(bindings['files']['sketch'][k] == bindings['files']['exported'][k]
                for k in ('bytes', 'sha256')), 'Packaged/exported bytes differ')
    require(app_source_hash(root) == request['source_sha256'], 'Current firmware source changed')
    policy = load_module(root, 'tools/app_build_policy.py', code['tools/app_build_policy.py'])
    checked_build(root, request, profile, policy)
    qualification = checked_qualification(root, request)
    digest = sha(canonical(request))
    checked_authorization(root, scope, qualification, digest, observed_time)
    return dict(root=root, relative=relative, request=request, profile=profile,
                scope_sha256=sha(raw_scope), request_sha256=digest, code=code)


def error_record(error):
    return {'type': type(error).__name__, 'message': str(error)}


def write_exclusive(path, value):
    plain(path.parent, directory=True)
    with path.open('xb') as stream:
        stream.write(canonical(value))
        stream.flush()
        os.fsync(stream.fileno())


def output_text(value):
    if value is None:
        return ''
    require(type(value) in (str, bytes), 'Malformed transport output')
    return value.decode('utf-8', errors='surrogateescape') if type(value) is bytes else value


def command(board, target, argv, timeout, label, outcome):
    receipt = dict(label=label, argv_sha256=sha(canonical(argv)), returncode=None,
                   stdout='', stderr='', error=None)
    outcome['commands'].append(receipt)
    try:
        result = board.remote(target, argv, capture=True, timeout=timeout)
        receipt.update(returncode=result.returncode, stdout=output_text(result.stdout),
                       stderr=output_text(result.stderr))
        require(type(result.returncode) is int, 'Malformed transport status')
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, argv, result.stdout, result.stderr)
        require(not receipt['stderr'], 'Transport stderr is not empty')
        return receipt['stdout']
    except Exception as error:
        if hasattr(error, 'stdout'):
            receipt['stdout'] = output_text(error.stdout)
        if hasattr(error, 'stderr'):
            receipt['stderr'] = output_text(error.stderr)
        receipt['returncode'] = getattr(error, 'returncode', receipt['returncode'])
        receipt['error'] = error_record(error)
        raise


def prerequisites(scope):
    values = []
    for name in ('cli_initialization_inventory', 'cli_builtin_files_inventory'):
        record = decode(scope['code'][STATIC + name + '.json'])
        require(type(record['returncode']) is int and record['returncode'] == 0 and
                record['stderr'] == '', 'Failed prerequisite baseline')
        baseline = decode(record['stdout'])
        require(baseline['status'] == 'COLLECTED', 'Incomplete prerequisite baseline')
        values.append((name, record['argv'], baseline))
    return values


def check_prerequisite(board, scope, item, label, outcome, projection):
    name, argv, baseline = item
    text = command(board, scope['request']['target'], argv, 90, label + ':' + name, outcome)
    require(len(text.encode('utf-8')) <= 1048576, 'Inventory response exceeds bound')
    current = decode(text)
    expected_identity = dict(baseline['identity'], boot_id=scope['request']['bindings']['boot_id'])
    require(current.get('status') == 'COLLECTED' and
            canonical(current.get('identity')) == canonical(expected_identity),
            'Fresh prerequisite identity/status differs')
    expected = {'uid': 1000, 'user': 'arduino', 'home': '/home/arduino',
                'sysname': 'Linux', 'machine': 'aarch64'}
    require(all(canonical(expected_identity.get(k)) == canonical(v) for k, v in expected.items()),
            'Wrong board identity')
    without_identity = lambda value: {k: v for k, v in value.items() if k != 'identity'}
    require(canonical(projection(without_identity(current))) ==
            canonical(projection(without_identity(baseline))), 'CLI prerequisites changed')


def revalidate(board, scope, now):
    current = load_scope(board.ROOT, scope['relative'], board.target(), board.transport(), now=now)
    require(current['scope_sha256'] == scope['scope_sha256'] and
            current['request_sha256'] == scope['request_sha256'], 'Scope changed after admission')
    require(current['code'] == scope['code'], 'Code changed after admission')


def prepared(board, scope):
    code, request = scope['code'], scope['request']
    payload = load_module(scope['root'], 'tools/match_payload.py', code['tools/match_payload.py'])
    helpers = load_module(scope['root'], STATIC + 'startup_run.py', code[STATIC + 'startup_run.py'])
    sources = dict(helper=code[HELPER], support=code[STATIC + 'capture_remote.py'],
                   upload=code[STATIC + 'upload_remote.py'], adapter=code['tools/match_upload.py'])
    native = ([board.adb_executable(), '-s', request['target'], 'shell', '-T']
              if request['transport'] == 'adb' else ['ssh', *board.SSH_OPTIONS, request['target']])
    argv = payload.build_command(sources, request['bindings'], request['source_sha256'],
                                  request['build_id'], request['run_id'], native)
    return argv, payload, helpers.projection, prerequisites(scope)


def new_outcome(scope, now):
    request = scope['request']
    result = {k: request[k] for k in ('run_id', 'source_sha256', 'target', 'transport')}
    result.update(schema='match-deploy-outcome-v1', scope_sha256=scope['scope_sha256'],
                  request_sha256=scope['request_sha256'], status='FAILED', attempts=0,
                  remote_result=None, commands=[], first_error=None, postcheck_errors=[],
                  started_utc=current_time(now).isoformat(), finished_utc=None)
    return result


def owner_identity(path):
    plain(path, directory=True)
    info = path.stat()
    return info.st_dev, info.st_ino


def check_owner(path, identity):
    require(owner_identity(path) == identity, 'Local attempt owner changed')


def claim(scope, argv, now):
    parent = scope['root'] / 'state/analysis'
    plain(parent, directory=True)
    output = parent / ('match_deploy_' + scope['request']['run_id'])
    require(not os.path.lexists(output), 'MATCH deployment attempt is consumed')
    output.mkdir(mode=0o700)
    identity = owner_identity(output)
    record = dict(schema='match-deploy-attempt-v1', scope_sha256=scope['scope_sha256'],
                  request_sha256=scope['request_sha256'], request=scope['request'],
                  argv_sha256=sha(canonical(argv)), started_utc=current_time(now).isoformat())
    write_exclusive(output / 'attempt.json', record)
    check_owner(output, identity)
    return output, identity


def closing_checks(board, scope, items, outcome, projection, output, identity, now):
    errors = []
    operations = [('local', lambda: revalidate(board, scope, now)),
                  ('owner', lambda: check_owner(output, identity))]
    operations.extend((item[0], lambda item=item: check_prerequisite(
        board, scope, item, 'after', outcome, projection)) for item in items)
    for name, operation in operations:
        try:
            operation()
        except Exception as error:
            outcome['postcheck_errors'].append({'check': name, **error_record(error)})
            errors.append(error)
    return errors


def save_outcome(board, output, identity, outcome, first):
    try:
        check_owner(output, identity)
        write_exclusive(output / 'outcome.json', outcome)
    except Exception as error:
        if first is None:
            raise
        first.evidence_write_errors = [error_record(error)]
        board.report_app_error(first, 'Could not save MATCH outcome: ' + str(error))
    if first is not None:
        first.deploy_outcome = outcome
        board.report_app_error(first, 'MATCH outcome ' + outcome['status'] + '; attempt: ' + str(output))
        raise first


def upload_precompiled(board, relative, *, now=None):
    scope = load_scope(board.ROOT, relative, board.target(), board.transport(), now=now)
    argv, payload, projection, items = prepared(board, scope)
    board.require_transport(sync=False)
    revalidate(board, scope, now)
    output, identity = claim(scope, argv, now)
    outcome, first = new_outcome(scope, now), None
    request = scope['request']
    try:
        for item in items:
            check_prerequisite(board, scope, item, 'before', outcome, projection)
        revalidate(board, scope, now)
        check_owner(output, identity)
        outcome['attempts'] = 1
        text = command(board, request['target'], argv, 240, 'upload', outcome)
        outcome['remote_result'] = payload.validate_reply(
            text, request['source_sha256'], request['build_id'], request['run_id'], argv[-2])
    except BaseException as error:
        first = error
    closing = closing_checks(board, scope, items, outcome, projection, output, identity, now)
    first = first if first is not None else (closing[0] if closing else None)
    outcome['first_error'] = None if first is None else error_record(first)
    outcome['finished_utc'] = current_time(now).isoformat()
    if first is None and outcome['remote_result'] is not None:
        outcome['status'] = 'ACCEPTED'
    elif outcome['attempts']:
        outcome['status'] = 'UNKNOWN'
    save_outcome(board, output, identity, outcome, first)
    return outcome
