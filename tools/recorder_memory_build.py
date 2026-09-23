# Prepares isolated recorder-memory candidates and delegates compile-only builds.
# Preserves production bytes and provenance while forbidding execution options.
# Independent controlled tests verify paths, copies, manifests and root restoration.
import argparse
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SKETCH = 'bench/p2_recorder_memory'
RATE_DECLARATION = re.compile(
    rb'(?m)^[ \t]*inline\s+constexpr\s+(?:std::uint32_t|unsigned)\s+'
    rb'(?P<name>LOG_HZ)\s*=\s*(?P<rate>25|50)U\s*;[ \t]*(?=\r?$)')
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


def _code_bytes(source):
    # Equal-length masking lets the final edit preserve every non-rate byte.
    noncode = (rb'R"(?P<delimiter>[^ ()\\\t\r\n]{0,16})\(.*?\)(?P=delimiter)"'
               rb'|//[^\r\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
    return re.sub(noncode, lambda match: re.sub(rb'[^\r\n]', b' ', match[0]),
                  source, flags=re.DOTALL)


def _namespace_scope(prefix):
    scopes = []
    for match in re.finditer(rb'([^{};]*)([{};])', prefix):
        statement, delimiter = match.groups()
        if delimiter == b'{':
            scopes.append(re.search(rb'\bnamespace(?:\s+[\w:]+)?\s*$', statement) is not None)
        elif delimiter == b'}':
            if not scopes:
                return False
            scopes.pop()
    return all(scopes)


def _unconditional_scope(prefix):
    depth = 0
    for directive in re.finditer(rb'(?m)^[ \t]*#[ \t]*(if|ifdef|ifndef|endif)\b', prefix):
        depth += -1 if directive[1] == b'endif' else 1
        if depth < 0:
            return False
    return depth == 0


def _candidate_config(source, rate_hz):
    # Line splicing precedes comment/directive parsing in C++; this narrow
    # literal editor rejects it rather than pretending to be a preprocessor.
    if b'\\\n' in source or b'\\\r\n' in source:
        raise ValueError('line-spliced configuration is unsupported for rate experiments')
    code = _code_bytes(source)
    declarations = list(RATE_DECLARATION.finditer(code))
    names = list(re.finditer(rb'\bLOG_HZ\s*(?:=|\{|\[|;|\()', code))
    directive = re.search(rb'(?m)^[ \t]*#[^\r\n]*\bLOG_HZ\b', code)
    if len(declarations) != 1 or len(names) != 1 or directive:
        raise ValueError('source config requires exactly one supported literal LOG_HZ declaration')
    declaration = declarations[0]
    prefix = code[:declaration.start()]
    if (names[0].start() != declaration.start('name') or
            not _namespace_scope(prefix) or not _unconditional_scope(prefix)):
        raise ValueError('LOG_HZ must be an unambiguous top-level literal declaration')
    start, end = declaration.span('rate')
    return int(declaration['rate']), source[:start] + str(rate_hz).encode() + source[end:]


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


def _record_provenance(root, candidate, rate_hz, source_rate_hz, config_bytes, original_files):
    candidate_files = _manifest(candidate)
    expected = dict(original_files)
    expected['src/config.h'] = hashlib.sha256(config_bytes).hexdigest()
    if candidate_files != expected or _manifest(root) != original_files:
        raise ValueError(f'candidate copy mismatch or original inputs changed: {candidate}')
    provenance = dict(rate_hz=rate_hz, source_rate_hz=source_rate_hz,
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
    source_rate_hz, config_bytes = _candidate_config((root / 'src/config.h').read_bytes(), rate_hz)
    base = root / 'build/memory_sources'
    base.mkdir(parents=True, exist_ok=True)
    _safe_path(base, root)
    candidate = Path(tempfile.mkdtemp(prefix=f'log{rate_hz}_', dir=base))
    _safe_path(candidate, root)
    # Failed copies remain for diagnosis; no candidate root is ever reused.
    shutil.copytree(root / 'src', candidate / 'src')
    (candidate / 'bench').mkdir()
    shutil.copytree(root / SKETCH, candidate / SKETCH)
    if rate_hz != source_rate_hz:
        (candidate / 'src/config.h').write_bytes(config_bytes)
    _validate_inputs(candidate)
    _record_provenance(root, candidate, rate_hz, source_rate_hz, config_bytes, original_files)
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
