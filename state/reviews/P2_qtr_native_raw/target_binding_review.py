"""Verify supplied D085 final ELF/export receipts offline, without a board."""
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
raw = root/'state/analysis/P2_qtr_native_raw'
source = raw/'target_57f4b001_bench-default.json'
supplement = raw/'target_additional_math.json'
r = json.loads(source.read_text())
s = json.loads(supplement.read_text())
u = next(item for item in r['records'] if item['path'].endswith('.ino.elf'))
assert r['returncode'] == s['returncode'] == 0
assert r['base_sha256'] == s['base_sha256']
assert u['sha256'] == s['elf_sha256']
assert not r['math_missing']


def functions(text):
    return {fields[2]:int(fields[0],16) for line in text.splitlines()
            if len(fields := line.split()) == 3 and fields[1] in ('T','t')}


base = functions('\n'.join(r['math_base_symbols']))
addresses = [int(value,16) for value in re.findall(r'= (0x[0-9a-f]+)',r['math_exports']['stdout'])]
names = sorted(r['math_symbols'].values())
assert len(names) == len(addresses) == 42
bindings = {}
for name,address in zip(names,addresses):
    canonical = name.removeprefix('__llext_sym___real_')
    assert address == base[canonical] | 1, name
    relocations = [line for line in u['relocations']['stdout'].splitlines()
                   if line.split() and line.split()[-1] == '__real_'+canonical]
    if relocations:
        assert {line.split()[2] for line in relocations} == {'R_ARM_THM_MOVW_ABS_NC','R_ARM_THM_MOVT_ABS'}
        assert '<'+canonical+'>:' in u['disassembly'], canonical
    bindings[canonical] = dict(base_thumb_address=hex(address),relocations=relocations)
native = [int(value,16) for value in re.findall(r'= (0x[0-9a-f]+)',r['native_exports']['stdout'])]
assert len(native) == len(r['native_names']) == 36 and all(native)
native_bindings = dict(zip(r['native_names'],map(hex,native)))
assert native_bindings['__device_dts_ord_89'] == '0x801c064'
assert native_bindings['__device_dts_ord_90'] == '0x801c040'
assert native_bindings['__device_dts_ord_91'] == '0x801c01c'
assert native_bindings['z_impl_device_is_ready'] == '0x8019e6f'
assert 'z_impl_gpio_' not in u['undefined']['stdout']

text_relocations = {}
in_text = False
for line in u['relocations']['stdout'].splitlines():
    if line.startswith('Relocation section '):
        in_text = "'.rel.text'" in line
    fields = line.split()
    if in_text and len(fields) >= 5 and re.fullmatch('[0-9a-f]{8}',fields[0]):
        text_relocations[int(fields[0],16)] = line


def bound(offset, symbol):
    line = text_relocations[offset]
    assert line.split()[-1] == symbol, (offset,line,symbol)
    return line


extra_base = functions(s['base_nm']['stdout'].replace('\\n','\n'))
extra_values = [int(value,16) for value in re.findall(r'= (0x[0-9a-f]+)',s['exports']['stdout'])]
assert s['names'] == ['fmod','sqrt'] and len(extra_values) == 2
extra = {}
for name,value,literal in zip(s['names'],extra_values,(0xd410,0xd418)):
    assert value == extra_base[name] | 1, name
    line = bound(literal,'__real_'+name)
    assert 'R_ARM_ABS32' in line
    extra[name] = dict(base_thumb_address=hex(value),literal=hex(literal),relocation=line)

required = ['line_qtr::Reader::begin(', 'line_qtr::Reader::start(',
            'line_qtr::Reader::advance(', 'line_qtr::Reader::cleanup(',
            'line_qtr::applySnapshot(', 'fsm::Robot::step(',
            'fsm::Robot::prepareLine(', 'fsm::Robot::admitLine(',
            'fsm::Robot::prepareFrame(', 'fsm::Robot::receiveFrame(',
            'edge::Classifier::observeMask(', 'edge::Escape::step(',
            'countdown::Services::step(', 'qtr_native_probe::exercise()']
assert all(any(name in line for line in u['nm']) for name in required)
chunks = re.findall(r'^[0-9a-f]+ <.*?(?=\n[0-9a-f]+ <|\Z)',u['disassembly'],re.M|re.S)
startup_names = ['setup','loop','_GLOBAL__sub_I__ZN16qtr_native_probe6readerE',
                 '_GLOBAL__sub_I__ZNK8line_qtr6Reader11globalOwnedEv']
startup = {}
for name in startup_names:
    chunk = next(c for c in chunks if '<'+name+'>:' in c.splitlines()[0])
    assert not re.search(r'\bblx?\s',chunk), name
    startup[name] = chunk
startup_bindings = [bound(0x74,'_ZN16qtr_native_probe5entryE'),
                    bound(0x78,'_ZN16qtr_native_probe8exerciseEv')]
for offsets in ((0x24ac,0x24b0,0x24b4),(0xacec,0xacf0,0xacf4)):
    for offset,symbol in zip(offsets,('_ZGVN12RouterBridge3HCIE','_ZN12RouterBridge3HCIE','Bridge')):
        startup_bindings.append(bound(offset,symbol))
path_bindings = [bound(offset,symbol) for offset,symbol in (
    (0xa184,'__device_dts_ord_89'),(0xa188,'z_impl_device_is_ready'),(0xa18c,'__device_dts_ord_90'),
    (0xa454,'gpio_pin_configure_dt'),(0xa458,'micros'),
    (0xa494,'_ZNK8line_qtr6Reader9bankOwnedEv'),(0xa498,'micros'),
    (0xa49c,'_ZN8line_qtr6Reader9checkTimeEj'),
    (0xb39c,'_ZN8line_qtr6Reader5beginEb'),(0xb3a0,'_ZN8line_qtr6Reader5startEv'),
    (0xb3a4,'_ZN8line_qtr6Reader7advanceEv'),(0xb3a8,'_ZN8line_qtr6Reader6cancelEv'),
    (0xb3b0,'_ZN8line_qtr13applySnapshotERN3fsm10RobotInputERKNS_8SnapshotE'),
    (0xb3bc,'_ZN3fsm5Robot4stepERKNS_10RobotInputE'),
    (0xb3d4,'_ZN8logframe9packFrameERKNS_10FrameInputERNS_10FrameBytesE'))]
result = dict(target_receipt_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              supplement_sha256=hashlib.sha256(supplement.read_bytes()).hexdigest(),
              base_sha256=r['base_sha256'],upload_elf_sha256=u['sha256'],
              native_bindings=native_bindings,aeabi_bindings=bindings,additional_math=extra,
              retained_methods=required,startup=startup,startup_bindings=startup_bindings,
              path_bindings=path_bindings,
              limits='Offline source/ELF/export consistency only. Inherited Bridge/loader runtime and clock remain unqualified.')
(out/'target_binding_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(native=len(native),aeabi=len(bindings),extra_math=extra,
                      retained_methods=len(required),startup_no_calls=startup_names)))
