# Stages Arduino sketches and invokes explicit board-side commands.
# Fails closed on missing configuration and separates builds from execution.
# Verified by controlled transport tests, not a claim of target compilation.
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SSH_OPTIONS = ['-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
               '-o', 'ConnectTimeout=10']
CORE_VERSION = '1.0.0'
BASE_FQBN = 'arduino:zephyr:unoq'


def fail(message):
    raise ValueError(message)


def setting(name, pattern):
    value = os.environ.get(name, '')
    if not re.fullmatch(pattern, value):
        fail(f'{name} is missing or invalid; see tools/README.md')
    return value


def target():
    if transport() == 'adb':
        return setting('SUMO_ADB_SERIAL', r'[A-Za-z0-9][A-Za-z0-9_.:-]*')
    return setting('SUMO_SSH_TARGET', r'[A-Za-z0-9_][A-Za-z0-9_.@-]*')


def transport():
    value = os.environ.get('SUMO_TRANSPORT', 'ssh')
    if value not in ('ssh', 'adb'):
        fail('SUMO_TRANSPORT must be ssh or adb')
    return value


def adb_executable():
    value = os.environ.get('SUMO_ADB_EXECUTABLE', 'adb')
    if not value or shutil.which(value) is None:
        fail('required local ADB executable is unavailable; see SUMO_ADB_EXECUTABLE')
    return value


def require_transport(sync=False):
    if transport() == 'adb':
        adb_executable()
    else:
        require_tools('ssh', *(['rsync'] if sync else []))


def require_tools(*names):
    for name in names:
        if shutil.which(name) is None:
            fail(f'required local tool is unavailable: {name}')


def check_source(folder):
    if not folder.resolve().is_relative_to(ROOT.resolve()):
        fail('staged source must remain inside the project')
    for ancestor in [folder, *folder.parents]:
        if ancestor == ROOT:
            break
        if ancestor.is_symlink():
            fail('symlinks are not permitted in staged source ancestry')
    if any(p.is_symlink() for p in folder.rglob('*')):
        fail('symlinks are not permitted in staged source')


def remote(board, args, capture=False, timeout=None):
    prefix = ([adb_executable(), '-s', board, 'shell', '-T']
              if transport() == 'adb' else ['ssh', *SSH_OPTIONS, board])
    return subprocess.run([*prefix, shlex.join(args)],
                          check=True, text=True, capture_output=capture,
                          timeout=timeout, stdin=subprocess.DEVNULL)


def sync_sources(board, folder, board_folder):
    if transport() == 'ssh':
        subprocess.run(['rsync', '-rlt', '--safe-links', '-e',
                        shlex.join(['ssh', *SSH_OPTIONS]), str(folder) + '/',
                        f'{board}:{board_folder}/'], check=True)
        return
    files = sorted(p for p in folder.rglob('*') if p.is_file())
    parents = sorted({f'{board_folder}/{p.relative_to(folder).parent.as_posix()}'
                      for p in files})
    remote(board, ['mkdir', '-p', *parents])
    # Exact filenames avoid adb's different existing-directory nesting semantics.
    for item in files:
        destination = f'{board_folder}/{item.relative_to(folder).as_posix()}'
        subprocess.run([adb_executable(), '-s', board, 'push', str(item), destination],
                       check=True, stdin=subprocess.DEVNULL)


def stage(sketch):
    if sketch == 'app':
        source, name = ROOT / 'src/app/app.ino', 'app'
    elif re.fullmatch(r'bench/[a-z][a-z0-9_]*', sketch):
        name = sketch.split('/')[1]
        source = ROOT / 'bench' / name / f'{name}.ino'
    else:
        fail('sketch must be app or bench/<lowercase_name>')
    if not source.is_file() or source.is_symlink():
        fail(f'sketch source does not exist or is a symlink: {sketch}')
    for folder in [source.parent, ROOT / 'src']:
        check_source(folder)
    local_src = source.parent / 'src'
    for reserved in ['config.h', 'core', 'hal']:
        if (local_src / reserved).exists():
            fail(f'sketch-local src/{reserved} conflicts with project source')
    base = ROOT / 'build/stage'
    destination = base / name
    if (ROOT / 'build').is_symlink() or base.is_symlink():
        fail('build/stage must not use symlinks')
    base.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink() or destination.resolve().parent != base.resolve():
        fail('unsafe staging destination')
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir()
    for item in source.parent.iterdir():
        if item.name == '.gitkeep':
            continue
        if item.is_file():
            shutil.copy2(item, destination / item.name)
        elif item.name != 'src':
            shutil.copytree(item, destination / item.name)
    staged_src = destination / 'src'
    if local_src.exists():
        shutil.copytree(local_src, staged_src)
    else:
        staged_src.mkdir()
    shutil.copy2(ROOT / 'src/config.h', staged_src / 'config.h')
    for module in ['core', 'hal']:
        shutil.copytree(ROOT / 'src' / module, staged_src / module)
    return destination


def source_hash(folder):
    digest = hashlib.sha256()
    for item in sorted(p for p in folder.rglob('*') if p.is_file()):
        digest.update(item.relative_to(folder).as_posix().encode() + b'\0')
        digest.update(item.read_bytes())
    return digest.hexdigest()


def verify_core(board):
    result = remote(board, ['arduino-cli', 'core', 'list'], capture=True)
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 2 and fields[0] == 'arduino:zephyr':
            if fields[1] == CORE_VERSION:
                return
            fail(f'installed Zephyr core {fields[1]} differs from pinned {CORE_VERSION}')
    fail('arduino:zephyr core not installed or inventory unreadable')


def verify_inert_source(sketch, checksum):
    # A name or MOTORS_ALLOWED macro cannot certify newly added global code.
    manifest = ROOT / 'tools/p0_inert_sources.json'
    approved = json.loads(manifest.read_text(encoding='utf-8'))
    if approved.get(sketch) != checksum:
        fail('inert upload source differs from reviewed P0 snapshot; '
             'use --compile-only and obtain a new source review')


def build_startup(args):
    if args.match and args.startup == 'default':
        fail('--match requires Immediate startup; omit --startup or use immediate')
    return args.startup or ('immediate' if args.match else 'default')


def flash(args):
    startup = build_startup(args)
    if not args.compile_only and args.sketch == 'bench/p0_matrix' and startup == 'immediate':
        fail('Immediate matrix uploads pending verified loader/matrix ownership; '
             'use --compile-only; see FACTS F-061')
    if not args.compile_only and args.sketch in ('bench/p0_adc', 'bench/p0_gpio') and startup == 'immediate':
        fail('P0 ADC/GPIO upload is reviewed for default startup only; use --compile-only')
    # P0 has no motor-run receipt workflow; reject motor uploads before any I/O.
    if args.match and not args.compile_only:
        fail('motor-capable uploads disabled in P0; --match is not STAND OK/RING OK')
    if not args.compile_only and args.sketch not in ['bench/p0_matrix', 'bench/p0_timing',
                                                   'bench/p0_adc', 'bench/p0_gpio']:
        fail('P0 uploads allow only reviewed inert p0_matrix, p0_timing, p0_adc and p0_gpio sketches')
    board = target()
    remote_root = setting('SUMO_REMOTE_ROOT', r'/[A-Za-z0-9_/-]+')
    if '..' in remote_root.split('/') or not remote_root.strip('/'):
        fail('SUMO_REMOTE_ROOT must be a dedicated absolute directory')
    require_transport(sync=True)
    folder = stage(args.sketch)
    checksum = source_hash(folder)
    if not args.compile_only:
        verify_inert_source(args.sketch, checksum)
    fqbn = BASE_FQBN + (':wait_linux_boot=no' if startup == 'immediate' else '')
    # A content-addressed remote path avoids stale files without remote deletion.
    board_folder = f'{remote_root.rstrip("/")}/{checksum}/{folder.name}'
    verify_core(board)
    remote(board, ['mkdir', '-p', board_folder])
    sync_sources(board, folder, board_folder)
    flags = f'-DMATCH={int(args.match)} -DMOTORS_ALLOWED={int(args.match)}'
    artifact_folder = f'{board_folder}/artifacts/{"match" if args.match else "bench"}-{startup}'
    remote(board, ['arduino-cli', 'compile', '--fqbn', fqbn,
                   '--output-dir', artifact_folder,
                   '--build-property', f'compiler.cpp.extra_flags={flags}',
                   '--build-property', f'compiler.c.extra_flags={flags}', board_folder])
    print(f'COMPILE command completed: {args.sketch}; source SHA256={checksum}; '
          f'MATCH={int(args.match)} MOTORS_ALLOWED={int(args.match)} STARTUP={startup}')
    if not args.compile_only:
        remote(board, ['arduino-cli', 'upload', '--fqbn', fqbn,
                       '--input-dir', artifact_folder, board_folder])
        print('UPLOAD command completed; physical operation still requires observation')
    else:
        print('Compile-only: no upload requested')


def logs():
    board = target()
    require_transport()
    # Router Monitor server, source-verified; installed service still needs P0 check.
    # recv only: no keyboard data or MCU command is transmitted.
    program = ('import socket,sys\n'
               'with socket.create_connection(("127.0.0.1",7500),10) as s:\n'
               ' s.settimeout(None)\n'
               ' while True:\n'
               '  data=s.recv(4096)\n'
               '  if not data: raise SystemExit("Monitor connection closed")\n'
               '  sys.stdout.buffer.write(data); sys.stdout.buffer.flush()\n')
    remote(board, ['python3', '-u', '-c', program])


def inventory_check(board, name, command):
    try:
        result = remote(board, command, capture=True, timeout=30)
        code, out, err = result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as error:
        code, out, err = error.returncode, error.stdout, error.stderr
    except subprocess.TimeoutExpired:
        code, out, err = 124, '', 'Inventory command exceeded its 30-second deadline'
    except OSError as error:
        code, out, err = 127, '', str(error)
    return dict(name=name, command=command, status='OK' if code == 0 else 'FAILED',
                returncode=code, stdout=out or '', stderr=err or '')


def preflight():
    board = target()
    require_transport()
    commands = [
        ('kernel', ['uname', '-srmo']),
        ('cli', ['arduino-cli', 'version']),
        ('cores', ['arduino-cli', 'core', 'list']),
        ('board_options', ['arduino-cli', 'board', 'details', '--fqbn', BASE_FQBN]),
        ('libraries', ['arduino-cli', 'lib', 'list']),
        ('rsync', ['rsync', '--version']),
        ('python', ['python3', '--version']),
        ('listeners', ['ss', '-ltn']),
    ]
    checks = []
    for name, command in commands:
        checks.append(inventory_check(board, name, command))
        code = checks[-1]['returncode']
        if code in (124, 255) or (transport() == 'adb' and code == 1):
            # ADB shares exit1 between transport and some remote-command failures.
            break  # Avoid repeating a failed or unresponsive connection.
    complete = len(checks) == len(commands) and all(c['status'] == 'OK' for c in checks)
    report = dict(status='INVENTORY-COLLECTED' if complete else 'INCOMPLETE',
                  target=board, transport=transport(),
                  captured_at_utc=datetime.now(timezone.utc).isoformat(),
                  checks=checks, limitations=[
                      'Inventory only; outputs still require version and option review.',
                      'No compile, upload, reset, monitor connection or sensor operation.',
                      'Does not verify wiring, pin safety, MCU behavior, timing or a phase gate.',
                      'Loader config, library source and router identity still need inspection.',
                      'Transport failure or timeout stops remaining checks.',
                  ])
    print(json.dumps(report, indent=2))
    return 0 if complete else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('flash', description='P0 compile-only board workflow')
    build.add_argument('sketch')
    build.add_argument('--match', action='store_true')
    build.add_argument('--compile-only', action='store_true')
    build.add_argument('--startup', choices=('default', 'immediate'))
    commands.add_parser('logs')
    commands.add_parser('preflight', description='Read-only installed-board inventory')
    args = parser.parse_args()
    try:
        if args.command == 'flash':
            flash(args)
        elif args.command == 'logs':
            logs()
        else:
            return preflight()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return error.returncode if isinstance(error, subprocess.CalledProcessError) else 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
