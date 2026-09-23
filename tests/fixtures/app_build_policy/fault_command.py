#!/usr/bin/python3
# Injects independent failures into the documented synthetic command protocol.
# Proves integration rejects incorrect evidence rather than merely invoking validators.
# Runs only as an isolated remote-bin fixture, with no physical transport available.
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import sys


helper = runpy.run_path(os.environ['APP_POLICY_BASE_HELPER'])
name = Path(sys.argv[0]).name
args = sys.argv[1:]
fault = os.environ.get('APP_POLICY_FAULT', '')
stdout, stderr = io.StringIO(), io.StringIO()
function = {'arduino-cli': helper['fake_arduino'],
            'sha256sum': helper['fake_sha256sum']}[name]
with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
    status = function(args)
out, err = stdout.getvalue(), stderr.getvalue()

if name == 'arduino-cli' and args == ['version']:
    if fault == 'cli_version':
        out = out.replace('1.5.1', '1.5.2')
    if fault == 'cli_commit':
        out = out.replace('01f3d4f2b', '01f3d4f2c')

if (name == 'arduino-cli' and args and args[0] == 'compile' and '--json' in args
        and '--show-properties=expanded' not in args):
    if fault == 'compile_failure':
        out = '{"success":false,"error":"fixture failed","compiler_out":' \
              '"retained inner stdout\\n","compiler_err":"retained inner stderr\\n"}\n'
        err, status = 'retained outer stderr\n', 43
    elif fault == 'compile_nonzero_success':
        err, status = 'nonzero process despite success JSON\n', 43
    elif fault == 'compile_malformed':
        out = '{"success":true, broken\n'
    elif fault in ('compile_libraries', 'compile_property_drift', 'compile_failed_flag'):
        document = json.loads(out)
        if fault == 'compile_libraries':
            document['builder_result']['used_libraries'] = [{'name': 'SumoPolicyFixture'}]
        elif fault == 'compile_property_drift':
            values = document['builder_result']['build_properties']
            values[:] = [value if not value.startswith('build.link_mode=') else
                         'build.link_mode=static' for value in values]
        else:
            document['success'] = False
        out = json.dumps(document) + '\n'

if name == 'sha256sum':
    lines = out.splitlines()
    pin_rows = [i for i, line in enumerate(lines) if '/fixture/.arduino15/' in line]
    artifact_rows = [i for i, line in enumerate(lines)
                     if Path(line[66:]).name.startswith('app.ino')]
    if fault == 'changed_pin' and pin_rows:
        index = pin_rows[0]
        lines[index] = '0' * 64 + lines[index][64:]
    elif fault == 'missing_pin' and pin_rows:
        del lines[pin_rows[0]]
        err, status = 'fixture dependency file missing\n', 1
    elif fault == 'empty_artifact' and artifact_rows:
        index = artifact_rows[0]
        lines[index] = hashlib.sha256(b'').hexdigest() + lines[index][64:]
    elif fault == 'missing_artifact' and artifact_rows:
        del lines[artifact_rows[0]]
        err, status = 'fixture artifact missing\n', 1
    elif fault == 'malformed_hash' and lines:
        lines[0] = 'z' * 64 + lines[0][64:]
    elif fault == 'extra_hash' and lines:
        lines.append(lines[0])
    elif fault == 'reordered_hash':
        lines.reverse()
    elif fault == 'hash_wrong_path' and lines:
        lines[0] += '.other'
    out = ''.join(line + '\n' for line in lines)

sys.stdout.write(out)
sys.stderr.write(err)
raise SystemExit(status)
