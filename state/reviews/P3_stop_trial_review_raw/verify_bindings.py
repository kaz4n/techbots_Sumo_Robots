"""Read-only verification of D126 source, local ELF and retained compile receipts."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P3_stop_trial_raw'
sys.path.insert(0, str(ROOT / 'tools'))
import app_build_policy as policy


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks = {}
frozen = read(RAW / 'freeze.json')['sha256']
for path, digest in frozen.items():
    checks['freeze:' + path] = sha(ROOT / path) == digest
public_runs = {}
for name in ('normal', 'sanitize', 'configured', 'configured_sanitize',
             'duty40', 'duty50', 'duty60', 'duty70'):
    result = read(RAW / (name + '.json'))
    transcript = (RAW / (name + '.txt')).read_text(encoding='utf-8-sig')
    test_log = (RAW / (name + '_build/LastTest.log')).read_text(encoding='utf-8-sig')
    expected_targets = 10 if name == 'normal' else 2
    checks['public:' + name + ':exit'] = result['returncode'] == 0 and all(
        command['returncode'] == 0 for command in result['commands'])
    checks['public:' + name + ':summary'] = (
        f'100% tests passed, 0 tests failed out of {expected_targets}' in transcript)
    rows = re.findall(r'test cases:\s*(\d+)\s*\|\s*(\d+) passed \| (\d+) failed \| (\d+) skipped', test_log)
    checks['public:' + name + ':case_status'] = len(rows) == expected_targets and all(
        total == passed and failed == skipped == '0' for total, passed, failed, skipped in rows)
    if name != 'normal':
        expected_cases = 31 if name.startswith('configured') else 30
        checks['public:' + name + ':case_count'] = all(int(row[0]) == expected_cases for row in rows)
    public_runs[name] = dict(cases=[int(row[0]) for row in rows],
        receipt_sha256=sha(RAW / (name + '.json')), test_log_sha256=sha(RAW / (name + '_build/LastTest.log')))
checks['tooling:pass'] = read(RAW / 'tooling.json')['returncode'] == 0 and 'Ran 121 tests' in (
    RAW / 'tooling.txt').read_text()
checks['registry:pass'] = read(RAW / 'registry.json')['returncode'] == 0 and read(RAW / 'registry.json')['tests_run'] == 2
protected = read(RAW / 'prior_locked.json')
checks['protected:count'] = len(protected) == 37
for path, digest in protected.items():
    checks['protected:' + path] = sha(ROOT / path) == digest
private = read(OUT / 'private_validation.json')
for path, digest in read(OUT / 'private_freeze.json')['sha256'].items():
    checks['private_freeze:' + path] = sha(ROOT / path.replace('\\', '/')) == digest
checks['private:pass'] = private['result'] == 'PASS'
checks['private:prior_layouts_unchanged'] = private['prior_layouts_unchanged']
checks['private:source_unchanged_during_execution'] = private['source_unchanged_during_execution']
for path, digest in private['hashes'].items():
    checks['private_source:' + path] = sha(ROOT / path) == digest

loader_path = ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py'
spec = importlib.util.spec_from_file_location('retained_loader_model', loader_path)
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
targets = {}
for profile in ('app', 'stopping_distance'):
    folder = RAW / profile
    manifest = read(folder / 'source_manifest.json')
    receipt = read(folder / 'receipt/verified.json')
    source_dir = ROOT / ('src/app' if profile == 'app' else 'bench/stopping_distance')
    staged = hashlib.sha256()
    for name, digest in sorted(manifest['files'].items()):
        path = ROOT / name if name.startswith('src/') else source_dir / name
        checks[profile + ':source:' + name] = sha(path) == digest
        staged.update(name.encode() + b'\0')
        staged.update(path.read_bytes())
    checks[profile + ':staged_hash'] = staged.hexdigest() == manifest['source_sha256'] == receipt['source_sha256']
    image_path = folder / (profile + '.ino.elf')
    expected_elf = [v for k, v in receipt['file_sha256'].items()
                    if k.endswith('/build/' + profile + '.ino.elf')]
    checks[profile + ':elf_hash'] = len(expected_elf) == 1 and sha(image_path) == expected_elf[0]
    flags = '-DMATCH=0 -DMOTORS_ALLOWED=0' + (' -DSUMOX_P3_STOP_TRIAL=1' if profile == 'stopping_distance' else '')
    properties = policy.validate_result((folder / 'receipt/compile.stdout.json').read_text(),
        'arduino:zephyr:unoq', flags, receipt['build_path'], project=profile + '.ino')
    policy.validate_preflight((folder / 'receipt/properties.stdout.json').read_text(),
        'arduino:zephyr:unoq', flags, receipt['build_path'],
        receipt['resolved_directories']['data'], project=profile + '.ino')
    checks[profile + ':checked_flags'] = all(properties[k] == flags for k in
        ('compiler.c.extra_flags', 'compiler.cpp.extra_flags'))
    checks[profile + ':compile_exit'] = read(RAW / (profile + '_compile.json'))['returncode'] == 0
    command = read(folder / 'receipt/command.json')
    checks[profile + ':compile_only'] = command[:2] == ['arduino-cli', 'compile'] and 'upload' not in command
    measured = loader.Elf(image_path).account()
    declared = read(folder / 'loader_account.json')
    for key in ('conditional_pristine_peak_consumption', 'conditional_pristine_peak_free_span',
                'conditional_largest_payload'):
        checks[profile + ':' + key] = measured[key] == declared[key]
    names = {symbol['name'] for symbol in loader.Elf(image_path).symbols}
    if profile == 'stopping_distance':
        checks[profile + ':dedicated_route'] = any('routeStopTrial' in name for name in names)
        checks[profile + ':no_combat_route'] = not any(any(part in name for part in ('routeNormal', 'checkStall', 'startOpener')) for name in names)
    checks[profile + ':conditional_fit'] = measured['conditional_pristine_peak_free_span'] >= 0
    targets[profile] = dict(source_sha256=manifest['source_sha256'],
        elf_sha256=sha(image_path), source_files=len(manifest['files']),
        conditional_peak=measured['conditional_pristine_peak_consumption'],
        conditional_free=measured['conditional_pristine_peak_free_span'])
    if profile == 'app':
        prior = read(ROOT / 'state/analysis/P3_turn_integration_raw/app/receipt/verified.json')
        for suffix in ('/build/app.ino.elf', '/artifacts/app.ino.elf-zsk.bin',
                       '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'):
            current_hash = [v for k, v in receipt['file_sha256'].items() if k.endswith(suffix)]
            prior_hash = [v for k, v in prior['file_sha256'].items() if k.endswith(suffix)]
            checks['app:prior_identity:' + suffix] = len(current_hash) == 1 and current_hash == prior_hash

report = dict(result='PASS' if all(checks.values()) else 'FAIL',
    checked_utc=datetime.now(timezone.utc).isoformat(), checks=checks, targets=targets, public_runs=public_runs,
    protected_files=len(protected), frozen_files=len(frozen), loader_model_sha256=sha(loader_path),
    limits='Local ELF bytes and retained checked compile receipts; reused conditional loader model. No actual MCU load, heap, WCET or physical accuracy claim.')
(OUT / 'evidence_bindings.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(dict(result=report['result'], checks=len(checks), targets=targets,
                     failures=[key for key, ok in checks.items() if not ok])))
raise SystemExit(0 if report['result'] == 'PASS' else 1)
