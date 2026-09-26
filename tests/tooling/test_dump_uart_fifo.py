"""Additive D117 public-contract native FIFO, sketch and capacity tests.

Existing D090/D101/D116 assertions remain unchanged; all execution is isolated.
The rational serial model and capacity bound are host assumptions, never measurements.
"""
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import zlib

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'state/analysis/P2_dump_fifo_raw/author'
FIXTURE=ROOT/'tests/fixtures/dump_uart_fifo'
D116_WIRE=ROOT/'state/analysis/P2_recorder_transport_raw/author/run1_commands/normal_exports_1790205416118983952/positive.wire'
D116_HASH='420b4657c0a13d813ca66e29d6217c406de4d13befd8f7584b625724e9dfdfef'
PREFIX=bytes((0x93,0x02,0xa9))+b'mon/write'+bytes((0x91,0xd9))
EXPECTED_RAW=bytes.fromhex('ffffffffffffffff000000800080008000808080ffffffffff')


def receipt(kind,value):
    RAW.mkdir(parents=True,exist_ok=True)
    with (RAW/f'{kind}_{time.time_ns()}.json').open('x') as stream:
        json.dump(value,stream,indent=2);stream.write('\n')


def command(argv,expected=0,timeout=300):
    argv=list(map(str,argv));result=subprocess.run(argv,text=True,capture_output=True,timeout=timeout)
    receipt('command',{'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    if result.returncode!=expected:raise AssertionError(result.stdout+result.stderr)
    return result


def sanitizers():
    return ['-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-fno-pie','-no-pie']


def decode_packets(data):
    offset=0;decoded=bytearray();sizes=[]
    while offset<len(data):
        if data[offset:offset+14]!=PREFIX:raise AssertionError('Exact MessagePack prefix mismatch')
        if offset+15>len(data):raise AssertionError('Truncated packet header')
        size=data[offset+14]
        if not 1<=size<=64:raise AssertionError('Invalid payload count')
        body=data[offset+15:offset+15+size]
        if len(body)!=size:raise AssertionError('Truncated payload')
        decoded.extend(body);sizes.append(size);offset+=15+size
    return bytes(decoded),sizes


def common(stage,match=0):
    return ['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror',
            '-fno-exceptions','-fno-rtti',f'-DMATCH={match}',f'-DMOTORS_ALLOWED={match}',
            '-DARDUINO_ARCH_ZEPHYR','-DCONFIG_UART_INTERRUPT_DRIVEN',
            '-I',stage/'tests/fixtures/dump_uart_native','-I',stage/'src','-I',stage,
            '-isystem',stage/'host/third_party']


def pure(stage):
    return [*sorted((stage/'src/core').glob('*.cpp')),*[stage/'src/hal'/name for name in
            ('motors.cpp','recorder_frames.cpp','recorder.cpp','recorder_csv.cpp','recorder_dump.cpp')]]


def copy_inputs(stage):
    for name in ('src','tests','bench/recorder','host/third_party'):
        shutil.copytree(ROOT/name,stage/name,ignore=shutil.ignore_patterns('__pycache__'))
    paths=list((stage/'src').rglob('*'))+list((stage/'bench/recorder').rglob('*'))
    paths+=list((stage/'tests/fixtures/dump_uart_fifo').rglob('*'))
    receipt('opaque_source_copy',{str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in paths if p.is_file()})


@unittest.skipUnless(os.name=='posix','Native mapped-register tests require Linux')
class DumpUartFifoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='d117-native-',dir='/dev/shm')
        cls.addClassCleanup(cls.temp.cleanup);cls.stage=Path(cls.temp.name);copy_inputs(cls.stage)
        cls.binaries=[];fixture=cls.stage/'tests/fixtures/dump_uart_fifo'
        sources=[fixture/'hardware.cc',fixture/'cases.cc',fixture/'streams.cc',
                 cls.stage/'src/hal/dump_uart_unoq.cpp',cls.stage/'src/app/dump_port_unoq.cpp',*pure(cls.stage)]
        for label,flags in (('normal',[]),('asan_ubsan',sanitizers())):
            binary=cls.stage/label;command([*common(cls.stage),*flags,*sources,'-o',binary]);cls.binaries.append(binary)

    def cases(self,cases):
        for binary in self.binaries:
            for values in cases:
                with self.subTest(profile=binary.name,args=values):command([binary,*values])

    def test_passive_constructors_factory_and_first_enum_grant_context_priority(self):
        cases=[('passive',)]
        cases += [('admission',mode,bits,context) for mode in (2,255) for bits in (0,15) for context in (0,1,2)]
        cases += [('admission',mode,bits,1) for mode in (0,1) for bits in range(15)]
        cases += [('admission',mode,15,context) for mode in (0,1) for context in (1,2)]
        self.cases(cases)

    def test_exact_setup_sequence_readbacks_readiness_and_lifetime_owner(self):
        self.cases([('setup',mask,low) for mask in (0,1) for low in (0,1)])

    def test_initial_metadata_installed_state_and_autonomous_uart_refuse(self):
        self.cases([('initial',kind) for kind in range(7)]+[('legacy_autocr',v) for v in (1,1<<31)])

    def test_each_partial_setup_stage_preserves_first_fault_owned_or_skipped_cleanup(self):
        cases=[('partial',stage,fault,0,mask) for stage in (1,2,3)
               for fault in (0,1,3,4,5,6,7,8) for mask in (0,1)]
        cases += [('partial',3,fault,cleanup,mask) for fault in (2,9)
                  for cleanup in (0,1) for mask in (0,1)]
        cases += [('partial',stage,0,1,mask) for stage in (1,2,3) for mask in (0,1)]
        self.cases(cases)

    def test_real_fifo_room_and_stop_bit_completion_exact_packet_lengths(self):
        self.cases([('model',size,wrap) for size in (1,31,32,63,64) for wrap in (0,1)]+[('full',),('tc',)])

    def test_unchanged_time_store_packet_caps_wrap_and_pending_identity(self):
        self.cases([('timeout',age,wrap) for age in (99999,100000,100001) for wrap in (0,1)]
                   +[('budget',cost) for cost in (0,1,40,79,80,81)]
                   +[('identity',kind) for kind in range(5)])

    def test_live_loss_before_first_mid_and_after_eighth_store(self):
        self.cases([('live',kind,after) for kind in range(15) for after in (0,1,8)])

    def test_cancellation_keeps_shifted_prefix_and_never_repairs_foreign_state(self):
        self.cases([('cancel',kind) for kind in (0,1,2)])

    def test_real_transfer_failure_then_cancel_retains_first_evidence(self):
        self.cases([('transfer_failure',kind) for kind in range(6)])

    def test_actual_d116_payload_packet_replay_and_strict_receiver(self):
        wire=D116_WIRE.read_bytes();self.assertEqual(hashlib.sha256(wire).hexdigest(),D116_HASH)
        sys.path.insert(0,str(ROOT/'tools'));receiver=importlib.import_module('dump_match')
        validator=importlib.import_module('validate_csv_bundle')
        for binary in self.binaries:
            with self.subTest(profile=binary.name):
                output=RAW/f'{binary.name}_d116_{time.time_ns()}.mp'
                command([binary,'replay',D116_WIRE,output]);data=output.read_bytes()
                decoded,sizes=decode_packets(data);self.assertEqual(decoded,wire)
                self.assertEqual((len(data),len(sizes)),(682967,10027))
                parser=receiver.Parser()
                for start in range(0,len(decoded),257):parser.feed(decoded[start:start+257])
                captured=parser.finish()
                self.assertEqual((captured.session,captured.epoch,captured.origin),(202472,69,1))
                self.assertEqual((captured.frame_count,captured.event_count),(5001,8))
                destination=receiver.save_capture([decoded],RAW/f'{binary.name}_received_{time.time_ns()}')
                paths={r:next(destination.glob('*_'+r+'.csv')) for r in ('frames','events','summary')}
                report=validator.validate_bundle(paths['frames'],paths['events'],paths['summary'],destination/'manifest.json')
                self.assertEqual((report['format_integrity'],report['consistency']),('PASS','PASS'))
                self.assertFalse(report['hardware_acceptance'])

    def test_all_raw_capacity_slots_use_actual_formatter_and_native_packets(self):
        for binary in self.binaries:
            with self.subTest(profile=binary.name):
                output=RAW/f'{binary.name}_raw_capacity_{time.time_ns()}'
                command([binary,'capacity',output]);wire=output.with_suffix('.wire').read_bytes()
                decoded,sizes=decode_packets(output.with_suffix('.mp').read_bytes());self.assertEqual(decoded,wire)
                frames=[s for s in wire.splitlines(keepends=True) if s.startswith(b'FR,')]
                events=[s for s in wire.splitlines(keepends=True) if s.startswith(b'ER,')]
                self.assertEqual((len(frames),len(events)),(5001,4096))
                for ordinal,row in enumerate(frames):
                    fields=row.rstrip(b'\n').split(b',');self.assertEqual(fields[:5],[b'FR',b'18446744073709551615',b'1',str(ordinal).encode(),b'2'])
                    self.assertEqual(fields[5:-1],list(map(lambda v:str(v).encode(),struct.unpack('<IBBBBihhhbbHBH',EXPECTED_RAW))))
                    self.assertEqual(fields[-1],EXPECTED_RAW.hex().encode());self.assertLessEqual(len(row),170)
                for ordinal,row in enumerate(events):
                    expected=f'ER,18446744073709551615,1,{ordinal},4294967295,255,255,65535,ffffffffffffffff\n'.encode()
                    self.assertEqual(row,expected);self.assertLessEqual(len(row),73)
                self.assertEqual(len(frames[-1]),170);self.assertEqual(len(events[-1]),73)
                other=[s for s in wire.splitlines(keepends=True) if not s.startswith((b'FR,',b'ER,'))]
                self.assertEqual(len(other),6);self.assertTrue(all(len(s)<=1151 for s in other))
                self.assertLessEqual(len(wire),1156084);self.assertLessEqual(len(wire)+15*len(sizes),1505629)
                # Invalid raw enums deliberately test retention; this is not a valid Robot stream.
                self.assertEqual(zlib.crc32(wire[:wire.rfind(b'END,')]),int(other[-1].split(b',')[-1]))


class CapacityModelTests(unittest.TestCase):
    def test_six_effective_stores_complete_and_five_refuse_without_invented_fifo_contents(self):
        chunks=[]
        for count,length in ((5001,170),(4096,73),(6,1151)):
            pieces=[min(64,length-offset) for offset in range(0,length,64)]
            chunks.extend(pieces*count)
        self.assertEqual((len(chunks),sum(chunks),sum(p+15 for p in chunks)),(23303,1156084,1505629))
        results={}
        for budget,expected in ((8,217659),(6,288575),(5,331091)):
            required=sum(math.ceil((p+15)/budget)+1 for p in chunks);self.assertEqual(required,expected)
            calls=0;acknowledged=0;submitted=0;refused=False
            for size in chunks:
                pending=size+15
                while pending:
                    if calls==300000:refused=True;break
                    amount=min(budget,pending);pending-=amount;submitted+=amount;calls+=1
                if refused:break
                if calls==300000:refused=True;break
                calls+=1;acknowledged+=size
            self.assertEqual(refused,budget==5)
            if not refused:self.assertEqual((calls,acknowledged),(expected,1156084))
            else:self.assertEqual(calls,300000);self.assertLess(acknowledged,1156084)
            results[str(budget)]={'required_calls':required,'observed_model_calls':calls,
                'acknowledged_payload_bytes':acknowledged,'submitted_wire_bytes':submitted,'deadline_refused':refused}
        receipt('capacity_model',{'assumption':'Effective stores per call plus one reserved completion call per packet; no hardware minimum claim.','profiles':results})


@unittest.skipUnless(os.name=='posix','Opaque sketch compilation runs in Linux')
class SelectedSketchTests(unittest.TestCase):
    def test_both_real_sketches_select_fifo_with_unchanged_default_dump_passivity(self):
        with tempfile.TemporaryDirectory(prefix='d117-sketch-',dir='/dev/shm') as temporary:
            stage=Path(temporary);copy_inputs(stage);fixtures=stage/'tests/fixtures/dump_uart_fifo'
            shutil.copyfile(fixtures/'sketch_dump_stub.h',stage/'src/hal/dump_uart_unoq.h')
            shutil.copyfile(fixtures/'sketch_sources_stub.h',stage/'src/app/native_sources_unoq.h')
            shutil.copyfile(fixtures/'sketch_runner_stub.h',stage/'bench/recorder/src/recorder_transport.h')
            (stage/'Arduino.h').write_text('#pragma once\nunsigned long micros();\n')
            for sketch,match in (('recorder',0),('app',0),('app',1)):
                original=stage/('src/app/app.ino' if sketch=='app' else 'bench/recorder/recorder.ino')
                translated=original.with_suffix('.cpp');shutil.copyfile(original,translated)
                sources=[translated,fixtures/'sketch.cc',stage/'src/app/dump_port_unoq.cpp']
                extras=[]
                if sketch=='app':
                    extras=['-DD117_APP','-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS']
                    sources+=pure(stage)+list(sorted((stage/'src/app').glob('runtime*.cpp')))
                    sources += [stage/'src/app/transaction.cpp',stage/'src/app/transaction_service.cpp']
                    sources += [stage/'src/hal'/name for name in ('power_inputs.cpp','ui.cpp','imu_heading.cpp','imu_adapter.cpp',
                              'line_qtr_adapter.cpp','qtr_cal.cpp','qtr_cal_format.cpp','ui_display.cpp')]
                for label,flags in (('normal',[]),('asan_ubsan',sanitizers())):
                    with self.subTest(sketch=sketch,match=match,profile=label):
                        binary=stage/f'{sketch}_{match}_{label}'
                        command([*common(stage,match),'-I',stage,*flags,*extras,*sources,'-o',binary])
                        result=command([binary]);self.assertEqual(result.stdout,'');self.assertEqual(result.stderr,'')


if __name__=='__main__':unittest.main(verbosity=2)
