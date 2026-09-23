"""Check supplied D084 ELF bindings offline; never contact the board."""
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
raw = root/'state/analysis/P2_imu_integration_raw'
source = raw/'target_f3bc1f7f_bench-default.json'
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
            if len(fields := line.split()) == 3 and fields[1] in ('T', 't')}


base = functions('\n'.join(r['math_base_symbols']))
addresses = [int(value,16) for value in re.findall(r'= (0x[0-9a-f]+)', r['math_exports']['stdout'])]
names = sorted(r['math_symbols'].values())
assert len(names) == len(addresses) == 42
bindings = {}
for name, address in zip(names, addresses):
    canonical = name.removeprefix('__llext_sym___real_')
    assert address == base[canonical] | 1, name
    symbol = '__real_' + canonical
    relocations = [line for line in u['relocations']['stdout'].splitlines()
                   if line.split() and line.split()[-1] == symbol]
    kinds = {line.split()[2] for line in relocations}
    assert kinds == {'R_ARM_THM_MOVW_ABS_NC', 'R_ARM_THM_MOVT_ABS'}, (name,kinds)
    assert '<'+canonical+'>:' in u['disassembly'], canonical
    bindings[canonical] = {'base_thumb_address':hex(address), 'relocations':relocations}

native = [int(value,16) for value in re.findall(r'= (0x[0-9a-f]+)', r['native_exports']['stdout'])]
assert len(native) == len(r['native_names']) == 36 and all(native)
# Supplemental collector joined its selected lines with literal escapes; normalize
# those separators explicitly while preserving the supplied receipt bytes.
extra_base = functions(s['base_nm']['stdout'].replace('\\n','\n'))
extra_values = [int(value,16) for value in re.findall(r'= (0x[0-9a-f]+)', s['exports']['stdout'])]
extra = {}
assert s['names'] == ['fmod','sqrt'] and len(extra_values) == 2
for name, value, literal in zip(s['names'], extra_values, (0xc770,0xc778)):
    assert value == extra_base[name] | 1, name
    matching = [line for line in u['relocations']['stdout'].splitlines()
                if line.startswith(f'{literal:08x} ') and line.split()[-1] == '__real_'+name]
    assert len(matching) == 1 and 'R_ARM_ABS32' in matching[0]
    extra[name] = {'base_thumb_address':hex(value), 'literal':hex(literal),
                   'relocation':matching[0]}

required = ['fsm::Robot::step(', 'fsm::Robot::prepareImu(', 'fsm::Robot::admitImu(',
            'fsm::Robot::admitImuHeading(', 'fsm::Robot::prepareFrame(',
            'fsm::Robot::receiveFrame(', 'fsm::HeadingReference::advance(',
            'imu::applyEstimate(', 'imu::Estimator::observe(',
            'imu_integration_probe::exercise()']
assert all(any(name in line for line in u['nm']) for name in required)
setup = re.search(r'0000006c <setup>:(.*?)(?=\n[0-9a-f]+ <)', u['disassembly'], re.S).group(1)
loop = re.search(r'0000007c <loop>:(.*?)(?=\n[0-9a-f]+ <)', u['disassembly'], re.S).group(1)
initializer = re.search(r'00002490 <_GLOBAL__sub_I__ZN21imu_integration_probe9estimatorE>:(.*?)(?=\n[0-9a-f]+ <)', u['disassembly'], re.S).group(1)
assert not re.search(r'\bblx?\s', setup+loop+initializer)
assert re.search(r'\bstr\s', setup) and re.search(r'\bbx\s+lr', loop)
result = {'target_receipt_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'supplement_sha256':hashlib.sha256(supplement.read_bytes()).hexdigest(),
          'base_sha256':r['base_sha256'], 'upload_elf_sha256':u['sha256'],
          'native_export_count':len(native), 'aeabi_bindings':bindings,
          'additional_math':extra, 'required_retained_methods':required,
          'startup':{'setup_address':'0x6c','loop_address':'0x7c',
                     'probe_initializer_address':'0x2490','no_call_in_these_functions':True},
          'scope':'Offline source/ELF/export consistency only; inherited runtime remains unqualified'}
(out/'target_binding_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'native':len(native),'aeabi':len(bindings),'additional_math':extra,
                  'retained_methods':len(required),'startup_no_call':True}))
