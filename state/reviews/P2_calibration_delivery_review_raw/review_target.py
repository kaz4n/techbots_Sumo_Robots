"""Offline source/ELF/ordered loader accounting for one exact D105 artifact folder."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P2_calibration_delivery_raw'
OUT = Path(__file__).resolve().parent
name = sys.argv[1]
assert name.startswith('target_') and '/' not in name and '\\' not in name
folder = RAW / name
audit = json.loads((folder/'audit.json').read_text())
source = audit['source_sha256']
frozen = RAW / ('target_sources_' + source[:8])
manifest = json.loads((frozen/'manifest.json').read_text())
assert manifest['source_files'] == audit['source_files']
aggregate = hashlib.sha256()
for path, digest in sorted(audit['source_files'].items()):
    data = (frozen/path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest, path
    aggregate.update(path.encode()); aggregate.update(b'\0'); aggregate.update(data)
assert aggregate.hexdigest() == manifest['source_sha256'] == source
spec = importlib.util.spec_from_file_location('independent_prior_elf',
    ROOT/'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
elfmod = importlib.util.module_from_spec(spec); spec.loader.exec_module(elfmod)
results = []
for row in audit['records']:
    file = folder / Path(row['path']).name
    assert hashlib.sha256(file.read_bytes()).hexdigest() == row['sha256']
    elf = elfmod.Elf(file)
    account = elf.account()
    assert len(account['init']) == 1 and not account['fini']
    assert account['init'][0]['name'] == '_GLOBAL__sub_I_setup'
    assert elf.functions()['_Z10__loopHookv'] == bytes.fromhex('7047')
    assert next(s for s in elf.sections if s['name']=='.static_thread_data_area')['size']==0
    metadata = account['metadata_chunks']
    regions = {r['name']:r['retained_chunk'] for r in account['copied_regions']}
    order = ['.text','.data','.rodata','.bss','.exported_sym','.preinit_array','.init_array','.fini_array']
    allocations = [('extension',metadata['extension']),('section_map',metadata['section_map'])]
    allocations += [(section,regions[section]) for section in order if section in regions]
    extra_regions = [section for section in regions if section not in order]
    assert not extra_regions or file.name == 'app.ino_temp.elf'
    allocations += [(section,regions[section]) for section in extra_regions]
    allocations += [('symbols',metadata['global_symbols']),('export_copy',metadata['export_copy'])]
    used = metadata['initial_bookkeeping']; ledger=[]
    for purpose, chunk in allocations:
        ledger.append(dict(purpose=purpose, chunk=chunk, available_before=262144-used,
                           fits=chunk<=262144-used))
        used += chunk
    assert used == account['conditional_pristine_peak_consumption']
    new_symbols = [{'name':s['name'],'section':s['section'],'size':s['size']}
        for s in elf.symbols if s['size'] and any(word in s['name'] for word in
            ('CalibrationOutput','calibrationOutput','formatConfig','inhibitedIdle'))]
    results.append(dict(file=file.name, sha256=row['sha256'], bytes=len(elf.raw),
        compiler_payload=account['compiler_payload'], conditional_peak=used,
        free_span=262144-used, largest_free_payload=262144-used-4,
        ordered_allocations=ledger, calibration_symbols=new_symbols,
        allocation_scope='Intermediate section sum only' if extra_regions else 'Deployment section order'))
package = folder/'app.ino.elf-zsk.bin'
package_row = next(r for r in audit['bundles'] if r['name']==package.name)
assert hashlib.sha256(package.read_bytes()).hexdigest() == package_row['sha256']
final = next(r for r in results if r['file']=='app.ino.elf')
verdict = 'BLOCKER_TARGET_LOADER_FIT' if any(not row['fits'] for row in final['ordered_allocations']) else 'PASS_CONDITIONAL_TARGET_FIT_ONLY'
result = dict(verdict=verdict, source_sha256=source, source_files=len(audit['source_files']),
    objects=len(audit['objects']), artifacts=results, zsk_sha256=package_row['sha256'],
    limitation='Exact artifact model only; not upload authorization, loaded RAM, WCET or physical evidence')
(OUT/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(verdict=verdict,source_sha256=source,source_files=result['source_files'],
    final_elf=final['sha256'],compiler_payload=final['compiler_payload'],
    conditional_peak=final['conditional_peak'],free_span=final['free_span']),indent=2))
