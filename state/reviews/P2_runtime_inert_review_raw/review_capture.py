"""Independent bounded D104 capture guard/sequence probes; no subprocess permitted."""
from contextlib import ExitStack
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / 'tools')]
from tests.fixtures import recorder_heap_vectors
spec = importlib.util.spec_from_file_location('review_d104_capture', ROOT / 'tools/runtime_capture.py')
subject = importlib.util.module_from_spec(spec)
with mock.patch.object(subprocess, 'run', side_effect=AssertionError('No process during import')):
    spec.loader.exec_module(subject)

def diagnostic():
    # Literal declaration-order ABI, independent of the decoder's field list.
    report = [1,192,2,0,1000,1010,1020,1030,200000980,200000985,200000990,
              200001000,200000010,200000,0,20,30,200000,0,1,0,1,0,0,0,0,0,
              15,31,0,0,0,0,1,4,200001,800004,200001,3000000,0,0,0]
    stack = [1,0x20002000,32768,0,0x20009000,3000000,28672,0]
    return struct.pack('<58I', *([4] + report + [0]*6 + stack + [4]))

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.process = mock.patch.object(subprocess, 'run', side_effect=AssertionError('No process'))
        self.process.start(); self.addCleanup(self.process.stop)
        self.temporary = tempfile.TemporaryDirectory(prefix='d104-capture-review-')
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)

    def capture(self):
        value = subject.Capture(self.folder, subject.initial_report())
        value.identities_verified = True
        value.binary_size = 124996
        value.report.update(flash_identity_verified=True,
            layout={'bss_size':166856,'symbols':{'runtimeDiagnostics':{'offset':166624,'size':232}}},
            extension={'bss_address':0x20020000})
        return value

    def test_literal_positive_and_failed_semantics_are_separate(self):
        value = subject.decode_diagnostics(diagnostic())
        self.assertEqual(value['acceptance'], {'passed':True,'failures':[]})
        words = list(struct.unpack('<58I', diagnostic()))
        words[3], words[4] = 3, 11
        failed = subject.decode_diagnostics(struct.pack('<58I', *words))
        self.assertFalse(failed['acceptance']['passed'])
        self.assertEqual(failed['report']['failure'], 11)

    def test_command_whitelist_refuses_halt_reset_write_and_arbitrary_exec(self):
        capture = self.capture()
        for argv in ([str(subject.OPENOCD),'-c','halt'],
                     [str(subject.OPENOCD),'-c','reset'],
                     [str(subject.OPENOCD),'-c','mww 0x20000000 1'],
                     ['sh','-c','true'],[str(subject.READELF),'-sW','/other.elf']):
            with self.subTest(argv=argv), self.assertRaises(ValueError): capture.run(argv)
        self.assertEqual(capture.report['commands'], [])
        capture.identities_verified = False
        with self.assertRaises(ValueError): capture.run([subject.OPENOCD,'--version'])

    def test_unknown_misaligned_or_overlarge_read_purposes_never_invoke_run(self):
        capture = self.capture()
        tests = [('node-4',0x20002000,196,'ram'), ('pool-1-16',0x20013890,16384,'ram'),
                 ('pool-1-00',0x20013894,16384,'ram'), ('pool-1-00',0x20013890,16385,'ram'),
                 ('heap-descriptor-first',0x20001130,24,'ram'),
                 ('diagnostics-first',0x20020000,232,'ram'),
                 ('loader',0x08000000,263680,'loader'),
                 ('sketch',0x08100000,124996,'sketch'),
                 ('loader-00',0x08000000,65535,'loader'),
                 ('sketch-02',0x08120000,1,'sketch'),
                 ('node-1',True,196,'ram'), ('node-1',0x20002000,True,'ram')]
        with mock.patch.object(capture,'run') as run:
            for args in tests:
                with self.subTest(args=args), self.assertRaises(ValueError): capture.read(*args)
            run.assert_not_called()
        self.assertEqual(capture.read_count,0)

    def test_deployed_identity_and_limits_are_checked_before_each_read(self):
        capture = self.capture()
        with mock.patch.object(capture,'run') as run:
            capture.report['flash_identity_verified'] = False
            with self.assertRaises(ValueError): capture.read('llext-list',subject.LIST_ADDRESS,8)
            capture.report['flash_identity_verified'] = True
            capture.read_count = 48
            with self.assertRaises(ValueError): capture.read('llext-list',subject.LIST_ADDRESS,8)
            capture.read_count = 0; capture.read_bytes = 2097152-7
            with self.assertRaises(ValueError): capture.read('llext-list',subject.LIST_ADDRESS,8)
            run.assert_not_called()

    def test_failed_read_is_counted_and_same_purpose_cannot_retry(self):
        capture = self.capture()
        with mock.patch.object(capture,'run',side_effect=ValueError('controlled failure')) as run:
            with self.assertRaises(ValueError): capture.read('llext-list',subject.LIST_ADDRESS,8)
            self.assertEqual((capture.read_count,capture.read_bytes),(1,8))
            self.assertIsNone(capture._read_command)
            with self.assertRaises(ValueError): capture.read('llext-list',subject.LIST_ADDRESS,8)
            self.assertEqual(run.call_count,1)

    def test_precomputed_budget48_accepts_and49_refuses_before_commands(self):
        loader = self.folder/'loader.bin'; loader.write_bytes(bytes(263680))
        elf = self.folder/'runtime_inert.ino.elf'; elf.write_bytes(b'ELF fixture')
        binary = self.folder/'runtime_inert.ino.elf-zsk.bin'
        def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
        for size, accepted in ((124996,True),(131073,False)):
            binary.write_bytes(bytes(size))
            capture = subject.Capture(self.folder,subject.initial_report())
            with mock.patch.multiple(subject,ARTIFACT_DIR=self.folder,ELF_PATH=elf,
                ELF_HASH=digest(elf),BINARY_HASH=digest(binary),LOADER=loader,
                EXPECTED_HASHES={loader:digest(loader)}):
                def version(argv,attach=False):
                    capture.report['commands'].append({'stdout':'fixture','stderr':''}); return 'fixture'
                with mock.patch.object(capture,'run',side_effect=version) as run:
                    if accepted:
                        subject.check_identities(capture,str(self.folder))
                        self.assertEqual(capture.report['maximum_read_budget'],
                            {'reads':48,'bytes':914080,'extension_nodes':3})
                        self.assertEqual(run.call_count,2)
                    else:
                        with self.assertRaises(ValueError): subject.check_identities(capture,str(self.folder))
                        run.assert_not_called(); self.assertFalse(capture.identities_verified)

    def test_unset_artifact_pins_refuse_without_process_or_reads(self):
        capture = self.capture()
        with mock.patch.multiple(subject,ARTIFACT_DIR=None,ELF_HASH=None,BINARY_HASH=None):
            with self.assertRaises(ValueError): subject.check_identities(capture,str(self.folder))
        self.assertEqual(capture.report['commands'],[])

    def test_extension_three_node_bound_never_reads_fourth(self):
        calls=[]; addresses=[0x20001000+i*200 for i in range(4)]
        class Fixture:
            report={'flash_identity_verified':True}
            def read(self,label,address,size):
                calls.append(label)
                if label=='llext-list': return struct.pack('<II',addresses[0],addresses[-1])
                index=int(label[-1])-1
                blob=bytearray(196); struct.pack_into('<I',blob,0,addresses[index+1])
                blob[4:10]=b'other\0'; return bytes(blob)
        with self.assertRaises(ValueError): subject.find_bss(Fixture(),166856)
        self.assertEqual(calls,['llext-list','node-1','node-2','node-3'])

    def test_complete_capture_requires_stable_diagnostics_and_descriptor(self):
        pool=recorder_heap_vectors.all_free()
        descriptor=struct.pack('<6I',subject.HEAP_BASE,subject.HEAP_BASE,262144,0,0,0)
        for changed in (None,'diagnostics-last','heap-descriptor-last'):
            with tempfile.TemporaryDirectory(dir=self.folder) as temporary:
                calls=[]
                class Fixture:
                    folder=Path(temporary)
                    report={}
                    def read(self,label,address,size):
                        calls.append(label)
                        if label.startswith('diagnostics'): data=diagnostic()
                        elif label.startswith('heap'): data=descriptor
                        else:
                            index=int(label[-2:]); data=pool[index*16384:(index+1)*16384]
                        if label==changed: data=data[:-1]+bytes([data[-1]^1])
                        return data
                fixture=Fixture()
                if changed:
                    with self.assertRaises(ValueError): subject.capture_values(fixture,0x20020000,
                        {'runtimeDiagnostics':{'offset':166624,'size':232}})
                else:
                    subject.capture_values(fixture,0x20020000,
                        {'runtimeDiagnostics':{'offset':166624,'size':232}})
                    self.assertEqual(len(calls),36)
                    self.assertTrue(fixture.report['diagnostics']['acceptance']['passed'])

buffer=io.StringIO()
suite=unittest.defaultTestLoader.loadTestsFromTestCase(GuardTests)
result=unittest.TextTestRunner(stream=buffer,verbosity=2).run(suite)
record={'scope':'Local controlled capture guards; subprocess globally prohibited per test',
        'source_sha256':hashlib.sha256((ROOT/'tools/runtime_capture.py').read_bytes()).hexdigest(),
        'tests':result.testsRun,'successful':result.wasSuccessful(),'output':buffer.getvalue()}
(RAW/'capture_guards.json').write_text(json.dumps(record,indent=2)+'\n')
print(buffer.getvalue())
raise SystemExit(0 if result.wasSuccessful() else 1)
