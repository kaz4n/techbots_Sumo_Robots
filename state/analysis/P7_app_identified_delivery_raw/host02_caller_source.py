# Pairs one qualified application upload with a fresh identified receive owner.
# Consumes the compiled session once and preserves the existing physical admission.
# Focused host fixtures cover real admission, receiver composition and failed closure.
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import types

ROOT = Path(__file__).absolute().parents[1]
DEPLOY = 'tools/deploy_commissioning_app.py'
RECEIVER = 'tools/run_recorder_delivery.py'
TARGET = '2629958581'
ADB = 'C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe'
ADB_SHA = 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'


def require(value, message):
    if not value:
        raise ValueError(message)


def error_record(error):
    return dict(type=type(error).__name__, message=str(error))


def load_deployer(root, head):
    require(type(head) is str and len(head) == 40 and all(c in '0123456789abcdef' for c in head),
            'Exact reviewed HEAD required')
    result = subprocess.run(['git', '-C', str(root), 'show', head + ':' + DEPLOY],
                            stdin=subprocess.DEVNULL, capture_output=True, timeout=30, check=True)
    require(not result.stderr and len(result.stdout) <= 65536 and
            (root / DEPLOY).read_bytes() == result.stdout, 'Reviewed deployer source differs')
    module = types.ModuleType('_app_delivery_deployer')
    module.__file__ = str(root / DEPLOY)
    exec(compile(result.stdout, module.__file__, 'exec'), module.__dict__)
    return module


def admit(root, relative, head, *, now=None):
    root = Path(root).absolute()
    deploy = load_deployer(root, head)
    base = deploy.bootstrap(root)
    document = base.decode(base.read_file(root, relative, 65536))
    run_id = document['request']['run_id']
    base.hexadecimal(run_id, 32)
    delivery = dict(run_id=run_id, session=int(run_id[:16], 16), claimed=False)
    scope = deploy.load_scope(root, relative, head, TARGET, 'adb', now=now, _delivery=delivery)
    board = base.load_module(root, 'tools/board_tool.py', scope['code']['tools/board_tool.py'])
    board.ROOT = root
    board.target, board.transport = lambda: TARGET, lambda: 'adb'
    board.adb_executable = lambda: ADB
    # The receiver and uploader use the same fixed executable, not ambient routing.
    deploy.check_only(board, relative, head, now=now, _delivery=delivery)
    return deploy, scope, board


def check_only(root, relative, head, *, now=None):
    deploy, scope, unused = admit(root, relative, head, now=now)
    return dict(schema='app-identified-delivery-check-v1', status='ADMITTED_LOCAL',
                board_observed=False, session=scope['delivery']['session'],
                owner=scope['delivery_owner'].relative_to(scope['root']).as_posix(),
                source_commit=scope['request']['source_commit'],
                source_sha256=scope['request']['source_sha256'],
                scope_sha256=scope['scope_sha256'], reviewed_head=head)


def reserve(deploy, scope):
    owner, base = scope['delivery_owner'], scope['base']
    base.plain(owner.parent, directory=True)
    owner.mkdir(mode=0o700)  # Session-prefix collisions consume the same owner.
    identity = base.owner_identity(owner)
    base.write_exclusive(owner / 'claim.json', deploy.delivery_claim(scope))
    (owner / 'run').mkdir(mode=0o700)
    scope['delivery']['claimed'] = True
    return identity


def receiver_scope(scope, board):
    base, code = scope['base'], scope['code']
    receiver = base.load_module(scope['root'], RECEIVER, code[RECEIVER])
    require(receiver.TARGET == TARGET and receiver.BOOT == scope['request']['bindings']['boot_id'],
            'Receiver target/boot differs from qualified upload')
    receiver.accept_capture = accept_capture
    owner = types.SimpleNamespace(root=scope['root'], output=scope['delivery_owner'],
        attempt=scope['request']['run_id'], session=scope['delivery']['session'],
        reviewed_head=scope['request']['source_commit'], source_sha256=scope['request']['source_sha256'],
        code={**code, 'src/config.h': scope['compiler_owner'].code['src/config.h']},
        board=board, base=types.SimpleNamespace(ADB=ADB, ADB_SHA=ADB_SHA))
    commands = receiver.ReceiverCommands(owner)
    dump = receiver.receiver_modules(owner, commands)
    return receiver, owner, commands, dump


def accept_capture(owner, destination, dump):
    directory = dump.local_path(destination)
    require(directory.parent == owner.output / 'run/capture', 'Capture escaped session owner')
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
            require(stream.read() == getattr(capture, role), 'CSV differs from retained wire')
    identities = dict(firmware_revision=owner.reviewed_head, source_sha256=owner.source_sha256,
                      config_sha256=hashlib.sha256(owner.code['src/config.h']).hexdigest())
    require(all(manifest.get(key) == value for key, value in identities.items()) and
            manifest.get('target') == TARGET, 'Capture source declaration differs')
    require(all(type(metadata.get(key)) is int and metadata[key] == owner.session
                for key in ('session', 'expected_session', 'observed_session')) and
            metadata.get('rejected_session') is None and metadata.get('transport_integrity') == 'PASS',
            'Capture session/integrity differs')
    require(validation.get('format_integrity') == validation.get('consistency') == 'PASS' and
            validation.get('errors') == [], 'Capture CSV validation failed')
    return dict(status='IDENTIFIED_TRANSPORT_PASS', session=capture.session, epoch=capture.epoch,
                frames=capture.frame_count, events=capture.event_count, crc32=capture.crc32,
                recording=validation['recording'], origin_is_caller_declaration=True,
                hardware_acceptance=False)


def revalidate(deploy, scope, board, identity, *, now=None):
    current = deploy.load_scope(scope['root'], scope['relative'], scope['reviewed_head'],
                                TARGET, 'adb', now=now, _delivery=scope['delivery'])
    require(current['scope_sha256'] == scope['scope_sha256'] and
            current['request_sha256'] == scope['request_sha256'] and current['code'] == scope['code'],
            'Paired delivery inputs changed')
    scope['base'].check_owner(scope['delivery_owner'], identity)
    require(hashlib.sha256(Path(ADB).read_bytes()).hexdigest() == ADB_SHA, 'Fixed ADB executable changed')


def run(root, relative, head, *, now=None):
    deploy, scope, board = admit(root, relative, head, now=now)
    identity = reserve(deploy, scope)
    output, base = scope['delivery_owner'], scope['base']
    report = dict(schema='app-identified-delivery-result-v1', status='FAILED',
        session=scope['delivery']['session'], run_id=scope['request']['run_id'],
        source_commit=scope['request']['source_commit'], source_sha256=scope['request']['source_sha256'],
        reviewed_head=head, scope_sha256=scope['scope_sha256'], upload=None, upload_attempts=0,
        capture=None, capture_acceptance=None, connection=None, closing_errors=[],
        receiver_cleanup_errors=[], first_error=None, framing_clean='UNKNOWN', hardware_acceptance=False)
    first = worker = state = receiver = owner = commands = dump = None
    started = time.monotonic()
    try:
        revalidate(deploy, scope, board, identity, now=now)
        receiver, owner, commands, dump = receiver_scope(scope, board)
        worker, state = receiver.arm_receiver(owner, output / 'run', dump)
        report['connection'] = receiver.await_connection(owner, dump, worker, state)
        base.write_exclusive(output / 'connection.json', report['connection'])
        revalidate(deploy, scope, board, identity, now=now)
        require(worker.is_alive() and state['error'] is None and time.monotonic() - started < 180,
                'Paired receiver ended or admission expired before upload')
        outcome = deploy.upload_precompiled(board, relative, head, now=now, _delivery=scope['delivery'])
        report['upload'], report['upload_attempts'] = outcome, outcome['attempts']
        require(outcome['status'] == 'ACCEPTED' and outcome['attempts'] == 1 and
                outcome['first_error'] is None and outcome['postcheck_errors'] == [],
                'Qualified application upload did not close successfully')
    except BaseException as error:
        first = error
        if getattr(error, 'deploy_outcome', None) is not None:
            report['upload'] = error.deploy_outcome
            report['upload_attempts'] = error.deploy_outcome['attempts']
    if receiver is not None:
        try:
            first = receiver.close_receiver(owner, output / 'run', worker, state, dump,
                                            commands, report, started, first)
        except BaseException as error:
            first = first or error
            report['closing_errors'].append(dict(check='receiver_close', **error_record(error)))
    try:
        revalidate(deploy, scope, board, identity, now=now)
    except BaseException as error:
        first = first or error
        report['closing_errors'].append(dict(check='local', **error_record(error)))
    if first is None and (report['capture_acceptance'] is None or report['closing_errors'] or
                          report['receiver_cleanup_errors']):
        first = ValueError('Identified capture or complete closing evidence is absent')
    report['first_error'] = None if first is None else error_record(first)
    if first is None:
        report['status'] = 'DELIVERED'
    try:
        base.check_owner(output, identity)
        base.write_exclusive(output / 'result.json', report)
    except BaseException as error:
        first = first or error
        report['status'] = 'FAILED'
        report['first_error'] = error_record(first)
        report['closing_errors'].append(dict(check='result_write', **error_record(error)))
    if first is not None:
        first.delivery_outcome = report
        raise first
    return report


def main(argv):
    require(sys.flags.isolated and sys.dont_write_bytecode, 'Python -I -B required')
    require(type(argv) is list and len(argv) == 5 and argv[0] in ('--check-only', '--execute') and
            argv[1::2] == ['--scope', '--reviewed-head'], 'Expected action --scope PATH --reviewed-head HEAD')
    operation = check_only if argv[0] == '--check-only' else run
    result = operation(ROOT, argv[2], argv[4])
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
