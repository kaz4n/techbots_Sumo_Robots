# Collect the explicitly selected D102 completed app evidence without MCU access.
# Reuse the frozen-source D101 collector and unchanged D098 offline ELF program.
# Validate the new 85-file digest before writing a separate D102 evidence tree.
import argparse
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = '3bf0da005d3268adfca52bb86f96ab40921c4bb4f2c2d10ea1cd90a8cf2a0f38'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('receipt', type=Path)
    parser.add_argument('mode', choices=('bench-default', 'match-immediate'))
    args = parser.parse_args()
    path = REPO / 'state/analysis/P2_app_dump_target_collect.py'
    spec = importlib.util.spec_from_file_location('d101_collector', path)
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    collector.SOURCE = SOURCE
    collector.RAW = REPO / 'state/analysis/P2_frame_packing_raw'
    collector.collect(args.receipt.resolve(), args.mode)
