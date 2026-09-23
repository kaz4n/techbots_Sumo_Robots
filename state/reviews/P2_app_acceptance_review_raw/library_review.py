"""Verify the completed isolated fixture receipts locally; never execute a build."""
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'tools'))
import app_build_policy as policy


def load(path):
    return policy.decode(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hashes(path):
    result = {}
    for line in path.read_text().splitlines():
        digest, name = line.split('  ', 1)
        assert len(digest) == 64 and all(c in '0123456789abcdef' for c in digest)
        assert name not in result
        result[name] = digest
    return result


folders = [Path(sys.argv[1]).resolve(),Path(sys.argv[2]).resolve()]
results = []
commands = []
sources = []
manifests = {}
for phase,folder in enumerate(folders):
    source = load(folder/'source.json')
    sources.append(source)
    assert len(source) == 3
    assert all(sha(ROOT/'tests/fixtures/app_build_policy'/name) == digest for name,digest in source.items())
    policy.validate_cli((folder/'version.stdout.json').read_text())
    inventory = (folder/'core.stdout.json').read_text()
    assert [line.split()[1] for line in inventory.splitlines() if line.split() and line.split()[0]=='arduino:zephyr'] == ['1.0.0']
    data = policy.resolved_directory((folder/'data.stdout.json').read_text())
    pins = policy.installed_pins(data)
    pre = hashes(folder/'precompile_hashes.stdout.json')
    assert all(pre[path] == digest for path,digest in pins.items())
    fixture = {path:digest for path,digest in pre.items() if path not in pins}
    assert len(fixture) == 3
    assert sorted(fixture.values()) == sorted(source.values())
    assert (folder/'overrides.stdout.json').read_text() == ''
    assert (folder/'overrides.stderr.txt').read_text() == ''
    name = 'phase'+str(phase)
    command = load(folder/(name+'.argv.json'))
    commands.append(command)
    build_path = command[command.index('--build-path')+1]
    for step in ('version','core','data','user','overrides','precompile_hashes',name,
                 name+'_source_before',name+'_source_after',name+'_hashes'):
        assert load(folder/(step+'.exit.json'))['returncode'] == 0, step
    assert command[:3] == ['arduino-cli','compile','--json']
    assert not any(x in command for x in ('--upload','--show-properties=expanded','--skip-libraries-discovery'))
    assert command[command.index('--fqbn')+1] == 'arduino:zephyr:unoq'
    properties = [command[i+1] for i,x in enumerate(command) if x == '--build-property']
    discovery = '0' if phase == 0 else '{build.library_discovery_phase}'
    assert properties == ['compiler.cpp.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0',
        'compiler.c.extra_flags=-DMATCH=0 -DMOTORS_ALLOWED=0',
        'build.library_discovery_phase_flag=-DARDUINO_LIBRARY_DISCOVERY_PHASE='+discovery]
    text = (folder/(name+'.stdout.json')).read_text()
    builder, platform = policy.validated_builder(text, build_path)
    libs = [entry['name'] for entry in builder['used_libraries']]
    assert libs.count('SumoPolicyFixture') == 1
    build_props = policy.properties_from(builder)
    assert build_props['build.library_discovery_phase_flag'] == '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0'
    assert build_props['build.project_name'] == 'phase_probe.ino'
    assert build_props['compiler.cpp.extra_flags'] == '-DMATCH=0 -DMOTORS_ALLOWED=0'
    assert build_props['compiler.c.extra_flags'] == '-DMATCH=0 -DMOTORS_ALLOWED=0'
    assert load(folder/(name+'_source_before.stdout.json')) == fixture
    assert load(folder/(name+'_source_after.stdout.json')) == fixture
    post = hashes(folder/(name+'_hashes.stdout.json'))
    assert all(post[path] == digest for path,digest in pre.items())
    artifact_hashes = {path:digest for path,digest in post.items() if path not in pre}
    assert len(artifact_hashes) == 4
    assert all(digest != hashlib.sha256(b'').hexdigest() for digest in artifact_hashes.values())
    try:
        policy.validate_result(text, 'arduino:zephyr:unoq', '-DMATCH=0 -DMOTORS_ALLOWED=0', build_path)
    except ValueError as error:
        assert str(error) == 'App native dependency policy rejects every external library'
    else:
        raise AssertionError('Actual fixture result was accepted')
    results.append(dict(phase=phase, libraries=libs, actual_success=True,
        discovery_property=discovery, raw_folder=str(folder.relative_to(ROOT)),
        result_sha256=sha(folder/(name+'.stdout.json')), artifact_hashes=artifact_hashes,
        exact_sources_before_after=True, policy_rejected_actual_nonempty_library_array=True))
    if phase == 1:
        summary = load(folder/'summary.json')
        assert summary['source'] == source
        assert len(summary['branches']) == 1
        saved = summary['branches'][0]
        assert saved['phase'] == 1 and saved['file_sha256'] == post
        assert saved['libraries'] == builder['used_libraries']
        assert saved['policy_rejection'] == 'App native dependency policy rejects every external library'
    manifests[str(folder.relative_to(ROOT))] = {p.name:sha(p) for p in sorted(folder.iterdir()) if p.is_file()}
assert sources[0] == sources[1]
normalized = []
for phase, command in enumerate(commands):
    discovery = '0' if phase == 0 else '{build.library_discovery_phase}'
    normalized.append([s.replace(folders[phase].name,'RUN').replace('/phase'+str(phase)+'/', '/PHASE/').replace('DISCOVERY_PHASE='+discovery, 'DISCOVERY_PHASE=PHASE') for s in command])
assert normalized[0] == normalized[1]
report = dict(scope='Isolated direct fixture compilation evidence, not app-wrapper acceptance or arbitrary-library compatibility',
    runner_sha256=sha(ROOT/'state/analysis/P2_app_library_probe.py'),
    source=source, branches=results, pinned_files=len(pins),
    raw_manifest=manifests)
(OUT/'library_results.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(dict(branches=results,pinned_files=len(pins)),indent=2))
