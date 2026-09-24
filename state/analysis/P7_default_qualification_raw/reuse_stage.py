"""Verify the existing exact stage without writing, deleting or falling back to staging."""
import hashlib

AUTHORIZED_SOURCE_SHA256 = 'fcddbd8ef5ba4c92a2080b03e9343ac78c2406b13d9514793aa147e02f0d1da2'


def verifiedStage(board_tool, sketch, source_manifest, stage_manifest):
    if stage_manifest['source_sha256'] != AUTHORIZED_SOURCE_SHA256:
        board_tool.fail('D139 stage manifest is not the authorized source identity')
    root = board_tool.ROOT
    if sketch != 'app':
        board_tool.fail('D139 stage reuse accepts only the full app')
    source = root / 'src/app/app.ino'
    if not source.is_file() or source.is_symlink():
        board_tool.fail('D139 app source is missing or a symlink')
    for folder in (source.parent, root / 'src'):
        board_tool.check_source(folder)
    local_src = source.parent / 'src'
    for reserved in ('config.h', 'core', 'hal', 'app'):
        if (local_src / reserved).exists():
            board_tool.fail('D139 sketch-local source conflicts with project source')
    base = root / 'build/stage'
    stage = base / 'app'
    if (root / 'build').is_symlink() or base.is_symlink() or stage.is_symlink():
        board_tool.fail('D139 stage ancestry must not use symlinks')
    if not stage.is_dir() or stage.resolve().parent != base.resolve():
        board_tool.fail('D139 existing stage is absent or outside its exact parent')
    board_tool.check_source(stage)
    sources = {p.relative_to(root).as_posix(): p for p in (root / 'src').rglob('*') if p.is_file()}
    expected_sources = source_manifest['files']
    if len(expected_sources) != 103 or set(sources) != set(expected_sources):
        board_tool.fail('D139 current source file set differs from the 103 frozen inputs')
    for name, path in sources.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected_sources[name]['sha256']:
            board_tool.fail('D139 current source bytes differ: ' + name)
    files = {p.relative_to(stage).as_posix(): p for p in stage.rglob('*') if p.is_file()}
    expected_stage = stage_manifest['files']
    if len(expected_stage) != 102 or set(files) != set(expected_stage):
        board_tool.fail('D139 existing stage file set differs from the 102 checked files')
    digest = hashlib.sha256()
    for name, path in sorted(files.items()):
        data = path.read_bytes()
        original = 'src/app/app.ino' if name == 'app.ino' else name
        if expected_stage[name] != expected_sources.get(original, {}).get('sha256'):
            board_tool.fail('D139 stage manifest has no matching frozen source: ' + name)
        if hashlib.sha256(data).hexdigest() != expected_stage[name]:
            board_tool.fail('D139 existing stage bytes differ: ' + name)
        digest.update(name.encode() + b'\0' + data)
    if digest.hexdigest() != AUTHORIZED_SOURCE_SHA256:
        board_tool.fail('D139 existing stage digest differs from its checked identity')
    board_tool.validate_push_through_config(stage / 'src/config.h')
    board_tool.validate_mode_availability_config(stage / 'src/config.h')
    return stage, {'source_files': len(sources), 'stage_files': len(files),
                   'source_sha256': digest.hexdigest(), 'read_only_reuse': True}
