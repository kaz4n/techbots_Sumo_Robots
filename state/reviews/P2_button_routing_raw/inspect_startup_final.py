"""Inspect frozen D087 target startup and additional math receipts offline."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'state/analysis/P2_button_routing_raw'
target = json.loads((RAW / sys.argv[1]).read_text())
extra = json.loads((RAW / 'target_additional_math.json').read_text())
upload = next(r for r in target['records'] if r['path'].endswith('.ino.elf'))
assert extra['returncode'] == 0
assert extra['base_sha256'] == target['base_sha256']
assert extra['elf_sha256'] == upload['sha256']
functions = {f[2]: int(f[0], 16) for line in extra['base_nm']['stdout'].splitlines()
             if len(f := line.split()) == 3 and f[1] in ('t', 'T')}
bindings = {}
addresses = extra['exports']['stdout'].splitlines()
assert len(addresses) == len(extra['names']) == 2
for name, line in zip(extra['names'], addresses):
    address = int(line.split('=')[1], 16)
    assert address != 0 and address & ~1 == functions[name]
    assert '<' + name + '>:' in extra['wrappers']['stdout']
    assert '__real_' + name in upload['relocations']['stdout']
    bindings[name] = address

assembly = upload['disassembly']
blocks = {}
current = None
for line in assembly.splitlines():
    match = re.match(r'^[0-9a-f]+ <(.+)>:$', line)
    if match:
        current = match[1]
        blocks[current] = []
    if current:
        blocks[current].append(line)
chosen = ['setup', 'loop', 'initVariant', '__loopHook()']
chosen += [name for name in blocks if name.startswith('_GLOBAL__sub_I')]
for name in ['setup', 'loop', 'initVariant', '_GLOBAL__sub_I__ZN12button_probe6readerE']:
    assert name in blocks
    assert not any(re.search(r'\b(bl|blx)\b', line) for line in blocks[name]), name
assert 'ui::decodeButtons(power::ButtonSample const&)' in blocks
assert 'ui::applyButtons(fsm::RobotInput&, power::ButtonSample const&)' in blocks
assert any('fsm::Robot::prepareButtons' in name for name in blocks)
assert any('power::Reader::beginWithButtons' in name for name in blocks)
assert any('power::Reader::readButtons' in name for name in blocks)
assert 'button_probe::exercise()' in blocks
assert not any(re.search(r'_ZN[K]?(3fsm|2ui)', name) for name in chosen if name.startswith('_GLOBAL__sub_I'))
relocations = upload['relocations']['stdout'].splitlines()
start = next(i for i, line in enumerate(relocations) if "'.rel.init_array'" in line)
init = relocations[start:start + 12]
assert '9 entries' in init[0]
selected = [line for line in relocations if any(s in line for s in (
    'button_probe', '__real_fmod', '__real_sqrt', '_GLOBAL__sub_I',
    'uart_serial', 'getInstance', 'thread', 'msgpack', 'k_mutex', 'initVariant'))]
(OUT / 'startup_final_selected.txt').write_text('\n'.join('\n'.join(blocks[name]) for name in chosen))
(OUT / 'startup_final_relocations.txt').write_text('\n'.join(init + selected))
data = dict(scope='Offline receipt review, not MCU startup execution',
            source=target['source_sha256'], base_sha256=target['base_sha256'],
            upload_elf_sha256=upload['sha256'], additional_math_bindings=bindings,
            startup_functions=chosen, init_array_entries=9,
            no_calls_in_new_TU_initializer_setup_loop_and_initVariant=True,
            project_methods_retained=True,
            receipt_sha256=hashlib.sha256((RAW / sys.argv[1]).read_bytes()).hexdigest(),
            limit='Inherited Bridge/UART/libstdc++ startup and base static thread remain. No new project pin/native initialization; this is not a globally I/O-free runtime claim.')
(OUT / 'startup_final_audit.json').write_text(json.dumps(data, indent=2) + '\n')
print(json.dumps(data))

