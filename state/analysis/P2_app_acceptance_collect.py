# Collect completed checked-app source, object and ELF evidence from board Linux.
# Reuse the D098 offline audit program without any compile, upload or MCU action.
# Verified against receipt hashes, exact current/D098 sources and three ELF files.
import argparse
import ast
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
import app_build_policy as policy
import board_tool as board


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def reused_program():
    source = REPO / 'state/analysis/P2_bridge_dependency_target_audit.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    matches = [node.value for node in tree.body if isinstance(node, ast.Assign)
               and any(isinstance(target, ast.Name) and target.id == 'program'
                       for target in node.targets)]
    if len(matches) != 1:
        raise ValueError('Expected the unique D098 offline program literal')
    program = ast.literal_eval(matches[0])
    if not isinstance(program, str):
        raise ValueError('D098 program is not a literal string')
    return program, dict(path=str(source.relative_to(REPO)),
                         file_sha256=sha256(source.read_bytes()),
                         program_sha256=sha256(program.encode()))


SUPPLEMENT = r'''
import base64
digest=hashlib.sha256()
for name in sorted(files):
    digest.update(name.encode()+b'\0'); digest.update((root/name).read_bytes())
bundles=[]
for path in [*sorted(artifacts.glob('*.elf')), pathlib.Path(sys.argv[4])/'app.ino.elf-zsk.bin']:
    payload=path.read_bytes()
    bundles.append(dict(name=path.name,path=str(path),bytes=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),base64=base64.b64encode(payload).decode(),
        alloc_sections=alloc_sections(path) if path.suffix=='.elf' else []))
print(json.dumps(dict(source_sha256=digest.hexdigest(),bundles=bundles)))
'''


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def current_sources():
    paths = [REPO / 'src/config.h']
    for module in ('core', 'hal'):
        paths.extend(path for path in (REPO / 'src' / module).rglob('*') if path.is_file())
    paths.extend(path for path in (REPO / 'src/app').rglob('*')
                 if path.is_file() and path.suffix in ('.c', '.cc', '.cpp', '.h', '.hpp'))
    actual = {path.relative_to(REPO).as_posix(): sha256(path.read_bytes()) for path in paths}
    for path in (REPO / 'src/app').iterdir():
        if path.is_file() and path.name != '.gitkeep' and path.suffix not in ('.c', '.cc', '.cpp', '.h', '.hpp'):
            actual[path.name] = sha256(path.read_bytes())
    return actual


def collect(receipt, mode):
    verified = policy.decode((receipt / 'verified.json').read_text(encoding='utf-8'))
    command = policy.decode((receipt / 'command.json').read_text(encoding='utf-8'))
    if verified.get('compiler_returncode') != 0 or verified.get('precompile_checks') is not True:
        raise ValueError('Requires a completed corrected-wrapper receipt')
    flags = '-DMATCH=1 -DMOTORS_ALLOWED=1' if mode == 'match-immediate' else '-DMATCH=0 -DMOTORS_ALLOWED=0'
    props = policy.validate_result((receipt / 'compile.stdout.json').read_text(encoding='utf-8'),
                                   verified['fqbn'], flags, verified['build_path'])
    if verified['policy'] != 'native-app-v1' or '/' + mode + '/' not in verified['build_path']:
        raise ValueError('Policy/mode mismatch')
    baseline = policy.decode((REPO / 'state/analysis/P2_bridge_dependency_raw/570ef35f_candidate.json').read_text())
    if verified['source_sha256'] != baseline['source_sha256']:
        raise ValueError('This audit requires the frozen D098 source')
    if command[-1] != os.environ['SUMO_REMOTE_ROOT'].rstrip('/') + '/' + verified['source_sha256'] + '/app':
        raise ValueError('Unexpected exact source directory')
    output = REPO / 'state/analysis/P2_app_acceptance_raw' / mode
    output.mkdir(parents=True, exist_ok=False)
    program, provenance = reused_program()
    args = ['python3', '-c', program + SUPPLEMENT, command[-1], mode,
            verified['build_path'], verified['artifacts']]
    execution = dict(start_utc=datetime.now(timezone.utc).isoformat(),
                     receipt=str(receipt.relative_to(REPO)), mode=mode,
                     transport=board.transport(), target=board.target(),
                     scope='Board Linux files and offline ELF only; no compile/upload/reset/MCU',
                     reused_program=provenance, argv=args)
    write_json(output / 'command.json', execution)
    try:
        result = board.remote(board.target(), args, capture=True, timeout=180)
    except subprocess.CalledProcessError as error:
        (output / 'stdout.txt').write_text(error.stdout or '', encoding='utf-8')
        (output / 'stderr.txt').write_text(error.stderr or '', encoding='utf-8')
        execution.update(returncode=error.returncode, end_utc=datetime.now(timezone.utc).isoformat())
        write_json(output / 'command.json', execution)
        raise
    (output / 'stdout.txt').write_text(result.stdout, encoding='utf-8')
    (output / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
    execution.update(returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
    write_json(output / 'command.json', execution)
    decoder = json.JSONDecoder()
    audit, end = decoder.raw_decode(result.stdout)
    supplement = policy.decode(result.stdout[end:].strip())
    checks = dict(source_digest=supplement['source_sha256'] == verified['source_sha256'],
                  exact_source_set=audit['source_files'] == baseline['source_files'],
                  current_sources=current_sources() == audit['source_files'])
    for bundle in supplement['bundles']:
        payload = base64.b64decode(bundle.pop('base64'), validate=True)
        (output / bundle['name']).write_bytes(payload)
        checks[bundle['name']] = (sha256(payload) == bundle['sha256'] == verified['file_sha256'][bundle['path']])
    checks['three_elf'] = len(audit['records']) == 3
    checks['elf_record_hashes'] = all(record['sha256'] == verified['file_sha256'][record['path']]
                                     for record in audit['records'])
    audit.update(source_sha256=supplement['source_sha256'], mode=mode,
                 properties=props, bundles=supplement['bundles'], checks=checks,
                 receipt_sha256={name: sha256((receipt / name).read_bytes()) for name in
                                 ('verified.json', 'command.json', 'compile.stdout.json')})
    write_json(output / 'audit.json', audit)
    if not all(checks.values()):
        raise ValueError('Evidence identity failed; complete raw output preserved: ' + str(checks))
    print(json.dumps(dict(output=str(output.relative_to(REPO)), checks=checks,
                          sources=len(audit['source_files']), objects=len(audit['objects']),
                          native_imports=len(audit['native_names']))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipt', type=Path)
    parser.add_argument('mode', choices=('bench-default', 'bench-immediate', 'match-immediate'))
    arguments = parser.parse_args()
    collect(arguments.receipt.resolve(), arguments.mode)
