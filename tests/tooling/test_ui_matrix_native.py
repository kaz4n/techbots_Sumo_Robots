# Tests the actual D088 native adapter with contract-derived device and CMSIS substitutes.
# Public declarations and frozen contract are the only sources of expected behavior.
# Every compile and process receipt is retained, including failures, under state/analysis.
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import struct
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'tests/fixtures/ui_matrix_native'
RAW = ROOT / 'state/analysis/P2_matrix_raw/author'


class NativeMatrixTests(unittest.TestCase):
    @classmethod
    def command(cls, argv):
        result = subprocess.run([str(item) for item in argv], text=True, capture_output=True)
        cls.command_count += 1
        receipt = {'argv': [str(item) for item in argv], 'returncode': result.returncode,
                   'stdout': result.stdout, 'stderr': result.stderr,
                   'native_source_sha256': cls.source_sha}
        (RAW / f'native_{time.time_ns()}.json').write_text(json.dumps(receipt, indent=2)+'\n')
        if result.returncode:
            raise AssertionError(json.dumps(receipt, indent=2))
        return result

    @classmethod
    def setUpClass(cls):
        RAW.mkdir(parents=True, exist_ok=True)
        if not shutil.which('g++'):
            raise RuntimeError('Run this native compiler suite with Linux/WSL python3 and g++.')
        cls.command_count = 0
        cls.scenario_count = 0
        cls.source_sha = hashlib.sha256((ROOT/'src/hal/ui_matrix_unoq.cpp').read_bytes()).hexdigest()
        cls.temp = tempfile.TemporaryDirectory(prefix='sumo-matrix-spec-')
        cls.stage = Path(cls.temp.name)
        files = [ROOT/'src/hal/ui_matrix_unoq.cpp', ROOT/'src/hal/ui_matrix_unoq.h',
                 ROOT/'src/hal/ui_display.h', ROOT/'src/config.h', Path(__file__),
                 ROOT/'tests/test_ui_display.cpp', ROOT/'state/analysis/P2_matrix_contract.md']
        files += [p for p in FIXTURE.rglob('*') if p.is_file()]
        (RAW/f'native_freeze_{time.time_ns()}.json').write_text(json.dumps({
            'basis':'Frozen public D088 contract, no implementation body read for expectations',
            'sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        },indent=2)+'\n')
        base = ['g++','-std=c++17','-Wall','-Wextra','-Wpedantic','-Werror',
                '-fno-exceptions','-fno-rtti','-DARDUINO_ARCH_ZEPHYR',
                '-I',FIXTURE,'-I',ROOT/'src']
        cls.command([*base,'-fsyntax-only',FIXTURE/'native_cases.cc'])
        cls.binaries=[]
        for name, flags in [('plain',[]),('san',['-fsanitize=address,undefined',
                                             '-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
            binary=cls.stage/name
            cls.command([*base,*flags,FIXTURE/'native_cases.cc',
                         ROOT/'src/hal/ui_matrix_unoq.cpp','-o',binary])
            cls.binaries.append(binary)

    @classmethod
    def tearDownClass(cls):
        (RAW/f'native_summary_{time.time_ns()}.json').write_text(json.dumps({
            'command_count':cls.command_count,'successful_scenarios':cls.scenario_count,
            'source_sha256':cls.source_sha,'variants':['plain','address+undefined'],
            'scope':'Actual adapter CPP, controlled native/device/CMSIS calls; no board or optical claims'
        },indent=2)+'\n')
        cls.temp.cleanup()

    def execute(self,*args):
        for binary in self.binaries:
            with self.subTest(binary=binary.name,args=args):
                result=self.command([binary,*args])
                self.assertTrue(result.stdout.startswith('PASS scenario='))
                type(self).scenario_count += 1

    def test_b13_constructor_destructor_and_uninitialized_submit_have_no_io(self):
        self.execute(0)

    def test_b13_both_explicit_grants_required_and_faults_do_not_consume_owner(self):
        for grant in range(3): self.execute(1,grant)

    def test_b13_setup_rejects_unprivileged_and_interrupt_context_before_mutation(self):
        for context in (3,4): self.execute(1,context)

    def test_b13_null_device_never_calls_readiness_or_native_writes(self):
        self.execute(1,5)

    def test_b13_unready_device_never_calls_native_writes(self):
        self.execute(1,6)

    def test_b13_success_claim_is_unconfirmed_and_second_owner_cannot_write(self):
        self.execute(2)

    def test_b13_repeat_begin_latches_fault_without_reinitialization(self):
        self.execute(3)

    def test_b13_destruction_never_releases_boot_lifetime_owner(self):
        self.execute(4)

    def test_b13_postsetup_wrong_context_faults_and_cannot_recover(self):
        for context in (0,1): self.execute(5,context)

    def test_b13_every_frame_byte_is_checked_before_native_mutation(self):
        for index in range(104):
            for value in (8,255): self.execute(6,index,value,0)

    def test_b13_every_frame_byte_is_checked_even_when_throttled(self):
        for index in range(104):
            for value in (8,255): self.execute(6,index,value,1)

    def test_b13_first_submit_and_exact_throttle_boundary_no_catchup(self):
        self.execute(7,1234,0)

    def test_b13_throttle_boundary_survives_uint32_wrap(self):
        self.execute(7,4294967280,0)

    def test_b13_initial_blank_and_submissions_restore_masked_caller_exactly(self):
        self.execute(7,1234,1)

    def test_b13_privileged_thread_other_control_bits_do_not_false_reject(self):
        self.execute(8)


class MatrixCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/'state/analysis/P2_matrix_runtime_capture.py'
        spec=importlib.util.spec_from_file_location('matrix_capture_under_test',path)
        cls.capture=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.capture)
        RAW.mkdir(parents=True,exist_ok=True)
        (RAW/f'capture_freeze_{time.time_ns()}.json').write_text(json.dumps({
            'wrapper_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'Pure host parsing/arithmetic/bounded identity fixtures; no board calls'
        },indent=2)+'\n')

    def payload(self,**changes):
        values=dict(magic=0x55494d58,version=1,initialized=1,submissions=42,failures=0,
                    scene=5,last_status=2,last_render=0,last_us=0xffffffff,max_call_us=88)
        values.update(changes)
        return struct.pack('<10I',*values.values())

    def test_b13_capture_uint32_counter_exact_boundaries_and_wrap(self):
        for first,second,expected in [(0,1,1),(0,0x7fffffff,0x7fffffff),
                                      (0xffffffff,0,1),(0xfffffff0,0x20,48)]:
            self.assertEqual(self.capture.analyze_counter(first,second),
                             dict(first=first,second=second,advance=expected))
        for first,second in [(0,0),(1,0),(0,0x80000000),(0,0xffffffff),
                             (-1,0),(0,0x100000000),(True,2),(0,False),(0,1.0),('0',1)]:
            with self.subTest(first=first,second=second),self.assertRaises(ValueError):
                self.capture.analyze_counter(first,second)

    def test_b13_capture_exact_little_endian_identity_and_all_scenes(self):
        for scene in range(12):
            result=self.capture.decode_snapshot(self.payload(scene=scene))
            self.assertEqual(result,dict(magic=0x55494d58,version=1,initialized=1,
                submissions=42,failures=0,scene=scene,last_status=2,last_render=0,
                last_us=0xffffffff,max_call_us=88))
        for count in (0,0xffffffff):
            self.assertEqual(self.capture.decode_snapshot(self.payload(submissions=count))['submissions'],count)

    def test_b13_capture_rejects_wrong_shape_identity_and_unsuccessful_status(self):
        for value in (b'',bytes(39),bytes(41),bytearray(self.payload()),'x'*40,None):
            with self.subTest(value=type(value)),self.assertRaises(ValueError):
                self.capture.decode_snapshot(value)
        for field,values in [('magic',[0,0x584d4955]),('version',[0,2]),
                ('initialized',[0,2]),('failures',[1,0xffffffff]),('scene',[12,0xffffffff]),
                ('last_status',[0,1,3,9]),('last_render',[1,0xffffffff])]:
            for value in values:
                with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                    self.capture.decode_snapshot(self.payload(**{field:value}))

    def test_b13_capture_read_snapshot_requests_exact_40_bytes(self):
        read=mock.Mock(return_value=self.payload())
        capture=SimpleNamespace(read=read)
        result=self.capture.read_snapshot(capture,0x20010000,'test-label')
        read.assert_called_once_with('test-label',0x20010000,40)
        self.assertEqual(result['address'],0x20010000)
        self.assertEqual(result['values']['submissions'],42)
        self.assertGreaterEqual(result['monotonic_end'],result['monotonic_start'])

    def test_b13_capture_short_deadline_cannot_trigger_second_read_or_sleep(self):
        capture=SimpleNamespace(report={},deadline=102.0,read=mock.Mock(return_value=self.payload()))
        helper=SimpleNamespace(ram_range=mock.Mock(),in_range=mock.Mock(return_value=True))
        with mock.patch.object(self.capture.time,'monotonic',return_value=100.0),\
                mock.patch.object(self.capture.time,'sleep') as sleep,\
                self.assertRaises(ValueError):
            self.capture.observe_counter(helper,capture,0x20000000)
        self.assertEqual(capture.read.call_count,1);sleep.assert_not_called()
        self.assertNotIn('counter',capture.report)

    def test_b13_capture_two_bounded_reads_report_only_modular_advance(self):
        capture=SimpleNamespace(report={},deadline=200.0,
            read=mock.Mock(side_effect=[self.payload(submissions=0xfffffff0),self.payload(submissions=0x20)]))
        helper=SimpleNamespace(ram_range=mock.Mock(),in_range=mock.Mock(return_value=True))
        with mock.patch.object(self.capture.time,'monotonic',return_value=100.0),\
                mock.patch.object(self.capture.time,'sleep') as sleep:
            self.capture.observe_counter(helper,capture,0x20000000)
        self.assertEqual(capture.read.call_count,2);sleep.assert_called_once_with(3.0)
        self.assertEqual(capture.report['counter']['advance'],48)
        self.assertNotIn('optical',capture.report);self.assertNotIn('wcet',capture.report)

    def test_b13_capture_initial_dump_requires_unique_bounded_hashed_exact_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'01-llext-list.bin';path.write_bytes(b'abcdefgh')
            record=dict(address=0x20001000,size=8,region='ram',file=path.name,
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest())
            capture=SimpleNamespace(folder=Path(folder),report={'reads':[record]})
            helper=SimpleNamespace(no_symlinks=mock.Mock())
            self.assertEqual(self.capture.initial_dump(helper,capture,0x20001000,8,
                             r'\d{2}-llext-list\.bin'),b'abcdefgh')
            for records in ([],[record,record],[record]*17):
                capture.report['reads']=records
                with self.assertRaises(ValueError):
                    self.capture.initial_dump(helper,capture,0x20001000,8,r'\d{2}-llext-list\.bin')
            capture.report['reads']=[record];path.write_bytes(b'ABCDEFGH')
            with self.assertRaises(ValueError):
                self.capture.initial_dump(helper,capture,0x20001000,8,r'\d{2}-llext-list\.bin')

    def test_b13_capture_extension_confirmation_checks_identity_fields(self):
        node=bytes(range(196));head=b'abcdefgh'
        for offset in (0,19,32,35,92,95):
            changed=bytearray(node);changed[offset]^=1
            capture=SimpleNamespace(report={'extension':{'node_address':0x20002000}},
                                    read=mock.Mock(side_effect=[head,bytes(changed)]))
            helper=SimpleNamespace(LIST_ADDRESS=0x20001000)
            with mock.patch.object(self.capture,'initial_dump',side_effect=[head,node]),\
                    self.assertRaises(ValueError):
                self.capture.confirm_extension(helper,capture)
            self.assertNotIn('extension_confirmed_after_counters',capture.report)
        capture=SimpleNamespace(report={'extension':{'node_address':0x20002000}},
                                read=mock.Mock(side_effect=[head,node]))
        with mock.patch.object(self.capture,'initial_dump',side_effect=[head,node]):
            self.capture.confirm_extension(helper,capture)
        self.assertTrue(capture.report['extension_confirmed_after_counters'])


if __name__=='__main__':
    unittest.main(verbosity=2)
