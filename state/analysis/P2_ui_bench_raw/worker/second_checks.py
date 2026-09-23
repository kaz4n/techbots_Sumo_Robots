"""Reuse the unchanged first-check programs with separate second-source receipts."""
from pathlib import Path

raw = Path(__file__).resolve().parent
statuses = []
for filename, replacements in [
    ('syntax_check.py', [('first_source_freeze.json', 'second_source_freeze.json'),
                         ('first_syntax.json', 'second_syntax.json')]),
    ('function_lengths.py', [('first_function_lengths.json', 'second_function_lengths.json')])]:
    code = (raw / filename).read_text()
    for old, new in replacements:
        code = code.replace(old, new)
    try:
        exec(compile(code, str(raw / filename), 'exec'), {'__file__': str(raw / filename), '__name__': '__main__'})
    except SystemExit as error:
        statuses.append(bool(error.code))
raise SystemExit(any(statuses))
