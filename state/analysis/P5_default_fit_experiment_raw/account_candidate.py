"""Account the exact candidate ELF in pinned loader order and compare retained baselines."""
from pathlib import Path
import hashlib
import importlib.util
import json

out = Path(__file__).resolve().parent
root = out.parents[2]
folder = out / 'app_attempt02'
model_path = root / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py'
spec = importlib.util.spec_from_file_location('loader_model', model_path)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
receipt = json.loads((folder / 'receipt/verified.json').read_text())
image = model.Elf(folder / 'app.ino.elf')
account = image.account()
assert receipt['file_sha256'][receipt['build_path'] + '/app.ino.elf'] == account['sha256']
account['model_sha256'] = hashlib.sha256(model_path.read_bytes()).hexdigest()
account['relocation_used_imports'] = sorted({r['name'] for r in image.relocations if not r['symbol_section']})
account['owners'] = [s for s in image.symbols if s['type'] == 1 and s['size'] >= 100]
account['peek_alignment'] = []
for section in image.sections:
    if section['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab', '.shstrtab'):
        aligned = (0x08100010 + section['offset']) % section['alignment'] == 0
        assert aligned
        account['peek_alignment'].append({'name': section['name'], 'aligned': aligned})
assert (0x08100010 + image.section_header_offset) % 4 == 0
account['section_header_peek_aligned'] = True
metadata = account['metadata_chunks']
regions = {r['name']: r['retained_chunk'] for r in account['copied_regions']}
order = ['.text', '.data', '.rodata', '.bss', '.exported_sym',
         '.preinit_array', '.init_array', '.fini_array']
assert set(regions) <= set(order)
allocations = [('extension', metadata['extension']), ('section_map', metadata['section_map'])]
allocations += [(name, regions[name]) for name in order if name in regions]
allocations += [('global_symbols', metadata['global_symbols']), ('export_copy', metadata['export_copy'])]
used = metadata['initial_bookkeeping']
account['ordered_allocations'] = []
for name, chunk in allocations:
    account['ordered_allocations'].append({'purpose': name, 'chunk': chunk,
        'free_span_before': 262144 - used, 'fits': chunk <= 262144 - used})
    used += chunk
assert used == account['conditional_pristine_peak_consumption']
account['conditional_pristine_fit'] = all(r['fits'] for r in account['ordered_allocations'])
account['comparisons'] = {}
for label, path in (
    ('D134_default', root / 'state/analysis/P5_native_compile_raw/app/app.ino.elf'),
    ('D128_default', root / 'state/analysis/P4_reactive_profile_raw/app/app.ino.elf'),
):
    old = model.Elf(path)
    old_account = old.account()
    new_sizes = {s['name']: s['size'] for s in image.symbols if s['type'] == 2 and s['size']}
    old_sizes = {s['name']: s['size'] for s in old.symbols if s['type'] == 2 and s['size']}
    section_names = {s['name'] for s in image.sections} | {s['name'] for s in old.sections}
    account['comparisons'][label] = {
        'prior_sha256': old_account['sha256'],
        'numeric_delta': {k: account[k] - old_account[k] for k in (
            'bytes', 'compiler_payload', 'global_func_object_count',
            'conditional_pristine_peak_consumption', 'conditional_pristine_peak_free_span')},
        'changed_function_sizes': [{'name': name, 'prior': old_sizes.get(name, 0),
            'candidate': new_sizes.get(name, 0), 'delta': new_sizes.get(name, 0) - old_sizes.get(name, 0)}
            for name in sorted(new_sizes.keys() | old_sizes.keys())
            if new_sizes.get(name, 0) != old_sizes.get(name, 0)],
        'region_comparison': {'candidate': account['copied_regions'], 'prior': old_account['copied_regions']},
    }
(folder / 'loader_account.json').write_text(json.dumps(account, indent=2) + '\n')
print(json.dumps({k: account[k] for k in ('sha256', 'bytes', 'compiler_payload',
    'conditional_pristine_peak_consumption', 'conditional_pristine_peak_free_span',
    'conditional_pristine_fit', 'ordered_allocations', 'comparisons')}, indent=2))
