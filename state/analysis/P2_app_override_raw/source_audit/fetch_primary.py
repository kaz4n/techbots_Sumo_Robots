"""Retrieve only pinned official CLI sources for the D099-R1 source audit."""
from datetime import datetime, timezone
from hashlib import sha1, sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

PIN = "01f3d4f2ba7c2eaafb5dc710c8a1903af7762fea"
DEST = Path(__file__).resolve().parent
ROOT = DEST.parents[3]
TREE = json.loads((ROOT / "state/analysis/P2_bridge_dependency_raw/cli_tree_v1.5.1.json").read_text())
ENTRIES = {row["path"]: row for row in TREE["tree"] if row["type"] == "blob"}
FILES = [
    "docs/configuration.md",
    "internal/cli/arguments/show_properties.go",
    "internal/cli/cli.go",
    "internal/cli/configuration/configuration.go",
    "internal/cli/configuration/directories.go",
    "internal/cli/configuration/defaults.go",
    "internal/cli/configuration/configuration.schema.json",
    "internal/arduino/cores/packagemanager/loader.go",
    "internal/cli/instance/instance.go",
    "commands/service_init.go",
    "internal/arduino/cores/packagemanager/profiles.go",
    "internal/cli/config/dump.go",
]

receipt = {"timestamp": datetime.now(timezone.utc).isoformat(), "pin": PIN,
           "scope": "Version-pinned official source retrieval only; no board, compile, or MCU action", "files": []}
for rel in FILES:
    row = {"path": rel, "url": f"https://raw.githubusercontent.com/arduino/arduino-cli/{PIN}/{rel}"}
    try:
        expected = ENTRIES[rel]["sha"]
        with urlopen(Request(row["url"], headers={"User-Agent": "D099-R1-primary-source-audit"}), timeout=25) as response:
            data = response.read()
            row["status"] = response.status
        blob = sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        row.update(bytes=len(data), sha256=sha256(data).hexdigest(), git_blob=blob,
                   expected_git_blob=expected, tree_match=blob == expected)
        if blob != expected:
            raise ValueError("Pinned-tree blob identity mismatch")
        target = DEST / "primary" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    except Exception as error:
        row["error"] = str(error)
    receipt["files"].append(row)
    print(json.dumps(row), flush=True)
    (DEST / "retrieval_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
