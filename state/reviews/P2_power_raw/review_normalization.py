"""Independently bind formatting-only fixture changes to the completed review."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
AUTHOR = ROOT / 'state/analysis/P2_power_raw'
manifest = json.loads((AUTHOR / 'fixture_normalization.json').read_text())
review = json.loads((OWN / 'final_receipt_summary.json').read_text())
sha = lambda b: hashlib.sha256(b).hexdigest()

def canonical(data):
    return b'\n'.join(line.rstrip(b' \t') for line in data.replace(b'\r\n', b'\n').split(b'\n')).rstrip(b'\n') + b'\n'

def git_blob(path):
    return subprocess.check_output(['git', 'show', 'e6b7060:' + path], cwd=ROOT)

archive = AUTHOR / 'fixture_normalization.before.zip'
assert sha(archive.read_bytes()) == manifest['zip_sha256']
expected_loop = """for path in [out/'installed_bits.h', out/'installed_types.h', *[out/f'stm32u5xx_ll_{kind}.h' for kind in selections]]:
    path.write_bytes(('\\n'.join(line.rstrip(' \\t') for line in path.read_text().splitlines()).rstrip('\\n')+'\\n').encode('utf-8'))
"""
rows = []
with zipfile.ZipFile(archive) as z:
    assert len(z.namelist()) == 58
    expected_entries = {prefix + f['path'] for f in manifest['files'] for prefix in ('worktree/', 'git_e6b7060/')}
    assert set(z.namelist()) == expected_entries
    for entry in manifest['files']:
        path = entry['path']
        before = z.read('worktree/' + path)
        git = z.read('git_e6b7060/' + path)
        after = (ROOT / path).read_bytes()
        assert sha(before) == entry['before_worktree_sha256'] == review['reviewed_file_sha256'][path]
        assert sha(git) == entry['git_reviewed_sha256'] and git == git_blob(path)
        assert before.replace(b'\r\n', b'\n') == git
        assert sha(after) == entry['after_sha256']
        assert b'\r' not in after
        if path.endswith('/extract_bits.py'):
            old_ast, new_ast = ast.parse(git), ast.parse(after)
            assert len(new_ast.body) == len(old_ast.body) + 1
            assert all(ast.dump(a) == ast.dump(b) for a, b in zip(old_ast.body, new_ast.body))
            assert ast.dump(new_ast.body[-1]) == ast.dump(ast.parse(expected_loop).body[0])
            assert canonical(git).rstrip(b'\n') + b'\n' + expected_loop.encode() == after
            compile(after, path, 'exec')
            continuation_equal = True
        else:
            assert canonical(git) == after
            old_lines = git.splitlines()
            new_lines = after.splitlines()
            while old_lines and not old_lines[-1].strip():
                old_lines.pop()
            while new_lines and not new_lines[-1].strip():
                new_lines.pop()
            assert len(old_lines) == len(new_lines)
            assert all(a.rstrip(b' \t') == b for a, b in zip(old_lines, new_lines))
            continuation_equal = all(a.endswith(b'\\') == b.endswith(b'\\') for a, b in zip(old_lines, new_lines))
            assert continuation_equal
        if 'Copyright (c) 2021 STMicroelectronics.' in git.decode():
            first = git.index(b'/* Copyright')
            last = git.index(b' */', first) + 3
            assert git[first:last] in after
        rows.append({'path': path, 'original_review_bytes_match': True,
                     'git_blob_matches_archive': True, 'canonical_equivalent': True,
                     'macro_continuations_unchanged': continuation_equal,
                     'after_sha256': sha(after), 'changed_git_blob': git != after})

changed = [row['path'] for row in rows if row['changed_git_blob']]
assert set(changed) == {'tests/native_power/cases.cc', 'tests/native_power/ownership_cases.cc',
                       'tests/native_power/native_fixture.cc', 'tests/native_power/stm32u5xx_ll_adc.h',
                       'tests/native_power/extract_bits.py'}

# Generator execution is isolated: no test, production or source-evidence files are written.
with tempfile.TemporaryDirectory(prefix='normalization_probe_', dir=OWN) as temporary:
    sandbox = Path(temporary).resolve()
    assert sandbox.parent == OWN.resolve()
    inputs = sandbox / 'state/analysis/P2_adc_ownership_raw/headers'
    outputs = sandbox / 'tests/native_power'
    inputs.mkdir(parents=True)
    outputs.mkdir(parents=True)
    for name in ('stm32u585xx.h', 'stm32u5xx_ll_adc.h', 'stm32u5xx_ll_gpio.h', 'stm32u5xx_ll_rcc.h'):
        shutil.copyfile(ROOT / 'state/analysis/P2_adc_ownership_raw/headers' / name, inputs / name)
    extractor = outputs / 'extract_bits.py'
    shutil.copyfile(ROOT / 'tests/native_power/extract_bits.py', extractor)
    generated = subprocess.run([sys.executable, '-B', str(extractor)], cwd=sandbox,
                               text=True, capture_output=True, check=True)
    regenerated = {}
    for name in ('installed_bits.h', 'installed_types.h', 'stm32u5xx_ll_adc.h',
                 'stm32u5xx_ll_gpio.h', 'stm32u5xx_ll_rcc.h'):
        data = (outputs / name).read_bytes()
        assert data == (ROOT / 'tests/native_power' / name).read_bytes()
        regenerated[name] = sha(data)

production = {}
for path in ('src/hal/power.cpp', 'src/hal/power.h', 'src/config.h'):
    digest = sha((ROOT / path).read_bytes())
    assert digest == review['reviewed_file_sha256'][path]
    production[path] = digest

check = subprocess.run(['git', 'diff', '--check', 'e6b7060', '--',
                        'tests/native_power', 'tests/tooling/test_power_unoq.py'],
                       cwd=ROOT, text=True, capture_output=True, check=True)
result = {'verdict': 'PASS', 'scope': 'bounded formatting followup; no broad suite rerun',
          'reviewed_commit': 'e6b7060', 'archive_sha256': sha(archive.read_bytes()),
          'archive_entries': 58, 'original_review_fixture_files': len(rows),
          'changed_git_blobs': changed, 'files': rows,
          'extractor_original_ast_prefix_equal': True, 'extractor_added_loop_only_formats_outputs': True,
          'isolated_generator_exit': generated.returncode, 'isolated_generator_stdout': generated.stdout,
          'isolated_generator_stderr': generated.stderr, 'regenerated_output_sha256': regenerated,
          'production_sha256_unchanged': production, 'scoped_git_diff_check_exit': check.returncode,
          'prior_software_scope_review_applies': True, 'SC_AJ_global_runtime_blocker_preserved': True}
(OWN / 'normalization_review.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ('verdict', 'archive_entries', 'original_review_fixture_files',
                                             'changed_git_blobs', 'isolated_generator_exit',
                                             'prior_software_scope_review_applies')}, indent=2))
