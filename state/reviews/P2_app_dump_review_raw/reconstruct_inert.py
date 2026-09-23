"""Read-only staged-byte reconstruction for the seven existing inert allowlist keys."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
BASE = "f5f8f34"
EXPECTED = {"bench/p0_adc", "bench/p0_gpio", "bench/p0_matrix", "bench/p0_qtr",
            "bench/p0_timing", "bench/recorder_inert", "bench/ui_matrix"}
manifest = json.loads((ROOT / "tools/p0_inert_sources.json").read_text())
assert set(manifest) == EXPECTED
baseline_names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASE], cwd=ROOT).decode().splitlines()

def eligible_shared(name):
    p = Path(name)
    return name == "src/config.h" or name.startswith(("src/core/", "src/hal/")) or (
        name.startswith("src/app/") and not name.startswith("src/app/src/") and
        p.suffix in (".h", ".hpp", ".c", ".cc", ".cpp"))

def checksum(entries):
    total = hashlib.sha256()
    for name, data in sorted(entries.items()):
        total.update(name.encode() + b"\0"); total.update(data)
    return total.hexdigest()

baseline_shared = {name: subprocess.check_output(["git", "show", f"{BASE}:{name}"], cwd=ROOT)
                   for name in baseline_names if eligible_shared(name)}
current_shared = {p.relative_to(ROOT).as_posix(): p.read_bytes() for p in (ROOT / "src").rglob("*")
                  if p.is_file() and eligible_shared(p.relative_to(ROOT).as_posix())}
records = {}
for key in sorted(EXPECTED):
    baseline = dict(baseline_shared)
    baseline.update({name[len(key)+1:]: subprocess.check_output(["git", "show", f"{BASE}:{name}"], cwd=ROOT)
                     for name in baseline_names if name.startswith(key + "/") and Path(name).name != ".gitkeep"})
    current = dict(current_shared)
    for p in (ROOT / key).rglob("*"):
        if p.is_file() and p.name != ".gitkeep":
            assert not p.is_symlink()
            current[p.relative_to(ROOT / key).as_posix()] = p.read_bytes()
    assert not any(name.endswith("app.ino") for name in current)
    assert checksum(baseline) == manifest[key], (key, checksum(baseline), manifest[key])
    changes = {name: {"before": hashlib.sha256(baseline[name]).hexdigest() if name in baseline else None,
                      "after": hashlib.sha256(current[name]).hexdigest() if name in current else None}
               for name in sorted(set(baseline) | set(current)) if baseline.get(name) != current.get(name)}
    records[key] = dict(source_sha256=checksum(current), files=len(current), manifest_at_review=manifest[key],
                        changed_files=changes, file_sha256={n: hashlib.sha256(d).hexdigest() for n,d in sorted(current.items())})
result = dict(scope="Read-only independent source reconstruction; no staging, transport, key refresh or upload",
              baseline=BASE, baseline_all_seven_exact=True, entries=records)
label = sys.argv[1] if len(sys.argv) == 2 else "initial"
assert label.isidentifier()
target = RAW / ("inert_source_reconstruction.json" if label == "initial" else
                "inert_source_reconstruction_" + label + ".json")
assert not target.exists(), "Preserve prior receipt"
target.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({key: {"files": value["files"], "changed": list(value["changed_files"]),
                        "source_sha256": value["source_sha256"]} for key, value in records.items()}, indent=2))
