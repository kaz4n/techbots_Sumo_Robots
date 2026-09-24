"""Read-only final D128 review bindings; writes only reviewer evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P4_reactive_profile_raw'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


freeze = read(RAW / 'freeze.json')['sha256']
frozen = {name: digest(ROOT / name) == value for name, value in freeze.items()}
private = read(OUT / 'private_freeze.json')['files']
private_equal = {item['path']: digest(ROOT / item['path']) == item['sha256'] for item in private}
locked = read(RAW / 'prior_locked.json')
locked_equal = {}
for name, value in locked.items():
    prior = subprocess.run(['git', '-C', str(ROOT), 'show', 'c58aeae0:' + name],
                           capture_output=True, check=True).stdout
    locked_equal[name] = digest(ROOT / name) == value == hashlib.sha256(prior).hexdigest()

targets = {}
for profile in ('app', 'reactive_test'):
    folder = RAW / profile
    manifest = read(folder / 'source_manifest.json')
    checked = read(folder / 'receipt/verified.json')
    expected_folder = ROOT / ('src/app' if profile == 'app' else 'bench/reactive_test')
    files_equal = {name: digest(ROOT / name if name.startswith('src/') else expected_folder / name) == value
                   for name, value in manifest['files'].items()}
    account = read(folder / 'loader_account.json')
    artifact = folder / (profile + '.ino.elf')
    actual_elf = digest(artifact)
    receipt_elf = [value for name, value in checked['file_sha256'].items()
                   if name.endswith('/' + profile + '.ino.elf')]
    command = read(folder / 'receipt/command.json')
    expected_flags = '-DMATCH=0 -DMOTORS_ALLOWED=0' + (' -DSUMOX_P4_REACTIVE=1' if profile != 'app' else '')
    targets[profile] = dict(source_sha256=manifest['source_sha256'], files_equal=files_equal,
        source_identity_equal=manifest['source_sha256'] == checked['source_sha256'],
        elf_sha256=actual_elf, elf_equal=receipt_elf == [actual_elf] and account['sha256'] == actual_elf,
        exact_flags=all('compiler.' + language + '.extra_flags=' + expected_flags in command for language in ('c', 'cpp')),
        compile_only=command[:2] == ['arduino-cli', 'compile'] and checked['fqbn'] == 'arduino:zephyr:unoq',
        peak_model=account['conditional_pristine_peak_consumption'],
        free_model=account['conditional_pristine_peak_free_span'])

prior_account = read(ROOT / 'state/analysis/P3_stop_trial_raw/app/loader_account.json')
prior_receipt = read(ROOT / 'state/analysis/P3_stop_trial_raw/app/receipt/verified.json')
current_receipt = read(RAW / 'app/receipt/verified.json')
identity = {}
for suffix in ('app.ino.elf', 'app.ino.elf-zsk.bin'):
    before = [v for k, v in prior_receipt['file_sha256'].items() if k.endswith('/' + suffix)]
    after = [v for k, v in current_receipt['file_sha256'].items() if k.endswith('/' + suffix)]
    identity[suffix] = len(before) == len(after) == 1 and before == after
identity['loader_model'] = (targets['app']['peak_model'] == prior_account['conditional_pristine_peak_consumption'] and
                             targets['app']['free_model'] == prior_account['conditional_pristine_peak_free_span'])
passed = all(frozen.values()) and all(private_equal.values()) and all(locked_equal.values()) and all(identity.values())
passed = passed and all(all(t['files_equal'].values()) and t['source_identity_equal'] and t['elf_equal'] and
                        t['exact_flags'] and t['compile_only'] for t in targets.values())
result = dict(result='PASS' if passed else 'FAIL', utc=datetime.now(timezone.utc).isoformat(),
              frozen_source=frozen, private_oracle=private_equal, prior_locked=locked_equal,
              targets=targets, prior_default_identity=identity)
(OUT / 'final_bindings.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(result=result['result'], frozen=len(frozen), locked=len(locked_equal),
                     target_files={k: len(v['files_equal']) for k, v in targets.items()},
                     prior_default_identity=identity)))
raise SystemExit(0 if passed else 1)
