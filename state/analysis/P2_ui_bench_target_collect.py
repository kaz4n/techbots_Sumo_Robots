# Freezes the exact finite A1 raw/decoder bench sources and completed generic CLI artifacts.
# Uses board Linux/offline ELF tools only; never attaches to or resets the MCU.
# Preserves complete source hashes, artifact bytes, tool identities and failures.
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'state/analysis/P2_ui_bench_raw'
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board
import app_build_policy as policy

PROGRAM = r'''
import base64,hashlib,json,pathlib,subprocess,sys
root=pathlib.Path(sys.argv[1]); mode=sys.argv[2]
build=pathlib.Path(sys.argv[3]); folder=pathlib.Path(sys.argv[4])
prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
base=pathlib.Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf')
sources={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
 for p in root.rglob('*') if p.is_file() and p.relative_to(root).parts[0]!='artifacts'}
records=[]
def run(args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=30)
 return dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
paths=[build/('ui.ino'+suffix) for suffix in ('.elf','_debug.elf','_temp.elf')]
paths.append(folder/'ui.ino.elf-zsk.bin')
for p in paths:
 blob=p.read_bytes()
 record=dict(name=p.name,path=str(p),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),base64=base64.b64encode(blob).decode())
 if p.suffix=='.elf':
  record['commands']=[run([prefix+'readelf','-SW',str(p)]),run([prefix+'readelf','-rW',str(p)]),
   run([prefix+'nm','-S',str(p)]),run([prefix+'objdump','-dr',str(p)])]
 records.append(record)
debug=build/'ui.ino_debug.elf'
gdb=[prefix+'gdb','-nx','-nh','-batch',str(debug),'-ex','set language c++','-ex','set max-value-size unlimited']
for q in ['p sizeof(ui_bench::Runner)','p sizeof(ui_bench::Native)','ptype /o ui_bench::Runner']:
 gdb+=['-ex',q]
paths=[base,pathlib.Path(prefix+'readelf'),pathlib.Path(prefix+'nm'),pathlib.Path(prefix+'objdump'),pathlib.Path(prefix+'gdb')]
print(json.dumps(dict(source_files=sources,records=records,abi=run(gdb),
 file_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}),indent=2))
'''


def freeze(source):
    output = RAW / ('target_sources_' + source[:8])
    manifest = output / 'manifest.json'
    if manifest.exists():
        return json.loads(manifest.read_text())
    stage = ROOT / 'build/stage/ui'
    payloads = {p.relative_to(stage).as_posix(): p.read_bytes()
                for p in stage.rglob('*') if p.is_file()}
    expected_files = 96 if 'README.md' in payloads else 95
    if len(payloads) != expected_files or board.source_hash(stage) != source:
        raise ValueError('Expected exact selected95-source-file tree plus optional bench README')
    output.mkdir(parents=True, exist_ok=False)
    for name, blob in payloads.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
    data = dict(source_sha256=source,
                source_files={n: hashlib.sha256(b).hexdigest() for n, b in sorted(payloads.items())})
    manifest.write_text(json.dumps(data, indent=2) + '\n')
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('mode', choices=('bench-default', 'bench-immediate'))
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{64}', args.source):
        raise ValueError('Requires explicit source SHA256')
    frozen = freeze(args.source)
    remote_root = os.environ['SUMO_REMOTE_ROOT'].rstrip('/') + '/' + args.source + '/ui'
    artifact_path = remote_root + '/artifacts/' + args.mode
    build_path = artifact_path
    checked = None
    if args.receipt:
        checked = policy.decode((args.receipt / 'verified.json').read_text())
        expected_fqbn = policy.BASE_FQBN + (':wait_linux_boot=no' if args.mode == 'bench-immediate' else '')
        assert checked['source_sha256'] == args.source and checked['fqbn'] == expected_fqbn
        assert checked['compiler_returncode'] == 0 and checked['precompile_checks'] is True
        assert checked['policy'] == policy.POLICY and checked['used_libraries'] == []
        assert '/' + args.mode + '/' in checked['build_path']
        policy.validate_result((args.receipt / 'compile.stdout.json').read_text(), expected_fqbn,
            '-DMATCH=0 -DMOTORS_ALLOWED=0', checked['build_path'], project='ui.ino')
        assert policy.decode((args.receipt / 'command.json').read_text())[-1] == remote_root
        build_path, artifact_path = checked['build_path'], checked['artifacts']
    output = RAW / ('target_' + args.source[:8] + '_' + args.mode + ('_checked' if checked else ''))
    output.mkdir(parents=True, exist_ok=False)
    if checked:
        shutil.copytree(args.receipt, output / 'build_receipt')
    command = ['python3', '-c', PROGRAM, remote_root, args.mode, build_path, artifact_path]
    receipt = dict(argv=command, start_utc=datetime.now(timezone.utc).isoformat(),
                   scope=('Checked native policy' if checked else 'Generic bench, not checked policy') +
                         '; completed board Linux/offline files only; no upload/reset/MCU')
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    result = board.remote(board.target(), command, capture=True, timeout=180)
    (output / 'stdout.json').write_text(result.stdout, encoding='utf-8')
    (output / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
    receipt.update(returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    data = json.loads(result.stdout)
    assert data['source_files'] == frozen['source_files']
    assert len([r for r in data['records'] if r['name'].endswith('.elf')]) == 3
    for record in data['records']:
        blob = base64.b64decode(record.pop('base64'), validate=True)
        assert hashlib.sha256(blob).hexdigest() == record['sha256']
        if checked:
            assert checked['file_sha256'][record['path']] == record['sha256']
        assert Path(record['name']).name == record['name']
        (output / record['name']).write_bytes(blob)
    data.update(source_sha256=args.source, mode=args.mode)
    (output / 'audit.json').write_text(json.dumps(data, indent=2) + '\n')
    commands = [data['abi']] + [c for r in data['records'] for c in r.get('commands', [])]
    assert result.returncode == 0 and not result.stderr
    assert all(c['returncode'] == 0 and not c['stderr'] for c in commands)
    print(json.dumps(dict(path=str(output.relative_to(ROOT)), sources=len(data['source_files']), artifacts=len(data['records']))))


if __name__ == '__main__':
    main()
