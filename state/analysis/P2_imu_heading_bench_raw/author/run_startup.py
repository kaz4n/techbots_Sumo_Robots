"""Rerun only the approved additive Native startup coverage, using frozen harness methods."""
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from tests.tooling import test_imu_heading_bench as harness

harness.RAW = harness.RAW / "startup"
case = harness.ImuHeadingBenchTests()
with tempfile.TemporaryDirectory(prefix="sumo-d111-startup-", dir="/dev/shm") as temporary:
    stage = Path(temporary)
    source, bench = stage / "src", stage / "bench"
    shutil.copytree(ROOT / "src", source)
    shutil.copytree(ROOT / "bench/imu_heading", bench)
    shutil.copyfile(harness.CASES, stage / "cases.cc")
    harness.receipt("opaque_source_copy", {"sha256": {
        str(p.relative_to(stage)): hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in (source, bench) for p in sorted(folder.rglob("*")) if p.is_file()},
        "cases_sha256": hashlib.sha256((stage / "cases.cc").read_bytes()).hexdigest(),
        "harness_sha256": hashlib.sha256(Path(harness.__file__).read_bytes()).hexdigest()})
    (stage / "Arduino.h").write_text("#pragma once\nunsigned long micros();\n")
    (stage / "main.cc").write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
    shutil.copyfile(bench / "imu_heading.ino", bench / "sketch.cpp")
    common = [shutil.which("g++"), "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
              "-fno-exceptions", "-fno-rtti", "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS",
              "-DD111_TEST_SEPARATE_MAIN", "-DMOTORS_ALLOWED=0", "-DMATCH=0",
              "-I", source, "-I", bench / "src", "-I", stage, "-isystem", ROOT / "host/third_party",
              "-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free"]
    sources = [stage / "cases.cc", bench / "src/imu_heading_bench.cpp",
               source / "hal/imu_heading.cpp", source / "core/countdown.cpp",
               bench / "src/imu_heading_bench_native.cpp", bench / "sketch.cpp"]
    sanitizer = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-fno-omit-frame-pointer", "-no-pie"]
    for name, flags in (("startup_native_normal", []), ("startup_native_san", sanitizer)):
        case.execute(common, [*flags, "-DARDUINO_ARCH_ZEPHYR", "-DTEST_NATIVE_BINDING"], sources,
                     stage / name, "D111 default sketch*,D111 Native*")
