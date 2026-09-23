"""Bind D117 completed review to actual frozen sources and independent receipts."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
RAW = OUT.parent
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
freeze = read(RAW / 'implementer/second_source_freeze.json')
for name, meta in freeze['files'].items():
    assert sha(ROOT / name) == meta['sha256']
changed = subprocess.run(['git', 'diff', '--name-only', '993afdd0', '--', 'src', 'bench', 'host', 'tools'],
                         cwd=ROOT, capture_output=True, check=True).stdout.decode().splitlines()
assert set(changed) == set(freeze['files'])
test_freeze = read(RAW / 'author/first_test_freeze.json')
private_copy = read(OUT / 'private_new12_source_copy.json')['sha256']
author_copy = read(RAW / 'author/run1_source_copy.json')['sha256']
for name, expected in test_freeze['sha256'].items():
    assert sha(ROOT / name) == expected
    if name.startswith('tests/'):
        assert private_copy[name] == author_copy[name] == expected
assert sha(OUT / 'run_tests_private.py') == test_freeze['sha256']['state/analysis/P2_dump_fifo_raw/author/run_tests.py']
for name, meta in freeze['files'].items():
    assert private_copy[name] == author_copy[name] == meta['sha256']
for p, count in ((OUT / 'private_new12_summary.json', 12), (RAW / 'author/run1_summary.json', 26)):
    assert read(p) == dict(tests_run=count, failures=0, errors=0, skipped=0, success=True, findings=[])
for p in (OUT / 'private_new12_command.json', RAW / 'author/run1_command.json'):
    assert read(p)['returncode'] == 0
private_commands = [read(p) for p in sorted((OUT / 'private_new12_new').glob('command_*.json'))]
assert len(private_commands) == 416 and all(r['returncode'] == 0 and not r['stderr'] for r in private_commands)
profiles = {}
for profile in ('normal', 'asan_ubsan'):
    executions = [r for r in private_commands if Path(r['argv'][0]).name == profile]
    assert len(executions) == 201
    checks = 0
    for row in executions:
        count, failures = re.search(r'checks=(\d+) failures=(\d+)', row['stdout']).groups()
        checks += int(count)
        assert failures == '0'
    assert checks == 21915290
    replay = next(r for r in executions if r['argv'][1] == 'replay')['stdout']
    capacity = next(r for r in executions if r['argv'][1] == 'capacity')['stdout']
    assert 'D116 payload=532562 wire=682967 calls=99267' in replay
    assert 'RAW_STRESS payload=1148071 wire=1496311 calls=215676 frames=5001 events=4096' in capacity
    profiles[profile] = dict(stimuli=len(executions), checks=checks, d116_replay=replay, raw_capacity=capacity)
host = read(RAW / 'coordinator/full_host_summary.json')
for row in host:
    path = ROOT / row['artifact']
    assert sha(path) == row['sha256']
    text = path.read_text()
    assert all(line in text for line in row['doctest_summaries'])
    assert text.count('Test Passed.') == 2
factory_path = RAW / 'coordinator/factory_1790206942549918673.json'
factory = read(factory_path)
assert all(r['returncode'] == 0 and not r['stderr'] for r in factory['commands'])
assert 'actual factory: 193 checks passed' in factory['commands'][-1]['stdout']
for name, expected in factory['source_sha256'].items():
    if name.startswith('src/'):
        assert private_copy[name] == expected
targets = []
for name, final_name, records_key in (
        ('target_e820c0e1_bench-default', 'app.ino.elf', 'records'),
        ('target_e820c0e1_match-immediate', 'app.ino.elf', 'records'),
        ('target_ce5a1f4e_bench-default_checked', 'recorder.ino.elf', 'artifact_records')):
    path = OUT / (name + '.json')
    result = read(path)
    assert result['verdict'].startswith('PASS')
    final = next(r for r in result[records_key] if r['file'] == final_name)
    assert all(r['fits'] for r in final['allocations'])
    assert sha(RAW / name / final_name) == final['sha256']
    targets.append(dict(review_path=str(path.relative_to(ROOT)), review_sha256=sha(path),
                        source_sha256=result['source_sha256'], elf_sha256=final['sha256'],
                        zsk_sha256=result['zsk_sha256'], payload=final['payload'],
                        peak=final.get('peak', final.get('conditional_peak')),
                        span=final.get('span', final.get('free_span')),
                        largest_payload=final.get('largest_payload', final.get('largest_free_payload'))))
assert [(r['peak'], r['span'], r['largest_payload']) for r in targets] == [(262136, 8, 4), (260504, 1640, 1636), (220744, 41400, 41396)]
result = dict(utc=datetime.now(timezone.utc).isoformat(),
    verdict='PASS_SCOPED_SOURCE_TESTS_AND_CONDITIONAL_THREE_TARGET_FIT',
    independence='Reused separate same-model source-aware reviewer, not cross-model or human gate. Independent author froze public-contract oracles before first execution; reviewer executed exact frozen new12 in a private WSL copy.',
    source_files=freeze['files'], changed_production_paths=changed,
    contract_sha256=sha(ROOT / 'state/analysis/P2_dump_fifo_contract.md'),
    test_sha256=test_freeze['sha256'], private_methods=12, private_commands=416,
    private_profiles=profiles, author_methods=26, author_test_amendments=0,
    root_factory_checks=193, root_full_host_profiles=host,
    target_profiles=targets,
    closed_finding=dict(first_source='5e30199705228299231025e1048c90566feaf625516763d1f1eae312d561b0ab',
        first_elf='0ac42e6cd098e4ce8c8932d199603b429fa6d0a35f2a7546137afa99d12f40f0',
        first_peak=262152, deficit=8, disposition='Preserved failed artifact. Only beginFifo bounded-index representation changes; native byte/time caps and behavior untouched; actual repaired default peak262136.'),
    reviewer_corrections='Retained raw app failures: existing THM_JUMP24 handled exactly and final-only supplementary command keys. Retained recorder BSS-size assumption failure corrected from Runner164176+owner4 symbols to164180 before allocator rounding. Supplemental local objdump corrects initial excerpt-only witness labels. No product/test/model/capacity change.',
    remaining_limits=['Default app has only8 free modeled bytes/largest payload4 at allocation peak; not an actual free-RAM result.',
        'Pristine256KiB pool, fixed loader, aligned persistent flash peeks and no interleaved/constructor allocations required.',
        'Eight-queue-plus-shifter rational serial timing and six-effective-store cadence are reference-model assumptions, not hardware minima.',
        'Immediate setup TEACK reliability and inherited device_init waits are unqualified; no native WCET/whole800us tick measurement.',
        'No physical framing reset, actual receiver delivery, source/ownership grants, motor permission or human phase gate.',
        'No reviewer board/MCU/upload operation; compile-only M1 artifact is not permission to run.'])
(OUT / 'final_review.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(verdict=result['verdict'], private_methods=12, author_methods=26, targets=targets), indent=2))
