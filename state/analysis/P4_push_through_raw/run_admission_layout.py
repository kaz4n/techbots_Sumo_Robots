"""Check D131 compiler bounds and host layouts without contacting a board."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
freeze = json.loads((out/'freeze.json').read_text())
for name, expected in freeze.items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest() == expected, name
records = []

def run(name, argv):
    result = subprocess.run(argv, capture_output=True, text=True)
    (out/(name+'.txt')).write_text(result.stdout + result.stderr)
    records.append({'name': name, 'argv': argv, 'returncode': result.returncode})
    return result

with tempfile.TemporaryDirectory(prefix='sumox_d131_admission_', dir='/dev/shm') as temp:
    work = Path(temp)
    probe = work/'layout.cc'
    probe.write_text('''#include "app/runtime.h"
#include <cstdio>
#include <cstddef>
int main(){std::printf("%zu %zu %zu %zu %zu %zu %zu %zu %zu %zu %zu\\n",
sizeof(edge::Escape),sizeof(edge::EscapeSample),sizeof(fsm::Robot),
sizeof(fsm::RobotResult),sizeof(app::Transaction),sizeof(app::Runtime),
sizeof(fsm::RobotInput),sizeof(logframe::EventInput),sizeof(logframe::EventBatch),
offsetof(edge::EscapeSample,heading_updated),offsetof(edge::EscapeSample,line_updated));}
''')
    layouts = {}
    profiles = [('default', []), ('b4', ['-DSUMOX_B4_STAND=1']),
                ('drive', ['-DSUMOX_P3_DRIVE_TEST=1']), ('turn', ['-DSUMOX_P3_TURN_TRIAL=1']),
                ('stop', ['-DSUMOX_P3_STOP_TRIAL=1']), ('reactive', ['-DSUMOX_P4_REACTIVE=1']),
                ('timing', ['-DSUMOX_P4_REACTIVE=1', '-DSUMOX_TIMING_EVIDENCE=1'])]
    for profile, flags in profiles:
        for version, folder in [('prior', out/'before'), ('current', root)]:
            name = 'layout_'+profile+'_'+version
            binary = work/name
            result = run(name+'_build', ['g++', '-std=c++17', '-I', str(folder/'src'),
                                        *flags, str(probe), '-o', str(binary)])
            assert result.returncode == 0, name
            result = run(name, [str(binary)])
            assert result.returncode == 0, name
            layouts[name] = result.stdout.strip()
        assert layouts['layout_'+profile+'_prior'] == layouts['layout_'+profile+'_current'], profile
    fixture = work/'fixture'
    shutil.copytree(root/'src', fixture/'src')
    original = (root/'src/config.h').read_text()
    assert original.count('EDGE_PUSH_THROUGH_MS = 0U') == 1
    for value, accepted in [('0U', True), ('20U', True), ('100U', True),
                            ('101U', False), ('4294967295U', False), ('4294967296ULL', False)]:
        (fixture/'src/config.h').write_text(original.replace('EDGE_PUSH_THROUGH_MS = 0U',
                                                            'EDGE_PUSH_THROUGH_MS = '+value))
        result = run('admission_'+value, ['g++', '-std=c++17', '-Wall', '-Wextra',
                    '-Wpedantic', '-Werror', '-fno-exceptions', '-fno-rtti',
                    '-fsyntax-only', str(fixture/'src/core/edge.cpp')])
        assert (result.returncode == 0) == accepted, value
        if not accepted:
            assert '100ms bound' in result.stderr or 'overflow' in result.stderr, result.stderr
report = {'result': 'PASS', 'commands': records, 'layouts': layouts,
          'limits': 'Host compiler and object layouts only; native image fit and full tick WCET pending.'}
(out/'admission_layout.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report))
