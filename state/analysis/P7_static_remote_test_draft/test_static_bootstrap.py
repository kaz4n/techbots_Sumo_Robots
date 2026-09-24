# Tests the public fixed bootstrap using synthetic helper bytes only.
# Keeps framing, raw-byte authority and execution boundaries independent of H.
# Draft: do not execute until the coordinator freezes and authorizes this suite.
import base64
import contextlib
import hashlib
import io
import json
from pathlib import Path
import random
import sys
import traceback
import unittest
from unittest import mock
import zlib


TEMPLATE_SHA256 = "a6bb46737bea18fc564e77bbd7124c20771258b4fe4ca41a17cbd4cce9798419"
TOKEN = "@HELPER_SHA256@"
HELPER_MAX_BYTES = 98_304
MARKER = b"print('SYNTHETIC_HELPER_EXECUTED')\n"
TEMPLATE_PATH = (
    Path(__file__).resolve().parents[1]
    / "P7_static_link_probe_raw"
    / "static_bootstrap.txt"
)


def frame(raw, level=9):
    return base64.b64encode(zlib.compress(raw, level)).decode("ascii")


class StaticBootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[3]
        freeze_path = Path(__file__).with_name('freeze_remote.json')
        freeze = json.loads(freeze_path.read_text(encoding='utf-8'))
        if freeze.get('status') != 'FROZEN_FOR_AUTHORIZED_HOST_TEST':
            raise RuntimeError('Remote/bootstrap tests have not been frozen')
        for relative, expected in freeze['inputs_sha256'].items():
            if hashlib.sha256((root / relative).read_bytes()).hexdigest() != expected:
                raise RuntimeError('Frozen bootstrap input changed: ' + relative)
        raw = TEMPLATE_PATH.read_bytes()
        if hashlib.sha256(raw).hexdigest() != TEMPLATE_SHA256:
            raise AssertionError("The reviewed public bootstrap template changed")
        cls.template = raw.decode("utf-8")
        if cls.template.count(TOKEN) != 1:
            raise AssertionError("Expected exactly one literal helper-hash token")

    def invoke_argv(self, argv, pin):
        self.assertEqual(len(pin), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in pin))
        rendered = self.template.replace(TOKEN, pin)
        namespace = {"__name__": "bootstrap_test", "BOOTSTRAP_SENTINEL": object()}
        vector = list(argv)
        stdout, stderr = io.StringIO(), io.StringIO()
        caught = None
        with mock.patch.object(sys, "argv", vector):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                try:
                    exec(compile(rendered, "<reviewed-bootstrap>", "exec"), namespace)
                except Exception as error:
                    caught = error
        return {
            "error": caught,
            "stdout": stdout.getvalue(),
            "stderr": stderr.getvalue(),
            "argv": vector,
            "namespace": namespace,
        }

    def invoke(self, raw, *, encoded=None, pin=None, trailing=None):
        if encoded is None:
            encoded = frame(raw)
        if pin is None:
            pin = hashlib.sha256(raw).hexdigest()
        if trailing is None:
            trailing = ["inventory", "0123456789abcdef" * 2]
        return self.invoke_argv(["-c", encoded] + list(trailing), pin)

    def assert_rejected(self, result, original_argv):
        self.assertIsNotNone(result["error"])
        self.assertEqual(result["stdout"], "")
        self.assertEqual(result["stderr"], "")
        self.assertEqual(result["argv"], original_argv)
        self.assertNotIn("SYNTHETIC_HELPER_EXECUTED", result["stdout"])

    def reject_encoded(self, encoded, raw=MARKER, **kwargs):
        trailing = ["inventory", "0123456789abcdef" * 2]
        result = self.invoke(raw, encoded=encoded, trailing=trailing, **kwargs)
        self.assert_rejected(result, ["-c", encoded] + trailing)
        return result

    def test_canonical_level9_frame_executes_hash_pinned_source(self):
        result = self.invoke(MARKER)
        self.assertIsNone(result["error"])
        self.assertEqual(result["stdout"], "SYNTHETIC_HELPER_EXECUTED\n")
        self.assertEqual(result["stderr"], "")

    def test_removes_only_hz_and_preserves_every_other_argument(self):
        raw = b"import json, sys\nprint(json.dumps(sys.argv))\n"
        trailing = ["layout", "f" * 32, "", "space and 'quotes'", "\\", "\u03bb"]
        result = self.invoke(raw, trailing=trailing)
        self.assertIsNone(result["error"])
        self.assertEqual(json.loads(result["stdout"]), ["-c"] + trailing)
        self.assertEqual(result["argv"], ["-c"] + trailing)

    def test_fresh_main_namespace_has_no_bootstrap_globals(self):
        raw = (
            b"initial_names = sorted(globals())\n"
            b"import json\n"
            b"print(json.dumps([__name__, initial_names]))\n"
        )
        result = self.invoke(raw)
        self.assertIsNone(result["error"])
        self.assertEqual(
            json.loads(result["stdout"]),
            ["__main__", ["__builtins__", "__name__"]],
        )
        self.assertNotIn("initial_names", result["namespace"])

    def test_missing_hz_remains_an_uncaught_command_failure(self):
        result = self.invoke_argv(["-c"], hashlib.sha256(MARKER).hexdigest())
        self.assert_rejected(result, ["-c"])
        self.assertIsInstance(result["error"], ValueError)

    def test_malformed_and_whitespace_base64_rejected(self):
        valid = frame(MARKER)
        for encoded in ["!", "a", valid + "\n", " " + valid, valid + "\t", "\u00e9"]:
            with self.subTest(encoded=encoded):
                self.reject_encoded(encoded)

    def test_noncanonical_pad_bits_rejected_before_zlib(self):
        # Both strings decode to b'x'; only eA== has zero unused pad bits.
        self.assertEqual(base64.b64decode("eA=="), base64.b64decode("eB=="))
        result = self.reject_encoded("eB==")
        self.assertIsInstance(result["error"], ValueError)
        self.assertIn("Noncanonical", str(result["error"]))

    def test_missing_and_extra_padding_rejected(self):
        for encoded in ["eA", "eA=", "eA===", "eA===="]:
            with self.subTest(encoded=encoded):
                self.reject_encoded(encoded)

    def test_empty_base64_is_not_a_complete_zlib_stream(self):
        self.reject_encoded("")

    def test_raw_deflate_and_gzip_are_not_rfc1950(self):
        for window_bits in [-zlib.MAX_WBITS, zlib.MAX_WBITS + 16]:
            with self.subTest(window_bits=window_bits):
                compressor = zlib.compressobj(level=9, wbits=window_bits)
                compressed = compressor.compress(MARKER) + compressor.flush()
                result = self.reject_encoded(base64.b64encode(compressed).decode("ascii"))
                self.assertIsInstance(result["error"], zlib.error)

    def test_truncated_streams_rejected(self):
        compressed = zlib.compress(MARKER, 9)
        for removed in [1, 4, len(compressed) - 1]:
            with self.subTest(removed=removed):
                self.reject_encoded(base64.b64encode(compressed[:-removed]).decode("ascii"))

    def test_adler_checksum_corruption_rejected(self):
        compressed = bytearray(zlib.compress(MARKER, 9))
        compressed[-1] ^= 1
        result = self.reject_encoded(base64.b64encode(compressed).decode("ascii"))
        self.assertIsInstance(result["error"], zlib.error)

    def test_trailing_bytes_and_concatenated_streams_rejected(self):
        first = zlib.compress(MARKER, 9)
        for suffix in [b"\x00", b"trailing", zlib.compress(b"", 9), first]:
            with self.subTest(suffix_length=len(suffix)):
                self.reject_encoded(base64.b64encode(first + suffix).decode("ascii"))

    def test_preset_dictionary_stream_rejected(self):
        compressor = zlib.compressobj(level=9, zdict=b"SYNTHETIC_HELPER_EXECUTED")
        compressed = compressor.compress(MARKER) + compressor.flush()
        result = self.reject_encoded(base64.b64encode(compressed).decode("ascii"))
        self.assertIsInstance(result["error"], zlib.error)

    def test_exact_decompressed_limit_is_accepted(self):
        raw = b"#" + b"x" * (HELPER_MAX_BYTES - len(MARKER) - 2) + b"\n" + MARKER
        self.assertEqual(len(raw), HELPER_MAX_BYTES)
        result = self.invoke(raw)
        self.assertIsNone(result["error"])
        self.assertEqual(result["stdout"], "SYNTHETIC_HELPER_EXECUTED\n")

    def test_one_byte_above_decompressed_limit_is_rejected(self):
        raw = b"#" + b"x" * (HELPER_MAX_BYTES - len(MARKER) - 1) + b"\n" + MARKER
        self.assertEqual(len(raw), HELPER_MAX_BYTES + 1)
        result = self.reject_encoded(frame(raw), raw=raw)
        self.assertIsInstance(result["error"], ValueError)
        self.assertIn("98304", str(result["error"]))

    def test_large_compressed_stream_with_oversize_output_is_rejected(self):
        # No independent compressed-byte cap is specified. This fixture exceeds
        # the output cap even when compression leaves more than 98,304 bytes.
        noise = random.Random(43127).randbytes(110_000)
        raw = b"#" + base64.b64encode(noise) + b"\n" + MARKER
        compressed = zlib.compress(raw, 9)
        self.assertGreater(len(compressed), HELPER_MAX_BYTES)
        result = self.reject_encoded(base64.b64encode(compressed).decode("ascii"), raw=raw)
        self.assertIsInstance(result["error"], ValueError)
        self.assertIn("98304", str(result["error"]))

    def test_wrong_raw_hash_prevents_execution(self):
        result = self.reject_encoded(frame(MARKER), pin="0" * 64)
        self.assertIsInstance(result["error"], ValueError)
        self.assertIn("SHA256", str(result["error"]))

    def test_hash_is_checked_before_utf8_decoding(self):
        raw = b"\xff\xfe"
        result = self.reject_encoded(frame(raw), raw=raw, pin="0" * 64)
        self.assertIs(type(result["error"]), ValueError)
        self.assertIn("SHA256", str(result["error"]))

    def test_correct_hash_invalid_utf8_rejected_before_argument_removal(self):
        raw = b"\xff\xfe"
        result = self.reject_encoded(frame(raw), raw=raw)
        self.assertIsInstance(result["error"], UnicodeDecodeError)

    def test_hash_is_checked_before_compiling_helper(self):
        raw = b"this is invalid Python !\n"
        result = self.reject_encoded(frame(raw), raw=raw, pin="0" * 64)
        self.assertIs(type(result["error"]), ValueError)
        self.assertIn("SHA256", str(result["error"]))

    def test_raw_hash_authority_does_not_require_compressed_byte_identity(self):
        # Producers use level 9; acceptance must not pin version-specific bytes.
        for level in [0, 1, 6, 9]:
            with self.subTest(level=level):
                result = self.invoke(MARKER, encoded=frame(MARKER, level))
                self.assertIsNone(result["error"])
                self.assertEqual(result["stdout"], "SYNTHETIC_HELPER_EXECUTED\n")

    def test_decode_failure_retains_original_exception_and_traceback(self):
        result = self.reject_encoded("!")
        error = result["error"]
        frames = traceback.extract_tb(error.__traceback__)
        self.assertTrue(any(frame.filename == "<reviewed-bootstrap>" for frame in frames))
        self.assertFalse(any(frame.filename == "<static-remote>" for frame in frames))
        self.assertIsNone(error.__cause__)
        self.assertFalse(error.__suppress_context__)

    def test_helper_exception_is_not_converted_to_a_success_envelope(self):
        raw = b"raise RuntimeError('synthetic helper failure')\n"
        result = self.invoke(raw)
        self.assertIs(type(result["error"]), RuntimeError)
        self.assertEqual(str(result["error"]), "synthetic helper failure")
        self.assertEqual(result["stdout"], "")
        self.assertEqual(result["stderr"], "")
        self.assertEqual(result["argv"], ["-c", "inventory", "0123456789abcdef" * 2])
        formatted = "".join(traceback.format_exception(
            type(result["error"]), result["error"], result["error"].__traceback__
        ))
        self.assertIn("<reviewed-bootstrap>", formatted)
        self.assertIn("<static-remote>", formatted)
        self.assertIn("RuntimeError: synthetic helper failure", formatted)


if __name__ == "__main__":
    unittest.main()
