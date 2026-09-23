# Derives complete synthetic command metadata from saved actual D099 evidence.
# Keeps fixture values independent from the production D100 reference/validator.
# Re-run with Python from the repository root; existing assertions remain unchanged.
import hashlib
import json
from pathlib import Path

source = Path('state/analysis/P2_app_build_raw/default_receipt/compile.stdout.json')
raw = source.read_bytes()
actual = json.loads(raw)['builder_result']
properties = dict(row.split('=', 1) for row in actual['build_properties'])
prefixes = ('recipe.', 'compiler.', 'build.link', 'build.check', 'build.zsk',
            'build.postbuild')
other_keys = ('build.compiler_path', 'build.crossprefix', 'build.zip.pattern')
selected = {key: value for key, value in properties.items()
            if key.startswith(prefixes) or key in other_keys}
assert len(selected) == 84
reference = dict(source=str(source), source_sha256=hashlib.sha256(raw).hexdigest(),
                 build_path=actual['build_path'], data_directory='/home/arduino/.arduino15',
                 properties=selected)
Path('tests/tooling/fake_app_reference.json').write_text(json.dumps(reference, indent=2) + '\n')

fixture_path = Path('tests/fixtures/app_build_policy/valid_result.json')
fixture = json.loads(fixture_path.read_text())
builder = fixture['builder_result']
fixture_properties = dict(row.split('=', 1) for row in builder['build_properties'])
fixture_properties.update({key: value.replace(actual['build_path'], builder['build_path'])
                           for key, value in selected.items()})
fixture_properties['build.path'] = builder['build_path']
fixture_properties['runtime.tools.arm-zephyr-eabi-1.0.1.path'] = properties[
    'runtime.tools.arm-zephyr-eabi-1.0.1.path']
builder['build_properties'] = [key + '=' + value for key, value in fixture_properties.items()]
fixture_path.write_text(json.dumps(fixture, indent=2) + '\n')
print(json.dumps({'source_sha256': reference['source_sha256'],
                  'effective_properties': len(selected),
                  'fixture_properties': len(fixture_properties)}, indent=2))
