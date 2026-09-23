"""Compile frozen D108 tests against opaque source copies; preserve red and green."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
RAW = Path(__file__).resolve().parent


def run(argv, label, expected=0):
    result = subprocess.run(list(map(str, argv)), cwd=ROOT, text=True, capture_output=True, timeout=180)
    receipt = {"time_ns": time.time_ns(), "argv": list(map(str, argv)), "returncode": result.returncode,
               "expected": expected, "stdout": result.stdout, "stderr": result.stderr}
    (RAW / (label + ".json")).write_text(json.dumps(receipt, indent=2) + "\n")
    (RAW / (label + ".txt")).write_text(result.stdout + result.stderr)
    print(label, result.returncode, flush=True)
    for line in result.stdout.splitlines():
        if "test cases:" in line or "assertions:" in line: print(line, flush=True)
    if expected == "failure": assert result.returncode != 0
    else: assert result.returncode == expected, result.stdout + result.stderr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("--expect-failure", action="store_true")
    parser.add_argument("--renderer-hash", required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="sumo-d108-author-", dir="/dev/shm") as temporary:
        stage = Path(temporary); source = stage / "src"; tests = stage / "tests"
        shutil.copytree(ROOT / "src", source); tests.mkdir()
        for name in ("test_ui_display.cpp", "test_display_channels.cpp", "robot_scenario.h"):
            shutil.copyfile(ROOT / "tests" / name, tests / name)
        sha = {str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest()
               for folder in (source, tests) for path in folder.rglob("*") if path.is_file()}
        assert sha["src/hal/ui_display.cpp"] == args.renderer_hash
        (RAW / (args.label + "_source.json")).write_text(json.dumps(sha, indent=2) + "\n")
        shutil.copyfile(source / "hal/ui_display.cpp", RAW / (args.label + "_ui_display.cpp"))
        print("OPAQUE_COPY_READY " + args.renderer_hash, flush=True)
        (stage / "main.cc").write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
        common = ["g++", "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                  "-fno-exceptions", "-fno-rtti", "-DDOCTEST_CONFIG_NO_EXCEPTIONS",
                  "-I", source, "-I", tests, "-isystem", ROOT / "host/third_party"]
        files = [stage / "main.cc", *sorted((source / "core").glob("*.cpp")),
                 source / "hal/ui_display.cpp", tests / "test_ui_display.cpp", tests / "test_display_channels.cpp"]
        for kind, flags in (("normal", []), ("san", ["-fsanitize=address,undefined",
                            "-fno-sanitize-recover=all", "-fno-omit-frame-pointer", "-no-pie"])):
            binary = stage / kind; label = args.label + "_" + kind
            run([*common, *flags, *files, "-o", binary], label + "_build")
            run([binary, "--no-colors"], label + "_run", "failure" if args.expect_failure else 0)


if __name__ == "__main__":
    main()
