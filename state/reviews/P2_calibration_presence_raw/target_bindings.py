"""Check collected D083 target bindings without opening any board connection."""
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
path = root/'state/analysis/P2_calibration_presence_raw/target_9a7c6432_bench-default.json'
receipt = json.loads(path.read_text())
assert receipt['returncode'] == 0 and not receipt['math_missing']
record, = [item for item in receipt['records'] if item['path'].endswith('.ino.elf')]
base = {line.split()[-1]: int(line.split()[0], 16)
        for line in receipt['math_base_symbols']}
math_commands = receipt['math_exports']['argv']
math_symbols = [argument.removeprefix('p/x ').removesuffix('.addr')
                for argument in math_commands if argument.startswith('p/x ')]
math_addresses = [int(value, 16) for value in re.findall(
    r'\$\d+ = (0x[0-9a-f]+)', receipt['math_exports']['stdout'])]
assert len(math_symbols) == len(math_addresses) == 42
exports = dict(zip(math_symbols, math_addresses))
for symbol, address in exports.items():
    function = symbol.removeprefix('__llext_sym___real_')
    assert address == base[function] | 1, (symbol, address, base[function])
native_values = re.findall(r'\$\d+ = (0x[0-9a-f]+)', receipt['native_exports']['stdout'])
assert len(native_values) == len(receipt['native_names']) == 36
assert all(int(value, 16) != 0 for value in native_values)

relocations = []
for line in record['relocations']['stdout'].splitlines():
    fields = line.split()
    if len(fields) >= 5 and re.fullmatch('[0-9a-f]{8}', fields[0]):
        relocations.append(dict(address=int(fields[0], 16), kind=fields[2], symbol=fields[4]))
blocks = {}
for match in re.finditer(r'^([0-9a-f]+) <(.*?)>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',
                         record['disassembly'], re.M | re.S):
    blocks[match[2]] = (int(match[1], 16), match[3])
helpers = set()
for method in ('countdown::Services::observeCalibration(countdown::ServiceSample const&)',
               'countdown::Services::finishCalibration()'):
    _, code = blocks[method]
    addresses = {int(value, 16) for value in re.findall(r'@ \(?([0-9a-f]+) ', code)}
    helpers.update(item['symbol'] for item in relocations
                   if item['address'] in addresses and item['symbol'].startswith('__aeabi_'))
bindings = {}
for helper in sorted(helpers):
    address, code = blocks[helper]
    name = '__real_' + helper
    selected = [item for item in relocations if item['address'] in (address, address + 4)]
    assert {item['kind'] for item in selected} == {'R_ARM_THM_MOVW_ABS_NC', 'R_ARM_THM_MOVT_ABS'}
    assert {item['symbol'] for item in selected} == {name}
    bindings[helper] = dict(wrapper_address=hex(address), relocations=selected,
                            base_export_address=hex(exports['__llext_sym_' + name]))
assert len(bindings) == 9

init_name = '_GLOBAL__sub_I__ZN17calibration_probe9lifecycleE'
_, initializer = blocks[init_name]
assert not re.search(r'\bblx?\s', initializer)
assert not any('countdown' in name and name.startswith('_GLOBAL') for name in blocks)
startup = {}
for address, expected in {0xd4: '_ZN17calibration_probe5entryE',
                          0xd8: '_ZN17calibration_probe8exerciseEv',
                          0x250c: '_ZGVN12RouterBridge3HCIE',
                          0x2510: '_ZN12RouterBridge3HCIE',
                          0x2514: 'Bridge'}.items():
    assert any(item['address'] == address and item['symbol'] == expected for item in relocations)
    startup[hex(address)] = expected
result = dict(receipt_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
              base_sha256=receipt['base_sha256'], all_literal_math_exports=len(exports),
              all_exports_match_thumb_function_addresses=True,
              calibration_helpers=bindings, nonzero_native_exports=len(native_values),
              startup_literal_relocations=startup, probe_initializer_has_no_calls=True,
              scope='Offline source/ELF/export consistency only; no executed loader, MCU, or WCET qualification')
(out/'target_binding_audit.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
