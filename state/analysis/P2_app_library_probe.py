# Compile the existing phase-independent D099 fixture; never upload or run it.
# Observe explicit discovery and policy rejection without editing installed libraries.
# Preserve real compiler exits, discovered libraries, source and artifact hashes.
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board
import app_build_policy as policy


def captured(command, folder, name):
    (folder / (name + '.argv.json')).write_text(json.dumps(command, indent=2) + '\n')
    start = datetime.now(timezone.utc).isoformat()
    try:
        result = board.remote(board.target(), command, capture=True)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as error:
        code, stdout, stderr = error.returncode, error.stdout or '', error.stderr or ''
    (folder / (name + '.stdout.json')).write_text(stdout, encoding='utf-8')
    (folder / (name + '.stderr.txt')).write_text(stderr, encoding='utf-8')
    (folder / (name + '.exit.json')).write_text(json.dumps(dict(returncode=code,
        start_utc=start, end_utc=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')
    if code:
        raise SystemExit(code)
    return stdout


def hash_files(raw, name, expected, artifacts=()):
    reader = lambda target, args, **kwargs: subprocess.CompletedProcess(args, 0, captured(args, raw, name), '')
    return policy.verify_hashes(reader, board.target(), expected, artifacts)


def verify_fixture(raw, name, base, expected_files):
    program = ('import hashlib,json,pathlib,sys\n'
               'base=pathlib.Path(sys.argv[1]); result={}\n'
               'for folder in (base/"phase_probe",base/"libraries"):\n'
               ' for path in sorted(folder.rglob("*")):\n'
               '  if path.is_symlink(): raise SystemExit("Unexpected fixture symlink")\n'
               '  if path.is_file(): result[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()\n'
               'print(json.dumps(result))\n')
    actual = policy.decode(captured(['python3', '-c', program, base], raw, name))
    if actual != expected_files:
        raise SystemExit('Target fixture exact file set or bytes changed')


def probe_branch(raw, base, phase, expected_files, pins):
    build = base + '/phase' + str(phase) + '/build'
    output = base + '/phase' + str(phase) + '/artifacts'
    flags = '-DMATCH=0 -DMOTORS_ALLOWED=0'
    discovery = '0' if phase == 0 else '{build.library_discovery_phase}'
    command = ['arduino-cli', 'compile', '--json', '--fqbn', board.BASE_FQBN,
               '--build-path', build, '--output-dir', output,
               '--libraries', base + '/libraries',
               '--build-property', 'compiler.cpp.extra_flags=' + flags,
               '--build-property', 'compiler.c.extra_flags=' + flags,
               '--build-property', 'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE=' + discovery,
               base + '/phase_probe']
    verify_fixture(raw, 'phase' + str(phase) + '_source_before', base, expected_files)
    text = captured(command, raw, 'phase' + str(phase))
    verify_fixture(raw, 'phase' + str(phase) + '_source_after', base, expected_files)
    result = policy.decode(text)
    builder, _ = policy.validated_builder(text, build)
    libraries = builder.get('used_libraries')
    if not isinstance(libraries, list) or not any(isinstance(item, dict) and item.get('name') == 'SumoPolicyFixture' for item in libraries):
        raise SystemExit('Actual result did not discover the explicit fixture library')
    try:
        policy.validate_result(text, board.BASE_FQBN, flags, build)
    except ValueError as error:
        if str(error) != 'App native dependency policy rejects every external library':
            raise
        rejection = str(error)
    else:
        raise SystemExit('Policy incorrectly accepted an external library')
    artifacts = [build + '/phase_probe.ino' + suffix for suffix in ('.elf', '_debug.elf', '_temp.elf')]
    artifacts.append(output + '/phase_probe.ino.elf-zsk.bin')
    hashes = hash_files(raw, 'phase' + str(phase) + '_hashes', {**pins, **expected_files}, artifacts)
    return dict(phase=phase, discovery_property=discovery, build_path=build, libraries=libraries, file_sha256=hashes,
                policy_rejection=rejection, compiler_out=result.get('compiler_out', ''))


def main():
    if sys.argv[1:] not in ([], ['ordinary-control']):
        raise SystemExit('Only optional ordinary-control is accepted')
    run_id = uuid.uuid4().hex
    raw = ROOT / 'state/analysis/P2_app_library_raw' / run_id
    raw.mkdir(parents=True, exist_ok=False)
    base = board.setting('SUMO_REMOTE_ROOT', r'/[A-Za-z0-9_/-]+') + '/_library_probes/' + run_id
    fixture = ROOT / 'tests/fixtures/app_build_policy'
    files = {p.relative_to(fixture).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for name in ('phase_probe', 'SumoPolicyFixture')
             for p in sorted((fixture / name).rglob('*')) if p.is_file()}
    (raw / 'source.json').write_text(json.dumps(files, indent=2) + '\n')
    policy.validate_cli(captured(['arduino-cli', 'version'], raw, 'version'))
    inventory = captured(['arduino-cli', 'core', 'list'], raw, 'core')
    installed = [line.split()[1] for line in inventory.splitlines()
                 if len(line.split()) >= 2 and line.split()[0] == 'arduino:zephyr']
    if installed != [board.CORE_VERSION]:
        raise SystemExit('Core identity differs from the pinned installed version')
    data = policy.resolved_directory(captured(['arduino-cli', 'config', 'get', 'directories.data', '--json'], raw, 'data'))
    user = policy.resolved_directory(captured(['arduino-cli', 'config', 'get', 'directories.user', '--json'], raw, 'user'))
    board.sync_sources(board.target(), fixture / 'phase_probe', base + '/phase_probe')
    board.sync_sources(board.target(), fixture / 'SumoPolicyFixture', base + '/libraries/SumoPolicyFixture')
    override_reader = lambda target, args, **kwargs: subprocess.CompletedProcess(args, 0, captured(args, raw, 'overrides'), '')
    policy.check_overrides(override_reader, board.target(), data, user, base + '/phase_probe')
    expected_files = {base + '/' + (name if name.startswith('phase_probe/') else 'libraries/' + name): digest
                      for name, digest in files.items()}
    pins = policy.installed_pins(data)
    hash_files(raw, 'precompile_hashes', {**pins, **expected_files})
    phases = (1,) if sys.argv[1:] else (0, 1)
    summaries = [probe_branch(raw, base, phase, expected_files, pins) for phase in phases]
    (raw / 'summary.json').write_text(json.dumps(dict(run_id=run_id, source=files,
        branches=summaries, scope='Actual compile-only fixture; no upload, runtime or physical evidence'), indent=2) + '\n')
    print('Selected actual discovery branches compiled and external-library results rejected: ' + str(raw))


if __name__ == '__main__':
    main()
