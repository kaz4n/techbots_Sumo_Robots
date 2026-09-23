# Tests D113 receive-only connection evidence from the adopted public contract.
# Executes generated receiver/observer scripts with confined Linux and socket fixtures.
# Synthetic identity and clock evidence never qualifies a board or MCU run.
import base64
import builtins
import contextlib
import copy
import importlib
import io
import json
import os
from pathlib import Path
import socket
import stat
import subprocess
import sys
import tempfile
import time
import traceback
import unittest
from unittest import mock

from tests.tooling.test_dump_match import wire

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
TICKET = '0123456789abcdef0123456789abcdef'
TARGET = 'fixture@board.invalid'
BOOT = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
UTC = '2026-09-24T00:00:00.000000Z'
MAX_BYTES = 16 * 1024 * 1024
CLAIM_KEYS = {'schema_version', 'ticket', 'transport', 'target', 'boot_id', 'uid',
              'directory_device', 'directory_inode', 'receiver_pid',
              'receiver_start_ticks', 'started_monotonic_ns', 'claimed_utc',
              'claimed_monotonic_ns', 'deadline_monotonic_ns'}
CONNECTION_KEYS = {'schema_version', 'claim', 'event', 'local_address', 'local_port',
                   'peer_address', 'peer_port', 'socket_fd', 'socket_inode',
                   'connected_utc', 'connected_monotonic_ns'}
TERMINAL_KEYS = {'schema_version', 'claim', 'closed_utc', 'closed_monotonic_ns',
                 'observed_byte_count', 'reason'}
RESULT_KEYS = {'schema_version', 'ticket', 'state', 'error', 'router_registration',
               'hardware_permission', 'mcu_permission', 'query_start_utc',
               'query_end_utc', 'observed_utc', 'observed_monotonic_ns', 'claim',
               'connection', 'terminal', 'command_outcome'}
OUTCOME_KEYS = {'target', 'remote_argv', 'returncode', 'start_utc', 'end_utc',
                'timeout_seconds', 'timed_out', 'stderr', 'stderr_truncated'}


def claim_record(**updates):
    result = dict(schema_version=1, ticket=TICKET, transport='ssh', target=TARGET,
                  boot_id=BOOT, uid=os.getuid() if hasattr(os, 'getuid') else 1000,
                  directory_device=1, directory_inode=2, receiver_pid=123,
                  receiver_start_ticks=900, started_monotonic_ns=0,
                  claimed_utc=UTC, claimed_monotonic_ns=1,
                  deadline_monotonic_ns=30_000_000_000)
    result.update(updates)
    return result


def connection_record(claim):
    return dict(schema_version=1, claim=copy.deepcopy(claim), event='TCP_CONNECTED',
                local_address='127.0.0.1', local_port=40000, peer_address='127.0.0.1',
                peer_port=7500, socket_fd=987, socket_inode=6000, connected_utc=UTC,
                connected_monotonic_ns=2)


def terminal_record(claim, reason='END_OBSERVED', count=None):
    return dict(schema_version=1, claim=copy.deepcopy(claim), closed_utc=UTC,
                closed_monotonic_ns=3, observed_byte_count=len(wire()) if count is None else count,
                reason=reason)


def response(state='CONNECTED', **updates):
    claim = claim_record()
    result = dict(state=state, observed_utc=UTC, observed_monotonic_ns=10_000_000_000,
                  claim=claim, connection=connection_record(claim), terminal=None)
    if state == 'TERMINAL':
        result['terminal'] = terminal_record(claim)
    if state == 'PENDING':
        result.update(claim=None, connection=None)
    if state == 'EXPIRED':
        result['observed_monotonic_ns'] = claim['deadline_monotonic_ns']
    result.update(updates)
    return result


def completed(payload, code=0, stderr=''):
    return subprocess.CompletedProcess(['fixture'], code,
                                       stdout=json.dumps(payload) if isinstance(payload, dict) else payload,
                                       stderr=stderr)


class ConnectionBase(unittest.TestCase):
    def setUp(self):
        self.module = importlib.import_module('dump_match')
        self.temp = tempfile.TemporaryDirectory(prefix='d113-author-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = mock.patch.dict(os.environ, {'SUMO_TRANSPORT': 'ssh', 'SUMO_SSH_TARGET': TARGET})
        self.env.start()
        self.addCleanup(self.env.stop)

    def evidence(self, evidence, state):
        self.assertEqual(set(evidence), RESULT_KEYS)
        self.assertEqual(evidence['state'], state)
        self.assertEqual(evidence['ticket'], TICKET)
        self.assertEqual(evidence['schema_version'], 1)
        self.assertEqual(evidence['router_registration'], 'UNKNOWN')
        self.assertIs(evidence['hardware_permission'], False)
        self.assertIs(evidence['mcu_permission'], False)
        self.assertEqual(set(evidence['command_outcome']), OUTCOME_KEYS)
        self.assertEqual(evidence['command_outcome']['timeout_seconds'], 5)
        self.assertEqual(evidence['query_start_utc'], evidence['command_outcome']['start_utc'])
        self.assertEqual(evidence['query_end_utc'], evidence['command_outcome']['end_utc'])

    def observe_reply(self, reply):
        with mock.patch.object(self.module.board, 'remote', return_value=completed(reply)) as remote:
            result = self.module.observe_connection(TARGET, TICKET)
        self.assertEqual(remote.call_count, 1)
        args, options = remote.call_args
        self.assertEqual(args[0], TARGET)
        self.assertEqual(args[1][:3], ['python3', '-u', '-c'])
        self.assertTrue(options['capture'])
        self.assertEqual(options['timeout'], 5)
        return result

    def metadata_error(self, payload):
        with mock.patch.object(self.module.board, 'remote', return_value=completed(payload)):
            with self.assertRaises(self.module.CaptureError) as caught:
                self.module.observe_connection(TARGET, TICKET)
        self.assertEqual(caught.exception.code, 'CONNECTION_METADATA')
        self.evidence(caught.exception.connection_evidence, None)


class ConnectionHostTests(ConnectionBase):
    def test_invalid_environment_is_argument_error_before_transport(self):
        environments = ({'SUMO_TRANSPORT': 'invalid', 'SUMO_SSH_TARGET': TARGET},
                        {'SUMO_TRANSPORT': 'ssh'}, {'SUMO_TRANSPORT': 'adb'})
        commands = (['--observe-connection', TICKET],
                    ['--connection-ticket', TICKET, '--output-dir', str(self.root / 'capture')])
        for environment in environments:
            for args in commands:
                with self.subTest(environment=environment, args=args):
                    with mock.patch.dict(os.environ, environment, clear=True):
                        with mock.patch.object(self.module.board, 'remote', side_effect=AssertionError('I/O')):
                            with contextlib.redirect_stderr(io.StringIO()):
                                with self.assertRaises(SystemExit) as caught:
                                    self.module.main(args)
                            self.assertEqual(caught.exception.code, 2)

    def test_missing_explicit_transport_is_argument_error_for_both_new_modes(self):
        commands = (['--observe-connection', TICKET],
                    ['--connection-ticket', TICKET, '--output-dir', str(self.root / 'capture')])
        for args in commands:
            with self.subTest(args=args), mock.patch.dict(os.environ, {'SUMO_SSH_TARGET': TARGET}, clear=True):
                with mock.patch.object(self.module.board, 'remote', side_effect=AssertionError('missing transport reached remote')):
                    with contextlib.redirect_stderr(io.StringIO()):
                        with self.assertRaises(SystemExit) as caught:
                            self.module.main(args)
                    self.assertEqual(caught.exception.code, 2)

    def test_passive_constructor_and_invalid_public_arguments_before_transport(self):
        with mock.patch.object(self.module.board, 'remote', side_effect=AssertionError('I/O')):
            capture = self.module.live_chunks(TARGET, 30, connection_ticket=TICKET)
            self.assertIsNone(capture.connection_evidence)
            for ticket in ('', TICKET.upper(), '0'*31, '0'*33, '../'+TICKET, None, True, 5):
                with self.subTest(ticket=ticket):
                    with self.assertRaises(ValueError):
                        self.module.observe_connection(TARGET, ticket)
            for timeout in (0, 3601, True, 1.5, '3'):
                with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                    self.module.live_chunks(TARGET, timeout, connection_ticket=TICKET)
            for target in ('a'*129, '-x', 'bad\ntarget', 'bad;target', 'é'):
                with self.subTest(target=target), self.assertRaises(ValueError):
                    self.module.live_chunks(target, 3, connection_ticket=TICKET)

    def test_cli_rejects_combinations_and_paths_without_remote(self):
        observer = ['--observe-connection', TICKET]
        variants = [observer + pair for pair in (
            ['--connection-ticket', TICKET], ['--timeout', '330'],
            ['--output-dir', str(self.root)], ['--input', 'missing'],
            ['--firmware-revision', 'a'*40], ['--source-sha256', 'b'*64],
            ['--config-sha256', 'c'*64])]
        variants += [['--input', 'missing', '--connection-ticket', TICKET],
                     ['--connection-ticket', TICKET.upper()]]
        occupied = self.root / 'occupied'
        occupied.write_text('retained')
        variants += [['--connection-ticket', TICKET, '--output-dir', str(occupied)]]
        with mock.patch.object(self.module.board, 'remote', side_effect=AssertionError('I/O')):
            for args in variants:
                with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as caught:
                        self.module.main(args)
                    self.assertEqual(caught.exception.code, 2)
        self.assertEqual(occupied.read_text(), 'retained')

    def test_all_observer_states_return_exact_envelope_and_original_identity(self):
        for state in ('PENDING', 'CONNECTED', 'TERMINAL', 'EXPIRED', 'UNKNOWN'):
            with self.subTest(state=state):
                remote = response(state)
                result = self.observe_reply(remote)
                self.evidence(result, state)
                self.assertIsNone(result['error'])
                for key in ('claim', 'connection', 'terminal', 'observed_utc', 'observed_monotonic_ns'):
                    self.assertEqual(result[key], remote[key])
        self.assertEqual(self.observe_reply(response())['claim']['deadline_monotonic_ns'], 30_000_000_000)

    def test_cli_valid_nonconnected_states_exit_zero_and_errors_exit_one(self):
        for state in ('PENDING', 'CONNECTED', 'TERMINAL', 'EXPIRED', 'UNKNOWN'):
            with self.subTest(state=state), mock.patch.object(self.module.board, 'remote', return_value=completed(response(state))):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = self.module.main(['--observe-connection', TICKET])
                self.assertEqual(code, 0)
                self.evidence(json.loads(output.getvalue()), state)
        diagnostic = response()
        diagnostic.pop('state')
        diagnostic['error'] = {'code': 'CONNECTION_METADATA', 'message': 'unsafe receipt'}
        with mock.patch.object(self.module.board, 'remote', return_value=completed(diagnostic)):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(self.module.main(['--observe-connection', TICKET]), 1)
            result = json.loads(output.getvalue())
            self.evidence(result, None)
            self.assertEqual(result['error'], diagnostic['error'])

    def test_observer_transport_outcomes_preserve_actual_failure(self):
        failures = [OSError('spawn rejected'),
                    subprocess.CalledProcessError(7, 'fixture', output=json.dumps(response()), stderr='actual failure'),
                    subprocess.TimeoutExpired('fixture', 5, output=json.dumps(response()), stderr='actual timeout')]
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                with mock.patch.object(self.module.board, 'remote', side_effect=failure):
                    with self.assertRaises(self.module.CaptureError) as caught:
                        self.module.observe_connection(TARGET, TICKET)
                self.assertEqual(caught.exception.code, 'CONNECTION_TRANSPORT')
                evidence = caught.exception.connection_evidence
                self.evidence(evidence, None)
                self.assertIsNone(evidence['claim'])
                self.assertIsNone(evidence['connection'])
                self.assertEqual(evidence['command_outcome']['timed_out'], isinstance(failure, subprocess.TimeoutExpired))
                self.assertEqual(evidence['command_outcome']['returncode'], 7 if isinstance(failure, subprocess.CalledProcessError) else None)

    def test_remote_json_strict_shape_bounds_and_errors(self):
        good = json.dumps(response())
        variants = [good + '{}', good.replace('"state": "CONNECTED"', '"state":"CONNECTED","state":"CONNECTED"'),
                    '['+good+']', 'x'*16385, '{', good.replace('"schema_version": 1', '"schema_version": true')]
        variants += [dict(response(), extra=0), dict(response(), state='READY'),
                     dict(response(), state='CONNECTED', connection=None),
                     dict(response(), observed_monotonic_ns=True)]
        for variant in variants:
            with self.subTest(variant=str(variant)[:100]):
                self.metadata_error(variant)
        diagnostic = response()
        diagnostic.pop('state')
        diagnostic['error'] = {'code': 'CONNECTION_METADATA', 'message': 'x'*512}
        self.metadata_error(diagnostic)
        for update in ({'code': 'TRANSPORT'}, {'message': 'x'*513}, {'extra': 0}):
            bad = copy.deepcopy(diagnostic)
            bad['error'].update(update)
            self.metadata_error(bad)

    def test_host_rejects_each_record_key_omission_and_extra(self):
        for kind, keys in (('claim', CLAIM_KEYS), ('connection', CONNECTION_KEYS), ('terminal', TERMINAL_KEYS)):
            for key in sorted(keys):
                with self.subTest(kind=kind, key=key):
                    bad = response('TERMINAL')
                    del bad[kind][key]
                    self.metadata_error(bad)
            bad = response('TERMINAL')
            bad[kind]['unrecognized'] = 0
            self.metadata_error(bad)

    def test_host_rejects_schema_identity_time_and_endpoint_mismatch(self):
        changes = [('claim', 'schema_version', True), ('claim', 'ticket', 'f'*32),
                   ('claim', 'target', 'different'), ('claim', 'transport', 'adb'),
                   ('claim', 'uid', -1), ('claim', 'receiver_pid', 0),
                   ('claim', 'started_monotonic_ns', 1.0), ('claim', 'claimed_utc', 'not UTC'),
                   ('claim', 'deadline_monotonic_ns', 1), ('connection', 'event', 'READY'),
                   ('connection', 'peer_port', 7501), ('connection', 'local_address', '1.2.3.4'),
                   ('connection', 'socket_inode', 0), ('connection', 'connected_monotonic_ns', 30_000_000_000),
                   ('terminal', 'closed_monotonic_ns', 1), ('terminal', 'reason', 'SUCCESS'),
                   ('terminal', 'observed_byte_count', True)]
        for kind, key, value in changes:
            with self.subTest(kind=kind, key=key):
                bad = response('TERMINAL')
                bad[kind][key] = value
                self.metadata_error(bad)

    def test_capture_success_stores_final_terminal_and_exact_wire(self):
        data = wire()
        encoded = base64.b64encode(data).decode() + '\n'
        replies = [completed(encoded), completed(response('TERMINAL'))]
        with mock.patch.object(self.module.board, 'remote', side_effect=replies) as remote:
            chunks = self.module.live_chunks(TARGET, 30, connection_ticket=TICKET)
            destination = self.module.save_capture(chunks, self.root, receive_mode='ssh', target=TARGET)
        self.assertEqual(remote.call_count, 2)
        self.assertEqual((destination / 'wire.txt').read_bytes(), data)
        metadata = json.loads((destination / 'capture.json').read_text())
        self.evidence(metadata['connection_evidence'], 'TERMINAL')
        self.assertEqual(metadata['connection_evidence'], chunks.connection_evidence)
        self.assertEqual(metadata['transport_outcome']['timeout_seconds'], 45)
        self.assertEqual(metadata['connection_evidence']['command_outcome']['timeout_seconds'], 5)

    def fail_capture(self, receive, query, expected, payload):
        before = set(self.root.iterdir())
        with mock.patch.object(self.module.board, 'remote', side_effect=[receive, query]) as remote:
            chunks = self.module.live_chunks(TARGET, 30, connection_ticket=TICKET)
            with self.assertRaises(self.module.CaptureError) as caught:
                self.module.save_capture(chunks, self.root, receive_mode='ssh', target=TARGET)
        self.assertEqual(caught.exception.code, expected)
        self.assertEqual(remote.call_count, 2)
        created = set(self.root.iterdir()) - before
        self.assertEqual(len(created), 1)
        partial = created.pop()
        self.assertIn('partial', partial.name)
        self.assertEqual((partial / 'wire.txt').read_bytes(), payload)
        result = json.loads((partial / 'error.json').read_text())
        self.assertIn('connection_evidence', result)
        self.assertIsNotNone(result['connection_evidence'])
        return result

    def test_metadata_failure_never_hides_good_prefix_or_publishes_success(self):
        data = wire()
        receive = completed(base64.b64encode(data).decode()+'\n')
        replies = [completed(response('CONNECTED')), completed(response('PENDING')),
                   completed('{'), subprocess.TimeoutExpired('fixture', 5)]
        for reply in replies:
            expected = 'CONNECTION_TRANSPORT' if isinstance(reply, subprocess.TimeoutExpired) else 'CONNECTION_METADATA'
            with self.subTest(reply=type(reply).__name__):
                self.fail_capture(receive, reply, expected, data)
        for reason in ('EOF', 'TIMEOUT', 'ERROR'):
            reply = response('TERMINAL')
            reply['terminal']['reason'] = reason
            self.fail_capture(receive, completed(reply), 'CONNECTION_METADATA', data)

    def test_failed_receive_is_primary_even_when_prefix_is_malformed(self):
        for data in (wire(), b'malformed\n'):
            encoded = base64.b64encode(data).decode()+'\n'
            receive = subprocess.CalledProcessError(9, 'fixture', output=encoded, stderr='first failure')
            result = self.fail_capture(receive, completed('{'), 'TRANSPORT', data)
            self.assertEqual(result['transport_outcome']['returncode'], 9)
            self.assertEqual(result['transport_outcome']['stderr'], 'first failure')

    def test_final_query_precedes_first_yield_and_parser_fault_keeps_evidence(self):
        data = b'invalid\n'
        replies = [completed(base64.b64encode(data).decode()+'\n'), completed('{')]
        with mock.patch.object(self.module.board, 'remote', side_effect=replies) as remote:
            chunks = self.module.live_chunks(TARGET, 30, connection_ticket=TICKET)
            iterator = iter(chunks)
            self.assertEqual(next(iterator), data)
            self.assertEqual(remote.call_count, 2)
            self.assertIsNotNone(chunks.connection_evidence)
        parser = self.module.Parser()
        with self.assertRaises(self.module.CaptureError) as original:
            parser.feed(data)
        self.fail_capture(replies[0], replies[1], original.exception.code, data)


class SyntheticSocket:
    def __init__(self, sandbox):
        self.sandbox = sandbox

    def settimeout(self, timeout):
        self.sandbox.timeouts.append(timeout)
        if not 0 < timeout <= self.sandbox.timeout:
            raise AssertionError('unbounded recv timeout')

    def fileno(self):
        return 987

    def getsockname(self):
        return ('127.0.0.1', 40000)

    def getpeername(self):
        return ('127.0.0.1', 7500)

    def recv(self, count):
        box = self.sandbox
        box.events.append('recv')
        box.recv_sizes.append(count)
        if not (box.directory / 'connected.json').exists():
            raise AssertionError('recv before connected publication')
        box.connection_at_recv = json.loads((box.directory / 'connected.json').read_text())
        if box.after_recv:
            box.after_recv(box)
        piece = box.pieces.pop(0) if box.pieces else b''
        if isinstance(piece, BaseException):
            raise piece
        if len(piece) > count:
            box.pieces.insert(0, piece[count:])
            piece = piece[:count]
        box.returned += len(piece)
        return piece

    def close(self):
        self.sandbox.events.append('close')
        self.sandbox.close_count += 1
        if self.sandbox.close_error:
            raise OSError('synthetic close failure')

    def send(self, *args, **kwargs):
        raise AssertionError('application send forbidden')

    sendall = send
    sendto = send

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class LinuxFixture:
    """Maps only /tmp and /proc; actual no-replace rename uses confined real FDs."""
    def __init__(self, root):
        self.root = root / 'linux'
        self.tmp = self.root / 'tmp'
        self.proc = self.root / 'proc'
        self.tmp.mkdir(parents=True)
        self.proc.mkdir()
        self.tmp.chmod(0o1777)
        self.directory = self.tmp / ('sumox26-dump-connection-'+TICKET)
        self.pid = os.getpid()
        self.now = 10_000_000_000
        self.timeout = 30
        self.pieces = [wire()]
        self.after_recv = None
        self.after_connect = None
        self.close_error = False
        self.connect_error = None
        self.events, self.timeouts, self.recv_sizes = [], [], []
        self.close_count = self.returned = 0
        self.fd_paths = {}
        self.proc_reads = []
        self.proc_hook = None
        self.file_hook = None
        self.connection_at_recv = None
        self.real = {name: getattr(os, name) for name in
                     ('open', 'close', 'stat', 'lstat', 'fstat', 'mkdir', 'readlink', 'rename', 'replace', 'unlink')}
        self.real_open = builtins.open
        self.real_io_open = io.open
        self.real_realpath = os.path.realpath
        self.populate_proc()

    def mapped(self, path):
        if isinstance(path, int):
            return path
        raw = os.fsdecode(path)
        if raw.startswith(str(self.root)) or not raw.startswith('/'):
            return path
        if raw == '/tmp' or raw.startswith('/tmp/'):
            return str(self.tmp) + raw[4:]
        if raw == '/proc' or raw.startswith('/proc/'):
            self.proc_reads.append(raw)
            if self.proc_hook:
                self.proc_hook(self, raw)
            return str(self.proc) + raw[5:]
        if raw == '/':
            return str(self.root)
        raise AssertionError('unexpected absolute path '+raw)

    def populate_proc(self, process_state='S', ticks=900, socket_inode=6000, tcp_state='01'):
        directory = self.proc / str(self.pid)
        (directory / 'fd').mkdir(parents=True, exist_ok=True)
        (directory / 'net').mkdir(exist_ok=True)
        boot = self.proc / 'sys/kernel/random'
        boot.mkdir(parents=True, exist_ok=True)
        (boot / 'boot_id').write_text(BOOT+'\n')
        values = ' '.join(['0']*18 + [str(ticks)] + ['0']*30)
        (directory / 'stat').write_text(f'{self.pid} (receiver (nested) name) {process_state} {values}\n')
        tcp = '  sl  local_address rem_address st tx_queue rx_queue tr tm->when retrnsmt uid timeout inode\n'
        tcp += f'  0: 0100007F:9C40 0100007F:1D4C {tcp_state} 00000000:00000000 00:00000000 00000000 {os.getuid()} 0 {socket_inode} 1 0\n'
        (directory / 'net/tcp').write_text(tcp)
        fd = directory / 'fd/987'
        if fd.is_symlink():
            fd.unlink()
        fd.symlink_to(f'socket:[{socket_inode}]')
        if not (self.proc / 'self').is_symlink():
            (self.proc / 'self').symlink_to(str(self.pid))

    def save(self, name, record):
        self.directory.mkdir(mode=0o700, exist_ok=True)
        path = self.directory / name
        path.write_text(json.dumps(record) if isinstance(record, dict) else record)
        path.chmod(0o600)

    def install_records(self, connected=True, terminal=None):
        self.directory.mkdir(mode=0o700, exist_ok=True)
        info = self.directory.stat()
        claim = claim_record(directory_device=info.st_dev, directory_inode=info.st_ino,
                             receiver_pid=self.pid)
        self.save('claim.json', claim)
        if connected:
            self.save('connected.json', connection_record(claim))
        if terminal:
            self.save('terminal.json', terminal_record(claim, terminal))
        return claim

    def fake_open(self, path, flags, mode=0o777, *, dir_fd=None):
        actual = self.mapped(path)
        fd = self.real['open'](actual, flags, mode, dir_fd=dir_fd)
        if dir_fd is not None and not os.path.isabs(os.fsdecode(path)):
            actual = os.path.join(self.fd_paths.get(dir_fd, ''), os.fsdecode(path))
        self.fd_paths[fd] = os.fsdecode(actual)
        return fd

    def fake_close(self, fd):
        self.fd_paths.pop(fd, None)
        return self.real['close'](fd)

    def root_stat(self, result, path):
        if os.fsdecode(path) != str(self.tmp):
            return result
        fields = list(result)
        fields[4] = 0
        return os.stat_result(fields)

    def fake_stat(self, path, *args, **kwargs):
        actual = self.mapped(path)
        result = self.real['stat'](actual, *args, **kwargs)
        if kwargs.get('dir_fd') is not None and not isinstance(actual, int) and not os.path.isabs(actual):
            actual = os.path.join(self.fd_paths.get(kwargs['dir_fd'], ''), os.fsdecode(actual))
        return self.root_stat(result, actual) if not isinstance(actual, int) else result

    def fake_lstat(self, path, *args, **kwargs):
        actual = self.mapped(path)
        result = self.real['lstat'](actual, *args, **kwargs)
        if kwargs.get('dir_fd') is not None and not os.path.isabs(actual):
            actual = os.path.join(self.fd_paths.get(kwargs['dir_fd'], ''), os.fsdecode(actual))
        return self.root_stat(result, actual)

    def fake_fstat(self, fd):
        if fd == 987:
            return os.stat_result((stat.S_IFSOCK | 0o600, 6000, 1, 1, os.getuid(), 0, 0, 0, 0, 0))
        result = self.real['fstat'](fd)
        if self.file_hook:
            result = self.file_hook(self, self.fd_paths.get(fd, ''), result)
        return self.root_stat(result, self.fd_paths.get(fd, ''))

    def fake_realpath(self, path, *args, **kwargs):
        logical = os.fsdecode(path)
        actual = self.real_realpath(self.mapped(path), *args, **kwargs)
        if logical == '/tmp' or logical.startswith('/tmp/'):
            return '/tmp'+actual[len(str(self.tmp)):] if actual.startswith(str(self.tmp)) else actual
        if logical == '/proc' or logical.startswith('/proc/'):
            return '/proc'+actual[len(str(self.proc)):] if actual.startswith(str(self.proc)) else actual
        return actual

    def connect(self, address, timeout=None, **kwargs):
        self.events.append('connect')
        if address != ('127.0.0.1', 7500):
            raise AssertionError('unexpected endpoint')
        if not (self.directory / 'claim.json').exists():
            raise AssertionError('connect before claim publication')
        if not 0 < timeout <= min(10, self.timeout):
            raise AssertionError('unbounded connect timeout')
        if self.after_connect:
            self.after_connect(self)
        if self.connect_error:
            raise self.connect_error
        return SyntheticSocket(self)

    @contextlib.contextmanager
    def patched(self):
        with contextlib.ExitStack() as stack:
            for name in ('open', 'close', 'stat', 'lstat', 'fstat'):
                stack.enter_context(mock.patch.object(os, name, getattr(self, 'fake_'+name)))
            stack.enter_context(mock.patch.object(os.path, 'realpath', self.fake_realpath))
            for name in ('mkdir', 'readlink', 'unlink'):
                original = self.real[name]
                stack.enter_context(mock.patch.object(os, name, lambda p, *a, _fn=original, **k: _fn(self.mapped(p), *a, **k)))
            for name in ('rename', 'replace'):
                original = self.real[name]
                stack.enter_context(mock.patch.object(os, name, lambda p, q, *a, _fn=original, **k: _fn(self.mapped(p), self.mapped(q), *a, **k)))
            for module, name, original in ((builtins, 'open', self.real_open), (io, 'open', self.real_io_open)):
                stack.enter_context(mock.patch.object(module, name, lambda p, *a, _fn=original, **k: _fn(self.mapped(p), *a, **k)))
            for name in ('link', 'kill', 'system', 'fork'):
                if hasattr(os, name):
                    stack.enter_context(mock.patch.object(os, name, side_effect=AssertionError('forbidden '+name)))
            stack.enter_context(mock.patch.object(socket, 'create_connection', self.connect))
            stack.enter_context(mock.patch.object(socket, 'socket', side_effect=AssertionError('unexpected socket')))
            stack.enter_context(mock.patch.object(time, 'monotonic', lambda: self.now / 1_000_000_000))
            stack.enter_context(mock.patch.object(time, 'monotonic_ns', lambda: self.now))
            stack.enter_context(mock.patch.object(time, 'sleep', side_effect=AssertionError('unexpected sleep')))
            yield

    def execute(self, argv):
        if argv[:3] != ['python3', '-u', '-c']:
            raise AssertionError('unexpected remote command shape')
        output = io.TextIOWrapper(io.BytesIO(), encoding='utf-8', newline='')
        error = io.StringIO()
        code, failure = 0, None
        with self.patched(), mock.patch.object(sys, 'argv', ['-c']+argv[4:]):
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
                try:
                    exec(compile(argv[3], '<opaque-D113-remote>', 'exec'), {'__name__': '__main__'})
                except SystemExit as exc:
                    code = exc.code or 0
                except AssertionError:
                    raise
                except Exception:
                    code = 1
                    failure = sys.exc_info()
        if failure:
            traceback.print_exception(*failure, file=error)
        output.flush()
        return subprocess.CompletedProcess(argv, code, output.buffer.getvalue().decode('utf-8'), error.getvalue())


@unittest.skipUnless(sys.platform.startswith('linux'), 'Actual remote Python requires isolated Linux fixtures')
class ConnectionRemoteTests(ConnectionBase):
    def setUp(self):
        super().setUp()
        self.box = LinuxFixture(self.root)

    def command(self, observer=False):
        with mock.patch.object(self.module.board, 'remote', return_value=completed(response('PENDING'))) as remote:
            if observer:
                self.module.observe_connection(TARGET, TICKET)
            else:
                try:
                    list(self.module.live_chunks(TARGET, self.box.timeout, connection_ticket=TICKET))
                except self.module.CaptureError:
                    pass
        self.assertGreater(remote.call_count, 0)
        return remote.call_args_list[0].args[1]

    def run_receiver(self):
        return self.box.execute(self.command())

    def run_observer(self):
        result = self.box.execute(self.command(observer=True))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLessEqual(len(result.stdout.encode()), 16384)
        return json.loads(result.stdout)

    def terminal(self, result, reason, success=False):
        self.assertEqual(result.returncode == 0, success, result.stderr)
        record = json.loads((self.box.directory / 'terminal.json').read_text())
        self.assertEqual(set(record), TERMINAL_KEYS)
        self.assertEqual(record['reason'], reason)
        self.assertEqual(record['observed_byte_count'], self.box.returned)
        self.assertEqual(self.box.close_count, 1)
        self.assertEqual(record['claim'], json.loads((self.box.directory / 'claim.json').read_text()))
        return record

    def decoded(self, result):
        return b''.join(base64.b64decode(line, validate=True) for line in result.stdout.splitlines())

    def test_actual_receiver_order_records_exact_bytes_and_zero_sends(self):
        data = wire()
        self.box.pieces = [data[:7], data[7:109], data[109:]]
        result = self.run_receiver()
        self.terminal(result, 'END_OBSERVED', True)
        self.assertEqual(self.decoded(result), data)
        self.assertEqual(self.box.events, ['connect', 'recv', 'recv', 'recv', 'close'])
        claim = json.loads((self.box.directory / 'claim.json').read_text())
        connection = json.loads((self.box.directory / 'connected.json').read_text())
        self.assertEqual(set(claim), CLAIM_KEYS)
        self.assertEqual(set(connection), CONNECTION_KEYS)
        self.assertEqual(connection['claim'], claim)
        self.assertEqual(self.box.connection_at_recv, connection)
        self.assertEqual(claim['deadline_monotonic_ns']-claim['started_monotonic_ns'], 30_000_000_000)
        self.assertEqual(claim['receiver_pid'], self.box.pid)
        self.assertEqual(claim['receiver_start_ticks'], 900)
        for path in self.box.directory.iterdir():
            self.assertLessEqual(path.stat().st_size, 4096)
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(path.stat().st_nlink, 1)

    def test_actual_receiver_ticket_collision_never_connects_or_overwrites(self):
        self.box.install_records(terminal='END_OBSERVED')
        old = {p.name: p.read_bytes() for p in self.box.directory.iterdir()}
        result = self.run_receiver()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.box.events, [])
        self.assertEqual({p.name: p.read_bytes() for p in self.box.directory.iterdir()}, old)

    def test_actual_receiver_connect_deadline_and_connect_failure(self):
        self.box.after_connect = lambda box: setattr(box, 'now', 40_000_000_000)
        result = self.run_receiver()
        self.terminal(result, 'TIMEOUT')
        self.assertFalse((self.box.directory / 'connected.json').exists())
        self.assertNotIn('recv', self.box.events)

    def test_actual_receiver_late_end_preserves_bytes_and_timeout_wins(self):
        self.box.pieces = [b'END,late\n']
        self.box.after_recv = lambda box: setattr(box, 'now', 40_000_000_000)
        result = self.run_receiver()
        self.terminal(result, 'TIMEOUT')
        self.assertEqual(self.decoded(result), b'END,late\n')
        self.assertEqual(self.box.events.count('recv'), 1)

    def test_actual_receiver_early_raw_end_is_only_receiver_observation(self):
        self.box.pieces = [b'END,not-valid-CRC\n']
        result = self.run_receiver()
        self.terminal(result, 'END_OBSERVED', True)
        self.assertEqual(self.decoded(result), b'END,not-valid-CRC\n')
        parser = self.module.Parser()
        with self.assertRaises(self.module.CaptureError):
            parser.feed(self.decoded(result))

    def test_actual_receiver_line_failure_preserves_chunk_and_precedes_end(self):
        self.box.pieces = [b'x'*1152 + b'\nEND,ignored\n']
        result = self.run_receiver()
        self.terminal(result, 'ERROR')
        self.assertEqual(self.decoded(result), b'x'*1152+b'\nEND,ignored\n')

    def test_actual_receiver_eof_preserves_prefix_and_socket_timeout(self):
        self.box.pieces = [b'partial\r\n', b'']
        result = self.run_receiver()
        record = json.loads((self.box.directory / 'terminal.json').read_text())
        self.assertEqual(record['reason'], 'EOF')
        self.assertEqual(self.decoded(result), b'partial\r\n')
        self.assertEqual(self.box.close_count, 1)

    def test_actual_receiver_thrown_timeout_is_timeout(self):
        self.box.pieces = [socket.timeout('fixture timeout')]
        self.terminal(self.run_receiver(), 'TIMEOUT')

    def test_actual_receiver_close_failure_has_no_terminal(self):
        self.box.close_error = True
        result = self.run_receiver()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.box.close_count, 1)
        self.assertFalse((self.box.directory / 'terminal.json').exists())
        self.assertEqual(self.decoded(result), wire())

    def test_actual_receiver_failed_connect_retains_claim_and_error_terminal(self):
        self.box.connect_error = OSError('synthetic refused connection')
        result = self.run_receiver()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((self.box.directory / 'claim.json').exists())
        self.assertFalse((self.box.directory / 'connected.json').exists())
        record = json.loads((self.box.directory / 'terminal.json').read_text())
        self.assertEqual(record['reason'], 'ERROR')
        self.assertEqual(record['observed_byte_count'], 0)
        self.assertEqual(self.box.events, ['connect'])

    def test_actual_receiver_connected_publication_collision_is_not_repaired(self):
        def collision(box):
            box.save('connected.json', 'existing receipt must survive')
        self.box.after_connect = collision
        result = self.run_receiver()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.box.directory / 'connected.json').read_text(), 'existing receipt must survive')
        self.assertNotIn('recv', self.box.events)
        self.assertEqual(self.box.close_count, 1)

    def test_actual_receiver_terminal_publication_collision_keeps_wire_and_fails(self):
        def collision(box):
            box.save('terminal.json', 'existing terminal must survive')
        self.box.after_recv = collision
        result = self.run_receiver()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.decoded(result), wire())
        self.assertEqual((self.box.directory / 'terminal.json').read_text(), 'existing terminal must survive')
        self.assertEqual(self.box.close_count, 1)

    def test_actual_receiver_total_limit_returns_plus_one_then_errors(self):
        block = b'x\n' * 32768
        self.box.pieces = [block]*256 + [b'z', b'END,ignored\n']
        result = self.run_receiver()
        self.terminal(result, 'ERROR')
        self.assertEqual(self.box.returned, MAX_BYTES+1)
        self.assertEqual(len(self.decoded(result)), MAX_BYTES+1)
        self.assertEqual(self.box.recv_sizes[-1], 1)
        self.assertEqual(len(self.box.recv_sizes), 257)

    def test_actual_receiver_exact_line_bound_and_pending_bound(self):
        self.box.pieces = [b'x'*1151+b'\nEND,raw\n']
        result = self.run_receiver()
        self.terminal(result, 'END_OBSERVED', True)
        self.assertEqual(len(self.decoded(result)), 1160)

    def test_actual_observer_missing_and_unpublished_claim_are_pending(self):
        self.assertEqual(self.run_observer()['state'], 'PENDING')
        self.assertFalse(self.box.directory.exists())
        self.box.directory.mkdir(mode=0o700)
        result = self.run_observer()
        self.assertEqual(result['state'], 'PENDING')
        self.assertIsNone(result['claim'])
        self.assertEqual(self.box.events, [])

    def test_actual_observer_connected_original_identity_and_live_claim_pending(self):
        claim = self.box.install_records(connected=False)
        self.assertEqual(self.run_observer()['state'], 'PENDING')
        self.box.save('connected.json', connection_record(claim))
        result = self.run_observer()
        self.assertEqual(result['state'], 'CONNECTED')
        self.assertEqual(result['claim'], claim)
        self.assertEqual(result['connection'], connection_record(claim))
        self.assertEqual(self.box.events, [])

    def test_actual_observer_terminal_then_expiry_before_dead_process(self):
        self.box.install_records(terminal='END_OBSERVED')
        self.box.now = 30_000_000_000
        (self.box.proc / str(self.box.pid) / 'stat').unlink()
        self.assertEqual(self.run_observer()['state'], 'TERMINAL')
        (self.box.directory / 'terminal.json').unlink()
        self.assertEqual(self.run_observer()['state'], 'EXPIRED')
        self.box.now -= 1
        self.assertEqual(self.run_observer()['state'], 'UNKNOWN')

    def test_actual_observer_pid_and_fd_reuse_zombie_and_tcp_state_are_unknown(self):
        self.box.install_records()
        for updates in ({'ticks': 901}, {'process_state': 'Z'}, {'socket_inode': 6001}, {'tcp_state': '08'}):
            with self.subTest(updates=updates):
                self.box.populate_proc(**updates)
                result = self.run_observer()
                self.assertEqual(result['state'], 'UNKNOWN')
                self.assertEqual(result['connection']['socket_inode'], 6000)
                self.box.populate_proc()

    def test_actual_observer_missing_malformed_and_bounded_proc_are_unknown(self):
        self.box.install_records()
        tcp = self.box.proc / str(self.box.pid) / 'net/tcp'
        good = tcp.read_bytes()
        for content in (b'invalid\n', b'x'*(1024*1024+1), b'header\n'+b'x\n'*4097):
            with self.subTest(length=len(content)):
                tcp.write_bytes(content)
                self.assertEqual(self.run_observer()['state'], 'UNKNOWN')
        tcp.write_bytes(good)
        tcp.unlink()
        self.assertEqual(self.run_observer()['state'], 'UNKNOWN')

    def test_actual_observer_strict_files_and_identity_refuse_as_metadata(self):
        claim = self.box.install_records()
        changes = [('claim.json', '{'), ('claim.json', 'x'*4097),
                   ('claim.json', dict(claim, boot_id='ffffffff-bbbb-cccc-dddd-eeeeeeeeeeee')),
                   ('claim.json', dict(claim, uid=claim['uid']+1)),
                   ('claim.json', dict(claim, directory_inode=claim['directory_inode']+1)),
                   ('connected.json', dict(connection_record(claim), peer_port=7501))]
        for name, content in changes:
            with self.subTest(name=name, content=str(content)[:70]):
                old = (self.box.directory / name).read_bytes()
                self.box.save(name, content)
                result = self.run_observer()
                self.assertNotIn('state', result)
                self.assertEqual(result['error']['code'], 'CONNECTION_METADATA')
                (self.box.directory / name).write_bytes(old)

    def test_actual_observer_wrong_file_mode_hardlink_and_symlink_refuse(self):
        self.box.install_records()
        path = self.box.directory / 'claim.json'
        path.chmod(0o644)
        self.assertEqual(self.run_observer()['error']['code'], 'CONNECTION_METADATA')
        path.chmod(0o600)
        os.link(path, self.root / 'second-link')
        self.assertEqual(self.run_observer()['error']['code'], 'CONNECTION_METADATA')
        (self.root / 'second-link').unlink()
        original = path.read_bytes()
        path.unlink()
        replacement = self.root / 'replacement'
        replacement.write_bytes(original)
        path.symlink_to(replacement)
        self.assertEqual(self.run_observer()['error']['code'], 'CONNECTION_METADATA')

    def test_actual_observer_terminal_cannot_hide_malformed_connection(self):
        self.box.install_records(terminal='END_OBSERVED')
        self.box.now = 50_000_000_000
        self.box.save('connected.json', '{')
        result = self.run_observer()
        self.assertNotIn('state', result)
        self.assertEqual(result['error']['code'], 'CONNECTION_METADATA')

    def test_actual_observer_second_identity_check_detects_pid_reuse(self):
        self.box.install_records()
        def replace(box, path):
            if path.endswith('/net/tcp'):
                box.proc_hook = None
                values = ' '.join(['0']*18+['901']+['0']*30)
                (box.proc / str(box.pid) / 'stat').write_text(f'{box.pid} (reused process) S {values}\n')
        self.box.proc_hook = replace
        self.assertEqual(self.run_observer()['state'], 'UNKNOWN')

    def test_actual_observer_second_identity_check_detects_fd_reuse(self):
        self.box.install_records()
        def replace(box, path):
            if path.endswith('/net/tcp'):
                box.proc_hook = None
                fd = box.proc / str(box.pid) / 'fd/987'
                fd.unlink()
                fd.symlink_to('socket:[6001]')
        self.box.proc_hook = replace
        self.assertEqual(self.run_observer()['state'], 'UNKNOWN')

    def test_actual_observer_directory_replacement_cannot_keep_connected(self):
        self.box.install_records()
        def replace(box, path):
            if path.endswith('/net/tcp'):
                box.proc_hook = None
                box.directory.rename(box.tmp / 'original-directory')
                box.directory.mkdir(mode=0o700)
        self.box.proc_hook = replace
        self.assertEqual(self.run_observer()['state'], 'UNKNOWN')

    def test_actual_observer_file_identity_change_during_read_is_error(self):
        self.box.install_records()
        hits = []
        def replace(box, path, result):
            if path.endswith('/claim.json'):
                hits.append(path)
                if len(hits) >= 2:
                    fields = list(result)
                    fields[1] += 1
                    return os.stat_result(fields)
            return result
        self.box.file_hook = replace
        result = self.run_observer()
        self.assertEqual(result['error']['code'], 'CONNECTION_METADATA')
        self.assertGreaterEqual(len(hits), 2)

    def test_actual_observer_orphan_receipt_is_error_and_private_temporary_is_ignored(self):
        self.box.directory.mkdir(mode=0o700)
        self.box.save('claim.tmp', '{')
        result = self.run_observer()
        self.assertEqual(result['state'], 'PENDING')
        self.box.save('terminal.json', terminal_record(claim_record()))
        self.assertEqual(self.run_observer()['error']['code'], 'CONNECTION_METADATA')

    def test_actual_observer_future_event_is_invalid_but_future_deadline_is_live(self):
        claim = self.box.install_records()
        self.assertEqual(self.run_observer()['state'], 'CONNECTED')
        bad = connection_record(claim)
        bad['connected_monotonic_ns'] = self.box.now+1
        self.box.save('connected.json', bad)
        self.assertEqual(self.run_observer()['error']['code'], 'CONNECTION_METADATA')


if __name__ == '__main__':
    unittest.main(verbosity=2)
