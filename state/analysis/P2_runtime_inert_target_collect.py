# Collect the exact completed D104 probe source and target artifacts.
# Reuse offline D098 inspection with explicit probe filename/source invariants.
# Linux file and ELF inspection only; no firmware compile, upload or MCU access.
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'state/analysis/P2_runtime_inert_raw'
SOURCE = '2bd817c4e535324964a031cdd44720f26fd145a3cd317ab7b3ced089f35db7e5'
PROJECT = 'runtime_inert.ino'
spec = importlib.util.spec_from_file_location('prior', ROOT / 'state/analysis/P2_app_acceptance_collect.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)


def freeze():
    old = json.loads((ROOT / 'state/analysis/P2_service_reset_raw/target_sources_1fbd7238/manifest.json').read_text())
    shared = prior.current_sources()
    assert shared == old['source_files'] and len(shared) == 87
    del shared['app.ino']
    payloads = {name: (ROOT / name).read_bytes() for name in shared}
    bench = ROOT / 'bench/runtime_inert'
    selected = json.loads((OUT / 'implementation/source_freeze.json').read_text())
    assert len(selected['files']) == 5
    # Explicit final correction: enforce the observed closing-clock deadline too.
    expected = {row['path']: row['sha256'] for row in selected['files']}
    expected['bench/runtime_inert/src/runtime_bench.cpp'] = '987eb73ad16510ae2895e938aba3ac3d6e197f7987cb5b8c1d7c6df5982f0b89'
    observed = {path.relative_to(ROOT).as_posix(): prior.sha256(path.read_bytes())
                for path in bench.rglob('*') if path.is_file()}
    assert observed == expected
    for name in observed:
        path = ROOT / name
        payloads[path.relative_to(bench).as_posix()] = path.read_bytes()
    assert len(payloads) == 91 and PROJECT in payloads and 'app.ino' not in payloads
    digest = hashlib.sha256()
    for name, data in sorted(payloads.items()):
        digest.update(name.encode()+b'\0'); digest.update(data)
    assert digest.hexdigest() == SOURCE
    target = OUT / ('target_sources_' + SOURCE[:8])
    target.mkdir(parents=True, exist_ok=False)
    for name, data in payloads.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    manifest = dict(source_sha256=SOURCE, source_files={n: prior.sha256(b) for n, b in payloads.items()},
                    shared_d103_files=86, new_bench_files=5,
                    frozen_utc=datetime.now(timezone.utc).isoformat())
    prior.write_json(target / 'manifest.json', manifest)
    return manifest


def collect(receipt):
    checked = prior.policy.decode((receipt / 'verified.json').read_text())
    assert checked['source_sha256'] == SOURCE and checked['compiler_returncode'] == 0
    assert checked['precompile_checks'] is True and checked['policy'] == 'native-app-v1'
    assert checked['fqbn'] == 'arduino:zephyr:unoq'
    props = prior.policy.validate_result((receipt / 'compile.stdout.json').read_text(), checked['fqbn'],
        '-DMATCH=0 -DMOTORS_ALLOWED=0', checked['build_path'], PROJECT)
    command = prior.policy.decode((receipt / 'command.json').read_text())
    assert command[-1] == os.environ['SUMO_REMOTE_ROOT'].rstrip('/') + '/' + SOURCE + '/runtime_inert'
    assert '/bench-default/' in checked['build_path']
    frozen = freeze()
    output = OUT / ('target_' + SOURCE[:8])
    output.mkdir(parents=True, exist_ok=False)
    shutil.copytree(receipt, output / 'build_receipt')
    program, provenance = prior.reused_program()
    assert program.count("'app.ino.cpp'") == 1
    program = program.replace("'app.ino.cpp'", "'runtime_inert.ino.cpp'")
    assert program.count("markers=('app::'") == 1
    program = program.replace("markers=('app::'", "markers=('runtime_bench::','runtime_native::','app::'")
    supplement = prior.SUPPLEMENT.replace('app.ino.elf-zsk.bin', PROJECT + '.elf-zsk.bin')
    args = ['python3', '-c', program + supplement, command[-1], 'bench-default',
            checked['build_path'], checked['artifacts']]
    run = dict(argv=args, source_sha256=SOURCE, reused_program=provenance,
        adaptations=['generated probe filename', 'probe disassembly markers', 'probe package filename'],
        start_utc=datetime.now(timezone.utc).isoformat(),
        scope='Board Linux file/offline ELF only; no compile/upload/reset/MCU')
    prior.write_json(output / 'command.json', run)
    try:
        result = prior.board.remote(prior.board.target(), args, capture=True, timeout=180)
    except Exception as error:
        run.update(error=str(error), returncode=getattr(error,'returncode',None),
                   end_utc=datetime.now(timezone.utc).isoformat())
        prior.write_json(output / 'command.json', run)
        for name in ('stdout','stderr'):
            value = getattr(error,name,'') or ''
            if isinstance(value,bytes): value=value.decode(errors='replace')
            (output / (name+'.txt')).write_text(value,encoding='utf-8')
        raise
    (output / 'stdout.txt').write_text(result.stdout, encoding='utf-8')
    (output / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
    run.update(returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
    prior.write_json(output / 'command.json', run)
    audit, end = json.JSONDecoder().raw_decode(result.stdout)
    extra = prior.policy.decode(result.stdout[end:].strip())
    checks = dict(source_digest=extra['source_sha256'] == SOURCE,
        exact_frozen_source=audit['source_files'] == frozen['source_files'],
        three_elf=len(audit['records']) == 3,
        exact_artifact_names=sorted(b['name'] for b in extra['bundles']) == sorted(
            PROJECT+s for s in ('.elf', '_debug.elf', '_temp.elf', '.elf-zsk.bin')))
    for bundle in extra['bundles']:
        data = base64.b64decode(bundle.pop('base64'), validate=True)
        (output / bundle['name']).write_bytes(data)
        checks[bundle['name']] = prior.sha256(data) == bundle['sha256'] == checked['file_sha256'][bundle['path']]
    audit.update(source_sha256=SOURCE, mode='bench-default', project=PROJECT,
                 properties=props, bundles=extra['bundles'], checks=checks)
    prior.write_json(output / 'audit.json', audit)
    assert result.returncode == 0 and all(checks.values()), checks
    print(json.dumps(dict(path=str(output.relative_to(ROOT)), files=len(audit['source_files']),
                          objects=len(audit['objects']), checks=checks)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('receipt', type=Path)
    collect(parser.parse_args().receipt.resolve())
