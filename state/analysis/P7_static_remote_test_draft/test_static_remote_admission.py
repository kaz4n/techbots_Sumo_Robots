# Tests bounded claim decoding and descriptor stability for rejected file sizes.
# Preserves the original frozen suite and derives all expectations from its contract.
# Execute only after the separate admission freeze and coordinator host-test GO.
import base64
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest import mock

import test_static_remote as fixture


@unittest.skipUnless(sys.platform.startswith('linux'), 'Actual Linux descriptor fixtures required')
class StaticRemoteAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        freeze = json.loads(Path(__file__).with_name('freeze_admission.json').read_text())
        if freeze.get('status') != 'FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Admission supplement is not frozen')
        for name, expected in freeze['inputs_sha256'].items():
            if hashlib.sha256((fixture.ROOT/name).read_bytes()).hexdigest() != expected:
                raise RuntimeError('Admission supplement input changed: '+name)
        fixture.StaticRemoteContract.setUpClass.__func__(cls)

    setUp = fixture.StaticRemoteContract.setUp
    logical = fixture.StaticRemoteContract.logical
    invoke = fixture.StaticRemoteContract.invoke
    action = fixture.StaticRemoteContract.action
    succeed = fixture.StaticRemoteContract.succeed
    rejected = fixture.StaticRemoteContract.rejected
    make_claim = fixture.StaticRemoteContract.make_claim
    materialize_artifacts = fixture.StaticRemoteContract.materialize_artifacts

    def test_deep_claim_json_is_bad_request_for_every_claim_action(self):
        self.make_claim()
        before = sorted(str(path.relative_to(self.root)) for path in self.root.rglob('*'))
        nested = ('['*3000+'0'+']'*3000, '{"x":'*3000+'0'+'}'*3000)
        for raw in nested:
            claim = base64.b64encode(raw.encode('ascii')).decode('ascii')
            cases = [('absent', [claim]), ('artifacts', [claim]),
                     ('layout', [claim, self.v]),
                     ('read', [claim, 'app.ino.elf', '0', '8', '0'*64]),
                     ('postcheck', [claim, self.m])]
            for action, arguments in cases:
                with self.subTest(action=action, prefix=raw[:8]):
                    self.assertEqual(self.rejected(action, *arguments, code='BAD_REQUEST'), {})
        self.assertEqual(sorted(str(path.relative_to(self.root)) for path in self.root.rglob('*')), before)

    def prepare_size(self, size):
        handle = self.make_claim()
        self.materialize_artifacts()
        target = self.logical(self.f.paths()[1]+'/app.ino.elf')
        with target.open('wb') as output:
            output.truncate(size)
        return handle, target

    @staticmethod
    def identity(info):
        return dict(device=info.st_dev, inode=info.st_ino, bytes=info.st_size,
                    mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns)

    def fd_names(self, fd, target):
        try:
            return os.readlink('/proc/self/fd/'+str(fd)) == str(target)
        except OSError:
            return False

    def assert_observed_size(self, size, state):
        handle, target = self.prepare_size(size)
        initial, calls = target.stat(), []
        original_fstat, original_read = os.fstat, os.read
        def observed(fd):
            info = original_fstat(fd)
            if self.fd_names(fd, target):
                calls.append(info)
            return info
        def unread(fd, count):
            self.assertFalse(self.fd_names(fd, target), 'Rejected file sizes must not read contents')
            return original_read(fd, count)
        with mock.patch.object(os, 'fstat', observed), mock.patch.object(os, 'read', unread):
            data = self.rejected('artifacts', handle, code='ARTIFACT_SET')
        self.assertTrue(calls, 'Size admission must obtain real metadata through the opened descriptor')
        self.assertEqual(data['files']['build/app.ino.elf'],
                         dict(state=state, identity=self.identity(initial), sha256=None))

    def test_empty_records_require_open_descriptor_metadata(self):
        self.assert_observed_size(0, 'empty')

    def test_oversize_records_require_open_descriptor_metadata(self):
        self.assert_observed_size(16777217, 'oversize')

    def assert_replacement(self, size):
        handle, target = self.prepare_size(size)
        initial, fired = target.stat(), []
        original = os.fstat
        def observed(fd):
            info = original(fd)
            if not fired and self.fd_names(fd, target):
                fired.append(True)
                replacement = target.with_name(target.name+'.replacement')
                with replacement.open('wb') as output:
                    output.truncate(size)
                os.replace(replacement, target)
            return info
        with mock.patch.object(os, 'fstat', observed):
            data = self.rejected('artifacts', handle, code='ARTIFACT_SET')
        self.assertTrue(fired, 'Mutation seam must fire after the first real descriptor observation')
        self.assertEqual(data['files']['build/app.ino.elf'],
                         dict(state='unstable', identity=self.identity(initial), sha256=None))

    def test_empty_replacement_is_unstable_with_first_descriptor_identity(self):
        self.assert_replacement(0)

    def test_oversize_replacement_is_unstable_with_first_descriptor_identity(self):
        self.assert_replacement(16777217)


if __name__ == '__main__':
    unittest.main()
