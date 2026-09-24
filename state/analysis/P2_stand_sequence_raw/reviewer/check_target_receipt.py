"""Read-only local review of D119 compile-only receipt and staged-source identity."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COORD = HERE.parent / "coordinator"
archive = json.loads((COORD / "app_build_archive.json").read_text())
receipt = json.loads((COORD / "app_build_receipt/verified.json").read_text())
prior = json.loads((ROOT / "build/app-receipts/10f172276dcb46edab7c991b8cf03e3f/verified.json").read_text())
compile_only = json.loads((COORD / "app_compile.json").read_text())
assert compile_only["returncode"] == 0 and compile_only["compile_only"] is True
assert compile_only["argv"][-1] == "--compile-only"
assert archive["receipt"] == "e72172eec9c649e7b785c42d7c570ad9"
assert receipt["compiler_returncode"] == 0 and receipt["precompile_checks"] is True
assert receipt["fqbn"] == "arduino:zephyr:unoq"
for entry in archive["files"]:
    data = (COORD / "app_build_receipt" / entry["name"]).read_bytes()
    assert len(data) == entry["bytes"]
    assert hashlib.sha256(data).hexdigest() == entry["sha256"]
stage = ROOT / "build/stage/app"
digest = hashlib.sha256()
stage_files = sorted(item for item in stage.rglob("*") if item.is_file())
for item in stage_files:
    relative = item.relative_to(stage)
    data = item.read_bytes()
    digest.update(relative.as_posix().encode() + b"\0")
    digest.update(data)
    current = ROOT / relative if relative.parts[0] == "src" else ROOT / "src/app" / relative
    assert data == current.read_bytes(), str(relative)
assert digest.hexdigest() == receipt["source_sha256"] == archive["source_sha256"]
compared = {}
for suffix in ("/build/app.ino.elf", "/artifacts/app.ino.elf-zsk.bin",
               "/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf"):
    before = [value for name, value in prior["file_sha256"].items() if name.endswith(suffix)]
    after = [value for name, value in receipt["file_sha256"].items() if name.endswith(suffix)]
    assert len(before) == len(after) == 1 and before[0] == after[0]
    assert archive["comparison_to_D118"][suffix] == {
        "before": before[0], "after": after[0], "identical": True}
    compared[suffix] = after[0]
obj = json.loads((COORD / "target_object.stdout.json").read_text())
obj_command = json.loads((COORD / "target_object.command.json").read_text())
assert obj_command["returncode"] == 0
assert obj["object_bytes"] == 13244 and obj["object_path"].startswith(receipt["build_path"] + "/")
assert obj["compile_command"]["file"].endswith("/src/core/stand_sequence.cpp")
assert "-DMATCH=0" in obj["compile_command"]["arguments"]
assert "-DMOTORS_ALLOWED=0" in obj["compile_command"]["arguments"]
result = {
    "reviewed_utc": datetime.now(timezone.utc).isoformat(), "successful": True,
    "receipt": archive["receipt"], "archived_files_rehashed": len(archive["files"]),
    "stage_files_matching_current_source": len(stage_files), "stage_sha256": digest.hexdigest(),
    "identical_loadables_and_loader_to_D118": compared,
    "sequence_object_bytes": obj["object_bytes"], "sequence_object_sha256": obj["object_sha256"],
    "scope": "Local receipt/stage review only; compiler/loadable hashes support unchanged current app footprint, not integration or WCET. No board action by reviewer."
}
(HERE / "target_receipt_review.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
