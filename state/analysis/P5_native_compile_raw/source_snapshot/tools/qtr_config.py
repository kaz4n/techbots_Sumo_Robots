# Decodes one exact B13 threshold snippet into an explicitly unattributed receipt.
# Keeps received calibration evidence separate from an approved config.h change.
# Independent D105 parser and actual-Runtime round trips verify this boundary.
import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import sys


def decode_snippet(blob, timeout_us):
    if type(blob) is not bytes or not 1 <= len(blob) <= 79:
        raise ValueError('Expected one canonical immutable snippet of at most79 bytes')
    if type(timeout_us) is not int or not 1 <= timeout_us <= 0x7fffffff:
        raise ValueError('timeout_us must be an explicit positive half-range integer')
    number = rb'([1-9][0-9]{0,9})U'
    pattern = rb'QTR_WHITE_US\[4\] = \{' + rb', '.join([number] * 4) + rb'\}; // us\n'
    match = re.fullmatch(pattern, blob)
    if match is None:
        raise ValueError('Input is not exactly one canonical QTR config line')
    values = [int(value) for value in match.groups()]
    if any(value > timeout_us for value in values):
        raise ValueError('Threshold exceeds the supplied firmware timeout')
    return {'white_us': values, 'timeout_us': timeout_us,
            'provenance': 'UNATTRIBUTED_BARE_LINE'}


def reject_symlinks(path):
    for item in (path, *path.parents):
        if item.is_symlink():
            raise ValueError('Symlink paths are not accepted')


def capture_file(source, destination, timeout_us):
    source, destination = Path(source), Path(destination)
    reject_symlinks(source)
    reject_symlinks(destination)
    if not stat.S_ISREG(source.stat().st_mode):
        raise ValueError('Input must be a regular file')
    if destination.exists():
        raise ValueError('Output directory must be new')
    with source.open('rb') as stream:
        blob = stream.read(80)
    receipt = decode_snippet(blob, timeout_us)
    receipt.update(sha256=hashlib.sha256(blob).hexdigest(), byte_count=len(blob))
    destination.mkdir(exist_ok=False)
    with (destination / 'snippet.txt').open('xb') as stream:
        stream.write(blob)
    with (destination / 'receipt.json').open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write('\n')
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description='Validate one received QTR config line; never apply it')
    parser.add_argument('input')
    parser.add_argument('--timeout-us', type=int, required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args(argv)
    try:
        receipt = capture_file(args.input, args.output_dir, args.timeout_us)
    except (OSError, ValueError) as error:
        print(f'QTR snippet rejected: {error}', file=sys.stderr)
        return 1
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
