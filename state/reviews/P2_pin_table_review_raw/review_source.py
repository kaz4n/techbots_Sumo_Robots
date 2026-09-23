"""Literal source and protected-test comparison against final D105 and D106 freeze."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
OLD = ROOT / 'state/analysis/P2_calibration_delivery_raw/target_sources_c05916c6'
def sha(data): return hashlib.sha256(data).hexdigest()
worker = ROOT / 'state/analysis/P2_pin_table_raw/worker'
frozen = json.loads((worker / 'source_freeze.json').read_text())
consumers = ('motor_port_unoq.cpp', 'line_qtr.cpp', 'opp_sensors.cpp', 'power.cpp')
rows = []
for name in consumers:
    path = 'src/hal/' + name
    old = (OLD / path).read_bytes()
    assert old == (worker / ('before_' + name)).read_bytes()
    text = old.decode().replace('\r\n', '\n')
    text = text.replace('#include <wiring_private.h>\n', '#include <wiring_private.h>\n#include "native_pins.h"\n')
    text, count = re.subn(r'constexpr std::size_t PIN_COUNT = sizeof\(zephyr::arduino::arduino_pins\) /\n +sizeof\(zephyr::arduino::arduino_pins\[0\]\);\n', '', text)
    assert count == 1
    text = text.replace('PIN_COUNT', 'native_pins::COUNT').replace('zephyr::arduino::arduino_pins', 'native_pins::TABLE')
    current = (ROOT / path).read_bytes()
    assert text == current.decode().replace('\r\n', '\n'), path
    assert sha(current) == frozen[path]
    rows.append(dict(path=path, old_sha256=sha(old), new_sha256=sha(current), mechanical_only=True))
unchanged = []
for file in (OLD / 'src').rglob('*'):
    if not file.is_file(): continue
    path = file.relative_to(OLD).as_posix()
    if path in frozen: continue
    assert file.read_bytes() == (ROOT / path).read_bytes(), path
    unchanged.append(path)
class RemoveDependency(ast.NodeTransformer):
    def clean(self, node):
        node.elts = [e for e in node.elts if 'native_pins.' not in ast.unparse(e)]
        return self.generic_visit(node)
    visit_List = clean
    visit_Tuple = clean
audit = json.loads((ROOT / 'state/analysis/P2_pin_table_raw/harness_audit.json').read_text())
test_rows = []
for row in audit['files']:
    old = subprocess.check_output(['git', 'show', '4778ced:' + row['path']], cwd=ROOT)
    current = (ROOT / row['path']).read_bytes()
    assert sha(old) == row['before_sha256'] and sha(current) == row['after_sha256']
    assert ast.dump(RemoveDependency().visit(ast.parse(old))) == ast.dump(RemoveDependency().visit(ast.parse(current)))
    test_rows.append(row)
protected = subprocess.check_output(['git', 'diff', '4778ced', '--', 'src/config.h', 'src/core', 'tests/locked'], cwd=ROOT)
assert protected == b''
original_test = (ROOT / 'state/analysis/P2_pin_table_raw/author/test_native_pins_v1_frozen.py').read_text()
current_test = (ROOT / 'tests/tooling/test_native_pins.py').read_text()
added = '            (stage / "Arduino.h").write_text("#pragma once\\n#include <zephyr/drivers/gpio.h>\\n")\n'
assert current_test.replace(added, '') == original_test
new = {p:sha((ROOT/p).read_bytes()) for p in ('src/hal/native_pins.h','src/hal/native_pins.cpp','tests/tooling/test_native_pins.py')}
result = dict(verdict='PASS_MECHANICAL_SOURCE_AND_TEST_SCOPE', consumers=rows,
              unchanged_source_files=len(unchanged), new_files=new, legacy_test_modules=test_rows,
              protected_config_core_locked_tests_unchanged=True,
              new_test_correction='Only missing Arduino.h fixture; all stimuli/assertions unchanged')
(OUT/'source_review.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(dict(verdict=result['verdict'], unchanged_source_files=len(unchanged), consumers=len(rows), legacy_test_modules=len(test_rows)), indent=2))
