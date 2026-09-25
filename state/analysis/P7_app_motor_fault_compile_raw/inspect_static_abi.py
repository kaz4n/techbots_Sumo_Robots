# Observes the compiled inhibited full-application diagnostic's static ABI.
# Reads pinned ELF files only; no compiler, upload, reset or MCU access exists here.
# Checked with controlled local fixtures and a separate source review before use.
import base64
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import subprocess
import sys
import types
import zlib

ROOT = Path(__file__).absolute().parents[3]
RAW = 'state/analysis/P7_app_motor_fault_compile_raw'
SELF = RAW + '/inspect_static_abi.py'
LEGACY = 'state/analysis/P7_current_app_compile_raw/compile_current_app.py'
COMPILE = 'tools/compile_app_motor_fault.py'
OLD_READER = 'state/analysis/P7_motor_fault_raw/inspect_active_abi.py'
MANIFEST = RAW + '/inputs_static.json'
OUTCOME = RAW + '/native_static01/result.json'
ARTIFACTS = RAW + '/native_static01/artifacts.json'
SOURCE = '21df6ae82cca4b09dc6b1e0de5bc719cf98ec6887800d5ce8297522e491a7950'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
OWNER = '/home/arduino/sumox26_codex_build/app-motor-fault-static01'
HARD_PINS = {
    LEGACY: 'aed3fbf4db5c962761affd5a3e2e52b1002feaaefe4e44f9f34df6ec78ba5ede',
    COMPILE: 'cf0c826feca483a78ce9839d0037d1e005a0ce73a3aa01df1ad4b309729ed25a',
    OLD_READER: '50c074024105e5920ab1557557abfd45c1bcd4280224e2360935a40caf46869a',
    MANIFEST: 'd4eae97c1c47a1ce0fa24c9d7e3ae44857a565cd7b85b9c17be45143654d3eb5',
    OUTCOME: 'f8928bd0b9a59f47c1bc02c627523af8f250535ffcd269e37e5a80414cc0ce82',
    ARTIFACTS: '57b98c00db1ed5d90394812fcbb3fb28effedd4381f6e2fc03a6e7c04b45a6ce',
}
TYPES = ('app_motor_fault::Runner', 'app_motor_fault::Report', 'app_motor_fault::Snapshot',
         'motor_fault::Trace', 'motor_fault::TraceReport', 'motor_fault::Call',
         'app::Runtime', 'app::RuntimeReport', 'app::Transaction', 'app::TransactionReport',
         'fsm::RobotResult', 'fsm::PreviousTick', 'motors::MotorGate', 'motors::Result',
         'motors::HaltResult', 'core::Outputs', 'countdown::LifecycleResult', 'countdown::Result')
WINDOWS = {
    'trace_.report_': 'motor_fault::TraceReport',
    'report_': 'app_motor_fault::Report',
    'report_.before_abort.runtime': 'app::RuntimeReport',
    'report_.before_abort.transaction': 'app::TransactionReport',
    'report_.before_abort.previous': 'fsm::PreviousTick',
    'runtime_.report_': 'app::RuntimeReport',
    'runtime_.transaction_.report_': 'app::TransactionReport',
    'runtime_.transaction_.previous_': 'fsm::PreviousTick',
    'runtime_.transaction_.gate_': 'motors::MotorGate',
    'attempted_': 'bool',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned(path, expected, limit=1048576):
    for item in (path, *path.parents):
        info = item.lstat()
        kind = stat.S_ISREG if item == path else stat.S_ISDIR
        require(kind(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 1024,
                'Linked or nonplain local input: ' + str(item))
    before = path.stat()
    require(0 < before.st_size <= limit, 'Local input size bound')
    with path.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(limit + 1)
    stamp = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns)
    require(stamp(before) == stamp(opened) == stamp(path.stat()) and len(raw) == before.st_size,
            'Local input changed during read')
    require(sha(raw) == expected, 'Local digest changed: ' + str(path))
    return raw


def loaded(name, expected):
    raw = pinned(ROOT / name, expected)
    module = types.ModuleType('_static_abi_' + Path(name).stem)
    module.__file__ = str(ROOT / name)
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def queries(reader):
    expressions = ['set max-value-size 1048576']
    for name in (*TYPES, 'bool'):
        for label, expression in (('SIZE', 'sizeof'), ('ALIGN', 'alignof')):
            expressions += ['echo SUMOX_' + label + ' ' + name + '\\n',
                            'p/d ' + expression + '(' + name + ')']
        expressions += ['echo SUMOX_LAYOUT ' + name + '\\n', 'ptype /o ' + name]
    for member in WINDOWS:
        expressions += ['echo SUMOX_OFFSET ' + member + '\\n',
                        'p/d (unsigned long)&((app_motor_fault::Runner*)0)->' + member]
    build = OWNER + '/build/app_motor_fault.ino'
    return [[reader.PREFIX + 'readelf', '--version'], [reader.PREFIX + 'gdb', '--version'],
            [reader.PREFIX + 'readelf', '-hSWs', build + '.elf'],
            reader.gdb(build + '_debug.elf', expressions)]


def number(text, label, name):
    pattern = r'^SUMOX_' + label + ' ' + re.escape(name) + r'\r?\n\$\d+ = (\d+)\r?$'
    values = re.findall(pattern, text, re.MULTILINE)
    require(len(values) == 1, 'Missing or duplicate tagged number: ' + label + ' ' + name)
    return int(values[0])


def checked_command(record, command):
    require(record['argv'] == command and record['execution'] ==
            dict(returncode=0, timed_out=False, reaped=True) and
            record['deadline_seconds'] == 60 and record['reap_seconds'] == 5 and
            'error' not in record, 'File tool execution differs')
    for name in ('stdout', 'stderr'):
        count, encoded = record[name + '_bytes'], record[name + '_base64']
        require(type(count) is int and 0 <= count <= 1048576 and type(encoded) is str and
                len(encoded) <= 1398104, 'File tool stream exceeds bound')
        raw = base64.b64decode(encoded, validate=True)
        require(len(raw) == count and base64.b64encode(raw).decode() == encoded,
                'File tool stream accounting differs')
        require(name != 'stderr' or not raw, 'File tool stderr is not empty')


def summarize(result, layout):
    texts = [base64.b64decode(row['stdout_base64'], validate=True).decode('utf-8')
             for row in result['commands']]
    elf, debug = texts[2:]
    require(re.search(r'^\s*Type:\s+EXEC \(Executable file\)\s*$', elf, re.MULTILINE),
            'Expected static ET_EXEC image')
    sizes, aligns = {}, {}
    for name in (*TYPES, 'bool'):
        sizes[name], aligns[name] = number(debug, 'SIZE', name), number(debug, 'ALIGN', name)
        require(0 < sizes[name] <= 1048576 and 0 < aligns[name] <= 16 and
                aligns[name] & (aligns[name] - 1) == 0, 'Invalid ABI size/alignment')
        require(debug.count('SUMOX_LAYOUT ' + name + '\n') == 1, 'Missing layout marker')
    symbol = '_ZN12_GLOBAL__N_110diagnosticE'
    pattern = r'^\s*\d+:\s+([0-9a-fA-F]+)\s+(\d+)\s+OBJECT\s+LOCAL\s+DEFAULT\s+(\d+)\s+' + symbol + r'\s*$'
    symbols = re.findall(pattern, elf, re.MULTILINE)
    require(len(symbols) == 1, 'Expected exactly one static diagnostic OBJECT')
    address, length, section = int(symbols[0][0], 16), int(symbols[0][1]), int(symbols[0][2])
    bss = next(item for item in layout['sections'] if item['name'] == '.bss')
    pattern = r'^\s*\[\s*' + str(section) + r'\]\s+\.bss\s+NOBITS\s+([0-9a-fA-F]+)\s+[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+\S+\s+WA\s+'
    sections = re.findall(pattern, elf, re.MULTILINE)
    require(len(sections) == 1 and tuple(int(x, 16) for x in sections[0]) ==
            (bss['address'], bss['size']), 'Diagnostic section differs from checked layout')
    require(length == sizes['app_motor_fault::Runner'] and address % aligns['app_motor_fault::Runner'] == 0 and
            layout['bss_zero']['start'] <= address < address + length <= layout['bss_zero']['end'],
            'Diagnostic object not wholly inside initialized BSS')
    windows = {}
    for member, name in WINDOWS.items():
        offset = number(debug, 'OFFSET', member)
        require(offset + sizes[name] <= length and (address + offset) % aligns[name] == 0,
                'Capture window leaves diagnostic object or violates alignment')
        windows[member] = dict(type=name, offset=offset, address=address + offset, bytes=sizes[name])
    return dict(status='STATIC_ABI_OBSERVED', symbol=symbol, address=address, bytes=length,
                section=section, sizes=sizes, alignments=aligns, windows=windows,
                limitation='File layout only; no MCU contents, runtime acceptance, RAM or WCET measurement')


class StaticAbi:
    def __init__(self, head):
        self.root, self.reviewed_head = ROOT, head
        self.output = ROOT / RAW / 'native_abi_static01'
        self.remote = '/home/arduino/sumox26_codex_build/app-motor-fault-abi-static01'
        self.inputs_path = ROOT / MANIFEST
        self.inputs_raw = self.executor = None
        self.claimed, self.counter = False, 0
        self.base = loaded(LEGACY, HARD_PINS[LEGACY])
        self.compiler = loaded(COMPILE, HARD_PINS[COMPILE])
        self.reader = loaded(OLD_READER, HARD_PINS[OLD_READER])
        self.local_pins = {**HARD_PINS, SELF: sha(self.base.read(ROOT / SELF))}
        for name in ('source_names', 'source_mapping'):
            setattr(self, name, types.MethodType(getattr(self.compiler.CompileDiagnostic, name), self))
        for name in ('git_state', 'transport', 'direct', 'preamble'):
            setattr(self, name, types.MethodType(getattr(self.base.CompileCurrent, name), self))

    def local(self):
        require(sys.dont_write_bytecode, 'Python -B required')
        require(not os.path.lexists(self.output / 'pycache'), 'Bytecode output must stay absent')
        head, changes = self.git_state()
        prefix = self.output.relative_to(ROOT).as_posix() + '/'
        require(head == self.reviewed_head and all(self.claimed and status == '??' and name.startswith(prefix)
                for status, name in changes), 'Reviewed HEAD or clean working tree changed')
        for name, digest in self.local_pins.items():
            pinned(ROOT / name, digest)
        self.compiler.CompileDiagnostic.admission(self)
        require(self.source_sha256 == SOURCE and self.boot == BOOT, 'Diagnostic source/boot changed')
        pinned(Path(self.base.ADB), self.base.ADB_SHA, 16777216)

    def prepare(self):
        self.local()
        require(not os.path.lexists(self.output), 'ABI observation owner already consumed')
        self.base.plain(self.output.parent, directory=True)
        require(shutil.disk_usage(ROOT).free >= 134217728, 'Less than 128MiB local free space')
        self.executor = self.base.executor_namespace(ROOT, self.code[self.base.EXECUTOR])
        self.executor['BOOT'] = self.base.BOOT = BOOT
        outcome = self.base.decode(pinned(ROOT / OUTCOME, HARD_PINS[OUTCOME]))
        require(outcome['status'] == 'COMPILE_CHECKED' and outcome['first_error'] is None and
                outcome['source_sha256'] == SOURCE and outcome['boot_id'] == BOOT and
                outcome['compiler_calls'] == outcome['query_calls'] == 1 and
                all(row['status'] == 'PASS' for row in outcome['final_checks']), 'Compile evidence differs')
        self.packet = self.base.decode(pinned(ROOT / ARTIFACTS, HARD_PINS[ARTIFACTS]))
        self.build_path, self.artifacts = OWNER + '/build', OWNER + '/artifacts'
        self.validate_layout = types.MethodType(self.compiler.CompileDiagnostic.validate_layout, self)
        self.compiler.CompileDiagnostic.validate_artifact_reply(self, self.base.read(ROOT / ARTIFACTS).decode())
        pins = {OWNER + '/' + name: row['sha256'] for name, row in self.packet['files'].items()}
        pins.update(self.reader.TOOLS)
        core = '/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0'
        pins[core + '/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf'] = self.packet['loader']['sha256']
        pins[core + '/variants/arduino_uno_q_stm32u585xx/tls-syms.S'] = self.packet['tls_source']['sha256']
        self.remote_pins, self.commands = pins, queries(self.reader)
        self.program = self.preamble() + 'import subprocess,base64\n'
        self.program += "if os.path.lexists(REMOTE):raise ValueError('ABI scope path exists')\n"
        self.program += self.executor['extracted_wait'](self.code[self.base.SUPPORT])
        self.program += 'pins=' + repr(pins) + '\ncommands=' + repr(self.commands) + '\n'
        require(self.reader.REMOTE_READ.count('D173_FILE_ONLY_ABI') == 1, 'Reader scope changed')
        self.program += self.reader.REMOTE_READ.replace('D173_FILE_ONLY_ABI', 'D188_STATIC_FILE_ONLY_ABI')
        packed = base64.b64encode(zlib.compress(self.program.encode(), 9)).decode()
        self.bootstrap = 'import base64,zlib;exec(zlib.decompress(base64.b64decode(' + repr(packed) + ')))'
        command = ['/usr/bin/env', '-i', *(k + '=' + v for k, v in self.base.ENV.items()),
                   '/usr/bin/python3', '-I', '-B', '-c', self.bootstrap]
        argv = [self.base.ADB, '-s', self.base.BOARD, 'shell', '-T', shlex.join(command)]
        self.units = len(subprocess.list2cmdline(argv).encode('utf-16-le')) // 2 + 1
        require(self.units <= 30000, 'Windows command exceeds 30000 units')
        return dict(status='STATIC_ABI_CHECKED', reviewed_head=self.reviewed_head, source_sha256=SOURCE,
                    boot_id=BOOT, command_units=self.units, file_commands=len(self.commands), output=str(self.output))

    def execute(self):
        check = self.prepare()
        self.output.mkdir(mode=0o700)
        self.claimed = True
        write = self.executor['write']
        closure = dict(status='FAILED', first_error=None, final_checks=[],
                       started_utc=datetime.now(timezone.utc).isoformat())
        failure = None
        try:
            write(self.output / 'inputs.json', dict(**check, local_pins={**self.inputs['files'], **self.local_pins},
                remote_pins=self.remote_pins, commands=self.commands, program_sha256=sha(self.program.encode())))
            reply, _ = self.direct(self.bootstrap, 'file-abi', 400)
            require(not reply.stderr and len(reply.stdout) <= 8388608, 'Invalid ABI transport response')
            result = self.base.decode(reply.stdout)
            write(self.output / 'result.json', result)
            require(result['scope'] == 'D188_STATIC_FILE_ONLY_ABI' and result['status'] == 'OBSERVED' and
                    result['first_error'] is None and len(result['commands']) == len(self.commands),
                    'File-only ABI commands failed')
            require(result['final_checks'] == [dict(path=name, status='PASS') for name in self.remote_pins] +
                    [dict(path='board_identity', status='PASS')], 'Remote closure differs')
            for record, command in zip(result['commands'], self.commands):
                checked_command(record, command)
            write(self.output / 'abi.json', summarize(result, self.packet['layout']['validator_report']))
            closure['status'] = 'STATIC_ABI_OBSERVED'
        except Exception as error:
            failure = error
            closure['first_error'] = self.base.error_value(error)
        finally:
            try:
                self.local()
                closure['final_checks'].append(dict(name='local', status='PASS'))
            except Exception as error:
                failure = failure or error
                closure['status'] = 'FAILED'
                closure['first_error'] = closure['first_error'] or self.base.error_value(error)
                closure['final_checks'].append(dict(name='local', status='FAILED', error=str(error)))
            closure['finished_utc'] = datetime.now(timezone.utc).isoformat()
            closure['transport_calls'] = self.counter
            try:
                write(self.output / 'local_result.json', closure)
            except Exception as error:
                if failure is not None:
                    failure.local_closure = closure
                    failure.evidence_write_errors = [*getattr(failure, 'evidence_write_errors', []),
                                                     self.base.error_value(error)]
                    raise failure from error
                raise
        if failure is not None:
            raise failure
        return closure


def main(argv):
    require(len(argv) == 3 and argv[0] in ('--check-only', '--execute') and argv[1] == '--reviewed-head' and
            re.fullmatch('[0-9a-f]{40}', argv[2]), 'Expected --check-only|--execute --reviewed-head <40lowerhex>')
    owner = StaticAbi(argv[2])
    result = owner.prepare() if argv[0] == '--check-only' else owner.execute()
    print(owner.base.json.dumps(result, indent=2))


if __name__ == '__main__':
    main(sys.argv[1:])
