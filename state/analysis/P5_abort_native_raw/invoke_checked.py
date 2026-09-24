"""Invoke committed D135 board tooling once, compile-only, one native job."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import json
import sys

out = Path(__file__).resolve().parent
root = out.parents[2]
sys.path.insert(0, str(root / 'tools'))
spec = importlib.util.spec_from_file_location('p5_checked_board_tool', root / 'tools/board_tool.py')
board_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board_tool)
original_remote = board_tool.remote


def serial_remote(board, args, capture=False, timeout=None):
    actual = list(args)
    if actual[:2] == ['arduino-cli', 'compile']:
        actual[2:2] = ['--jobs', '1']
    row = {'utc': datetime.now(timezone.utc).isoformat(), 'board': board,
           'argv': actual, 'capture': capture, 'timeout': timeout}
    if actual[:2] == ['arduino-cli', 'compile'] and '--show-properties=expanded' not in actual:
        (out / 'remote_snapshot_ready.json').write_text(json.dumps(row, indent=2) + '\n')
    try:
        result = original_remote(board, actual, capture=capture, timeout=timeout)
        row['returncode'] = result.returncode
        return result
    except BaseException as error:
        row['error_type'] = type(error).__name__
        row['returncode'] = getattr(error, 'returncode', None)
        raise
    finally:
        with (out / 'actual_remote_commands.jsonl').open('a', encoding='utf-8') as log:
            log.write(json.dumps(row) + '\n')


board_tool.remote = serial_remote
sys.argv = ['tools/board_tool.py', 'flash', 'bench/opener_timing', '--compile-only']
board_tool.main()
