"""Invoke unchanged snapshot board tooling with one native compiler process."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import sys

out = Path(__file__).resolve().parent
snapshot = out / 'source_snapshot'
profile = sys.argv[1]
assert profile in ('app', 'reactive_timing')
sys.path.insert(0, str(snapshot / 'tools'))
spec = importlib.util.spec_from_file_location('p5_checked_board_tool', snapshot / 'tools/board_tool.py')
board_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board_tool)
original_remote = board_tool.remote


def serial_remote(board, args, capture=False, timeout=None):
    actual = list(args)
    if actual[:2] == ['arduino-cli', 'compile']:
        actual[2:2] = ['--jobs', '1']
    row = {'utc': datetime.now(timezone.utc).isoformat(), 'board': board,
           'argv': actual, 'capture': capture, 'timeout': timeout}
    try:
        result = original_remote(board, actual, capture=capture, timeout=timeout)
        row['returncode'] = result.returncode
        return result
    except BaseException as error:
        row['error_type'] = type(error).__name__
        row['returncode'] = getattr(error, 'returncode', None)
        raise
    finally:
        with (out / (profile + '_actual_remote_commands.jsonl')).open('a', encoding='utf-8') as log:
            log.write(json.dumps(row) + '\n')


board_tool.remote = serial_remote
sys.argv = ['tools/board_tool.py', 'flash',
            'app' if profile == 'app' else 'bench/reactive_timing', '--compile-only']
board_tool.main()
