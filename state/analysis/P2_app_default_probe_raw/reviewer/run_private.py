"""Redirect the frozen author harness to reviewer receipts; host fixtures only."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
EXPECTED = {
    'tools/app_default_capture.py': 'beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1',
    'tests/tooling/test_app_default_capture.py': '0acddcc62b369f4ec725521b996a13622d6dcaf06fc1d89c592350d4aa0b4e15',
    'state/analysis/P2_app_default_probe_contract.md': 'fbf34f25d99392bd75cbaaaf666c8ae88d112075f5a3ba16c5210b0ba68d0bff',
    'state/analysis/P2_app_default_probe_raw/author/run_tests.py': 'd3dba189bc269f0e60020ddba12fe11f83bb503ee166a3bb4816881e44dfc460',
}

def main():
    for name, expected in EXPECTED.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    harness = ROOT / 'state/analysis/P2_app_default_probe_raw/author/run_tests.py'
    spec = importlib.util.spec_from_file_location('frozen_author_harness', harness)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT, module.RAW = ROOT, RAW
    sys.argv = [str(harness), 'private1']
    with (RAW / 'private1_harness_admission.json').open('x') as stream:
        json.dump({'sha256': EXPECTED, 'changes': 'ROOT/RAW receipt destinations only; exact frozen harness and cases unchanged',
                   'scope': 'Private WSL RAM fixture execution; no board/network/MCU'}, stream, indent=2)
    return module.main()

if __name__ == '__main__':
    raise SystemExit(main())
