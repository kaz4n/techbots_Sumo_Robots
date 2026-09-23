"""Compare opaque compiled source hashes with final workspace bytes."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUN = HERE / 'run_1790185111677398343'
entries = []
for filename, configured in (('command_01.json', False), ('command_05.json', True)):
    receipt = json.loads((RUN / filename).read_text())
    for staged, expected in receipt['sha256'].items():
        if '/src/' in staged and staged.startswith('/dev/shm/'):
            relative = staged.split('/src/', 1)[1]
            current = ROOT / 'src' / relative
            if relative == 'config.h' and configured:
                current = RUN / 'synthetic_config.h'
        else:
            current = Path(staged)
        actual = hashlib.sha256(current.read_bytes()).hexdigest()
        entries.append({'receipt': filename, 'compiled': staged, 'current': str(current),
                        'expected': expected, 'actual': actual, 'match': actual == expected})
tools = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
         for path in (ROOT / 'tools').glob('*.py')}
test_dependencies = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in [ROOT / 'tests/fixtures/qtr_cal_fixture.h', ROOT / 'host/third_party/doctest.h',
                 ROOT / 'tests/locked/native_motor_port/test_main.cc']}
report = {'all_compiled_sources_match': all(item['match'] for item in entries),
          'entries': entries, 'receiver_tool_sha256': tools,
          'additional_test_dependency_sha256': test_dependencies}
(RUN / 'final_source_integrity.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'all_compiled_sources_match': report['all_compiled_sources_match'],
                  'comparisons': len(entries), 'receipt': str(RUN / 'final_source_integrity.json')}))
assert report['all_compiled_sources_match']
