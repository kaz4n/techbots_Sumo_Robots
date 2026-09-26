# Runs one fixed capture-only B4 observation with guarded staging and retrieval.
# Reuses the accepted caller guards without an upload predecessor or board writes.
# Focused independent fixtures cover admission, one-shot sequencing and local export.
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import types
import uuid

ROOT = Path(__file__).absolute().parents[1]
RAW = "state/analysis/P7_b4_recorder_run_raw/"
COMPILED = "state/analysis/P7_b4_app_compile_raw/"
SCOPE = RAW + "capture01_scope.json"
OUTPUT = RAW + "native_capture01"
RUN_ID = "b4-recorder-9044ebbb-capture01"
SOURCE = "9044ebbb3cd3b2dbb7aa5984dd5ff23bfff697372f1f29d56693af9ea5eaf31a"
BOARD = "2629958581"
PREPARATION = RAW + "preparation.json"
LAYOUT = "state/analysis/P7_b4_recorder_decode_raw/layout01.json"
ADAPTER_ROOT = "/home/arduino/sumox26_codex_build/" + RUN_ID + "-adapter"
MANIFEST_SHA = "fc8e6fc1131c1952d5e1809f9dc6fb96763dd5e111749424e9ccfaec9b58d38c"
SCOPE_FILES = ["tools/capture_b4_recorder.py","state/analysis/P7_b4_recorder_run_raw/actions.py","state/analysis/P7_b4_recorder_run_raw/preparation.json","state/analysis/P7_b4_recorder_run_raw/derivation01.json","state/analysis/P7_b4_recorder_run_contract.md","tests/tooling/test_b4_recorder_run.py","state/analysis/P7_b4_recorder_run_raw/run_oracle01.json","state/reviews/P7_b4_recorder_run_review.md"]
PROVENANCE = ["state/analysis/P7_b4_app_compile_raw/inputs_static.json","state/analysis/P7_b4_app_compile_raw/native_static01/result.json","state/analysis/P7_b4_app_compile_raw/native_static01/artifacts.json","state/analysis/P7_b4_app_compile_raw/native_abi_static01/result.json","state/analysis/P7_b4_app_compile_raw/native_abi_static01/local_result.json","state/analysis/P7_b4_app_compile_raw/native_abi_static01/abi.json","state/analysis/P7_b4_app_compile_raw/native_entry_static01/result.json","state/analysis/P7_b4_app_compile_raw/native_entry_static01/local_result.json","state/analysis/P7_b4_app_compile_raw/native_entry_static01/entry.json","state/reviews/P7_b4_app_compile_actual_review.md","state/reviews/P7_b4_app_abi_actual_review.md","state/reviews/P7_b4_app_entry_actual_review.md","state/analysis/P7_b4_recorder_decode_raw/layout01.json","state/analysis/P7_b4_recorder_decode_contract.md","state/reviews/P7_b4_recorder_decode_review.md","state/analysis/P7_b4_recorder_capture_contract.md","state/analysis/P7_b4_recorder_capture_raw/plan01.json","state/analysis/P7_b4_recorder_capture_raw/derivation02.json","state/reviews/P7_b4_recorder_capture_review.md","state/analysis/P7_b4_recorder_run_raw/plan02.json"]
OLD_CALLER = "state/analysis/P7_ordinary_app_run_raw/run.py"
OLD_CALLER_SHA = "f48a8be9fa380a2a922613d188ae7622eafffdf3dc5fec12edc1372b4f7fc2d2"
ACTIONS_SHA = "59f1b3ba14e87796f5eafaa79f4da60e88c0d52560d8ba334ffb92fd7d18c336"


def _module(name, path, raw, **injected):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT / path)
    module.__dict__.update(injected)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


def _checked(path, digest):
    import stat
    target = ROOT / path
    for node in (target, *target.parents):
        info = node.lstat()
        plain = stat.S_ISREG if node == target else stat.S_ISDIR
        if not plain(info.st_mode) or getattr(info, "st_file_attributes", 0) & 1024:
            raise ValueError("Nonplain dependency: " + str(node))
    body = target.read_bytes()
    if hashlib.sha256(body).hexdigest() != digest:
        raise ValueError("Changed dependency: " + path)
    return body


actions = _module("_b4_recorder_actions", RAW + "actions.py",
                  _checked(RAW + "actions.py", ACTIONS_SHA))
_old_source = _checked(OLD_CALLER, OLD_CALLER_SHA)
_old_import = b"actions = _module('actions', RAW + 'actions.py', (ROOT / RAW / 'actions.py').read_bytes())"
if _old_source.count(_old_import) != 1:
    raise ValueError("D212 action injection seam changed")
_old_source = _old_source.replace(_old_import, b"actions = INJECTED_ACTIONS")
legacy = _module("_b4_recorder_d212", OLD_CALLER, _old_source, INJECTED_ACTIONS=actions)
PINS = dict(legacy.PINS, **{OLD_CALLER: OLD_CALLER_SHA})
PINS.update({"tools/" + name + ".py": pin[1] for name, pin in actions.HOST_INPUTS.items()})
helpers, compiler, current = legacy.helpers, legacy.compiler, legacy.current
STATIC, PROBE = legacy.STATIC, legacy.PROBE
BASELINE_LABELS, BASELINES = legacy.BASELINE_LABELS, legacy.BASELINES
safe_path, pinned_file = helpers.safe_path, helpers.pinned_file
canonical, sha, keys, require = helpers.canonical, helpers.sha, helpers.keys, helpers.require
decode, error_record = legacy.decode, legacy.error_record
native_arguments, command_record = legacy.native_arguments, legacy.command_record
ADB, ADB_SHA = legacy.ADB, legacy.ADB_SHA
for module in (legacy, legacy.legacy):
    module.__dict__.update(ROOT=ROOT, RAW=RAW, COMPILED=COMPILED, SCOPE=SCOPE,
        OUTPUT=OUTPUT, RUN_ID=RUN_ID, SOURCE=SOURCE, SCOPE_FILES=SCOPE_FILES,
        PINS=PINS, actions=actions, PREPARATION=PREPARATION, PROVENANCE=PROVENANCE,
        ADAPTER_ROOT=ADAPTER_ROOT, MANIFEST_SHA=MANIFEST_SHA)
legacy.legacy.CALLER_SHA = sha(Path(__file__).read_bytes())


class CaptureRun(legacy.InertRun):
    def __init__(self, reviewed_head, *, root=None):
        super().__init__(reviewed_head, root=root)
        self.retrieval_intent_ready = self.retrieval_started = False

    def load_scope(self):
        path = self.root / SCOPE
        safe_path(path)
        self.scope_raw = path.read_bytes()
        self.scope = decode(self.scope_raw, 65536)
        keys(self.scope, ("schema", "run_id", "board", "source_sha256",
                          "expected_identity", "files"))
        for name, expected in (("schema", "b4-recorder-native-scope-v1"),
                               ("run_id", RUN_ID), ("board", BOARD), ("source_sha256", SOURCE)):
            require(type(self.scope[name]) is str and self.scope[name] == expected,
                    "Wrong capture scope identity")
        keys(self.scope["files"], SCOPE_FILES)
        require(all(type(v) is str and re.fullmatch("[0-9a-f]{64}", v)
                    for v in self.scope["files"].values()), "Invalid scope pin")
        require(self.scope["files"]["tools/capture_b4_recorder.py"] ==
                legacy.legacy.CALLER_SHA, "Scope caller differs")
        require(actions.same(self.scope["expected_identity"], actions.EXPECTED_IDENTITY),
                "Wrong fixed board identity")
        self.expected_identity = copy.deepcopy(self.scope["expected_identity"])

    def load_inputs(self):
        self.fixed_pins = dict(PINS)
        self.fixed_bytes = {name: pinned_file(self.root, name, digest)
                            for name, digest in PINS.items()}
        raw = pinned_file(self.root, PREPARATION, self.scope["files"][PREPARATION])
        value = decode(raw, 65536)
        keys(value, ("schema", "run_id", "source_sha256", "bindings", "files"))
        require(value["schema"] == "b4-recorder-run-preparation-v1"
                and value["run_id"] == RUN_ID and value["source_sha256"] == SOURCE,
                "Wrong preparation identity")
        keys(value["files"], PROVENANCE)
        for name, pin in value["files"].items():
            keys(pin, ("bytes", "sha256"))
            body = pinned_file(self.root, name, pin["sha256"])
            require(type(pin["bytes"]) is int and 0 < pin["bytes"] == len(body),
                    "Wrong provenance size")
            self.fixed_bytes[name], self.fixed_pins[name] = body, pin["sha256"]
        keys(value["bindings"], ("capture",))
        self.bindings = copy.deepcopy(value["bindings"])
        self.check_bindings()
        self.load_source()
        self.check_evidence()
        self.load_baselines()

    def check_bindings(self):
        require(actions.same(self.bindings, {"capture": actions.BINDINGS}),
                "Wrong fixed capture-only bindings")
        require(actions.same(self.expected_identity, actions.EXPECTED_IDENTITY),
                "Capture boot/identity differs")

    def load_source(self):
        raw = self.fixed_bytes[COMPILED + "inputs_static.json"]
        require(sha(raw) == MANIFEST_SHA, "B4 manifest changed")
        value = decode(raw, 65536)
        keys(value, ("schema", "source_sha256", "boot_id", "files"))
        require(value["schema"] == "b4-app-m0-static-inputs-v1"
                and value["source_sha256"] == SOURCE
                and value["boot_id"] == self.expected_identity["boot_id"]
                and type(value["files"]) is dict and len(value["files"]) == 130,
                "B4 source identity differs")
        for name, digest in value["files"].items():
            self.fixed_bytes[name] = pinned_file(self.root, name, digest)
            self.fixed_pins[name] = digest
        owner = types.SimpleNamespace(root=self.root, base=current)
        names = self.source_inventory()
        self.source_hashes, source = legacy.diagnostic.CompileDiagnostic.source_mapping(
            owner, self.fixed_bytes, names)
        require(source == SOURCE, "Current source projection differs")
        sizes = {sha(raw): len(raw) for raw in self.fixed_bytes.values()}
        self.source_files = {name: dict(bytes=sizes[digest], sha256=digest)
                             for name, digest in self.source_hashes.items()}
        self.adapter_pin = dict(actions.ADAPTER_PIN)
        require(self.fixed_pins["tools/b4_recorder_capture.py"] == actions.ADAPTER_SHA,
                "Fixed adapter differs")

    def check_evidence(self):
        super().check_evidence()
        value = decode(self.fixed_bytes[COMPILED + "native_static01/result.json"], 1048576)
        require(value["schema"] == "b4-app-m0-static-compile-outcome-v1"
                and value["project"] == "app.ino"
                and value["fqbn"] == "arduino:zephyr:unoq:link_mode=static"
                and value["flags"] == "-DMATCH=0 -DMOTORS_ALLOWED=0 -DSUMOX_B4_STAND=1 -DSUMOX_P3_DRIVE_TEST=0 -DSUMOX_P3_TURN_TRIAL=0 -DSUMOX_P3_STOP_TRIAL=0 -DSUMOX_P4_REACTIVE=0 -DSUMOX_TIMING_EVIDENCE=0 -DSUMOX_P5_ABORT_TIMING=0 -DSUMOX_MOTOR_FAULT_PROBE=0", "Not the fixed inhibited B4 build")

    def prepare_commands(self):
        sources = {"helper": self.fixed_bytes[PROBE + "static_remote.py"],
                   "support": self.fixed_bytes[STATIC + "capture_remote.py"]}
        remote = {"capture": tuple(actions.build_capture_command(
                    sources, copy.deepcopy(self.bindings["capture"]))),
                  "retrieve": tuple(actions.build_retrieval_command(
                    sources["helper"], self.expected_identity))}
        self.commands = types.MappingProxyType(dict(remote))
        remote.update({label: tuple(receipt["argv"])
                       for label, receipt, unused in self.prerequisite_receipts})
        isolated = legacy.legacy.CAPABILITY_ARGV[:-1]
        remote["capabilities"] = isolated + (legacy.capability_program(
            sources["helper"], self.source_hashes, self.adapter_pin),)
        values = dict(BOOT=self.expected_identity["boot_id"], CLI=compiler.CLI,
                      CLI_SHA=compiler.CLI_SHA, REMOTE=ADAPTER_ROOT)
        claim = "\n".join(name + "=" + repr(value) for name, value in values.items())
        claim += "\n" + compiler.IDENTITY
        claim += "Path(REMOTE).mkdir(mode=0o700)\nprint(json.dumps(identity))\n"
        remote["adapter-claim"] = isolated + (claim,)
        self.push_arguments = ("push", str(self.root / "tools/b4_recorder_capture.py"),
                               actions.ADAPTER)
        self.all_commands = types.MappingProxyType(remote)
        self.timeouts = types.MappingProxyType({**{name: 630 if name == "capture" else 60
                                                  for name in remote}, "adapter-push": 60})
        self.command_records = {name: command_record(argv, self.timeouts[name])
                                for name, argv in remote.items()}
        self.command_records["adapter-push"] = dict(
            argv_sha256=sha(canonical(list(self.push_arguments))), timeout=60)
        allowed = {(native_arguments(argv), self.timeouts[name], name)
                   for name, argv in remote.items()}
        allowed.add((self.push_arguments, 60, "adapter-push"))
        self.allowed = frozenset(allowed)
        require(len(self.allowed) == 7, "Wrong fixed capture allowlist")
        self.input_state = self.state_bytes()

    def claim(self):
        require(self.admitted and not self.claim_started, "Missing admission/repeated claim")
        self.claim_started = True
        self.local()
        require(not os.path.lexists(self.output), "Host attempt already consumed")
        self.output.mkdir(mode=0o700)
        info = self.output.stat()
        self.output_identity = (info.st_dev, info.st_ino)
        self.claimed = True
        inputs = {**self.scope["files"], **self.fixed_pins, SCOPE: sha(self.scope_raw),
                  ADB: ADB_SHA}
        self.write("inputs.json", {**self.identity_record(), "input_hashes": inputs,
                   "commands": self.command_records,
                   "remote_evidence": {"capture": self.bindings["capture"]["output"]}})
        self.claim_ready = True

    def transport(self, arguments, timeout, label):
        require(type(self.counter) is int and self.counter < 10, "Capture transport bound")
        limit = 2 if label in (*BASELINE_LABELS, "capabilities") else 1
        require(self.command_counts.get(label, 0) < limit, "Capture command already consumed")
        if label == "retrieve":
            require(self.retrieval_intent_ready and self.retrieval_started,
                    "Retrieval lacks consumed intent")
        return super().transport(arguments, timeout, label)

    def intent(self, action, predecessor):
        require(action == "capture" and predecessor is None and self.stage_ready,
                "Only staged capture without predecessor is permitted")
        require(self.claim_ready and not self.intent_actions and not self.dispatched_actions,
                "Missing claim or repeated capture intent")
        self.local()
        self.write("capture_attempt.json", {**self.identity_record(), "action": "capture",
                   "command": self.command_records["capture"], "predecessor_sha256": None})
        self.intent_actions.add("capture")

    def retrieval_intent(self, reply):
        require(not self.retrieval_intent_ready and not self.retrieval_started
                and self.dispatched_actions == {"capture"}, "Wrong retrieval order")
        actions.validate_capture_reply(reply)
        require(sha(canonical(reply)) == self.reply_hashes.get("capture"),
                "Retrieval predecessor differs from returned capture")
        self.local()
        self.write("retrieve_attempt.json", {**self.identity_record(),
                   "command": self.command_records["retrieve"],
                   "capture_sha256": sha(canonical(reply))})
        self.retrieval_intent_ready = True

    def retrieve(self):
        require(self.retrieval_intent_ready and not self.retrieval_started,
                "Missing or consumed retrieval intent")
        self.local()
        self.retrieval_started = True
        return self.query("retrieve", 1048576)

    def check_counters(self, result):
        require(type(self.counter) is int and self.counter == self.transport_calls <= 10,
                "Transport counter differs")
        require(self.dispatched_actions <= self.intent_actions <= {"capture"},
                "Invalid capture action set")
        if result["status"] == "COMPLETED":
            expected = {name: 2 for name in (*BASELINE_LABELS, "capabilities")}
            expected.update({name: 1 for name in ("adapter-claim", "adapter-push",
                                                 "capture", "retrieve")})
            require(self.counter == 10 and self.command_counts == expected
                    and self.stage_ready and self.stage_intent_ready
                    and self.stage_claim_verified
                    and self.stage_dispatches == {"adapter-claim", "adapter-push"}
                    and self.intent_actions == self.dispatched_actions == {"capture"}
                    and self.retrieval_intent_ready and self.retrieval_started,
                    "Incomplete successful capture dispatch set")
            require(type(result["capture_attempts"]) is int and result["capture_attempts"] == 1
                    and type(result["retrieval_attempts"]) is int
                    and result["retrieval_attempts"] == 1, "Wrong capture attempt counts")
            require(not (self.local_errors or self.prerequisite_errors or self.transport_errors),
                    "Successful diagnostics contain errors")

    def write_bytes(self, name, raw):
        require(type(name) is str and re.fullmatch("[A-Za-z0-9_.-]+", name)
                and type(raw) is bytes, "Invalid local output")
        self.check_output()
        with (self.output / name).open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        self.check_output()

    def export_bundle(self, packet, reply):
        returned = actions.canonical(reply)
        decoded = actions.decode_retrieval(packet, returned_raw=returned,
                                           layout_raw=self.fixed_bytes[LAYOUT])
        self.write_bytes("capture_envelope.json", returned)
        for name, raw in decoded["raw_files"].items():
            self.write_bytes(name, raw)
        csv = decoded["decoder"]["csv"] if decoded["decoder"] is not None else {}
        if decoded["decoder"] is not None and decoded["decoder"]["export_status"] == "PASS":
            require(set(csv) == {"frames", "events", "summary"}
                    and all(type(v) is bytes for v in csv.values()), "Incomplete decoder CSV")
            for name, raw in csv.items():
                self.write_bytes(name + ".csv", raw)
        summary = _export_summary(decoded)
        self.write("export.json", summary)
        self.local()
        return summary

    def run(self):
        require(not self.run_started, "Run already consumed")
        self.run_started = True
        self.admit()
        self.claim()
        result = {"schema": "b4-recorder-sequence-v1", "status": "FAILED", "capture": None,
                  "capture_attempts": 0, "retrieval_attempts": 0, "export": None,
                  "first_error": None, "postcheck_errors": []}
        packet = None
        try:
            self.stage()
            self.local()
            self.prerequisites()
            self.intent("capture", None)
            result["capture_attempts"] += 1
            result["capture"] = self.action("capture")
            actions.validate_capture_reply(result["capture"])
            self.retrieval_intent(result["capture"])
            result["retrieval_attempts"] += 1
            packet = self.retrieve()
        except Exception as error:
            _remember(result, error)
        for name in ("local", "prerequisites"):
            try:
                getattr(self, name)()
            except Exception as error:
                _remember(result, error, name)
        if result["first_error"] is None:
            try:
                result["export"] = self.export_bundle(packet, result["capture"])
                require(result["export"]["bundle_status"] == "PASS", "Local bundle refused")
                result["status"] = "COMPLETED"
            except Exception as error:
                _remember(result, error, "export")
        self.finish(result)
        return result


def _remember(result, error, check=None):
    if result["first_error"] is None:
        result["first_error"] = error_record(error)
    if check is not None:
        result["postcheck_errors"].append(dict(check=check, **error_record(error)))


def _reference(body, **location):
    return dict(location, bytes=len(body), sha256=sha(body))


def _export_summary(decoded):
    result = {key: copy.deepcopy(value) for key, value in decoded.items()
              if key not in ("raw_returned", "raw_layout", "raw_files", "raw_owner", "decoder")}
    result["raw_returned"] = _reference(decoded["raw_returned"], file="capture_envelope.json")
    result["raw_layout"] = _reference(decoded["raw_layout"], source=LAYOUT)
    result["raw_files"] = {name: _reference(body, file=name)
                           for name, body in decoded["raw_files"].items()}
    chunks = ["{:02d}-owner.{}.bin".format(i + 8, i) for i in range(10)]
    result["raw_owner"] = None if decoded["raw_owner"] is None else _reference(
        decoded["raw_owner"], chunks=chunks)
    nested = decoded["decoder"]
    if nested is not None:
        nested = {key: copy.deepcopy(value) for key, value in nested.items()
                  if key not in ("raw_owner", "csv")}
        nested["raw_owner"] = result["raw_owner"]
        nested["csv"] = {name: None if body is None else _reference(body, file=name + ".csv")
                         for name, body in decoded["decoder"]["csv"].items()}
    result["decoder"] = nested
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description="One fixed B4 recorder capture", allow_abbrev=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check-only", action="store_true")
    group.add_argument("--execute", action="store_true")
    parser.add_argument("--reviewed-head", required=True)
    args = parser.parse_args(argv)
    if not re.fullmatch("[0-9a-f]{40}", args.reviewed_head):
        parser.error("--reviewed-head must be forty lowercase hexadecimal characters")
    try:
        owner = CaptureRun(args.reviewed_head)
        if args.check_only:
            owner.admit()
            return 0
        return 0 if owner.run()["status"] == "COMPLETED" else 1
    except Exception as error:
        print(json.dumps(error_record(error), sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
