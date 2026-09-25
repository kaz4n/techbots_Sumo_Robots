# Tests the D177 bounded base85 fallback from public contract commit 2ac0f702.
# Keeps the original frozen oracle unchanged and checks both transport forms.
# Run only after source/oracle freeze with Linux Python -B; no native process runs.
"""Additive independent oracle; no subject source inspected during authorship.

The frozen test_inert_actions fixture utilities provide inert module execution.
Expected tokens, compression, Windows quoting and sizes are computed separately
from the public BOOTSTRAP string and specified command prefix.
"""

import base64
import bz2
import copy
import random
import shlex
import subprocess
import unittest
from unittest import mock

import test_inert_actions as original


PREFIX = ["/usr/bin/env", "-i", "HOME=/home/arduino", "USER=arduino", "LOGNAME=arduino",
          "PATH=/usr/bin:/bin", "LANG=C", "LC_ALL=C", "/usr/bin/python3", "-I", "-B", "-c"]
B85_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"


def encoded(raw, codec):
    compressed = bz2.compress(raw, compresslevel=9)
    if codec == "base64":
        return base64.b64encode(compressed).decode("ascii")
    return "b85:" + base64.b85encode(compressed).decode("ascii")


def windows_argv(remote):
    return [original.ADB, "-s", "2629958581", "shell", "-T", shlex.join(remote)]


def windows_units(remote):
    return len(subprocess.list2cmdline(windows_argv(remote)).encode("utf-16-le")) // 2


class D177EncodingOracle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        original.D177Oracle.setUpClass.__func__(cls)
        cls._boundary_cache = None
        rng = random.Random(2177)
        cls.noise = "".join(rng.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                            for _ in range(64000)).encode("ascii")

    def setUp(self):
        self.process_guard = mock.patch.object(subprocess, "Popen", side_effect=AssertionError("no subprocess"))
        self.process_guard.start()
        self.addCleanup(self.process_guard.stop)

    def expected_command(self, action, raw, codec):
        return PREFIX + [self.subject.BOOTSTRAP, action, original.digest(raw), encoded(raw, codec)]

    def fixture(self, length, action="upload"):
        sources = original.inline_sources(action)
        sources["helper"] += b"#" + self.noise[:length] + b"\n"
        bindings = original.binding(action)
        raw = original.canonical(original.payload(action, sources, bindings))
        return {"sources": sources, "bindings": bindings, "raw": raw,
                "base64": self.expected_command(action, raw, "base64"),
                "base85": self.expected_command(action, raw, "base85")}

    def boundary(self):
        if self.__class__._boundary_cache is not None:
            return self.__class__._boundary_cache
        low, high = 0, len(self.noise)
        self.assertLessEqual(windows_units(self.fixture(low)["base64"]), 30000,
                             "small contract command must fit")
        self.assertGreater(windows_units(self.fixture(high)["base64"]), 30000)
        while high - low > 1:
            middle = (low + high) // 2
            if windows_units(self.fixture(middle)["base64"]) <= 30000:
                low = middle
            else:
                high = middle
        small, fallback = self.fixture(low), self.fixture(high)
        self.assertLessEqual(windows_units(small["base64"]), 30000)
        self.assertGreater(windows_units(fallback["base64"]), 30000)
        self.assertLessEqual(windows_units(fallback["base85"]), 30000)
        self.__class__._boundary_cache = small, fallback
        return small, fallback

    def build(self, fixture, action="upload"):
        return self.subject.build_command(action, fixture["sources"], fixture["bindings"])

    def accepted(self, action, raw=None, codec="base85"):
        harness = original.BootstrapHarness(self.subject, action)
        raw = original.canonical(original.payload(action)) if raw is None else raw
        value = original.D177Oracle.output(self, harness, raw=raw, token=encoded(raw, codec))
        return harness, value

    def denied(self, *, raw=None, token=None, sha=None, bytecode=False):
        harness = original.BootstrapHarness(self.subject, "upload")
        raw = original.canonical(original.payload("upload")) if raw is None else raw
        token = encoded(raw, "base85") if token is None else token
        text, error = harness.run(raw=raw, token=token, sha=sha, bytecode=bytecode)
        self.assertIsNotNone(error)
        self.assertEqual(text, "")
        self.assertEqual(harness.events, [], "framing/admission failure must precede source execution")

    def test_small_commands_keep_exact_existing_base64_framing(self):
        for action in ("upload", "capture"):
            with self.subTest(action=action):
                fixture = self.fixture(0, action)
                actual = self.build(fixture, action)
                self.assertEqual(actual, fixture["base64"])
                self.assertFalse(actual[-1].startswith("b85:"))
                self.assertLessEqual(windows_units(actual), 30000)

    def test_last_fitting_default_stays_base64_and_over_limit_switches(self):
        small, fallback = self.boundary()
        self.assertEqual(self.build(small), small["base64"])
        actual = self.build(fallback)
        self.assertEqual(actual, fallback["base85"])
        self.assertLessEqual(windows_units(actual), 30000)

    def test_trigger_uses_full_windows_command_including_adb_and_quoting(self):
        _, fallback = self.boundary()
        remote = fallback["base64"]
        # The remote shell command alone still fits; the actual Windows argv does not.
        self.assertLessEqual(len(shlex.join(remote).encode("utf-16-le")) // 2, 30000)
        self.assertGreater(windows_units(remote), 30000)
        self.assertEqual(self.build(fallback), fallback["base85"])
        self.assertEqual(windows_argv(remote)[:5], [original.ADB, "-s", "2629958581", "shell", "-T"])

    def test_fallback_keeps_same_compressed_payload_sha_and_all_other_arguments(self):
        _, fallback = self.boundary()
        before = copy.deepcopy((fallback["sources"], fallback["bindings"]))
        actual = self.build(fallback)
        self.assertEqual((fallback["sources"], fallback["bindings"]), before)
        self.assertEqual(actual[:-1], fallback["base64"][:-1])
        compressed = base64.b85decode(actual[-1][4:].encode("ascii"))
        self.assertEqual(compressed, base64.b64decode(fallback["base64"][-1], validate=True))
        self.assertEqual(compressed, bz2.compress(fallback["raw"], compresslevel=9))
        self.assertEqual(bz2.decompress(compressed), fallback["raw"])
        self.assertEqual(actual[-2], original.digest(fallback["raw"]))
        self.assertEqual(actual[-1], "b85:" + base64.b85encode(compressed).decode("ascii"))

    def test_fallback_metacharacters_survive_shell_and_windows_quoting_as_one_token(self):
        _, fallback = self.boundary()
        actual = self.build(fallback)
        token = actual[-1]
        self.assertTrue(set("$&;|<>`()") <= set(token))
        shell_command = shlex.join(actual)
        self.assertEqual(shlex.split(shell_command), actual)
        self.assertEqual(shlex.split(shell_command)[-1], token)
        line = subprocess.list2cmdline(windows_argv(actual))
        self.assertEqual(windows_units(actual), len(line.encode("utf-16-le")) // 2)
        self.assertLessEqual(windows_units(actual), 30000)

    def test_both_encodings_too_long_reject_without_relaxing_payload_bound(self):
        fixture = self.fixture(len(self.noise))
        self.assertLessEqual(len(fixture["raw"]), 196608)
        self.assertGreater(windows_units(fixture["base64"]), 30000)
        self.assertGreater(windows_units(fixture["base85"]), 30000)
        with self.assertRaises(ValueError):
            self.build(fixture)

    def test_both_canonical_forms_dispatch_upload_with_same_compact_receipt(self):
        values = []
        for codec in ("base64", "base85"):
            with self.subTest(codec=codec):
                harness, value = self.accepted("upload", codec=codec)
                values.append(value)
                self.assertEqual(value["report"], original.upload_report())
                self.assertEqual(value["full_result_sha256"], original.digest(original.canonical(original.upload_report(True))))
                self.assertEqual(sum(e[0] == "upload" for e in harness.events), 1)
                self.assertFalse(any(e[0] in ("open", "capture") for e in harness.events))
        self.assertEqual(values[0], values[1])

    def test_both_canonical_forms_dispatch_capture_with_all_installed_postchecks(self):
        values = []
        for codec in ("base64", "base85"):
            with self.subTest(codec=codec):
                harness, value = self.accepted("capture", codec=codec)
                values.append(value)
                self.assertEqual(value, original.envelope("capture", harness.report))
                self.assertEqual([e[1] for e in harness.events if e[0] == "read"],
                                 [p[0] for p in original.MODULE_PINS] * 2)
                self.assertEqual(sum(e[0] == "capture" for e in harness.events), 1)
                self.assertEqual(harness.events[-1], ("close", 781))
        self.assertEqual(values[0], values[1])

    def test_actual_fallback_token_is_executable_with_inert_sources(self):
        _, fallback = self.boundary()
        actual = self.build(fallback)
        harness = original.BootstrapHarness(self.subject, "upload")
        value = original.D177Oracle.output(self, harness, raw=fallback["raw"], token=actual[-1], sha=actual[-2])
        self.assertEqual(value["report"], original.upload_report())
        self.assertEqual(sum(e[0] == "upload" for e in harness.events), 1)

    def test_base85_requires_exact_prefix_and_valid_ascii_alphabet(self):
        good = encoded(original.canonical(original.payload("upload")), "base85")
        body = good[4:]
        bad_tokens = ["b85:", "b85:a", "B85:" + body, "base85:" + body, body,
                      "b85:b85:" + body, " " + good, good + "\n", good + " ", good + "\t"]
        bad_tokens.extend("b85:" + body[:10] + bad + body[10:] for bad in ("/", ":", "'", '"', "\\", "[", "]", "\u00e9"))
        for token in bad_tokens:
            with self.subTest(token_tail=token[-12:]):
                self.denied(token=token)

    def test_base85_rejects_noncanonical_tail_that_decodes_to_identical_bytes(self):
        alias = None
        for padding in range(32):
            value = original.payload("upload")
            value["bindings"]["opaque"]["padding"] = "x" * padding
            raw = original.canonical(value)
            compressed = bz2.compress(raw, compresslevel=9)
            body = base64.b85encode(compressed).decode("ascii")
            if len(body) % 5 == 0:
                continue
            for last in B85_ALPHABET:
                candidate = body[:-1] + last
                if candidate == body:
                    continue
                try:
                    matches = base64.b85decode(candidate) == compressed
                except ValueError:
                    matches = False
                if matches:
                    alias = raw, "b85:" + candidate
                    break
            if alias is not None:
                break
        self.assertIsNotNone(alias, "fixture needs a noncanonical base85 final-group alias")
        self.denied(raw=alias[0], token=alias[1])

    def test_base85_one_bounded_bz2_member_no_trailing_or_concatenated_data(self):
        raw = original.canonical(original.payload("upload"))
        compressed = bz2.compress(raw, compresslevel=9)
        for malformed in (compressed[:-1], compressed + b"tail", compressed + bz2.compress(b"{}\n"),
                          compressed + b"\x00", b"not a bz2 member"):
            with self.subTest(length=len(malformed)):
                self.denied(raw=raw, token="b85:" + base64.b85encode(malformed).decode("ascii"))

    def test_base85_decompression_exact_payload_limit_and_one_byte_over(self):
        sources = original.inline_sources("upload")
        sources["helper"] += b"#"
        sources["helper"] += b"x" * (196608 - len(original.canonical(original.payload("upload", sources))))
        raw = original.canonical(original.payload("upload", sources))
        self.assertEqual(len(raw), 196608)
        harness, value = self.accepted("upload", raw=raw)
        self.assertEqual(value["report"], original.upload_report())
        self.assertEqual(sum(e[0] == "upload" for e in harness.events), 1)
        sources["helper"] += b"x"
        too_long = original.canonical(original.payload("upload", sources))
        self.assertEqual(len(too_long), 196609)
        self.denied(raw=too_long)

    def test_base85_payload_and_inline_hash_failures_precede_all_execution(self):
        self.denied(sha="0" * 64)
        for role in ("helper", "support", "upload"):
            value = original.payload("upload")
            value["sources"][role]["sha256"] = "0" * 64
            with self.subTest(role=role):
                self.denied(raw=original.canonical(value))

    def test_base85_duplicate_nonfinite_and_closed_shape_checks_are_unchanged(self):
        raw = original.canonical(original.payload("upload"))
        self.denied(raw=b'{"run_id":"duplicate",' + raw[1:])
        for token in (b"NaN", b"Infinity", b"-Infinity"):
            with self.subTest(number=token):
                self.denied(raw=raw.replace(b'"opaque":{', b'"opaque":{"nonfinite":' + token + b','))
        value = original.payload("upload")
        value["extra"] = "rejected"
        self.denied(raw=original.canonical(value))
        value = original.payload("upload")
        value["bindings"]["run_id"] = "wrong"
        self.denied(raw=original.canonical(value))

    def test_base85_active_bytecode_setting_must_still_be_true(self):
        self.denied(bytecode=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
