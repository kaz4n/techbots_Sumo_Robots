"""Inspect saved target build only; no transport or MCU interaction."""
from pathlib import Path,PureWindowsPath
import hashlib,json,re
root=Path.cwd(); out=root/'state/reviews/P2_power_inputs_review_raw'
path=root/'state/analysis/P2_power_inputs_raw/target_4d5e21cc_bench-default.json'
d=json.loads(path.read_text())
prior=json.loads((root/'state/analysis/P2_tick_timing_raw/target_5451e99d_bench-default.json').read_text())
assert d['returncode']==0 and len(d['records'])==3 and not d['math_missing']
h=hashlib.sha256()
# The actual board_tool invocation staged on Windows: pathlib sorts case-insensitively.
for p,digest in sorted(d['source_files'].items(),key=lambda item:PureWindowsPath(item[0])):
    origin=root/p if p.startswith(('src/core/','src/hal/')) or p=='src/config.h' else root/'bench/p2_power_inputs_compile'/p
    data=origin.read_bytes()
    assert hashlib.sha256(data).hexdigest()==digest,p
    h.update(p.encode()+b'\0');h.update(data)
assert h.hexdigest()==d['source_sha256']
assert d['base_sha256']==prior['base_sha256']
assert d['native_names']==prior['native_names']
assert d['math_symbols']==prior['math_symbols']
required=['power::InputOwner::begin()', 'power::InputOwner::readBatteryIfDue(bool)',
          'power::InputOwner::readButtons(bool)', 'power::readerInputPort(power::Reader&)',
          'power::Reader::read()', 'power::Reader::readButtons()',
          'power_inputs_probe::exercise', 'fsm::Robot::step', 'motors::MotorGate::apply',
          'recorder::AttemptRecorder::consume', '__loopHook()']
records=[]; excerpts={}
for r,p in zip(d['records'],prior['records']):
    assert set(r['undefined']['stdout'].splitlines())==set(p['undefined']['stdout'].splitlines())
    symbols='\n'.join(r['nm'])
    assert all(s in symbols for s in required)
    records.append(dict(path=r['path'],sha256=r['sha256'],bytes=r['bytes'],
                        symbols=[s for s in r['nm'] if any(t in s for t in required)]))
    if 'disassembly' not in r: continue
    name=None
    for line in r['disassembly'].splitlines():
        if line.endswith('>:'):
            name=line.split('<',1)[1][:-2]
            if name in ['setup','loop','__loopHook()','power::readerInputPort(power::Reader&)',
                        'power::InputOwner::InputOwner(power::InputPort const&)'] or name.startswith('_GLOBAL__sub_I_'):
                excerpts[name]=[line]
            else: name=None
        elif name is not None: excerpts[name].append(line)
assert 'bx\tlr' in '\n'.join(excerpts['loop'])
assert 'bx\tlr' in '\n'.join(excerpts['__loopHook()'])
assert 'bl\t' not in '\n'.join(excerpts['setup'])
(out/'startup_disassembly.txt').write_text('\n\n'.join('\n'.join(lines) for lines in excerpts.values())+'\n')
result=dict(source_sha256=d['source_sha256'],source_file_count=len(d['source_files']),
            raw_receipt_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),records=records,
            loader_sha256=d['base_sha256'],native_count=len(d['native_names']),aeabi_count=len(d['math_symbols']),
            imports_unchanged_from='D092 5451e99d',scope='Saved compile-only source and ELF evidence; no hardware action')
(out/'target_review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
