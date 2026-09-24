"""Run frozen D118 tests in an isolated RAM copy without reading collector bodies."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / 'state/analysis/P2_app_default_probe_raw/author'
PRODUCTION = ['tools/app_default_capture.py', 'tools/p0_capture.py',
              'tools/p0_mem_read.cfg', 'tools/recorder_heap.py']
TESTS = ['tests/tooling/test_app_default_capture.py', 'tests/tooling/test_recorder_heap.py',
         'tests/fixtures/recorder_heap_vectors.py']
INPUTS = ['state/analysis/P2_dump_fifo_raw/target_e820c0e1_bench-default/app.ino.elf',
          'state/analysis/P2_dump_fifo_raw/target_e820c0e1_bench-default/app.ino.elf-zsk.bin',
          'state/analysis/P2_ui_adc_probe_raw/root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.elf',
          'state/analysis/P2_ui_adc_probe_raw/root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.bin',
          'state/analysis/P2_app_default_probe_raw/fixture_tools/openocd.bin',
          'state/analysis/P2_app_default_probe_raw/fixture_tools/readelf.bin',
          'state/analysis/P2_app_default_probe_raw/fixture_tools/swj-dp.tcl',
          'state/analysis/P2_app_default_probe_contract.md']


def identity(path):
    value = path.read_bytes()
    return {'bytes': len(value), 'sha256': hashlib.sha256(value).hexdigest()}


def main():
    label = sys.argv[1]
    receipt = RAW / (label + '_summary.json')
    if receipt.exists():
        raise ValueError('Attempt receipt already exists')
    folder = Path(tempfile.mkdtemp(prefix='d118-author-', dir='/dev/shm'))
    manifest = {}
    for name in PRODUCTION + TESTS + INPUTS:
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
        manifest[name] = identity(target)
    for name in ('tools', 'tests', 'tests/fixtures', 'tests/tooling'):
        (folder / name / '__init__.py').touch()
    (RAW / (label + '_source_copy.json')).write_text(json.dumps(
        {'workspace': str(folder), 'files': manifest}, indent=2) + '\n')
    argv = [sys.executable, '-m', 'unittest', '-v', 'tests.tooling.test_app_default_capture',
            'tests.tooling.test_recorder_heap']
    start = time.time()
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TMPDIR='/dev/shm')
    result = subprocess.run(argv, cwd=folder, env=environment, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180)
    (RAW / (label + '_full.txt')).write_text(result.stdout)
    evidence = {'argv': argv, 'cwd': str(folder), 'returncode': result.returncode,
                'elapsed_seconds': time.time() - start, 'files': manifest,
                'output_sha256': hashlib.sha256(result.stdout.encode()).hexdigest(),
                'scope': 'Host fixtures only; exact opaque tool bytes are never executed; no board or MCU.'}
    receipt.write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2))
    print(result.stdout)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
