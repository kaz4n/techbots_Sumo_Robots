"""Read-only reviewer check of frozen final D101 sources and downloaded target ELF."""
from pathlib import Path
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[3]
RAW = Path(__file__).resolve().parent
source = json.loads((RAW / "app_source_reconstruction_final.json").read_text())
folder = ROOT / "state/analysis/P2_app_dump_raw/target_83600858_match-immediate"
audit = json.loads((folder / "audit.json").read_text())
assert source["file_sha256"] == audit["source_files"]
assert source["source_sha256"] == audit["source_sha256"]
decoder = ROOT / "state/reviews/P2_bridge_dependency_review_raw/elf_review.py"
spec = importlib.util.spec_from_file_location("review_elf", decoder)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
verified = []
for row in audit["records"]:
    path = folder / Path(row["path"]).name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
    elf = module.Elf(path)
    verified.append(dict(path=path.name, sha256=row["sha256"],
                         imports=len({s["name"] for s in elf.symbols if not s["section_index"] and s["name"]})))
elf = module.Elf(folder / "app.ino.elf")
account = elf.account()
assert account["compiler_payload"] == 257784
assert account["conditional_pristine_peak_consumption"] == 262400
assert len(account["init"]) == 1 and not account["fini"]
assert account["init"][0]["name"] == "_GLOBAL__sub_I_setup"
assert elf.functions()["_Z10__loopHookv"] == bytes.fromhex("7047")
assert next(s for s in elf.symbols if s["name"] == "_Z10__loopHookv")["bind"] == 1
assert next(s for s in elf.sections if s["name"] == ".static_thread_data_area")["size"] == 0

def refs(name):
    symbol = next(s for s in elf.symbols if s["name"] == name and s["size"])
    section = elf.sections[symbol["section_index"]]
    offset = (symbol["value"] & ~1) - section["address"]
    return [r["name"] for r in elf.relocations if r["section"] == section["name"]
            and offset <= r["offset"] < offset + symbol["size"]]

factory = "_ZN3app12unoQDumpPortERN8recorder4dump12UnoQDumpPortE"
expected = {"_ZN3app12_GLOBAL__N_15beginEPvRKN8recorder4dump10SetupGrantE",
            "_ZN3app12_GLOBAL__N_15readyEPv", "_ZN8recorder4dump12UnoQDumpPort4portEv"}
assert set(refs(factory)) == expected
startup_refs = refs("_GLOBAL__sub_I_setup")
assert factory in startup_refs
assert not any("DumpPort5begin" in name or "DumpPort5ready" in name or "DumpPort7advance" in name
               for name in startup_refs)
assert "_Z10__loopHookv" in refs("main")
assert set(refs("setup")) >= {"_ZN3app7Runtime5beginERKNS_11SetupGrantsE"}
assert "_ZN3app7Runtime4stepEv" in refs("loop")
owners = {name: next(s["size"] for s in elf.symbols if s["name"] == name and s["size"])
          for name in ("_ZN12_GLOBAL__N_17runtimeE", "_ZN12_GLOBAL__N_19dump_portE",
                       "_ZN12_GLOBAL__N_17sourcesE")}
result = dict(scope="Independent reviewer offline source/ELF/relocation verification; no target connection",
              source_sha256=source["source_sha256"], exact_source_files=85, elfs=verified,
              owners=owners, factory_refs=refs(factory), static_initializer_refs=startup_refs,
              compiler_payload=account["compiler_payload"],
              conditional_pristine_peak=account["conditional_pristine_peak_consumption"],
              conditional_pool_excess=account["conditional_pristine_peak_consumption"]-262144,
              verdict="TARGET_BLOCKED",
              limit="Pinned pristine allocator/flash-peek model, not measured load/freeRAM/stack/WCET")
target = RAW / "final_target_verification.json"
assert not target.exists()
target.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
