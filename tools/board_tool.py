# Stages Arduino sketches and invokes explicit board-side commands.
# Fails closed on missing configuration and separates builds from execution.
# Verified by controlled transport tests, not a claim of target compilation.
import argparse
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
    return setting('SUMO_SSH_TARGET', r'[A-Za-z0-9_][A-Za-z0-9_.@-]*')


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


def remote(board, args, capture=False):
    return subprocess.run(['ssh', *SSH_OPTIONS, board, shlex.join(args)],
                          check=True, text=True, capture_output=capture)


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


def flash(args):
    # P0 has no motor-run receipt workflow; reject motor uploads before any I/O.
    if args.match and not args.compile_only:
        fail('motor-capable uploads disabled in P0; --match is not STAND OK/RING OK')
    if not args.compile_only and args.sketch not in ['bench/p0_matrix', 'bench/p0_timing']:
        fail('P0 uploads allow only the reviewed inert p0_matrix and p0_timing sketches')
    board = target()
    remote_root = setting('SUMO_REMOTE_ROOT', r'/[A-Za-z0-9_/-]+')
    if '..' in remote_root.split('/') or remote_root == '/':
        fail('SUMO_REMOTE_ROOT must be a dedicated absolute directory')
    require_tools('ssh', 'rsync')
    folder = stage(args.sketch)
    checksum = source_hash(folder)
    if not args.compile_only:
        verify_inert_source(args.sketch, checksum)
    fqbn = BASE_FQBN + (':wait_linux_boot=no' if args.match else '')
    # A content-addressed remote path avoids stale files without remote deletion.
    board_folder = f'{remote_root.rstrip("/")}/{checksum}/{folder.name}'
    verify_core(board)
    remote(board, ['mkdir', '-p', board_folder])
    subprocess.run(['rsync', '-rlt', '--safe-links', '-e',
                    shlex.join(['ssh', *SSH_OPTIONS]), str(folder) + '/',
                    f'{board}:{board_folder}/'], check=True)
    flags = f'-DMATCH={int(args.match)} -DMOTORS_ALLOWED={int(args.match)}'
    artifact_folder = f'{board_folder}/artifacts/{"match" if args.match else "bench"}'
    remote(board, ['arduino-cli', 'compile', '--fqbn', fqbn,
                   '--output-dir', artifact_folder,
                   '--build-property', f'compiler.cpp.extra_flags={flags}',
                   '--build-property', f'compiler.c.extra_flags={flags}', board_folder])
    print(f'COMPILE command completed: {args.sketch}; source SHA256={checksum}; '
          f'MATCH={int(args.match)} MOTORS_ALLOWED={int(args.match)}')
    if not args.compile_only:
        remote(board, ['arduino-cli', 'upload', '--fqbn', fqbn,
                       '--input-dir', artifact_folder, board_folder])
        print('UPLOAD command completed; physical operation still requires observation')
    else:
        print('Compile-only: no upload requested')


def logs():
    board = target()
    require_tools('ssh')
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('flash', description='P0 compile-only board workflow')
    build.add_argument('sketch')
    build.add_argument('--match', action='store_true')
    build.add_argument('--compile-only', action='store_true')
    commands.add_parser('logs')
    args = parser.parse_args()
    try:
        if args.command == 'flash':
            flash(args)
        else:
            logs()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return error.returncode if isinstance(error, subprocess.CalledProcessError) else 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
