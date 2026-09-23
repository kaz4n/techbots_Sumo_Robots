"""Supply D096's approved additions to the unchanged D093 config registry test.

The frozen runtime contract supplies literals; config.h is checked, not an oracle.
Negative copied profiles retain all legacy assertions and make each value drift.
"""
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import time
import unittest
from unittest import mock

from . import test_p0_config as legacy
from . import test_power_inputs as power_inputs


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "state/analysis/P2_pin_table_raw"
# D096: contract 'Actual release grid' and 'Per-epoch acquisition', plus D-096.
# These are literal approved expectations, not values parsed from config.h.
D096_DEFAULTS = {
    "APP_QTR_SERVICE_US": 600,
    "APP_SERVICE_MAX_PASSES": 8192,
    "APP_CLOCK_STALL_MAX_POLLS": 65536,
}
METHOD = "test_additive_config_registry_preserves_all_existing_assertions"
FROZEN = (
    "tests/tooling/test_runtime_config_registry.py",
    "tests/tooling/test_power_inputs.py",
    "tests/tooling/test_dump_match.py",
    "tests/tooling/test_p0_config.py",
    "state/analysis/P2_app_runtime_contract.md",
    "src/config.h",
)


def hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in FROZEN}


def receipt(record):
    RAW.mkdir(parents=True, exist_ok=True)
    with (RAW / "registry_cases.jsonl").open("a", encoding="utf-8") as output:
        output.write(json.dumps({"time_ns": time.time_ns(), **record}) + "\n")


class RuntimeConfigRegistryTests(unittest.TestCase):
    def run_registry(self, label, project=ROOT, expected_failure=False):
        before = hashes()
        original_registry = legacy.BEHAVIOR_EXTRA_DEFAULTS.copy()
        with tempfile.TemporaryDirectory(prefix="sumox_d106_registry_receipt_") as temporary:
            with ExitStack() as patches:
                patches.enter_context(mock.patch.dict(legacy.BEHAVIOR_EXTRA_DEFAULTS,
                                                      D096_DEFAULTS))
                patches.enter_context(mock.patch.object(legacy, "PROJECT", project))
                patches.enter_context(mock.patch.object(power_inputs, "RAW", Path(temporary)))
                case = power_inputs.PowerInputsTests(METHOD)
                error = None
                try:
                    # This Python-only method needs none of its class's native build setup.
                    getattr(case, METHOD)()
                except AssertionError as caught:
                    error = str(caught)
                nested = json.loads((Path(temporary) / "registry.jsonl").read_text())
            receipt({"profile": label, "approved_defaults": D096_DEFAULTS,
                     "expected_failure": expected_failure, "assertion": error,
                     "nested_d093_receipt": nested, "before_sha256": before,
                     "after_sha256": hashes()})
        self.assertEqual(before, hashes(), "Registry execution changed source files")
        self.assertEqual(legacy.BEHAVIOR_EXTRA_DEFAULTS, original_registry)
        self.assertEqual(nested["tests_run"], 1)
        if expected_failure:
            self.assertIsNotNone(error)
            self.assertFalse(nested["success"])
            self.assertIn("Ran 18 tests", error)
            self.assertIn("test_explicit_behavior_text_defaults_match_spec", error)
            self.assertIn("FAILED (failures=1)", error)
            self.assertNotIn("ERROR", error)
        else:
            self.assertIsNone(error, error)
            self.assertTrue(nested["success"], nested["output"])

    def test_d096_additions_run_unchanged_d093_and_all_18_legacy_config_checks(self):
        self.run_registry("approved-D096-defaults")

    def test_each_wrong_value_is_rejected_by_unchanged_legacy_value_assertion(self):
        with tempfile.TemporaryDirectory(prefix="sumox_d106_registry_profiles_") as temporary:
            project = Path(temporary)
            (project / "docs").mkdir()
            (project / "src").mkdir()
            shutil.copyfile(ROOT / "docs/BEHAVIOR.md", project / "docs/BEHAVIOR.md")
            original = (ROOT / "src/config.h").read_text(encoding="utf-8")
            for name, approved in D096_DEFAULTS.items():
                with self.subTest(constant=name):
                    changed, count = re.subn(r"(\b" + name + r"\s*=\s*)[^;]+;",
                                            r"\g<1>" + str(approved + 1) + "U;", original)
                    self.assertEqual(count, 1)
                    (project / "src/config.h").write_text(changed, encoding="utf-8")
                    self.run_registry(name + "-wrong-value", project, expected_failure=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
