# Checks literal path-token substitution independently of the frozen public oracle.
# Rejects commands redirected away from the exact canonical requested build path.
# Run with python -B; synthetic host validation only, with existing I/O tripwires.
import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'state/analysis/P7_static_link_probe_raw'
BUILD = '/synthetic/@DATA_DIR@/build'
DATA = '/synthetic/data'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    policy = load('path_token_subject', RAW / 'static_policy.py')
    fixture = load('path_token_fixture', ROOT /
                   'state/analysis/P7_static_link_probe_test_draft/test_static_policy.py')
    reference = json.loads((RAW / 'static_reference.json').read_bytes())
    rows = []
    for literal in (True, False):
        envelope = fixture.public_envelope(reference, BUILD, DATA)
        if literal:
            replacements = {'BUILD_PATH': BUILD, 'DATA_DIR': DATA}
            for key, template in reference.items():
                value = re.sub(r'@(BUILD_PATH|DATA_DIR)@',
                               lambda match: replacements[match[1]], template)
                fixture.replace_property(envelope, key, value)
        for name in ('validate_preflight', 'validate_compile_result'):
            try:
                with fixture.io_tripwires():
                    getattr(policy, name)(json.dumps(envelope),
                                          build_path=BUILD, data_dir=DATA)
                actual = 'ACCEPT'
            except ValueError:
                actual = 'REJECT'
            expected = 'ACCEPT' if literal else 'REJECT'
            rows.append({'validator': name, 'literal_path': literal,
                         'expected': expected, 'actual': actual,
                         'pass': actual == expected})
    print(json.dumps({'build_path': BUILD, 'data_dir': DATA, 'cases': rows,
                      'passed': sum(row['pass'] for row in rows)}, indent=2))
    return 0 if all(row['pass'] for row in rows) else 1


if __name__ == '__main__':
    sys.exit(main())
