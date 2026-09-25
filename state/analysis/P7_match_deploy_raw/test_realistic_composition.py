# Checks D183 Windows command capacity with actual source and realistic metadata.
# This source-aware reviewer supplement is not the independent specification oracle.
# Uses synthetic operation identities, no scope files, native processes or transport.
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
PARENT = '/home/arduino/sumox26_codex_build'
SOURCE = hashlib.sha256(b'D183 reviewer synthetic source identity').hexdigest()
BUILD = hashlib.sha256(b'D183 reviewer synthetic build identity').hexdigest()[:32]
RUN = hashlib.sha256(b'D183 reviewer synthetic run identity').hexdigest()[:32]
BOOT = '09876543-21fe-dcba-9876-543210fedcba'


def load_subject():
    spec = importlib.util.spec_from_file_location(
        'd183_reviewer_payload', ROOT / 'tools/match_payload.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def realistic_bindings():
    # Historical metadata only supplies nonrepetitive hashes/extents/directories.
    # It is never represented as current qualification or authorization.
    value = json.loads((ROOT / 'state/analysis/P7_static_startup_raw/'
                       'upload_bindings.json').read_text(encoding='utf-8'))
    sketch = PARENT + '/' + SOURCE + '/app'
    build = (PARENT + '/_app_builds/native-app-v1/' + SOURCE +
             '/match-immediate/' + BUILD)
    value.update(schema='fixed-match-upload-v1', run_id=RUN, source_sha256=SOURCE,
                 boot_id=BOOT, output=PARENT + '/match-' + SOURCE[:8] + '-' + RUN + '-upload')
    value['files']['raw']['path'] = build + '/build/app.ino.elf'
    value['files']['sketch']['path'] = build + '/build/app.ino.elf-zsk.bin'
    value['files']['exported'] = copy.deepcopy(value['files']['sketch'])
    value['files']['exported']['path'] = build + '/artifacts/app.ino.elf-zsk.bin'
    value['absent'] = value['absent'][:-3] + [sketch + '/sketch.' + suffix
                                           for suffix in ('yaml', 'yml', 'json')]
    return value


class RealisticCompositionTests(unittest.TestCase):
    def test_D183_actual_sources_and_nonrepetitive_metadata_fit_windows_bound(self):
        sources = {role: (ROOT / path).read_bytes() for role, path in {
            'helper': 'state/analysis/P7_static_link_probe_raw/static_remote.py',
            'support': 'state/analysis/P7_static_startup_raw/capture_remote.py',
            'upload': 'state/analysis/P7_static_startup_raw/upload_remote.py',
            'adapter': 'tools/match_upload.py'}.items()}
        prefixes = {
            'adb': ['C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/'
                    'adb/32.0.0/adb.exe', '-s', 'synthetic-target', 'shell', '-T'],
            'ssh': ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                    '-o', 'ConnectTimeout=10', 'arduino@synthetic.local']}
        subject, bound = load_subject(), realistic_bindings()
        with mock.patch.object(subprocess, 'Popen',
                               side_effect=AssertionError('Native execution forbidden')):
            for transport, prefix in prefixes.items():
                with self.subTest(transport=transport):
                    command = subject.build_command(sources, bound, SOURCE, BUILD, RUN, prefix)
                    units = len(subprocess.list2cmdline(
                        prefix + [shlex.join(command)]).encode('utf-16-le')) // 2 + 1
                    self.assertLessEqual(units, 30000)
                    print('REVIEWER_COMPOSITION ' + json.dumps(
                        {'transport': transport, 'utf16_units_including_nul': units,
                         'native_calls': 0}, sort_keys=True))


if __name__ == '__main__':
    unittest.main()
