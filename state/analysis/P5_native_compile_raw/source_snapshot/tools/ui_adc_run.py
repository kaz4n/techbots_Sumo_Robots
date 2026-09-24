# Guards one identified, reviewed bare ADC upload after a fresh checked build.
# Preserves generic refusal and consumes the attempt before any upload launch.
# Independently specified receipt, failure and transport tests cover this boundary.
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

import app_build_policy as policy

RUN_ID = 'd114-ui-adc-01'
TARGET = '2629958581'
SOURCE = '396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642'
ELF_HASH = '76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b'
BINARY_HASH = '567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9'
FQBN = 'arduino:zephyr:unoq'
RAW = 'state/analysis/P2_ui_adc_probe_raw'
RUN_RECORD = 'state/analysis/P2_ui_adc_probe_run01.json'
APPROVAL = RAW + '/reviewer/run01_approval.json'
ATTEMPT = RAW + '/run01_upload_attempt.json'
OUTCOME = RAW + '/run01_upload_outcome.json'
FILES = ('tools/board_tool.py', 'tools/app_build_policy.py',
         'tools/app_build_pins.json', 'tools/app_build_commands.json',
         'tools/ui_adc_run.py', 'tools/ui_adc_capture.py', 'tools/p0_capture.py',
         'tools/p0_mem_read.cfg', 'tools/p0_inert_sources.json',
         'state/analysis/P2_ui_adc_capture_contract.md',
         'state/analysis/P2_ui_adc_run_contract.md')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_request(args, startup):
    value = getattr(args, 'run_ui_adc_probe', None)
    if value is None:
        return False
    require(value == RUN_ID and args.sketch == 'bench/ui_adc_probe' and
            not args.match and not args.compile_only and startup == 'default',
            'The identified ADC run requires its exact sketch, default inert upload profile')
    return True


def safe_path(root, relative, missing=False):
    require(root.is_dir() and not root.is_symlink(), 'Run root must be a real directory')
    path = root
    parts = Path(relative).parts
    require(parts and not Path(relative).is_absolute() and '..' not in parts, 'Invalid fixed run path')
    for index, part in enumerate(parts):
        path = path / part
        if missing and index == len(parts) - 1 and not os.path.lexists(path):
            return path
        info = path.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'Run paths must not use symlinks')
        require(stat.S_ISREG(info.st_mode) if index == len(parts) - 1 else stat.S_ISDIR(info.st_mode),
                'Run path has an unexpected file type')
    return path


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(root, name, keys):
    path = safe_path(root, name)
    with path.open('rb') as stream:
        blob = stream.read(65537)
    require(len(blob) <= 65536, 'Run record exceeds its byte limit')
    value = policy.decode(blob.decode('utf-8'))
    require(type(value) is dict and set(value) == set(keys), 'Unexpected run record schema')
    require(type(value['schema_version']) is int and value['schema_version'] == 1,
            'Unknown run record version')
    return value, hashlib.sha256(blob).hexdigest()


def identity(value):
    expected = dict(run_id=RUN_ID, source_sha256=SOURCE, elf_sha256=ELF_HASH,
                    binary_sha256=BINARY_HASH)
    require(all(value[key] == item for key, item in expected.items()), 'Run image identity differs')


def digest(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


def load_scope(root, target, transport):
    root = Path(root).absolute()
    require(target == TARGET and transport == 'adb', 'Run requires the identified ADB board')
    for name in (ATTEMPT, OUTCOME):
        require(not os.path.lexists(safe_path(root, name, missing=True)), 'ADC run attempt is already consumed')
    run, run_hash = record(root, RUN_RECORD, ('schema_version', 'run_id', 'target', 'transport',
        'source_sha256', 'elf_sha256', 'binary_sha256', 'review_sha256', 'software_commit', 'setup', 'scope'))
    approval, approval_hash = record(root, APPROVAL, ('schema_version', 'run_id', 'verdict',
        'source_sha256', 'elf_sha256', 'binary_sha256', 'file_sha256'))
    identity(run)
    identity(approval)
    require(run['target'] == TARGET and run['transport'] == 'adb', 'Run target differs')
    require(type(run['software_commit']) is str and re.fullmatch('[0-9a-f]{40}', run['software_commit']),
            'Run requires its reviewed local revision')
    require(run['setup'] == 'human-reported bare UNO Q' and run['scope'] ==
            'one inert ADC diagnostic upload; no motors; passive readout separately', 'Run scope differs')
    require(digest(run['review_sha256']) and run['review_sha256'] == approval_hash, 'Run review differs')
    require(approval['verdict'] == 'PASS_EXACT_INERT_ADC_SOURCE_TARGET_CAPTURE_GUARD', 'Run review is not approved')
    hashes = approval['file_sha256']
    require(type(hashes) is dict and set(hashes) == set(FILES), 'Unexpected run source pin set')
    for name, expected in hashes.items():
        require(digest(expected) and file_hash(safe_path(root, name)) == expected, 'Reviewed run file differs: ' + name)
    return dict(root=root, run_record=run, approval=approval,
                run_record_sha256=run_hash, approval_sha256=approval_hash)


def revalidate(board, target, scope):
    require(type(scope) is dict and set(scope) == {'root', 'run_record', 'approval',
        'run_record_sha256', 'approval_sha256'}, 'Unexpected in-memory run scope')
    require(scope['root'] == Path(board.ROOT).absolute(), 'Run workspace differs')
    require(load_scope(board.ROOT, target, board.transport()) == scope, 'Run scope changed during build')


def artifact_pins(board, artifacts, folder):
    root = board.setting('SUMO_REMOTE_ROOT', r'/[A-Za-z0-9_/-]+')
    require('..' not in root.split('/') and root.strip('/'), 'Invalid dedicated remote root')
    root = root.rstrip('/')
    prefix = root + '/_app_builds/native-app-v1/' + SOURCE + '/bench-default/'
    require(type(artifacts) is str and re.fullmatch(re.escape(prefix) + '[0-9a-f]{32}/artifacts', artifacts),
            'ADC upload requires the fresh checked artifact path')
    require(folder == root + '/' + SOURCE + '/ui_adc_probe', 'ADC staged folder differs')
    build = artifacts.removesuffix('/artifacts') + '/build'
    return {build + '/ui_adc_probe.ino.elf': ELF_HASH,
            artifacts + '/ui_adc_probe.ino.elf-zsk.bin': BINARY_HASH}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def write_exclusive(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def output_text(value):
    if value is None:
        return ''
    return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else str(value)


def launch(board, target, argv, outcome_path):
    outcome = dict(schema_version=1, run_id=RUN_ID, returncode=None,
                   stdout='', stderr='', timed_out=False, error=None)
    try:
        result = board.remote(target, argv, capture=True, timeout=120)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, argv, result.stdout, result.stderr)
        outcome.update(returncode=result.returncode, stdout=output_text(result.stdout), stderr=output_text(result.stderr))
    except Exception as error:
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
    pins = artifact_pins(board_module, artifact_folder, board_folder)
    policy.verify_hashes(board_module.remote, target, pins)
    revalidate(board_module, target, scope)
    root = scope['root']
    attempt = safe_path(root, ATTEMPT, missing=True)
    outcome = safe_path(root, OUTCOME, missing=True)
    argv = ['arduino-cli', 'upload', '--fqbn', FQBN, '--input-dir', artifact_folder, board_folder]
    claim = dict(schema_version=1, run_id=RUN_ID, target=target, source_sha256=SOURCE,
                 elf_sha256=ELF_HASH, binary_sha256=BINARY_HASH,
                 approval_sha256=scope['approval_sha256'], started_utc=utc_now(), argv=argv)
    write_exclusive(attempt, claim)
    launch(board_module, target, argv, outcome)
