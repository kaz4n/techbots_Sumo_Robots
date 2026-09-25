# Tests D174's public offline decoder against independently assembled ARM bytes.
# Preserves structural evidence without treating decoded state as acceptance.
# Run with unittest; fixtures use public headers and the observed D173 ABI only.
import hashlib
import importlib.util
import math
from pathlib import Path
import struct
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "motor_fault_decode_under_test", ROOT / "tools" / "motor_fault_decode.py"
)
DECODER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DECODER)

# Literal independent observations from active_abi.json (SHA-256 822c917d32d5
# bbbcb209ebfad88fd347b516141f85351b84058b3a5ac4ab77a4). Never import offsets.
SNAPSHOT_SIZE = 2592
CALL_BASES = tuple(44 + 32 * index for index in range(64)) + (2108, 2140)
RESULT_BASES = (2336, 2392, 2448, 2504)
HALT_BASES = (2292, 2560)
PHASE_NAMES = ("NOT_STARTED", "DISABLED", "RUNNING", "COMPLETE", "FAULT")


class Fixture:
    def __init__(self):
        self.blob = bytearray(SNAPSHOT_SIZE)
        self.occupied = set()

    def put(self, offset, fmt, value):
        struct.pack_into("<" + fmt, self.blob, offset, value)
        self.occupied.update(range(offset, offset + struct.calcsize("<" + fmt)))
        return value

    def fields(self, base, members):
        return {name: self.put(base + offset, fmt, value)
                for name, offset, fmt, value in members}


def make_call(fixture, base, seed):
    return fixture.fields(base, (
        ("stage", 0, "B", seed % 3),
        ("operation", 1, "B", seed % 5),
        ("channel", 2, "B", seed % 4),
        ("application", 4, "I", 0xFEDC0000 + seed),
        ("requested_high", 8, "?", seed % 2 == 0),
        ("period_cycles", 12, "I", 0x12340000 + seed),
        ("pulse_cycles", 16, "I", 0x56780000 + seed),
        ("invoked", 20, "?", seed % 3 != 0),
        ("completed", 21, "?", seed % 3 != 1),
        ("returned", 22, "?", seed % 3 != 2),
        ("timing_valid", 23, "?", seed % 2 != 0),
        ("started_us", 24, "I", 0xFFFFFF00 + seed),
        ("completed_us", 28, "I", seed),
    ))


def make_halt(fixture, base, seed):
    return fixture.fields(base, (
        ("fresh", 0, "?", seed % 2 == 0),
        ("attempted", 1, "?", seed % 2 != 0),
        ("inhibition_confirmed", 2, "?", seed % 3 == 0),
        ("timing_valid", 3, "?", seed % 3 != 0),
        ("started_us", 4, "I", 0xFFFFFFFE - seed),
        ("completed_us", 8, "I", seed + 1),
        ("fault", 12, "B", seed % 7),
    ))


def make_result(fixture, base, seed):
    feedback = fixture.fields(base, (
        ("applied_valid", 0, "?", seed % 2 == 0),
        ("token", 8, "Q", (1 << 63) + 2 * seed + 1),
        ("applied_us", 16, "I", 0xFFFFFFFA + seed),
        ("motors_enabled", 20, "?", seed % 2 != 0),
        ("duty_l", 24, "f", seed + 1.25),
        ("duty_r", 28, "f", -seed - 2.5),
        ("duration_valid", 32, "?", seed % 3 != 0),
        ("completed_us", 36, "I", seed + 2),
        ("execution_us", 40, "I", 0x80000000 + seed),
    ))
    return {"feedback": feedback,
            "fault": fixture.put(base + 48, "B", seed + 2),
            "consumed": fixture.put(base + 49, "?", seed % 2 != 0)}


def populated_snapshot():
    fixture = Fixture()
    calls = [make_call(fixture, base, seed)
             for seed, base in enumerate(CALL_BASES[:64])]
    trace = fixture.fields(44, (
        ("count", 2048, "I", 64), ("rejected", 2052, "I", 0xFFFFFFFF),
        ("clock_reads", 2056, "I", 0xABCDEF12),
        ("overflow", 2060, "?", True), ("timing_fault", 2061, "?", False),
        ("has_failure", 2062, "?", False), ("has_current", 2063, "?", True),
    ))
    trace.update(calls=calls, current=make_call(fixture, 2108, 64),
                 first_failure=make_call(fixture, 2140, 65))
    report = fixture.fields(2312, (
        ("phase", 0, "B", 4), ("failure", 1, "B", 5),
        ("begin_called", 2, "?", True), ("begin_ok", 3, "?", False),
        ("halt_called", 4, "?", True), ("begin_fault", 5, "B", 6),
        ("applications", 8, "I", 4),
        ("next_release_us", 12, "I", 0xFFFFFFFD),
        ("missed_releases", 16, "I", 0xFFFFFFFF),
    ))
    report.update(applied=[make_result(fixture, base, seed)
                           for seed, base in enumerate(RESULT_BASES)],
                  halt=make_halt(fixture, 2560, 5))
    return fixture, trace, report


def populated_expected():
    fixture, trace, report = populated_snapshot()
    gate = fixture.fields(2224, (
        ("fault_", 44, "B", 3), ("initialized_", 45, "?", True),
        ("began_", 46, "?", False), ("armed_", 47, "?", True),
        ("hold_complete_", 48, "?", False),
        ("release_us_", 52, "I", 0xFFFFFFFF),
        ("last_token_", 56, "Q", 0xFFFFFFFFFFFFFFFF),
        ("halted_", 64, "?", True),
    ))
    gate["halt_result_"] = make_halt(fixture, 2292, 6)
    runner = fixture.fields(0, (
        ("attempted_", 2576, "?", True),
        ("last_us_", 2580, "I", 0x80000001),
        ("equal_polls_", 2584, "I", 0xFFFFFFFF),
    ))
    return fixture, {
        "status": "DECODED", "schema": "motor-fault-snapshot-v1",
        "coherence": "UNPROVEN", "reported_phase": "FAULT",
        "runner": runner, "trace": trace, "report": report, "gate": gate,
    }


def bool_offsets():
    result = [base + relative for base in CALL_BASES
              for relative in (8, 20, 21, 22, 23)]
    result += [2104, 2105, 2106, 2107, 2314, 2315, 2316, 2576]
    result += [2269, 2270, 2271, 2272, 2288]
    result += [base + relative for base in RESULT_BASES
               for relative in (0, 20, 32, 49)]
    result += [base + relative for base in HALT_BASES for relative in range(4)]
    return result


def enum_offsets():
    result = [(base + relative, upper) for base in CALL_BASES
              for relative, upper in ((0, 2), (1, 4), (2, 3))]
    result += [(2312, 4), (2313, 5), (2317, 6), (2268, 6)]
    result += [(base + 48, 6) for base in RESULT_BASES]
    result += [(base + 12, 6) for base in HALT_BASES]
    return result


def float_locations():
    return [(base + relative, index, name)
            for index, base in enumerate(RESULT_BASES)
            for relative, name in ((24, "duty_l"), (28, "duty_r"))]


class MotorFaultDecodeTests(unittest.TestCase):
    def decode(self, blob):
        return DECODER.decode_snapshot(blob)

    def assert_structural_only(self, result, phase):
        self.assertEqual(result["status"], "DECODED")
        self.assertEqual(result["schema"], "motor-fault-snapshot-v1")
        self.assertEqual(result["coherence"], "UNPROVEN")
        self.assertEqual(result["reported_phase"], PHASE_NAMES[phase])
        self.assertEqual(set(result), {"status", "schema", "coherence",
                                      "reported_phase", "runner", "trace",
                                      "report", "gate"})

    def test_D174_fixture_abi_receipt_remains_exactly_the_observed_source(self):
        receipt = ROOT / "state" / "analysis" / "P7_motor_fault_raw" / "active_abi.json"
        self.assertEqual(hashlib.sha256(receipt.read_bytes()).hexdigest(),
                         "822c917d32d5bbbcb209ebfad88fd347b516141f85351b84058b3a5ac4ab77a4")

    def test_D174_zero_snapshot_preserves_every_slot_and_not_started(self):
        result = self.decode(bytes(SNAPSHOT_SIZE))
        self.assert_structural_only(result, 0)
        self.assertEqual(result["runner"], {
            "attempted_": False, "last_us_": 0, "equal_polls_": 0})
        self.assertEqual(len(result["trace"]["calls"]), 64)
        self.assertEqual(len(result["report"]["applied"]), 4)
        self.assertEqual(result["trace"]["count"], 0)
        self.assertEqual(result["report"]["applications"], 0)
        self.assertEqual(result["trace"]["current"], result["trace"]["calls"][0])
        self.assertEqual(result["trace"]["first_failure"], result["trace"]["calls"][0])
        self.assertEqual(result["report"]["halt"], result["gate"]["halt_result_"])
        self.assertIs(result["trace"]["has_failure"], False)
        self.assertIs(result["trace"]["has_current"], False)

    def test_D174_all_fields_and_array_endpoints_match_literal_arm_oracle(self):
        fixture, expected = populated_expected()
        original = bytes(fixture.blob)
        actual = self.decode(original)
        self.assertEqual(actual, expected)
        self.assertEqual(original, bytes(fixture.blob))
        self.assertEqual(actual["trace"]["calls"][63]["application"], 0xFEDC003F)
        self.assertEqual(actual["report"]["applied"][3]["feedback"]["token"],
                         (1 << 63) + 7)

    def test_D174_padding_ignored_ports_and_internal_state_are_not_interpreted(self):
        fixture, expected = populated_expected()
        for offset in set(range(SNAPSHOT_SIZE)) - fixture.occupied:
            fixture.blob[offset] = 0xFF
        self.assertEqual(self.decode(bytes(fixture.blob)), expected)

    def test_D174_every_reported_phase_remains_structurally_reportable(self):
        for phase in range(5):
            with self.subTest(phase=phase):
                fixture, expected = populated_expected()
                fixture.blob[2312] = phase
                expected["report"]["phase"] = phase
                expected["reported_phase"] = PHASE_NAMES[phase]
                result = self.decode(bytes(fixture.blob))
                self.assertEqual(result, expected)
                self.assert_structural_only(result, phase)

    def test_D174_absent_flags_and_partial_counts_do_not_erase_stored_records(self):
        for count, applications in ((0, 0), (1, 1), (63, 3), (64, 4)):
            with self.subTest(count=count, applications=applications):
                fixture, expected = populated_expected()
                fixture.put(2092, "I", count)
                fixture.put(2320, "I", applications)
                fixture.blob[2106:2108] = b"\x00\x00"
                expected["trace"].update(count=count, has_failure=False,
                                          has_current=False)
                expected["report"]["applications"] = applications
                self.assertEqual(self.decode(bytes(fixture.blob)), expected)

    def test_D174_failure_presence_flag_is_not_inferred_from_record_contents(self):
        blob = bytearray(SNAPSHOT_SIZE)
        blob[2106] = 1
        result = self.decode(bytes(blob))
        self.assertIs(result["trace"]["has_failure"], True)
        self.assertEqual(result["trace"]["first_failure"], result["trace"]["calls"][0])

    def test_D174_in_progress_callback_retains_unfinished_receipt(self):
        fixture, expected = populated_expected()
        fixture.blob[2312] = 2
        fixture.blob[2128:2132] = b"\x01\x00\x00\x00"
        expected["reported_phase"] = "RUNNING"
        expected["report"]["phase"] = 2
        expected["trace"]["current"].update(invoked=True, completed=False,
                                             returned=False, timing_valid=False)
        self.assertEqual(self.decode(bytes(fixture.blob)), expected)

    def test_D174_capacity_limits_reject_only_values_above_literal_extent(self):
        for offset, maximum in ((2092, 64), (2320, 4)):
            for value in (maximum + 1, 0xFFFFFFFF):
                with self.subTest(offset=offset, value=value):
                    blob = bytearray(SNAPSHOT_SIZE)
                    struct.pack_into("<I", blob, offset, value)
                    with self.assertRaises(ValueError):
                        self.decode(bytes(blob))

    def test_D174_every_decoded_enum_accepts_all_public_numeric_codes(self):
        for offset, maximum in enum_offsets():
            for value in range(maximum + 1):
                with self.subTest(offset=offset, value=value):
                    blob = bytearray(SNAPSHOT_SIZE)
                    blob[offset] = value
                    self.assertEqual(self.decode(bytes(blob))["status"], "DECODED")

    def test_D174_every_decoded_enum_rejects_invalid_codes_in_absent_late_slots(self):
        for offset, maximum in enum_offsets():
            for value in (maximum + 1, 255):
                with self.subTest(offset=offset, value=value):
                    blob = bytearray(SNAPSHOT_SIZE)
                    blob[offset] = value
                    with self.assertRaises(ValueError):
                        self.decode(bytes(blob))

    def test_D174_every_decoded_bool_accepts_one_without_lifecycle_inference(self):
        for offset in bool_offsets():
            with self.subTest(offset=offset):
                blob = bytearray(SNAPSHOT_SIZE)
                blob[offset] = 1
                self.assertEqual(self.decode(bytes(blob))["status"], "DECODED")

    def test_D174_every_decoded_bool_rejects_nonbinary_in_absent_late_slots(self):
        for offset in bool_offsets():
            for value in (2, 128, 255):
                with self.subTest(offset=offset, value=value):
                    blob = bytearray(SNAPSHOT_SIZE)
                    blob[offset] = value
                    with self.assertRaises(ValueError):
                        self.decode(bytes(blob))

    def test_D174_nonfinite_float_payloads_rejected_in_every_receipt_slot(self):
        for offset, index, name in float_locations():
            for bits in (0x7F800000, 0xFF800000, 0x7FC00001, 0x7F800001, 0xFFC12345):
                with self.subTest(slot=index, name=name, bits=hex(bits)):
                    blob = bytearray(SNAPSHOT_SIZE)
                    struct.pack_into("<I", blob, offset, bits)
                    with self.assertRaises(ValueError):
                        self.decode(bytes(blob))

    def test_D174_finite_float_edges_are_preserved_without_duty_thresholds(self):
        bit_patterns = (0, 0x80000000, 1, 0x80000001, 0x00800000,
                        0x7F7FFFFF, 0xFF7FFFFF, 0x41200000, 0xC1200000)
        for offset, index, name in float_locations():
            for bits in bit_patterns:
                with self.subTest(slot=index, name=name, bits=hex(bits)):
                    blob = bytearray(SNAPSHOT_SIZE)
                    struct.pack_into("<I", blob, offset, bits)
                    actual = self.decode(bytes(blob))["report"]["applied"][index]
                    value = actual["feedback"][name]
                    self.assertTrue(math.isfinite(value))
                    self.assertEqual(struct.pack("<f", value), struct.pack("<I", bits))

    def test_D174_uint64_tokens_preserve_exact_integer_precision(self):
        for offset, index in [(2280, None)] + [(base + 8, index)
                                              for index, base in enumerate(RESULT_BASES)]:
            for token in (0, 1, (1 << 53) + 1, (1 << 63) + 1, (1 << 64) - 1):
                with self.subTest(offset=offset, token=token):
                    blob = bytearray(SNAPSHOT_SIZE)
                    struct.pack_into("<Q", blob, offset, token)
                    result = self.decode(bytes(blob))
                    actual = result["gate"]["last_token_"] if index is None else (
                        result["report"]["applied"][index]["feedback"]["token"])
                    self.assertIs(type(actual), int)
                    self.assertEqual(actual, token)

    def test_D174_maximum_counters_are_not_misread_as_invalid_signed_values(self):
        fixture, expected = populated_expected()
        for offset in (2096, 2100, 2328, 2584):
            fixture.put(offset, "I", 0xFFFFFFFF)
        expected["trace"].update(rejected=0xFFFFFFFF, clock_reads=0xFFFFFFFF)
        self.assertEqual(self.decode(bytes(fixture.blob)), expected)

    def test_D174_wrapped_and_reversed_times_remain_raw_uint32(self):
        fixture, expected = populated_expected()
        for index, base in enumerate(CALL_BASES):
            start, end = ((0xFFFFFFFF, 0) if index % 2 else (100, 99))
            fixture.put(base + 24, "I", start)
            fixture.put(base + 28, "I", end)
            call = (expected["trace"]["calls"][index] if index < 64 else
                    expected["trace"]["current" if index == 64 else "first_failure"])
            call.update(started_us=start, completed_us=end)
        self.assertEqual(self.decode(bytes(fixture.blob)), expected)

    def test_D174_input_extent_must_match_one_snapshot_exactly(self):
        for size in (0, 1, 32, 2588, 2591, 2593, 2596, 5184):
            with self.subTest(size=size):
                with self.assertRaises(ValueError):
                    self.decode(bytes(size))

    def test_D174_other_builtin_input_types_raise_valueerror(self):
        good = bytes(SNAPSHOT_SIZE)
        values = (None, True, 2592, 2592.0, "\x00" * SNAPSHOT_SIZE,
                  bytearray(good), memoryview(good), list(good), tuple(good),
                  {"blob": good}, object(), iter(good))
        for value in values:
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(ValueError):
                    self.decode(value)

    def test_D174_byte_conversion_protocol_is_not_accepted(self):
        class Convertible:
            def __bytes__(self):
                raise AssertionError("decoder must not invoke coercion")
        with self.assertRaises(ValueError):
            self.decode(Convertible())

    def test_D174_rejected_mutable_input_is_not_modified(self):
        fixture, _ = populated_expected()
        original = bytes(fixture.blob)
        with self.assertRaises(ValueError):
            self.decode(fixture.blob)
        self.assertEqual(bytes(fixture.blob), original)

if __name__ == "__main__":
    unittest.main()
