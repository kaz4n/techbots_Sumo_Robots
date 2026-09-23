# Prepares isolated recorder-memory candidates and delegates compile-only builds.
# Preserves production bytes and provenance while forbidding execution options.
# Independent controlled tests verify paths, copies, manifests and root restoration.
import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKETCH = 'bench/p2_recorder_memory'
CONFIG_LITERAL = b'LOG_HZ = 50U'
_spec = importlib.util.spec_from_file_location('memory_board_tool',
                                             ROOT / 'tools/board_tool.py')
board_tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(board_tool)


@contextmanager
def _board_root(root):
    original = board_tool.ROOT
    try:
        board_tool.ROOT = root
        yield
    finally:
        board_tool.ROOT = original


def _validate_rate(rate_hz):
    if type(rate_hz) is not int or rate_hz not in (25, 50):
        raise ValueError('rate_hz must be the integer 25 or 50')


def _is_link(path):
    return path.is_symlink() or getattr(path, 'is_junction', lambda: False)()


def _safe_path(path, root):
    if not path.is_relative_to(root) or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'candidate source/build path escapes ROOT: {path}')
    for ancestor in (path, *path.parents):
        if _is_link(ancestor):
            raise ValueError(f'symlinks are not permitted in candidate ancestry: {ancestor}')
        if ancestor == root:
            break


def _files(folder, root):
    _safe_path(folder, root)
    for item in sorted(folder.iterdir()):
        _safe_path(item, root)
        if item.is_dir():
            yield from _files(item, root)
        elif item.is_file():
            yield item
        else:
            raise ValueError(f'candidate input is not a regular file or directory: {item}')


def _manifest(root):
    files = [*_files(root / 'src', root), *_files(root / SKETCH, root)]
    return {item.relative_to(root).as_posix(): hashlib.sha256(item.read_bytes()).hexdigest()
            for item in files}


def _validate_inputs(root):
    if not root.is_absolute() or not root.is_dir():
        raise ValueError('ROOT must be an existing absolute project directory')
    for folder in ('src', 'src/core', 'src/hal', SKETCH, 'build', 'build/memory_sources'):
        path = root / folder
        _safe_path(path, root)
        if path.exists() and not path.is_dir():
            raise ValueError(f'candidate source/build directory is not a directory: {path}')
        if not folder.startswith('build') and not path.is_dir():
            raise ValueError(f'required candidate directory is missing: {path}')
    for name in ('src/config.h', f'{SKETCH}/p2_recorder_memory.ino',
                 f'{SKETCH}/src/memory_probe.h', f'{SKETCH}/src/memory_probe.cpp'):
        path = root / name
        _safe_path(path, root)
        if not path.is_file():
            raise ValueError(f'required candidate input is missing: {path}')
    with _board_root(root):
        board_tool.check_source(root / 'src')
        board_tool.check_source(root / SKETCH)


def _record_provenance(root, candidate, rate_hz, original_files):
    candidate_files = _manifest(candidate)
    expected = dict(original_files)
    expected['src/config.h'] = hashlib.sha256(
        (root / 'src/config.h').read_bytes().replace(
            CONFIG_LITERAL, f'LOG_HZ = {rate_hz}U'.encode(), 1)).hexdigest()
    if candidate_files != expected or _manifest(root) != original_files:
        raise ValueError(f'candidate copy mismatch or original inputs changed: {candidate}')
    provenance = dict(rate_hz=rate_hz,
                      original_config_sha256=original_files['src/config.h'],
                      candidate_config_sha256=candidate_files['src/config.h'],
                      source_files=original_files, candidate_files=candidate_files)
    with (candidate / 'provenance.json').open('x', encoding='utf-8', newline='\n') as output:
        json.dump(provenance, output, indent=2, sort_keys=True)
        output.write('\n')


def prepare_source(rate_hz):
    _validate_rate(rate_hz)
    root = Path(ROOT)
    _validate_inputs(root)
    original_files = _manifest(root)
    config_bytes = (root / 'src/config.h').read_bytes()
    if config_bytes.count(CONFIG_LITERAL) != 1:
        raise ValueError('source config must contain exactly one LOG_HZ = 50U literal')
    base = root / 'build/memory_sources'
    base.mkdir(parents=True, exist_ok=True)
    _safe_path(base, root)
    candidate = Path(tempfile.mkdtemp(prefix=f'log{rate_hz}_', dir=base))
    _safe_path(candidate, root)
    # Failed copies remain for diagnosis; no candidate root is ever reused.
    shutil.copytree(root / 'src', candidate / 'src')
    (candidate / 'bench').mkdir()
    shutil.copytree(root / SKETCH, candidate / SKETCH)
    if rate_hz == 25:
        (candidate / 'src/config.h').write_bytes(
            config_bytes.replace(CONFIG_LITERAL, b'LOG_HZ = 25U', 1))
    _validate_inputs(candidate)
    _record_provenance(root, candidate, rate_hz, original_files)
    return candidate


def compile_candidate(rate_hz):
    candidate = prepare_source(rate_hz)
    provenance = candidate / 'provenance.json'
    print(f'Candidate source root: {candidate}', flush=True)
    print(f'Candidate provenance: {provenance}', flush=True)
    print(provenance.read_text(encoding='utf-8'), flush=True)
    args = argparse.Namespace(sketch=SKETCH, match=False, compile_only=True,
                              startup='default')
    with _board_root(candidate):
        return board_tool.flash(args)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Compile inert recorder memory candidates only',
                                     allow_abbrev=False)
    parser.add_argument('--log-hz', type=int, choices=(25, 50), required=True)
    parser.add_argument('--compile-only', action='store_true', required=True)
    args = parser.parse_args(argv)
    try:
        status = compile_candidate(args.log_hz)
        return status if isinstance(status, int) else 0
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f'Recorder memory compilation failed: {error}', file=sys.stderr)
        return getattr(error, 'returncode', 1) or 1


if __name__ == '__main__':
    sys.exit(main())
