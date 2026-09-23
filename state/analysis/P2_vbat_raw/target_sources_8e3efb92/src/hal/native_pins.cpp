// Binds one immutable view of the installed UNO Q native pin descriptors.
// Eliminates duplicate retained tables without changing pins or native owners.
// Cross-unit native tests and exact target bytes/relocations verify D106.
#include "native_pins.h"

#if defined(ARDUINO_ARCH_ZEPHYR)
#include <Arduino.h>
#include <zephyr/drivers/gpio.h>
#include <wiring_private.h>

namespace native_pins {
const gpio_dt_spec* const TABLE = zephyr::arduino::arduino_pins;
const std::size_t COUNT = sizeof(zephyr::arduino::arduino_pins) /
                          sizeof(zephyr::arduino::arduino_pins[0]);
} // namespace native_pins
#endif
