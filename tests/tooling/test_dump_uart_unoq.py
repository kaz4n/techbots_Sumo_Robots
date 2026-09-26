# Runs contract-derived D090 native UART tests against observed register substitutes.
# Keeps implementation unread by the test author and preserves every command outcome.
# Normal and sanitizer subprocesses isolate boot-lifetime native ownership state.
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/dump_uart_native"
RAW = ROOT / "state/analysis/P2_dump_raw/author"


class NativeDumpTests(unittest.TestCase):
    @classmethod
    def command(cls, command):
        outcome = subprocess.run(list(map(str, command)), capture_output=True, text=True, timeout=45)
        record = {"time_ns": time.time_ns(), "command": list(map(str, command)),
                  "returncode": outcome.returncode, "stdout": outcome.stdout, "stderr": outcome.stderr}
        with (RAW / "native_commands.jsonl").open("a") as stream:
            stream.write(json.dumps(record) + "\n")
        return outcome

    @classmethod
    def setUpClass(cls):
        if shutil.which("g++") is None:
            raise unittest.SkipTest("Run native substitutions with Linux/WSL g++.")
        RAW.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="sumo-dump-native-")
        cls.addClassCleanup(cls.temp.cleanup)
        cls.stage = Path(cls.temp.name)
        files = [ROOT / "src/hal/dump_uart_unoq.h", ROOT / "state/analysis/P2_dump_native_contract.md"]
        files += sorted(path for path in FIXTURE.rglob("*") if path.is_file())
        with (RAW / "native_freeze.jsonl").open("a") as stream:
            stream.write(json.dumps({"time_ns": time.time_ns(), "basis": "public contract and installed headers",
                "sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in files}}) + "\n")
        base = ["g++", "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                "-fno-exceptions", "-fno-rtti", "-DARDUINO_ARCH_ZEPHYR", "-DCONFIG_UART_INTERRUPT_DRIVEN",
                "-I", FIXTURE, "-I", ROOT / "src"]
        syntax = cls.command([*base, "-fsyntax-only", FIXTURE / "cases.cc"])
        if syntax.returncode: raise AssertionError(syntax.stderr)
        cls.binaries = []
        for name, flags in (("normal", []), ("san", ["-fsanitize=address,undefined",
                            "-fno-omit-frame-pointer", "-fno-pie", "-no-pie"])):
            executable = cls.stage / name
            built = cls.command([*base, *flags, FIXTURE / "cases.cc",
                                 ROOT / "src/hal/dump_uart_unoq.cpp", "-o", executable])
            if built.returncode: raise AssertionError(built.stderr)
            cls.binaries.append(executable)

    def run_cases(self, cases):
        for executable in self.binaries:
            for case in cases:
                with self.subTest(variant=executable.name, case=case):
                    result = self.command([executable, *case])
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exact_messagepack_packets_and_primask_preservation(self):
        self.run_cases([("happy", size) for size in (1, 31, 32, 63, 64)] +
                       [("happy", 64, "masked")])

    def test_setup_grants_and_thread_privilege_refuse_before_io(self):
        self.run_cases([("grant", index) for index in range(6)])

    def test_ready_low_error_and_setup_api_errors(self):
        self.run_cases([("ready", index) for index in range(4)])

    def test_txe_low_and_mid_call_partial_progress_stay_pending(self):
        self.run_cases([("pending", 0), ("pending", 1)])

    def test_tc_pending_does_not_acknowledge_submission(self):
        self.run_cases([("tc",)])

    def test_packet_deadline_adjacent_values_and_wrap(self):
        self.run_cases([("timeout", delta) for delta in (99999, 100000, 100001)] +
                       [("timeout", delta, "wrap") for delta in (99999, 100000, 100001)])

    def test_invalid_payloads_and_pending_identity_changes(self):
        self.run_cases([("payload", index) for index in range(7)])

    def test_live_register_context_dma_irq_and_metadata_corruption(self):
        self.run_cases([("corruption", index) for index in range(21)])

    def test_partial_cancel_poison_and_foreign_context_no_register_write(self):
        self.run_cases([("cancel", 0), ("cancel", 1)])

    def test_step_clock_budget_stops_before_any_late_submission(self):
        self.run_cases([("budget", increment) for increment in (0, 1, 40, 79, 80, 81)])

    def test_initial_clock_metadata_and_baud_corruption_refuse(self):
        self.run_cases([("metadata", index) for index in range(16)])

    def test_first_failure_progress_cleanup_and_terminal_retention(self):
        self.run_cases([("first_failure", index) for index in range(6)])


if __name__ == "__main__":
    unittest.main()
