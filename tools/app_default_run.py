# Guards one reviewed unchanged default-app upload with inhibited native outputs.
# Keeps the generic manifest closed and consumes one claim before upload launch.
# Independent D118 contract fixtures verify identities, ordering and failures.
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import uuid

import app_build_policy as policy

RUN_ID = 'app-default-e820c0e1-run01'
TARGET = '2629958581'
SOURCE = 'e820c0e16c29cfd289889273f02721a995e5336b14397f64d6093cffd42b8b69'
ELF_HASH = '8379f152554649fd1b96165f29fda1f165c2b5cfc51d8dca430a37e19f693257'
BINARY_HASH = 'c60443cd8d90c26a85591153dfa38d5f9233bd686b413b2ab7daa3e1457f6df5'
MANIFEST_HASH = 'a1587931afa5f817bf8b93054f384918dc8cd36d4fb71c8f7b083d76e6128802'
REMOTE_ROOT = '/home/arduino/sumox26_codex_build'
FQBN = 'arduino:zephyr:unoq'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
RAW = 'state/analysis/P2_app_default_probe_raw'
RUN_RECORD = 'state/analysis/P2_app_default_probe_run01.json'
APPROVAL = RAW + '/reviewer/run01_approval.json'
REVIEW = 'state/reviews/P2_app_default_run01_review.md'
ATTEMPT = RAW + '/run01_upload_attempt.json'
OUTCOME = RAW + '/run01_upload_outcome.json'
SCOPE_TEXT = ('one unchanged default app upload with inhibited native GPIO/PWM setup; '
              'optional grants false; passive readout separately')
VERDICT = 'PASS_EXACT_DEFAULT_APP_SOURCE_TARGET_CAPTURE_GUARD'
FILES = ('tools/board_tool.py', 'tools/app_build_policy.py',
         'tools/app_build_pins.json', 'tools/app_build_commands.json',
         'tools/app_default_run.py', 'tools/app_default_capture.py',
         'tools/p0_capture.py', 'tools/recorder_heap.py', 'tools/p0_mem_read.cfg',
         'tools/p0_inert_sources.json', 'state/analysis/P2_app_default_probe_contract.md',
         'state/analysis/P2_app_default_run_contract.md')
RUN_KEYS = ('schema_version', 'run_id', 'target', 'transport', 'source_sha256',
            'elf_sha256', 'binary_sha256', 'approval_sha256', 'software_commit',
            'remote_root', 'setup', 'scope')
APPROVAL_KEYS = ('schema_version', 'run_id', 'verdict', 'source_sha256',
                 'elf_sha256', 'binary_sha256', 'software_commit', 'review_sha256',
                 'file_sha256', 'source_file_sha256')
SCOPE_KEYS = {'root', 'run_record', 'approval', 'run_record_sha256',
              'approval_sha256', 'review_sha256', 'head_commit'}
# One synchronous orchestration owns this ephemeral diagnostic list.
_git_checks = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def output_text(value):
    if value is None:
        return ''
    return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else str(value)


def digest(value, length=64):
    return type(value) is str and re.fullmatch('[0-9a-f]{' + str(length) + '}', value) is not None


def validate_request(args, startup):
    require(getattr(args, 'run_id', None) == RUN_ID and
            getattr(args, 'sketch', None) == 'app' and
            getattr(args, 'match', None) is False and
            getattr(args, 'compile_only', None) is False and startup == 'default' and
            getattr(args, 'startup', None) in (None, 'default'),
            'Only the identified default MATCH0/MOTORS_ALLOWED0 app request is admitted')
    return True


def environment():
    require(os.environ.get('SUMO_TRANSPORT') == 'adb', 'Explicit ADB transport is required')
    require(os.environ.get('SUMO_ADB_SERIAL') == TARGET, 'The identified ADB board is required')
    require(os.environ.get('SUMO_REMOTE_ROOT') == REMOTE_ROOT, 'The dedicated remote root differs')


def relative_parts(relative):
    require(type(relative) is str and relative and '\\' not in relative and
            ':' not in relative, 'Invalid fixed relative path')
    parts = relative.split('/')
    require(all(part not in ('', '.', '..') for part in parts), 'Invalid path component')
    return parts


def safe_path(root, relative, missing=False, directory=False):
    require(root.is_dir() and not root.is_symlink(), 'Workspace root must be a real directory')
    path, parts = root, relative_parts(relative)
    for index, part in enumerate(parts):
        path = path / part
        last = index == len(parts) - 1
        if missing and last and not os.path.lexists(path):
            return path
        info = path.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'Symlink ancestry is not admitted')
        expected = stat.S_ISDIR if not last or directory else stat.S_ISREG
        require(expected(info.st_mode), 'Unexpected path type')
    return path


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounded_blob(root, name):
    path = safe_path(root, name)
    with path.open('rb') as stream:
        blob = stream.read(65537)
    require(len(blob) <= 65536, 'Review record exceeds its byte bound')
    return blob


def record(root, name, keys):
    blob = bounded_blob(root, name)
    value = policy.decode(blob.decode('utf-8'))
    require(type(value) is dict and set(value) == set(keys), 'Unexpected record fields')
    require(type(value['schema_version']) is int and value['schema_version'] == 1,
            'Unknown record schema')
    return value, hashlib.sha256(blob).hexdigest()


def identity(value):
    expected = dict(run_id=RUN_ID, source_sha256=SOURCE, elf_sha256=ELF_HASH,
                    binary_sha256=BINARY_HASH)
    require(all(value[key] == actual for key, actual in expected.items()), 'Image identity differs')


def available_claim(root):
    for name in (ATTEMPT, OUTCOME):
        path = safe_path(root, name, missing=True)
        require(not os.path.lexists(path), 'This upload attempt is already consumed')


def current_head(root):
    argv = ['git', '-C', str(root), 'rev-parse', 'HEAD']
    check = dict(argv=argv, started_utc=utc_now(), returncode=None,
                 stdout='', stderr='', timed_out=False, error=None)
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=10,
                                check=False, stdin=subprocess.DEVNULL)
        check.update(returncode=result.returncode, stdout=output_text(result.stdout),
                     stderr=output_text(result.stderr))
        require(result.returncode == 0, 'Local Git HEAD query failed')
        head = check['stdout'].strip()
        require(digest(head, 40), 'Local Git HEAD is not an exact revision')
        return head
    except BaseException as error:
        check.update(error=str(error), timed_out=isinstance(error, subprocess.TimeoutExpired))
        if isinstance(error, subprocess.SubprocessError):
            check.update(returncode=getattr(error, 'returncode', None),
                         stdout=output_text(getattr(error, 'stdout', None)),
                         stderr=output_text(getattr(error, 'stderr', None)))
        raise
    finally:
        check['finished_utc'] = utc_now()
        if _git_checks is not None:
            _git_checks.append(check)


def validate_file_pins(root, hashes):
    require(type(hashes) is dict and set(hashes) == set(FILES), 'Reviewed tool pin set differs')
    for name, expected in hashes.items():
        require(digest(expected) and file_hash(safe_path(root, name)) == expected,
                'Reviewed file differs: ' + name)
    require(hashes['tools/p0_inert_sources.json'] == MANIFEST_HASH,
            'The existing nine-key manifest must remain byte-identical')


def validate_source_pins(root, hashes, staged=False):
    require(type(hashes) is dict and len(hashes) == 91 and 'app.ino' in hashes,
            'The exact91-file source map is required')
    combined = hashlib.sha256()
    for name in sorted(hashes):
        relative_parts(name)
        require(name == 'app.ino' or name.startswith('src/'), 'Source name is outside the app stage')
        local = name if staged or name != 'app.ino' else 'src/app/app.ino'
        blob = safe_path(root, local).read_bytes()
        require(digest(hashes[name]) and hashlib.sha256(blob).hexdigest() == hashes[name],
                'Reviewed source differs: ' + name)
        combined.update(name.encode('utf-8') + b'\0')
        combined.update(blob)
    require(combined.hexdigest() == SOURCE, 'The complete reviewed source digest differs')


def validate_records(run, approval, approval_hash, review_hash):
    identity(run)
    identity(approval)
    require(run['target'] == TARGET and run['transport'] == 'adb' and
            run['remote_root'] == REMOTE_ROOT, 'Run transport scope differs')
    require(run['setup'] == 'human-reported bare UNO Q' and run['scope'] == SCOPE_TEXT,
            'Run physical scope differs')
    require(digest(run['approval_sha256']) and run['approval_sha256'] == approval_hash,
            'Approval receipt differs')
    require(approval['verdict'] == VERDICT and digest(approval['review_sha256']) and
            approval['review_sha256'] == review_hash, 'Exact review is not approved')
    require(digest(run['software_commit'], 40) and
            run['software_commit'] == approval['software_commit'], 'Reviewed revisions differ')


def load_scope(root, target, transport):
    environment()
    require(target == TARGET and transport == 'adb', 'Target or transport differs')
    root = Path(root).absolute()
    available_claim(root)
    run, run_hash = record(root, RUN_RECORD, RUN_KEYS)
    approval, approval_hash = record(root, APPROVAL, APPROVAL_KEYS)
    review_hash = hashlib.sha256(bounded_blob(root, REVIEW)).hexdigest()
    validate_records(run, approval, approval_hash, review_hash)
    validate_file_pins(root, approval['file_sha256'])
    validate_source_pins(root, approval['source_file_sha256'])
    head = current_head(root)
    require(head == approval['software_commit'], 'Current local HEAD is not the reviewed commit')
    return dict(root=root, run_record=run, approval=approval, run_record_sha256=run_hash,
                approval_sha256=approval_hash, review_sha256=review_hash, head_commit=head)


def revalidate(board, target, scope):
    require(type(scope) is dict and set(scope) == SCOPE_KEYS, 'Unexpected in-memory scope')
    require(scope['root'] == Path(board.ROOT).absolute(), 'Workspace root differs')
    require(load_scope(board.ROOT, target, board.transport()) == scope,
            'Reviewed scope changed during preparation')


def validate_stage(board, scope):
    root = scope['root']
    folder = safe_path(root, 'build/stage/app', directory=True)
    board.check_source(folder)
    actual = set()
    for item in folder.rglob('*'):
        require(not item.is_symlink(), 'Staged source includes a symlink')
        if item.is_file():
            actual.add(item.relative_to(folder).as_posix())
        else:
            require(item.is_dir(), 'Unexpected staged source entry')
    hashes = scope['approval']['source_file_sha256']
    require(actual == set(hashes), 'Staged file set differs from the exact source map')
    validate_source_pins(folder, hashes, staged=True)
    require(board.source_hash(folder) == SOURCE, 'Staged digest differs')
    return folder


def artifact_pins(artifacts, folder):
    prefix = REMOTE_ROOT + '/_app_builds/native-app-v1/' + SOURCE + '/bench-default/'
    require(type(artifacts) is str and
            re.fullmatch(re.escape(prefix) + '[0-9a-f]{32}/artifacts', artifacts),
            'Fresh checked app artifact path is required')
    require(folder == REMOTE_ROOT + '/' + SOURCE + '/app', 'Staged board folder differs')
    build = artifacts.removesuffix('/artifacts') + '/build'
    return {build + '/app.ino.elf': ELF_HASH,
            artifacts + '/app.ino.elf-zsk.bin': BINARY_HASH}


def write_exclusive(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def launch(board, target, argv, outcome_path):
    outcome = dict(schema_version=1, run_id=RUN_ID, returncode=None,
                   stdout='', stderr='', timed_out=False, error=None)
    try:
        result = board.remote(target, argv, capture=True, timeout=120)
        outcome.update(returncode=result.returncode, stdout=output_text(result.stdout),
                       stderr=output_text(result.stderr))
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, argv, result.stdout, result.stderr)
    except BaseException as error:
        outcome.update(returncode=getattr(error, 'returncode', None),
                       stdout=output_text(getattr(error, 'stdout', None)),
                       stderr=output_text(getattr(error, 'stderr', None)),
                       timed_out=isinstance(error, subprocess.TimeoutExpired), error=str(error))
        raise
    finally:
        outcome['finished_utc'] = utc_now()
        write_exclusive(outcome_path, outcome)


def upload_once(board_module, target, artifact_folder, board_folder, scope):
    revalidate(board_module, target, scope)
    pins = artifact_pins(artifact_folder, board_folder)
    policy.verify_hashes(board_module.remote, target, pins)
    validate_stage(board_module, scope)
    revalidate(board_module, target, scope)
    root = scope['root']
    attempt = safe_path(root, ATTEMPT, missing=True)
    outcome = safe_path(root, OUTCOME, missing=True)
    argv = ['arduino-cli', 'upload', '--fqbn', FQBN, '--input-dir', artifact_folder, board_folder]
    claim = dict(schema_version=1, run_id=RUN_ID, target=target, transport='adb',
                 source_sha256=SOURCE, elf_sha256=ELF_HASH, binary_sha256=BINARY_HASH,
                 software_commit=scope['head_commit'], run_record_sha256=scope['run_record_sha256'],
                 approval_sha256=scope['approval_sha256'], review_sha256=scope['review_sha256'],
                 artifact_folder=artifact_folder, board_folder=board_folder,
                 started_utc=utc_now(), argv=argv)
    write_exclusive(attempt, claim)
    launch(board_module, target, argv, outcome)


def preparation_path(root):
    parent = safe_path(root, RAW, directory=True)
    directory = parent / 'preparations'
    if not os.path.lexists(directory):
        directory.mkdir()
    safe_path(root, RAW + '/preparations', directory=True)
    return directory / (uuid.uuid4().hex + '.json')


def prepare_local(board, scope):
    root = scope['root']
    for name in ('sketch.yaml', 'sketch.yml'):
        require(not os.path.lexists(root / 'src/app' / name), 'App sketch profiles are unreviewed')
    board.check_source(root / 'src/app')
    board.check_source(root / 'src')
    board.require_transport(sync=True)
    folder = Path(board.stage('app'))
    require(folder == root / 'build/stage/app', 'Local stage path differs')
    require(validate_stage(board, scope) == folder, 'Staged folder differs')
    return folder


def prepare_remote(board, target, folder, board_folder, trace):
    trace['phase'] = 'CORE'
    board.verify_core(target)
    trace['phase'] = 'SYNC'
    board.remote(target, ['mkdir', '-p', board_folder])
    board.sync_sources(target, folder, board_folder)
    trace['phase'] = 'COMPILE'
    artifacts = board.compile_app(target, SOURCE, board_folder, REMOTE_ROOT, FQBN, FLAGS, 'default')
    trace['artifact_folder'] = artifacts
    artifact_pins(artifacts, board_folder)
    build_id = artifacts.split('/')[-2]
    trace['checked_receipt'] = 'build/app-receipts/' + build_id
    return artifacts


def run_once(board_module, args):
    global _git_checks
    validate_request(args, 'default')
    environment()
    require(_git_checks is None, 'An app preparation is already active in this process')
    root = Path(board_module.ROOT).absolute()
    trace = dict(schema_version=1, run_id=RUN_ID, started_utc=utc_now(), finished_utc=None,
                 phase='SCOPE', local_git_checks=[], source_sha256=SOURCE,
                 artifact_folder=None, checked_receipt=None, error=None)
    _git_checks = trace['local_git_checks']
    receipt = None
    try:
        receipt = preparation_path(root)
        scope = load_scope(root, TARGET, board_module.transport())
        target = board_module.target()
        require(target == TARGET, 'Target lookup differs from reviewed board')
        trace['phase'] = 'STAGE'
        folder = prepare_local(board_module, scope)
        revalidate(board_module, target, scope)
        board_folder = REMOTE_ROOT + '/' + SOURCE + '/app'
        artifacts = prepare_remote(board_module, target, folder, board_folder, trace)
        trace['phase'] = 'VERIFY'
        validate_stage(board_module, scope)
        revalidate(board_module, target, scope)
        trace['phase'] = 'UPLOAD'
        upload_once(board_module, target, artifacts, board_folder, scope)
        trace['phase'] = 'UPLOAD_COMMAND_SUCCEEDED'
        return dict(run_id=RUN_ID, source_sha256=SOURCE, artifact_folder=artifacts,
                    board_folder=board_folder, attempt_file=str(root / ATTEMPT),
                    outcome_file=str(root / OUTCOME))
    except BaseException as error:
        trace['error'] = dict(type=type(error).__name__, message=str(error))
        raise
    finally:
        trace['finished_utc'] = utc_now()
        _git_checks = None
        if receipt is not None:
            write_exclusive(receipt, trace)


def main(argv=None):
    parser = argparse.ArgumentParser(description='One reviewed inhibited default-app upload')
    parser.add_argument('--run-id', required=True)
    parser.set_defaults(sketch='app', match=False, compile_only=False, startup='default')
    args = parser.parse_args(argv)
    try:
        validate_request(args, 'default')
        import board_tool
        result = run_once(board_tool, args)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as error:
        print(type(error).__name__ + ': ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
