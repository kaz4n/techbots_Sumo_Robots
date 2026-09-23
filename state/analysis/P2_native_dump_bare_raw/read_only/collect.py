"""Read Linux metadata/source files only; never open a UART or socket endpoint."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("board_tool", ROOT / "tools/board_tool.py")
board = importlib.util.module_from_spec(spec)
spec.loader.exec_module(board)
os.environ["SUMO_TRANSPORT"] = "adb"
os.environ["SUMO_ADB_SERIAL"] = "2629958581"
os.environ["SUMO_ADB_EXECUTABLE"] = str(Path(os.environ["LOCALAPPDATA"]) /
    "Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe")

def stamp():
    return datetime.now(timezone.utc).isoformat()

def run(name, argv):
    destination = HERE / (name + ".json")
    if destination.exists():
        raise RuntimeError("Refuse to replace receipt " + str(destination))
    receipt = {"start_utc": stamp(), "target": board.target(), "remote_argv": argv,
        "transport_argv": [board.adb_executable(), "-s", board.target(), "shell", "-T", shlex.join(argv)],
        "timeout_seconds": 45}
    try:
        result = board.remote(board.target(), argv, capture=True, timeout=45)
        receipt.update(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except subprocess.CalledProcessError as error:
        receipt.update(returncode=error.returncode, stdout=error.stdout, stderr=error.stderr)
    except subprocess.TimeoutExpired as error:
        receipt.update(returncode=None, timed_out=True, stdout=repr(error.stdout), stderr=repr(error.stderr))
    receipt["end_utc"] = stamp()
    for key in ("stdout", "stderr"):
        receipt[key + "_sha256"] = hashlib.sha256((receipt.get(key) or "").encode()).hexdigest()
    destination.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(name, receipt["returncode"], flush=True)

run("01_identity", ["python3", "-c", "import os,datetime,json; print(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),uid=os.getuid(),gid=os.getgid())))"])
run("02_package", ["dpkg-query", "-W", "-f=${Package} ${Version} ${Architecture}\\n", "arduino-router"])
run("03_package_paths", ["dpkg-query", "-L", "arduino-router"])
properties = ["ActiveState", "SubState", "MainPID", "FragmentPath", "DropInPaths", "User", "Group",
    "ExecMainStartTimestamp", "ExecMainStartTimestampMonotonic", "NRestarts", "ExecStart", "ExecStartPre", "ExecStopPost"]
run("04_service", ["systemctl", "show", "arduino-router.service", *["--property=" + x for x in properties]])
run("05_known_files", ["python3", "-c", (HERE / "remote_files.py").read_text(encoding="utf-8")])
run("06_socket_ownership", ["python3", "-c", (HERE / "remote_ownership.py").read_text(encoding="utf-8")])
