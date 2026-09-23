"""D108 offline target proof: exactly two coordinate bytes vs audited D106."""
import hashlib
import importlib.util
import json
from pathlib import Path, PureWindowsPath
import struct
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_display_channel_raw'
sys.path.insert(0, str(ROOT / 'tools'))
import app_build_policy as policy
spec = importlib.util.spec_from_file_location('reviewed_elf', ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
def sha(data): return hashlib.sha256(data).hexdigest()
def read(path): return json.loads(path.read_text())
mode = sys.argv[1]
assert mode in ('bench-default', 'match-immediate')
folder = RAW / ('target_618d3a96_' + mode)
prior_folder = ROOT / ('state/analysis/P2_pin_table_raw/target_d72bff70_' + mode)
audit = read(folder / 'audit.json'); prior_audit = read(prior_folder / 'audit.json')
verified = read(folder / 'build_receipt/verified.json')
command = read(folder / 'build_receipt/command.json')
match = mode == 'match-immediate'
fqbn = policy.BASE_FQBN + (':wait_linux_boot=no' if match else '')
flags = f'-DMATCH={int(match)} -DMOTORS_ALLOWED={int(match)}'
assert command[command.index('--fqbn')+1] == verified['fqbn'] == fqbn
assert verified['compiler_returncode'] == 0 and verified['precompile_checks'] is True
assert verified['used_libraries'] == [] and verified['policy'] == policy.POLICY
assert verified['source_sha256'] == audit['source_sha256']
receipt = folder / 'build_receipt'
policy.validate_result((receipt / 'compile.stdout.json').read_text(), fqbn, flags, verified['build_path'])
policy.validate_preflight((receipt / 'properties.stdout.json').read_text(), fqbn, flags, verified['build_path'], verified['resolved_directories']['data'])
pins = policy.installed_pins(verified['resolved_directories']['data'])
assert all(verified['file_sha256'][p] == h for p, h in pins.items())
assert (receipt / 'precompile_pins.stdout.json').read_text().splitlines() == [h + '  ' + p for p, h in pins.items()]
assert all(not p.read_bytes() for p in receipt.glob('*.stderr.txt'))
assert audit['base_sha256'] == prior_audit['base_sha256'] == '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
frozen = RAW / ('target_sources_' + audit['source_sha256'][:8])
assert read(frozen / 'manifest.json')['source_files'] == audit['source_files']
assert len(audit['source_files']) == 91 and len(audit['objects']) == 79
digest = hashlib.sha256()
for name, expected in sorted(audit['source_files'].items(), key=lambda item: PureWindowsPath(item[0])):
    data = (frozen / name).read_bytes(); assert sha(data) == expected
    digest.update(name.encode()); digest.update(b'\0'); digest.update(data)
assert digest.hexdigest() == audit['source_sha256']
source_delta = {p: dict(before=prior_audit['source_files'].get(p), after=h)
                for p, h in audit['source_files'].items() if prior_audit['source_files'].get(p) != h}
assert set(source_delta) == {'src/hal/ui_display.cpp'}
assert source_delta['src/hal/ui_display.cpp']['after'] == '9e9d5d9a44d8b0d637f2301d042f7021df890a270995e1806d4d4456dd58c535'
old_table = struct.pack('<14I', 4,1,2,1,6,1,0,3,8,3,2,5,6,5)
new_table = struct.pack('<14I', 2,1,4,1,6,1,0,3,8,3,2,5,6,5)
records = []
for row in audit['records']:
    name = Path(row['path']).name
    elf = module.Elf(folder / name); prior = module.Elf(prior_folder / name)
    account = elf.account(); prior_account = prior.account()
    assert sha(elf.raw) == row['sha256'] == verified['file_sha256'][row['path']]
    assert elf.functions() == prior.functions()
    assert account['init'] == prior_account['init'] and account['fini'] == prior_account['fini']
    assert account['undefined'] == prior_account['undefined']
    assert [r for r in elf.relocations if r['symbol_section'] == ''] == [r for r in prior.relocations if r['symbol_section'] == '']
    sections = {s['name']: s for s in elf.sections if s['flags'] & 2}
    prior_sections = {s['name']: s for s in prior.sections if s['flags'] & 2}
    assert sections.keys() == prior_sections.keys()
    changed = []
    for section_name, section in sections.items():
        prev = prior_sections[section_name]
        for key in ('size', 'alignment', 'flags', 'type'): assert section[key] == prev[key]
        a = prior.section_bytes(prev); b = elf.section_bytes(section)
        if a == b: continue
        assert a.count(old_table) == 1 and a.replace(old_table, new_table) == b
        assert not section['flags'] & 1
        changed.append(dict(section=section_name, table_offset=a.index(old_table),
                            differences=[dict(offset=i, before=x, after=y) for i, (x,y) in enumerate(zip(a,b)) if x != y]))
    assert len(changed) == 1
    assert account['copied_regions'] == prior_account['copied_regions']
    assert account['metadata_chunks'] == prior_account['metadata_chunks']
    prior_review = read(ROOT / ('state/reviews/P2_pin_table_review_raw/target_d72bff70_' + mode + '.json'))
    previous = next(r for r in prior_review['artifacts'] if r['file'] == name)
    assert previous['sha256'] == sha(prior.raw)
    assert account['conditional_pristine_peak_consumption'] == previous['conditional_peak']
    raw_delta = None
    if name == 'app.ino.elf':
        # Only the packaged final ELF is loaded; temp/debug are audit inputs.
        assert all(r['fits'] for r in previous['allocations'])
        assert elf.sections == prior.sections and elf.symbols == prior.symbols and elf.relocations == prior.relocations
        assert len(elf.raw) == len(prior.raw)
        raw_delta = [dict(offset=i, before=x, after=y) for i, (x,y) in enumerate(zip(prior.raw, elf.raw)) if x != y]
        assert len(raw_delta) == 2 and sorted((r['before'],r['after']) for r in raw_delta) == [(2,4),(4,2)]
    records.append(dict(file=name, sha256=sha(elf.raw), bytes=len(elf.raw), prior_sha256=sha(prior.raw),
        changed_readonly_table=changed, complete_final_byte_delta=raw_delta,
        payload=account['compiler_payload'], conditional_peak=previous['conditional_peak'],
        free_span=previous['free_span'], largest_free_payload=previous['largest_free_payload'],
        all_function_bytes_equal=True, all_final_symbols_sections_relocations_equal=(name == 'app.ino.elf')))
package = folder / 'app.ino.elf-zsk.bin'
bundle = next(r for r in audit['bundles'] if r['name'] == package.name)
assert sha(package.read_bytes()) == bundle['sha256'] == verified['file_sha256'][bundle['path']]
result = dict(verdict='PASS_EXACT_TWO_BYTE_DISPLAY_CHANGE_AND_UNCHANGED_CONDITIONAL_FIT',
    source_sha256=audit['source_sha256'], source_files=91, objects=79, source_delta=source_delta,
    mode=mode, artifacts=records, zsk_sha256=bundle['sha256'],
    limitation='Inherits exact D106 startup/import/loader audit, proven unchanged apart from two read-only coordinate bytes. No upload, optical evidence, actual free RAM or WCET.')
(OUT / ('target_618d3a96_' + mode + '.json')).write_text(json.dumps(result, indent=2) + '\n')
final = next(r for r in records if r['file'] == 'app.ino.elf')
print(json.dumps(dict(verdict=result['verdict'], source_sha256=result['source_sha256'], **final), indent=2))
