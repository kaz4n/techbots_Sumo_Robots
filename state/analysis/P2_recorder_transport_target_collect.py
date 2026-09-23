# Freezes the exact D116 default recorder sources and checked CLI artifacts.
# Uses board Linux/offline ELF tools only; never attaches to or resets the MCU.
# Preserves source hashes, artifact bytes, tool identities and failure receipts.
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
RAW = ROOT / 'state/analysis/P2_recorder_transport_raw'
PROJECT = 'recorder.ino'
BENCH_FILES = {'recorder.ino', 'src/recorder_transport.h', 'src/recorder_transport.cpp',
               'src/recorder_transport_io.cpp', 'src/recorder_transport_scenario.cpp'}
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board
import app_build_policy as policy

PROGRAM = r'''
import base64,hashlib,json,pathlib,subprocess,sys
root=pathlib.Path(sys.argv[1]); build=pathlib.Path(sys.argv[2]); folder=pathlib.Path(sys.argv[3])
prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
base=pathlib.Path('/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf')
data=dict(source_files={},records=[],abi=None,file_sha256={})

def text(value):
 return value.decode('utf-8',errors='replace') if isinstance(value,bytes) else value or ''

def run(args):
 try:
  r=subprocess.run(args,capture_output=True,text=True,timeout=30)
  return dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
 except Exception as exc:
  return dict(argv=args,returncode=getattr(exc,'returncode',None),
   stdout=text(getattr(exc,'stdout','')),stderr=text(getattr(exc,'stderr','')),
   exception=type(exc).__name__,message=str(exc))

try:
 files=sorted(p for p in root.rglob('*') if p.is_file())
 if any(p.is_symlink() for p in root.rglob('*')):
  raise ValueError('Remote source symlink')
 data['source_files']={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
 paths=[build/('recorder.ino'+suffix) for suffix in ('.elf','_debug.elf','_temp.elf')]
 paths.append(folder/'recorder.ino.elf-zsk.bin')
 for p in paths:
  blob=p.read_bytes()
  record=dict(name=p.name,path=str(p),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),base64=base64.b64encode(blob).decode())
  data['records'].append(record)
  if p.suffix=='.elf':
   record['commands']=[run([prefix+'readelf',option,str(p)]) for option in ('-SW','-rW','-sW')]
   record['commands'] += [run([prefix+'nm','-S',str(p)]),run([prefix+'objdump','-dr',str(p)])]
 debug=build/'recorder.ino_debug.elf'
 gdb=[prefix+'gdb','-nx','-nh','-batch',str(debug),'-ex','set language c++','-ex','set max-value-size unlimited']
 for name in ('recorder_transport::Runner','recorder_transport::Report','recorder_transport::ClockPort',
              'app::Transaction','app::TransactionReport','app::DumpPort','recorder::AttemptRecorder',
              'recorder::FrameBuffer','recorder::dump::Transfer','recorder::dump::UnoQDumpPort'):
  gdb+=['-ex','p sizeof('+name+')','-ex','ptype /o '+name]
 data['abi']=run(gdb)
 for p in [base]+[pathlib.Path(prefix+name) for name in ('readelf','nm','objdump','gdb')]:
  data['file_sha256'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
except Exception as exc:
 data['error']=dict(exception=type(exc).__name__,message=str(exc))
finally:
 print(json.dumps(data,indent=2))
sys.exit(1 if 'error' in data else 0)
'''


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def freeze(source):
    stage = ROOT / 'build/stage/recorder'
    board.check_source(stage)
    payloads = {p.relative_to(stage).as_posix(): p.read_bytes()
                for p in sorted(stage.rglob('*')) if p.is_file()}
    shared = {'src/config.h'}
    for module in ('core', 'hal'):
        shared.update(p.relative_to(ROOT).as_posix()
                      for p in (ROOT / 'src' / module).rglob('*') if p.is_file())
    shared.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'src/app').rglob('*')
                  if p.is_file() and p.suffix in ('.c', '.cc', '.cpp', '.h', '.hpp')
                  and p.relative_to(ROOT / 'src/app').parts[0] != 'src')
    require(len(shared) == 90 and set(payloads) == shared | BENCH_FILES,
            'Requires exact 95 staged files: 90 shared and five recorder files')
    digest = hashlib.sha256()
    for name, blob in payloads.items():
        digest.update(name.encode() + b'\0')
        digest.update(blob)
    require(digest.hexdigest() == source, 'Staged source SHA256 differs')
    data = dict(source_sha256=source, source_files={
        name: hashlib.sha256(blob).hexdigest() for name, blob in payloads.items()})
    output = RAW / ('target_sources_' + source[:8])
    if output.exists():
        require(policy.decode((output / 'manifest.json').read_text()) == data,
                'Existing source freeze differs')
        actual = {p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in output.rglob('*') if p.is_file() and p.name != 'manifest.json'}
        require(actual == data['source_files'], 'Existing source copies differ')
        return data
    output.mkdir(parents=True, exist_ok=False)
    for name, blob in payloads.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
    write_json(output / 'manifest.json', data)
    return data


def checked_paths(args, remote_root):
    checked = policy.decode((args.receipt / 'verified.json').read_text())
    require(checked['source_sha256'] == args.source and checked['fqbn'] == policy.BASE_FQBN,
            'Receipt source/default FQBN differs')
    require(checked['compiler_returncode'] == 0 and checked['precompile_checks'] is True
            and checked['policy'] == policy.POLICY and checked['used_libraries'] == [],
            'Requires successful checked native policy receipt without libraries')
    prefix = os.environ['SUMO_REMOTE_ROOT'].rstrip('/') + '/_app_builds/'
    prefix += policy.POLICY + '/' + args.source + '/bench-default/'
    require(re.fullmatch(re.escape(prefix) + r'[0-9a-f]{32}/build', checked['build_path'])
            and checked['artifacts'] == checked['build_path'][:-5] + 'artifacts',
            'Receipt must use one exact checked default build/artifact pair')
    policy.validate_result((args.receipt / 'compile.stdout.json').read_text(),
        policy.BASE_FQBN, '-DMATCH=0 -DMOTORS_ALLOWED=0', checked['build_path'], project=PROJECT)
    command = ['arduino-cli', 'compile', '--json', '--fqbn', policy.BASE_FQBN,
               '--build-path', checked['build_path'], '--output-dir', checked['artifacts'],
               '--build-property', 'compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0',
               '--build-property', 'compiler.c.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0',
               '--build-property', 'build.library_discovery_phase_flag=' + policy.DISCOVERY,
               remote_root]
    require(policy.decode((args.receipt / 'command.json').read_text()) == command,
            'Receipt compile argv differs from exact recorder default command')
    return checked


def preserve_streams(output, result):
    for attribute, name in (('stdout', 'stdout.json'), ('stderr', 'stderr.txt')):
        value = getattr(result, attribute, '') or ''
        blob = value if isinstance(value, bytes) else value.encode('utf-8')
        (output / name).write_bytes(blob)


def save_artifacts(output, data, checked, frozen):
    require(data['source_files'] == frozen['source_files'], 'Remote source tree differs')
    expected = {PROJECT + suffix for suffix in ('.elf', '_debug.elf', '_temp.elf', '.elf-zsk.bin')}
    require(len(data['records']) == 4 and {r['name'] for r in data['records']} == expected,
            'Requires exactly three named ELFs and one ZSK')
    for record in data['records']:
        blob = base64.b64decode(record.pop('base64'), validate=True)
        digest = hashlib.sha256(blob).hexdigest()
        folder = checked['build_path'] if record['name'].endswith('.elf') else checked['artifacts']
        require(record['path'] == folder + '/' + record['name'] and len(blob) == record['bytes'],
                'Artifact path/length differs')
        require(digest == record['sha256'] == checked['file_sha256'][record['path']],
                'Artifact SHA256 differs from checked receipt')
        (output / record['name']).write_bytes(blob)
    write_json(output / 'audit.json', data)
    commands = [data['abi']] + [c for r in data['records'] for c in r.get('commands', [])]
    require(len(commands) == 16 and all(c['returncode'] == 0 and not c['stderr']
                                       and 'exception' not in c for c in commands),
            'One or more offline ELF/ABI commands failed; evidence retained')


def collect(args, output, receipt):
    frozen = freeze(args.source)
    shutil.copytree(args.receipt, output / 'build_receipt')
    require(os.environ.get('SUMO_TRANSPORT') == 'adb' and board.target() == '2629958581',
            'Requires explicit ADB target 2629958581')
    remote_root = policy.absolute_path(os.environ['SUMO_REMOTE_ROOT'].rstrip('/'))
    remote_root += '/' + args.source + '/recorder'
    checked = checked_paths(args, remote_root)
    command = ['python3', '-c', PROGRAM, remote_root, checked['build_path'], checked['artifacts']]
    receipt.update(argv=command, transport='adb', target='2629958581', timeout_seconds=180)
    write_json(output / 'receipt.json', receipt)
    try:
        result = board.remote(board.target(), command, capture=True, timeout=180)
    except BaseException as exc:
        preserve_streams(output, exc)
        receipt['returncode'] = getattr(exc, 'returncode', None)
        raise
    preserve_streams(output, result)
    receipt['returncode'] = result.returncode
    data = policy.decode(result.stdout)
    data.update(source_sha256=args.source, mode=args.mode)
    require(result.returncode == 0 and not result.stderr and 'error' not in data,
            'Remote collection failed; original output retained')
    save_artifacts(output, data, checked, frozen)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('mode', choices=('bench-default',))
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    require(re.fullmatch(r'[0-9a-f]{64}', args.source), 'Requires explicit source SHA256')
    output = RAW / ('target_' + args.source[:8] + '_bench-default_checked')
    output.mkdir(parents=True, exist_ok=False)
    receipt = dict(start_utc=datetime.now(timezone.utc).isoformat(), status='STARTED',
                   source_sha256=args.source, mode=args.mode, build_receipt=str(args.receipt),
                   scope='Checked D116 board Linux/offline files only; no upload/reset/MCU')
    write_json(output / 'receipt.json', receipt)
    try:
        collect(args, output, receipt)
        receipt['status'] = 'COLLECTED'
    except BaseException as exc:
        receipt.update(status='FAILED', exception=type(exc).__name__, message=str(exc))
        raise
    finally:
        receipt['end_utc'] = datetime.now(timezone.utc).isoformat()
        write_json(output / 'receipt.json', receipt)
    print(json.dumps(dict(path=str(output.relative_to(ROOT)), sources=95, artifacts=4)))


if __name__ == '__main__':
    main()
