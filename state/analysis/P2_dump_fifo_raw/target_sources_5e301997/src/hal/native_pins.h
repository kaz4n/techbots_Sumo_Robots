// Shares the installed native pin descriptors without changing their meaning.
// Avoids retaining one identical read-only table in each HAL translation unit.
// Cross-unit native tests and exact target table/relocation audits verify D106.
#pragma once
#if defined(ARDUINO_ARCH_ZEPHYR)
#include <cstddef>
struct gpio_dt_spec;
namespace native_pins {
extern const gpio_dt_spec* const TABLE;
extern const std::size_t COUNT;
} // namespace native_pins
#endif
