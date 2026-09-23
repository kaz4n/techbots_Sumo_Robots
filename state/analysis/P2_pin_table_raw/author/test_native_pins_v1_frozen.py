"""Verify D106's public shared descriptor binding through independent host TUs.

Only the frozen interface/spec and existing installed-shaped fixtures were read.
Production cpp is copied and hashed opaquely after this test file is frozen.
Synthetic descriptor data is not a pin map, hardware observation or I/O grant.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "state/analysis/P2_pin_table_raw/author"

GPIO_HEADER = """#pragma once
#include <cstdint>
struct device { std::uint32_t marker; };
using gpio_pin_t = std::uint8_t;
using gpio_dt_flags_t = std::uint16_t;
using gpio_flags_t = std::uint32_t;
struct gpio_dt_spec { const device* port; gpio_pin_t pin; gpio_dt_flags_t dt_flags; };
extern const device fixture_devices[3];
bool device_is_ready(const device*);
int gpio_pin_configure_dt(const gpio_dt_spec*, gpio_flags_t);
int gpio_pin_get_raw(const device*, gpio_pin_t);
int gpio_pin_set_raw(const device*, gpio_pin_t, int);
unsigned long micros();
void delay(unsigned long);
"""
PEER_A = """#include "hal/native_pins.h"
// Deliberately needs only the forward declaration, not a private definition.
extern "C" const gpio_dt_spec* peer_a_table() { return native_pins::TABLE; }
extern "C" const void* peer_a_pointer_object() { return &native_pins::TABLE; }
extern "C" const void* peer_a_count_object() { return &native_pins::COUNT; }
extern "C" std::size_t peer_a_count() { return native_pins::COUNT; }
"""
PEER_B = """#include <zephyr/drivers/gpio.h>
#include "hal/native_pins.h"
extern "C" const gpio_dt_spec* peer_b_table() { return native_pins::TABLE; }
extern "C" const void* peer_b_pointer_object() { return &native_pins::TABLE; }
extern "C" const void* peer_b_count_object() { return &native_pins::COUNT; }
extern "C" const gpio_dt_spec* peer_b_entry(std::size_t index) {
    return index < native_pins::COUNT ? &native_pins::TABLE[index] : nullptr;
}
"""
MAIN = """#include <zephyr/drivers/gpio.h>
#include "hal/native_pins.h"
#include <cstddef>
#include <cstdint>
#include <type_traits>
#include <cstdio>
const device fixture_devices[3] = {{101U}, {202U}, {303U}};
static unsigned io_calls = 0U;
bool device_is_ready(const device*) { ++io_calls; return false; }
int gpio_pin_configure_dt(const gpio_dt_spec*, gpio_flags_t) { ++io_calls; return -1; }
int gpio_pin_get_raw(const device*, gpio_pin_t) { ++io_calls; return -1; }
int gpio_pin_set_raw(const device*, gpio_pin_t, int) { ++io_calls; return -1; }
unsigned long micros() { ++io_calls; return 0U; }
void delay(unsigned long) { ++io_calls; }
extern "C" const gpio_dt_spec* peer_a_table();
extern "C" const void* peer_a_pointer_object();
extern "C" const void* peer_a_count_object();
extern "C" std::size_t peer_a_count();
extern "C" const gpio_dt_spec* peer_b_table();
extern "C" const void* peer_b_pointer_object();
extern "C" const void* peer_b_count_object();
extern "C" const gpio_dt_spec* peer_b_entry(std::size_t);
static_assert(std::is_same<decltype(native_pins::TABLE), const gpio_dt_spec* const>::value);
static_assert(std::is_same<decltype(native_pins::COUNT), const std::size_t>::value);
static_assert(std::is_same<decltype(native_pins::TABLE[0]), const gpio_dt_spec&>::value);
#define VERIFY(condition) do { if (!(condition)) { \
    std::fprintf(stderr, "line %d: %s\\n", __LINE__, #condition); return 1; } } while (false)
int main() {
    VERIFY(io_calls == 0U);
    VERIFY(native_pins::TABLE != nullptr);
    VERIFY(native_pins::COUNT == EXPECTED_COUNT);
    VERIFY(peer_a_count() == EXPECTED_COUNT);
    VERIFY(peer_a_table() == native_pins::TABLE);
    VERIFY(peer_b_table() == native_pins::TABLE);
    VERIFY(peer_a_pointer_object() == &native_pins::TABLE);
    VERIFY(peer_b_pointer_object() == &native_pins::TABLE);
    VERIFY(peer_a_count_object() == &native_pins::COUNT);
    VERIFY(peer_b_count_object() == &native_pins::COUNT);
    for (std::size_t i = 0U; i < EXPECTED_COUNT; ++i) {
        const auto* entry = peer_b_entry(i);
        VERIFY(entry == &native_pins::TABLE[i]);
        VERIFY(entry->port == &fixture_devices[i % 3U]);
        VERIFY(entry->pin == static_cast<gpio_pin_t>((i * 5U + 3U) % 32U));
        VERIFY(entry->dt_flags == static_cast<gpio_dt_flags_t>(0xA500U + i));
        VERIFY(entry->port->marker == (i % 3U + 1U) * 101U);
    }
    // These bounds checks belong to this test consumer, not to raw TABLE itself.
    VERIFY(peer_b_entry(EXPECTED_COUNT) == nullptr);
    VERIFY(peer_b_entry(static_cast<std::size_t>(-1)) == nullptr);
    VERIFY(io_calls == 0U);
    std::puts("PASS shared native descriptors");
    return 0;
}
"""


def receipt(kind, record):
    RAW.mkdir(parents=True, exist_ok=True)
    record["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (RAW / f"{kind}_{time.time_ns()}.json").open("x", encoding="utf-8") as stream:
        json.dump(record, stream, indent=2); stream.write("\n")


class NativePinsTests(unittest.TestCase):
    def command(self, argv, success=True):
        values = list(map(str, argv))
        result = subprocess.run(values, cwd=ROOT, capture_output=True, text=True, timeout=180)
        receipt("command", {"argv": values, "returncode": result.returncode,
                             "stdout": result.stdout, "stderr": result.stderr})
        if success: self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else: self.assertNotEqual(result.returncode, 0, "Const mutation unexpectedly compiled")
        return result

    def test_cross_translation_unit_identity_count_metadata_constness_and_passivity(self):
        receipt("test_freeze", {"implementation_body_read": False, "sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (Path(__file__), ROOT / "src/hal/native_pins.h",
                         ROOT / "state/analysis/P2_pin_table_contract.md")}})
        if os.name == "nt":
            self.command(["wsl.exe", "--exec", "python3", "-m", "unittest",
                          "tests.tooling.test_native_pins", "-v"])
            return
        compiler, nm, objdump = (shutil.which(tool) for tool in ("g++", "nm", "objdump"))
        self.assertIsNotNone(compiler); self.assertIsNotNone(nm); self.assertIsNotNone(objdump)
        with tempfile.TemporaryDirectory(prefix="sumo-d106-author-", dir="/dev/shm") as temporary:
            stage = Path(temporary); source = stage / "src/hal"; source.mkdir(parents=True)
            for name in ("native_pins.h", "native_pins.cpp"):
                shutil.copyfile(ROOT / "src/hal" / name, source / name)
            receipt("opaque_source_copy", {"sha256": {
                name: hashlib.sha256((source / name).read_bytes()).hexdigest()
                for name in ("native_pins.h", "native_pins.cpp")}})
            (stage / "zephyr/drivers").mkdir(parents=True)
            (stage / "zephyr/drivers/gpio.h").write_text(GPIO_HEADER)
            for name, content in (("peer_a.cc", PEER_A), ("peer_b.cc", PEER_B), ("main.cc", MAIN)):
                (stage / name).write_text(content)
            common = [compiler, "-std=c++17", "-O1", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                      "-fno-exceptions", "-fno-rtti", "-DARDUINO_ARCH_ZEPHYR", "-I", stage,
                      "-I", stage / "src"]
            for count in (1, 3, 17, 70, 71):
                rows = ",\n".join("{&fixture_devices[%d], %dU, %dU}" %
                                  (index % 3, (index * 5 + 3) % 32, 0xA500 + index)
                                  for index in range(count))
                (stage / "wiring_private.h").write_text("#pragma once\n#include <zephyr/drivers/gpio.h>\n"
                    "namespace zephyr { namespace arduino {\nconstexpr gpio_dt_spec arduino_pins[] = {\n" +
                    rows + "\n}; }}\n")
                for sanitized in (False, True):
                    with self.subTest(count=count, sanitizer=sanitized):
                        label = f"{count}-" + ("san" if sanitized else "normal")
                        native = stage / (label + "-native.o"); binary = stage / label
                        flags = (["-fsanitize=address,undefined", "-fno-sanitize-recover=all", "-no-pie"]
                                 if sanitized else [])
                        self.command([*common, *flags, "-c", source / "native_pins.cpp", "-o", native])
                        if not sanitized:
                            symbols = self.command([nm, "-C", "--undefined-only", native]).stdout
                            self.assertEqual([line.split()[-1] for line in symbols.splitlines() if line.strip()],
                                             ["fixture_devices"])
                            all_symbols = self.command([nm, "-C", native]).stdout
                            self.assertNotIn("_GLOBAL__sub_I", all_symbols)
                            self.assertNotIn("__static_initialization", all_symbols)
                            sections = self.command([objdump, "-h", native]).stdout
                            self.assertNotIn(".init_array", sections); self.assertNotIn(".ctors", sections)
                        self.command([*common, *flags, f"-DEXPECTED_COUNT={count}", native,
                                      stage / "peer_a.cc", stage / "peer_b.cc", stage / "main.cc", "-o", binary])
                        result = self.command([binary]); self.assertEqual(result.stdout.strip(), "PASS shared native descriptors")
            for name, statement in (("pointer", "native_pins::TABLE = nullptr;"),
                                     ("count", "native_pins::COUNT = 0U;"),
                                     ("entry", "native_pins::TABLE[0].pin = 0U;")):
                with self.subTest(refused_mutation=name):
                    path = stage / (name + "-mutation.cc")
                    path.write_text('#include <zephyr/drivers/gpio.h>\n#include "hal/native_pins.h"\n'
                                    'void change() { ' + statement + ' }\n')
                    self.command([*common, "-fsyntax-only", path], success=False)
            host = stage / "non-native.cc"
            host.write_text('#include "hal/native_pins.h"\nnamespace native_pins { int TABLE; int COUNT; }\n')
            self.command([compiler, "-std=c++17", "-Wall", "-Wextra", "-Werror", "-I", stage / "src",
                          "-c", host, "-o", stage / "non-native.o"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
