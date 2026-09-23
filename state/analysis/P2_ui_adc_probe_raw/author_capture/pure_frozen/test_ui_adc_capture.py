# Tests D114's public pinned decoder and bounded passive collector independently.
# Literal little-endian fixtures derive from the enabled debug ABI, not decoder constants.
# Synthetic bytes and commands establish software behavior only; no board is contacted.
import builtins
import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
