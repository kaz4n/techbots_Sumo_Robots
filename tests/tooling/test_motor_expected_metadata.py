# Freezes D202 expectations from its contract and the committed D201 predecessor.
# Checks fixed numeric metadata and complete four-way native diagnostic transcripts.
# Linux-only controlled fixtures use exclusive RAM scratch and serial bounded tools.
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'state/analysis/P7_motor_expected_metadata_raw'
FREEZE = RAW / 'independent_freeze02.json'
CONTRACT = 'state/analysis/P7_motor_expected_metadata_contract.md'
CONTRACT_SHA = '2abaae2995e1938e4c7f0dcef2522c9334d9550bd77d9da37727b47a7940a846'
PREDECESSOR_BLOB = 'cd825eb8f5496d023062d69a2d98bc2474492fde'
PREDECESSOR_SHA = 'f1ee755a7bddec38e86545f4c5e5457b3ed5e5f1bdd7f5cf368cc77f91664f5e'
PREDECESSOR_BYTES = 19185
D197 = 'tests/tooling/test_motor_settle_probe.py'
D197_SHA = '29c6cac3d837263d7e1a90b2a677dade79915e02970cea53e839933ec502a183'
MANIFEST = 'state/analysis/P7_motor_settle_compile_raw/inputs_static.json'
MANIFEST_SHA = 'aa314548521968fd3b1b7b1ef415da3c72c90a6bc914d0a9204ff707bcd7d282'
SUBJECT = 'src/hal/motor_port_unoq.cpp'
CASES = ROOT / 'tests/native_motor_expected_metadata_cases.cc'
SHIM = ROOT / 'tests/native_motor_expected_metadata_shim.h'
RECEIPT_ENV = 'SUMO_EXPECTED_METADATA_RECEIPT_DIR'
CONFIG_OLD = b'inline constexpr std::uint32_t MOTOR_PWM_HZ = 10000U; // Hz'
DEFAULTS = {'HCLK':160000000, 'AHB':1, 'APB1':1, 'APB2':1,
            'PSC0':63, 'PSC1':4, 'PSC2':4, 'DOMAIN0':14, 'DOMAIN1':13, 'DOMAIN2':13,
            'SELECTOR0':255, 'SELECTOR1':255, 'SELECTOR2':255,
            'DIV0':0, 'DIV1':0, 'DIV2':0, 'CARRIER':10000}
# Numeric results are an independent, explicit table, not computed by subject code.
# Each row is name, isolated metadata changes, rates[0..2], periods[0..2].
MATRIX = (
 ('default_apb1', {}, (2500000,32000000,32000000), (250,3200,3200)),
 ('both_apb2', {'APB1':2,'APB2':2}, (2500000,32000000,32000000), (250,3200,3200)),
 ('both_apb4', {'APB1':4,'APB2':4}, (1250000,16000000,16000000), (125,1600,1600)),
 ('both_apb8', {'APB1':8,'APB2':8}, (625000,8000000,8000000), (0,800,800)),
 ('both_apb16', {'APB1':16,'APB2':16}, (312500,4000000,4000000), (0,400,400)),
 ('apb1_zero', {'APB1':0}, (2500000,0,0), (250,0,0)),
 ('apb1_nonpower', {'APB1':3}, (2500000,0,0), (250,0,0)),
 ('apb1_over16', {'APB1':32}, (2500000,0,0), (250,0,0)),
 ('apb2_zero', {'APB2':0}, (0,32000000,32000000), (0,3200,3200)),
 ('apb2_nonpower', {'APB2':3}, (0,32000000,32000000), (0,3200,3200)),
 ('apb2_over16', {'APB2':32}, (0,32000000,32000000), (0,3200,3200)),
 ('apb1_nondivisible', {'HCLK':160000001,'APB1':2,'PSC0':0,'PSC1':0,'PSC2':0,'CARRIER':1}, (160000001,0,0), (0,0,0)),
 ('apb2_nondivisible', {'HCLK':160000001,'APB2':2,'PSC0':0,'PSC1':0,'PSC2':0,'CARRIER':1}, (0,160000001,160000001), (0,0,0)),
 ('hclk_zero', {'HCLK':0}, (0,0,0), (0,0,0)),
 ('hclk_80mhz', {'HCLK':80000000}, (1250000,16000000,16000000), (125,1600,1600)),
 ('ahb_zero', {'AHB':0}, (0,0,0), (0,0,0)),
 ('ahb_two_does_not_divide_hclk_twice', {'AHB':2}, (2500000,32000000,32000000), (250,3200,3200)),
 ('prescalers_zero', {'PSC0':0,'PSC1':0,'PSC2':0}, (160000000,160000000,160000000), (16000,16000,16000)),
 ('prescalers_asymmetric', {'PSC0':0,'PSC1':7,'PSC2':15}, (160000000,20000000,10000000), (16000,2000,1000)),
 ('prescalers_max', {'HCLK':6553600000,'PSC0':65535,'PSC1':65535,'PSC2':65535}, (100000,100000,100000), (10,10,10)),
 ('prescaler0_overmax', {'PSC0':65536}, (0,32000000,32000000), (0,3200,3200)),
 ('prescaler1_overmax', {'PSC1':65536}, (2500000,0,32000000), (250,0,3200)),
 ('prescaler2_overmax', {'PSC2':65536}, (2500000,32000000,0), (250,3200,0)),
 ('prescalers_uint32max', {'PSC0':4294967295,'PSC1':4294967295,'PSC2':4294967295}, (0,0,0), (0,0,0)),
 ('prescaler0_nondivisible', {'PSC0':2}, (0,32000000,32000000), (0,3200,3200)),
 ('prescaler1_nondivisible', {'PSC1':2}, (2500000,0,32000000), (250,0,3200)),
 ('prescaler2_nondivisible', {'PSC2':2}, (2500000,32000000,0), (250,3200,0)),
 ('domain0_wrong', {'DOMAIN0':13}, (0,32000000,32000000), (0,3200,3200)),
 ('domain1_wrong', {'DOMAIN1':14}, (2500000,0,32000000), (250,0,3200)),
 ('domain2_wrong', {'DOMAIN2':14}, (2500000,32000000,0), (250,3200,0)),
 ('selector0_wrong', {'SELECTOR0':254}, (0,32000000,32000000), (0,3200,3200)),
 ('selector1_wrong', {'SELECTOR1':0}, (2500000,0,32000000), (250,0,3200)),
 ('selector2_wrong', {'SELECTOR2':256}, (2500000,32000000,0), (250,3200,0)),
 ('encoded_divisor0', {'DIV0':1}, (0,32000000,32000000), (0,3200,3200)),
 ('encoded_divisor1', {'DIV1':1}, (2500000,0,32000000), (250,0,3200)),
 ('encoded_divisor2', {'DIV2':1}, (2500000,32000000,0), (250,3200,0)),
 ('carrier_zero', {'CARRIER':0}, (2500000,32000000,32000000), (0,0,0)),
 ('carrier_nondivisible', {'CARRIER':3}, (2500000,32000000,32000000), (0,0,0)),
 ('period_one', {'HCLK':10000,'PSC0':0,'PSC1':0,'PSC2':0}, (10000,10000,10000), (1,1,1)),
 ('period_65536', {'HCLK':655360000,'PSC0':0,'PSC1':0,'PSC2':0}, (655360000,655360000,655360000), (65536,65536,65536)),
 ('period_65537', {'HCLK':655370000,'PSC0':0,'PSC1':0,'PSC2':0}, (655370000,655370000,655370000), (0,0,0)),
 ('period_below_one', {'HCLK':5000,'PSC0':0,'PSC1':0,'PSC2':0}, (5000,5000,5000), (0,0,0)),
 ('hclk_above_uint32', {'HCLK':4294967296,'PSC0':65535,'PSC1':65535,'PSC2':65535,'CARRIER':1}, (65536,65536,65536), (65536,65536,65536)),
 ('hclk_uint64max', {'HCLK':18446744073709551615,'PSC0':0,'PSC1':0,'PSC2':0,'CARRIER':4294967295}, (18446744073709551615,18446744073709551615,18446744073709551615), (0,0,0)),
 ('carrier_uint32max_period_one', {'HCLK':4294967295,'PSC0':0,'PSC1':0,'PSC2':0,'CARRIER':4294967295}, (4294967295,4294967295,4294967295), (1,1,1)),
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(name, digest):
    raw = (ROOT / name).read_bytes()
    if sha(raw) != digest:
        raise AssertionError('Frozen dependency changed: ' + name)
    return raw


def function(text, name):
    pattern = r'(?m)^(?:constexpr\s+)?std::uint(?:32|64)_t\s+' + name + r'\(std::uint32_t timer\)\s*\{'
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise AssertionError('Expected one exact-signature function: ' + name)
    match = matches[0]
    depth = 1
    for end in range(match.end(), len(text)):
        depth += (text[end] == '{') - (text[end] == '}')
        if depth == 0:
            return text[match.start():end + 1], text[match.end():end]
    raise AssertionError('Unterminated function: ' + name)


class MotorExpectedMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sys.platform != 'linux' or not hasattr(os, 'memfd_create'):
            raise RuntimeError('Linux native fixture/memfd required; no silent skip')
        if not sys.dont_write_bytecode or not sys.flags.dont_write_bytecode:
            raise RuntimeError('Frozen oracle requires Python -B')
        cls.freeze = json.loads(FREEZE.read_bytes())
        cls.verify_frozen()
        raw = checked(D197, D197_SHA)
        cls.old = types.ModuleType('_d202_pinned_d197_support')
        cls.old.__file__ = str(ROOT / D197)
        exec(compile(raw, cls.old.__file__, 'exec'), cls.old.__dict__)
        cls.old.MotorSettleProbeTests.verify_unchanged()
        cls.compiler, cls.nm = shutil.which('g++'), shutil.which('nm')
        if not cls.compiler or not cls.nm or shutil.disk_usage('/dev/shm').free < 134217728:
            raise RuntimeError('g++, nm and 128MiB free /dev/shm are required')
        folder = os.environ.get(RECEIPT_ENV)
        if not folder:
            raise RuntimeError('Set SUMO_EXPECTED_METADATA_RECEIPT_DIR to a fresh evidence owner')
        cls.receipt_dir = Path(folder)
        cls.receipt_dir.mkdir(parents=False, exist_ok=False)
        cls.stage = Path(tempfile.mkdtemp(prefix='sumox-d202-', dir='/dev/shm'))
        cls.addClassCleanup(cls.clean_owned)
        cls.environment = dict(os.environ, TMPDIR=str(cls.stage), UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        cls.sequence = 0
        cls.subject = (ROOT / SUBJECT).read_bytes()
        cls.subject_pin = {'bytes':len(cls.subject), 'sha256':sha(cls.subject)}
        cls.previous = cls.command(['git','cat-file','blob',PREDECESSOR_BLOB], 'predecessor').stdout
        if len(cls.previous) != PREDECESSOR_BYTES or sha(cls.previous) != PREDECESSOR_SHA:
            raise AssertionError('Exact committed predecessor changed')
        cls.header_pins = {n:d for n,d in json.loads(checked(MANIFEST, MANIFEST_SHA))['files'].items()
                           if n.startswith('src/') and n.endswith('.h')}
        cls.trees, cls.common, cls.binaries = {}, [], {}

    @classmethod
    def verify_frozen(cls):
        for name, pin in cls.freeze['files'].items():
            raw = (ROOT / name).read_bytes()
            if len(raw) != pin['bytes'] or sha(raw) != pin['sha256']:
                raise AssertionError('Independent frozen input changed: ' + name)

    @classmethod
    def clean_owned(cls):
        cls.verify_frozen()
        if (ROOT / SUBJECT).read_bytes() != cls.subject:
            raise AssertionError('Current implementation changed during oracle')
        target = cls.stage.resolve()
        if target.parent != Path('/dev/shm').resolve() or not target.name.startswith('sumox-d202-') or cls.stage.is_symlink():
            raise AssertionError('Unsafe fixture cleanup target')
        (cls.receipt_dir / 'closing.json').write_text(json.dumps({
            'schema':'d202-independent-host-closing-v1','inputs_unchanged':True,
            'current_subject':cls.subject_pin,'scratch':str(target),'commands':cls.sequence,
            'cleanup':'remove only this uniquely owned RAM fixture tree'},indent=2)+'\n')
        shutil.rmtree(target)
        if target.exists():
            raise AssertionError('Owned fixture scratch remains')

    @classmethod
    def command(cls, argv, label, *, success=True, **kwargs):
        started = time.monotonic()
        try:
            result = subprocess.run(list(map(str,argv)),cwd=ROOT,env=cls.environment,
                                    capture_output=True,timeout=120,**kwargs)
        except subprocess.TimeoutExpired as error:
            result = subprocess.CompletedProcess(argv,-1,error.stdout or b'',error.stderr or b'')
            cls.receipt(argv,label,result,time.monotonic()-started)
            raise
        cls.receipt(argv,label,result,time.monotonic()-started)
        if success and result.returncode:
            raise AssertionError(label + ': ' + result.stderr[-8000:].decode('utf-8','replace'))
        return result

    @classmethod
    def receipt(cls, argv, label, result, elapsed):
        cls.sequence += 1
        record = dict(schema='d202-independent-host-command-v1',label=label,argv=list(map(str,argv)),
                      returncode=result.returncode,elapsed_seconds=elapsed,current_subject=cls.subject_pin,
                      stdout_bytes=len(result.stdout),stdout_sha256=sha(result.stdout),
                      stderr_bytes=len(result.stderr),stderr_sha256=sha(result.stderr),
                      stdout_failure_prefix=result.stdout[:2000].decode('utf-8','replace') if result.returncode else '',
                      stderr_prefix=result.stderr[:8000].decode('utf-8','replace'))
        with (cls.receipt_dir / f'{cls.sequence:04d}-{label}.json').open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(record,stream,indent=2,sort_keys=True); stream.write('\n')

    @classmethod
    def flags(cls, probe, tree=None, match=0, motors=0):
        flags = cls.old.MotorSettleProbeTests.flags.__func__(cls,probe,match,motors)
        return flags[:1] + (['-I',str(tree / 'src')] if tree else []) + flags[1:]

    @classmethod
    def tree(cls, carrier):
        if carrier in cls.trees:
            return cls.trees[carrier]
        tree = cls.stage / ('carrier-' + str(carrier))
        projected = None
        for name,digest in cls.header_pins.items():
            raw = checked(name,digest)
            if name == 'src/config.h':
                if raw.count(CONFIG_OLD) != 1:
                    raise AssertionError('Exact isolated carrier projection seam changed')
                raw = raw.replace(CONFIG_OLD, CONFIG_OLD.replace(b'10000U',str(carrier).encode()+b'U'))
                projected = {'before_sha256':digest,'after_sha256':sha(raw),'carrier':carrier,'count':1}
            path = tree / name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(raw)
        for name,raw in [('previous',cls.previous),('current',cls.subject)]:
            (tree / 'src/hal' / (name + '.cpp')).write_bytes(raw)
        with (cls.receipt_dir / ('config-' + str(carrier) + '.json')).open('x',encoding='utf-8') as stream:
            json.dump(projected,stream,indent=2);stream.write('\n')
        cls.trees[carrier] = tree
        return tree

    @classmethod
    def common_objects(cls, full=False):
        sources = [cls.old.FIXTURE / 'native_fixture.cc',ROOT / 'src/hal/native_pins.cpp',
                   ROOT / 'src/hal/motors.cpp',ROOT / 'src/core/opp_fusion.cpp']
        needed = 4 if full else 2
        while len(cls.common) < needed:
            i = len(cls.common);target=cls.stage / f'common-{i}.o'
            cls.command([*cls.flags(0),'-c',sources[i],'-o',target],f'common-{i}')
            cls.common.append(target)
        return cls.common[:needed]

    @classmethod
    def run_binary(cls, binary, label, *arguments):
        fd = os.memfd_create('sumox-d202',flags=0)
        try:
            with os.fdopen(os.dup(fd),'wb') as stream:
                stream.write(binary.read_bytes())
            return cls.command([f'/proc/self/fd/{fd}',*arguments],label,pass_fds=(fd,))
        finally:
            os.close(fd)

    def region(self):
        before = self.previous.decode();after = self.subject.decode()
        start = before.index('std::uint64_t candidateRate(std::uint32_t timer) {')
        end = before.index('std::uint32_t pinMask(std::uint32_t pin) {')
        self.assertTrue(after.startswith(before[:start]))
        self.assertTrue(after.endswith(before[end:]))
        return before[start:end],after[start:len(after)-len(before[end:])]

    def test_01_exact_outside_region_and_derivation_bodies(self):
        before,after = self.region()
        for kind in ['Rate','Period']:
            prior,body = function(before,'candidate'+kind)
            current,observed = function(after,'expected'+kind)
            self.assertEqual(observed,body.replace('candidateRate(', 'expectedRate('))
            self.assertTrue(current.startswith('constexpr std::uint'+('64' if kind=='Rate' else '32')+'_t expected'+kind+'('))
            runtime,unused = function(after,'candidate'+kind)
            self.assertEqual(runtime.split('{',1)[0],prior.split('{',1)[0])
        remaining = after
        for name in ['expectedRate','expectedPeriod','candidateRate','candidatePeriod']:
            span,unused=function(after,name);self.assertEqual(remaining.count(span),1);remaining=remaining.replace(span,'',1)
        remaining=re.sub(r'/\*.*?\*/|//[^\n]*','',remaining,flags=re.S)
        self.assertEqual(remaining.strip(),'','No new region state, initializer or extra function')

    def test_02_runtime_helpers_force_three_automatic_constexpr_scalar_results(self):
        unused,after=self.region()
        for kind,width in [('Rate','64'),('Period','32')]:
            unused,body=function(after,'candidate'+kind)
            clean=re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S)
            pattern=r'constexpr\s+(?:auto|std::uint'+width+r'_t)\s+([A-Za-z_]\w*)\s*(?:=\s*|\{\s*)expected'+kind+r'\(\s*([012])U?\s*\)\s*\}?\s*;'
            matches=list(re.finditer(pattern,clean))
            self.assertEqual(len(matches),3)
            self.assertEqual(sorted(m.group(2) for m in matches),['0','1','2'])
            names={m.group(1) for m in matches};self.assertEqual(len(names),3)
            rest=re.sub(pattern,'',clean)
            identifiers=set(re.findall(r'[A-Za-z_]\w*',re.sub(r'\b\d+U?\b','',rest)))
            self.assertLessEqual(identifiers,names|{'timer','if','else','return','switch','case','default'})
            self.assertNotRegex(rest,r'[\[\]*/%&|]|\b(?:static|new|volatile|thread_local)\b')
            self.assertIn('return',rest)

    def test_03_all_21_full_transcripts_previous_current_probe0_probe1(self):
        tree=self.tree(10000);common=self.common_objects(full=True)
        wrappers='-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free,--wrap=_Z6microsv'
        for version in ['previous','current']:
            for probe in [0,1]:
                name=f'{version}-probe{probe}';binary=self.stage / name
                self.command([*self.flags(probe,tree),tree/'src/hal'/f'{version}.cpp',self.old.CASES,
                              *common,wrappers,'-o',binary],'transcript-build-'+name)
                self.binaries[name]=binary
        for scenario in self.old.SCENARIOS:
            outputs={}
            for name,binary in self.binaries.items():
                reply=self.run_binary(binary,'transcript-'+scenario+'-'+name,scenario)
                self.assertEqual(reply.stderr,b'');self.assertIn(b'SEGMENT ',reply.stdout)
                outputs[name]=reply.stdout
            self.assertEqual(len(outputs),4)
            for name,value in outputs.items():self.assertEqual(value,outputs['previous-probe0'],(scenario,name))
            print(scenario+': exact four-way transcript '+sha(outputs['previous-probe0']),flush=True)

    def test_04_explicit_numeric_matrix_and_whole_port_zeroing(self):
        common=self.common_objects();wrappers='-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free'
        for name,changes,rates,periods in MATRIX:
            metadata={**DEFAULTS,**changes};tree=self.tree(metadata['CARRIER']);outputs={}
            definitions=[f'-DD202_{k}={v}'+('ULL' if k=='HCLK' else 'U') for k,v in metadata.items() if k!='CARRIER']
            for version in ['previous','current']:
                for probe in [0,1]:
                    label=f'matrix-{name}-{version}-{probe}';binary=self.stage / 'matrix-executable'
                    warning_flags=['-Wno-error=div-by-zero'] if name=='carrier_zero' else []
                    build=self.command([*self.flags(probe,tree),*warning_flags,*definitions,'-include',SHIM,
                        '-DD202_SUBJECT="'+str(tree/'src/hal'/f'{version}.cpp')+'"',CASES,*common,wrappers,'-o',binary],label+'-build')
                    if name=='carrier_zero':
                        self.assertEqual(metadata['CARRIER'],0)
                        self.assertEqual(build.stderr.count(b'warning:'),1)
                        self.assertEqual(build.stderr.count(b'warning: division by zero [-Wdiv-by-zero]'),1)
                        self.assertLessEqual(len(build.stderr),8000,'Full warning must fit the retained command receipt')
                    reply=self.run_binary(binary,label+'-run');self.assertEqual(reply.stderr,b'')
                    value=json.loads(reply.stdout);self.assertEqual(set(value),{'rates','periods','port','native_bytes','port_bytes','calls','allocations'})
                    self.assertEqual(value['rates'],[*rates,0,0],label)
                    self.assertEqual(value['periods'],[*periods,0,0],label)
                    expected_port=[periods[i] for i in (1,0,1,2)] if all(periods) else [0,0,0,0]
                    self.assertEqual(value['port'],expected_port,label)
                    self.assertEqual((value['calls'],value['allocations']),(0,0))
                    outputs[(version,probe)]=reply.stdout
                    binary.unlink()
            for value in outputs.values():self.assertEqual(value,outputs[('previous',0)],name)
            print(name+': numeric rates/periods + whole-Port + four-way equality PASS',flush=True)

    def test_05_probe0_report_absent_probe1_single_zero_initialized_report_present(self):
        tree=self.tree(10000)
        for version in ['previous','current']:
            for probe in [0,1]:
                label=f'probe-storage-{version}-{probe}';obj=self.stage/(label+'.o')
                self.command([*self.flags(probe,tree),'-c',tree/'src/hal'/f'{version}.cpp','-o',obj],label+'-build')
                raw=self.command([self.nm,'-S','-C','--defined-only',obj],label+'-symbols').stdout.decode()
                self.assertNotRegex(raw,r'_GLOBAL__sub_I|__static_initialization_and_destruction')
                if probe==0:
                    self.assertNotRegex(raw,r'settle[Pp]robe|settle_probe')
                else:
                    rows=[m.groups() for m in re.finditer(r'(?m)^([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([A-Za-z])\s+(.+)$',raw)]
                    reports=[row for row in rows if row[3]=='motors::(anonymous namespace)::settle_probe_report']
                    accessors=[row for row in rows if row[3]=='motors::settleProbeReport()']
                    self.assertEqual(len(reports),1);self.assertEqual(int(reports[0][1],16),28)
                    self.assertIn(reports[0][2],('b','B'))
                    self.assertEqual(len(accessors),1);self.assertIn(accessors[0][2],('t','T'))
                    self.assertGreater(int(accessors[0][1],16),0)
                obj.unlink()

    def test_06_public_probe_exclusion_and_inert_guards_remain(self):
        include=b'#include "hal/motor_settle_probe.h"\n'
        use=include+b'#include "hal/motor_port_unoq.h"\nauto pointer=&motors::settleProbeReport;\n'
        result=self.command([*self.flags(0),'-x','c++','-fsyntax-only','-'],'probe0-interface',success=False,input=use)
        self.assertNotEqual(result.returncode,0);self.assertIn(b'settleProbeReport',result.stderr)
        for match,motors in [(1,0),(0,1),(1,1)]:
            result=self.command([*self.flags(1,match=match,motors=motors),'-x','c++','-fsyntax-only','-'],
                                f'inert-{match}-{motors}',success=False,input=include)
            self.assertNotEqual(result.returncode,0)
            self.assertIn(b'Motor fault probe is exclusive and requires inert flags',result.stderr)

    def test_07_all_frozen_headers_config_d197_and_locked_fixtures_preserved(self):
        self.verify_frozen();self.old.MotorSettleProbeTests.verify_unchanged()
        self.assertEqual((ROOT/SUBJECT).read_bytes(),self.subject)
        self.assertEqual(len(self.old.SCENARIOS),21)
        self.assertEqual(len(MATRIX),45)


if __name__=='__main__':
    unittest.main(verbosity=2)
