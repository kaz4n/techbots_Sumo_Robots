"""Private header/profile refusal checks after the independent D120 oracle freeze."""
from pathlib import Path
import hashlib
import json
import subprocess
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = r'''
#include "core/fsm.h"
#include "app/runtime.h"
#include <type_traits>
#include <utility>
template<class T, class = void> struct HasStand : std::false_type {};
template<class T> struct HasStand<T, std::void_t<decltype(std::declval<T>().stand)>> : std::true_type {};
static_assert(fsm::RobotResult::STAND_PROFILE == (SUMOX_B4_STAND != 0));
static_assert(HasStand<fsm::RobotResult>::value == (SUMOX_B4_STAND != 0));
static_assert(static_cast<unsigned>(governor::Profile::SEARCH_FORWARD) == 0);
static_assert(static_cast<unsigned>(governor::Profile::PIVOT) == 1);
static_assert(static_cast<unsigned>(governor::Profile::OPENER) == 2);
static_assert(static_cast<unsigned>(governor::Profile::ATTACK) == 3);
static_assert(static_cast<unsigned>(governor::Profile::EDGE_REVERSE) == 4);
static_assert(static_cast<unsigned>(governor::Profile::REFLANK_BACK) == 5);
static_assert(static_cast<unsigned>(governor::Profile::REFLANK_TURN) == 6);
static_assert(static_cast<unsigned>(governor::Profile::EDGE_FORWARD) == 7);
#if SUMOX_B4_STAND == 1
static_assert(static_cast<unsigned>(governor::Profile::STAND) == 8);
static_assert(std::is_same_v<decltype(fsm::RobotResult{}.stand_stopping), bool>);
#endif
int main() { return 0; }
'''
CASES = [
    ("default", [], True, ""),
    ("explicit_default", ["-DSUMOX_B4_STAND=0"], True, ""),
    ("match_default", ["-DMATCH=1", "-DMOTORS_ALLOWED=1"], True, ""),
    ("stand_m0", ["-DSUMOX_B4_STAND=1", "-DMOTORS_ALLOWED=0"], True, ""),
    ("stand_m1_host", ["-DSUMOX_B4_STAND=1", "-DMOTORS_ALLOWED=1"], True, ""),
    ("invalid_negative", ["-DSUMOX_B4_STAND=-1"], False, "SUMOX_B4_STAND must be 0 or 1"),
    ("invalid_two", ["-DSUMOX_B4_STAND=2"], False, "SUMOX_B4_STAND must be 0 or 1"),
    ("stand_match_m0", ["-DSUMOX_B4_STAND=1", "-DMATCH=1", "-DMOTORS_ALLOWED=0"], False, "not a MATCH build"),
    ("stand_match_m1", ["-DSUMOX_B4_STAND=1", "-DMATCH=1", "-DMOTORS_ALLOWED=1"], False, "not a MATCH build"),
]
started = datetime.now(timezone.utc).isoformat()
(HERE / "profile_header_probe.cpp").write_text(SOURCE)
records = []
for name, flags, valid, diagnostic in CASES:
    command = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
               "-fno-exceptions", "-fno-rtti", "-fsyntax-only", "-I", str(ROOT / "src"),
               *flags, str(HERE / "profile_header_probe.cpp")]
    result = subprocess.run(command, capture_output=True, text=True)
    (HERE / (name + ".stderr.txt")).write_text(result.stderr)
    success = result.returncode == 0 if valid else result.returncode != 0 and diagnostic in result.stderr
    records.append({"name": name, "command": command, "returncode": result.returncode,
                    "expected_valid": valid, "expected_diagnostic": diagnostic, "successful": success})
report = {"start_utc": started, "end_utc": datetime.now(timezone.utc).isoformat(),
          "source_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                            for name in ("src/config.h", "src/core/fsm.h", "src/core/governor.h", "src/app/runtime.h")},
          "cases": records, "successful": all(item["successful"] for item in records),
          "scope": "Header compilation only; no public-test/source changes, board action, or powered execution."}
(HERE / "profile_compilation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"cases": len(records), "successful": report["successful"]}))
raise SystemExit(0 if report["successful"] else 1)
