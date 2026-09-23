# Verifies old native test programs changed only source dependency list entries.
# Keeps complete existing assertions and fixtures independent of the implementation.
# Compares parsed historical/current modules after removing the new dependency.
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
FILES = ['test_motor_port_unoq.py', 'test_opp_sensors.py', 'test_qtr_native.py',
         'test_power_unoq.py', 'test_adc_pair_unoq.py', 'test_button_decoder.py',
         'test_app_transaction.py', 'test_power_inputs.py']


class RemoveDependency(ast.NodeTransformer):
    def clean(self, node):
        node.elts = [e for e in node.elts if 'native_pins.' not in ast.unparse(e)]
        return self.generic_visit(node)
    visit_List = clean
    visit_Tuple = clean


records = []
for name in FILES:
    path = 'tests/tooling/' + name
    before = subprocess.check_output(['git', 'show', '4778ced:' + path], cwd=ROOT)
    after = (ROOT / path).read_bytes()
    old = ast.dump(RemoveDependency().visit(ast.parse(before)), include_attributes=False)
    new = ast.dump(RemoveDependency().visit(ast.parse(after)), include_attributes=False)
    assert old == new, 'Change outside new native-pins dependency: ' + path
    records.append(dict(path=path, before_sha256=hashlib.sha256(before).hexdigest(),
                        after_sha256=hashlib.sha256(after).hexdigest(), equivalent=True))
output = ROOT / 'state/analysis/P2_pin_table_raw/harness_audit.json'
output.parent.mkdir(parents=True, exist_ok=True)
if output.exists():
    raise ValueError('Preserve earlier audit; use a new evidence name if sources change')
output.write_text(json.dumps(dict(baseline='4778ced', changes='Dependency list entries only',
                                  files=records), indent=2) + '\n')
print('PASS: eight legacy harness modules preserve all non-dependency syntax')
