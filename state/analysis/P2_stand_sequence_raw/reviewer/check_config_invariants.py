"""Isolated D119 reviewer checks; run only after the independent oracle freeze."""
from pathlib import Path
import hashlib
import json
import subprocess
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ORIGINALS = {
    name: (ROOT / name).read_bytes()
    for name in ("src/config.h", "src/core/stand_sequence.h", "src/core/stand_sequence.cpp")
}
STARTED = datetime.now(timezone.utc).isoformat()
CASES = [
    ("duration_zero", "0U", "0.25F", False, "must have a duration"),
    ("duration_first_outside_half_range", "89479U", "0.25F", False, "clock half range"),
    ("duration_uint32_max", "4294967295U", "0.25F", False, "clock half range"),
    ("duty_zero", "500U", "0.0F", False, "strictly between zero and one"),
    ("duty_negative", "500U", "-0.25F", False, "strictly between zero and one"),
    ("duty_one", "500U", "1.0F", False, "strictly between zero and one"),
    ("duty_above_one", "500U", "1.25F", False, "strictly between zero and one"),
    ("duty_nan", "500U", '__builtin_nanf("")', False, "strictly between zero and one"),
    ("duty_infinite", "500U", "__builtin_inff()", False, "strictly between zero and one"),
    ("minimum_duration", "1U", "0.25F", True, ""),
    ("maximum_duration", "89478U", "0.25F", True, ""),
    ("different_positive_duty", "500U", "0.125F", True, ""),
]
MAIN = r'''
#include "src/core/stand_sequence.h"
#include <cmath>
#include <cstdint>
using namespace stand_sequence;
int main() {
    constexpr std::uint32_t d = DURATION_LITERAL;
    constexpr float duty = DUTY_LITERAL;
    constexpr Phase phases[3] = {Phase::DRIVE, Phase::BRAKE, Phase::COAST};
    Sequence sequence;
    const std::uint32_t origin = 0xfff00000U;
    if (!sequence.start(origin)) return 1;
    auto entered = origin;
    for (unsigned row = 0; row < 12; ++row) {
        const auto report = sequence.report();
        const float signed_duty = (row == 0 || row == 6) ? duty : -duty;
        const float left = (row == 0 || row == 3) ? signed_duty : 0.0F;
        const float right = (row == 6 || row == 9) ? signed_duty : 0.0F;
        if (report.phase != phases[row % 3] || report.segment != row ||
            report.reason != Reason::NONE || report.duty_l != left ||
            report.duty_r != right || !std::isfinite(left) || !std::isfinite(right) ||
            !report.fresh || !report.phase_changed) return 2;
        const auto before = sequence.step(entered + d - 1U);
        if (before.segment != row || before.phase_changed || !before.fresh) return 3;
        entered += 2U * d - 2U;
        const auto after = sequence.step(entered);
        if (after.segment != row + 1U || !after.phase_changed || !after.fresh) return 4;
    }
    const auto complete = sequence.report();
    if (complete.phase != Phase::COMPLETE || complete.reason != Reason::NONE ||
        complete.duty_l != 0 || complete.duty_r != 0 ||
        static_cast<std::uint32_t>(entered - origin) != 12U * (2U * d - 2U)) return 5;
    if (sequence.start(0)) return 6;
    const auto passive = sequence.step(origin, true, true);
    if (passive.phase != Phase::COMPLETE || passive.reason != Reason::NONE ||
        passive.segment != 12 || passive.fresh || passive.phase_changed) return 7;
    Sequence gap;
    if (!gap.start(origin)) return 8;
    const auto failure = gap.step(origin + d);
    if (failure.phase != Phase::FAULT || failure.reason != Reason::CLOCK_GAP ||
        failure.duty_l != 0 || failure.duty_r != 0) return 9;
    return 0;
}
'''
records = []
for name, milliseconds, duty, valid, expected_diagnostic in CASES:
    directory = HERE / "fixtures" / name
    directory.mkdir(parents=True, exist_ok=False)
    for relative, data in ORIGINALS.items():
        target = directory / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative == "src/config.h":
            text = data.decode()
            assert text.count("STAND_SEGMENT_MS = 500U") == 1
            assert text.count("STAND_DUTY = 0.25F") == 1
            data = text.replace("STAND_SEGMENT_MS = 500U", "STAND_SEGMENT_MS = " + milliseconds).replace(
                "STAND_DUTY = 0.25F", "STAND_DUTY = " + duty).encode()
        target.write_bytes(data)
    command = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
               "-fno-exceptions", "-fno-rtti"]
    if valid:
        main = MAIN.replace("DURATION_LITERAL", str(int(milliseconds[:-1]) * 1000) + "U").replace("DUTY_LITERAL", duty)
        (directory / "main.cpp").write_text(main)
        command += ["src/core/stand_sequence.cpp", "main.cpp", "-o", "probe"]
    else:
        command += ["-c", "src/core/stand_sequence.cpp", "-o", "probe.o"]
    process = subprocess.run(command, cwd=directory, capture_output=True, text=True)
    (directory / "compile.stdout").write_text(process.stdout)
    (directory / "compile.stderr").write_text(process.stderr)
    record = {"case": name, "command": command, "compile_exit": process.returncode,
              "expected_valid": valid, "expected_diagnostic": expected_diagnostic}
    if valid and process.returncode == 0:
        run = subprocess.run([str(directory / "probe")], capture_output=True, text=True)
        record.update(run_exit=run.returncode, successful=run.returncode == 0)
    else:
        record["successful"] = not valid and process.returncode != 0 and expected_diagnostic in process.stderr
    records.append(record)
result = {
    "start_utc": STARTED, "end_utc": datetime.now(timezone.utc).isoformat(),
    "source_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in ORIGINALS.items()},
    "cases": records, "successful": all(record["successful"] for record in records),
    "scope": "Copied sources only; no public oracle, production, or locked-test edits; no board action."
}
(HERE / "config_invariants.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"cases": len(records), "successful": result["successful"]}))
raise SystemExit(0 if result["successful"] else 1)
