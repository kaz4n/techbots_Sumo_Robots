"""Execute independent D116 full-lifecycle, wire, config and default native tests.

Production bodies remain opaque; actual owners run only after the author freeze.
The fast sink proves composition, while one-byte progress retains the TOTAL gap.
"""
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import zlib

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'state/analysis/P2_recorder_transport_raw/author'
FRAME_HEADER=b'schema_version,ordinal,pack_status,t_ms,state,mode,line_mask,opp_mask,heading_cdeg,gyro_z_dps10,ax_mg,ay_mg,duty_l_127,duty_r_127,vbat_cv,flags,tick_max_us,raw_hex\n'
EVENT_HEADER=b'schema_version,ordinal,t_us,type,detail,value,raw_hex\n'
SUMMARY_HEADER=b'schema_version,epoch_token,last_frame_token,release_us,mode,phase,observed_results,missing_results,rejected_results,identity_rejected,malformed_batches,event_semantic_rejected,upstream_event_rejected,upstream_event_invalid,source_regressions,skipped_frames,ticks,overruns,tick_max_us,ticks_saturated,upstream_event_overflow,timing_incomplete,recording_incomplete,go_seen,final_frame_missing,interrupted,terminal_exhausted,frame_count,frame_overwritten,frame_rejected_status,frame_clamped,frame_invalid,event_count,event_overflow,event_rejected,incomplete\n'
FRAME=struct.Struct('<IBBBBihhhbbHBH')
EVENT=struct.Struct('<IBBH')


def receipt(kind,value):
    RAW.mkdir(parents=True,exist_ok=True)
    with (RAW/f'{kind}_{time.time_ns()}.json').open('x',encoding='utf-8') as output:
        json.dump(value,output,indent=2);output.write('\n')


def fragments(data):
    offset=0;index=0;sizes=(1,2,17,64,257)
    while offset<len(data):
        size=sizes[index%len(sizes)];yield data[offset:offset+size]
        offset+=size;index+=1


@unittest.skipUnless(os.name=='posix','Run isolated compiler profiles in Linux')
class RecorderTransportTests(unittest.TestCase):
    def command(self,argv,refusal=False,env=None):
        argv=list(map(str,argv))
        completed=subprocess.run(argv,capture_output=True,text=True,timeout=240,env=env)
        receipt('command',{'argv':argv,'returncode':completed.returncode,
                'stdout':completed.stdout,'stderr':completed.stderr})
        if refusal:
            self.assertNotEqual(completed.returncode,0)
            self.assertIn('static assertion failed',completed.stderr)
        else:self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
        return completed

    @staticmethod
    def sanitizers():
        return ['-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-no-pie']

    @staticmethod
    def common(stage):
        return ['g++','-std=c++17','-O1','-Wall','-Wextra','-Wpedantic','-Werror',
                '-fno-exceptions','-fno-rtti','-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS',
                '-DMATCH=0','-DMOTORS_ALLOWED=0','-I',stage/'src','-I',stage,
                '-I',stage/'bench/recorder/src','-isystem',ROOT/'host/third_party']

    @staticmethod
    def owners(stage):
        files=[*sorted((stage/'src/core').glob('*.cpp')),
               *sorted((stage/'bench/recorder/src').glob('*.cpp'))]
        files += [stage/'src/hal'/name for name in
                  ('motors.cpp','recorder_frames.cpp','recorder.cpp','recorder_csv.cpp','recorder_dump.cpp')]
        files += [stage/'src/app/transaction.cpp',stage/'src/app/transaction_service.cpp']
        return files

    def copy_inputs(self,stage):
        for folder in ('src','tests','bench/recorder'):
            shutil.copytree(ROOT/folder,stage/folder,ignore=shutil.ignore_patterns('__pycache__'))
        (stage/'Arduino.h').write_text('#pragma once\nunsigned long micros();\n')
        (stage/'main.cc').write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
        hashes={str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest()
                for folder in (stage/'src',stage/'bench/recorder',stage/'tests/fixtures/recorder_transport')
                for p in sorted(folder.rglob('*')) if p.is_file()}
        hashes['tests/test_recorder_transport.cpp']=hashlib.sha256((stage/'tests/test_recorder_transport.cpp').read_bytes()).hexdigest()
        receipt('opaque_source_copy',hashes)

    def test_full_actual_pipeline_normal_and_sanitized_strict_receiver(self):
        with tempfile.TemporaryDirectory(prefix='d116-pipeline-',dir='/dev/shm') as temporary:
            stage=Path(temporary);self.copy_inputs(stage)
            common=self.common(stage)+['-DD116_ALLOCATION_GUARD',
                   '-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free']
            for label,flags in (('normal',[]),('asan_ubsan',self.sanitizers())):
                with self.subTest(profile=label):
                    binary=stage/label;output=stage/(label+'_outputs');output.mkdir()
                    self.command([*common,*flags,*self.owners(stage),stage/'tests/test_recorder_transport.cpp',
                                  stage/'main.cc','-o',binary])
                    env=dict(os.environ,D116_OUTPUT=str(output))
                    try:
                        result=self.command([binary,'--no-colors','--order-by=file'],env=env)
                    finally:
                        shutil.copytree(output,RAW/f'{label}_exports_{time.time_ns()}')
                    self.assertIn('Status: SUCCESS!',result.stdout)
                    print(label+': '+' | '.join(s for s in result.stdout.splitlines()
                          if 'test cases:' in s or 'assertions:' in s),flush=True)
                    for name in ('positive','partial'):self.compare_complete(output,name)
                    self.assertEqual((output/'positive.wire').read_bytes(),(output/'partial.wire').read_bytes())
                    self.compare_slow(output)
            for motor,match in ((1,0),(0,1),(1,1)):
                base=[f for f in self.common(stage) if f not in ('-DMATCH=0','-DMOTORS_ALLOWED=0')]
                self.command([*base,f'-DMATCH={match}',f'-DMOTORS_ALLOWED={motor}',
                              '-fsyntax-only',stage/'bench/recorder/src/recorder_transport.cpp'],refusal=True)

    def expected_csv(self,output,label):
        meta=json.loads((output/(label+'.json')).read_text())
        raw=(output/(label+'.frames')).read_bytes();self.assertEqual(len(raw),5001*26)
        frames=bytearray(FRAME_HEADER)
        for ordinal,start in enumerate(range(0,len(raw),26)):
            data=raw[start:start+25];status=raw[start+25]
            self.assertEqual(status,0)
            values=[1,ordinal,status,*FRAME.unpack(data),data.hex()]
            frames.extend((','.join(map(str,values))+'\n').encode())
        events=bytearray(EVENT_HEADER);raw_events=(output/(label+'.events')).read_bytes()
        self.assertEqual(len(raw_events)%8,0)
        for ordinal,start in enumerate(range(0,len(raw_events),8)):
            data=raw_events[start:start+8];values=[1,ordinal,*EVENT.unpack(data),data.hex()]
            events.extend((','.join(map(str,values))+'\n').encode())
        self.assertEqual(len(meta['summary']),36)
        summary=SUMMARY_HEADER+(','.join(map(str,meta['summary']))+'\n').encode()
        return meta,bytes(frames),bytes(events),summary

    def compare_complete(self,output,label):
        sys.path.insert(0,str(ROOT/'tools'));receiver=importlib.import_module('dump_match')
        validator=importlib.import_module('validate_csv_bundle')
        meta,frames,events,summary=self.expected_csv(output,label)
        wire=(output/(label+'.wire')).read_bytes();parser=receiver.Parser()
        for part in fragments(wire):self.assertIsNone(parser.feed(part))
        capture=parser.finish()
        self.assertEqual((capture.session,capture.epoch,capture.origin,capture.log_hz),(202472,69,1,25))
        self.assertEqual((capture.frame_capacity,capture.event_capacity),(5001,4096))
        self.assertEqual((capture.frame_count,capture.event_count,capture.mode),(5001,meta['events'],1))
        self.assertEqual((capture.frames,capture.events,capture.summary),(frames,events,summary))
        crc=zlib.crc32(wire[:wire.rfind(b'END,')]);self.assertEqual(capture.crc32,crc)
        self.assertEqual(meta['crc'],crc);self.assertEqual(meta['bytes'],len(wire))
        self.assertEqual(meta['largest_offer'],64)
        destination=receiver.save_capture(fragments(wire),output/(label+'_received'))
        files={role:next(destination.glob('*_'+role+'.csv')) for role in ('frames','events','summary')}
        for role,expected in (('frames',frames),('events',events),('summary',summary)):
            self.assertEqual(files[role].read_bytes(),expected)
        report=validator.validate_bundle(files['frames'],files['events'],files['summary'],destination/'manifest.json')
        self.assertEqual((report['format_integrity'],report['consistency']),('PASS','PASS'))
        self.assertFalse(report['hardware_acceptance'])
        manifest=json.loads((destination/'manifest.json').read_text())
        self.assertEqual(manifest['origin'],'synthetic')
        if label=='positive':
            estimate=len(wire)+15*meta['write_calls']
            self.assertGreater(estimate,2*300000)
            receipt('wire_accounting',{'payload_bytes':len(wire),'payload_chunks':meta['write_calls'],
                'messagepack_overhead_bytes_per_packet':15,'estimated_native_wire_bytes':estimate,
                'epochs_available':300000,'required_average_wire_bytes_per_epoch':estimate/300000,
                'scope':'Protocol byte accounting; no native throughput or physical measurement.'})

    def compare_slow(self,output):
        sys.path.insert(0,str(ROOT/'tools'));receiver=importlib.import_module('dump_match')
        meta,_,_,_=self.expected_csv(output,'slow')
        wire=(output/'slow.wire').read_bytes();self.assertEqual(len(wire),300000)
        self.assertEqual(wire,(output/'positive.wire').read_bytes()[:300000])
        self.assertEqual(meta['write_calls'],300000);self.assertEqual(meta['bytes'],300000)
        self.assertEqual(meta['summary'][27],5001);self.assertEqual(meta['summary'][16],194901)
        parser=receiver.Parser()
        for part in fragments(wire):parser.feed(part)
        with self.assertRaises(receiver.CaptureError):parser.finish()
        with self.assertRaises(receiver.CaptureError):receiver.save_capture(fragments(wire),output/'slow_received')
        children=list((output/'slow_received').iterdir());self.assertEqual(len(children),1)
        self.assertIn('partial',children[0].name)

    def test_invalid_copied_config_profiles_never_initialize(self):
        profiles=(('TICK_US',0),('BTN_DEBOUNCE_MS',0),('BTN_LONG_MS',0),
                  ('APP_CLOCK_STALL_MAX_POLLS',0),('BTN_LONG_MS',24),
                  ('LOG_FRAME_WINDOW_MS',5099),('DUMP_TOTAL_MS',2000000))
        with tempfile.TemporaryDirectory(prefix='d116-config-',dir='/dev/shm') as temporary:
            stage=Path(temporary);self.copy_inputs(stage);original=(stage/'src/config.h').read_bytes()
            for key,value in profiles:
                with self.subTest(key=key,value=value):
                    pattern=rb'(inline constexpr std::uint32_t '+key.encode()+rb' = )\d+U;'
                    altered,count=re.subn(pattern,lambda m:m[1]+str(value).encode()+b'U;',original)
                    self.assertEqual(count,1);(stage/'src/config.h').write_bytes(altered)
                    binary=stage/(key+str(value))
                    self.command([*self.common(stage),*self.owners(stage),
                                  stage/'tests/fixtures/recorder_transport/config.cc',stage/'main.cc','-o',binary])
                    self.command([binary,'--no-colors'])

    def test_actual_factory_and_default_sketch_remain_passive(self):
        with tempfile.TemporaryDirectory(prefix='d116-native-',dir='/dev/shm') as temporary:
            stage=Path(temporary);self.copy_inputs(stage)
            shutil.copyfile(stage/'bench/recorder/recorder.ino',stage/'bench/recorder/sketch.cpp')
            sources=[*self.owners(stage),stage/'src/app/dump_port_unoq.cpp',stage/'bench/recorder/sketch.cpp',
                     stage/'tests/fixtures/recorder_transport/native.cc']
            for label,flags in (('normal',[]),('asan_ubsan',self.sanitizers())):
                with self.subTest(profile=label):
                    binary=stage/label
                    self.command([*self.common(stage),*flags,'-DARDUINO_ARCH_ZEPHYR',*sources,'-o',binary])
                    result=self.command([binary]);self.assertEqual(result.stdout,'');self.assertEqual(result.stderr,'')
            for motor,match in ((1,0),(0,1),(1,1)):
                base=[f for f in self.common(stage) if f not in ('-DMATCH=0','-DMOTORS_ALLOWED=0')]
                self.command([*base,f'-DMATCH={match}',f'-DMOTORS_ALLOWED={motor}','-DARDUINO_ARCH_ZEPHYR',
                              '-fsyntax-only',stage/'bench/recorder/sketch.cpp'],refusal=True)


if __name__=='__main__':
    unittest.main(verbosity=2)
