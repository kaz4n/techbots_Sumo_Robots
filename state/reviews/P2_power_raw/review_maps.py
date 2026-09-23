"""Read-only independent reproduction of the five existing staged inert hashes."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SKETCHES = ("bench/p0_matrix", "bench/p0_timing", "bench/p0_adc", "bench/p0_gpio", "bench/p0_qtr")
result = {"kind": "read-only-independent-source-map", "baseline": "fbd9d96", "sketches": {}}
for sketch in SKETCHES:
    folder = ROOT / sketch
    files = {}
    for path in folder.rglob("*"):
        if path.is_file() and not (path.parent == folder and path.name == ".gitkeep"):
            files[path.relative_to(folder).as_posix()] = path.read_bytes()
    files["src/config.h"] = (ROOT / "src/config.h").read_bytes()
    for module in ("core", "hal"):
        for path in (ROOT / "src" / module).rglob("*"):
            if path.is_file():
                files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    digest = hashlib.sha256()
    for name, raw in sorted(files.items()):
        digest.update(name.encode() + b"\0")
        digest.update(raw)
    result["sketches"][sketch] = {"hash": digest.hexdigest(), "files": {
        name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(files.items())}}
result["protected_diff"] = subprocess.check_output([
    "git", "diff", "fbd9d96", "--", "src/core", "src/app", "tests/locked", "src/config.h", "tools/board_tool.py"
], cwd=ROOT).decode()
manifest = json.loads((ROOT / "tools/p0_inert_sources.json").read_text())
result["manifest_has_exact_original_five"] = set(manifest) == set(SKETCHES)
result["manifest_matches_current_source"] = all(manifest[k] == v["hash"] for k, v in result["sketches"].items())
(OUT / "inert_maps.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"maps": {k: v["hash"] for k, v in result["sketches"].items()},
    "protected_unchanged": result["protected_diff"] == "", "manifest_has_exact_original_five": result["manifest_has_exact_original_five"],
    "manifest_matches_current_source": result["manifest_matches_current_source"]}, indent=2))
