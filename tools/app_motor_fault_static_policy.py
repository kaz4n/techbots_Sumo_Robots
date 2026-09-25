# Validates the fixed inhibited full-application diagnostic metadata and artifacts.
# Reuses pinned static checks privately without admitting another build profile.
# Tested by independent D187 contract cases with synthetic compiler and ELF data.
import builtins
import hashlib
import importlib.util
import os
from pathlib import Path
import stat
from types import ModuleType


PROJECT = 'app_motor_fault.ino'
FQBN = 'arduino:zephyr:unoq:link_mode=static'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_MOTOR_FAULT_PROBE=1'
_ROOT = Path(__file__).absolute().parents[1]
_RAW = 'state/analysis/P7_static_link_probe_raw/'
_COMMON = 'tools/app_build_policy.py'
_POLICY = _RAW + 'static_policy.py'
_REFERENCE = _RAW + 'static_reference.json'
_ARTIFACTS = _RAW + 'static_native_artifacts.py'
_PINS = {
    _COMMON: 'adc7f42a3325381c3cf15122409dfe9d92db7ca187cb242e416fef356be667f8',
    _POLICY: 'ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775',
    _REFERENCE: '1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b',
    _ARTIFACTS: 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0',
}
_OLD_FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
_ALIASES = {PROJECT + suffix: 'app.ino' + suffix for suffix in (
    '.elf', '_debug.elf', '_temp.elf', '.bin', '.bin-zsk.bin', '.elf-zsk.bin', '.map')}


def _stamp(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns,
            getattr(info, 'st_file_attributes', 0))


def _plain_path(path):
    chain = [*reversed(path.parents), path]
    stamps = []
    for item in chain:
        info = item.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 1024:
            raise ValueError('Linked static validator path: ' + str(item))
        expected = stat.S_ISREG if item == path else stat.S_ISDIR
        if not expected(info.st_mode) or (item == path and info.st_nlink != 1):
            raise ValueError('Nonordinary static validator path: ' + str(item))
        stamps.append(_stamp(info))
    return stamps


def _checked_source(relative):
    path = _ROOT / relative
    try:
        before = _plain_path(path)
        if not 0 < before[-1][4] <= 65536:
            raise ValueError('Static validator input size invalid: ' + relative)
        with path.open('rb') as source:
            opened = _stamp(os.fstat(source.fileno()))
            raw = source.read(65537)
            closed = _stamp(os.fstat(source.fileno()))
        after = _plain_path(path)
    except OSError as error:
        raise ValueError('Missing or unreadable static validator input: ' + relative) from error
    if before != after or before[-1] != opened or opened != closed:
        raise ValueError('Static validator input changed while reading: ' + relative)
    if not 0 < len(raw) <= 65536 or hashlib.sha256(raw).hexdigest() != _PINS[relative]:
        raise ValueError('Reviewed static validator bytes changed: ' + relative)
    return raw


class _SnapshotLoader:
    def __init__(self, raw, path):
        self.raw = raw
        self.path = path

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        module.__file__ = str(self.path)
        exec(compile(self.raw, str(self.path), 'exec'), module.__dict__)


def _snapshot_import(common_raw):
    # D141 imports its dependency itself; route only that import to checked bytes.
    private_importlib = ModuleType('importlib')
    private_util = ModuleType('importlib.util')

    def fixed_spec(name, path):
        if name != 'sumox_static_common_policy' or Path(path) != _ROOT / _COMMON:
            raise ValueError('Unexpected static validator dependency')
        return importlib.util.spec_from_loader(
            name, _SnapshotLoader(common_raw, path), origin=str(path))

    def private_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == 'importlib.util' and level == 0:
            return private_util if fromlist else private_importlib
        return builtins.__import__(name, globals, locals, fromlist, level)

    private_util.spec_from_file_location = fixed_spec
    private_util.module_from_spec = importlib.util.module_from_spec
    private_importlib.util = private_util
    return private_import


def _adapt_reference(raw, common):
    reference = common.decode(raw.decode('utf-8'))
    if (type(reference) is not dict or len(reference) != 84 or
            any(type(value) is not str for value in reference.values()) or
            sum(value.count('app.ino') for value in reference.values()) != 24 or
            sum(value.count(_OLD_FLAGS) for value in reference.values()) != 5):
        raise ValueError('Reviewed static reference substitution counts changed')
    return {key: value.replace('app.ino', PROJECT).replace(_OLD_FLAGS, FLAGS)
            for key, value in reference.items()}


def _metadata_policy():
    common_raw = _checked_source(_COMMON)
    policy_raw = _checked_source(_POLICY)
    reference_raw = _checked_source(_REFERENCE)
    private_builtins = dict(vars(builtins), __import__=_snapshot_import(common_raw))
    namespace = {'__name__': '_sumox_app_motor_fault_static',
                 '__file__': str(_ROOT / _POLICY), '__builtins__': private_builtins}
    exec(compile(policy_raw, str(_ROOT / _POLICY), 'exec'), namespace)
    reference = _adapt_reference(reference_raw, namespace['_common'])
    original_metadata = namespace['_expected_metadata']

    def expected_metadata(build_path, data_dir):
        expected = original_metadata(build_path, data_dir)
        expected['build.project_name'] = PROJECT
        return expected

    # Only expectations change; D141 receives the original response and paths.
    namespace['FLAGS'] = FLAGS
    namespace['_expected_metadata'] = expected_metadata
    namespace['_read_reference'] = lambda: dict(reference)
    return namespace


def validate_preflight(text, *, build_path, data_dir):
    """Check fixed static metadata; a properties query does not prove compilation."""
    policy = _metadata_policy()
    return policy['validate_preflight'](text, build_path=build_path, data_dir=data_dir)


def validate_compile_result(text, *, build_path, data_dir):
    """Check compiler metadata without inferring artifact or runtime acceptance."""
    policy = _metadata_policy()
    return policy['validate_compile_result'](text, build_path=build_path, data_dir=data_dir)


def validate_artifacts(artifacts, native_tls_source, frozen_validator_source,
                       *, exported_flat_package):
    """Check the fixed seven-file packet through unchanged D147/D142 validation."""
    raw = _checked_source(_ARTIFACTS)
    if (type(artifacts) is not dict or any(type(name) is not str for name in artifacts) or
            artifacts.keys() != _ALIASES.keys()):
        raise ValueError('Exactly seven diagnostic artifact filenames required')
    if any(type(value) is not bytes for value in artifacts.values()):
        raise ValueError('Diagnostic artifacts must be bytes')
    if (type(exported_flat_package) is not bytes or
            exported_flat_package != artifacts[PROJECT + '.bin-zsk.bin']):
        raise ValueError('Exported flat package must equal the build package bytes')
    namespace = {'__name__': '_sumox_app_motor_fault_artifacts',
                 '__file__': str(_ROOT / _ARTIFACTS)}
    exec(compile(raw, str(_ROOT / _ARTIFACTS), 'exec'), namespace)
    legacy = {_ALIASES[name]: data for name, data in artifacts.items()}
    report = namespace['validate_artifacts'](legacy, native_tls_source,
                                              frozen_validator_source)
    return {'status': 'STATIC_APP_MOTOR_FAULT_LAYOUT_PACKAGE_PASS',
            'project': PROJECT, 'fqbn': FQBN, 'flags': FLAGS,
            'artifact_aliases': dict(_ALIASES),
            'artifact_sha256': {name: hashlib.sha256(data).hexdigest()
                                for name, data in artifacts.items()},
            'validator_report': report}
