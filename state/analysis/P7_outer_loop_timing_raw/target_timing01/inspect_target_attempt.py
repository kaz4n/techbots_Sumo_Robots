# Inspects only the closed D243 compiler's ELF files and retained diagnostics.
# Separates offline target-code/layout evidence from MCU memory or timing evidence.
# Source review and syntax validation precede root's separately admitted execution.
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import stat
import subprocess
import sys
import time

ROOT = Path(__file__).absolute().parents[3]
SCRIPT = Path(__file__).absolute()
HEAD = 'ce15bb967614af54cf7f059dc541949ce754c776'
SOURCE = 'fcb9a31adef28ca7d2f79335cc466dcc4ddb31007ff2da4341a33fb07983cace'
BOOT = '55c386b9-fe6d-4388-a7f4-1d91e0bb49d8'
ADB = Path('C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe')
ADB_SHA = 'e79dc8fc3c6385192bdccd7ff7eabe3d5c1ec292475a06b04d82759f07655982'
SERIAL = '2629958581'
GDB = '/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb'
GDB_SHA = '8e709e322c50351a932d1bdf4103caf238eaf226a4984e56e6f353e64bc4b778'
PARSER = 'state/analysis/P7_static_link_probe_raw/static_artifacts.py'
TLS = 'state/analysis/P7_static_link_probe_raw/static_native_artifacts.py'
PINS = {PARSER: 'd30372dd4b8fb8c2661d00affc4a215cc88e3f62511995ff6303827bed4b7368',
        TLS: 'cd52a29a32b8ae1da4bea51dd55d9011386dd4be0ca537195bb124d13031d6c0'}
KINDS = {'timing': ('sumox-outer-timing-native-20260927', 'P7_commissioning_build_raw',
                    'commission-p4_timing-m0-', 'p4_timing', 0, 'commissioning'),
         'match': ('sumox-outer-match-native-20260927', 'P7_match_static_raw',
                   'match-static-match-m1-', 'match', 1, 'match-static')}
CHECKS = ('local', 'identity', 'initialization', 'builtins', 'remote_sources',
          'installed_pins', 'overrides', 'artifacts', 'artifact_sources')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def stamp(info):
    return (info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode), info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def plain(path, directory=False):
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        folder = directory or item != path
        require((stat.S_ISDIR(info.st_mode) if folder else stat.S_ISREG(info.st_mode)) and
                not getattr(info, 'st_file_attributes', 0) & 1024, 'Nonplain path: ' + str(item))
        if not folder:
            require(info.st_nlink == 1, 'Multiply linked input')


def read(path, limit=1048576):
    plain(path)
    before = stamp(path.stat())
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        require(stamp(os.fstat(stream.fileno())) == before, 'Opened input changed')
        raw = stream.read(limit + 1)
        require(stamp(os.fstat(stream.fileno())) == before, 'Read input changed')
    require(len(raw) <= limit and stamp(path.stat()) == before, 'Input size/identity changed')
    return raw


def save(output, name, value):
    body = value if isinstance(value, bytes) else (json.dumps(value, indent=2) + '\n').encode()
    with (output / name).open('xb') as stream:
        stream.write(body)


def command(output, report, argv, timeout=90, limit=1048576):
    number, started = len(report['commands']), time.monotonic()
    require(len(subprocess.list2cmdline(argv).encode('utf-16-le')) // 2 <= 30000,
            'Command exceeds Windows transport bound')
    save(output, f'{number:02d}.argv.json', argv)
    code, stdout, stderr, error = None, b'', b'', None
    try:
        result = subprocess.run(argv, capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as caught:
        code, stdout, stderr, error = 124, caught.stdout or b'', caught.stderr or b'', repr(caught)
    except Exception as caught:
        error = repr(caught)
    row = dict(argv=argv, returncode=code, seconds=time.monotonic() - started,
               stdout_bytes=len(stdout), stderr_bytes=len(stderr), error=error,
               truncated=len(stdout) > limit or len(stderr) > limit, save_errors=[])
    report['commands'].append(row)
    for name, body in (('stdout', stdout), ('stderr', stderr)):
        try:
            save(output, f'{number:02d}.{name}', body[:limit])
        except Exception as caught:
            row['save_errors'].append(dict(stream=name, error=repr(caught)))
            row[name + '_unsaved_hex_prefix'] = body[:limit].hex()
    require(not row['truncated'], 'Output bound exceeded; prefix retained')
    require(error is None and code == 0 and not stderr, 'Command failed; original streams retained')
    require(not row['save_errors'], 'Command evidence write failed; original result retained')
    return stdout


def flags(kind):
    names = ('SUMOX_B4_STAND', 'SUMOX_P3_DRIVE_TEST', 'SUMOX_P3_TURN_TRIAL',
             'SUMOX_P3_STOP_TRIAL', 'SUMOX_P4_REACTIVE', 'SUMOX_TIMING_EVIDENCE',
             'SUMOX_P5_ABORT_TIMING', 'SUMOX_MOTOR_FAULT_PROBE')
    values = [('MATCH', int(kind == 'match')), ('MOTORS_ALLOWED', int(kind == 'match'))]
    values += [(name, int(kind == 'timing' and index in (4, 5))) for index, name in enumerate(names)]
    return ' '.join(f'-D{name}={value}' for name, value in values)


def records(worktree, kind):
    folder, raw, prefix, profile, motors, schema = KINDS[kind]
    require(worktree.name == folder and worktree.is_absolute(), 'Unexpected frozen worktree')
    plain(worktree, directory=True)
    owners = sorted((worktree / 'state/analysis' / raw).glob(prefix + '*/result.json'))
    require(len(owners) == 1, 'Expected exactly one closed compile owner')
    owner = owners[0].parent
    blobs = {name: read(owner / name) for name in ('result.json', 'artifacts.json', 'inputs.json', 'intent.json')}
    result, artifacts, inputs, intent = [json.loads(blobs[name]) for name in blobs]
    suffix = digest((SOURCE + '\0' + intent['attempt']).encode())[:12]
    require(owner.name == prefix + suffix, 'Owner derivation differs')
    expected = dict(profile=profile, motors_allowed=motors, source_sha256=SOURCE)
    for record in (result, artifacts, inputs, intent):
        require(all(type(record.get(k)) is type(v) and record[k] == v for k, v in expected.items()),
                'Compile identity differs')
        require(record['attempt'] == intent['attempt'], 'Attempt differs')
    for record in (result, inputs, intent):
        require(record['reviewed_head'] == HEAD and record['boot_id'] == BOOT, 'Compile HEAD/boot differs')
    require(result['schema'] == schema + '-app-static-compile-outcome-v1' and
            result['status'] == 'COMPILE_CHECKED' and result['first_error'] is None and
            result['compiler_calls'] == result['query_calls'] == 1, 'Compile is not closed/checked')
    require(result['final_checks'] == [dict(name=n, status='PASS', error=None) for n in CHECKS],
            'Compile closing checks differ')
    require(intent['inputs_sha256'] == digest(blobs['inputs.json']), 'Inputs receipt changed')
    fqbn = 'arduino:zephyr:unoq:link_mode=static' + (',wait_linux_boot=no' if kind == 'match' else '')
    require(all(r['flags'] == flags(kind) and r['fqbn'] == fqbn for r in (result, intent)), 'Tuple differs')
    remote = '/home/arduino/sumox26_codex_build/' + owner.name
    require(re.fullmatch(re.escape(prefix) + '[0-9a-f]{12}', owner.name) and
            intent['remote'] == remote and artifacts['build_path'] == remote + '/build' and
            artifacts['artifacts_path'] == result['artifacts'] == remote + '/artifacts', 'Owner paths differ')
    require(artifacts['status'] == 'ARTIFACTS_CHECKED' and artifacts['first_error'] is None and
            artifacts['schema'] == schema + '-app-static-artifacts-v1', 'Artifact receipt unchecked')
    require(artifacts['postchecks'] == [dict(name=n, status='PASS', error=None)
            for n in ('loader', 'tls_source', 'files')], 'Artifact closing checks differ')
    return owner, blobs, artifacts, inputs


def local_inputs(worktree, inputs, output, report):
    names = sorted(inputs['files'])
    require(len(names) == 136 and all(not PurePosixPath(n).is_absolute() and
            '..' not in PurePosixPath(n).parts and '\\' not in n for n in names), 'Input set differs')
    tree = command(output, report, ['git', '-C', str(worktree), 'ls-tree', '-rz', HEAD, '--', *names])
    expected = {}
    for entry in tree.split(b'\0'):
        if not entry:
            continue
        meta, name = entry.split(b'\t', 1)
        mode, kind, oid = meta.split()
        require(mode in (b'100644', b'100755') and kind == b'blob', 'Nonordinary Git input')
        expected[name.decode()] = oid.decode()
    require(set(expected) == set(names), 'Git input set differs')
    for name in names:
        body = read(worktree / name)
        require(digest(body) == inputs['files'][name], 'Compiled input changed: ' + name)
        blob = b'blob ' + str(len(body)).encode() + b'\0' + body
        require(hashlib.sha1(blob).hexdigest() == expected[name], 'Historical source differs: ' + name)
    return {name: inputs['files'][name] for name in names}


REMOTE = r'''
import hashlib,json,os,selectors,signal,stat,subprocess,time
def expired(unused,frame):raise TimeoutError('File inspection deadline')
def identity():
    with open('/proc/sys/kernel/random/boot_id','r') as f:boot=f.read(64).strip()
    value=dict(boot_id=boot,uid=os.getuid(),euid=os.geteuid())
    assert value==payload['identity']
    return value
def observe(path,expected):
    before=os.lstat(path)
    assert stat.S_ISREG(before.st_mode) and before.st_nlink==1
    def stamp(s):return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    assert 0<before.st_size<=67108864
    h=hashlib.sha256()
    with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK),'rb') as f:
        assert stamp(os.fstat(f.fileno()))==stamp(before)
        for unused in range(65):
            b=f.read(1048576)
            if not b:break
            h.update(b)
        else:raise ValueError('File read bound')
        assert stamp(os.fstat(f.fileno()))==stamp(before)
    assert stamp(os.lstat(path))==stamp(before)
    identity=dict(bytes=before.st_size,device=before.st_dev,inode=before.st_ino,
                  mtime_ns=before.st_mtime_ns,ctime_ns=before.st_ctime_ns)
    assert h.hexdigest()==expected['sha256']
    if 'identity' in expected:assert identity==expected['identity']
    return dict(identity=identity,stamp=stamp(before),sha256=h.hexdigest())
def invoke(argv):
    p=None;out,err=bytearray(),bytearray()
    row=dict(argv=argv,returncode=None,first_error=None,closing_errors=[],reaped=False)
    try:
        p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        with selectors.DefaultSelector() as selected:
            selected.register(p.stdout,selectors.EVENT_READ,out)
            selected.register(p.stderr,selectors.EVENT_READ,err)
            deadline=time.monotonic()+25
            while selected.get_map():
                if time.monotonic()>deadline:raise TimeoutError('GDB deadline')
                for key,unused in selected.select(0.25):
                    space=payload['remaining_output']-len(out)-len(err)
                    if space<=0:raise ValueError('GDB output bound')
                    body=os.read(key.fileobj.fileno(),min(4096,space))
                    if body:key.data.extend(body)
                    else:selected.unregister(key.fileobj)
                if len(out)+len(err)>payload['remaining_output']:raise ValueError('GDB output bound')
        p.wait(timeout=2)
    except BaseException as error:row['first_error']=repr(error)
    finally:
        if p is not None:
            try:
                if p.poll() is None:p.kill()
            except BaseException as error:row['closing_errors'].append(repr(error))
            try:row['returncode']=p.wait(timeout=2);row['reaped']=True
            except BaseException as error:row['closing_errors'].append(repr(error))
            for stream,target in ((p.stdout,out),(p.stderr,err)):
                try:
                    os.set_blocking(stream.fileno(),False)
                    for unused in range(122):
                        space=payload['remaining_output']-len(out)-len(err)
                        if space<=0:raise ValueError('Final pipe drain output bound')
                        try:body=os.read(stream.fileno(),min(4096,space))
                        except BlockingIOError:break
                        if not body:break
                        target.extend(body)
                    else:raise ValueError('Final pipe drain iteration bound')
                except BaseException as error:row['closing_errors'].append(repr(error))
                try:stream.close()
                except BaseException as error:row['closing_errors'].append(repr(error))
        row.update(stdout=bytes(out).hex(),stderr=bytes(err).hex(),encoding='hex')
    return row
answer=dict(before={},after={},commands=[],first_error=None,closing_errors=[])
signal.signal(signal.SIGALRM,expired);signal.alarm(70)
try:
    answer['identity_before']=identity()
    for path,expected in payload['files'].items():answer['before'][path]=observe(path,expected)
    for argv in payload['commands']:
        row=invoke(argv);answer['commands'].append(row)
        assert row['first_error'] is None and row['reaped'] and not row['closing_errors']
        assert row['returncode']==0 and not row['stderr']
        payload['remaining_output']-=len(bytes.fromhex(row['stdout']))+len(bytes.fromhex(row['stderr']))
except BaseException as error:answer['first_error']=repr(error)
finally:
    for path,expected in payload['files'].items():
        try:
            value=observe(path,expected);answer['after'][path]=value
            assert value==answer['before'].get(path)
        except BaseException as error:answer['closing_errors'].append(dict(path=path,error=repr(error)))
    try:answer['identity_after']=identity()
    except BaseException as error:answer['closing_errors'].append(dict(path='identity',error=repr(error)))
    signal.alarm(0)
print(json.dumps(answer,separators=(',',':')))
'''


def remote(output, report, files, commands):
    payload = dict(files=files, commands=commands, identity=dict(boot_id=BOOT, uid=1000, euid=1000),
                   remaining_output=491520 - report.get('gdb_output_bytes', 0))
    program = 'payload=' + repr(payload) + '\n' + REMOTE
    argv = [str(ADB), '-s', SERIAL, 'shell', shlex.join(['python3', '-I', '-B', '-c', program])]
    value = json.loads(command(output, report, argv))
    report['file_observations'].append(value)
    for row in value['commands']:
        index = report.get('gdb_commands', 0)
        save(output, f'gdb_{index:02d}.json', row)
        for name in ('stdout', 'stderr'):
            body = bytes.fromhex(row[name])
            save(output, f'gdb_{index:02d}.{name}', body)
            report['gdb_output_bytes'] = report.get('gdb_output_bytes', 0) + len(body)
            row[name] = body.decode('utf-8', errors='strict')
        row['encoding'] = 'utf-8'
        report['gdb_commands'] = index + 1
    require(report.get('gdb_output_bytes', 0) <= 491520, 'Total GDB output bound; original bytes retained')
    require(value['first_error'] is None and not value['closing_errors'], 'File-only command failed')
    return value


def gdb(file, expressions):
    argv = [GDB, '-nx', '-nh', '-batch', '-iex', 'set auto-load no',
            '-iex', 'set may-call-functions off', '-iex', 'set debuginfod enabled off',
            file, '-ex', 'set language c++', '-ex', 'set pagination off', '-ex', 'set width 0']
    for expression in expressions:
        argv += ['-ex', expression]
    return argv


def image(worktree, raw):
    modules = {}
    for name, pin in PINS.items():
        body = read(worktree / name)
        require(digest(body) == pin, 'ELF parser input changed')
        namespace = {'__name__': '_d243_offline_' + Path(name).stem}
        exec(compile(body, name, 'exec'), namespace)
        modules[name] = namespace
    return modules[TLS]['image_type'](modules[PARSER])(raw)


def ranges(elf, kind):
    objects = elf.symbols.get('outer_loop_timing', [])
    helpers = [name for name in elf.symbols if 'outer_loop_timing' in name]
    object_info = None
    if kind == 'timing':
        require(len(objects) == 1 and objects[0]['type'] == 1, 'Missing unique observer object')
        obj = objects[0]; section = elf.sections[obj['section']]
        start, end = obj['value'], obj['value'] + obj['size']
        require(0 < obj['size'] <= 16384 and section['flags'] & 3 == 3 and
                section['address'] <= start < end <= section['address'] + section['size'], 'Observer bounds')
        lower, upper = ((elf.bounds['_sdata'], elf.bounds['_edata']) if section['name'] == '.data'
                        else (elf.bounds['_sbss'], elf.bounds['_ebss']))
        require(section['name'] in ('.data', '.bss') and lower <= start < end <= upper,
                'Observer outside validated initialization interval')
        object_info = dict(symbol=obj, section=section['name'])
    else:
        require(not helpers, 'Production contains observer object/helper')
    selected, deferred = {}, {}
    for name, entries in elf.symbols.items():
        for symbol in entries:
            if symbol['type'] != 2 or not symbol['size']:
                continue
            entry = name in ('loop', '_Z4loopv')
            outer = 'outer_loop_timing' in name
            distribution = 'epoch_timing' in name and 'observe' in name
            if not (entry or outer or distribution):
                continue
            section = elf.sections[symbol['section']]
            start, end = symbol['value'] & ~1, (symbol['value'] & ~1) + symbol['size']
            require(section['flags'] & 6 == 6 and section['address'] <= start < end <=
                    section['address'] + section['size'], 'Function range outside allocated code')
            target = deferred if distribution else selected
            target[name] = dict(start=start, end=end, bytes=symbol['size'])
    require(sum(name in selected for name in ('loop', '_Z4loopv')) == 1, 'Missing unique loop FUNC')
    require(len(selected) <= 32 and sum(v['bytes'] for v in selected.values()) <= 16384, 'Code range bound')
    return object_info, selected, deferred


def layout_queries():
    types = ('app::outer_loop_timing::Observer', 'app::outer_loop_timing::Data',
             'app::outer_loop_timing::Context', 'app::outer_loop_timing::Poll',
             'app::outer_loop_timing::Count', 'app::epoch_timing::Distribution', 'app::epoch_timing::Data')
    commands = ['set max-value-size 1048576', 'echo OBJECT_LAYOUT\\n', 'ptype /o outer_loop_timing']
    for name in types:
        commands += ['echo SIZE ' + name + '\\n', 'p/d sizeof(' + name + ')',
                     'echo ALIGN ' + name + '\\n', 'p/d alignof(' + name + ')', 'ptype /o ' + name]
    return commands


def inspect(worktree, kind, output, report, artifacts, files):
    final = artifacts['build_path'] + '/app.ino.elf'
    before = remote(output, report, files, [])
    report['first_bracket'] = before['before']
    command(output, report, [str(ADB), '-s', SERIAL, 'pull', final, str(output / 'app.ino.elf')])
    raw = read(output / 'app.ino.elf', 1048576)
    require(digest(raw) == files[final]['sha256'] and len(raw) == files[final]['identity']['bytes'],
            'Pulled ELF differs from checked receipt')
    elf = image(worktree, raw)
    obj, selected, deferred = ranges(elf, kind)
    report.update(object=obj, ranges=selected, parser_pins=PINS)
    expressions = [f'disassemble /r 0x{x["start"]:x},0x{x["end"]:x}' for x in selected.values()]
    commands = [gdb(final, expressions)]
    if kind == 'timing':
        commands += [gdb(artifacts['build_path'] + '/app.ino_debug.elf', layout_queries())]
    observed = remote(output, report, files, commands)
    code = observed['commands'][0]['stdout']
    calls = {int(x, 16) for x in re.findall(r'\b(?:bl(?:\.w)?|blx(?:\.w)?|b\.w)\s+(?:0x)?([0-9a-fA-F]+)\s', code)}
    reached = {name: x for name, x in deferred.items() if x['start'] in calls}
    require(sum(x['bytes'] for x in [*selected.values(), *reached.values()]) <= 16384, 'Reached code bound')
    if reached:
        commands = [gdb(final, [f'disassemble /r 0x{x["start"]:x},0x{x["end"]:x}' for x in reached.values()])]
        remote(output, report, files, commands)
    report['reached_distribution_ranges'] = reached
    if kind == 'timing':
        text = observed['commands'][1]['stdout']
        layout = {}
        for label in ('SIZE', 'ALIGN'):
            for name in ('Observer', 'Data'):
                pattern = label + r' app::outer_loop_timing::' + name + r'\s+\$[0-9]+ = ([0-9]+)'
                found = re.search(pattern, text)
                require(found is not None and int(found[1]) > 0, 'Missing actual DWARF size/alignment')
                layout[label + '_' + name] = int(found[1])
        require(layout['SIZE_Observer'] == obj['symbol']['size'] and
                layout['SIZE_Data'] <= layout['SIZE_Observer'], 'DWARF/object size differs')
        require(all(value & (value - 1) == 0 and obj['symbol']['value'] % value == 0
                    for key, value in layout.items() if key.startswith('ALIGN_')), 'DWARF alignment differs')
        report['dwarf_layout'] = layout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worktree', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--kind', choices=KINDS, required=True)
    args = parser.parse_args()
    require(sys.dont_write_bytecode and args.output.is_absolute(), 'Use python -I -B and absolute output')
    require(args.output.parent == ROOT / 'state/analysis/P7_outer_loop_timing_raw' and
            re.fullmatch('target_' + args.kind + '[0-9]{2}', args.output.name), 'Unexpected evidence owner')
    plain(args.output.parent, directory=True)
    args.output.mkdir(mode=0o700)
    report = dict(schema='d243-file-only-inspection-v1', kind=args.kind, status='FAILED',
                  commands=[], file_observations=[], first_error=None, closing_errors=[])
    owner = blobs = inputs = files = None
    try:
        report['script_sha256'] = digest(read(SCRIPT))
        require(digest(read(ADB, 16777216)) == ADB_SHA, 'ADB changed')
        owner, blobs, artifacts, inputs = records(args.worktree, args.kind)
        report['receipts'] = {str(owner / name): digest(body) for name, body in blobs.items()}
        report['inputs'] = local_inputs(args.worktree, inputs, args.output, report)
        files = {artifacts['build_path'] + '/' + name: artifacts['files']['build/' + name]
                 for name in ('app.ino.elf', 'app.ino_debug.elf')}
        files[GDB] = dict(sha256=GDB_SHA)
        inspect(args.worktree, args.kind, args.output, report, artifacts, files)
    except Exception as error:
        report['first_error'] = repr(error)
    finally:
        closing(args, report, owner, blobs, inputs, files)
        if report['first_error'] is None and not report['closing_errors']:
            report['status'] = 'FILE_ONLY_INSPECTION_PASS'
        try:
            save(args.output, 'summary.json', report)
        except Exception as error:
            report['closing_errors'].append(dict(name='summary_write', error=repr(error)))
            report['status'] = 'FAILED'
            print(json.dumps(report), file=sys.stderr)
    print(json.dumps(dict(status=report['status'], output=str(args.output))))
    return int(report['status'] != 'FILE_ONLY_INSPECTION_PASS')


def closing(args, report, owner, blobs, inputs, files):
    operations = []
    if files:
        operations.append(('remote_files', lambda: remote(args.output, report, files, [])))
    if inputs:
        operations.append(('local_inputs', lambda: local_inputs(args.worktree, inputs, args.output, report)))
    if owner:
        operations.append(('receipts', lambda: require(all(read(owner / n) == b for n, b in blobs.items()),
                                                       'Compile receipts changed')))
    operations.append(('adb', lambda: require(digest(read(ADB, 16777216)) == ADB_SHA, 'ADB changed')))
    if 'script_sha256' in report:
        operations.append(('inspector', lambda: require(digest(read(SCRIPT)) == report['script_sha256'],
                                                         'Inspection script changed')))
    for name, operation in operations:
        try:
            value = operation()
            if name == 'remote_files' and 'first_bracket' in report:
                require(value['after'] == report['first_bracket'], 'Full inspection bracket differs')
        except Exception as error:
            report['closing_errors'].append(dict(name=name, error=repr(error)))


if __name__ == '__main__':
    sys.exit(main())
