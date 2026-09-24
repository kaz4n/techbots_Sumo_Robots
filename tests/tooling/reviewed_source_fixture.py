# Restores D133's immutable approved P0 source inside temporary test fixtures.
# Keeps current tooling under test without changing production upload approvals.
# Historical file maps and aggregate hashes must match before any fixture copy.
from functools import lru_cache
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tarfile


ROOT = Path(__file__).resolve().parents[2]
REVISION = '1b1d77dcc3fc9ecfe5f6cbc0e47cb2dac9e4f461'
SOURCE_ROOTS = ('src', 'bench/p0_matrix', 'bench/p0_timing')
SOURCE_MAP = ROOT / 'state/reviews/P2_service_reset_review_raw/source_maps_1790187050866977000.json'
APPROVED = {
    'bench/p0_matrix': (91, '2d6a5cc49c30e59af0d1b96ac160e85a358490837165ca97833cbad8e8794c70'),
    'bench/p0_timing': (87, '8df06a48afb4f91a663f4f89b22acf0391331a82858e6de11619784321e900b9'),
}


def _require(condition, message):
    if not condition:
        raise AssertionError('Reviewed P0 source fixture: ' + message)


def _safe_name(name, directory=False):
    _require(isinstance(name, str) and bool(re.fullmatch(r'[A-Za-z0-9_./-]+', name)),
             'unsafe source path')
    parts = name.split('/')
    _require(all(part not in ('', '.', '..', '.git') and not part.endswith('.')
                 for part in parts), 'unsafe source path: ' + name)
    within_root = any(name.startswith(root + '/') for root in SOURCE_ROOTS)
    parent_directory = directory and any(
        name == root or root.startswith(name + '/') for root in SOURCE_ROOTS)
    _require(within_root or parent_directory,
             'source path outside approved roots: ' + name)


def _git_source():
    # Requires the pinned commit in local Git history; no shallow-checkout fallback.
    try:
        result = subprocess.run(
            ['git', '-C', str(ROOT), 'archive', '--format=tar', REVISION, *SOURCE_ROOTS],
            check=False, capture_output=True, stdin=subprocess.DEVNULL)
    except OSError as error:
        raise AssertionError('Reviewed P0 source fixture: local Git unavailable') from error
    _require(result.returncode == 0,
             'cannot read pinned commit; a full-history checkout is required')
    files = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(result.stdout), mode='r:') as archive:
            for member in archive:
                name = member.name.rstrip('/') if member.isdir() else member.name
                _safe_name(name, member.isdir())
                if member.isdir():
                    continue
                _require(member.isfile(), 'non-regular source entry: ' + name)
                _require(name not in files, 'duplicate source entry: ' + name)
                source = archive.extractfile(member)
                _require(source is not None, 'missing source contents: ' + name)
                with source:
                    files[name] = source.read()
                _require(len(files[name]) == member.size, 'incomplete source: ' + name)
    except (OSError, tarfile.TarError) as error:
        raise AssertionError('Reviewed P0 source fixture: invalid Git archive') from error
    for root in SOURCE_ROOTS:
        _require(any(name.startswith(root + '/') for name in files),
                 'missing approved source root: ' + root)
    return files


def _staged_source(files, bench):
    staged = {}
    for name, data in files.items():
        target = None
        if name.startswith(bench + '/'):
            target = name[len(bench) + 1:]
            if target == '.gitkeep':
                continue
        elif name == 'src/config.h' or name.startswith(('src/core/', 'src/hal/')):
            target = name
        elif name.startswith('src/app/'):
            relative = PurePosixPath(name[len('src/app/'):])
            if relative.parts[0] != 'src' and relative.suffix in ('.c', '.cc', '.cpp', '.h', '.hpp'):
                target = name
        if target is not None:
            _require(target not in staged, 'conflicting staged path: ' + target)
            staged[target] = data
    return staged


def _verify_source(files):
    _require(SOURCE_MAP.is_file() and not SOURCE_MAP.is_symlink(),
             'saved approved source map is missing or non-regular')
    try:
        entries = json.loads(SOURCE_MAP.read_text(encoding='utf-8'))['entries']
        for bench, (count, expected_hash) in APPROVED.items():
            saved = entries[bench]
            expected = saved['file_sha256']
            _require(saved['files'] == count and saved['source_sha256'] == expected_hash,
                     'saved aggregate identity changed: ' + bench)
            staged = _staged_source(files, bench)
            _require(len(staged) == count and set(staged) == set(expected),
                     'missing or unexpected staged entries: ' + bench)
            digest = hashlib.sha256()
            for name in sorted(staged):
                data = staged[name]
                _require(hashlib.sha256(data).hexdigest() == expected[name],
                         'source hash mismatch: ' + bench + '/' + name)
                digest.update(name.encode('utf-8') + b'\0')
                digest.update(data)
            _require(digest.hexdigest() == expected_hash, 'aggregate hash mismatch: ' + bench)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as error:
        raise AssertionError('Reviewed P0 source fixture: unreadable approved source map') from error


@lru_cache(maxsize=1)
def _verified_source():
    files = _git_source()
    _verify_source(files)
    return files


def copy_p0_source(relative, destination):
    """Copy one approved source root; caller owns its TemporaryDirectory cleanup."""
    _require(relative in SOURCE_ROOTS, 'unsupported source root: ' + str(relative))
    destination = Path(destination)
    _require(not os.path.lexists(destination), 'destination already exists')
    _require(not any(parent.is_symlink() for parent in destination.parents),
             'destination ancestry must not contain symlinks')
    resolved = destination.resolve()
    repository = ROOT.resolve()
    _require(resolved != repository and repository not in resolved.parents,
             'destination must be outside the repository')
    files = _verified_source()
    prefix = relative + '/'
    try:
        destination.mkdir(parents=True)
        for name, data in files.items():
            if not name.startswith(prefix):
                continue
            target = destination.joinpath(*PurePosixPath(name[len(prefix):]).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as output:
                output.write(data)
    except OSError as error:
        raise AssertionError('Reviewed P0 source fixture: cannot copy temporary source') from error
    return destination
