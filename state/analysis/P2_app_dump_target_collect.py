# Collect D101 completed app artifacts from board Linux only.
# Freeze the explicitly selected new source before reusing D098 ELF inspection.
# Hashes bind 85 source files, three ELFs and package to a checked D100 receipt.
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
import app_build_policy as policy
import board_tool as board

spec = importlib.util.spec_from_file_location('prior_collector',
    REPO / 'state/analysis/P2_app_acceptance_collect.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
SOURCE = '96c80701b2149cbc080c0416e5beacfc17d2da8a21ab9831fa6c20d1ec58a8a7'
RAW = REPO / 'state/analysis/P2_app_dump_raw'


def freeze_source():
    folder = RAW / ('target_sources_' + SOURCE[:8])
    manifest = folder / 'manifest.json'
    if manifest.exists():
        return policy.decode(manifest.read_text())
    files = prior.current_sources()
    if len(files) != 85:
        raise ValueError('D101 expects the explicitly selected 85-file source')
    digest = hashlib.sha256()
    payloads = {}
    for name in sorted(files):
        source = REPO / ('src/app/app.ino' if name == 'app.ino' else name)
        payload = source.read_bytes()
        if prior.sha256(payload) != files[name]:
            raise ValueError('Source changed while freezing')
        digest.update(name.encode() + b'\0'); digest.update(payload)
        payloads[name] = payload
    if digest.hexdigest() != SOURCE:
        raise ValueError('Current source differs from explicitly selected D101 receipt')
    folder.mkdir(parents=True, exist_ok=False)
    for name, payload in payloads.items():
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    data = dict(source_sha256=SOURCE, source_files=files,
                frozen_utc=datetime.now(timezone.utc).isoformat())
    prior.write_json(manifest, data)
    return data


def collect(receipt, mode):
    frozen = freeze_source()
    checked = policy.decode((receipt / 'verified.json').read_text())
    if checked['source_sha256'] != SOURCE or checked['compiler_returncode'] != 0 or checked['precompile_checks'] is not True:
        raise ValueError('Requires the completed corrected-wrapper D101 receipt')
    flags = '-DMATCH=1 -DMOTORS_ALLOWED=1' if mode == 'match-immediate' else '-DMATCH=0 -DMOTORS_ALLOWED=0'
    props = policy.validate_result((receipt / 'compile.stdout.json').read_text(),
                                   checked['fqbn'], flags, checked['build_path'])
    if '/' + mode + '/' not in checked['build_path']:
        raise ValueError('Wrong build mode')
    command = policy.decode((receipt / 'command.json').read_text())
    if command[-1] != os.environ['SUMO_REMOTE_ROOT'].rstrip('/') + '/' + SOURCE + '/app':
        raise ValueError('Wrong remote source tree')
    output = RAW / ('target_' + SOURCE[:8] + '_' + mode)
    output.mkdir(parents=True, exist_ok=False)
    shutil.copytree(receipt, output / 'build_receipt')
    program, provenance = prior.reused_program()
    args = ['python3', '-c', program + prior.SUPPLEMENT, command[-1], mode,
            checked['build_path'], checked['artifacts']]
    run = dict(argv=args, mode=mode, source_sha256=SOURCE,
               start_utc=datetime.now(timezone.utc).isoformat(), reused_program=provenance,
               scope='Completed board Linux files/offline ELF only; no compile/upload/reset/MCU')
    prior.write_json(output / 'command.json', run)
    try:
        result = board.remote(board.target(), args, capture=True, timeout=180)
    except Exception as error:
        run.update(error=str(error), returncode=getattr(error, 'returncode', None),
                   end_utc=datetime.now(timezone.utc).isoformat())
        prior.write_json(output / 'command.json', run)
        for name in ('stdout', 'stderr'):
            data = getattr(error, name, '') or ''
            if isinstance(data, bytes): data = data.decode(errors='replace')
            (output / (name + '.txt')).write_text(data, encoding='utf-8')
        raise
    (output / 'stdout.txt').write_text(result.stdout, encoding='utf-8')
    (output / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
    run.update(returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
    prior.write_json(output / 'command.json', run)
    audit, end = json.JSONDecoder().raw_decode(result.stdout)
    supplement = policy.decode(result.stdout[end:].strip())
    checks = dict(source_digest=supplement['source_sha256'] == SOURCE,
                  exact_frozen_source=audit['source_files'] == frozen['source_files'],
                  current_source_at_collection=prior.current_sources() == frozen['source_files'],
                  three_elf=len(audit['records']) == 3)
    for bundle in supplement['bundles']:
        payload = base64.b64decode(bundle.pop('base64'), validate=True)
        (output / bundle['name']).write_bytes(payload)
        checks[bundle['name']] = prior.sha256(payload) == bundle['sha256'] == checked['file_sha256'][bundle['path']]
    audit.update(source_sha256=SOURCE, properties=props, mode=mode, checks=checks,
                 bundles=supplement['bundles'])
    prior.write_json(output / 'audit.json', audit)
    # A later concurrent revision does not invalidate this completed frozen build.
    # Preserve that observation, but bind acceptance to the frozen set and digest.
    if not all(value for key, value in checks.items() if key != 'current_source_at_collection'):
        raise ValueError('Identity failure; complete raw evidence preserved')
    print(json.dumps(dict(path=str(output.relative_to(REPO)), checks=checks,
                          files=len(audit['source_files']), objects=len(audit['objects']))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('receipt', type=Path)
    parser.add_argument('mode', choices=('bench-default', 'match-immediate'))
    parser.add_argument('--source', default=SOURCE)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{64}', args.source):
        raise ValueError('Expected an explicit complete source SHA256')
    SOURCE = args.source
    collect(args.receipt.resolve(), args.mode)
