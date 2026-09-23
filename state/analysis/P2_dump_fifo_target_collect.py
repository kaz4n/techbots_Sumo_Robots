# Collects D117 completed app/recorder artifacts through existing checked collectors.
# Changes only the evidence destination and exact explicit source selection.
# Performs board-Linux offline reads; never compiles, uploads or accesses the MCU.
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'state/analysis/P2_dump_fifo_raw'
ABI_PROGRAM = r'''
import hashlib,json,pathlib,subprocess,sys
path=pathlib.Path(sys.argv[1]); expected=sys.argv[2]
tool='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-gdb'
record={'before_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
args=[tool,'-nx','-nh','-batch',str(path),'-ex','set language c++','-ex','set max-value-size unlimited']
for name in ('recorder::dump::UnoQDumpPort','app::Runtime','app::Transaction','app::DumpPort','recorder::dump::Transfer'):
 args+=['-ex','p sizeof('+name+')','-ex','p alignof('+name+')','-ex','ptype /o '+name]
record.update(argv=args,gdb_sha256=hashlib.sha256(pathlib.Path(tool).read_bytes()).hexdigest())
try:
 if record['before_sha256']!=expected:raise ValueError('Debug ELF changed before ABI query')
 r=subprocess.run(args,capture_output=True,text=True,timeout=30)
 record.update(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
 record['after_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
 if r.returncode!=0 or r.stderr or record['after_sha256']!=expected:raise ValueError('ABI query or identity failed')
except Exception as e:
 record.update(error=type(e).__name__,message=str(e),stdout=getattr(e,'stdout',record.get('stdout','')),stderr=getattr(e,'stderr',record.get('stderr','')))
 for key in ('stdout','stderr'):
  if isinstance(record.get(key),bytes):record[key]=record[key].decode(errors='replace')
print(json.dumps(record))
sys.exit(1 if 'error' in record else 0)
'''


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'state/analysis' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def app_abi(prior, args):
    checked = prior.collector.policy.decode((args.receipt / 'verified.json').read_text())
    debug = checked['build_path'] + '/app.ino_debug.elf'
    output = RAW / ('target_' + args.source[:8] + '_' + args.mode)
    command = ['python3', '-c', ABI_PROGRAM, debug, checked['file_sha256'][debug]]
    record = dict(argv=command, start_utc=datetime.now(timezone.utc).isoformat(),
                  scope='Board Linux offline debug ELF; no MCU attachment', timeout_seconds=60)
    try:
        result = prior.collector.board.remote('2629958581', command, capture=True, timeout=60)
        record.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
        if result.returncode != 0 or result.stderr:
            raise ValueError('App ABI query failed; receipt preserved')
        data = prior.collector.policy.decode(result.stdout)
        if 'error' in data:
            raise ValueError('App ABI returned failure; receipt preserved')
        (output / 'd117_abi.json').write_text(json.dumps(data, indent=2) + '\n')
    except Exception as error:
        record.update(error=type(error).__name__, message=str(error))
        for key in ('stdout', 'stderr'):
            value = getattr(error, key, record.get(key, '')) or ''
            record[key] = value.decode(errors='replace') if isinstance(value, bytes) else value
        raise
    finally:
        record['end_utc'] = datetime.now(timezone.utc).isoformat()
        (output / 'd117_abi_receipt.json').write_text(json.dumps(record, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('project', choices=('app', 'recorder'))
    parser.add_argument('receipt', type=Path)
    parser.add_argument('mode', choices=('bench-default', 'match-immediate'))
    parser.add_argument('--source', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{64}', args.source):
        raise ValueError('Requires exact source SHA256')
    if os.environ.get('SUMO_TRANSPORT') != 'adb' or os.environ.get('SUMO_ADB_SERIAL') != '2629958581':
        raise ValueError('Requires explicit ADB target2629958581')
    if args.project == 'recorder':
        if args.mode != 'bench-default':
            raise ValueError('Recorder requires inert default')
        prior = load('d116_collector', 'P2_recorder_transport_target_collect.py')
        prior.RAW = RAW
        sys.argv = [sys.argv[0], args.source, args.mode, '--receipt', str(args.receipt)]
        prior.main()
        return
    prior = load('d105_collector', 'P2_calibration_delivery_target_collect.py')
    prior.collector.SOURCE = args.source
    prior.EXPECTED_FILES = 91
    prior.collector.RAW = RAW
    prior.collector.freeze_source = prior.freeze_source
    prior.collector.collect(args.receipt.resolve(), args.mode)
    app_abi(prior, args)


if __name__ == '__main__':
    main()
