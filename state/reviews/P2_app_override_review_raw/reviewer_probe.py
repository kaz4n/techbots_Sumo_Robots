# Independently reviews D100 reference normalization and opaque public validators.
# Uses saved actual default metadata and pinned startup source, never live transport.
# Run locally with Python; JSON output records source hashes and all probe outcomes.
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
SOURCE = ROOT / 'state/analysis/P2_app_build_raw/default_receipt/compile.stdout.json'
FLAGS = '-DMATCH=0 -DMOTORS_ALLOWED=0'
BASE = 'arduino:zephyr:unoq'
DATA = '/home/arduino/.arduino15'
snapshot = ['tools/app_build_policy.py', 'tools/app_build_commands.json',
            'tools/board_tool.py', 'state/analysis/P2_app_override_contract.md']
before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in snapshot}
doc = json.loads(SOURCE.read_text())
props = dict(x.split('=', 1) for x in doc['builder_result']['build_properties'])
build = doc['builder_result']['build_path']
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == '416a0f71c229863fc8e4325138b9eae8897bd439979bb4afac84c21a4e08ca69'

# This selector comes from the D100 contract/source audit, not production constants.
prefixes = ('compiler.', 'recipe.', 'build.link', 'build.check', 'build.zsk', 'build.postbuild')
aliases = ('build.compiler_path', 'build.crossprefix', 'build.zip.pattern')
selected = {k: v for k, v in props.items() if k.startswith(prefixes) or k in aliases}
assert len(selected) == 84
independent = {k: v.replace(build, '@BUILD_PATH@').replace(DATA, '@DATA_DIR@').replace(FLAGS, '@SAFETY_FLAGS@')
               for k, v in selected.items()}
hooks = ['recipe.hooks.objcopy.postobjcopy.' + str(i) + '.pattern' for i in (1, 2)]
platform = (ROOT / 'state/analysis/P2_bridge_dependency_raw/installed/core/platform.txt').read_text()
boards = (ROOT / 'state/analysis/P2_bridge_dependency_raw/installed/core/boards.txt').read_text()
assert 'build.zsk_args.startup-mode-immediate=-immediate' in platform
assert 'unoq.menu.wait_linux_boot.no.build.boot_mode=immediate' in boards
for k in hooks:
    assert independent[k].count('    "') == 1
    independent[k] = independent[k].replace('    "', '   @BOOT_ARGUMENT@ "')
reference = json.loads((ROOT / 'tools/app_build_commands.json').read_text())
assert reference == independent, 'Reference differs from independent normalization'

spec = importlib.util.spec_from_file_location('reviewed_policy', ROOT / 'tools/app_build_policy.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
passes = 0
rejects = 0
def set_properties(document, values):
    document['builder_result']['build_properties'] = [k + '=' + v for k, v in values.items()]

def validate(document, fqbn, flags, path, data, preflight):
    global passes
    if preflight:
        value = policy.validate_preflight(json.dumps(document), fqbn, flags, path, data)
    else:
        value = policy.validate_result(json.dumps(document), fqbn, flags, path)
    passes += 1
    return value

def reject(document, fqbn, flags, path, data, preflight):
    global rejects
    try:
        validate(document, fqbn, flags, path, data, preflight)
    except ValueError:
        rejects += 1
        return
    raise AssertionError('Accepted adverse properties')

for mode, match, immediate in [('default', False, False), ('immediate', False, True), ('match', True, True)]:
    fqbn = BASE + (':wait_linux_boot=no' if immediate else '')
    flags = '-DMATCH=1 -DMOTORS_ALLOWED=1' if match else FLAGS
    for data, path in [(DATA, build), ('/relocated data', '/relocated build/one'),
                       ('/literal;data', '/literal;build/one')]:
        values = {k: v.replace(build, path).replace(DATA, data).replace(FLAGS, flags) for k, v in props.items()}
        values.update({'build.fqbn': fqbn, 'build.boot_mode': 'immediate' if immediate else 'wait'})
        if immediate:
            for key in hooks:
                values[key] = values[key].replace('    "', '   -immediate "')
        current = copy.deepcopy(doc)
        current['builder_result']['build_path'] = path
        for kind in ('board_platform', 'build_platform'):
            current['builder_result'][kind]['install_dir'] = data + '/packages/arduino/hardware/zephyr/1.0.0'
        set_properties(current, values)
        for preflight in (False, True):
            assert validate(current, fqbn, flags, path, data, preflight) == values
            for key in selected:
                for action in ('alter', 'remove'):
                    altered = dict(values)
                    if action == 'alter':
                        altered[key] += ' unreviewed'
                    else:
                        del altered[key]
                    bad = copy.deepcopy(current)
                    set_properties(bad, altered)
                    reject(bad, fqbn, flags, path, data, preflight)
            for key in ('recipe.hooks.prebuild.99.pattern', 'recipe.c.combine.999.pattern',
                        'compiler.unreviewed.cmd', 'tools.ctags.unreviewed', 'preproc.unreviewed'):
                bad = copy.deepcopy(current)
                altered = dict(values, **{key: 'unreviewed'})
                set_properties(bad, altered)
                reject(bad, fqbn, flags, path, data, preflight)

# Properties preflight has no discovered-library proof; the actual result does.
pre = copy.deepcopy(doc)
pre['builder_result']['used_libraries'] = [{'name': 'not-yet-discovered'}]
validate(pre, BASE, FLAGS, build, DATA, True)
reject(pre, BASE, FLAGS, build, DATA, False)
for flags, fqbn in [('-DMATCH=1 -DMOTORS_ALLOWED=1', BASE),
                    ('-DMATCH=0 -DMOTORS_ALLOWED=1', BASE), (FLAGS, BASE + ':wait_linux_boot=app')]:
    reject(doc, fqbn, flags, build, DATA, False)

# Preserve established test bodies; helper/protocol additions remain separately reviewed.
integrity = {}
for name in ['tests/tooling/test_tools.py', 'tests/tooling/test_adb_transport.py',
             'tests/tooling/test_app_build_policy.py']:
    old = subprocess.check_output(['git', 'show', 'cf61b84:' + name], cwd=ROOT, text=True)
    def methods(text):
        return {node.name: ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(text))
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')}
    earlier, current = methods(old), methods((ROOT / name).read_text())
    assert earlier == current, name
    integrity[name] = len(current)

# Re-check cached primary source bytes against the auditor's pinned-tree receipt.
primary_receipt = json.loads((ROOT / 'state/analysis/P2_app_override_raw/source_audit/identity_verification.json').read_text())
for item in primary_receipt['files']:
    raw = (ROOT / item['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == item['sha256']
    assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == item['expected_git_blob']
after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in snapshot}
assert before == after, 'Review target changed during run'
result = dict(scope='Local read-only review, synthetic property mutations; no target or transport',
              pass_=True, reference_properties=84, accepted_controls=passes,
              rejected_mutations=rejects, supported_modes=3, path_pairs=3,
              established_test_methods_unchanged=integrity,
              cached_primary_files_rechecked=len(primary_receipt['files']), source_sha256=before)
print(json.dumps(result, indent=2))
