"""Read-only D099 parser probes from the saved default compile receipt."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
receipt = ROOT / 'build/app-receipts/d7e381cb91b1464fa5aca4503bc050f7'
spec = importlib.util.spec_from_file_location('policy', ROOT / 'tools/app_build_policy.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
text = (receipt / 'compile.stdout.json').read_text(encoding='utf-8')
original = json.loads(text)
verified = json.loads((receipt / 'verified.json').read_text())
flags = '-DMATCH=0 -DMOTORS_ALLOWED=0'
path = verified['build_path']
fqbn = verified['fqbn']
baseline = policy.validate_result(text, fqbn, flags, path)
probes = {}
mutations = {
    'recipe_drops_controlled_safety_flags': (
        'recipe.cpp.o.pattern',
        baseline['recipe.cpp.o.pattern'].replace(
            flags, '-DMATCH=1 -DMOTORS_ALLOWED=1')),
    'compiler_command_changes': ('compiler.cpp.cmd', 'unreviewed-compiler'),
    'additional_build_hook': ('recipe.hooks.prebuild.1.pattern', 'unreviewed-hook'),
}
for name, (key, value) in mutations.items():
    document = copy.deepcopy(original)
    entries = document['builder_result']['build_properties']
    entries[:] = [entry for entry in entries if entry.split('=', 1)[0] != key]
    entries.append(key + '=' + value)
    try:
        result = policy.validate_result(json.dumps(document), fqbn, flags, path)
        outcome = 'ACCEPTED'
    except ValueError as error:
        outcome = 'REJECTED: ' + str(error)
    probes[name] = dict(property=key, original=baseline.get(key), replacement=value,
                        result=outcome, changed=value != baseline.get(key))
report = dict(scope='LOCAL SYNTHETIC MUTATIONS ONLY; no board or network call',
              policy_sha256=hashlib.sha256((ROOT / 'tools/app_build_policy.py').read_bytes()).hexdigest(),
              baseline_validated=True, saved_default_source=verified['source_sha256'],
              probes=probes)
print(json.dumps(report, indent=2))
