"""Read-only D129 host review bindings; no board/toolchain calls."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P4_timing_evidence_raw'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


freeze = read(RAW / 'freeze.json')['sha256']
original_frozen = {name: digest(ROOT / name) == value for name, value in freeze.items()}
correction = read(RAW / 'oracle_correction_freeze.json')
approved_correction = dict(path='tests/tooling/test_reactive_timing.py',
    old='178ae1a10e9e8850b7967c495776538c477b42423ad4a708f47e65f85cbf9bf7',
    new='4b9e896fdc5112246f8db1a669e493819601d9d110bb625e2dfd5cbea784bc2a')
corrected_name = approved_correction['path']
correction_valid = correction['changed'] == [approved_correction]
correction_valid = correction_valid and correction['frozen_before_execution'] is True
correction_valid = correction_valid and freeze[corrected_name] == approved_correction['old']
correction_valid = correction_valid and digest(RAW / 'original_oracles' / corrected_name) == approved_correction['old']
correction_valid = correction_valid and {name for name, equal in original_frozen.items() if not equal} == {corrected_name}
accepted = dict(freeze)
accepted[corrected_name] = approved_correction['new']
frozen = {name: digest(ROOT / name) == value for name, value in accepted.items()}
private = read(OUT / 'private_freeze.json')['files']
private_equal = {item['path']: digest(ROOT / item['path']) == item['sha256'] for item in private}
locked = read(RAW / 'prior_locked.json')['sha256']
locked_equal = {}
locked_git_equal = {}
for name, value in locked.items():
    prior = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', '3985da16:' + name],
                           capture_output=True, check=True, text=True).stdout.strip()
    current = subprocess.run(['git', '-C', str(ROOT), 'hash-object', '--path=' + name, name],
                             capture_output=True, check=True, text=True).stdout.strip()
    locked_equal[name] = digest(ROOT / name) == value
    locked_git_equal[name] = current == prior
repro = read(OUT / 'repro_freeze.json')
repro_unchanged = digest(OUT / 'repro_original.cc') == repro['oracle_sha256']
fixed = read(OUT / 'fixed.json')
fixed_san = read(OUT / 'fixed_sanitize.json')
fixed_equal = {name: digest(ROOT / name) == value for name, value in fixed['source_sha256'].items()}
san_equal = {name: digest(ROOT / name) == value for name, value in fixed_san['source_sha256'].items()}
private_run = read(OUT / 'private_validation.json')
private_source_equal = {name: digest(ROOT / name) == value for name, value in private_run['hashes'].items()}
passed = all(frozen.values()) and all(private_equal.values()) and all(locked_equal.values())
passed = passed and all(locked_git_equal.values()) and repro_unchanged and all(fixed_equal.values()) and all(san_equal.values())
passed = passed and correction_valid and private_run['result'] == 'PASS' and all(private_source_equal.values())
result = dict(result='PASS' if passed else 'FAIL', utc=datetime.now(timezone.utc).isoformat(),
    original_frozen_source=original_frozen, accepted_frozen_source=frozen,
    exact_one_adjudicated_replacement=correction_valid, approved_oracle_correction=approved_correction,
    private_oracle=private_equal, private_run_source=private_source_equal, prior_locked_raw=locked_equal,
    prior_locked_git_filtered=locked_git_equal, original_oracle_unchanged=repro_unchanged,
    fixed_repro_sources=fixed_equal, sanitized_repro_sources=san_equal,
    native='Pending: no board available; no D129 native compilation/identity/fit claim.')
(OUT / 'final_bindings.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(result=result['result'], frozen=len(frozen), locked=len(locked_equal),
                     original_oracle_unchanged=repro_unchanged)))
raise SystemExit(0 if passed else 1)
