"""Read-only D120 final ELF, receipt, staged source and conditional footprint review."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COORD = HERE.parent / "coordinator"
spec = importlib.util.spec_from_file_location("reviewed_elf_parser", ROOT / "state/reviews/P2_bridge_dependency_review_raw/elf_review.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)
baseline = json.loads((ROOT / "state/analysis/P2_stand_sequence_raw/coordinator/app_build_receipt/verified.json").read_text())

def ending(mapping, suffix):
    values = [value for key, value in mapping.items() if key.endswith(suffix)]
    assert len(values) == 1
    return values[0]

records = {}
images = {}
for profile in ("app", "motor_direction"):
    folder = COORD / profile
    receipt = json.loads((folder / "receipt/verified.json").read_text())
    command = json.loads((folder / "receipt/compile.command.json").read_text())
    outer = json.loads((COORD / (profile + "_compile.json")).read_text())
    assert outer["returncode"] == 0 and outer["compile_only"] is True
    assert outer["argv"][-1] == "--compile-only"
    assert command[:3] == ["arduino-cli", "compile", "--json"]
    assert receipt["compiler_returncode"] == 0 and receipt["precompile_checks"] is True
    assert receipt["fqbn"] == "arduino:zephyr:unoq" and receipt["used_libraries"] == []
    flags = "-DMATCH=0 -DMOTORS_ALLOWED=0" + (" -DSUMOX_B4_STAND=1" if profile != "app" else "")
    for language in ("c", "cpp"):
        assert "compiler." + language + ".extra_flags=" + flags in command
    manifest = json.loads((folder / "source_manifest.json").read_text())
    stage = ROOT / "build/stage" / profile
    items = sorted(path for path in stage.rglob("*") if path.is_file())
    assert {path.relative_to(stage).as_posix() for path in items} == set(manifest["files"])
    digest = hashlib.sha256()
    for path in items:
        relative = path.relative_to(stage)
        data = path.read_bytes()
        current = ROOT / relative if relative.parts[0] == "src" else ROOT / ("src/app" if profile == "app" else "bench/motor_direction") / relative
        assert data == current.read_bytes()
        assert hashlib.sha256(data).hexdigest() == manifest["files"][relative.as_posix()]
        digest.update(relative.as_posix().encode() + b"\0")
        digest.update(data)
    assert digest.hexdigest() == manifest["source_sha256"] == receipt["source_sha256"]
    image = model.Elf(folder / (profile + ".ino.elf"))
    images[profile] = image
    account = image.account()
    assert account["sha256"] == ending(receipt["file_sha256"], "/build/" + profile + ".ino.elf")
    assert ending(receipt["file_sha256"], "/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf") == ending(baseline["file_sha256"], "/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf")
    assert account["conditional_pristine_peak_consumption"] <= 262144
    record = {key: account[key] for key in ("sha256", "bytes", "compiler_payload", "metadata_chunks",
               "conditional_pristine_peak_consumption", "conditional_pristine_peak_free_span",
               "conditional_largest_payload", "limitation")}
    record.update(source_sha256=digest.hexdigest(), matching_current_source_files=len(items),
                  flags=flags, receipt_id=Path(receipt["build_path"]).parent.name,
                  undefined=account["undefined"])
    if profile == "app":
        for suffix in ("/build/app.ino.elf", "/artifacts/app.ino.elf-zsk.bin"):
            assert ending(receipt["file_sha256"], suffix) == ending(baseline["file_sha256"], suffix)
        record["D119_loadable_ELF_ZSK_loader_unchanged"] = True
    records[profile] = record

bench = images["motor_direction"]
names = {symbol["name"] for symbol in bench.symbols}
records["motor_direction"]["stand_symbols"] = sorted(name for name in names if "routeStand" in name or "stand_sequence" in name)
assert records["motor_direction"]["stand_symbols"]
assert not any("routeNormal" in name or "checkStall" in name for name in names)
hooks = [symbol for symbol in bench.symbols if symbol["name"] == "_Z10__loopHookv"]
assert len(hooks) == 1 and hooks[0]["bind"] == 1
assert set(records["motor_direction"]["undefined"]) <= set(records["app"]["undefined"])
records["motor_direction"].update(ordinary_routing_symbols_absent=True, strong_loop_hook_count=1,
                                 imports_subset_of_unchanged_default=True)
result = {"reviewed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "successful": True, "targets": records,
          "scope": "Local final-ELF and checked-receipt review only; pristine-heap footprint model, not loaded RAM, stack, WCET, physical or powered evidence."}
(HERE / "target_evidence.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"successful": True, "targets": {name: {key: record[key] for key in
    ("source_sha256", "sha256", "matching_current_source_files", "conditional_pristine_peak_consumption", "conditional_pristine_peak_free_span")}
    for name, record in records.items()}}))
