// Supplies installed GPIO argument types and checked operations.
// Raw status and pin configuration remain independent from requested output.
// Host cases cover failures, readiness, flags and readback at the EN boundary.
#pragma once
#include <cstdint>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
using gpio_pin_t = std::uint8_t;
using gpio_dt_flags_t = std::uint16_t;
using gpio_flags_t = std::uint32_t;
using gpio_port_pins_t = std::uint32_t;
struct gpio_driver_config { gpio_port_pins_t port_pin_mask; };
struct gpio_dt_spec { const device* port; gpio_pin_t pin; gpio_dt_flags_t dt_flags; };
constexpr gpio_flags_t GPIO_OUTPUT = 1U << 17;
constexpr gpio_flags_t GPIO_OUTPUT_INIT_LOW = 1U << 18;
constexpr gpio_flags_t GPIO_OUTPUT_LOW = GPIO_OUTPUT | GPIO_OUTPUT_INIT_LOW;
int gpio_pin_configure_dt(const gpio_dt_spec*, gpio_flags_t);
int gpio_pin_set_raw(const device*, gpio_pin_t, int);
int gpio_pin_get_raw(const device*, gpio_pin_t);
inline bool gpio_is_ready_dt(const gpio_dt_spec* s) { return device_is_ready(s->port); }
