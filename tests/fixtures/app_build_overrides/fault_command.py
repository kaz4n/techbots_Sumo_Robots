#!/usr/bin/python3
# Injects D100 faults into isolated remote commands without a board or network.
# Exercises the documented shell probe against local regular and dangling paths.
# Used only by test_app_build_overrides.py with the controlled fixture helper.
import contextlib
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile


helper = runpy.run_path(os.environ['APP_OVERRIDE_BASE_HELPER'])
name = Path(sys.argv[0]).name
args = sys.argv[1:]
fault = os.environ.get('APP_OVERRIDE_FAULT', '')


def shell_probe():
    helper['record']('override_execution', args=args)
    if len(args) != 9 or args[0] != '-c' or args[2] != 'sumo-app-override-check':
        return 96
    if any(not path.startswith('/') for path in args[3:]):
        return 96
    expected = 'for path do if test -e "$path" || test -L "$path"; then ' \
               "printf 'Unreviewed app override: %s\\n' \"$path\" >&2; exit 1; fi; done"
    if args[1] != expected:
        print('Unexpected override shell literal', file=sys.stderr)
        return 96
    with tempfile.TemporaryDirectory(prefix='sumo-override-paths-') as folder:
        paths = [str(Path(folder) / ('override-' + str(index))) for index in range(6)]
        if fault.startswith(('override_file_', 'override_link_')):
            index = int(fault.rsplit('_', 1)[1])
            path = Path(paths[index])
            if fault.startswith('override_link_'):
                path.symlink_to(Path(folder) / 'missing-target')
            else:
                path.write_text('recipe.hooks.prebuild.99.pattern=unreviewed\n')
        # Run the production-supplied fixed script, with only isolated local paths.
        return subprocess.run(['/bin/sh', '-c', args[1], args[2], *paths],
                              check=False).returncode


if name == 'sh':
    raise SystemExit(shell_probe())

stdout, stderr = io.StringIO(), io.StringIO()
function = {'arduino-cli': helper['fake_arduino'], 'sha256sum': helper['fake_sha256sum']}[name]
with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
    status = function(args)
out, err = stdout.getvalue(), stderr.getvalue()

if name == 'arduino-cli' and args[:2] == ['config', 'get']:
    which = 'data' if args[2] == 'directories.data' else 'user'
    if fault.startswith('directory_' + which + '_'):
        defect = fault.rsplit('_', 1)[1]
        outputs = {'relative': '"relative/path"\n', 'empty': '""\n',
                   'malformed': '{bad\n', 'object': '{"value":"/fixture"}\n',
                   'multiple': '"/first"\n"/second"\n', 'null': 'null\n',
                   'nonzero': '"/fixture/.arduino15"\n'}
        out = outputs[defect]
        if defect == 'nonzero':
            err, status = 'retained directory stderr\n', 47

if name == 'arduino-cli' and '--show-properties=expanded' in args:
    if fault == 'preflight_malformed':
        out = '{bad preflight\n'
    elif fault == 'preflight_nonzero':
        err, status = 'retained preflight outer stderr\n', 48
    elif fault == 'preflight_failure':
        out = '{"success":false,"error":"retained preflight failure",' \
              '"compiler_out":"retained preflight inner stdout\\n",' \
              '"compiler_err":"retained preflight inner stderr\\n"}\n'
        err, status = 'retained preflight outer stderr\n', 48
    elif fault.startswith('preflight_'):
        document = json.loads(out)
        entries = document['builder_result']['build_properties']
        values = dict(entry.split('=', 1) for entry in entries)
        changes = {
            'preflight_recipe': ('recipe.cpp.o.pattern', values['recipe.cpp.o.pattern'].replace(
                '-DMATCH=0 -DMOTORS_ALLOWED=0', '-DMATCH=1 -DMOTORS_ALLOWED=1')),
            'preflight_compiler': ('compiler.cpp.cmd', 'unreviewed-compiler'),
            'preflight_hook': ('recipe.hooks.prebuild.1.pattern', 'unreviewed-hook'),
            'preflight_new_hook': ('recipe.hooks.prebuild.99.pattern', 'unreviewed-hook'),
            'preflight_numbered_link': ('recipe.c.combine.5.pattern', 'unreviewed-link'),
            'preflight_data_root': ('runtime.platform.path', '/different/platform'),
        }
        if fault == 'preflight_missing_recipe':
            values.pop('recipe.c.o.pattern')
        elif fault == 'preflight_unsuccessful':
            document['success'] = False
        else:
            key, value = changes[fault]
            values[key] = value
        document['builder_result']['build_properties'] = [key + '=' + value
                                                           for key, value in values.items()]
        out = json.dumps(document) + '\n'

if name == 'sha256sum' and fault.startswith('prepin_'):
    rows = out.splitlines()
    if fault == 'prepin_changed' and rows:
        rows[0] = '0' * 64 + rows[0][64:]
    elif fault == 'prepin_missing' and rows:
        rows.pop(0)
        err, status = 'retained missing pin stderr\n', 49
    elif fault == 'prepin_malformed' and rows:
        rows[0] = 'invalid hash row'
    out = ''.join(row + '\n' for row in rows)

sys.stdout.write(out)
sys.stderr.write(err)
raise SystemExit(status)
