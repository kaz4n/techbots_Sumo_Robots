# Copies exactly two reviewed compile artifacts into a fresh board Linux folder.
# Supplies immutable passive-readout inputs without uploading or touching the MCU.
# Saves argv, hashes and actual results; an existing destination is an error.
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board

SOURCE = '396bcc45fbaf30d38b170bf0c0063c555d5e88cdad512829b86a52ffede18642'
RECEIPT = ROOT / 'build/app-receipts/73d13df1e7244ddc8a71d1a7e52c0ed8/verified.json'
OUT = ROOT / 'state/analysis/P2_ui_adc_probe_raw/artifact_preparation.json'
PROGRAM = r'''
import hashlib,json,os,pathlib,stat,sys
data=json.loads(sys.argv[1]); dest=pathlib.Path(data['destination'])
assert dest.parent==pathlib.Path('/home/arduino/sumox26-capture-input')
assert not os.path.lexists(dest)
for path in [dest.parent,*dest.parent.parents]:
    if os.path.lexists(path):
        info=path.lstat(); assert stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode)
payloads={}
for item in data['files']:
    src=pathlib.Path(item['source']); assert src.is_file() and not src.is_symlink()
    blob=src.read_bytes(); assert len(blob)==19840
    assert hashlib.sha256(blob).hexdigest()==item['sha256']
    assert pathlib.Path(item['name']).name==item['name']
    payloads[item['name']]=blob
assert len(payloads)==2
dest.parent.mkdir(mode=0o700,exist_ok=True)
assert dest.parent.stat().st_uid==os.getuid()
dest.mkdir(mode=0o700)
result={}
for name,blob in payloads.items():
    fd=os.open(dest/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream: stream.write(blob)
    actual=(dest/name).read_bytes(); assert actual==blob
    result[name]={'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest()}
print(json.dumps({'destination':str(dest),'files':result,'MCU_actions':False}))
'''


def main():
    assert not OUT.exists()
    receipt = json.loads(RECEIPT.read_text())
    assert receipt['source_sha256'] == SOURCE and receipt['compiler_returncode'] == 0
    assert receipt['precompile_checks'] and receipt['fqbn'] == 'arduino:zephyr:unoq'
    files = []
    for name, expected, directory in (
        ('ui_adc_probe.ino.elf', '76e23fe03631d5cc2144578d35ca78b9bafd44158e0d18b2ab026922e4c9d05b', 'build_path'),
        ('ui_adc_probe.ino.elf-zsk.bin', '567fb90da6965cf74efc5ac2221e543d6d2150e3bf70ddae3e2346e6646c7fb9', 'artifacts')):
        source = receipt[directory] + '/' + name
        assert receipt['file_sha256'][source] == expected
        files.append(dict(name=name, source=source, sha256=expected))
    assert board.transport() == 'adb' and board.target() == '2629958581'
    argument = dict(destination='/home/arduino/sumox26-capture-input/ui_adc_probe_' + SOURCE, files=files)
    command = ['python3', '-c', PROGRAM, json.dumps(argument)]
    record = dict(argv=command, target=board.target(), started_utc=datetime.now(timezone.utc).isoformat())
    try:
        result = board.remote(board.target(), command, capture=True, timeout=10)
        record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except Exception as error:
        record.update(error=repr(error), returncode=getattr(error, 'returncode', None),
                      stdout=getattr(error, 'stdout', None), stderr=getattr(error, 'stderr', None))
        raise
    finally:
        record['finished_utc'] = datetime.now(timezone.utc).isoformat()
        with OUT.open('x') as stream:
            json.dump(record, stream, indent=2)
            stream.write('\n')
    print(result.stdout)


if __name__ == '__main__':
    main()
