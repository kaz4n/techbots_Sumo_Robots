# Tests ordinary ABI semantics from the adopted D209 contract, not implementation.
# Retains scoped descriptor/lifecycle oracles and builds independent two-object packets.
# Root runs frozen host suites; every compiler, transport and network endpoint is blocked.
import ast
import base64
import builtins
from contextlib import ExitStack
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).absolute().parents[2]
RAW = 'state/analysis/P7_ordinary_app_static_compile_raw'
SUBJECT = RAW + '/inspect_static_abi.py'
CONTRACT = 'state/analysis/P7_ordinary_app_abi_contract.md'
FIXTURE = RAW + '/abi_fixture_derivation01.json'
FIXTURE_PIN = {'bytes': 51052, 'sha256': '56761c40ce35a10a91712acb1901671a9492a61253d929efc260d0dbeedca1ef'}
PLAN = None
BASE = None
HEAD = '1234567890abcdef1234567890abcdef12345678'
SOURCE = '9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a'
OWNER = '/home/arduino/sumox26_codex_build/ordinary-app-static01'
SCOPE = '/home/arduino/sumox26_codex_build/ordinary-app-abi-static01'
REJECT = (ValueError, TypeError, RuntimeError, OSError, SystemExit, KeyError)
ADDRESS = 0x20030000  # Synthetic; unrelated to saved object coordinates.
TYPES = ('app::Runtime', 'app::RuntimeReport', 'app::Transaction', 'app::TransactionReport',
         'motors::MotorGate', 'motors::UnoQPort', 'motors::Result', 'motors::HaltResult',
         'fsm::RobotResult', 'fsm::PreviousTick', 'core::Outputs', 'app::SetupGrants', 'bool')
WINDOWS = {'report_': 'app::RuntimeReport', 'transaction_.report_': 'app::TransactionReport',
           'transaction_.previous_': 'fsm::PreviousTick', 'transaction_.gate_': 'motors::MotorGate',
           'grants_': 'app::SetupGrants', 'attempted_': 'bool'}
ENUMS = {
    'app::RuntimePhase': ('NOT_STARTED', 'RUNNING', 'STOPPED', 'FAULT', 'STOP_OBSERVING'),
    'app::RuntimeFault': ('NONE', 'PORT', 'CLOCK', 'SERVICE_LIMIT', 'TRANSACTION', 'PROJECTION'),
    'app::Phase': ('NOT_INITIALIZED', 'IDLE', 'ACQUIRING', 'DECIDED', 'FAULT'),
    'app::Fault': ('NONE', 'SETUP', 'ORDER', 'CLOCK', 'IDENTITY', 'RECEIPT', 'ABORTED'),
    'motors::Fault': ('NONE', 'NOT_INITIALIZED', 'PORT', 'IO', 'COMMAND', 'TOKEN', 'STOPPED'),
    'core::State': ('BOOT', 'IDLE', 'COUNTDOWN', 'OPENER', 'SEARCH', 'TRACK', 'ATTACK',
                    'DEFEND_TURN', 'EDGE_ESCAPE', 'REFLANK', 'STOPPED', 'DRIVE_TEST'),
    'edge::EscapeFault': ('NONE', 'WHITE_PATTERN', 'REPLAN_LIMIT', 'PERMISSION_LOST', 'INVALID_CONTEXT'),
}
SYMBOLS = {'runtime': '_ZN12_GLOBAL__N_17runtimeE', 'motor_port': '_ZN12_GLOBAL__N_110motor_portE'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def identity(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}


def checked(path, pin):
    raw = Path(path).read_bytes()
    if identity(raw) != pin:
        raise AssertionError('Frozen oracle input differs: ' + str(path))
    return raw


def plan():
    global PLAN
    if PLAN is None:
        if FIXTURE_PIN is None:
            raise AssertionError('Oracle freeze is unfinished')
        PLAN = json.loads(checked(ROOT / FIXTURE, FIXTURE_PIN))
    return PLAN


def original(path):
    return checked(ROOT / path, plan()['inputs'][path])


def subject_raw():
    return checked(ROOT / SUBJECT, plan()['subject_expected'])


def module(raw, path, name):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    value.__dict__['__builtins__'] = dict(vars(builtins))
    exec(compile(raw, str(path), 'exec'), value.__dict__)
    return value


def project(raw, steps):
    for row in steps:
        old, new = row['old'].encode(), row['new'].encode()
        if raw.count(old) != row['count']:
            raise AssertionError('Independent projection count differs')
        raw = raw.replace(old, new)
    return raw


def spans(raw):
    lines = raw.splitlines(keepends=True)
    result = {}
    for node in ast.parse(raw).body:
        if isinstance(node, ast.FunctionDef):
            result[node.name] = b''.join(lines[node.lineno-1:node.end_lineno])
        elif isinstance(node, ast.Assign):
            result[','.join(ast.unparse(t) for t in node.targets)] = b''.join(lines[node.lineno-1:node.end_lineno])
    return result


def expected_expressions():
    expressions = ['set max-value-size 1048576']
    for name in TYPES:
        for label, function in (('SIZE', 'sizeof'), ('ALIGN', 'alignof')):
            expressions += ['echo SUMOX_' + label + ' ' + name + '\\n',
                            'p/d ' + function + '(' + name + ')']
        expressions += ['echo SUMOX_LAYOUT ' + name + '\\n', 'ptype /o ' + name]
    for name in WINDOWS:
        expressions += ['echo SUMOX_OFFSET ' + name + '\\n',
                        'p/d (unsigned long)&((app::Runtime*)0)->' + name]
    for kind, members in ENUMS.items():
        for name in members:
            expressions += ['echo SUMOX_ENUM ' + kind + '::' + name + '\\n',
                            'p/d (unsigned int)' + kind + '::' + name]
    return expressions


def expected_commands():
    prefix = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
    gdb = [prefix + 'gdb', '-nx', '-nh', '-batch', '-iex', 'set auto-load no',
           OWNER + '/build/app.ino_debug.elf', '-ex', 'set language c++',
           '-ex', 'set may-call-functions off']
    for expression in expected_expressions():
        gdb += ['-ex', expression]
    return [[prefix + 'readelf', '--version'], [prefix + 'gdb', '--version'],
            [prefix + 'readelf', '-hSWs', OWNER + '/build/app.ino.elf'], gdb]


def record(argv, text=''):
    raw = text.encode()
    return dict(argv=argv, execution=dict(returncode=0, timed_out=False, reaped=True),
                deadline_seconds=60, reap_seconds=5, stdout_bytes=len(raw),
                stdout_base64=base64.b64encode(raw).decode(), stderr_bytes=0, stderr_base64='')


def text(result, index):
    return base64.b64decode(result['commands'][index]['stdout_base64']).decode()


def replace_text(result, index, value):
    raw = value.encode()
    result['commands'][index].update(stdout_bytes=len(raw), stdout_base64=base64.b64encode(raw).decode())


def numeric(result, label, name, value):
    current = text(result, 3)
    pattern = r'(SUMOX_' + label + ' ' + re.escape(name) + r'\n\$\d+ = )[^\n]+'
    changed, count = re.subn(pattern, lambda match: match[1] + str(value), current)
    if count != 1:
        raise AssertionError('Independent numeric fixture tag is not unique')
    replace_text(result, 3, changed)


def packet(size_token='4096', *, address=ADDRESS, motor_token='40', shift=0, sizes_override=None):
    # Different synthetic coordinates, dimensions and offsets are accepted evidence.
    sizes = dict.fromkeys(TYPES, 32)
    sizes.update({'app::Runtime': 4096, 'app::RuntimeReport': 256, 'app::Transaction': 2048,
                  'app::TransactionReport': 512, 'motors::MotorGate': 128,
                  'motors::UnoQPort': 40, 'app::SetupGrants': 64, 'bool': 1})
    sizes.update(sizes_override or {})
    aligns = dict.fromkeys(TYPES, 4)
    aligns.update({'app::Runtime': 8, 'app::Transaction': 8, 'bool': 1})
    offsets = {'report_': 2048 + shift, 'transaction_.report_': 512 + shift,
               'transaction_.previous_': 1104 + shift, 'transaction_.gate_': 128 + shift,
               'grants_': 2304 + shift, 'attempted_': 2400 + shift}
    lines = []
    for name in TYPES:
        for label, value in (('SIZE', sizes[name]), ('ALIGN', aligns[name])):
            lines += ['SUMOX_' + label + ' ' + name, '$1 = ' + str(value)]
        lines += ['SUMOX_LAYOUT ' + name]
        if name == 'bool':
            lines += ['type = bool']
        else:
            lines += ['/* offset | size */ type = struct ' + name + ' {',
                      '/* 0 | ' + str(sizes[name]) + ' */ unsigned char fixture[' + str(sizes[name]) + '];',
                      '/* total size (bytes): ' + str(sizes[name]) + ' */', '}']
    for name, offset in offsets.items():
        lines += ['SUMOX_OFFSET ' + name, '$2 = ' + str(offset)]
    for kind, names in ENUMS.items():
        for value, name in enumerate(names):
            lines += ['SUMOX_ENUM ' + kind + '::' + name, '$3 = ' + str(value)]
    motor_address = address + 6144
    elf = ('  Type: EXEC (Executable file)\n'
           ' [ 7] .bss NOBITS ' + format(address, 'x') + ' 000100 002000 00 WA 0 0 8\n'
           '  91: ' + format(address, 'x') + ' ' + size_token + ' OBJECT LOCAL DEFAULT 7 ' + SYMBOLS['runtime'] + '\n'
           '  92: ' + format(motor_address, 'x') + ' ' + motor_token + ' OBJECT LOCAL DEFAULT 7 ' + SYMBOLS['motor_port'] + '\n')
    commands = expected_commands()
    result = dict(scope='D209_STATIC_FILE_ONLY_ABI', status='OBSERVED', first_error=None,
                  commands=[record(commands[0], 'controlled readelf\n'), record(commands[1], 'controlled gdb\n'),
                            record(commands[2], elf), record(commands[3], '\n'.join(lines) + '\n')],
                  final_checks=[dict(path='board_identity', status='PASS')])
    layout = dict(sections=[dict(name='.bss', address=address, size=8192)],
                  bss_zero=dict(start=address, end=address + 8192))
    return result, layout


def historical():
    global BASE
    if BASE is not None:
        return BASE
    spec = plan()['historical']['base']
    raw = project(original(spec['source']), spec['steps'])
    if identity(raw) != spec['projected']:
        raise AssertionError('Frozen inherited fixture projection differs')
    base = module(raw, ROOT / spec['source'], '_d209_private_lifecycle_oracle')
    base.WRAPPER, base.CONTRACT, base.CONTRACT_SHA = SUBJECT, CONTRACT, plan()['inputs'][CONTRACT]['sha256']
    base.COMPILE_RAW, base.SOURCE, base.OWNER, base.SCOPE = RAW, SOURCE, OWNER, SCOPE
    base.LAUNCHER = 'tools/compile_ordinary_app_static.py'
    base.PINS = {name: (row['bytes'], row['sha256']) for name, row in plan()['original_inputs'].items()}
    base.packet = lambda *args, **kwargs: packet('0x1000')
    original_setup = base.ContractCase.setUpClass.__func__
    def setup(cls):
        original_setup(cls)
        if identity(cls.raw) != plan()['subject_expected']:
            raise AssertionError('New wrapper differs from metadata-only seal')
    base.ContractCase.setUpClass = classmethod(setup)
    BASE = base
    return base


class OrdinaryAbiContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode:
            raise AssertionError('Use Python -B')
        cls.raw = subject_raw()
        cls.spec = plan()
        cls.base = historical()
        cls.inputs = {name: original(name) for name in cls.spec['original_inputs']}
        cls.contract_raw = original(CONTRACT)
        cls.original_reader = original(cls.spec['reader_base'])
        cls.metadata_intermediate = project(cls.original_reader, cls.spec['reader_metadata_steps'])

    def setUp(self):
        for owner, names in ((subprocess, ('run', 'Popen', 'call', 'check_call', 'check_output')),
                             (socket, ('socket', 'create_connection'))):
            for name in names:
                patch = mock.patch.object(owner, name, side_effect=AssertionError('External operation: ' + name))
                patch.start()
                self.addCleanup(patch.stop)
        self.subject = module(self.raw, ROOT / SUBJECT, '_d209_independent_subject')

    def scratch(self):
        temporary = tempfile.TemporaryDirectory(prefix='sumox-d209-abi-',
                    dir='/dev/shm' if sys.platform == 'linux' else None)
        self.addCleanup(temporary.cleanup)
        return Path(temporary.name).resolve()

    def loaded(self):
        return self.subject.load_reader(root=ROOT)

    def reject(self, call):
        with self.assertRaises(REJECT):
            call()

    def prepared_owner(self):
        return self.base.LifecycleContract.prepared_owner(self)

    def executing_owner(self):
        return self.base.LifecycleContract.executing_owner(self)

    def test_import_is_passive_and_seven_guard_cli_bodies_are_exact(self):
        baseline = spans(original(self.spec['guard_source']))
        with ExitStack() as stack:
            for owner, names in ((Path, ('read_bytes', 'read_text', 'open', 'write_bytes', 'write_text', 'mkdir')),
                                 (builtins, ('open',)), (io, ('open',)), (os, ('open',))):
                for name in names:
                    stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('Import I/O')))
            value = module(self.raw, ROOT / SUBJECT, '_d209_passive')
        for name in ('project_reader', 'load_reader', 'main'):
            self.assertTrue(callable(getattr(value, name)))
        actual = spans(self.raw)
        for name in ('require', '_stamp', '_plain_chain', '_read_handle', 'pinned', '_verify', 'main'):
            self.assertEqual(actual[name], baseline[name], name)

    def test_projection_has_only_four_semantic_spans_after_counted_metadata(self):
        before = spans(self.metadata_intermediate)
        self.subject.__dict__['__builtins__']['exec'] = mock.Mock(side_effect=AssertionError('Projection executed'))
        with ExitStack() as stack:
            for owner, names in ((Path, ('read_bytes', 'read_text', 'open', 'write_bytes', 'write_text', 'mkdir')),
                                 (builtins, ('open',)), (io, ('open',)), (os, ('open',))):
                for name in names:
                    stack.enter_context(mock.patch.object(owner, name, side_effect=AssertionError('Projection I/O')))
            actual = self.subject.project_reader(self.original_reader)
        self.assertIs(type(actual), bytes)
        self.assertEqual(identity(actual), self.spec['projected_expected'])
        after, restored = spans(actual), actual
        for name in ('TYPES', 'WINDOWS', 'queries', 'summarize'):
            self.assertEqual(restored.count(after[name]), 1)
            restored = restored.replace(after[name], before[name], 1)
        self.assertEqual(restored, self.metadata_intermediate)

    def test_projector_refuses_types_drift_occurrences_line_endings_and_projected_input(self):
        raw = self.original_reader
        bad = [None, True, 1, raw.decode(), bytearray(raw), memoryview(raw), b'', raw[:-1], raw+b'\n',
               raw.replace(b'\n', b'\r\n'), self.subject.project_reader(raw)]
        for row in self.spec['reader_metadata_steps']:
            bad += [raw + b'\n# ' + row['old'].encode(), raw.replace(row['old'].encode(), row['new'].encode(), 1)]
        for value in bad:
            if type(value) is bytes and value == raw:
                continue
            with self.subTest(type=type(value).__name__):
                self.reject(lambda: self.subject.project_reader(value))

    def test_main_exact_forms_B_requirement_and_once_only_result_error_delegation(self):
        invalid = [None, (), '--execute', [], ['--execute'], ['--execute','--reviewed-head',HEAD,'extra'],
                   ['--upload','--reviewed-head',HEAD], ['--execute','--head',HEAD],
                   ['--execute','--reviewed-head',HEAD.upper()], ['--execute','--reviewed-head',True]]
        with mock.patch.object(self.subject, 'load_reader') as load:
            for args in invalid:
                self.reject(lambda: self.subject.main(args))
            load.assert_not_called()
            with mock.patch.object(sys, 'dont_write_bytecode', False):
                self.reject(lambda: self.subject.main(['--check-only','--reviewed-head',HEAD]))
            load.assert_not_called()
        for action in ('--check-only','--execute'):
            args = [action,'--reviewed-head',HEAD]
            called = mock.Mock(return_value=object())
            with mock.patch.object(self.subject,'load_reader',return_value=types.SimpleNamespace(main=called)) as load:
                self.assertIs(self.subject.main(args), called.return_value)
                load.assert_called_once_with(root=self.subject.ROOT)
                called.assert_called_once_with(args)
            error = RuntimeError('original main failure')
            called = mock.Mock(side_effect=error)
            with mock.patch.object(self.subject,'load_reader',return_value=types.SimpleNamespace(main=called)):
                with self.assertRaises(RuntimeError) as caught:
                    self.subject.main(args)
                self.assertIs(caught.exception,error)
                called.assert_called_once_with(args)

    def test_every_original_and_contract_is_checked_before_private_execution(self):
        inputs = dict(self.inputs, **{CONTRACT:self.contract_raw})
        for failed in inputs:
            root = self.scratch()
            for name, raw in inputs.items():
                path = root/name
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(raw)
            (root/failed).write_bytes(inputs[failed]+b'\n')
            execute = mock.Mock(side_effect=AssertionError('Unverified private execution'))
            self.subject.__dict__['__builtins__']['exec'] = execute
            with self.subTest(input=failed):
                self.reject(lambda:self.subject.load_reader(root=root))
                execute.assert_not_called()

    def test_loading_is_private_passive_and_preserves_all_current_and_original_pins(self):
        before = dict(sys.modules)
        with mock.patch.object(self.subject,'pinned',wraps=self.subject.pinned) as pins:
            reader = self.loaded()
            self.assertIs(reader.pinned,self.subject.pinned)
        self.assertEqual(dict(sys.modules),before)
        observed = {str(call.args[0]) for call in pins.call_args_list}
        self.assertTrue({str(ROOT/name) for name in (*self.inputs,CONTRACT)} <= observed)
        self.assertEqual(reader.SELF,SUBJECT)
        self.assertEqual(reader.SOURCE,SOURCE)
        self.assertEqual(reader.OWNER,OWNER)
        baseline_tree = ast.parse(self.metadata_intermediate)
        baseline_pins = next(ast.literal_eval(n.value) for n in baseline_tree.body if isinstance(n,ast.Assign)
                             and any(isinstance(t,ast.Name) and t.id=='HARD_PINS' for t in n.targets))
        for name,digest in baseline_pins.items():
            self.assertEqual(reader.HARD_PINS[name],digest)
        for name in (self.spec['reader_base'],self.spec['guard_source'],CONTRACT):
            self.assertEqual(reader.HARD_PINS[name],self.spec['inputs'][name]['sha256'])
        self.assertFalse((ROOT/RAW/'native_abi_static01').exists())

    def test_real_ordinary_admission_rechecks_125_inputs_mapping_and_hash_helper(self):
        reader = self.loaded()
        owner = reader.StaticAbi(HEAD)
        seen,previous = [],sys.getprofile()
        def observe(frame,event,result):
            if event=='return' and frame.f_code.co_name=='app_source_hash':
                seen.append(result)
        try:
            sys.setprofile(observe)
            owner.compiler.CompileDiagnostic.admission(owner)
        finally:
            sys.setprofile(previous)
        self.assertEqual(seen,[SOURCE])
        self.assertEqual(owner.source_sha256,SOURCE)
        self.assertEqual(len(owner.inputs['files']),125)
        self.assertEqual(len(owner.source_names()),105)
        self.assertEqual(len(owner.expected_stage),104)
        self.assertEqual(sum(len(owner.code[name]) for name in owner.source_names()),764405)
        self.assertEqual(owner.sketch,'/home/arduino/sumox26_codex_build/'+SOURCE+'/app')
        for name,digest in owner.inputs['files'].items():
            self.assertEqual(sha(owner.code[name]),digest,name)
        self.assertFalse(owner.claimed)
        self.assertFalse(owner.output.exists())

    def test_current_source_manifest_artifact_and_scope_reject_const_diagnostic_substitutes(self):
        reader,owner = self.prepared_owner()
        owner.prepare()
        oldraw = 'state/analysis/P7_motor_const_compile_raw'
        oldmanifest = self.scratch()/'stale.json'
        oldmanifest.write_bytes(original(oldraw+'/inputs_static.json'))
        stale = reader.StaticAbi(HEAD)
        stale.inputs_path = oldmanifest
        self.reject(lambda:stale.compiler.CompileDiagnostic.admission(stale))
        self.reject(lambda:owner.compiler.CompileDiagnostic.validate_artifact_reply(
            owner,original(oldraw+'/native_static01/artifacts.json').decode()))
        self.assertEqual(owner.remote,SCOPE)
        self.assertEqual(reader.OWNER,OWNER)
        for raw in ('P7_app_motor_fault_compile_raw','P7_app_motor_observe_compile_raw',
                    'P7_motor_settle_compile_raw','P7_motor_const_compile_raw'):
            fresh = reader.StaticAbi(HEAD)
            fresh.claimed=True
            fresh.git_state=mock.Mock(return_value=(HEAD,[('??','state/analysis/'+raw+'/native_abi_static01/result.json')]))
            self.reject(fresh.local)

    def test_queries_are_exact_185_expressions_four_commands_and_no_target_actions(self):
        reader = self.loaded()
        seen=[]
        backend=types.SimpleNamespace(PREFIX='/fixture/tool-',gdb=lambda f,e:seen.append((f,e)) or ['gdb',f,*e])
        commands=reader.queries(backend)
        self.assertEqual(commands[:3],[['/fixture/tool-readelf','--version'],['/fixture/tool-gdb','--version'],
            ['/fixture/tool-readelf','-hSWs',OWNER+'/build/app.ino.elf']])
        self.assertEqual(seen,[(OWNER+'/build/app.ino_debug.elf',expected_expressions())])
        self.assertEqual(len(commands),4)
        self.assertEqual(len(expected_expressions()),185)
        self.assertEqual(reader.queries(reader.loaded(reader.OLD_READER,reader.HARD_PINS[reader.OLD_READER])),expected_commands())
        self.assertFalse(any('\n' in value for value in expected_expressions()))
        self.assertFalse(any(word in ' '.join(expected_expressions()) for word in ('RobotFault','Runner','SettleProbe','target ','call ')))

    def test_complete_two_objects_windows_types_enums_and_exact_schema(self):
        reader=self.loaded()
        result,layout=packet()
        answer=reader.summarize(result,layout)
        self.assertEqual(set(answer),{'schema','status','objects','sizes','alignments','layouts','windows','enums','limitation'})
        self.assertEqual(answer['schema'],'ordinary-app-static-abi-v1')
        self.assertEqual(answer['status'],'STATIC_ABI_OBSERVED')
        self.assertEqual(answer['objects'],{
            'runtime':dict(symbol=SYMBOLS['runtime'],type='app::Runtime',address=ADDRESS,bytes=4096,alignment=8,section=7),
            'motor_port':dict(symbol=SYMBOLS['motor_port'],type='motors::UnoQPort',address=ADDRESS+6144,bytes=40,alignment=4,section=7)})
        for key in ('sizes','alignments','layouts'):
            self.assertEqual(set(answer[key]),set(TYPES))
        self.assertEqual(answer['sizes']['bool'],1)
        self.assertEqual(answer['alignments']['bool'],1)
        self.assertEqual(set(answer['windows']),set(WINDOWS))
        offsets=dict(zip(WINDOWS,(2048,512,1104,128,2304,2400)))
        for member,kind in WINDOWS.items():
            self.assertEqual(answer['windows'][member],dict(object='runtime',type=kind,offset=offsets[member],
                address=ADDRESS+offsets[member],bytes=answer['sizes'][kind],alignment=answer['alignments'][kind]))
        self.assertEqual(answer['enums'],{kind:dict((name,i) for i,name in enumerate(names)) for kind,names in ENUMS.items()})
        for name,block in answer['layouts'].items():
            self.assertIs(type(block),str)
            self.assertIn('type =',block)
            if name!='bool':
                self.assertIn('fixture[',block)
                self.assertIn('total size (bytes)',block)
        self.assertIs(type(answer['limitation']),str)
        self.assertIn('file',answer['limitation'].lower())
        self.assertIn('MCU',answer['limitation'])

    def test_decimal_hex_sizes_and_fresh_addresses_offsets_are_observed(self):
        reader=self.loaded()
        for runtime_token,motor_token in (('4096','40'),('004096','040'),('0x1000','0x28'),('0x01000','0x028')):
            for address,shift in ((ADDRESS,0),(ADDRESS+0x4000,64)):
                result,layout=packet(runtime_token,motor_token=motor_token,address=address,shift=shift)
                before,prior=copy.deepcopy(result),copy.deepcopy(layout)
                answer=reader.summarize(result,layout)
                self.assertEqual(answer['objects']['runtime']['address'],address)
                self.assertEqual(answer['objects']['motor_port']['address'],address+6144)
                self.assertEqual(answer['objects']['runtime']['bytes'],4096)
                self.assertEqual(answer['objects']['motor_port']['bytes'],40)
                self.assertEqual(answer['windows']['report_']['offset'],2048+shift)
                self.assertEqual(result,before)
                self.assertEqual(layout,prior)
        result,layout=packet('4104',motor_token='48',
            sizes_override={'app::Runtime':4104,'motors::UnoQPort':48})
        numeric(result,'ALIGN','app::Runtime',4)
        numeric(result,'ALIGN','motors::UnoQPort',8)
        answer=reader.summarize(result,layout)
        self.assertEqual(answer['objects']['runtime']['bytes'],4104)
        self.assertEqual(answer['objects']['runtime']['alignment'],4)
        self.assertEqual(answer['objects']['motor_port']['bytes'],48)
        self.assertEqual(answer['objects']['motor_port']['alignment'],8)

    def test_summary_is_pure_under_IO_guards_and_preserves_every_raw_field(self):
        reader=self.loaded()
        result,layout=packet('0x1000',motor_token='0x28')
        before,prior=copy.deepcopy(result),copy.deepcopy(layout)
        with ExitStack() as stack:
            for owner,names in ((Path,('read_bytes','read_text','open','write_bytes','write_text','mkdir')),
                                (builtins,('open',)),(io,('open',)),(os,('open',))):
                for name in names:
                    stack.enter_context(mock.patch.object(owner,name,side_effect=AssertionError('Summary I/O')))
            answer=reader.summarize(result,layout)
        self.assertEqual(answer['status'],'STATIC_ABI_OBSERVED')
        self.assertEqual(result,before)
        self.assertEqual(layout,prior)

    def test_invalid_result_containers_command_counts_rows_and_layout_containers_refuse(self):
        reader=self.loaded()
        result,layout=packet()
        for bad in (None,[],{},dict(commands=[]),dict(commands=result['commands'][:3]),
                    dict(commands=result['commands']+[{}]),dict(commands=[None]*4)):
            with self.subTest(container=type(bad).__name__):
                self.reject(lambda:reader.summarize(bad,layout))
        for bad in (None,[],{},dict(sections=[]),dict(sections=None,bss_zero=layout['bss_zero']),
                    dict(sections=layout['sections'],bss_zero=None)):
            self.reject(lambda:reader.summarize(result,bad))

    def test_each_command_identity_execution_limit_encoding_and_stderr_is_required(self):
        reader=self.loaded()
        result,layout=packet()
        mutations=[('argv',['unreviewed']),('execution',dict(returncode=1,timed_out=False,reaped=True)),
            ('execution',dict(returncode=0,timed_out=True,reaped=True)),
            ('execution',dict(returncode=0,timed_out=False,reaped=False)),
            ('deadline_seconds',61),('reap_seconds',6),('stdout_bytes',True),('stdout_bytes',1048577),
            ('stdout_base64','@@'),('stderr_base64','eA=='),('stderr_bytes',True),('error',None)]
        for index in range(4):
            for field,value in mutations:
                bad=copy.deepcopy(result)
                bad['commands'][index][field]=value
                with self.subTest(command=index,field=field):
                    self.reject(lambda:reader.summarize(bad,layout))
            bad=copy.deepcopy(result)
            bad['commands'][index]['stdout_bytes']+=1
            self.reject(lambda:reader.summarize(bad,layout))
        for index in (2,3):
            bad=copy.deepcopy(result)
            bad['commands'][index].update(stdout_bytes=1,stdout_base64='/w==')
            self.reject(lambda:reader.summarize(bad,layout))

    def test_each_marker_missing_duplicate_reordered_or_unknown_refuses(self):
        reader=self.loaded()
        result,layout=packet()
        raw=text(result,3)
        markers=[line for line in raw.splitlines() if line.startswith('SUMOX_')]
        self.assertEqual(len(markers),92)
        for marker in markers:
            for changed in (raw.replace(marker+'\n','',1),raw+marker+'\n',
                            raw.replace(marker+'\n','',1)+marker+'\n'):
                bad=copy.deepcopy(result)
                replace_text(bad,3,changed)
                with self.subTest(marker=marker):
                    self.reject(lambda:reader.summarize(bad,layout))
        for line in ('SUMOX_UNKNOWN x\n$1 = 1\n','SUMOX_SIZE bool extra\n$1 = 1\n',
                     ' SUMOX_ALIGN bool\n$1 = 1\n'):
            bad=copy.deepcopy(result)
            replace_text(bad,3,raw+line)
            self.reject(lambda:reader.summarize(bad,layout))

    def test_every_numeric_answer_requires_one_unsigned_integer(self):
        reader=self.loaded()
        result,layout=packet()
        raw=text(result,3)
        tags=re.findall(r'^SUMOX_(SIZE|ALIGN|OFFSET|ENUM) ([^\n]+)\n\$\d+ = ([^\n]+)',raw,re.M)
        self.assertEqual(len(tags),79)
        for label,name,old in tags:
            for value in ('-1','True','1.5','0x10','not_available'):
                bad=copy.deepcopy(result)
                numeric(bad,label,name,value)
                with self.subTest(label=label,name=name,value=value):
                    self.reject(lambda:reader.summarize(bad,layout))
            bad=copy.deepcopy(result)
            replace_text(bad,3,text(bad,3).replace('SUMOX_'+label+' '+name+'\n',
                'SUMOX_'+label+' '+name+'\n$99 = '+old+'\n',1))
            self.reject(lambda:reader.summarize(bad,layout))

    def test_all_type_size_alignment_bounds_and_exact_bool_are_enforced(self):
        reader=self.loaded()
        for name in TYPES:
            for label,values in (('SIZE',(0,1048577)),('ALIGN',(0,3,32))):
                for value in values:
                    result,layout=packet()
                    numeric(result,label,name,value)
                    with self.subTest(name=name,label=label,value=value):
                        self.reject(lambda:reader.summarize(result,layout))
        for label in ('SIZE','ALIGN'):
            result,layout=packet()
            numeric(result,label,'bool',2)
            self.reject(lambda:reader.summarize(result,layout))

    def test_each_layout_block_must_be_present_nonempty_and_available(self):
        reader=self.loaded()
        result,layout=packet()
        raw=text(result,3)
        for name in TYPES:
            pattern=r'(SUMOX_LAYOUT '+re.escape(name)+r'\n)(.*?)(?=^SUMOX_|\Z)'
            matches=list(re.finditer(pattern,raw,re.M|re.S))
            self.assertEqual(len(matches),1)
            for body in ('','\n','No symbol "'+name+'" in current context.\n'):
                changed=re.sub(pattern,lambda m:m[1]+body,raw,flags=re.M|re.S)
                bad=copy.deepcopy(result)
                replace_text(bad,3,changed)
                with self.subTest(name=name,body=body):
                    self.reject(lambda:reader.summarize(bad,layout))

    def test_all_47_enum_values_must_be_observed_and_equal_source_definition(self):
        reader=self.loaded()
        count=0
        for kind,names in ENUMS.items():
            for expected,name in enumerate(names):
                count+=1
                result,layout=packet()
                numeric(result,'ENUM',kind+'::'+name,expected+1)
                with self.subTest(enum=kind,name=name):
                    self.reject(lambda:reader.summarize(result,layout))
        self.assertEqual(count,47)

    def test_each_object_symbol_requires_unique_complete_local_object_identity(self):
        reader=self.loaded()
        result,layout=packet()
        raw=text(result,2)
        for name,symbol in SYMBOLS.items():
            row=next(line for line in raw.splitlines(keepends=True) if line.split()[-1]==symbol)
            replacements=(raw.replace(row,''),raw+row,raw+'bad '+symbol+'\n',
                raw.replace(row,row.replace(symbol,symbol+'x')),
                raw.replace(row,row.replace('OBJECT','FUNC')),
                raw.replace(row,row.replace('LOCAL','GLOBAL')),
                raw.replace(row,row.replace('LOCAL','WEAK')),
                raw.replace(row,row.replace('DEFAULT','HIDDEN')),
                raw.replace(row,row.replace('DEFAULT 7','DEFAULT UND')),
                raw.replace(row,row.rstrip()+' junk\n'))
            for changed in replacements:
                bad=copy.deepcopy(result)
                replace_text(bad,2,changed)
                with self.subTest(object=name):
                    self.reject(lambda:reader.summarize(bad,layout))

    def test_each_object_size_tokens_and_alignment_must_match_queried_type(self):
        reader=self.loaded()
        result,layout=packet()
        raw=text(result,2)
        for name,symbol in SYMBOLS.items():
            row=next(line for line in raw.splitlines(keepends=True) if line.split()[-1]==symbol)
            words=row.split()
            for token in ('0','0x0','1048577','0x100001','0X28','-1','1e3','0xZZ','41'):
                changed=row.replace(' '+words[2]+' OBJECT',' '+token+' OBJECT')
                bad=copy.deepcopy(result)
                replace_text(bad,2,raw.replace(row,changed))
                with self.subTest(object=name,size=token):
                    self.reject(lambda:reader.summarize(bad,layout))
            changed=row.replace(words[1],format(int(words[1],16)+1,'x'),1)
            bad=copy.deepcopy(result)
            replace_text(bad,2,raw.replace(row,changed))
            self.reject(lambda:reader.summarize(bad,layout))

    def test_objects_independently_require_initialized_bss_and_nonoverlap(self):
        reader=self.loaded()
        result,layout=packet()
        raw=text(result,2)
        for name,symbol in SYMBOLS.items():
            row=next(line for line in raw.splitlines(keepends=True) if line.split()[-1]==symbol)
            old_address=row.split()[1]
            for value in (ADDRESS-8,ADDRESS+8192,ADDRESS+8160):
                bad=copy.deepcopy(result)
                replace_text(bad,2,raw.replace(row,row.replace(old_address,format(value,'x'),1)))
                with self.subTest(object=name,address=value):
                    self.reject(lambda:reader.summarize(bad,layout))
        bad=copy.deepcopy(result)
        replace_text(bad,2,raw.replace(format(ADDRESS+6144,'x')+' 40 OBJECT',format(ADDRESS+256,'x')+' 40 OBJECT'))
        self.reject(lambda:reader.summarize(bad,layout))
        for end in (ADDRESS+4095,ADDRESS+6183):
            badlayout=copy.deepcopy(layout)
            badlayout['bss_zero']['end']=end
            self.reject(lambda:reader.summarize(result,badlayout))

    def test_unique_observed_bss_section_and_checked_layout_agreement_are_required(self):
        reader=self.loaded()
        result,layout=packet()
        raw=text(result,2)
        section=next(line for line in raw.splitlines(keepends=True) if '.bss NOBITS' in line)
        for changed in (raw.replace('EXEC (Executable file)','DYN (Shared object file)'),
                        raw.replace(section,''),raw+section,raw.replace('NOBITS','PROGBITS'),
                        raw.replace('002000','001000'),raw.replace('00 WA ','00 W '),
                        raw.replace('DEFAULT 7','DEFAULT 8')):
            bad=copy.deepcopy(result)
            replace_text(bad,2,changed)
            self.reject(lambda:reader.summarize(bad,layout))
        cases=[]
        for field,value in (('address',ADDRESS+4),('address',True),('size',True),('size',8191)):
            bad=copy.deepcopy(layout)
            bad['sections'][0][field]=value
            cases.append(bad)
        bad=copy.deepcopy(layout)
        bad['sections']*=2
        cases.append(bad)
        for field,value in (('start',True),('end',True),('start',ADDRESS-1),
                            ('end',ADDRESS+8193),('start',ADDRESS+8192)):
            bad=copy.deepcopy(layout)
            bad['bss_zero'][field]=value
            cases.append(bad)
        for bad in cases:
            self.reject(lambda:reader.summarize(result,bad))

    def test_every_window_containment_alignment_and_pairwise_nonoverlap_are_checked(self):
        reader=self.loaded()
        for member,kind in WINDOWS.items():
            for offset in (4096,5000):
                result,layout=packet()
                numeric(result,'OFFSET',member,offset)
                self.reject(lambda:reader.summarize(result,layout))
            if kind!='bool':
                result,layout=packet()
                numeric(result,'OFFSET',member,1)
                self.reject(lambda:reader.summarize(result,layout))
            overlap=512 if member=='report_' else 2048
            result,layout=packet()
            numeric(result,'OFFSET',member,overlap)
            with self.subTest(member=member):
                self.reject(lambda:reader.summarize(result,layout))

    def test_each_forbidden_diagnostic_symbol_refuses_without_querying_its_type(self):
        reader=self.loaded()
        for symbol in ('_ZN12_GLOBAL__N_110diagnosticE','_ZN6motors12_GLOBAL__N_119settle_probe_reportE',
                       '_ZN6motors17settleProbeReportEv'):
            result,layout=packet()
            replace_text(result,2,text(result,2)+'  99: 20031c00 28 OBJECT LOCAL DEFAULT 7 '+symbol+'\n')
            with self.subTest(symbol=symbol):
                self.reject(lambda:reader.summarize(result,layout))

    def test_success_retains_raw_before_ordinary_summary_and_independent_local_closure(self):
        _,owner,result,writes=self.executing_owner()
        before=copy.deepcopy(result)
        closure=owner.execute()
        self.assertEqual([name for name,_ in writes],['inputs.json','result.json','abi.json','local_result.json'])
        self.assertEqual(writes[1][1],before)
        self.assertEqual(writes[2][1]['schema'],'ordinary-app-static-abi-v1')
        self.assertEqual(set(writes[2][1]['objects']),{'runtime','motor_port'})
        self.assertNotIn('readelf_size_projection',writes[2][1])
        self.assertEqual(result,before)
        self.assertEqual(closure['status'],'STATIC_ABI_OBSERVED')
        self.assertEqual(closure['final_checks'],[dict(name='local',status='PASS')])
        owner.direct.assert_called_once_with(owner.bootstrap,'file-abi',400)
        owner.local.assert_called_once_with()
        self.assertTrue(owner.claimed)
        self.assertTrue(owner.output.is_dir())

    def test_all_current_artifact_pins_and_thirteen_closures_are_required(self):
        _,prepared=self.prepared_owner()
        prepared.prepare()
        current=json.loads(self.inputs[RAW+'/native_static01/artifacts.json'])
        expected={OWNER+'/'+name:row['sha256'] for name,row in current['files'].items()}
        expected.update(self.spec['file_tool_pins'])
        core='/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
        expected[core+'/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf']=current['loader']['sha256']
        expected[core+'/variants/arduino_uno_q_stm32u585xx/tls-syms.S']=current['tls_source']['sha256']
        self.assertEqual(prepared.remote_pins,expected)
        self.assertEqual(len(expected),12)
        paths=[*expected,'board_identity']
        self.assertEqual(len(paths),13)
        for failed in (None,*paths):
            _,owner,result,writes=self.executing_owner()
            owner.remote_pins=dict(expected)
            result['final_checks']=[dict(path=p,status='FAILED' if p==failed else 'PASS') for p in paths]
            before=copy.deepcopy(result)
            owner.direct.return_value=(types.SimpleNamespace(stdout=json.dumps(result),stderr=''),None)
            with self.subTest(failed=failed):
                if failed is None:
                    self.assertEqual(owner.execute()['status'],'STATIC_ABI_OBSERVED')
                else:
                    self.reject(owner.execute)
                    self.assertNotIn('abi.json',[name for name,_ in writes])
                self.assertEqual(writes[1],('result.json',before))
                self.assertEqual(result,before)
                owner.local.assert_called_once_with()


def load_tests(loader,standard,pattern):
    if not sys.dont_write_bytecode:
        raise AssertionError('Use Python -B')
    base=historical()
    selected=plan()['selection']
    inherited=unittest.TestSuite()
    for cls in ('BootstrapContract','LifecycleContract','AbiContract'):
        inherited.addTests(getattr(base,cls)(name) for name in selected[cls])
    spec=plan()['historical']['windows_mode']
    raw=original(spec['source'])
    mode=module(raw,ROOT/spec['source'],'_d209_private_windows_mode')
    mode.SUBJECT=ROOT/SUBJECT
    previous=mode.WindowsExecutableModeContract.setUpClass.__func__
    def setup(cls):
        previous(cls)
        if identity(cls.source)!=plan()['subject_expected']:
            raise AssertionError('Current Windows bootstrap source identity differs')
    mode.WindowsExecutableModeContract.setUpClass=classmethod(setup)
    inherited.addTests(mode.WindowsExecutableModeContract(name) for name in selected['WindowsExecutableModeContract'])
    if inherited.countTestCases()!=39:
        raise AssertionError('Expected39 selected inherited methods')
    result=unittest.TestSuite([standard,inherited])
    if result.countTestCases()!=plan()['counts']['total']:
        raise AssertionError('Frozen ordinary ABI method inventory differs')
    return result


if __name__=='__main__':
    unittest.main(verbosity=2)
