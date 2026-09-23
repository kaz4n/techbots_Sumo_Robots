# Reads completed target types and exporter stack instructions without MCU access.
# Binds offline GDB/objdump output to the checked build and installed tools.
# Records failures explicitly; type size and static frames are not stack watermark.
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import board_tool as board

PROGRAM = r'''
import hashlib,json,pathlib,subprocess,sys
debug,final=sys.argv[1:]
prefix='/home/arduino/.arduino15/packages/zephyr/tools/arm-zephyr-eabi/1.0.1/bin/arm-zephyr-eabi-'
records=[]
def run(args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=30)
 records.append(dict(argv=args,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
args=[prefix+'gdb','-nx','-nh','-batch',debug,'-ex','set language c++',
 '-ex','set max-value-size unlimited']
for query in ['p sizeof(app::Runtime)','p alignof(app::Runtime)',
 'p sizeof(app::CalibrationOutputReport)','p sizeof(line_qtr::Thresholds)',
 'p sizeof(app::SetupGrants)','ptype /o app::Runtime','ptype /o app::CalibrationOutputReport']:
 args+=['-ex',query]
run(args)
for name in ['_ZN3app7Runtime22writeCalibrationOutputEj',
 '_ZN7qtr_cal12formatConfigERKNS_6ReportEPcjRj',
 '_ZN3app7Runtime24serviceCalibrationOutputEv','_ZN3app7Runtime12postDecisionEv']:
 run([prefix+'objdump','-dr','--disassemble='+name,final])
paths=[debug,final,prefix+'gdb',prefix+'objdump']
print(json.dumps(dict(commands=records,file_sha256={p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in paths}),indent=2))
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('receipt', type=Path)
    parser.add_argument('mode', choices=('bench-default', 'bench-immediate', 'match-immediate'))
    parser.add_argument('--large-types', action='store_true')
    args = parser.parse_args()
    checked = json.loads((args.receipt / 'verified.json').read_text())
    if checked['compiler_returncode'] != 0 or '/' + args.mode + '/' not in checked['build_path']:
        raise ValueError('Requires successful checked receipt for requested mode')
    output = ROOT / 'state/analysis/P2_pin_table_raw' / ('abi_' + checked['source_sha256'][:8] + '_' + args.mode)
    if args.large_types:
        output = output.with_name(output.name + '_large_types')
    output.mkdir(parents=True, exist_ok=False)
    command = ['python3', '-c', PROGRAM, checked['build_path'] + '/app.ino_debug.elf',
               checked['build_path'] + '/app.ino.elf']
    run = dict(argv=command, source_sha256=checked['source_sha256'],
               start_utc=datetime.now(timezone.utc).isoformat(),
               scope='Board Linux files/offline tools only; no MCU/compile/upload/reset')
    result = board.remote(board.target(), command, capture=True, timeout=90)
    (output / 'stdout.json').write_text(result.stdout, encoding='utf-8')
    (output / 'stderr.txt').write_text(result.stderr, encoding='utf-8')
    run.update(returncode=result.returncode, end_utc=datetime.now(timezone.utc).isoformat())
    (output / 'receipt.json').write_text(json.dumps(run, indent=2) + '\n')
    data = json.loads(result.stdout)
    for path, digest in data['file_sha256'].items():
        if path in checked['file_sha256']:
            assert digest == checked['file_sha256'][path]
    assert result.returncode == 0 and not result.stderr
    assert all(c['returncode'] == 0 and not c['stderr'] for c in data['commands'])
    print(json.dumps(dict(path=str(output.relative_to(ROOT)), values=data['commands'][0]['stdout'].splitlines()[:5])))


if __name__ == '__main__':
    main()
