#!/usr/bin/env python3
# Runs independently authored B15/D102 tests without displaying implementation.
# Preserves immutable command, source-hash and failure receipts for each run.
# Executed under WSL with binaries and source snapshots isolated in /dev/shm.
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone

parser = argparse.ArgumentParser()
parser.add_argument("label")
parser.add_argument("--revision", default=None)
args = parser.parse_args()
here = Path(__file__).resolve().parent
root = here.parents[3]
receipt = here / args.label
receipt.mkdir(exist_ok=False)
work = Path(tempfile.mkdtemp(prefix="d102-author-", dir="/dev/shm"))
sources = ["tests/test_frame_packing.cpp", "src/hal/recorder_frames.cpp",
           "src/hal/recorder_frames.h", "src/core/logframe.h", "src/core/types.h",
           "src/config.h", "host/third_party/doctest.h"]
hashes = {}
for name in sources:
    content = (subprocess.check_output(["git", "show", f"{args.revision}:{name}"], cwd=root)
               if args.revision and name != "tests/test_frame_packing.cpp"
               else (root / name).read_bytes())
    destination = work / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    hashes[name] = hashlib.sha256(content).hexdigest()
    stored = receipt / "source" / name
    stored.parent.mkdir(parents=True, exist_ok=True)
    stored.write_bytes(content)
(work / "main.cpp").write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
(work / "abi.cpp").write_text('''#include "hal/recorder_frames.h"
#include <cstdio>
int main() {
  std::printf("FrameBuffer sizeof=%zu alignof=%zu\\n", sizeof(recorder::FrameBuffer), alignof(recorder::FrameBuffer));
  std::printf("StoredFrame sizeof=%zu alignof=%zu\\n", sizeof(recorder::StoredFrame), alignof(recorder::StoredFrame));
  std::printf("size_t sizeof=%zu capacity=%llu cadence=%u\\n", sizeof(std::size_t), static_cast<unsigned long long>(config::LOG_FRAME_CAPACITY), config::LOG_HZ);
}
''')
commands = []

def run(name, command, env=None):
    completed = subprocess.run(command, cwd=work, env=env, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True)
    (receipt / f"{name}.log").write_text(completed.stdout)
    record = {"name": name, "command": command, "cwd": str(work),
              "exit": completed.returncode}
    commands.append(record)
    print(f"{name}: exit={completed.returncode}", flush=True)
    return completed.returncode

base = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
        "-fno-exceptions", "-fno-rtti", "-DDOCTEST_CONFIG_NO_EXCEPTIONS",
        "-Isrc", "-Ihost/third_party"]
run("compiler", ["g++", "--version"])
run("abi_compile", base + ["abi.cpp", "-o", "abi"])
run("abi", [str(work / "abi")])
test_sources = ["tests/test_frame_packing.cpp", "src/hal/recorder_frames.cpp", "main.cpp"]
normal = run("normal_compile", base + ["-O2"] + test_sources + ["-o", "normal"])
if normal == 0:
    run("normal", [str(work / "normal"), "--no-colors"])
sanitizer = run("sanitizer_compile", base + ["-O1", "-g", "-fno-omit-frame-pointer",
                "-fno-pie", "-no-pie", "-fsanitize=address,undefined"] + test_sources + ["-o", "sanitizer"])
if sanitizer == 0:
    environment = os.environ.copy()
    environment.update(ASAN_OPTIONS="detect_leaks=1:abort_on_error=1",
                       UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1")
    run("sanitizer", [str(work / "sanitizer"), "--no-colors"], environment)
summary = {"utc": datetime.now(timezone.utc).isoformat(), "revision": args.revision,
           "root": str(root), "work": str(work), "source_sha256": hashes,
           "sanitizer_environment": {"ASAN_OPTIONS": "detect_leaks=1:abort_on_error=1",
                                     "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1"},
           "commands": commands}
(receipt / "receipt.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
