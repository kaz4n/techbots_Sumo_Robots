#!/usr/bin/python3
# Substitutes local transport and board commands in an isolated tooling fixture.
# Prevents the test suite from reaching SSH, a router, or an upload device.
# Exercised only through the public shell entry points in test_tools.py.
import json
import os
from pathlib import Path
import shlex
import socket
import subprocess
import sys
import types


def record(kind, **fields):
    with open(os.environ['FAKE_TRACE'], 'a', encoding='utf-8') as output:
        output.write(json.dumps(dict(kind=kind, **fields)) + '\n')


def fake_ssh(args):
    record('ssh', args=args)
    if os.environ.get('FAKE_FAIL') == 'ssh':
        return 41
    index = 0
    while index < len(args) and args[index].startswith('-'):
        index += 2 if args[index] in ('-o', '-p', '-i', '-l', '-F') else 1
    if index >= len(args) or args[index] != 'fixture@board.invalid':
        return 91
    command = shlex.split(' '.join(args[index + 1:]))
    if not command or command[0] not in ('arduino-cli', 'mkdir', 'python3'):
        record('rejected_remote', args=command)
        return 92
    if command[0] == 'mkdir':
        root = Path(os.environ['FAKE_TEMP_ROOT']).resolve()
        for arg in command[1:]:
            if not arg.startswith('-') and not Path(arg).resolve().is_relative_to(root):
                return 93
    env = os.environ.copy()
    env['PATH'] = os.environ['FAKE_REMOTE_BIN'] + os.pathsep + env['PATH']
    return subprocess.run(command, env=env, check=False).returncode


def fake_rsync(args):
    record('rsync', args=args)
    return 42 if os.environ.get('FAKE_FAIL') == 'sync' else 0


def fake_arduino(args):
    record('arduino', args=args)
    if args[:2] == ['core', 'list']:
        version = os.environ.get('FAKE_CORE_VERSION', '1.0.0')
        print('ID Installed Latest Name')
        if version:
            print('arduino:zephyr ' + version + ' 1.0.0 Arduino Zephyr')
        return 0
    if not args or args[0] not in ('compile', 'upload'):
        return 94
    if os.environ.get('FAKE_FAIL') == args[0]:
        return {'compile': 43, 'upload': 44}[args[0]]
    print('SIMULATED ' + args[0])
    return 0


class NoInput:
    def read(self, *args):
        record('stdin_read')
        raise AssertionError('Monitor must not read keyboard input')

    readline = read
    readinto = read

    @property
    def buffer(self):
        return self


class ReceiveOnlySocket:
    def __init__(self, *args, **kwargs):
        self.remaining = b'fixture monitor counter=7\n'

    def connect(self, endpoint):
        record('socket_connect', endpoint=endpoint)

    def recv(self, size):
        record('socket_recv', size=size)
        data, self.remaining = self.remaining[:size], self.remaining[size:]
        return data

    def send(self, *args):
        record('socket_send')
        raise AssertionError('Monitor must not transmit to the MCU')

    sendall = send
    sendto = send

    def settimeout(self, value):
        pass

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def fake_remote_python(args):
    record('remote_python', args=args)
    args = [arg for arg in args if arg != '-u']
    if len(args) != 2 or args[0] != '-c':
        return 95
    replacement = types.ModuleType('socket')
    replacement.AF_INET, replacement.SOCK_STREAM = socket.AF_INET, socket.SOCK_STREAM
    replacement.socket = ReceiveOnlySocket

    def connect(endpoint, *args, **kwargs):
        result = ReceiveOnlySocket()
        result.connect(endpoint)
        return result

    replacement.create_connection = connect
    sys.modules['socket'] = replacement
    sys.stdin = NoInput()
    exec(compile(args[1], '<remote-monitor-request>', 'exec'), {'__name__': '__main__'})
    return 0


if __name__ == '__main__':
    functions = {'ssh': fake_ssh, 'rsync': fake_rsync,
                 'arduino-cli': fake_arduino, 'python3': fake_remote_python}
    raise SystemExit(functions[Path(sys.argv[0]).name](sys.argv[1:]))
