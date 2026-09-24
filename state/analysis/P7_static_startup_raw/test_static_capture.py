# Checks the fixed static-image capture contract with independent in-memory inputs.
# Keeps interpretation expectations separate from collector and implementation code.
# Run with Python -B only after the coordinator freezes this specification suite.
import copy
import importlib.util
from pathlib import Path
import struct
import unittest


PLAN = (
    ("before.loader.0", 0x08000000, 65536),
    ("before.loader.1", 0x08010000, 65536),
    ("before.loader.2", 0x08020000, 65536),
    ("before.loader.3", 0x08030000, 65536),
    ("before.loader.4", 0x08040000, 1536),
    ("before.sketch.0", 0x08100000, 65536),
    ("before.sketch.1", 0x08110000, 27560),
    ("first.runtime", 0x2003BC98, 28),
    ("first.transaction", 0x2003B2B0, 24),
    ("second.runtime", 0x2003BC98, 28),
    ("second.transaction", 0x2003B2B0, 24),
    ("after.sketch.0", 0x08100000, 65536),
    ("after.sketch.1", 0x08110000, 27560),
    ("after.loader.0", 0x08000000, 65536),
    ("after.loader.1", 0x08010000, 65536),
    ("after.loader.2", 0x08020000, 65536),
    ("after.loader.3", 0x08030000, 65536),
    ("after.loader.4", 0x08040000, 1536),
)
RUNTIME_PHASES = ("NOT_STARTED", "RUNNING", "STOPPED", "FAULT", "STOP_OBSERVING")
RUNTIME_FAULTS = ("NONE", "PORT", "CLOCK", "SERVICE_LIMIT", "TRANSACTION", "PROJECTION")
TRANSACTION_PHASES = ("NOT_INITIALIZED", "IDLE", "ACQUIRING", "DECIDED", "FAULT")
TRANSACTION_FAULTS = ("NONE", "SETUP", "ORDER", "CLOCK", "IDENTITY", "RECEIPT", "ABORTED")
RUNTIME_FLAGS = ("fresh", "initialization_complete", "raw_lines", "imu_expired", "calibration_interrupted")
TRANSACTION_FLAGS = ("decision_made", "finished", "timing_valid")
RUNTIME_WORDS = ("next_release_us", "missed_releases", "epochs", "service_passes", "maximum_execution_us")
TRANSACTION_WORDS = ("started_us", "decision_us", "completed_us", "execution_us")
FLASH_KEYS = ("before_loader", "before_sketch", "after_loader", "after_sketch")
RESULT_KEYS = {"flash", "observation", "runtime", "transaction", "epoch_delta", "errors"}
LOADER = (bytes(range(256)) * 1030)[:263680]
SKETCH = (bytes(reversed(range(256))) * 364)[:93096]


class StringSubclass(str):
    pass


class IntSubclass(int):
    pass


class BytesSubclass(bytes):
    pass


def runtime(phase=1, fault=0, flags=(0, 0, 1, 0, 0), epochs=100):
    return bytes((phase, fault, *flags, 0)) + struct.pack("<5I", 0, 0, epochs, 0, 0)


def transaction(phase=1, fault=0, flags=(0, 0, 0)):
    return bytes((phase, fault, *flags, 0, 0, 0)) + struct.pack("<4I", 0, 0, 0, 0)


def capture(first=None, second=None, first_tx=None, second_tx=None):
    samples = {
        "first.runtime": runtime() if first is None else first,
        "second.runtime": runtime(epochs=101) if second is None else second,
        "first.transaction": transaction() if first_tx is None else first_tx,
        "second.transaction": transaction() if second_tx is None else second_tx,
    }
    reads = []
    for name, address, count in PLAN:
        if name in samples:
            data = samples[name]
        else:
            source, base = (LOADER, 0x08000000) if ".loader." in name else (SKETCH, 0x08100000)
            data = source[address - base:address - base + count]
        reads.append((name, address, data))
    return reads


def replace_field(reads, index, field, value):
    triple = list(reads[index])
    triple[field] = value
    reads[index] = tuple(triple)


def alter_byte(reads, index, offset, value):
    data = reads[index][2]
    replace_field(reads, index, 2, data[:offset] + bytes((value,)) + data[offset + 1:])


class StaticCaptureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        target = Path(__file__).with_name("static_capture.py")
        spec = importlib.util.spec_from_file_location("static_capture_contract_subject", target)
        cls.subject = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.subject)

    def analyze(self, reads=None, loader=LOADER, sketch=SKETCH):
        return self.subject.analyze_capture(capture() if reads is None else reads, loader, sketch)

    def assert_observation(self, reads, status, delta=None, errors=()):
        result = self.analyze(reads)
        self.assertEqual(result["observation"], status)
        self.assertEqual(result["epoch_delta"], delta)
        if delta is not None:
            self.assertIs(type(result["epoch_delta"]), int)
        self.assertEqual(result["errors"], list(errors))
        return result

    def test_public_plan_exact_addresses_order_sizes_and_total(self):
        plan = self.subject.read_plan()
        self.assertEqual(plan, PLAN)
        self.assertEqual(len(plan), 18)
        self.assertEqual(sum(row[2] for row in plan), 713656)
        self.assertEqual(plan[4][1] + plan[4][2], 0x08040600)
        self.assertEqual(plan[6][1] + plan[6][2], 0x08116BA8)

    def test_public_plan_is_immutable_at_both_levels(self):
        plan = self.subject.read_plan()
        self.assertIs(type(plan), tuple)
        for row in plan:
            self.assertIs(type(row), tuple)
            self.assertEqual(tuple(type(value) for value in row), (str, int, int))
        with self.assertRaises(TypeError):
            plan[0] = ("wrong", 0, 0)
        with self.assertRaises(TypeError):
            plan[0][0] = "wrong"
        self.assertEqual(self.subject.read_plan(), PLAN)

    def test_public_result_exact_shape_and_success_types(self):
        result = self.assert_observation(capture(), "RUNNING_COUNTER_ADVANCED", 1)
        self.assertIs(type(result), dict)
        self.assertEqual(set(result), RESULT_KEYS)
        self.assertIs(type(result["flash"]), dict)
        self.assertEqual(result["flash"], dict.fromkeys(FLASH_KEYS, True))
        for flag in result["flash"].values():
            self.assertIs(type(flag), bool)
        for kind in ("runtime", "transaction", "errors"):
            self.assertIs(type(result[kind]), list)
        self.assertEqual(len(result["runtime"]), 2)
        self.assertEqual(len(result["transaction"]), 2)
        self.assertIs(type(result["observation"]), str)

    def test_public_accepts_list_and_tuple_outer_and_triples(self):
        for outer in (list, tuple):
            for inner in (list, tuple):
                with self.subTest(outer=outer, inner=inner):
                    reads = outer(inner(row) for row in capture())
                    self.assert_observation(reads, "RUNNING_COUNTER_ADVANCED", 1)

    def test_public_rejects_outer_types_without_coercion(self):
        for bad in (None, False, 18, "reads", b"reads", {}, iter(capture())):
            with self.subTest(type=type(bad)):
                with self.assertRaises(ValueError):
                    self.subject.analyze_capture(bad, LOADER, SKETCH)

    def test_public_rejects_read_counts_below_and_above_eighteen(self):
        for reads in ([], capture()[:-1], capture() + [capture()[0]]):
            with self.subTest(count=len(reads)):
                with self.assertRaises(ValueError):
                    self.analyze(reads)

    def test_public_rejects_triple_shape_and_type_at_every_position(self):
        for index in range(18):
            for bad in (None, {}, "abc", b"abc", (), (1, 2), (1, 2, 3, 4)):
                with self.subTest(index=index, bad=bad):
                    reads = capture()
                    reads[index] = bad
                    with self.assertRaises(ValueError):
                        self.analyze(reads)

    def test_public_rejects_non_string_and_subclass_labels(self):
        for index in range(18):
            for bad in (None, True, index, PLAN[index][0].encode(), StringSubclass(PLAN[index][0])):
                with self.subTest(index=index, type=type(bad)):
                    reads = capture()
                    replace_field(reads, index, 0, bad)
                    with self.assertRaises(ValueError):
                        self.analyze(reads)

    def test_public_rejects_unknown_duplicate_and_reordered_labels(self):
        for index in range(18):
            for label in ("unknown", PLAN[(index + 1) % 18][0]):
                with self.subTest(index=index, label=label):
                    reads = capture()
                    replace_field(reads, index, 0, label)
                    with self.assertRaises(ValueError):
                        self.analyze(reads)
        for first, second in ((0, 1), (7, 9), (8, 10), (5, 11), (0, 13)):
            reads = capture()
            reads[first], reads[second] = reads[second], reads[first]
            with self.subTest(swapped=(first, second)):
                with self.assertRaises(ValueError):
                    self.analyze(reads)

    def test_public_rejects_addresses_of_wrong_type_or_value(self):
        for index, (_, address, _) in enumerate(PLAN):
            for bad in (True, float(address), str(address), None, IntSubclass(address), address - 1, address + 1):
                with self.subTest(index=index, value=bad, type=type(bad)):
                    reads = capture()
                    replace_field(reads, index, 1, bad)
                    with self.assertRaises(ValueError):
                        self.analyze(reads)

    def test_public_rejects_non_bytes_and_bytes_subclass_data(self):
        for index in range(18):
            data = capture()[index][2]
            for bad in (None, True, bytearray(data), memoryview(data), list(data), BytesSubclass(data)):
                with self.subTest(index=index, type=type(bad)):
                    reads = capture()
                    replace_field(reads, index, 2, bad)
                    with self.assertRaises(ValueError):
                        self.analyze(reads)

    def test_public_rejects_each_read_length_one_byte_either_side(self):
        for index in range(18):
            data = capture()[index][2]
            for bad in (data[:-1], data + b"\x00"):
                with self.subTest(index=index, length=len(bad)):
                    reads = capture()
                    replace_field(reads, index, 2, bad)
                    with self.assertRaises(ValueError):
                        self.analyze(reads)

    def test_public_rejects_each_reference_type_and_subclass(self):
        for position, reference in enumerate((LOADER, SKETCH)):
            for bad in (None, True, "image", bytearray(reference), memoryview(reference), BytesSubclass(reference)):
                references = [LOADER, SKETCH]
                references[position] = bad
                with self.subTest(position=position, type=type(bad)):
                    with self.assertRaises(ValueError):
                        self.subject.analyze_capture(capture(), *references)

    def test_public_rejects_reference_lengths_at_both_boundaries(self):
        for position, reference in enumerate((LOADER, SKETCH)):
            for bad in (b"", reference[:-1], reference + b"\x00"):
                references = [LOADER, SKETCH]
                references[position] = bad
                with self.subTest(position=position, length=len(bad)):
                    with self.assertRaises(ValueError):
                        self.subject.analyze_capture(capture(), *references)
        with self.assertRaises(ValueError):
            self.subject.analyze_capture(capture(), SKETCH, LOADER)

    def test_public_shape_rejection_still_applies_with_flash_mismatch(self):
        reads = capture()
        alter_byte(reads, 0, 0, 99)
        replace_field(reads, 17, 1, 0)
        with self.assertRaises(ValueError):
            self.analyze(reads)

    def test_flash_complete_comparison_catches_first_and_last_byte_of_every_chunk(self):
        for index, (name, _, count) in enumerate(PLAN):
            if name.startswith(("first.", "second.")):
                continue
            key = "_".join(name.split(".")[:2])
            for offset in (0, count - 1):
                with self.subTest(index=index, offset=offset):
                    reads = capture()
                    alter_byte(reads, index, offset, reads[index][2][offset] ^ 0xFF)
                    result = self.assert_observation(reads, "FLASH_MISMATCH")
                    self.assertEqual(result["flash"], {item: item != key for item in FLASH_KEYS})
                    self.assertEqual(result["runtime"], [])
                    self.assertEqual(result["transaction"], [])

    def test_flash_all_mismatch_combinations_keep_four_independent_booleans(self):
        for mask in range(1, 16):
            reads = capture()
            for bit, index in enumerate((0, 5, 13, 11)):
                if mask & (1 << bit):
                    alter_byte(reads, index, 0, reads[index][2][0] ^ 1)
            with self.subTest(mask=mask):
                result = self.assert_observation(reads, "FLASH_MISMATCH")
                self.assertEqual(result["flash"], {key: not bool(mask & (1 << bit)) for bit, key in enumerate(FLASH_KEYS)})
                self.assertTrue(all(type(value) is bool for value in result["flash"].values()))

    def test_flash_reference_bytes_are_compared_in_full(self):
        for which, reference in enumerate((LOADER, SKETCH)):
            changed = reference[:-1] + bytes((reference[-1] ^ 1,))
            references = [LOADER, SKETCH]
            references[which] = changed
            result = self.subject.analyze_capture(capture(), *references)
            expected = {key: ("loader" not in key if which == 0 else "sketch" not in key) for key in FLASH_KEYS}
            self.assertEqual(result["flash"], expected)
            self.assertEqual(result["observation"], "FLASH_MISMATCH")

    def test_priority_flash_mismatch_suppresses_all_malformed_ram_decoding(self):
        reads = capture(first=b"\xff" * 28, second=b"\xff" * 28,
                        first_tx=b"\xff" * 24, second_tx=b"\xff" * 24)
        alter_byte(reads, 17, 1535, reads[17][2][-1] ^ 1)
        result = self.assert_observation(reads, "FLASH_MISMATCH")
        self.assertEqual(result["runtime"], [])
        self.assertEqual(result["transaction"], [])

    def test_layout_runtime_literal_little_endian_fields_and_raw_padding(self):
        raw = bytes.fromhex("04 05 01 00 01 00 01 a5 04 03 02 01 ff ff ff ff 78 56 34 12 00 00 00 80 01 00 00 00")
        expected = {
            "phase": 4, "fault": 5, "phase_name": "STOP_OBSERVING", "fault_name": "PROJECTION",
            "fresh": 1, "initialization_complete": 0, "raw_lines": 1,
            "imu_expired": 0, "calibration_interrupted": 1,
            "next_release_us": 0x01020304, "missed_releases": 0xFFFFFFFF,
            "epochs": 0x12345678, "service_passes": 0x80000000,
            "maximum_execution_us": 1, "raw_hex": raw.hex(),
        }
        for pair in (0, 1):
            reads = capture(first=raw) if pair == 0 else capture(second=raw)
            result = self.assert_observation(reads, "SAMPLED_FAULT")
            self.assertEqual(result["runtime"][pair], expected)

    def test_layout_transaction_literal_little_endian_fields_and_raw_padding(self):
        raw = bytes.fromhex("03 06 01 00 01 aa bb cc 04 03 02 01 ff ff ff ff 00 00 00 80 78 56 34 12")
        expected = {
            "phase": 3, "fault": 6, "phase_name": "DECIDED", "fault_name": "ABORTED",
            "decision_made": 1, "finished": 0, "timing_valid": 1,
            "started_us": 0x01020304, "decision_us": 0xFFFFFFFF,
            "completed_us": 0x80000000, "execution_us": 0x12345678,
            "raw_hex": raw.hex(),
        }
        for pair in (0, 1):
            reads = capture(first_tx=raw) if pair == 0 else capture(second_tx=raw)
            result = self.assert_observation(reads, "SAMPLED_FAULT")
            self.assertEqual(result["transaction"][pair], expected)

    def test_layout_decoded_fields_have_exact_keys_and_raw_integer_types(self):
        result = self.analyze()
        for kind, flags, words in (("runtime", RUNTIME_FLAGS, RUNTIME_WORDS),
                                   ("transaction", TRANSACTION_FLAGS, TRANSACTION_WORDS)):
            keys = {"phase", "fault", "phase_name", "fault_name", "raw_hex", *flags, *words}
            for decoded in result[kind]:
                self.assertIs(type(decoded), dict)
                self.assertEqual(set(decoded), keys)
                for key in ("phase", "fault", *flags, *words):
                    self.assertIs(type(decoded[key]), int)
                for key in ("phase_name", "fault_name", "raw_hex"):
                    self.assertIs(type(decoded[key]), str)

    def test_layout_padding_never_adds_errors_or_changes_status(self):
        reads = capture()
        for index, offsets in ((7, (7,)), (9, (7,)), (8, (5, 6, 7)), (10, (5, 6, 7))):
            for offset in offsets:
                alter_byte(reads, index, offset, 255)
        result = self.assert_observation(reads, "RUNNING_COUNTER_ADVANCED", 1)
        for index, kind, pair in ((7, "runtime", 0), (8, "transaction", 0), (9, "runtime", 1), (10, "transaction", 1)):
            self.assertEqual(result[kind][pair]["raw_hex"], reads[index][2].hex())

    def test_enums_every_documented_name_and_first_invalid_and_byte_max(self):
        specifications = (("runtime", (7, 9), "phase", 0, RUNTIME_PHASES),
                          ("runtime", (7, 9), "fault", 1, RUNTIME_FAULTS),
                          ("transaction", (8, 10), "phase", 0, TRANSACTION_PHASES),
                          ("transaction", (8, 10), "fault", 1, TRANSACTION_FAULTS))
        for kind, indices, field, offset, names in specifications:
            for pair, index in enumerate(indices):
                for value in (*range(len(names)), len(names), 255):
                    reads = capture()
                    alter_byte(reads, index, offset, value)
                    with self.subTest(kind=kind, pair=pair, field=field, value=value):
                        result = self.analyze(reads)
                        decoded = result[kind][pair]
                        self.assertEqual(decoded[field], value)
                        self.assertEqual(decoded[field + "_name"], names[value] if value < len(names) else "UNKNOWN")
                        expected_errors = [] if value < len(names) else [f"{kind}[{pair}].{field}"]
                        self.assertEqual(result["errors"], expected_errors)
                        if expected_errors:
                            self.assertEqual(result["observation"], "MALFORMED_SAMPLES")
                            self.assertIsNone(result["epoch_delta"])

    def test_flags_every_field_in_each_pair_accepts_zero_one_rejects_two_255(self):
        for kind, indices, fields in (("runtime", (7, 9), RUNTIME_FLAGS),
                                      ("transaction", (8, 10), TRANSACTION_FLAGS)):
            for pair, index in enumerate(indices):
                for offset, field in enumerate(fields, start=2):
                    for value in (0, 1, 2, 255):
                        reads = capture()
                        alter_byte(reads, index, offset, value)
                        errors = () if value < 2 else (f"{kind}[{pair}].{field}",)
                        status = "RUNNING_COUNTER_ADVANCED" if value < 2 else "MALFORMED_SAMPLES"
                        delta = 1 if value < 2 else None
                        with self.subTest(kind=kind, pair=pair, field=field, value=value):
                            result = self.assert_observation(reads, status, delta, errors)
                            self.assertIs(type(result[kind][pair][field]), int)
                            self.assertEqual(result[kind][pair][field], value)

    def test_errors_order_is_pair_then_runtime_transaction_then_phase_fault_flags(self):
        reads = capture(first=b"\xff" * 28, second=b"\xff" * 28,
                        first_tx=b"\xff" * 24, second_tx=b"\xff" * 24)
        errors = []
        for pair in (0, 1):
            for kind, flags in (("runtime", RUNTIME_FLAGS), ("transaction", TRANSACTION_FLAGS)):
                errors.extend(f"{kind}[{pair}].{field}" for field in ("phase", "fault", *flags))
        result = self.assert_observation(reads, "MALFORMED_SAMPLES", errors=errors)
        self.assertEqual(len(result["runtime"]), 2)
        self.assertEqual(len(result["transaction"]), 2)
        self.assertTrue(all(type(error) is str for error in result["errors"]))

    def test_priority_malformed_beats_valid_sampled_fault_and_progress(self):
        for bad_index in (7, 8, 9, 10):
            reads = capture(first=runtime(fault=1), second_tx=transaction(phase=4))
            alter_byte(reads, bad_index, 2, 2)
            kind = "runtime" if bad_index in (7, 9) else "transaction"
            pair = 0 if bad_index in (7, 8) else 1
            field = "fresh" if kind == "runtime" else "decision_made"
            self.assert_observation(reads, "MALFORMED_SAMPLES", errors=(f"{kind}[{pair}].{field}",))

    def test_status_every_valid_nonzero_fault_in_either_pair_suppresses_delta(self):
        for kind, indices, faults in (("runtime", (7, 9), RUNTIME_FAULTS),
                                      ("transaction", (8, 10), TRANSACTION_FAULTS)):
            for index in indices:
                for fault in range(1, len(faults)):
                    reads = capture()
                    alter_byte(reads, index, 1, fault)
                    with self.subTest(kind=kind, index=index, fault=fault):
                        self.assert_observation(reads, "SAMPLED_FAULT")

    def test_status_fault_phase_with_zero_fault_still_suppresses_delta(self):
        for index, phase in ((7, 3), (9, 3), (8, 4), (10, 4)):
            reads = capture()
            alter_byte(reads, index, 0, phase)
            with self.subTest(index=index):
                self.assert_observation(reads, "SAMPLED_FAULT")

    def test_status_each_non_running_runtime_phase_in_either_pair_has_no_delta(self):
        for index in (7, 9):
            for phase in (0, 2, 4):
                reads = capture()
                alter_byte(reads, index, 0, phase)
                with self.subTest(index=index, phase=phase):
                    self.assert_observation(reads, "NO_RUNNING_PROGRESS")

    def test_status_non_atomic_transaction_phases_flags_and_times_add_no_coherence_rule(self):
        for phase in range(4):
            for bits in range(8):
                flags = tuple((bits >> bit) & 1 for bit in range(3))
                raw = transaction(phase=phase, flags=flags)[:8] + struct.pack("<4I", 999, 7, 0, 0xFFFFFFFF)
                reads = capture(first_tx=raw, second_tx=transaction(phase=0, flags=(1, 1, 1)))
                with self.subTest(phase=phase, flags=flags):
                    self.assert_observation(reads, "RUNNING_COUNTER_ADVANCED", 1)

    def test_status_runtime_readiness_flags_do_not_infer_progress_qualification(self):
        reads = capture(first=runtime(flags=(1, 0, 0, 1, 1), epochs=5),
                        second=runtime(flags=(0, 0, 1, 1, 1), epochs=6))
        self.assert_observation(reads, "RUNNING_COUNTER_ADVANCED", 1)

    def test_counters_modulo_wrap_zero_and_half_range_boundaries(self):
        cases = (
            (0, 0, 0, "NO_RUNNING_PROGRESS"),
            (17, 17, 0, "NO_RUNNING_PROGRESS"),
            (0, 1, 1, "RUNNING_COUNTER_ADVANCED"),
            (0, 0x7FFFFFFF, 0x7FFFFFFF, "RUNNING_COUNTER_ADVANCED"),
            (0, 0x80000000, 0x80000000, "NO_RUNNING_PROGRESS"),
            (0, 0x80000001, 0x80000001, "NO_RUNNING_PROGRESS"),
            (0, 0xFFFFFFFF, 0xFFFFFFFF, "NO_RUNNING_PROGRESS"),
            (0xFFFFFFFF, 0, 1, "RUNNING_COUNTER_ADVANCED"),
            (0xFFFFFFFE, 1, 3, "RUNNING_COUNTER_ADVANCED"),
            (1, 0, 0xFFFFFFFF, "NO_RUNNING_PROGRESS"),
            (0x80000001, 0, 0x7FFFFFFF, "RUNNING_COUNTER_ADVANCED"),
            (0x80000000, 0, 0x80000000, "NO_RUNNING_PROGRESS"),
        )
        for first, second, delta, status in cases:
            with self.subTest(first=first, second=second):
                self.assert_observation(capture(first=runtime(epochs=first), second=runtime(epochs=second)), status, delta)

    def test_counters_runtime_epoch_word_alone_determines_delta(self):
        first = runtime(epochs=7)[:8] + struct.pack("<5I", 999, 10, 7, 999, 888)
        second = runtime(epochs=8)[:8] + struct.pack("<5I", 0, 0, 8, 0, 0)
        self.assert_observation(capture(first=first, second=second), "RUNNING_COUNTER_ADVANCED", 1)

    def test_inputs_preserved_for_success_mismatch_malformed_and_fault(self):
        variants = [capture(), capture(first=b"\xff" * 28), capture(first_tx=transaction(fault=6))]
        mismatch = capture()
        alter_byte(mismatch, 11, 65535, mismatch[11][2][-1] ^ 1)
        variants.append(mismatch)
        for variant in variants:
            reads = [list(row) for row in variant]
            before = copy.deepcopy(reads)
            references = [LOADER, SKETCH]
            reference_ids = [id(item) for item in references]
            contained_ids = [[id(item) for item in row] for row in reads]
            self.subject.analyze_capture(reads, *references)
            self.assertEqual(reads, before)
            self.assertEqual([[id(item) for item in row] for row in reads], contained_ids)
            self.assertEqual([id(item) for item in references], reference_ids)
            self.assertEqual(references, [LOADER, SKETCH])

    def test_inputs_preserved_on_validation_error(self):
        reads = [list(row) for row in capture()]
        reads[-1][0] = "incorrect"
        before = copy.deepcopy(reads)
        with self.assertRaises(ValueError):
            self.analyze(reads)
        self.assertEqual(reads, before)

    def test_public_repeated_calls_do_not_retain_mutated_returned_results(self):
        reads = capture()
        pristine = self.analyze(reads)
        changed = self.analyze(reads)
        changed["flash"]["before_loader"] = False
        changed["runtime"][0]["epochs"] = 123456
        changed["transaction"].clear()
        changed["errors"].append("injected")
        self.assertEqual(self.analyze(reads), pristine)
        self.assertEqual(self.subject.read_plan(), PLAN)


if __name__ == "__main__":
    unittest.main()
