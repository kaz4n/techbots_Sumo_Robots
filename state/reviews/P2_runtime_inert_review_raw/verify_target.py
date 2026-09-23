"""Independent local-only D104 exact ELF/source/constructor/allocator audit."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P2_runtime_inert_raw'
OUT = Path(__file__).resolve().parent
prefix = sys.argv[1]
assert len(prefix) == 8 and all(c in '0123456789abcdef' for c in prefix)
folder = RAW / ('target_' + prefix)
frozen = RAW / ('target_sources_' + prefix)
audit = json.loads((folder / 'audit.json').read_text())
manifest = json.loads((frozen / 'manifest.json').read_text())
decoder_path = ROOT / 'state/reviews/P2_bridge_dependency_review_raw/elf_review.py'
spec = importlib.util.spec_from_file_location('review_d104_elf', decoder_path)
decoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)
assert audit['source_sha256'] == manifest['source_sha256']
assert audit['source_files'] == manifest['source_files']
aggregate = hashlib.sha256()
for name, digest in sorted(audit['source_files'].items()):
    data = (frozen / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest, name
    if name == 'runtime_inert.ino':
        local = ROOT / 'bench/runtime_inert/runtime_inert.ino'
    elif name.startswith('src/runtime_'):
        local = ROOT / 'bench/runtime_inert' / name
    else:
        local = ROOT / name
    assert hashlib.sha256(local.read_bytes()).hexdigest() == digest, name
    aggregate.update(name.encode()); aggregate.update(b'\0'); aggregate.update(data)
assert aggregate.hexdigest() == audit['source_sha256']

def references(elf, name):
    symbol = next(s for s in elf.symbols if s['name'] == name and s['size'])
    section = elf.sections[symbol['section_index']]
    offset = (symbol['value'] & ~1) - section['address']
    return [r['name'] for r in elf.relocations if r['section'] == section['name'] and
            offset <= r['offset'] < offset + symbol['size']]

baseline = json.loads((ROOT / 'state/analysis/P2_service_reset_raw/'
                      'target_1fbd7238_bench-default/audit.json').read_text())
for key in ('base_sha256', 'math_missing', 'math_symbols',
            'math_aliases', 'base_static_threads'):
    assert audit[key] == baseline[key], key
for key in ('math_exports',):
    assert audit[key]['returncode'] == 0
    assert audit[key]['stdout'] == baseline[key]['stdout']
def native_map(value):
    assert value['native_exports']['returncode'] == 0
    addresses = re.findall(r'(?m)^\$\d+ = (0x[0-9a-f]+)$', value['native_exports']['stdout'])
    assert len(addresses) == len(value['native_names'])
    return dict(zip(value['native_names'], addresses))
old_native, new_native = native_map(baseline), native_map(audit)
assert set(new_native) <= set(old_native)
assert all(address == old_native[name] for name, address in new_native.items())
for name, row in audit['metadata'].items():
    data = row['text'].encode()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
commands = json.loads(audit['metadata']['compile_commands.json']['text'])
for command in commands:
    arguments = command['arguments']
    assert '-DMATCH=0' in arguments and '-DMOTORS_ALLOWED=0' in arguments
    assert '-DMATCH=1' not in arguments and '-DMOTORS_ALLOWED=1' not in arguments
    if not command['file'].endswith('/tls-syms.S'):
        assert '-DARDUINO_LIBRARY_DISCOVERY_PHASE=0' in arguments
    assert not any('/Arduino/libraries/' in value for value in arguments)
verified = []
for record in audit['records']:
    file = folder / Path(record['path']).name
    assert hashlib.sha256(file.read_bytes()).hexdigest() == record['sha256']
    elf = decoder.Elf(file)
    account = elf.account()
    assert len(account['init']) == 1 and not account['fini']
    assert account['init'][0]['name'] == '_GLOBAL__sub_I_runtimeDiagnostics'
    assert elf.functions()['_Z10__loopHookv'] == bytes.fromhex('7047')
    assert next(s for s in elf.symbols if s['name'] == '_Z10__loopHookv')['bind'] == 1
    assert next(s for s in elf.sections if s['name'] == '.static_thread_data_area')['size'] == 0
    assert '_ZN14runtime_native5beginEv' in references(elf, 'setup')
    assert '_ZN14runtime_native4pollEv' in references(elf, 'loop')
    functions = elf.functions()
    forbidden = ('UnoQPort', 'UnoQSources', 'UnoQDumpPort', 'gpio_pin', 'pwm_set',
                 'i2c_write', 'i2c_read', 'uart_poll', 'malloc', 'calloc', 'realloc')
    assert not [name for name in functions if any(word in name for word in forbidden)]
    actual_imports = sorted({r['name'] for r in elf.relocations if r['name'] in account['undefined']})
    assert not [name for name in actual_imports if any(word in name for word in (
        'gpio', 'pwm', 'i2c', 'uart', 'malloc', 'calloc', 'realloc', 'pinctrl', 'device_init'))]
    verified.append({'filename': file.name, 'sha256': record['sha256'],
                     'import_declarations': len(account['undefined']),
                     'actual_external_relocations': actual_imports})

elf = decoder.Elf(folder / 'runtime_inert.ino.elf')
account = elf.account()
package = (folder / 'runtime_inert.ino.elf-zsk.bin').read_bytes()
assert len(package) == len(elf.raw) and package[:7] == elf.raw[:7] and package[16:] == elf.raw[16:]
package_record = next(row for row in audit['bundles'] if row['name'] == 'runtime_inert.ino.elf-zsk.bin')
assert hashlib.sha256(package).hexdigest() == package_record['sha256']
for section in elf.sections:
    if section['name'] in ('.llext.rodata.noreloc', '.symtab', '.strtab', '.shstrtab'):
        assert (0x08100010 + section['offset']) % section['alignment'] == 0
assert (0x08100010 + elf.section_header_offset) % 4 == 0
metadata = account['metadata_chunks']
used, pool = metadata['initial_bookkeeping'], 262144
order = ['.text', '.data', '.rodata', '.bss', '.exported_sym', '.preinit_array', '.init_array', '.fini_array']
regions = {section['name']: section['retained_chunk'] for section in account['copied_regions']}
assert set(regions) <= set(order)
allocations = [('extension', metadata['extension']), ('section_map', metadata['section_map'])]
allocations += [(name, regions[name]) for name in order if name in regions]
allocations += [('symbols', metadata['global_symbols']), ('export_copy', metadata['export_copy'])]
ledger = []
for name, chunk in allocations:
    assert chunk <= pool - used, (name, chunk, pool - used)
    ledger.append({'name': name, 'chunk': chunk, 'remaining_before': pool - used})
    used += chunk
assert used == account['conditional_pristine_peak_consumption']
diagnostic = next(symbol for symbol in elf.symbols if symbol['name'] == 'runtimeDiagnostics')
assert diagnostic['size'] == 232 and diagnostic['section'] == '.bss'
owners = {symbol['name']: symbol['size'] for symbol in elf.symbols if symbol['size'] > 100000}
assert owners == {'_ZN14runtime_native12_GLOBAL__N_16runnerE': 166584}
result = {'source_sha256': audit['source_sha256'], 'source_count': len(audit['source_files']),
          'objects': len(audit['objects']), 'metadata_files': len(audit['metadata']),
          'elfs': verified, 'package_sha256': package_record['sha256'], 'package_bytes': len(package),
          'compiler_payload': account['compiler_payload'], 'conditional_peak': used,
          'conditional_free_span': pool-used, 'conditional_largest_payload': pool-used-4,
          'ordered_allocations': ledger, 'diagnostic': diagnostic, 'owners': owners,
          'constructor_refs': references(elf, '_GLOBAL__sub_I_runtimeDiagnostics'),
          'native_clock_refs': references(elf, '_ZN14runtime_native12_GLOBAL__N_17clockUsEPv'),
          'native_begin_refs': references(elf, '_ZN14runtime_native5beginEv'),
          'native_poll_refs': references(elf, '_ZN14runtime_native4pollEv'),
          'scope': 'Offline exact source/ELF and conditional pristine-pool model; no load or upload approval'}
(OUT / ('target_' + prefix + '.json')).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: result[key] for key in ('source_sha256', 'source_count', 'package_bytes',
    'compiler_payload', 'conditional_peak', 'conditional_free_span', 'diagnostic', 'owners')}, indent=2))
