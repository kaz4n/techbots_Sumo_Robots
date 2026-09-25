# Tests D177 thin action composition from its frozen public contract.
# Keeps host admission, error evidence and conditional capture independently checked.
# Run only after oracle freeze with Linux Python -B; all action dependencies are inert.
"""Independent oracle; authored without reading/importing the subject implementation.

Basis: P7_motor_fault_actions_contract.md (aacce7cc, clarification 1933c59c), D175/D176 contracts,
and explicit public clarification: upload stdout/stderr are top-level fields;
all read/relocation addresses are integers. No physical evidence is inferred.
"""

import base64
import bz2
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import random
import shlex
import subprocess
import sys
import types
import unittest
from unittest import mock


RUN = "motor-fault-8f592937-run01"
SOURCE = "8f592937961a0c95b7cc4db88617169fcc9504644aa8b8b7dcf62f83c4c33f36"
PARENT = "/home/arduino/sumox26_codex_build/"
ADB = "C:/Users/narut/AppData/Local/Arduino15/packages/arduino/tools/adb/32.0.0/adb.exe"
INSTALLED = "/home/arduino/sumox26-capture-tools/runtime-a4d58b3cbac8/"
MODULE_PINS = (
    ("p0_capture", 18880, "885c4e4206aea4ac9e03c4e92e48258db2a0ae302ff83a86430e6913afeeb57c"),
    ("recorder_heap", 11002, "d661024975925a7d8a83f4b772199bbf59911adb5adb8ea69a2082b69eed4b92"),
    ("runtime_capture", 28644, "a4d58b3cbac8b0a3cf96ce6d4f53bc17e935b9aee9bc1c09809ee20ea806fdae"),
)
ENVELOPE_KEYS = {"schema", "action", "run_id", "source_sha256", "report",
                 "remote_result_path", "full_result_bytes", "full_result_sha256",
                 "first_error", "postcheck_errors"}
SEQUENCE_KEYS = {"schema", "status", "upload", "capture", "upload_attempts",
                 "capture_attempts", "first_error", "postcheck_errors"}
REAL_SHA256 = hashlib.sha256
CONTROL_NAME = "_d177_oracle_control"


def canonical(value, *, allow_nan=False):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True,
                       separators=(",", ":"), allow_nan=allow_nan) + "\n").encode("ascii")


def digest(raw):
    return REAL_SHA256(raw).hexdigest()


def binding(action):
    return {"schema": "fixed-motor-fault-" + action + "-v1", "run_id": RUN,
            "source_sha256": SOURCE, "output": PARENT + RUN + "-" + action,
            "opaque": {"nested": ["left to public API", 9]}}


def common_report(action):
    return {"schema": "motor-fault-" + action + "-result-v1", "run_id": RUN,
            "source_sha256": SOURCE, "status": "UPLOADED" if action == "upload" else "COLLECTED",
            "started_utc": "2026-09-25T01:00:00Z", "finished_utc": "2026-09-25T01:00:03Z",
            "started_monotonic": 10.0, "finished_monotonic": 13.0,
            "first_error": None, "postcheck_errors": []}


def upload_report(streams=False):
    value = common_report("upload")
    value.update(attempts=1, subprocess={"returncode": 0, "timed_out": False, "reaped": True})
    if streams:
        value.update(stdout="full stdout\n", stderr="full stderr\n")
    return value


def capture_report(nodes=1):
    value = common_report("capture")
    visited = [0x20002000 + 0x100 * i for i in range(nodes)]
    bss = 0x20004000
    reads = []

    def add(name, address, size):
        equal_bytes_key = name.replace("before.", "").replace("after.", "").replace("-confirm", "")
        reads.append({"name": name, "address": address, "bytes": size,
                      "sha256": digest(equal_bytes_key.encode()), "file": f"{len(reads):02d}-{name}.bin"})

    def loader(prefix):
        for i in range(5):
            add(f"{prefix}.loader.{i}", 0x08000000 + i * 65536, 65536 if i < 4 else 1536)

    def relocation(prefix):
        add(prefix + ".llext-list", 0x200017BC, 8)
        for i, address in enumerate(visited, 1):
            add(f"{prefix}.node-{i}", address, 196)
        add(prefix + ".llext-list-confirm", 0x200017BC, 8)

    loader("before")
    add("before.sketch.0", 0x08100000, 29836)
    relocation("before")
    add("first.diagnostic", bss, 2592)
    add("second.diagnostic", bss, 2592)
    relocation("after")
    add("after.sketch.0", 0x08100000, 29836)
    loader("after")
    extension = {"node_address": visited[-1], "bss_address": bss,
                 "bss_size": 2632, "visited_nodes": visited}
    value.update(counts={"commands": 18 + 2 * nodes, "reads": 18 + 2 * nodes,
                         "requested_bytes": 592248 + 392 * nodes},
                 wait={"requested_seconds": 2, "before": 10.5, "after": 12.5}, reads=reads,
                 analysis={"schema": "motor-fault-capture-analysis-v1", "coherence": "UNPROVEN",
                           "flash": dict.fromkeys(("before_loader", "before_sketch",
                                                   "after_loader", "after_sketch"), True),
                           "relocation": {"before": extension, "after": copy.deepcopy(extension)},
                           "snapshots": [copy.deepcopy(x) for x in reads if x["name"].endswith("diagnostic")]})
    return value


def envelope(action, report=None):
    if report is None:
        report = upload_report() if action == "upload" else capture_report()
    raw = canonical(report)
    return {"schema": "motor-fault-action-v1", "action": action, "run_id": RUN,
            "source_sha256": SOURCE, "report": copy.deepcopy(report),
            "remote_result_path": PARENT + RUN + "-" + action + "/" + action + "_result.json",
            "full_result_bytes": len(raw), "full_result_sha256": digest(raw),
            "first_error": None, "postcheck_errors": []}


def refresh(value):
    raw = canonical(value["report"], allow_nan=True)
    value.update(full_result_bytes=len(raw), full_result_sha256=digest(raw))
    return value


def inline_sources(action):
    start = f"import sys\nimport {CONTROL_NAME} as c\nc.loaded(__name__, __file__, sys.modules[__name__])\n"
    sources = {"helper": (start + "def logical_read(fd, path, limit):\n return c.read(fd, path, limit)\n").encode(),
               "support": (start + "import fixed_motor_fault_helper\n"
                           "def collect_motor_fault(helper, runtime, loader_image, *, bindings, run_id):\n"
                           " return c.capture(helper, runtime, loader_image, bindings, run_id)\n").encode()}
    if action == "upload":
        sources["upload"] = (start + "import fixed_motor_fault_support\n"
                             "def upload_loader(helper, support, *, bindings, run_id):\n"
                             " return c.upload(helper, support, bindings, run_id)\n").encode()
    return sources


def payload(action, sources=None, bindings=None):
    if sources is None:
        sources = inline_sources(action)
    return {"run_id": RUN, "source_sha256": SOURCE,
            "sources": {key: {"source": raw.decode("utf-8"), "sha256": digest(raw)}
                        for key, raw in sources.items()},
            "bindings": binding(action) if bindings is None else bindings}


class BootstrapHarness:
    """Executes only exported bootstrap text against fake modules and root reads."""

    def __init__(self, subject, action="capture"):
        self.subject, self.action = subject, action
        self.events, self.read_counts = [], {}
        self.read_errors, self.corrupt_reads = {}, set()
        self.import_failure, self.action_error, self.close_error = None, None, None
        self.report = capture_report() if action == "capture" else upload_report(True)
        self.loader_image = object()
        self.control = types.ModuleType(CONTROL_NAME)
        for name in ("loaded", "read", "upload", "capture"):
            setattr(self.control, name, getattr(self, name))
        self.control.loader_image = self.loader_image
        self.installed_bytes = {}

    def loaded(self, name, filename, module):
        self.events.append(("import", name, filename, sys.modules.get(name) is module))
        if name == self.import_failure:
            raise RuntimeError("installed-import-failure")

    def read(self, fd, path, limit):
        name = Path(str(path)).stem
        number = self.read_counts.get(name, 0) + 1
        self.read_counts[name] = number
        self.events.append(("read", name, number, fd, str(path), limit))
        if (name, number) in self.read_errors:
            raise self.read_errors[name, number]
        raw = self.installed_bytes[name]
        return raw + b"!" if (name, number) in self.corrupt_reads else raw

    def upload(self, helper, support, bindings, run_id):
        self.events.append(("upload", helper.__name__, support.__name__, copy.deepcopy(bindings), run_id))
        if self.action_error:
            raise self.action_error
        return self.report

    def capture(self, helper, runtime, loader_image, bindings, run_id):
        self.events.append(("capture", helper.__name__, runtime.__name__, loader_image is self.loader_image,
                            copy.deepcopy(bindings), run_id))
        if self.action_error:
            raise self.action_error
        return self.report

    def prepare_installed(self):
        for name, length, _ in MODULE_PINS:
            code = f"import sys\nimport {CONTROL_NAME} as c\nc.loaded(__name__, __file__, sys.modules[__name__])\n"
            if name == "p0_capture":
                code += "loader_image = c.loader_image\n"
            if name == "runtime_capture":
                code += "import p0_capture, recorder_heap\ndef collect(*a, **k):\n raise AssertionError('legacy collector forbidden')\n"
            raw = code.encode()
            self.installed_bytes[name] = raw + b"#" + b" " * (length - len(raw) - 2) + b"\n"

    def run(self, *, raw=None, token=None, sha=None, argv=None, bytecode=False):
        self.prepare_installed()
        raw = canonical(payload(self.action)) if raw is None else raw
        token = base64.b64encode(bz2.compress(raw, compresslevel=9)).decode() if token is None else token
        sha = digest(raw) if sha is None else sha
        arguments = ["-c", self.action, sha, token] if argv is None else argv
        pinned = {self.installed_bytes[name]: pin for name, _, pin in MODULE_PINS}
        class HashAdapter:
            def __init__(self, data=b"", **kwargs):
                self.data = bytes(data)

            def update(self, data):
                self.data += bytes(data)

            def hexdigest(self):
                return pinned.get(self.data, digest(self.data))

            def digest(self):
                return bytes.fromhex(self.hexdigest())

        def open_root(path, flags, *args, **kwargs):
            self.events.append(("open", str(path), flags))
            if str(path) != "/" or not flags & os.O_DIRECTORY or not flags & os.O_NOFOLLOW:
                raise AssertionError("root must be no-follow directory /")
            return 781

        def close_root(fd):
            self.events.append(("close", fd))
            if fd != 781:
                raise AssertionError("unexpected descriptor")
            if self.close_error:
                raise self.close_error

        names = [CONTROL_NAME] + ["fixed_motor_fault_" + x for x in ("helper", "support", "upload")]
        names += [x[0] for x in MODULE_PINS]
        saved = {name: sys.modules.get(name) for name in names}
        for name in names:
            sys.modules.pop(name, None)
        sys.modules[CONTROL_NAME] = self.control
        class CapturedStdout(io.StringIO):
            @property
            def buffer(self):
                return self

            def write(self, value):
                return super().write(value.decode("utf-8") if isinstance(value, bytes) else value)

        stream, caught = CapturedStdout(), None
        try:
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(sys, "argv", arguments))
                stack.enter_context(mock.patch.object(sys, "dont_write_bytecode", not bytecode))
                stack.enter_context(mock.patch.object(hashlib, "sha256", HashAdapter))
                stack.enter_context(mock.patch.object(os, "open", open_root))
                stack.enter_context(mock.patch.object(os, "close", close_root))
                stack.enter_context(mock.patch.object(subprocess, "Popen", side_effect=AssertionError("no process")))
                stack.enter_context(contextlib.redirect_stdout(stream))
                try:
                    exec(compile(self.subject.BOOTSTRAP, "<D177-public-BOOTSTRAP>", "exec"), {"__name__": "__main__"})
                except BaseException as error:
                    if not isinstance(error, SystemExit) or error.code not in (None, 0):
                        caught = error
        finally:
            for name in names:
                sys.modules.pop(name, None)
                if saved[name] is not None:
                    sys.modules[name] = saved[name]
        return stream.getvalue(), caught


class D177Oracle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not sys.dont_write_bytecode:
            raise RuntimeError("run the frozen oracle with Python -B")
        path = Path(__file__).with_name("inert_actions.py")
        spec = importlib.util.spec_from_file_location("d177_subject_under_test", path)
        cls.subject = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.subject
        with mock.patch.object(subprocess, "Popen", side_effect=AssertionError("no process during import")), \
                mock.patch.object(os, "system", side_effect=AssertionError("no shell during import")):
            spec.loader.exec_module(cls.subject)

    def command(self, action="upload", sources=None, bindings=None):
        return self.subject.build_command(action, inline_sources(action) if sources is None else sources,
                                          binding(action) if bindings is None else bindings)

    def decoded(self, command):
        return bz2.decompress(base64.b64decode(command[-1], validate=True))

    def output(self, harness, **kwargs):
        text, error = harness.run(**kwargs)
        self.assertIsNone(error, repr(error))
        value = json.loads(text)
        self.assertEqual(text.encode(), canonical(value))
        self.assertLessEqual(len(text.encode()), 65536)
        self.assertEqual(set(value), ENVELOPE_KEYS)
        return value

    def denied_bootstrap(self, **kwargs):
        harness = BootstrapHarness(self.subject, "upload")
        text, error = harness.run(**kwargs)
        self.assertIsNotNone(error)
        self.assertEqual(text, "")
        self.assertEqual(harness.events, [])

    def rejects_report(self, action, mutate):
        value = envelope(action)
        mutate(value["report"])
        refresh(value)
        with self.assertRaises(ValueError):
            self.subject.validate_reply(action, value)

    def test_command_fixed_argv_and_canonical_payload_for_both_actions(self):
        prefix = ["/usr/bin/env", "-i", "HOME=/home/arduino", "USER=arduino", "LOGNAME=arduino",
                  "PATH=/usr/bin:/bin", "LANG=C", "LC_ALL=C", "/usr/bin/python3", "-I", "-B", "-c"]
        for action in ("upload", "capture"):
            with self.subTest(action=action):
                command = self.command(action)
                self.assertIs(type(command), list)
                self.assertEqual(command[:12], prefix)
                self.assertEqual(command[12], self.subject.BOOTSTRAP)
                self.assertEqual(command[13], action)
                self.assertEqual(len(command), 16)
                raw = self.decoded(command)
                self.assertEqual(raw, canonical(payload(action)))
                self.assertEqual(command[-2], digest(raw))
                self.assertEqual(base64.b64encode(base64.b64decode(command[-1])).decode(), command[-1])
                actual = [ADB, "-s", "2629958581", "shell", "-T", shlex.join(command)]
                self.assertLessEqual(len(subprocess.list2cmdline(actual).encode("utf-16-le")) // 2, 30000)

    def test_command_preserves_caller_sources_bindings_and_utf8_source(self):
        sources, bindings = inline_sources("upload"), binding("upload")
        sources["helper"] += "# caf\u00e9 \u03bb\n".encode()
        before = copy.deepcopy((sources, bindings))
        command = self.command(sources=sources, bindings=bindings)
        self.assertEqual((sources, bindings), before)
        self.assertEqual(json.loads(self.decoded(command))["sources"]["helper"]["source"], sources["helper"].decode())

    def test_command_rejects_nonexact_actions_and_bad_sources(self):
        class Text(str):
            pass
        for action in (None, b"upload", Text("upload"), "UPLOAD", "capture ", "reset", "../upload"):
            with self.subTest(action=repr(action)), self.assertRaises((TypeError, ValueError)):
                self.command(action, sources=inline_sources("upload"), bindings=binding("upload"))
        for changed in (None, [], {}, {"helper": b"x"}, {**inline_sources("upload"), "extra": b"x"}):
            with self.subTest(sources=repr(changed)), self.assertRaises((TypeError, ValueError)):
                self.subject.build_command("upload", changed, binding("upload"))
        for bad in (b"", b"\xff", "text", 1, None):
            sources = inline_sources("upload")
            sources["helper"] = bad
            with self.subTest(source=repr(bad)), self.assertRaises((TypeError, ValueError)):
                self.command(sources=sources)

    def test_command_rejects_binding_identity_mixes_but_defers_deep_schema(self):
        for key in ("schema", "run_id", "source_sha256", "output"):
            wrong = binding("upload")
            wrong[key] = "wrong"
            with self.subTest(key=key), self.assertRaises((TypeError, ValueError)):
                self.command(bindings=wrong)
        for bad in ([], None, {"schema": "fixed-motor-fault-upload-v1"}):
            with self.subTest(bindings=bad), self.assertRaises((TypeError, ValueError)):
                self.subject.build_command("upload", inline_sources("upload"), bad)
        self.command(bindings=binding("upload"))  # Opaque shape is delegated, not independently cloned.

    def test_command_rejects_nonfinite_or_nonjson_bindings(self):
        for bad in (float("nan"), float("inf"), float("-inf"), object(), b"bytes"):
            bindings = binding("upload")
            bindings["opaque"] = bad
            with self.subTest(value=repr(bad)), self.assertRaises((TypeError, ValueError)):
                self.command(bindings=bindings)

    def test_command_payload_exact_limit_and_one_byte_over(self):
        sources = inline_sources("upload")
        sources["helper"] += b"#"
        gap = 196608 - len(canonical(payload("upload", sources)))
        sources["helper"] += b"x" * gap
        self.assertEqual(len(self.decoded(self.command(sources=sources))), 196608)
        sources["helper"] += b"x"
        with self.assertRaises(ValueError):
            self.command(sources=sources)

    def test_command_rejects_actual_windows_ceiling(self):
        rng = random.Random(177)
        noisy = "".join(chr(rng.randrange(33, 127)) for _ in range(45000)).encode()
        sources = inline_sources("upload")
        sources["helper"] += b"#" + noisy
        self.assertLess(len(canonical(payload("upload", sources))), 196608)
        with self.assertRaises(ValueError):
            self.command(sources=sources)

    def test_bootstrap_upload_order_registration_dispatch_and_compact_digest(self):
        harness = BootstrapHarness(self.subject, "upload")
        original = copy.deepcopy(harness.report)
        value = self.output(harness)
        expected = upload_report()
        self.assertEqual(value["report"], expected)
        self.assertEqual(value["full_result_bytes"], len(canonical(original)))
        self.assertEqual(value["full_result_sha256"], digest(canonical(original)))
        self.assertEqual(value["remote_result_path"], envelope("upload")["remote_result_path"])
        self.assertIsNone(value["first_error"])
        self.assertEqual(value["postcheck_errors"], [])
        imports = [e for e in harness.events if e[0] == "import"]
        self.assertEqual(imports, [("import", "fixed_motor_fault_" + role, "/__sumox__/" + role + ".py", True)
                                   for role in ("helper", "support", "upload")])
        self.assertEqual(harness.events[-1], ("upload", "fixed_motor_fault_helper", "fixed_motor_fault_support", binding("upload"), RUN))

    def test_bootstrap_capture_pin_reads_before_exec_and_independent_rereads(self):
        harness = BootstrapHarness(self.subject)
        value = self.output(harness)
        self.assertEqual(value, envelope("capture", harness.report))
        reads = [e for e in harness.events if e[0] == "read"]
        self.assertEqual([(e[1], e[2]) for e in reads], [(name, turn) for turn in (1, 2) for name, _, _ in MODULE_PINS])
        for event in reads:
            self.assertEqual(event[3], 781)
            self.assertEqual(event[4], INSTALLED + event[1] + ".py")
            self.assertEqual(event[5], dict((n, size) for n, size, _ in MODULE_PINS)[event[1]])
        imports = [e for e in harness.events if e[0] == "import"]
        self.assertEqual([e[1] for e in imports], ["fixed_motor_fault_helper", "fixed_motor_fault_support"] + [p[0] for p in MODULE_PINS])
        self.assertTrue(all(e[3] for e in imports))
        first_installed = next(i for i, e in enumerate(harness.events) if e[:2] == ("import", "p0_capture"))
        self.assertEqual(sum(e[0] == "read" for e in harness.events[:first_installed]), 3)
        self.assertEqual([e for e in harness.events if e[0] == "capture"],
                         [("capture", "fixed_motor_fault_helper", "runtime_capture", True, binding("capture"), RUN)])
        self.assertEqual(harness.events[-1], ("close", 781))

    def test_bootstrap_rejects_action_count_or_missing_B_before_sources(self):
        raw = canonical(payload("upload"))
        token = base64.b64encode(bz2.compress(raw)).decode()
        for argv in (["-c"], ["-c", "upload", digest(raw), token, "extra"], ["-c", "reset", digest(raw), token]):
            with self.subTest(argv=argv[:2]):
                self.denied_bootstrap(argv=argv)
        self.denied_bootstrap(bytecode=True)

    def test_bootstrap_rejects_noncanonical_base64_and_bz2_frames(self):
        raw = canonical(payload("upload"))
        compressed = bz2.compress(raw)
        token = base64.b64encode(compressed).decode()
        for bad in (token + "\n", " " + token, token + "=", "!" + token, token.rstrip("=") + "==="):
            with self.subTest(kind=bad[-8:]):
                self.denied_bootstrap(token=bad)
        for blob in (compressed[:-1], compressed + b"garbage", compressed + bz2.compress(b"{}"), b"not-bz2"):
            with self.subTest(blob_size=len(blob)):
                self.denied_bootstrap(token=base64.b64encode(blob).decode())

    def test_bootstrap_bounded_expansion_and_digest(self):
        self.denied_bootstrap(raw=b" " * 196609)
        for bad in ("0" * 64, "F" * 64, "abc", "", "g" * 64):
            with self.subTest(sha=bad):
                self.denied_bootstrap(sha=bad)

    def test_bootstrap_rejects_duplicate_keys_nonfinite_and_closed_shape(self):
        raw = canonical(payload("upload"))
        self.denied_bootstrap(raw=b'{"run_id":"duplicate",' + raw[1:])
        self.denied_bootstrap(raw=raw.replace(b'"opaque":{', b'"opaque":{"dup":0,"dup":1,'))
        for token in (b"NaN", b"Infinity", b"-Infinity"):
            with self.subTest(token=token):
                self.denied_bootstrap(raw=raw.replace(b'"opaque":{', b'"bad":' + token + b',"opaque":{'))
        for changed in ({**payload("upload"), "extra": 1}, {k: v for k, v in payload("upload").items() if k != "sources"}, []):
            with self.subTest(shape=type(changed).__name__):
                self.denied_bootstrap(raw=canonical(changed))

    def test_bootstrap_validates_all_inline_hashes_and_identities_before_exec(self):
        for role in ("helper", "support", "upload"):
            value = payload("upload")
            value["sources"][role]["sha256"] = "0" * 64
            with self.subTest(role=role):
                self.denied_bootstrap(raw=canonical(value))
        for scope, keys in (("outer", ("run_id", "source_sha256")),
                            ("bindings", ("schema", "run_id", "source_sha256", "output"))):
            for key in keys:
                value = payload("upload")
                (value if scope == "outer" else value["bindings"])[key] = "wrong"
                with self.subTest(scope=scope, key=key):
                    self.denied_bootstrap(raw=canonical(value))

    def test_bootstrap_rejects_source_entry_shape_and_action_role_mixing(self):
        for mutate in (lambda p: p["sources"].pop("upload"),
                       lambda p: p["sources"].update(extra={"source": "pass", "sha256": digest(b"pass")}),
                       lambda p: p["sources"]["helper"].update(extra=True),
                       lambda p: p["sources"]["helper"].update(source=7),
                       lambda p: p["sources"]["helper"].update(source="", sha256=digest(b""))):
            value = payload("upload")
            mutate(value)
            self.denied_bootstrap(raw=canonical(value))

    def test_bootstrap_capture_initial_read_or_hash_failure_still_postchecks_every_pin(self):
        for fault in ("read", "hash"):
            for name, _, _ in MODULE_PINS:
                harness = BootstrapHarness(self.subject)
                if fault == "read":
                    harness.read_errors[name, 1] = RuntimeError("initial-read")
                else:
                    harness.corrupt_reads.add((name, 1))
                with self.subTest(fault=fault, module=name):
                    value = self.output(harness)
                    self.assertIsNotNone(value["first_error"])
                    self.assertIsNone(value["report"])
                    self.assertIsNone(value["full_result_bytes"])
                    self.assertIsNone(value["full_result_sha256"])
                    self.assertEqual([e[1] for e in harness.events if e[0] == "read"][-3:], [x[0] for x in MODULE_PINS])
                    self.assertFalse(any(e[0] == "capture" or e[:2] == ("import", "p0_capture") for e in harness.events))
                    self.assertEqual(harness.events[-1], ("close", 781))

    def test_bootstrap_capture_import_failures_postcheck_and_close(self):
        for name, _, _ in MODULE_PINS:
            harness = BootstrapHarness(self.subject)
            harness.import_failure = name
            with self.subTest(module=name):
                value = self.output(harness)
                self.assertEqual(value["first_error"], {"type": "RuntimeError", "message": "installed-import-failure"})
                self.assertEqual([e[1] for e in harness.events if e[0] == "read"][-3:], [x[0] for x in MODULE_PINS])
                self.assertFalse(any(e[0] == "capture" for e in harness.events))
                self.assertEqual(harness.events[-1], ("close", 781))

    def test_bootstrap_capture_action_first_error_and_all_later_failures_preserved(self):
        harness = BootstrapHarness(self.subject)
        harness.action_error = RuntimeError("action-primary")
        for name, _, _ in MODULE_PINS:
            harness.read_errors[name, 2] = OSError("post-" + name)
        harness.close_error = OSError("root-close")
        value = self.output(harness)
        self.assertEqual(value["first_error"], {"type": "RuntimeError", "message": "action-primary"})
        self.assertEqual([x["message"] for x in value["postcheck_errors"]],
                         ["post-" + x[0] for x in MODULE_PINS] + ["root-close"])
        self.assertTrue(all(set(x) == {"check", "type", "message"} for x in value["postcheck_errors"]))

    def test_bootstrap_capture_successful_report_survives_posthash_and_close_failure(self):
        harness = BootstrapHarness(self.subject)
        harness.corrupt_reads.add(("p0_capture", 2))
        harness.close_error = OSError("close-secondary")
        value = self.output(harness)
        self.assertEqual(value["report"], harness.report)
        self.assertEqual(value["full_result_sha256"], digest(canonical(harness.report)))
        self.assertIsNotNone(value["first_error"])
        self.assertTrue(any(x["message"] == "close-secondary" for x in value["postcheck_errors"]))
        self.assertEqual([e[1] for e in harness.events if e[0] == "read"][-3:], [x[0] for x in MODULE_PINS])

    def test_bootstrap_preserves_failed_report_and_omits_only_upload_streams(self):
        harness = BootstrapHarness(self.subject, "upload")
        harness.report.update(status="FAILED", first_error={"type": "RuntimeError", "message": "child"})
        harness.report["extra_evidence"] = {"stdout": "nested must remain", "stderr": "nested remains"}
        original = copy.deepcopy(harness.report)
        value = self.output(harness)
        expected = {k: v for k, v in original.items() if k not in ("stdout", "stderr")}
        self.assertEqual(value["report"], expected)
        self.assertEqual(value["full_result_bytes"], len(canonical(original)))
        self.assertEqual(value["full_result_sha256"], digest(canonical(original)))

    def test_bootstrap_upload_exception_has_no_fabricated_report_or_digest(self):
        harness = BootstrapHarness(self.subject, "upload")
        harness.action_error = ValueError("upload-failed")
        value = self.output(harness)
        self.assertEqual(value["first_error"], {"type": "ValueError", "message": "upload-failed"})
        for key in ("report", "full_result_bytes", "full_result_sha256"):
            self.assertIsNone(value[key])

    def test_bootstrap_oversize_reply_raises_and_never_truncates(self):
        harness = BootstrapHarness(self.subject, "upload")
        harness.report["retained"] = "x" * 65536
        text, error = harness.run()
        self.assertIsNotNone(error)
        self.assertEqual(text, "")

    def test_reply_admits_upload_and_all_three_capture_node_counts_without_mutation(self):
        for action, report in [("upload", upload_report())] + [("capture", capture_report(n)) for n in (1, 2, 3)]:
            with self.subTest(action=action, nodes=report.get("counts")):
                value = envelope(action, report)
                before = copy.deepcopy(value)
                self.assertIsNone(self.subject.validate_reply(action, value))
                self.assertEqual(value, before)

    def test_reply_closed_envelope_identity_path_error_and_type_checks(self):
        for action in ("upload", "capture"):
            candidates = [None, [], {}, {**envelope(action), "extra": True}]
            for key in ENVELOPE_KEYS:
                value = envelope(action)
                del value[key]
                candidates.append(value)
            for key in ("schema", "action", "run_id", "source_sha256", "remote_result_path"):
                value = envelope(action)
                value[key] = "wrong"
                candidates.append(value)
            for key, bad in (("first_error", {}), ("postcheck_errors", [{}]), ("postcheck_errors", None),
                             ("report", None), ("report", [])):
                value = envelope(action)
                value[key] = bad
                candidates.append(value)
            for value in candidates:
                with self.subTest(action=action, value=repr(value)[:80]), self.assertRaises(ValueError):
                    self.subject.validate_reply(action, value)

    def test_reply_full_size_digest_and_exact_action_types(self):
        for key, bad_values in (("full_result_bytes", (False, True, 0, -1, 1.5, "1", 16777217, math.nan, math.inf)),
                                ("full_result_sha256", (None, "", "A" * 64, "g" * 64, "0" * 63, "0" * 65))):
            for bad in bad_values:
                value = envelope("upload")
                value[key] = bad
                with self.subTest(key=key, bad=bad), self.assertRaises(ValueError):
                    self.subject.validate_reply("upload", value)
        class Text(str):
            pass
        for action in (None, b"upload", Text("upload"), "UPLOAD", "reset"):
            with self.subTest(action=repr(action)), self.assertRaises(ValueError):
                self.subject.validate_reply(action, envelope("upload"))

    def test_reply_common_schema_identity_status_and_extra_keys(self):
        for action in ("upload", "capture"):
            for key, value in (("schema", "wrong"), ("run_id", "wrong"), ("source_sha256", "wrong"),
                               ("status", "FAILED"), ("extra", 1), ("first_error", {}),
                               ("postcheck_errors", [1]), ("postcheck_errors", None)):
                with self.subTest(action=action, key=key):
                    self.rejects_report(action, lambda report, k=key, v=value: report.update({k: v}))
            for key in common_report(action):
                with self.subTest(action=action, missing=key):
                    self.rejects_report(action, lambda report, k=key: report.pop(k))

    def test_reply_finite_clock_types_order_and_utc(self):
        for action in ("upload", "capture"):
            for key in ("started_utc", "finished_utc"):
                for bad in ("", None, 123, False):
                    with self.subTest(action=action, key=key, bad=bad):
                        self.rejects_report(action, lambda r, k=key, v=bad: r.update({k: v}))
            for key in ("started_monotonic", "finished_monotonic"):
                for bad in (False, True, -1, "10", math.nan, math.inf, -math.inf):
                    with self.subTest(action=action, key=key, bad=bad):
                        self.rejects_report(action, lambda r, k=key, v=bad: r.update({k: v}))
            self.rejects_report(action, lambda r: r.update(finished_monotonic=9))

    def test_reply_duration_strict_thresholds(self):
        for action, limit in (("upload", 180), ("capture", 600)):
            value = envelope(action)
            value["report"]["finished_monotonic"] = 10 + limit - 0.001
            refresh(value)
            self.subject.validate_reply(action, value)
            for elapsed in (limit, limit + 0.001):
                with self.subTest(action=action, elapsed=elapsed):
                    self.rejects_report(action, lambda r, v=elapsed: r.update(finished_monotonic=10 + v))

    def test_reply_upload_attempts_and_subprocess_are_exact(self):
        for bad in (False, True, 0, 2, 1.0, "1", None):
            with self.subTest(attempts=bad):
                self.rejects_report("upload", lambda r, v=bad: r.update(attempts=v))
        for key, values in (("returncode", (False, True, 1, 0.0, "0", None)),
                            ("timed_out", (0, None, True)), ("reaped", (1, None, False))):
            for bad in values:
                with self.subTest(key=key, value=bad):
                    self.rejects_report("upload", lambda r, k=key, v=bad: r["subprocess"].update({k: v}))
        for mutate in (lambda r: r["subprocess"].update(stdout=""), lambda r: r["subprocess"].pop("reaped"),
                       lambda r: r.update(stdout=""), lambda r: r.update(stderr="")):
            self.rejects_report("upload", mutate)

    def test_reply_capture_full_report_hash_and_length_must_match(self):
        for key, bad in (("full_result_bytes", 1), ("full_result_sha256", "0" * 64)):
            value = envelope("capture")
            value[key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.subject.validate_reply("capture", value)

    def test_reply_capture_analysis_flash_coherence_and_shapes(self):
        mutations = [lambda r: r["analysis"].update(extra=1), lambda r: r["analysis"].pop("schema"),
                     lambda r: r["analysis"].update(schema="wrong"), lambda r: r["analysis"].update(coherence="PROVEN"),
                     lambda r: r["analysis"]["flash"].update(extra=True)]
        for flag in ("before_loader", "before_sketch", "after_loader", "after_sketch"):
            for bad in (False, 1, None):
                mutations.append(lambda r, k=flag, v=bad: r["analysis"]["flash"].update({k: v}))
        for mutate in mutations:
            self.rejects_report("capture", mutate)

    def test_reply_capture_relocation_types_bounds_alignment_and_matching(self):
        bad_fields = {"node_address": [True, "0x20002000", 0x20002004],
                      "bss_address": [True, 0x20004004, 0x1FFFFFF8, 0x200C0000 - 2632 + 8],
                      "bss_size": [True, 2632.0, 2631, 2633],
                      "visited_nodes": [[], [0x20002000] * 2, [0x20002000] * 4,
                                        [True], [0x20002002], [0x1FFFFFFC], [0x200C0000 - 192]]}
        for key, values in bad_fields.items():
            for bad in values:
                def mutate(report, key=key, bad=bad):
                    for side in ("before", "after"):
                        report["analysis"]["relocation"][side][key] = bad
                with self.subTest(key=key, value=bad):
                    self.rejects_report("capture", mutate)
        for mutate in (lambda r: r["analysis"]["relocation"].update(extra=None),
                       lambda r: r["analysis"]["relocation"].update(after=None),
                       lambda r: r["analysis"]["relocation"]["after"].update(bss_address=0x20005000),
                       lambda r: r["analysis"]["relocation"]["before"].update(extra=1)):
            self.rejects_report("capture", mutate)

    def test_reply_capture_counts_are_exact_and_bool_is_not_integer(self):
        for key in ("commands", "reads", "requested_bytes"):
            for bad in (True, 0, 1, 24, "20", 20.0):
                with self.subTest(key=key, bad=bad):
                    self.rejects_report("capture", lambda r, k=key, v=bad: r["counts"].update({k: v}))
        self.rejects_report("capture", lambda r: r["counts"].update(extra=1))

    def test_reply_capture_read_order_addresses_sizes_hashes_and_basenames(self):
        for index in range(20):
            for key, bad in (("name", "wrong"), ("address", True), ("address", "0x20004000"),
                             ("address", 0), ("bytes", True), ("bytes", 1), ("sha256", "F" * 64),
                             ("sha256", "bad"), ("file", "../raw.bin"), ("file", "/raw.bin"), ("extra", 1)):
                with self.subTest(index=index, key=key, bad=bad):
                    self.rejects_report("capture", lambda r, i=index, k=key, v=bad: r["reads"][i].update({k: v}))
        for mutate in (lambda r: r["reads"].reverse(), lambda r: r["reads"].pop(),
                       lambda r: r["reads"].append(copy.deepcopy(r["reads"][0])),
                       lambda r: r["reads"][0].pop("sha256")):
            self.rejects_report("capture", mutate)

    def test_reply_capture_snapshots_exactly_bind_the_two_read_entries(self):
        for mutate in (lambda r: r["analysis"].update(snapshots=[]),
                       lambda r: r["analysis"]["snapshots"].reverse(),
                       lambda r: r["analysis"]["snapshots"][0].update(sha256="0" * 64),
                       lambda r: r["analysis"]["snapshots"].append(copy.deepcopy(r["analysis"]["snapshots"][0]))):
            self.rejects_report("capture", mutate)

    def test_reply_capture_bracket_and_list_confirm_hashes_must_agree(self):
        for name in ("before.loader.0", "before.loader.4", "before.sketch.0", "before.llext-list",
                     "before.llext-list-confirm", "before.node-1", "after.loader.0", "after.loader.4",
                     "after.sketch.0", "after.llext-list", "after.llext-list-confirm", "after.node-1"):
            def mutate(report, name=name):
                next(item for item in report["reads"] if item["name"] == name)["sha256"] = "0" * 64
            with self.subTest(read=name):
                self.rejects_report("capture", mutate)
        value = envelope("capture")
        self.assertNotEqual(value["report"]["analysis"]["snapshots"][0]["sha256"],
                            value["report"]["analysis"]["snapshots"][1]["sha256"])
        self.assertIsNone(self.subject.validate_reply("capture", value))

    def test_reply_capture_wait_interval_requested_time_and_finiteness(self):
        for key, values in (("requested_seconds", (True, 1, 3, "2", math.inf)),
                            ("before", (True, 9.99, 11, math.nan, math.inf, "10.5")),
                            ("after", (True, 12.499, 13.001, math.nan, math.inf, "12.5"))):
            for bad in values:
                with self.subTest(key=key, bad=bad):
                    self.rejects_report("capture", lambda r, k=key, v=bad: r["wait"].update({k: v}))
        self.rejects_report("capture", lambda r: r["wait"].update(extra=1))

    def sequence(self, failures=None, replies=None, finish_error=None):
        failures, replies = failures or {}, replies or {}
        calls, counts, final = [], {}, []

        def invoke(name, *args):
            counts[name] = counts.get(name, 0) + 1
            calls.append((name, *args))
            if (name, counts[name]) in failures:
                raise failures[name, counts[name]]
            if name in ("upload", "capture"):
                return replies.get(name, envelope(name))

        def finish(report):
            calls.append(("finish",))
            final.append(report)
            if finish_error:
                raise finish_error

        operations = {name: (lambda name=name: invoke(name)) for name in ("local", "prerequisites", "upload", "capture")}
        operations.update(intent=lambda action, predecessor: invoke("intent", action, predecessor), finish=finish)
        caught = None
        try:
            self.subject.run_actions(operations)
        except BaseException as error:
            caught = error
        return calls, counts, final, caught

    def test_sequence_success_order_intent_predecessor_and_exact_report(self):
        calls, counts, final, caught = self.sequence()
        self.assertIsNone(caught)
        self.assertEqual([c[0] for c in calls], ["local", "prerequisites", "intent", "upload",
                                              "local", "prerequisites", "intent", "capture",
                                              "local", "prerequisites", "finish"])
        self.assertEqual(calls[2], ("intent", "upload", None))
        self.assertEqual(calls[6], ("intent", "capture", envelope("upload")))
        self.assertEqual(len(final), 1)
        self.assertEqual(final[0], {"schema": "motor-fault-sequence-v1", "status": "COMPLETED",
                                    "upload": envelope("upload"), "capture": envelope("capture"),
                                    "upload_attempts": 1, "capture_attempts": 1,
                                    "first_error": None, "postcheck_errors": []})

    def test_sequence_each_action_stage_failure_stops_without_retry(self):
        stages = [("local", 1, 0, 0), ("prerequisites", 1, 0, 0), ("intent", 1, 0, 0), ("upload", 1, 1, 0),
                  ("local", 2, 1, 0), ("prerequisites", 2, 1, 0), ("intent", 2, 1, 0), ("capture", 1, 1, 1)]
        for name, number, uploads, captures in stages:
            with self.subTest(stage=name, number=number):
                calls, counts, final, caught = self.sequence({(name, number): RuntimeError("primary")})
                self.assertIsNone(caught)
                self.assertEqual([c[0] for c in calls[-3:]], ["local", "prerequisites", "finish"])
                self.assertEqual(len(final), 1)
                report = final[0]
                self.assertEqual(set(report), SEQUENCE_KEYS)
                self.assertEqual(report["status"], "FAILED")
                self.assertEqual(report["first_error"], {"type": "RuntimeError", "message": "primary"})
                self.assertEqual((report["upload_attempts"], report["capture_attempts"]), (uploads, captures))
                self.assertEqual((counts.get("upload", 0), counts.get("capture", 0)), (uploads, captures))

    def test_sequence_invalid_upload_keeps_raw_reply_and_never_calls_capture(self):
        bad = envelope("upload")
        bad["report"]["status"] = "FAILED"
        calls, counts, final, caught = self.sequence(replies={"upload": bad})
        self.assertIsNone(caught)
        self.assertEqual(final[0]["upload"], bad)
        self.assertIsNone(final[0]["capture"])
        self.assertEqual(final[0]["status"], "FAILED")
        self.assertEqual(final[0]["first_error"]["type"], "ValueError")
        self.assertNotIn("capture", counts)
        self.assertEqual(final[0]["capture_attempts"], 0)

    def test_sequence_invalid_capture_keeps_raw_reply_and_one_attempt(self):
        bad = {"malformed": [1, 2]}
        calls, counts, final, caught = self.sequence(replies={"capture": bad})
        self.assertIsNone(caught)
        self.assertEqual(final[0]["capture"], bad)
        self.assertEqual(final[0]["status"], "FAILED")
        self.assertEqual(final[0]["capture_attempts"], 1)
        self.assertEqual(counts["capture"], 1)

    def test_sequence_final_checks_independent_preserve_primary_and_finish_once(self):
        failures = {("upload", 1): RuntimeError("upload-primary"),
                    ("local", 2): OSError("local-post"), ("prerequisites", 2): ValueError("prerequisites-post")}
        calls, counts, final, caught = self.sequence(failures)
        self.assertIsNone(caught)
        self.assertEqual(len(final), 1)
        report = final[0]
        self.assertEqual(report["first_error"], {"type": "RuntimeError", "message": "upload-primary"})
        self.assertEqual([e["message"] for e in report["postcheck_errors"]], ["local-post", "prerequisites-post"])
        self.assertTrue(all(set(e) == {"check", "type", "message"} for e in report["postcheck_errors"]))
        self.assertEqual([c[0] for c in calls[-3:]], ["local", "prerequisites", "finish"])

    def test_sequence_final_check_failure_prevents_completed_status(self):
        for name in ("local", "prerequisites"):
            with self.subTest(check=name):
                calls, counts, final, caught = self.sequence({(name, 3): RuntimeError("post-primary")})
                self.assertIsNone(caught)
                self.assertEqual(final[0]["status"], "FAILED")
                self.assertEqual(final[0]["first_error"], {"type": "RuntimeError", "message": "post-primary"})
                self.assertEqual((counts["local"], counts["prerequisites"]), (3, 3))

    def test_sequence_finish_failure_is_raised_with_failed_report_attached(self):
        error = OSError("finish-primary")
        calls, counts, final, caught = self.sequence(finish_error=error)
        self.assertIs(caught, error)
        self.assertEqual(len(final), 1)
        self.assertEqual(caught.sequence_result["status"], "FAILED")
        self.assertEqual(caught.sequence_result["first_error"], {"type": "OSError", "message": "finish-primary"})
        self.assertEqual(sum(c[0] == "finish" for c in calls), 1)

    def test_sequence_finish_failure_never_replaces_earlier_primary_or_postchecks(self):
        failures = {("upload", 1): RuntimeError("upload-primary"), ("local", 2): ValueError("local-post")}
        error = OSError("finish-secondary")
        calls, counts, final, caught = self.sequence(failures, finish_error=error)
        self.assertIs(caught, error)
        report = caught.sequence_result
        self.assertEqual(report["status"], "FAILED")
        self.assertEqual(report["first_error"], {"type": "RuntimeError", "message": "upload-primary"})
        self.assertEqual([e["message"] for e in report["postcheck_errors"]], ["local-post", "finish-secondary"])
        self.assertEqual(sum(c[0] == "finish" for c in calls), 1)
        self.assertNotIn("capture", counts)

    def test_sequence_rejects_nonclosed_or_noncallable_operations_before_callbacks(self):
        calls = []
        base = {name: (lambda: calls.append("called")) for name in ("local", "prerequisites", "intent", "upload", "capture", "finish")}
        for bad in (None, [], {}, {**base, "extra": lambda: None}, {**base, "capture": None},
                    {key: value for key, value in base.items() if key != "finish"}):
            with self.subTest(shape=repr(bad)[:70]), self.assertRaises((TypeError, ValueError)):
                self.subject.run_actions(bad)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
