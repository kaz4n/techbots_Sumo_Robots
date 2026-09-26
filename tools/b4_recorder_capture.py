# Captures the fixed B4 recorder through the accepted passive MEM-AP lifecycle.
# Preserves bounded raw evidence without loading firmware or claiming atomicity.
# Focused fixtures exercise fixed hooks; descriptor and child guards are inherited.
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

SOURCE = "9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a"
RUN_ID = "b4-recorder-9044ebbb-capture01"
_BINDINGS = {
    "boot_id": "55c386b9-fe6d-4388-a7f4-1d91e0bb49d8",
    "files": {
        "config": {
            "bytes": 694,
            "path": "/home/arduino/sumox26-capture-tools/app-default-beeffff315b2e28a95a20dc1e26477fc924b2da26d1fdd8a8b36fb013ca110e1/p0_mem_read.cfg",
            "sha256": "89d16a28a1489c23ec743be55ade39824f9ca5213b02b20ef4785079122e4339"
        },
        "loader": {
            "bytes": 2303728,
            "path": "/home/arduino/.arduino15/packages/arduino/hardware/zephyr/1.0.0/firmwares/zephyr-arduino_uno_q_stm32u585xx.elf",
            "sha256": "39d4a4fd47241663323f6e04f94dd8f5a9f9ad6582cf1df37f9709b74026adcd"
        },
        "openocd": {
            "bytes": 14435552,
            "path": "/opt/openocd/bin/openocd",
            "sha256": "04778a80c5c619ee4eef7505db91328f1d7e789107c496f2ddcf96d081f5b0ff"
        },
        "sketch": {
            "bytes": 82912,
            "path": "/home/arduino/sumox26_codex_build/b4-app-m0-static01/build/app.ino.bin-zsk.bin",
            "sha256": "84667b0a22ff7701059a266b6c82bb61de1f7ccec96280e4f13b5692bf785a28"
        },
        "swj": {
            "bytes": 1148,
            "path": "/opt/openocd/share/openocd/scripts/target/swj-dp.tcl",
            "sha256": "aad132008735bbafea3d18a304632c638f0fb99bfc19530c9f577eda2b10410a"
        }
    },
    "loader_image": {
        "bytes": 263680,
        "sha256": "e9322826c422fb234ac8c2e79ea38a050d0dd8dc32b2a89f6930e0a0ff7ebab2"
    },
    "output": "/home/arduino/sumox26_codex_build/b4-recorder-9044ebbb-capture01",
    "run_id": "b4-recorder-9044ebbb-capture01",
    "schema": "fixed-b4-recorder-capture-v1",
    "source_sha256": "9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a",
    "uid": 1000
}
DEPENDENCIES = {
    "capture": [
        37525,
        "95b0344d01886b6db30d55aa18a536f9a481b82348e22643e7920d817dbfac3e"
    ],
    "helper": [
        33321,
        "8ba9b190c38e728013a383348c60c287b0366607f65f703161cf7f2e142d36f8"
    ],
    "p0": [
        18880,
        "885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c"
    ]
}
_READ_PLAN = (("before.loader.0", 134217728, 65536),
              ("before.loader.1", 134283264, 65536),
              ("before.loader.2", 134348800, 65536),
              ("before.loader.3", 134414336, 65536),
              ("before.loader.4", 134479872, 1536),
              ("before.sketch.0", 135266304, 65536),
              ("before.sketch.1", 135331840, 17376),
              ("before.lifecycle", 537113200, 120),
              ("owner.0", 536954120, 16384),
              ("owner.1", 536970504, 16384),
              ("owner.2", 536986888, 16384),
              ("owner.3", 537003272, 16384),
              ("owner.4", 537019656, 16384),
              ("owner.5", 537036040, 16384),
              ("owner.6", 537052424, 16384),
              ("owner.7", 537068808, 16384),
              ("owner.8", 537085192, 16384),
              ("owner.9", 537101576, 11744),
              ("after.lifecycle", 537113200, 120),
              ("after.sketch.0", 135266304, 65536),
              ("after.sketch.1", 135331840, 17376),
              ("after.loader.0", 134217728, 65536),
              ("after.loader.1", 134283264, 65536),
              ("after.loader.2", 134348800, 65536),
              ("after.loader.3", 134414336, 65536),
              ("after.loader.4", 134479872, 1536),)
COUNTS = {"commands": 26, "reads": 26, "requested_bytes": 852624}
OWNER_ADDRESS, OWNER_BYTES, BRACKET_OFFSET = 536954120, 159200, 159080
FLASH_KEYS = ("before_loader", "before_sketch", "after_loader", "after_sketch")
LIFECYCLE_FIELDS = ("epoch_token", "last_frame_token", "phase")


def _require(value, message):
    if not value:
        raise ValueError(message)


def _same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return (all(type(key) is str for key in left) and left.keys() == right.keys()
                and all(_same(left[key], right[key]) for key in right))
    if type(left) in (list, tuple):
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right))
    return left == right


def fixed_bindings():
    return json.loads(json.dumps(_BINDINGS))


def read_plan():
    return _READ_PLAN


def load_dependencies(sources):
    _require(type(sources) is dict and all(type(k) is str for k in sources)
             and set(sources) == set(DEPENDENCIES), "Wrong dependency selections")
    snapshots = dict(sources)
    for name, (size, digest) in DEPENDENCIES.items():
        raw = snapshots[name]
        _require(type(raw) is bytes and len(raw) == size
                 and hashlib.sha256(raw).hexdigest() == digest,
                 "Pinned dependency differs: " + name)
    modules = {}
    for name, raw in snapshots.items():
        module = ModuleType("_b4_recorder_private_" + name)
        module.__file__ = "<pinned-b4-recorder-" + name + ">"
        exec(compile(raw, module.__file__, "exec"), module.__dict__)
        modules[name] = module
    return SimpleNamespace(**modules)


def _lifecycle(raw):
    return {"epoch_token": int.from_bytes(raw[0:8], "little"),
            "last_frame_token": int.from_bytes(raw[8:16], "little"),
            "phase": raw[113]}


def _analysis(samples, flash):
    observed = {name: raw for name, address, raw in samples}
    owner = None
    names = ["owner." + str(i) for i in range(10)]
    if all(name in observed for name in names):
        owner = b"".join(observed[name] for name in names)
    lifecycle = {
        "before": _lifecycle(observed["before.lifecycle"])
        if "before.lifecycle" in observed else None,
        "body": _lifecycle(owner[BRACKET_OFFSET:]) if owner is not None else None,
        "after": _lifecycle(observed["after.lifecycle"])
        if "after.lifecycle" in observed else None}
    pairs = (("before_body", "before", "body"), ("body_after", "body", "after"),
             ("before_after", "before", "after"))
    equalities = {
        name: None if lifecycle[left] is None or lifecycle[right] is None else {
            key: lifecycle[left][key] == lifecycle[right][key] for key in LIFECYCLE_FIELDS}
        for name, left, right in pairs}
    return {"schema": "b4-recorder-capture-analysis-v1", "flash": dict(flash),
            "owner": None if owner is None else {
                "address": OWNER_ADDRESS, "bytes": len(owner),
                "sha256": hashlib.sha256(owner).hexdigest(), "chunks": 10},
            "lifecycle": lifecycle, "equalities": equalities, "coherence": "UNPROVEN"}


def _capture_type(dependencies):
    support = dependencies.capture

    class B4RecorderCapture(support.Capture):
        source = SOURCE
        result_schema = "b4-recorder-capture-result-v1"
        attempt_schema = "b4-recorder-capture-attempt-v1"

        def profile_bindings(self):
            _require(_same(self.input_bindings, _BINDINGS), "Wrong fixed B4 binding")
            _require(sys.flags.dont_write_bytecode, "Python -B is required")
            return fixed_bindings()

        def prepare_plan(self):
            self.plan = read_plan()
            _require(_same(self.plan, _READ_PLAN), "Wrong fixed B4 read plan")
            for name, address, size in self.plan[7:19]:
                dependencies.p0.ram_range(address, size)
            self.report["analysis"] = _analysis([], dict.fromkeys(FLASH_KEYS, False))

        def gather(self):
            flash = dict.fromkeys(FLASH_KEYS, False)
            brackets = {4: ("before_loader", 0, 5, self.loader),
                        6: ("before_sketch", 5, 7, self.sketch),
                        20: ("after_sketch", 19, 21, self.sketch),
                        25: ("after_loader", 21, 26, self.loader)}
            for index, item in enumerate(self.plan):
                _require(self.report["first_error"] is None, "Earlier capture read failed")
                try:
                    self.one_read(index, item)
                    if index in brackets:
                        label, begin, end, reference = brackets[index]
                        flash[label] = b"".join(row[2] for row in
                                              self.samples[begin:end]) == reference
                        _require(flash[label], "Captured flash image differs: " + label)
                finally:
                    self.report["analysis"] = _analysis(self.samples, flash)
                self.budget()

        def complete(self):
            analysis = self.report["analysis"]
            return (analysis is not None and _same(self.report["counts"], COUNTS)
                    and len(self.report["reads"]) == 26
                    and all(analysis["flash"].values()) and analysis["owner"] is not None
                    and all(value is not None for value in analysis["lifecycle"].values())
                    and all(value is not None for value in analysis["equalities"].values()))

    return B4RecorderCapture


def collect(dependencies, *, bindings, fs_root=Path("/"), executor=None, clock=None):
    capture = _capture_type(dependencies)(
        dependencies.helper, None, dependencies.p0.loader_image, fs_root, executor,
        clock, None, bindings, RUN_ID)
    return dependencies.capture._collect(capture)
