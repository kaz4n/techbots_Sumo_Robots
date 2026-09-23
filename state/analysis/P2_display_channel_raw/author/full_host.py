"""Run unchanged full host targets on an isolated opaque D108 source snapshot."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent
EXPECTED_RENDERER = "9e9d5d9a44d8b0d637f2301d042f7021df890a270995e1806d4d4456dd58c535"


def run(argv, label):
    env = dict(os.environ)
    env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
    started = time.time_ns()
    result = subprocess.run(list(map(str, argv)), text=True, capture_output=True, timeout=600, env=env)
    receipt = {"started_ns": started, "finished_ns": time.time_ns(), "argv": list(map(str, argv)),
               "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    (RAW / (label + ".json")).write_text(json.dumps(receipt, indent=2) + "\n")
    (RAW / (label + ".txt")).write_text(result.stdout + result.stderr)
    print(label, result.returncode, flush=True)
    for line in result.stdout.splitlines():
        if "test cases:" in line or "assertions:" in line or "tests passed" in line:
            print(line, flush=True)
    assert result.returncode == 0, result.stdout + result.stderr


def main():
    with tempfile.TemporaryDirectory(prefix="sumo-d108-full-", dir="/dev/shm") as temporary:
        stage = Path(temporary)
        for name in ("src", "tests"):
            shutil.copytree(ROOT / name, stage / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        (stage / "host").mkdir()
        for name in ("CMakeLists.txt", "motor_gate_main.cpp"):
            shutil.copyfile(ROOT / "host" / name, stage / "host" / name)
        shutil.copytree(ROOT / "host/third_party", stage / "host/third_party")
        hashes = {str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in stage.rglob("*") if path.is_file()}
        assert hashes["src/hal/ui_display.cpp"] == EXPECTED_RENDERER
        (RAW / "full_host_source.json").write_text(json.dumps(hashes, indent=2) + "\n")
        print("FULL_HOST_OPAQUE_COPY_READY " + EXPECTED_RENDERER, flush=True)
        for kind, flags in (("normal", "-O1"), ("san", "-O1 -g -fsanitize=address,undefined "
                           "-fno-sanitize-recover=all -fno-omit-frame-pointer -fno-pie")):
            build = stage / ("build-" + kind)
            run(["cmake", "-S", stage / "host", "-B", build, "-DCMAKE_BUILD_TYPE=Debug",
                 "-DCMAKE_CXX_FLAGS_DEBUG=" + flags,
                 "-DCMAKE_EXE_LINKER_FLAGS=" + ("-no-pie" if kind == "san" else "")], "full_" + kind + "_configure")
            run(["cmake", "--build", build, "-j", "4"], "full_" + kind + "_build")
            run(["ctest", "--test-dir", build, "-V"], "full_" + kind + "_test")
            shutil.copyfile(build / "Testing/Temporary/LastTest.log", RAW / ("full_" + kind + "_LastTest.log"))


if __name__ == "__main__":
    main()
