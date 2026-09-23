"""Bind D085 independent review to baseline files without operating a board."""
import hashlib
import ast
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
baseline = '4ada2cd'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=root)


protected = {}
for name in git('ls-tree', '-r', '--name-only', baseline, 'tests', 'src/app',
                'tools/board_tool.py').decode().splitlines():
    old = git('show', baseline + ':' + name)
    new = (root / name).read_bytes()
    equal = old.replace(b'\r\n', b'\n') == new.replace(b'\r\n', b'\n')
    if name == 'tests/tooling/test_p0_config.py':
        continue  # Its additive declaration allowlist is audited separately below.
    protected[name] = dict(baseline_sha256=sha(old), current_sha256=sha(new),
                           equal_after_crlf_normalization=equal)
assert all(value['equal_after_crlf_normalization'] for value in protected.values())
config_test_name = 'tests/tooling/test_p0_config.py'
old_test = ast.parse(git('show', baseline+':'+config_test_name).decode())
new_test = ast.parse((root/config_test_name).read_text())
old_functions = {n.name:ast.dump(n, include_attributes=False) for n in ast.walk(old_test)
                 if isinstance(n, (ast.FunctionDef,ast.AsyncFunctionDef))}
new_functions = {n.name:ast.dump(n, include_attributes=False) for n in ast.walk(new_test)
                 if isinstance(n, (ast.FunctionDef,ast.AsyncFunctionDef))}
allowed = 'test_only_b16_and_explicit_spec_diagnostic_proposed_pin_defaults_are_declared'
assert all(new_functions.get(name) == value for name,value in old_functions.items() if name != allowed)
config_test_audit = dict(unchanged_original_function_bodies=len(old_functions)-1,
                        manual_additive_allowlist_review_required=allowed,
                        current_sha256=sha((root/config_test_name).read_bytes()))
old_config = git('show', baseline + ':src/config.h').decode()
new_config = (root / 'src/config.h').read_text()
declarations = re.findall(r'inline constexpr [^;]+;', old_config, re.S)
missing = [value for value in declarations if value not in new_config]
assert not missing, missing
production = {p.relative_to(root).as_posix(): sha(p.read_bytes())
              for p in sorted((root/'src').rglob('*')) if p.is_file()}
new_tests = {p.relative_to(root).as_posix(): sha(p.read_bytes())
             for p in sorted((root/'tests').rglob('*'))
             if p.is_file() and 'qtr' in p.as_posix().lower()}
contract = root/'state/analysis/P2_qtr_native_contract.md'
result = dict(baseline=baseline, head=git('rev-parse', 'HEAD').decode().strip(),
              contract_sha256=sha(contract.read_bytes()), protected=protected,
              old_config_declarations_unchanged=len(declarations),
              config_test_audit=config_test_audit,
              production=production, qtr_tests=new_tests,
              diff_names=git('diff', '--name-only', baseline).decode().splitlines(),
              untracked=git('ls-files', '--others', '--exclude-standard').decode().splitlines())
(out/'scope_audit.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(dict(protected_unchanged=len(protected),
                      old_config_declarations_unchanged=len(declarations),
                      production_files=len(production), qtr_test_files=len(new_tests))))
