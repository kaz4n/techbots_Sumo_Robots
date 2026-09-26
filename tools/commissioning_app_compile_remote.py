# Checks one closed commissioning profile's static application artifacts.
# Reuses reviewed descriptor observations without adding an upload or run path.
# Tested with independent D222 artifact, identity and closing-failure cases.
import hashlib
from pathlib import Path
import re
import types


PRIMITIVE = (7821, '7dc788cbfb92688d3b1a2343f673da1bae3fa3ade1df5836ae437c013750b2d3')
POLICY = (4779, '1e46cf058ccab40a2cb8e0aa9f3e9583b1f11d35fd22baaf93ff9b55d78ba931')
PINS = {'helper': '8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8', 'policy': '1e46cf058ccab40a2cb8e0aa9f3e9583b1f11d35fd22baaf93ff9b55d78ba931', 'adapter': '3e5d49e4a70c0cf6197e26b1ba5ce2b7e07601bf5d9250ba430f90d1f9eab270', 'common': 'adc7f42a3325381c3cf15122409dfe9d92db7ca187cb242e416fef356be667f8', 'static_policy': 'ec3d8a5e8c4910bbdbbb96fb5123c8bb42b294ce9342c76db73b8d3b5eab7775', 'reference': '1dc8ac6dec8534536acfcc4da73516416ea465cfcc1a349900fd13e210144a2b', 'extension': 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0', 'base': 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368', 'primitive': '7dc788cbfb92688d3b1a2343f673da1bae3fa3ade1df5836ae437c013750b2d3'}
SIZES = {'helper': 33321, 'policy': 4779, 'adapter': 8262, 'common': 14956, 'static_policy': 4836, 'reference': 17809, 'extension': 3718, 'base': 18322, 'primitive': 7821}
PROFILES = ('b4_stand', 'p3_drive', 'p3_turn', 'p3_stop', 'p4_reactive',
            'p4_timing', 'p5_abort_timing')
PARENT = '/home/arduino/sumox26_codex_build'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def owner_name(profile, motors_allowed, attempt, source_digest):
    require(type(profile) is str and profile in PROFILES, 'Exact profile required')
    require(type(motors_allowed) is int and motors_allowed in (0, 1), 'Exact motor integer required')
    require(type(attempt) is str and re.fullmatch('[a-z][a-z0-9_]{0,23}', attempt), 'Invalid attempt')
    require(type(source_digest) is str and re.fullmatch('[0-9a-f]{64}', source_digest),
            'Invalid source digest')
    digest = hashlib.sha256((source_digest + '\0' + attempt).encode()).hexdigest()
    return 'commission-' + profile + '-m' + str(motors_allowed) + '-' + digest[:12]


def _verified(raw, identity, name):
    require(type(raw) is bytes and len(raw) == identity[0] and
            hashlib.sha256(raw).hexdigest() == identity[1], 'Changed source: ' + name)


def load_bundle(bundle, *, profile, motors_allowed, attempt, source_digest):
    owner = owner_name(profile, motors_allowed, attempt, source_digest)
    require(type(bundle) is dict and all(type(name) is str for name in bundle) and
            set(bundle) == set(PINS), 'Invalid bundle')
    bundle = dict(bundle)
    for name in PINS:
        _verified(bundle[name], (SIZES[name], PINS[name]), name)
    primitive = types.ModuleType('_sumox_commissioning_remote_primitive')
    exec(compile(bundle['primitive'], '<checked-d214-artifacts>', 'exec'), primitive.__dict__)
    require(set(bundle) == set(primitive.PINS) | {'primitive'}, 'Invalid bundle field set')
    sources = {name: raw for name, raw in bundle.items() if name != 'primitive'}
    primitive.PINS = dict(primitive.PINS, policy=POLICY[1])
    primitive.SIZES = dict(primitive.SIZES, policy=POLICY[0])
    # The inherited loader validates all eight dependencies before exec.
    primitive.load_bundle(sources)
    primitive.REMOTE = PARENT + '/' + owner
    primitive.BUILD = primitive.REMOTE + '/build'
    primitive.ARTIFACTS = primitive.REMOTE + '/artifacts'
    primitive.FLAGS = None

    def first_observation(helper, adapter, root_fd, checked, result):
        payloads = primitive.artifact_files(helper, root_fd, result['build_path'],
                                           result['artifacts_path'], result['files'])
        _, result['loader'] = primitive.installed(helper, root_fd, primitive.LOADER,
                                                 16777216, primitive.LOADER_SHA)
        tls, result['tls_source'] = primitive.installed(helper, root_fd, primitive.TLS,
                                                       65536, primitive.TLS_SHA)
        inputs = {key.split('/')[1]: raw for key, raw in payloads.items() if key.startswith('build/')}
        result['layout'] = adapter.validate_artifacts(inputs, tls, checked['base'],
            exported_flat_package=payloads['artifacts/app.ino.bin-zsk.bin'],
            profile=profile, motors_allowed=motors_allowed,
            snapshots={path: checked[name] for name, path in primitive.SNAPSHOT_PATHS.items()})

    primitive.first_observation = first_observation
    return primitive, sources


def inspect_artifacts(build_path, artifacts_path, bundle, *, profile, motors_allowed,
                      attempt, source_digest, fs_root=Path('/')):
    primitive, sources = load_bundle(bundle, profile=profile, motors_allowed=motors_allowed,
                                    attempt=attempt, source_digest=source_digest)
    result = primitive.inspect_artifacts(build_path, artifacts_path, sources, fs_root=fs_root)
    result.update(schema='commissioning-app-static-artifacts-v1', profile=profile,
                  motors_allowed=motors_allowed, attempt=attempt, source_sha256=source_digest)
    return result
