"""Check D105 canonical snippet decoding and file-only publication from its contract.

Authored and frozen before inspecting/importing the new Python implementation.
The author has earlier D104 runner context, not D105 implementation knowledge.
All inputs are synthetic local files; no serial, network or board is exercised.
"""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tools/qtr_config.py"
PROVENANCE = "UNATTRIBUTED_BARE_LINE"


def snippet(values=(350, 351, 352, 353)):
    return ("QTR_WHITE_US[4] = {" + ", ".join(str(value) + "U" for value in values) +
            "}; // us\n").encode("ascii")


def import_passive():
    name = "d105_independent_qtr_config"
    spec = importlib.util.spec_from_file_location(name, TOOL)
    module = importlib.util.module_from_spec(spec)
    out, err = io.StringIO(), io.StringIO()
    forbidden = AssertionError("No external action during parser import")
    with ExitStack() as context:
        for action in ("run", "Popen", "call", "check_call", "check_output"):
            context.enter_context(mock.patch.object(subprocess, action, side_effect=forbidden))
        context.enter_context(mock.patch.object(socket, "socket", side_effect=forbidden))
        context.enter_context(mock.patch.object(os, "system", side_effect=forbidden))
        context.enter_context(mock.patch("builtins.input", side_effect=forbidden))
        context.enter_context(mock.patch.dict(sys.modules, {name: module}))
        context.enter_context(mock.patch.object(sys, "argv", [str(TOOL), "--not-a-run"]))
        context.enter_context(redirect_stdout(out))
        context.enter_context(redirect_stderr(err))
        spec.loader.exec_module(module)
    return module, out.getvalue(), err.getvalue()


class QtrConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.subject, cls.stdout, cls.stderr = import_passive()

    def reject(self, blob, limit=1500):
        with self.assertRaises(ValueError):
            self.subject.decode_snippet(blob, limit)

    def cli(self, source, output, limit="1500", *extra):
        return subprocess.run([sys.executable, str(TOOL), str(source), "--timeout-us", limit,
                               "--output-dir", str(output), *extra], cwd=ROOT,
                              capture_output=True, text=True, timeout=5)

    def test_import_is_passive_and_decode_uses_exact_result(self):
        self.assertEqual(self.stdout, ""); self.assertEqual(self.stderr, "")
        self.assertEqual(self.subject.decode_snippet(snippet(), 1500),
                         {"white_us": [350, 351, 352, 353], "timeout_us": 1500,
                          "provenance": PROVENANCE})

    def test_value_and_timeout_boundaries(self):
        for values, limit in (((1, 1, 1, 1), 1), ((1, 1500, 2, 1499), 1500),
                              ((2147483647,) * 4, 2147483647),
                              ((7, 8, 9, 10), 10)):
            with self.subTest(values=values, limit=limit):
                self.assertEqual(self.subject.decode_snippet(snippet(values), limit),
                    {"white_us": list(values), "timeout_us": limit, "provenance": PROVENANCE})
        for values in ((0, 1, 1, 1), (1, 0, 1, 1), (1, 1, 0, 1), (1, 1, 1, 0),
                       (1501, 1, 1, 1), (1, 1501, 1, 1), (1, 1, 1501, 1), (1, 1, 1, 1501)):
            with self.subTest(values=values): self.reject(snippet(values))

    def test_blob_and_timeout_require_exact_types(self):
        class BytesChild(bytes): pass
        class IntChild(int): pass
        raw = snippet()
        for blob in (None, "text", list(raw), bytearray(raw), memoryview(raw), BytesChild(raw)):
            with self.subTest(blobtype=type(blob).__name__): self.reject(blob)
        for limit in (None, True, False, 1500.0, "1500", IntChild(1500), 0, -1, 2147483648):
            with self.subTest(limit=limit): self.reject(raw, limit)

    def test_canonical_ascii_grammar_has_no_alternate_spellings(self):
        raw = snippet()
        invalid = [b"", raw[:-1], raw + b"\n", raw + b"x", b" " + raw, raw + b" ",
                   raw.replace(b"\n", b"\r\n"), raw.replace(b"\n", b"\x00\n"),
                   raw.replace(b"[4]", b"[3]"), raw.replace(b" = ", b"="),
                   raw.replace(b", ", b","), raw.replace(b"U", b"u"),
                   raw.replace(b"350U", b"0350U"), raw.replace(b"350U", b"+350U"),
                   raw.replace(b"350U", b"-350U"), raw.replace(b"350U", b"350"),
                   raw.replace(b"350U", b"0x15eU"), raw.replace(b"350U", b"350.0U"),
                   raw.replace(b"350U", b"3_50U"), raw.replace(b"350U", b"\xffU"),
                   raw.replace(b"350U", "３５０U".encode()),
                   raw.replace(b"}; // us", b"}; // us "), raw.replace(b"}; // us", b"};"),
                   raw.replace(b"QTR_WHITE_US", b"QTR_WHITE_us"), raw * 2,
                   snippet((350, 351, 352)), snippet((350, 351, 352, 353, 354)),
                   b"QTR_WHITE_US[4] = {" + b"9" * 1000 + b"U, 1U, 1U, 1U}; // us\n"]
        for index, blob in enumerate(invalid):
            with self.subTest(index=index): self.reject(blob)

    def test_decoder_performs_no_file_network_or_process_io(self):
        raw = snippet()
        forbidden = AssertionError("Pure snippet decoding must not perform I/O")
        with ExitStack() as context:
            context.enter_context(mock.patch("builtins.open", side_effect=forbidden))
            context.enter_context(mock.patch.object(Path, "read_bytes", side_effect=forbidden))
            context.enter_context(mock.patch.object(socket, "socket", side_effect=forbidden))
            context.enter_context(mock.patch.object(subprocess, "run", side_effect=forbidden))
            first = self.subject.decode_snippet(raw, 1500)
            first["white_us"][0] = 0
            self.assertEqual(self.subject.decode_snippet(raw, 1500)["white_us"], [350, 351, 352, 353])

    def test_cli_publishes_only_exact_bytes_and_literal_receipt(self):
        before = hashlib.sha256((ROOT / "src/config.h").read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root / "input.txt"; out = root / "published"
            source.write_bytes(snippet())
            result = self.cli(source, out)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual({path.name for path in out.iterdir()}, {"snippet.txt", "receipt.json"})
            self.assertEqual((out / "snippet.txt").read_bytes(), snippet())
            self.assertEqual(json.loads((out / "receipt.json").read_text()),
                {"white_us": [350, 351, 352, 353], "timeout_us": 1500,
                 "provenance": PROVENANCE, "sha256": hashlib.sha256(snippet()).hexdigest(),
                 "byte_count": len(snippet())})
            self.assertEqual(source.read_bytes(), snippet())
        self.assertEqual(hashlib.sha256((ROOT / "src/config.h").read_bytes()).hexdigest(), before)

    def test_cli_rejects_malformed_extra_oversize_and_missing_inputs_without_publication(self):
        for index, blob in enumerate((snippet() + b"x", snippet() * 2, b"x" * 80,
                                       b"x" * 8192, snippet((0, 1, 1, 1)), b"")):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary); source = root / "input"; out = root / "out"
                source.write_bytes(blob); result = self.cli(source, out)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(out.exists())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for source in (root / "missing", root):
                with self.subTest(source=source):
                    result = self.cli(source, root / "out")
                    self.assertNotEqual(result.returncode, 0); self.assertFalse((root / "out").exists())

    def test_cli_refuses_existing_output_and_unknown_options_preserving_existing_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root / "input"; out = root / "out"
            source.write_bytes(snippet()); out.mkdir(); (out / "sentinel").write_bytes(b"keep")
            result = self.cli(source, out)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual({p.name for p in out.iterdir()}, {"sentinel"})
            self.assertEqual((out / "sentinel").read_bytes(), b"keep")
            result = self.cli(source, root / "new", "1500", "--serial", "COM1")
            self.assertNotEqual(result.returncode, 0); self.assertFalse((root / "new").exists())

    @unittest.skipIf(os.name == "nt", "Symlink/FIFO boundaries run in the Linux/WSL suite")
    def test_cli_refuses_input_output_symlinks_and_fifo(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root / "input"; source.write_bytes(snippet())
            link = root / "input-link"; link.symlink_to(source)
            result = self.cli(link, root / "out")
            self.assertNotEqual(result.returncode, 0); self.assertFalse((root / "out").exists())
            target = root / "target"; target.mkdir()
            outlink = root / "output-link"; outlink.symlink_to(target, target_is_directory=True)
            result = self.cli(source, outlink)
            self.assertNotEqual(result.returncode, 0); self.assertEqual(list(target.iterdir()), [])
            dangling = root / "dangling"; dangling.symlink_to(root / "missing")
            result = self.cli(source, dangling)
            self.assertNotEqual(result.returncode, 0); self.assertFalse((root / "missing").exists())
            fifo = root / "fifo"; os.mkfifo(fifo)
            result = self.cli(fifo, root / "out")
            self.assertNotEqual(result.returncode, 0); self.assertFalse((root / "out").exists())

    def test_cli_requires_explicit_valid_timeout(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); source = root / "input"; source.write_bytes(snippet())
            for value in ("0", "-1", "2147483648", "text", "1.5", "349"):
                with self.subTest(value=value):
                    result = self.cli(source, root / "out", value)
                    self.assertNotEqual(result.returncode, 0); self.assertFalse((root / "out").exists())
            result = subprocess.run([sys.executable, str(TOOL), str(source), "--output-dir", str(root / "out")],
                                    cwd=ROOT, capture_output=True, text=True, timeout=5)
            self.assertNotEqual(result.returncode, 0); self.assertFalse((root / "out").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
