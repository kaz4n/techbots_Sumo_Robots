"""Read-only follow-up after UID1000 proc-fd denial; preserve all initial receipts."""
from pathlib import Path
program = (Path(__file__).resolve().parent / 'collect.py').read_text(encoding='utf-8')
exec(program.split('run("01_identity"')[0])
ownership = (HERE / 'remote_ownership.py').read_text(encoding='utf-8')
ownership = ownership.replace("item['exe'] = os.readlink(path / 'exe')",
    "item['exe'] = os.readlink(path / 'exe')\n            item['cgroup'] = (path / 'cgroup').read_text().splitlines()")
run('07_privileged_socket_ownership', ['sudo', '-n', 'python3', '-c', ownership])
run('08_serial_path_units', ['systemctl', 'show', 'arduino-router-serial.path',
    'arduino-router-serial.service', '--property=Id', '--property=ActiveState',
    '--property=SubState', '--property=FragmentPath', '--property=ExecStart',
    '--property=MainPID', '--property=Triggers', '--property=TriggeredBy'])
run('09_related_unit_files', ['python3', '-c', (HERE / 'remote_related_units.py').read_text(encoding='utf-8')])
