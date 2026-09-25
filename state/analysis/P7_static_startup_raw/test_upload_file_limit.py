# Proves inherited Linux file-size limits against the retained loader's exact bytes.
# Separates harmless host copy behavior from uploader validation or target authority.
# Four bounded child/descendant cases use owned RAM scratch and a read-only source.
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'state/analysis/P2_ui_adc_probe_raw/root_capture_inputs/zephyr-arduino_uno_q_stm32u585xx.elf'
SIZE = 2303728
SHA256 = '39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd'
PREFIX_SHA256 = 'b6fced5c7a35d75e5e5b681ad9806510bb1f066f8097a198b9186d06867d50cf'

COPY_CHILD = r'''
import json, resource, shutil, signal, sys
signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
result = {'limit': list(resource.getrlimit(resource.RLIMIT_FSIZE)), 'copied': False, 'errno': None}
try:
    shutil.copyfile(sys.argv[1], sys.argv[2])
    result['copied'] = True
except OSError as error:
    result['errno'] = error.errno
print(json.dumps(result), flush=True)
raise SystemExit(0 if result['copied'] else 1)
'''

LIMIT_PARENT = r'''
import resource, subprocess, sys
limit = int(sys.argv[3])
resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))
child = subprocess.Popen([sys.executable, '-I', '-B', '-c', sys.argv[4], sys.argv[1], sys.argv[2]],
                         stdin=subprocess.DEVNULL)
try:
    code = child.wait(timeout=8)
except subprocess.TimeoutExpired:
    child.kill()
    child.wait(timeout=2)
    raise
raise SystemExit(code)
'''


@unittest.skipUnless(sys.platform.startswith('linux'), 'Linux RLIMIT_FSIZE required')
class InheritedLoaderCopyLimit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_bytes = SOURCE.read_bytes()
        if len(cls.source_bytes) != SIZE or hashlib.sha256(cls.source_bytes).hexdigest() != SHA256:
            raise AssertionError('Retained loader source does not match the frozen reference')
        if hashlib.sha256(cls.source_bytes[:1048576]).hexdigest() != PREFIX_SHA256:
            raise AssertionError('Retained loader prefix does not match D156 evidence')

    @classmethod
    def tearDownClass(cls):
        if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SHA256:
            raise AssertionError('Read-only loader source changed during host tests')

    def copy_with_limit(self, limit):
        with tempfile.TemporaryDirectory(prefix='sumox_file_limit_only_', dir='/dev/shm') as folder:
            target = Path(folder) / 'loader-copy.elf'
            argv = [sys.executable, '-I', '-B', '-c', LIMIT_PARENT,
                    str(SOURCE), str(target), str(limit), COPY_CHILD]
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, start_new_session=True)
            try:
                stdout, stderr = child.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child.communicate(timeout=2)
                self.fail('Owned copy process group exceeded its host timeout')
            self.assertEqual(stderr, b'')
            self.assertLess(len(stdout), 1024)
            report = json.loads(stdout)
            self.assertEqual(report['limit'], [limit, limit])
            copied = target.read_bytes()
            self.assertLessEqual(len(copied), limit)
            return child.returncode, report, copied

    def test_original_one_mib_limit_reproduces_the_exact_failed_prefix(self):
        code, report, copied = self.copy_with_limit(1048576)
        self.assertNotEqual(code, 0)
        self.assertFalse(report['copied'])
        self.assertEqual(report['errno'], 27)
        self.assertEqual(len(copied), 1048576)
        self.assertEqual(hashlib.sha256(copied).hexdigest(), PREFIX_SHA256)

    def test_exact_loader_size_limit_allows_complete_copy(self):
        code, report, copied = self.copy_with_limit(SIZE)
        self.assertEqual(code, 0)
        self.assertTrue(report['copied'])
        self.assertIsNone(report['errno'])
        self.assertEqual(len(copied), SIZE)
        self.assertEqual(hashlib.sha256(copied).hexdigest(), SHA256)

    def test_copy_one_byte_beyond_limit_fails_at_the_limit(self):
        code, report, copied = self.copy_with_limit(SIZE - 1)
        self.assertNotEqual(code, 0)
        self.assertFalse(report['copied'])
        self.assertEqual(report['errno'], 27)
        self.assertEqual(copied, self.source_bytes[:-1])

    def test_copy_one_byte_below_limit_succeeds(self):
        code, report, copied = self.copy_with_limit(SIZE + 1)
        self.assertEqual(code, 0)
        self.assertTrue(report['copied'])
        self.assertIsNone(report['errno'])
        self.assertEqual(hashlib.sha256(copied).hexdigest(), SHA256)


if __name__ == '__main__':
    unittest.main(verbosity=2)
