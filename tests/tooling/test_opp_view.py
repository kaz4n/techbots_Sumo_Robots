"""Run independent D107 cases against opaque isolated implementation copies.

Contract/header-derived expectations are frozen before execution. Native tests
substitute existing public owners, not their algorithms or the new binding.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "state/analysis/P2_opp_view_raw/author"
CASES = ROOT / "tests/tooling/opp_view_cases.cc"


def receipt(kind, record):
    RAW.mkdir(parents=True, exist_ok=True)
    record["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (RAW / f"{kind}_{time.time_ns()}.json").open("x", encoding="utf-8") as output:
        json.dump(record, output, indent=2); output.write("\n")


class OppViewTests(unittest.TestCase):
    def command(self, argv, refuse=False):
        argv = list(map(str, argv))
        try:
            result = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, timeout=240)
        except (OSError, subprocess.TimeoutExpired) as error:
            receipt("command", {"argv": argv, "exception": repr(error)})
            raise
        receipt("command", {"argv": argv, "returncode": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr})
        if refuse:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("static assertion failed", result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def execute(self, common, flags, sources, binary, selection=None):
        main = binary.parent / ("doctest-san.o" if "-fsanitize=address,undefined" in flags else "doctest-normal.o")
        if not main.exists():
            self.command([*common, *flags, "-c", binary.parent / "main.cc", "-o", main])
        self.command([*common, *flags, *sources, main, "-o", binary])
        args = [binary, "--no-colors"]
        if selection: args.append("--test-case=" + selection)
        result = self.command(args)
        self.assertIn("Status: SUCCESS!", result.stdout)
        print(binary.name + ": " + " | ".join(line for line in result.stdout.splitlines()
              if "test cases:" in line or "assertions:" in line), flush=True)

    def test_frozen_runner_profiles_native_binding_and_disabled_sketch(self):
        receipt("test_freeze", {"implementation_body_read": False, "sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (CASES, Path(__file__), ROOT / "state/analysis/P2_opp_view_contract.md",
                         ROOT / "bench/opp_view/src/opp_view.h",
                         ROOT / "bench/opp_view/src/opp_view_native.h")}})
        if os.name == "nt":
            self.command(["wsl.exe", "--exec", "python3", "-m", "unittest",
                          "tests.tooling.test_opp_view", "-v"])
            return
        compiler = shutil.which("g++"); self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory(prefix="sumo-d107-author-", dir="/dev/shm") as temporary:
            stage = Path(temporary); source = stage / "src"; bench = stage / "bench"
            shutil.copytree(ROOT / "src", source)
            shutil.copytree(ROOT / "bench/opp_view", bench)
            shutil.copyfile(CASES, stage / "cases.cc")
            receipt("opaque_source_copy", {"sha256": {
                str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest()
                for folder in (source, bench) for path in sorted(folder.rglob("*")) if path.is_file()}})
            (stage / "Arduino.h").write_text("#pragma once\nunsigned long micros();\n")
            (stage / "main.cc").write_text('#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN\n#include "doctest.h"\n')
            shutil.copyfile(bench / "opp_view.ino", bench / "sketch.cpp")
            common = [compiler, "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                      "-fno-exceptions", "-fno-rtti", "-DDOCTEST_CONFIG_NO_EXCEPTIONS_BUT_WITH_ALL_ASSERTS",
                      "-DD107_TEST_SEPARATE_MAIN",
                      "-DMOTORS_ALLOWED=0", "-DMATCH=0", "-I", source, "-I", bench / "src", "-I", stage,
                      "-isystem", ROOT / "host/third_party",
                      "-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free"]
            sources = [stage / "cases.cc", bench / "src/opp_view.cpp"]
            sanitizer = ["-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                         "-fno-omit-frame-pointer", "-no-pie"]
            for label, flags in (("normal", []), ("asan_ubsan", sanitizer)):
                with self.subTest(profile=label):
                    self.execute(common, flags, sources, stage / label)
            for label, flags in (("native_normal", []), ("native_san", sanitizer)):
                with self.subTest(profile=label):
                    self.execute(common, [*flags, "-DARDUINO_ARCH_ZEPHYR", "-DTEST_NATIVE_BINDING"],
                                 [*sources, bench / "src/opp_view_native.cpp", bench / "sketch.cpp"],
                                 stage / label, "D107 Native*,D107 default sketch*")
            config = source / "config.h"; original = config.read_text(encoding="utf-8")
            invalid = [("TICK_US", "0U"), ("TICK_US", "0x80000000U"),
                       ("UI_FRAME_PERIOD_US", "0U"), ("UI_FRAME_PERIOD_US", "0x80000000U"),
                       ("OPP_ACTIVE_LOW_MASK", "0x80U"), ("OPP_ACTIVE_LOW_MASK", "0xffffffffU")]
            profiles = [(name, value, True) for name, value in invalid]
            profiles += [("OPP_ACTIVE_LOW_MASK", "0U", False), ("OPP_ACTIVE_LOW_MASK", "0x7fU", False)]
            for index, (name, value, bad) in enumerate(profiles):
                with self.subTest(config=name, value=value):
                    changed, count = re.subn(r"(\b" + name + r"\s*=\s*)[^;]+;", r"\g<1>" + value + ";", original)
                    self.assertEqual(count, 1); config.write_text(changed, encoding="utf-8")
                    receipt("config_profile", {"name": name, "value": value, "bad": bad,
                                              "sha256": hashlib.sha256(config.read_bytes()).hexdigest()})
                    self.execute(common, [*sanitizer, *(["-DTEST_BAD_CONFIG"] if bad else [])],
                                 sources, stage / f"config-{index}", None if bad else "D107 all 128*")
            config.write_text(original, encoding="utf-8")
            for allowed, match in ((1, 0), (0, 1), (1, 1)):
                with self.subTest(refused_motor=allowed, refused_match=match):
                    flags = [part for part in common if part not in ("-DMOTORS_ALLOWED=0", "-DMATCH=0")]
                    self.command([*flags, f"-DMOTORS_ALLOWED={allowed}", f"-DMATCH={match}",
                                  "-DARDUINO_ARCH_ZEPHYR", "-fsyntax-only", bench / "sketch.cpp"], refuse=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
