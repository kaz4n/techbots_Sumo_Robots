# Tests D114's public pinned decoder and bounded passive collector independently.
# Literal little-endian fixtures derive from the enabled debug ABI, not decoder constants.
# Synthetic bytes and commands establish software behavior only; no board is contacted.
import builtins
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import copy
import hashlib
import importlib
import json
import io
import os
from pathlib import Path
import struct
import re
import subprocess
import sys
import time
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
SIZE, REPORT, CAPTURES, STRIDE = 9892, 16, 148, 76
U32, HALF = 0xffffffff, 0x80000000
PAIR_KEYS = {'schema_version','first_sha256','second_sha256','byte_identical',
             'snapshots','frozen','acquisition','physical_acceptance'}
REPORT_KEYS = {'phase','fault','fresh','clock_fault','counter_saturated','sample_seen',
               'last_read_accepted','decode_matches_sample','setup','sample','decoded',
               'captured_samples','not_due','missed_releases','setup_timing',
               'read_timing','poll_timing'}


def sample(raw=0, start=0, end=0, sequence=0, status=0, shutdown=0, valid=1):
    return dict(status=status,shutdown=shutdown,raw=raw,started_us=start,
                completed_us=end,sequence=sequence,valid=valid)


def decoded(value, qualification=2, explicit_values=1, contract_valid=1, presence=3, level=0, mask=0):
    return {'qualification':qualification,'candidate_mask':mask,'evidence':{
        'explicit_values':explicit_values,'contract_valid':contract_valid,'presence':presence,
        'level':level,'raw':value['raw'],'sequence':value['sequence'],
        'started_us':value['started_us'],'completed_us':value['completed_us']}}


def timing(calls=0, measured=0, last=0, maximum=0, valid=0):
    return dict(calls=calls,measured_calls=measured,last_us=last,maximum_us=maximum,last_valid=valid)


def put_sample(blob, offset, value):
    struct.pack_into('<BBHIIIB3x',blob,offset,*[value[key] for key in
        ('status','shutdown','raw','started_us','completed_us','sequence','valid')])


def put_decoded(blob, offset, value):
    evidence=value['evidence']
    struct.pack_into('<B3xBBBBH2xIIIB3x',blob,offset,value['qualification'],
        *[evidence[key] for key in ('explicit_values','contract_valid','presence','level','raw',
                                   'sequence','started_us','completed_us')],value['candidate_mask'])


def put_timing(blob, offset, value):
    struct.pack_into('<IIIIB3x',blob,offset,*[value[key] for key in
        ('calls','measured_calls','last_us','maximum_us','last_valid')])


def encode_report(blob, report):
    struct.pack_into('<8B',blob,REPORT,*[report[key] for key in
        ('phase','fault','fresh','clock_fault','counter_saturated','sample_seen',
         'last_read_accepted','decode_matches_sample')])
    struct.pack_into('<3B',blob,REPORT+8,*[report['setup'][key] for key in ('status','shutdown','ready')])
    put_sample(blob,REPORT+12,report['sample'])
    put_decoded(blob,REPORT+32,report['decoded'])
    struct.pack_into('<III',blob,REPORT+60,report['captured_samples'],report['not_due'],report['missed_releases'])
    for name,offset in (('setup_timing',72),('read_timing',92),('poll_timing',112)):
        put_timing(blob,REPORT+offset,report[name])


def encode_capture(blob, index, record):
    offset=CAPTURES+index*STRIDE
    put_sample(blob,offset,record['sample'])
    put_decoded(blob,offset+20,record['decoded'])
    struct.pack_into('<7I',blob,offset+48,*[record[key] for key in
        ('call_started_us','call_returned_us','poll_closed_us','source_us','read_us','poll_us','missed_before')])


def complete_fixture(count=128, start=100, misses=None, not_due=0):
    blob=bytearray(SIZE)
    records=[]
    misses=[0]*count if misses is None else misses
    for index in range(count):
        started=(start+2)&U32
        value=sample(0 if index%2==0 else 16383,started,(started+10)&U32,index+1)
        read_us,poll_us=20+index%5,30+index%7
        record=dict(sample=value,decoded=decoded(value),call_started_us=start,
                    call_returned_us=(start+read_us)&U32,poll_closed_us=(start+poll_us)&U32,
                    source_us=10,read_us=read_us,poll_us=poll_us,missed_before=misses[index])
        records.append(record)
        encode_capture(blob,index,record)
        if index+1<count: start=(started+1000*(1+misses[index+1]))&U32
    latest=records[-1] if records else None
    value=copy.deepcopy(latest['sample']) if latest else sample(status=1,valid=0)
    display=copy.deepcopy(latest['decoded']) if latest else decoded(value,0,0,1,1)
    report=dict(phase=3 if count==128 else 2,fault=0,fresh=0,clock_fault=0,
                counter_saturated=int(not_due+count>U32),sample_seen=int(count>0),
                last_read_accepted=int(count>0),decode_matches_sample=int(count>0),
                setup={'status':0,'shutdown':0,'ready':1},sample=value,decoded=display,
                captured_samples=count,not_due=not_due,missed_releases=min(U32,sum(misses)),
                setup_timing=timing(1,1,7,7,1),
                read_timing=timing(count,count,latest['read_us'] if latest else 0,
                                   max((r['read_us'] for r in records),default=0),int(count>0)),
                poll_timing=timing(min(U32,count+not_due),count,latest['poll_us'] if latest else 0,
                                   max((r['poll_us'] for r in records),default=0),int(count>0)))
    encode_report(blob,report)
    return blob,report,records


def diagnostic_fixture(phase=4, fault=3, count=0):
    blob,report,records=complete_fixture(count)
    report.update(phase=phase,fault=fault,clock_fault=int(fault==7))
    if phase in (0,1) or fault==3:
        report['setup']={'status':4 if fault==3 else 1,'shutdown':0,'ready':0}
        if phase in (0,1): report['setup_timing']=timing()
    encode_report(blob,report)
    return blob,report,records


class UiAdcDecoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module=importlib.import_module('ui_adc_capture')

    def pair(self, first, second=None):
        first=bytes(first)
        second=first if second is None else bytes(second)
        result=self.module.decode_runner_pair(first,second)
        self.assertEqual(set(result),PAIR_KEYS)
        self.assertEqual(result['schema_version'],1)
        self.assertEqual(result['first_sha256'],hashlib.sha256(first).hexdigest())
        self.assertEqual(result['second_sha256'],hashlib.sha256(second).hexdigest())
        self.assertIs(result['byte_identical'],first==second)
        self.assertIs(result['physical_acceptance'],False)
        self.assertEqual(len(result['snapshots']),2)
        for snapshot in result['snapshots']:
            self.assertEqual(set(snapshot),{'valid','errors','report','captures'})
            self.assertEqual(set(snapshot['report']),REPORT_KEYS)
            errors=[(error['code'],error['path']) for error in snapshot['errors']]
            self.assertEqual(len(errors),len(set(errors)))
            for error in snapshot['errors']:
                self.assertEqual(set(error),{'code','path'})
                self.assertIn(error['code'],{'BOOL','ENUM','COUNT','TIMING','PHASE','SOURCE','DECODER','CONSISTENCY'})
                self.assertIsInstance(error['path'],str)
        return result

    def valid_pair(self, fixture, acquisition, frozen):
        blob,report,records=fixture
        result=self.pair(blob)
        self.assertIs(result['frozen'],frozen)
        self.assertEqual(result['acquisition'],acquisition)
        for snapshot in result['snapshots']:
            self.assertIs(snapshot['valid'],True)
            self.assertEqual(snapshot['errors'],[])
            self.assertEqual(snapshot['report'],report)
            self.assertEqual(snapshot['captures'],records)
        return result

    def invalid(self, blob, code=None, path=None):
        result=self.pair(blob)
        self.assertIs(result['frozen'],False)
        self.assertEqual(result['acquisition'],'UNAVAILABLE')
        for snapshot in result['snapshots']:
            self.assertIs(snapshot['valid'],False)
            self.assertTrue(snapshot['errors'])
            if code:
                self.assertTrue(any(error['code']==code and (path is None or error['path']==path)
                                    for error in snapshot['errors']),snapshot['errors'])
        return result

    def test_literal_complete_128_preserves_every_public_field_and_raw_endpoints(self):
        result=self.valid_pair(complete_fixture(),'COMPLETE_128',True)
        captures=result['snapshots'][0]['captures']
        self.assertEqual(len(captures),128)
        self.assertEqual({record['sample']['raw'] for record in captures},{0,16383})
        self.assertEqual([record['sample']['sequence'] for record in captures],list(range(1,129)))
        for key in ('fresh','clock_fault','counter_saturated','sample_seen','last_read_accepted','decode_matches_sample'):
            self.assertIs(type(result['snapshots'][0]['report'][key]),int)

    def test_natural_microsecond_wrap_and_missed_cadence_are_accepted(self):
        self.valid_pair(complete_fixture(start=U32-25),'COMPLETE_128',True)
        misses=[0]+[index%5 for index in range(1,128)]
        self.valid_pair(complete_fixture(misses=misses,not_due=9),'COMPLETE_128',True)

    def test_counter_saturation_and_retained_unmeasured_duration_are_truthful(self):
        self.valid_pair(complete_fixture(not_due=U32),'COMPLETE_128',True)
        blob,report,records=diagnostic_fixture(fault=7,count=2)
        report['read_timing']=timing(3,2,21,25,0)
        report['poll_timing']=timing(3,2,31,40,0)
        encode_report(blob,report)
        self.valid_pair((blob,report,records),'FAULT',True)

    def test_frozen_setup_rejection_is_fault_not_successful_acquisition(self):
        for status in range(1,15):
            for shutdown in range(3):
                with self.subTest(status=status,shutdown=shutdown):
                    blob,report,records=diagnostic_fixture()
                    report['setup']={'status':status,'shutdown':shutdown,'ready':0}
                    encode_report(blob,report)
                    self.valid_pair((blob,report,records),'FAULT',True)

    def test_failure_reports_keep_actual_failed_sample_and_historical_decoder(self):
        blob,report,records=diagnostic_fixture(fault=4,count=2)
        report.update(sample_seen=1,last_read_accepted=0,decode_matches_sample=0)
        report['sample']=sample(65535,U32,17,U32,status=8,shutdown=2,valid=0)
        encode_report(blob,report)
        result=self.valid_pair((blob,report,records),'FAULT',True)
        self.assertNotEqual(result['snapshots'][0]['report']['sample']['sequence'],
                            result['snapshots'][0]['report']['decoded']['evidence']['sequence'])

    def test_actual_valid_native_return_can_precede_source_or_clock_fault(self):
        for fault in (5,6,7):
            with self.subTest(fault=fault):
                blob,report,records=diagnostic_fixture(fault=fault,count=2)
                report['sample']=sample(42,4,3,3)
                report.update(decode_matches_sample=0,last_read_accepted=0)
                encode_report(blob,report)
                self.valid_pair((blob,report,records),'FAULT',True)

    def test_bad_s_retains_earlier_accepted_flags_and_complete_prefix(self):
        self.valid_pair(diagnostic_fixture(fault=7,count=2),'FAULT',True)

    def test_nonterminal_equal_snapshots_never_become_frozen(self):
        for phase in (0,1,2):
            with self.subTest(phase=phase):
                self.valid_pair(diagnostic_fixture(phase=phase,fault=0),'NONTERMINAL',False)
        self.valid_pair(complete_fixture(count=127),'NONTERMINAL',False)

    def test_ignored_regions_and_nonzero_padding_remain_visible_in_byte_identity(self):
        blob,report,records=diagnostic_fixture(fault=4,count=2)
        ignored=[0,3,12,REPORT+11,REPORT+29,REPORT+33,REPORT+42,REPORT+57,
                 REPORT+89,REPORT+109,REPORT+129,CAPTURES+17,CAPTURES+21,
                 CAPTURES+30,CAPTURES+45,CAPTURES+2*STRIDE,9876,9891]
        for offset in ignored:
            with self.subTest(offset=offset):
                changed=bytearray(blob)
                changed[offset]=0xa5
                self.valid_pair((changed,report,records),'FAULT',True)
                result=self.pair(blob,changed)
                self.assertIs(result['frozen'],False)
                self.assertEqual(result['acquisition'],'UNAVAILABLE')
                self.assertTrue(all(snapshot['valid'] for snapshot in result['snapshots']))

    def test_changed_valid_public_field_preserves_both_distinct_snapshots(self):
        first,report,records=diagnostic_fixture()
        second=bytearray(first)
        second[REPORT+8]=5
        result=self.pair(first,second)
        self.assertIs(result['frozen'],False)
        self.assertEqual(result['acquisition'],'UNAVAILABLE')
        self.assertEqual(result['snapshots'][0]['report']['setup']['status'],4)
        self.assertEqual(result['snapshots'][1]['report']['setup']['status'],5)

    def test_mutable_wrong_type_and_wrong_length_inputs_are_rejected(self):
        good=bytes(complete_fixture()[0])
        bad=[None,'x'*SIZE,bytearray(good),memoryview(good),good[:-1],good+b'\0',b'']
        for value in bad:
            for pair in ((value,good),(good,value)):
                with self.subTest(kind=type(value).__name__,length=len(value) if hasattr(value,'__len__') else None):
                    with self.assertRaises(ValueError):
                        self.module.decode_runner_pair(*pair)

    def test_pure_decoder_has_no_file_process_clock_or_board_side_effect(self):
        blob=bytes(complete_fixture()[0])
        with mock.patch.object(builtins,'open',side_effect=AssertionError('file')):
            with mock.patch.object(os,'open',side_effect=AssertionError('file')):
                with mock.patch.object(subprocess,'run',side_effect=AssertionError('process')):
                    with mock.patch.object(time,'monotonic',side_effect=AssertionError('clock')):
                        self.assertEqual(self.module.decode_runner_pair(blob,blob)['acquisition'],'COMPLETE_128')

    def test_unknown_enums_and_bool_bytes_are_preserved_and_rejected(self):
        enum_fields=[(0,'phase'),(1,'fault'),(8,'setup.status'),(9,'setup.shutdown'),
                     (12,'sample.status'),(13,'sample.shutdown'),(32,'decoded.qualification'),
                     (38,'decoded.evidence.presence'),(39,'decoded.evidence.level')]
        for offset,path in enum_fields:
            blob=diagnostic_fixture()[0]
            blob[REPORT+offset]=255
            self.invalid(blob,'ENUM','report.'+path)
        booleans=[(i,name) for i,name in enumerate(('fresh','clock_fault','counter_saturated','sample_seen',
                                                  'last_read_accepted','decode_matches_sample'),2)]
        booleans += [(10,'setup.ready'),(28,'sample.valid'),(36,'decoded.evidence.explicit_values'),
                     (37,'decoded.evidence.contract_valid'),(88,'setup_timing.last_valid'),
                     (108,'read_timing.last_valid'),(128,'poll_timing.last_valid')]
        for offset,path in booleans:
            blob=diagnostic_fixture()[0]
            blob[REPORT+offset]=2
            result=self.invalid(blob,'BOOL','report.'+path)
            value=result['snapshots'][0]['report']
            for key in path.split('.'): value=value[key]
            self.assertEqual(value,2)
            self.assertIs(type(value),int)

    def test_count_outside_capacity_has_null_capture_prefix(self):
        for count in (129,U32):
            blob=complete_fixture()[0]
            struct.pack_into('<I',blob,REPORT+60,count)
            result=self.invalid(blob,'COUNT','report.captured_samples')
            for snapshot in result['snapshots']: self.assertIsNone(snapshot['captures'])

    def test_phase_fault_count_and_clock_relationships_are_checked(self):
        variants=[(3,0,127,0),(4,0,0,0),(4,4,128,0),(2,4,0,0),(0,0,1,0),
                  (1,0,1,0),(2,0,1,1),(4,7,1,0)]
        for phase,fault,count,clock in variants:
            with self.subTest(phase=phase,fault=fault,count=count,clock=clock):
                blob,report,records=complete_fixture(count)
                report.update(phase=phase,fault=fault,clock_fault=clock)
                encode_report(blob,report)
                self.invalid(blob,'PHASE')

    def test_timing_domains_and_unmeasured_history_are_checked(self):
        invalids=[timing(1,2),timing(2,1,5,4,1),timing(1,1,HALF,HALF,1),
                  timing(1,0,1,1,0),timing(1,0,0,0,1)]
        for name in ('setup_timing','read_timing','poll_timing'):
            for value in invalids:
                blob,report,records=diagnostic_fixture()
                report[name]=value
                encode_report(blob,report)
                self.invalid(blob,'TIMING')

    def test_capture_source_shape_sequence_and_decoder_are_checked(self):
        for offset,fmt,value in ((0,'B',1),(1,'B',1),(2,'H',16384),(12,'I',2),(16,'B',0)):
            blob=complete_fixture()[0]
            struct.pack_into('<'+fmt,blob,CAPTURES+offset,value)
            self.invalid(blob)
        for offset,fmt,value in ((20,'B',1),(24,'B',0),(25,'B',0),(26,'B',2),
                                 (27,'B',1),(28,'H',99),(32,'I',3),(36,'I',999),(40,'I',999),(44,'B',1)):
            blob=complete_fixture()[0]
            struct.pack_into('<'+fmt,blob,CAPTURES+offset,value)
            self.invalid(blob,'DECODER')

    def test_capture_wrapper_chronology_half_range_and_source_duration_boundary(self):
        for offset,value in ((4,99),(8,101),(52,105),(56,119),(56,100+HALF)):
            blob=complete_fixture()[0]
            struct.pack_into('<I',blob,CAPTURES+offset,value)
            self.invalid(blob,'TIMING','captures[0]')
        for duration in (99,100):
            blob,report,records=complete_fixture()
            record=records[0]
            record['sample']['completed_us']=record['sample']['started_us']+duration
            record['decoded']=decoded(record['sample'])
            record.update(source_us=duration,read_us=duration+3,poll_us=duration+5,
                          call_returned_us=record['call_started_us']+duration+3,
                          poll_closed_us=record['call_started_us']+duration+5)
            encode_capture(blob,0,record)
            report['read_timing']['maximum_us']=max(r['read_us'] for r in records)
            report['poll_timing']['maximum_us']=max(r['poll_us'] for r in records)
            encode_report(blob,report)
            if duration==99: self.valid_pair((blob,report,records),'COMPLETE_128',True)
            else: self.invalid(blob)

    def test_wrong_stored_source_read_poll_duration_and_cadence_are_rejected(self):
        for offset,code,path in ((60,'SOURCE','captures[0].source_us'),(64,None,None),(68,None,None),(72,None,None)):
            blob=complete_fixture()[0]
            struct.pack_into('<I',blob,CAPTURES+offset,1)
            self.invalid(blob,code,path)
        blob=complete_fixture()[0]
        struct.pack_into('<I',blob,CAPTURES+STRIDE+72,1)
        self.invalid(blob)

    def test_complete_summary_statistics_and_latest_semantic_identity_are_checked(self):
        changes=[(8,'B',1),(10,'B',0),(3,'B',1),(5,'B',0),(6,'B',0),(7,'B',0),
                 (14,'H',42),(44,'I',33),(72,'I',2),(76,'I',0),(88,'B',0),
                 (92,'I',127),(96,'I',127),(100,'I',0),(104,'I',25),(108,'B',0),
                 (112,'I',129),(116,'I',127),(120,'I',0),(124,'I',37),(128,'B',0),
                 (68,'I',1)]
        for offset,fmt,value in changes:
            with self.subTest(offset=offset):
                blob=complete_fixture()[0]
                struct.pack_into('<'+fmt,blob,REPORT+offset,value)
                self.invalid(blob)

    def test_failed_final_call_may_add_misses_beyond_committed_prefix(self):
        blob,report,records=diagnostic_fixture(fault=6,count=2)
        report['missed_releases']=12
        encode_report(blob,report)
        self.valid_pair((blob,report,records),'FAULT',True)
        blob,report,records=complete_fixture(count=2,misses=[0,4])
        report.update(phase=4,fault=6,missed_releases=3)
        encode_report(blob,report)
        self.invalid(blob)


ARTIFACT = Path('/home/arduino/sumox26-capture-input/ui_adc_probe_396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642')
OPENOCD = '/opt/openocd/bin/openocd'
READELF = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-readelf'
LOADER_ROOT = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx'
ELF_HASH = '76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b'
ZSK_HASH = '567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9'
P0_HASH = '885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c'
PIN_HASHES = {
    OPENOCD:'04778a80c5c619ee4eef7505db91328f1d7e789107c496f2ddcf96d081f5b0ff',
    '/opt/openocd/share/openocd/scripts/target/swj-dp.tcl':'aad132008735bbafea3d18a304632c638f0fb99bfc19530c9f577eda2b10410a',
    LOADER_ROOT+'.bin':'6b2ffd3a24aa77ca40bac1a8c61460c5cdd3292a2ff38cb377b938a6ac939713',
    LOADER_ROOT+'.elf':'39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd',
    str(ROOT/'tools/p0_mem_read.cfg'):'89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339',
    READELF:'c37462dcd380ae1039eb8a0aab379a619415e1100472291ffea2eae34161092e',
    str(ROOT/'tools/p0_capture.py'):P0_HASH,
}
LAYOUT = {'bss_section':8,'bss_address':5776,'bss_file_offset':6616,'bss_size':9893,
          'bss_alignment':4,'symbol':'_ZN12_GLOBAL__N_16runnerE','symbol_value':0,
          'symbol_size':9892,'symbol_binding':'LOCAL','symbol_type':'OBJECT',
          'symbol_visibility':'DEFAULT','runner_offset':0,'report_offset':16,
          'report_size':132,'captures_offset':148,'capture_stride':76,'capture_count':128}
ELF_HEADER = '''ELF Header:
  Class:                             ELF32
  Data:                              2's complement, little endian
  Type:                              REL (Relocatable file)
  Machine:                           ARM
Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 8] .bss              NOBITS          00001690 0019d8 0026a5 00  WA  0   0  4
'''
ELF_SYMBOLS = '''Symbol table '.symtab' contains 1 entries:
   Num:    Value  Size Type    Bind   Vis      Ndx Name
     1: 00000000  9892 OBJECT  LOCAL  DEFAULT    8 _ZN12_GLOBAL__N_16runnerE
'''
LOADER_IMAGE = bytes((i*37+i//65536*13)&255 for i in range(263680))


def node(next_address=0, name=b'sketch\0', base=0x20060000, size=9893):
    value=bytearray(196)
    struct.pack_into('<I',value,0,next_address)
    value[4:20]=name.ljust(16,b'\0')[:16]
    struct.pack_into('<I',value,32,base)
    struct.pack_into('<I',value,92,size)
    return bytes(value)


def read_plan(nodes):
    before=[]
    for kind,base,total in (('loader',0x08000000,263680),('sketch',0x08100000,19840)):
        for index,offset in enumerate(range(0,total,65536)):
            before.append((f'{kind}-before-{index:02}',base+offset,min(65536,total-offset),kind))
    middle=[('llext-list-before',0x200017bc,8,'ram')]
    middle += [(f'node-before-{i+1}',address,196,'ram') for i,address in enumerate(nodes)]
    middle += [('runner-first',0x20060000,9892,'ram'),('runner-second',0x20060000,9892,'ram'),
               ('llext-list-after',0x200017bc,8,'ram')]
    middle += [(f'node-after-{i+1}',address,196,'ram') for i,address in enumerate(nodes)]
    return before+middle+[(label.replace('before','after'),address,size,region)
                          for label,address,size,region in before]


class CollectorFixture:
    """Public pure-helper substitutions plus literal filesystem/process replies only."""
    def __init__(self, module, folder, nodes=1):
        self.module,self.folder=module,Path(folder)
        self.folder.mkdir(exist_ok=True)
        self.now=100.0
        self.hashes=dict(PIN_HASHES)
        self.hashes[str(ARTIFACT/'ui_adc_probe.ino.elf')]=ELF_HASH
        self.hashes[str(ARTIFACT/'ui_adc_probe.ino.elf-zsk.bin')]=ZSK_HASH
        self.files={name:b'opaque public identity fixture' for name in self.hashes}
        target=ROOT/'state/analysis/P2_ui_adc_probe_raw/target_396bcc45_bench-default_checked'
        for name in ('ui_adc_probe.ino.elf','ui_adc_probe.ino.elf-zsk.bin'):
            self.files[str(ARTIFACT/name)]=(target/name).read_bytes()
        self.files[LOADER_ROOT+'.bin']=LOADER_IMAGE
        self.nodes=[0x20010000+i*0x100 for i in range(nodes)]
        self.plan=read_plan(self.nodes)
        self.memory={'llext-list-before':struct.pack('<II',self.nodes[0],self.nodes[-1])}
        for i,address in enumerate(self.nodes):
            name=b'sketch\0' if i==nodes-1 else f'lib{i}'.encode()+b'\0'
            self.memory[f'node-before-{i+1}']=node(self.nodes[i+1] if i+1<nodes else 0,name)
        self.memory['runner-first']=bytes(complete_fixture()[0])
        self.memory['runner-second']=self.memory['runner-first']
        self.overrides,self.commands,self.reads,self.timeouts,self.paths={},[],[],[],[]
        self.header,self.symbols=ELF_HEADER,ELF_SYMBOLS
        self.hash_queries,self.symlinks=[],set()
        self.on_command=None

    def file_hash(self,path):
        self.hash_queries.append(str(path))
        if str(path) not in self.hashes: raise AssertionError('Unpinned hash path: '+str(path))
        return self.hashes[str(path)]

    def payload(self,label,address,size,region):
        if label in self.overrides: return self.overrides[label]
        if region=='loader': return LOADER_IMAGE[address-0x08000000:address-0x08000000+size]
        if region=='sketch':
            image=self.files[str(ARTIFACT/'ui_adc_probe.ino.elf-zsk.bin')]
            return image[address-0x08100000:address-0x08100000+size]
        return self.memory[label.replace('-after','-before')]

    @staticmethod
    def stream_output(options,key,text):
        stream=options.get(key)
        if hasattr(stream,'write'):
            try: stream.write(text)
            except TypeError: stream.write(text.encode())
            stream.flush()

    def run(self,argv,**options):
        argv=[str(value) for value in argv]
        self.commands.append(argv)
        self.timeouts.append(options['timeout'])
        if self.on_command: self.on_command(argv,options)
        output='Open On-Chip Debugger 0.12.0\n' if argv==[OPENOCD,'--version'] else ''
        if argv==[READELF,'--version']: output='GNU readelf (GNU Binutils) 2.38\n'
        elif argv==[READELF,'-hSW',str(ARTIFACT/'ui_adc_probe.ino.elf')]: output=self.header
        elif argv==[READELF,'-sW',str(ARTIFACT/'ui_adc_probe.ino.elf')]: output=self.symbols
        elif argv!=[OPENOCD,'--version']:
            assert len(argv)==7 and argv[:3]==[OPENOCD,'-f',str(ROOT/'tools/p0_mem_read.cfg')]
            assert argv[3]=='-c' and argv[5:]==['-c','shutdown']
            match=re.fullmatch(r'dump_image \{([^{}]+)\} (0x[0-9a-fA-F]+) ([0-9]+)',argv[4])
            assert match, 'Only literal bounded dump_image is permitted'
            destination,address,size=Path(match[1]),int(match[2],16),int(match[3])
            assert destination.resolve().parent==self.folder.resolve(), 'Output must remain in fixture directory'
            label,expected,size_expected,region=self.plan[len(self.reads)]
            assert (address,size)==(expected,size_expected), (label,address,size)
            self.reads.append((label,address,size,region)); self.paths.append(destination)
            value=self.payload(label,address,size,region)
            if isinstance(value,Exception):
                destination.write_bytes(b'partial-before-command-error')
                raise value
            destination.write_bytes(value)
        self.stream_output(options,'stdout',output)
        self.stream_output(options,'stderr','')
        return subprocess.CompletedProcess(argv,0,output,'')

    def __enter__(self):
        self.context=ExitStack()
        original_read=Path.read_bytes
        original_isfile,original_exists,original_symlink=Path.is_file,Path.exists,Path.is_symlink
        original_stat=Path.stat
        fixture=self
        def read(path):
            return fixture.files[str(path)] if str(path) in fixture.files else original_read(path)
        def exists(path):
            return True if str(path) in fixture.files or str(path)==str(ARTIFACT) else original_exists(path)
        def stat(path,*args,**kwargs):
            if str(path) in fixture.files:
                actual=original_stat(fixture.folder)
                fields=list(actual);fields[0]=0o100644;fields[6]=len(fixture.files[str(path)])
                return os.stat_result(fields)
            return original_stat(path,*args,**kwargs)
        self.context.enter_context(mock.patch.object(Path,'read_bytes',read))
        self.context.enter_context(mock.patch.object(Path,'exists',exists))
        self.context.enter_context(mock.patch.object(Path,'is_file',lambda p:str(p) in fixture.files or original_isfile(p)))
        self.context.enter_context(mock.patch.object(Path,'is_symlink',lambda p:str(p) in fixture.symlinks or original_symlink(p)))
        self.context.enter_context(mock.patch.object(Path,'stat',stat))
        self.context.enter_context(mock.patch.object(self.module.p0,'file_hash',self.file_hash))
        self.context.enter_context(mock.patch.object(self.module.p0,'loader_image',return_value=LOADER_IMAGE))
        self.context.enter_context(mock.patch.object(subprocess,'run',self.run))
        self.context.enter_context(mock.patch.object(time,'monotonic',lambda:self.now))
        self.report={}
        self.capture=self.module.Capture(self.folder,self.report)
        return self

    def __exit__(self,*args):
        return self.context.__exit__(*args)

    def collect(self):
        return self.module.collect(self.capture,ARTIFACT)


class UiAdcCollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module=importlib.import_module('ui_adc_capture')

    def assert_failed(self,fixture):
        with self.assertRaises((ValueError,OSError,subprocess.SubprocessError)):
            fixture.collect()
        self.assertNotEqual(fixture.report.get('collection_integrity'),'VERIFIED')
        self.assertIsNone(fixture.report.get('diagnostic'))

    def test_literal_layout_identity_plan_and_unchanged_helper_hash(self):
        self.assertEqual(self.module.PINNED_LAYOUT,LAYOUT)
        self.assertEqual(self.module.MAXIMUM_READ_PLAN,{'reads':22,'bytes':588016,'commands':26,'extension_nodes':3})
        self.assertEqual(Path(self.module.ARTIFACT_DIR),ARTIFACT)
        actual={str(key):value for key,value in self.module.EXPECTED_HASHES.items()}
        for path,digest in PIN_HASHES.items(): self.assertEqual(actual[path],digest)
        self.assertEqual(hashlib.sha256((ROOT/'tools/p0_capture.py').read_bytes()).hexdigest(),P0_HASH)

    def test_constructor_and_import_have_no_process_or_memory_effect(self):
        with tempfile.TemporaryDirectory() as folder:
            with mock.patch.object(subprocess,'run',side_effect=AssertionError('external process')):
                with mock.patch.object(Path,'read_bytes',side_effect=AssertionError('memory/file')):
                    report={}; self.module.Capture(Path(folder),report)
            self.assertEqual(report['commands'],[])
            self.assertEqual(report['reads'],[])

    def test_exact_one_and_three_node_full_identity_bracket_read_sequence(self):
        for count in (1,3):
            with self.subTest(nodes=count),tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module,folder,count) as fixture:
                    result=fixture.collect()
                    self.assertIs(result,fixture.report)
                    self.assertEqual(result['collection_integrity'],'VERIFIED')
                    self.assertIs(result['physical_acceptance'],False)
                    self.assertEqual(result['diagnostic']['acquisition'],'COMPLETE_128')
                    self.assertEqual(fixture.reads,read_plan(fixture.nodes))
                    self.assertEqual(len(fixture.commands),22 if count==1 else 26)
                    self.assertEqual(sum(item[2] for item in fixture.reads),587232 if count==1 else 588016)
                    self.assertTrue(all(0<value<=30 for value in fixture.timeouts))
                    self.assertTrue(set(PIN_HASHES).issubset(fixture.hash_queries))
                    self.assertTrue(all(path.exists() for path in fixture.paths))
                    for label,path in zip((r[0] for r in fixture.reads),fixture.paths):
                        if label.startswith('runner-'): self.assertEqual(path.read_bytes(),fixture.memory[label])

    def test_collection_integrity_is_separate_from_frozen_acquisition_result(self):
        for kind in ('FAULT','NONTERMINAL','UNAVAILABLE'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module,folder) as fixture:
                    value=diagnostic_fixture(fault=4,count=2)[0] if kind=='FAULT' else complete_fixture(count=2)[0]
                    fixture.memory.update({'runner-first':bytes(value),'runner-second':bytes(value)})
                    if kind=='UNAVAILABLE': fixture.memory['runner-second']=bytes(value[:-1])+b'\1'
                    result=fixture.collect()
                    self.assertEqual(result['collection_integrity'],'VERIFIED')
                    self.assertEqual(result['diagnostic']['acquisition'],kind)

    def test_every_wrong_hash_refuses_before_any_command(self):
        for path in list(PIN_HASHES)+[str(ARTIFACT/'ui_adc_probe.ino.elf'),str(ARTIFACT/'ui_adc_probe.ino.elf-zsk.bin')]:
            with self.subTest(path=path),tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module,folder) as fixture:
                    fixture.hashes[path]='0'*64
                    self.assert_failed(fixture)
                    self.assertEqual(fixture.commands,[])

    def test_unpinned_artifact_symlink_and_exact_image_extent_refuse(self):
        with tempfile.TemporaryDirectory() as folder:
            for wrong in (ARTIFACT.parent,ARTIFACT/'subdir',Path('/tmp/unreviewed')):
                with CollectorFixture(self.module,folder) as fixture:
                    with self.assertRaises(ValueError): self.module.check_identities(fixture.capture,wrong)
                    self.assertEqual(fixture.commands,[])
            for name in ('ui_adc_probe.ino.elf','ui_adc_probe.ino.elf-zsk.bin'):
                for wrong in ('symlink','short','large'):
                    with self.subTest(name=name,wrong=wrong),CollectorFixture(self.module,folder) as fixture:
                        path=str(ARTIFACT/name)
                        if wrong=='symlink': fixture.symlinks.add(path)
                        elif wrong=='short': fixture.files[path]=fixture.files[path][:-1]
                        else: fixture.files[path]+=b'\0'
                        self.assert_failed(fixture)
                        self.assertEqual(fixture.commands,[])

    def test_every_layout_identity_disagreement_refuses_before_memory(self):
        headers=[ELF_HEADER.replace('ELF32','ELF64'),ELF_HEADER.replace('little endian','big endian'),
                 ELF_HEADER.replace('REL (Relocatable file)','DYN (Shared object file)'),
                 ELF_HEADER.replace('ARM','AArch64'),ELF_HEADER.replace('0026a5','0026a4'),
                 ELF_HEADER.replace('0019d8','0019d4'),ELF_HEADER.replace('00001690','00001694'),
                 ELF_HEADER.replace('  4\n','  8\n'),ELF_HEADER+ELF_HEADER.split('Section Headers:')[1]]
        symbols=[ELF_SYMBOLS.replace('00000000','00001690'),ELF_SYMBOLS.replace('9892','9891'),
                 ELF_SYMBOLS.replace('LOCAL','GLOBAL'),ELF_SYMBOLS.replace('OBJECT','FUNC'),
                 ELF_SYMBOLS.replace('DEFAULT','HIDDEN'),ELF_SYMBOLS.replace('    8 ','    7 '),
                 ELF_SYMBOLS.replace('runnerE','runnexE'),ELF_SYMBOLS+ELF_SYMBOLS.splitlines()[-1]+'\n']
        for header,symbols in [(h,ELF_SYMBOLS) for h in headers]+[(ELF_HEADER,s) for s in symbols]:
            with self.subTest(header=header,symbols=symbols),tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module,folder) as fixture:
                    fixture.header,fixture.symbols=header,symbols
                    self.assert_failed(fixture)
                    self.assertEqual(fixture.reads,[])

    def test_every_flash_chunk_first_and_last_byte_is_verified_both_passes(self):
        for label,address,size,region in read_plan([0x20010000]):
            if region=='ram': continue
            for byte in (0,size-1):
                with self.subTest(label=label,byte=byte),tempfile.TemporaryDirectory() as folder:
                    with CollectorFixture(self.module,folder) as fixture:
                        value=bytearray(fixture.payload(label,address,size,region)); value[byte]^=1
                        fixture.overrides[label]=bytes(value)
                        self.assert_failed(fixture)
                        self.assertEqual(fixture.reads[-1][0],label)
                        if '-before-' in label: self.assertFalse(any(r[3]=='ram' for r in fixture.reads))

    def test_bad_list_head_tail_and_node_addresses_never_admit_runner(self):
        bad_lists=[(0,0),(0x1ffffffc,0x1ffffffc),(0x200c0000,0x200c0000),
                   (0x20010001,0x20010001),(0xfffffffC,0xfffffffC),(0x20010000,0x20010100)]
        for head,tail in bad_lists:
            with self.subTest(head=head,tail=tail),tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module,folder) as fixture:
                    fixture.memory['llext-list-before']=struct.pack('<II',head,tail)
                    self.assert_failed(fixture)
                    self.assertFalse(any(r[0].startswith('runner') for r in fixture.reads))

    def test_bad_node_cycle_name_bss_extent_alignment_and_range_are_rejected(self):
        bad=[node(next_address=0x20010000),node(name=b'x'*16),node(name=b'other\0'),
             node(size=9892),node(size=9894),node(base=0x20060001),node(base=0x1ffffffc),
             node(base=0x200c0000-9892),node(base=0xfffffffC)]
        for value in bad:
            with self.subTest(node=value.hex()),tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module,folder) as fixture:
                    fixture.memory['node-before-1']=value
                    self.assert_failed(fixture)
                    self.assertFalse(any(r[0].startswith('runner') for r in fixture.reads))

    def test_duplicate_sketch_and_fourth_node_fail_without_following_extra_node(self):
        for wrong in ('duplicate','fourth'):
            with self.subTest(wrong=wrong),tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module,folder,3) as fixture:
                    if wrong=='duplicate': fixture.memory['node-before-1']=node(fixture.nodes[1])
                    else: fixture.memory['node-before-3']=node(0x20010300)
                    self.assert_failed(fixture)
                    self.assertLessEqual(sum(r[0].startswith('node-before') for r in fixture.reads),3)
                    self.assertFalse(any(r[0].startswith('runner') for r in fixture.reads))

    def test_post_runner_list_and_every_node_byte_change_prevents_verified_result(self):
        for label in ('llext-list-after','node-after-1','node-after-2','node-after-3'):
            with self.subTest(label=label),tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module,folder,3) as fixture:
                    value=bytearray(fixture.memory[label.replace('-after','-before')]);value[-1]^=1
                    fixture.overrides[label]=bytes(value)
                    self.assert_failed(fixture)
                    self.assertEqual(fixture.reads[-1][0],label)

    def test_short_or_failed_read_preserves_partial_file_and_consumes_purpose(self):
        for label in ('loader-before-00','llext-list-before','node-before-1','runner-first','runner-second','loader-after-00'):
            for command_error in (False,True):
                with self.subTest(label=label,error=command_error),tempfile.TemporaryDirectory() as folder:
                    with CollectorFixture(self.module,folder) as fixture:
                        error=subprocess.TimeoutExpired(['synthetic'],30)
                        fixture.overrides[label]=error if command_error else b'partial'
                        self.assert_failed(fixture)
                        self.assertTrue(fixture.paths[-1].read_bytes().startswith(b'partial'))
                        previous=len(fixture.commands)
                        attempted=fixture.reads[-1]
                        with self.assertRaises(ValueError): fixture.capture.read(*attempted)
                        self.assertEqual(len(fixture.commands),previous)
                        self.assertEqual(len(fixture.report['reads']),len(fixture.reads))

    def test_out_of_order_or_arbitrary_memory_and_command_requests_refuse(self):
        with tempfile.TemporaryDirectory() as folder,CollectorFixture(self.module,folder) as fixture:
            for arguments in [('runner-first',0x20060000,9892,'ram'),('llext-list-before',0x200017bc,8,'ram'),
                              ('loader-before-00',0x08000000,65536,'loader'),('arbitrary',0x40000000,4,'ram')]:
                with self.assertRaises(ValueError): fixture.capture.read(*arguments)
            for argv in (['sh','-c','true'],[OPENOCD,'-c','reset halt'],[OPENOCD,'-c','mww 0x20000000 1'],
                         [READELF,'-sW','/tmp/other.elf'],['systemctl','restart','arduino-router']):
                with self.assertRaises(ValueError): fixture.capture.run(argv)
            self.assertEqual(fixture.commands,[])

    def test_wrong_range_region_label_and_replay_stay_closed_during_collection(self):
        with tempfile.TemporaryDirectory() as folder,CollectorFixture(self.module,folder) as fixture:
            checked=[]
            def during(argv,options):
                del options
                if len(argv)!=7: return
                label,address,size,region=fixture.plan[len(fixture.reads)]
                before=len(fixture.commands)
                for args in ((label,address+4,size,region),(label,address,size-1,region),
                             (label,address,size+1,region),(label,address,size,'unreviewed'),
                             ('arbitrary',address,size,region)):
                    with self.assertRaises(ValueError): fixture.capture.read(*args)
                for previous in fixture.reads:
                    with self.assertRaises(ValueError): fixture.capture.read(*previous)
                self.assertEqual(len(fixture.commands),before)
                checked.append(label)
            fixture.on_command=during
            fixture.collect()
            self.assertEqual(checked,[item[0] for item in fixture.plan])

    def test_expiry_between_commands_stops_collection_without_retry(self):
        with tempfile.TemporaryDirectory() as folder,CollectorFixture(self.module,folder) as fixture:
            def expire(argv,options):
                del options
                if len(argv)==7: fixture.now=700.0
            fixture.on_command=expire
            self.assert_failed(fixture)
            self.assertEqual(len(fixture.reads),1)
            self.assertEqual(len(fixture.commands),5)

    def test_public_command_limit_and_remaining_deadline_without_private_mutation(self):
        with tempfile.TemporaryDirectory() as folder,CollectorFixture(self.module,folder) as fixture:
            for unused in range(64): fixture.capture.run([OPENOCD,'--version'])
            with self.assertRaises(ValueError): fixture.capture.run([OPENOCD,'--version'])
            self.assertEqual(len(fixture.commands),64)
        with tempfile.TemporaryDirectory() as folder,CollectorFixture(self.module,folder) as fixture:
            fixture.now=699.75
            fixture.capture.run([OPENOCD,'--version'])
            self.assertLessEqual(fixture.timeouts[-1],0.25)
            fixture.now=700
            with self.assertRaises(ValueError): fixture.capture.run([OPENOCD,'--version'])
            self.assertEqual(len(fixture.commands),1)

    def test_inconsistent_or_overbudget_loader_image_fails_before_memory(self):
        for size in (263679,263681,2097152):
            with self.subTest(size=size),tempfile.TemporaryDirectory() as folder:
                with CollectorFixture(self.module,folder) as fixture:
                    with mock.patch.object(self.module.p0,'loader_image',return_value=bytes(size)):
                        self.assert_failed(fixture)
                    self.assertEqual(fixture.reads,[])

    def test_main_writes_failure_or_success_json_and_separates_fault_from_acquisition(self):
        for kind,expected in (('COMPLETE_128',0),('FAULT',0),('NONTERMINAL',1),('UNAVAILABLE',1),('error',1)):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as folder:
                logical=Path('/home/arduino/sumox26-capture/d114-independent-cli')
                actual=Path(folder)/logical.name
                original_open,original_mkdir,original_exists=Path.open,Path.mkdir,Path.exists
                original_chmod,original_constructor=os.chmod,self.module.Capture
                captured={}
                def mapped(path):
                    return actual/Path(path).relative_to(logical) if Path(path).is_relative_to(logical) else Path(path)
                def mkdir(path,*args,**kwargs):
                    if path==logical.parent: return None
                    return original_mkdir(mapped(path),*args,**kwargs)
                def construct(path,report):
                    captured.update(path=path,report=report)
                    return original_constructor(path,report)
                def collected(capture,artifact):
                    del capture
                    self.assertEqual(artifact,ARTIFACT)
                    report=captured['report']
                    report.update(collection_integrity='FAILED' if kind=='error' else 'VERIFIED',
                                  physical_acceptance=False,diagnostic=None)
                    if kind=='error': raise ValueError('retained synthetic collection failure')
                    value=diagnostic_fixture(fault=4,count=2)[0] if kind=='FAULT' else complete_fixture(count=2 if kind=='NONTERMINAL' else 128)[0]
                    second=bytes(value)
                    if kind=='UNAVAILABLE': second=second[:-1]+b'\1'
                    report['diagnostic']=self.module.decode_runner_pair(bytes(value),second)
                    return report
                with ExitStack() as context:
                    context.enter_context(mock.patch.object(Path,'open',lambda p,*a,**k:original_open(mapped(p),*a,**k)))
                    context.enter_context(mock.patch.object(Path,'mkdir',mkdir))
                    context.enter_context(mock.patch.object(Path,'exists',lambda p:original_exists(mapped(p))))
                    context.enter_context(mock.patch.object(os,'chmod',lambda p,*a,**k:original_chmod(mapped(p),*a,**k)))
                    context.enter_context(mock.patch.object(self.module,'Capture',construct))
                    context.enter_context(mock.patch.object(self.module,'collect',collected))
                    context.enter_context(mock.patch.object(subprocess,'run',side_effect=AssertionError('external')))
                    output=io.StringIO(); context.enter_context(redirect_stdout(output))
                    result=self.module.main(['--artifact-dir',str(ARTIFACT),'--output',str(logical)])
                self.assertEqual(result,expected)
                stored=json.loads((actual/'capture.json').read_text())
                printed=json.loads(output.getvalue())
                self.assertEqual(stored,printed)
                self.assertIn(str(logical),json.dumps(stored))
                self.assertEqual(stored['collection_integrity'],'FAILED' if kind=='error' else 'VERIFIED')
                self.assertIs(stored['physical_acceptance'],False)
                self.assertEqual(actual.stat().st_mode&0o777,0o700)

    def test_cli_wrong_output_path_and_existing_directory_never_collect(self):
        bad=['/tmp/d114-output','/home/arduino/sumox26-capture/nested/child',
             '/home/arduino/sumox26-capture/../escape','/home/arduino/sumox26-capture/-bad',
             '/home/arduino/sumox26-capture/'+('x'*97)]
        for output in bad:
            with self.subTest(output=output),redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                with mock.patch.object(self.module,'collect',side_effect=AssertionError('collection forbidden')):
                    try: result=self.module.main(['--artifact-dir',str(ARTIFACT),'--output',output])
                    except SystemExit as error: result=error.code
                    self.assertIn(result,(1,2))
        with redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
            with mock.patch.object(Path,'mkdir',side_effect=FileExistsError('already exists')):
                with mock.patch.object(self.module,'collect',side_effect=AssertionError('collection forbidden')):
                    try: result=self.module.main(['--artifact-dir',str(ARTIFACT),'--output','/home/arduino/sumox26-capture/existing'])
                    except SystemExit as error: result=error.code
                    self.assertIn(result,(1,2))

    def test_cli_parse_rejects_arbitrary_modes_and_required_artifact_is_missing(self):
        for argv in ([],['--address','0x20000000'],['--artifact-dir',str(ARTIFACT),'--timeout','999'],
                     ['--artifact-dir',str(ARTIFACT),'--reset'],['--artifact-dir',str(ARTIFACT),'--upload']):
            with self.subTest(argv=argv),redirect_stderr(io.StringIO()):
                with mock.patch.object(subprocess,'run',side_effect=AssertionError('external')):
                    with self.assertRaises(SystemExit) as result: self.module.main(argv)
                    self.assertEqual(result.exception.code,2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
