"""Bind final D127 review to exact local source and retained execution receipts."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P3_countdown_analysis_raw'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks = {}
public = read(RAW / 'freeze_repair1.json')['sha256']
for path, digest in public.items():
    checks['public:' + path] = sha(ROOT / path) == digest
first = read(RAW / 'freeze.json')['sha256']
checks['public:sole_oracle_correction'] = set(first) == set(public) and [
    path for path in public if first[path] != public[path]] == [
    'tests/tooling/test_countdown_analysis.py']
for path, digest in first.items():
    checks['original:' + path] = sha(RAW / 'original' / path) == digest
private = read(OUT / 'private_freeze.json')['sha256']
for path, digest in private.items():
    checks['private:' + path] = sha(ROOT / path) == digest
original = read(OUT / 'private_freeze_before_clarification.json')['sha256']
checks['private:clarification_only'] = set(original) == set(private) and [
    path for path in private if original[path] != private[path]] == [
    'state/analysis/P3_countdown_analysis_contract.md']
protected = read(RAW / 'prior_locked.json')
checks['protected:count'] = len(protected) == 38
for path, digest in protected.items():
    checks['protected:' + path] = sha(ROOT / path) == digest
for platform in ('linux', 'windows'):
    outcome = read(OUT / ('private_' + platform + '.json'))
    checks['private:' + platform + ':tests'] = outcome['result'] == 'PASS'
    checks['private:' + platform + ':count'] = outcome['tests'] == 7
    checks['private:' + platform + ':failures'] = outcome['failures'] == 0
    checks['private:' + platform + ':errors'] = outcome['errors'] == 0
public_runs = {}
for name in ('windows', 'linux', 'linux_repair1'):
    receipt = read(RAW / (name + '.json'))
    log = (RAW / (name + '.txt')).read_text(encoding='utf-8-sig')
    if name == 'linux_repair1':
        checks['run:' + name + ':exit'] = receipt['returncode'] == 0
        checks['run:' + name + ':summary'] = '\nOK\n' in log and '\nFAILED' not in log
    else:
        checks['run:' + name + ':first_failure_preserved'] = receipt['returncode'] != 0 and '\nFAILED' in log
    matches = re.findall(r'Ran (\d+) tests in ', log)
    checks['run:' + name + ':count_present'] = len(matches) == 1
    public_runs[name] = dict(tests=int(matches[0]) if matches else None, returncode=receipt['returncode'],
        receipt_sha256=sha(RAW / (name + '.json')), log_sha256=sha(RAW / (name + '.txt')))
report = dict(result='PASS' if all(checks.values()) else 'FAIL',
    utc=datetime.now(timezone.utc).isoformat(), checks=checks, public_runs=public_runs,
    frozen_files=len(public), protected_files=len(protected),
    limits='Local synthetic test and exact source checks only; no hardware/provenance/phase-gate claim.')
(OUT / 'evidence_bindings.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(dict(result=report['result'], checks=len(checks), public_runs=public_runs,
    failures=[name for name, passed in checks.items() if not passed])))
raise SystemExit(0 if report['result'] == 'PASS' else 1)
