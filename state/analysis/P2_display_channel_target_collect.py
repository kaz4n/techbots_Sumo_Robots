# Freezes D108 exact app source and already completed checked target artifacts.
# Reuses the existing verified collector without issuing compile/upload/MCU commands.
# Records source, object, ELF, package and installed-tool identity for separate review.
import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('d105_collector',
    ROOT / 'state/analysis/P2_calibration_delivery_target_collect.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('receipt', type=Path)
    parser.add_argument('mode', choices=('bench-default', 'match-immediate'))
    parser.add_argument('--source', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{64}', args.source):
        raise ValueError('Requires the exact explicit source SHA256')
    prior.collector.SOURCE = args.source
    prior.EXPECTED_FILES = 91
    prior.collector.RAW = ROOT / 'state/analysis/P2_display_channel_raw'
    prior.collector.freeze_source = prior.freeze_source
    prior.collector.collect(args.receipt.resolve(), args.mode)
