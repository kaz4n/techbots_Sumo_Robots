"""Verify source binding and exact experiment count; write a compact evidence index."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

out = Path(__file__).resolve().parent
root = out.parents[2]
project = root / 'build/p5_default_fit_candidate2'
manifest = json.loads((out / 'candidate2_materialized_manifest.json').read_text())
candidate = json.loads((out / 'candidate2_manifest.json').read_text())
baseline = json.loads((root / 'state/analysis/P5_abort_native_raw/working_source_manifest.json').read_text())
source = json.loads((out / 'app_candidate2/source_manifest.json').read_text())
receipt = json.loads((out / 'app_candidate2/receipt/verified.json').read_text())
account = json.loads((out / 'app_candidate2/loader_account.json').read_text())
abi = json.loads((out / 'candidate2_abi_comparison.json').read_text())
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
for name, row in manifest['files'].items():
    assert digest(project / name) == row['sha256'], name
    expected = (candidate['files'][name]['candidate_sha256'] if name in candidate['files']
                else baseline['files'][name]['sha256'])
    assert row['sha256'] == expected, name
for name, row in baseline['files'].items():
    assert digest(root / name) == row['sha256'], name
for name, expected in source['files'].items():
    original = 'src/app/app.ino' if name == 'app.ino' else name
    assert expected == manifest['files'][original]['sha256'], name
    assert expected == digest(project / 'build/stage/app' / name), name
assert source['source_sha256'] == receipt['source_sha256']
assert source['source_sha256'] != json.loads((out / 'app/source_manifest.json').read_text())['source_sha256']
commands = [json.loads(line) for line in (out / 'candidate2_actual_remote_commands.jsonl').read_text().splitlines()]
actual = [row for row in commands if row['argv'][:2] == ['arduino-cli', 'compile']
          and '--show-properties=expanded' not in row['argv']]
assert len(actual) == 1 and actual[0]['returncode'] == 0
assert actual[0]['argv'][2:4] == ['--jobs', '1']
assert abi['existing_sizes_alignments_identical']
assert abi['existing_member_offsets_identical']
runtime = next(s for s in account['owners'] if s['name'] == '_ZN12_GLOBAL__N_17runtimeE')
assert runtime['size'] == abi['candidate2']['types']['app::Runtime']['sizeof']
old_imports = json.loads((root / 'state/analysis/P5_abort_native_raw/import_exports.json').read_text())
loader_path = next(p for p in receipt['file_sha256'] if p.endswith('/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'))
assert receipt['file_sha256'][loader_path] == old_imports['expected_loader_sha256']
missing = sorted(set(account['relocation_used_imports']) - old_imports['addresses'].keys())
assert not missing
assert all(old_imports['addresses'][name] for name in account['relocation_used_imports'])
result = {'utc': datetime.now(timezone.utc).isoformat(),
    'source_sha256': receipt['source_sha256'], 'exact_candidate_files': len(candidate['files']),
    'materialized_input_files': len(manifest['files']), 'staged_files_bound': len(source['files']),
    'unchanged_production_baseline_files': len(baseline['files']),
    'candidate2_source_distinct_and_bound': True, 'actual_native_compiler_count': len(actual),
    'native_compile_returncode': actual[0]['returncode'], 'existing_ABI_and_offsets_preserved': True,
    'ELF_Runtime_equals_DWARF': True, 'conditional_pristine_fit': account['conditional_pristine_fit'],
    'conditional_pristine_peak_consumption': account['conditional_pristine_peak_consumption'],
    'conditional_pristine_peak_free_span': account['conditional_pristine_peak_free_span'],
    'used_imports_bound_to_same_packaged_loader': len(account['relocation_used_imports']),
    'import_address_evidence': 'state/analysis/P5_abort_native_raw/import_exports.json',
    'import_evidence_sha256': digest(root / 'state/analysis/P5_abort_native_raw/import_exports.json'),
    'no_host_compiler_no_upload_no_MCU_no_cleanup': True,
}
(out / 'candidate2_final_verification.json').write_text(json.dumps(result, indent=2) + '\n')
files = {p.relative_to(out).as_posix(): {'sha256': digest(p), 'bytes': p.stat().st_size}
         for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'evidence_index.json'}
(out / 'evidence_index.json').write_text(json.dumps({'files': files, 'file_count': len(files),
    'total_bytes': sum(row['bytes'] for row in files.values())}, indent=2) + '\n')
print(json.dumps(result, indent=2))
print('Retained files', len(files), 'logical bytes', sum(row['bytes'] for row in files.values()))
