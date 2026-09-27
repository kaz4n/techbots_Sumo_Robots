# Admits only D244 B7 builds through a checked private D227 deployment caller.
# Preserves artifact and hardware qualification while requiring specific STAND OK.
# Independent D245 host fixtures exercise scope refusal and the retained lifecycle.
import hashlib
import os
from pathlib import Path
import stat
import sys
import types


ROOT = Path(__file__).absolute().parents[1]
BASE = 'tools/deploy_commissioning_app.py'
BASE_PIN = (32202, 'e030c2497605fc77938c70e7cb76e8c29db65322bdb4cba87381a70d2ddcfde4')
COMPILER = 'tools/compile_b7_app.py'
COMPILER_PIN = '267efb9f3f661a12411a41ac75761be2d5a571a59f48e1b965abc4210139330a'
COMPILER_BASE = 'tools/compile_commissioning_app.py'
COMPILER_BASE_PIN = '038a74777db7d26a15ff543d311fc4df2503e6f6b8e3b08fabcfb1c853220462'
CALLER = 'tools/deploy_b7_app.py'
ADAPTER = 'tools/b7_app_upload.py'
CONTRACT = 'state/analysis/P2_b7_deploy_contract.md'

# Literal substitutions are checked against the complete frozen source first.
# Everything outside these closed selection/identity seams remains D227 code.
SUBSTITUTIONS = (
    ("CALLER = 'tools/deploy_commissioning_app.py'", "CALLER = '" + CALLER + "'", 1),
    ("ADAPTER = 'tools/commissioning_app_upload.py'", "ADAPTER = '" + ADAPTER + "'", 1),
    ("CONTRACT = 'state/analysis/P7_commissioning_deploy_contract.md'",
     "CONTRACT = '" + CONTRACT + "'", 1),
    ("COMPILER = 'tools/compile_commissioning_app.py'", "COMPILER = '" + COMPILER + "'", 1),
    ("    COMPILER: '" + COMPILER_BASE_PIN + "',",
     "    COMPILER: '" + COMPILER_PIN + "',\n" +
     "    '" + BASE + "': '" + BASE_PIN[1] + "',\n" +
     "    '" + COMPILER_BASE + "': '" + COMPILER_BASE_PIN + "',", 1),
    ("GATES = dict(b4_stand='GATE P1 PASS', p3_drive='GATE P2 PASS', p3_turn='GATE P2 PASS',\n"
     "    p3_stop='GATE P2 PASS', p4_reactive='GATE P3 PASS', p4_timing='GATE P3 PASS',\n"
     "    p5_abort_timing='GATE P4 PASS')", "GATES = {'b7_brownout': 'GATE P1 PASS'}", 1),
    ("def checked_code(base, root, reviewed_head, *, identified=False):\n",
     "def checked_code(base, root, reviewed_head, *, identified=False):\n"
     "    require(identified is False, 'B7 identified delivery is unavailable')\n", 1),
    ("'tools/board_tool.py'} | set(base.FIXED)",
     "'tools/board_tool.py'} | set(base.FIXED) | set(FROZEN)", 1),
    ("compiler._head_bytes(root, reviewed_head, names)",
     "compiler._checked_base(root)._head_bytes(root, reviewed_head, names)", 1),
    ("'tools/commissioning_app_static_policy.py'", "'tools/b7_app_static_policy.py'", 2),
    ("def checked_qualification(base, root, request, config):\n",
     "def checked_qualification(base, root, request, config):\n"
     "    require(request['profile'] == 'b7_brownout', 'Only B7 can qualify here')\n", 1),
    ("operation = 'stand' if request['profile'] == 'b4_stand' else 'ring'",
     "operation = 'stand'", 1),
    ("def checked_authorization(base, root, scope, now):\n    request = scope['request']\n",
     "def checked_authorization(base, root, scope, now):\n    request = scope['request']\n"
     "    require(request['profile'] == 'b7_brownout', 'Only B7 can be authorized here')\n", 1),
    ("reply = 'STAND OK' if request['profile'] == 'b4_stand' else 'RING OK'",
     "reply = 'STAND OK'", 1),
    ("               _delivery=None):\n    root = Path(root).absolute()",
     "               _delivery=None):\n"
     "    require(_delivery is None, 'B7 identified delivery is unavailable')\n"
     "    root = Path(root).absolute()", 1),
    ("'commissioning-app-deploy-v1'", "'b7-app-deploy-v1'", 1),
    ("'commissioning-app-deploy-check-v1'", "'b7-app-deploy-check-v1'", 1),
    ("'commissioning-app-deploy-outcome-v1'", "'b7-app-deploy-outcome-v1'", 1),
    ("'commissioning-app-attempt-v1'", "'b7-app-deploy-attempt-v1'", 1),
    ("('commissioning_deploy_' + scope['request']['run_id'])",
     "('b7_deploy_' + scope['request']['run_id'])", 1),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_source(root):
    path = root / BASE
    for item in (*reversed(path.parents), path):
        info = item.lstat()
        require((stat.S_ISREG(info.st_mode) if item == path else stat.S_ISDIR(info.st_mode)) and
                not getattr(info, 'st_file_attributes', 0) & 1024, 'Nonplain D227 bootstrap path')
    before = path.stat()
    require(before.st_nlink == 1 and before.st_size == BASE_PIN[0], 'Invalid D227 identity')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    with os.fdopen(os.open(path, flags), 'rb') as stream:
        opened = os.fstat(stream.fileno())
        raw = stream.read(BASE_PIN[0] + 1)
        closed = os.fstat(stream.fileno())
    stamp = lambda info: (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
                         info.st_size, info.st_mtime_ns)
    require(stamp(before) == stamp(opened) == stamp(closed) == stamp(path.stat()) and
            len(raw) == BASE_PIN[0] and hashlib.sha256(raw).hexdigest() == BASE_PIN[1],
            'Frozen D227 bootstrap changed')
    return raw


def load_deployer(*, root=ROOT):
    root = Path(root).absolute()
    source = checked_source(root).decode('utf-8')
    for old, new, count in SUBSTITUTIONS:
        require(source.count(old) == count, 'Frozen D227 adaptation seam changed')
        source = source.replace(old, new)
    module = types.ModuleType('_sumox_b7_checked_d227')
    module.__file__ = str(root / BASE)
    exec(compile(source, str(root / BASE), 'exec'), module.__dict__)
    module.ROOT = root
    return module


def parse_request(argv):
    return load_deployer().parse_request(argv)


def load_scope(root, relative, reviewed_head, target, transport, *, now=None):
    return load_deployer(root=root).load_scope(root, relative, reviewed_head, target, transport, now=now)


def check_only(board, relative, reviewed_head, *, now=None):
    return load_deployer(root=board.ROOT).check_only(board, relative, reviewed_head, now=now)


def upload_precompiled(board, relative, reviewed_head, *, now=None):
    return load_deployer(root=board.ROOT).upload_precompiled(board, relative, reviewed_head, now=now)


def main(argv):
    require(sys.flags.isolated and sys.dont_write_bytecode, 'Python -I -B required')
    return load_deployer().main(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
