"""Audit final reviewer subprocess receipts and bind the reviewed fixture bytes."""
from pathlib import Path
import collections
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
receipts = [json.loads(p.read_text()) for p in (OUT / "native_final").glob("*.json")]
assert len(receipts) == 104
statuses = collections.Counter(r["returncode"] for r in receipts)
assert statuses == {0: 102, 1: 2}
negative = [r for r in receipts if r["returncode"]]
assert all(any(a in ("--test-case=*assertion*", "--test-case=*signal*") for a in r["argv"]) for r in negative)
assert {r["production_sha256"] for r in receipts} == {"505e008ea99f6e739968572ae5674a858fc646a81001f6e6af01e3117c60543d"}
runs = [r for r in receipts if "g++" not in r["argv"][0] and r["returncode"] == 0]
cases = sum(int(re.search(r"test cases:\s*(\d+)", r["stdout"]).group(1)) for r in runs)
assertions = sum(int(re.search(r"assertions:\s*(\d+)", r["stdout"]).group(1)) for r in runs)
assert cases == 75 and assertions == 480
paths = [p for p in (ROOT / "tests/native_power").rglob("*") if p.is_file() and "receipts" not in p.parts]
paths += [ROOT / "tests/tooling/test_power_unoq.py", ROOT / "src/hal/power.cpp", ROOT / "src/hal/power.h", ROOT / "src/config.h"]
files = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
result = dict(scope="independent reviewer native rerun only", python_methods=9, duration_seconds=163.787,
    exit_code=0, positive_case_executions=cases, parent_status_assertions=assertions,
    child_assertion_total="not claimed", subprocess_receipts=len(receipts), subprocess_statuses=dict(statuses),
    expected_negative_commands=[r["argv"] for r in negative], reviewed_file_sha256=files)
(OUT / "final_receipt_summary.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k not in ("reviewed_file_sha256", "expected_negative_commands")}))
