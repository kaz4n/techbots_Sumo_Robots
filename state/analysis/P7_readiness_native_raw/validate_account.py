from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re

root = Path.cwd()
out = root / 'state/analysis/P7_readiness_native_raw'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
receipt = read(out / 'app/receipt/verified.json')
account = read(out / 'app/loader_account.json')
imports = read(out / 'import_exports.json')
manifest = read(out / 'working_source_manifest.json')
source = read(out / 'app/source_manifest.json')
compile_run = read(out / 'compile.json')
assert receipt['compiler_returncode'] == compile_run['returncode'] == 0
assert sha(out / 'working_source_manifest.json') == compile_run['working_source_manifest_sha256']
assert sha(out / 'app/app.ino.elf') == account['sha256'] == receipt['file_sha256'][receipt['build_path'] + '/app.ino.elf']
assert sha(root / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py') == account['model_sha256']
assert receipt['source_sha256'] == source['source_sha256']
digest = hashlib.sha256()
for name, expected in sorted(source['files'].items()):
    original = 'src/app/app.ino' if name == 'app.ino' else name
    assert manifest['files'][original]['sha256'] == expected, name
    data = (root / original).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected, name
    digest.update(name.encode() + b'\0' + data)
assert digest.hexdigest() == source['source_sha256']
commands = [json.loads(line) for line in (out / 'actual_remote_commands.jsonl').read_text().splitlines()]
compiled = [row for row in commands if row['argv'][:2] == ['arduino-cli', 'compile'] and '--show-properties=expanded' not in row['argv']]
assert len(compiled) == 1 and compiled[0]['returncode'] == 0
assert compiled[0]['argv'][2:4] == ['--jobs', '1']
assert receipt['fqbn'] == 'arduino:zephyr:unoq:wait_linux_boot=no'
assert 'compiler.cpp.extra_flags=-DMATCH=1 -DMOTORS_ALLOWED=1' in compiled[0]['argv']
assert 'compiler.c.extra_flags=-DMATCH=1 -DMOTORS_ALLOWED=1' in compiled[0]['argv']
assert imports['hash_returncode'] == imports['returncode'] == 0
loader_path = next(p for p in receipt['file_sha256'] if p.endswith('/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'))
assert imports['expected_loader_sha256'] == receipt['file_sha256'][loader_path]
assert imports['hash_stdout'].splitlines()[1].split()[0] == imports['expected_loader_sha256']
addresses = {name: int(value, 16) for name, value in re.findall(r'IMPORT (\S+)\s+\$\d+ = (0x[0-9a-fA-F]+)', imports['stdout'])}
assert sorted(addresses) == sorted(account['relocation_used_imports']) == sorted(imports['used_imports'])
assert addresses == imports['addresses'] and all(addresses.values())
peeks = []
for section in account['sections']:
    if section['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab', '.shstrtab'):
        assert (0x08100010 + section['offset']) % section['alignment'] == 0
        peeks.append({'name': section['name'], 'offset': section['offset'], 'alignment': section['alignment']})
assert (0x08100010 + account['section_header_offset']) % 4 == 0
meta = account['metadata_chunks']
regions = {r['name']: r['retained_chunk'] for r in account['copied_regions']}
order = ['.text', '.data', '.rodata', '.bss', '.exported_sym', '.preinit_array', '.init_array', '.fini_array']
assert set(regions) <= set(order)
chunks = [('extension', meta['extension']), ('section_map', meta['section_map'])]
chunks += [(name, regions[name]) for name in order if name in regions]
chunks += [('global_symbols', meta['global_symbols']), ('export_copy', meta['export_copy'])]
used, ordered = meta['initial_bookkeeping'], []
for purpose, chunk in chunks:
    ordered.append({'purpose': purpose, 'chunk': chunk, 'available_before': 262144 - used, 'fits': chunk <= 262144 - used})
    used += chunk
assert used == account['conditional_pristine_peak_consumption']
fits = all(row['fits'] for row in ordered)
result = {'validated_utc': datetime.now(timezone.utc).isoformat(), 'verdict': 'PASS_CONDITIONAL_PRISTINE_MATCH_FIT_ONLY' if fits else 'FAIL_CONDITIONAL_PRISTINE_MATCH_FIT',
          'source_sha256': source['source_sha256'], 'source_files_bound': len(source['files']),
          'working_manifest_files': manifest['file_count'], 'ELF_sha256': account['sha256'],
          'compiler_payload': account['compiler_payload'], 'compiler_nominal_remaining': account['nominal_compiler_remaining'],
          'pool_bytes': 262144, 'ordered_peak_consumption': used, 'conditional_free_span': 262144 - used,
          'conditional_largest_payload': 262144 - used - 4, 'ordered_allocations': ordered,
          'flash_peek_base': '0x08100010', 'aligned_peek_sections': peeks, 'section_headers_aligned': True,
          'used_imports_verified': len(addresses), 'loader_sha256': imports['expected_loader_sha256'],
          'archived_compiler_commands': len(compiled), 'new_compile_commands': 1,
          'limitation': 'Source-derived pristine-pool and aligned persistent-peek model; no actual load, live RAM, stack, WCET, physical acceptance or default-profile repair'}
(out / 'app/ordered_account.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('ordered_allocations','aligned_peek_sections')}, indent=2))
assert fits, 'Ordered loader allocation does not fit the pristine pool'
