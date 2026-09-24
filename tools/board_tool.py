# Stages Arduino sketches and invokes explicit board-side commands.
# Fails closed on missing configuration and separates builds from execution.
# Verified by controlled transport tests, not a claim of target compilation.
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import uuid

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


def _push_config_code(text, name='EDGE_PUSH_THROUGH_MS'):
    # Preserve line boundaries while removing comments and literal contents.
    token = re.compile(r'//|/\*|(?:u8|[uUL])?R"|["\']')
    output, cursor = [], 0
    while match := token.search(text, cursor):
        start, kind = match.start(), match.group()
        output.append(text[cursor:start])
        if kind == '//':
            end = text.find('\n', match.end())
            end = len(text) if end < 0 else end
        elif kind == '/*':
            end = text.find('*/', match.end())
            if end < 0:
                fail(f'{name}: unterminated block comment')
            end += 2
        elif kind.endswith('R"'):
            opener = re.match(r'([^ ()\\\t\r\n]{0,16})\(', text[match.end():match.end() + 17])
            if not opener:
                fail(f'{name}: unsupported raw literal')
            closing = ')' + opener.group(1) + '"'
            end = text.find(closing, match.end() + opener.end())
            if end < 0:
                fail(f'{name}: unterminated raw literal')
            end += len(closing)
        else:
            end = match.end()
            while end < len(text) and text[end] != kind:
                if text[end] in '\r\n':
                    fail(f'{name}: unterminated quoted literal')
                end += 2 if text[end] == '\\' else 1
            if end >= len(text):
                fail(f'{name}: unterminated quoted literal')
            end += 1
        output.append(re.sub(r'[^\n]', ' ', text[start:end]))
        cursor = end
    output.append(text[cursor:])
    return ''.join(output)


def _push_config_directives(code, names=('EDGE_PUSH_THROUGH_MS',),
                            label='EDGE_PUSH_THROUGH_MS'):
    # Track nesting only; no condition or macro is evaluated.
    output, depth = [], 0
    for line in code.split('\n'):
        directive = re.match(r'^\s*#\s*([A-Za-z_][A-Za-z0-9_]*)', line)
        in_directive = directive is not None
        for name in names:
            if re.search(r'\b' + re.escape(name) + r'\b', line) and (depth or in_directive):
                fail(f'{name}: conditional or macro declaration unsupported')
        if directive:
            kind = directive.group(1)
            if kind in ('if', 'ifdef', 'ifndef'):
                depth += 1
            elif kind == 'endif':
                depth -= 1
                if depth < 0:
                    fail(f'{label}: unmatched conditional directive')
            elif kind in ('else', 'elif') and depth == 0:
                fail(f'{label}: unmatched conditional directive')
        output.append(re.sub(r'[^\n]', ' ', line) if in_directive else line)
    if depth:
        fail(f'{label}: unterminated conditional directive')
    return '\n'.join(output)


def validate_push_through_config(path):
    try:
        text = Path(path).read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        fail(f'EDGE_PUSH_THROUGH_MS: cannot read copied config: {error}')
    if re.search(r'\\[ \t\v\f]*\r?\n', text):
        fail('EDGE_PUSH_THROUGH_MS: physical line splices are unsupported')
    code = _push_config_code(text)
    if re.search(r'(?m)^[ \t\v\f\r]*%:', code):
        fail('EDGE_PUSH_THROUGH_MS: digraph directives are unsupported')
    if len(re.findall(r'\bEDGE_PUSH_THROUGH_MS\b', code)) != 1:
        fail('EDGE_PUSH_THROUGH_MS: require exactly one active declaration')
    code = _push_config_directives(code)
    declaration = re.search(
        r'\binline\s+constexpr\s+std\s*::\s*uint32_t\s+'
        r'EDGE_PUSH_THROUGH_MS\s*=\s*([0-9]+)[Uu]\s*;', code)
    if not declaration:
        fail('EDGE_PUSH_THROUGH_MS: require canonical unsigned decimal declaration')
    prefix = code[:declaration.start()]
    boundary = max(prefix.rfind(';'), prefix.rfind('{'), prefix.rfind('}')) + 1
    if prefix[boundary:].strip():
        fail('EDGE_PUSH_THROUGH_MS: unsupported declaration prefix')
    digits = declaration.group(1)
    if len(digits) > 3 or (len(digits) > 1 and digits.startswith('0')):
        fail('EDGE_PUSH_THROUGH_MS: require canonical decimal in 0..100')
    if int(digits) > 100:
        fail('EDGE_PUSH_THROUGH_MS: value must be in 0..100')


def _mode_config_value(code, name, allowed):
    if len(re.findall(r'\b' + re.escape(name) + r'\b', code)) != 1:
        fail(f'{name}: require exactly one active declaration')
    declaration = re.search(
        r'\binline\s+constexpr\s+std\s*::\s*uint32_t\s+' + re.escape(name) +
        r'\s*=\s*([0-9]+)[Uu]\s*;', code)
    if not declaration:
        fail(f'{name}: require canonical unsigned decimal declaration')
    prefix = code[:declaration.start()]
    boundary = max(prefix.rfind(';'), prefix.rfind('{'), prefix.rfind('}')) + 1
    if prefix[boundary:].strip():
        fail(f'{name}: unsupported declaration prefix')
    digits = declaration.group(1)
    if len(digits) != 1 or digits not in allowed:
        fail(f'{name}: require one decimal digit from {allowed}')
    return int(digits)


def validate_mode_availability_config(path):
    label = 'MODE_ARC_ENABLED/MODE_WAIT_ENABLED'
    try:
        text = Path(path).read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        fail(f'{label}: cannot read copied config: {error}')
    if re.search(r'\\[ \t\v\f]*\r?\n', text):
        fail(f'{label}: physical line splices are unsupported')
    code = _push_config_code(text, label)
    if re.search(r'(?m)^[ \t\v\f\r]*%:', code):
        fail(f'{label}: digraph directives are unsupported')
    names = ('MODE_ARC_ENABLED', 'MODE_WAIT_ENABLED')
    counts = tuple(len(re.findall(r'\b' + name + r'\b', code)) for name in names)
    checked = (*names, 'MODE_DEFAULT') if any(counts) else names
    code = _push_config_directives(code, checked, label)
    if not any(counts):
        return  # Historical source has no feature symbols; new core requires both.
    for name, count in zip(names, counts):
        if count != 1:
            fail(f'{name}: require exactly one active declaration')
    arc = _mode_config_value(code, names[0], '01')
    wait = _mode_config_value(code, names[1], '01')
    default = _mode_config_value(code, 'MODE_DEFAULT', '123456')
    if (default in (4, 5) and arc == 0) or (default == 6 and wait == 0):
        fail('MODE_DEFAULT: selected mode is disabled')


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
    for reserved in ['config.h', 'core', 'hal', 'app']:
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
        if sketch == 'app' and item.suffix in ('.c', '.cc', '.cpp', '.h', '.hpp'):
            continue  # Shared app support belongs under src/app, never beside the .ino.
        if item.is_file():
            shutil.copy2(item, destination / item.name)
        elif item.name != 'src' and sketch != 'app':
            shutil.copytree(item, destination / item.name)
    staged_src = destination / 'src'
    if local_src.exists():
        shutil.copytree(local_src, staged_src)
    else:
        staged_src.mkdir()
    stage_ui_probe_sources(sketch, staged_src)
    try:
        shutil.copy2(ROOT / 'src/config.h', staged_src / 'config.h')
    except OSError as error:
        fail(f'EDGE_PUSH_THROUGH_MS: cannot copy config: {error}')
    validate_push_through_config(staged_src / 'config.h')
    validate_mode_availability_config(staged_src / 'config.h')
    for module in ['core', 'hal']:
        shutil.copytree(ROOT / 'src' / module, staged_src / module)
    for item in (ROOT / 'src/app').rglob('*'):
        relative = item.relative_to(ROOT / 'src/app')
        if relative.parts[0] != 'src' and item.is_file() and item.suffix in ('.c', '.cc', '.cpp', '.h', '.hpp'):
            target_file = staged_src / 'app' / relative
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_file)
    return destination


def stage_ui_probe_sources(sketch, destination):
    if sketch != 'bench/ui_adc_probe':
        return
    shared = ROOT / 'bench/ui/src'
    check_source(shared)
    for name in ('ui_bench.h', 'ui_bench.cpp', 'ui_bench_native.h', 'ui_bench_native.cpp'):
        source = shared / name
        target_file = destination / name
        if not source.is_file() or source.is_symlink() or os.path.lexists(target_file):
            fail('bare ADC probe requires exact non-conflicting shared UI sources')
        shutil.copy2(source, target_file)


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


def verify_runtime_artifacts(board, artifacts):
    # A fresh checked build must reproduce the reviewed loadable bytes before upload.
    import runtime_capture
    import app_build_policy
    if not artifacts.endswith('/artifacts'):
        fail('Runtime probe artifact directory is not a checked build output')
    pins = {
        artifacts + '/runtime_inert.ino.elf': runtime_capture.ELF_HASH,
        artifacts + '/runtime_inert.ino.elf-zsk.bin': runtime_capture.BINARY_HASH,
    }
    if any(not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{64}', value) is None
           for value in pins.values()):
        fail('Runtime probe reviewed artifact hashes are unset')
    app_build_policy.verify_hashes(remote, board, pins)


def build_startup(args):
    if args.match and args.startup == 'default':
        fail('--match requires Immediate startup; omit --startup or use immediate')
    return args.startup or ('immediate' if args.match else 'default')


def capture_app_command(board, command, receipt, name):
    (receipt / (name + '.command.json')).write_text(json.dumps(command, indent=2) + '\n')
    try:
        result = remote(board, command, capture=True)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, command,
                                                result.stdout, result.stderr)
    except subprocess.CalledProcessError as error:
        (receipt / (name + '.stdout.json')).write_text(error.stdout or '', encoding='utf-8')
        (receipt / (name + '.stderr.txt')).write_text(error.stderr or '', encoding='utf-8')
        print(f'App {name} failed; raw output: {receipt}', file=sys.stderr)
        raise
    (receipt / (name + '.stdout.json')).write_text(result.stdout, encoding='utf-8')
    (receipt / (name + '.stderr.txt')).write_text(result.stderr, encoding='utf-8')
    return result


def app_preflight(policy, board, command, receipt, fqbn, flags, build_path, project='app.ino'):
    directories = {}
    for name in ('data', 'user'):
        result = capture_app_command(board, ['arduino-cli', 'config', 'get',
                                     'directories.' + name, '--json'], receipt, name + '_directory')
        directories[name] = policy.resolved_directory(result.stdout)
    override_reader = lambda target, args, **kwargs: capture_app_command(target, args, receipt, 'overrides')
    policy.check_overrides(override_reader, board, directories['data'], directories['user'], command[-1])
    pin_reader = lambda target, args, **kwargs: capture_app_command(target, args, receipt, 'precompile_pins')
    policy.verify_hashes(pin_reader, board, policy.installed_pins(directories['data']))
    query = [*command[:-1], '--show-properties=expanded', command[-1]]
    result = capture_app_command(board, query, receipt, 'properties')
    options = {} if project == 'app.ino' else {'project': project}
    policy.validate_preflight(result.stdout, fqbn, flags, build_path, directories['data'], **options)
    return directories


def compile_app(board, checksum, board_folder, remote_root, fqbn, flags, startup, project='app.ino'):
    spec = importlib.util.spec_from_file_location('sumo_app_policy', ROOT / 'tools/app_build_policy.py')
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    policy.selected_project(project, fqbn, flags)
    version = remote(board, ['arduino-cli', 'version'], capture=True)
    policy.validate_cli(version.stdout)
    mode = ('match' if 'MATCH=1' in flags else 'bench') + '-' + startup
    run_id = uuid.uuid4().hex
    run_root = f'{remote_root.rstrip("/")}/_app_builds/{policy.POLICY}/{checksum}/{mode}/{run_id}'
    build_path, artifacts = run_root + '/build', run_root + '/artifacts'
    command = ['arduino-cli', 'compile', '--json', '--fqbn', fqbn,
               '--build-path', build_path, '--output-dir', artifacts,
               '--build-property', f'compiler.cpp.extra_flags={flags}',
               '--build-property', f'compiler.c.extra_flags={flags}',
               '--build-property', 'build.library_discovery_phase_flag=' + policy.DISCOVERY,
               board_folder]
    receipt = ROOT / 'build/app-receipts' / run_id
    receipt.mkdir(parents=True, exist_ok=False)
    (receipt / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
    options = {} if project == 'app.ino' else {'project': project}
    directories = app_preflight(policy, board, command, receipt, fqbn, flags, build_path, **options)
    result = capture_app_command(board, command, receipt, 'compile')
    properties = policy.validate_result(result.stdout, fqbn, flags, build_path, **options)
    hashes = policy.verify_files(remote, board, properties, build_path, artifacts)
    report = dict(policy=policy.POLICY, source_sha256=checksum, fqbn=fqbn,
                  build_path=build_path, artifacts=artifacts, file_sha256=hashes,
                  compiler_returncode=result.returncode, used_libraries=[],
                  resolved_directories=directories, precompile_checks=True)
    (receipt / 'verified.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'APP BUILD CHECKED: {policy.POLICY}; receipt={receipt}')
    result_object = policy.decode(result.stdout)
    print(result_object.get('compiler_out', ''), end='')
    print(result_object.get('compiler_err', ''), end='', file=sys.stderr)
    return artifacts


def flash_profile(args):
    startup = build_startup(args)
    identified = False
    if getattr(args, 'run_ui_adc_probe', None) is not None:
        import ui_adc_run
        identified = ui_adc_run.validate_request(args, startup)
    probe = args.sketch == 'bench/runtime_inert'
    sensor_bench = args.sketch in ('bench/opp_view', 'bench/qtr_raw', 'bench/vbat', 'bench/imu_heading', 'bench/ui', 'bench/ui_adc_probe', 'bench/motor_stand', 'bench/recorder', 'bench/motor_direction', 'bench/drive_test', 'bench/turn_accuracy', 'bench/stopping_distance', 'bench/reactive_test', 'bench/reactive_timing')
    if (probe or args.sketch in ('bench/ui_adc_probe', 'bench/motor_stand', 'bench/recorder', 'bench/motor_direction', 'bench/drive_test', 'bench/turn_accuracy', 'bench/stopping_distance', 'bench/reactive_test', 'bench/reactive_timing')) and (args.match or startup != 'default'):
        fail('Native probe requires default startup and MATCH=0 MOTORS_ALLOWED=0')
    if sensor_bench and args.match:
        fail('Sensor bench requires MATCH=0 MOTORS_ALLOWED=0')
    checked_folder = ROOT / (args.sketch if probe or sensor_bench else 'src/app')
    if (args.sketch == 'app' or probe or sensor_bench) and any(os.path.lexists(checked_folder / name)
                                    for name in ('sketch.yaml', 'sketch.yml')):
        fail('App sketch profiles are unreviewed; remove sketch.yaml/sketch.yml from this build')
    if not args.compile_only and args.sketch in ('bench/p0_matrix', 'bench/ui_matrix') and startup == 'immediate':
        fail('Immediate matrix uploads pending verified loader/matrix ownership; '
             'use --compile-only; see FACTS F-061')
    if not args.compile_only and args.sketch in ('bench/p0_adc', 'bench/p0_gpio', 'bench/p0_qtr',
                                                      'bench/recorder_inert') and startup == 'immediate':
        fail('This inert diagnostic upload is reviewed for default startup only; use --compile-only')
    # P0 has no motor-run receipt workflow; reject motor uploads before any I/O.
    if args.match and not args.compile_only:
        fail('motor-capable uploads disabled in P0; --match is not STAND OK/RING OK')
    if not args.compile_only and not identified and args.sketch not in ['bench/p0_matrix', 'bench/p0_timing',
                                                   'bench/p0_adc', 'bench/p0_gpio', 'bench/p0_qtr',
                                                   'bench/ui_matrix', 'bench/recorder_inert', 'bench/runtime_inert']:
        fail('Uploads allow only the explicitly reviewed inert diagnostic sketches')
    return startup, probe, sensor_bench, identified


def build_flags(args):
    flags = f'-DMATCH={int(args.match)} -DMOTORS_ALLOWED={int(args.match)}'
    if args.sketch == 'bench/motor_direction':
        flags += ' -DSUMOX_B4_STAND=1'
    if args.sketch == 'bench/drive_test':
        flags += ' -DSUMOX_P3_DRIVE_TEST=1'
    if args.sketch == 'bench/turn_accuracy':
        flags += ' -DSUMOX_P3_TURN_TRIAL=1'
    if args.sketch == 'bench/stopping_distance':
        flags += ' -DSUMOX_P3_STOP_TRIAL=1'
    if args.sketch == 'bench/reactive_test':
        flags += ' -DSUMOX_P4_REACTIVE=1'
    if args.sketch == 'bench/reactive_timing':
        flags += ' -DSUMOX_P4_REACTIVE=1 -DSUMOX_TIMING_EVIDENCE=1'
    return flags


def flash(args):
    startup, probe, sensor_bench, identified = flash_profile(args)
    board = target()
    scope = None
    if identified:
        import ui_adc_run
        scope = ui_adc_run.load_scope(ROOT, board, transport())
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
    flags = build_flags(args)
    artifact_folder = f'{board_folder}/artifacts/{"match" if args.match else "bench"}-{startup}'
    if args.sketch == 'app':
        compile_app(board, checksum, board_folder, remote_root, fqbn, flags, startup)
    elif probe or sensor_bench:
        project = {'bench/runtime_inert': 'runtime_inert.ino',
                   'bench/opp_view': 'opp_view.ino', 'bench/qtr_raw': 'qtr_raw.ino',
                   'bench/vbat': 'vbat.ino', 'bench/imu_heading': 'imu_heading.ino',
                   'bench/ui': 'ui.ino', 'bench/ui_adc_probe': 'ui_adc_probe.ino',
                   'bench/motor_stand': 'motor_stand.ino', 'bench/recorder': 'recorder.ino',
                   'bench/motor_direction': 'motor_direction.ino',
                   'bench/drive_test': 'drive_test.ino',
                   'bench/turn_accuracy': 'turn_accuracy.ino',
                   'bench/stopping_distance': 'stopping_distance.ino',
                   'bench/reactive_test': 'reactive_test.ino',
                   'bench/reactive_timing': 'reactive_timing.ino'}[args.sketch]
        artifact_folder = compile_app(board, checksum, board_folder, remote_root, fqbn,
                                      flags, startup, project=project)
    else:
        remote(board, ['arduino-cli', 'compile', '--fqbn', fqbn,
                       '--output-dir', artifact_folder,
                       '--build-property', f'compiler.cpp.extra_flags={flags}',
                       '--build-property', f'compiler.c.extra_flags={flags}', board_folder])
    print(f'COMPILE command completed: {args.sketch}; source SHA256={checksum}; '
          f'MATCH={int(args.match)} MOTORS_ALLOWED={int(args.match)} STARTUP={startup}')
    if not args.compile_only:
        if identified:
            ui_adc_run.upload_once(sys.modules[__name__], board, artifact_folder, board_folder, scope)
        elif probe:
            verify_runtime_artifacts(board, artifact_folder)
        if not identified:
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
    build.add_argument('--run-ui-adc-probe', help='Exact reviewed single bare ADC run identifier')
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
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return error.returncode if isinstance(error, subprocess.CalledProcessError) else 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
