# Audit the exact D104 source, retained entry paths and offline target ABI.
# Reuse established ELF/loader helpers while enforcing this probe's distinct layout.
# Produce capture pins and budgets without performing any MCU operation.
import ast
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'state/analysis/P2_runtime_inert_raw'
FOLDER = OUT / 'target_2bd817c4'
SOURCE = '2bd817c4e535324964a031cdd44720f26fd145a3cd317ab7b3ced089f35db7e5'
PROJECT = 'runtime_inert.ino'
REVIEW = ROOT / 'state/reviews/P2_bridge_dependency_review_raw'
sys.path.insert(0, str(REVIEW))
from elf_review import Elf
sys.path.insert(0, str(ROOT / 'tools'))
import p0_capture

prior = ROOT / 'state/analysis/P2_app_dump_raw/target_analyze.py'
definitions = [n for n in ast.parse(prior.read_text()).body if isinstance(n, ast.FunctionDef)]
scope = dict(ROOT=ROOT, OUT=OUT, REVIEW=REVIEW, Path=Path, json=json, ast=ast,
             hashlib=hashlib, re=re, struct=struct, Elf=Elf)
exec(compile(ast.Module(body=definitions, type_ignores=[]), str(prior), 'exec'), scope)
scope['prior_function'] = scope['load_function']('verify_elfs.py', 'function')
scope['relocations'] = scope['load_function']('compare_objects.py', 'relocations')
order_path = ROOT / 'state/analysis/P2_frame_packing_target_analyze.py'
order = next(n for n in ast.parse(order_path.read_text()).body
             if isinstance(n, ast.FunctionDef) and n.name == 'allocation_order')
exec(compile(ast.Module(body=[order], type_ignores=[]), str(order_path), 'exec'), scope)

audit = json.loads((FOLDER / 'audit.json').read_text())
assert audit['source_sha256'] == SOURCE and all(audit['checks'].values())
frozen = OUT / 'target_sources_2bd817c4'
manifest = json.loads((frozen / 'manifest.json').read_text())
assert len(manifest['source_files']) == 91 and manifest['source_files'] == audit['source_files']
digest = hashlib.sha256()
for name, expected in sorted(manifest['source_files'].items()):
    payload = (frozen / name).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == expected
    digest.update(name.encode()+b'\0'); digest.update(payload)
assert digest.hexdigest() == SOURCE
old_folder = ROOT / 'state/analysis/P2_service_reset_raw/target_1fbd7238_bench-default'
old_audit = json.loads((old_folder / 'audit.json').read_text())
old_shared = {n: h for n, h in old_audit['source_files'].items() if n != 'app.ino'}
assert len(old_shared) == 86 and all(audit['source_files'].get(n) == h for n, h in old_shared.items())
assert set(audit['source_files'])-set(old_shared) == {PROJECT, 'src/runtime_bench.cpp',
    'src/runtime_bench.h', 'src/runtime_native.cpp', 'src/runtime_native.h'}
baseline_sources = json.loads((OUT/'target_sources_1cd2f6cc/manifest.json').read_text())['source_files']
assert [n for n,h in audit['source_files'].items() if baseline_sources.get(n) != h] == ['src/runtime_bench.cpp']
assert audit['source_files']['src/runtime_bench.cpp'] == '987eb73ad16510ae2895e938aba3ac3d6e197f7987cb5b8c1d7c6df5982f0b89'
assert 'if (ended_us - report_.boot_us >= DEADLINE_US) fail(Failure::DEADLINE);' in (frozen/'src/runtime_bench.cpp').read_text()
metadata = scope['metadata'](audit)

elf = Elf(FOLDER / (PROJECT+'.elf'))
old_elf = Elf(old_folder / 'app.ino.elf')
names = {s['name']: s for s in elf.symbols if s['section_index'] and s['name']}
imports = sorted({s['name'] for s in elf.symbols if not s['section_index'] and s['name']})
old_imports = set(old_elf.account()['undefined'])
assert set(imports)-old_imports == {'z_impl_k_sched_current_thread_query'}
assert old_imports-set(imports) == {'__device_dts_ord_'+n for n in ('30','34','61','70','73','83','88')}
verified = []
receipt = json.loads((FOLDER / 'build_receipt/verified.json').read_text())
for record in audit['records']:
    path = FOLDER / Path(record['path']).name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'] == receipt['file_sha256'][record['path']]
    observed = sorted({s['name'] for s in Elf(path).symbols if not s['section_index'] and s['name']})
    assert observed == imports == sorted(row.split()[-1] for row in record['undefined']['stdout'].splitlines())
    verified.append(dict(name=path.name, bytes=len(path.read_bytes()), sha256=record['sha256'], imports=len(imports)))
assert audit['base_sha256'] == old_audit['base_sha256']
assert audit['math_symbols'] == old_audit['math_symbols'] and not audit['math_missing']
assert audit['math_exports']['stdout'] == old_audit['math_exports']['stdout']
assert len(audit['native_names']) == 32
assert len(re.findall(r'^\$\d+ = 0x[1-9a-f][0-9a-f]*$', audit['native_exports']['stdout'], re.M)) == 32
forbidden = ('UnoQ', 'Bridge', 'RPClite', 'ZephyrSerial', 'HardwareSerial', 'TwoWire', 'msgpack',
             'pinMode', 'digitalWrite', 'analogWrite', 'analogRead', 'uart_', 'gpio_', 'pwm_')
assert not any(any(token in name for token in forbidden) for name in names)
forbidden_relocations = ('matrix', 'pinctrl', 'device_init', 'device_is_ready', 'malloc', 'calloc',
                         'realloc', 'free', 'uart', 'gpio', 'pwm', 'analog_read')
assert not any(any(token in r['name'] for token in forbidden_relocations) for r in elf.relocations)

startup_names = ['main','setup','loop','initVariant','_Z10__loopHookv','_Z20start_static_threadsv',
                 'micros','_GLOBAL__sub_I_runtimeDiagnostics']
startup = {n: scope['function'](elf, n) for n in startup_names}
for name in ('main','initVariant','_Z10__loopHookv','_Z20start_static_threadsv','micros'):
    for key in ('normalized_bytes_hex','relocations','bss_targets'):
        assert startup[name][key] == scope['function'](old_elf, name)[key], (name,key)
assert startup['_Z10__loopHookv']['symbol']['bind'] == 1
assert startup['_Z10__loopHookv']['bytes_hex'] == '7047'
assert startup['initVariant']['bytes_hex'] == '7047'
assert next(s for s in elf.sections if s['name'] == '.static_thread_data_area')['size'] == 0
retained = {n: scope['function'](elf,n) for n,s in names.items()
            if s['type'] == 2 and (n.startswith('_ZN13runtime_bench') or n.startswith('_ZN14runtime_native'))}
edges = [('setup','_ZN14runtime_native5beginEv'), ('loop','_ZN14runtime_native4pollEv'),
    ('_GLOBAL__sub_I_runtimeDiagnostics','_ZN13runtime_bench6RunnerC1ERKNS_9ClockPortE'),
    ('_ZN13runtime_bench6RunnerC2ERKNS_9ClockPortE', '_ZN3app7RuntimeC1ERKN6motors4PortERKN5power9InputPortERKNS_10SourcePortERKNS_8DumpPortE'),
    ('_ZN13runtime_bench6Runner5beginEv','_ZN3app7Runtime5beginERKNS_11SetupGrantsE'),
    ('_ZN13runtime_bench6Runner4pollEv','_ZN3app7Runtime4stepEv')]
for caller, callee in edges:
    row = startup.get(caller, retained.get(caller))
    assert row and any(r['name'] == callee for r in row['relocations']), (caller,callee)
assert names['runtimeDiagnostics']['size'] == 232 and names['runtimeDiagnostics']['value'] == 166624
assert names['runtimeDiagnostics']['section'] == '.bss'
runner_name = '_ZN14runtime_native12_GLOBAL__N_16runnerE'
assert names[runner_name]['size'] == 166584 and names[runner_name]['value'] == 0
memory = scope['loader'](elf)
assert memory['temporary_symbols_fit'] and memory['complete_peak_deficit'] == 0
account = memory['account']
assert [r['name'] for r in account['init']] == ['_GLOBAL__sub_I_runtimeDiagnostics'] and not account['fini']
assert any(r['section'] == '.exported_sym' and r['name'] == 'main' for r in elf.relocations)
allocation_order = scope['allocation_order'](account)
scope['baseline'] = dict(old_audit, objects=[o for o in old_audit['objects'] if o['path'] != 'sketch/app.ino.cpp.o'])
objects = scope['compare_objects'](audit)
assert not objects['changes'] and objects['objects'] == 79
assert objects['added_objects'] == ['sketch/runtime_inert.ino.cpp.o', 'sketch/src/runtime_bench.cpp.o',
                                    'sketch/src/runtime_native.cpp.o']

abi_dir = OUT / 'target_abi_2bd817c4'
abi = json.loads((abi_dir / 'stdout.json').read_text())
abi_receipt = json.loads((abi_dir / 'receipt.json').read_text())
assert abi_receipt['returncode'] == 0 and not (abi_dir / 'stderr.txt').read_text()
assert all(c['returncode'] == 0 and not c['stderr'] for c in abi['commands'])
for path, value in abi['file_sha256'].items():
    if path in receipt['file_sha256']:
        assert value == receipt['file_sha256'][path]
for path, expected in p0_capture.EXPECTED_HASHES.items():
    if path.as_posix() in abi['file_sha256']:
        assert abi['file_sha256'][path.as_posix()] == expected
assert abi['file_sha256'][p0_capture.READELF.as_posix()] == 'c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e'
assert hashlib.sha256((ROOT/'tools/p0_mem_read.cfg').read_bytes()).hexdigest() == '89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339'
type_text = abi['commands'][0]['stdout']
values = [int(v) for v in re.findall(r'^\$\d+ = (\d+)$', type_text, re.M)]
assert values == [232,4,192,32,166584,8,166304,162544,2640,159200]
assert re.search(r'/\*\s+4\s+\|\s+192 \*/\s+struct runtime_bench::Report', type_text)
assert re.search(r'/\*\s+196\s+\|\s+32 \*/\s+struct runtime_bench::StackSample', type_text)
assert re.search(r'/\*\s+228\s+\|\s+4 \*/\s+uint32_t sequence_tail', type_text)
assert re.search(r'/\*\s+64\s+\|\s+166304 \*/\s+class app::Runtime', type_text)
base_text = abi['commands'][1]['stdout']
assert all(x in base_text for x in ('$1 = 256', '$2 = 160', '$3 = 32768', '$4 = 24', '$5 = 262144',
    '0x2000112c', '0x20013890', '$7 = 0x8011ae1', '$8 = 0x0'))
disassembly = abi['commands'][2]['stdout']
assert 'mrs' in disassembly and all(x in disassembly for x in ('CONTROL','IPSR','PSP','dmb'))

package = FOLDER / (PROJECT+'.elf-zsk.bin')
package_bytes = package.read_bytes()
bundle = next(b for b in audit['bundles'] if b['name'] == package.name)
assert len(package_bytes) == bundle['bytes'] and 65536 < len(package_bytes) <= 131072
assert hashlib.sha256(package_bytes).hexdigest() == bundle['sha256'] == receipt['file_sha256'][bundle['path']]
assert package_bytes[16:] == elf.raw[16:] and len(package_bytes) == len(elf.raw)
header_differences = [i for i in range(16) if package_bytes[i] != elf.raw[i]]
inventory_run = json.loads((OUT/'target_artifact_inventory.json').read_text())
assert inventory_run['returncode'] == 0 and not inventory_run['stderr']
inventory = {Path(r['path']).name:r for r in json.loads(inventory_run['stdout'])}
assert inventory[PROJECT+'.elf']['sha256'] == account['sha256']
assert inventory[package.name]['sha256'] == bundle['sha256']
assert all(row['path'].startswith(receipt['artifacts']+'/') for row in inventory.values())
budget = []
for nodes in range(1,5):
    reads = 5+2+2+nodes+2+2+32
    byte_count = 263680+len(package_bytes)+16+nodes*196+2*232+2*24+2*262144
    budget.append(dict(extension_nodes=nodes, reads=reads, bytes=byte_count,
                       fits_48_reads=reads <= 48, fits_2MiB=byte_count <= 2097152))
sources = json.loads((ROOT / 'state/analysis/P2_memory_validation_raw/source_receipt.json').read_text())
for source in sources:
    assert hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256']
pins = dict(source_sha256=SOURCE, project=PROJECT, build_path=receipt['build_path'],
    artifact_path=receipt['artifacts'], elf_sha256=account['sha256'], package_sha256=bundle['sha256'],
    package_bytes=len(package_bytes), package_flash_chunks=[65536,len(package_bytes)-65536],
    loader_flash_bytes=263680, loader_flash_chunks=[65536,65536,65536,65536,1536],
    file_sha256=abi['file_sha256'], capture_config_sha256=hashlib.sha256((ROOT/'tools/p0_mem_read.cfg').read_bytes()).hexdigest(),
    diagnostics=dict(symbol='runtimeDiagnostics', bss_section=7, bss_size=166856, offset=166624,
        size=232, alignment=4, front_offset=0, report_offset=4, stack_offset=196, tail_offset=228),
    loader_abi=dict(thread_bytes=256, stack_info_offset=160, main_stack_reserved=32768,
        heap_descriptor_address=0x2000112c, heap_descriptor_bytes=24, pool_address=0x20013890, pool_bytes=262144,
        current_thread_export=0x08011ae1, stack_space_export=0), capture_budget=budget)
report = dict(scope='Exact completed-target offline source/ELF/ABI/conditional-loader evidence only',
    superseded_baseline_source='1cd2f6ccce8d7c44649ad7ec48494704060ffbc4266feb748e03fd413be818b8',
    source_files=91, shared_d103_files=86, metadata=metadata, verified_elfs=verified,
    native_exports=32, aeabi_exports=len(audit['math_symbols']), imports=imports,
    unused_native_declarations=[n for n in imports if any(t in n for t in ('matrix','pinctrl','device_init','device_is_ready'))],
    no_native_owner_symbols_or_io_allocation_relocations=True, startup=startup,
    retained_probe_functions=retained, checked_call_edges=edges, objects=objects, memory=memory,
    allocation_order=allocation_order, target_abi_values=values, capture_pins=pins,
    package_payload_after_header_identical=True, package_header_differences=header_differences,
    pinned_loader_sources=sources, reused_helpers_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (prior, order_path)})
(OUT/'target_summary.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'target_capture_pins.json').write_text(json.dumps(pins,indent=2)+'\n')
print(json.dumps(dict(payload=account['compiler_payload'], peak=account['conditional_pristine_peak_consumption'],
    largest=account['conditional_largest_payload'], imports=len(imports), diagnostics=pins['diagnostics'],
    capture_budget=budget),indent=2))
