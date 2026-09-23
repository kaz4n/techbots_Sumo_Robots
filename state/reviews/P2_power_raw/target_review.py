"""Bind final offline ELF evidence to the current staged source and inspect it."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
receipt = ROOT / "state/analysis/P2_power_raw/target_a936d10d_bench-default.json"
data = json.loads(receipt.read_text())
stage = ROOT / "build/stage/p2_power_compile"
files = {p.relative_to(stage).as_posix(): p.read_bytes() for p in stage.rglob("*") if p.is_file()}
hashes = {name: hashlib.sha256(raw).hexdigest() for name, raw in files.items()}
digest = hashlib.sha256()
for name, raw in sorted(files.items()):
    digest.update(name.encode() + b"\0")
    digest.update(raw)
assert hashes == data["source_files"]
assert digest.hexdigest() == data["source_sha256"]
record = data["records"][0]
text = record["disassembly"]
parts = [p for p in re.split(r"(?=^\S+ <)", text, flags=re.M) if p.strip()]
functions = {p.splitlines()[0]: p for p in parts}
startup = {name: body for name, body in functions.items() if any(x in name for x in (
    "<setup>", "<loop>", "_GLOBAL__sub_I__ZN11power_probe6readerE", "_GLOBAL__sub_I__ZNK5power6Reader13controlsOwnedEv"))}
assert len(startup) == 4
assert all(not re.search(r"\sblx?\s", body) for body in startup.values())
mmio = ["42028000", "42020000", "46020c00", "46020800", "46000400", "46021000", "46021800", "e000e100"]
assert all(x in text for x in mmio)
assert "#776" in text and "#65536" in text and "#4096" in text
assert text.count("dmb\tsy") == 2
assert all(any("power::Reader::" + method in name for name in functions) for method in (
    "begin()", "read()", "initialize()", "waitFlag", "waitCalibrationGap()", "finishSample", "stopOwned()"))
assert data["returncode"] == 0 and data["native_exports"]["returncode"] == 0
assert len(data["native_names"]) == len(re.findall(r"^\$\d+ = 0x", data["native_exports"]["stdout"], re.M)) == 36
assert all(v["returncode"] == 0 for r in data["records"] for v in r.values() if isinstance(v, dict) and "returncode" in v)
relocs = record["relocations"]["stdout"]
interesting = [line for line in relocs.splitlines() if re.match(
    r"(000024ac|000024b0|000024b4|00003040|00003044|00003048|000030b4|000030b8|000030bc)\s", line)]
result = dict(kind="offline-evidence-review-not-runtime", source_sha256=data["source_sha256"],
    matched_source_files=len(files), raw_receipt_sha256=hashlib.sha256(receipt.read_bytes()).hexdigest(),
    all_collection_commands_zero=True, native_export_bindings=36,
    elf=[{k:r[k] for k in ("path", "bytes", "sha256")} for r in data["records"]],
    mmio_literals=mmio, source_startup_functions=startup, selected_relocations=interesting,
    observations=["setup only stores exercise address; loop returns", "new power/probe constructor wrappers only initialize inherited RouterBridge::HCI memory; no call instruction",
    "exercise retains begin/read through function relocations", "ADC1 + 0x308 common CCR offset and 65536/4096 finite count literals retained",
    "two calibration DMB instructions retained", "inherited Bridge constructor and __loopHook remain separate runtime limitations",
    "this does not prove deployed-loader identity, electrical accuracy or timing"])
(OUT / "target_review.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k:result[k] for k in ("source_sha256", "matched_source_files", "all_collection_commands_zero", "native_export_bindings")}))
