# Derives upload-loader coverage from the frozen D154 fixture and its assertions.
# Changes only entry selection and the two approved child file-limit expectations.
# Frozen inherited cases plus four additions run only after the new oracle freeze.
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('frozen_upload_contract', HERE / 'test_upload_remote.py')
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


class UploadLoaderContract(legacy.UploadContract):
    def upload(self, **kwargs):
        options = dict(fs_root=self.root, executor=self.execute, clock=self.clock)
        options.update(kwargs)
        return self.subject.upload_loader(self.helper, self.support, **options)

    def fake_popen(self, argv, **kwargs):
        self.assertEqual(argv, legacy.ARGV)
        self.assertEqual(kwargs['env'], legacy.ENV)
        self.assertEqual(kwargs['cwd'], '/home/arduino')
        self.assertFalse(kwargs['shell'])
        self.assertTrue(kwargs['start_new_session'])
        self.assertEqual(kwargs['stdin'], subprocess.DEVNULL)
        self.assertIs(kwargs['preexec_fn'], self.subject.limit_upload_files)
        with mock.patch.object(self.support.resource, 'setrlimit') as limit:
            kwargs['preexec_fn']()
            limit.assert_called_once_with(self.support.resource.RLIMIT_FSIZE, (2303728, 2303728))
        self.assertTrue((self.output / 'upload_attempt.json').exists())
        self.assertTrue((self.output / 'upload_command.json').exists())
        for stream, raw in ((kwargs['stdout'], self.stdout), (kwargs['stderr'], self.stderr)):
            if isinstance(stream, int):
                os.write(stream, raw)
            else:
                stream.write(raw)
        return self.child

    def test_stderr_exactly_one_mib_is_rejected(self):
        self.stderr = b'x' * 1048576
        self.failed()

    def test_both_streams_just_below_one_mib_remain_accepted(self):
        self.stdout, self.stderr = b'x' * 1048575, b'y' * 1048575
        report = self.upload()
        self.assert_report(report, 'UPLOADED')
        self.assertEqual(len(report['stdout']), 1048575)
        self.assertEqual(len(report['stderr']), 1048575)

    def test_frozen_d153_limit_remains_one_mib(self):
        with mock.patch.object(self.support.resource, 'setrlimit') as limit:
            self.support.limit_child_output()
        limit.assert_called_once_with(self.support.resource.RLIMIT_FSIZE, (1048576, 1048576))

    def test_new_limit_equals_largest_pinned_copy_extent(self):
        bindings = json.loads((HERE / 'upload_bindings.json').read_text())
        copied = {role: bindings['files'][role]['bytes']
                  for role in ('loader', 'sketch', 'flash_config')}
        self.assertEqual(copied, {'loader': 2303728, 'sketch': 93096, 'flash_config': 680})
        with mock.patch.object(self.support.resource, 'setrlimit') as limit:
            self.subject.limit_upload_files()
        largest = max(copied.values())
        limit.assert_called_once_with(self.support.resource.RLIMIT_FSIZE, (largest, largest))


if __name__ == '__main__':
    unittest.main(verbosity=2)
