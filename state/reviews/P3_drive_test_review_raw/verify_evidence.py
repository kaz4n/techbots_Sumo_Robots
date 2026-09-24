"""Read-only independent binding checks for reviewed D123 source and target receipts."""
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P3_drive_test_raw'
sys.path.insert(0, str(ROOT / 'tools'))
policy = importlib.import_module('app_build_policy')
freeze = json.loads((RAW / 'freeze.json').read_text())
source = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == expected
          for p, expected in freeze['sha256'].items()}
prior = json.loads((RAW / 'prior_locked.json').read_text())
locked = {}
git_normalized = {}
for path in prior:
    original = subprocess.run(['git', 'show', '1672de8b:' + path], cwd=ROOT,
                              capture_output=True, check=True).stdout
    current = (ROOT / path).read_bytes()
    locked[path] = hashlib.sha256(current).hexdigest() == prior[path]
    git_normalized[path] = original.replace(b'\r\n', b'\n') == current.replace(b'\r\n', b'\n')
targets = {}
for name in ('app', 'drive_test'):
    folder = RAW / name
    receipt = json.loads((folder / 'receipt/verified.json').read_text())
    project = name + '.ino'
    flags = '-DMATCH=0 -DMOTORS_ALLOWED=0' + (
        ' -DSUMOX_P3_DRIVE_TEST=1' if name == 'drive_test' else '')
    props = policy.validate_result((folder / 'receipt/compile.stdout.json').read_text(),
        receipt['fqbn'], flags, receipt['build_path'], project=project)
    expected = receipt['file_sha256'][receipt['build_path'] + '/' + project + '.elf']
    actual = hashlib.sha256((folder / (project + '.elf')).read_bytes()).hexdigest()
    account = json.loads((folder / 'loader_account.json').read_text())
    targets[name] = dict(elf_hash_matches=actual == expected == account['sha256'],
        flags=props['compiler.cpp.extra_flags'], compiler_returncode=receipt['compiler_returncode'],
        project=props['build.project_name'], conditional_model_peak=account[
            'conditional_pristine_peak_consumption'], conditional_model_free=account[
                'conditional_pristine_peak_free_span'])
report = dict(source_freeze_matches=source, existing_locked_byte_matches=locked,
    existing_locked_git_content_matches=git_normalized,
    existing_locked_count=len(locked), targets=targets,
    result='PASS' if all(source.values()) and all(locked.values()) and all(git_normalized.values()) and
        all(t['elf_hash_matches'] and t['compiler_returncode'] == 0 for t in targets.values())
        else 'FAIL', limitation='Offline receipts and conditional model only; no new board operation.')
(OUT / 'evidence_bindings.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(dict(result=report['result'], frozen_files=len(source), old_locked=len(locked))))
raise SystemExit(0 if report['result'] == 'PASS' else 1)
