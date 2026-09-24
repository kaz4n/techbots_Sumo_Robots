"""Read-only final oracle/source and archived sanitizer evidence checks."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "state/analysis/P2_stand_integration_raw"

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

checks = {"checked_utc": datetime.now(timezone.utc).isoformat()}
oracle = read_json(RAW / "oracle/oracle_freeze.json")
for item in oracle["files"]:
    assert digest(ROOT / item["path"]) == item["sha256"], item["path"]
checks["frozen_public_files_current"] = len(oracle["files"])
checks["runs"] = {}
for name in ("normal", "sanitize", "sanitizer_archive"):
    run = read_json(RAW / f"coordinator/{name}.json")
    assert run["returncode"] == 0, name
    assert run["before_sha256"] == run["after_sha256"], name
    for path, expected in run["after_sha256"].items():
        assert digest(ROOT / path) == expected, (name, path)
    checks["runs"][name] = {"returncode": 0, "before_after_current_files_identical": len(run["after_sha256"])}

targets = ("sumox26_tests", "motor_gate_enabled_tests", "stand_integration_m0_tests", "stand_integration_m1_tests")
for target in targets:
    directory = RAW / "coordinator/sanitize_build"
    flags = (directory / f"{target}.dir.flags.make").read_text()
    link = (directory / f"{target}.dir.link.txt").read_text()
    assert "-fsanitize=address,undefined" in flags and "-fsanitize=address,undefined" in link, target
    assert "-fno-omit-frame-pointer" in flags, target
checks["sanitizer_instrumented_and_linked_targets"] = list(targets)
last = (RAW / "coordinator/sanitize_build/LastTest.log").read_text()
case_rows = re.findall(r"test cases:\s+(\d+) \|\s+(\d+) passed \| 0 failed \| 0 skipped", last)
assert case_rows == [("1496", "1496"), ("187", "187"), ("18", "18"), ("18", "18")]
assert last.count("Test Passed.") == 4
checks["sanitizer_cases"] = dict(zip(targets, [int(row[0]) for row in case_rows]))
established_locked = subprocess.run(["git", "diff", "--name-only", "1c387810", "--", "tests/locked"], cwd=ROOT, capture_output=True, text=True, check=True)
assert not established_locked.stdout.strip(), established_locked.stdout
checks["established_locked_tests_unchanged_from_D119"] = True
checks["new_locked_oracle_frozen_hash"] = digest(ROOT / "tests/locked/test_stand_integration_safety.cc")
checks["successful"] = True
checks["scope"] = "Read-only archived evidence/hash verification; no tests rerun or source modifications."
(RAW / "reviewer/final_evidence.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
print(json.dumps(checks, indent=2))
