"""Deferred host sizeof/alignment comparison; no target-fit or private-offset claim."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE = 'cf35d0a8fcfd75c9f2b74830e07e83e1e408f524'
label, = sys.argv[1:]
assert label.replace('_', '').isalnum()
assert not any((HERE / (label + suffix)).exists() for suffix in ('.json', '.txt'))
assert os.environ.get('TMPDIR') == '/dev/shm'
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
freeze_path = ROOT / 'state/analysis/P5_mode_availability_raw/freeze.json'
freeze = json.loads(freeze_path.read_text())
sources = {name: value for name, value in freeze.items() if name.startswith('src/')}
assert sources
for name, expected in sources.items():
    assert digest(ROOT / name) == expected, name
record = dict(label=label, baseline_commit=BASELINE, commands=[], layouts={},
              start_utc=datetime.now(timezone.utc).isoformat(),
              freeze_sha256=digest(freeze_path), source_files_checked=len(sources),
              runner_sha256=digest(Path(__file__)), hardware_access=False,
              scope='Host sizeof and alignof only; no target-fit, member-offset, or WCET claim')
probe = '''#include "app/runtime.h"
#include <cstdio>
int main() {
    std::printf("Menu %zu %zu\\n", sizeof(countdown::Menu), alignof(countdown::Menu));
    std::printf("Flank %zu %zu\\n", sizeof(openers::Flank), alignof(openers::Flank));
    std::printf("Wait %zu %zu\\n", sizeof(openers::Wait), alignof(openers::Wait));
    std::printf("Robot %zu %zu\\n", sizeof(fsm::Robot), alignof(fsm::Robot));
    std::printf("Runtime %zu %zu\\n", sizeof(app::Runtime), alignof(app::Runtime));
}
'''
record['probe_sha256'] = hashlib.sha256(probe.encode()).hexdigest()
code = 1
with (HERE / (label + '.txt')).open('w') as log:
    def run(argv):
        result = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        record['commands'].append(dict(argv=argv, returncode=result.returncode))
        log.write(json.dumps(argv) + '\n' + result.stdout.decode(errors='replace') + '\n')
        log.flush()
        if result.returncode:
            raise RuntimeError('Layout command failed; see retained command and output')
        return result.stdout

    try:
        with tempfile.TemporaryDirectory(prefix='sumox_d134_layout_', dir='/dev/shm') as temp:
            scratch = Path(temp)
            baseline = scratch / 'baseline'
            current = scratch / 'current'
            baseline.mkdir()
            current.mkdir()
            archive_argv = ['git', '-c', 'safe.directory=' + str(ROOT), 'archive',
                            '--format=tar', BASELINE, 'src']
            result = subprocess.run(archive_argv, cwd=ROOT, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            record['commands'].append(dict(argv=archive_argv, returncode=result.returncode))
            log.write(json.dumps(archive_argv) + '\n' + result.stderr.decode(errors='replace'))
            assert result.returncode == 0
            record['baseline_archive_sha256'] = hashlib.sha256(result.stdout).hexdigest()
            with tarfile.open(fileobj=io.BytesIO(result.stdout), mode='r:') as archive:
                members = archive.getmembers()
                assert members
                for member in members:
                    path = PurePosixPath(member.name)
                    assert not path.is_absolute() and '..' not in path.parts
                    assert path.parts[0] == 'src' and (member.isdir() or member.isfile())
                    destination = baseline.joinpath(*path.parts)
                    if member.isdir():
                        destination.mkdir(parents=True, exist_ok=True)
                    else:
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        stream = archive.extractfile(member)
                        assert stream is not None
                        destination.write_bytes(stream.read())
            shutil.copytree(ROOT / 'src', current / 'src')
            baseline_config = digest(baseline / 'src/config.h')
            current_config = (current / 'src/config.h').read_bytes()
            record['baseline_config_sha256'] = baseline_config
            probe_path = scratch / 'layout.cc'
            probe_path.write_text(probe)
            record['compiler_version'] = run(['g++', '--version']).decode().splitlines()[0]
            for motors in (0, 1):
                for variant, arc, wait in (('baseline', None, None), ('final11', 1, 1),
                                            ('final00', 0, 0), ('final01', 0, 1),
                                            ('final10', 1, 0)):
                    source = baseline if variant == 'baseline' else current
                    if variant != 'baseline':
                        changed = current_config
                        for name, value in (('MODE_ARC_ENABLED', arc), ('MODE_WAIT_ENABLED', wait)):
                            before = (name + ' = 1U').encode()
                            after = (name + ' = ' + str(value) + 'U').encode()
                            assert changed.count(before) == 1
                            changed = changed.replace(before, after)
                        (current / 'src/config.h').write_bytes(changed)
                    binary = scratch / (variant + '_m' + str(motors))
                    argv = ['g++', '-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                            '-fno-exceptions', '-fno-rtti', '-DMOTORS_ALLOWED=' + str(motors),
                            '-I' + str(source / 'src'), str(probe_path), '-o', str(binary)]
                    run(argv)
                    text = run([str(binary)]).decode()
                    layout = {parts[0]: {'size': int(parts[1]), 'alignment': int(parts[2])}
                              for parts in (line.split() for line in text.splitlines())}
                    assert set(layout) == {'Menu', 'Flank', 'Wait', 'Robot', 'Runtime'}
                    key = variant + '_m' + str(motors)
                    record['layouts'][key] = layout
                    if variant != 'baseline':
                        assert layout == record['layouts']['baseline_m' + str(motors)], key
            record['baseline_config_unchanged'] = digest(baseline / 'src/config.h') == baseline_config
            assert record['baseline_config_unchanged']
        record['scratch_released'] = True
        assert all(digest(ROOT / name) == value for name, value in sources.items())
        record['source_inputs_unchanged'] = True
        code = 0
    except Exception as error:
        record['error'] = repr(error)
        log.write(repr(error) + '\n')
record.update(returncode=code, end_utc=datetime.now(timezone.utc).isoformat())
(HERE / (label + '.json')).write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(dict(returncode=code, layouts=record['layouts'], error=record.get('error'))))
sys.exit(code)
