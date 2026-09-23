# Collects D117 completed app/recorder artifacts through existing checked collectors.
# Changes only the evidence destination and exact explicit source selection.
# Performs board-Linux offline reads; never compiles, uploads or accesses the MCU.
import argparse
import importlib.util
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'state/analysis/P2_dump_fifo_raw'


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'state/analysis' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('project', choices=('app', 'recorder'))
    parser.add_argument('receipt', type=Path)
    parser.add_argument('mode', choices=('bench-default', 'match-immediate'))
    parser.add_argument('--source', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{64}', args.source):
        raise ValueError('Requires exact source SHA256')
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


if __name__ == '__main__':
    main()
