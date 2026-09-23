"""Independent D104 exact-template mutation sweep; no transport is imported."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
source = ROOT / 'tools/app_build_policy.py'
spec = importlib.util.spec_from_file_location('reviewed_d104_policy', source)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
fixture = ROOT / 'tests/fixtures/app_build_policy/valid_result.json'
original = json.loads(fixture.read_text().replace('app.ino', 'runtime_inert.ino'))
fqbn, flags = 'arduino:zephyr:unoq', '-DMATCH=0 -DMOTORS_ALLOWED=0'
build = original['builder_result']['build_path']
keys = json.loads((ROOT / 'tools/app_build_commands.json').read_text()).keys()
result = {'policy_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(),
          'positive_controls': 0, 'rejections': [], 'unexpected_acceptances': []}
for document, project in ((original, 'runtime_inert.ino'),
                          (json.loads(fixture.read_text()), 'app.ino')):
    policy.validate_result(json.dumps(document), fqbn, flags, build, project=project)
    result['positive_controls'] += 1
for key in keys:
    for alteration in ('missing', 'suffix_space', 'nul'):
        document = copy.deepcopy(original)
        entries = document['builder_result']['build_properties']
        matches = [index for index, value in enumerate(entries) if value.startswith(key + '=')]
        assert len(matches) == 1, key
        index = matches[0]
        if alteration == 'missing':
            del entries[index]
        else:
            entries[index] += ' ' if alteration == 'suffix_space' else '\x00'
        identity = {'key': key, 'alteration': alteration}
        try:
            policy.validate_result(json.dumps(document), fqbn, flags, build,
                                   project='runtime_inert.ino')
        except ValueError as error:
            result['rejections'].append({**identity, 'error': str(error)})
        else:
            result['unexpected_acceptances'].append(identity)
(RAW / 'policy_mutations.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'controls': result['positive_controls'],
                  'rejections': len(result['rejections']),
                  'unexpected_acceptances': result['unexpected_acceptances']}))
assert not result['unexpected_acceptances']
